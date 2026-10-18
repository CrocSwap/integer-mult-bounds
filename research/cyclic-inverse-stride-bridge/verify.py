"""Replay for the stride bridge. Standard library only.

    python3 -B research/cyclic-inverse-stride-bridge/verify.py --check
    python3 -B research/cyclic-inverse-stride-bridge/verify.py --write   # regenerate EXPECTED.json
"""
from fractions import Fraction as F
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import math
import sys

sys.set_int_max_str_digits(100000)
HERE = Path(__file__).resolve().parent


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


st = load(HERE / 'stride.py', 'bridge_stride')
need = st.need


def pinned_vendor():
    source = json.loads((HERE / 'SOURCE.json').read_text())
    for name, digest in source['vendored_sha256'].items():
        need(hashlib.sha256((HERE / 'vendor' / name).read_bytes()).hexdigest() == digest,
             'vendored source drift: ' + name)
    # check.py loads scan.py and interval_kernel.py from its own directory.
    return load(HERE / 'vendor' / 'check.py', 'pr628_check')


def unit(t):
    t = F(t)
    return ((1 - t * t) / (1 + t * t), 2 * t / (1 + t * t))


def coefficients(L, beta, seed):
    out = []
    for i in range(L):
        scale = (F(1), F(1, 2), F(0), F(1))[(i * 7 + seed) % 4]
        out.append(tuple((1 - beta) * scale * v for v in unit(F((i * 5 + seed) % 13 - 6, 5))))
    return out


def inputs(L, seed):
    return [(F((5 * i + seed) % 9 - 4, 8), F((7 * i + 3 * seed) % 11 - 5, 16)) for i in range(L)]


def generic():
    cases = 0
    worst = F(0)
    for g in (2, 3, 5):
        beta = F(1, 1 << g)
        for bits in (g + 6, 2 * g + 9):
            for L in range(1, 19):
                for w in range(-L, L):
                    K = st.levels(L, w)
                    need(st.admitted(beta, bits, K), 'admission')
                    b, x = coefficients(L, beta, L + w), inputs(L, L * w)
                    trace = []
                    y = st.solve(x, b, w, bits, st.Tape(), trace)
                    for row in trace:  # margin is preserved at every level
                        need(all(st.norm2(c) <= (1 - beta) ** 2 for c in row['b']), 'level margin')
                        need(2 * row['stride'] <= row['length'], 'stride halving')
                    exact = st.exact_cycle_solve(x, b, w)
                    bound = st.solve_error_bound(F(1), beta, bits, K)
                    for v, e in zip(y, exact):
                        err2 = st.norm2(st.sub(v, e))
                        need(err2 <= bound ** 2, 'generic error bound L=%d w=%d' % (L, w))
                        worst = max(worst, err2 / bound ** 2)
                    cases += 1
    return dict(cases=cases, max_error_to_bound_squared=float(worst))


