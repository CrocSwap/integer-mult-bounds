"""Check the saved dirty GF9 word with separate field operations."""
from pathlib import Path
import json

HERE=Path(__file__).resolve().parent
word=json.loads((HERE/'dirty-word.json').read_text())
def add(a,b):
    return (a%3+b%3)%3+3*((a//3+b//3)%3)
def neg(a):
    return (-a%3)%3+3*((-(a//3))%3)
def mul(a,b):
    return ((a%3)*(b%3)-(a//3)*(b//3))%3+3*(((a%3)*(b//3)+(a//3)*(b%3))%3)
def inv(a):
    assert a
    return next(b for b in range(1,9) if mul(a,b)==1)
def rowcomb(coeff,rows):
    out=[0]*len(rows[0])
    for a,row in zip(coeff,rows):
        for j,b in enumerate(row):
            out[j]=add(out[j],mul(a,b))
    return out
def rank(matrix):
    a=[row[:] for row in matrix]
    out=0
    for col in range(len(a[0])):
        p=next((p for p in range(out,len(a)) if a[p][col]),None)
        if p is None:
            continue
        a[out],a[p]=a[p],a[out]
        scale=inv(a[out][col])
        a[out]=[mul(scale,v) for v in a[out]]
        for j in range(len(a)):
            if j!=out and a[j][col]:
                factor=neg(a[j][col])
                a[j]=[add(u,mul(factor,v)) for u,v in zip(a[j],a[out])]
        out+=1
        if out==len(a):
            break
    return out
n=len(word['inputs'])
inputs={tuple(stub):[int(j==i) for j in range(n)] for i,stub in enumerate(word['inputs'])}
packets={}
outputs={}
for local in word['local_words']:
    assert rank(local['matrix'])==5
    v=local['vertex']
    rows=[inputs[v,e] if (v,e) in inputs else packets[e] for e in local['known_edges']]
    for e,coeff in zip(local['unknown_edges'],local['matrix']):
        value=rowcomb(coeff,rows)
        if [v,e] in word['outputs']:
            outputs[v,e]=value
        else:
            assert e not in packets
            packets[e]=value
matrix=[outputs[tuple(stub)] for stub in word['outputs']]
assert matrix==word['transfer']
assert len(packets)==735 and rank(matrix)==175
assert [r[:157] for r in matrix[:157]]==[[int(i==j) for j in range(157)] for i in range(157)]
inpairs={e:[] for v,e in word['inputs'][157:]}
for j,(v,e) in enumerate(word['inputs'][157:],157):
    inpairs[e].append(j)
outpairs={e:[] for v,e in word['outputs'][157:]}
for j,(v,e) in enumerate(word['outputs'][157:],157):
    outpairs[e].append(j)
assert all(len(p)==2 for p in inpairs.values())
assert all(len(p)==2 for p in outpairs.values())
Q=[row[:157]+[add(row[a],row[b]) for a,b in inpairs.values()] for row in matrix]
assert all(not any(row[157:]) for row in Q[:157])
for a,b in outpairs.values():
    assert Q[a]==Q[b]
quotient=Q[:157]+[Q[p[0]] for p in outpairs.values()]
assert rank(quotient)==166
assert rank([row[157:] for row in quotient[157:]])==9
ranks={'F':rank([r[157:] for r in matrix[:157]]),'G':rank([r[:157] for r in matrix[157:]]),'H':rank([r[157:] for r in matrix[157:]])}
assert ranks=={'F':9,'G':9,'H':18}
result=dict(status='PASS',all_saved_local_maps_invertible=True,replayed_physical_transmissions=735,independent_field_implementation=True,whole_dirty_word_rank=175,block_ranks=ranks,paired_C_quotient_rank=166,paired_C_does_not_contaminate_B=True,paired_J_outputs_agree=True,dirty_quotient_junk_block_rank=9,scope='A separate replay of the saved finite GF9 word. No rational frame realization or recursive paid cost is checked.')
(HERE/'INDEPENDENT-DIRTY.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
