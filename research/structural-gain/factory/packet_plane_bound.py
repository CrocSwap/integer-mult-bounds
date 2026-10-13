#!/usr/bin/env python3
"""Exact packet-plane bottleneck and cross-block output-borrowing screen.

Prepared by Dominik Scholz with OpenAI Codex (GPT-6 Astra) assistance.
Reads the icekylinx PR531 packet modules, whose source credits are retained
in direct-delivery504-global. This is a necessary-condition screen, not a
replacement scalar word or a new exponent certificate.
"""

import argparse
from collections import Counter, defaultdict
from fractions import Fraction as Q
import gzip
import hashlib
import itertools
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def basis(vectors):
    rows = {}
    for vector in vectors:
        for pivot in sorted(rows, reverse=True):
            if vector >> pivot & 1:
                vector ^= rows[pivot]
        if vector:
            pivot = vector.bit_length() - 1
            for other in rows:
                if rows[other] >> pivot & 1:
                    rows[other] ^= vector
            rows[pivot] = vector
    return tuple(rows[pivot] for pivot in sorted(rows, reverse=True))


def inside(left, right):
    return basis(left + right) == right


def space(rows):
    values = {0}
    for row in rows:
        values |= {value ^ row for value in list(values)}
    return values


def kernel(normals):
    return basis(x for x in range(1, 512)
                 if all((x & normal).bit_count() % 2 == 0 for normal in normals))


def matching(edges):
    """Integral bipartite matching, with its explicit matched-edge witness."""
    owner = {}

    def augment(left, seen):
        for right in edges[left]:
            if right in seen:
                continue
            seen.add(right)
            if right not in owner or augment(owner[right], seen):
                owner[right] = left
                return True
        return False

    for left in sorted(edges):
        augment(left, set())
    return {left: right for right, left in owner.items()}


def span_remainder(wanted, donors, ids):
    """Return the exact remainder after elimination by the donor row span."""
    pivots = {}
    for row in donors:
        vector = [row.get(source, Q(0)) for source in ids]
        for pivot, previous in sorted(pivots.items()):
            if vector[pivot]:
                coefficient = vector[pivot]
                vector = [x - coefficient*y for x, y in zip(vector, previous)]
        pivot = next((i for i, value in enumerate(vector) if value), None)
        if pivot is not None:
            coefficient = vector[pivot]
            pivots[pivot] = [value/coefficient for value in vector]
    vector = [wanted.get(source, Q(0)) for source in ids]
    for pivot, previous in sorted(pivots.items()):
        if vector[pivot]:
            coefficient = vector[pivot]
            vector = [x-coefficient*y for x, y in zip(vector, previous)]
    return vector


def first_alias_attempt(module, cap):
    """Emit and execute the smallest suggested partial-butterfly cleanup."""
    ids = module['receipt']['source_lines']
    rows = [{str(source): Q(1)} for source in ids] + [{} for _ in range(16)]
    rows[17] = {'initial_output_28': Q(1)}
    frames = list(map(tuple, module['start_frames']))

    def add(target, donor, coefficient):
        for symbol, value in rows[donor].copy().items():
            rows[target][symbol] = rows[target].get(symbol, Q(0)) + coefficient*value
            if not rows[target][symbol]:
                del rows[target][symbol]

    for event, frame in zip(module['events'][:40], module['event_frames'][:40]):
        target, donor, numerator, denominator = event
        add(target, donor, Q(numerator, denominator))
        frames[target] = frames[donor] = tuple(frame)
    before = {str(register): {symbol: str(value) for symbol, value in rows[register].items()}
              for register in (17, 23)}
    require(inside(basis(frames[17] + frames[23]), cap), 'first inverse butterfly exceeds output cap')
    add(23, 17, Q(1, 2))
    require(rows[23] == {'71': Q(1)}, 'partial butterfly did not restore source 71')
    add(17, 23, Q(-1))
    require(rows[17] == {'initial_output_28': Q(1), '68': Q(1)}, 'unexpected residual on borrowed output')
    blocked_source_branches = []
    for register in (4, 16):
        joined = basis(frames[17] + frames[register])
        require(not inside(joined, cap), 'an existing source-68 branch unexpectedly fits')
        blocked_source_branches.append(dict(register=register, frame=list(frames[register]),
                                            joined_frame=list(joined), output_cap_contains_join=False,
                                            row={symbol: str(value) for symbol, value in rows[register].items()}))
    return dict(status='PARTIAL_BUTTERFLY_EXECUTES_BUT_BORROWED_OUTPUT_IS_NOT_RESTORED',
                block=[0, 1, 2, 3], alias=dict(factory_module_helper=17, pre_restriction_output_port=28,
                                            physical_output_register=148),
                cut='after first forty packet-module operations; before any center changes',
                output_cap=list(cap), before=before,
                attempted_cleanup=[dict(target=23, donor=17, coefficient='1/2'),
                                   dict(target=17, donor=23, coefficient='-1')],
                after={str(register): {symbol: str(value) for symbol, value in rows[register].items()}
                       for register in (17, 23)},
                residual_source='68', blocked_existing_source_branches=blocked_source_branches,
                next_required_action='Cancel source 68 while retaining its other factory branches. '
                                     'Its untouched line could do this if copied before those branches grow, '
                                     'but that allocates a replacement helper and cancels the raw one-helper saving.',
                scope='Literal partial inverse executed over exact rational clean sources plus arbitrary initial borrowed-output column. '
                      'This is deliberately earlier and more permissive than the actual late factory cut. '
                      'It is a failed local alias attempt, not a complete dirty-word verifier or a universal borrowing impossibility.')


