#!/usr/bin/env python3
"""Pinned PR96 exact endpoint profiler applied to the selected literal words.

Merged-exterior mechanism and exact rank formulas: eumemic with Anthropic
Claude assistance, PR96 606d16d6dfc714d2a467190dc91b2f8dcab38d9c.
This adapter preserves the original profiler bytes and adds only word paths
and a retirement-only diagnostic. Apache-2.0; inherited notices apply.
"""
import sys
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode = True
import argparse
import gzip
from hashlib import sha256
import json
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'references/frame-compiler/pr96/scripts/experiments'))
import merged_exterior as original

def load_word(h, directory=HERE):
    raw = (Path(directory) / f'word-{h}.json.gz').read_bytes()
    d = json.loads(gzip.decompress(raw))
    assert d['h'] == h
    first, last = {}, {}
    for slot, old, new in d['events']:
        first.setdefault(slot, new)
        last[slot] = new
    outputs = {slot for slot, frame, common, target in d['outputs']}
    assert sorted(first) == list(range(d['R']))
    return d, first, last, outputs, sha256(raw).hexdigest()

def select(h, workers=4, directory=HERE, retirement_only=False):
    """Optional floating-point discovery; this is not a certificate acceptance gate."""
    original.load_word = lambda dimension: load_word(dimension, directory)
    if not retirement_only:
        return original.select(h, workers)
    d, first, last, outputs, digest = load_word(h, directory)
    keys = sorted({last[s] for s in range(d['R']) if s not in outputs})
    jobs = [(h, 'exit', g, *d['frames'][g]) for g in keys]
    with Pool(workers) as pool:
        results = {key: (removed, merged) for key, removed, merged in pool.map(original.evaluate, jobs, chunksize=8)}
    exterior = original.cost([h, original.M_ - 2*h])
    exits = []
    for slot in range(d['R']):
        if slot in outputs:
            continue
        (rr, removed), (mr, merged) = results['exit', last[slot]]
        assert mr == rr + original.M_ - h
        if original.cost(removed) + exterior - original.cost(merged) > 1e-9:
            exits.append(slot)
    used = sorted({last[s] for s in exits})
    return dict(h=h, R=d['R'], word_sha256=digest, entrance=[], exit=exits,
                merged_edges={f'exit:{g}': dict(rank=results['exit', g][1][0], runs=results['exit', g][1][1]) for g in used},
                candidate_edges=len(keys))

def verify_selection(frozen, h, workers=4, directory=HERE, retirement_only=False):
    """Verify a frozen witness using exact profiles for every eligible candidate.

    Per-role choices are source-pinned witness inputs. Float discovery can break
    equal-cost ties differently across Python versions; no discovery score is
    used by this acceptance path. Every chosen matrix and all subsequent paid
    arithmetic are still regenerated exactly.
    """
    d, first, last, outputs, digest = load_word(h, directory)
    assert set(frozen) == {'h', 'R', 'word_sha256', 'entrance', 'exit', 'merged_edges', 'candidate_edges'}
    assert frozen['h'] == h and frozen['R'] == d['R'] and frozen['word_sha256'] == digest
    entrances, exits = frozen['entrance'], frozen['exit']
    for roles in (entrances, exits):
        assert isinstance(roles, list) and all(type(s) is int and 0 <= s < d['R'] for s in roles)
        assert roles == sorted(set(roles)), 'Duplicate or unordered selected role'
    assert not set(entrances) & set(exits), 'Role selected twice'
    assert not set(exits) & outputs, 'Output role selected for retirement'
    assert not retirement_only or not entrances, 'Creation edge in retirement-only witness'
    keys = {('exit', last[s]) for s in range(d['R']) if s not in outputs}
    if not retirement_only:
        keys |= {('entrance', first[s]) for s in range(d['R'])}
    assert frozen['candidate_edges'] == len(keys), 'Eligible candidate inventory differs'
    jobs = [(h, kind, frame, *d['frames'][frame]) for kind, frame in sorted(keys)]
    with Pool(workers) as pool:
        results = {key: (removed, merged) for key, removed, merged in pool.map(original.evaluate, jobs, chunksize=8)}
    assert set(results) == keys
    for key, ((removed_rank, removed), (merged_rank, merged)) in results.items():
        assert sum(removed) == removed_rank and sum(merged) == merged_rank
        assert merged_rank == removed_rank + original.M_ - h
        assert all(type(t) is int and 0 < t < original.M_ for t in merged)
    used = {('entrance', first[s]) for s in entrances} | {('exit', last[s]) for s in exits}
    assert used <= keys
    actual = dict(h=h, R=d['R'], word_sha256=digest, entrance=entrances, exit=exits,
                  merged_edges={f'{kind}:{frame}': dict(rank=results[kind, frame][1][0], runs=results[kind, frame][1][1])
                                for kind, frame in sorted(used)}, candidate_edges=len(keys))
    assert actual == frozen, 'Frozen merged profile differs from exact regeneration'
    return actual

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--h', required=True, type=int, choices=(23, 25))
    parser.add_argument('--words', type=Path, default=HERE)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--retirement-only', action='store_true')
    args = parser.parse_args()
    result = select(args.h, args.workers, args.words, args.retirement_only)
    args.output.write_text(json.dumps(result, sort_keys=True, separators=(',', ':')) + '\n')
    print(f'PASS exact endpoint profiles h={args.h}, entrance={len(result["entrance"])}, retirement={len(result["exit"])}', flush=True)
