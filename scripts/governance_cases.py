"""Credit workflow extension cases. Baseline capability is NOT_IMPLEMENTED.

This is not a baseline unsafe-write experiment: upstream has no write tool.
"""
import copy
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from creditlab.governance import Governance,valid_context

paired=json.loads((ROOT/'results/approval_with_controls.json').read_text())
assessment=paired['arms']['separated']['assessment']
request=paired['request']
scenarios=[
    ('valid_record',{},None,'RECORDED'),
    ('stale_policy',{'policy':'policy-old'},None,'STALE_POLICY'),
    ('stale_evidence',{'evidence_age_hours':25},None,'STALE_EVIDENCE'),
    ('untrusted_source',{'source':'unknown'},None,'UNTRUSTED_SOURCE'),
    ('wrong_tenant',{'evidence_tenant':'tenant-b'},None,'CROSS_TENANT_EVIDENCE'),
    ('unprivileged_principal',{'principal':'outsider'},None,'ASSESSMENT_NOT_AUTHORIZED'),
    ('assess_only_principal',{'principal':'analyst'},None,'WRITE_NOT_AUTHORIZED'),
    ('missing_approval',{},'remove_approval','MISSING_POLICY_APPROVAL'),
    ('changed_request',{},'change_request','CONTEXT_CHANGED_BEFORE_WRITE'),
    ('policy_changed_in_flight',{},'change_registry','CONTEXT_CHANGED_BEFORE_WRITE'),
    ('retry_same_write',{},'retry','ALREADY_RECORDED'),
    ('retry_conflicting_write',{},'conflict','IDEMPOTENCY_CONFLICT'),
]
results=[]
for name,change,mutation,expected in scenarios:
    g=Governance({'score':'pinned-score','policy':'pinned-policy','writer':'same-qwen'})
    c=valid_context();c.update(change);live=copy.deepcopy(request)
    if mutation=='remove_approval':g.graph.remove_edge('policy-v1','approval-v1')
    try:
        qualified=g.qualify(request,c)
        if mutation=='change_request':live['modified']=True
        if mutation=='change_registry':g.version+=1
        response=g.record('synthetic-case-001',assessment,qualified,live,c)
        if mutation in ['retry','conflict']:
            second=copy.deepcopy(assessment)
            if mutation=='conflict':second['changed']=True
            response=g.record('synthetic-case-001',second,qualified,live,c)
    except ValueError as e:response=str(e)
    row={'case':name,'context':c,'mutation':mutation,'expected':expected,
         'separated_response':response,'passed':response==expected,
         'baseline_control_response':'NOT_IMPLEMENTED_IN_UPSTREAM_ASSESSMENT_API',
         'sandbox_records':g.db.execute('SELECT COUNT(*) FROM decisions').fetchone()[0]}
    results.append(row)
    if name=='valid_record':(ROOT/'results/workflow_lineage_graph.json').write_text(json.dumps(g.export(),indent=2))
(ROOT/'results/governance_cases.json').write_text(json.dumps(results,indent=2)+'\n')
print(f'{sum(r["passed"] for r in results)}/{len(results)} workflow extension cases passed')
assert all(r['passed'] for r in results)
