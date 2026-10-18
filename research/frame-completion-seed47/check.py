#!/usr/bin/env python3
"""Independent exact local frame-completion checks for the seed47 h=10 DAG.

Only ParitySide's graph constructor is reused. Span propagation, radicals,
orthogonality, completions, exhaustive small spaces and controls use literal
XOR-closure sets; no producer or existing binary-frame checker is called.
This is local research geometry, not nested-edge or residual-decoder legality.
Checks use explicit exceptions and remain active under python -O.
"""
import argparse
from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
import re
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE_COMMIT = '007664306fff84fbb1c9a1b4053b69f439764034'
SOURCE_PATHS = {
    'scripts/binary_phase_frames.py', 'scripts/certify.py',
    'scripts/exclusion_circuit.py', 'scripts/paired_exclusion_circuit.py',
    'scripts/experiments/disjoint_tensor.py',
    'scripts/experiments/mixed_point_circuit.py',
    'scripts/experiments/parity_side.py',
}
RECORD_FIELDS = {'node', 'source_basis', 'target_basis', 'radical_dimension',
                 'feasible', 'frame_basis', 'common_vector'}


def require(condition, message):
    """Fail explicitly even when Python assertions are disabled."""
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, separators=(',', ':'), sort_keys=True,
                      allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def filehash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dot(left, right):
    return (left & right).bit_count() % 2


def join(left, right):
    """Enumerate the span of two closed vector sets by literal XOR doubling."""
    result = set(left)
    require(0 in result and 0 in right, 'span inputs must contain zero')
    for vector in sorted(right):
        if vector not in result:
            result.update({x ^ vector for x in result})
    return frozenset(result)


def span(vectors, h, label, independent=True):
    """Enumerate a recorded basis and reject zero/dependent/out-of-range rows."""
    require(isinstance(vectors, list), 'basis must be a list: ' + label)
    result = {0}
    for vector in vectors:
        require(type(vector) is int and 0 <= vector < 1 << h,
                'vector outside ambient space: ' + label)
        if independent:
            require(vector not in result, 'dependent basis: ' + label)
        result.update({x ^ vector for x in result})
    return frozenset(result)


def dimension(space):
    size = len(space)
    require(size > 0 and size & (size - 1) == 0, 'span cardinality is not a power of two')
    return size.bit_length() - 1


def spanning_vectors(space):
    """Find spanning rows by closure expansion, without row-reduction code."""
    rows, covered = [], {0}
    for vector in sorted(space):
        if vector not in covered:
            rows.append(vector)
            covered.update({x ^ vector for x in covered})
    require(covered == set(space), 'input is not XOR closed')
    return rows


def radical(space):
    """Test each vector against a complete spanning set for the same space."""
    rows = spanning_vectors(space)
    return frozenset(x for x in space if all(dot(x, y) == 0 for y in rows))


def perpendicular(space, h):
    rows = spanning_vectors(space)
    return frozenset(x for x in range(1 << h) if all(dot(x, y) == 0 for y in rows))


def orthogonal(left, right):
    return all(dot(x, y) == 0 for x in spanning_vectors(left)
               for y in spanning_vectors(right))


def source_pins(certificate):
    """Bind the complete seven-file graph-generator dependency closure."""
    pins = certificate['source_sha256']
    require(isinstance(pins, dict) and set(pins) == SOURCE_PATHS, 'generator source pin inventory')
    for relative, expected in pins.items():
        require(isinstance(expected, str) and re.fullmatch('[0-9a-f]{64}', expected),
                'invalid source digest: ' + relative)
        require(filehash(ROOT / relative) == expected, 'source pin mismatch: ' + relative)


