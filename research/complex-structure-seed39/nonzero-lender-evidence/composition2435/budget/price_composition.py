#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Price the explicitly conditional PR2435 entrance + FOUR428 composition.

Prepared for Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
Credits Jeremy Kothe (@jeremykothe2), PR2435, for the 24 entrance raises.
This is a favorable accounting screen, not a construction or kappa claim.
"""
from collections import Counter, defaultdict
from fractions import Fraction as Q
import argparse
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RESEARCH = ROOT.parent
ENGINE = RESEARCH/'face-hoist-evidence/budget/inherited/vendor/moment.py'
RAISED = {474,475,476,477,486,487,488,489,522,523,524,525,526,527,528,529,534,535,536,537,538,539,540,541}
DELTA = {1:24,2:120,3:-96}
COMPARISON = Q('0.001698511343697629')
PINS = {
    ROOT/'budget/RESTRICTED-OWNERS.json.gz': 'cbc1b15a63288d64432d0548774b83526ae1d196b5a6594c0d8f0f4f0418d847',
    ROOT/'FOUR-CANDIDATE.json': '71dd95ccf4d8ef2e0122befc14ab17a1703bff3e6f2eafe23068dc7e7ca5e80f',
    RESEARCH/'anticipatory-stage-evidence/parent/new/PLAN.json': 'bf1abd33c8ba946371cae37e021747343ef6603a31297bcc962197cc23f535e2',
    ROOT/'composition2435/vendor/new/borrow/inputs/entrance_43base.json': '1b3c09f9558c50e7f299aa10fb21dcbd1b5ff397794838d8629c80d4c7a565f5',
    ENGINE: '81cbc864e106418fc7854322746f72180cb8110ff39f74450a3b8d55a82c1482',
}

def need(ok, message):
    if not ok:
        raise ValueError(message)

def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)

def integer_counter(obj):
    return Counter({int(k):v for k,v in obj.items()})

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path)
    args = ap.parse_args()
    need(__debug__, 'optimized Python unsupported')
    for path, expected in PINS.items():
        need(hashlib.sha256(path.read_bytes()).hexdigest() == expected, 'source pin mismatch')
    entrance = read(ROOT/'composition2435/vendor/new/borrow/inputs/entrance_43base.json')
    need({int(k) for k,v in entrance['fields']['start_extra'].items() if len(v)==2} == RAISED, 'entrance object mismatch')
    plan = read(RESEARCH/'anticipatory-stage-evidence/parent/new/PLAN.json')
    roles = read(ROOT/'budget/RESTRICTED-OWNERS.json.gz')
    rows = {r['provider']:r for r in read(ROOT/'FOUR-CANDIDATE.json')['cases'] if r['baseline']=='high48'}
    dispatch = Counter(c['provider'] for c in plan['provider_calls'])
    need(dispatch == {'gauge44':249,'extra':417}, 'dispatch changed')
    need((plan['live'],plan['deficit'],plan['M']) == (66304,23680,73), 'geometry changed')
    bins = defaultdict(list)
    for row in roles:
        bins[row['owner_replica'],row['child'],row['port']].append(row)
    profiles = {}; inventories = {}
    for tag,row in rows.items():
        profile = integer_counter(row['local_profile'])
        for rank,n in DELTA.items():
            profile[rank] += n
        widths = integer_counter(row['width_inventory'])
        widths[8] -= 24; widths[7] += 24
        need(sum(r*n for r,n in profile.items()) == 5304, 'conditional local mass')
        need(sum(w*n for w,n in widths.items()) == 3448, 'conditional helper width')
        need(sum(widths.values()) == 428, 'helper count')
        profiles[tag] = profile; inventories[tag] = widths
    residuals = {}; global_profiles = {}; changed_bins = 0
    for changed in (False, True):
        idle = Counter(); changed_roles = 0
        for key,(capacity,_) in plan['windows'].items():
            owner,child = map(int,key.split(','))
            for port in range(112):
                entries = bins[owner,child,port]
                used = sum(row['width'] for row in entries)
                if changed:
                    local_raised = sum(row['origin_helper'] in RAISED for row in entries)
                    need(all(row['width']==8 for row in entries if row['origin_helper'] in RAISED), 'raised width is not eight')
                    used -= local_raised
                    changed_roles += local_raised
                    changed_bins += bool(local_raised)
                need(0 <= used <= capacity, 'bin overflow')
                if capacity-used:
                    idle[capacity-used] += 1
        H = Counter(idle)
        for tag,n in dispatch.items():
            p = profiles[tag] if changed else integer_counter(rows[tag]['local_profile'])
            H.update({r:n*c for r,c in p.items()})
        need(73*66304-sum(r*n for r,n in H.items()) == 23680, 'global mass deficit changed')
        if changed:
            need(changed_roles == 24*666, 'not every raised helper retained exactly once')
        else:
            need(H == integer_counter(read(ROOT/'budget/RESTRICTED-PROFILE.json')), 'baseline global profile')
            need(idle == integer_counter(read(ROOT/'budget/RESTRICTED-IDLE.json')), 'baseline idle profile')
        residuals[str(changed)] = dict(sorted(idle.items()))
        global_profiles[str(changed)] = dict(sorted(H.items()))
    spec = importlib.util.spec_from_file_location('composition_moment', ENGINE)
    engine = importlib.util.module_from_spec(spec); spec.loader.exec_module(engine)
    result = {}
    for changed,H in global_profiles.items():
        bracket = engine.certify(H,73,66304,bad=True)
        lo,hi = engine.moment(H,73,66304,COMPARISON,bad=True)
        result[changed] = dict(root_lower=bracket['lower'],root_upper=bracket['upper'],
            lower_endpoint_residual_upper=bracket['lower_endpoint_residual_upper'],
            upper_endpoint_residual_lower=bracket['upper_endpoint_residual_lower'],
            moment_minus_one_at_comparison=[engine.decimal(lo-1),engine.decimal(hi-1)],
            pass_comparison=hi < 1)
    # Meaningful accounting control: shrinking width without the matching paid
    # mass saving consumes 24*666 units of deficit instead of preserving it.
    wrong = Counter(global_profiles['True'])
    for rank,n in DELTA.items():
        wrong[rank] -= 666*n
    need(73*66304-sum(r*n for r,n in wrong.items()) == 7696, 'unpaid-shrink control')
    receipt = dict(status='PASS_CONDITIONAL_COMPOSITION_COST_SCREEN_NO_CONSTRUCTION_CLAIM',
        seed=39,base='7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261',
        entrance_source_head='324d7d3590dc21003940a44cb0cbdc32b3620f25',
        attribution='Tekalign (@tekuuu), substantial OpenAI Codex assistance; entrance mechanism by Jeremy Kothe (@jeremykothe2), PR2435.',
        assumption='The exact PR2435 delta +24H1+120H2-96H3 composes with FOUR428, with 24 retained helper widths 8->7 and no extra gates, frame work, buffers or restoration. This assumption requires separate interface and native replay.',
        raised_original_helpers=sorted(RAISED),conditional_local_profiles=profiles,
        conditional_width_inventories=inventories,local_mass=5304,helper_width_sum=3448,
        mass_minus_width=1856,helpers=428,changed_roles=24*666,changed_bins=changed_bins,
        live=66304,dimension=73,global_deficit=23680,
        physical_stock_if_no_new_buffers=66304+428+8+2+76,
        physical_obligation='76 inherited private zero buffers, 428 helper reservations, eight auxiliary reserves and two scratch reserves remain fully charged; any changed lifetime/label or extra buffer must be separately admitted.',
        global_profiles=global_profiles,idle_profiles=residuals,comparison_rate=str(COMPARISON),
        exact_moments=result,controls=['baseline owner profile reconstructed','24 raises retained in all666 calls','missing paid delta lowers deficit to7696'],
        pins={str(p.relative_to(RESEARCH)):h for p,h in PINS.items()},
        scope='Literal existing owner allocation with smaller helper slices and complete residual padding, no new packing optimization. Fixed inherited nine-stage geometry, all666 local profiles, all pending bins, exact inherited bad envelope. B frame composition, native realization, global scalar equivalence, physical invoice and modern outer admission remain unverified here; no new kappa is claimed.')
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(receipt,indent=2)+'\n')
    print(receipt['status'])
    print(json.dumps(result,indent=2))

if __name__ == '__main__':
    main()
