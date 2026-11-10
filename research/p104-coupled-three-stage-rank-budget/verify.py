"""Small exact controls of the all-even-n uniform prefix rank-budget theorem.

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
def prior_n4_controls():
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
def row_prefix(n,i):return [[Q(j<=i)for j in range(n)]]
def row_tail(n,i):return [[Q(j>i)for j in range(n)]]
def column(n,i):return [[Q(j==i)]for j in range(n)]
def alt_column(n,i):return [[Q((-1)**j if j<=i else 0)]for j in range(n)]
def sharp_basis(n):
    need(n>=4 and n%2==0,'Even dimension for sharp basis')
    H=zero(n,n);first=[[1,1,0,0],[1,2,1,0],[1,2,2,0]]
    for j,c in enumerate(first):
        for i,x in enumerate(c):H[i][j]=x
    for j in range(3,n):
        for i,x in enumerate([0,1,1,1]):H[i][j]=x
    for j in range(3,n-1):H[j+1][j]=1;H[j+1][n-1]=-(-1)**(j+1)
    return H
def formal_commutator_identity():
    # Ordered free words: no matrix variables are commuted.
    def product(a,b):
        out={}
        for x,s in a.items():
            for y,t in b.items():out[x+y]=out.get(x+y,0)+s*t
        return {k:v for k,v in out.items()if v}
    def plus(*parts):
        out={}
        for a,m in parts:
            for k,v in a.items():out[k]=out.get(k,0)+m*v
        return {k:v for k,v in out.items()if v}
    def comm(a,b):return plus((product(a,b),1),(product(b,a),-1))
    ei={('Ei',):1};ej={('Ej',):1};fi={('Fi',):1};fj={('Fj',):1};pi=plus((ei,1),(fi,1));pj=plus((ej,1),(fj,1))
    need(not plus((comm(ei,ej),1),(comm(pi,pj),-1),(comm(pi,fj),1),(comm(fi,ej),1)),
         'Exact ordered identity [Ei,Ej]=[Pi,Pj]-[Pi,Fj]-[Fi,Ej]')
def check():
    prior=prior_n4_controls();formal_commutator_identity();fixtures=[]
    for n,q in [(4,1),(4,2),(6,1),(6,2),(6,3),(8,1),(8,2),(10,1),(12,1)]:
        us,vs=canonical(n,q);bs=prefixes(us,vs);d=n*q;I=eye(d)
        need(bs[-1]==scale(I,-1),'Complete shortest source tuple')
        odds={};even_count=0;endpoint_closures=0
        for i in range(n):
            ai=tensor(alt_column(n,i),q);ei=us[i];hall=tensor([[1]*n],q)
            J=tensor([[Q(a==b)*(1 if a>i else-1)for b in range(n)]for a in range(n)],q)
            need(bs[i]==add(J,mm(ai,hall),2),'Uniform closed prefix formula')
            if i%2==0 and i:
                A=blockcols([ei,ai]);C=blockrows([tensor(row_prefix(n,i-1),q),tensor(row_tail(n,i),q)])
                need(rank(A)==rank(C)==2*q and mm(C,A)==zero(2*q,2*q),'Every even interior full stage costs4q')
                even_count+=1
            if i%2:
                hi=tensor(row_prefix(n,i),q);vi=vs[i];E=add(mm(ei,hi),mm(ai,vi))
                A=blockcols([ei,ai]);C=blockrows([hi,vi])
                need(mm(C,A)==eye(2*q),'Odd minimal closure has nondegenerate pairing')
                need(mm(E,E)==E and rank(E)==2*q,'Uniform minimal odd projector')
                Ri=mm(ei,vi);need(mm(E,Ri)==mm(Ri,E)==Ri and mm(E,bs[i])==mm(bs[i],E),'Odd compatibility and prefix invariance')
                need(mm(bs[i],ei)==add(scale(ei,-1),ai,2)and mm(vi,bs[i])==add(scale(vi,-1),hi,2),'Odd closure forces Ei below every admissible Pi')
                odds[i]=E
                far=([0]if i>=3 else[])+([n]if i<=n-3 else[])
                need(far,'Every odd site has at least one far endpoint')
                for j in far:
                        Aend=blockcols([us[j],mm(E,us[j])]);Cend=blockrows([vs[j],mm(vs[j],E)])
                        need(rank(Aend)==rank(Cend)==2*q and mm(Cend,Aend)==zero(2*q,2*q),'Far endpoint zero-pair closure for every odd site')
                        endpoint_closures+=1
        pair_count=0
        for i,j in combinations(odds,2):
            ai=tensor(alt_column(n,i),q);aj=tensor(alt_column(n,j),q);hi=tensor(row_prefix(n,i),q)
            tj=tensor(add([[int(k==j)for k in range(n)]],row_tail(n,j)),q)
            need(mm(odds[i],odds[j])==scale(mm(ai,tj),-1),'Uniform ordered EiEj formula')
            need(mm(odds[j],odds[i])==mm(add(us[j],aj),hi),'Uniform ordered EjEi formula')
            need(rank(add(mm(odds[i],odds[j]),mm(odds[j],odds[i]),-1))==2*q,'Every two odd minimal projectors have commutatorrank2q')
            pair_count+=1
        H0=sharp_basis(n);H=tensor(H0,q);Hi=inverse(H)
        # Exact unimodular column-reduction recipe, with no determinant inference.
        reduced=[r.copy()for r in H0]
        for j in range(3,n-1):
            w=(-1)**(j+1)
            for a in range(n):reduced[a][n-1]+=w*reduced[a][j]
        for j in range(3,n-1):
            for a in range(n):reduced[a][j]-=reduced[a][n-1]
        order=[0,1,2,n-1,*range(3,n-1)];reduced=[[r[j]for j in order]for r in reduced]
        expected=zero(n,n);H4=[[1,1,1,0],[1,2,2,1],[0,1,2,1],[0,0,0,1]]
        for a in range(n):
            for b in range(n):expected[a][b]=H4[a][b]if a<4 and b<4 else Q(a==b)if a>=4 and b>=4 else Q(0)
        need(reduced==expected,'Uniform unimodular all-n sharp basis reduction')
        uu=[mm(H,u)for u in us];vv=[mm(v,Hi)for v in vs];bb=prefixes(uu,vv)
        ps={i:(axis,tensor([[Q(a==b and a<4 and mask>>a&1)for b in range(n)]for a in range(n)],q))
            for axis,(i,mask)in enumerate([(0,3),(1,7),(n,9)])}
        need(bb[-1]==scale(I,-1),'All-n sharp full query product')
        for u,v in zip(uu,vv):
            R=mm(u,v);need(rank(R)==q and mm(R,R)==zero(d,d),'All sharp queries rankq and square-zero')
        for i,(axis,P)in ps.items():
            R=mm(uu[i],vv[i]);need(mm(P,R)==mm(R,P)==R and mm(P,bb[i])==mm(bb[i],P),'All-n sharp actualprefix and compatibility')
        need([rank(P)for _,P in ps.values()]==[2*q,3*q,2*q],'All-n sharp rank budget7q')
        for (_,P),(_,Qp)in combinations(ps.values(),2):need(mm(P,Qp)==mm(Qp,P),'All-n sharp selectedprojectors commute')
        plus=stage_word(uu,vv,ps,False);minus=stage_word(uu,vv,ps,True);wanted={}
        for block in range(n):
            mask=[(1,1,1),(1,1,0),(0,1,0),(0,0,1)][block]if block<4 else(0,0,0)
            A=wanted.setdefault(mask,zero(d,d))
            for t in range(q):A[block*q+t][block*q+t]=1
        need(plus==wanted and minus=={k:scale(v,-1)for k,v in wanted.items()},'Literal all-n three-independent-stage endpoint')
        fixtures.append({'n':n,'q':q,'even_interior_rank4q_controls':even_count,'odd_minimal_projectors':len(odds),
                         'odd_commutator_rank2q_controls':pair_count,'far_endpoint_closures':endpoint_closures,
                         'sharp_projector_ranks':[2*q,3*q,2*q],'sharp_fullsites':[0,1,n],
                         'nonzero_endpoint_monomials':len(wanted),'matrix_entry_positions':d*d,
                         'sharp_endpoint':'S diag(ABC,AB,B,C,I_(n-4)) tensor Iq','unimodular_basis':True})
    # Concrete n6 next-gate witness; the extra four arrays are independent,
    # with zero stage selectors, rather than initialized zero data.
    c=json.loads((HERE/'inputs/LOCAL13.json').read_text());U=[[Q(x)for x in r]for r in c['U']];V=[[Q(x)for x in r]for r in c['V']]
    P=[[Q(x)for x in r]for r in c['projectors'][2]]
    Uordered=blockcols([[[r[2],r[3]]for r in U],[[r[4],r[5]]for r in U],[[-r[0],-r[1]]for r in U]])
    Vordered=blockrows([V[2:4],V[4:6],scale(V[0:2],-1)])
    z=[[Q(x)]for x in[1,0,0,0,1,0]];payload=mm(Uordered,z)
    need(mm(P,payload)==zero(8,1)and mm(Vordered[2:4],P)==Vordered[2:4],'N6 target lost source combination')
    U12=Uordered+zero(4,6);V12=[r+[Q(0)]*4 for r in Vordered];P12=zero(12,12)
    for a in range(8):
        for b in range(8):P12[a][b]=P[a][b]
    need(rank(U12)==rank(V12)==6 and rank(P12)==5,'Four additional independent zero-selector coordinates')
    need(nonzero(mm(U12,z))and mm(P12,mm(U12,z))==zero(12,1)and mm(V12[2:4],P12)==V12[2:4],
         'Literal12-dimensional target prefix obstruction with nonzero payload')
    cu,cv=canonical(6,2);B=prefixes(cu,cv)[3];Uc=blockcols([cu[0],cu[3],cu[6]])
    need(mm(cv[3],mm(Uc,z))==zero(2,1),'Own-query compatibility alone does not expose n6 obstruction')
    need(mm(cv[3],mm(B,mm(Uc,z)))==[[Q(2)],[Q(0)]],'Actual n6 prefix exposes forbidden response2e0')
    # Check the endpoint-defect numerical implication; written two cases
    # e>=q and e<=q prove every nonnegative real/integer parameter.
    for q in range(1,129):
        for e in range(3*q+1):need(e+max(0,2*q-2*e)>=q,'One far endpoint defect inequality implies totalextra>=q')
    return {'schema':'all-even-coupled-prefix-stage-rank-budget/1','status':'PASS_EXACT_CONTROLS_FOR_ALL_EVEN_WRITTEN_THEOREM',
            'theorem':'Every even n>=4 and q>=1, characteristic!=2: any three pairwisecommuting compatible full projectors with actualprefixcommutation in a shortest n+1-query tuple have totalrank>=7q; sharp.',
            'fixtures':fixtures,'prior_n4_controls':prior,'freeword_commutator_identity':True,
            'endpoint_defect_inequality_q_controls':128,
            'n6_local13_next_gate':{'target_P_endpoints_payload_zero':True,'source_zerothmoment':[0,0],'source_firstprefixmoment':[2,0],
                                  'verdict':'No prefix-compatible embedding of this fixed local model with four extra independent zero-selector coordinates.'},
            'scope':'Written uniform proof establishes alln/allq; finite exact controls corroborate. No physicalnative, paidprice, kappa, externalreview or scientificacceptance claim.',
            'credit':'Ali Romman scalar obstruction/forcedoddclosure/basicranklemma/completecouplednormalform and all-length fixed alternating-interior/curvature/lowrankcommutator tools retained; prior PR6717 n4 result retained. New arbitrary3 mixedrank7q all-even application via extra-rank and endpoint-leakage combination, with explicit alln attainment: thu-nmrc with substantial OpenAI Codex assistance.'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();result=check();path=HERE/'RESULT.json'
    if a.write:path.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    else:need(result==json.loads(path.read_text()),'Frozen controls')
    print(json.dumps({'status':result['status'],'all_even_fixtures':len(result['fixtures']),'n6_local13':result['n6_local13_next_gate']['verdict']},sort_keys=True))
