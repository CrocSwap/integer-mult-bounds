"""Exact conditional P104 consumer audit; no producer code imported.

Prepared for Vasek with OpenAI Codex assistance. Apache-2.0.
The covered contract and analytic implications are in README.md.
"""
from collections import Counter
from fractions import Fraction as Q
from math import factorial
from pathlib import Path
import copy
import hashlib
import json
import sys

P=Path(__file__).resolve().parent
ROOT=P.parents[1]
M,W,NF,ND=73,832,5,4
FORGIVE=416


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    def unique(items):
        value={}
        for key,item in items:
            need(key not in value,'duplicate JSON key')
            value[key]=item
        return value
    return json.loads(path.read_text(encoding='utf-8'),object_pairs_hook=unique)


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)


def input_path(relative):
    if relative == 'certificates/selected-result.json':
        return P/'inputs/SELECTED-AT-BASE.json'
    return ROOT/relative


def authenticate():
    for root,name,key in ((ROOT,'SOURCES.json','path'),(P,'PREDECESSORS.json','local')):
        for pin in read(P/name)['files']:
            if pin.get('usage') == 'provenance' and pin.get(key) != 'certificates/selected-result.json':
                continue
            raw=(input_path(pin[key]) if root == ROOT else root/pin[key]).read_bytes()
            need(hashlib.sha256(raw).hexdigest() == pin['sha256'],'source SHA256: '+pin[key])
            blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
            need(blob == pin['git_blob'],'source Git blob: '+pin[key])


def basis(values):
    pivots={}
    for v in values:
        need(type(v) is int and 0 < v < 512,'frame vector domain')
        while v:
            bit=v.bit_length()-1
            if bit not in pivots:
                pivots[bit]=v
                break
            v ^= pivots[bit]
    for bit in sorted(pivots):
        for high in pivots:
            if high>bit and (pivots[high]>>bit)&1:
                pivots[high] ^= pivots[bit]
    return tuple(pivots[bit] for bit in sorted(pivots,reverse=True))


def forward_word(base,circuit,raw_base):
    need(hashlib.sha256(raw_base).hexdigest()==circuit['source_witness_sha256'],'forward insertion source binding')
    result=copy.deepcopy(base)
    for end in ('initial_frames','final_frames'):
        need(not(set(base[end]) & set(circuit[end])),'new helper namespace')
        result[end].update(copy.deepcopy(circuit[end]))
    insertions={}
    for insertion in circuit['insertions']:
        cut=insertion['completed_cut']
        need(type(cut) is int and 0<=cut<=len(base['program']) and cut not in insertions,'insertion cut')
        insertions[cut]=insertion['events']
    result['program']=[]
    for cut in range(len(base['program'])+1):
        result['program'].extend(copy.deepcopy(insertions.get(cut,[])))
        if cut<len(base['program']):
            result['program'].append(copy.deepcopy(base['program'][cut]))
    return result


def census(word):
    initial={role:basis(frame) for role,frame in word['initial_frames'].items()}
    frames=dict(initial)
    counts,profile=Counter(),Counter()
    descents=0
    for e in word['program']:
        op,role=e[:2]
        counts[op]+=1
        if op=='transport':
            u,v=basis(e[2]),basis(e[3])
            need(frames[role]==u and basis(u+v) in (u,v),'transport chronology/nesting')
            rank=abs(len(v)-len(u))
            need(type(e[4]) is int and e[4]==rank and 0<rank<=9,'declared intrinsic rank')
            profile[rank]+=1
            descents+=len(v)<len(u)
            frames[role]=v
        elif op=='add':
            need(role!=e[2] and frames[role]==frames[e[2]]==basis(e[4]),'common ADD frame')
            Q(e[3])
        elif op=='sign':
            need(e[2]=='-1' and frames[role]==basis(e[3]),'sign frame')
        elif op=='zero':
            need(role=='C' and role not in frames,'private allocation')
            frames[role]=basis(e[2])
        elif op=='copy':
            need(role=='C' and frames[role]==frames[e[2]]==basis(e[3]),'COPY frame')
        elif op=='erase':
            need(role=='C' and frames[role]==basis(e[2]),'private erasure frame')
            del frames[role]
        else:
            raise ValueError('unknown instruction')
    final={role:basis(frame) for role,frame in word['final_frames'].items()}
    need(frames==final and set(initial)==set(final),'public final boundary')
    role_types=Counter()
    progress=0
    for role,start in initial.items():
        finish=final[role]
        kind='X' if role.startswith('X') else 'Y' if role.startswith('Y') else 'dirty'
        dimensions={'X':(1,9),'Y':(0,8),'dirty':(0,9)}[kind]
        need((len(start),len(finish))==dimensions and basis(start+finish)==finish,'persistent boundary type')
        role_types[kind]+=1
        progress+=len(finish)-len(start)
    need(role_types=={'X':104,'Y':104,'dirty':150},'public role inventory')
    need(progress==3014 and counts['zero']==counts['erase']==8,'boundary/lifetime count')
    return dict(events=len(word['program']),operations=dict(sorted(counts.items())),
                profile={str(r):profile[r] for r in sorted(profile)},
                rank_mass=sum(r*n for r,n in profile.items()),
                persistent_endpoint_progress=progress,role_types=dict(sorted(role_types.items())),
                descending_transports=descents,
                program_sha256=hashlib.sha256(canonical(word['program']).encode()).hexdigest())


