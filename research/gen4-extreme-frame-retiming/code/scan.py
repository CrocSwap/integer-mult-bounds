"""Discovery only (not run by verify.py): extreme-frame retiming scan.

Per unit (equal-frame ADD component, or single ADD with --gates), score G = join(previous frames) and
G = meet(next frames) by the change in sum r ln r of the operand roles' frame jumps (dimensions by
rank mod 2^31-1). Usage: scan.py FRAMES.json STATES.json WORD_DIR OUT.json [--gates]
"""
import json,struct,sys,math
from collections import Counter,defaultdict
from fractions import Fraction
FRAMES,STATES,CAND,OUT=sys.argv[1:5]; GATES='--gates' in sys.argv; PR=2**31-1
st=json.load(open(STATES)); n=st['n']; v=st['v']
fs={int(k):x for k,x in json.load(open(FRAMES))['frames'].items()}
fs.update({int(k):x for k,x in json.load(open(CAND+'/COHORT249-FRAMES.json')).items()})
def modrow(row):
    out=[]
    for t in row:
        q=Fraction(t) if isinstance(t,str) else Fraction(t)
        out.append(q.numerator*pow(q.denominator,-1,PR)%PR)
    return out
Bm={k:[modrow(r) for r in x['B']] for k,x in fs.items()}
Am={k:[modrow(r) for r in x['A']] for k,x in fs.items()}
dim={k:x['dim'] for k,x in fs.items()}
def rank(rows):
    M=[r[:] for r in rows]; rk=0; cols=24
    for c in range(cols):
        piv=next((i for i in range(rk,len(M)) if M[i][c]),None)
        if piv is None: continue
        M[rk],M[piv]=M[piv],M[rk]; inv=pow(M[rk][c],-1,PR)
        M[rk]=[x*inv%PR for x in M[rk]]
        for i in range(len(M)):
            if i!=rk and M[i][c]:
                t=M[i][c]; M[i]=[(x-t*y)%PR for x,y in zip(M[i],M[rk])]
        rk+=1
    return rk
init={int(k):f for k,f in json.load(open(CAND+'/COHORT249-INITIAL.json')).items()}
final={int(k):f for k,f in json.load(open(CAND+'/COHORT249-FINAL.json')).items()}
raw=list(struct.iter_unpack('<6i',open(CAND+'/COHORT249-RECORDS.bin','rb').read()))
uses=defaultdict(list)
for i,(op,a,b,c,f,z) in enumerate(raw):
    if op==1: uses[a].append((i,f)); uses[b].append((i,f))
    elif op==2: uses[a].append((i,c))
par={}
def find(x):
    while par.get(x,x)!=x: par[x]=par.get(par[x],par[x]); x=par[x]
    return x
for r,L in uses.items():
    for k in range(len(L)-1):
        (i,f),(j,g)=L[k],L[k+1]
        if not GATES and f==g and raw[i][0]==1 and raw[j][0]==1: par[find(i)]=find(j)
comps=defaultdict(list)
for i,e in enumerate(raw):
    if e[0]==1: comps[find(i)].append(i)
roleidx={r:{i:k for k,(i,_) in enumerate(L)} for r,L in uses.items()}
def rl(k): return k*math.log(k) if k>0 else 0.0
out=[];stats=Counter()
for root,gates in comps.items():
    F=raw[gates[0]][4]; roles=set()
    for g in gates: roles.add(raw[g][1]); roles.add(raw[g][2])
    if n in roles: continue
    bnd=[]
    for r in roles:
        L=uses[r]; ri=roleidx[r]; ks=[ri[g] for g in gates if g in ri]; k0,k1=min(ks),max(ks)
        bnd.append((r,L[k0-1][1] if k0>0 else init[r], L[k1+1][1] if k1+1<len(L) else final[r]))
    def score(dG):
        return sum(rl(dG-dim[pv])+rl(dim[nx]-dG) for _,pv,nx in bnd)
    base=sum(rl(dim[F]-dim[pv])+rl(dim[nx]-dim[F]) for _,pv,nx in bnd)
    pvs={pv for _,pv,_ in bnd}; nxs={nx for _,_,nx in bnd}
    dj=rank([row for p in pvs for row in Bm[p]])
    dm=24-rank([row for x in nxs for row in Am[x]])
    assert dj<=dim[F]<=dm,(dj,dim[F],dm)
    for kind,dG in (('join',dj),('meet',dm)):
        if dG==dim[F]: continue
        sc=score(dG)-base
        if sc>1e-9:
            stats[kind,len(gates)]+=1
            out.append(dict(component=root,gates=sorted(gates),old_frame=F,kind=kind,old_dim=dim[F],new_dim=dG,score=sc,roles=sorted(roles),
                            pv=sorted(pvs),nx=sorted(nxs),cats=sorted(Counter(raw[g][5] for g in gates).items())))
print('candidates',len(out),'total score',sum(o['score'] for o in out))
print(stats.most_common(10))
print(Counter((o['kind'],o['old_dim'],o['new_dim'],str(o['cats'])) for o in out).most_common(15))
json.dump(out,open(OUT,'w'))
