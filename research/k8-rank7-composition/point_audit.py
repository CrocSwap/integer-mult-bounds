# SPDX-License-Identifier: Apache-2.0
# Adapted from Alexander Schwartzman PR1030 audit_points.py; see NOTICE.md.
"""Independent frame accounting by explicit subsets of the 512-point space.

No builder, solver, native auditor, or Gaussian elimination is imported.
Scalar identities, row/column cones, phases, and global admission are separate.
Prepared with OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter
import copy
from functools import lru_cache
import gzip
import hashlib
import json
from pathlib import Path


BASE_SHA = '090fd574747fbf9628e70cb9beb792732914cfa52e1df147579fe4dbccc68c5a'
WORD_SHA = '096ed4abee4bb02c0d6f03bb8191510e57f6b1fcd34e8644f4fd336254e46411'
RECIPE = Path(__file__).resolve().parent / 'data/END-RECIPE.json'


class Reject(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise Reject(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def read(path):
    raw = gzip.decompress(path.read_bytes())
    return json.loads(raw), hashlib.sha256(raw).hexdigest()


@lru_cache(None)
def points(vectors):
    space = {0}
    for vector in vectors:
        require(type(vector) is int and 0 <= vector < 512, 'invalid GF2 vector')
        space |= {value ^ vector for value in space}
    require(len(space) == 1 << len(vectors), 'dependent frame basis')
    return frozenset(space)


def dimension(space):
    return len(space).bit_length() - 1


def registers(event):
    require(event[0] in ('add', 'scale'), 'unknown gate')
    result = event[1:3] if event[0] == 'add' else event[1:2]
    require(all(type(q) is int and 0 <= q < 704 for q in result), 'register range')
    return result


def recount(word):
    require(tuple(word['report'][k] for k in ('v', 'h', 'R')) == (112, 9, 480), 'dimensions')
    require(len(word['ports']) == len(set(word['ports'])) == 112, 'ports')
    full, zero = frozenset(range(512)), points(())
    start = [points((p,)) for p in word['ports']] + [zero] * 592
    for q, frame in word['start_extra'].items():
        require(224 <= int(q) < 704, 'start register')
        start[int(q)] = points(tuple(frame))
    current, paid = start.copy(), Counter()

    def climb(q, target):
        require(current[q] <= target, 'nonmonotone frame')
        degree = dimension(target) - dimension(current[q])
        if degree:
            paid[degree] += 1
        current[q] = target

    for section in ('A', 'B'):
        if section == 'B':
            levels = {int(q): points(tuple(frame)) for q, frame in word['target_levels'].items()}
            require(all(current[112 + q] == levels.get(q, zero) for q in range(112)), 'target interface')
            require(len(word['centers']) == len(word['center_frames']) == 8, 'center count')
            for q, frame in zip(word['centers'], word['center_frames']):
                frame = points(tuple(frame))
                require(current[q] == frame, 'center interface')
                served = {levels.get(event[1] - 112, zero) for event in word['cut'] if event[2] == q}
                for target in sorted(served, key=len, reverse=True):
                    require(target <= frame, 'center descent')
                    degree = dimension(frame) - dimension(target)
                    if degree:
                        paid[degree] += 1
                    frame = target
        for event in word[section]:
            frame = points(tuple(event[-1]))
            for q in registers(event):
                climb(q, frame)
    seen = set()
    for index, frame in word['early_cleanup']:
        require(type(index) is int and 0 <= index < len(word['cleanup']), 'tail index')
        require(index not in seen, 'duplicate tail')
        seen.add(index)
        for q in registers(word['cleanup'][index]):
            climb(q, points(tuple(frame)))
    end = ([full] * 112 +
           [frozenset(x for x in range(512) if (x & p).bit_count() % 2 == 0) for p in word['ports']] +
           [full] * 480)
    for q, frame in word['helper_final'].items():
        require(224 <= int(q) < 704, 'end register')
        end[int(q)] = points(tuple(frame))
    for q, frame in enumerate(end):
        climb(q, frame)
    for index, event in enumerate(word['cleanup']):
        if index not in seen:
            require(all(end[q] == full for q in registers(event)), 'full cleanup reads a low end')
    profile = {str(k): count for k, count in sorted(paid.items())}
    require(canonical(profile) == canonical(word['report']['local_profile']), 'paid profile')
    mass = sum(rank * count for rank, count in paid.items())
    require(type(word['report']['local_rank_mass']) is int and word['report']['local_rank_mass'] == mass, 'rank mass')
    widths = [dimension(end[q]) - dimension(start[q]) for q in range(224, 704)]
    require(all(0 < width <= 9 for width in widths), 'helper width range')
    inventory = {str(k): count for k, count in sorted(Counter(widths).items())}
    require(canonical(inventory) == canonical(word['report']['width_inventory']), 'width inventory')
    return paid, widths


def verify(path):
    word, _ = read(path)
    paid, widths = recount(word)
    require(dict(paid) == {1:2406,2:432,3:424,4:142,5:82,8:8}, 'new local profile')
    return dict(paid=paid,widths=widths)

if __name__ == '__main__':
    import sys
    verify(Path(sys.argv[1]))
    print('PASS_K8_512_POINT_FRAME_ACCOUNTING')
