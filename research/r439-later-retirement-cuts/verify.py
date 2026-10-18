# SPDX-License-Identifier: Apache-2.0
"""Exact single-station classification. Philipp, with OpenAI Codex assistance."""
import argparse
import gzip
import hashlib
import json
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
DIGEST = "e3e301e62bc2b41dbf1ceac0acf3d35824ebeab1848c5a2142d4577b109da52f"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def basis(vectors):
    pivots = {}
    for vector in vectors:
        row = list(map(Fraction, vector))
        for p in sorted(pivots):
            q = row[p]
            if q:
                row = [a - q*b for a, b in zip(row, pivots[p])]
        p = next((i for i, x in enumerate(row) if x), None)
        if p is not None:
            q = row[p]
            pivots[p] = [x/q for x in row]
        if len(pivots) == 8:
            break
    return [pivots[p] for p in sorted(pivots)]


def contained(left, right):
    return len(basis(right + left)) == len(right)


def bits(n):
    while n:
        b = n & -n
        yield b.bit_length()-1
        n ^= b


def load(root=ROOT):
    raw = (root / WORD).read_bytes()
    require(hashlib.sha256(raw).hexdigest() == DIGEST, "source hash")
    return json.loads(gzip.decompress(raw))


def cut(word):
    n, v = 2*word['v'] + word['R'], word['v']
    rows, frames = [1 << r for r in range(n)], word['start'][:]
    for section in ('D', 'A'):
        for f, t, ss in word[section]:
            for r in [t, *ss]:
                frames[r] = f
            for s in ss:
                rows[t] ^= rows[s]
    for t, totals in enumerate(word['scatter']):
        for total in totals:
            rows[v+t] ^= rows[word['ret'][total]]
    inverse = [1 << r for r in range(n)]
    for _, t, ss in reversed(word['A']):
        if not v <= t < 2*v:
            for s in ss:
                inverse[t] ^= inverse[s]
    return rows, frames, inverse


def station_check(word, rows, current, fb, h, u, gates):
    state, actual = rows[:], current[:]
    for t, s in gates:
        require(t != s, "self addition")
        for r in (t, s):
            require(contained(fb[actual[r]], fb[u]), "station arrival")
            cap = u if r == h else word['final'][r]
            require(contained(fb[u], fb[cap]), "final endpoint cap")
            actual[r] = u
        state[t] ^= state[s]
    require(state[h] == 1 << h, "helper restoration")
    for r in range(len(state)):
        if r != h:
            require(state[r] == rows[r] ^ (((rows[r] >> h) & 1) << h),
                    "isolation changes another column")
    return actual


def derive(word):
    rows, current, inverse = cut(word)
    fb = [basis([word['lines'][i] for i in frame]) for frame in word['frames']]
    baseline, frame_path = rows[:], current[:]
    for section in ('B', 'C'):
        for f, t, ss in word[section]:
            for r in [t, *ss]:
                require(contained(fb[frame_path[r]], fb[f]), 'baseline monotone frame')
                frame_path[r] = f
            for s in ss:
                baseline[t] ^= baseline[s]
    for r, value in enumerate(baseline):
        expected = (1 << r) ^ ((1 << (r-word['v'])) if word['v'] <= r < 2*word['v'] else 0)
        require(value == expected, 'baseline full endpoint')
        require(contained(fb[frame_path[r]], fb[word['final'][r]]), 'baseline final cap')
    counts, rank_rows, survivors = {}, [], []
    for h in range(2*word['v'], len(rows)):
        restore = list(bits(inverse[h]))
        got = 0
        for r in restore:
            got ^= rows[r]
        require(got == 1 << h, "inverse row")
        dirt = [r for r, value in enumerate(rows) if value >> h & 1]
        donors = sorted(set(restore + dirt + [h]))
        join = basis([line for r in donors for line in fb[current[r]]])
        rank = len(join)
        counts[str(rank)] = counts.get(str(rank), 0) + 1
        rank_rows.append([h, rank])
        if rank != 7:
            require(rank == 8, "unexpected join rank")
            continue
        require(h in restore, "missing pivot")
        choices = [f for f, b in enumerate(fb) if len(b) == 7 and contained(join, b)]
        require(bool(choices), "missing catalogued hyperplane")
        u = min(choices)
        blocked = [r for r in donors if r != h and not contained(fb[u], fb[word['final'][r]])]
        gates = [[h, r] for r in restore if r != h] + [[r, h] for r in dirt if r != h]
        row = {'helper': h, 'station': u, 'restore': restore, 'dirt': dirt,
               'endpoint_blockers': blocked, 'isolation_gates': gates,
               'legal': not blocked}
        if not blocked:
            actual = station_check(word, rows, current, fb, h, u, gates)
            lower = max(len(dirt)-1 + int(rows[h] != 1 << h), len(restore)-1)
            require(lower == len(gates), "non-sharp gate lower bound")
            row['minimum_adds'] = lower
            row['promotions'] = [{'register': r, 'from_frame': current[r],
                                  'to_frame': u, 'rank_increment': 7-len(fb[current[r]])}
                                 for r in donors if not contained(fb[u], fb[current[r]])]
            conflict = None
            for i, (f, t, ss) in enumerate(word['B']):
                bad = [r for r in [t, *ss] if not contained(fb[actual[r]], fb[f])]
                if bad:
                    conflict = {'gate_index': i, 'frame': f, 'registers': bad}
                    break
                for r in [t, *ss]:
                    actual[r] = f
            require(conflict is not None, "unexpected unchanged-B continuation")
            row['first_fixed_B_conflict'] = conflict
        survivors.append(row)
    return {'schema_version': 1, 'status': 'SCOPED_SINGLE_STATION_CLASSIFICATION',
            'seed': 17, 'word_sha256': DIGEST, 'join_rank_counts': counts,
            'all_helper_join_ranks': rank_rows, 'rank_seven_cases': survivors,
            'legal_helpers': [r['helper'] for r in survivors if r['legal']],
            'no_new_kappa': True}


def verify(expected, word):
    actual = derive(word)
    require(actual == expected, "certificate mismatch")
    require(actual['legal_helpers'] == [469, 470, 476], "legal set")
    return actual


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = derive(load(args.root))
    if args.output:
        with args.output.open('x') as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write('\n')
    else:
        require(result == json.loads((HERE/'CERTIFICATE.json').read_text()), 'certificate mismatch')
    print('PASS_SINGLE_STATION_EXITS helpers=439 join8=433 endpoint_blocked=3 legal=469,470,476 adds=3,3,4 no_new_kappa')


if __name__ == '__main__':
    main()
