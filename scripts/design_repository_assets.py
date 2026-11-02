"""Generate exact, editable repository figures from the measured evidence.

SVGs have no external assets or fonts. Run with --render to also produce PNGs
using CairoSVG (optional documentation dependency).
"""
import argparse
from pathlib import Path
from html import escape
import json

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'docs/assets'
ASSETS.mkdir(exist_ok=True)
INK='#152B3C'; MUTED='#526777'; TEAL='#007F78'; CORAL='#B95138'
LINE='#CFDCE3'; PAPER='#F4F7F9'; DARK='#102A39'; WHITE='#FFFFFF'

class SVG:
    def __init__(self,w,h,title,description,bg=WHITE):
        self.w,self.h=w,h
        self.s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">',
                f'<title id="title">{escape(title)}</title><desc id="desc">{escape(description)}</desc>',
                '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#708692"/></marker></defs>',
                f'<rect width="{w}" height="{h}" rx="24" fill="{bg}"/>']
    def rect(self,x,y,w,h,fill=WHITE,stroke=LINE,r=14):
        self.s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}"/>')
    def text(self,x,y,text,size=24,color=INK,weight=400,anchor='start',family='Arial, Helvetica, sans-serif',spacing=None):
        extra=f' letter-spacing="{spacing}"' if spacing is not None else ''
        self.s.append(f'<text x="{x}" y="{y}" fill="{color}" font-family="{family}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}"{extra}>{escape(str(text))}</text>')
    def lines(self,x,y,lines,size=24,color=INK,weight=400,leading=32):
        for i,line in enumerate(lines):self.text(x,y+i*leading,line,size,color,weight)
    def line(self,x1,y1,x2,y2,color=LINE,width=1.5):
        self.s.append(f'<path d="M{x1} {y1} L{x2} {y2}" fill="none" stroke="{color}" stroke-width="{width}"/>')
    def arrow(self,points,label=None,lx=None,ly=None,dashed=False):
        d='M'+' L'.join(f'{x} {y}' for x,y in points)
        dash=' stroke-dasharray="6 6"' if dashed else ''
        self.s.append(f'<path d="{d}" fill="none" stroke="#708692" stroke-width="2" marker-end="url(#arrow)"{dash}/>')
        if label:self.text(lx,ly,label,18,MUTED)
    def node(self,x,y,w,h,number,title,body,accent=TEAL,fill=WHITE):
        self.rect(x,y,w,h,fill)
        self.rect(x+18,y+18,34,30,accent,accent,7)
        self.text(x+35,y+39,number,17,WHITE,700,'middle')
        self.text(x+66,y+40,title,25,INK,700)
        self.lines(x+22,y+78,body,20,MUTED,leading=27)
    def save(self,path):
        Path(path).write_text('\n'.join(self.s+['</svg>'])+'\n')

def hero():
    run=json.loads((ROOT/'results/summary.json').read_text())
    parity=json.loads((ROOT/'results/policy_parity.json').read_text())
    controls=json.loads((ROOT/'results/governance_cases.json').read_text())
    tests=json.loads((ROOT/'results/test_summary.json').read_text())
    s=SVG(1600,610,'Qwender, rearchitected','Independent credit components, identical tested responses. Seven of seven response matches; 30,029 policy parity inputs; twelve workflow scenarios; sixty passing tests.',DARK)
    s.text(64,67,'QWENDER / REARCHITECTED',19,'#90B9C5',700,spacing=3)
    s.lines(64,159,['Separate the controls.','Preserve the decision.'],68,WHITE,700,leading=78)
    s.lines(67,310,['A credit architecture with an exact scorecard, external policy,',
                    'a bounded Qwen writer and an independent execution gate.'],25,'#C0D4DD',leading=37)
    for y,tag,title,detail,color in [
        (72,'01','SCORE + ATTRIBUTION','Fixed-point tensors · independent artifact','#40C5B5'),
        (196,'02','CREDIT POLICY','Rego rules + versioned policy data','#40C5B5'),
        (320,'03','LANGUAGE WRITER','Same Qwen3.5-0.8B · verified paragraph','#FFAD8D')]:
        s.rect(1050,y,486,102,'#183746','#345463',13)
        s.text(1074,y+35,tag,18,color,700)
        s.text(1124,y+36,title,21,WHITE,700)
        s.text(1124,y+70,detail,17,'#BBD2DA')
    s.line(64,461,1536,461,'#3A5665')
    stats=[(f'{run["full_assessment_matches"]} / {run["requests"]}','identical credit responses'),
           (f'{parity["dataset_rows"]+parity["boundary_cases"]:,}','policy parity inputs'),
           (f'{sum(c["passed"] for c in controls)} / {len(controls)}','workflow control scenarios'),
           (str(tests['upstream_tests_passed']+tests['added_tests_passed']),'passing repository tests')]
    for i,(value,label) in enumerate(stats):
        x=64+i*380
        s.text(x,526,value,41,WHITE,700)
        s.text(x,564,label,21,'#ABC8D3')
    s.save(ASSETS/'hero.svg')

