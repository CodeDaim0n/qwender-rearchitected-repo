"""Reusable credit orchestration; each boundary has a separate owner/artifact."""
import hashlib
from pathlib import Path
from .engine import DetachedEngine
from .governance import Governance,valid_context
from .routing import route_request


class CreditWorkflow:
    def __init__(self, models, writer=None, ledger=':memory:'):
        self.models=Path(models)
        self.engine=DetachedEngine(self.models)
        self.writer=writer
        self.governance=Governance(self.live_components(),db=ledger,component_reader=self.live_components)

    def live_components(self):
        self.engine._verify_compiled_receipt()
        paths={'scorer':self.models/'scorer-attribution.safetensors',
               'policy':self.models/'policy.json',
               'rego':self.engine.compiled_credit.demo_policy.policy}
        return {name:hashlib.sha256(path.read_bytes()).hexdigest() for name,path in paths.items()}

    def assess(self,request,context,case_id,record=False):
        manifest=self.governance.qualify(request,context)
        metadata=self.engine.config.compiled_credit
        labels={v['raw_feature_name']:v['factual_label'] for v in metadata['reason_metadata']}
        thresholds=self.engine.compiled_credit.demo_policy.thresholds.tolist()
        result=route_request(request,self.engine.score_credit,self.writer,feature_labels=labels,thresholds=thresholds)
        output={'assessment':result.payload,'trusted_context':manifest,'record_status':'NOT_REQUESTED'}
        if record:
            output['record_status']=self.governance.record(case_id,result.payload,manifest,request,context)
        return output
