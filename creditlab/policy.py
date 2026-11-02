"""OPA service adapter; all outcome selection lives in versioned Rego."""
import hashlib
import json
import subprocess
from pathlib import Path
import torch
from .features import calculate

ROOT = Path(__file__).resolve().parents[1]


class OpaPolicy(torch.nn.Module):
    def __init__(self, state, opa=None, policy=None, bundle=None):
        super().__init__()
        self.opa = str(opa or ROOT / 'bin/opa')
        self.policy = Path(policy or ROOT / 'policies/credit.rego')
        self.bundle = Path(bundle or ROOT / 'models/policy.json')
        self.bundle_hash = hashlib.sha256(self.bundle.read_bytes()).hexdigest()
        self.rego_hash = hashlib.sha256(self.policy.read_bytes()).hexdigest()
        for name, value in state.items():
            self.register_buffer(name, value.clone())

    def forward(self, features, missing, margin):
        from .native_core import CheckpointDemoPolicyOutput
        if hashlib.sha256(self.policy.read_bytes()).hexdigest() != self.rego_hash:
            raise RuntimeError('unapproved policy code change')
        if hashlib.sha256(self.bundle.read_bytes()).hexdigest() != self.bundle_hash:
            raise RuntimeError('unapproved policy data change')
        bundle = json.loads(self.bundle.read_text())
        # Versioned policy data is loaded independently of the Qwen checkpoint.
        thresholds = bundle['thresholds']
        if thresholds != self.thresholds.tolist():
            raise RuntimeError('policy contract and active bundle disagree')
        c, f = calculate(features.cpu().numpy(), missing.cpu().numpy(),
                         [self.dev_minimum.numpy(), self.dev_maximum.numpy()], thresholds)
        rows = [dict(calculations=a, flags=b, margin=int(m))
                for a,b,m in zip(c.tolist(), f.tolist(), margin.tolist())]
        process = subprocess.run([self.opa, 'eval', '-f', 'json', '-d', str(self.policy),
                                  '--stdin-input', 'data.credit.decisions'],
                                 input=json.dumps({'rows': rows, 'thresholds': thresholds}),
                                 text=True, capture_output=True, timeout=90)
        if process.returncode:
            raise RuntimeError(process.stdout + process.stderr)
        result = json.loads(process.stdout)
        try:
            values = result['result'][0]['expressions'][0]['value']
        except (KeyError,IndexError) as exc:
            raise RuntimeError('OPA returned no decision') from exc
        if len(values) != len(rows):
            raise RuntimeError('OPA did not return exactly one decision per row')
        integer = lambda a: torch.tensor(a, dtype=torch.int64)
        risk = integer([v['risk_band'] for v in values])
        outcome = integer([v['outcome'] for v in values])
        p = torch.sigmoid(margin.to(torch.float64) / 1e9)
        calibrated = torch.sigmoid(self.platt[1] + self.platt[0]*(margin.to(torch.float64)/1e9))
        return CheckpointDemoPolicyOutput(integer(c), integer(f), risk,
            torch.nn.functional.one_hot(risk,4), integer([v['triggers'] for v in values]),
            outcome, torch.nn.functional.one_hot(outcome,5),
            integer([v['final_reasons'] for v in values]), p, calibrated)
