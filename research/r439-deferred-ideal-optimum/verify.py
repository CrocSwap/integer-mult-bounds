#!/usr/bin/env python3
"""Exact all-ideal certificate; standard library, Apache-2.0.
Charles Bethin with substantial OpenAI Codex assistance.
"""
import argparse
import copy
import gzip
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = 'research/r439-bsection-stars-seed01/candidate.json.gz'
WITNESS = (31, 51, 52)
EXCEPTIONAL = {24, 28, 47, 68, 93}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load():
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    pin = next(p for p in pins['files'] if p['path'] == SOURCE)
    raw = (ROOT / SOURCE).read_bytes()
    need(hashlib.sha256(raw).hexdigest() == pin['sha256'], 'source digest')
    return json.loads(gzip.decompress(raw))


def extract(w):
    v = w['v']
    need(v == 111 and w['R'] == 439 and len(w['ret']) == 9, 'source dimensions')
    yy = lambda g: v <= g[1] < 2*v and all(v <= s < 2*v for s in g[2])
    reads = [i for i, g in enumerate(w['D'])
             if v <= g[1] < 2*v and all(s >= 2*v for s in g[2])]
    lo, hi = min(reads), max(reads)
    prep = [g for i, g in enumerate(w['D']) if i < lo and yy(g)]
    undo_positions = [i for i, g in enumerate(w['D']) if i > hi and yy(g)]
    undo = [w['D'][i] for i in undo_positions]
    need(not any(yy(g) for g in w['D'][lo:hi+1]), 'interspersed target gate')
    need(prep == undo[::-1] and len(undo) == 306, 'literal undo binding')
    need(all(not v <= g[1] < 2*v and all(not v <= s < 2*v for s in g[2]) for g in w['A']), 'A target isolation')
    need(all(not v <= r < 2*v for r in w['ret']), 'scatter source isolation')
    need(all(g[0] == 0 and len(g[2]) == 1 and g[1] != g[2][0]
             for g in prep + undo), 'elementary zero-frame gates')
    need(all(len(r) == len(set(r)) and all(type(j) is int and 0 <= j < 9 for j in r)
             for r in w['scatter']), 'scatter indices')
    S = [sum(1 << j for j in row) for row in w['scatter']]
    P = S.copy()
    for _, d, (s,) in prep:
        P[d-v] ^= P[s-v]
    q = P.copy()
    increments, predecessors = [], []
    for i, (_, d, (s,)) in enumerate(undo):
        increments.append(q[s-v])
        q[d-v] ^= q[s-v]
        predecessors.append([j for j, (_, e, (t,)) in enumerate(undo[:i]) if e == s or t == d])
    need(q == S, 'undo of scatter')
    return dict(v=v, prep=prep, undo=undo, undo_positions=undo_positions,
                initial_rows=P, scatter_rows=S, increments=increments, predecessors=predecessors)


def row_certificate(m):
    P, U, inc, v = m['initial_rows'], m['undo'], m['increments'], m['v']
    rows, cases = [], 0
    for d, p in enumerate(P):
        ids = [i for i, g in enumerate(U) if g[1]-v == d]
        minimum = 10
        for bits in itertools.product((0, 1), repeat=len(ids)):
            chosen = dict(zip(ids, bits))
            q = p
            for i in ids:
                if chosen[i]:
                    q ^= inc[i]
            weight = q.bit_count()
            minimum = min(minimum, weight)
            cases += 1
            if d == 47 and weight < 2:
                need(chosen[47] == 1, 'row47 saving requires gate47')
            if d == 68 and weight < 2:
                need(chosen[93] == 1, 'row68 saving requires gate93')
            if d == 93 and weight < 2:
                need(chosen[39] == 1, 'row93 saving requires gate39')
            if d == 96 and chosen[6]:
                need(weight >= 4, 'gate6 forces row96 weight4')
            if d == 6 and chosen[36]:
                need(weight >= 2, 'gate36 forces row6 weight2')
        if d not in EXCEPTIONAL:
            need(minimum >= p.bit_count(), 'unlisted improving row')
        rows.append(dict(row=d, initial=p, gates=ids, minimum=minimum, subsets=1 << len(ids)))
    need(sum(p.bit_count() for p in P) == 97, 'initial charge')
    need([P[d].bit_count() for d in (24, 28, 47, 68, 93)] == [5, 2, 2, 2, 2], 'exceptional initial weights')
    need([rows[d]['minimum'] for d in (24, 28, 47, 68, 93)] == [4, 0, 1, 1, 1], 'exceptional minima')
    need(P[96].bit_count() == 2 and P[6] == 0, 'compensating row baseline')
    dependencies = [[47, 6], [93, 37], [37, 36], [39, 36]]
    need(all(j in m['predecessors'][i] for i, j in dependencies), 'essential dependency')
    # Group {47,96} costs at least its initial 4. Group {68,93,6} costs at least 4.
    # The only remaining reductions are <=1 on row24 and <=2 on row28.
    lower = sum(p.bit_count() for p in P) - 1 - 2
    need(cases == 1386 and lower == 94, 'certificate coverage')
    return dict(rows=rows, row_subsets=cases, essential_dependencies=dependencies, lower_bound=lower)


