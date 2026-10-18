import sys,collections
sys.path.insert(0,(__import__('os').environ['HM_ROOT']+'/cards/B171'))
import lawler799 as L
path=(__import__('os').environ['HM_ROOT']+'/inputs/words/799-X4-CANONICAL-WORD.json.gz')
# monkeypatch site classification: treat bridges as 'BR', all S3/S4 as before
import csv
orig=csv.DictReader
def run2():
    d,v,ops=L.load(path);n=len(d['start']);P=d['ports']
    from fractions import Fraction as Q
    fr=[L.basis(d['frames'][f]) for f in d['start']]
    rows=[{i:Q(1)} if i<v else {} for i in range(n)]
    site={int(x['reg']):x['site'][:2] for x in orig(open((__import__('os').environ['HM_ROOT']+'/inputs/ledger_helpers.csv')))}
    SEQ=[];Lpre=[];copies=[];fill=set()
    for t,s,e in ops:
        if e[0]=='add':
            q=Q(e[3],e[4])
            if t not in fill and not rows[t] and rows[s]:
                fill.add(t)
                c=site.get(t,'BR' if t>=716 else '?')
                copies.append((c,s,t,len(SEQ)))
            rt=rows[t]
            for j,x in list(rows[s].items()):
                z=rt.get(j,0)+q*x
                if z: rt[j]=z
                else: rt.pop(j,None)
            SEQ.append((t,s));Lpre.append((fr[t],fr[s]));fr[t]=L.basis(list(fr[t])+list(fr[s]))
        else:
            q=Q(e[2],e[3]);rows[t]={j:q*x for j,x in rows[t].items()}
    return d,v,SEQ,Lpre,copies,P
d,v,SEQ,Lpre,copies,P=run2()
print(collections.Counter(c[0] for c in copies))
sel=[c for c in copies if c[0]=='BR' or c[0]=='S3' and (450<=c[2]<=457 or 484<=c[2]<=569)]
print(len(sel),[c for c in sel if c[0]=='BR'])
out,bad=L.certify(d,v,SEQ,Lpre,sel,P)
for k,c in sorted(out.items()):print(k,c)
print('passing',[(b[0],b[1],b[2]) for b in bad])
# value check: bridge rows at fill time pairwise non-proportional
from fractions import Fraction as Q
d2,v2,ops=L.load(path);rows=[{i:Q(1)} if i<v2 else {} for i in range(728)]
snap={}
for t,s,e in ops:
    if e[0]=='add':
        if t>=716 and t not in snap and not rows[t] and rows[s]:
            q=Q(e[3],e[4]);snap[t]={j:q*x for j,x in rows[s].items()}
        q=Q(e[3],e[4])
        for j,x in list(rows[s].items()):
            z=rows[t].get(j,0)+q*x
            if z: rows[t][j]=z
            else: rows[t].pop(j,None)
    else:
        q=Q(e[2],e[3]);rows[t]={j:q*x for j,x in rows[t].items()}
def norm(r):
    k=min(r);return tuple(sorted((j,x/r[k]) for j,x in r.items()))
print('distinct',len({norm(r) for r in snap.values()}),'of',len(snap),[len(r) for r in snap.values()])
