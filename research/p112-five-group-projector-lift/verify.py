"""Solver-free sharp cost-45 floor for arbitrary low-tariff case30 frames.

No producer imports or writes. Physical labels are authenticated from the retained
archive. All finite term counts are covered when each whole-group tariff is at most 3.
"""
from pathlib import Path
from fractions import Fraction as F
from itertools import combinations
from hashlib import sha256
import argparse, io, json, tarfile, time

HERE=Path(__file__).resolve().parent
PORTS=[[10,18,93],[6,36,74],[13,23,102],[41,73,88],[30,50,87]]
PINS={'candidate':'dfb886d683dfef7b54ba582ebec5baf2cf84962915009fc28d8f9252fc8a7707',
      'certificate':'127260a387bef913d544558299946e61106012423aaf057b268149de75d2efe9',
      'archive':'f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6',
      'member':'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa'}
MEMBER='candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json'

def need(p,m):
    if not p:raise ValueError(m)

def auth(raw,pin):
    need(sha256(raw).hexdigest()==pin,'authenticated input SHA256')
    return raw

def qrank(matrix):
    rows=[[F(x) for x in row] for row in matrix]
    if not rows:return 0
    k=0
    for j in range(len(rows[0])):
        p=next((i for i in range(k,len(rows)) if rows[i][j]),None)
        if p is None:continue
        rows[k],rows[p]=rows[p],rows[k];scale=rows[k][j]
        rows[k]=[v/scale for v in rows[k]]
        for i in range(k+1,len(rows)):
            scale=rows[i][j]
            if scale:rows[i]=[a-scale*b for a,b in zip(rows[i],rows[k])]
        k+=1
        if k==len(rows):break
    return k

def brank(rows):
    piv={}
    for x in rows:
        while x:
            j=(x&-x).bit_length()-1
            if j in piv:x^=piv[j]
            else:piv[j]=x;break
    return len(piv)

