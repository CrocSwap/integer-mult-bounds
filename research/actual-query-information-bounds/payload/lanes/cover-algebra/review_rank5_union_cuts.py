"""Review the twelve rank-five query spaces and their unit-weight cuts."""

from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import gzip
import json


HERE = Path(__file__).resolve().parent
LANES = HERE.parent
SNAPSHOT_PIN = '3dd1d7388c7d3bca104a21e642b5fcafe175d83a2f1dfce1a3ee3e86b864276c'
INTERFACE_PIN = '5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3'
CERTIFICATE_PIN = 'caf4ea536cc79ec7cd585b9f3d4714efc86874785cf463dc215d0158caff5607'
PROOF_PIN = 'd85d71839a600f7d8d0cb511530ca2d1169f0efa543f8c342d2b2cbfe9396629'
EXPECTED = {630, 631, 632, 633, 635, 637, 734, 735, 736, 737, 739, 741}


def require(value, message):
    if not value:
        raise ValueError(message)


def add(row, other, factor):
    for j, value in other.items():
        new = row.get(j, 0) + factor * value
        if new:
            row[j] = new
        else:
            row.pop(j, None)


class Span:
    def __init__(self):
        self.rows = {}

    def reduce(self, row):
        row = dict(row)
        for pivot, old in sorted(self.rows.items()):
            if pivot in row:
                add(row, old, -row[pivot])
        return row

    def insert(self, row):
        row = self.reduce(row)
        if row:
            pivot = min(row)
            value = row[pivot]
            self.rows[pivot] = {j: x / value for j, x in row.items()}


def bitspan(basis):
    values = {0}
    for v in basis:
        values |= {x ^ v for x in tuple(values)}
    return values


def rank(rows):
    span = Span()
    for row in rows:
        span.insert(row)
    return len(span.rows)


