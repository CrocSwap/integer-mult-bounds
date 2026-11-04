"""Small exact controls of the written uniform prefix rank-budget theorem.

thu-nmrc with substantial OpenAI Codex assistance, Apache-2.0.
Canonical query normal form and scalar triangle barrier: Ali Romman.
Finite controls corroborate conventions, not the unbounded proof.
"""
from fractions import Fraction as Q
from pathlib import Path
from hashlib import sha1,sha256
from itertools import combinations
import argparse,json
HERE=Path(__file__).resolve().parent
def need(ok,why):
    if not ok:raise ValueError(why)
def zero(m,n):return [[Q(0)for _ in range(n)]for _ in range(m)]
def eye(n):return [[Q(i==j)for j in range(n)]for i in range(n)]
def add(a,b,t=1):return [[x+t*y for x,y in zip(r,s)]for r,s in zip(a,b)]
def scale(a,t):return [[t*x for x in r]for r in a]
def mm(a,b):return [[sum(x*y for x,y in zip(r,c))for c in zip(*b)]for r in a]
def blockcols(xs):return [sum((list(x[i])for x in xs),[])for i in range(len(xs[0]))]
def blockrows(xs):return sum((list(x)for x in xs),[])
def rref(a):
    a=[[Q(x)for x in r]for r in a];m,n=len(a),len(a[0]);k=0;piv=[]
    for c in range(n):
        h=next((h for h in range(k,m)if a[h][c]),None)
        if h is None:continue
        a[k],a[h]=a[h],a[k];v=a[k][c];a[k]=[x/v for x in a[k]]
        for h in range(m):
            if h!=k and a[h][c]:
                v=a[h][c];a[h]=[x-v*y for x,y in zip(a[h],a[k])]
        piv.append(c);k+=1
        if k==m:break
    return a,piv
def rank(a):return len(rref(a)[1])
def inverse(a):
    n=len(a);out,piv=rref([r+s for r,s in zip(a,eye(n))]);need(piv[:n]==list(range(n)),'Invertible exact basis')
    need([r[:n]for r in out]==eye(n),'Exact inverse')
    return [r[n:]for r in out]
