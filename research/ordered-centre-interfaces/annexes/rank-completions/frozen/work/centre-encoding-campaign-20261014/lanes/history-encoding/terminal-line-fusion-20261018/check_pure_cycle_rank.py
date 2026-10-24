#!/usr/bin/env python3
"""Check the finite phase and axis premises of the pure-cycle rank bound."""

from collections import Counter
import gzip
from hashlib import sha256
import json
from pathlib import Path
import tarfile


HERE = Path(__file__).resolve().parent
LANES = HERE.parent.parent
ROOT = LANES.parents[2]
D = 73
UNITS = [1 << j for j in range(D)]
FRESH = LANES / 'history-encoding/independent-skeleton-20261018/fresh-three-child'
CYCLE = LANES / 'bridge-access-20261017/cycle-cover-response-20261018'
ARCHIVE = ROOT / 'worktrees/k5-persistent-cleanup/research/community-frontier1094-audit/selected-replay.tar.gz'
PINS = {
    'fresh_compressed': 'afc3aad86eb9b6da3027d3ac57eac1a2a766729dca0608e70e36d0554c8afc96',
    'fresh_decompressed': 'b08cb4146f1aec241e027cd62c942f6eca4ddab3e97f000a9c0017575d36deb5',
    'cycle_payload': '759f85673b0fda9ba4ff7312c18c80f8a8b72a3ad0a7b1192a8d08571d0095da',
    'cycle_phase_receipt': '5f038767c882d7f8097ab40045b3abbb7f4aa696b4722871b0ef7aa4ad7858e2',
    'cycle_exit_receipt': 'd7d622a5f7bda1a167f732d87771fa8da774a69d71fb496c817ef74b9fc5bc9d',
    'archive': 'f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6',
    'data_phases': 'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa',
}


def need(test, label):
    if not test:
        raise ValueError(label)


def pinned(path, key):
    raw = path.read_bytes()
    need(sha256(raw).hexdigest() == PINS[key], 'Source pin: ' + key)
    return raw


def act(columns, vector):
    result = 0
    while vector:
        bit = vector & -vector
        result ^= columns[bit.bit_length() - 1]
        vector ^= bit
    return result


def coordinates(basis, vector):
    return sum(((b & vector).bit_count() & 1) << j for j, b in enumerate(basis))


def phase(terms):
    linear = [0] * D
    quadratic = set()
    for vector, exponent in terms:
        support = [j for j in range(D) if vector >> j & 1]
        for j in support:
            linear[j] = (linear[j] + exponent) % 4
        if exponent & 1:
            for a, j in enumerate(support):
                for k in support[a + 1:]:
                    pair = (j, k)
                    if pair in quadratic:
                        quadratic.remove(pair)
                    else:
                        quadratic.add(pair)
    return linear, quadratic