def architecture():
    s=SVG(1600,1230,'The implemented credit architecture','A trusted-context boundary precedes exact scoring and external OPA policy. Structured evidence feeds an optional Qwen writer and its verifier, then a separate gate authorizes a sandbox record and linked lineage.')
    s.text(52,62,'THE IMPLEMENTED ARCHITECTURE',18,TEAL,700,spacing=2)
    s.text(52,111,'Every decision has evidence. Every action has a gate.',38,INK,700)
    s.text(52,152,'Real component boundaries; synthetic authority and source assertions in this research prototype.',22,MUTED)
    bands=[(186,190,'A','QUALIFY THE CONTEXT'),(396,338,'B','ASSESS THE CREDIT'),(754,196,'C','EXPLAIN THE RESULT'),(970,202,'D','AUTHORIZE THE EFFECT')]
    for y,h,tag,label in bands:
        s.rect(32,y,1536,h,PAPER,PAPER,18)
        s.text(54,y+33,tag,18,TEAL,700);s.text(84,y+33,label,17,MUTED,700,spacing=1)
    s.node(58,241,430,108,'01','Evidence / approval graph',['Source · tenant · active policy · approval'])
    s.node(570,241,456,108,'02','Trusted-context manifest',['Request + component hashes + version'])
    s.node(1106,241,412,108,'03','Typed request validation',['23 fields · integer / null contract'])
    s.arrow([(488,293),(570,293)]);s.arrow([(1026,293),(1106,293)])
    s.node(58,456,430,131,'04','Score + attribution',['Exact tree margin + TreeSHAP', 'No language weights loaded'])
    s.node(570,456,456,131,'05','Feature calculations',['Independent NumPy calculations', 'Utilization · delinquency · payments'])
    s.node(1106,456,412,131,'06','OPA credit policy',['Priority rules in Rego', 'Versioned thresholds and bounds'])
    s.arrow([(1312,349),(1312,385),(440,385),(440,456)])
    s.arrow([(488,521),(570,521)]);s.arrow([(1026,521),(1106,521)])
    s.text(799,443,'fixed margin + raw values',17,MUTED,anchor='middle')
    s.rect(58,632,1460,75,WHITE,LINE,12)
    s.text(83,664,'07  EVIDENCE + RECOURSE',21,TEAL,700)
    s.text(83,692,'Decision · controlling rules · drivers · calculations · bounded recourse · reproducible receipt',21,MUTED)
    s.arrow([(1312,587),(1312,632)])
    s.node(58,808,645,112,'08','Qwen writer + explanation verifier',['Same prompt and base weights in the paired experiment', 'Verifier rejection withholds the paragraph, not the assessment'],CORAL)
    s.node(835,808,683,112,'09','Assembled assessment',['Structured JSON + receipt; optional verified paragraph', 'Language generation can be disabled'],CORAL)
    s.arrow([(510,707),(510,808)],'facts',530,764)
    s.arrow([(1312,707),(1312,808)],'structured assessment',1060,764)
    s.arrow([(703,864),(835,864)],'optional text',713,846)
    s.node(58,1024,468,118,'10','Execution gate',['Recheck live context + component identity', 'Require a separate recording permission'],CORAL)
    s.node(606,1024,422,118,'11','Sandbox ledger',['SQLite idempotency key', 'Same retry = no duplicate record'])
    s.node(1106,1024,412,118,'12','Linked lineage',['Policy + evidence + decision links', 'Timestamped, hash-linked events'])
    s.arrow([(1176,920),(1176,960),(470,960),(470,1024)])
    s.arrow([(526,1083),(606,1083)]);s.arrow([(1028,1083),(1106,1083)])
    s.text(52,1191,'Deployment scope: Python components + OPA subprocess. No live lending system, production IAM or immutable audit-store claim.',19,MUTED)
    s.save(ASSETS/'architecture.svg')

