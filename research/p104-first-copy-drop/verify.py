"""Independent E8 construction and column-code census; no predecessor imports."""
from collections import Counter
from fractions import Fraction
import hashlib
from itertools import combinations, product
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rank_basis(vectors):
    pivots, basis = {}, []
    for vector in vectors:
        value = vector
        while value:
            bit = value.bit_length() - 1
            if bit in pivots:
                value ^= pivots[bit]
            else:
                pivots[bit] = value
                basis.append(vector)
                break
    return basis


def codewords(basis):
    words = [0]
    for b in basis:
        words += [v ^ b for v in words]
    require(len(set(words)) == len(words), 'dependent code generators')
    return words[1:]


def build():
    roots = []
    for a, b in combinations(range(8), 2):
        for sign in (1, -1):
            row = [0] * 8
            row[a], row[b] = 2, 2 * sign
            roots.append(tuple(row))
    for tail in product((1, -1), repeat=7):
        if tail.count(-1) % 2 == 0:
            roots.append((1,) + tail)
    require(len(roots) == len(set(roots)) == 120, 'root line construction failed')
    ip = []
    for a in roots:
        row = []
        for b in roots:
            dot = sum(x * y for x, y in zip(a, b))
            require(dot % 4 == 0, 'nonintegral root pairing')
            row.append(dot // 4)
        ip.append(row)
    labels = [sum(((v + 1) % 2) << j for j, v in enumerate(row)) for row in ip]
    require(len(rank_basis(labels)) == 9 and len(set(labels)) == 120, 'label pairing model failed')
    f0 = []
    for a in range(0, 8, 2):
        for sign in (1, -1):
            root = [0] * 8
            root[a], root[a + 1] = 2, 2 * sign
            f0.append(roots.index(tuple(root)))
    return roots, ip, labels, f0


def mask(indices):
    return sum(1 << i for i in indices)


def bits(value):
    while value:
        low = value & -value
        yield low.bit_length() - 1
        value ^= low


def frames(ip, f0):
    pool = [i for i in range(120) if i not in f0]
    adjacency = [mask(j for j in pool if j != i and ip[i][j] == 0) for i in range(120)]
    out = []

    def visit(chosen, available):
        if len(chosen) == 8:
            out.append(tuple(chosen))
            return
        if available.bit_count() < 8 - len(chosen):
            return
        while available:
            low = available & -available
            j = low.bit_length() - 1
            available ^= low
            visit(chosen + [j], available & adjacency[j])

    visit([], mask(pool))
    return sorted(out)


def decoders(ip, f0, f1):
    adjacency = [sum(bool(ip[g][f]) << i for i, f in enumerate(f0)) for g in f1]
    answer = []
    for selected in range(256):
        source_ids = list(bits(selected))
        groups = [[j for j, a in enumerate(adjacency) if a & selected == 1 << i]
                  for i in source_ids]
        if any(not group for group in groups):
            continue
        for chosen in product(*groups):
            require(len(set(chosen)) == len(chosen), 'partner groups overlap')
            remaining_f0 = 255 ^ selected
            remaining_f1 = 255 ^ mask(chosen)
            other = []
            used = 0
            for j in bits(remaining_f1):
                neighbours = adjacency[j] & remaining_f0
                if neighbours.bit_count() != 1 or used & neighbours:
                    break
                used |= neighbours
                other.append((f1[j], f0[neighbours.bit_length() - 1]))
            else:
                require(used == remaining_f0, 'incomplete complement matching')
                pairs = [(f0[i], f1[j]) for i, j in zip(source_ids, chosen)] + other
                answer.append(pairs)
    return answer


def pair_rank(ip, labels, pair, live):
    a, b = pair
    row_ids = [i for i in live if ip[a][i]]
    columns = mask(i for i in live if ip[b][i])
    return len(rank_basis(labels[i] & columns for i in row_ids))


def whole_ranks(ip, labels, pairs, live):
    return [pair_rank(ip, labels, pair, live) for pair in pairs]


def dual_check(ip, pairs):
    require(len(pairs) == 8, 'decoder does not have eight terms')
    for k, (a, b) in enumerate(pairs):
        require(ip[a][b] in (-1, 1), 'nonodd decoder pair')
        for l, (_, partner) in enumerate(pairs):
            require(2 * ip[a][partner] * ip[pairs[l][0]][partner] == (2 if k == l else 0),
                    'decoder is not an exact dual basis')


def census(ip, labels, f0):
    inventory = frames(ip, f0)
    require(len(inventory) == 1260, 'frame enumeration coverage gap')
    records, total, term_histogram = [], 0, Counter()
    for f1 in inventory:
        solutions = decoders(ip, f0, f1)
        if not solutions:
            continue
        require(len(solutions) == 8, 'unexpected number of exact decoders')
        for pairs in solutions:
            dual_check(ip, pairs)
        total += len(solutions)
        edges = sorted({tuple(sorted(pair)) for pairs in solutions for pair in pairs})
        require(len(edges) == 32, 'different possible term inventory')
        base = set(f0) | set(f1)
        live = [i for i in range(120) if i not in base]
        supports = {a: mask(i for i in live if ip[a][i]) for a in base}
        support_min = 120
        for a in base:
            generators = rank_basis(row & supports[a] for row in labels)
            require(len(generators) == 8, 'baseline support is not a label hyperplane')
            support_min = min(support_min, min(v.bit_count() for v in codewords(generators)))
        minimum, hits = 120, 0
        for a, b in edges:
            edge_min = 120
            for normal, partner in ((a, b), (b, a)):
                # These are columns of the complete baseline pairing matrix,
                # viewed as functions on surviving source labels.
                columns = rank_basis(labels[j] & supports[normal] for j in bits(supports[partner]))
                require(len(columns) == 7, 'baseline COPY pairing rank differs')
                cuts = codewords(columns)
                require(len(cuts) == 127, 'column hyperplane coverage gap')
                for cut in cuts:
                    weight = cut.bit_count()
                    edge_min = min(edge_min, weight)
                    if weight < minimum:
                        minimum, hits = weight, 1
                    elif weight == minimum:
                        hits += 1
            term_histogram[edge_min] += 1
        records.append({'frame': list(f1), 'minimum_added': minimum,
                        'first_support_span_drop': support_min,
                        'minimum_quotient_cuts': hits})
    require(len(records) == 896 and total == 7168, 'exact family coverage gap')
    return records, term_histogram


def source_checks():
    pins = json.loads((ROOT / 'SOURCES.json').read_text())
    expected = {'sources/BASE-selected-result.json', 'sources/PR968-README.md',
                'sources/PR968-PROOF.md', 'sources/PR968-verify.py',
                'sources/PR1020-README.md', 'sources/PR1020-PROOF.md', 'sources/PR1020-NOTICE.md'}
    require(set(pins['files']) == expected, 'source inventory gap')
    for path, pin in pins['files'].items():
        require(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == pin['sha256'],
                'source pin mismatch: ' + path)


def main():
    source_checks()
    result = json.loads((ROOT / 'CERTIFICATE.json').read_text())
    require(result['frames_in_p112'] == 1260 and result['admissible_frames'] == 896
            and result['exact_decoders'] == 7168, 'family metadata mismatch')
    require(result['normal_hyperplanes'] == 255 and result['support_cut_evaluations'] == 3655680
            and result['quotient_cut_evaluations'] == 7282688, 'cut coverage metadata mismatch')
    require(result['frame_minimum_histogram'] == {'22': 896}, 'frame histogram metadata mismatch')
    roots, ip, labels, f0 = build()
    records, term_histogram = census(ip, labels, f0)
    require(records == result['frame_records'], 'independent frame census mismatch')
    digest = hashlib.sha256(json.dumps(records, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    require(digest == result['frame_records_sha256'], 'frame receipt digest mismatch')
    require(term_histogram == Counter({22: 28672}), 'term threshold is not uniformly 22')
    require(result['term_minimum_histogram'] == {'22': 28672}, 'term histogram receipt mismatch')
    require(result['first_extra_punctures'] == 22 and result['first_total_punctures'] == 38,
            'wrong claimed first-drop threshold')
    require(all(r['first_support_span_drop'] == 20 and r['minimum_quotient_cuts'] == 1536 for r in records),
            'boundary counts mismatch')
    witness = result['witness']
    require(witness['frame0'] == f0, 'wrong coordinate frame')
    f1 = witness['frame1']
    solutions = decoders(ip, f0, f1)
    require(sorted(map(tuple, witness['pairs'])) in [sorted(map(tuple, p)) for p in solutions],
            'witness is outside exact frame-pair family')
    pairs = witness['pairs']
    dual_check(ip, pairs)
    base = set(f0) | set(f1)
    added = witness['added_punctures']
    require(len(added) == len(set(added)) == 22 and not base.intersection(added), 'wrong added puncture set')
    live = [i for i in range(120) if i not in base and i not in added]
    ranks = whole_ranks(ip, labels, pairs, live)
    require(ranks == witness['ranks'] == [7, 7, 7, 6, 7, 7, 7, 7], 'attaining ranks differ')
    require(len(live) == witness['live_ports'] == 82 and sum(ranks) == witness['copy_cost'] == 55,
            'witness width/copy invoice differs')
    coefficients = 0
    for i in live:
        for j in live:
            actual = sum(2 * ip[a][b] * ip[i][a] * ip[j][b] for a, b in pairs)
            require(actual == 2 * ip[i][j], 'all-pairs decoder identity fails')
            coefficients += 1
    control = result['span_only_control']
    ctrl_live = [i for i in range(120) if i not in base and i not in control['added_punctures']]
    require(len(ctrl_live) == 84 and len(control['added_punctures']) == 20, 'bad span-only fixture')
    support = [i for i in ctrl_live if ip[control['normal']][i]]
    require(len(rank_basis(labels[i] for i in support)) == control['side_span'] == 7,
            'span-only fixture does not lose dimension')
    require(whole_ranks(ip, labels, pairs, ctrl_live) == control['ranks'] == [7] * 8,
            'span-only fixture incorrectly loses COPY rank')
    controls = 1
    for restored in added:
        require(whole_ranks(ip, labels, pairs, sorted(live + [restored])) == [7] * 8,
                'one-port restoration failed to cross the sharp boundary')
    controls += 22
    bad = [list(p) for p in pairs]
    bad[0][1], bad[1][1] = bad[1][1], bad[0][1]
    try:
        dual_check(ip, bad)
    except ValueError:
        controls += 1
    else:
        raise ValueError('swapped decoder partners accepted')
    require(Fraction(55, 82) > Fraction(56, 104), 'first-drop witness unexpectedly improves COPY ratio')
    controls += 1
    require(result['assignment_seed'] == 46 and result['base_commit'] == 'c0e3631dc24e3c24a861f7d3d79e0608481cccec',
            'assignment provenance mismatch')
    print('PASS_P104_FIRST_COPY_DROP frames=896 decoders=7168 terms=28672 '
          'extra_punctures=22 total_punctures=38 span_only=20 copies=55 ports=82 no_new_kappa')
    print(json.dumps({'independent_method': 'column-space binary codes; no predecessor imports',
                      'frame_records_sha256': digest, 'all_pairs_coefficients': coefficients,
                      'mathematical_controls': controls,
                      'copy_ratio': '55/82', 'baseline_copy_ratio': '7/13'}, sort_keys=True))


if __name__ == '__main__':
    main()
