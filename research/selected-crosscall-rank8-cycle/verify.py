#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Selected fixed-map cross-call cycles: {0,1,7} -> {0,0,8}.

Aaron Wang / navinor, with help from chatgpt. PR1091 supplies the unchanged
owner admission audit; PR1790 supplies its pinned fixture and map conventions.
No new supplier or kappa is claimed.
"""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction as Q
import hashlib
from itertools import product
import json
from pathlib import Path
import time
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SWAP = 'research/frontier1094-swap-census/verify.py'


def require(ok, why):
    if not ok:
        raise ValueError(why)


def canonical(value):
    # JSON stringifies rank keys; normalize them before sorting on both sides.
    normalized=json.loads(json.dumps(value))
    return (json.dumps(normalized, sort_keys=True, indent=2)+'\n').encode()


def bin_key(role):
    return role['owner_replica'], role['child'], role['port']


def cycle_slacks(old, widths):
    a,b,c = old
    x,y,z = widths
    return a+x-z, b+y-x, c+z-y


def family_rejection(model, indices):
    """Remove every outgoing family at each call before inserting any landing."""
    removed, added = defaultdict(set), defaultdict(list)
    for p,i in enumerate(indices):
        source = model.roles[i]
        destination = bin_key(model.roles[indices[(p+1) % 3]])
        removed[source['time']].add(model.bins[bin_key(source)].family)
        added[source['time']].append(model.bins[destination].family)
    for t,families in added.items():
        if len(set(families)) != len(families):
            return 'same_call_duplicate_landings'
        if set(families) & (model.families[t] - removed[t]):
            return 'same_call_unvacated_family'
    return None


def enumerate_cycles(model, limit=1_000_000, seconds=300):
    """Complete class prefilter plus exact window join; fail on any budget limit.

    The unique slack-7 source anchors each directed cycle; B and C have
    slacks 0/1 in either order. Thus rotations are not counted twice.
    """
    started = time.monotonic()
    def check_deadline():
        require(time.monotonic()-started <= seconds,
                'time budget exceeded; census incomplete')
    members = defaultdict(list)
    by_call = defaultdict(Counter)
    for i,r in enumerate(model.roles):
        typ = model.bins[bin_key(r)].remainder, r['width']
        if typ[0] in (0,1,7):
            members[typ].append(i)
            by_call[typ][r['time']] += 1
    check_deadline()
    a_types = [t for t in members if t[0] == 7]
    rows, joined = [], []
    cached = {}
    for a_type in sorted(a_types):
        for b_slack,c_slack in ((0,1),(1,0)):
            b_types = sorted(t for t in members if t[0] == b_slack)
            c_types = sorted(t for t in members if t[0] == c_slack)
            for b_type,c_type in product(b_types,c_types):
                check_deadline()
                typs = a_type,b_type,c_type
                old = tuple(t[0] for t in typs)
                widths = tuple(t[1] for t in typs)
                new = cycle_slacks(old,widths)
                if sorted(new) != [0,0,8]:
                    continue
                total = len(members[a_type])*len(members[b_type])*len(members[c_type])
                same_call = sum(n*by_call[b_type][t]*by_call[c_type][t]
                                for t,n in by_call[a_type].items())
                row = dict(types=typs, old=old, widths=widths, new=new,
                           arithmetic_triples=total, same_call_excluded=same_call,
                           cross_call_triples=total-same_call, window_joined=0,
                           legal=0, family_rejected=0)
                for i in members[a_type]:
                    a = model.roles[i]
                    ba = bin_key(a)
                    for j in members[b_type]:
                        check_deadline()
                        b = model.roles[j]
                        if model.window_active_rejection(a,bin_key(b)) is not None:
                            continue
                        # Last leg C->A and middle leg B->C depend on this key.
                        key = c_type,b['time'],ba
                        if key not in cached:
                            cached[key] = [k for k in members[c_type]
                                if model.window_active_rejection(model.roles[k],ba) is None
                                and model.window_active_rejection(b,bin_key(model.roles[k])) is None]
                        for k in cached[key]:
                            check_deadline()
                            c = model.roles[k]
                            if a['time'] == b['time'] == c['time']:
                                continue
                            require(len({ba,bin_key(b),bin_key(c)}) == 3,
                                    'non-distinct cycle bins')
                            reason = family_rejection(model,(i,j,k))
                            row['window_joined'] += 1
                            row['family_rejected' if reason else 'legal'] += 1
                            joined.append(dict(indices=[i,j,k],rejection=reason))
                            require(len(joined) <= limit, 'candidate budget exceeded; census incomplete')
                rows.append(row)
    check_deadline()
    require(len(joined) == sum(r['window_joined'] for r in rows), 'join accounting')
    require(sum(r['legal']+r['family_rejected'] for r in rows) == len(joined),
            'family accounting')
    return dict(class_rows=rows,
                cross_call_arithmetic_candidates=sum(r['cross_call_triples'] for r in rows),
                window_rejected=sum(r['cross_call_triples']-r['window_joined'] for r in rows),
                window_joined=len(joined), family_rejected=sum(r['family_rejected'] for r in rows),
                legal_cycles=sum(r['legal'] for r in rows), joined_candidates=joined)


def toy(times=(0,1,2)):
    roles = [dict(owner_replica=i,child=0,port=0,width=w,time=t,stage=t,replica=0)
             for i,(w,t) in enumerate(zip((8,7,7),times))]
    bins = {bin_key(r): types.SimpleNamespace(remainder=s,family=i)
            for i,(r,s) in enumerate(zip(roles,(7,1,0)))}
    families = defaultdict(set)
    for r in roles:
        families[r['time']].add(bins[bin_key(r)].family)
    return types.SimpleNamespace(roles=roles,bins=bins,families=families,
                                 window_active_rejection=lambda r,b: None)


def controls():
    require(cycle_slacks((7,1,0),(8,7,7)) == (8,0,0), 'wrong transfer direction')
    m = toy()
    result = enumerate_cycles(m)
    require(result['cross_call_arithmetic_candidates'] == 1
            and result['legal_cycles'] == 1
            and result['joined_candidates'] == [dict(indices=[0,1,2],rejection=None)],
            'toy gain missed')
    m = toy((0,0,1))
    require(enumerate_cycles(m)['legal_cycles'] == 1,
            'same-call vacated family incorrectly treated as occupied')
    m.families[1].add(0)
    require(enumerate_cycles(m)['family_rejected'] == 1, 'unvacated family control accepted')
    m = toy((0,0,0))
    require(enumerate_cycles(m)['cross_call_arithmetic_candidates'] == 0,
            'same-call scope control accepted')
    m = toy()
    m.window_active_rejection = lambda r,b: 'outside_strict_source_event_window' if r['time']==2 else None
    require(enumerate_cycles(m)['window_rejected'] == 1, 'closed-window control accepted')
    # Independent direct triple loop, including an extra same-type C role.
    m = toy()
    extra = dict(m.roles[2],owner_replica=3,time=3,stage=3)
    m.roles.append(extra)
    m.bins[bin_key(extra)] = types.SimpleNamespace(remainder=0,family=3)
    m.families[3].add(3)
    expected = []
    for i,j,k in product(range(len(m.roles)),repeat=3):
        old = [m.bins[bin_key(m.roles[h])].remainder for h in (i,j,k)]
        if old[0] != 7 or sorted(old) != [0,1,7]:
            continue
        w = [m.roles[h]['width'] for h in (i,j,k)]
        if sorted((old[0]+w[0]-w[2],old[1]+w[1]-w[0],old[2]+w[2]-w[1])) == [0,0,8]:
            expected.append([i,j,k])
    require(expected == [[0,1,2],[0,1,3]], 'direct toy fixture changed')
    require([c['indices'] for c in enumerate_cycles(m)['joined_candidates']] == expected,
            'indexed join disagrees with direct triples')
    return ['toy_gain','same_call_vacancy','unvacated_family','same_call_scope',
            'closed_window','direct_triple_crosscheck']


def fixture():
    manifest = json.loads((HERE/'SOURCES.json').read_bytes())
    raw = {}
    for pin in manifest['files']:
        if pin['usage'] == 'input':
            data = (ROOT/pin['path']).read_bytes()
            require(hashlib.sha256(data).hexdigest() == pin['sha256'], 'source drift: '+pin['path'])
            raw[pin['path']] = data
    module = types.ModuleType('pinned_swap_fixture')
    module.__file__ = str(ROOT/SWAP)
    # dataclass resolves the defining module through sys.modules.
    import sys
    sys.modules[module.__name__] = module
    exec(compile(raw[SWAP],module.__file__,'exec'),module.__dict__)
    return module,module.fixture(),raw


def direct_census(model):
    """Separate role-first enumeration via the three possible target placements.

    No primary class rows, transfer helper, window predicate or family
    predicate is reused. Geometry/role decoding remains the shared PR1091 input.
    """
    roles = model.roles
    buckets = defaultdict(list)
    for i,r in enumerate(roles):
        buckets[model.bins[bin_key(r)].remainder,r['width']].append(i)
    pivots = [i for (slack,w),indices in buckets.items() if slack==7 for i in indices]
    candidates, masks, samples = [], Counter(), {}
    for i in pivots:
        a = roles[i]
        x = a['width']
        for rb,rc in ((0,1),(1,0)):
            middle = [j for (slack,w),indices in buckets.items() if slack==rb for j in indices]
            for j in middle:
                b = roles[j]
                y = b['width']
                for target in ((8,0,0),(0,8,0),(0,0,8)):
                    if rb+y-x != target[1]:
                        continue
                    incoming_to_a = 7+x-target[0]
                    if rc+incoming_to_a-y != target[2]:
                        continue
                    for k in buckets.get((rc,incoming_to_a),()):
                        c = roles[k]
                        if a['time']==b['time']==c['time']:
                            continue
                        triple = i,j,k
                        sources = a,b,c
                        destinations = bin_key(b),bin_key(c),bin_key(a)
                        require(len(set(destinations))==3,'direct non-distinct bins')
                        lands = []
                        detail = []
                        for r,dest in zip(sources,destinations):
                            position = model.positions[r['stage'],r['replica']]
                            lo,hi = model.windows[dest[:2]]
                            lands.append('1' if lo<position<hi else '0')
                            detail.append(dict(role=[r['stage'],r['replica'],r['helper']],
                                               destination=dest,position=position,window=[lo,hi]))
                        mask = ''.join(lands)
                        masks[mask] += 1
                        samples.setdefault(mask,dict(indices=triple,landings=detail))
                        candidates.append(triple)
    require(len(set(candidates))==len(candidates),'direct census repeated a cycle')
    candidates.sort()
    return dict(candidates=len(candidates),window_masks=dict(sorted(masks.items())),
                all_windows_pass=masks['111'],
                candidate_ids_sha256=hashlib.sha256(canonical(candidates)).hexdigest(),
                representative_per_window_mask=samples,
                source_role_counts={str(r):sum(len(v) for (slack,w),v in buckets.items() if slack==r)
                                    for r in (0,1,7)},
                eligible_pivots=[dict(index=i,role=[roles[i]['stage'],roles[i]['replica'],roles[i]['helper']],
                                     width=roles[i]['width'],bin=bin_key(roles[i])) for i in pivots])


def supplier_prices(f,module,raw):
    """Reprice unchanged complete source profiles; no physical supplier replay."""
    assembly = json.loads(raw['research/community-frontier1094-audit/ASSEMBLY.json'])
    bit = json.loads(raw['research/e8-bit-p111-tuned/tune/EXPECTED.json'])['nine']
    calculator = types.ModuleType('pinned_packing_calculator')
    calculator.__file__ = str(ROOT/module.CEILING)
    exec(compile(raw[module.CEILING],calculator.__file__,'exec'),calculator.__dict__)

    def moment(profile,m,live,a,bad=False):
        lo=hi=Q(0)
        for r,n in profile.items():
            l,u = calculator.child_cost(r,m,a)
            lo += n*l/live
            hi += n*u/live
        if bad:
            # Inherited bad-residue envelope: 32*m^2 rank-one calls per paid child,
            # times 10^-16. No new smaller surcharge is assumed.
            count = Q(32*m*m*sum(profile.values()),10**16)
            l,u = calculator.child_cost(1,m,a)
            lo += count*l/live
            hi += count*u/live
        return calculator.down(lo),calculator.up(hi)

    receipts = {}
    for name,profile,m,live,a,bad in (
        ('complex',dict(f['baseline']['profile']),73,14336,Q(assembly['complex_lower']),False),
        ('bit',{int(r):n for r,n in bit['profile'].items()},64,bit['bit']['live'],Q(bit['bit_lower']),True)):
        now = moment(profile,m,live,a,bad)
        following = moment(profile,m,live,a+Q(1,10**24),bad)
        require(now[1]<1 and following[0]>1,name+' source endpoint/next-tick signs')
        receipts[name] = dict(endpoint=str(a),moment=[str(v) for v in now],
                              next_tick_moment=[str(v) for v in following],
                              bad_residue_surcharge_included=bad,
                              rank_mass=sum(r*n for r,n in profile.items()),
                              deficit=m*live-sum(r*n for r,n in profile.items()))
    require(Q(receipts['complex']['endpoint'])<Q(receipts['bit']['endpoint']),
            'binding side changed')
    receipts['binding']='complex'
    return receipts


def build():
    checks = controls()
    module,f,raw = fixture()
    result = enumerate_cycles(f['model'])
    direct = direct_census(f['model'])
    require(direct['candidates']==result['cross_call_arithmetic_candidates'],
            'direct and indexed candidate accounting disagree')
    require(direct['all_windows_pass']==result['window_joined']==0,
            'strict-window obstruction not reproduced')
    require(result['cross_call_arithmetic_candidates']==21886,'domain count changed')
    require(result['legal_cycles']==0,'unexpected legal coalescing cycle')
    model=f['model']
    by_type=defaultdict(list)
    for i,r in enumerate(model.roles):
        by_type[model.bins[bin_key(r)].remainder,r['width']].append(i)
    require(len(by_type[7,8])==len(by_type[1,7])==1,'constant block is not unique')
    late=model.roles[by_type[7,8][0]]
    early=model.roles[by_type[1,7][0]]
    block_specs=[('C->A',early,bin_key(late)),('A->B',late,bin_key(early))]
    blocks=[]
    require([r['types'] for r in result['class_rows']]
            == [((7,8),(0,8),(1,7)),((7,8),(1,7),(0,7))],
            'constant blocks do not cover every supported type')
    for row,(leg,role,dest) in zip(result['class_rows'],block_specs):
        position=model.positions[role['stage'],role['replica']]
        lo,hi=model.windows[dest[:2]]
        require(not lo<position<hi,'constant window block unexpectedly legal')
        blocks.append(dict(types=row['types'],blocked_leg=leg,
                           blocked_role=[role['stage'],role['replica'],role['helper']],
                           destination=dest,position=position,window=[lo,hi],
                           rejected_cycles=row['cross_call_triples']))
    cap = module.packing_cap(f,raw)
    prices = supplier_prices(f,module,raw)
    return dict(status='PASS_SELECTED_CROSSCALL_RANK8_CYCLE_OBSTRUCTION',
                domain='fixed_selected_PR1094; distinct occupied bins; at least two calls; '
                       'old slack multiset0,1,7; new0,0,8; both directed orientations',
                canonicalization='unique old-slack7 pivot; A->B->C->A; rotations counted once',
                baseline_owner_audit=f['baseline'],census=result,independent_direct=direct,
                constant_window_blocks=blocks,
                supplier_prices=prices,packing_ceiling=cap,
                fraction_of_packing_headroom_realized='0',
                inherited_owner_mutations=f['owner_controls'],synthetic_controls=checks,
                input_sha256={r['path']:r['sha256'] for r in json.loads((HERE/'SOURCES.json').read_bytes())['files']
                              if r['usage']=='input'},
                scope='finite rank-transition exclusion, not all cross-call cycles or a global '
                      'packing optimum; no supplier/controller/invoice/outer/Lean/cold replay or new kappa')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--controls', action='store_true')
    parser.add_argument('--probe', action='store_true')
    parser.add_argument('--write', type=Path, help='write a complete receipt to a NEW path')
    parser.add_argument('--receipt', type=Path, default=HERE/'RESULT.json')
    args = parser.parse_args()
    checks = controls()
    if args.controls:
        print('PASS_CROSSCALL_CYCLE_CONTROLS controls='+str(len(checks)))
        return
    if args.probe:
        module,f,raw = fixture()
        result = enumerate_cycles(f['model'])
        print(json.dumps(result,indent=2))
        print('PASS_CROSSCALL_CYCLE_PROBE legal='+str(result['legal_cycles']))
        return
    result = build()
    if args.write:
        with args.write.open('xb') as out:
            out.write(canonical(result))
    else:
        expected = json.loads(args.receipt.read_bytes())
        require(canonical(expected)==canonical(result),'receipt mismatch')
    print(result['status']+' candidates=21886 all_window_blocked '
          'direct_crosscheck=PASS owner_controls=11 new_kappa=NO')


if __name__ == '__main__':
    try:
        main()
    except (ValueError,KeyError,OSError) as error:
        raise SystemExit('FAIL_CROSSCALL_CYCLE: '+str(error))
