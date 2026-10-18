"""Independent integer-rank replay of the all-term low-tariff case30 floor.

The producer, its output, and its rank helpers are not imported. This replay
uses 3H, primitive integer row elimination, and reverse-order mask enumeration.
"""
from pathlib import Path
from itertools import product
from math import gcd
from functools import reduce
from hashlib import sha256
import argparse,io,json,tarfile

HERE=Path(__file__).resolve().parent
CANDIDATE_HASH='dfb886d683dfef7b54ba582ebec5baf2cf84962915009fc28d8f9252fc8a7707'
CERTIFICATE_HASH='127260a387bef913d544558299946e61106012423aaf057b268149de75d2efe9'
PORTS=((10,18,93),(6,36,74),(13,23,102),(41,73,88),(30,50,87))
ARCHIVE='f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6'
MEMBER='candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json'
MEMBER_HASH='c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa'
def check(p,s):
    if not p:raise ValueError(s)
def irank(rows):
    pivots={}
    for row in rows:
        v=list(row)
        for p,w in sorted(pivots.items()):
            if v[p]:
                a,b=v[p],w[p];v=[b*x-a*y for x,y in zip(v,w)]
                d=reduce(gcd,v,0)
                if d:v=[x//d for x in v]
        p=next((j for j,x in enumerate(v) if x),None)
        if p is not None:
            d=reduce(gcd,v,0)*(1 if v[p]>0 else -1)
            pivots[p]=[x//d for x in v]
    return len(pivots)
def binary_rank(rows):
    piv={}
    for row in rows:
        while row:
            p=row.bit_length()-1
            if p not in piv:piv[p]=row;break
            row^=piv[p]
    return len(piv)
def run(repo):
    raw_candidate=(HERE/'CANDIDATE.json').read_bytes();raw_certificate=(HERE/'CERTIFICATE.json').read_bytes()
    check(sha256(raw_candidate).hexdigest()==CANDIDATE_HASH,'candidate pin')
    check(sha256(raw_certificate).hexdigest()==CERTIFICATE_HASH,'certificate pin')
    candidate=json.loads(raw_candidate);certificate=json.loads(raw_certificate)
    check(candidate['ports']==list(map(list,PORTS)) and candidate['payload_dimensions']==[3]*5 and candidate['endpoint']=='I15','candidate ports and endpoint')
    check(candidate['excluded_profile']=={'nonzero_rank_one_terms':16,'whole_group_tariff_histogram':{'1':2,'3':14}},'candidate profile')
    check(candidate['theorem']=={'term_count':'any finite number','maximum_per_term_whole_group_tariff':3,'minimum_total_invoice':45,'attained_by_direct_copies':True},'all-term theorem scope')
    raw=(repo/'research/community-frontier1094-audit/selected-replay.tar.gz').read_bytes()
    check(sha256(raw).hexdigest()==ARCHIVE,'archive pin')
    with tarfile.open(fileobj=io.BytesIO(raw)) as stream:physical=stream.extractfile(MEMBER).read()
    check(sha256(physical).hexdigest()==MEMBER_HASH,'member pin')
    recipes=json.loads(physical)['recipes'];labels={r['port']:r['q'] for r in recipes}
    check(len(recipes)==len(labels)==112 and len(set(labels.values()))==112,'label uniqueness')
    E=[[labels[p] for p in pp] for pp in PORTS];flat=sum(E,[])
    parity=lambda x,y:(x&y).bit_count()%2
    check(all(parity(x,y)==int(i==j) for e in E for i,x in enumerate(e) for j,y in enumerate(e)),'own physical identity')
    H=[[3*parity(x,y) for y in flat] for x in flat]
    for g in (0,2,3):
        for h in (0,2,3):
            if g!=h:
                for i in range(3*g,3*g+3):
                    for j in range(3*h,3*h+3):
                        check(H[i][j]==3,'triangle rank1 block');H[i][j]=1
    check(certificate['schema_version']==1 and certificate['auxiliary_dimension']==3 and certificate['matrix_denominator']==3,'certificate format')
    check(certificate['scaled_bilinear_matrix']==H,'independently regenerated scaled matrix')
    ix={s:[i for i in range(15) if s>>(i//3)&1] for s in range(1,32)}
    rho={};ranks={}
    for s,t in product(range(31,0,-1),repeat=2):
        rho[s,t]=binary_rank(sum(parity(flat[i],flat[j])<<k for k,j in enumerate(ix[t])) for i in ix[s])
        ranks[s,t]=irank([[H[i][j] for j in ix[t]] for i in ix[s]])
    check(all(rho[1<<g,1<<h]>0 for g in range(5) for h in range(5)),'strict endpointI15')
    cheap=sorted(st for st,c in rho.items() if c==1);regular=sorted(st for st,c in rho.items() if c==3)
    common=[(s,t) for s,t in regular if s&t]
    check(len(cheap)==14 and len(regular)==273 and len(common)==165,'full price domains')
    check(all(ranks[p]==1 for p in cheap),'cheap lift rank')
    check(all(ranks[p]<=3 for p in common),'common footprint domination')
    check(min(rho.values())==1 and sum(c==2 for c in rho.values())==20,'complete tariff0/2 domains')
    low_defects=sorted(st for st,c in rho.items() if c<=3 and ranks[st]>c)
    check(low_defects==[(9,20),(12,17),(17,12),(20,9)],'all low-tariff defects')
    check(all(rho[s,t]==3 and ranks[s,t]==4 and not(s&t) for s,t in low_defects),'four disjoint rank4 defects')
    check(certificate['low_tariff_exceptional_types']==list(map(list,low_defects)) and certificate['sharp_invoice_floor']==45,'all-term finite certificate')
    def crosses(p,q):return bool(p[0]&q[1]) and bool(q[0]&p[1])
    branches={};excluded_pairs=0
    for p in cheap:
        for q in cheap:
            if p>=q:continue
            if not crosses(p,q) or not any(crosses(t,p) and crosses(t,q) for t in common):
                excluded_pairs+=1;continue
            allowed=[t for t in regular if t[0]&t[1] or (crosses(t,p) and crosses(t,q))]
            exceptional=[t for t in allowed if ranks[t]>3]
            check(len(exceptional)<=1,'only one exceptional type per branch')
            if exceptional:
                s,t=exceptional[0]
                check(not(s&t) and ranks[s,t]==4,'rank4 squarezero type')
                # Two equal disjoint types force an I2 complement minor.
                check(irank([[1,0],[0,1]])==2,'rank1 projector disallows duplicate')
            branches[p,q]=exceptional
    check(len(branches)==21 and excluded_pairs==70,'complete91 cheap type pairs')
    exceptional=sorted((p,q,tuple(ex)) for (p,q),ex in branches.items() if ex)
    check(len(exceptional)==4,'exactly four rank-tight branches')
    check(sorted(ex[0] for ex in branches.values() if ex)==[(9,20),(12,17),(17,12),(20,9)],'exceptional types')
    check(certificate['expected_counts']=={'rectangles':961,'cost1_types':14,'cost3_types':273,'common_cost3_types':165,'cheap_pair_candidates':91,'branches':21,'direct_exclusions':17,'rank_tight_exclusions':4,'cost0_types':0,'cost2_types':20,'low_tariff_exceptional_types':4},'certificate counts')
    saved={(tuple(x['cheap_pair'][0]),tuple(x['cheap_pair'][1])):tuple(x['exceptional_type']) for x in certificate['exceptional_branches']}
    actual={(p,q):ex[0] for (p,q),ex in branches.items() if ex}
    check(saved==actual,'independently regenerated exceptional branches')
    # Diagonal I15 terms lift to 3I45, total rank45. Division by3 matters.
    check(all(H[3*g+i][3*g+j]==3*int(i==j) for g in range(5) for i in range(3) for j in range(3)),'lifted3I45')
    untuned=[[3*parity(x,y) for y in flat] for x in flat]
    check(irank([[untuned[i][j] for j in ix[5]] for i in ix[12]])==4 and ranks[12,5]==3,'mutation changes material rank')
    # Different integer control: tensor I2=E11+E22+E12-E12 with I4.
    X0=((1,0,1,-1),(0,1,0,0));Y0=((1,0),(0,1),(0,1),(0,1))
    X=[[X0[i//4][j//4]*int(i%4==j%4) for j in range(16)] for i in range(8)]
    Y=[[Y0[i//4][j//4]*int(i%4==j%4) for j in range(8)] for i in range(16)]
    mul=lambda A,B:[[sum(x*y for x,y in zip(a,b)) for b in zip(*B)] for a in A]
    check(mul(X,Y)==[[int(i==j) for j in range(8)] for i in range(8)],'tensor surplus endpoint')
    YX=mul(Y,X);P=[[int(i==j)-YX[i][j] for j in range(16)] for i in range(16)]
    check(irank(P)==8 and mul(P,P)==P,'integer surplus projector rank8')
    check([[P[i][j] for j in range(8,16)] for i in range(8,16)]==[[int(i==j) for j in range(8)] for i in range(8)],'two same-type rank4 blocks force I8')
    return {'status':'PASS','ports':PORTS,'physical_labels':E,'archive_sha256':ARCHIVE,'member_sha256':MEMBER_HASH,
            'rectangles':len(ranks),'cost0_types':0,'cost2_types':20,'low_tariff_exceptional_types':low_defects,'all_term_low_tariff_invoice_floor':45,'attaining_direct_invoice':45,'surplus_projector_control_rank':8,'cheap_pair_domain':91,'cheap_pairs_ruled_out_by_projector':excluded_pairs,
            'branches':21,'direct_rank_contradictions':17,'rank_tight_nilpotent_contradictions':4,
            'exceptional_branches':exceptional,'scope':'Any finite rational I15 frame on these five triads whose individual whole-group tariffs are at most 3 costs at least 45. Frames containing tariff4-or-higher terms and the global target remain outside this result.',
            'source_sha256':sha256(Path(__file__).read_bytes()).hexdigest()}
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--repo-root',type=Path,default=HERE.parents[1])
    args=parser.parse_args();print(json.dumps(run(args.repo_root),indent=2))
