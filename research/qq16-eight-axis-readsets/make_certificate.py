"""Deterministic BFS discovery; verification does not trust this search.

Gareth Davidson with OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
import argparse
import json
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from verify import need, sources, rref


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    need(not args.out.exists(), 'output already exists')
    prior, model, bases, routes, _, _, _ = sources()
    seen, frontier, patterns = {1: []}, [1], {1: []}
    for depth in range(1, 5):
        new = []
        for vector in frontier:
            for p in range(112):
                out = prior.action(routes[1, p], vector)
                if out not in seen:
                    word = seen[vector] + [p]
                    seen[out] = word
                    new.append(out)
                    patterns.setdefault(out & 511, word)
            if len(patterns) == 512:
                break
        frontier = new
        if len(patterns) == 512:
            break
    need(len(patterns) == 512, 'bounded owner search did not cover all prefixes')
    _, pivots = rref([[row[p] for p in prior.U] for row in model.R])
    result = {'schema': 'qq16-eight-axis-owner-certificate/1',
              'owner_words_by_prefix': {str(k): v for k, v in sorted(patterns.items())},
              'occurring_axes': sorted({b for p in prior.U for b in bases[p]}),
              'unread_basis': [prior.U[j] for j in pivots]}
    with args.out.open('x') as f:
        json.dump(result, f, sort_keys=True, indent=2);f.write('\n')
    print('FOUND_OWNER_CERTIFICATE', 'depth=' + str(depth), 'visited=' + str(len(seen)))


if __name__ == '__main__':
    main()
