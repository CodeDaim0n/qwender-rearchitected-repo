"""Generate the evidence-based technical report from measured artifacts."""
import json
from pathlib import Path
from html import escape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,Image,KeepTogether

ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'docs/Credit_Architecture_Research_Paper.pdf'
summary=json.loads((ROOT/'results/summary.json').read_text())
pairs=json.loads((ROOT/'results/paired_responses.json').read_text())
policy=json.loads((ROOT/'results/policy_parity.json').read_text())
governance=json.loads((ROOT/'results/governance_cases.json').read_text())
release=json.loads((ROOT/'results/policy_release.json').read_text())
manifest=json.loads((ROOT/'models/model_manifest.json').read_text())
metrics=json.loads((ROOT/'models/metrics.json').read_text())
styles=getSampleStyleSheet()
navy=colors.HexColor('#132b43');teal=colors.HexColor('#126c72');muted=colors.HexColor('#536376')
styles.add(ParagraphStyle(name='BodyLab',fontName='Helvetica',fontSize=10,leading=14.6,textColor=navy,spaceAfter=9))
styles.add(ParagraphStyle(name='TitleLab',fontName='Helvetica-Bold',fontSize=31,leading=35,textColor=navy,spaceAfter=19))
styles.add(ParagraphStyle(name='H1Lab',fontName='Helvetica-Bold',fontSize=20,leading=24,textColor=navy,spaceAfter=16))
styles.add(ParagraphStyle(name='H2Lab',fontName='Helvetica-Bold',fontSize=12,leading=16,textColor=teal,spaceBefore=10,spaceAfter=7))
styles.add(ParagraphStyle(name='SmallLab',fontName='Helvetica',fontSize=8.2,leading=11,textColor=muted,spaceAfter=7))
styles.add(ParagraphStyle(name='CellLab',fontName='Helvetica',fontSize=8.4,leading=11,textColor=navy))
story=[]
def p(text,style='BodyLab'):return Paragraph(text,styles[style])
def add(text,style='BodyLab'):story.append(p(text,style))
def table(rows,widths):
    data=[[p(escape(str(v)).replace('\n','<br/>'),'CellLab') for v in row] for row in rows]
    t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e4eff0')),
                          ('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),8),
                          ('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),7),
                          ('BOTTOMPADDING',(0,0),(-1,-1),7),('LINEBELOW',(0,0),(-1,0),1,teal),
                          ('LINEBELOW',(0,1),(-1,-1),.4,colors.HexColor('#dce3e9'))]))
    story.append(t);story.append(Spacer(1,10))
def page(title):story.append(PageBreak());add(title,'H1Lab')

add('EXPERIMENTAL TECHNICAL REPORT  |  02 NOVEMBER 2026','SmallLab')
story.append(Spacer(1,25))
add('Separating the<br/>Credit Decision Stack','TitleLab')
add('A controlled Qwen3.5-0.8B comparison of bundled and independently governed credit components','H2Lab')
story.append(Spacer(1,18))
add('Abstract','H2Lab')
add('Qwenderwriter combines a fixed-point credit scorecard, exact TreeSHAP tables, a demonstration policy and a language writer in one checkpoint. We reconstruct its deterministic build and mechanically extract its score and attribution engine, externalize credit rules into Open Policy Agent (OPA), and add an evidence graph, trusted-context checks and a sandbox execution gate. Both paths use the same unadapted Qwen3.5-0.8B weights, prompts, decoding settings and seven published requests. The comparison asks whether component separation changes credit responses, and separately tests the additional workflow controls.')
table([['Measured result','Finding'],['Credit response parity',f'{summary["full_assessment_matches"]}/{summary["requests"]} complete assessment JSON responses identical'],
       ['OPA policy parity',f'{policy["dataset_rows"]:,} applications + {policy["boundary_cases"]} boundary cases; zero mismatches'],
       ['Workflow extensions',f'{sum(c["passed"] for c in governance)}/{len(governance)} expected control outcomes'],
       ['Independent policy release','Decline becomes manual review; scorer hash and raw score unchanged']], [160,339])
add('The evidence supports separation without changing the tested decisions. It does not establish better credit accuracy, lower cost, production readiness or superiority over the author\'s fine-tuned writer. The released fine-tuning stage was not reproduced.','SmallLab')
add('Non-commercial derivative experiment. Original Qwenderwriter authors: Javier Mancilla and Tomas Tagliani, SquareOne Labs. This report is an independent implementation comparison, not a peer-reviewed publication.','SmallLab')

