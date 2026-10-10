#!/usr/bin/env python3
"""T1: the admissible tilings of a width-66 bank, enumerated -- and what they rule out.

A complex bank is a width-66 coordinate block.  Filling it means choosing blocks whose
sizes sum to 66, and absorbing a family *uniformly* -- the same block pattern in every bank,
which is what the certified bit-side construction does (eighteen 4-coordinate cores, or
three 24-coordinate cores, per width-72 bank) -- means

    k_f blocks of family f per bank,  and  n_f = k_f * B items of family f

for one **common** B.  Writing it out, B must divide every absorbed family's item count
``n_f``, ``k_f = n_f / B``, and the pattern has to fit: ``sum_f k_f * f <= 66``, the leftover
registers being filled by blocks of retained families (the padding).

So the enumeration is not over partitions of 66 -- it is over the common divisors of the
absorbed item counts, which is exact and small.  Run on the pinned complex word
(``references/pr219-run1/references/pr193-source-assisted-v4.certificate.json``) it answers
the obligation this package carries as T1:

* **rank 11 tiles alone.**  3186 three-copy items, ``66 = 6 * 11``: four admissible uniform
  patterns, B in {3186, 1593, 1062, 531}, of which rung 2's 531 is the tightest (six blocks
  per bank, no padding).
* **ranks 16 and 20 tile alone too** -- but only at bank counts *above* the ones the volume
  criterion prices.  ``66 = 4 * 16 + 2`` and ``66 = 3 * 20 + 6``, so a bank holds at most 4
  rank-16 or 3 rank-20 blocks; 792 rank-16 items therefore need **198** banks, not the 192
  that ``12,672 / 66`` gives, and 198 rank-20 items need **66**, not 60.  The priced counts
  are below their own capacity bound: 792/192 = 4.125 items per bank in a bank that fits
  4.
* **no mixture is admissible.**  For a set of families absorbed together B must divide every
  count in the set, and the pattern must fit in 66; for {11,16} the only common divisor is 6
  (k = 531 and 132 blocks per bank), for {16,20} it is 198 (k = 4 and 1, using 84 of the 66
  registers), and for all three it is 18 (k = 177, 44, 11).  Every one of them overflows the
  bank, so **no uniform tiling of width 66 absorbs two whole bins at once**.
* consequently the rungs' shortfall cannot be repaired by mixing in a *retained* family
  either: the padding registers are 2 per rank-16 bank (396 three-copy registers) and 6 per
  rank-20 bank (again 396), and paying them from a retained family means removing *part* of
  that family's bin -- an absorption the priced ledger does not model, since it removes a
  bin whole.  That is the precise form of T1's obstruction, and it is what rungs 3 and 4
  owe on top of C1's normalizer.

The volume criterion (``m | r * n``) and the capacity criterion (``n <= B * floor(m / r)``)
agree exactly when the rank divides the bank width -- which is why rung 1 (rank 22, width
72), rung 2 (rank 11, width 66) and the certified bit-side absorption (rank 60 exteriors,
396,000 / 72 = 5,500 banks, cores of 4 and 24) are all consistent, and why ranks 16 and 20
are not.
"""
import json
import sys
from fractions import Fraction as Q
from math import gcd
from pathlib import Path

HERE = Path(__file__).resolve().parent
SUPPLIER = (HERE / 'references' / 'pr219-run1' / 'references'
            / 'pr193-source-assisted-v4.certificate.json')
PR205 = HERE / 'references' / 'pr219-run1' / 'references' / 'pr205-packed.certificate.json'
WIDTH = 66
COPIES = 3
LADDER = (11, 16, 20)


def supplier():
    """The pinned complex profile: width, ledger bins, local rings, stock, deficit."""
    row = json.loads(SUPPLIER.read_text())['complex_profile']
    return dict(m=int(row['m']),
                ledger={int(r): int(n) for r, n in row['child_histogram'].items() if n},
                local={int(r): int(n) for r, n in row['local_histogram'].items() if n},
                W=int(row['W_per_vertex']), deficit=int(row['deficit_per_vertex']),
                v=int(row['v']), h=int(row['h']), rank=int(row['rank_per_vertex']))