def inspect(source):
    paths = [source / 'PROTOTYPE.json', source / 'PACKET-PROGRAMS.json.gz']
    prototype = json.loads(paths[0].read_bytes())
    modules = json.loads(gzip.decompress(paths[1].read_bytes()))
    ports, roots = prototype['binary_ports'], prototype['root_lines']
    coordinate_ports = {
        next(i for i, x in enumerate(row) if x): ports[s]
        for s, row in enumerate(roots) if sum(x != 0 for x in row) == 1
    }
    require(len(coordinate_ports) == 8, 'eight coordinate centers required')

    # The existing selected two-output basis is explicit in the construction.
    # Each output coordinate must remain in BOTH final target hyperplanes,
    # and in every center frame contributing to that coordinate before K.
    output_caps = {}
    own_frames = {}
    selected_by_block = {}
    for module in modules:
        coords = tuple(module['receipt']['block'])
        ids = module['receipt']['source_lines']
        i, j, k, _ = coords
        selected_pairs = []
        for parity in (0, 1):
            tetrahedron = [s for s in ids if sum(roots[s][a] < 0 for a in coords) % 2 == parity]
            groups = defaultdict(list)
            for target in tetrahedron:
                groups[roots[target][i] * roots[target][j]].append(target)
            for targets in groups.values():
                t, u = sorted(targets)
                z = -Q(2 * roots[u][i], roots[t][i])
                left, right = [Q(x, 4) for x in roots[t]], [Q(x, 4) for x in roots[u]]
                selected_pairs.append((t, u))
                for target, coefficients in (
                    (t, [a / 2 - b / z for a, b in zip(left, right)]),
                    (u, [a / 2 + b / z for a, b in zip(left, right)]),
                ):
                    normals = [ports[t], ports[u]] + [
                        coordinate_ports[a] for a, q in enumerate(coefficients) if q
                    ]
                    output_caps[target] = kernel(normals)
        selected_by_block[coords] = selected_pairs

    all_packets = []
    late_candidates = []
    block_reports = []
    restoration_checks = []
    all_source_ports = set(ports[8:])
    for block_index, module in enumerate(sorted(modules, key=lambda m: m['receipt']['block'])):
        coords = tuple(module['receipt']['block'])
        ids = module['receipt']['source_lines']
        rows = [{s: Q(1)} for s in ids] + [{} for _ in range(16)]
        frames = [(ports[s],) for s in ids] + [()] * 16
        protected = set()
        partial_snapshot = None
        for event_index, (event, frame) in enumerate(zip(module['events'], module['event_frames'])):
            target, donor, numerator, denominator = event
            frame = tuple(frame)
            require(inside(frames[target], frame) and inside(frames[donor], frame), 'nonmonotone module')
            frames[target] = frames[donor] = frame
            for source_id, value in rows[donor].copy().items():
                rows[target][source_id] = rows[target].get(source_id, Q(0)) + Q(numerator, denominator) * value
                if not rows[target][source_id]:
                    del rows[target][source_id]
            if event_index != 39:
                continue
            # Recover exactly the protected rank-two own-output rows.
            for t, u in selected_by_block[coords]:
                i = coords[0]
                z = -Q(2 * roots[u][i], roots[t][i])
                parity = sum(roots[t][a] < 0 for a in coords) % 2
                opposite = [s for s in ids if sum(roots[s][a] < 0 for a in coords) % 2 != parity]
                for target_id, sign in ((t, -1), (u, 1)):
                    wanted = {}
                    for source_id in opposite:
                        gt = sum(a*b for a,b in zip(roots[t], roots[source_id])) // 2
                        gu = sum(a*b for a,b in zip(roots[u], roots[source_id])) // 2
                        value = -Q(gt, 4) - sign * Q(gu, 2) / z
                        if value:
                            wanted[source_id] = value
                    matches = []
                    for register, row in enumerate(rows):
                        if set(row) != set(wanted):
                            continue
                        source_id = next(iter(wanted))
                        scale = wanted[source_id] / row[source_id]
                        if all(wanted[s] == scale * row[s] for s in wanted):
                            matches.append(register)
                    require(len(matches) == 1, 'own-output row is not unique')
                    protected.add(matches[0])
                    own_frames[target_id] = frames[matches[0]]
            require(len(protected) == 8, 'eight protected rows required')
            partial_snapshot = ([row.copy() for row in rows], frames.copy())

        planes = []
        packet_keys = [(pair, sign) for pair in itertools.combinations(coords, 2) for sign in (-1, 1)]
        for packet_index, ((pair, sign), (register, scale)) in enumerate(zip(packet_keys, module['outputs'])):
            row = {s: Q(scale) * q for s, q in rows[register].items()}
            expected = {s: Q(roots[s][pair[0]]) for s in ids
                        if roots[s][pair[0]] * roots[s][pair[1]] == sign}
            require(row == expected, 'packet identity mismatch')
            frame = basis(ports[s] for s in row)
            require(len(frame) == 3 and frames[register] == frame, 'packet does not occupy its exact rank-three plane')
            require(len(row) == 4, 'packet must have four nonzero source coefficients')
            require(space(frame) & all_source_ports == {ports[s] for s in row}, 'unexpected foreign port in packet plane')
            require(not any(inside(frame, kernel([ports[t]])) for t in ids), 'a local output unexpectedly fits a packet plane')
            # All proper two-dimensional subspaces contain at most two ports.
            proper = {basis(pair) for pair in itertools.combinations(space(frame) - {0}, 2)}
            require(all(len(space(subspace) & all_source_ports) <= 2 for subspace in proper), 'proper plane contains too many source ports')
            allowed = [t for t, cap in sorted(output_caps.items()) if inside(frame, cap)]
            record = dict(block=list(coords), packet=packet_index, coordinate_pair=list(pair), sign=sign,
                          frame=list(frame), source_ids=sorted(row), compatible_external_outputs=allowed)
            all_packets.append(record)
            planes.append(frame)
        require(len(set(planes)) == 12, 'packet planes are not pairwise distinct')

        late = []
        for event_index, (event, frame) in enumerate(zip(module['events'][40:], module['event_frames'][40:])):
            target, donor, _, _ = event
            if not ({target, donor} & protected):
                continue
            frame = tuple(frame)
            allowed = [t for t, cap in sorted(output_caps.items()) if inside(frame, cap)]
            require(donor in protected, 'late donor is not protected')
            candidate = dict(id=len(late_candidates), block=list(coords), retired_module_register=donor,
                             is_helper=donor >= 8, frame=list(frame), compatible_external_outputs=allowed)
            late_candidates.append(candidate)
            late.append(candidate['id'])
            if donor < 8:
                continue
            for output in allowed:
                cap = output_caps[output]
                for cut_name, (cut_rows, cut_frames) in (
                    ('first_forty_operations', partial_snapshot),
                    ('all_face_assemblies_before_center_changes', (rows, frames)),
                ):
                    available = [r for r, frame in enumerate(cut_frames)
                                 if r != donor and inside(frame, cap)]
                    remainder = span_remainder(cut_rows[donor], [cut_rows[r] for r in available], ids)
                    restoration_checks.append(dict(candidate=candidate['id'], output=output, cut=cut_name,
                                                   available_registers=available,
                                                   clean_restore_in_other_row_span=not any(remainder),
                                                   exact_remainder=[str(q) for q in remainder]))
        require(len(late) == 4, 'four late retired carriers required')
        block_reports.append(dict(block=list(coords), distinct_rank_three_packet_planes=12,
                                  one_copy_minimum_registers=24, two_copy_minimum_registers=36,
                                  borrowed_sources=8, one_copy_minimum_helpers=16,
                                  two_copy_minimum_helpers=28, late_retired_candidate_ids=late))

    require(len({tuple(packet['frame']) for packet in all_packets}) == 168,
            'distinct block packet planes unexpectedly coincide')
    for target, frame in own_frames.items():
        require(inside(frame, output_caps[target]), 'inherited own row exceeds selected-output cap')
    edges = {row['id']: row['compatible_external_outputs'] for row in late_candidates}
    assignment = matching(edges)
    helper_assignment = matching({row['id']: row['compatible_external_outputs']
                                  for row in late_candidates if row['is_helper']})
    require(len(set(assignment.values())) == len(assignment), 'output borrowing witness repeats an output')
    for candidate, target in assignment.items():
        require(target in edges[candidate], 'output borrowing witness contains an invalid edge')
    return dict(
        status='PASS_EXACT_PACKET_PLANE_BOUND_AND_NECESSARY_OUTPUT_BORROWING_SCREEN',
        input_sha256={path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths},
        blocks=block_reports, packet_planes=all_packets,
        minimum_factory_helpers=224,
        minimum_factory_and_second_face_copy_helpers=392,
        local_output_borrowing_compatible_pairs=0,
        external_output_compatibility_histogram=dict(sorted(Counter(len(row['compatible_external_outputs']) for row in all_packets).items())),
        late_retired_carriers=late_candidates,
        late_retired_matching={str(k): v for k, v in sorted(assignment.items())},
        matched_late_retired_carriers=len(assignment),
        late_retired_actual_helpers=sum(row['is_helper'] for row in late_candidates),
        matched_late_retired_actual_helpers=len(helper_assignment),
        helper_only_matching={str(k): v for k, v in sorted(helper_assignment.items())},
        restoration_checks=restoration_checks,
        restoration_checks_passed=sum(row['clean_restore_in_other_row_span'] for row in restoration_checks),
        restoration_checks_total=len(restoration_checks),
        first_alias_attempt=first_alias_attempt(next(module for module in modules
                                                   if module['receipt']['block'] == [0, 1, 2, 3]), output_caps[28]),
        restoration_scope='Tests whether the borrowed helper clean row can be canceled by adding any linear combination of the other existing register rows whose current frames lie in the selected output cap, at two specified cuts. Extra clean packet copies add duplicate row vectors and cannot enlarge the span. All donor rows are left unchanged. Failure also rejects partial-butterfly cleanup expressed by such row additions. Fresh computation, changes to the other packet rows, a different initial packet circuit, and nonmonotone visits remain open.',
        matching_scope='A simultaneous necessary geometric assignment only. No arbitrary-dirt cleanup, emitted word, phase lowering, new profile, or kappa is supplied.',
        lower_bound_scope='Fixed twelve normalized face packets per Hamming block, exact packet planes, nested scalar register frames, two-register additions and nonzero scales; source inputs may be borrowed. No output registers or outside auxiliary registers are granted for free. Alternative packet decompositions and nonmonotone frame schedules are excluded.',
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True, help='PR531 inputs/hamming directory')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    result = inspect(args.source)
    args.out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: value for key, value in result.items()
                      if key not in ('blocks', 'packet_planes', 'late_retired_carriers', 'late_retired_matching',
                                     'helper_only_matching', 'restoration_checks', 'first_alias_attempt')}, indent=2))


if __name__ == '__main__':
    main()
