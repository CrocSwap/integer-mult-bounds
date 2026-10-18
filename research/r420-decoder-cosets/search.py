# Apache-2.0; cxnmai with substantial OpenAI assistance.
"""Bounded source-null descent, charging compensation as well as A and C."""
import hashlib
import json
import random
from functools import reduce
from operator import xor
from model import INDEX, SOURCE, bits, counts, kernel, load, prefix, rebuild


def search():
    w = load()
    values = prefix(w)
    old = w['A'][-9+INDEX][2]
    d6 = [g for g in w['A'][:-9] if len(w['frames'][g[0]]) == 30]
    dead = [g[2][0] for g in d6[:180]]
    assert len(set(dead)) == 180
    pool = sorted(set(dead) - set(w['ret']))
    current = sum(1 << s for s in old)
    original = current
    dirt = [sum(1 << s for s in g[2]) for g in w['D']]
    affected = [t for t, row in enumerate(w['scatter']) if INDEX in row]
    rng = random.Random(3)
    moves, tested, dimensions = [], 0, set()
    for trial in range(32):
        order = pool[:]
        rng.shuffle(order)
        basis = kernel(values, order)
        dimensions.add(len(basis))
        # One steepest-descent pass to a local minimum for each ordered basis.
        while True:
            best = None
            for dep in basis:
                tested += 1
                delta = reduce(xor, (values[r] for r in bits(dep)), 0)
                assert delta & ((1 << 240)-1) == 0
                diff = 2*((current ^ dep).bit_count()-current.bit_count())
                diff += sum((dirt[t] ^ delta).bit_count()-dirt[t].bit_count()
                            for t in affected)
                if best is None or diff < best[0]:
                    best = (diff, dep, delta)
            if best is None or best[0] >= 0:
                break
            diff, dep, delta = best
            current ^= dep
            for t in affected:
                dirt[t] ^= delta
            moves.append({'trial': trial, 'toggle': list(bits(dep)), 'delta_cost': diff})
    candidate = rebuild(w, list(bits(current)))
    assert counts(candidate)['total']-counts(w)['total'] == sum(m['delta_cost'] for m in moves)
    assert all(sum(1 << s for s in candidate['D'][t][2]) == dirt[t] for t in range(120))
    return {'seed': 3, 'trials': 32, 'pool_size': len(pool),
            'kernel_dimensions': sorted(dimensions), 'candidates_scored': tested,
            'total_index': INDEX, 'host': w['ret'][INDEX],
            'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            'original_operands': list(bits(original)), 'operands': list(bits(current)),
            'affected_targets': affected, 'moves': moves,
            'before': counts(w), 'after': counts(candidate)}


if __name__ == '__main__':
    print(json.dumps(search(), indent=2, sort_keys=True))
