#!/usr/bin/env python3
# Copyright 2026 Adam Gall. SPDX-License-Identifier: Apache-2.0
"""Exact observer-defect census and emitted recursive shear words; stdlib only."""
import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def eye(n):
    return tuple(tuple(int(i == j) for j in range(n)) for i in range(n))


def mul(a, b):
    return tuple(tuple(sum(x * y for x, y in zip(row, col))
                       for col in zip(*b)) for row in a)


def sub(a, b):
    return tuple(tuple(x - y for x, y in zip(r, s)) for r, s in zip(a, b))


def add(a, b):
    return tuple(tuple(x + y for x, y in zip(r, s)) for r, s in zip(a, b))


def inverse(a):
    n = len(a)
    rows = [[Q(x) for x in a[i] + eye(n)[i]] for i in range(n)]
    for j in range(n):
        k = next(i for i in range(j, n) if rows[i][j])
        rows[j], rows[k] = rows[k], rows[j]
        scale = rows[j][j]
        rows[j] = [x / scale for x in rows[j]]
        for i in range(n):
            if i != j:
                scale = rows[i][j]
                rows[i] = [x - scale * y for x, y in zip(rows[i], rows[j])]
    return tuple(tuple(row[n:]) for row in rows)


def block(b, g):
    return ((1,) + tuple(b),) + tuple((0,) + row for row in g)


def defect(bs, gs):
    p, delta, prefixes = eye(2), ((0, 0),), []
    for b, g in zip(bs, gs):
        delta = add(delta, mul((b,), sub(p, eye(2))))
        prefixes.append(delta)
        p = mul(g, p)
    return delta, prefixes, p


def operator(bs, gs, eager):
    word = eye(3)
    for b, g in zip(bs, gs):
        word = mul(block(b, g), word)
        if eager:
            word = mul(block((0, 0), inverse(g)), word)
    if not eager:
        p = eye(2)
        for g in gs:
            p = mul(g, p)
        word = mul(block((0, 0), inverse(p)), word)
    return word


def census():
    gs_domain = (((1, 1), (0, 1)), ((1, -1), (0, 1)),
                 ((1, 0), (1, 1)), ((1, 0), (-1, 1)))
    readers = list(product((-1, 0, 1), repeat=2))
    counts = Counter()
    digest = sha256()
    # Block products here use the known integral inverse of each elementary shear.
    # Avoid rational elimination in the 46,656-case inner loop.
    for gs in product(gs_domain, repeat=3):
        p = eye(2)
        for g in gs:
            p = mul(g, p)
        pinv = tuple(tuple(int(x) for x in row) for row in inverse(p))
        for bs in product(readers, repeat=3):
            delta, prefixes, _ = defect(bs, gs)
            word = eye(3)
            eager = eye(3)
            for index, (b, g) in enumerate(zip(bs, gs)):
                word = mul(block(b, g), word)
                eager = mul(block(b, eye(2)), eager)
                require(tuple(x - y for x, y in zip(word[0][1:], eager[0][1:])) == prefixes[index][0],
                        'prefix block product disagrees with defect')
            word = mul(block((0, 0), pinv), word)
            difference = sub(word, eager)
            require(difference == ((0,) + delta[0], (0, 0, 0), (0, 0, 0)),
                    'block product disagrees with defect')
            terminal = delta == ((0, 0),)
            causal = all(v == ((0, 0),) for v in prefixes)
            counts['cases'] += 1
            counts['terminal_safe'] += terminal
            counts['prefix_safe'] += causal
            counts['terminal_only'] += terminal and not causal
            counts['safe_with_reader'] += terminal and any(any(b) for b in bs)
            digest.update(bytes((terminal, causal)))
    return dict(counts, classification_sha256=digest.hexdigest())


