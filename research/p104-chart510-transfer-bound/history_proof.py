"""Verify the temporal exterior-span premise and every optimal hub for chart 510.

Usage: python3 -I -B history_proof.py /path/to/strong-bit.json.gz
A directory containing strong-bit.json.gz is also accepted. Standard library only.
"""

import argparse
from collections import Counter
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path


SOURCE_SHA = '74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326'
EXPANDED_SHA = 'b096d6df2a0c4688296b13ab0cfd50fec1c7dec732819c624ddd7a745a144b69'
MOVES = {
    8105: (2335, 330, 510), 8113: (2337, 331, 510),
    10036: (2828, 510, 1), 10039: (2829, 510, 1), 11017: (3151, 510, 328),
}
EARLY = 11021
FIRST_AT_TOP = 29578
LAST_AT_TOP = 29847


class Span:
    """An echelon basis of binary linear forms on the 630 native public inputs."""

    def __init__(self, pivots=None):
        self.pivots = {} if pivots is None else pivots.copy()

    def remainder(self, word):
        while word:
            other = self.pivots.get(word.bit_length())
            if other is None:
                break
            word ^= other
        return word

    def contains(self, word):
        return self.remainder(word) == 0

    def insert(self, word):
        word = self.remainder(word)
        if word:
            self.pivots[word.bit_length()] = word

    def extend(self, other):
        for word in other.pivots.values():
            self.insert(word)

    @classmethod
    def pool(cls, bases):
        result = cls()
        for basis in bases:
            result.extend(basis)
        return result

    def defect(self, words):
        extension = Span(self.pivots)
        for word in words:
            extension.insert(word)
        return len(extension.pivots) - len(self.pivots)


def replay(word, substitutions, checkpoints, observe, *, check_full=False):
    n = word['public']
    charts = dict(enumerate(word['start']))
    forms = {i: 1 << i for i in range(n)}
    history = {int(i): Span() for i in word['frames']}
    for i, form in forms.items():
        history[charts[i]].insert(form)
    move_forms = {}
    for clock, (op, dest, *args) in enumerate(word['program']):
        if clock in checkpoints:
            observe(clock, history)
            if clock == max(checkpoints) and not check_full:
                return
        touched = (dest,)
        if op == 'INIT':
            assert dest >= n and dest not in forms
            charts[dest], forms[dest] = args[0], 0
        elif op == 'ADD':
            src, chart = args
            assert charts[src] == charts[dest] == chart
            forms[dest] ^= forms[src]
        elif op == 'SWAP':
            src, = args
            charts[dest], charts[src] = charts[src], charts[dest]
            forms[dest], forms[src] = forms[src], forms[dest]
            touched = (dest, src)
        elif op == 'MOVE':
            before, after = args
            assert charts[dest] == before
            if clock in MOVES:
                assert (dest, before, after) == MOVES[clock]
                move_forms[clock] = forms[dest]
            charts[dest] = after
            if clock in substitutions:
                forms[dest] = substitutions[clock]
        else:
            assert op == 'CLEAR' and dest >= n and charts.pop(dest) == args[0]
            forms.pop(dest)
            touched = ()
        for i in touched:
            history[charts[i]].insert(forms[i])
    assert check_full and not substitutions
    assert charts == dict(enumerate(word['final'])) and n == len(forms) == 630
    for i, form in forms.items():
        expected = 1 << i
        if 111 <= i < 222:
            expected ^= 1 << (i - 111)
        assert form == expected
    return move_forms


