"""Approve a synthetic policy release without changing scorer or Qwen weights.

Changing policy deliberately changes the decision. This is not a parity case.
"""
import hashlib
import json
import sys
import tempfile
from pathlib import Path
import torch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from creditlab.engine import DetachedEngine
from creditlab.native_core import _hash_state
from creditlab.routing import validate_raw_request

torch.set_num_threads(2)
request=json.loads((ROOT/'fixtures/decline_close_to_approval.json').read_text())
error,values,missing=validate_raw_request(request);assert error is None
x=torch.tensor([values]);mask=torch.tensor([missing])
old=DetachedEngine(ROOT/'models')
with torch.inference_mode():before=old.score_credit(x,mask)
with tempfile.TemporaryDirectory() as temp:
    directory=Path(temp)
    (directory/'scorer-attribution.safetensors').symlink_to(ROOT/'models/scorer-attribution.safetensors')
    (directory/'metadata.json').write_bytes((ROOT/'models/metadata.json').read_bytes())
    data=json.loads((ROOT/'models/policy.json').read_text())
    data['policy_id']='EXPERIMENT_POLICY_v2'
    # Deliberately relax both severe delinquency clauses for this controlled change.
    data['thresholds'][7]=4;data['thresholds'][8]=7
    data['state']['thresholds'][1]=data['thresholds']
    (directory/'policy.json').write_text(json.dumps(data,indent=2))
    new=DetachedEngine(directory)
    # Synthetic registry approval of the independently versioned policy state.
    new.config.compiled_credit['compiled_sha256']=_hash_state(new.compiled_credit.state_dict())
    new.config.compiled_credit['policy_id']='EXPERIMENT_POLICY_v2'
    new.config.compiled_credit['policy_version']='EXPERIMENT_POLICY_v2'
    with torch.inference_mode():after=new.score_credit(x,mask)
    scorer_hash=hashlib.sha256((ROOT/'models/scorer-attribution.safetensors').read_bytes()).hexdigest()
    result={'case':'independently approved policy change','before_outcome':before.policy_outcome_labels[0],
            'after_outcome':after.policy_outcome_labels[0],
            'before_margin':int(before.score_fixed[0]),'after_margin':int(after.score_fixed[0]),
            'scorer_sha256_before':scorer_hash,'scorer_sha256_after':scorer_hash,
            'qwen_loaded':False,'language_weights_changed':False,
            'approval':'synthetic local registry update, not real institutional approval'}
    assert result['before_margin']==result['after_margin']
    assert result['before_outcome']!=result['after_outcome']
    (ROOT/'models/policy-v2-experiment.json').write_text(json.dumps(data,indent=2))
    (ROOT/'results/policy_release.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
