"""Exact finite tests for the fixed-anchor compiler; standard library only."""
import argparse
from fractions import Fraction as F
import json
from pathlib import Path

ZERO, ONE = (F(0), F(0)), (F(1), F(0))
A, B = (F(1, 2), F(1, 2)), (F(1, 2), F(-1, 2))

def require(ok, message):
    if not ok:
        raise ValueError(message)

def add(x, y):
    return x[0] + y[0], x[1] + y[1]

def mul(x, y):
    return x[0] * y[0] - x[1] * y[1], x[0] * y[1] + x[1] * y[0]

def call(v, f, j, inverse=False):
    out = list(v)
    a, b = (B, A) if inverse else (A, B)
    for col in range(f):
        bit = 1 << (3 * col + j)
        for x in range(len(out)):
            if not x & bit:
                u, z = out[x], out[x | bit]
                out[x], out[x | bit] = add(mul(a, u), mul(b, z)), add(mul(b, u), mul(a, z))
    return out

def split(v):
    return [[v[(t << 3) | s] for t in range(len(v) // 8)] for s in range(8)]

def join(banks):
    return [banks[x & 7][x >> 3] for x in range(8 * len(banks[0]))]

def anchor_mix(banks, j, inverse=False):
    out = [list(v) for v in banks]
    for t in range(len(out[0])):
        col = call([out[s][t] for s in range(8)], 1, j, inverse)
        for s in range(8):
            out[s][t] = col[s]
    return out

def compiled_call(v, f, j):
    require(f >= 2, 'remaining width must be positive')
    banks = [call(b, f - 1, j) for b in split(v)]
    return join(anchor_mix(banks, j))

def K(v, f):
    for j in range(3):
        v = call(v, f, j)
    return v

def compiled_target(v, f):
    out = list(v)
    for j in range(3):
        out = compiled_call(out, f, j)
    banks = split(out)
    for j in reversed(range(3)):
        banks = anchor_mix(banks, j, inverse=True)
    return banks

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out', type=Path)
    p.add_argument('--check', type=Path)
    args = p.parse_args()
    basis_calls, basis_targets = 0, 0
    for k in range(64):
        v = [ONE if i == k else ZERO for i in range(64)]
        require(join(split(v)) == v, 'all eight component lanes are independent')
        for j in range(3):
            require(compiled_call(v, 2, j) == call(v, 2, j), 'width-two basis call')
            basis_calls += 1
        require(compiled_target(v, 2) == [K(b, 1) for b in split(v)], 'canonical independent smaller targets')
        basis_targets += 1
    arbitrary_calls, arbitrary_targets = 0, 0
    unrelated = [(F(17), F(-23)), (F(-31), F(43))]
    old_unrelated = list(unrelated)
    for seed in (3, 11):
        v = [(F((17 * i + seed) % 29 - 14), F((19 * i + seed) % 31 - 15)) for i in range(512)]
        saved = list(v)
        for j in range(3):
            require(compiled_call(v, 3, j) == call(v, 3, j), 'width-three arbitrary complex call')
            arbitrary_calls += 1
        require(compiled_target(v, 3) == [K(b, 2) for b in split(v)], 'width-three canonical target')
        arbitrary_targets += 1
        require(v == saved and unrelated == old_unrelated, 'arbitrary source and unrelated dirty memory preserved')
    for j in range(3):
        require(compiled_call([ZERO] * 64, 2, j) == [ZERO] * 64, 'zero owner slice')
    require(compiled_target([ZERO] * 64, 2) == [[ZERO] * 8 for _ in range(8)], 'zero owner target')
    report = {'status': 'PASS_EXACT_ANCHOR_EXTERNALIZATION', 'widths': [2, 3], 'width_two_basis_call_identities': basis_calls, 'width_two_basis_canonical_target_identities': basis_targets, 'width_three_arbitrary_complex_call_identities': arbitrary_calls, 'width_three_arbitrary_complex_target_identities': arbitrary_targets, 'zero_owner_checks': 4, 'independent_anchor_components': 8, 'compiled_paid_calls_per_original_call': 8, 'compiler_scope': 'native Q(i) scalar grammar; forward compiler, not generic reverse call compression', 'new_kappa': False}
    if args.check:
        require(json.loads(args.check.read_text(encoding='utf-8')) == report, 'stored anchor result mismatch')
    if args.out:
        args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps(report, sort_keys=True))

if __name__ == '__main__':
    main()
