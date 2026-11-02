"""Extract identical deterministic tensors into separately deployable artifacts."""
import hashlib
import json
import sys
from pathlib import Path
import torch
from safetensors import safe_open
from safetensors.torch import save_file

ROOT = Path(__file__).resolve().parents[1]
checkpoint = Path(sys.argv[1])
config = json.loads((checkpoint/'config.json').read_text())
metadata = config['compiled_credit']
state = {}
with safe_open(checkpoint/'model.safetensors', framework='pt', device='cpu') as f:
    for key in f.keys():
        if key.startswith('compiled_credit.'):
            state[key[len('compiled_credit.'):]] = f.get_tensor(key)
policy = {key[len('demo_policy.'):]:value for key,value in state.items() if key.startswith('demo_policy.')}
scorer = {key:value for key,value in state.items() if not key.startswith('demo_policy.')}
save_file(scorer, str(ROOT/'models/scorer-attribution.safetensors'))
(ROOT/'models/metadata.json').write_text(json.dumps(metadata,indent=2))
policy_data = {'policy_id':metadata['policy_id'], 'thresholds':policy['thresholds'].tolist(),
               'state':{key:[str(value.dtype).split('.')[1],value.tolist()] for key,value in policy.items()}}
(ROOT/'models/policy.json').write_text(json.dumps(policy_data,indent=2))
identity = {'source_checkpoint':str(checkpoint),'source_compiled_sha256':metadata['compiled_sha256'],
            'scorer_attribution_file_sha256':hashlib.sha256((ROOT/'models/scorer-attribution.safetensors').read_bytes()).hexdigest(),
            'qwen_weights_changed':False,'policy_execution':'external OPA 1.22.0'}
(ROOT/'models/extraction.json').write_text(json.dumps(identity,indent=2))
print(json.dumps(identity,indent=2))