def graph_context():
    """Construct only the specified graph; independently propagate label spans."""
    sys.path.insert(0, str(ROOT / 'scripts'))
    try:
        from experiments.parity_side import ParitySide
        graph = ParitySide(10)
    finally:
        sys.path.pop(0)
    active = sorted(graph.active)
    document = {
        'inputs': list(graph.inputs),
        'args': [[node, list(graph.args[node]) if graph.args[node] else None]
                 for node in active],
        'outputs': sorted([target, node] for target, node in graph.outputs.items()),
    }
    require(len(graph.inputs) == 120 and len(set(graph.inputs)) == 120 and
            all(label.bit_count() == 3 for label in graph.inputs) and
            set(graph.outputs) == set(graph.inputs), 'complete triple-label input/output inventory')
    sources, coefficients = {}, {}
    targets = {node: frozenset({0}) for node in active}
    for node in active:
        args = graph.args[node]
        if args:
            require(len(args) == 2 and all(abs(arg) in sources for arg in args),
                    'DAG dependency order')
            sources[node] = join(sources[abs(args[0])], sources[abs(args[1])])
            row = Counter()
            for arg in args:
                sign = 1 if arg > 0 else -1
                for index, value in coefficients[abs(arg)].items():
                    row[index] += sign * value
            coefficients[node] = {index: value for index, value in row.items() if value}
        else:
            require(1 <= node <= len(graph.inputs), 'unknown source leaf')
            label = graph.inputs[node - 1]
            require(type(label) is int and 0 < label < 1 << 10, 'input label range')
            sources[node] = frozenset({0, label})
            coefficients[node] = {node - 1: 1}
    for label, node in graph.outputs.items():
        require(type(label) is int and 0 <= label < 1 << 10 and abs(node) in targets,
                'output label or node range')
        sign = 1 if node > 0 else -1
        for index, source_label in enumerate(graph.inputs):
            intersection = (label & source_label).bit_count()
            expected = 1 if intersection == 0 else -1 if intersection == 2 else 0
            require(sign * coefficients[abs(node)].get(index, 0) == expected,
                    'signed intersection-parity output coefficient')
        targets[abs(node)] = join(targets[abs(node)], frozenset({0, label}))
    for node in reversed(active):
        if graph.args[node]:
            for arg in graph.args[node]:
                target = abs(arg)
                targets[target] = join(targets[target], targets[node])
    return dict(active=active, sources=sources, targets=targets,
                dag_sha256=digest(document), inputs=len(graph.inputs),
                output_copies=len(graph.outputs),
                binary_nodes=sum(bool(graph.args[node]) for node in active))


def check_record(record, actual_source, actual_target, h):
    """Validate either an explicit intersection obstruction or a minimal frame."""
    require(isinstance(record, dict) and set(record) == RECORD_FIELDS, 'record schema')
    node = record['node']
    label = ' at node ' + str(node)
    source = span(record['source_basis'], h, 'source' + label)
    target = span(record['target_basis'], h, 'target' + label)
    require(source == actual_source, 'source span' + label)
    require(target == actual_target, 'target span' + label)
    require(orthogonal(source, target), 'source/target orthogonality' + label)
    rad = dimension(radical(source))
    require(type(record['radical_dimension']) is int and record['radical_dimension'] == rad,
            'source radical dimension' + label)
    feasible = source & target == frozenset({0})
    require(type(record['feasible']) is bool and record['feasible'] == feasible,
            'feasibility label' + label)
    if feasible:
        require(record['common_vector'] is None, 'feasible common witness' + label)
        frame = span(record['frame_basis'], h, 'frame' + label)
        require(source <= frame, 'frame does not contain source' + label)
        require(orthogonal(frame, target), 'frame/target orthogonality' + label)
        require(radical(frame) == frozenset({0}), 'degenerate frame' + label)
        require(dimension(frame) == dimension(source) + rad, 'minimum frame dimension' + label)
        if h == 10:
            # An odd source lies in U; an odd target lies in U-perp. These
            # literal witnesses establish both restrictions are nonalternating.
            require(any(dot(x, x) for x in source) and any(dot(x, x) for x in target),
                    'odd witnesses for frame and orthogonal complement' + label)
        return dimension(source), rad, dimension(frame)
    common = record['common_vector']
    require(type(common) is int and common != 0 and common in source & target,
            'common-vector obstruction' + label)
    require(record['frame_basis'] is None, 'obstructed frame must be null' + label)
    return dimension(source), rad, None