def example():
    rows=json.loads((ROOT/'results/paired_responses.json').read_text())
    r=next(row for row in rows if row['case']=='decline_close_to_approval')
    a=r['arms']['separated']['assessment']
    assert r['assessment_identical'] and a['explanation_status']=='VERIFIED'
    assert a['recourse']['next_better']['moves_needed']==1
    s=SVG(1600,750,'One application, two architectures, the same measured response','The published decline fixture produces the same complete assessment in the bundled and separated arms: decline, 69.9 percent model probability, elevated risk, severe delinquency, and one-move recourse.')
    s.text(52,60,'ONE APPLICATION. TWO ARCHITECTURES.',18,TEAL,700,spacing=2)
    s.text(52,109,'The output is equivalent. The control boundaries are different.',36,INK,700)
    s.rect(48,151,610,427,DARK,DARK,18)
    s.text(76,198,'REQUEST',19,'#8DBAC4',700,spacing=2)
    lines=['{','  "action": "ASSESS",','  "credit": {','    "LIMIT_BAL": 200000,','    "AGE": 39,','    "PAY_0": 3,','    "PAY_2": 2,','    "...": "19 other original fields"','  }','}']
    for i,line in enumerate(lines):s.text(77,241+i*29,line,21,'#E1ECF0',family='DejaVu Sans Mono, monospace')
    s.text(75,555,'Request excerpt; run the complete 23-field JSON fixture.',17,'#A6C7D1')
    s.rect(710,151,842,427,PAPER,LINE,18)
    s.text(740,198,'SAME RESPONSE IN BOTH ARMS',19,TEAL,700,spacing=1)
    s.text(740,256,a['decision']['outcome'].title(),39,INK,700)
    s.text(740,305,a['model']['probability_pct'],44,CORAL,700)
    s.text(905,300,'raw model probability · elevated band',22,MUTED)
    for y,label,value in [(357,'CONTROLLING RULE','Severe delinquency'),(414,'RECOURSE','1 move to approval with controls'),(471,'EXPLANATION','Verified paragraph; text matches exactly'),(528,'ASSESSMENT JSON','Identical, including evidence and receipt')]:
        s.text(741,y,label,16,MUTED,700,spacing=1)
        s.text(741,y+28,value,23,INK,600)
    s.arrow([(658,364),(710,364)])
    s.rect(48,611,1504,90,'#E8F3EF','#BFDAD2',14)
    s.text(76,649,'PARITY CHECK',17,TEAL,700,spacing=1)
    s.text(270,650,'Same application + same tensors + same Qwen + same prompt + same decoding',24,INK,600)
    s.text(76,680,'Measured fixture: decline_close_to_approval.json. Demonstration policy on historical UCI data; no real lending decision.',18,MUTED)
    s.save(ASSETS/'sample_io.svg')

def comparison():
    s=SVG(1200,1000,'Bundled and separated credit architectures','A bounded assessment packaged in one checkpoint compared with independent score, policy and writer artifacts plus explicit context and execution controls.')
    s.text(44,55,'ONE ASSESSMENT. TWO RELEASE MODELS.',17,TEAL,700,spacing=2)
    s.text(44,102,'Preserve exactness. Separate responsibility.',34,INK,700)
    s.rect(38,145,530,670,PAPER,LINE,18);s.rect(596,145,566,670,'#EEF7F4','#BFDAD2',18)
    s.text(66,187,'A  ORIGINAL BUNDLED DESIGN',21,INK,700)
    s.text(626,187,'B  INDEPENDENT COMPONENTS',21,TEAL,700)
    s.text(66,223,'One checkpoint identity',20,MUTED)
    s.text(626,223,'A manifest links separate artifact identities',20,MUTED)
    def card(x,y,w,title,detail,accent=INK):
        s.rect(x,y,w,82,WHITE,LINE,10)
        s.text(x+18,y+31,title,23,accent,700)
        s.text(x+18,y+60,detail,18,MUTED)
    left=[('Validate the request','Typed credit application'),('Compiled score + attribution','Fixed-point trees and exact TreeSHAP'),('Compiled credit policy','Priority rules inside the checkpoint'),('Recourse + evidence','Deterministic assessment and receipt'),('Qwen writer + verifier','Attach or withhold one paragraph')]
    right=[('Qualify context + validate','Approved policy, source, tenant, freshness'),('Independent score + attribution','Same tensors; standalone artifact'),('External OPA policy','Rego rules and versioned threshold data'),('Recourse + evidence','Same response contract and search'),('Same Qwen writer + verifier','Identical prompts, weights and decoding')]
    for i,(a,b) in enumerate(zip(left,right)):
        y=252+i*106;card(64,y,478,*a);card(623,y,512,*b,TEAL)
        if i<4:s.arrow([(303,y+82),(303,y+106)]);s.arrow([(879,y+82),(879,y+106)])
    s.rect(64,845,478,95,DARK,DARK,12)
    s.text(87,882,'ASSESSMENT JSON + RECEIPT',21,WHITE,700)
    s.text(87,914,'Bounded, reproducible credit assessment',18,'#BBD2DA')
    s.rect(623,845,512,95,'#FFF0E8','#E6C7B6',12)
    s.text(647,882,'SEPARATE EXECUTION GATE',21,CORAL,700)
    s.text(647,914,'Permission + recheck + ledger + lineage',18,INK)
    s.arrow([(303,758),(303,845)]);s.arrow([(879,758),(879,845)])
    s.text(44,980,'Same tested credit responses; added workflow controls. The original assessment API has no recording workflow.',18,MUTED)
    s.save(ROOT/'docs/architecture_comparison.svg')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--render',action='store_true');args=parser.parse_args()
    hero();architecture();example();comparison()
    if args.render:
        import cairosvg
        for path in [*ASSETS.glob('*.svg'),ROOT/'docs/architecture_comparison.svg']:
            cairosvg.svg2png(url=str(path),write_to=str(path.with_suffix('.png')),scale=1.25)
    print('Generated four editable repository figures.')

if __name__=='__main__':main()
