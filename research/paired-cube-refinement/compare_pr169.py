#!/usr/bin/env python3
"""Independently check PR169's bit profile and compare equal paid suppliers.

PR169: Joel Pulikkan/GamingPuzzled, with Anthropic Claude assistance;
Apache-2.0, based on PR168 and PR165. Comparison prepared with OpenAI Codex.
"""
import argparse
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
REFERENCE=HERE/'references/pr169'
FRAMES=ROOT/'research/paired-cube-bit-descent'
sys.dont_write_bytecode=True
if hasattr(sys,'set_int_max_str_digits'):sys.set_int_max_str_digits(0)
sys.path.insert(0,str(FRAMES));sys.path.insert(0,str(HERE))
from arithmetic import certificate as arithmetic_certificate,js
from paid_moment import require
from plan_validation import validate_plan


def digest(path):return sha256(path.read_bytes()).hexdigest()


def build():
    require(not sys.flags.optimize,'Run without optimization')
    source=json.loads((REFERENCE/'SOURCE.json').read_text())
    require(source['pr_commit']=='4895ba1104cedc7908b6d6ba64fdd6290e0ed7ae','PR169 source commit')
    require(source['base_commit']=='98c115b53742b6613ad630de4d493f37b0119da7','common PR168 base')
    require({p:digest(REFERENCE/p) for p in source['files']}==source['files'],'PR169 snapshot source drift')
    from word import Candidate
    from prime_check import certificate as prime_certificate
    plan=json.loads((REFERENCE/'replacement-frames.json').read_text())
    published=json.loads((REFERENCE/'bit-profile.json').read_text())
    print('Checking PR169 geometry, physical chains and paid inventory.',file=sys.stderr,flush=True)
    candidate=Candidate(plan=plan);validate_plan(plan,len(candidate.ops));candidate.exact_frames();row=candidate.row()
    for key in row:require(js(row[key])==published[key],'PR169 checked profile mismatch '+key)
    outside=sum(not candidate.C.sub(candidate.opframe[i],candidate.nf[candidate.ops[i][2]]) for i in candidate.changed_frames)
    require(outside==published['frames_not_contained_in_original'],'PR169 changed-subspace count')
    primes=prime_certificate(REFERENCE/'replacement-frames.json')
    require(primes['total_operation_frames']==row['changed_operation_frames'],'PR169 determinant coverage')
    print('Checking every PR169 bit source, target and dirty column.',file=sys.stderr,flush=True)
    formal=[candidate.formal(r) for r in (2,0)]
    print('Pricing both complete profiles with identical refined suppliers and transfer.',file=sys.stderr,flush=True)
    theirs=arithmetic_certificate(row,comparisons=False)
    selected=json.loads((HERE/'certificate.json').read_text())
    ours=arithmetic_certificate(selected['bit']['profile'],comparisons=False)
    require(ours['kappa']==Q(selected['kappa']),'selected kappa reproduction')
    require(js(ours['paid_moment'])==selected['arithmetic']['paid_moment'],'selected paid moment reproduction')
    require(js(ours['assembly'])==selected['arithmetic']['assembly'],'selected assembly reproduction')
    require(ours['kappa']>theirs['kappa']>Q(source['published_kappa']),'strict matched and published improvements')
    def summary(receipt,profile):
        return dict(kappa=receipt['kappa'],coarse_saving=receipt['paid_moment']['coarse_saving'],
                    ordinary_saving=receipt['paid_moment']['ordinary_saving'],
                    complex_saving=receipt['assembly']['complex_saving'],atom_beta=receipt['paid_moment']['atom_beta'],
                    changed_operation_frames=profile['changed_operation_frames'],
                    edge_count=sum(profile['child_histogram'].values()),W=profile['W_per_vertex'],
                    rank=profile['rank_per_vertex'],deficit=profile['deficit_per_vertex'],
                    constraints=47,margins=7)
    return js(dict(status='PASS independent PR169 finite bit replay and matched arithmetic comparison',
                   pr169_commit=source['pr_commit'],common_base_commit=source['base_commit'],
                   pr169_published_kappa=Q(source['published_kappa']),pr169_refined=summary(theirs,row),
                   selected_refined=summary(ours,selected['bit']['profile']),
                   absolute_gain_over_published=ours['kappa']-Q(source['published_kappa']),
                   relative_gain_over_published_percent=100*(ours['kappa']/Q(source['published_kappa'])-1),
                   absolute_matched_gain=ours['kappa']-theirs['kappa'],
                   relative_matched_gain_percent=100*(ours['kappa']/theirs['kappa']-1),
                   pr169_formal=formal,pr169_prime_summary={k:v for k,v in primes.items() if k!='frame_witnesses'},
                   source_sha256=dict(reference_manifest=digest(REFERENCE/'SOURCE.json'),
                                      upstream_certificate=source['upstream_certificate_sha256'],
                                      selected_certificate=digest(HERE/'certificate.json')),
                   scope='PR169 original scalar sources equal PR168. Its supplied bit plan, complete profile, prime compatibility and all formal bit columns are independently checked here. Both profiles use exactly the same refined paid envelope, atom rule, complex supplier and balanced transfer. Inherited all-size assumptions remain unchanged; no practical speedup claim.'))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--write',action='store_true');args=parser.parse_args()
    record=build();path=HERE/'pr169-comparison.json'
    text=json.dumps(record,indent=2,sort_keys=True)+'\n'
    if args.write:path.write_text(text,encoding='utf-8',newline='\n')
    else:require(path.read_text(encoding='utf-8')==text,'PR169 comparison receipt drift')
    print('PASS PR169 matched comparison: '+record['pr169_refined']['kappa']+' < '+record['selected_refined']['kappa'])
