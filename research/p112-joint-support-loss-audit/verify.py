#!/usr/bin/env python3
"""Exact P112 joint deletion-loss audit; no predecessor verifier imported.

Philipp / mightyOil with substantial OpenAI Codex GPT-6 Astra assistance.
Apache-2.0. Written finite proof, not a full multiplication theorem.
"""
import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GEOMETRY = 'research/p112-single-lift/reference-geometry.json'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()


def rank(rows):
    """Lowest-pivot elimination, independently used on literal pairing rows."""
    basis = {}
    for value in rows:
        while value:
            p = value & -value
            if p in basis:
                value ^= basis[p]
            else:
                basis[p] = value
                break
    return len(basis)


def span(rows):
    values = {0}
    for row in rows:
        if row not in values:
            values |= {old ^ row for old in values}
    return sorted(values)


def bits(mask):
    return [i for i in range(112) if mask >> i & 1]


def mask_of(ports):
    return sum(1 << i for i in ports)


def load_geometry():
    raw = (ROOT / GEOMETRY).read_bytes()
    manifest = json.loads((HERE / 'SOURCES.json').read_text())
    entry = next(x for x in manifest['files'] if x['path'] == GEOMETRY)
    need(sha256(raw).hexdigest() == entry['sha256'], 'geometry source pin')
    return json.loads(raw)


def words_from_pairing(data):
    x, labels, duals = data['X'], data['labels'], data['duals']
    need(len(x) == len(labels) == len(duals) == 112, 'port count')
    supports = [sum((row[j] != 0) << i for i, row in enumerate(x)) for j in range(8)]
    codes = []
    for support in supports:
        ports = bits(support)
        need(len(ports) == 56, 'coordinate source support')
        # Actual pairing rows, then XOR closure: no RREF parameter enumeration.
        rows = [sum(((duals[i] & labels[t]).bit_count() & 1) << t
                    for t in ports) for i in ports]
        code = span(rows)
        need(len(code) == 256 and rank(rows) == 8, 'evaluation dimension')
        # Separate ambient functional construction authenticates the inventory.
        ambient = {sum(((q & labels[t]).bit_count() & 1) << t
                       for t in ports) for q in range(512)}
        need(set(code) == ambient, 'literal and ambient code inventories')
        need(Counter(w.bit_count() for w in code) ==
             {0: 1, 24: 63, 28: 128, 32: 63, 56: 1}, 'word weights')
        codes.append(code)
    need(all((supports[a] & supports[b]).bit_count() == 24
             for a, b in combinations(range(8), 2)), 'support intersections')
    return supports, codes


def direct_losses(data, deleted):
    """Literal submatrix ranks, with columns repacked after deletion."""
    x, labels, duals = data['X'], data['labels'], data['duals']
    out = []
    for j in range(8):
        readers = [i for i in range(112) if x[i][j]]
        sources = [i for i in readers if not deleted >> i & 1]
        rows = [sum(((duals[i] & labels[t]).bit_count() & 1) << p
                    for p, t in enumerate(sources)) for i in readers]
        out.append(8 - rank(rows))
    return out


def code_losses(codes, deleted):
    counts = [sum(w & ~deleted == 0 for w in code) for code in codes]
    need(all(n > 0 and n & (n - 1) == 0 for n in counts), 'kernel cardinalities')
    return [n.bit_length() - 1 for n in counts]


def checked_losses(data, codes, deleted):
    a, b = code_losses(codes, deleted), direct_losses(data, deleted)
    need(a == b, 'kernel versus literal rank')
    return a


def rank_mod3(rows):
    a = [[v % 3 for v in row] for row in rows]
    k = 0
    for j in range(8):
        pivot = next((i for i in range(k, len(a)) if a[i][j]), None)
        if pivot is None:
            continue
        a[k], a[pivot] = a[pivot], a[k]
        a[k] = [(v * pow(a[k][j], -1, 3)) % 3 for v in a[k]]
        for i in range(k + 1, len(a)):
            t = a[i][j]
            if t:
                a[i] = [(u - t * v) % 3 for u, v in zip(a[i], a[k])]
        k += 1
    return k