def dot(x,y):return sum(a*b for a,b in zip(x,y))
def product(A,B):return [[dot(a,b) for b in zip(*B)] for a in A]
def transpose(A):return list(map(list,zip(*A)))
def indices(mask):return [j for j in range(15) if mask>>(j//3)&1]
def rectangle(H,s,t):return [[H[i][j] for j in indices(t)] for i in indices(s)]

def read_geometry(repo):
    candidate=json.loads(auth((HERE/'CANDIDATE.json').read_bytes(),PINS['candidate']))
    need(candidate['ports']==PORTS and candidate['payload_dimensions']==[3]*5 and candidate['endpoint']=='I15','literal package candidate')
    need(candidate['excluded_profile']=={'nonzero_rank_one_terms':16,'whole_group_tariff_histogram':{'1':2,'3':14}},'literal excluded profile')
    need(candidate['theorem']=={'term_count':'any finite number','maximum_per_term_whole_group_tariff':3,'minimum_total_invoice':45,'attained_by_direct_copies':True},'all-term low-tariff theorem scope')
    raw=auth((repo/'research/community-frontier1094-audit/selected-replay.tar.gz').read_bytes(),PINS['archive'])
    with tarfile.open(fileobj=io.BytesIO(raw)) as stream:
        member=stream.extractfile(MEMBER);need(member is not None,'exact archive member')
        physical=auth(member.read(),PINS['member'])
    recipes=json.loads(physical)['recipes'];q={r['port']:r['q'] for r in recipes}
    need(set(q)==set(range(112)) and len(set(q.values()))==112,'112 distinct labels')
    E=[[q[p] for p in group] for group in PORTS]
    need(len(set(sum(PORTS,[])))==15,'disjoint selected ports')
    need(all(((x&y).bit_count()&1)==int(i==j) for group in E for i,x in enumerate(group) for j,y in enumerate(group)),'orthonormal physical triads')
    union=[[x for g in range(5) if s>>g&1 for x in E[g]] for s in range(32)]
    price=[[brank(sum((((x&y).bit_count()&1)<<j) for j,y in enumerate(B)) for x in A) for B in union] for A in union]
    need(all(price[1<<g][1<<h]>0 for g,h in combinations(range(5),2)),'all cross endpoints constrained')
    return E,price

def lift(u,v,H):
    # Index physical group, payload coordinate, auxiliary coordinate.
    out=[[F(0)]*45 for _ in range(45)]
    for g in range(5):
        for h in range(5):
            for a in range(3):
                for b in range(3):
                    c=u[3*g+a]*v[3*h+b]
                    if c:
                        for x in range(3):
                            for y in range(3):out[9*g+3*a+x][9*h+3*b+y]=c*H[3*g+x][3*h+y]
    return out

def support(v):return sum(1<<g for g in range(5) if any(v[3*g:3*g+3]))

def unit(j,n=15):return [F(i==j) for i in range(n)]

def controls(H,price,bad_types):
    eye=[[F(i==j) for j in range(45)] for i in range(45)]
    total=[[F(0)]*45 for _ in range(45)]
    for j in range(15):
        A=lift(unit(j),unit(j),H)
        need(qrank(A)==3,'direct factor lifted rank3')
        total=[[x+y for x,y in zip(a,b)] for a,b in zip(total,A)]
    need(total==eye,'literal I45 endpoint')
    nilpotents=[]
    for s,t in bad_types:
        u=[F((1,2,-3)[i%3],2) if s>>(i//3)&1 else F(0) for i in range(15)]
        v=[F((2,-1,4)[i%3],3) if t>>(i//3)&1 else F(0) for i in range(15)]
        A=lift(u,v,H)
        need(support(u)==s and support(v)==t and qrank(A)==4,'mixed rational exceptional exact rank4')
        need(not any(any(row) for row in product(A,A)),'exceptional square zero')
        need(A!=product(A,A),'exceptional not idempotent')
        nilpotents.append([s,t])
    # A genuine rational redundant frame with arbitrary cross-group mixing.
    a=[F(0)]*15;a[0]=F(1);a[6]=F(2)
    t=[F(0)]*15;t[0]=F(1,2);t[9]=F(-1,3)
    U=[unit(j) for j in range(15)]+[a]
    V=[[F(i==j)-a[j]*t[i] for i in range(15)] for j in range(15)]+[t]
    endpoint=[[sum(u[i]*v[j] for u,v in zip(U,V)) for j in range(15)] for i in range(15)]
    need(endpoint==[[F(i==j) for j in range(15)] for i in range(15)],'rational frame exact I15')
    P=[[F(i==j)-dot(V[i],U[j]) for j in range(16)] for i in range(16)]
    need(qrank(P)==1 and product(P,P)==P,'rank1 complementary projector fixture')
    total=[[F(0)]*45 for _ in range(45)]
    charges=[]
    for u,v in zip(U,V):
        s,t=support(u),support(v);A=lift(u,v,H)
        need(qrank(A)==qrank(rectangle(H,s,t)),'injective mixed factor lift')
        total=[[x+y for x,y in zip(a,b)] for a,b in zip(total,A)];charges.append(price[s][t])
    need(total==eye and sum(charges)>=45,'rational positive fixture not claimed cost44')
    # Equality of rank-sum can hold for nonorthogonal idempotents.
    X=[[F(1),F(1,2),F(0)],[F(0),F(1),F(1,3)],[F(0),F(0),F(1)]]
    Y=[[F(1),F(-1,2),F(1,6)],[F(0),F(1),F(-1,3)],[F(0),F(0),F(1)]]
    need(product(X,Y)==[[F(i==j) for j in range(3)] for i in range(3)],'invertible tight fixture')
    for j in range(3):
        A=[[X[i][j]*Y[j][k] for k in range(3)] for i in range(3)]
        need(product(A,A)==A and qrank(A)==1,'tight summand is idempotent')
    need(qrank([[1,0],[0,1]])==2,'duplicate disjoint type projector obstruction')
    original=[row[:] for row in H]
    for g,h in ((0,2),(0,3),(2,0),(2,3),(3,0),(3,2)):
        for i in range(3*g,3*g+3):
            for j in range(3*h,3*h+3):original[i][j]=1
    need(qrank(rectangle(original,12,5))==4 and qrank(rectangle(H,12,5))==3,'division by3 is material')
    corrupt=[row[:] for row in H];corrupt[0][0]=2
    need(corrupt[:3]!=H[:3] and lift(unit(0),unit(0),corrupt)!=lift(unit(0),unit(0),H),'own-block mutation changes lifted identity')
    # Sharp repeated-type surplus projector: I2 = E11+E22+E12-E12.
    X=[[F(1),F(0),F(1),F(-1)],[F(0),F(1),F(0),F(0)]]
    Y=[[F(1),F(0)],[F(0),F(1)],[F(0),F(1)],[F(0),F(1)]]
    need(product(X,Y)==[[1,0],[0,1]],'surplus control endpoint')
    YX=product(Y,X);P=[[F(i==j)-YX[i][j] for j in range(4)] for i in range(4)]
    need(qrank(P)==2 and product(P,P)==P,'surplus control projector rank')
    need([[P[i][j] for j in (2,3)] for i in (2,3)]==[[1,0],[0,1]],'same disjoint type I2 block')
    return {'baseline_invoice':45,'rational_positive_invoice':sum(charges),'nilpotent_rank4_controls':nilpotents,
            'controls':['same-type surplus projector','literal I45','mixed rational redundant frame','exact factor-lift ranks','rank1 projector','tight idempotents','duplicate projector rank2','critical division by3','own-block mutation']}

def run(repo):
    start=time.monotonic();E,price=read_geometry(repo);labels=sum(E,[])
    H=[[F((x&y).bit_count()&1) for y in labels] for x in labels]
    for g,h in combinations((0,2,3),2):
        need(all(H[i][j]==1 for i in range(3*g,3*g+3) for j in range(3*h,3*h+3)),'triangle all-ones crossblock')
        for i in range(3*g,3*g+3):
            for j in range(3*h,3*h+3):H[i][j]=H[j][i]=F(1,3)
    cert=json.loads(auth((HERE/'CERTIFICATE.json').read_bytes(),PINS['certificate']))
    need(cert['schema_version']==1 and cert['auxiliary_dimension']==3 and cert['matrix_denominator']==3,'certificate format')
    need(cert['scaled_bilinear_matrix']==[[int(3*x) for x in row] for row in H],'literal scaled lift matrix')
    need(all(H[3*g+i][3*g+j]==int(i==j) for g in range(5) for i in range(3) for j in range(3)),'own I3 blocks')
    lifted={(s,t):qrank(rectangle(H,s,t)) for s in range(1,32) for t in range(1,32)}
    cheap=[(s,t) for s,t in lifted if price[s][t]==1]
    regular=[(s,t) for s,t in lifted if price[s][t]==3]
    common=[(s,t) for s,t in regular if s&t]
    need((len(cheap),len(regular),len(common))==(14,273,165),'complete type counts')
    need(all(not(s&t) for s,t in cheap),'every cheap type has disjoint supports')
    need(all(lifted[x]<=1 for x in cheap),'all cost1 dominated')
    need(all(lifted[x]<=3 for x in common),'all common-footprint cost3 dominated')
    cost2=[x for x in lifted if price[x[0]][x[1]]==2]
    need(len(cost2)==20 and all(price[s][t]>=1 for s,t in lifted),'all nonzero tariff domains including zero/2')
    low_bad=sorted((s,t) for s,t in lifted if price[s][t]<=3 and lifted[s,t]>price[s][t])
    need(low_bad==[(9,20),(12,17),(17,12),(20,9)],'complete all-term low-tariff exceptional catalogue')
    need(all(not(s&t) and price[s][t]==3 and lifted[s,t]==4 for s,t in low_bad),'four disjoint rank4 excess1 rectangles')
    need(cert['low_tariff_exceptional_types']==list(map(list,low_bad)) and cert['sharp_invoice_floor']==45,'all-term certificate data')
    branches=[]
    for p,q in combinations(cheap,2):
        if not(p[0]&q[1] and q[0]&p[1]):continue
        comp=[(s,t) for s,t in common if s&p[1] and s&q[1] and t&p[0] and t&q[0]]
        if not comp:continue
        zero=[(s,t) for s,t in regular if not s&t and s&p[1] and s&q[1] and t&p[0] and t&q[0]]
        bad=[(s,t) for s,t in zero if lifted[s,t]>3]
        need(len(bad)<=1 and all(lifted[x]==4 for x in bad),'at most one exceptional type, excess1')
        branches.append({'cheap_pair':[list(p),list(q)],'compatible_zero_footprint':list(map(list,zero)),
                         'exceptional_types':list(map(list,bad)),
                         'exclusion':'rank-tight nonzero square-zero summand' if bad else 'rank sum at most44'})
    need(len(branches)==21,'complete cheap-pair branch count')
    exceptional=sorted({tuple(x) for b in branches for x in b['exceptional_types']})
    need(exceptional==[(9,20),(12,17),(17,12),(20,9)],'exact exceptional four types')
    need(all(not(s&t) for s,t in exceptional),'every exceptional type is square-zero by support')
    need(sum(bool(b['exceptional_types']) for b in branches)==4,'17 direct and4 tight exclusions')
    need(cert['exceptional_branches']==[{'cheap_pair':b['cheap_pair'],'exceptional_type':b['exceptional_types'][0]} for b in branches if b['exceptional_types']],'literal exceptional branch certificate')
    need(cert['expected_counts']=={'rectangles':961,'cost1_types':14,'cost3_types':273,'common_cost3_types':165,'cheap_pair_candidates':91,'branches':21,'direct_exclusions':17,'rank_tight_exclusions':4,'cost0_types':0,'cost2_types':20,'low_tariff_exceptional_types':4},'certificate coverage counts')
    ctl=controls(H,price,exceptional)
    return {'status':'PASS','ports':PORTS,'physical_labels':E,'pins':PINS,
            'lift_matrix':[[str(x) for x in row] for row in H],'lift_full_rank':qrank(H),
            'rectangles_checked':961,'cost0_types':0,'cost2_types':20,'low_tariff_exceptional_types':low_bad,'all_term_low_tariff_invoice_floor':45,'cost1_types':14,'cost3_types':273,'common_cost3_types':165,
            'branches':branches,'all_21_branches_excluded':True,'controls':ctl,'seconds':time.monotonic()-start,
            'scope':'Any finite rational I15 decomposition on these five triads with every nonzero term tariff at most 3 has total invoice at least 45, attained by direct copies. Higher individual tariffs and the global P112 target remain outside this result.'}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--repo-root',type=Path,default=HERE.parents[1])
    args=ap.parse_args();out=run(args.repo_root)
    print(json.dumps({k:v for k,v in out.items() if k not in ('lift_matrix','branches')},indent=2))
