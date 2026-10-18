#!/usr/bin/env python3
"""Exact post-B restoration support certificate. Python 3.10+, standard library.

Prepared for Charles Bethin with substantial OpenAI Codex assistance.
Apache-2.0. The pinned word and its construction belong to eumemic and the
cumulative E8 supplier authors identified in README.md.
"""
from collections import Counter
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def bits(n):
    while n:
        low = n & -n
        yield low.bit_length() - 1
        n ^= low


def add_basis(basis, vector):
    """Fraction elimination, retaining selected original vectors externally."""
    row = list(map(Fraction, vector))
    for pivot, old in basis:
        f = row[pivot]
        row = [a - f * b for a, b in zip(row, old)]
    pivot = next((i for i, x in enumerate(row) if x), None)
    if pivot is None:
        return False
    f = row[pivot]
    row = [x / f for x in row]
    basis.append((pivot, row))
    basis.sort()
    return True


def read_source(name='r420'):
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    for filename, expected in pins['sha256'].items():
        require(hashlib.sha256((ROOT / filename).read_bytes()).hexdigest() == expected,
                'source hash: ' + filename)
    return json.loads(gzip.decompress((ROOT / pins['words'][name]).read_bytes()))


def derive(w):
    v, h = w['v'], w['h']
    n = 2 * v + w['R']
    require((v, h, w['R']) in ((120, 8, 420), (111, 8, 439)), 'word dimensions')
    z = list(range(v)) + list(range(2 * v, n))
    zs = set(z)
    frames = [set(f) for f in w['frames']]
    full = next(i for i, f in enumerate(frames) if len(f) == len(w['lines']))
    require(all(w['final'][r] == full for r in range(v)), 'source endpoint contract')
    current = list(w['start'])
    for phase in ('A', 'B'):
        for f, d, sources in w[phase]:
            require(d not in sources and len(set(sources)) == len(sources), 'gate aliases')
            if d in zs:
                require(all(s in zs for s in sources), 'raw z reads target')
            for r in [d] + sources:
                require(frames[current[r]] <= frames[f], 'raw frame nesting')
                current[r] = f
    zgates = [g for g in w['A'] + w['B'] if g[1] in zs]
    require(w['C'] == [[full, d, ss] for _, d, ss in reversed(zgates)],
            'literal inverse source binding')
    inverse = [1 << r for r in range(n)]
    for _, d, ss in w['C']:
        for s in ss:
            inverse[d] ^= inverse[s]
    rows = []
    full_inputs = [r for r in z if current[r] == full]
    full_mask = sum(1 << r for r in full_inputs)
    dimensions = []
    for frame in w['frames']:
        basis = []
        for line in frame:
            add_basis(basis, w['lines'][line])
        dimensions.append(len(basis))
    for r in z:
        basis, witness = [], []
        # Monotonicity requires the destination's own initial frame, even if
        # its own inverse coefficient is zero.
        origins = [r] + [s for s in bits(inverse[r]) if s != r]
        for s in origins:
            for line in w['frames'][current[s]]:
                if add_basis(basis, w['lines'][line]):
                    witness.append([s, line])
                    if len(basis) == h:
                        break
            if len(basis) == h:
                break
        if r >= 2 * v:
            require(len(witness) == h, 'helper has a proper lower bound: ' + str(r))
        rows.append({'register': r, 'inverse_support': list(bits(inverse[r])),
                     'rank_lower_bound': len(witness), 'witness': witness})
    return {'format': 'r420-cleanup-frame-obstruction/1',
            'boundary_frames': current,
            'full_boundary_z': full_inputs,
            'cleanup_profile': dict(sorted(Counter(str(h - dimensions[current[r]])
                for r in z if dimensions[current[r]] < h).items())),
            'full_input_hits': dict(sorted(Counter(
                str((inverse[r] & full_mask).bit_count()) for r in z).items())),
            'endpoints': rows}


def bareiss(matrix):
    """Independent integer determinant; no Fraction elimination."""
    a = [list(r) for r in matrix]
    sign, previous = 1, 1
    for k in range(len(a) - 1):
        p = next((i for i in range(k, len(a)) if a[i][k]), None)
        if p is None:
            return 0
        if p != k:
            a[p], a[k] = a[k], a[p]
            sign = -sign
        pivot = a[k][k]
        for i in range(k + 1, len(a)):
            for j in range(k + 1, len(a)):
                numerator = a[i][j] * pivot - a[i][k] * a[k][j]
                require(numerator % previous == 0, 'nonintegral Bareiss division')
                a[i][j] = numerator // previous
            a[i][k] = 0
        previous = pivot
    return sign * a[-1][-1]