def consumer(forward,dual,kappa,primitive):
    need(forward['persistent_endpoint_progress']==dual['persistent_endpoint_progress']==3014,'fixed credited boundary')
    profile=Counter({int(r):NF*n for r,n in forward['profile'].items()})
    profile.update({int(r):ND*n for r,n in dual['profile'].items()})
    original=dict(sorted(profile.items()))
    original_mass=sum(r*n for r,n in profile.items())
    remaining=(M-1)*W-(NF+ND)*3014
    need(remaining==32778,'remaining coverage')
    need(profile[1]>=ND*FORGIVE,'available optimistic H1 discount')
    profile[1]-=ND*FORGIVE
    mass=sum(r*n for r,n in profile.items())
    need(mass==27854 and max(profile)==8,'audited discounted shape')
    deficit=M*W-mass-remaining
    slope=4*profile[1]+2*sum(r*n for r,n in profile.items() if r>1)
    need(deficit==104,'zero-saving slack')
    lower={}
    for label,a in (('selected_kappa',kappa),('selected_primitive',primitive)):
        need(0<a<1,'saving domain')
        numerator=slope*a-deficit
        need(numerator>0,'consumer not rejected by this bound')
        lower[label]=dict(a=str(a),moment_strictly_above=str(1+numerator/(M*W)),
                          numerator_margin=str(numerator),
                          minimum_additional_unpaid_units_for_this_guard_to_stop_rejecting=numerator.numerator//numerator.denominator+1)
    return dict(original_profile={str(r):n for r,n in original.items()},
                discounted_profile={str(r):profile[r] for r in sorted(profile)},
                original_local_mass=original_mass,discounted_local_mass=mass,
                remaining_coverage_mass=remaining,
                raw_zero_saving_ratio=str(Q(original_mass+remaining,M*W)),
                discounted_zero_saving_ratio=str(Q(mass+remaining,M*W)),
                log_slope=slope,lower_bounds=lower,
                bank_extension='For every finite integer B>=0: M_B(a)>1+(slope*a-104)/(73*(832+B)). Banks earn no unpaid-coordinate credit and do not rewrite the fixed profiled calls.')


def elementary_bounds(primitive):
    # e = 1+1+1/2 + tail from 1/3!. Subsequent ratios are at most 1/4.
    e_upper=Q(5,2)+Q(1,6)/(1-Q(1,4))
    need(e_upper<Q(11,4),'exp1 upper bound')
    need(Q(11,4)**4<73 and Q(11,4)**2<Q(73,8),'coarse log lower bounds')
    # A profile-only witness to materiality of the no-resynthesis premise.
    # Each forward mass3070 =341*9+1; each discounted dual3126=347*9+3.
    coarse={1:17,9:3093}
    need(sum(r*n for r,n in coarse.items())==27854,'coarsening preserves mass')
    upper_logs={1:Q(9,2),9:Q(17,8)}
    partials={r:sum(L**j/factorial(j) for j in range(11)) for r,L in upper_logs.items()}
    for r,L in upper_logs.items():
        need(partials[r]>Q(M,r),'finite Taylor logarithm upper bound')
        need(0<primitive*L<1,'geometric exponential upper domain')
    # exp(x)<=1/(1-x) for0<=x<1 by termwise series comparison.
    upper=(sum(Q(r*n,M)/(1-primitive*upper_logs[r]) for r,n in coarse.items())+Q(32778,M))/W
    need(upper<1,'scope witness must pass the optimistic profile screen')
    uniform_a=Q(1,580)
    need(primitive<uniform_a and all(uniform_a*L<1 for L in upper_logs.values()),'uniform witness domain')
    uniform_upper=(sum(Q(r*n,M)/(1-uniform_a*upper_logs[r]) for r,n in coarse.items())+Q(32778,M))/W
    need(uniform_upper<1,'uniform scope witness must pass')
    return dict(e_upper=str(e_upper),log_lower_claims=['ln(73)>4','ln(73/r)>2 for integer2<=r<=8'],
                scope_witness=dict(profile={str(r):n for r,n in coarse.items()},local_mass=27854,
                    construction='5*(341H9+H1) +4*(347H9+3H1)',
                    log_upper={str(r):str(L) for r,L in upper_logs.items()},
                    taylor_degree=10,taylor_lower={str(r):str(v) for r,v in partials.items()},
                    selected_primitive=str(primitive),moment_upper=str(upper),
                    uniform_a_max=str(uniform_a),uniform_moment_upper=str(uniform_upper),
                    scope='Abstract same-mass profile only, with fractional rank73 remainder; no realizable circuit, owner packing, or supplier is supplied. Not permitted by the fixed-profile rank-deletion contract.'))


def recompute():
    authenticate()
    raw=(ROOT/'research/p104-native-channel/inputs/LOWRANK-WITNESS.json').read_bytes()
    forward=forward_word(read(ROOT/'research/p104-native-channel/inputs/LOWRANK-WITNESS.json'),read(P/'inputs/PR2458-CIRCUIT.json'),raw)
    words={'forward2458':forward,'dual2712':read(P/'inputs/PR2712-WORD.json'),'dual2725':read(P/'inputs/PR2725-WORD.json')}
    censuses={name:census(word) for name,word in words.items()}
    expected={'forward2458':(1216,74,86,104,48,42,68,8),'dual2712':(1498,60,74,92,58,56,92,8),'dual2725':(1502,58,74,93,57,56,91,9)}
    for name,counts in expected.items():
        need(censuses[name]['profile']=={str(i+1):n for i,n in enumerate(counts)},'source-derived profile')
    selected=read(input_path('certificates/selected-result.json'))
    assembly_path=ROOT/selected['certificate']
    need(selected['certificate']=='research/community-frontier1094-audit/ASSEMBLY.json','selected certificate path')
    need(hashlib.sha256(assembly_path.read_bytes()).hexdigest()==selected['certificate_sha256'],'selected certificate digest')
    assembly=read(assembly_path)
    need(selected['kappa']==assembly['kappa'],'selected kappa binding')
    kappa,primitive=Q(assembly['kappa']),Q(assembly['complex_lower'])
    need(0<kappa<primitive<1,'benchmarks are distinct')
    bills={name:consumer(censuses['forward2458'],censuses[name],kappa,primitive) for name in ('dual2712','dual2725')}
    need(bills['dual2712']['lower_bounds']['selected_kappa']['moment_strictly_above']=='7594999831115139259129/7592000000000000000000','Discussion fraction independently reproduced')
    return dict(schema_version=1,status='PASS_P104_CONSUMER_BUDGET_AUDIT',
                contract=dict(width=M,original_families=W,forward_calls=NF,dual_calls=ND,
                    unpaid_per_original_family=1,maximum_original_progress_per_call=3014,
                    rank_deletion_per_dual=FORGIVE,remaining_child_rank_cap=M,
                    scope='Fixed profiled calls, per-child integer rank deletion only; no other fusion, resynthesis, shared children or additional unpaid bank coordinates.'),
                censuses=censuses,bills=bills,elementary_bounds=elementary_bounds(primitive),
                boundary='Conditional consumer rejection, not a native/owner construction or a universal P104 obstruction. Scalar inverse-transpose identities are separately checked; physical recipes remain inherited.')


def main():
    need(sys.argv[1:] in ([],['--emit']),'usage: verify.py [--emit]')
    result=recompute()
    if sys.argv[1:]:
        print(json.dumps(result,indent=2))
    else:
        need(canonical(result)==canonical(read(P/'RESULT.json')),'typed receipt mismatch')
        print(result['status'])


if __name__=='__main__':
    main()
