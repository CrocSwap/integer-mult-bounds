"""Independent eigenspace review by concurrent research agent A for @CubeJerry.
Substantial OpenAI GPT-6 Astra Pro assistance. Apache-2.0.
No author-model imports. Packaged from the completed independent review with
only relative input paths and output/report handling adapted by agent B.
"""
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path
import hashlib,json

HERE=Path(__file__).resolve().parent
AUTHOR=HERE.parent
N=20

def need(ok,msg):
    if not ok:raise ValueError(msg)

def identity(n):return [[Q(i==j) for j in range(n)] for i in range(n)]
def transpose(a):return [list(x) for x in zip(*a)]
def mm(a,b):return [[sum(x*y for x,y in zip(r,c)) for c in zip(*b)] for r in a]
def outer(x,y):return [[a*b for b in y] for a in x]
def add(a,b,c=1):return [[u+c*v for u,v in zip(r,s)] for r,s in zip(a,b)]
def dot(x,y):return sum(a*b for a,b in zip(x,y))
def e(j):return [Q(i==j) for i in range(N)]

def rref(a,width=None):
    width=len(a[0]) if a else width
    a=[[Q(x) for x in row] for row in a]
    piv=[]; row=0
    for col in range(width):
        pivot=next((i for i in range(row,len(a)) if a[i][col]),None)
        if pivot is None:continue
        a[row],a[pivot]=a[pivot],a[row]
        divisor=a[row][col];a[row]=[x/divisor for x in a[row]]
        for i in range(len(a)):
            if i!=row and a[i][col]:
                c=a[i][col];a[i]=[x-c*y for x,y in zip(a[i],a[row])]
        piv.append(col);row+=1
        if row==len(a):break
    return a[:row],piv

def nullspace(a):
    reduced,piv=rref(a,N)
    ans=[]
    for j in range(N):
        if j in piv:continue
        v=e(j)
        for row,p in zip(reduced,piv):v[p]=-row[j]
        ans.append(v)
    return ans

def rank(a):return len(rref(a,len(a[0]) if a else 0)[1])
def pairing(left,right):return rank([[dot(l,r) for r in right] for l in left])

I=identity(N)
A,E=e(0),e(19)
F=[Q(1<=i<=9) for i in range(N)]
H=[Q(10<=i<=18) for i in range(N)]
p=[Q((-1)**(i-1) if 1<=i<=9 else 0) for i in range(N)]
q=[Q((-1)**(i-10) if 10<=i<=18 else 0) for i in range(N)]
u=[f+h for f,h in zip(F,H)]
v=[a+f-h for a,f,h in zip(A,F,H)]
z=[-a+b-c for a,b,c in zip(A,p,q)]
w=[2*a-b+c for a,b,c in zip(A,p,q)]
P=add(outer(E,E),outer(v,z))
J=outer(u,w)
B=add(add(I,P,-2),J,-2)
R=add(I,P,-1)
full=[]
for j in range(9):
    x=[a+Q(i==1+j)+2*Q(1<=i<1+j) for i,a in enumerate(A)]
    y=[a-Q(i==1+j) for i,a in enumerate(A)]
    full.append((x,y))
for j in range(9):
    x=[-a+Q(i==10+j)+2*Q(10+j<i<=18) for i,a in enumerate(A)]
    y=[a+Q(i==10+j) for i,a in enumerate(A)]
    full.append((x,y))
thin=[([a+b for a,b in zip(u,E)],A),
      ([a-b for a,b in zip(u,v)],[a+b for a,b in zip(w,E)]),
      ([a-b-c for a,b,c in zip(u,v,E)],[2*a-b+c for a,b,c in zip(w,A,E)])]


def algebra():
    literal=I
    for x,y in thin:
        need(dot(y,x)==0,'nilpotent thin')
        literal=mm(add(I,outer(x,y),-2),literal)
    need(literal==B,'independent bridge closed form')
    root=I
    for x,y in full[:9]+thin+full[9:]:root=mm(add(I,outer(x,y),-2),root)
    need(root==add(I,I,-2),'complete twenty-dimensional source root')
    quotient_root=I
    for x,y in full[:9]+[(u,w)]+full[9:]:
        quotient_root=mm(add(I,outer(x,y),-2),quotient_root)
    need(quotient_root==add(add(I,I,-2),P,2),'nineteen-factor quotient root, identity on idle plane')
    need(mm(P,P)==P and rank(P)==2,'rank-two idle-plane projector')
    zero=[[Q(0)]*N for _ in range(N)]
    need(mm(J,J)==zero and rank(J)==1,'rank-one nilpotent Jordan remainder')
    need(mm(P,J)==zero and mm(J,P)==zero,'separate spectral summands')
    need(mm(mm(add(B,I),add(B,I,-1)),add(B,I,-1))==zero,'degree-three polynomial')
    need(rank(add(B,I))==18 and rank(add(B,I,-1))==3,'minus eigendim2 plus eigendim17')
    for k,(x,y) in enumerate(full):
        need(mm(P,[[a] for a in x])==[[Q(0)] for _ in range(N)] and
             mm([y],P)==[[Q(0)]*N],'full queries annihilate common idle plane')
        need(dot(w,x)==(1 if k<9 else -1) and dot(y,u)==(-1 if k<9 else 1),
             'full query forces nilpotent summand annihilation')
    minus=outer(v,z)
    need(mm(B,minus)==mm(minus,B),'minus carrier commutes whole bridge')
    need(mm(add(I,outer(*thin[0]),-2),minus)!=mm(minus,add(I,outer(*thin[0]),-2)),
         'minus carrier fails pointwise thin commutation')
    return {'right_minus_eigenspace_dimension':2,'right_plus_eigenspace_dimension':17,
            'generalized_plus_dimension':18,'nilpotent_remainder_rank':1,'source_root_checked':True,'quotient_root_checked':True,
            'minus_carrier_commutes_block_but_not_first_thin':True}