def independent(w, certificate):
    """Forward dense Boolean simulation, Gauss-Jordan inverse, reverse last-use
    boundary lookup and integer determinant checking. Does not read w['C'].
    """
    v = w['v']
    z = list(range(v)) + list(range(2 * v, 2 * v + w['R']))
    position = {r: i for i, r in enumerate(z)}
    n = len(z)
    # Dense lists deliberately use a different representation and forward
    # traversal. Inversion is by elimination, not reverse gate replay.
    u = [[int(i == j) for j in range(n)] for i in range(n)]
    for _, destination, sources in w['A'] + w['B']:
        if destination not in position:
            continue
        row = u[position[destination]]
        for source in sources:
            other = u[position[source]]
            row[:] = [(a + b) % 2 for a, b in zip(row, other)]
    # Sparse set Gauss-Jordan on [U|I].
    augmented = [{j for j, x in enumerate(row) if x} | {n + i}
                 for i, row in enumerate(u)]
    for col in range(n):
        pivot = next((i for i in range(col, n) if col in augmented[i]), None)
        require(pivot is not None, 'singular forward matrix')
        augmented[col], augmented[pivot] = augmented[pivot], augmented[col]
        for i in range(n):
            if i != col and col in augmented[i]:
                augmented[i] ^= augmented[col]
    require(all({j for j in row if j < n} == {i}
                for i, row in enumerate(augmented)), 'inverse left half')
    inv_support = [{z[j - n] for j in row if j >= n} for row in augmented]

    # Latest raw use determines the boundary. Scatter reads do not move the
    # retained registers: R420 totals are rank 8; punctured R439 totals rank 7.
    full = next(i for i, f in enumerate(w['frames']) if len(f) == len(w['lines']))
    require(all(w['final'][r] == full for r in range(v)), 'source endpoint contract')
    boundary = {}
    events = w['A'] + w['B']
    for f, d, ss in reversed(events):
        for r in [d] + ss:
            if r not in boundary:
                boundary[r] = f
    boundary = [boundary.get(r, f) for r, f in enumerate(w['start'])]
    require(boundary == certificate['boundary_frames'], 'boundary disagreement')
    require([r for r in z if boundary[r] == full] == certificate['full_boundary_z'],
            'full boundary disagreement')
    require([r['register'] for r in certificate['endpoints']] == z, 'endpoint coverage')
    # Fraction-free integer elimination also checks the boundary dimensions.
    # It uses cross multiplication, with no normalization or Fraction RREF.
    def integer_rank(vectors):
        a = [list(row) for row in vectors]
        rank = 0
        for col in range(8):
            p = next((j for j in range(rank, len(a)) if a[j][col]), None)
            if p is None:
                continue
            a[p], a[rank] = a[rank], a[p]
            for j in range(rank + 1, len(a)):
                x, y = a[rank][col], a[j][col]
                if y:
                    a[j] = [x * b - y * c for b, c in zip(a[j], a[rank])]
            rank += 1
        return rank
    dim = {f: integer_rank([w['lines'][j] for j in w['frames'][f]])
           for f in set(boundary[r] for r in z)}
    profile = dict(sorted(Counter(str(8 - dim[boundary[r]])
        for r in z if dim[boundary[r]] < 8).items()))
    require(profile == certificate['cleanup_profile'], 'cleanup profile disagreement')
    determinants = []
    for i, record in enumerate(certificate['endpoints']):
        r = record['register']
        require(set(record['inverse_support']) == inv_support[i], 'inverse disagreement')
        all_lines = set(w['frames'][boundary[r]])
        for origin in inv_support[i]:
            all_lines.update(w['frames'][boundary[origin]])
        rank = integer_rank([w['lines'][j] for j in sorted(all_lines)])
        require(rank == record['rank_lower_bound'], 'support span rank disagreement')
        require(len(record['witness']) == rank, 'witness size')
        if r >= 2 * v:
            require(rank == 8, 'helper not forced full')
        for origin, line in record['witness']:
            require(origin == r or origin in inv_support[i], 'unsupported origin')
            require(line in w['frames'][boundary[origin]], 'line outside boundary frame')
        vectors = [w['lines'][line] for _, line in record['witness']]
        if rank == 8:
            determinant = bareiss(vectors)
            require(determinant != 0, 'dependent witness')
            determinants.append(abs(determinant))
        else:
            require(integer_rank(vectors) == rank, 'dependent proper witness')
    return {'independent_forward_dimension': n,
            'cleanup_profile': profile,
            'proper_source_bounds': {str(r['register']): r['rank_lower_bound']
                for r in certificate['endpoints'] if r['rank_lower_bound'] < 8},
            'nonzero_determinants': len(determinants),
            'absolute_determinants': dict(sorted(Counter(map(str, determinants)).items()))}


