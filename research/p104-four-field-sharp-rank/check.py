#!/usr/bin/env python3
"""Independent exact checks for the sharp n4 four-stage rank theorem.

No predecessor executable is imported. Rational arithmetic, standard library.
Prepared by worker B with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path

F=Fraction
HERE=Path(__file__).resolve().parent
PIN='b22d9085b8b0112b94b80ab807a11564e9a515dc8559c60b1f4a5a08ff04bb43'
def matrix(rows):return [[F(x) for x in row] for row in rows]
def zeros(n,m=None):return [[F(0)]*(n if m is None else m) for _ in range(n)]
def identity(n):return matrix([[int(i==j) for j in range(n)] for i in range(n)])
def plus(a,b):return [[x+y for x,y in zip(ar,br)] for ar,br in zip(a,b)]
def times(c,a):return [[c*x for x in row] for row in a]
def minus(a,b):return plus(a,times(-1,b))
def product(a,b):return [[sum(x*y for x,y in zip(row,col)) for col in zip(*b)] for row in a]
def transpose(a):return [list(col) for col in zip(*a)]
def horizontal(*aa):return [sum((a[i] for a in aa),[]) for i in range(len(aa[0]))]
def vertical(*aa):return sum(([row[:] for row in a] for a in aa),[])
def blocks(*aa):
    nr=sum(len(a) for a in aa);nc=sum(len(a[0]) for a in aa);out=zeros(nr,nc);r=c=0
    for a in aa:
        for i,row in enumerate(a):out[r+i][c:c+len(row)]=row
        r+=len(a);c+=len(a[0])
    return out

def reduced(a):
    a=[r[:] for r in a];row=0;piv=[]
    for col in range(len(a[0])):
        pick=next((i for i in range(row,len(a)) if a[i][col]),None)
        if pick is None:continue
        a[row],a[pick]=a[pick],a[row];f=a[row][col];a[row]=[x/f for x in a[row]]
        for i in range(len(a)):
            if i!=row:
                f=a[i][col];a[i]=[x-f*y for x,y in zip(a[i],a[row])]
        piv.append(col);row+=1
        if row==len(a):break
    return a,piv

def rank(a):return len(reduced(a)[1])
def inverse(a):
    n=len(a);r,piv=reduced(horizontal(a,identity(n)))
    demand(piv[:n]==list(range(n)),'inverse exists')
    return [row[n:] for row in r]
def demand(condition,label):
    if not condition:raise RuntimeError(label)
def equal(a,b,label):demand(a==b,label)
def scalar_fixture():
    u=[matrix([[1],[1],[0],[0]]),matrix([[2],[1],[1],[-1]]),None,matrix([[1],[0],[0],[1]]),matrix([[1],[0],[1],[0]])]
    v=[matrix([[-1,1,0,0]]),matrix([[-1,2,0,0]]),None,matrix([[1,0,-2,-1]]),matrix([[1,0,-1,0]])]
    u[2]=minus(plus(minus(u[1],u[0]),u[3]),u[4]);v[2]=minus(plus(minus(v[1],v[0]),v[3]),v[4])
    ds=[[1,1,0,0],[1,1,1,1],[1,0,1,1],[1,0,1,0]]
    ps=[matrix([[int(i==j)*d[i] for j in range(4)] for i in range(4)]) for d in ds]
    return dict(q=1,U=u,V=v,P=ps,H=identity(4),masks=[15,3,14,6])
def coupled_fixture():
    raw=(HERE/'ROOT-RANK21.json').read_bytes();demand(sha256(raw).hexdigest()==PIN,'rank21 fixture pin')
    a=json.loads(raw)
    return dict(q=2,U=[matrix(a) for a in a['U']],V=[matrix(a) for a in a['V']],P=[matrix(a['P'][str(j)]) for j in [0,1,3,4]],H=matrix(a['H']),masks=a['output_stage_masks'])
def direct_sum(*ff):
    return dict(q=sum(f['q'] for f in ff),U=[blocks(*(f['U'][j] for f in ff)) for j in range(5)],V=[blocks(*(f['V'][j] for f in ff)) for j in range(5)],P=[blocks(*(f['P'][j] for f in ff)) for j in range(4)],H=blocks(*(f['H'] for f in ff)),masks=sum((f['masks'] for f in ff),[]))
def reflect(f):
    # Query reversal with U'_i=U_(4-i), V'_i=-V_(4-i) restores ordered Gram.
    masks=[]
    for m in f['masks']:
        masks.append(sum(((m>>i)&1)<<(3-i) for i in range(4)))
    return dict(q=f['q'],U=list(reversed(f['U'])),V=[times(-1,v) for v in reversed(f['V'])],P=list(reversed(f['P'])),H=f['H'],masks=masks)
def literal(f,s,omit_query=None,omit_stage=None):
    n=4*f['q'];one=identity(n);out={0:one};index=0
    for site in range(5):
        r=product(f['U'][site],f['V'][site]);query=one if site==omit_query else plus(one,times(s-1,r))
        out={m:product(query,a) for m,a in out.items()}
        if site==2:continue
        p=f['P'][index];bit=1<<index;index+=1
        if site==omit_stage:continue
        dest={}
        for m,a in out.items():
            for mask,op in [(m,minus(one,p)),(m|bit,p)]:dest[mask]=plus(dest.get(mask,zeros(n)),product(op,a))
        out=dest
    return out

def check(f,label):
    q=f['q'];n=4*q;one=identity(n);zero=zeros(n);rr=[product(u,v) for u,v in zip(f['U'],f['V'])]
    demand(rank(f['H'])==n,label+' input basis')
    demand(all(x.denominator==1 for row in inverse(f['H']) for x in row),label+' unimodular input basis')
    for i in range(5):
        demand(rank(f['U'][i])==rank(f['V'][i])==rank(rr[i])==q,label+' query ranks')
        equal(product(rr[i],rr[i]),zero,label+' square-zero')
        for j in range(5):equal(product(f['V'][i],f['U'][j]),times((i>j)-(i<j),identity(q)),label+' ordered Gram')
    prefix=one;prefixes=[];ranks=[];sindex=0
    for i in range(5):
        prefix=product(minus(one,times(2,rr[i])),prefix);prefixes.append(prefix)
        if i==2:continue
        p=f['P'][sindex];equal(product(p,p),p,label+' idempotent');equal(product(p,rr[i]),rr[i],label+' left support');equal(product(rr[i],p),rr[i],label+' right support')
        equal(product(p,prefix),product(prefix,p),label+' actual prefix')
        mask=matrix([[int(i==j and (f['masks'][i]&(1<<sindex))!=0) for j in range(n)] for i in range(n)])
        equal(product(p,f['H']),product(f['H'],mask),label+' sector basis');ranks.append(rank(p));sindex+=1
    equal(prefix,times(-1,one),label+' full endpoint')
    demand(sum(ranks)==(21*q+1)//2,label+' sharp integer budget')
    for p in f['P']:
        for r in f['P']:equal(product(p,r),product(r,p),label+' stage commutation')
    for s in [1,-1]:
        coeff=literal(f,s)
        for m in range(16):
            want=matrix([[s*int(i==j and f['masks'][i]==m) for j in range(n)] for i in range(n)])
            equal(product(coeff.get(m,zero),f['H']),product(f['H'],want),label+' formal coefficient')
    # Independent recovery of proof sectors and ordered reduced identities.
    selected=horizontal(*(f['U'][i] for i in [0,1,3,4]));selected_inv=inverse(selected)
    k=product(vertical(*(f['V'][i] for i in [0,1,3,4])),selected);kinv=inverse(k)
    sectors={}
    for m in range(16):
        e=one
        for j,p in enumerate(f['P']):e=product(p if (m>>j)&1 else minus(one,p),e)
        sectors[m]=product(product(selected_inv,e),selected)
    allowed={3,6,12,7,14,15}
    for m,e in sectors.items():
        if m not in allowed:equal(e,zero,label+' absent singleton/empty sector')
    J=vertical(horizontal(zeros(q),identity(q)),horizontal(times(-1,identity(q)),zeros(q)))
    FF=vertical(horizontal(zeros(q),times(-1,identity(q))),horizontal(identity(q),times(-1,identity(q))))
    FF2=product(FF,FF);NN=vertical(horizontal(identity(q),zeros(q)),horizontal(identity(q),zeros(q)))
    equal(product(FF2,FF),identity(2*q),label+' F order three')
    local=[]
    for mask,start in [(3,0),(6,q),(12,2*q)]:
        m=product(k,sectors[mask]);ix=range(start,start+2*q)
        demand(all(m[i][j]==0 for i in range(n) for j in range(n) if i not in ix or j not in ix),label+' sector support')
        b=[[m[i][j] for j in ix] for i in ix];equal(product(product(b,J),b),b,label+' supported sector idempotency');local.append(product(b,J))
    P=local[0];Q=product(product(FF,local[1]),FF2);R=product(product(FF2,local[2]),FF)
    z2=zeros(2*q)
    for a,b in [(P,Q),(Q,P),(Q,R),(R,Q)]:equal(product(a,b),z2,label+' adjacent reduced orthogonality')
    equal(product(product(P,NN),R),z2,label+' forward separated reduction')
    equal(product(product(R,minus(identity(2*q),NN)),P),z2,label+' reverse separated reduction')
    x,y,z=map(rank,[P,Q,R]);w=rank(sectors[15]);h=rank(sectors[7]);j=rank(sectors[14])
    demand(x+z<=2*q and 3*(x+z)<=4*(2*q-y) and 2*(x+y+z)<=5*q,label+' capacity bounds')
    if q%2==0:demand((x,y,z,w,h+j)==(q,q//2,q,q,q//2),label+' equality classification')
    return dict(label=label,q=q,ranks=ranks,total=sum(ranks),sectors=dict(AB=x,BC=y,CD=z,ABC=h,BCD=j,ABCD=w),formal_coefficients=32),prefixes

def controls(f,prefixes):
    n=4*f['q'];one=identity(n);zero=zeros(n)
    def fails(word,s):
        return any(product(word.get(m,zero),f['H'])!=product(f['H'],matrix([[s*int(i==j and f['masks'][i]==m) for j in range(n)] for i in range(n)])) for m in range(16))
    demand(all(fails(literal(f,-1,omit_query=i),-1) for i in range(5)),'five query omissions detected')
    demand(all(fails(literal(f,1,omit_stage=i),1) for i in [0,1,3,4]),'four stage omissions detected')
    # A legitimate query-B support need not commute with B's actual prefix.
    uu=horizontal(f['U'][1],f['U'][4]);vv=vertical(f['V'][1],f['V'][4]);bad=product(product(uu,inverse(product(vv,uu))),vv)
    rb=product(f['U'][1],f['V'][1]);equal(product(bad,bad),bad,'prefix control is idempotent');equal(product(bad,rb),rb,'prefix control left support');equal(product(rb,bad),rb,'prefix control right support')
    demand(product(bad,prefixes[1])!=product(prefixes[1],bad),'missing actual-prefix hypothesis detected')
    # Forced minimal odd stage respects its prefix but need not commute with all stages.
    uu=horizontal(f['U'][0],f['U'][1]);vv=vertical(f['V'][0],f['V'][1]);bad=product(product(uu,inverse(product(vv,uu))),vv)
    equal(product(bad,bad),bad,'commutation control idempotent')
    equal(product(bad,rb),rb,'commutation control left query support')
    equal(product(rb,bad),rb,'commutation control right query support')
    equal(product(bad,prefixes[1]),product(prefixes[1],bad),'commutation control has actual prefix')
    demand(sum(rank(p) for i,p in enumerate(f['P']) if i!=1)+rank(bad)==19,'commutation-omitted budget is nineteen')
    demand(any(product(bad,p)!=product(p,bad) for p in f['P']),'missing pairwise commutation detected')
    # Each ordered separated-pair condition is independently necessary.
    q=f['q'];nn=vertical(horizontal(identity(q),zeros(q)),horizontal(identity(q),zeros(q)));co=minus(identity(2*q),nn)
    equal(product(product(co,nn),co),zeros(2*q),'forward-only control')
    demand(product(product(co,co),co)!=zeros(2*q),'reverse condition rejects forward-only control')
    equal(product(product(nn,co),nn),zeros(2*q),'reverse-only control')
    demand(product(product(nn,nn),nn)!=zeros(2*q),'forward condition rejects reverse-only control')
    demand(2*(rank(co)+rank(nn)+rank(co))>5*q,'forward-only violates capacity')
    demand(2*(rank(nn)+rank(co)+rank(nn))>5*q,'reverse-only violates capacity')
    # One-sided query idleness does not justify rank-one trimming.
    rp=matrix([[0,1],[0,0]]);fp=matrix([[1,0],[0,0]]);ip=identity(2);bp=times(-1,ip)
    equal(product(fp,fp),fp,'idle control idempotent')
    equal(product(fp,bp),product(bp,fp),'idle control actual-prefix commutation')
    equal(product(rp,fp),zeros(2),'idle control right product zero')
    equal(product(fp,rp),rp,'idle control left product nonzero')
    demand(product(minus(ip,fp),rp)!=rp,'one-sided idle trim loses query support')
    return 14

def main():
    source_pins={'SOURCE6773_FOUR-STAGE-NOTE.md':'952c25f3f7e211887f2bfb98d426dc8f3510d291e84ea6e9668511a06a99bf3f','SOURCE6773_ORIGINS.json':'244a92888275732276f5fd9493979fea21a11e4be99fbaf792f6b80940fbc18e'}
    for name,pin in source_pins.items():demand(sha256((HERE/name).read_bytes()).hexdigest()==pin,'source pin '+name)
    a=scalar_fixture();b=coupled_fixture();fixtures=[('q1',a),('q2',b),('q2-reflected',reflect(b)),('q3',direct_sum(a,b)),('q4',direct_sum(b,reflect(b)))]
    reports=[];prefixes=None
    for name,f in fixtures:
        r,p=check(f,name);reports.append(r)
        if name=='q2':prefixes=p
    result=dict(status='PASS_SHARP_N4_FOUR_STAGE',fixtures=reports,hypothesis_and_omission_controls=controls(b,prefixes),fixture_sha256=PIN,scope='Finite exact fixtures and ordered reductions; universal lower bound is the written proof.')
    out=json.dumps(result,indent=2)+'\n';(HERE/'CHECK-RESULT.json').write_text(out);print(out,end='')
if __name__=='__main__':main()
