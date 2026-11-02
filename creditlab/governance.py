"""Prototype evidence graph, trusted context, authority gate and sandbox ledger.

Synthetic identities/approvals are trusted server fixtures, not real IAM or PKI.
"""
import hashlib
import json
import sqlite3
from datetime import datetime, timezone
import networkx as nx


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',',':')).encode()).hexdigest()


class Governance:
    def __init__(self, component_hashes, db=':memory:', component_reader=None):
        self.hashes = component_hashes.copy()
        self.component_reader = component_reader
        self.graph = nx.DiGraph()
        for node, kind in [('credit-v1','release'),('policy-v1','policy'),('approval-v1','approval')]:
            self.graph.add_node(node,kind=kind)
        self.graph.add_edge('credit-v1','policy-v1',relation='uses')
        self.graph.add_edge('policy-v1','approval-v1',relation='approved_by')
        self.active_policy = 'policy-v1'
        self.version = 1
        self.authorities = {'analyst': {'assess'}, 'credit-officer': {'assess','record'}}
        self.db = sqlite3.connect(db)
        self.db.execute('CREATE TABLE IF NOT EXISTS decisions (id TEXT PRIMARY KEY, payload TEXT)')
        self.events = []

    def qualify(self, request, context):
        if self.component_reader and self.component_reader() != self.hashes:
            raise ValueError('COMPONENT_CHANGED')
        if context['policy'] != self.active_policy:
            raise ValueError('STALE_POLICY')
        if not self.graph.has_edge(context['policy'],'approval-v1'):
            raise ValueError('MISSING_POLICY_APPROVAL')
        if context['evidence_age_hours'] > 24:
            raise ValueError('STALE_EVIDENCE')
        if context['source'] != 'approved-bureau':
            raise ValueError('UNTRUSTED_SOURCE')
        if context['tenant'] != context['evidence_tenant']:
            raise ValueError('CROSS_TENANT_EVIDENCE')
        if 'assess' not in self.authorities.get(context['principal'],set()):
            raise ValueError('ASSESSMENT_NOT_AUTHORIZED')
        manifest = {'request_hash':digest(request),'context':context.copy(),
                    'components':self.hashes.copy(),'registry_version':self.version}
        manifest['context_hash'] = digest(manifest)
        return manifest

    def record(self, case_id, assessment, manifest, live_request, context):
        # Recheck authoritative context immediately before the simulated effect.
        fresh = self.qualify(live_request,context)
        if fresh['context_hash'] != manifest['context_hash']:
            raise ValueError('CONTEXT_CHANGED_BEFORE_WRITE')
        if 'record' not in self.authorities.get(context['principal'],set()):
            raise ValueError('WRITE_NOT_AUTHORIZED')
        if assessment.get('status') != 'OK' or assessment.get('decision',{}).get('outcome_code') == 'II':
            raise ValueError('INVALID_ASSESSMENT')
        payload = json.dumps(assessment,sort_keys=True)
        prior = self.db.execute('SELECT payload FROM decisions WHERE id=?',(case_id,)).fetchone()
        if prior:
            if prior[0] != payload:
                raise ValueError('IDEMPOTENCY_CONFLICT')
            return 'ALREADY_RECORDED'
        self.db.execute('INSERT INTO decisions VALUES (?,?)',(case_id,payload));self.db.commit()
        event = {'case_id':case_id,'timestamp':datetime.now(timezone.utc).isoformat(),
                 'context_hash':manifest['context_hash'],
                 'assessment_hash':digest(assessment),'previous_event_hash':digest(self.events[-1]) if self.events else None}
        self.events.append(event)
        self.graph.add_node(case_id,kind='assessment',**event)
        self.graph.add_edge(case_id,context['policy'],relation='governed_by')
        self.graph.add_node(manifest['request_hash'],kind='evidence',source=context['source'])
        self.graph.add_edge(case_id,manifest['request_hash'],relation='uses_evidence')
        return 'RECORDED'

    def export(self):
        return {'nodes':[{'id':node,**attrs} for node,attrs in self.graph.nodes(data=True)],
                'edges':[{'source':a,'target':b,**attrs} for a,b,attrs in self.graph.edges(data=True)],
                'events':self.events}


def valid_context():
    return {'policy':'policy-v1','source':'approved-bureau','evidence_age_hours':1,
            'tenant':'tenant-a','evidence_tenant':'tenant-a','principal':'credit-officer'}