page('1. Architecture and research question')
add('The original already separates deterministic arithmetic from language generation. Its architectural choice is to ship these components under one checkpoint identity. Our question concerns independent governance and deployment artifacts, not whether an LLM should calculate credit decisions.')
story.append(Image(str(ROOT/'docs/architecture_comparison.png'),width=499,height=420))
add('Figure 1. Left: original source design. Right: implemented component refactor. The right side is a modular Python application with a separate OPA process; it is not a deployed microservices system.','SmallLab')
add('The DataNext Christmas pattern is adapted to credit: source and version relationships determine applicable evidence; policy is evaluated explicitly; the writer receives fixed facts; an application gate separately checks authority before a sandbox write. The graph here is a minimal policy-approval and decision-lineage graph, not an enterprise ontology.','BodyLab')

page('2. What changed and what stayed fixed')
table([['Layer','Original path','Separated path'],
 ['Input contract','Upstream 23-field validator','Verbatim validator retained'],
 ['Score / attribution','Compiled checkpoint buffers','Identical tensors in independent safetensors file'],
 ['Credit policy','CheckpointDemoPolicy tensor rules','Independent feature calculations + Rego outcome rules'],
 ['Language','Qwen writer inside original class','Same Qwen callable behind writer adapter'],
 ['Explanation checks','Upstream licensed-vocabulary verifier','Same verifier, unchanged for comparison'],
 ['Recourse','Upstream candidate search, up to 3 moves','Same search, rescored through external policy'],
 ['Evidence context','Typed application and compiled receipt','Additional source, tenant, policy-approval and freshness checks'],
 ['Execution','No external write workflow','Authorization, context recheck and SQLite sandbox ledger']], [88,199,212])
add('Mechanically extracted arithmetic','H2Lab')
add('The deterministic source classes and score verification methods are extracted with Python AST tooling. The language-model superclass and constructor are removed; arithmetic methods remain unchanged. A test verifies that the detached component loads no Transformers module and instantiates no language parameters. The extraction is credited and remains under the original non-commercial licence.')
add('Policy ownership','H2Lab')
add('The 15 demonstration credit triggers and priority outcome selection are implemented in Rego. Numerical feature calculations are independent NumPy code. Thresholds, development bounds and calibration coefficients live in policy.json. Legacy score grading and its raw-margin binary threshold are retained as scorer metadata for exact response parity; they are distinct from the demonstration credit-policy outcome.')
add('A correction to the initial critique','H2Lab')
add('The original paper explicitly states that policy can be recompiled without retraining the writer. Our contribution is an independently versioned policy artifact and runtime boundary, rather than avoiding an inherently required retraining step.')

page('3. Controlled experimental method')
table([['Variable','Configuration'],['Upstream source',manifest['upstream_commit']],['Common writer','Qwen/Qwen3.5-0.8B; unadapted base weights'],
 ['Qwen revision',manifest['qwen_revision']],['Decoding','Greedy; thinking disabled; max_new_tokens = 320; seed = 20261102'],
 ['Requests','Seven JSON requests shipped by the upstream repository'],['Generation','Both arms actually generate each applicable paragraph; no response cache'],
 ['Hardware','CPU execution, four Torch threads; no GPU used'],['Policy runtime','OPA 1.22.0 via local subprocess'],
 ['Software',f'Python 3.12.14; Torch {summary["environment"]["torch"]}; Transformers 5.22.1; XGBoost 3.1.2']], [121,378])
add('Build and numerical evidence','H2Lab')
add('The original training search and frozen data splits were reused. The reconstructed scorer achieves ROC-AUC 0.777889 and KS 0.436571, matching the paper\'s rounded 0.778 and 0.437. Native-to-compiled parity has zero sign inversions over 30,000 rows and zero ROC-AUC/KS difference. TreeSHAP compilation produces 344,106 regions and zero fixed-point local-accuracy residual.')
add('A compatibility repair restored feature names and integer types omitted from the saved booster by the installed XGBoost/pandas combination. Tree parameters were not changed. Exact source, model and OPA identities are recorded in models/model_manifest.json, together with dependency versions and build logs.')
add('The policy comparison uses the same compiled margins in both arms, with each of the ten returned tensor fields compared exactly: calculations, flags, risk indices and one-hot bands, triggers, outcome indices and one-hot outcomes, final reasons, raw model probability and frozen calibrated probability.')
add('The author\'s LoRA-adapted writer and its reported 98.1% verification rate are outside this reproduction. Substituting the same base writer on both sides is a controlled architecture ablation, not a reproduction of that released writer.','SmallLab')

