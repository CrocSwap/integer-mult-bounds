"""Review the movable rank-eight cuts and their FULL extensions."""

from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import gzip
import json


HERE = Path(__file__).resolve().parent
LANES = HERE.parent
SNAPSHOT_PIN = '3dd1d7388c7d3bca104a21e642b5fcafe175d83a2f1dfce1a3ee3e86b864276c'
INTERFACE_PIN = '5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3'
CERT_PIN = '62c3b26274ef80a75bbc90b680ceeed9ed24fb158fd7db32594995859c875951'
PROOF_PIN = '9e8ebc108a758883e9811798900bbaa7c42ffa90ac960953a7596d3427f50708'


def require(value, message):
    if not value:
        raise ValueError(message)


def span(basis):
    values = {0}
    for v in basis:
        values |= {x ^ v for x in tuple(values)}
    require(len(values) == 1 << len(basis), 'A frame basis is dependent')
    return values


def add(row, other, factor):
    for j, x in other.items():
        value = row.get(j, 0) + factor * x
        if value:
            row[j] = value
        else:
            row.pop(j, None)


def minor(R, ports):
    pivots = {}
    selected = []
    for port in sorted(ports):
        vector = [R[i][port] for i in range(8)]
        for p, row in sorted(pivots.items()):
            value = vector[p]
            vector = [x - value * y for x, y in zip(vector, row)]
        p = next((i for i, x in enumerate(vector) if x), None)
        if p is not None:
            value = vector[p]
            pivots[p] = [x / value for x in vector]
            selected.append(port)
    require(len(selected) == 8, 'A source test does not have rank eight')
    matrix = [[R[i][p] for p in selected] for i in range(8)]
    determinant = F(1)
    for j in range(8):
        p = next(i for i in range(j, 8) if matrix[i][j])
        if p != j:
            matrix[p], matrix[j] = matrix[j], matrix[p]
            determinant = -determinant
        value = matrix[j][j]
        determinant *= value
        matrix[j] = [x / value for x in matrix[j]]
        for i in range(j + 1, 8):
            value = matrix[i][j]
            matrix[i] = [x - value * y for x, y in zip(matrix[i], matrix[j])]
    require(determinant != 0, 'Zero source minor')
    return {'ports': selected, 'determinant': str(determinant)}


