#!/usr/bin/env python3
"""Independent structural/accounting audit of the selected joint construction.

Chafik Boukhalfa with OpenAI Codex assistance, Apache-2.0. Does not repeat
the separate full source/dirty-response pass or the interval calculations.
Those independent results are bound as evidence, not claimed as work here.
"""
from pathlib import Path
from collections import Counter,defaultdict
from fractions import Fraction as Q
from hashlib import sha256
from functools import lru_cache
import argparse,gzip,json,pickle,sys

if sys.flags.optimize:raise RuntimeError('Assertions must be enabled')
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--selected',type=Path,required=True)
p.add_argument('--certificate',type=Path,required=True)
p.add_argument('--out',type=Path,required=True)
a=p.parse_args();S=a.selected.resolve()
read=lambda path:json.loads(path.read_text())
g=pickle.loads((S/'inputs/FRAMES.pkl').read_bytes())
matches=json.loads(gzip.decompress((S/'inputs/BIRTH_MATCHES.json.gz').read_bytes()))
ids=read(S/'inputs/TERMINAL_ROLES.json');inventory=read(S/'inventory.json')
profile=read(S/'complex-profile.json');bill=read(S/'READOUT_COST.json')
oldbill=read(S/'inputs/READOUT_COST.json');physical=read(S/'physical-audit.json')
certificate=read(a.certificate);rows={r['role']:r for r in inventory['selected']}
assert set(ids)==set(rows)and len(ids)==len(set(ids))
assert len({row['target']for row in rows.values()})==len(ids)
donors={r['donor']for r in matches['pairs']};births={r['recipient']for r in matches['pairs']}
assert len(donors)==len(births)==len(matches['pairs'])
assert not donors&births and not set(ids)&(donors|births)
v,h=g['v'],g['h'];m=h*h;rep=2*v
@lru_cache(None)
def inside(A,B):
    for x in A:
        for r in B:
            if x>>(r.bit_length()-1)&1:x^=r
        if x:return False
    return True
def basis(rows):
    piv={}
    for x in rows:
        for k in sorted(piv,reverse=True):
            if x>>k&1:x^=piv[k]
        if x:
            k=x.bit_length()-1
            for j in piv:
                if piv[j]>>k&1:piv[j]^=x
            piv[k]=x
    return tuple(piv[k]for k in sorted(piv,reverse=True))
def nondeg(F):
    return len(basis(sum(((x&y).bit_count()&1)<<j for j,y in enumerate(F))for x in F))==len(F)
H=Counter(g['histogram'])
for r in matches['pairs']:
    donor,birth=r['donor'],r['recipient'];A,F=tuple(r['donor_frame']),tuple(r['birth_frame'])
    assert A==g['U'][g['holds'][donor][-1]] and F==g['placed'][birth]
    assert donor not in g['placed']and donor not in g['terminal']
    assert g['last'][donor]in g['phase']and birth not in g['touched']and g['first'][birth]>v
    assert inside(A,F)and nondeg(A)and nondeg(F)
    e,s=len(A),len(F);assert (e,s)==(r['e'],r['s'])
    H[h-e]-=rep;H[m-h+s]-=rep
    if s>e:H[s-e]+=rep
assert {r:n for r,n in H.items()if n}=={int(r):n for r,n in matches['child_histogram'].items()}
incoming=defaultdict(list);outgoing=Counter()
for i,(op,s,t,x)in enumerate(g['ops']):
    if op==0:continue
    dst,src=(s,t)if op==1 else(t,s)
    incoming[dst].append((i,src,x));outgoing[src]+=1