def is_ideal(m, I):
    return all(set(m['predecessors'][i]) <= I for i in I)


def split_word(w, m, I):
    need(is_ideal(m, I), 'not a dependency ideal')
    v, undo = m['v'], m['undo']
    q = m['initial_rows'].copy()
    for i, (_, d, (s,)) in enumerate(undo):
        if i in I:
            q[d-v] ^= q[s-v]
    fixed = m['initial_rows'].copy()
    for i in I:
        fixed[undo[i][1]-v] ^= m['increments'][i]
    need(q == fixed, 'fixed-increment witness binding')
    result = copy.deepcopy(w)
    removed = set(m['undo_positions'])
    result['D'] = [g for j, g in enumerate(w['D']) if j not in removed] + [undo[i] for i in sorted(I)]
    result['B'] = [g for i, g in enumerate(undo) if i not in I] + w['B']
    result['scatter'] = [[b for b in range(9) if r >> b & 1] for r in q]
    return result, q


def literal(w, reverse=False):
    n = 2*w['v'] + w['R']
    state = [1 << i for i in range(n)]
    operations = []
    for section in ('D', 'A', 'scatter', 'B', 'C'):
        if section != 'scatter':
            operations += [('xor', d, s) for _, d, ss in w[section] for s in ss]
        else:
            for j, r in enumerate(w['ret']):
                operations.append(('copy', n, r))
                operations += [('xor', w['v']+t, n) for t, row in enumerate(w['scatter']) if j in row]
                operations.append(('erase', n, r))
    if reverse:
        operations = [('copy' if op == 'erase' else 'erase' if op == 'copy' else op, d, s)
                      for op, d, s in operations[::-1]]
    for op, d, s in operations:
        if op == 'copy':
            need(len(state) == n, 'temporary already live')
            state.append(state[s])
        elif op == 'erase':
            need(len(state) == n+1 and state[d] == state[s], 'COPY lifetime')
            state.pop()
        else:
            state[d] ^= state[s]
    expected = [1 << i for i in range(n)]
    for i in range(w['v']):
        expected[w['v']+i] ^= 1 << i
    need(state == expected, 'arbitrary-dirty boundary')
    return len([op for op, _, _ in operations if op == 'xor'])


def controls(w, m, candidate):
    names = []
    def reject(name, f):
        try:
            f()
        except ValueError:
            names.append(name)
        else:
            raise ValueError('control accepted: ' + name)
    reject('nonideal relaxed 93-ADD proposal', lambda: split_word(w, m, set(WITNESS) | {47}))
    broken = copy.deepcopy(m)
    broken['predecessors'][47].remove(6)
    reject('missing essential dependency', lambda: row_certificate(broken))
    broken = copy.deepcopy(m)
    broken['increments'][36] = 0
    reject('erased compensating row cost', lambda: row_certificate(broken))
    broken = copy.deepcopy(candidate)
    broken['scatter'] = w['scatter']
    reject('old scatter with changed basis', lambda: literal(broken))
    broken = copy.deepcopy(candidate)
    # Removing the first deferred gate can be invisible on a scatter column;
    # arbitrary dirty target columns still detect the missing undo.
    broken['B'].pop(0)
    reject('omitted undo on dirty targets', lambda: literal(broken))
    return names


def compute():
    w = load()
    m = extract(w)
    cert = row_certificate(m)
    candidate, q = split_word(w, m, set(WITNESS))
    cost = sum(x.bit_count() for x in q)
    need(cost == cert['lower_bound'], 'sharpness')
    counts = [literal(word, rev) for word in (w, candidate) for rev in (False, True)]
    need(counts == [11500, 11500, 11067, 11067], 'complete local ADD count')
    need(candidate['A'] == w['A'] and candidate['C'] == w['C'] and candidate['ret'] == w['ret'], 'unchanged continuation')
    return dict(status='PASS_R439_DEFERRED_IDEAL_OPTIMUM', lower_bound=94, attaining_ideal=list(WITNESS),
                initial_scatter=97, original_scatter=527, undo_gates=306, dependency_edges=sum(map(len, m['predecessors'])),
                row_subsets=cert['row_subsets'], row_certificates=cert['rows'], essential_dependencies=cert['essential_dependencies'],
                initial_rows=m['initial_rows'], increments=m['increments'],
                dirty_columns=661, complete_ADDs=[11500,11067], controls=controls(w,m,candidate),
                scope='All dependency ideals of this pinned undo circuit, not arbitrary circuits or supplier admission')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    result = compute()
    path = HERE / 'CERTIFICATE.json'
    if args.write:
        path.write_text(json.dumps(result, indent=2) + '\n')
    else:
        need(result == json.loads(path.read_text()), 'certificate mismatch')
    print('PASS_R439_DEFERRED_IDEAL_OPTIMUM minimum=94 gates=306 row_subsets=1386 dirty_columns=661 controls=5 no_new_kappa')


if __name__ == '__main__':
    main()
