"""Independent, small exact audit of post-gauge rank-four kernel blocks.

Prepared for icekylinx with GPT-6 Astra assistance. Apache-2.0.
This does not import the response builder, run a full endpoint replay, or
certify Clifford phases/global hosting. It pulls the raw B suffix backwards
and checks the new local algebra and all entrance-frame containments.
"""
import argparse
import gzip
import hashlib
import json
import time
from collections import Counter, defaultdict
from fractions import Fraction as Q
from pathlib import Path


def basis(vectors):
    rows = {}
    for x in vectors:
        for p in sorted(rows, reverse=True):
            if x >> p & 1:
                x ^= rows[p]
        if x:
            p = x.bit_length()-1
            for q in rows:
                if rows[q] >> p & 1:
                    rows[q] ^= x
            rows[p] = x
    return tuple(rows[p] for p in sorted(rows, reverse=True))


def inside(a, b):
    return basis(tuple(a)+tuple(b)) == basis(b)


def axpy(dst, src, q):
    for t, x in list(src.items()):
        z = dst.get(t, Q(0))+q*x
        if z:
            dst[t] = z
        else:
            dst.pop(t, None)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(source, groups_path, gauges_path, out):
    started = time.monotonic()
    word = json.load(gzip.open(source))
    groups = json.loads(groups_path.read_text())
    original_gauges = {int(h): basis(E) for h, E in
                       json.loads(gauges_path.read_text())['gauge'].items()}
    v, R, hdim = (word['report'][key] for key in ('v', 'R', 'h'))
    offset, n = 2*v, 2*v+R
    assert (v, R, hdim) == (112, 504, 9)
    touched_early = {r for e in word['A']+word['cut']
                     for r in (e[1:3] if e[0] == 'add' else e[1:2])}
    first = {}
    for e in word['B']:
        for r in (e[1:3] if e[0] == 'add' else e[1:2]):
            first.setdefault(r, basis(e[-1]))
        assert not (e[0] == 'add' and v <= e[2] < offset
                    and not v <= e[1] < offset), 'Y is never read into X/helpers'
    for e in word['A']+word['cut']:
        if v <= e[1] < offset:
            assert e[0] == 'add' and not v <= e[2] < offset

    # Exact reverse accumulation: column[r][t] is the coefficient of the
    # scalar present in r at B's beginning in output target t after raw B.
    column = [{r-v: Q(1)} if v <= r < offset else {} for r in range(n)]
    for e in reversed(word['B']):
        if e[0] == 'add':
            _, t, s, a, b, _ = e
            axpy(column[s], column[t], Q(a, b))
        else:
            _, t, a, b, _ = e
            column[t] = {j: Q(a, b)*x for j, x in column[t].items()}

    all_donors = set()
    all_pivots = set()
    group_rows = []
    shear_count = 0
    for group in groups:
        E = basis(group['E'])
        donors, pivots = group['donors'], group['pivots']
        assert len(E) == len(donors) == len(pivots) == 4
        assert not (set(donors+pivots) & (all_donors | all_pivots))
        assert not set(donors) & set(pivots)
        all_donors.update(donors)
        all_pivots.update(pivots)
        for helper in donors+pivots:
            assert offset+helper not in touched_early
            assert helper in original_gauges
            assert inside(E, first[offset+helper])
        for donor in donors:
            assert inside(original_gauges[donor], E)
        for pivot in pivots:
            relation = {int(d): Q(q) for d, q in group['relations'][str(pivot)].items()}
            assert set(relation) <= set(donors)
            assert all(q.denominator & (q.denominator-1) == 0 for q in relation.values())
            expected = {}
            for donor, q in relation.items():
                axpy(expected, column[offset+donor], q)
            assert column[offset+pivot] == expected
            shear_count += len(relation)
        group_rows.append({'E': list(E), 'donors': donors, 'pivots': pivots,
                           'native_first_ranks': [len(first[offset+x]) for x in donors+pivots],
                           'exact_raw_B_relations': True,
                           'gauge_to_kernel_to_native_nesting': True})
    assert len(groups) == 14 and len(all_donors) == len(all_pivots) == 56
    assert all_donors | all_pivots == set(range(392, 504))

    # Independently form K^{-1} D for the B-born gauges, using only the
    # unchanged preconditioner. This checks the compensations can happen
    # at their lines while every Y remains compatible with its next B use.
    gauges = {helper: E for helper, E in original_gauges.items()
              if helper not in all_pivots}
    assert len(original_gauges) == 168 and len(gauges) == 112
    assert not {offset+helper for helper in gauges} & touched_early
    rows = [{} for _ in range(n)]
    for helper in gauges:
        for target, q in column[offset+helper].items():
            rows[v+target][helper] = q
    for e in word['precondition']:
        if e[0] == 'add':
            _, t, s, a, b, _ = e
            axpy(rows[t], rows[s], Q(a, b))
        else:
            _, t, a, b, _ = e
            rows[t] = {j: Q(a, b)*q for j, q in rows[t].items()}
    target_frames = {}
    compensation_additions = 0
    for target in range(v):
        Es = [gauges[helper] for helper in rows[v+target]]
        for E in Es:
            assert inside(E, first[v+target])
        for E in Es:
            for F in Es:
                assert inside(E, F) or inside(F, E)
        target_frames[target] = list(max(Es, key=len, default=()))
        compensation_additions += len(Es)
    for helper, E in gauges.items():
        assert inside(E, first[offset+helper])

    result = {
        'status': 'PASS_EXACT_LOCAL_POST_GAUGE_RANK4_DELTA',
        'scope': 'Raw-B adjoint relations, dyadic coefficients, untouched-before-B guards, gauge compensation compatibility, and gauge/kernel/native frame nesting only. No full endpoint or phase replay and no global hosting claim.',
        'source_sha256': digest(source),
        'groups_sha256': digest(groups_path),
        'original_gauges_sha256': digest(gauges_path),
        'groups': group_rows,
        'remaining_post_gauges': len(gauges),
        'gauge_compensation_additions': compensation_additions,
        'rank4_pivots': len(all_pivots),
        'kernel_shears': shear_count,
        'new_rank4_entrance_mass': 4*len(all_pivots),
        'removed_rank1_gauge_mass': len(all_pivots),
        'entrance_rank_gain': 3*len(all_pivots),
        'ordering_required': 'unchanged pre-A face kernel; unchanged A/cut; all remaining post-gauge target compensations; rank4 donor shears; raw B; inverse source/helper cleanup',
        'seconds': time.monotonic()-started,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({key: value for key, value in result.items()
                      if key != 'groups'}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True, type=Path)
    parser.add_argument('--groups', required=True, type=Path)
    parser.add_argument('--gauges', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    run(args.source, args.groups, args.gauges, args.out)
