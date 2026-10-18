"""Seeded fixed-block XOR rewrite search; standard library only.

Prepared for yongjae321 with substantial OpenAI Codex assistance; Apache-2.0.
Input is read-only. Output creation uses exclusive mode.
"""
import argparse
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import random

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'e8-bit-r420/data/bitE8mut-r420.json.gz'
N = 12
IDENTITY = tuple(1 << i for i in range(N))


def need(condition, message):
    if not condition:
        raise ValueError(message)


def endpoint(ops):
    rows = list(IDENTITY)
    for a, b in ops:
        rows[a] ^= rows[b]
    return tuple(rows)


def positive(ops):
    rows = [[int(i == j) for j in range(N)] for i in range(N)]
    for a, b in ops:
        rows[a] = [x + y for x, y in zip(rows[a], rows[b])]
    return rows


def dominates(old, new):
    return all(y <= x for ar, br in zip(old, new) for x, y in zip(ar, br))


def commute(a, b):
    return a[0] != b[1] and a[1] != b[0]


def extract():
    raw = SOURCE.read_bytes()
    w = json.loads(gzip.decompress(raw))
    groups = []
    for frame, group in itertools.groupby(enumerate(w['B'][120:], 120), lambda x: x[1][0]):
        chunk = list(group)
        if len(chunk) == 1:
            break
        groups.append((frame, chunk))
    need(len(groups) == 10, 'Expected exactly ten initial phase-B block groups')
    frame, chunk = groups[3]
    need(all(len(g[2]) == 1 for _, g in chunk), 'Selected block must contain only binary XOR gates')
    registers = sorted({r for _, g in chunk for r in [g[1], *g[2]]})
    need(len(registers) == N, 'Selected block must use exactly twelve registers')
    index = {r: i for i, r in enumerate(registers)}
    ops = [(index[g[1]], index[g[2][0]]) for _, g in chunk]
    return ops, dict(source_path=SOURCE.relative_to(HERE.parent.parent).as_posix(),
                     source_sha256=hashlib.sha256(raw).hexdigest(),
                     block_index=3, b_start=chunk[0][0], b_stop=chunk[-1][0]+1,
                     frame=frame, registers=registers)


def pair_table():
    gates = [(a, b) for a in range(N) for b in range(N) if a != b]
    table = {IDENTITY: ()}
    for g in gates:
        table[endpoint([g])] = (g,)
    for a in gates:
        for b in gates:
            table.setdefault(endpoint([a, b]), (a, b))
    return table


def reduce(ops, table, rng):
    """Reduce a shuffled order of adjacent triples using exact matrix lookup."""
    changes = 0
    while True:
        positions = list(range(len(ops)-2))
        rng.shuffle(positions)
        for i in positions:
            old = ops[i:i+3]
            new = table.get(endpoint(old))
            if new is None:
                continue
            if not dominates(positive(old), positive(new)):
                continue
            if not dominates(positive(reversed(old)), positive(reversed(new))):
                continue
            ops[i:i+3] = new
            changes += 1
            break
        else:
            return changes


def search(seed, steps, trials):
    original, metadata = extract()
    rng = random.Random(seed)
    table = pair_table()
    best = list(original)
    accepted = 0
    attempted = 0
    improvements = []
    for trial in range(trials):
        ops = list(original if trial % 4 == 0 else best)
        for step in range(steps):
            attempted += 1
            i = rng.randrange(len(ops))
            direction = rng.choice((-1, 1))
            limit = rng.randrange(1, len(ops))
            for _ in range(limit):
                j = i + direction
                if not 0 <= j < len(ops) or not commute(ops[i], ops[j]):
                    break
                ops[i], ops[j] = ops[j], ops[i]
                i = j
            accepted += reduce(ops, table, rng)
            if len(ops) < len(best):
                best = list(ops)
                improvements.append(dict(trial=trial, step=step, gates=len(best)))
                print(json.dumps(improvements[-1]), flush=True)
    need(endpoint(original) == endpoint(best), 'Replacement changed the ordered F2 endpoint')
    need(dominates(positive(original), positive(best)), 'Replacement increased a forward nonnegative coefficient')
    need(dominates(positive(reversed(original)), positive(reversed(best))),
         'Replacement increased a reverse nonnegative coefficient')
    return dict(schema='r420-block3-xor-candidate/1', **metadata,
                seed=seed, method='commuting transvections plus exact 3-to-at-most-2 lookup',
                domain='12 original registers; same ordered 12x12 F2 endpoint; no helpers or relabelling',
                coverage=dict(trials=trials, shuffle_steps_per_trial=steps,
                              attempted_shuffle_steps=attempted, accepted_reductions=accepted,
                              stopping_rule='fixed trials times steps; no claim of exhaustive optimality'),
                original_gate_count=len(original), replacement_gate_count=len(best),
                original_local_ops=original, replacement_local_ops=best,
                endpoint_rows=list(endpoint(best)),
                nonnegative_forward_componentwise_no_worse=True,
                nonnegative_reverse_componentwise_no_worse=True,
                improvements=improvements)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seed', type=int, default=13)
    parser.add_argument('--steps', type=int, default=400)
    parser.add_argument('--trials', type=int, default=50)
    parser.add_argument('--output', type=Path, default=HERE / 'candidate.json')
    args = parser.parse_args()
    if args.seed < 0:
        parser.error('--seed must be nonnegative')
    if args.steps <= 0 or args.trials <= 0:
        parser.error('--steps and --trials must be positive')
    result = search(args.seed, args.steps, args.trials)
    with args.output.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps({k: result[k] for k in ('original_gate_count', 'replacement_gate_count', 'coverage')}))


if __name__ == '__main__':
    main()
