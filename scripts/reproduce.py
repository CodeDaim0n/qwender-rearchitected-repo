"""Rebuild the experiment with pinned source, model revision and OPA binary.

Requires Python dependencies from requirements.txt; downloads ~1.8GB of Qwen
weights unless --base points to an existing snapshot. No LoRA training is run.
"""
import argparse,hashlib,json,os,subprocess,sys,urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PIN='8d6015075d421eb1102db6dcc48a1caa62f84828'
QWEN='2fc06364715b967f1860aea9cf38778875588b17'
p=argparse.ArgumentParser();p.add_argument('--base');p.add_argument('--no-language',action='store_true')
args=p.parse_args();source=ROOT/'vendor/qwenderwriter';source.parent.mkdir(exist_ok=True)
def run(argv,log):
    print('Running',log,flush=True)
    env=os.environ.copy();env['OMP_NUM_THREADS']='4';env['TOKENIZERS_PARALLELISM']='false'
    env['HF_HUB_OFFLINE']='1';env['TRANSFORMERS_OFFLINE']='1'
    env['PYTHONPATH']=str(source)+os.pathsep+str(ROOT)
    with (ROOT/'results'/log).open('w') as f:subprocess.run(argv,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
if not source.exists():
    subprocess.run(['git','clone','https://github.com/maximer-v/qwenderwriter.git',str(source)],check=True)
subprocess.run(['git','-C',str(source),'checkout',PIN],check=True)
opa=ROOT/'bin/opa';opa.parent.mkdir(exist_ok=True)
if not opa.exists():
    urllib.request.urlretrieve('https://openpolicyagent.org/downloads/v1.22.0/opa_linux_amd64_static',opa)
    opa.chmod(0o755)
provenance=json.loads((ROOT/'models/model_manifest.json').read_text())
assert hashlib.sha256(opa.read_bytes()).hexdigest()==provenance['opa_binary_sha256'],'OPA binary identity mismatch'
run([sys.executable,str(source/'scripts/03_train_scorer.py'),'--threads','4'],'train.log')
# Newer pandas can omit XGBoost column metadata. Restore names/types only;
# training always used the declared, ordered 23-column DataFrame.
sys.path.insert(0,str(source))
import xgboost as xgb
from compiled_credit_llm.data.uci import FEATURE_NAMES
model_json=source/'artifacts/scorer/xgboost_model.json'
booster=xgb.Booster();booster.load_model(model_json)
if not booster.feature_names:
    booster.feature_names=list(FEATURE_NAMES);booster.feature_types=['int']*23;booster.save_model(model_json)
for script in ['04_compile_scorer.py','05_compile_treeshap.py','06_compile_policy.py']:
    run([sys.executable,str(source/'scripts'/script)],script+'.log')
base=args.base
if not base:
    from huggingface_hub import snapshot_download
    base=snapshot_download('Qwen/Qwen3.5-0.8B',revision=QWEN,
                           allow_patterns=['*.json','*.safetensors','*.jinja','*.txt'])
run([sys.executable,str(source/'scripts/07_build_base_checkpoint.py'),'--base',base],'package.log')
checkpoint=source/'artifacts/checkpoints/CompiledCreditLLM-0.8B-UCI-base'
run([sys.executable,str(ROOT/'scripts/extract_native_core.py'),str(source)],'extract-core.log')
run([sys.executable,str(ROOT/'scripts/extract_components.py'),str(checkpoint)],'extract-components.log')
run([sys.executable,str(ROOT/'scripts/check_policy_parity.py'),'--csv',str(source/'data/default_of_credit_card_clients.csv')],'policy-parity.log')
command=[sys.executable,str(ROOT/'scripts/compare.py'),'--checkpoint',str(checkpoint),'--upstream',str(source)]
if args.no_language:command.append('--no-language')
run(command,'paired-run.log')
run([sys.executable,str(ROOT/'scripts/governance_cases.py')],'governance-cases.log')
run([sys.executable,str(ROOT/'scripts/policy_release_experiment.py')],'policy-release.log')
run([sys.executable,'-m','pytest','tests','-q'],'modular-tests.log')
run([sys.executable,'-c','import torch,pytest; torch.set_num_threads(2); raise SystemExit(pytest.main(['+repr(str(source/'tests'))+', "-q"]))'],'upstream-tests.log')
print('Complete. Inspect results/summary.json and results/paired_responses.json.')
