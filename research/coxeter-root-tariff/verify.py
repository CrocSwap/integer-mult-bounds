#!/usr/bin/env python3
"""Exact Cartan-coordinate and full group-algebra corroboration; stdlib only."""
import argparse
from collections import Counter, deque
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
INPUTS = {
    'research/finite-dihedral-cut-bound/README.md',
    'research/infinite-dihedral-register-bound/README.md',
    'research/symmetric-adjacent-cut-bound/PROOF.md',
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def unique_object(pairs):
    out = {}
    for key, value in pairs:
        require(key not in out, 'duplicate JSON key: '+key)
        out[key] = value
    return out


def read_json(path):
    return json.loads(path.read_text(), object_pairs_hook=unique_object)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def ident(n):
    return tuple(tuple(int(i == j) for j in range(n)) for i in range(n))


def mul(a, b):
    n = len(a)
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(n))
                       for j in range(n)) for i in range(n))


def action(a, v):
    return tuple(sum(x * y for x, y in zip(row, v)) for row in a)


def neg(v):
    return tuple(-x for x in v)


def positive(v):
    return any(v) and all(x >= 0 for x in v)


def reflections(cartan):
    out = []
    for i in range(len(cartan)):
        a = [list(row) for row in ident(len(cartan))]
        for j, x in enumerate(cartan[i]):
            a[i][j] -= x
        out.append(tuple(map(tuple, a)))
    return out


def closure(cartan, expected_order):
    n = len(cartan)
    gens = reflections(cartan)
    unit = ident(n)
    words = {unit: ()}
    queue = deque([unit])
    while queue:
        g = queue.popleft()
        for i, s in enumerate(gens):
            h = mul(g, s)
            if h not in words:
                words[h] = words[g] + (i,)
                queue.append(h)
                require(len(words) <= expected_order, 'unexpected group order')
    require(len(words) == expected_order, 'incomplete group')
    roots = {action(g, a) for g in words for a in ident(n)}
    require(all(positive(a) or positive(neg(a)) for a in roots), 'root sign')
    remaining = set(roots)
    orbits = []
    while remaining:
        a = min(remaining)
        orbit = {action(g, a) for g in words}
        require(orbit <= remaining, 'overlapping root orbits')
        orbits.append(orbit)
        remaining -= orbit
    simple = ident(n)
    orbits.sort(key=lambda o: min(i for i, a in enumerate(simple) if a in o))
    classes = [next(k for k, o in enumerate(orbits) if a in o) for a in simple]
    for i, s in enumerate(gens):
        crossing = {a for a in roots if positive(a) and positive(neg(action(s, a)))}
        require(crossing == {simple[i]}, 'simple-reflection crossing')
    inversions = {}
    for g, word in words.items():
        inv = tuple(sum(positive(a) and positive(neg(action(g, a))) for a in o)
                    for o in orbits)
        count = Counter(classes[i] for i in word)
        require(inv == tuple(count[k] for k in range(len(orbits))), 'orbit tariff')
        require(sum(inv) == len(word), 'length/inversion identity')
        inversions[g] = inv
    for g, inv in inversions.items():
        for i, s in enumerate(gens):
            wanted = list(inv)
            wanted[classes[i]] += 1 if positive(action(g, simple[i])) else -1
            require(inversions[mul(g, s)] == tuple(wanted), 'weighted inversion recurrence')
    return gens, words, orbits, {
        'order': len(words), 'roots': len(roots),
        'positive_orbit_sizes': [sum(map(positive, o)) for o in orbits],
        'directed_edges': len(words) * n,
        'tariff_histogram': [[list(k), v] for k, v in sorted(Counter(inversions.values()).items())],
    }


def brank(rows):
    basis = {}
    for x in rows:
        while x:
            p = x.bit_length() - 1
            if p in basis:
                x ^= basis[p]
            else:
                basis[p] = x
                break
    return len(basis)


def bmul(a, b, n):
    out = 0
    for i in range(n):
        for j in range(n):
            x = 0
            for k in range(n):
                x ^= ((a >> (i*n+k)) & 1) & ((b >> (k*n+j)) & 1)
            out |= x << (i*n+j)
    return out