def tensor(a,q):return [[Q(a[i//q][j//q])*int(i%q==j%q)for j in range(len(a[0])*q)]for i in range(len(a)*q)]
def canonical(n,q):
    us=[];vs=[]
    for i in range(n+1):
        us.append(tensor([[int(j==i)if i<n else(-1)**(j+1)]for j in range(n)],q))
        vs.append(tensor([[(i>j)-(i<j)for j in range(n)]],q))
    return us,vs
def prefixes(us,vs):
    I=eye(len(us[0]));out=[];B=I
    for u,v in zip(us,vs):B=mm(add(I,mm(u,v),-2),B);out.append(B)
    return out
def nonzero(a):return any(any(r)for r in a)
def poly_mul(a,b):
    d=len(next(iter(a.values())));out={}
    for i,x in a.items():
        for j,y in b.items():
            k=tuple(s+t for s,t in zip(i,j));out[k]=add(out.get(k,zero(d,d)),mm(x,y))
    return {k:v for k,v in out.items()if nonzero(v)}
def stage_word(us,vs,ps,minus):
    d=len(us[0]);I=eye(d);z=(0,0,0);out={z:I}
    for i,(u,v)in enumerate(zip(us,vs)):
        t=add(I,mm(u,v),-2)if minus else I
        if i in ps:
            axis,P=ps[i];key=tuple(int(j==axis)for j in range(3))
            call={z:mm(add(I,P,-1),t),key:mm(P,t)}
        else:call={z:t}
        out=poly_mul(call,out)
    return out
def stable(v):
    if isinstance(v,Q):return str(v)
    if isinstance(v,dict):return {str(k):stable(x)for k,x in v.items()}
    if isinstance(v,list):return [stable(x)for x in v]
    return v
def check():
    sources=json.loads((HERE/'SOURCES.json').read_text())
    for source in sources['sources']:
        raw=(HERE/source['copy']).read_bytes()
        need(len(raw)==source['size']and sha256(raw).hexdigest()==source['sha256'],'Pinned predecessor including notices')
        need(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==source['git_blob'],'Original Git blob')
    src=sources['local_counterexample'];raw=(HERE/src['copy']).read_bytes()
    need(sha256(raw).hexdigest()==src['sha256']and len(raw)==src['size'],'Pinned local13 necessary control')
    # The dimension identity is a coefficient identity, not an enumeration.
    def lin(**kw):return kw
    def total(*parts):
        out={}
        for a in parts:
            for k,v in a.items():out[k]=out.get(k,0)+v
        return {k:v for k,v in out.items()if v}
    R=lin(c=3,a01=2,a02=2,a12=2,b0=1,b1=1,b2=1)
    minusW=lin(c=-1,a01=-1,a02=-1,a12=-1,b0=-1,b1=-1,b2=-1)
    need(not total(R,minusW,lin(c=-1,a01=-1),lin(c=-1,a02=-1),lin(a12=-1)),
         'Exact formal identity R-W=t01+t02+a12')
    center=[];triples=[]
    for q in [1,2,3,4]:
        us,vs=canonical(4,q);bs=prefixes(us,vs)
        A=blockcols([us[2],mm(bs[2],us[2])]);C=blockrows([vs[2],mm(vs[2],bs[2])])
        need(rank(A)==rank(C)==2*q and mm(C,A)==zero(2*q,2*q),'Uniform middle-site image/row closure control')
        center.append({'q':q,'column_rank':2*q,'row_rank':2*q,'pairing_rank':0,'rank_floor':4*q})
        for inds in combinations(range(5),3):
            U=blockcols([us[i]for i in inds]);V=blockrows([vs[i]for i in inds])
            need(rank(U)==rank(V)==3*q and rank(mm(V,U))==2*q,'All three-site Sylvester hypotheses')
        triples.append({'q':q,'all10_triples_column_row_rank':3*q,'all10_Gram_ranks':2*q})
    # Exact sharp family: the displayed q1 construction tensored with Iq.
    H1=[[1,1,1,0],[1,2,2,1],[0,1,2,1],[0,0,0,1]];sharp=[]
    masks={0:3,1:7,4:9}
    for q in [1,2,3,4]:
        cu,cv=canonical(4,q);H=tensor(H1,q);Hi=inverse(H)
        us=[mm(H,u)for u in cu];vs=[mm(v,Hi)for v in cv];bs=prefixes(us,vs);I=eye(4*q)
        ps={i:(axis,tensor([[int(a==b and mask>>a&1)for b in range(4)]for a in range(4)],q))
            for axis,(i,mask)in enumerate(masks.items())}
        need(bs[-1]==scale(I,-1),'Sharp full shortest tuple')
        for u,v in zip(us,vs):
            R=mm(u,v);need(mm(R,R)==zero(4*q,4*q)and rank(R)==q,'All five sharp queries rank-q and square-zero')
        for i,(axis,P)in ps.items():
            R=mm(us[i],vs[i]);need(mm(R,R)==zero(4*q,4*q)and rank(R)==q,'Sharp rank-q square-zero query')
            need(mm(P,R)==mm(R,P)==R and mm(P,bs[i])==mm(bs[i],P),'Actual selected compatibility and prefix condition')
        for (_,P),(_,Qp)in combinations(ps.values(),2):need(mm(P,Qp)==mm(Qp,P),'Sharp projectors commute')
        need([rank(P)for _,P in ps.values()]==[2*q,3*q,2*q],'Sharp rank budget7q')
        plus=stage_word(us,vs,ps,False);minus=stage_word(us,vs,ps,True)
        expected={};row_masks=[(1,1,1),(1,1,0),(0,1,0),(0,0,1)]
        for i,mask in enumerate(row_masks):
            a=expected.setdefault(mask,zero(4*q,4*q))
            for j in range(q):a[i*q+j][i*q+j]=1
        need(plus==expected and minus=={k:scale(v,-1)for k,v in expected.items()},'Literal independent3-stage central-character endpoint')
        sharp.append({'q':q,'rank_budget':7*q,'projector_ranks':[2*q,3*q,2*q],'prefix_commutator_ranks':[0,0,0],
                      'independent_stage_masks':['ABC','AB','B','C'],'nonzero_endpoint_monomials':len(expected),
                      'matrix_entry_positions':(4*q)**2,'all_five_query_ranks':q,'all_inputs':4*q})
    # Missing-prefix counterexample is replayed independently as matrices.
    c=json.loads(raw);Rs=[[[Q(x)for x in r]for r in a]for a in c['queries']]
    Ps=[[[Q(x)for x in r]for r in a]for a in c['projectors']];U=[[Q(x)for x in r]for r in c['U']];V=[[Q(x)for x in r]for r in c['V']]
    need(rank(U)==rank(V)==6 and rank(mm(V,U))==4,'Counterexample genuinely independent')
    gram=[[Q(((i//2>j//2)-(i//2<j//2))*int(i%2==j%2))for j in range(6)]for i in range(6)]
    need(mm(V,U)==gram,'All selected counterexample Gram entries')
    need([rank(P)for P in Ps]==[4,4,5],'Individual counterexample ranks')
    for i,P in enumerate(Ps):
        need(mm(P,P)==P,'Counterexample idempotence')
        Ui=[r[2*i:2*i+2]for r in U];Vi=V[2*i:2*i+2]
        need(mm(Ui,Vi)==Rs[i],'Counterexample selected factors match full queries')
    for P,Qp in combinations(Ps,2):need(mm(P,Qp)==mm(Qp,P),'Counterexample projectors really commute')
    product=eye(8);comm=[]
    for i,R in enumerate(Rs):
        need(rank(R)==2 and mm(R,R)==zero(8,8),'All counterexample queries retained')
        product=mm(add(eye(8),R,-2),product)
        if i<3:
            need(mm(Ps[i],R)==mm(R,Ps[i])==R,'Counterexample compatibility')
            comm.append(rank(add(mm(Ps[i],product),mm(product,Ps[i]),-1)))
    need(product==scale(eye(8),-1)and comm==[0,4,4]and sum(rank(P)for P in Ps)==13,'Actual prefix failure preventsfalse7q contradiction')
    # Drop the sharp middle's one extra direction: this fails compatibility.
    cu,cv=canonical(4,1);Hi=inverse([[Q(x)for x in r]for r in H1]);R1=mm(mm(H1,mm(cu[1],cv[1])),Hi)
    bad=[[Q(int(i==j and i<2))for j in range(4)]for i in range(4)]
    need(mm(bad,R1)!=R1 or mm(R1,bad)!=R1,'Dropping the charged middle idle direction is rejected')
    return {'schema':'uniform-coupled-prefix-stage-rank-budget/1','status':'PASS_EXACT_CONTROLS_FOR_WRITTEN_UNIFORM_THEOREM',
            'theorem':'n4, every q>=1, characteristic!=2: three commuting compatible full projectors satisfying actualprefixcommutation have rank sum>=7q; sharp.',
            'boundary_lemma':'Any even n>=4; any commuting full triple containing sites0,1 or n-1,n with prefixconditions has rank sum>=7q.',
            'symbolic_dimension_identity':'R-W=t01+t02+a12; t01>=2q,t02>=q,W>=4q implyR>=7q.',
            'center_controls':center,'shortest_triple_controls':triples,'sharp_controls':sharp,
            'missing_prefix_control':{'q':2,'rank_sum':13,'projector_ranks':[4,4,5],'idempotent':True,'commuting':True,
                                      'selected_factors_match':True,'prefix_commutator_ranks':comm,'full_product':'-I8','both_UV_ranks':6},
            'mutation_control':'Dropping the sharp middle charged direction breaks actualcompatibility.',
            'scope':'Written dimension proof establishes allq; finite rational controls corroborate. No native physicalphase, callerinvoice, kappa, externalreview or scientificacceptance claim.',
            'credit':'Scalar barrier/basic rank lemma and complete coupled normalform retain AliRomman/source credit. New prefix stage-rank budget and bounded controls: thu-nmrc with substantial OpenAI Codex assistance.'}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();result=check();path=HERE/'RESULT.json'
    if a.write:path.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    else:need(result==json.loads(path.read_text()),'Frozen controls')
    print(json.dumps({'status':result['status'],'sharp_controls':len(result['sharp_controls']),'local13_prefix':result['missing_prefix_control']['prefix_commutator_ranks']},sort_keys=True))
