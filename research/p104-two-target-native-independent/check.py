"""Independent finite forward binding; no compiler or PR2445 producer imports.

The retained p104-native-channel/check_native.py is explicitly reused to audit
the inherited channel. Its vendor/native_verify.py supplies the independent
signed-Pauli/exact-Gaussian interpreter. Everything concerning the new literal
insertions, occurrence coverage, common charts and 358-column composition is
checked here. File provenance is authenticated separately by replay/the wrapper.
"""
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
import copy
import gzip
import hashlib
import json

H = Path(__file__).resolve().parent
_loader_path = H / 'source_exec.py'
_loader = {'__file__': str(_loader_path)}
exec(compile(_loader_path.read_bytes(), str(_loader_path), 'exec'), _loader)
INPUTS = _loader['authenticated_inputs'](H)
BASE = _loader['retained_checker'](INPUTS)
N = BASE.N


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def binary_span(vectors):
    values = {0}
    for vector in vectors:
        need(type(vector) is int and 0 < vector < 512, 'nine-bit nonzero frame vector')
        values |= {value ^ vector for value in tuple(values)}
    need(len(values) == 2 ** len(vectors), 'independent literal frame basis')
    return frozenset(values)


def canonical(vectors):
    """Independent RREF by exhaustive coset minima, not compiler elimination.

    In a binary subspace the minimum element at each occurring highest bit is
    its reduced pivot row. The space has at most 512 elements.
    """
    minima = {}
    for value in binary_span(vectors) - {0}:
        pivot = value.bit_length() - 1
        minima[pivot] = min(value, minima.get(pivot, value))
    return tuple(minima[pivot] for pivot in sorted(minima, reverse=True))


@lru_cache(maxsize=1)
def inherited():
    """Reuse the independently written retained checker, with attribution."""
    raw = INPUTS['research/p104-native-channel/inputs/LOWRANK-WITNESS.json']
    witness = json.loads(raw)
    native = json.loads(gzip.decompress(INPUTS['research/p104-native-channel/NATIVE-RECIPES.json.gz']))
    fixture = json.loads(INPUTS['research/p104-native-channel/inputs/P104-FIXTURE.json'])['section4_explicit_P104']
    need(hashlib.sha256(raw).hexdigest() == native['source_witness_sha256'], 'inherited witness pin')
    need(hashlib.sha256(INPUTS['research/p104-native-channel/vendor/native_verify.py']).hexdigest()
         == native['source_native_checker_sha256'], 'inherited independent interpreter pin')
    result = BASE.validate(native, witness, fixture, False)
    return native, witness, fixture, result


def physical_conversion(isometry):
    dual = isometry['compressed_dual_gram']
    orthogonal = isometry['orthonormal_basis_compressed']
    dual_images = [sum(((row & vector).bit_count() % 2) << i
                       for i, row in enumerate(dual)) for vector in orthogonal]

    def convert(vector):
        return sum(((vector & dual).bit_count() % 2) << i
                   for i, dual in enumerate(dual_images))

    def frame(vectors):
        # Check the supplied compressed basis too, before changing coordinates.
        binary_span(vectors)
        return canonical(tuple(convert(vector) for vector in vectors))

    return frame


def recipe_domain(recipe):
    need(type(recipe['rank']) is int and 0 < recipe['rank'] <= 9, 'positive recipe rank')
    for side in ('left', 'right'):
        monomial = recipe[side]
        for field in ('matrix_rows', 'quadratic_rows'):
            rows = monomial[field]
            need(len(rows) == 9 and all(type(v) is int and 0 <= v < 512 for v in rows),
                 'native monomial nine-bit domain')
        need(len(monomial['linear_Z4']) == 9
             and all(type(v) is int and 0 <= v < 4 for v in monomial['linear_Z4']),
             'native linear phase domain')
        need(type(monomial['offset']) is int and 0 <= monomial['offset'] < 512,
             'native offset domain')
        need(type(monomial['phase']) is int and 0 <= monomial['phase'] < 4,
             'native global phase domain')


