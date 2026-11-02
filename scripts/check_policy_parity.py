"""Independent OPA versus original tensor policy on 30,000 rows and boundaries."""
import argparse
import json
import sys
import time
from pathlib import Path
import numpy as np
import pandas as pd
import torch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from creditlab.engine import DetachedEngine
from creditlab.native_core import CheckpointDemoPolicy

parser=argparse.ArgumentParser();parser.add_argument('--csv',required=True)
args=parser.parse_args();torch.set_num_threads(4)
engine=DetachedEngine(ROOT/'models')
opa=engine.compiled_credit.demo_policy
original=CheckpointDemoPolicy(23);original.load_state_dict(opa.state_dict())
names=engine.config.compiled_credit['feature_names']
features=torch.tensor(pd.read_csv(args.csv,skiprows=1)[names].to_numpy(dtype=np.int64))
with torch.inference_mode():
    margins=torch.cat([engine.compiled_credit(x,torch.zeros_like(x,dtype=torch.bool)).score
                       for x in features.split(256)])

checks=[]
started=time.perf_counter()
for start in range(0,len(features),1000):
    x=features[start:start+1000];missing=torch.zeros_like(x,dtype=torch.bool);m=margins[start:start+1000]
    with torch.inference_mode():a=original(x,missing,m);b=opa(x,missing,m)
    mismatches={field:int((getattr(a,field)!=getattr(b,field)).sum()) for field in a._fields}
    if any(mismatches.values()):raise AssertionError(mismatches)
    checks.append({'start':start,'rows':len(x),'mismatches':mismatches})
    print('Policy parity',start+len(x),flush=True)

# Exercise every risk-band boundary, hard/soft policy thresholds and null flags.
base=features[0].clone()
base[0]=100000;base[1:5]=torch.tensor([1,2,1,35]);base[5:11]=-1
base[11:17]=10000;base[17:23]=2000
cases=[]
for margin in [-1000000001,-1000000000,-999999999,-1,0,1,999999999,1000000000,1000000001]:
    cases.append((base.clone(),torch.zeros(23,dtype=torch.bool),margin))
for severity in [1,2,3,4]:
    row=base.clone();row[5]=severity;cases.append((row,torch.zeros(23,dtype=torch.bool),-2000000000))
for bill in [89999,90000,90001,149999,150000,150001]:
    row=base.clone();row[11]=bill;row[5]=1;cases.append((row,torch.zeros(23,dtype=torch.bool),-2000000000))
for count in [1,2,3,4,5]:
    row=base.clone();row[5:5+count]=1;cases.append((row,torch.zeros(23,dtype=torch.bool),-2000000000))
for idx in [0,1,5,11,17]:
    missing=torch.zeros(23,dtype=torch.bool);missing[idx]=True
    row=base.clone();row[idx]=0;cases.append((row,missing,-2000000000))
x=torch.stack([v[0] for v in cases]);missing=torch.stack([v[1] for v in cases]);m=torch.tensor([v[2] for v in cases])
with torch.inference_mode():a=original(x,missing,m);b=opa(x,missing,m)
boundary={field:int((getattr(a,field)!=getattr(b,field)).sum()) for field in a._fields}
assert not any(boundary.values()),boundary
summary={'dataset_rows':len(features),'boundary_cases':len(cases),'mismatches':0,
         'fields_compared':list(a._fields),'seconds':time.perf_counter()-started,
         'opa_version':'1.22.0','batches':checks,'boundary_mismatches':boundary}
(ROOT/'results/policy_parity.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k!='batches'},indent=2))
