#!/usr/bin/env python3
"""Exact mutable-source connector certificate. Arham Tahir / OpenAI, Apache-2.0."""
import argparse
from collections import Counter
import hashlib
from itertools import combinations
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def census():
    fixed = {0, 1, 2, 4, 8, 16}
    extras = sorted(set(range(32)) - fixed)
    histogram = Counter()
    for tail in combinations(extras, 3):
        points = fixed | set(tail)
        histogram[len({a ^ b for a in points for b in points})] += 1
    return {str(k): v for k, v in sorted(histogram.items())}


def source_bindings():
    manifest = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    inputs = []
    for row in manifest['files']:
        if row['usage'] == 'input':
            data = (ROOT / row['path']).read_bytes()
            require(hashlib.sha256(data).hexdigest() == row['sha256'], 'source drift: ' + row['path'])
            blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
            require(blob == row['git_blob'], 'source blob: ' + row['path'])
            inputs.append(row['path'])
    prefix = 'research/universal-connector-boundary/'
    require(sorted(inputs) == [prefix + name for name in ('CERTIFICATE.json', 'NOTICE.md', 'README.md')],
            'missing live source inventory')
    return inputs


def schedule(points):
    require(points[0] == points[-1] == 0, 'source path is not closed')
    require(len(points) == 11 and len(set(points)) == 10, 'ten distinct boundary points required')
    require(all(type(p) is int and 0 <= p < 32 for p in points), 'invalid source point')
    readouts = [[] for _ in points]
    pairs = []
    for mask in range(1, 32):
        pair = next(((s, t) for s in range(len(points)) for t in range(s + 1, len(points))
                     if points[s] ^ points[t] == mask), None)
        require(pair is not None, 'uncovered output mask')
        pairs.append(list(pair))
        for boundary in pair:
            readouts[boundary].append(mask)
    # x0..x4, y1..y31, root connector z; lower-level scratch 37..39.
    word = []
    for s, masks in enumerate(readouts):
        word.extend(('A', mask, 36, 4 + mask) for mask in masks)
        if s == len(points) - 1:
            break
        support = [j for j in range(5) if (points[s] ^ points[s + 1]) >> j & 1]
        require(support, 'zero source step')
        pivot, *others = support
        word.extend(('X', -1, j, pivot) for j in others)
        word.append(('B', 0, pivot, 36))
        word.extend(('X', -1, j, pivot) for j in reversed(others))
    return word, pairs


def lower(factors, source, target, scratch):
    require(source != target and source not in scratch and target not in scratch, 'aliased child ports')
    if len(factors) == 1:
        return [(factors[0], source, target)]
    require(bool(scratch), 'insufficient dirty scratch')
    mid = len(factors) // 2
    temp = scratch[0]
    r = lower(factors[:mid], source, temp, scratch[1:])
    l = lower(factors[mid:], temp, target, scratch[1:])
    return r + l + list(reversed(r)) + list(reversed(l))


def expand(word):
    gates = []
    for kind, index, source, target in word:
        if kind == 'X':
            require(index == -1 and source < 5 and target < 5 and source != target, 'illegal source shear')
            gates.append((-1, source, target))
        else:
            require(kind in ('A', 'B'), 'unknown query')
            require((kind == 'B' and index == 0 and source < 5 and target == 36) or
                    (kind == 'A' and 1 <= index <= 31 and source == 36 and target == 4 + index),
                    'query outside typed interface')
            factors = list(range(5 * index, 5 * index + 5))
            gates.extend(lower(factors, source, target, [37, 38, 39]))
    return gates


def toggle(target, values):
    for value in values:
        if value in target:
            target.remove(value)
        else:
            target.add(value)


def free_replay(gates):
    # (noncommuting operator word, arbitrary incoming row) over F2.
    state = [{((), row)} for row in range(40)]
    for operator, source, target in gates:
        require(0 <= source < 40 and 0 <= target < 40 and source != target, 'invalid primitive ports')
        values = list(state[source])
        if operator >= 0:
            values = [((operator,) + monomial, row) for monomial, row in values]
        toggle(state[target], values)
    return state


def expected_state():
    state = [{((), row)} for row in range(40)]
    for mask in range(1, 32):
        factors = tuple(reversed(range(5 * mask, 5 * mask + 5))) + tuple(reversed(range(5)))
        for j in range(5):
            if mask >> j & 1:
                state[4 + mask].add((factors, j))
    return state