def bidentity(n):
    return sum(1 << (i*n+i) for i in range(n))


def formal_mul(a, b, n):
    """Group-matrix keys and packed binary role-matrix coefficients."""
    c = {}
    for g, x in a.items():
        for h, y in b.items():
            gh = mul(g, h)
            c[gh] = c.get(gh, 0) ^ bmul(x, y, n)
    return {g: x for g, x in c.items() if x}


def paid(s, p, r):
    return {g: x for g, x in [(ident(len(s)), bidentity(r) ^ p), (s, p)] if x}


def represented(a, roots, r):
    labels = {v: i for i, v in enumerate(roots)}
    n = len(roots)
    rows = [0] * (r*n)
    for g, coeff in a.items():
        for col, v in enumerate(roots):
            row = labels[action(g, v)]
            for i in range(r):
                for j in range(r):
                    if (coeff >> (i*r+j)) & 1:
                        rows[i*n+row] ^= 1 << (j*n+col)
    return rows


def cut_rank(a, orbit, r):
    roots = sorted(orbit)
    rows = represented(a, roots, r)
    n = len(roots)
    columns = sum(1 << (j*n+k) for j in range(r)
                  for k, v in enumerate(roots) if positive(v))
    return brank([rows[i*n+k] & columns for i in range(r)
                  for k, v in enumerate(roots) if not positive(v)])


def formal_checks(gens, words, orbits):
    e = ident(2)
    gate_count = nilpotent_count = 0
    for r in range(1, 4):
        for p in range(1 << (r*r)):
            rank = brank([(p >> (i*r)) & ((1 << r)-1) for i in range(r)])
            if p and bmul(p, p, r) == 0:
                nilpotent_count += 1
            for i, s in enumerate(gens):
                d = paid(s, p, r)
                require(formal_mul(d, d, r) == {e: bidentity(r)}, 'arbitrary coupling involution')
                for orbit in orbits:
                    want = rank if ident(2)[i] in orbit else 0
                    require(cut_rank(d, orbit, r) == want, 'rank charged crossing')
                gate_count += 1
    formal_targets = omitted_rejections = 0
    r = 3
    for a, b in itertools.product(words, repeat=2):
        circuit = [paid(gens[i], 1 << (role*r+role), r)
                   for role, g in enumerate((a, b)) for i in words[g]]
        target = {}
        for role, g in enumerate((a, b, e)):
            target[g] = target.get(g, 0) ^ (1 << (role*r+role))
        state = {e: bidentity(r)}
        for d in circuit:
            state = formal_mul(state, d, r)
        require(state == target, 'formal endpoint')
        for k in range(len(circuit)):
            bad = {e: bidentity(r)}
            for j, d in enumerate(circuit):
                if j != k:
                    bad = formal_mul(bad, d, r)
            require(bad != target, 'omission not detected')
            omitted_rejections += 1
        formal_targets += 1
    # Norm of B2 is nonzero formally, zero on both four-root orbits.
    # A dirty offdiagonal norm leak is therefore invisible in this quotient.
    leak = {g: 1 << 1 for g in words}
    require(len(leak) == 8, 'norm is formally zero')
    for orbit in orbits:
        require(not any(represented(leak, sorted(orbit), 3)), 'norm kernel')
    corrupt = dict(leak)
    corrupt[e] = corrupt.get(e, 0) ^ bidentity(3)
    require(corrupt != {e: bidentity(3)}, 'dirty leak endpoint accepted')
    rank_two = (1 << 0) | (1 << 4)
    require(cut_rank(paid(gens[0], rank_two, 3), orbits[0], 3) == 2,
            'rank-two undercharging control')
    a = (1, 0)
    require(a != neg(a) and tuple(x % 2 for x in a) == tuple(x % 2 for x in neg(a)),
            'signed labels control')
    return {'arbitrary_coupling_gates': gate_count,
            'nonzero_square_zero_couplings': nilpotent_count,
            'formal_B2_target_pairs': formal_targets,
            'single_gate_omissions_rejected': omitted_rejections,
            'norm_kernel_formal_terms': len(leak),
            'boundary_controls': ['norm_kernel_dirty_leak', 'rank_two_undercharge', 'root_sign_mod2']}