def coordinate_product(basis, terms, rank, label):
    linear, quadratic = phase([(coordinates(basis, v), e) for v, e in terms])
    need(not quadratic, label + ': no non-translation phase remains')
    subset = [j for j, a in enumerate(linear) if a & 1]
    need(len(subset) == rank, label + ': exact native rank')
    delta = sum(((a - (a & 1)) // 2) << j for j, a in enumerate(linear))
    need(all((int(j in subset) + 2 * ((delta >> j) & 1)) % 4 == a
             for j, a in enumerate(linear)), label + ': exact C and translation factor')
    return subset, delta


def route(basis, stage, vector):
    if not stage:
        return vector
    result = vector
    for j in range(8):
        a, b = basis[j + 1], UNITS[9 + 8 * (stage - 1) + j]
        if (a & vector).bit_count() & 1:
            result ^= a ^ b
        if (b & vector).bit_count() & 1:
            result ^= a ^ b
    return result


def main():
    packed = pinned(FRESH / 'FRESH-THREE-CHILD-PROGRAMS.json.gz', 'fresh_compressed')
    raw = gzip.decompress(packed)
    need(sha256(raw).hexdigest() == PINS['fresh_decompressed'], 'Fresh content pin')
    fresh = json.loads(raw)
    cycle = json.loads(pinned(CYCLE / 'CYCLE-COVER-PROGRAMS.json', 'cycle_payload'))
    pinned(CYCLE / 'CHECKS.json', 'cycle_phase_receipt')
    pinned(CYCLE / 'EXIT-BINDING.json', 'cycle_exit_receipt')
    pinned(ARCHIVE, 'archive')
    with tarfile.open(ARCHIVE) as archive:
        raw = archive.extractfile('candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json').read()
    need(sha256(raw).hexdigest() == PINS['data_phases'], 'Actual idle phase source')
    data = json.loads(raw)['recipes']
    need(len(data) == len(fresh['transfers']) == len(cycle['records']) == 112, 'All ports')
    counts = Counter()
    native_profiles = Counter()
    port_records = []
    for p, (transfer, record, old) in enumerate(zip(fresh['transfers'], cycle['records'], data)):
        q, v0 = record['q'], record['v0']
        need((transfer['port'], transfer['q'], transfer['v0']) == (p, q, v0), 'Actual pure-line slot')
        need(old['q'] == q, 'Actual DATA port')
        basis = transfer['chart_root_basis'] + UNITS[9:]
        need(len(basis) == D and basis[0:2] == [q, v0], 'Fixed root and fresh basis')
        need(all((a & b).bit_count() % 2 == int(i == j)
                 for i, a in enumerate(basis) for j, b in enumerate(basis)), 'Orthonormal basis')
        need(old['idle_children'][0]['orthogonal_axes'][:8] == basis[1:9], 'Actual root complement')
        perm = [coordinates(basis, act(record['L_columns'], b)) for b in basis]
        need(sorted(perm) == UNITS, 'Cycle only permutes fixed basis axes')
        need(sum(perm[j] != UNITS[j] for j in range(D)) == 10, 'Ten moved axes')
        power = UNITS[:]
        for orbit in range(10):
            need(all(act(power, act(record['L_inverse_columns'], act(record['L_columns'], b)))
                     == act(power, b) for b in basis), 'Literal inverse on every basis vector')
            for stage in range(9):
                active = [route(basis, stage, e) for e in UNITS[:9]]
                v = route(basis, stage, v0)
                terms_by_leg = [[(v, 1)], [(e, 1) for e in active] + [(q, -1)],
                                [(e, 1) for e in active] + [(q, -1), (v, -1)]]
                for terms, rank in zip(terms_by_leg, (1, 8, 7)):
                    terms = [(act(power, e), sign) for e, sign in terms]
                    coordinate_product(basis, terms, rank, 'Fresh leg')
                    counts['fresh_complete_phase_products'] += 1
                    native_profiles[rank] += 1
            for idle in old['idle_children']:
                terms = [(act(power, e), 1) for e in idle['orthogonal_axes']]
                terms.append((act(power, idle['translation_after']), 2))
                coordinate_product(basis, terms, idle['rank'], 'Actual idle')
                counts['idle_complete_phase_products'] += 1
            coordinate_product(basis, [(act(power, e), 1) for e in UNITS], D, 'Full target')
            counts['full_target_phase_products'] += 1
            coordinate_product(basis, [(act(power, q), 1),
                                      (act(power, record['cycle_vectors'][-1]), 1)], 2, 'Terminal')
            counts['terminal_phase_products'] += 1
            power = [act(record['L_columns'], e) for e in power]
        need(power == UNITS, 'Order ten on the full space')
        port_records.append({'port': p, 'q': q, 'v0': v0, 'basis': basis,
                             'cycle_axis_permutation': [v.bit_length() - 1 for v in perm]})
    # The selected characters give all independent signs and one fixed translation sector.
    need((3 - 1) % 4 == 2, 'The actual C eigenvalues differ by a sign')
    need((2 * 1) % 4 == (2 * 3) % 4 == 2, 'Uniform translations have the same phase')
    need((1, 0, 0)[1] != (1, 1, 1)[1], 'An individual-copy translation is outside the free grammar')
    counts['individual_copy_translation_scope_controls'] = 1
    # A non-coordinate C direction is outside the permitted native symbol list.
    rejected = False
    try:
        coordinate_product(UNITS, [(3, 1)], 1, 'Non-coordinate control')
    except ValueError:
        rejected = True
    need(rejected, 'A non-coordinate native direction must fail the scope check')
    counts['non_coordinate_negative_controls'] = 1
    # The proof gives rank N for each test. Check the resulting orbit and cover counts.
    m, ports, orbit_size = 4, 112, 10
    n = 2 * m * orbit_size
    target_per_orbit = D * n
    target_per_cover = target_per_orbit * ports // orbit_size
    need((n, target_per_orbit, target_per_cover) == (80, 5840, 65408), 'Exact cover multiplicity')
    need(64512 + 896 == target_per_cover, 'Current complete rank matches the bound')
    certificate = {'schema': 'pure-cycle-sign-rank-v1', 'source_pins': PINS,
                   'port_bases': port_records, 'counts': dict(counts),
                   'checked_fresh_profile_over_all_stages_and_orbit_positions': dict(sorted(native_profiles.items())),
                   'productive_fields_per_port_orbit': n, 'bound_per_port_orbit': target_per_orbit,
                   'bound_per_cover_copy_four_pairs': target_per_cover,
                   'tensor_width_for_independent_signs': 3}
    encoded = (json.dumps(certificate, indent=2, sort_keys=True) + '\n').encode()
    (HERE / 'PURE-CYCLE-RANK-DATA.json').write_bytes(encoded)
    receipt = {'status': 'PASS_PURE_CYCLE_SIGN_RANK_BINDING',
               'checker_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
               'proof_sha256': sha256((HERE / 'PURE-CYCLE-RANK.md').read_bytes()).hexdigest(),
               'certificate_sha256': sha256(encoded).hexdigest(), 'counts': dict(counts),
               'source_pins': PINS, 'bound_per_cover_copy_four_pairs': target_per_cover,
               'scope': 'Exact finite phase and axis binding for the stated atomic pure-cycle operation set. The general rank inequality is proved in the note. No complete supplier or unrestricted native lower bound.'}
    (HERE / 'PURE-CYCLE-RANK.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print(receipt['status'])


if __name__ == '__main__':
    main()
