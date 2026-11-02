import json
import subprocess
import sys
from pathlib import Path
import pytest
import torch
from creditlab.engine import DetachedEngine
from creditlab.routing import validate_raw_request

ROOT=Path(__file__).resolve().parents[1]


@pytest.fixture
def engine():
    torch.set_num_threads(2)
    return DetachedEngine(ROOT/'models')


def test_scorer_runs_without_loading_transformers():
    code="import sys; from creditlab.engine import DetachedEngine; e=DetachedEngine('models'); assert 'transformers' not in sys.modules; assert len(list(e.parameters()))==0"
    result=subprocess.run([sys.executable,'-c',code],cwd=ROOT,text=True,capture_output=True)
    assert result.returncode==0,result.stderr


def test_compiled_buffer_tamper_is_blocked(engine):
    x=torch.zeros((1,23),dtype=torch.int64);x[0,0]=100000;x[0,4]=35
    with torch.no_grad():engine.compiled_credit.experts[0].leaf_value[0]+=1
    with pytest.raises(RuntimeError,match='receipt mismatch'):
        engine.score_credit(x,torch.zeros_like(x,dtype=torch.bool))


def test_opa_code_tamper_is_blocked(engine,tmp_path):
    policy=engine.compiled_credit.demo_policy
    replacement=tmp_path/'credit.rego';replacement.write_text(policy.policy.read_text()+'\n# altered\n')
    policy.policy=replacement
    with pytest.raises(RuntimeError,match='unapproved policy code change'):
        policy(torch.zeros((1,23),dtype=torch.int64),torch.zeros((1,23),dtype=torch.bool),torch.tensor([0]))


def test_opa_bundle_tamper_is_blocked(engine,tmp_path):
    policy=engine.compiled_credit.demo_policy
    replacement=tmp_path/'policy.json';data=json.loads(policy.bundle.read_text());data['thresholds'][7]+=1
    replacement.write_text(json.dumps(data));policy.bundle=replacement
    with pytest.raises(RuntimeError,match='unapproved policy data change'):
        policy(torch.zeros((1,23),dtype=torch.int64),torch.zeros((1,23),dtype=torch.bool),torch.tensor([0]))


def test_opa_unavailable_fails_closed(engine):
    policy=engine.compiled_credit.demo_policy;policy.opa='/nonexistent/opa'
    with pytest.raises(FileNotFoundError):
        policy(torch.zeros((1,23),dtype=torch.int64),torch.zeros((1,23),dtype=torch.bool),torch.tensor([0]))
