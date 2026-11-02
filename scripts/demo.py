"""Run the modular credit process without loading Qwen; optionally attach it."""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import torch
from creditlab.workflow import CreditWorkflow
from creditlab.governance import valid_context

p=argparse.ArgumentParser();p.add_argument('--request',default=str(ROOT/'fixtures/approval_with_controls.json'))
p.add_argument('--record',action='store_true');p.add_argument('--checkpoint')
args=p.parse_args();torch.set_num_threads(4)
writer=None
if args.checkpoint:
    from transformers import AutoModelForImageTextToText
    from creditlab.writer import SharedWriter
    lm=AutoModelForImageTextToText.from_pretrained(args.checkpoint,trust_remote_code=True,local_files_only=True,dtype=torch.bfloat16).eval()
    writer=SharedWriter(lm,args.checkpoint)
workflow=CreditWorkflow(ROOT/'models',writer)
request=json.loads(Path(args.request).read_text())
print(json.dumps(workflow.assess(request,valid_context(),'demo-application',args.record),indent=2))
