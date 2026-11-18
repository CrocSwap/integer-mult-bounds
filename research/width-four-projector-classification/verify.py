"""Replay the complete finite classification. Ali Romman, with Codex. Apache-2.0."""

from collections import Counter
from contextlib import redirect_stdout
from hashlib import sha256
import importlib.util
from io import StringIO
import json
from pathlib import Path

import census
import matrix_check as direct

ROOT = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_sources():
    pins = json.loads((ROOT / 'SOURCE-PINS.json').read_text())
    for pin in pins:
        raw = (ROOT / pin['retained_path']).read_bytes()
        require(sha256(raw).hexdigest() == pin['sha256'], 'source digest')
    require(len(pins) == 9, 'source count')
    spec = importlib.util.spec_from_file_location(
        'source7749', ROOT / 'retained/even-one-edge-maximizer/verify.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    receipt = StringIO()
    with redirect_stdout(receipt):
        module.main()
    require('PASS_EVEN_ONE_EDGE_MAXIMIZER' in receipt.getvalue(), 'source replay')
    return receipt.getvalue().strip().splitlines()


def expand_pattern(value):
    return sum(((value >> bit) & 1) << (4 * i + j)
               for bit, (i, j) in enumerate(census.COORDINATES))


def collect():
    source_receipt = check_sources()
    count, found = census.census()
    require(count == 698027, 'quotient plane count')
    projectors, second = direct.second_census()
    expanded = {tuple(sorted(expand_pattern(v) for v in h)):
                tuple(sorted(direct.packed(direct.matrix(*p)) for p in pool))
                for h, pool in found.items()}
    require(len(projectors) == 120 and second == expanded, 'independent census')
    actions, labels = direct.group_actions(projectors)
    require(len(actions) == 20160, 'full linear group')
    classes = {}
    witnesses = {}
    for patterns, pool in sorted(found.items()):
        key, basis = census.canonical(pool)
        transform = tuple(sum(((v >> i) & 1) << j for j, v in enumerate(basis))
                          for i in range(4))
        back = direct.inverse(transform)
        actual = sorted(direct.packed(direct.multiply(
            direct.multiply(back, direct.matrix(*pair)), transform)) for pair in pool)
        expected = sorted(direct.packed(direct.matrix(*divmod(value, 16))) for value in key)
        require(actual == expected, 'matrix conjugacy witness')
        classes.setdefault(key, []).append(patterns)
        witnesses[patterns] = basis
    distinct = set()
    rows = []
    assignments = []
    for number, (key, spaces) in enumerate(sorted(classes.items()), 1):
        label = f'C{number:03d}'
        pool = found[spaces[0]]
        matrices = tuple(direct.matrix(*pair) for pair in pool)
        orbit_key, stabilizer, orbit_size = direct.orbit_summary(matrices, actions, labels)
        require(orbit_key not in distinct, 'two classes have the same full-group orbit')
        distinct.add(orbit_key)
        invariant = direct.invariant_subspaces(matrices)
        trace_pairs = sum((x & v).bit_count() % 2 and (u & y).bit_count() % 2
                          for i, (x, y) in enumerate(pool) for u, v in pool[i + 1:])
        rows.append(dict(id=label, canonical_factors=list(key),
                         representative_patterns=list(spaces[0]),
                         representative_pool=[list(pair) for pair in pool],
                         anchored_spaces=len(spaces), pool_size=len(pool),
                         invariant_subspaces_by_dimension=invariant,
                         irreducible=not any(invariant[1:4]),
                         trace_one_pairs=trace_pairs, stabilizer=stabilizer,
                         orbit_size=orbit_size, full_group_key=list(orbit_key)))
        assignments.extend(dict(patterns=list(h), action_class=label,
                                image_basis=list(witnesses[h])) for h in spaces)
    known = {'PR7749': ((1, 3), (3, 2), (5, 9), (11, 6)),
             'PR7707': ((1, 3), (3, 2), (6, 5), (10, 9))}
    references = {}
    for name, pool in known.items():
        h = tuple(sorted(census.span(census.off(*pair) for pair in pool) - {0}))
        require(found[h] == tuple(sorted(pool)), 'known complete pool')
        key, _ = census.canonical(pool)
        row = next(row for row in rows if row['canonical_factors'] == list(key))
        references[name] = row['id']
        require(row['irreducible'], 'known irreducibility')
    require(len(set(references.values())) == 2, 'distinct source actions')
    require(census.qualifying(tuple(sorted(census.span((1, 2, 1 << 8)) - {0})))
            is None, 'matching-two negative control')
    require(census.qualifying(tuple(sorted(census.span((1, 2)) - {0})))
            is None, 'dimension-two negative control')
    require(all(census.off(*pair) for pool in found.values() for pair in pool),
            'zero-pattern exclusion')
    histogram = Counter((row['pool_size'], row['irreducible']) for row in rows)
    return dict(schema_version=1, quotient_planes=count, anchored_spaces=len(found),
                action_classes=len(rows), irreducible_classes=sum(row['irreducible'] for row in rows),
                projectors=len(projectors), invertible_matrices=len(actions),
                class_histogram=[dict(pool_size=n, irreducible=b, classes=amount)
                                 for (n, b), amount in sorted(histogram.items())],
                source_receipt=source_receipt, source_classes=references,
                classes=rows, assignments=sorted(assignments, key=lambda row: row['patterns']))


def main():
    actual = collect()
    expected = json.loads((ROOT / 'classification.json').read_text())
    require(actual == expected, 'classification certificate differs')
    require((actual['anchored_spaces'], actual['action_classes'], actual['irreducible_classes'])
            == (2070, 386, 40), 'classification totals')
    print('PASS_WIDTH_FOUR_PROJECTOR_CLASSIFICATION')
    print('698027 planes; 2070 anchored spaces; 386 action classes; 40 irreducible classes')
    print('120 projectors; 20160 direct matrix conjugacies per class; 67 invariant subspaces per class')
    print('Source classes: ' + json.dumps(actual['source_classes'], sort_keys=True))


if __name__ == '__main__':
    main()