def reference_checks():
    data = json.loads((ROOT / 'research/universal-connector-boundary/CERTIFICATE.json').read_text(encoding='utf-8'))
    receipts = {}
    for name in ('five_extra_source', 'five_extra_output'):
        original = data['schedules'][name]
        require(original['rows'] == list(range(1, 32)), 'reference rows changed')
        word = [('B', 0, index, 36) if kind == 'B' else ('A', index + 1, 36, index + 5)
                for kind, index in original['word']]
        gates = expand(word)
        require(len(word) == 74 and len(gates) == 2072, 'reference invoice')
        require(free_replay(gates) == expected_state(), 'reference forward identity')
        require(free_replay(list(reversed(gates))) == expected_state(), 'reference inverse identity')
        receipts[name] = dict(sorted(Counter(g[0] for g in word).items()))
    return receipts


def controls(points, gates):
    expected = expected_state()
    count = 0
    i = next(i for i, g in enumerate(gates) if g[0] == -1)
    mutants = [gates[:i] + gates[i + 1:], gates[:-1]]
    changed = list(gates)
    i = next(i for i, g in enumerate(changed) if g[0] == 0)
    changed[i] = (159, changed[i][1], changed[i][2])
    mutants.append(changed)  # Violates the common-B premise.
    changed = list(gates)
    i = next(i for i, g in enumerate(changed) if g[0] >= 5)
    changed[i] = (changed[i][0], changed[i][1], 4 + ((changed[i][2] - 4) % 31) + 1)
    mutants.append(changed)
    # Wrong factor order must be observable for noncommuting maps.
    mutants.append([(4 - op if 0 <= op < 5 else op, s, t) for op, s, t in gates])
    for mutant in mutants:
        require(free_replay(mutant) != expected, 'semantic control was accepted')
        count += 1
    for bad in ([0] + points[1:-1] + [1], points[:-2] + [points[-3], 0]):
        try:
            schedule(bad)
        except ValueError:
            count += 1
        else:
            raise ValueError('bad path accepted')
    for args in ((list(range(5)), 0, 36, [37, 38]), ([0], 0, 0, [37])):
        try:
            lower(*args)
        except ValueError:
            count += 1
        else:
            raise ValueError('bad child admission accepted')
    return count


def compute(points):
    word, pairs = schedule(points)
    gates = expand(word)
    require(free_replay(gates) == expected_state(), 'forward free-algebra identity')
    require(free_replay(list(reversed(gates))) == expected_state(), 'inverse free-algebra identity')
    counts = dict(sorted(Counter(g[0] for g in word).items()))
    return {'schema_version': 1, 'points': points, 'readout_pairs': pairs,
            'nine_point_histogram': census(), 'root_counts': counts,
            'primitive_count': len(gates), 'borrowed_dirty_rows': 4,
            'word_sha256': hashlib.sha256(json.dumps(word, separators=(',', ':')).encode()).hexdigest(),
            'primitive_sha256': hashlib.sha256(json.dumps(gates, separators=(',', ':')).encode()).hexdigest(),
            'reference_primitives': 74 * 28, 'saving': 74 * 28 - len(gates),
            'reference_root_counts': reference_checks(),
            'internal_nodes': 72 * 9, 'reference_internal_nodes': 74 * 9,
            'unit_complete_tariff': {'candidate': 2016 + 12 + 648 + 84,
                                     'reference': 2072 + 666 + 74, 'saving': 52},
            'semantic_controls': controls(points, gates)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', type=Path, help='write a new certificate; never overwrite')
    args = parser.parse_args()
    source_bindings()
    result = compute([0, 16, 8, 31, 5, 4, 6, 2, 3, 1, 0])
    require(sum(result['nine_point_histogram'].values()) == 2600 and
            '32' not in result['nine_point_histogram'], 'nine-point exclusion')
    require(result['root_counts'] == {'A': 62, 'B': 10, 'X': 12}, 'unpaid query or source shear')
    require(result['primitive_count'] == 2028 and result['saving'] == 44, 'primitive invoice')
    if args.write:
        with args.write.open('x', encoding='utf-8', newline='\n') as stream:
            json.dump(result, stream, indent=2)
            stream.write('\n')
    else:
        require(result == json.loads((HERE / 'CERTIFICATE.json').read_text(encoding='utf-8')), 'certificate mismatch')
    print('PASS_MUTABLE_SOURCE_CONNECTOR B=10 A=62 XOR=12 census=2600 primitives=2028_vs_2072 controls=9 no_new_kappa')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError) as error:
        print('FAIL_MUTABLE_SOURCE_CONNECTOR: ' + str(error), file=sys.stderr)
        raise SystemExit(1)
