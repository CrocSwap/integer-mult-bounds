#!/usr/bin/env python3
"""Exact typed complementary-consumer screen. Apache-2.0; OpenAI Codex assistance."""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha1, sha256
from pathlib import Path
import argparse, json
HERE=Path(__file__).resolve().parent

def need(ok,msg):
    if not ok: raise ValueError(msg)

def add(a,b):
    c=dict(a)
    for k,v in b.items(): c[k]=c.get(k,0)+v
    return {k:v for k,v in c.items() if v}

def mul(a,b):
    c={}
    for k,v in a.items():
        for l,w in b.items():
            e=tuple(x+y for x,y in zip(k,l));c[e]=c.get(e,0)+v*w
    return {k:v for k,v in c.items() if v}

def mon(a=0,b=0,q=0,c=1): return {(a,b,q):F(c)} if c else {}
I=[[mon(),{}],[{},mon()]]
def mm(a,b): return [[add(mul(a[i][0],b[0][j]),mul(a[i][1],b[1][j])) for j in range(2)] for i in range(2)]
def tr(a): return [[a[j][i] for j in range(2)] for i in range(2)]
def sh(c): return [[mon(),{}],[c,mon()]]
def diag(x,y): return [[x,{}],[{},y]]
def gaussian(stage,q=0,sign=1): return mon(sign if stage==1 else 0,sign if stage==2 else 0,q)
def minus(a): return {k:-v for k,v in a.items()}
def inverse_monomial(a):
    need(len(a)==1,'monomial diagonal')
    (k,v),=a.items();return {tuple(-x for x in k):1/v}
def rawdual(a):
    need(not a[0][1],'lower triangular source')
    x,z=inverse_monomial(a[0][0]),inverse_monomial(a[1][1])
    return [[x,minus(mul(mul(x,a[1][0]),z))],[{},z]]
def source(stage,kind):
    d=gaussian(stage)
    if kind=='A':return mm(diag(d,d),sh(mon(q=-1)))
    if kind=='B':return mm(diag(d,mul(d,mon(q=1))),sh(mon(q=-1)))
    if kind=='C':return mm(diag(d,d),mm(sh(mon(q=-1)),diag(mon(q=1),mon())))
    raise ValueError(kind)

def certify():
    for r in json.loads((HERE/'SNAPSHOTS.json').read_text()):
        data=(HERE/r['snapshot']).read_bytes()
        need(sha256(data).hexdigest()==r['sha256'],'source SHA256')
        need(sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==r['git_blob'],'source Git blob')
    profiles={}; lower={}
    for name in 'BC':
        x=json.loads((HERE/'inputs'/f'{name}.json').read_text());p={int(k):v for k,v in x['paid'].items()};h={int(k):v for k,v in x['helpers'].items()}
        need(sum(h.values())==408,'independent helper census')
        net={r:p.get(r,0)-h.get(r,0) for r in p.keys()|h.keys()}
        mass=sum(r*v for r,v in net.items()); need(mass==x['local_deficit'],'source mass')
        # d/dC [(P-H-112)/7^(1-C)] : all terms nonnegative
        # except rank6; rank7 is constant. log7>1, log(7/6)<1.
        c=dict(net);c[1]-=112
        need(all(v>=0 for r,v in c.items() if r<7 and r!=6),'derivative signs below separator')
        need(all(v<=0 for r,v in c.items() if r>7),'derivative signs above separator')
        need(c.get(6,0)<=0,'only negative derivative term')
        L=F(c[1],7)+c.get(6,0);need(L>0,'strict all-domain derivative lower bound')
        lower[name]=str(L)
        profiles[name]={'paid':p,'helpers':h,'net_mass':mass,'direct_gap_mass':mass-1680}
    need(profiles['B']['direct_gap_mass']==8 and profiles['C']['direct_gap_mass']==0,'actual source gaps')
    D=mon(1,1);Q=mon(q=1)
    # Execute C on fresh block1, then B on fresh block2, then Y-=2X.
    cb=[source(1,'C'),source(2,'B'),sh(mon(c=-2))]
    aa=[source(1,'A'),source(2,'A'),sh(mon(q=-1,c=-2))]
    for name,word,target in [('exceptional',cb,diag(mul(D,Q),mul(D,Q))),('ordinary',aa,diag(D,D))]:
        f=I;dual=I
        for op in word:f=mm(op,f);dual=mm(rawdual(op),dual)
        need(f==target,name+' arbitrary-input Laurent endpoint')
        need(mm(tr(f),dual)==I,name+' actual raw inverse transpose')
    need(mm(sh(mon(c=-1)),mm(cb[1],cb[0]))!=diag(mul(D,Q),mul(D,Q)),'wrong cancellation coefficient rejected')
    need(mm(sh(mon(c=-2)),mm(aa[1],aa[0]))!=diag(D,D),'ordinary Q inverse cannot be dropped')
    need(mm(tr(mm(cb[1],cb[0])),mm(cb[1],cb[0]))!=I,'forward word is not raw dual')
    paid=Counter();helpers=Counter()
    for v in profiles.values():paid.update(v['paid']);helpers.update(v['helpers'])
    paid[1]+=56 # the retained ordinary A/A contamination is charged once per pair
    targets=dict(helpers);targets[14]=112;targets[15]=112
    mass=lambda c:sum(r*n for r,n in c.items())
    need(mass(paid)-mass(targets)==176,'complete pair deficit')
    need(sum(targets.values())==1040,'224 main plus two disjoint408 helper banks')
    # Explicit n=2 extremal cap; universal-n result is algebraic in PROOF.md.
    screens={}
    for b in range(3):screens[f'{b}B+{2-b}C']={'maximum_main_rank':15,'maximum_main_count':224,'optimistic_mass_deficit':8*b}
    return {'status':'PASS_SCOPED_COMPLEMENTARY_SERIAL_SCREEN','new_kappa':False,'profiles':profiles,'normalized_direct_gap_derivative_lower_bounds':lower,'complete_pair_paid':dict(sorted(paid.items())),'complete_pair_targets':dict(sorted(targets.items())),'complete_pair_rank_deficit':176,'persistent_independent_inputs':1040,'two_call_screens':screens,'serial_domain':'n>=2 complete whole calls; same224 main owners; independent408 helpers per call; one shared Q; n disjoint seven-axis transverse blocks; each main target rank<=7n+1; no extra productive inputs or ranks','uniform_optimistic_moment_bound':'M(C)<=224*(7n+1)^(1-C)-n*(224*7^(1-C)+112)-8*n_B*7^(-C); strict negative for0<C<1, n>=2','verification_scope':'typed-interface Laurent identities and source receipt arithmetic only; source native/phase audit inherited from4712, not freshly replayed'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');a=ap.parse_args();r=certify();s=json.dumps(r,sort_keys=True,indent=2)+'\n'
    if a.write:(HERE/'RESULT.json').write_text(s)
    else:need(json.dumps(json.loads((HERE/'RESULT.json').read_text()),sort_keys=True)==json.dumps(json.loads(json.dumps(r)),sort_keys=True),'type-sensitive canonical receipt')
    print(r['status'])
if __name__=='__main__':main()
