"""Audit six frozen frame edits using explicit subsets of F_2^9.

No imports from the supplier's frame algebra or profile implementation.
Adam Gall, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter
from functools import cache
import gzip
import hashlib
import json
from pathlib import Path
import tempfile

from rebuild import rebuild

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = 'ba82555c64e1879e4b7decce28186f208fcb8262'
SEED = 67
FULL = frozenset(range(512))
ZERO = frozenset({0})


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


@cache
def space(vectors):
    """List every vector, rather than row reducing a binary basis."""
    result = {0}
    for vector in vectors:
        require(type(vector) is int and 0 <= vector < 512, 'vector outside F2^9')
        result |= {x ^ vector for x in result}
    return frozenset(result)


def dimension(frame):
    size = len(frame)
    require(size > 0 and size & (size - 1) == 0, 'not a subspace cardinality')
    return size.bit_length() - 1


def incident(operation):
    require(operation[0] in ('add', 'scale'), 'unknown scalar operation')
    return operation[1:3] if operation[0] == 'add' else operation[1:2]


def replay(word, replacements):
    """Read every A/B incidence, centre descent and final endpoint."""
    ports = word['ports']
    count = len(ports)
    helpers = word['report']['R']
    starts = word.get('start_extra', {})
    current = [space((port,)) for port in ports] + [ZERO] * count
    current += [space(tuple(starts.get(str(r), ())))
                for r in range(2 * count, 2 * count + helpers)]
    widths = [9 - dimension(frame) for frame in current[2 * count:]]
    profile = Counter()
    histories = [[] for _ in current]

    def climb(register, frame, site):
        old = current[register]
        require(old <= frame, f'nonnested frame at {site}, register {register}')
        rank = dimension(frame) - dimension(old)
        if rank:
            profile[rank] += 1
        histories[register].append((site, tuple(sorted(old)), tuple(sorted(frame))))
        current[register] = frame

    levels = {int(t): space(tuple(v)) for t, v in word.get('target_levels', {}).items()}
    for part in ('A', 'B'):
        if part == 'B':
            for register, vectors in zip(word['centers'], word['center_frames'], strict=True):
                frame = space(tuple(vectors))
                require(current[register] == frame, 'centre frame mismatch')
                served = {levels.get(e[1] - count, ZERO)
                          for e in word['cut'] if e[2] == register}
                for lower in sorted(served, key=lambda s: (-len(s), tuple(sorted(s)))):
                    require(lower <= frame, 'nonnested centre descent')
                    rank = dimension(frame) - dimension(lower)
                    if rank:
                        profile[rank] += 1
                    frame = lower
            for target in range(count):
                require(current[count + target] == levels.get(target, ZERO),
                        'scatter target level mismatch')
        for index, operation in enumerate(word[part]):
            frame = replacements.get((part, index), space(tuple(operation[-1])))
            for register in incident(operation):
                climb(register, frame, f'{part}:{index}')
    for register in range(len(current)):
        endpoint = FULL
        if count <= register < 2 * count:
            port = ports[register - count]
            endpoint = frozenset(x for x in range(512) if (x & port).bit_count() % 2 == 0)
        climb(register, endpoint, 'endpoint')
    return dict(profile), widths, histories


def delta(after, before):
    return {r: after.get(r, 0) - before.get(r, 0)
            for r in sorted(after.keys() | before.keys())
            if after.get(r, 0) != before.get(r, 0)}


def audit(word, recipe):
    require(digest(canonical(word)) == recipe['input_content_sha256'], 'source word content pin')
    changes = recipe['changes']
    require(len(changes) == 6, 'expected six changes')
    touched = []
    for change in changes:
        part, index = change['section'], change['index']
        require(word[part][index] == change['before'], 'literal source operation mismatch')
        require(change['before'][:-1] == change['after'][:-1], 'scalar operation changed')
        old, new = (space(tuple(change[key][-1])) for key in ('before', 'after'))
        require(dimension(old) == 1 and dimension(new) == 2 and old < new,
                'not a containing-plane promotion')
        touched.extend(incident(change['before']))
    require(len(touched) == len(set(touched)), 'edits share an incident register')
    baseline, widths, histories = replay(word, {})
    require(baseline == {int(k): v for k, v in recipe['before'].items()}, 'baseline profile')
    profiles = {}
    for ordinal in range(64):
        mask = (ordinal + SEED) % 64
        replacements = {(c['section'], c['index']): space(tuple(c['after'][-1]))
                        for j, c in enumerate(changes) if mask & (1 << j)}
        profile, new_widths, _ = replay(word, replacements)
        require(new_widths == widths, 'helper width changed')
        k = mask.bit_count()
        expected = {} if k == 0 else {1: -2 * k, 2: k}
        require(delta(profile, baseline) == expected, f'nonadditive subset {mask}')
        profiles[mask] = profile
    require(profiles[63] == {int(k): v for k, v in recipe['after'].items()}, 'final profile')
    edges = 0
    for mask in range(64):
        for bit in range(6):
            if not mask & (1 << bit):
                require(delta(profiles[mask | (1 << bit)], profiles[mask]) == {1: -2, 2: 1},
                        'nonconstant Boolean-lattice marginal')
                edges += 1

    # Every containing plane at each fixed site, not just the nominated plane.
    # Only its incident neighbours can change legality or payment. Check the
    # local triple and then full-replay each surviving plane as a cross-check.
    plane_census = []
    controls = []
    for change in changes:
        site = (change['section'], change['index'])
        label = f'{site[0]}:{site[1]}'
        old = space(tuple(change['before'][-1]))
        generator = next(x for x in old if x)
        planes = {space((generator, vector)) for vector in range(1, 512) if vector not in old}
        require(len(planes) == 255, 'containing-plane domain')
        neighbours = []
        for register in incident(change['before']):
            chain = histories[register]
            position = next(j for j, row in enumerate(chain) if row[0] == label)
            prior = frozenset(chain[position][1])
            following = frozenset(chain[position + 1][2])
            neighbours.append((register, prior, following))
        nominated = space(tuple(change['after'][-1]))
        require([prior for _, prior, _ in neighbours] == [ZERO, old]
                and all(following == nominated for _, _, following in neighbours),
                'fixed-neighbour two-choice lemma premises')
        admissible = []
        for plane in sorted(planes, key=lambda s: tuple(sorted(s))):
            if all(prior <= plane <= following for _, prior, following in neighbours):
                profile, _, _ = replay(word, {site: plane})
                admissible.append({'vectors': sorted(plane), 'delta': delta(profile, baseline)})
        require(len(admissible) == 1 and admissible[0]['vectors'] == sorted(nominated),
                'nominated plane is not the unique legal plane')
        plane_census.append({
            'site': label,
            'tested': len(planes),
            'admissible': admissible,
            'neighbours': [{'register': r, 'before': sorted(lo), 'next': sorted(hi)}
                           for r, lo, hi in neighbours],
        })
        try:
            replay(word, {site: FULL})
        except ValueError as error:
            require('nonnested frame' in str(error), 'unexpected overpromotion failure')
            controls.append({'site': label, 'kind': 'overpromotion', 'failure': str(error)})
        else:
            raise ValueError('overpromotion accepted')
        j = changes.index(change)
        require(profiles[63 ^ (1 << j)] != profiles[63], 'omitted edit went undetected')
        controls.append({'site': label, 'kind': 'omission', 'delta_from_full': {1: 2, 2: -1}})
        # Same dimension and old-line containment do not suffice for legality.
        illegal = next(p for p in sorted(planes, key=lambda s: tuple(sorted(s)))
                       if not all(lo <= p <= hi for _, lo, hi in neighbours))
        try:
            replay(word, {site: illegal})
        except ValueError as error:
            require('nonnested frame' in str(error), 'unexpected wrong-plane failure')
            controls.append({'site': label, 'kind': 'wrong-containing-plane',
                             'vectors': sorted(illegal), 'failure': str(error)})
        else:
            raise ValueError('same-rank nonnested plane accepted')
    return {
        'status': 'PASS_SIX_COALESCENCES_ALL_SUBSETS_AND_CONTAINING_PLANES',
        'base_commit': BASE, 'assignment_seed': SEED,
        'source_word_content_sha256': digest(canonical(word)),
        'subset_count': 64, 'directed_subset_edges': edges,
        'subsets': [{'mask': mask, 'profile': profiles[mask]} for mask in range(64)],
        'plane_census': plane_census,
        'helper_width_inventory': dict(sorted(Counter(widths).items())),
        'negative_controls': controls,
        'scope': 'Exact finite frame-chain accounting only; no native phase, physical-owner, or kappa admission.',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--word', type=Path, help='Reuse a raw word; its exact decoded content pin is mandatory')
    parser.add_argument('--write-result', action='store_true', help='Regenerate only this audit receipt')
    args = parser.parse_args()
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    for relative, expected in pins['files'].items():
        require(digest((ROOT / relative).read_bytes()) == expected, f'source pin: {relative}')
    supplier = ROOT / 'research/kernel-frame-coalescing'
    for relative, expected in json.loads((supplier / 'MANIFEST.json').read_text()).items():
        require(digest((supplier / relative).read_bytes()) == expected,
                f'supplier manifest: {relative}')
    recipe = json.loads((ROOT / 'research/kernel-frame-coalescing/data/FRAME-CHANGES.json').read_text())
    with tempfile.TemporaryDirectory(prefix='coalescing-subset-') as work:
        path = args.word if args.word is not None else rebuild(ROOT, Path(work))
        word = json.loads(gzip.decompress(path.read_bytes()))
        result = audit(word, recipe)
    if args.write_result:
        (HERE / 'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        require(canonical(result) == canonical(json.loads((HERE / 'RESULT.json').read_text())),
                'audit receipt mismatch')
    print(result['status'])
    print('64 subsets; 192 marginals; 1530 containing planes; 18 negative controls')


if __name__ == '__main__':
    main()