def bind_edges(certificate, circuit, native, witness, frame):
    """Bind actual chart representatives, not merely their binary spans."""
    charts = {}

    def remember(vectors):
        vectors = tuple(vectors)
        key = binary_span(vectors)
        need(canonical(vectors) == vectors, 'canonical physical chart representative')
        if key in charts:
            need(charts[key] == vectors, 'inherited physical chart alignment')
        charts[key] = vectors
        return vectors

    inherited_occurrences, inherited_edges = {}, set()
    for edge in native['transports']:
        old, new = remember(edge['old']), remember(edge['new'])
        inherited_edges.add((old, new))
        for index in edge['events']:
            need(index not in inherited_occurrences, 'inherited unique occurrence')
            inherited_occurrences[index] = (old, new, edge['rank'])
    for adapter in native['endpoint_adapters']:
        remember(adapter['frame'])
    for index, event in enumerate(witness['program']):
        if event[0] == 'transport':
            need(inherited_occurrences.get(index) == (frame(event[2]), frame(event[3]), event[4]),
                 'inherited literal edge binding')
    need(set(inherited_occurrences) == {i for i, e in enumerate(witness['program'])
                                      if e[0] == 'transport'}, 'inherited occurrence coverage')

    covered, edges, paid = {}, set(), Counter()
    for edge in certificate['transports']:
        old, new = remember(edge['old']), remember(edge['new'])
        need((old, new) not in edges, 'added unique directed edge')
        edges.add((old, new))
        a, b = binary_span(old), binary_span(new)
        need(a <= b or b <= a, 'added nested physical frames')
        rank = abs(len(old) - len(new))
        need(type(edge['rank']) is int and edge['rank'] == rank and rank > 0, 'added rank')
        for orientation, start, end in (('forward', old, new), ('adjoint', new, old)):
            recipe = edge[orientation]
            recipe_domain(recipe)
            need(recipe['rank'] == rank, 'added recipe rank ' + orientation)
            expected = N.adjoint(N.frame(start, 9)) + N.frame(end, 9)
            N.equal(N.recipe(recipe), expected, 'added ' + orientation + ' edge')
        need(bool(edge['occurrences']), 'added nonempty occurrence list')
        for occurrence in edge['occurrences']:
            need(len(occurrence) == 2 and all(type(v) is int for v in occurrence),
                 'added occurrence address')
            insertion, index = occurrence
            need(0 <= insertion < len(circuit['insertions'])
                 and 0 <= index < len(circuit['insertions'][insertion]['events']),
                 'added occurrence range')
            key = (insertion, index)
            need(key not in covered, 'added duplicate occurrence')
            event = circuit['insertions'][insertion]['events'][index]
            need(event[0] == 'transport' and old == frame(event[2]) and new == frame(event[3])
                 and event[4] == rank, 'added literal physical edge binding')
            covered[key] = (old, new, rank)
            paid[rank] += 1
    expected = {(i, j) for i, insertion in enumerate(circuit['insertions'])
                for j, event in enumerate(insertion['events']) if event[0] == 'transport'}
    need(set(covered) == expected, 'added occurrence coverage')
    need(dict(sorted(paid.items())) == {int(k): v for k, v in certificate['added_profile'].items()},
         'added complete paid profile')
    need(sum(k * v for k, v in paid.items()) == certificate['added_rank_mass'] == 702,
         'added complete rank mass')
    return paid, len(edges), len(charts), len(edges & inherited_edges), len(edges - inherited_edges)


