"""Bounded fixed-output Boolean resynthesis; Apache-2.0, OpenAI Codex assistance."""
import collections
import argparse
import gzip
import json
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / 'research/e8-r480-dead-totals/data/bitE8mut-r480.json.gz'
FRAME, START, STOP = 487, 2409, 2460
REGS = [19, 24, 35, 40, 54, 56, 65, 74, 84, 95, 100, 111]
TRIALS, SEED = 2000, 2026101305


def load_word():
    return json.loads(gzip.decompress(SOURCE.read_bytes()))


def matrix(gates):
    index = {r: i for i, r in enumerate(REGS)}
    rows = [1 << i for i in range(12)]
    for f, d, sources in gates:
        if f != FRAME:
            raise ValueError('unexpected block frame')
        for s in sources:
            rows[index[d]] ^= rows[index[s]]
    return rows


def synthesize(target, rng):
    """L M R = P; emit R^-1, P, L^-1 chronologically, paying swaps."""
    rows = target[:]
    left, right = [], []
    active_r, active_c = list(range(12)), list(range(12))
    for _ in range(12):
        # Strictly weight-decreasing row/column moves on the active minor.
        while True:
            columns = {c: sum(((rows[r] >> c) & 1) << r for r in active_r)
                       for c in active_c}
            best, choices = 0, []
            for a in active_r:
                for b in active_r:
                    if a == b:
                        continue
                    gain = rows[a].bit_count() - (rows[a] ^ rows[b]).bit_count()
                    if gain > best:
                        best, choices = gain, [('row', a, b)]
                    elif gain == best and gain > 0:
                        choices.append(('row', a, b))
            for a in active_c:
                for b in active_c:
                    if a == b:
                        continue
                    gain = columns[b].bit_count() - (columns[b] ^ columns[a]).bit_count()
                    if gain > best:
                        best, choices = gain, [('col', a, b)]
                    elif gain == best and gain > 0:
                        choices.append(('col', a, b))
            if not choices:
                break
            kind, a, b = rng.choice(choices)
            if kind == 'row':
                rows[a] ^= rows[b]
                left.append((a, b))
            else:
                for r in active_r:
                    if rows[r] >> a & 1:
                        rows[r] ^= 1 << b
                right.append((a, b))
        # Choose a sparse pivot and clear its column and row.
        pivots = [(rows[r].bit_count() + sum(rows[x] >> c & 1 for x in active_r), r, c)
                  for r in active_r for c in active_c if rows[r] >> c & 1]
        score = min(p[0] for p in pivots)
        _, r, c = rng.choice([p for p in pivots if p[0] == score])
        for x in active_r:
            if x != r and rows[x] >> c & 1:
                rows[x] ^= rows[r]
                left.append((x, r))
        for y in active_c:
            if y != c and rows[r] >> y & 1:
                for x in active_r:
                    if rows[x] >> c & 1:
                        rows[x] ^= 1 << y
                right.append((c, y))
        active_r.remove(r)
        active_c.remove(c)
    if sorted(rows) != [1 << i for i in range(12)]:
        raise ValueError('elimination did not reach a permutation')
    perm = [1 << i for i in range(12)]
    swaps = []
    for i in range(12):
        if perm[i] != rows[i]:
            j = perm.index(rows[i])
            swaps.extend([(i, j), (j, i), (i, j)])
            perm[i], perm[j] = perm[j], perm[i]
    ops = right + swaps + left[::-1]
    gates = [[FRAME, REGS[a], [REGS[b]]] for a, b in ops]
    if matrix(gates) != target:
        raise ValueError('synthesis orientation error')
    return gates


def replace(word, gates):
    w = dict(word)
    w['A'] = word['A'][:START] + gates + word['A'][STOP:]
    w['C'] = [[1, d, list(ss)] for _, d, ss in reversed(w['A'] + w['B'])
              if d < w['v'] or d >= 2 * w['v']]
    return w


def stream(w):
    result = []
    for phase in ('D', 'A'):
        result.extend(('add', d, s) for _, d, ss in w[phase] for s in ss)
    temp = 2 * w['v'] + w['R']
    for k, q in enumerate(w['ret']):
        result.append(('copy', temp, q))
        result.extend(('add', w['v'] + t, temp) for t, row in enumerate(w['scatter']) if k in row)
        result.append(('erase', temp, q))
    for phase in ('B', 'C'):
        result.extend(('add', d, s) for _, d, ss in w[phase] for s in ss)
    return result


def bounds(w):
    events = stream(w)
    peaks = []
    for reverse in (False, True):
        norms = [1] * (2 * w['v'] + w['R'] + 1)
        peak = 1
        for kind, d, s in (reversed(events) if reverse else events):
            if reverse and kind != 'add':
                kind = 'erase' if kind == 'copy' else 'copy'
            if kind == 'add':
                norms[d] += norms[s]
                peak = max(peak, norms[d])
            elif kind == 'copy':
                norms[d] = norms[s]
            else:
                norms[d] = 0
        peaks.append(peak)
    f, b = peaks
    return f, b, 64 * f ** 3 * b ** 2


def run_search():
    word = load_word()
    target = matrix(word['A'][START:STOP])
    rng = random.Random(SEED)
    histogram = collections.Counter()
    best = None
    candidates = 0
    for trial in range(TRIALS):
        gates = synthesize(target, rng)
        histogram[len(gates)] += 1
        if best is not None and len(gates) > len(best['gates']):
            continue
        f, b, payload = bounds(replace(word, gates))
        candidates += 1
        if payload >= 1 << 104:
            continue
        key = (len(gates), payload, gates)
        if best is None or key < (len(best['gates']), best['payload'], best['gates']):
            best = dict(trial=trial, gates=gates, forward=f, reverse=b, payload=payload)
    if best is None:
        raise ValueError('no precision-admitted candidate')
    return dict(format='r480-qnode5-boolean-search-v1', assignment_seed=5,
                search_seed=SEED, trials=TRIALS, frame=FRAME, start=START, stop=STOP,
                registers=REGS, target=target, histogram=dict(sorted(histogram.items())),
                full_precision_candidates=candidates, best=best)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=HERE / 'CANDIDATE.json')
    args = parser.parse_args()
    result = run_search()
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n', encoding='utf-8', newline='\n')
    print('SEARCH_COMPLETE trials=%s gates=51->%s trial=%s payload_bits=%s' %
          (TRIALS, len(result['best']['gates']), result['best']['trial'], result['best']['payload'].bit_length()))