def main():
    raw = gzip.decompress((LANES / 'history-encoding/BACKWARD-SNAPSHOT-INTERVALS.json.gz').read_bytes())
    require(sha256(raw).hexdigest() == SNAPSHOT_PIN, 'Snapshot pin')
    data = json.loads(raw)
    interface_raw = (LANES / 'circuit-interface/INTERFACE.json').read_bytes()
    require(sha256(interface_raw).hexdigest() == INTERFACE_PIN, 'Interface pin')
    labels = json.loads(interface_raw)['ports']
    proof_raw = (LANES / 'history-encoding/MOVABLE-RANK8-CUTS.md').read_bytes()
    certificate_raw = (LANES / 'history-encoding/MOVABLE-FULL-RANK-CUTS.json').read_bytes()
    require(sha256(proof_raw).hexdigest() == PROOF_PIN, 'Proof pin')
    require(sha256(certificate_raw).hexdigest() == CERT_PIN, 'Certificate pin')
    certificate = json.loads(certificate_raw)
    require({case['merge_frame'] for case in certificate['merges']} == {983, 991}
            and len(certificate['merges']) == 2, 'The two merge cases differ')
    frames = data['frames']
    spaces = [span(U) for U in frames]
    require(len(frames[1]) == 9, 'FULL frame differs')
    R = [[F(row.get(str(p), 0)) for p in range(112)] for row in data['R']]
    final = [{int(j): F(x) for j, x in row.items()} for row in data['final_rows']]
    for p in range(112):
        expected = {p: F(1)}
        for q in range(112):
            value = sum(row[p] * row[q] for row in R) / 4 - (p == q)
            if value:
                expected[112 + q] = value
        require(final[p] == expected, 'A completed X row differs from X-JY')
    by_frame = {}
    for _, _, _, frame, rowid in data['intervals']:
        by_frame.setdefault(frame, set()).add(rowid)
    reduced = {}

    def observation_support(frame):
        support = set()
        for rowid in by_frame.get(frame, ()):
            if rowid not in reduced:
                row = {int(j): F(x) for j, x in data['rows'][rowid].items()}
                for j in list(row):
                    if j < 112:
                        add(row, final[j], -row[j])
                reduced[rowid] = {j - 112 for j, x in row.items() if 112 <= j < 224 and x}
            support |= reduced[rowid]
        return support

    require(not observation_support(1), 'A FULL snapshot is nonzero on the test family')
    reports = []
    for case in certificate['merges']:
        merge = case['merge_frame']
        require(len(frames[merge]) == 8, 'Merge rank differs')
        nodes = [u for u in range(len(frames)) if spaces[u] <= spaces[merge]]
        require(nodes == case['contained_frames'], 'The complete contained frame set differs')
        edges = [(u, v) for u in nodes for v in nodes if spaces[u] < spaces[v]]
        hasse = {(u, v, len(frames[v]) - len(frames[u])) for u, v in edges
                 if not any(spaces[u] < spaces[w] < spaces[v] for w in nodes)}
        require(hasse == {tuple(edge) for edge in case['hasse_edges']}, 'The Hasse graph differs')
        require(len(edges) == case['all_inclusion_edges_checked'], 'The direct inclusion count differs')
        supports = {}
        for u in nodes:
            allowed = {p for p, q in enumerate(labels)
                       if all((q & v).bit_count() % 2 == 0 for v in frames[u])}
            supports[u] = observation_support(u)
            require(supports[u] <= allowed, 'An actual snapshot violates the support premise')
        minors = []
        tests = []
        for test in case['source_tests']:
            ports = set(test['ports'])
            require(len(ports) == len(test['ports']) and ports <= set(range(112)), 'A source test repeats or exceeds the ports')
            minors.append(minor(R, ports))
            tests.append(ports)
            maximal = {u for u in nodes if all(any((labels[p] & v).bit_count() % 2 for v in frames[u]) for p in ports)}
            require(maximal == set(test['maximal_inside_frames']), 'A maximal support cut differs')
        cuts = []
        require(len(case['cuts']) == 7, 'There must be seven cuts')
        for cut in case['cuts']:
            inside = set(cut['inside_frames'])
            test = tests[cut['test']]
            require(inside <= set(nodes) and merge in inside, 'Cut node scope differs')
            require(all(not supports[u].intersection(test) for u in inside), 'A cut contains a nonzero free observation')
            require(all(u not in inside or v in inside for u, v in edges), 'A cut is not upward closed')
            entered = [i for i, (u, v, _) in enumerate(case['hasse_edges']) if u not in inside and v in inside]
            require(entered == cut['entering_edges'], 'The stated entering edges differ')
            cuts.append(inside)
        charges = [sum(u not in cut and v in cut for cut in cuts) for u, v in edges]
        require(all(charge <= len(frames[v]) - len(frames[u]) for charge, (u, v) in zip(charges, edges)), 'A direct edge is overcharged')
        extended = [cut | {1} for cut in cuts] + [{1}]
        full_edges = edges + [(u, 1) for u in nodes]
        full_charges = [sum(u not in cut and v in cut for cut in extended) for u, v in full_edges]
        require(all(charge <= len(frames[v]) - len(frames[u]) for charge, (u, v) in zip(full_charges, full_edges)), 'The FULL extension overcharges an edge')
        reports.append({'merge_frame': merge, 'contained_frames': len(nodes),
                        'all_internal_edges': len(edges), 'hasse_edges': len(hasse),
                        'source_test_minors': minors, 'internal_cuts': 7,
                        'extended_cuts': 8, 'extended_edges': len(full_edges),
                        'extended_charge_histogram': dict(sorted(Counter(full_charges).items())),
                        'bound_per_query_dimension': 8,
                        'bound_for_all_eight_queries': 64})
    report = {'status': 'PASS_INDEPENDENT_MOVABLE_RANK8_CUTS',
              'checker_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
              'reviewed_proof_sha256': PROOF_PIN, 'reviewed_certificate_sha256': CERT_PIN,
              'snapshot_decompressed_sha256': SNAPSHOT_PIN, 'interface_sha256': INTERFACE_PIN,
              'cases': reports, 'exact_snapshot_rows_reduced': len(reduced),
              'scope': 'At least8k native rank for any k-dimensional centre-query output at FULL when every proper frame is an actual subframe of one chosen V in{983,991}. Branches may bypass V. All snapshot times, frame zero, and arbitrary scalar sharing are granted.',
              'not_checked': ['Cross-cone networks', 'Synthetic intermediate frames', 'A global all-frame bound', 'Chronological native recipes', 'Complete supplier pricing']}
    (HERE / 'MOVABLE-RANK8-CUTS-REVIEW.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(report['status'])
    print('Both contained cones pass all edge charges, including direct completion to FULL; bound8k.')


if __name__ == '__main__':
    main()