def replay_rows(circuit, witness, fixture, frame):
    initial = dict(witness['initial_frames'])
    need(not (set(initial) & set(circuit['initial_frames'])), 'fresh dirty helper names')
    initial.update(circuit['initial_frames'])
    names = sorted(initial)
    need(len(names) == 358 and len(circuit['initial_frames']) == 78, 'complete arbitrary-input inventory')
    need(circuit['targets'] == [0, 1], 'fixed corrected targets')
    need([entry['completed_cut'] for entry in circuit['insertions']] == [0, len(witness['program'])]
         and len(witness['program']) == 4058, 'fixed insertion cuts')
    final = dict(witness['final_frames'])
    final.update(circuit['final_frames'])
    need(set(final) == set(names), 'complete final frame inventory')
    rows = {name: {name: Fraction(1)} for name in names}
    frames = {name: frame(value) for name, value in initial.items()}
    events = (circuit['insertions'][0]['events'] + witness['program']
              + circuit['insertions'][1]['events'])
    counts, lifetimes = Counter(), []
    private_copy_source = None
    for event in events:
        tag = event[0]
        counts[tag] += 1
        if tag == 'transport':
            _, name, old, new, rank = event
            need(name in frames and frames[name] == frame(old), 'physical transport entry chart')
            need(type(rank) is int and rank == abs(len(new) - len(old)), 'literal transport rank')
            frames[name] = frame(new)
        elif tag == 'add':
            _, target, source, coefficient, common = event
            need(target != source and target in frames and source in frames
                 and frames[target] == frames[source] == frame(common), 'common physical ADD chart')
            coefficient = Fraction(coefficient)
            need(coefficient.denominator & (coefficient.denominator - 1) == 0, 'dyadic ADD coefficient')
            for column, value in rows[source].items():
                result = rows[target].get(column, Fraction(0)) + coefficient * value
                if result:
                    rows[target][column] = result
                else:
                    rows[target].pop(column, None)
        elif tag == 'zero':
            _, name, common = event
            need(name == 'C' and name not in frames and private_copy_source is None,
                 'owned private initialization')
            frames[name], rows[name] = frame(common), {}
        elif tag == 'copy':
            _, name, source, common = event
            need(name == 'C' and source in frames and name in frames and not rows[name]
                 and private_copy_source is None and frames[name] == frames[source] == frame(common),
                 'owned common-chart zero-destination COPY')
            rows[name] = dict(rows[source])
            private_copy_source = source
        elif tag == 'erase':
            _, name, common = event
            need(name == 'C' and name in frames and frames[name] == frame(common)
                 and private_copy_source is not None, 'owned private-copy discard')
            # Inherited COPY contract permits discarding the owned live copy;
            # this is deliberately NOT asserted to be reversible zero cleanup.
            lifetimes.append(private_copy_source)
            del frames[name], rows[name]
            private_copy_source = None
        else:
            raise ValueError('unknown literal event')
    need(set(rows) == set(frames) == set(names) and private_copy_source is None,
         'complete private lifetime closure')
    need(lifetimes == ['Q' + str(i) for i in range(8)], 'eight inherited private-copy lifetimes')

    # The root reconstruction is reused from the independent inherited checker,
    # not read from the side-correction producer or its claimed target matrix.
    removed = {tuple(value) for value in fixture['F0'] + fixture['C']}
    roots = [value for value in BASE.roots() if value not in removed]
    need(len(roots) == 104, 'independent P104 target geometry')
    coefficient_checks = 0
    digest = hashlib.sha256()
    for name in names:
        expected = {name: Fraction(1)}
        if name.startswith('Y'):
            target = int(name[1:])
            if target in (0, 1):
                expected['X' + str(target)] = Fraction(1)
            else:
                for source, vector in enumerate(roots):
                    dot = sum(a * b for a, b in zip(roots[target], vector))
                    need(dot % 4 == 0, 'integral doubled-root Gram entry')
                    if dot:
                        expected['X' + str(source)] = Fraction(dot, 8)
        need(frames[name] == frame(final[name]), 'complete endpoint frame ' + name)
        for column in names:
            actual = rows[name].get(column, Fraction(0))
            wanted = expected.get(column, Fraction(0))
            need(actual == wanted, 'complete endpoint coefficient ' + name + ' <- ' + column)
            coefficient_checks += 1
            digest.update((name + ',' + column + ',' + str(actual) + '\n').encode())
    return dict(arbitrary_logical_inputs=len(names), boundary_coefficient_checks=coefficient_checks,
                boundary_matrix_sha256=digest.hexdigest(), restored_sources=104,
                restored_dirty_helpers=150, identity_corrected_targets=[0, 1],
                remaining_gram_targets=102, scalar_and_transport_events=dict(sorted(counts.items())),
                private_copy_lifetimes=len(lifetimes), final_frames_checked=len(frames))


def validate(certificate, circuit, controls=False, *, witness=None):
    native, frozen_witness, fixture, base_result = inherited()
    if witness is None:
        witness = frozen_witness
    need(certificate['schema_version'] == circuit['schema_version'] == 1, 'schema version')
    need(circuit['source_witness_sha256'] == native['source_witness_sha256'], 'correction witness binding')
    need(certificate['label_isometry'] == native['label_isometry'], 'frozen label isometry')
    frame = physical_conversion(native['label_isometry'])
    paid, edge_count, chart_count, overlap, new_pairs = bind_edges(
        certificate, circuit, native, witness, frame)
    result = replay_rows(circuit, witness, fixture, frame)
    result.update(status='PASS_FINITE_FORWARD_TWO_TARGET_NATIVE_BINDING',
                  added_distinct_edges=edge_count, added_edge_orientations_checked=2 * edge_count,
                  added_transport_occurrences=sum(paid.values()),
                  added_profile={str(k): v for k, v in sorted(paid.items())},
                  added_rank_mass=sum(k * v for k, v in paid.items()),
                  native_pair_overlap_with_baseline=overlap, new_distinct_pairs=new_pairs,
                  aligned_physical_charts=chart_count, inherited_check=base_result,
                  scope='Finite forward framed operator on 358 arbitrary logical input arrays. '
                  'Both added edge adjoints checked; no complete backward COPY program, '
                  'physical prefix precision, global helper ownership, all-size supplier or new kappa.')
    if controls:
        result['controls'] = run_controls(certificate, circuit)
    return result


