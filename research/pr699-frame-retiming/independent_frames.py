#!/usr/bin/env python3
"""Independent finite frame accounting for the eight PR699 B-gate retimings.

Subspaces are explicit subsets of GF(2)^9; no constructor or native auditor is
imported. This verifies frame containment and the complete local paid profile,
not scalar endpoint identities, phases, global hosting, or analytic transfer.
The preserved rank mass and eight copies of delta {1:+1, 2:-1, 3:-1, 4:+1}
strictly lower the moment for 0 < b < 1 by concavity of r^(1-b).
Prepared by Tekalign with substantial OpenAI Codex assistance; credits to
icekylinx and PR699 predecessors. Apache-2.0.
"""
import argparse
import collections
import copy
import functools
import gzip
import hashlib
import json
from pathlib import Path

BEFORE_SHA = 'd232183f233899961bf55cac67a18545ed33548d9a7ca7078990d1a83d557c59'
AFTER_SHA = 'e78047028c7dcd25fb1b6216c2b53eda76d2f91292b21d43f5d1903cc13a5c6c'
SITES = (856, 860, 868, 873, 876, 953, 961, 965)
SECTIONS = ('A', 'B', 'cut', 'cleanup', 'precondition')


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


@functools.lru_cache(None)
def span(vectors):
    points = {0}
    for vector in vectors:
        require(type(vector) is int and 0 <= vector < 512, 'vector outside GF(2)^9')
        points |= {point ^ vector for point in points}
    require(len(points) & (len(points) - 1) == 0, 'invalid subspace cardinality')
    return frozenset(points)


def dimension(points):
    return len(points).bit_length() - 1


def read(path):
    data = path.read_bytes()
    raw = gzip.decompress(data) if path.suffix == '.gz' else data
    return json.loads(raw), hashlib.sha256(raw).hexdigest()


def recount(word):
    v, helpers, h = (word['report'][key] for key in ('v', 'R', 'h'))
    require((v, helpers, h) == (112, 504, 9), 'word dimensions')
    n = 2 * v + helpers
    full = frozenset(range(512))
    cur = [frozenset((0, p)) for p in word['ports']] + [frozenset((0,))] * (n - v)
    for register, vectors in word['start_extra'].items():
        cur[int(register)] = span(tuple(vectors))
    starts = list(cur)
    paid = collections.Counter()

    def climb(register, target):
        require(cur[register] <= target, f'nonmonotone register {register}')
        rank = dimension(target) - dimension(cur[register])
        if rank:
            paid[rank] += 1
        cur[register] = target

    for section in ('A', 'B'):
        if section == 'B':
            levels = {int(t): span(tuple(u)) for t, u in word.get('target_levels', {}).items()}
            for register, vectors in zip(word['centers'], word['center_frames']):
                current = span(tuple(vectors))
                served = {levels.get(e[1] - v, frozenset((0,)))
                          for e in word['cut'] if e[2] == register}
                for target in sorted(served, key=len, reverse=True):
                    require(target <= current, 'center descent inclusion')
                    if target != current:
                        paid[dimension(current) - dimension(target)] += 1
                    current = target
        for event in word[section]:
            target = span(tuple(event[-1]))
            registers = event[1:3] if event[0] == 'add' else event[1:2]
            for register in registers:
                climb(register, target)
    for index, vectors in word['early_cleanup']:
        event = word['cleanup'][index]
        registers = event[1:3] if event[0] == 'add' else event[1:2]
        for register in registers:
            climb(register, span(tuple(vectors)))
    ends = ([full] * v +
            [frozenset(x for x in range(512) if (x & p).bit_count() % 2 == 0)
             for p in word['ports']] + [full] * helpers)
    for register, vectors in word['helper_final'].items():
        ends[int(register)] = span(tuple(vectors))
    for register, target in enumerate(ends):
        climb(register, target)
    widths = [dimension(ends[q]) - dimension(starts[q]) for q in range(2 * v, n)]
    claimed = {int(rank): count for rank, count in word['report']['local_profile'].items()}
    require(dict(paid) == claimed, 'local paid profile mismatch')
    require(sum(rank * count for rank, count in paid.items()) == word['report']['local_rank_mass'],
            'local rank mass mismatch')
    return paid, widths