def added_reader_premises(data):
    # A nonzero modular minor gives a rational/complex LOWER rank bound.
    # Eight columns (or one identically zero column) give the matching
    # symbolic UPPER bound, so no equality of unrelated field ranks is assumed.
    counts, exceptions = Counter(), []
    need(all(len(row) == 8 and all(type(v) is int for v in row)
             for row in data['X']), 'integer coordinate matrix')
    for q in range(1, 512):
        rows = [row for row, dual in zip(data['X'], data['duals'])
                if (q & dual).bit_count() & 1]
        r = rank_mod3(rows)
        counts[r] += 1
        if r == 7:
            zeros = [j for j in range(8) if all(row[j] == 0 for row in rows)]
            need(len(zeros) == 1, 'symbolic exceptional upper rank bound')
            exceptions.append({'q': q, 'kernel_coordinate': zeros[0]})
        else:
            need(r == 8, 'nonzero eight-minor modulo3')
    need(dict(counts) == {7: 8, 8: 503}, '511 rational rank certificates')
    need(sorted(e['kernel_coordinate'] for e in exceptions) == list(range(8)),
         'distinct exceptional rational kernels')
    labels = data['labels']
    need(len(set(labels)) == 112 and all(0 < q < 512 for q in labels),
         'distinct nonzero source labels')
    need(not set(labels).intersection(e['q'] for e in exceptions),
         'every live label visible to every nonzero on-column reader')
    return {'modulus': 3, 'rank8': counts[8], 'rank7': counts[7],
            'exceptions': exceptions}