def infinite_affine_checks():
    # Affine A2 exact integer matrices; never reduce to a finite quotient.
    gens = reflections(((2,-1,-1),(-1,2,-1),(-1,-1,2)))
    states = {ident(3): frozenset()}
    frontier = dict(states)
    layers = [1]
    transitions = 0
    for depth in range(1, 10):
        nxt = {}
        for g, inv in frontier.items():
            for i, s in enumerate(gens):
                alpha = ident(3)[i]
                out = {action(s, a) for a in inv if a != alpha}
                if alpha not in inv:
                    out.add(alpha)
                h = mul(g, s)
                require(all(positive(a) and positive(neg(action(h, a))) for a in out),
                        'affine inversion label/sign')
                require(len(out) == len(inv) + (1 if alpha not in inv else -1),
                        'affine one-root update')
                if h in states:
                    require(states[h] == frozenset(out), 'affine alternate-word consistency')
                else:
                    if h in nxt:
                        require(nxt[h] == frozenset(out), 'affine same-layer consistency')
                    nxt[h] = frozenset(out)
                transitions += 1
        require(all(len(inv) == depth for inv in nxt.values()), 'affine reduced lengths')
        states.update(nxt)
        frontier = nxt
        layers.append(len(nxt))
    require(max(abs(x) for g in states for row in g for x in row) > 2, 'affine quotient trap')
    return {'radius': 9, 'layers': layers, 'exact_matrices': len(states),
            'transitions': transitions, 'scope': 'finite exact probe; infinite claim rests on proof'}


def pins():
    manifest = read_json(HERE/'SOURCES.json')
    inputs = [x['path'] for x in manifest['files'] if x['usage'] == 'input']
    require(len(inputs) == len(INPUTS) and set(inputs) == INPUTS, 'source inventory mismatch')
    for item in manifest['files']:
        if item['usage'] == 'input':
            data = (ROOT/item['path']).read_bytes()
            require(hashlib.sha256(data).hexdigest() == item['sha256'], 'source drift: '+item['path'])


def compute():
    pins()
    systems = {
        'A2': (((2,-1),(-1,2)), 6),
        'A3': (((2,-1,0),(-1,2,-1),(0,-1,2)), 24),
        'A4': (((2,-1,0,0),(-1,2,-1,0),(0,-1,2,-1),(0,0,-1,2)), 120),
        'B2': (((2,-2),(-1,2)), 8),
        'B3': (((2,-2,0),(-1,2,-1),(0,-1,2)), 48),
        'B4': (((2,-2,0,0),(-1,2,-1,0),(0,-1,2,-1),(0,0,-1,2)), 384),
        'D4': (((2,-1,0,0),(-1,2,-1,-1),(0,-1,2,0),(0,-1,0,2)), 192),
        'F4': (((2,-1,0,0),(-1,2,-2,0),(0,-1,2,-1),(0,0,-1,2)), 1152),
        'G2': (((2,-3),(-1,2)), 12),
    }
    results = {}
    fixture = None
    for name, (cartan, order) in systems.items():
        gens, words, orbits, result = closure(cartan, order)
        results[name] = result
        if name == 'B2':
            fixture = (gens, words, orbits)
    return {'finite_systems': results, 'formal': formal_checks(*fixture),
            'affine_A2': infinite_affine_checks(), 'no_new_kappa': True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true', help='explicitly regenerate RESULT.json')
    args = parser.parse_args()
    result = compute()
    if args.write:
        (HERE/'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    else:
        require(canonical(result) == canonical(read_json(HERE/'RESULT.json')), 'receipt mismatch')
    count = sum(x['order'] for x in result['finite_systems'].values())
    print('PASS_COXETER_ROOT_TARIFF finite_elements='+str(count)+
          ' systems=9 affine_radius=9 formal_pairs=64 no_new_kappa')


if __name__ == '__main__':
    main()
