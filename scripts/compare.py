"""Paired experiment: original bundled class vs detached engine + OPA, same Qwen.

Every original route and modular route actually generates its own response.
There is no cached or replayed language output in the paired comparison.
"""
import argparse
import hashlib
import json
import os
import platform
import sys
import time
from pathlib import Path
import torch
from transformers import AutoModelForImageTextToText

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from compiled_credit_llm.checkpoint.routing import route_request
from creditlab.engine import DetachedEngine
from creditlab.writer import SharedWriter
from creditlab.governance import Governance,valid_context,digest
from creditlab.routing import route_request as separated_route


def dump(path,data):
    path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--checkpoint',required=True)
    parser.add_argument('--upstream',required=True)
    parser.add_argument('--no-language',action='store_true')
    parser.add_argument('--threads',type=int,default=4)
    args=parser.parse_args()
    torch.set_num_threads(args.threads)
    torch.manual_seed(20261102)
    checkpoint=Path(args.checkpoint)
    upstream=Path(args.upstream)
    print('Loading original bundled class',flush=True)
    model=AutoModelForImageTextToText.from_pretrained(checkpoint,trust_remote_code=True,
                local_files_only=True,dtype=torch.bfloat16).eval()
    # Keep fixed-point buffers in their declared integer/float64 dtypes.
    from safetensors import safe_open
    with safe_open(checkpoint/'model.safetensors',framework='pt',device='cpu') as f:
        for name,buffer in model.compiled_credit.named_buffers():
            value=f.get_tensor('compiled_credit.'+name)
            parent=model.compiled_credit
            parts=name.split('.')
            for part in parts[:-1]:parent=getattr(parent,part)
            parent._buffers[parts[-1]]=value
    engine=DetachedEngine(ROOT/'models')
    labels={v['raw_feature_name']:v['factual_label'] for v in model.config.compiled_credit['reason_metadata']}
    thresholds=model.compiled_credit.demo_policy.thresholds.tolist()
    writer=None if args.no_language else SharedWriter(model,checkpoint)
    pairs=[]
    def live_components():
        engine._verify_compiled_receipt()
        return {name:hashlib.sha256(path.read_bytes()).hexdigest() for name,path in {
            'scorer':ROOT/'models/scorer-attribution.safetensors',
            'policy':ROOT/'models/policy.json','rego':ROOT/'policies/credit.rego'}.items()}
    governance=Governance(live_components(),component_reader=live_components)
    out=ROOT/'results';out.mkdir(exist_ok=True)
    for path in sorted((upstream/'examples/requests').glob('*.json')):
        request=json.loads(path.read_text())
        print('Assessing',path.stem,flush=True)
        arms={}
        for name,scorer in [('bundled',model.score_credit),('separated',engine.score_credit)]:
            manifest=governance.qualify(request,valid_context()) if name=='separated' else None
            start=time.perf_counter(); before=len(writer.calls) if writer else 0
            router=route_request if name=='bundled' else separated_route
            response=router(request,scorer,writer,feature_labels=labels,thresholds=thresholds)
            arms[name]={'assessment':response.payload,'evidence':response.evidence,'prompt':response.prompt,
                        'seconds':time.perf_counter()-start,'generation_invoked':response.generation_invoked,
                        'generation':writer.calls[-1] if writer and len(writer.calls)>before else None}
            if manifest:
                arms[name]['trusted_context']=manifest
                if response.payload.get('status')=='OK' and response.payload.get('decision',{}).get('outcome_code')!='II':
                    arms[name]['sandbox_record_status']=governance.record(path.stem,response.payload,manifest,request,valid_context())
        native=arms['bundled']; separated=arms['separated']
        row={'case':path.stem,'request':request,'arms':arms,
             'evidence_identical':native['evidence']==separated['evidence'],
             'prompt_identical':native['prompt']==separated['prompt'],
             'assessment_identical':native['assessment']==separated['assessment']}
        pairs.append(row);dump(out/(path.stem+'.json'),row)
        print('Parity',row['assessment_identical'],flush=True)
    dump(out/'paired_responses.json',pairs)
    dump(out/'lineage_graph.json',governance.export())
    summary={'experiment':'controlled architecture ablation, common unadapted Qwen3.5-0.8B',
        'qwen_finetuning_reproduced':False,'seed':20261102,'thinking':False,'decoding':'greedy',
        'max_new_tokens':320,'requests':len(pairs),'language_enabled':not args.no_language,
        'evidence_matches':sum(p['evidence_identical'] for p in pairs),
        'prompt_matches':sum(p['prompt_identical'] for p in pairs),
        'full_assessment_matches':sum(p['assessment_identical'] for p in pairs),
        'generated_calls':len(writer.calls) if writer else 0,
        'verified_paragraphs':{arm:sum(p['arms'][arm]['assessment'].get('explanation_status')=='VERIFIED' for p in pairs)
                               for arm in ['bundled','separated']},
        'environment':{'python':sys.version,'torch':torch.__version__,'platform':platform.platform(),
                       'device':'cpu','threads':args.threads}}
    dump(out/'summary.json',summary);print(json.dumps(summary,indent=2),flush=True)


if __name__=='__main__': main()
