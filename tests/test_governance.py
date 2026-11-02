import copy
import pytest
from creditlab.governance import Governance,valid_context


@pytest.mark.parametrize('change,reason',[
    ({'policy':'policy-old'},'STALE_POLICY'),
    ({'evidence_age_hours':25},'STALE_EVIDENCE'),
    ({'source':'unapproved'},'UNTRUSTED_SOURCE'),
    ({'evidence_tenant':'tenant-b'},'CROSS_TENANT_EVIDENCE'),
    ({'principal':'outsider'},'ASSESSMENT_NOT_AUTHORIZED'),
])
def test_context_refusals(change,reason):
    g=Governance({'score':'s','policy':'p'});c=valid_context();c.update(change)
    with pytest.raises(ValueError,match=reason):g.qualify({'credit':1},c)


def test_missing_approval():
    g=Governance({});g.graph.remove_edge('policy-v1','approval-v1')
    with pytest.raises(ValueError,match='MISSING_POLICY_APPROVAL'):g.qualify({},valid_context())


def test_write_authority():
    g=Governance({});c=valid_context();c['principal']='analyst';m=g.qualify({},c)
    with pytest.raises(ValueError,match='WRITE_NOT_AUTHORIZED'):g.record('a',{'status':'OK'},m,{},c)


def test_changed_evidence_at_write():
    g=Governance({});c=valid_context();m=g.qualify({'a':1},c)
    with pytest.raises(ValueError,match='CONTEXT_CHANGED_BEFORE_WRITE'):g.record('a',{'status':'OK'},m,{'a':2},c)


def test_policy_release_during_assessment():
    g=Governance({});c=valid_context();m=g.qualify({},c);g.version+=1
    with pytest.raises(ValueError,match='CONTEXT_CHANGED_BEFORE_WRITE'):g.record('a',{'status':'OK'},m,{},c)


def test_idempotency_and_conflict():
    g=Governance({});c=valid_context();m=g.qualify({},c)
    assert g.record('a',{'status':'OK'},m,{},c)=='RECORDED'
    assert g.record('a',{'status':'OK'},m,{},c)=='ALREADY_RECORDED'
    with pytest.raises(ValueError,match='IDEMPOTENCY_CONFLICT'):g.record('a',{'status':'OK','changed':1},m,{},c)
    assert g.db.execute('SELECT COUNT(*) FROM decisions').fetchone()[0]==1


def test_invalid_assessment_blocked():
    g=Governance({});c=valid_context();m=g.qualify({},c)
    with pytest.raises(ValueError,match='INVALID_ASSESSMENT'):g.record('a',{'status':'REFUSE'},m,{},c)


def test_component_changed_before_write():
    live={'score':'original'}
    g=Governance(live,component_reader=lambda:live.copy());c=valid_context();m=g.qualify({},c)
    live['score']='tampered'
    with pytest.raises(ValueError,match='COMPONENT_CHANGED'):g.record('a',{'status':'OK'},m,{},c)
