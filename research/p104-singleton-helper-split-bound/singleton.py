"""Search fixed-word single-helper cuts with no shared change of basis."""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction
from functools import cache
import gzip
from hashlib import sha256
import json
from pathlib import Path
from random import Random
from time import monotonic

WORD_SHA256 = '2c523ce6fdd6092d758fedc3602a0bcedb692b9766f1e41f903351ba4dee1756'
PRIME = 2305843009213693951
SEED = 7277


def add(vector, r, value):
    updated = vector.get(r, 0) + value
    if updated:
        vector[r] = updated
    else:
        vector.pop(r, None)


def scale(vector, r, factor):
    if r in vector:
        value = vector[r] * factor
        if value:
            vector[r] = value
        else:
            del vector[r]


@cache
def residue(value):
    q = Fraction(value)
    return q.numerator * pow(q.denominator, -1, PRIME) % PRIME


@cache
def rational(value):
    return Fraction(value)


def span(frame):
    result = {0}
    for b in frame:
        assert b not in result
        result |= {a ^ b for a in result}
    return result


def assess(word, cap, seconds):
    start = monotonic()
    program, n, frames = word['program'], word['public'], word['frames']
    main = set(word['live']) | {r+112 for r in word['live']} | set(word['hosted']['X2'] + word['hosted']['Y2'])
    assert len(main) == 400 and n - len(main) == 1101
    spaces = list(map(span, frames))
    current = word['initial'] + [None] * word['owned_fields']
    end = word['final']
    rng = Random(SEED)
    public_x = [rng.randrange(1, PRIME) for r in range(n)]
    public_y = [rng.randrange(1, PRIME) for r in range(n)]
    prefix_x = public_x + [0] * word['owned_fields']
    prefix_one = [1] * n + [0] * word['owned_fields']
    suffix_y = public_y + [0] * word['owned_fields']
    signatures = defaultdict(list)

    @cache
    def signature(r, f):
        u, v = word['initial'][r], end[r]
        if r not in main and spaces[u] < spaces[f] < spaces[v]:
            return (u, f, v)
        return None

    for t, (op, r, *args) in enumerate(program):
        touched = (r,)
        if op == 'MOVE':
            assert current[r] == args[0]
            current[r] = args[1]
        elif op in ('INIT', 'CLEAR'):
            current[r] = args[0] if op == 'INIT' else None
            prefix_x[r] = prefix_one[r] = 0
        elif op == 'SCALE':
            q = residue(args[0])
            prefix_x[r] = prefix_x[r] * q % PRIME
            prefix_one[r] = prefix_one[r] * q % PRIME
        elif op in ('ADD', 'COPY'):
            s, q = args[0], residue(args[1])
            assert current[s] == current[r] == args[-1]
            if op == 'COPY':
                prefix_x[r] = prefix_one[r] = 0
            prefix_x[r] = (prefix_x[r] + q * prefix_x[s]) % PRIME
            prefix_one[r] = (prefix_one[r] + q * prefix_one[s]) % PRIME
            touched = (r, s) if r != s else (r,)
        else:
            raise ValueError(op)
        for role in touched:
            if role < n and (sig := signature(role, current[role])) is not None:
                coefficient = prefix_one[role]
                passes = prefix_x[role] == public_x[role] * coefficient % PRIME
                signatures[sig].append((t, role, coefficient, passes))
    assert current == end + [None] * word['owned_fields']

    def order(sig):
        u, f, v = sig
        a, b = len(frames[f])-len(frames[u]), len(frames[v])-len(frames[f])
        return (-(a+b), -min(a,b), sig)

    ordered = sorted(signatures, key=order)
    selected = set(ordered[:cap])
    waiting = defaultdict(list)
    counts = Counter()
    for sig in selected:
        for t, role, coefficient, passes in signatures[sig]:
            if passes:
                waiting[t].append((role, coefficient, sig))
                counts['prefix_projection_pass'] += 1
    survivors = []
    for t in range(len(program)-1, -1, -1):
        for role, coefficient, sig in waiting.get(t, ()):
            if coefficient * suffix_y[role] % PRIME == public_y[role]:
                survivors.append((t, role, sig))
        op, r, *args = program[t]
        if op in ('CLEAR', 'INIT'):
            suffix_y[r] = 0
        elif op == 'SCALE':
            suffix_y[r] = suffix_y[r] * residue(args[0]) % PRIME
        elif op in ('ADD', 'COPY'):
            s, q = args[0], residue(args[1])
            update = suffix_y[r] * q
            if op == 'COPY':
                suffix_y[r] = 0
            suffix_y[s] = (suffix_y[s] + update) % PRIME

    def exact(t, role, sig):
        prefix = {role: Fraction(1)}
        for op, r, *args in reversed(program[:t+1]):
            if r not in prefix:
                continue
            if op in ('INIT', 'CLEAR'):
                prefix.pop(r)
            elif op == 'SCALE':
                scale(prefix, r, rational(args[0]))
            elif op in ('ADD', 'COPY'):
                coeff = prefix.pop(r) if op == 'COPY' else prefix[r]
                add(prefix, args[0], coeff * rational(args[1]))
        prefix = {r:q for r,q in prefix.items() if r<n}
        if len(prefix) != 1 or role not in prefix:
            return 'prefix-not-singleton', None
        coefficient = prefix[role]
        suffix = {role: Fraction(1)}
        for op, r, *args in program[t+1:]:
            if op in ('INIT', 'CLEAR'):
                suffix.pop(r, None)
            elif op == 'SCALE':
                scale(suffix, r, rational(args[0]))
            elif op in ('ADD', 'COPY'):
                coeff = suffix.get(args[0], 0)
                if op == 'COPY':
                    suffix.pop(r, None)
                if coeff:
                    add(suffix, r, coeff * rational(args[1]))
        if suffix != {role: 1/coefficient}:
            return 'suffix-not-inverse-singleton', None
        u, f, v = sig
        witness = {'cut_after': t, 'pivot': role, 'frame': f,
                   'ranks': [len(frames[f])-len(frames[u]), len(frames[v])-len(frames[f])],
                   'a': {role: '1'}, 'b': {role: '1'},
                   'c': {role: str(coefficient)}, 'd': {role: str(1/coefficient)}}
        return 'exact-singleton', witness

    tested = []
    for t, role, sig in sorted(survivors, key=lambda entry: (order(entry[-1]), entry[0], entry[1])):
        if monotonic()-start >= seconds:
            break
        outcome, witness = exact(t, role, sig)
        tested.append({'cut':t, 'role':role, 'signature':sig, 'outcome':outcome, 'witness':witness})
        counts[outcome] += 1
        if witness:
            break

    return {
        'head':'ed090b57ed88f8859e5ff4643645099e6ba856ea',
        'word_sha256':WORD_SHA256, 'public':n, 'helpers':n-len(main), 'seed':SEED, 'prime':PRIME,
        'signature_cap':cap, 'seconds':seconds, 'signatures':len(ordered),
        'selected_signatures':len(selected), 'unvisited_signatures':ordered[cap:],
        'representative_cuts':sum(map(len,signatures.values())),
        'selected_cuts':sum(len(signatures[s]) for s in selected),
        'counts':dict(counts),'projection_survivors':len(survivors),
        'unresolved_exact':len(survivors)-len(tested),'tested':tested,
    }


if __name__ == '__main__':
    assert __debug__
    parser = argparse.ArgumentParser()
    parser.add_argument('word', type=Path)
    parser.add_argument('--cap', type=int, default=128)
    parser.add_argument('--seconds', type=int, default=25)
    args = parser.parse_args()
    raw = args.word.read_bytes()
    assert sha256(raw).hexdigest() == WORD_SHA256
    print(json.dumps(assess(json.loads(gzip.decompress(raw)),args.cap,args.seconds),sort_keys=True,indent=2))