def divisors(n):
    out = []
    for d in range(1, int(n ** 0.5) + 1):
        if n % d == 0:
            out.append(d)
            if d != n // d:
                out.append(n // d)
    return sorted(out)


def capacity(width, family):
    """Whole blocks of `family` that fit in a bank: the leftover is padding."""
    return width // family


def uniform_patterns(counts, width):
    """Every uniform pattern absorbing the whole set: B | gcd(counts), sum k_f f <= width."""
    common = 0
    for n in counts.values():
        common = gcd(common, n)
    out = []
    for B in divisors(common):
        blocks = {f: n // B for f, n in counts.items()}
        used = sum(blocks[f] * f for f in blocks)
        if used <= width:
            out.append(dict(banks=B, blocks=blocks, registers_used=used,
                            padding_per_bank=width - used,
                            padding_registers=(width - used) * B))
    return sorted(out, key=lambda entry: entry['banks'])


def best_overflow(counts, width):
    """The closest a uniform pattern gets for `counts`: its smallest-blocking pattern."""
    common = 0
    for n in counts.values():
        common = gcd(common, n)
    attempts = []
    for B in divisors(common):
        blocks = {f: n // B for f, n in counts.items()}
        used = sum(blocks[f] * f for f in blocks)
        attempts.append(dict(banks=B, blocks=blocks, registers_used=used,
                             overflow=used - width))
    if not attempts:
        return None
    return min(attempts, key=lambda entry: entry['overflow'])


def subset_scan(items, width, families):
    """For every subset of the ladder: admissible patterns, or the shortest overflow."""
    from itertools import combinations
    out = {}
    for size in range(1, len(families) + 1):
        for subset in combinations(families, size):
            counts = {f: items[f] for f in subset}
            patterns = uniform_patterns(counts, width)
            entry = dict(families=list(subset),
                         common_divisor=0, admissible=patterns)
            common = 0
            for n in counts.values():
                common = gcd(common, n)
            entry['common_divisor'] = common
            if not patterns:
                entry['closest_attempt'] = best_overflow(counts, width)
            out[','.join(map(str, subset))] = entry
    return out


def tiling():
    """The whole T1 record: capacities, priced counts, patterns, feasibility per subset."""
    data = supplier()
    width = data['m']
    one_copy = {f: data['ledger'][f] for f in LADDER}
    items = {f: one_copy[f] * COPIES for f in LADDER}
    assert width == WIDTH

    families = {}
    for f in LADDER:
        cap = capacity(width, f)
        priced = f * items[f] // width
        whole = (f * items[f]) % width == 0
        minimum = -(-items[f] // cap)
        families[str(f)] = dict(
            per_vertex=one_copy[f], three_copies=items[f],
            capacity_per_bank=cap, registers_per_block=f,
            whole_bank_volume=whole, volume_registers=f * items[f],
            priced_banks=priced, capacity_minimum_banks=minimum,
            shortfall_banks=minimum - priced,
            items_per_priced_bank=str(Q(items[f], priced)),
            fits_the_priced_banks=(Q(items[f], priced) <= cap),
            padding_per_bank=width - cap * f,
            padding_registers=(width - cap * f) * minimum,
            divides_width=(width % f == 0),
        )

    # the certified precedent, read from the pinned bit-side certificate
    packed = json.loads(PR205.read_text())['physical']
    precedent = dict(source='references/pr219-run1/references/pr205-packed.certificate.json',
                     width=72, banks=int(packed['banks']), copies=int(packed['copies']),
                     note='the only bank construction in the pins: width-72 entrance-gauge '
                          'banks filled by eighteen 4-coordinate or three 24-coordinate '
                          'cores (a rank-60 exterior family, 396,000 three-copy registers = '
                          '5,500 banks of its own volume)')

    scan = subset_scan(items, width, LADDER)
    return dict(
        width=width, copies=COPIES, ladder=list(LADDER),
        source_supplier=SUPPLIER.name, one_copy_bins=one_copy,
        three_copy_items=items, families=families,
        certified_precedent=precedent,
        subsets=scan,
        findings=dict(
            rank_11_tiles_alone=True,
            rank_11_patterns=len(scan['11']['admissible']),
            rank_11_tightest_banks=scan['11']['admissible'][-1]['banks'],
            ranks_16_20_tile_alone_only_above_their_priced_bank_counts=True,
            mixed_uniform_tilings=sum(len(entry['admissible'])
                                      for key, entry in scan.items() if ',' in key),
            verdict='no admissible uniform tiling of a width-66 bank absorbs two whole '
                    'bins at once, and neither rank 16 nor rank 20 fits the bank count '
                    'its own volume criterion prices',
        ),
        obligations=dict(
            T1='the enumeration above: the mixed tiling ranks 16 and 20 owe has no uniform '
               'solution, so it must remove part of a retained bin (padding) or use a '
               'different bank width -- the pins state neither, so the rungs above rung 2 '
               'stay priced rather than instantiated',
            C1='unchanged: the normalizer and item-to-block maps the bank construction owes',
        ),
    )


def main():
    sys.set_int_max_str_digits(0)
    sys.dont_write_bytecode = True
    record = tiling()
    target = HERE / 'schedule66.json'
    target.write_text(json.dumps(record, indent=1, sort_keys=True, default=str) + '\n',
                      newline='\n')
    print('width %d; three-copy items %s' % (record['width'], record['three_copy_items']))
    for f, entry in sorted(record['families'].items(), key=lambda kv: int(kv[0])):
        print('  rank %-3s %4d per vertex %5d three-copy: capacity %d/bank -> %4d banks '
              '(priced %4d, short by %d); priced = %s items per bank'
              % (f, entry['per_vertex'], entry['three_copies'], entry['capacity_per_bank'],
                 entry['capacity_minimum_banks'], entry['priced_banks'],
                 entry['shortfall_banks'], entry['items_per_priced_bank']))
    for key, entry in sorted(record['subsets'].items()):
        if entry['admissible']:
            print('  {%-8s} %d admissible uniform pattern(s): %s'
                  % (key, len(entry['admissible']),
                     [p['banks'] for p in entry['admissible']]))
        else:
            near = entry['closest_attempt']
            print('  {%-8s} NO uniform pattern: common divisor %d, closest uses %d registers '
                  '(%+d)' % (key, entry['common_divisor'], near['registers_used'],
                             near['overflow']))
    print('verdict %s' % record['findings']['verdict'])
    print('write   ' + str(target))


if __name__ == '__main__':
    main()