def reject_control(certificate, circuit, expected_reason, *, witness=None):
    try:
        validate(certificate, circuit, witness=witness)
    except ValueError as error:
        need(expected_reason in str(error), 'control rejected for wrong reason: ' + str(error))
        return expected_reason
    raise ValueError('control unexpectedly accepted: ' + expected_reason)


def run_controls(certificate, circuit):
    """Reject by the named predicate; unexpected acceptance is outside except."""
    results = {}
    for orientation in ('forward', 'adjoint'):
        bad = copy.deepcopy(certificate)
        factor = bad['transports'][0][orientation]['left']
        factor['phase'] = (factor['phase'] + 1) % 4
        results[orientation + '_global_phase'] = reject_control(
            bad, circuit, 'added ' + orientation + ' edge: exact global phase')
    bad = copy.deepcopy(certificate)
    # Choose an edge with multiple uses, so this isolates coverage from emptiness.
    next(edge for edge in bad['transports'] if len(edge['occurrences']) > 1)['occurrences'].pop()
    results['missing_occurrence'] = reject_control(bad, circuit, 'added occurrence coverage')
    bad = copy.deepcopy(certificate)
    bad['transports'][0]['occurrences'].append(bad['transports'][0]['occurrences'][0])
    results['duplicate_occurrence'] = reject_control(bad, circuit, 'added duplicate occurrence')
    bad = copy.deepcopy(certificate)
    bad['transports'][0]['rank'] += 1
    results['wrong_rank'] = reject_control(bad, circuit, 'added rank')
    bad = copy.deepcopy(certificate)
    bad['label_isometry']['physical_root_labels'][0] ^= 1
    results['wrong_physical_label'] = reject_control(bad, circuit, 'frozen label isometry')
    for label, insertion, index in (('missing_added_dirty_compensation', 0, 0),
                                     ('missing_added_capture_cleanup', 1, -1)):
        bad = copy.deepcopy(circuit)
        event = bad['insertions'][insertion]['events'][index]
        need(event[0] == 'add', 'control scalar position')
        event[3] = '0'
        results[label] = reject_control(certificate, bad, 'complete endpoint coefficient')
    for label, index in (('missing_inherited_gather_compensation', 0),
                         ('missing_inherited_query_cleanup', -1)):
        bad = copy.deepcopy(inherited()[1])
        need(bad['program'][index][0] == 'add', 'inherited control scalar position')
        bad['program'][index][3] = '0'
        results[label] = reject_control(certificate, circuit, 'complete endpoint coefficient', witness=bad)
    equivalent = copy.deepcopy(circuit)
    for key in ('initial_frames', 'final_frames'):
        for frame in equivalent[key].values():
            frame.reverse()
    for insertion in equivalent['insertions']:
        for event in insertion['events']:
            indices = (2, 3) if event[0] == 'transport' else (4,)
            for index in indices:
                event[index].reverse()
    validate(certificate, equivalent)
    results['equivalent_literal_frame_basis_order'] = 'accepted'
    equivalent = copy.deepcopy(certificate)
    equivalent['transports'].reverse()
    for edge in equivalent['transports']:
        edge['occurrences'].reverse()
    validate(equivalent, circuit)
    results['equivalent_edge_and_occurrence_order'] = 'accepted'
    return results


def replay(controls=True):
    circuit_raw = INPUTS['inputs/CIRCUIT.json']
    certificate_raw = gzip.decompress((H / 'NATIVE.json.gz').read_bytes())
    certificate, circuit = json.loads(certificate_raw), json.loads(circuit_raw)
    need(certificate['source_circuit_sha256'] == hashlib.sha256(circuit_raw).hexdigest(),
         'frozen literal correction hash')
    result = validate(certificate, circuit, controls)
    result['source_circuit_sha256'] = hashlib.sha256(circuit_raw).hexdigest()
    result['certificate_raw_sha256'] = hashlib.sha256(certificate_raw).hexdigest()
    return result


if __name__ == '__main__':
    print(json.dumps(replay(), sort_keys=True, indent=2))
