"""Independent sparse-Fraction checks of the two-ended composition repair.
Chi Zhao, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
from fractions import Fraction as F
import json,gzip,hashlib
import argparse
ap=argparse.ArgumentParser();ap.add_argument('--word',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
if not __debug__:raise RuntimeError('Assertions required')
pkg=Path(__file__).resolve().parents[1]
load=lambda p:json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
combined=load(args.word);repair=load(pkg/'data/COMPOSITION-REPAIR.json');nominal=dict(combined,A=combined['A'][len(repair):])
n=716

def apply(rows,e):
    if e[0]=='scale':
        z=F(e[2],e[3]);rows[e[1]]={j:z*v for j,v in rows[e[1]].items()}
    else:
        t,s=e[1:3];z=F(e[3],e[4])
        for j,v in list(rows[s].items()):
            v=rows[t].get(j,F(0))+z*v
            if v:rows[t][j]=v
            else:rows[t].pop(j,None)

def matrix(gates):
    rows=[{i:F(1)} for i in range(n)]
    for e in gates:apply(rows,e)
    return rows

def inverse(gates):
    out=[]
    for g in reversed(gates):
        e=list(g)
        if e[0]=='scale':e[2],e[3]=e[3],e[2]
        else:e[3]=-e[3]
        out.append(e)
    return matrix(out)

def span(vs):
    piv={}
    for x in vs:
        while x:
            k=x.bit_length()-1
            if k in piv:x^=piv[k]
            else:piv[k]=x;break
    return piv

def same(a,b):return len(span(a))==len(span(b))==len(span(a+b))
def regs(e):return e[1:3] if e[0]=='add' else e[1:2]
def tail(w):return [w['cleanup'][i][:-1]+[f]for i,f in w['early_cleanup']]

delayed=['add',95,403,1,4,[265,137,96,6]]
pos=nominal['A'].index(delayed);assert nominal['A'].count(delayed)==1
before=nominal['A'][:pos];after=nominal['A'][pos+1:]+nominal['cut']+nominal['B']+tail(nominal)
R=matrix(before);L=matrix(after)
cold=set(range(224,n))-set(map(int,nominal['start_extra']))
projection={j:v for j,v in R[403].items()if j not in cold}
assert projection=={90:F(-2),94:F(-2),91:F(-2),95:F(-2)},projection
ended=set(map(int,nominal['helper_final']))
influence={h:L[h][95]for h in ended if L[h].get(95)}
assert influence=={581:F(1,2)},influence
cur=[[]for _ in range(n)]
for i,v in enumerate(nominal['ports']):cur[i]=[v]
for h,v in nominal['start_extra'].items():cur[int(h)]=v
for g in before:
    for h in regs(g):cur[h]=g[-1]
assert same(cur[95],delayed[-1]) and same(cur[403],delayed[-1])
P=matrix(nominal['A']+nominal['cut']+nominal['B']+tail(nominal))
expected={581:{581:F(1),406:F(1,2),373:F(-1,2)},590:{590:F(1),421:F(1,2),423:F(-1,2),391:F(1,2),388:F(-1,2)}}
for h,row in expected.items():assert P[h]==row,(h,P[h])
assert all(j in cold for row in expected.values()for j in row)
assert combined['A']==repair+nominal['A']
assert all(g[-1]==[] and set(regs(g))<=cold for g in repair)
Q=matrix(combined['A']+combined['cut']+combined['B']+tail(combined))
for h in ended:
    assert Q[h]=={h:F(1)},(h,Q[h])
    assert all(not Q[j].get(h)for j in range(n)if j!=h),(h,'column not isolated')
# Check exact inverse columns after row corrections, before column corrections.
rowfix=[g for g in repair if g[1] in (581,590)]
I=inverse(rowfix+nominal['A']+nominal['cut']+nominal['B']+tail(nominal))
inverse_columns={h:{i:row[h]for i,row in enumerate(I)if row.get(h)} for h in (581,590)}
assert inverse_columns=={581:{308:F(1),321:F(-1),581:F(1)},590:{309:F(1),323:F(-1),590:F(1)}},inverse_columns
serial=lambda row:{str(k):str(v)for k,v in row.items()}
receipt={'status':'PASS_INDEPENDENT_TWO_HELPER_BASIS_PROOF','arithmetic':'Separate sparse Fraction replay; no construction/auditor imports','raw_word_content_sha256':hashlib.sha256(gzip.decompress(args.word.read_bytes())).hexdigest(),'original_hpe_anchor':1665,'delayed_gate':delayed,'combined_A_gate_index':combined['A'].index(delayed),'common_frame_rank':len(span(delayed[-1])),'source403_noncold_projection':serial(projection),'ended_row_influence_of_port95':serial(influence),'rows_after_delayed_gate_before_basis_repair':{str(k):serial(v)for k,v in expected.items()},'inverse_columns_after_row_correction':{str(k):serial(v)for k,v in inverse_columns.items()},'all_ended_rows_and_columns_isolated':len(ended),'repair_gates':repair,'rank_zero_repair':True,'proof':'The delayed same-frame q95 += S403/4 contributes (1/2)(1/4)(-2) to each residual data coefficient of row581 and zero to every other ended row. Remaining row defects are cold only. Prepending row shears removes them; the displayed inverse columns then give cold-only column shears isolating e581 and e590. The ten gates are at rank zero. All inherited ended rows and columns remain isolated. Exact FULL cleanup and scalar/frame/cone/compensation admission are separately checked by the unchanged native auditor.'}
args.out.write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(ended),'ended rows and columns isolated')