def verify(before, after):
    changes = []
    for section in SECTIONS:
        require(len(before[section]) == len(after[section]), 'gate count changed')
        for index, (old, new) in enumerate(zip(before[section], after[section])):
            require(old[:-1] == new[:-1], 'scalar gate changed')
            if old[-1] != new[-1]:
                changes.append([section, index])
    for key in before.keys() | after.keys():
        if key not in set(SECTIONS) | {'report'}:
            require(before.get(key) == after.get(key), 'non-frame word field changed: ' + key)
    old_paid, old_widths = recount(before)
    paid, widths = recount(after)
    require(old_widths == widths, 'helper footprints changed')
    require(changes == [['B', index] for index in SITES], 'exact eight changed sites')
    delta = {rank: paid[rank] - old_paid[rank] for rank in paid.keys() | old_paid.keys()
             if paid[rank] != old_paid[rank]}
    require(delta == {1: 8, 2: -8, 3: -8, 4: 8}, 'profile delta')
    require(sum(rank * count for rank, count in delta.items()) == 0, 'rank mass preservation')
    return dict(changed_frames=changes, scalar_gates_unchanged=True,
                helper_footprints_unchanged=True, width_inventory=dict(collections.Counter(widths)),
                local_profile=dict(sorted(paid.items())), delta=delta,
                rank_mass=sum(rank * count for rank, count in paid.items()))


def negative_controls(before, after):
    results = []

    def reject(name, mutant, expected):
        try:
            verify(before, mutant)
        except RuntimeError as error:
            require(str(error) == expected, 'unexpected rejection site: ' + name)
            results.append(dict(name=name, rejected=True, site=expected))
        else:
            raise RuntimeError('accepted negative control: ' + name)

    for index in SITES:
        mutant = copy.deepcopy(after)
        mutant['B'][index][-1] = list(before['B'][index][-1])
        reject(f'delete-frame-change-B-{index}', mutant, 'local paid profile mismatch')
    mutant = copy.deepcopy(after)
    mutant['report']['local_profile']['1'] += 2
    mutant['report']['local_profile']['2'] -= 1
    require(sum(int(r) * c for r, c in mutant['report']['local_profile'].items()) == 5634,
            'control must preserve rank mass')
    reject('mass-preserving-false-profile', mutant, 'local paid profile mismatch')
    mutant = copy.deepcopy(after)
    mutant['B'][SITES[0]][3] *= -1
    reject('scalar-coefficient-perturbation', mutant, 'scalar gate changed')
    mutant = copy.deepcopy(after)
    register = next(iter(mutant['start_extra']))
    current = span(tuple(mutant['start_extra'][register]))
    mutant['start_extra'][register].append(next(x for x in range(512) if x not in current))
    reject('helper-start-expansion', mutant, 'non-frame word field changed: start_extra')
    mutant = copy.deepcopy(after)
    register = next(iter(mutant['helper_final']))
    mutant['helper_final'][register].pop()
    reject('helper-end-contraction', mutant, 'non-frame word field changed: helper_final')
    require(len(results) == 12, 'negative control count')
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--before', type=Path, required=True)
    parser.add_argument('--after', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    before, before_sha = read(args.before)
    after, after_sha = read(args.after)
    require(before_sha == BEFORE_SHA and after_sha == AFTER_SHA, 'raw content pins')
    result = verify(before, after)
    result.update(status='PASS_EXPLICIT_512_POINT_FRAME_RECOUNT',
                  input_content_sha256=before_sha, output_content_sha256=after_sha,
                  negative_controls=negative_controls(before, after),
                  method='Explicit finite subspace sets, independent of native Gaussian elimination.',
                  strict_gain='For 0 < b < 1, strict concavity gives '
                              '1^(1-b) + 4^(1-b) < 2^(1-b) + 3^(1-b). '
                              'The profile delta is eight times this difference.',
                  scope='Finite frame containment and local paid-child accounting only. Scalar endpoint '
                        'identities, phases, controller admission, whole-owner invoices and analytic '
                        'transfer remain separate obligations.')
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + '\n')
    print(result['status'], '12 negative controls rejected')


if __name__ == '__main__':
    main()
