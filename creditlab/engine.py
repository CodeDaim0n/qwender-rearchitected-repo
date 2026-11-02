"""Detached deterministic engine. Qwen is never instantiated in this component.

The upstream arithmetic/serialization code is deliberately reused in both arms.
Only policy execution is replaced with an independent OPA process.
"""
import json
from pathlib import Path
from types import SimpleNamespace
import torch
from safetensors.torch import load_file
from . import native_core as native
from .policy import OpaPolicy


class DetachedEngine(native.CreditEngineMethods):

    def __init__(self, directory, opa=None, policy=None):
        super().__init__()
        directory = Path(directory)
        self.config = SimpleNamespace(compiled_credit=json.loads((directory/'metadata.json').read_text()))
        self.compiled_credit = native.CheckpointCompiledCredit(self.config.compiled_credit)
        state = load_file(str(directory/'scorer-attribution.safetensors'))
        policy_data = json.loads((directory/'policy.json').read_text())
        policy_state = {name: torch.tensor(value, dtype=getattr(torch,dtype))
                        for name, (dtype,value) in policy_data['state'].items()}
        # No policy weights reside in the standalone scorer artifact.
        self.compiled_credit.demo_policy = OpaPolicy(policy_state, opa, policy, directory/'policy.json')
        state.update({'demo_policy.'+name:value for name,value in policy_state.items()})
        self.compiled_credit.load_state_dict(state, strict=True)
        self.eval()