def controls(w, certificate):
    from copy import deepcopy
    corruptions = []
    c = deepcopy(certificate)
    c['endpoints'].pop()
    corruptions.append(('missing endpoint', c))
    c = deepcopy(certificate)
    c['endpoints'][0]['inverse_support'].append(w['v'])
    corruptions.append(('wrong inverse support', c))
    c = deepcopy(certificate)
    c['endpoints'][0]['witness'][1] = c['endpoints'][0]['witness'][0]
    corruptions.append(('dependent witness', c))
    c = deepcopy(certificate)
    c['endpoints'][0]['witness'][0][0] = w['v']
    corruptions.append(('target as unsupported input', c))
    c = deepcopy(certificate)
    c['boundary_frames'][0] = 0
    corruptions.append(('underpriced boundary', c))
    if w['v'] == 111:
        c = deepcopy(certificate)
        full = next(i for i, f in enumerate(w['frames']) if len(f) == len(w['lines']))
        c['boundary_frames'][w['ret'][0]] = full
        corruptions.append(('invented full-frame climb at rank-seven COPY', c))
    for name, c in corruptions:
        try:
            independent(w, c)
        except ValueError:
            continue
        raise ValueError('accepted control: ' + name)
    return [name for name, _ in corruptions]


def scope_controls():
    # On an abstract two-frame chain L < H, a <- a+b at L followed by b's
    # climb to H makes post-boundary restoration of a require H. Undoing a
    # before that climb is allowed outside this theorem's fixed prefix.
    for a in range(2):
        for b in range(2):
            encoded = a ^ b
            require((encoded ^ b) == a, 'early restoration toy')
    # Cancellation can delete syntactic paths. A twice-repeated XOR has no
    # off-diagonal coefficient; the theorem must use the semantic inverse.
    for a in range(2):
        for b in range(2):
            require((a ^ b ^ b) == a, 'cancelled dependency toy')
    # Forward support is insufficient: U = [[1,1,0],[0,1,1],[0,0,1]].
    for a in range(2):
        for b in range(2):
            for c in range(2):
                p, q, r = a ^ b, b ^ c, c
                require((p ^ q ^ r) == a, 'inverse orientation toy')
                if c:
                    require((p ^ q) != a, 'missing inverse coefficient toy')
    return ['early restoration outside fixed prefix',
            'cancelled syntactic paths', 'inverse versus forward dependence']


def exhaustive_toy():
    """Enumerate the closure of two-register XOR/MOVE circuits on a diamond
    0 < {L,M} < H. This finite check supports, but does not prove, the lemma.
    """
    from collections import deque
    checked = 0
    for f in range(4):
        for g in range(4):
            start = ((1, 2), (f, g))
            seen, queue = {start}, deque([start])
            while queue:
                rows, frames = queue.popleft()
                for r in range(2):
                    required = (f, g)[r]
                    for s in range(2):
                        if rows[r] >> s & 1:
                            required |= (f, g)[s]
                    require(required & ~frames[r] == 0, 'toy information flow')
                    checked += 1
                next_states = []
                for r in range(2):
                    for upper in range(4):
                        if frames[r] & ~upper == 0:
                            fs = list(frames)
                            fs[r] = upper
                            next_states.append((rows, tuple(fs)))
                    rr = list(rows)
                    rr[r] ^= rr[1-r]
                    common = frames[0] | frames[1]
                    next_states.append((tuple(rr), (common, common)))
                for state in next_states:
                    if state not in seen:
                        seen.add(state)
                        queue.append(state)
    return checked


def native_boundary(w, certificate, name):
    """Bind the model to the unchanged owning checker, including COPY frames.
    This is a third boundary check, not an independent new supplier replay.
    """
    import importlib.util
    paths = {'r420': 'research/e8-bit-r420/code/xcheck.py',
             'r439': 'research/e8-bit-p111-tuned/code/xcheck_p.py'}
    spec = importlib.util.spec_from_file_location('native_' + name, ROOT / paths[name])
    module = importlib.util.module_from_spec(spec)
    previous = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    native = module.Word(w)
    _, boundary, _ = native.replay(sections=('D', 'A', 'scatter', 'B'))
    require(boundary == certificate['boundary_frames'], 'owning checker boundary disagreement')
    _, scatter_boundary, _ = native.replay(sections=('D', 'A'))
    return [native.fdim[scatter_boundary[r]] for r in w['ret']]


def main():
    require(not sys.argv[1:], 'unknown arguments')
    result = {}
    for name in ('r420', 'r439'):
        w = read_source(name)
        certificate = derive(w)
        path = HERE / ('CERTIFICATE-' + name + '.json')
        require(certificate == json.loads(path.read_text()), 'certificate mismatch')
        result[name] = independent(w, certificate)
        result[name]['native_copy_ranks'] = native_boundary(w, certificate, name)
        result[name]['negative_controls'] = controls(w, certificate)
    result['scope_controls'] = scope_controls()
    result['toy_endpoint_checks'] = exhaustive_toy()
    print(json.dumps(result, sort_keys=True))
    print('PASS_BIT_CLEANUP_FRAME_OBSTRUCTION helpers=420+439 '
          'independent_inverse=540+550 proper_source_exceptions=3 controls=14')


if __name__ == '__main__':
    main()
