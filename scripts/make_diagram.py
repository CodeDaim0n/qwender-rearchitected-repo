"""Exact architecture figure; generated with ordinary vector drawing tools."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,FancyArrowPatch
ROOT=Path(__file__).resolve().parents[1]
fig,ax=plt.subplots(figsize=(12,10));fig.patch.set_facecolor('#f7f9fb')
ax.set_xlim(0,120);ax.set_ylim(0,100);ax.axis('off')
navy='#132b43';teal='#126c72';orange='#b65d30'
def box(x,y,w,h,title,detail='',color=navy):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.6,rounding_size=1.2',
                              facecolor='white',edgecolor=color,linewidth=1.5))
    ax.text(x+w/2,y+h*.64 if detail else y+h/2,title,ha='center',va='center',fontsize=11.3,color=color,fontweight='bold')
    if detail:ax.text(x+w/2,y+h*.25,detail,ha='center',va='center',fontsize=9,color='#4c5d6f')
def arrow(x1,y1,x2,y2,color=navy):
    ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle='-|>',mutation_scale=12,color=color,linewidth=1.3))
ax.text(3,97,'Same credit inputs. Same Qwen. Different governance boundaries.',fontsize=17,fontweight='bold',color=navy)
ax.text(3,91,'A  |  ORIGINAL BUNDLED DESIGN',fontsize=12,fontweight='bold',color=navy)
ax.text(58,91,'B  |  SEPARATED COMPONENTS',fontsize=12,fontweight='bold',color=teal)
ax.add_patch(FancyBboxPatch((3,17),46,66,boxstyle='round,pad=1,rounding_size=1.5',facecolor='#eaf0f6',edgecolor='#acbbc9',linestyle='--'))
ax.text(26,80,'One checkpoint artifact',ha='center',fontsize=10,color=navy)
for y,title,detail in [
    (67,'Validate application','23-field typed request'),
    (55,'Trees + exact TreeSHAP','Fixed-point scoring and attribution'),
    (43,'Compiled credit policy','Priority rules in tensor buffers'),
    (31,'Recourse + evidence','Deterministic facts and receipt'),
    (19,'Qwen writer + verifier','Attach paragraph or withhold')]:
    box(7,y,38,9,title,detail)
for y in [67,55,43,31]:arrow(26,y,26,y-3)
box(7,3,38,9,'Assessment JSON','Decision delivered either way')
arrow(26,19,26,12)
box(58,77,56,9,'Evidence and approval graph','Source, tenant, policy version and approval',teal)
box(58,64,56,9,'Trusted-context qualification','Bind request + component identities',teal)
arrow(86,77,86,73,teal)
box(56,49,27,10,'Scorer + TreeSHAP','Independent tensor file',teal)
box(90,49,27,10,'OPA credit policy','Rego + versioned data',teal)
arrow(72,64,69.5,59,teal);arrow(83,54,90,54,teal)
ax.text(86.5,57,'facts',ha='center',fontsize=8,color=teal)
box(58,35,56,9,'Evidence + recourse','Identical evidence contract and search',teal)
arrow(69.5,49,76,44,teal);arrow(103.5,49,96,44,teal)
box(58,22,56,9,'Same Qwen writer + verifier','Same prompt, weights and decoding',teal)
arrow(86,35,86,31,teal)
box(58,9,56,9,'Execution gate + sandbox ledger','Recheck context, authorize, deduplicate',orange)
arrow(86,22,86,18,orange)
ax.text(86,3,'Linked, timestamped lineage graph',ha='center',fontsize=10,color=teal,fontweight='bold')
ax.text(3,-2,'Implemented as modular Python components plus an OPA process; no distributed service or network isolation claim.',fontsize=9,color='#4c5d6f')
fig.savefig(ROOT/'docs/architecture_comparison.svg',bbox_inches='tight')
fig.savefig(ROOT/'docs/architecture_comparison.png',dpi=190,bbox_inches='tight')
print('Saved SVG and PNG architecture comparison')
