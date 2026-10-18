"""Separate finite rank corroboration on the owner/payload-constant subspace.

No primary checker or predecessor executable import. Modular full-row rank
is an exact rational lower bound, and row counts supply the matching upper
bound. The universal array theorem is the separate ordered proof, not an
extrapolation of these constant-subspace fixtures.
"""
from pathlib import Path
from math import isqrt
import gzip
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
A = (0, 7, 20, 27, 36, 46, 57, 111)
T = (21, 37, 47, 76, 81, 87, 92, 110)
V = A + T
U = tuple(p for p in range(112) if p not in V)


def need(ok, label):
    if not ok:
        raise ValueError(label)


def rank(matrix, prime):
    rows = [list(row) for row in matrix]
    pivot = 0
    for column in range(224):
        chosen = next((i for i in range(pivot, len(rows)) if rows[i][column] % prime), None)
        if chosen is None:
            continue
        rows[pivot], rows[chosen] = rows[chosen], rows[pivot]
        inverse = pow(rows[pivot][column] % prime, -1, prime)
        rows[pivot] = [v * inverse % prime for v in rows[pivot]]
        for i in range(pivot + 1, len(rows)):
            factor = rows[i][column] % prime
            if factor:
                rows[i] = [(x - factor * y) % prime for x, y in zip(rows[i], rows[pivot])]
        pivot += 1
        if pivot == len(rows):
            break
    return pivot


def compute(R, prime):
    inverse4 = pow(4, -1, prime)
    def add(*terms):
        return [sum(c * row[j] for c, row in terms) % prime for j in range(224)]
    def query(bank, ports):
        return [add(*[(R[k][p], bank[p]) for p in ports]) for k in range(8)]
    def inject(value, ports):
        return {p: add(*[(R[k][p] * inverse4, value[k]) for k in range(8)]) for p in ports}
    x = {p: [int(j == p) for j in range(224)] for p in range(112)}
    y = {p: [int(j == p + 112) for j in range(224)] for p in range(112)}
    f = query(x, range(112))
    kf, old_t = inject(f, U + T), inject(query(x, T), A)
    x1 = {p: add((1, x[p]), (-1, kf[p])) if p in U else old_t[p] if p in A else kf[p]
          for p in range(112)}
    y1 = {p: add((1, y[p]), (1, x1[p])) if p in U else add((1, x[p]), (1, y[p]), (-1, x1[p]))
          for p in range(112)}
    delta = inject(query(y1, U + T), A)
    u = y1 | {p: add((1, y1[p]), (1, delta[p])) for p in A}
    driver, total = query(x1, T), query(u, range(112))
    kd = inject(driver, U)
    t11 = inject([add((1, b), (11, a)) for a, b in zip(driver, total)], T)
    t12 = inject([add((1, b), (12, a)) for a, b in zip(driver, total)], T)
    x2 = ({p: add((1, x1[p]), (-1, y1[p])) for p in U}
          | {p: add((1, x1[p]), (1, y1[p]), (-1, u[p])) for p in A} | t12)
    y2 = ({p: add((1, y1[p]), (1, kd[p])) for p in U} | {p: u[p] for p in A}
          | {p: add((1, u[p]), (-1, t11[p])) for p in T})
    sums = [add((1, x2[p]), (1, y2[p])) for p in V]
    need(sums == [add((1, x[p]), (1, y[p])) for p in V], 'source conserved sums')
    live = [x2[p] for p in U] + [y2[p] for p in U] + sums
    early = [x1[p] for p in V]
    ranks = {'live': rank(live, prime), 'live_plus_early_X': rank(live + early, prime),
             'one_early_deleted': rank(live + early[1:], prime),
             'redundant_early_sums': rank(live + sums, prime),
             'alternative_early_Y': rank(live + [y1[p] for p in V], prime),
             'additional_current_selected_X': rank(live + [x2[p] for p in V], prime)}
    need(ranks == {'live': 208, 'live_plus_early_X': 224, 'one_early_deleted': 223,
                   'redundant_early_sums': 208, 'alternative_early_Y': 224,
                   'additional_current_selected_X': 224}, 'exact rank corroboration')
    return ranks


def main():
    manifest = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    name = 'research/joint-query/certificate.json.gz'
    pin = next(x for x in manifest['files'] if x['path'] == name)
    raw = (ROOT / name).read_bytes()
    need(hashlib.sha256(raw).hexdigest() == pin['sha256'], 'source SHA256')
    packet = json.loads(gzip.decompress(raw))
    need(tuple(packet['A_ports']) == A and tuple(packet['T_ports']) == T and tuple(packet['U_ports']) == U,
         'actual selected/ordinary partition')
    R = [[int(row.get(str(p), 0)) for p in range(112)] for row in packet['R_rows']]
    need(all(sum(R[i][p] * R[j][p] for p in ports) == scale * int(i == j)
             for ports, scale in ((A, 4), (T, 4), (U, 48)) for i in range(8) for j in range(8)),
         'actual selected and ordinary Grams')
    primes = (1000003, 1000033)
    need(all(all(prime % d for d in range(2, isqrt(prime) + 1)) for prime in primes), 'prime moduli')
    results = {str(prime): compute(R, prime) for prime in primes}
    print('PASS_INDEPENDENT_QQ16_CUT_RANKS ' + json.dumps(results, sort_keys=True))


if __name__ == '__main__':
    main()
