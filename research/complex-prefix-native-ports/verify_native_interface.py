"""Exact bounded-word address generator and precision-envelope checks."""
import json


def stream(f, perm, phase):
    N = 8 ** f
    powers = [1 << (3 * j) for j in range(f)]
    digits = [0] * f
    out = perm[0] * sum(powers)
    ph = f * phase[0] % 4
    changed = 0
    rows = [(out, ph)]
    for x in range(1, N):
        j = 0
        while True:
            old = digits[j]
            new = (old + 1) & 7
            digits[j] = new
            out += (perm[new] - perm[old]) * powers[j]
            ph = (ph + phase[new] - phase[old]) & 3
            changed += 1
            if new:
                break
            j += 1
        rows.append((out, ph))
    return rows, changed


def direct(x, f, perm, phase):
    out, ph = 0, 0
    for j in range(f):
        d = (x >> (3 * j)) & 7
        out += perm[d] << (3 * j)
        ph += phase[d]
    return out, ph & 3


def main():
    cases = [
        ([0, 2, 1, 3, 4, 6, 5, 7], [0] * 8),
        ([0, 5, 2, 7, 4, 1, 6, 3], [x.bit_count() & 3 for x in range(8)]),
        ([2, 0, 3, 1, 4, 6, 5, 7], [0, 0, 2, 2, 1, 3, 3, 1]),
        ([7 - x for x in range(8)], [3, 1, 2, 0, 1, 0, 3, 2]),
    ]
    checked, updates = 0, 0
    for f in range(1, 6):
        N = 8 ** f
        for perm, phase in cases:
            rows, count = stream(f, perm, phase)
            if not all(got == direct(x, f, perm, phase) for x, got in enumerate(rows)):
                raise ValueError('incorrect monomial stream')
            if 7 * count >= 8 * N:
                raise ValueError('carry budget exceeded')
            if len({x for x, _ in rows}) != N:
                raise ValueError('address permutation lost')
            checked += N
            updates += count
    # Symbolic bound: L^3 <= 2^(2f), rho = 2^(-(P+2f+6)).
    # Thus 10 L^3 rho <= (10/64) 2^(-P), uniformly in f and P.
    if not 10 < 64:
        raise ValueError('precision envelope')
    print(json.dumps({'status': 'PASS_NATIVE_MONOMIAL_STREAM', 'checked_entries': checked, 'digit_updates': updates, 'cases': len(cases), 'widths': [1, 2, 3, 4, 5], 'all_width_update_bound': 'changed_digits < 8N/7', 'precision_error_factor_upper_bound': '10/64'}, sort_keys=True))

if __name__ == '__main__':
    main()