def true_readers(word):
    # Check all post-export owner mutations as well as all non-clear readers.
    born = {reg: clock for clock, (reg, _, _) in MOVES.items()}
    readers = {reg: [] for reg in born}
    for clock, (op, dest, *args) in enumerate(word['program']):
        if dest in born and clock > born[dest]:
            assert op == 'CLEAR'
        if op in ('ADD', 'SWAP') and args[0] in born and clock > born[args[0]]:
            assert op == 'ADD'
            readers[args[0]].append(clock)
    assert readers[2335] == [10038,11015] and readers[2337] == [10035,11016]
    first = {reg: readers[reg][0] for reg in (3151,2828,2829)}
    assert first == {3151: EARLY, 2828: FIRST_AT_TOP, 2829: LAST_AT_TOP}
    return first


def rational_rows(rows):
    """Canonical reduced echelon row space over Q in the native eight coordinates."""
    rows = [list(map(Fraction, row)) for row in rows]
    r = 0
    for column in range(8):
        pivot = next((i for i in range(r, len(rows)) if rows[i][column]), None)
        if pivot is None:
            continue
        rows[r], rows[pivot] = rows[pivot], rows[r]
        divisor = rows[r][column]
        rows[r] = [x / divisor for x in rows[r]]
        for i, row in enumerate(rows):
            if i != r and row[column]:
                mul = row[column]
                rows[i] = [x - mul * y for x, y in zip(row, rows[r])]
        r += 1
    return tuple(tuple(row) for row in rows[:r])


def row_subset(small, big):
    # A canonical echelon basis has 1 in its pivot column and 0 in every other pivot.
    pivots = [(next(j for j, x in enumerate(row) if x), row) for row in big]
    for row in small:
        v = list(row)
        for j, basis_row in pivots:
            multiplier = v[j]
            if multiplier:
                v = [x - multiplier*y for x,y in zip(v,basis_row)]
        if any(v):
            return False
    return True


def charts_and_geometry(word):
    dims = {}
    geometry = {}
    for k, f in word['frames'].items():
        i = int(k)
        rank = dims[i] = f['dim']
        image, kernel = rational_rows(f['B']), rational_rows(f['A'])
        assert len(image) == rank and len(kernel) == 8 - rank
        assert len(rational_rows(f['B'] + f['A'])) == 8
        geometry[i] = (image,kernel)
    assert len(set(geometry.values())) == len(geometry) == 636
    assert {d: n for d,n in sorted(Counter(dims.values()).items())} == {
        0:1, 1:111, 2:153, 4:70, 6:180, 7:120, 8:1,
    }
    assert [dims[i] for i in (330,331,328,510,1)] == [6,6,6,7,8]
    def below(i,h):
        image, kernel = geometry[i]
        big_image, big_kernel = geometry[h]
        return row_subset(image,big_image) and row_subset(big_kernel,kernel)
    assert all(below(i,510) for i in (330,331,328)) and below(510,1)
    image_sum = len(rational_rows(geometry[330][0] + geometry[331][0]))
    kernel_sum = len(rational_rows(geometry[330][1] + geometry[331][1]))
    kernel_intersection = 2 + 2 - kernel_sum
    assert image_sum == 7 and kernel_intersection == 1
    return dims, below, image_sum, kernel_intersection