for role,row in rows.items():
    assert role in g['terminal']and not outgoing[role]
    assert role not in g['touched']and g['first'][role]>v
    assert incoming[role]and all(i not in g['phase']for i,_,_ in incoming[role])
    target=row['target'];F0=g['U'][incoming[role][0][2]];sigma=g['placed'][role]
    M=max((g['placed'][s]for s in g['bytarget'][target]),key=len)
    assert sigma==M==F0 and len(sigma)==row['sigma']==row['M']==row['F0']
    assert g['reach'][role]==1<<target
    assert row['incoming_operations']==[i for i,_,_ in incoming[role]]
    packet=[m-h+len(sigma),1,0,h-1-len(sigma)]
    assert row['old_packet']==packet and sum(packet)==m
    for r in packet:
        if r:H[r]-=rep
assert all(n>=0 for n in H.values())
H={r:n for r,n in H.items()if n}
assert H=={int(r):n for r,n in profile['child_multiplicities'].items()}
R=len(g['first'])-len(births)-len(ids);W=2*v*v+rep*R;mass=sum(r*n for r,n in H.items())
assert R==profile['R']==26216 and W==profile['W']==114315520
assert mass==profile['total_rank']==65843877440 and m*W-mass==1862080
direct=sum(len(incoming[s])for s in ids)
assert direct==bill['terminal_direct_updates']==1167
assert bill['local_scalar_upper']==oldbill['local_scalar_upper']+29*direct
assert bill['global_scalar_group_upper']==16*(rep*bill['local_scalar_upper']+8*v*v)==3116113870848
assert oldbill['denominator']==bill['denominator']==42 and abs(Q(1,42))<=1
assert oldbill['max_abs_numerator']==55 and 55*Q(1,42)==Q(55,42)
def no_float(x):
    if isinstance(x,float):raise AssertionError('Float entered canonical certificate')
    if isinstance(x,dict):
        for y in x.values():no_float(y)
    if isinstance(x,list):
        for y in x:no_float(y)
no_float(certificate)
assert len(certificate['assembly']['constraints'])==47 and len(certificate['assembly']['margins'])==7
assert all(Q(x)>0 for x in certificate['assembly']['constraints'].values())
assert all(Q(x)>Q(certificate['kappa'])for x in certificate['assembly']['margins'].values())
assert Q(certificate['kappa'])==Q(112802185097556,10**18)
pins={str(p.resolve()):sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),a.certificate,S/'inputs/FRAMES.pkl',S/'inputs/BIRTH_MATCHES.json.gz',S/'inputs/TERMINAL_ROLES.json',S/'inventory.json',S/'complex-profile.json',S/'READOUT_COST.json',S/'inputs/READOUT_COST.json',S/'physical-audit.json']}
result=dict(status='PASS independent selected liveness, disjoint packets, complete paid profile and conservative scalar bill audit',
    source_and_input_sha256=pins,births=len(births),terminals=len(ids),physical_roles=R,W=W,total_rank=mass,
    selected_kappa=certificate['kappa'],all_selected_packet_frames_equal=True,
    terminal_direct_updates=direct,global_scalar_upper=bill['global_scalar_group_upper'],
    coefficient_realization='Each old response numerator uses |n| same-frame shears of coefficient +/-1/42; each direct terminal update uses 21 such shears and eight bookkeeping groups. No new role or frame incidence is required.',
    canonical_certificate_has_no_float=True,all47_constraints_and7_margins_strict=True,
    separate_evidence='The package producer independently performs exact source/dirty response passes, both orientations, three mutants and all packet hinges. The arithmetic auditor independently encloses both moments by two methods. Their source-bound receipts are separate from this audit.',
    metadata_observation='The historical scalar input bill has deferred_readout_terms=9732 from its old placement. That diagnostic is not used in this upper bill proof. Selected virtual support is11884 terms and retained support after terminal removal is11503; current output should name inherited and current counts distinctly.',
    inherited_hypotheses=['Paid all-size complex residual and copied-center realization, including fixed common odd-grid and scalar guard interfaces','Stopped product-ring row reserves, balanced positional layout, exact recovery and eventual analytic thresholds'],
    scope='Finite selected construction and exact accounting only. No independent all-size proof or global kappa-optimality claim.')
a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(result['status'])