def emit(depth, r, alphas, eager, offset=0, n=None):
    """Events (target stream, source stream, coefficient, offset, length)."""
    n = r ** depth if n is None else n
    if depth == 0:
        return []
    out = []
    for i, alpha in enumerate(alphas):
        # Source-restoring child on its own partition, with inherited dirty W0.
        out += emit(depth - 1, r, alphas, eager, offset + i * (n // r), n // r)
        out.append((0, 2, 1, offset, n))  # observable reader D += W1
        out.append((1, 2, alpha, offset, n))  # drift W0 += alpha W1
        if eager:
            out.append((1, 2, -alpha, offset, n))
    if not eager and sum(alphas):
        out.append((1, 2, -sum(alphas), offset, n))
    return out


def replay(events, state):
    state = [list(row) for row in state]
    for t, s, a, offset, n in events:
        for j in range(offset, offset + n):
            state[t][j] += a * state[s][j]
    return state


def invoice(events):
    adds = sum(n for _, _, _, _, n in events)
    multiplies = sum(n for _, _, a, _, n in events if abs(a) != 1)
    return {'adds': adds, 'constant_multiplies': multiplies,
            'scalar_primitives': adds + multiplies,
            'data_reads': 2 * adds + multiplies,
            'data_writes': adds + multiplies}


def recursive_checks():
    rows = []
    columns = 0
    for r, alphas in [(3, (1, 1, 1)), (5, (1, -1, 1, -1, 1))]:
        for depth in range(4):
            n = r ** depth
            eager, deferred = emit(depth, r, alphas, True), emit(depth, r, alphas, False)
            e, f = invoice(eager), invoice(deferred)
            restoration = int(sum(alphas) != 0)
            extra_mul = int(abs(sum(alphas)) > 1)
            require(e['adds'] == 3 * r * n * depth, 'eager recurrence')
            require(f['adds'] == (2 * r + restoration) * n * depth, 'deferred recurrence')
            require(f['constant_multiplies'] == extra_mul * n * depth, 'multiply recurrence')
            # Full basis of arbitrary D,W0,W1, not just zero-initialized helpers.
            for k in range(3 * n):
                state = [[0] * n for _ in range(3)]
                state[k // n][k % n] = 1
                a, b = replay(eager, state), replay(deferred, state)
                require(a == b, 'recursive dirty-column mismatch')
                require(b[1:] == state[1:], 'recursive restoration mismatch')
                require(b[0] == [x + r * depth * y for x, y in zip(state[0], state[2])],
                        'recursive reader output mismatch')
                reverse = [(t, s, -c, off, size) for t, s, c, off, size in reversed(deferred)]
                require(replay(reverse, b) == state, 'inverse replay mismatch')
                columns += 1
            rows.append({'r': r, 'depth': depth, 'length': n,
                         'alphas': alphas, 'eager': e, 'deferred': f,
                         'dirty_data_scalars': 3 * n,
                         'temporary_scalar_bound': extra_mul,
                         'sufficient_magnitude_factor': 1 + r * depth})
    return {'basis_columns_both_directions': columns, 'invoices': rows}


def controls():
    up = ((1, 1), (0, 1))
    down = ((1, 0), (1, 1))
    safe = ((0, 1),) * 3
    require(operator(safe, (up,) * 3, True) == operator(safe, (up,) * 3, False),
            'nonzero invariant readers rejected')
    cancellation = ((0, 0), (2, 0), (-1, 0))
    delta, prefixes, _ = defect(cancellation, (up,) * 3)
    require(delta == ((0, 0),) and prefixes[1] != ((0, 0),), 'terminal cancellation fixture')
    require(operator(cancellation, (up,) * 3, True) == operator(cancellation, (up,) * 3, False),
            'terminal cancellation rejected')
    names = []
    bad = ((0, 1), (1, 1), (0, 1))
    require(operator(bad, (up,) * 3, True) != operator(bad, (up,) * 3, False), 'reader control')
    names.append('reader outside drift annihilator')
    require(prefixes[1] != ((0, 0),), 'prefix observation control')
    names.append('terminal cancellation is not prefix safe')
    gs = (up, down)
    p = mul(down, up)
    wrong_restore = mul(inverse(down), inverse(up))
    require(mul(wrong_restore, p) != eye(2), 'inverse order control')
    names.append('noncommuting inverse restoration order')
    require(mul(up, mul(up, up)) != eye(2), 'omitted restore control')
    names.append('omitted final restoration')
    require(defect(safe, (up, down, up))[0] != ((0, 0),), 'changed shear direction control')
    names.append('changed shear leaves reader annihilator')
    require(operator(bad, (up,) * 3, True)[0][2] != operator(bad, (up,) * 3, False)[0][2],
            'zero dirty helper hides defect control')
    names.append('arbitrary dirty helper required')
    # Nonintegral coefficients exercise exact rational arithmetic independently.
    rational = (((1, Q(1, 2)), (0, 1)), ((1, 0), (Q(-2, 3), 1)),
                ((1, Q(3, 5)), (0, 1)))
    bs = ((Q(2, 7), Q(-3, 4)), (Q(1, 3), Q(4, 5)), (Q(-2, 9), Q(1, 2)))
    d, _, _ = defect(bs, rational)
    difference = sub(operator(bs, rational, False), operator(bs, rational, True))
    require(difference == ((0,) + d[0], (0, 0, 0), (0, 0, 0)), 'rational defect')
    return {'rejected': names, 'invariant_reader': safe,
            'terminal_only_readers': cancellation, 'rational_defect': [[str(x) for x in row] for row in d]}


def calculate():
    pins = json.loads((ROOT / 'SOURCES.json').read_text())
    for name, expected in pins['files'].items():
        require(sha256((ROOT / name).read_bytes()).hexdigest() == expected, 'source pin: ' + name)
    return {'status': 'PASS_OBSERVER_SAFE_RESTORATION', 'seed': 52,
            'census': census(), 'recursive': recursive_checks(), 'controls': controls()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', type=Path, help='create a fresh certificate; never overwrite')
    args = parser.parse_args()
    result = calculate()
    payload = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.write:
        with args.write.open('x') as f:
            f.write(payload)
    else:
        require(json.loads(payload) == json.loads((ROOT / 'EXPECTED.json').read_text()), 'certificate drift')
    print(result['status'], 'cases=' + str(result['census']['cases']),
          'columns=' + str(result['recursive']['basis_columns_both_directions']),
          'controls=' + str(len(result['controls']['rejected'])))
    print(json.dumps(result['census'], sort_keys=True))


if __name__ == '__main__':
    main()
