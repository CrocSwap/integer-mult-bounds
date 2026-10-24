"""Rebuild the exact source-distance facts without producer imports."""

from collections import defaultdict
from hashlib import sha256
from itertools import product
from math import comb
from pathlib import Path
import gzip
import json

HERE = Path(__file__).resolve().parent
LANES = HERE.parent


def require(value, message):
    if not value:
        raise ValueError(message)


def main():
    raw = (LANES / 'circuit-interface/INTERFACE.json').read_bytes()
    require(sha256(raw).hexdigest() == '5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3', 'The interface pin differs')
    source = json.loads(raw)
    rows = [[int(row.get(str(p), '0')) for p in range(112)] for row in source['R']]
    columns = list(zip(*rows))
    groups = defaultdict(list)
    for column in columns:
        support = tuple(i for i, value in enumerate(column) if value)
        require(len(support) == 4, 'A column has the wrong support')
        groups[support].append(column)
    require(len(groups) == 14 and all(len(block) == 8 for block in groups.values()), 'The quartet sizes differ')
    for support, block in groups.items():
        expected = {(1,) + signs for signs in product((-1, 1), repeat=3)}
        found = {tuple(column[i] * column[support[0]] for i in support) for column in block}
        require(found == expected, 'The exact sign set differs')
    zero_bound = [0] + [2 * (comb(t, t // 2) // 2) for t in range(1, 5)]
    # Count full four-sign patterns first, then identify opposite patterns.
    table = [0] + [(16 - zero_bound[t] * 2 ** (4 - t)) // 2 for t in range(1, 5)]
    require(table == [0, 8, 4, 6, 5], 'The antichain table differs')
    minima = {}
    all_bounds = {}
    for signs in product((0, 1), repeat=8):
        count = sum(signs)
        if count == 0:
            continue
        bound = sum(table[sum(signs[i] for i in block)] for block in groups)
        minima[count] = min(minima.get(count, bound), bound)
        all_bounds[str(sum(value << i for i, value in enumerate(signs)))] = bound
    require(minima == {1: 56, 2: 76, 3: 78, 4: 53, 5: 73, 6: 75, 7: 77, 8: 70}, 'A support minimum differs')
    attaining = [sum(sum(a * b for a, b in zip(vector, col)) != 0 for col in columns) for vector in columns]
    require(attaining == [53] * 112, 'The attained distance differs')
    snap_raw = gzip.decompress((LANES / 'history-encoding/BACKWARD-SNAPSHOT-INTERVALS.json.gz').read_bytes())
    require(sha256(snap_raw).hexdigest() == '3dd1d7388c7d3bca104a21e642b5fcafe175d83a2f1dfce1a3ee3e86b864276c', 'The snapshot pin differs')
    maxima = {}
    for U in json.loads(snap_raw)['frames']:
        support = sum(all((q & v).bit_count() % 2 == 0 for v in U) for q in source['ports'])
        maxima[len(U)] = max(maxima.get(len(U), 0), support)
    require([maxima[r] for r in range(2, 9)] == [20, 10, 8, 8, 4, 2, 1], 'The frame support maxima differ')
    path = LANES / 'history-encoding/QUERY-SUPPORT-DISTANCE.json'
    producer = json.loads(path.read_bytes())
    require(all_bounds == producer['all_255_coefficient_support_bounds'], 'The independent support table differs')
    proof = LANES / 'history-encoding/QUERY-SUPPORT-DISTANCE.md'
    result = {
        'status': 'PASS_INDEPENDENT_QUERY_SUPPORT_DISTANCE_53_REVIEW',
        'checker_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
        'proof_sha256': sha256(proof.read_bytes()).hexdigest(),
        'source_checker_sha256': sha256((LANES / 'history-encoding/check_query_support_distance.py').read_bytes()).hexdigest(),
        'source_receipt_sha256': sha256(path.read_bytes()).hexdigest(),
        'interface_sha256': sha256(raw).hexdigest(), 'snapshot_decompressed_sha256': sha256(snap_raw).hexdigest(),
        'quartet_count': len(groups), 'nonzero_table': table, 'support_size_minima': minima,
        'attaining_directions': 112, 'actual_frame_support_maxima': maxima,
        'proof_review': [
            'A generic real projection keeps each nonzero coefficient nonzero and preserves every complex zero sum.',
            'Positive equal-sum subsets form an antichain. Opposite zero sign patterns give the even count bound.',
            'A scalar coefficient code with distance at least three remains injective after any two coordinate deletions.',
            'For block fields, choose a linear section of the surjective reconstruction map. Its kd-dimensional image has block distance at least three.',
        ],
        'scope': 'A k-dimensional query span needs at least k+2 birth fields when each has source support at most20. This does not price a multilevel shared network.',
        'not_rerun': ['The full scalar core', 'The snapshot producer', 'A native cache program'],
        'findings': [],
    }
    (HERE / 'QUERY-SUPPORT-DISTANCE-REVIEW.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(result['status'])


if __name__ == '__main__':
    main()
