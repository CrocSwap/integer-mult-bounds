"""Count retained records in small branch-dependent affine trees."""

from collections import defaultdict
from hashlib import sha256
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
PHYS = HERE.parents[1]
SOURCE = PHYS / 'affine-sector-cover'
PINS = {
    'SPLIT-LIMIT.md': '6e79f870420b99c59c10c0e91160e3dbf548d8e821bb2dc94b4f39cfb2713f8b',
    'SPLIT-LIMIT.json': '3e1e8af1935ac52b311a103f651114917212f1a529da43ad65fb5da362cfe6b5',
    'check_split_limit.py': 'ee7d39eadd9bbc61c146ddda9791c65b579044561643d7bf2c6c7807c02ae00d',
}


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def rank(rows):
    pivots = {}
    for row in rows:
        while row:
            p = row.bit_length() - 1
            if p not in pivots:
                pivots[p] = row
                break
            row ^= pivots[p]
    return len(pivots)


def phase(x, n, width):
    rows = [(x >> (i * width)) & ((1 << width) - 1) for i in range(n)]
    residues = set()
    for q in range(1 << n):
        if q.bit_count() % 2:
            total = 0
            for i in range(n):
                if q & (1 << i):
                    total ^= rows[i]
            residues.add(total.bit_count() % 4)
    return next(iter(residues)) if len(residues) == 1 else None


def case(n, width, desired):
    m, size = n * width, 1 << (n * width)
    labels = [phase(x, n, width) for x in range(size)]
    accepted = {x for x in range(size) if labels[x] is not None and (desired is None or labels[x] == desired)}
    visits = [0] * size
    masks_by_depth = defaultdict(set)
    internal_sizes, leaves = [], []
    block_checks = 0

    def tree(points, constraints):
        nonlocal block_checks
        depth = len(constraints)
        origin = min(points)
        need(len(points) == 1 << (m - depth), 'Node record count')
        need(rank([x ^ origin for x in points]) == m - depth, 'Node affine dimension')
        flags = {x in accepted for x in points}
        if len(flags) == 1:
            leaf = (points, depth, flags.pop())
            leaves.append(leaf)
            return 0, [leaf]
        candidates = [mask for mask in range(1, size)
                      if rank(constraints + [mask]) == depth + 1]
        if depth == 0:
            mask = 1
        elif depth == 1:
            mask = 2 if origin & 1 == 0 else 4
        else:
            mask = candidates[(sum(points) + 7 * origin + 11 * depth) % len(candidates)]
        need(mask in candidates, 'Nonconstant branch test')
        chart = constraints + [mask]
        for b in range(m):
            if rank(chart + [1 << b]) > len(chart):
                chart.append(1 << b)
        need(len(chart) == m and rank(chart) == m, 'Branch test extends to an invertible chart')
        masks_by_depth[depth].add(mask)
        offset = (origin.bit_count() + depth) % 2
        parts = [[], []]
        for x in points:
            visits[x] += 1
            parts[((x & mask).bit_count() + offset) % 2].append(x)
        need(len(parts[0]) == len(parts[1]), 'Both arbitrary halves are retained')
        internal_sizes.append(len(points))
        work, below = len(points), []
        for part in parts:
            subwork, subleaves = tree(part, constraints + [mask])
            work += subwork
            below += subleaves
        need(work == sum(len(a) * (d - depth) for a, d, _ in below), 'Grouped block identity')
        block_checks += 1
        return work, below

    work, _ = tree(list(range(size)), [])
    need(sum(len(a) for a, _, _ in leaves) == size, 'Full arbitrary-record conservation')
    need(sum(internal_sizes) == work == sum(visits), 'Independent record-visit count')
    need(work == sum(len(a) * d for a, d, _ in leaves), 'All-leaf depth identity')
    for a, d, _ in leaves:
        need(all(visits[x] == d for x in a), 'One visit per ancestor split')
    f = width // 2
    if desired is None:
        k = n * ((width + 1) // 2) - width % 2
    else:
        preferred = {f % 4} if width % 2 == 0 else {f % 4, (f + 1) % 4}
        k = n * (width - f + (desired not in preferred))
    need(all(d >= k for _, d, take in leaves if take), 'Accepted affine depth')
    need(work >= k * len(accepted), 'Accepted rank lower bound')
    need(any(len(v) > 1 for v in masks_by_depth.values()), 'Genuinely branch-dependent masks')
    kept_only = sum(len(a) * d for a, d, take in leaves if take)
    need(kept_only < work, 'Dropping arbitrary rejected details fails the exact identity')
    return {'n': n, 'width': width, 'residue': desired, 'accepted_rank': len(accepted),
            'processed_records': work, 'lower_bound': k * len(accepted),
            'leaves': len(leaves), 'block_identities': block_checks,
            'distinct_masks_by_depth': {str(d): len(v) for d, v in masks_by_depth.items()}}


def main():
    for name, pin in PINS.items():
        need(sha256((SOURCE / name).read_bytes()).hexdigest() == pin, 'Pin: ' + name)
    density_file = PHYS / 'correlated-sector-review/REVIEW.json'
    density_pin = '3fcd2ffd0fd91289ae1841a3b1543239e4cd891521a55879dad1403c2e6cff50'
    need(sha256(density_file.read_bytes()).hexdigest() == density_pin, 'Density review pin')
    density = json.loads(density_file.read_text())
    record = next(x for x in density['exact_distributions'] if x['ambient_dimension'] == 73)
    need(record['limit_exponent'] == -((73 - 1) * (73 + 2) // 2) == -2700, 'Exact limit exponent')
    need(record['least_width_with_ratio_below_101_over_100'] == 152, 'Inherited threshold')
    ratio, previous = record['ratio_at_threshold'], record['ratio_previous']
    need(ratio['denominator'] < ratio['numerator'], 'Finite density exceeds limit')
    need(100 * ratio['numerator'] < 101 * ratio['denominator'], 'Exact one-percent threshold')
    need(100 * previous['numerator'] > 101 * previous['denominator'], 'Exact preceding-width comparison')
    cases = [case(n, width, desired) for n, width, desired in [(3, 2, None), (3, 2, 1), (2, 3, None)]]
    active_block = [(8, 1), (4, 2), (2, 3), (2, 3)]
    need(sum(s * d for s, d in active_block) == 16 + 8 + 4 == 28, 'Unequal-depth active block')
    need(8 * 2 * 3 == 48 > 16, 'A literal rank-three full tree is not one scan')
    result = {'status': 'PASS_INDEPENDENT_AFFINE_SPLIT_VOLUME',
              'source_pins': PINS, 'density_review_pin': density_pin,
              'producer_imported_or_executed': False, 'cases': cases,
              'active_block_records': 28, 'full_rank_three_block_records': 48,
              'density_threshold_checked_by_integer_comparison': 152,
              'scope': 'Combinatorial record counts in the literal tree grammar; inherited density theorem; no general circuit lower bound.'}
    (HERE / 'CHECK.json').write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    print(result['status'])
    print(json.dumps({'trees': len(cases), 'processed_records': sum(c['processed_records'] for c in cases)}))


if __name__ == '__main__':
    main()
