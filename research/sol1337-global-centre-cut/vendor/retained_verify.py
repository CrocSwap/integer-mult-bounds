#!/usr/bin/env python3
"""Exact reversible center extension. Apache-2.0; substantial OpenAI assistance."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip
import json
import sys

HERE = Path(__file__).resolve().parent
SOURCE_HASH = '7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05'
PAID = {1: 2201, 2: 412, 3: 510, 4: 127, 5: 40, 8: 8}
N = 640


def need(ok, message):
    if not ok:
        raise ValueError(message)


def plus(dst, src, coefficient=Q(1)):
    for k, v in tuple(src.items()):
        value = dst.get(k, Q(0)) + coefficient * v
        if value:
            dst[k] = value
        else:
            dst.pop(k, None)


def load():
    raw = (HERE / 'inputs/round3-native.json.gz').read_bytes()
    need(sha256(raw).hexdigest() == SOURCE_HASH, 'exact PR4610 round-three source')
    return json.loads(gzip.decompress(raw))


def emit(payload, dual=False, baseline=False):
    """Same chronological order for inverse transpose; dualize every chart."""
    starts = list(payload['canonical']['start'])
    centers = []
    events = []
    center = -1
    for e in payload['programs']['forward']:
        kind = e[0]
        if kind == 'scalar':
            g, frame = e[1:]
            op = g[0]
            if op == 'clear':
                continue
            if op == 'copy':
                center += 1
                centers.append({'source': g[2][1], 'input_frame': frame})
                starts.append(frame)
            role = lambda x: x[1] if x[0] == 'L' else 632 + center
            dst = role(g[1])
            if op in ('add', 'copy'):
                src = role(g[2])
                a = Q(1) if op == 'copy' else Q(g[3], g[4])
                if baseline and op == 'copy':
                    events.append(('copy', dst, src, a, frame))
                else:
                    events.append(('add', src if dual else dst,
                                   dst if dual else src, -a if dual else a, frame))
            else:
                need(op == 'scale', 'known scalar opcode')
                a = Q(g[2], g[3])
                events.append(('scale', dst, 1 / a if dual else a, frame))
        elif kind == 'climb':
            _, _, r, a, b, width = e
            events.append(('transport', r, a, b, width))
        elif kind == 'center':
            _, _, a, b, width = e
            events.append(('transport', 632 + center, a, b, width))
        elif kind == 'warp':
            _, r, op, a, b = e
            symbol = (1 if op > 0 else -1) * (abs(op) + (1000000 if dual else 0))
            events.append(('warp', r[1], symbol, a, b))
        else:
            need(kind in ('phase', 'adapter'), 'known native marker')
    need(center == 7 and len(starts) == N, 'eight distinct arbitrary center inputs')
    return starts, centers, events


def span(basis):
    out = {0}
    for v in basis:
        out |= {x ^ v for x in tuple(out)}
    need(len(out) == 2 ** len(basis), 'independent chart basis')
    return out


def replay(payload, starts, events, baseline=False):
    rows = [{(i, ()): Q(1)} for i in range(N)]
    current = starts[:]
    frames = payload['canonical']['frames']
    spaces = list(map(span, frames))
    paid = Counter()
    for e in events:
        op, r = e[:2]
        if op in ('add', 'copy'):
            _, _, s, a, frame = e
            need(r != s and current[r] == current[s] == frame, 'actual scalar common chart')
            if op == 'copy':
                need(baseline and r >= 632, 'only baseline owned copy')
                rows[r] = dict(rows[s])
            else:
                plus(rows[r], rows[s], a)
        elif op == 'scale':
            _, _, a, frame = e
            need(current[r] == frame and a != 0, 'scale chart and invertibility')
            rows[r] = {k: a * v for k, v in rows[r].items()}
        elif op == 'transport':
            _, _, a, b, width = e
            need(current[r] == a, 'actual paid source chart')
            need(spaces[a] < spaces[b] or spaces[b] < spaces[a], 'strictly nested transport')
            need(width == abs(len(frames[a]) - len(frames[b])), 'rank derived from geometry')
            paid[width] += 1
            current[r] = b
        else:
            _, _, symbol, a, b = e
            need(op == 'warp' and current[r] == a, 'native warp source chart')
            out = {}
            for (variable, word), value in rows[r].items():
                word = word[1:] if word and word[0] == -symbol else (symbol,) + word
                plus(out, {(variable, word): value})
            rows[r] = out
            current[r] = b
    need(dict(paid) == PAID, 'complete emitted recursive invoice')
    need(current == payload['canonical']['final'] + [0] * 8, 'all 640 output charts')
    need(all(not word for row in rows for _, word in row), 'all free warp words cancel')
    return [{i: v for (i, _), v in row.items()} for row in rows]


def product(a, b):
    out = []
    for row in a:
        new = {}
        for j, v in row.items():
            plus(new, b[j], v)
        out.append(new)
    return out


def transpose(a):
    out = [{} for _ in a]
    for i, row in enumerate(a):
        for j, v in row.items():
            out[j][i] = v
    return out


def encoded(a):
    return [[[j, str(v)] for j, v in sorted(row.items())] for row in a]


def matrix_rank(rows):
    pivots = {}
    for old in rows:
        row = dict(old)
        while row:
            p = min(row)
            if p not in pivots:
                q = row[p]
                pivots[p] = {j: v / q for j, v in row.items()}
                break
            plus(row, pivots[p], -row[p])
    return len(pivots)


def run():
    payload = load()
    starts, centers, events = emit(payload)
    actual = replay(payload, starts, events)
    _, _, old_events = emit(payload, baseline=True)
    old = replay(payload, starts, old_events, baseline=True)
    identity = [{i: Q(1)} for i in range(N)]
    a = [dict(row) for row in identity]
    for i in range(112):
        a[112 + i][i] = Q(1)
    need(old[:632] == a[:632], 'source all-632-column native identity ABI')
    b = [{j: v for j, v in row.items() if j >= 632} for row in actual[:632]]
    r = [{j: v for j, v in row.items() if j < 632} for row in actual[632:]]
    need(all(actual[i] == a[i] | b[i] for i in range(632)), 'unchanged old-input columns')
    need(all(actual[632 + i] == r[i] | {632 + i: Q(1)} for i in range(8)), 'center residual ABI')
    need(all(not b[i] for i in list(range(112)) + list(range(224, 632))), 'noise only in Y outputs')
    need(all(all(j < 112 or 224 <= j < 632 for j in row) for row in r), 'center reads only X/helper inputs')
    need(matrix_rank(b) == matrix_rank(r) == 8, 'two actual rank-eight coupling maps')
    k = [dict(row) for row in actual]
    for i in range(N):
        plus(k[i], identity[i], -1)
    k2 = product(k, k)
    need(any(k2) and not any(product(k2, k)), 'K squared nonzero and K cubed zero')
    inverse = [dict(row) for row in identity]
    for i in range(N):
        plus(inverse[i], k[i], -1)
        plus(inverse[i], k2[i])
    need(product(inverse, actual) == product(actual, inverse) == identity, 'exact two-sided inverse')
    _, _, dual_events = emit(payload, dual=True)
    dual = replay(payload, starts, dual_events)
    need(dual == transpose(inverse), 'all-640-column raw inverse transpose with the same bill')
    need(product(transpose(dual), actual) == identity, 'exact primal/dual pairing')
    # Controls retain the same source/invoice but falsify actual operator claims.
    bad = list(events)
    i = next(i for i, e in enumerate(bad) if e[0] == 'add' and e[1] == 632)
    e = bad[i]
    bad[i] = (*e[:3], -e[3], e[4])
    need(replay(payload, starts, bad) != actual, 'changed center injection rejected')
    bad = list(dual_events)
    i = next(i for i, e in enumerate(bad) if e[0] == 'add' and e[2] == 632)
    e = bad[i]
    bad[i] = (*e[:3], -e[3], e[4])
    need(replay(payload, starts, bad) != transpose(inverse), 'wrong inverse-transpose sign rejected')
    bad = list(events)
    i = next(i for i, e in enumerate(bad) if e[0] == 'transport' and e[1] == 632)
    e = bad[i]
    bad[i] = (*e[:4], e[4] - 1)
    rejected = False
    try:
        replay(payload, starts, bad)
    except ValueError:
        rejected = True
    need(rejected, 'false center rank rejected from actual charts')
    # Independent Gram and support facts expose actual arbitrary-input leakage.
    gram = [[sum(b[i].get(632 + u, 0) * b[i].get(632 + v, 0) for i in range(632))
             for v in range(8)] for u in range(8)]
    need(gram == [[Q(7, 2) * (u == v) for v in range(8)] for u in range(8)], 'B transpose B = 7/2 I')
    # The zero-center source contract cannot certify eight independent new jobs.
    need(any(b), 'nonzero incoming center changes original target outputs')
    need(all(r), 'new center outputs are contaminated by original arbitrary inputs')
    abi = {'schema': 'retained-center-extension/1', 'source_sha256': SOURCE_HASH,
           'centers': centers, 'B_rows': encoded(b), 'R_rows': encoded(r)}
    result = {'status': 'EXACT_REVERSIBLE_640_FIELD_EXTENSION_NO_NEW_KAPPA',
              'source_inputs': 632, 'new_arbitrary_inputs': 8, 'outputs': N,
              'paid': PAID, 'new_recursive_calls': 0, 'owned_erase_or_copy_operations': 0,
              'B_rank': 8, 'R_rank': 8, 'nilpotence_index': 3,
              'noisy_old_outputs': sum(bool(row) for row in b),
              'old_input_terms_in_center_outputs': [len(row) for row in r],
              'center_residual_ranks_without_decoupling_credit': [8] * 8,
              'primal_and_raw_inverse_transpose_checked': True,
              'controls': ['center injection sign', 'dual sign', 'false center rank',
                           'new-input leakage', 'old-input contamination'],
              'independent_new_productive_jobs_certified': False,
              'abi_sha256': sha256((json.dumps(abi, sort_keys=True) + '\n').encode()).hexdigest()}
    return abi, result


if __name__ == '__main__':
    abi, result = run()
    if sys.argv[1:] == ['--write']:
        for name, value in [('ABI.json', abi), ('RESULT.json', result)]:
            (HERE / name).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
    else:
        need(not sys.argv[1:], 'known command arguments')
        for name, value in [('ABI.json', abi), ('RESULT.json', result)]:
            need(json.loads(json.dumps(value)) == json.loads((HERE / name).read_text()), 'exact receipt ' + name)
    print(json.dumps(result, sort_keys=True))
