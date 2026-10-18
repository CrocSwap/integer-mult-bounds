# SPDX-License-Identifier: Apache-2.0
"""Separate set-state / integer-elimination replay; no primary imports."""
import gzip
import hashlib
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = 'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz'
SHA = 'e3e301e62bc2b41dbf1ceac0acf3d35824ebeab1848c5a2142d4577b109da52f'


def need(ok, label):
    if not ok:
        raise ValueError(label)


def reduce_rows(vectors):
    out = {}
    for vector in vectors:
        row = list(vector)
        for p in sorted(out):
            if row[p]:
                a, b = row[p], out[p][p]
                row = [b*x-a*y for x, y in zip(row, out[p])]
                g = math.gcd(*row)
                if g:
                    row = [x//g for x in row]
        p = next((i for i, x in enumerate(row) if x), None)
        if p is not None:
            g = math.gcd(*row)
            out[p] = [x//g for x in row]
        if len(out) == 8:
            break
    return list(out.values())


def check(cert, root=ROOT):
    raw = (root/WORD).read_bytes()
    need(hashlib.sha256(raw).hexdigest() == SHA, 'source hash')
    w = json.loads(gzip.decompress(raw))
    n, v = 2*w['v']+w['R'], w['v']
    rows = [{i} for i in range(n)]
    current = w['start'][:]
    for section in ['D', 'A']:
        for frame, dst, srcs in w[section]:
            for r in [dst]+srcs:
                current[r] = frame
            for r in srcs:
                rows[dst].symmetric_difference_update(rows[r])
    for t, js in enumerate(w['scatter']):
        for j in js:
            rows[v+t].symmetric_difference_update(rows[w['ret'][j]])
    z = list(range(v))+list(range(2*v, n))
    matrix = {r: set(rows[r]) for r in z}
    inverse = {r: {r} for r in z}
    for pivot in z:
        donor = next(r for r in z if r >= pivot and pivot in matrix[r])
        matrix[pivot], matrix[donor] = matrix[donor], matrix[pivot]
        inverse[pivot], inverse[donor] = inverse[donor], inverse[pivot]
        for r in z:
            if r != pivot and pivot in matrix[r]:
                matrix[r] ^= matrix[pivot]
                inverse[r] ^= inverse[pivot]
    need(all(matrix[r] == {r} for r in z), 'matrix inverse')
    frames = [reduce_rows([w['lines'][i] for i in f]) for f in w['frames']]
    def subset(a, b):
        return len(reduce_rows(frames[a]+frames[b])) == len(frames[b])
    ranks = []
    cases = []
    for h in range(2*v, n):
        restore = sorted(inverse[h])
        dirt = [r for r in range(n) if h in rows[r]]
        involved = sorted(set(restore+dirt+[h]))
        vectors = [x for r in involved for x in frames[current[r]]]
        rank = len(reduce_rows(vectors))
        ranks.append([h, rank])
        if rank == 7:
            candidates = [f for f in range(len(frames)) if len(frames[f]) == 7
                          and len(reduce_rows(vectors+frames[f])) == 7]
            station = min(candidates)
            blocked = [r for r in involved if r != h and not subset(station, w['final'][r])]
            gates = [[h, r] for r in restore if r != h]+[[r, h] for r in dirt if r != h]
            case = {'helper':h, 'station':station, 'restore':restore, 'dirt':dirt,
                    'endpoint_blockers':blocked, 'isolation_gates':gates, 'legal':not blocked}
            if not blocked:
                values, now = [set(row) for row in rows], current[:]
                for dst, src in gates:
                    for r in (dst, src):
                        need(subset(now[r], station), 'arrival')
                        need(subset(station, station if r == h else w['final'][r]), 'cap')
                        now[r] = station
                    values[dst] ^= values[src]
                need(values[h] == {h}, 'restoration')
                need(all(values[r] == rows[r]-{h} for r in range(n) if r != h), 'clean columns')
                case['minimum_adds'] = max(len(dirt)-1+int(rows[h] != {h}), len(restore)-1)
                need(case['minimum_adds'] == len(gates), 'optimality')
                case['promotions'] = [{'register':r, 'from_frame':current[r], 'to_frame':station,
                                       'rank_increment':7-len(frames[current[r]])}
                                      for r in involved if not subset(station, current[r])]
                for i, (f, dst, srcs) in enumerate(w['B']):
                    bad = [r for r in [dst]+srcs if not subset(now[r], f)]
                    if bad:
                        case['first_fixed_B_conflict'] = {'gate_index':i,'frame':f,'registers':bad}
                        break
                    for r in [dst]+srcs:
                        now[r] = f
                need('first_fixed_B_conflict' in case, 'continuation conflict')
            cases.append(case)
    result = {'schema_version':1, 'status':'SCOPED_SINGLE_STATION_CLASSIFICATION',
              'seed':17, 'word_sha256':SHA, 'join_rank_counts':{str(k):sum(r==k for _,r in ranks) for k in [7,8]},
              'all_helper_join_ranks':ranks, 'rank_seven_cases':cases,
              'legal_helpers':[r['helper'] for r in cases if r['legal']], 'no_new_kappa':True}
    need(result == cert, 'independent certificate mismatch')
    return result


if __name__ == '__main__':
    check(json.loads((HERE/'CERTIFICATE.json').read_text()))
    print('PASS_INDEPENDENT_SINGLE_STATION sets=661 Gaussian_inverse=550 helpers=439 legal=3')