def calculate(data):
    supports, codes = words_from_pairing(data)
    added_premises = added_reader_premises(data)
    one = [[w for w in code if 0 < w.bit_count() < 44] for code in codes]
    two = []
    all_two = []
    local = []
    # Every binary 2-space is generated by two distinct nonzero words.
    # Under 44 ports its support suffices; words of weight56 cannot participate.
    for code, small in zip(codes, one):
        full_supports2 = sorted({a | b for a, b in combinations(code[1:], 2)})
        supports2 = [u for u in full_supports2 if u.bit_count() < 44]
        all_two.append(full_supports2)
        need(len(supports2) == 5313, 'complete two-dimensional supports')
        second = min(u.bit_count() for u in supports2)
        third = min((u | w).bit_count() for u in supports2 for w in small
                    if w & ~u)
        need(second == 36 and third == 44, 'second and third loss thresholds')
        # No support below44 contains more than its generating 2-space.
        need(all(sum(w & ~u == 0 for w in code) == 4 for u in supports2),
             'two-space support closure')
        two.append(supports2)
        local.append({'two_supports': len(supports2), 'minimum_two': second,
                      'minimum_third_extension': third,
                      'support_digest': sha256(canonical(supports2)).hexdigest()})

    pairs = {(a, b): {u | v for u in one[a] for v in one[b]
                     if (u | v).bit_count() < 44}
             for a, b in combinations(range(8), 2)}
    triple_min = min((u | w).bit_count()
                     for a, b, c in combinations(range(8), 3)
                     for u in pairs[a, b] for w in one[c])
    need(triple_min == 40, 'three distinct readers threshold')
    four = set()
    for a, b, c, d in combinations(range(8), 4):
        four.update(u | v for u in pairs[a, b] for v in pairs[c, d]
                    if (u | v).bit_count() < 44)
    need(len(four) == 42 and {u.bit_count() for u in four} == {40},
         'complete four-reader minimal supports')
    four_rows = []
    for u in sorted(four):
        losses = checked_losses(data, codes, u)
        hit = [j for j, loss in enumerate(losses) if loss]
        need(len(hit) == 4 and sum(losses) == 4, 'four-reader literal loss')
        fifth = min((w & ~u).bit_count() for j in range(8) if j not in hit
                    for w in codes[j] if w)
        second = min((v & ~u).bit_count() for j in hit for v in all_two[j])
        need(fifth == 8 and second == 12, 'four-reader extension margins')
        four_rows.append({'ports': bits(u), 'losses': losses,
                          'extra_for_fifth': fifth, 'extra_for_second': second})

    # Representatives are derived from the inventories, not read from RESULT.
    common = min(set(one[0]) & set(one[1]), key=lambda w: (w.bit_count(), w))
    need(common.bit_count() == 24, 'two-reader witness')
    witness36 = next(u for u in two[0] if u.bit_count() == 36 and
                     sum(checked_losses(data, codes, u)) == 3)
    witness40 = min(four)
    anchors = {0: 0, 2: common, 3: witness36, 4: witness40}
    exact = []
    for size in range(44):
        loss = 0 if size < 24 else 2 if size < 36 else 3 if size < 40 else 4
        u = anchors[loss]
        for i in range(112):
            if u.bit_count() == size:
                break
            u |= 1 << i
        actual = checked_losses(data, codes, u)
        need(u.bit_count() == size and sum(actual) == loss, 'sharp deletion witness')
        exact.append({'size': size, 'maximum_loss': loss,
                      'witness_ports': bits(u), 'witness_losses': actual})

    added_screen = []
    def price(m):
        return next(r for r in range(1, 10) if m <= 1 << (r + 1))
    for row in exact[1:]:
        size = row['size']
        added = min(price(a) + price(b) for a in range(1, size + 1)
                    for b in range(1, size + 1) if a + b >= size)
        margin = added - row['maximum_loss']
        need(margin >= 2, 'inherited added-price margin')
        added_screen.append({'size': size, 'minimum_added_price': added,
                             'copy_lower_bound': 64 + margin})

    # The paper proof uses these computed premises; it is not a literal
    # enumeration of all binomial(112,M) deletion sets.
    need(2 * 36 - 24 == 48, 'two second-loss readers need48')
    controls = []
    for row in exact:
        if row['maximum_loss']:
            actual = sum(direct_losses(data, mask_of(row['witness_ports'])))
            need(actual > row['maximum_loss'] - 1, 'false stronger maximum rejected')
            controls.append('lower_maximum_at_' + str(row['size']))
    need(sum(direct_losses(data, common ^ (common & -common))) == 0,
         'one port short destroys the minimum common cut')
    controls.append('common_cut_one_port_short')
    need(sum(x > 0 for x in direct_losses(data, witness36)) == 2 and
         sum(direct_losses(data, witness36)) == 3,
         'counting readers instead of nullity rejected')
    controls.append('reader_count_is_not_loss')
    need(sum(direct_losses(data, witness40)) == 4, 'false three-loss bound rejected')
    controls.append('three_loss_bound_at_40')
    return {'schema_version': 1, 'seed': 60,
            'predecessor_head': '2b821b14a7cd5888df95531c98d18ee3797e36c3',
            'added_reader_premises': added_premises, 'local_thresholds': local, 'three_reader_minimum': triple_min,
            'four_reader_supports': four_rows,
            'pair_union_counts': {f'{a},{b}': len(v) for (a,b),v in pairs.items()},
            'two_second_reader_minimum_lower_bound': 48,
            'exact_maxima': exact, 'added_price_screen': added_screen,
            'semantic_controls': controls}


def validate_result(actual, expected):
    need(actual == expected, 'complete result mismatch')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', type=Path)
    args = parser.parse_args()
    actual = calculate(load_geometry())
    if args.write:
        with args.write.open('x') as f:
            json.dump(actual, f, indent=2, sort_keys=True)
            f.write('\n')
    else:
        validate_result(actual, json.loads((HERE / 'RESULT.json').read_text()))
    print('PASS_P112_JOINT_SUPPORT_LOSS exact_maxima=0,2,3,4 domain=0..43 '
          'four_supports=42 fifth_extra=8 second_extra=12 no_new_kappa')


if __name__ == '__main__':
    main()