def main():
    raw = gzip.decompress((LANES / 'history-encoding/BACKWARD-SNAPSHOT-INTERVALS.json.gz').read_bytes())
    require(sha256(raw).hexdigest() == SNAPSHOT_PIN, 'Snapshot pin')
    source = json.loads(raw)
    interface_raw = (LANES / 'circuit-interface/INTERFACE.json').read_bytes()
    require(sha256(interface_raw).hexdigest() == INTERFACE_PIN, 'Interface pin')
    labels = json.loads(interface_raw)['ports']
    certificate_raw = (LANES / 'history-encoding/RANK5-UNION-CUTS.json').read_bytes()
    require(sha256(certificate_raw).hexdigest() == CERTIFICATE_PIN, 'Certificate pin')
    proof_raw = (LANES / 'history-encoding/LOW-BIRTH-UNION-CUTS.md').read_bytes()
    require(sha256(proof_raw).hexdigest() == PROOF_PIN, 'Reviewed proof pin')
    certificate = json.loads(certificate_raw)
    cases = certificate['merges']
    require({case['merge_frame'] for case in cases} == EXPECTED and len(cases) == 12, 'Twelve distinct cases')
    frames = source['frames']
    spaces = [bitspan(U) for U in frames]
    final = [{int(j): F(x) for j, x in row.items()} for row in source['final_rows']]
    R = [{int(j): F(x) for j, x in row.items()} for row in source['R']]
    for p in range(112):
        expected = {p: F(1)}
        for q in range(112):
            value = sum(row.get(p, 0) * row.get(q, 0) for row in R) / 4 - (p == q)
            if value:
                expected[112 + q] = value
        require(final[p] == expected, 'A complete X row differs')
    helpers = {j for j in range(224, 704) if source['final_frames'][j] == 1}
    require(len(helpers) == 402 and all(final[j] == {j: F(1)} for j in helpers), 'The free helper baselines differ')
    by_frame = {}
    for _, _, _, frame, rowid in source['intervals']:
        by_frame.setdefault(frame, set()).add(rowid)
    reduced = {}
    reports = []
    for case in cases:
        merge = case['merge_frame']
        require(len(frames[merge]) == 5, 'Merge dimension')
        nodes = sorted(u for u in by_frame if frames[u] and spaces[u] <= spaces[merge])
        edges = {(u, v) for u in nodes for v in nodes if spaces[u] < spaces[v]}
        require(edges == {tuple(edge) for edge in case['edges']}, 'The complete actual edge set differs')
        targets = []
        for coefficients in case['query_coefficients']:
            row = {}
            for i, value in coefficients.items():
                add(row, R[int(i)], F(value))
            targets.append(row)
        require(len(targets) == rank(targets) == 5, 'Independent target rows')
        observations = Span()
        support_tests = 0
        for u in nodes:
            allowed = {p for p, q in enumerate(labels) if all((q & v).bit_count() % 2 == 0 for v in frames[u])}
            for rowid in by_frame[u]:
                if rowid not in reduced:
                    row = {int(j): F(x) for j, x in source['rows'][rowid].items()}
                    for j in list(row):
                        if j < 112:
                            add(row, final[j], -row[j])
                    reduced[rowid] = {j: x for j, x in row.items() if j not in helpers}
                row = reduced[rowid]
                require({j - 112 for j in row if 112 <= j < 224} <= allowed, 'An annihilating-input support differs')
                observations.insert(row)
                support_tests += 1
        require(all(not observations.reduce({112 + p: x for p, x in row.items()}) for row in targets), 'A target row is absent')
        residuals = [observations.reduce({112 + p: x for p, x in row.items()}) for row in R]
        require(8 - rank(residuals) == 5, 'Exact maximal query overlap differs')

        positive = [cut for cut in case['cuts'] if F(cut['weight'])]
        require(len(positive) == 5 and all(F(cut['weight']) == 1 for cut in positive), 'Five unit-weight cuts')
        cuts = []
        for cut in positive:
            characters = set(cut['characters'])
            ports = {p for p, q in enumerate(labels)
                     if sum(((q & v).bit_count() % 2) << i for i, v in enumerate(frames[merge])) in characters}
            require(ports == set(cut['source_ports']), 'Source character classes differ')
            inside = {u for u in nodes
                      if all(any((labels[p] & v).bit_count() % 2 for v in frames[u]) for p in ports)}
            stated_inside = set(cut['inside_frames'])
            require(stated_inside <= inside and merge in stated_inside, 'A cut admits a nonzero observation')
            require(all(u not in stated_inside or v in stated_inside for u, v in edges), 'A cut is not upward closed')
            demand = rank([{p: value for p, value in row.items() if p in ports} for row in targets])
            require(demand == cut['demand'] == 5, 'A target restriction is not injective')
            cuts.append(stated_inside)
        charges = []
        for u, v in sorted(edges):
            charge = sum(u not in inside and v in inside for inside in cuts)
            cost = len(frames[v]) - len(frames[u])
            require(charge <= cost, 'A native edge is overcharged')
            charges.append(charge)
        require(F(case['internal_bound']) == 25 and case['completion_bound'] == 20, 'The reported bound differs')
        reports.append({'merge_frame': merge, 'exact_query_overlap': 5,
                        'actual_nodes': len(nodes), 'actual_edges': len(edges),
                        'support_tests': support_tests, 'positive_cuts': 5,
                        'every_positive_cut_rank': 5, 'internal_bound_per_query': 5,
                        'completion_bound_per_query': 4, 'total_bound_per_query': 9,
                        'edge_charge_histogram': {str(c): charges.count(c) for c in sorted(set(charges))}})
    report = {
        'status': 'PASS_INDEPENDENT_RANK5_UNION_CUT_REVIEW',
        'checker_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
        'snapshot_decompressed_sha256': SNAPSHOT_PIN,
        'interface_sha256': INTERFACE_PIN,
        'reviewed_certificate_sha256': sha256(certificate_raw).hexdigest(),
        'reviewed_proof_sha256': PROOF_PIN,
        'cases': reports,
        'scope': 'Every subspace of the exact maximal five-query space at each of the twelve listed rank-five frames costs at least nine rank units per query in the actual positive-frame common-merge network. Same-content monotone transport and no new observations after the merge are required. All source times are granted.',
        'not_checked': ['Other merge frames and the other displayed-space certificates in the proof', 'Synthetic intermediate frames', 'Cross-merge sharing',
                        'Chronological native recipes', 'A global64 bound', 'Supplier pricing'],
    }
    (HERE / 'RANK5-UNION-CUTS-REVIEW.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(report['status'])
    print('Twelve exact five-query overlaps; five injective unit-weight cuts each; lower cost9k.')


if __name__ == '__main__':
    main()