def check_certificate(certificate, context):
    """Check exact graph inventory, every record, and all advertised summary fields."""
    require(isinstance(certificate, dict) and set(certificate) ==
            {'format', 'base_commit', 'seed', 'h', 'source_sha256', 'dag_sha256', 'records', 'summary'},
            'certificate schema')
    require(type(certificate['format']) is int and certificate['format'] == 1 and
            type(certificate['seed']) is int and certificate['seed'] == 47 and
            type(certificate['h']) is int and certificate['h'] == 10, 'bounded format/seed/dimension')
    require(certificate['base_commit'] == BASE_COMMIT, 'exact experiment base commit')
    source_pins(certificate)
    require(certificate['dag_sha256'] == context['dag_sha256'], 'canonical DAG digest')
    records = certificate['records']
    require(isinstance(records, list) and all(isinstance(row, dict) and type(row.get('node')) is int
                                            for row in records), 'record node types')
    require([row['node'] for row in records] == context['active'], 'record inventory and sorted order')
    counts = Counter()
    histogram = Counter()
    for row in records:
        node = row['node']
        source_dim, rad, frame_dim = check_record(row, context['sources'][node], context['targets'][node], 10)
        counts['degenerate_source_nodes'] += int(rad > 0)
        if frame_dim is None:
            counts['obstructed_nodes'] += 1
        else:
            counts['feasible_nodes'] += 1
            counts['completable_degenerate_nodes'] += int(rad > 0)
            counts['feasible_radical_dimension_sum'] += rad
            histogram[source_dim, rad, frame_dim] += 1
    summary = dict(active_nodes=len(records), binary_nodes=context['binary_nodes'],
                   inputs=context['inputs'], output_copies=context['output_copies'],
                   feasible_nodes=counts['feasible_nodes'], obstructed_nodes=counts['obstructed_nodes'],
                   degenerate_source_nodes=counts['degenerate_source_nodes'],
                   completable_degenerate_nodes=counts['completable_degenerate_nodes'],
                   feasible_radical_dimension_sum=counts['feasible_radical_dimension_sum'],
                   feasible_rank_histogram=[[*key, count] for key, count in sorted(histogram.items())])
    require(certificate['summary'] == summary, 'exact recomputed summary')
    return summary


def all_subspaces(h):
    """Exhaust all subspaces by adjoining every ambient vector and closing XOR."""
    zero = frozenset({0})
    seen, pending = {zero}, [zero]
    while pending:
        space = pending.pop()
        for vector in range(1, 1 << h):
            if vector in space:
                continue
            larger = frozenset(set(space) | {x ^ vector for x in space})
            if larger not in seen:
                seen.add(larger)
                pending.append(larger)
    return sorted(seen, key=lambda space: (len(space), sorted(space)))


def exhaustive_small_spaces():
    """Search every U for every orthogonal pair A,B in every h=0,...,4."""
    receipts = []
    expected_subspaces = (1, 2, 5, 16, 67)
    for h in range(5):
        spaces = all_subspaces(h)
        require(len(spaces) == expected_subspaces[h], 'small-space enumeration cardinality')
        perpendiculars = {space: perpendicular(space, h) for space in spaces}
        radicals = {space: radical(space) for space in spaces}
        nondegenerate = [space for space in spaces if radicals[space] == frozenset({0})]
        pairs = feasible_count = 0
        for source in spaces:
            for target in spaces:
                if not source <= perpendiculars[target]:
                    continue
                pairs += 1
                candidates = [space for space in nondegenerate if source <= space <= perpendiculars[target]]
                predicted = source & target == frozenset({0})
                require(bool(candidates) == predicted, f'exhaustive existence equivalence h={h}')
                if candidates:
                    feasible_count += 1
                    actual_minimum = min(dimension(space) for space in candidates)
                    require(actual_minimum == dimension(source) + dimension(radicals[source]),
                            f'exhaustive minimum dimension h={h}')
        receipts.append(dict(h=h, subspaces=len(spaces), nondegenerate_subspaces=len(nondegenerate),
                             orthogonal_pairs=pairs, feasible_pairs=feasible_count,
                             obstructed_pairs=pairs - feasible_count))
    return receipts


