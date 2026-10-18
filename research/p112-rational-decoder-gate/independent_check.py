#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent exact P112 scalar fits and port-space tariff checks.

No producer, package verifier, or predecessor executable is imported.  Literal
cliques give lower bounds; independent disjoint support constructions give
matching upper bounds over every field.  The separate rational gauge replay
is over Q only.  This is not a native supplier or exponent certificate.
"""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha1, sha256
import json
from pathlib import Path
import sys
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parents[1]
OLD = 'research/tri-plane-port-p112-seeddb093026/CANDIDATE.json'
ARCHIVE = 'research/community-frontier1094-audit/selected-replay.tar.gz'
PINS = {
    OLD: ('92b5f2f835e9f226bba2d936b7bf9ba9300462a9112492bcb70229eb63a84901',
          '438d5c4b1564495bbfeaca2cffa42453c455b3ad'),
    ARCHIVE: ('f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6',
              'c24daf067f9c543421d89ca2eeaa4eb78a57fb6f'),
}
CANDIDATE_SHA = 'dc5fbe51f9cd3a14361256ac136736bffb18971d0247b891accf0d2ee060d06b'
MEMBER = 'candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json'
PAYLOAD_SHA = 'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa'
OLD_CLIQUE = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 14, 15, 16,
              17, 18, 20, 21, 22, 23, 24, 26, 27, 28, 29, 30,
              31, 32, 33, 34, 35, 36, 37)
NEW_CLIQUE = tuple(range(1, 38, 2))


def need(ok, why):
    if not ok:
        raise ValueError(why)


def require_digest(data, expected, why):
    need(sha256(data).hexdigest() == expected, why)


def authenticated(path):
    data = (ROOT / path).read_bytes()
    expected_sha, expected_blob = PINS[path]
    require_digest(data, expected_sha, 'sha256 ' + path)
    need(sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest() == expected_blob,
         'git blob ' + path)
    return data


def bit_rank(rows):
    pivots = {}
    for row in rows:
        while row:
            pivot = row.bit_length() - 1
            if pivot in pivots:
                row ^= pivots[pivot]
            else:
                pivots[pivot] = row
                break
    return len(pivots)


def dot(x, y):
    return (x & y).bit_count() % 2


def pairing(left, right):
    return bit_rank([sum(dot(x, y) << j for j, y in enumerate(right)) for x in left])


def geometry(groups, labels):
    need(len(groups) == 38 and len(groups[0]) == 1
         and all(len(g) == 3 for g in groups[1:]), 'one line and37 three-frames')
    need(sorted(i for g in groups for i in g) == list(range(112)), 'scalar port partition')
    spaces = [[labels[i] for i in g] for g in groups]
    for frame in spaces:
        need(all(dot(x, y) == int(i == j) for i, x in enumerate(frame)
                 for j, y in enumerate(frame)), 'orthonormal port space')
    owners = {i: g for g, coords in enumerate(groups) for i in coords}
    orth = [(i, j) for i in range(38) for j in range(i + 1, 38)
            if pairing(spaces[i], spaces[j]) == 0]
    free = {(i, j) for i in range(112) for j in range(112) if i != j
            and pairing(spaces[owners[i]], spaces[owners[j]]) == 0}
    return spaces, owners, orth, free


def valid_clique(indices, groups, spaces):
    return (len(set(indices)) == len(indices)
            and all(len(groups[i]) == 3 for i in indices)
            and all(pairing(spaces[i], spaces[j]) > 0 for i in indices for j in indices))


def tariff(support, spaces, owners):
    vectors = [x for g in {owners[i] for i in support} for x in spaces[g]]
    return pairing(vectors, vectors)


def matrix(supports, scale):
    result = [[F(0) for _ in range(112)] for _ in range(112)]
    for support in supports:
        for i in support:
            for j in support:
                result[i][j] += scale[i] / scale[j]
    return result


def valid_endpoint(K, free):
    return (all(K[i][i] == 1 for i in range(112))
            and all(i == j or (i, j) in free or K[i][j] == 0
                    for i in range(112) for j in range(112)))


def certify_fit(groups, labels, supports, clique, expected_rank, expected_profile, expected_free):
    spaces, owners, orth, free = geometry(groups, labels)
    need(len(free) == expected_free, 'exact free-pair count')
    need(valid_clique(clique, groups, spaces), 'literal nonorthogonal clique')
    principal = [i for g in clique for i in groups[g]]
    need(len(principal) == expected_rank, 'identity minor size')
    # Disjoint nonempty indicator columns are independent over EVERY field.
    # Their sum of outer products has one all-ones block per support and hence
    # rank exactly the number of supports, irrespective of characteristic.
    need(len(supports) == expected_rank and all(supports)
         and sorted(i for s in supports for i in s) == list(range(112)),
         'nonempty disjoint factor supports partition all scalar coordinates')
    K = matrix(supports, [F(1)] * 112)
    need(valid_endpoint(K, free), 'all12544 scalar coefficients fit the complete mask')
    need(all(K[i][j] == int(i == j) for i in principal for j in principal), 'forced identity minor')
    profile = Counter(tariff(s, spaces, owners) for s in supports)
    need(profile == expected_profile, 'exact port-space copy profile')
    need(sum(r * n for r, n in profile.items()) == 334, 'full copy mass')
    return spaces, owners, orth, free, principal, K


def main():
    old_data = json.loads(authenticated(OLD))
    old_groups = old_data.get('candidate', old_data)['groups']
    authenticated(ARCHIVE)
    with tarfile.open(ROOT / ARCHIVE, 'r:gz') as f:
        payload = f.extractfile(MEMBER).read()
    require_digest(payload, PAYLOAD_SHA, 'selected label member pin')
    recipes = sorted(json.loads(payload)['recipes'], key=lambda r: r['port'])
    need([r['port'] for r in recipes] == list(range(112)), 'selected port indexing')
    labels = [r['q'] for r in recipes]
    need(len(set(labels)) == 112 and all(0 < q < 512 and dot(q, q) for q in labels), 'selected odd labels')
    need(all(r['terminal_Y_translation'] == r['q'] for r in recipes), 'selected translation labels')
    candidate_bytes = (HERE / 'CANDIDATE.json').read_bytes()
    require_digest(candidate_bytes, CANDIDATE_SHA, 'published candidate pin')
    candidate = json.loads(candidate_bytes)
    need(candidate['scientific_base'] == '7ef5f7150476fdf995b286b9cdbed262c631939c'
         and candidate['source_payload_sha256'] == PAYLOAD_SHA, 'candidate source identity')

    # The old cover also has an exact99-factor fit. This construction is new
    # comparison evidence here, not PR2041's invalid11-factor binary decoder.
    old_pairs = [(6, 13), (7, 12), (9, 19), (22, 25)]
    old_supports = [[i, j] for a, b in old_pairs for i, j in zip(old_groups[a], old_groups[b])]
    old_supports.append([old_groups[0][0], old_groups[1][0]])
    old_used = {i for s in old_supports for i in s}
    old_supports.extend([[i] for i in range(112) if i not in old_used])
    old_fit = certify_fit(old_groups, labels, old_supports, OLD_CLIQUE, 99,
                          {3: 86, 4: 1, 6: 12}, 102)

    groups = candidate['groups']
    new_pairs = [(g, g + 1) for g in range(1, 36, 2)]
    supports = [[i, j] for a, b in new_pairs for i, j in zip(groups[a], groups[b])]
    # The residual line joins the first paired coordinates of groups15/16.
    residual_pair = next(s for s in supports if s == [groups[15][0], groups[16][0]])
    residual_pair.append(groups[0][0])
    supports.extend([[i] for i in groups[37]])
    new_fit = certify_fit(groups, labels, supports, NEW_CLIQUE, 57,
                          {3: 3, 6: 53, 7: 1}, 420)
    spaces, owners, orth, free, principal, unit_K = new_fit
    need(candidate['factor_supports'] == supports, 'published factors equal independent construction')
    need(candidate['disjoint_free_triad_pairs'] == [list(p) for p in new_pairs]
         and all(p in orth for p in new_pairs), '18 disjoint free triad pairs')
    need(candidate['orthogonal_group_pairs'] == [list(p) for p in orth], 'complete published orthogonality table')
    need(candidate['clique_groups'] == list(NEW_CLIQUE), 'published clique is independent literal clique')
    need(candidate['claimed_minimum_scalar_rank'] == 57
         and candidate['claimed_copy_profile'] == {'3': 3, '6': 53, '7': 1}
         and candidate['claimed_copy_mass'] == 334, 'published scalar rank and whole-space bill')

    # Gauge replay with halves: a_i=d_i and b_j=1/d_j on each support. This
    # checks genuine rational scalar entries, but introduces no2-adic gain:
    # undoing the diagonal gauge recovers the integral indicator fit above.
    scale = [F(x) for x in candidate['rational_test_scalings']]
    need(scale == [F(1 + (i % 2)) for i in range(112)], 'explicit rational gauge')
    K = matrix(supports, scale)
    need(valid_endpoint(K, free), 'all12544 rational-gauge endpoint coefficients')
    need(any(x.denominator == 2 for row in K for x in row), 'nonintegral scalar entries occur')
    need(all(K[i][j] * scale[j] / scale[i] == unit_K[i][j]
             for i in range(112) for j in range(112)), 'exact diagonal-gauge equivalence')
    need(all(K[i][j] == int(i == j) for i in principal for j in principal), 'rational identity minor')
    # Every source basis column is replayed against distinct arbitrary target
    # dirt. Forbidden outputs preserve it; the matching output receives one.
    dirty = [F(1000 + i, 13) for i in range(112)]
    for j in range(112):
        output = [dirty[i] + K[i][j] for i in range(112)]
        need(output[j] == dirty[j] + 1
             and all(output[i] == dirty[i] for i in range(112) if i != j and (i, j) not in free),
             'dirty target source-basis replay')
    need(F(8, 9) * 334 == F(2672, 9) and F(334) - F(2672, 9) == F(334, 9),
         'exact mixed-cover allowance and positive deficit')

    controls = 0
    try:
        require_digest(candidate_bytes + b' ', CANDIDATE_SHA, 'mutated source bytes')
    except ValueError:
        pass
    else:
        raise ValueError('source byte corruption was accepted')
    controls += 1
    bad = [row[:] for row in K]
    bad[principal[0]][principal[1]] = 1
    need(not valid_endpoint(bad, free), 'forbidden-entry corruption rejected')
    controls += 1
    bad = [row[:] for row in K]
    bad[groups[0][0]][groups[0][0]] = 0
    need(not valid_endpoint(bad, free), 'lost residual payload rejected')
    controls += 1
    broken_clique = tuple(2 if g == 3 else g for g in NEW_CLIQUE)
    need(not valid_clique(broken_clique, groups, spaces), 'orthogonal-pair clique corruption rejected')
    controls += 1
    need(3 * 3 + 54 * 6 == 333, 'rank-six residual undercharge is one unit short')
    need(tariff(residual_pair, spaces, owners) == 7, 'residual factor consumes all seven dimensions')
    controls += 1
    label_only_mass = sum(pairing([labels[i] for i in s], [labels[i] for i in s]) for s in supports)
    need(label_only_mass == 112 and label_only_mass != 334, 'label-only undercharge rejected')
    controls += 1
    need(pairing(spaces[15], spaces[16]) == 0
         and pairing(spaces[15] + spaces[16], spaces[15] + spaces[16]) == 6,
         'free cross pairing is not full support self-pairing tariff')
    controls += 1
    B0 = [[dot(labels[i], labels[j]) for j in range(112)] for i in range(112)]
    need(not valid_endpoint(B0, free), 'literal binary pairing is not scalar mask identity')
    need(sum(B0[i][j] != 0 for i in range(112) for j in range(112)
             if i != j and (i, j) not in free) == 6608, 'binary pairing forbidden entries')
    controls += 1
    bad = [[F(0) for _ in range(112)] for _ in range(112)]
    for s in supports:
        for i in s:
            for j in s:
                bad[i][j] += scale[i] * scale[j]
    need(not valid_endpoint(bad, free), 'lost reciprocal factor rejected')
    controls += 1
    need(old_fit[3] != free and 99 > 57, 'changed mask is not a rescaled old decoder')
    print('PASS_INDEPENDENT_P112_RATIONAL_FIT old_minrank=99 new_minrank=57 '
          'fields=all old_free=102 new_free=420 rational_entries=12544 dirty_columns=112 '
          'profile=3H3+53H6+H7 mass=334 allowance=2672/9 deficit=334/9 '
          'controls=%d no_native_or_exponent_claim' % controls)


if __name__ == '__main__':
    main()