page('4. Paired credit responses')
rows=[['Same test request','Outcome / probability','Paragraph','JSON parity']]
for row in pairs:
    a=row['arms']['bundled']['assessment']
    outcome=a.get('decision',{}).get('outcome_code',a.get('refusal_class','REFUSE'))
    probability=a.get('model',{}).get('probability_pct','-')
    status=a.get('explanation_status','NO LM CALL').replace('WITHHELD_BY_VERIFIER','WITHHELD')
    rows.append([row['case'].replace('_',' '),outcome+' / '+probability,status,'Identical' if row['assessment_identical'] else 'Different'])
table(rows,[189,135,96,79])
add(f'All {summary["requests"]} evidence strings, prompts and complete assessment JSON objects match. There were {summary["generated_calls"]} actual writer calls: five applicable requests per arm; the two malformed requests never invoke Qwen. Three of five generated paragraphs pass verification in each arm. Two are withheld in each arm, while the deterministic assessment remains available.')
add('Why an invalid-input case still invokes the writer','H2Lab')
add('The file named invalid_input_missing_field uses an explicit null, which the upstream router accepts as a policy input. It becomes outcome II (invalid input) rather than a malformed-envelope refusal. This behavior is preserved, including the attempted and withheld paragraph. A physically absent required key is a different malformed-request class.')
add('Latency interpretation','H2Lab')
rows=[['Case','Bundled seconds','Separated seconds']]
for row in pairs:
    if row['arms']['bundled']['generation_invoked']:
        rows.append([row['case'].replace('_',' '),f'{row["arms"]["bundled"]["seconds"]:.2f}',f'{row["arms"]["separated"]["seconds"]:.2f}'])
table(rows,[299,100,100])
add('These are single observations in fixed arm order, including generation and, on the separated path, context qualification. They are not randomized performance benchmarks. OPA process startup, hashes and graph checks add work; no speed or cost advantage is claimed.','SmallLab')

page('5. Actual language responses')
add('The paragraphs below were generated independently on each path and matched exactly. They are raw experimental wording, retained without editorial correction. Full requests, prompts, raw generations, verifier results and JSON responses are in results/paired_responses.json.','BodyLab')
for case in ['approval_with_controls','decline_close_to_approval','standard_approval']:
    row=next(r for r in pairs if r['case']==case)
    a=row['arms']['bundled']['assessment']
    add(case.replace('_',' ').title()+' | '+a['model']['probability_pct'],'H2Lab')
    add(escape(a['explanation']))
add('Verification is limited to the upstream gate\'s checks. Matching allowed numbers, labels and rule phrases does not establish comprehensive semantic correctness or suitability for customer communications.','SmallLab')

page('6. Enterprise workflow extension tests')
add('These cases use the actual approval-with-controls credit request and separated assessment. They test additional workflow controls. The upstream assessment API does not implement these controls or a write tool, so its capability is recorded as not implemented; it is not counted as making unsafe writes.')
rows=[['Scenario','Separated response','Result']]
for row in governance:
    rows.append([row['case'].replace('_',' '),row['separated_response'].replace('_',' '),'Pass' if row['passed'] else 'Fail'])
table(rows,[164,290,45])
add('Execution checks','H2Lab')
add('Final verification also passes all 43 original repository tests (plus six subtests) and all 17 added component/governance tests. Original artifact tests run with offline model loading and explicit Torch thread limits; raw test logs are included.','SmallLab')
add('Trusted context binds the request hash, current policy, component hashes and registry version. Before a sandbox write the application qualifies the live context again. A changed request, registry version or live component identity is rejected. Role checks distinguish assessment permission from recording permission. A SQLite primary key makes identical retries idempotent and conflicting retries fail.')
add('The approval graph, source labels, evidence ages, tenant identities and role registry are synthetic trusted fixtures. They are not an implemented bank IAM, live bureau integration, signed policy registry or independently verified source system.','SmallLab')