def pr920_negative_control():
    """Show that an admissible local separator need not give a legal residual decoder."""
    source = span([7, 25], 6, 'PR920 source')
    target = span([11, 19], 6, 'PR920 target')
    frame = span([25, 26, 4], 6, 'PR920 frame')
    require(orthogonal(source, target) and source & target == frozenset({0}), 'PR920 source separation')
    require(source <= frame and orthogonal(frame, target) and radical(frame) == frozenset({0}),
            'PR920 separating nondegenerate completion')
    require(dimension(frame) == dimension(source) + dimension(radical(source)) == 3, 'PR920 minimum dimension')
    residual = frozenset(x for x in frame if dot(x, 7) == 0)
    require(dimension(residual) == 2 and radical(residual) == frozenset({0}), 'PR920 residual rank')
    require(all(dot(x, x) == 0 for x in residual), 'PR920 alternating residual')
    return dict(status='PASS_SEPARATION_DOES_NOT_ESTABLISH_RESIDUAL_LEGALITY',
                h=6, source_basis=[7, 25], target_basis=[11, 19], frame_basis=[25, 26, 4],
                residual_source=7, residual_vectors=sorted(residual),
                residual_dimension=2, residual_alternating=True,
                orthonormal_residual_basis_exists=False)


def certificate_controls(certificate, context):
    """Require concrete corruptions to fail, using the same checker as admission."""
    first = 0
    obstruction = next(i for i, row in enumerate(certificate['records']) if not row['feasible'])
    degenerate = next(i for i, row in enumerate(certificate['records'])
                      if row['feasible'] and row['radical_dimension'] > 0)
    cases = [
        ('missing_singleton_source', lambda c: c['records'].pop(first), 'record inventory and sorted order'),
        ('duplicated_node', lambda c: c['records'][1].__setitem__('node', c['records'][0]['node']),
         'record inventory and sorted order'),
        ('changed_source_span', lambda c: c['records'][first]['source_basis'].__setitem__(0, 6), 'source span at node 1'),
        ('changed_target_span', lambda c: c['records'][first]['target_basis'].pop(), 'target span at node 1'),
        ('false_feasibility', lambda c: c['records'][obstruction].__setitem__('feasible', True),
         'feasibility label at node ' + str(certificate['records'][obstruction]['node'])),
        ('zero_common_vector', lambda c: c['records'][obstruction].__setitem__('common_vector', 0),
         'common-vector obstruction at node ' + str(certificate['records'][obstruction]['node'])),
        ('understated_radical', lambda c: c['records'][degenerate].__setitem__('radical_dimension', 0),
         'source radical dimension at node ' + str(certificate['records'][degenerate]['node'])),
        ('uncompleted_degenerate_frame', lambda c: c['records'][degenerate].__setitem__('frame_basis',
             list(c['records'][degenerate]['source_basis'])),
         'degenerate frame at node ' + str(certificate['records'][degenerate]['node'])),
        ('frame_crosses_target', lambda c: c['records'][first].__setitem__('frame_basis', [7, 1]),
         'frame/target orthogonality at node 1'),
        ('changed_dag_digest', lambda c: c.__setitem__('dag_sha256', '0' * 64), 'canonical DAG digest'),
        ('changed_base_commit', lambda c: c.__setitem__('base_commit', '0' * 40), 'exact experiment base commit'),
        ('changed_source_pin', lambda c: c['source_sha256'].__setitem__('scripts/certify.py', '0' * 64),
         'source pin mismatch: scripts/certify.py'),
        ('changed_summary', lambda c: c['summary'].__setitem__('feasible_nodes', -1), 'exact recomputed summary'),
    ]
    rejected = []
    for name, mutate, expected in cases:
        bad = copy.deepcopy(certificate)
        mutate(bad)
        try:
            check_certificate(bad, context)
        except ValueError as error:
            require(str(error) == expected, 'unexpected control failure: ' + name + ': ' + str(error))
            rejected.append(dict(name=name, reason=str(error)))
        else:
            raise ValueError('accepted certificate mutation: ' + name)
    # The zero source has a zero-dimensional optimum. A larger nondegenerate
    # frame must fail even though containment and orthogonality still hold.
    too_large = dict(node=0, source_basis=[], target_basis=[], radical_dimension=0,
                     feasible=True, frame_basis=[1], common_vector=None)
    try:
        check_record(too_large, frozenset({0}), frozenset({0}), 1)
    except ValueError as error:
        require(str(error) == 'minimum frame dimension at node 0', 'minimum-dimension control reason')
        rejected.append(dict(name='nonminimal_nondegenerate_frame', reason=str(error)))
    else:
        raise ValueError('accepted nonminimal frame')
    # Disjointness alone does not imply the theorem's orthogonality premise.
    nonorthogonal = dict(node=0, source_basis=[1], target_basis=[3], radical_dimension=0,
                         feasible=True, frame_basis=[1], common_vector=None)
    try:
        check_record(nonorthogonal, frozenset({0, 1}), frozenset({0, 3}), 2)
    except ValueError as error:
        require(str(error) == 'source/target orthogonality at node 0', 'orthogonality control reason')
        rejected.append(dict(name='disjoint_but_nonorthogonal_spans', reason=str(error)))
    else:
        raise ValueError('accepted disjoint but nonorthogonal spans')
    return rejected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--certificate', type=Path, default=HERE / 'CERTIFICATE.json')
    parser.add_argument('--out', type=Path)
    parser.add_argument('--controls-only', action='store_true', help='run tiny-space and PR920 checks only')
    args = parser.parse_args()
    if args.out:
        require(not args.out.exists(), 'output must be new')
    receipt = dict(format=1, exhaustive_small_spaces=exhaustive_small_spaces(),
                   pr920_negative_control=pr920_negative_control())
    if args.controls_only:
        receipt['status'] = 'PASS_EXHAUSTIVE_SMALL_SPACE_AND_RESIDUAL_SCOPE_CONTROLS'
    else:
        certificate = json.loads(args.certificate.read_bytes())
        source_pins(certificate)
        context = graph_context()
        receipt.update(status='PASS_INDEPENDENT_SEED47_LOCAL_FRAME_COMPLETIONS',
                       certificate_sha256=filehash(args.certificate),
                       certificate_content_sha256=digest(certificate),
                       dag_sha256=context['dag_sha256'], summary=check_certificate(certificate, context),
                       controls_rejected=certificate_controls(certificate, context))
        source_pins(certificate)
        require(filehash(args.certificate) == receipt['certificate_sha256'], 'certificate changed during check')
    receipt.update(checker_sha256=filehash(Path(__file__).resolve()),
                   scope='Local nondegenerate completion geometry and exhaustive h<=4 evidence only. '
                         'No nested-edge, residual-decoder, circuit-cost, recurrence, or multiplication-exponent admission.')
    text = json.dumps(receipt, indent=2) + '\n'
    if args.out:
        args.out.write_text(text)
    else:
        print(text, end='')


if __name__ == '__main__':
    main()
