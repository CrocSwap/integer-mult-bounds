import gzip,json,csv,math,sys
from fractions import Fraction as Q
from collections import defaultdict
d=json.load(gzip.open(__import__('os').environ['HM_ROOT']+'/inputs/words/656-CANONICAL-WORD.json.gz'))
fr=d['frames'];L=lambda f:len(fr[f])
H=list(csv.DictReader(open((__import__('os').environ['HM_ROOT']+'/inputs/ledger_helpers.csv'))))
blocks=defaultdict(list)
for h in H:
    if h['site'].startswith('S1'): blocks[h['detail'].split('|')[0]].append(int(h['reg']))
NREG=len(d['start'])
# value replay of A+B+tail in canonical order A,centers/cut,B,tail from identity on sources (regs 0..v-1 = e_i; others 0)
v=d['v'];print('v',v,'NREG',NREG,'ncut',len(d['cut']),'ncomp',len(d['compensation']) if hasattr(d['compensation'],'__len__') else d['compensation'])
rows=[dict() for _ in range(NREG)]
for i in range(v): rows[i]={i:Q(1)}
def ap(e):
    if e[0]=='add':
        _,t,s,a,b=e[:5];q=Q(a,b)
        for j,x in list(rows[s].items()):
            z=rows[t].get(j,Q(0))+q*x
            if z:rows[t][j]=z
            else:rows[t].pop(j,None)
    else:
        _,t,a,b=e[:4];q=Q(a,b);rows[t]={j:q*x for j,x in rows[t].items()}
def norm(r):
    if not r:return ()
    k=min(r);c=r[k]
    return tuple(sorted((j,x/c) for j,x in r.items()))
reads=defaultdict(list)  # reg -> list of (part,idx,tgt,frame dim,form)
seq=[('A',i,e) for i,e in enumerate(d['A'])]+[('B',i,e) for i,e in enumerate(d['B'])]+[('tail',i,e) for i,e in enumerate(d['tail'])]
allregs={r for b in blocks.values() for r in b}
for p,i,e in seq:
    if e[0]=='add' and e[2] in allregs and p!='A':
        reads[e[2]].append((p,i,e[1],L(e[-1]),norm(rows[e[2]])))
    ap(e)
import pickle;pickle.dump((dict(blocks),dict(reads)),open('iface.pkl','wb'))
b0=blocks['(0, 1, 2, 3)']
for r in b0:
    rs=reads[r]
    print(r,[(p,i,fd) for p,i,t,fd,f in rs][:12], 'nforms',len({f for *_,f in rs}))