page('7. Policy releases, strengths and costs')
add('An independent release experiment','H2Lab')
add('A second synthetic policy deliberately relaxes the two severe-delinquency thresholds. For the published decline example, the outcome changes from DEMO_DECLINE to MANUAL_REVIEW while the raw fixed-point margin remains 842436674 (69.9% raw model probability). The scorer/attribution artifact SHA-256 remains identical, and no Qwen model is loaded. The release changes policy behavior; it is intentionally outside the parity comparison.')
table([['Claim','Evidence and qualification'],
 ['Independent policy lifecycle','Separate Rego/data artifact; policy-only outcome change measured. Synthetic local approval, not institutional approval.'],
 ['Independent scoring','Detached runtime instantiates no Qwen weights and loads no Transformers module.'],
 ['Evidence applicability','Minimal graph and source/version/freshness/tenant checks reject declared invalid contexts.'],
 ['Execution control','Application gate rechecks context and permissions before a sandbox record.'],
 ['Audit reconstruction','Decision nodes link policy and evidence; events include timestamp, content hashes and previous-event hash.'],
 ['Costs of separation','More interfaces, deployment identities, failure modes, policy-code maintenance and orchestration checks. OPA outages fail closed.']], [132,367])
add('Neither packaging choice is universally superior','H2Lab')
add('A single checkpoint offers convenient offline distribution, a compact release identity and fewer operational components. Separate artifacts support different owners and update cycles but require a coherent release manifest and integration tests. A graph or an OPA process alone cannot supply trustworthy evidence, resolve ambiguous policy or establish lawful lending behavior.')
add('Our demonstrated strength is preserving bounded assessment behavior while making governance boundaries explicit and independently testable. We did not demonstrate better underwriting, cheaper inference, higher explanation quality or production-scale reliability.')

page('8. Limits, reproducibility and references')
add('Limits that affect interpretation','H2Lab')
add('Seven paired requests are a small regression set. The 30,000-row result establishes equivalence of this policy implementation on the benchmark, not universal equivalence on all signed-64-bit inputs. Large extreme inputs may inherit upstream arithmetic overflow risks. The 29 boundary cases cover selected risk, delinquency, utilization and null boundaries, not every combination.')
add('The writer is unadapted, English only, and has five generated test requests per arm. We retained the original explanation gate, including its known number-to-label semantic gap. We retained the bounded recourse search and its non-causal interpretation. No temporal validation, fairness assessment, regulatory certification, live lending action, distributed deployment or production access isolation was performed.')
add('The event graph is in memory and its hashes are not signatures. The SQLite ledger can be persisted, but this prototype does not provide a production immutable audit store or multi-party approvals. Evidence freshness and identity assertions must come from authenticated enterprise integrations before real deployment.')
add('Reproduction and deliverables','H2Lab')
add('The repository contains the rewritten components, native XGBoost model weights, policy bundles, pinned model identities, seven fixtures, exact response logs, policy parity output, control cases, tests, report and editable architecture diagrams. The larger model bundle contains the rebuilt original-layout base checkpoint plus the detached scorer/attribution artifact. The Qwen weights are a common base, not the author\'s fine-tuned release.')
add('Run scripts/reproduce.py to fetch the pinned upstream source and official Qwen snapshot, rebuild both deterministic layouts, run the paired generation and execute the control tests. A local base-model directory can be supplied to avoid another download. scripts/demo.py runs the separated credit workflow without Qwen when only structured output is needed.')
add('Primary references','H2Lab')
references=[
 '1. Mancilla, J.; Tagliani, T. (2026). Qwenderwriter. Original paper, sections 4-7. github.com/maximer-v/qwenderwriter/blob/main/paper/Qwenderwriter.pdf',
 '2. Qwenderwriter source, commit '+manifest['upstream_commit']+'. Original architecture, model card, policy, code and licence. github.com/maximer-v/qwenderwriter',
 '3. Qwen team. Qwen3.5-0.8B official model and Apache-2.0 licence. huggingface.co/Qwen/Qwen3.5-0.8B; pinned revision in model manifest.',
 '4. Open Policy Agent. Official documentation: decision-making is separated from enforcement; structured inputs and outputs. openpolicyagent.org/docs. Runtime version 1.22.0.',
 '5. Local evidence: results/summary.json; paired_responses.json; policy_parity.json; governance_cases.json; policy_release.json; lineage_graph.json; build and test logs.'
]
for r in references:add(escape(r),'SmallLab')

def footer(canvas,doc):
    canvas.setStrokeColor(colors.HexColor('#d9e2e8'));canvas.line(48,42,547,42)
    canvas.setFont('Helvetica',8);canvas.setFillColor(muted)
    canvas.drawString(48,28,'CREDIT ARCHITECTURE LAB | Non-commercial experimental evidence')
    canvas.drawRightString(547,28,str(doc.page))
doc=SimpleDocTemplate(str(out),pagesize=A4,rightMargin=48,leftMargin=48,topMargin=47,bottomMargin=57,
                      title='Separating the Credit Decision Stack',author='Credit Architecture Lab')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print(out)
