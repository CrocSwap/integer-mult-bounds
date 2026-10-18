#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Re-solve PR #2979's four fixed-capacity caps and price each stage-one group alone.

Inputs are read as data only (JSON); no code of the audited package is imported.
Prints RESULT JSON on stdout.
"""
import gzip, hashlib, json, sys
from fractions import Fraction as Q
from pathlib import Path
import capsolve as C

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / 'rank7-joint-endframes'
AUDIT = HERE.parent / 'rank7-joint-frame-audit'


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if raw[:2] == b'\x1f\x8b' else raw), hashlib.sha256(raw).hexdigest()


def add(base, delta):
    out = {int(k): int(v) for k, v in base.items()}
    for k, v in delta.items():
        out[int(k)] = out.get(int(k), 0) + int(v)
        C.need(out[int(k)] >= 0, 'negative count')
    return {k: v for k, v in out.items() if v}


def basis_key(entries):
    return sorted((e['capacity'], tuple(sorted(e['widths'])), Q(e['count_per_replica'])) for e in entries)


def setup(cert):
    local = {int(r): int(n) for r, n in cert['local_per_call'].items()}
    inv = {int(w): int(n) for w, n in cert['inventory_per_call'].items()}
    widths = sorted(inv)
    caps = sorted(C.BINS)
    pats = C.catalogue(widths)
    return local, inv, pats, caps, widths, C.rhs_of(inv, caps, widths)


def index_of(pats, widths, entry):
    counts = tuple(entry['widths'].count(w) for w in widths)
    return next(j for j, p in enumerate(pats) if p[0] == entry['capacity'] and p[1] == counts)


def expect_reject(label, fn):
    try:
        fn()
    except ValueError as error:
        return '%s: rejected (%s)' % (label, str(error)[:90])
    raise AssertionError('control accepted: ' + label)


def rejections(shipped):
    out = {}
    s1 = shipped['stage1']
    local, inv, pats, caps, widths, rhs = setup(s1)
    basis = sorted(index_of(pats, widths, e) for e in s1['basis_patterns'])
    bstar = float(Q(s1['cap_lower']))
    C.certify(local, inv, pats, caps, widths, rhs, basis, bstar)  # positive control
    swapped = [j for j in basis if j != basis[3]] + [next(j for j in range(len(pats)) if j not in basis and pats[j][0] == 32)]
    out['swapped_basis_column'] = expect_reject('stage-1 basis with one column replaced', lambda: C.certify(local, inv, pats, caps, widths, rhs, sorted(swapped), bstar))
    s2 = shipped['stage2']
    l2, inv2, pats2, caps2, widths2, rhs2 = setup(s2)
    b2 = sorted(index_of(pats2, widths2, e) for e in s2['basis_patterns'])
    out['stage2_basis_on_stage1_inputs'] = expect_reject('stage-2 optimal basis certified against stage-1 inputs', lambda: C.certify(local, inv, pats, caps, widths, rhs, b2, bstar))
    A = C.np.array([C.column(p, caps, widths) for p in pats], dtype=float).T
    suboptimal = C.float_lp(pats, A, C.np.array([float(v) for v in rhs]), 0.5)[1]
    out['feasible_basis_optimal_at_b_half'] = expect_reject('feasible stage-1 basis optimal at b = 1/2, not at the cap', lambda: C.certify(local, inv, pats, caps, widths, rhs, suboptimal, 0))
    bad = dict(s1['local_per_call']); bad['1'] = bad['1'] + 1
    out['extra_rank1_child'] = expect_reject('stage-1 local profile with one extra rank-1 child', lambda: C.solve_cap(bad, s1['inventory_per_call']))
    stale = C.solve_cap(shipped['stage2']['local_per_call'], shipped['final']['inventory_per_call'])
    C.need(Q(stale['cap_upper']) < Q(shipped['final']['cap_lower']), 'stage-2 local with final inventory must give a lower cap')
    out['stage2_local_with_final_inventory'] = 'lower cap %s < %s' % (stale['cap_upper'], shipped['final']['cap_lower'])
    return out


PINS = {
    'RELAX-STAGES.json': '0e5ec700a191b668ba3d4b6d675f5c047d264b9a5109fc55fa92961b3fcb7d68',
    'RELAX-CAP.json': 'b272680de5842f7fd5f442cd0aeadfd317fe6af266ddee1a1e0738a919ba856e',
    'rank7-joint-frame-audit/RESULT.json': '994c11f0126f17ecbd0b8392d8904ad58aaede25c4c2347d3f35de6f839b2503',
}


def compute():
    stages, h_st = read(SRC / 'certificates/RELAX-STAGES.json')
    final, h_cap = read(SRC / 'certificates/RELAX-CAP.json')
    audit, h_audit = read(AUDIT / 'RESULT.json')
    shipped = {'parent': stages['parent'], 'stage1': stages['stage1'], 'stage2': stages['stage2'], 'final': final}
    # bind the stage inputs to the separately implemented frame audit (PR2993 lineage)
    prov = audit['providers']['base']
    C.need({int(k): v for k, v in prov['parent']['profile'].items()} == {int(k): v for k, v in shipped['parent']['local_per_call'].items()}, 'parent local')
    C.need({int(k): v for k, v in prov['stage_one']['profile'].items()} == {int(k): v for k, v in shipped['stage1']['local_per_call'].items()}, 'stage1 local')
    C.need({int(k): v for k, v in prov['final']['profile'].items()} == {int(k): v for k, v in shipped['final']['local_per_call'].items()}, 'final local')
    ladder = {}
    for name, cert in shipped.items():
        r = C.solve_cap(cert['local_per_call'], cert['inventory_per_call'])
        ladder[name] = {
            'cap_lower': r['cap_lower'], 'cap_upper': r['cap_upper'], 'patterns': r['patterns'],
            'tight_patterns': r['tight_patterns'], 'idle_per_replica': r['idle_per_replica'],
            'matches_shipped_bracket': Q(r['cap_lower']) == Q(cert['cap_lower']) and Q(r['cap_upper']) == Q(cert['cap_upper']),
            'matches_shipped_idle': r['idle_per_replica'] == cert['idle_per_replica'],
            'same_basis_as_shipped': basis_key(r['basis']) == basis_key(cert['basis_patterns']),
            'patterns_match': r['patterns'] == cert['patterns'], 'basis': r['basis'],
        }
    names = list(ladder)
    for a, b in zip(names, names[1:]):
        C.need(Q(ladder[a]['cap_upper']) < Q(ladder[b]['cap_lower']), 'ladder rises %s -> %s' % (a, b))
    parent_local = shipped['parent']['local_per_call']
    parent_inv = shipped['parent']['inventory_per_call']
    parent_lo = Q(ladder['parent']['cap_lower'])
    parent_hi = Q(ladder['parent']['cap_upper'])
    # groups of stage one, alone on the parent: local deltas from the independent frame audit,
    # width changes from #2979's README (V45: four 8->7; A, B: one 8->7, four 7->6; C, D: four 7->6)
    widths = {'V45': {8: -4, 7: 4}, 'A': {8: -1, 7: -3, 6: 4}, 'B': {8: -1, 7: -3, 6: 4},
              'C': {7: -4, 6: 4}, 'D': {7: -4, 6: 4}}
    groups = {}
    tot_l, tot_w = {}, {}
    for g, dw in widths.items():
        dl = prov['groups'][g]['profile_delta']
        C.need(prov['groups'][g]['profile_delta'] == audit['providers']['extra']['groups'][g]['profile_delta'], 'providers agree')
        for k, v in dl.items():
            tot_l[int(k)] = tot_l.get(int(k), 0) + v
        for k, v in dw.items():
            tot_w[k] = tot_w.get(k, 0) + v
        r = C.solve_cap(add(parent_local, dl), add(parent_inv, dw))
        groups[g] = {'local_delta': dl, 'width_delta': {str(k): v for k, v in dw.items()},
                     'cap_lower': r['cap_lower'], 'cap_upper': r['cap_upper'],
                     'raises_parent_cap': Q(r['cap_lower']) > parent_hi,
                     'gain_over_parent_cap_float': float((Q(r['cap_lower']) + Q(r['cap_upper'])) / 2 - (parent_lo + parent_hi) / 2)}
    C.need(add(parent_local, tot_l) == {int(k): v for k, v in shipped['stage1']['local_per_call'].items()}, 'groups sum to stage1 local')
    C.need(add(parent_inv, tot_w) == {int(k): v for k, v in shipped['stage1']['inventory_per_call'].items()}, 'groups sum to stage1 inventory')
    # V45 endpoint subsets: Delta(k) = (2-k) H1 + 10 H2 + 6 H3 - 10 H4, k of four helpers 8 -> 7
    subsets = {}
    for k in range(5):
        dl = {1: 2 - k, 2: 10, 3: 6, 4: -10}
        r = C.solve_cap(add(parent_local, dl), add(parent_inv, {8: -k, 7: k}))
        subsets[str(k)] = {'cap_lower': r['cap_lower'], 'cap_upper': r['cap_upper'],
                           'raises_parent_cap': Q(r['cap_lower']) > parent_hi,
                           'gain_over_parent_cap_float': float((Q(r['cap_lower']) + Q(r['cap_upper'])) / 2 - (parent_lo + parent_hi) / 2)}
    C.need(subsets['4']['cap_lower'] == groups['V45']['cap_lower'], 'k=4 is the V45 group')
    for name, h in (('RELAX-STAGES.json', h_st), ('RELAX-CAP.json', h_cap), ('rank7-joint-frame-audit/RESULT.json', h_audit)):
        C.need(PINS[name] == h, 'input bytes differ from pin: ' + name)
    controls = rejections(shipped)
    out = {
        'status': 'PASS_INDEPENDENT_CAP_RESOLVE',
        'controls': controls,
        'inputs_sha256': {'RELAX-STAGES.json': h_st, 'RELAX-CAP.json': h_cap, 'rank7-joint-frame-audit/RESULT.json': h_audit},
        'ladder': ladder, 'stage1_groups_alone_on_parent': groups, 'v45_endpoint_subsets_on_parent': subsets,
    }
    return out


def main():
    print(json.dumps(compute(), indent=1, sort_keys=True))


if __name__ == '__main__':
    main()