def traffic():
    rows = []
    worst = 0
    for L in (1, 2, 3, 7, 64, 1000, 4096, 65536, 99991, 131072):
        phi = int(L * 0.6180339887) or 1
        for w in sorted({0, 1, 2, 3, L // 2, L // 2 + 1, L - 1, phi, (L // 3) or 1, 97 % L}):
            tape = st.Tape()
            st.solve([None] * L, [None] * L, w, None, tape)
            K = st.levels(L, w)
            need(K <= max(1, L).bit_length(), 'depth bound')
            need(sum(n for n, _ in tape.levels) <= 2 * L, 'geometric level sizes')
            ratio = F(tape.records, L)
            need(ratio <= 40, 'linear traffic L=%d w=%d' % (L, w))
            worst = max(worst, ratio)
            sort_route = 4 * L * max(1, math.ceil(math.log2(L))) if L > 1 else 0
            rows.append(dict(length=L, stride=w, levels=K, records=tape.records,
                             records_per_entry=float(ratio), pr628_sort_route_records=sort_route))
    return dict(max_records_per_entry=float(worst), rows=rows)


def apply_kernel(c, state, x, w, tau, bits, tape, mutate=None):
    r = state['radix']
    L = len(x)
    y = [(v[0] * r, v[1] * r) for v in x]
    taubar = (tau[0], -tau[1])
    for inside, b in state['factors']:
        if inside:  # (U-rho)^-1 = (I - rho U^-1)^-1 U^-1, U = tau Z^w
            shift = w if mutate != 'wrong_inner_shift' else -w
            v = [y[(i + shift) % L] for i in range(L)]
            y = st.solve(v, [st.mul(b, taubar)] * L, -w, bits, tape)
            y = [st.rounded(st.mul(taubar, t), bits) for t in y]
        else:  # (U-rho)^-1 = -rho^-1 (I - rho^-1 U)^-1, here b = 1/rho
            y = st.solve(y, [st.mul(b, tau)] * L, w, bits, tape)
            y = [st.rounded(st.mul((-b[0], -b[1]), t), bits) for t in y]
    return y


def cascade_bound(state, L, w):
    """Execution budget for the factor cascade, Theorem 2 of PROOF.md."""
    beta, bits, r = state['beta'], state['bits'], state['radix']
    K = max(st.levels(L, w), st.levels(L, -w))
    need(st.admitted(beta, bits, K), 'cascade admission')
    u = F(1, 1 << bits)
    error, norm = F(0), F(r)
    for _ in state['factors']:
        # one solve plus one rounded scalar multiplication of modulus <= 1
        error = error / beta + st.solve_error_bound(norm + error, beta, bits, K) + u
        norm /= beta
    return error


def kernels(c):
    data = json.loads((HERE / 'vendor' / 'FACTORS.json').read_text())
    rows = []
    for row in data:
        state = c.certify(row)
        perturbation = F(state['certificate']['factorization_inverse_error_bound'])
        for tau_name, tau in (('1', st.ONE), ('3/5+4i/5', (F(3, 5), F(4, 5)))):
            for L in (1, 2, 3, 5, 8):
                strides = range(L) if L <= 5 else (1, 3, 5, 7)
                for w in strides:
                    x = inputs(L, w + L)
                    tape = st.Tape()
                    y = apply_kernel(c, state, x, w, tau, state['bits'], tape)
                    bound = cascade_bound(state, L, w)
                    need(bound + perturbation <= F(1, 1 << row['target_bits']), 'target budget')
                    q = c.phased_polynomial(state['q'], tau)
                    dense = L <= 2 or (L == 3 and row['radix'] <= 9 and tau_name == '1')
                    if dense:  # independent exact Gauss-Jordan solve of Q(tau Z^w)
                        exact = c.matrix_solve(x, q, w)
                        need(all(st.norm2(st.sub(v, e)) <= bound ** 2 for v, e in zip(y, exact)),
                             'dense kernel comparison r=%d L=%d w=%d' % (row['radix'], L, w))
                    # expanded residual: ||Q(U)y - x|| <= ||Q||_1 * execution bound
                    scale = sum(abs(v[0]) + abs(v[1]) for v in q) * bound
                    for i in range(L):
                        total = st.ZERO
                        for j, v in enumerate(q):
                            total = st.add(total, st.mul(v, y[(i - w * j) % L]))
                        need(st.norm2(st.sub(total, x[i])) <= scale ** 2, 'kernel residual')
                    rows.append(dict(radix=row['radix'], embedding=row['embedding'], gauge=tau_name,
                                     length=L, stride=w, dense=dense,
                                     execution_bound_log2=round(math.log2(bound), 3),
                                     total_bound_log2=round(math.log2(bound + perturbation), 3),
                                     target_bits=row['target_bits']))
    return rows


def controls(c):
    out = []
    # 1. Reseeding with the wrong closure rotation must break the solution.
    L, w, beta, bits = 7, 3, F(1, 4), 16
    b, x = coefficients(L, beta, 1), inputs(L, 2)
    good = st.solve(x, b, w, bits, st.Tape())
    original = st.Fifo.__init__

    def rotated(self, tape, initial):
        initial = list(initial)
        original(self, tape, initial[1:] + initial[:1])
    st.Fifo.__init__ = rotated
    try:
        bad = st.solve(x, b, w, bits, st.Tape())
    finally:
        st.Fifo.__init__ = original
    exact = st.exact_cycle_solve(x, b, w)
    bound = st.solve_error_bound(F(1), beta, bits, st.levels(L, w))
    need(all(st.norm2(st.sub(v, e)) <= bound ** 2 for v, e in zip(good, exact)), 'control baseline')
    need(any(st.norm2(st.sub(v, e)) > bound ** 2 for v, e in zip(bad, exact)), 'rotated reseed accepted')
    out.append('rotated_closure_reseed_rejected')
    # 2. Precision below the admission is refused.
    need(not st.admitted(F(1, 8), 4, 3), 'low precision admitted')
    out.append('low_precision_refused')
    # 3. Margin-free coefficient (|b|=1) is not a contraction: the oracle divides by zero.
    try:
        st.exact_cycle_solve([st.ONE], [st.ONE], 0)
    except ValueError:
        out.append('unit_coefficient_rejected')
    else:
        raise ValueError('unit coefficient accepted')
    # 4. Wrong inner shift direction in the kernel cascade is caught by the dense solve.
    data = json.loads((HERE / 'vendor' / 'FACTORS.json').read_text())
    state = next(s for s in map(c.certify, data) if any(inside for inside, _ in s['factors']))
    x = inputs(3, 3)
    y = apply_kernel(c, state, x, 1, st.ONE, state['bits'], st.Tape(), mutate='wrong_inner_shift')
    exact = c.matrix_solve(x, c.phased_polynomial(state['q'], st.ONE), 1)
    bound = cascade_bound(state, 3, 1)
    need(any(st.norm2(st.sub(v, e)) > bound ** 2 for v, e in zip(y, exact)), 'wrong inner shift accepted')
    out.append('wrong_inner_shift_rejected')
    return out


def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--check', action='store_true')
    mode.add_argument('--write', action='store_true')
    args = parser.parse_args()
    c = pinned_vendor()
    result = dict(status='passed', generic=generic(), traffic=traffic(),
                  kernels=kernels(c), controls=controls(c))
    text = json.dumps(result, indent=1, sort_keys=True) + '\n'
    target = HERE / 'EXPECTED.json'
    if args.write:
        target.write_text(text)
    else:
        need(target.read_text() == text, 'replay differs from EXPECTED.json')
    print('PASS_CYCLIC_INVERSE_STRIDE_BRIDGE generic=%d kernel_cases=%d controls=%d max_records_per_entry=%s'
          % (result['generic']['cases'], len(result['kernels']), len(result['controls']),
             result['traffic']['max_records_per_entry']))


if __name__ == '__main__':
    main()