def check_early(history, dims, below, a, b):
    c = a ^ b
    high = Span.pool(s for i,s in history.items() if dims[i] >= 7)
    top = Span.pool(s for i,s in history.items() if dims[i] >= 8)
    pooled = Span.pool((high, history[328]))
    high_rank, top_rank, c_rank = len(high.pivots), len(top.pivots), len(history[328].pivots)
    assert (high_rank,top_rank,c_rank,len(pooled.pivots)) == (501,501,2,501)
    assert not history[328].contains(c) and not pooled.contains(c)
    sites = [i for i,d in dims.items() if d == 6]
    projected = {'a':[], 'b':[], 'a+b':[]}
    for i in sites:
        gift = Span(pooled.pivots)
        gift.extend(history[i])
        for name, form in [('a',a), ('b',b), ('a+b',c)]:
            if gift.contains(form):
                projected[name].append(i)
    assert projected == {'a':[330], 'b':[331], 'a+b':[]}

    # For a known hub H all its true local exterior gifts are admitted as well.
    hub_neighbours = {}
    matched = []
    tested = 0
    for h,d in dims.items():
        if d != 7 or not below(328,h):
            continue
        neighbours = sorted(i for i in sites if below(i,h))
        hub_neighbours[h] = neighbours
        for i,j in combinations(neighbours, 2):
            tested += 1
            gift = Span.pool(history[k] for k in (328,h,i,j))
            if gift.contains(c):
                matched.append((i,j,h))
    assert sorted(hub_neighbours) == [510,530] and tested == 6
    assert matched == [(330,331,510)]

    # A genuinely new hub starts with zero exterior stock. Drop its geometry and
    # test every pair, including ones that could never be nested under a common hub.
    new_matches = []
    new_tests = 0
    for i,j in combinations(sites, 2):
        new_tests += 1
        gift = Span.pool(history[k] for k in (328,i,j))
        if gift.contains(c):
            new_matches.append((i,j))
    assert new_tests == 16110 and new_matches == [(330,331)]
    return {'rank_ge_7':high_rank, 'rank_ge_8':top_rank, 'background_rank_328':c_rank,
            'rank6_single_site_pool_matches':projected, 'rank7_hubs_over_328':hub_neighbours,
            'listed_donor_pairs_tested':tested, 'listed_feasible_endpoints':matched,
            'new_hub_donor_pairs_tested':new_tests, 'new_hub_donor_pairs':new_matches}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('tape', type=Path)
    args = p.parse_args()
    tape = args.tape / 'strong-bit.json.gz' if args.tape.is_dir() else args.tape
    compressed = tape.read_bytes()
    assert sha256(compressed).hexdigest() == SOURCE_SHA
    expanded = decompress(compressed)
    assert sha256(expanded).hexdigest() == EXPANDED_SHA
    word = json.loads(expanded)
    assert len(word['program']) == 39600 and word['owned_fields'] == 3433
    moves = replay(word, {}, set(), None, check_full=True)
    a, b = moves[8105], moves[8113]
    c = a ^ b
    assert (a.bit_count(), b.bit_count(), (a & b).bit_count()) == (30,41,0)
    assert [moves[k] for k in (10036,10039,11017)] == [b,a,c]
    first = true_readers(word)
    dims, below, image_sum, kernel_intersection = charts_and_geometry(word)
    neutral = dict.fromkeys(MOVES, 0)
    results = {'tape_sha256': SOURCE_SHA, 'expanded_sha256': EXPANDED_SHA,
               'public_inputs':word['public'], 'instructions':len(word['program']),
               'first_exterior_read':first}
    def early(clock, history):
        results['early_cut'] = check_early(history, dims, below, a, b)
    replay(word, neutral, {EARLY}, early)
    # Gift the authentic c at 328 at its nominal delivery, so every one of its
    # chronological exterior descendants is included when proving the late cuts.
    restore_c = neutral.copy()
    restore_c[11017] = c
    results['late_cut'] = {}
    def late(clock, history):
        counts = {}
        for threshold, expected in ((7,614),(8,503)):
            base = Span.pool(s for i,s in history.items() if dims[i] >= threshold)
            assert len(base.pivots) == expected and base.defect([a,b]) == 2
            counts[threshold] = {'background_rank':expected, 'additional_rank_ab':2}
        results['late_cut'][clock] = counts
    replay(word, restore_c, {FIRST_AT_TOP, LAST_AT_TOP}, late)
    assert Fraction(9,10) < 1 - Fraction('0.00389046') <= 1 and 6**9 > 5**10
    results.update({'rank6_source_image_sum_dimension':image_sum,
                    'rank6_source_kernel_intersection_dimension':kernel_intersection,
                    'minimum_paid_price':5, 'required_rank_one_transfers':5,
                    'optimal_source_charts':[330,331], 'optimal_hub_projector_chart':510})
    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