@lru_cache(None)
def capacity(a,b,mask,eigen=True):
    outside=[e(i) for i in range(N) if not(mask>>i&1)]
    image_constraints=[y for x,y in full[a:b+1]]+outside
    row_constraints=[x for x,y in full[a:b+1]]+outside
    if not(a<9<=b and eigen):
        return pairing(nullspace(row_constraints),nullspace(image_constraints))
    result=0
    for lam in (-1,1):
        eig=add(B,I,-lam)
        image=nullspace(image_constraints+eig)
        rows=nullspace(row_constraints+transpose(eig))
        result+=pairing(rows,image)
    return result


def masks(a,b):
    ms=[]
    for k in range(18):
        base={0,*range(1,k+2)} if k<9 else {0,*range(k+1,19)}
        if a<=k<=b:base=set(range(19))
        ms.append(sum(1<<i for i in base))
    return ms


def capacities():
    raw=(HERE/'capacity-reference.json').read_bytes()
    proposals=json.loads(raw)
    need(len(proposals)==81,'eighty-one author cases')
    intervals=[(a,b) for a in range(18) for b in range(a,18)]
    checked=0; changed=0; summaries=[]
    for case in proposals:
        a,b=case['a'],case['b'];ms=masks(a,b)
        actual=[]
        for c,d in intervals:
            mask=(1<<N)-1
            for s in ms[c:d+1]:mask&=s
            actual.append(capacity(c,d,mask))
        need(actual==case['caps'],'independent eigenspace capacity agreement '+str((a,b)))
        changed+=case['changed_count'];checked+=len(actual)
        summaries.append({'a':a,'b':b,'caps':actual})
    dense=(1<<19)-1
    need(capacity(8,9,dense,False)==17 and capacity(8,9,dense)==15,
         'bridge closure eliminates two falsely admitted directions')
    need(capacity(0,17,dense)==1,'full-span dense mask retains exactly one carrier')
    return {'cases':81,'intervals_per_case':171,'capacities_checked':checked,
            'cached_unique_queries':capacity.cache_info().currsize,
            'author_report_sha256':hashlib.sha256(raw).hexdigest(),
            'author_block_vs_pointwise_differences':changed,
            'dense_two_site_raw_capacity':17,'dense_two_site_bridge_capacity':15,
            'dense_full_span_bridge_capacity':1},summaries


def quotient():
    # Compress the ACTUAL rank-two active projectors, not only the larger
    # whole-target coordinate masks, to the eighteen-dimensional complement.
    records=[]; corrected=[]
    for j,(x,y) in enumerate(full):
        mask={0,*range(1,j+2)} if j<9 else {0,*range(j+1,19)}
        active=[[Q(i==k and i in mask) for k in range(N)] for i in range(N)]
        if j<9:
            for k in range(1,j+1):active=add(active,outer(e(k),[a-2*b for a,b in zip(e(k),A)]),-1)
        else:
            for k in range(j+2,19):active=add(active,outer(e(k),[a+2*b for a,b in zip(e(k),A)]),-1)
        need(mm(active,active)==active and rank(active)==2,'source active rank-two projector')
        compressed=mm(mm(R,active),R)
        defect=add(mm(compressed,compressed),compressed,-1)
        coefficient=Q((-1)**j) if j<9 else Q(-(-1)**(j-9))
        need(defect==[[coefficient*a*b for b in y] for a in x], 'explicit active-projector compression defect')
        need(rank(compressed)==2 and rank(defect)==1,'quotient active projector is not idempotent')
        repair=add(compressed,outer(x,y),-coefficient)
        need(mm(repair,repair)==repair and rank(repair)==2,'locally repaired quotient projector')
        need(mm(repair,outer(x,y))==outer(x,y) and mm(outer(x,y),repair)==outer(x,y),
             'repaired quotient projector retains the query')
        corrected.append(repair)
        records.append({'site':j,'compression_rank':2,'idempotence_defect_rank':1,
                        'defect_coefficient_times_Ri':str(coefficient),
                        'rank_two_projector_repair_verified':True})
    comm=add(mm(corrected[0],corrected[1]),mm(corrected[1],corrected[0]),-1)
    need(rank(comm)>0,'local projector repairs are not simultaneously coordinate')
    return {'projectors':records,'corrected_first_pair_commutator_rank':rank(comm),
            'limitation':'Raw compression fails, but a rank-one correction repairs each projector locally; a common productive target interface remains unresolved.'}


def main():
    a=algebra();c,details=capacities();q=quotient()
    result={'verdict':'PASS_INDEPENDENT_EIGENSPACE_CAPACITY_REVIEW','bridge':a,'capacity_review':c,
            'active_quotient_projector_defects':q,'capacities':details,
            'scope':'Fixed source, sector-independent idempotent carriers commuting the central bridge and annihilating each full query in their interval.'}
    expected=json.loads((HERE/'EXPECTED-GEOMETRY.json').read_text())
    need(result==expected,'independent geometry expected report')
    print(json.dumps({'verdict':result['verdict'],'bridge':a,'capacity_review':c,
                      'quotient_active_projectors_checked':len(q['projectors']),
                      'corrected_first_pair_commutator_rank':q['corrected_first_pair_commutator_rank']},indent=2))

if __name__=='__main__':main()
