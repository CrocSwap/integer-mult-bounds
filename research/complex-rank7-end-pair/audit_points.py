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
    require(all(type(q) is int and 0 <= q < 728 for q in result), 'register range')
    return result


def recount(word):
    require(tuple(word['report'][k] for k in ('v', 'h', 'R')) == (112, 9, 504), 'dimensions')
    require(len(word['ports']) == len(set(word['ports'])) == 112, 'ports')
    full, zero = frozenset(range(512)), points(())
    start = [points((p,)) for p in word['ports']] + [zero] * 616
    for q, frame in word['start_extra'].items():
        require(224 <= int(q) < 728, 'start register')
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
           [full] * 504)
    for q, frame in word['helper_final'].items():
        require(224 <= int(q) < 728, 'end register')
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
    widths = [dimension(end[q]) - dimension(start[q]) for q in range(224, 728)]
    require(all(0 < width <= 9 for width in widths), 'helper width range')
    inventory = {str(k): count for k, count in sorted(Counter(widths).items())}
    require(canonical(inventory) == canonical(word['report']['width_inventory']), 'width inventory')
    return paid, widths


def check_edits(baseline, candidate, recipe):
    require(recipe['input_sha256'] == BASE_SHA and recipe['expected']['output_sha256'] == WORD_SHA, 'recipe pins')
    restored = copy.deepcopy(candidate)
    require([q for q, _, _ in recipe['ends']] == [588, 589], 'end sites')
    require([i for i, _, _ in recipe['B_frames']] ==
            [1018, 1019, 1050, 1051, 1130, 1131, 1162, 1163], 'B-frame sites')
    require([i for i, _, _, _ in recipe['early_cleanup']] == [148, 149], 'tail sites')
    changes = []
    for q, old, new in recipe['ends']:
        require(baseline['helper_final'][str(q)] == old and candidate['helper_final'][str(q)] == new, 'literal end edit')
        restored['helper_final'][str(q)] = old
        changes.append((old, new))
    for index, old, new in recipe['B_frames']:
        require(baseline['B'][index][-1] == old and candidate['B'][index][-1] == new, 'literal B edit')
        restored['B'][index][-1] = old
        changes.append((old, new))
    for index, cleanup_index, old, new in recipe['early_cleanup']:
        require(baseline['early_cleanup'][index] == [cleanup_index, old] and
                candidate['early_cleanup'][index] == [cleanup_index, new], 'literal tail edit')
        restored['early_cleanup'][index] = [cleanup_index, old]
        changes.append((old, new))
    for old, new in changes:
        a, b = points(tuple(old)), points(tuple(new))
        require(b < a and len(a) == 2 * len(b), 'codimension-one frame reduction')
    for key in ('local_profile', 'local_rank_mass', 'width_inventory'):
        require(canonical(candidate['report'][key]) == canonical(recipe['expected'][key]), 'reported recipe result')
        restored['report'][key] = baseline['report'][key]
    require(canonical(restored) == canonical(baseline), 'changes outside the twelve annotations and accounting')


def controls(candidate, recipe):
    cases = []
    mutant = copy.deepcopy(candidate)
    mutant['report']['local_profile']['1'] += 2
    mutant['report']['local_profile']['2'] -= 1
    cases.append(('mass-preserving false profile', mutant, 'paid profile'))
    mutant = copy.deepcopy(candidate)
    mutant['report']['local_profile']['1'] = float(mutant['report']['local_profile']['1'])
    cases.append(('floating profile count', mutant, 'paid profile'))
    mutant = copy.deepcopy(candidate)
    mutant['report']['width_inventory']['7'] -= 1
    mutant['report']['width_inventory']['8'] += 1
    cases.append(('false helper widths', mutant, 'width inventory'))
    mutant = copy.deepcopy(candidate)
    mutant['report']['local_rank_mass'] += 1
    cases.append(('false rank mass', mutant, 'rank mass'))
    mutant = copy.deepcopy(candidate)
    index, old, _ = recipe['B_frames'][0]
    mutant['B'][index][-1] = old
    cases.append(('omitted required B lowering', mutant, 'nonmonotone frame'))
    result = []
    for name, mutant, expected in cases:
        try:
            recount(mutant)
        except Reject as error:
            require(str(error) == expected, 'unexpected point-control rejection: ' + name)
            result.append(dict(name=name, rejected=expected))
        else:
            raise Reject('accepted point control: ' + name)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--word', type=Path, required=True)
    parser.add_argument('--recipe', type=Path, default=RECIPE)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    baseline, before_sha = read(args.baseline)
    candidate, after_sha = read(args.word)
    require((before_sha, after_sha) == (BASE_SHA, WORD_SHA), 'input content pins')
    recipe = json.loads(args.recipe.read_text(encoding='utf-8'))
    check_edits(baseline, candidate, recipe)
    before, old_widths = recount(baseline)
    after, widths = recount(candidate)
    delta = {r: after[r] - before[r] for r in before.keys() | after.keys() if before[r] != after[r]}
    require(delta == {1: -6, 2: 14, 3: -8}, 'profile delta')
    changes = [dict(helper=q + 224, before=a, after=b) for q, (a, b) in enumerate(zip(old_widths, widths)) if a != b]
    require(changes == [dict(helper=588, before=8, after=7), dict(helper=589, before=8, after=7)], 'individual helper widths')
    report = dict(status='PASS_EXPLICIT_512_POINT_END_PAIR_ACCOUNTING',
                  input_sha256=before_sha, output_sha256=after_sha,
                  changed_annotations=dict(helper_final=2, B=8, early_cleanup=2),
                  local_profile=dict(sorted(after.items())), delta=delta,
                  rank_mass_before=sum(r * n for r, n in before.items()),
                  rank_mass_after=sum(r * n for r, n in after.items()),
                  width_inventory=dict(sorted(Counter(widths).items())),
                  width_sum_before=sum(old_widths), width_sum_after=sum(widths),
                  changed_helper_widths=changes, rejected_controls=controls(candidate, recipe),
                  scope='Literal source, target, center, gate, tail, and end frames; paid profile; individual helper widths; '
                        'exact twelve-annotation recipe. Scalar identities, cones, phases, owners, and kappa are separate.')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(report['status'], '12 annotations; 5 rejected controls', flush=True)


if __name__ == '__main__':
    main()
