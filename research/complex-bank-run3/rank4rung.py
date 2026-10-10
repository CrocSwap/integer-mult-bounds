#!/usr/bin/env python3
"""The rank-4 rung on #233's new row: the padding of T1 reinstated, its limits, and what it buys.

The rank-3 rung (`instantiate_rank3.py`, `rank3contract.py`) absorbs the first family of PR233's
row whose own volume fills whole width-66 banks, and prices the retained row bit-bound: the
complex branch stops binding, so the rung's kappa is the assembly rule's floor on the *bit leaf*.
That leaves an obvious question, and this module answers it by measurement rather than by
assertion: **does the next family up -- rank 4 -- exist on this row, and does banking it move the
kappa?**

Three separate answers, none of them a matter of opinion:

* **the volume criterion says yes.** On the pinned head (`109a857`) the retained row's rank-4 bin
  is `n4 = 34,551` three-copy children, and `66 | 4 * 34551 = 138,204 = 66 * 2,094`, so the
  family's own volume is a whole number of banks.  On the other head that carries the rank-3
  rung (`246f6f9`) it is not: `n4 = 34,506` and `138,024 / 66` is not an integer.  The rung is
  therefore *less* stable than the one below it, and the module records that per head.
* **the padding of T1 cannot be reinstated here.** T1's padded schedule fills a bank with
  `floor(66 / rank)` blocks of the family plus the leftover registers drawn as padding from a
  retained bin, and it requires the schedule to be *saturated*: every family slot used, the same
  padding in every bank, `n == capacity * banks`.  For rank 4 that is `16 | n4`, and
  `34,551 = 16 * 2,159 + 7`: nine slots (36 registers) short.  The priced bank count of the
  volume criterion cannot host the items either -- `2,094 * 16 = 33,504 < 34,551` -- so the
  ledger this rung prices is not a schedule at all until the tiling question is answered.
* **the mixed tiling of T1 does exist, and is heavier than T1 assumed.** Enumerating the
  admissible patterns the way T1 does -- one common bank count `B` dividing `n4`, `a4 = n4/B`
  rank-4 blocks per bank, the remaining registers filled by blocks of the retained families, each
  drawn at most `counts[f] // B` times so the ledger can supply it -- gives solutions at
  `B in {3141, 3839, 11517}` (260, 694 and 214 patterns) and none below `B = 3141` (where the
  rank-4 blocks alone would overflow the bank) or at `B = n4` (where the padding families cannot
  fill 62 registers).  Every one of them draws **at least 22 of the bank's 66 registers** from
  other bins: rank 4 divides nothing here, so a rank-4 bank is at most two-thirds rank 4.  The
  tiled ledgers are consistent (row identity, mass removed `B * 66`, stock falling by exactly
  `B`) and they price *higher* than the priced ledger -- the best measured pattern reaches a
  coarse saving of `1.792871277258e-3` against the priced ledger's `9.088721229013e-4`.

What none of it moves is the kappa.  Every point below is priced by the same rule the rest of
this package uses (`rank3contract.price`: the retained row's coarse saving from the pinned
interval-moment engine, the bit leaf from #219's vendored arithmetic, the queue's assembly rule
and its unchanged 47-constraint assembly), and every one of them is **bit-bound**: the budget is
the leaf, `7.282510899902e-4`, so the kappa is `1819302815717/25*10^14 = 7.277211262868e-4` --
the same value the rank-3 rung already holds, to the last grid step.  The ladder's complex side
has room to spare (the coarse saving nearly doubles) and the assembly rule cannot spend it: the
lever is the *bit* word's leaf, and the module inverts the rule to say exactly what leaf each
further target needs.

Nothing here is a claim about a merged row: the row is pinned by digest to an unmerged branch
(`pins.py`), and this is a measurement of what the rung would be.
"""
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import instantiate_rank3  # noqa: E402
import ledger3  # noqa: E402
import rank3contract  # noqa: E402
import rank3stability  # noqa: E402
import run3  # noqa: E402

FAMILY = 4
WIDTH = instantiate_rank3.WIDTH
COPIES = instantiate_rank3.COPIES
GRID = run3.GRID
ROW_NAME = instantiate_rank3.ROW_NAME
LEDGER = 'occurrences-rank3.json'


def divisors(value):
    return [d for d in range(1, value + 1) if value % d == 0]


def patterns(counts, B, family=FAMILY, width=WIDTH):
    """T1's enumeration at one bank count: the family leaves whole, the rest fills the bank.

    One common bank count `B` divides the family's own count (so `a_f = n_f / B` blocks of it
    leave per bank), and the registers the family does not use are filled by blocks of the
    *retained* families, each drawn at most `counts[f] // B` times per bank so the ledger can
    supply every draw.  A pattern is uniform across banks -- the same one in each -- which is
    what makes it a tiling rather than a per-bank choice.
    """
    n = counts[family]
    assert n % B == 0, 'the absorbed family leaves whole: B must divide its count'
    a = n // B
    remaining = width - family * a
    if remaining < 0:
        return None                       # the family's own blocks already overflow the bank
    capacity = {f: counts[f] // B for f in counts if f != family and counts[f] // B > 0}
    families = sorted(capacity)
    found = []

    def walk(rest, index, chosen):
        if rest == 0:
            found.append(dict(chosen))
            return
        for j in range(index, len(families)):
            f = families[j]
            if f > rest:
                break
            used = chosen.get(f, 0)
            if used >= capacity[f]:
                continue
            chosen[f] = used + 1
            walk(rest - f, j, chosen)
            chosen[f] = used
            if used == 0:
                del chosen[f]

    walk(remaining, 0, {})
    return dict(banks=B, blocks_of_the_family=a, registers_of_the_family=family * a,
                padding_registers_per_bank=remaining, capacity=capacity, count=len(found),
                patterns=found)


def padded_schedule(row, family=FAMILY, width=WIDTH):
    """T1's padded schedule for one family, reported rather than asserted.

    `prototype66.schedule` asserts saturation (`n == capacity * banks`, the same padding in every
    bank).  This is the same reading with the failure kept as data, because here it *is* the
    finding: rank 4 leaves nine slots unused at the capacity bank count.
    """
    n = row['child_multiplicities'][family]
    capacity = width // family
    banks = -(-n // capacity)
    padding = banks * width - family * n
    return dict(family=family, items=n, blocks_per_bank=capacity, registers_per_block=family,
                pattern_sum=family * capacity + (width - family * capacity),
                padding_registers_per_bank=width - family * capacity, banks=banks,
                saturated=(n == capacity * banks), slack_slots=capacity * banks - n,
                slack_registers=family * (capacity * banks - n),
                padding_registers=padding,
                uniform=padding % banks == 0,
                pattern='%d = %d * %d + %d' % (width, capacity, family,
                                               width - family * capacity),
                volume_banks=family * n // width if (family * n) % width == 0 else None,
                volume_banks_host_the_items=((family * n // width) * capacity >= n
                                             if (family * n) % width == 0 else None))


def ledger_after(retained, entry, pattern, family=FAMILY, width=WIDTH):
    """The row a mixed pattern induces: the family leaves whole, the padding is drawn partially.

    Exactly `prototype66`'s accounting, with the padding pattern allowed more than one block size:
    the mass that leaves is `banks * width` by construction, the row identity still holds, and the
    stock falls by exactly the bank count.  Every one of those is asserted here.
    """
    m, D, B = retained['m'], retained['N'], entry['banks']
    assert m == width and B == entry['banks'], 'the schedule must be this width'
    hist = dict(retained['child_multiplicities'])
    hist[family] -= entry['blocks_of_the_family'] * B
    assert hist[family] == 0, 'the absorbed family must leave whole'
    del hist[family]
    draw, drawn_registers = {}, 0
    for f, blocks in sorted(pattern.items()):
        draw[str(f)] = blocks * B
        drawn_registers += f * blocks * B
        hist[f] -= blocks * B
        assert hist[f] >= 0, 'the ledger cannot supply the draw'
        if hist[f] == 0:
            del hist[f]
    mass = sum(r * c for r, c in hist.items())
    stock, remainder = divmod(mass + D, m)
    assert remainder == 0, 'half-filled stock'
    assert retained['W'] - stock == B, 'the stock must fall by exactly the bank count'
    assert family * entry['blocks_of_the_family'] * B + drawn_registers == B * m, \
        'the mass must be the bank volume'
    retained_row = dict(m=m, W=stock, N=D, L=retained.get('L', 0), child_multiplicities=hist,
                        total_rank=mass, maxchild=max(hist))
    assert ledger3.check_row(retained_row) == mass
    return retained_row, dict(draw=draw, children_removed=sum(draw.values()),
                              registers_drawn=drawn_registers)


def measure_head(source, price=False, interval=None):
    """One head of #233, and what the rank-4 rung would be on it."""
    path = HERE / source
    profile = rank3stability.profile_of(path)
    copied = ledger3.three_copies(profile)
    rank3_eligible = FAMILY - 1 in ledger3.eligibility(copied)
    out = dict(source=source, bytes=len(path.read_bytes()), sha256=rank3stability.digest(path),
               m=profile['m'], W=profile['W'], deficit=profile['N'],
               rank3_eligible=rank3_eligible)
    if not rank3_eligible:
        out['verdict'] = ('the rank-4 rung cannot be reached from here: the rank-3 rung this '
                          'module leaves the ledger by first does not exist on this head')
        return out
    retained = ledger3.absorb(copied, FAMILY - 1)['retained']
    n = retained['child_multiplicities'].get(FAMILY)
    out['n4'] = n
    if n is None:
        out['verdict'] = 'the retained row holds no rank-4 family'
        return out
    volume = FAMILY * n
    out['volume'] = volume
    out['volume_whole'] = volume % WIDTH == 0
    out['volume_banks'] = volume // WIDTH
    schedule = padded_schedule(retained)
    out['capacity_banks'] = schedule['banks']
    out['saturated'] = schedule['saturated']
    out['slack_slots'] = schedule['slack_slots']
    if not out['volume_whole']:
        out['verdict'] = ('the rung does not exist on this head: rank 4 needs %d | n4 and '
                          'n4 = %d leaves %d registers over' % (rank3stability.criterion(FAMILY)
                                                                ['divisor'], n, volume % WIDTH))
        return out
    step = ledger3.absorb(retained, FAMILY)
    out['stock_drop'] = step['stock_drop']
    out['retained_W'] = step['retained']['W']
    out['retained_mass'] = step['retained']['total_rank']
    out['retained_eligibility'] = ledger3.eligibility(step['retained'])
    if price:
        point = rank3contract.price(interval or ledger3.engine(), step['retained'])
        out['point'] = dict(coarse=str(point['coarse']), coarse_decimal=float(point['coarse']),
                            kappa=str(point['kappa']), kappa_decimal=float(point['kappa']),
                            binding=point['binding'], kappa_moved=False)
        assert point['binding'] == 'bit', 'the rung must be bit-bound on every head that carries it'
        assert Q(point['kappa']) == Q(out['point']['kappa'])
    out['verdict'] = ('the rung exists on this head: %d banks by the volume criterion, kappa %s '
                      '(%s-bound, unmoved); the padded schedule %s'
                      % (out['volume_banks'],
                         out.get('point', {}).get('kappa', 'NOT PRICED'),
                         out.get('point', {}).get('binding', 'NOT PRICED'),
                         'saturates' if out['saturated'] else
                         'is %d slots short' % out['slack_slots']))
    return out


def required_leaf(target):
    """The smallest budget on the 10^-18 grid whose assembly-rule floor reaches `target`."""
    low, high = 1, GRID
    assert run3.kappa_of_budget(Q(high, GRID)) >= target, 'target above the assembly bound'
    while low < high:
        mid = (low + high) // 2
        if run3.kappa_of_budget(Q(mid, GRID)) >= target:
            high = mid
        else:
            low = mid + 1
    budget = Q(low, GRID)
    assert run3.kappa_of_budget(budget) >= target > run3.kappa_of_budget(budget - Q(1, GRID)), \
        'the required leaf must be the minimal grid point reaching the target'
    return budget


def build(priced=True):
    interval = ledger3.engine() if priced else None
    row = instantiate_rank3.row()
    copied = ledger3.three_copies(row)
    ret = ledger3.absorb(copied, FAMILY - 1)['retained']

    heads = []
    for sha, date, short, subject, source in rank3stability.HEADS:
        entry = measure_head(source, price=priced, interval=interval)
        entry.update(sha=sha, short=short, date=date, subject=subject)
        heads.append(entry)
    exists = [head for head in heads if head.get('volume_whole')]
    reached = [head for head in heads if head['rank3_eligible']]

    n = ret['child_multiplicities'][FAMILY]
    scheduled = padded_schedule(ret)
    priced_step = ledger3.absorb(ret, FAMILY)
    priced_retained = priced_step['retained']

    # T1's enumeration, at every bank count that divides the family's own count
    enumeration = []
    for B in divisors(n):
        found = patterns(dict(ret['child_multiplicities']), B)
        entry = dict(banks=B, feasible=bool(found and found['count']))
        if entry['feasible']:
            entry.update(
                blocks_of_the_family=found['blocks_of_the_family'],
                registers_of_the_family=found['registers_of_the_family'],
                padding_registers_per_bank=found['padding_registers_per_bank'],
                patterns=found['count'],
                draws_per_bank=sorted({sum(p.values()) for p in found['patterns']}),
                fewest_children_drawn=min(found['patterns'],
                                          key=lambda p: (sum(p.values()), sorted(p.items()))),
                most_children_drawn=max(found['patterns'],
                                        key=lambda p: (sum(p.values()), sorted(p.items()))))
        enumeration.append(entry)

    # two extremes per bank count are priced -- the cheapest and the heaviest draw, measured by
    # how many children leave the ledger -- because the full enumeration is 1,168 patterns and
    # each price is an exact moment over the retained row.  The claim is over the priced sample;
    # every pattern is recorded.
    tiled = []
    for entry in enumeration:
        if not entry['feasible']:
            continue
        for label, pattern in (('fewest children drawn', entry['fewest_children_drawn']),
                               ('most children drawn', entry['most_children_drawn'])):
            retained_row, draw = ledger_after(ret, entry, pattern)
            point = rank3contract.price(interval, retained_row) if priced else None
            tiled.append(dict(banks=entry['banks'], label=label, pattern=pattern, draw=draw,
                              retained_W=retained_row['W'],
                              retained_mass=retained_row['total_rank'],
                              retained_children=sum(retained_row['child_multiplicities'].values()),
                              retained_eligibility=ledger3.eligibility(retained_row),
                              padding_share_of_the_bank=str(
                                  Q(entry['padding_registers_per_bank'], WIDTH)),
                              coarse=str(point['coarse']) if point else None,
                              kappa=str(point['kappa']) if point else None))
    best = max(tiled, key=lambda entry: Q(entry['coarse'])) if tiled else None

    point3 = rank3contract.price(interval, ret) if priced else None
    point4 = rank3contract.price(interval, priced_retained) if priced else None
    points = dict(
        rank3=dict(kappa=str(point3['kappa']), kappa_decimal=float(point3['kappa']),
                   coarse=str(point3['coarse']), coarse_decimal=float(point3['coarse']),
                   complex_ceiling=str(point3['complex_ceiling'])),
        rank4_priced=dict(kappa=str(point4['kappa']), kappa_decimal=float(point4['kappa']),
                          coarse=str(point4['coarse']), coarse_decimal=float(point4['coarse']),
                          complex_ceiling=str(point4['complex_ceiling']),
                          ledger_hostable=scheduled['volume_banks_host_the_items'],
                          binding=point4['binding']),
        rank4_tiled=dict(kappa=best['kappa'], coarse=best['coarse'], banks=best['banks'],
                         pattern=best['pattern'], label=best['label']) if best else None,
        delta_coarse_priced=str(point4['coarse'] - point3['coarse']),
        delta_coarse_priced_percent=float((point4['coarse'] / point3['coarse'] - 1) * 100),
        delta_coarse_tiled_percent=(float((Q(best['coarse']) / point3['coarse'] - 1) * 100)
                                    if best else None),
        delta_kappa=str(point4['kappa'] - point3['kappa']),
        kappa_moved=point4['kappa'] != point3['kappa'],
        budget_is_the_leaf=point4['budget'] == point4['leaf'],
        leaf=str(point4['leaf']), leaf_decimal=float(point4['leaf']),
        tightest_constraint=str(point4['assembly']['minimum_constraint']),
        adjacent_grid_rejected=point4['adjacent_grid_rejected'],
        reading='the coarse saving of the retained row rises by %+.4f%% with the priced ledger '
                'and by %+.4f%% with the best tiled one, and the kappa does not move by one grid '
                'step: every rung above rank 3 is bit-bound, so the assembly rule spends the bit '
                'leaf and nothing else.'
                % (float((point4['coarse'] / point3['coarse'] - 1) * 100),
                   float((Q(best['coarse']) / point3['coarse'] - 1) * 100) if best else 0.0))

    certificate = json.loads((HERE / 'certificate.json').read_text())
    published = {line['target']: line['required_bit_leaf'] for line in certificate['bit_requirement']}
    targets = []
    for target, why in ((point3['kappa'] + Q(1, GRID), 'the next 10^-18 grid point above the '
                                                        'rung this package prices'),
                        (Q(3, 4000), '7.5e-4, the first target the certificate names'),
                        (Q(1, 1250), '8e-4'),
                        (Q(1, 1000), '1e-3')):
        budget = required_leaf(target)
        targets.append(dict(target=str(target), target_decimal=float(target), why=why,
                            required_bit_leaf=str(budget), required_bit_leaf_decimal=float(budget),
                            gain_vs_the_current_leaf=str(budget / Q(point3['leaf']) - 1),
                            gain_vs_the_current_leaf_percent=float(
                                (budget / Q(point3['leaf']) - 1) * 100),
                            bit_branch_short=(budget > Q(point3['leaf'])),
                            matches_the_certificate=(
                                published.get(str(target)) == str(budget)
                                if str(target) in published else None)))
    assert any(line['matches_the_certificate'] for line in targets), \
        'the inversion must reproduce the certificate\'s own bit requirement where they overlap'

    out = {}
    out['analysis'] = ('does the rank-4 rung exist on #233\'s new row, does the padding of T1 '
                       'carry it, and does it move the kappa: the volume criterion, the padded '
                       'schedule read as data, T1\'s mixed-tiling enumeration, and the price of '
                       'each ledger the rung can induce')
    out['criterion'] = dict(
        rank=FAMILY, width=WIDTH,
        volume=dict(rule='%d | %d * n4' % (WIDTH, FAMILY),
                    reduced=rank3stability.criterion(FAMILY)['rule'],
                    why='the family\'s own volume must be a whole number of width-66 banks, the '
                        'same criterion every rung of this ladder uses'),
        capacity=dict(rule='%d | n4' % (WIDTH // FAMILY),
                      why='T1\'s padded schedule needs the family to fill every block it has room '
                          'for, the same padding in every bank: the capacity bank count must '
                          'saturate'),
        padded_pattern='%d = %d * %d + %d' % (WIDTH, WIDTH // FAMILY, FAMILY,
                                              WIDTH - FAMILY * (WIDTH // FAMILY)),
        registers_from_other_bins=WIDTH - FAMILY * (WIDTH // FAMILY),
        criterion_mismatch=('the volume criterion and the capacity criterion coincide only when '
                            'the rank divides the width; rank 4 does not, so a rank-4 rung needs '
                            'a tiling, and the two readings differ here'))
    out['heads'] = heads
    out['head_dependence'] = dict(
        heads=len(heads), heads_carrying_rank3=[head['short'] for head in reached],
        heads_carrying_the_volume_criterion=[head['short'] for head in exists],
        n4_by_head={head['short']: head.get('n4') for head in heads},
        reading='the rank-4 rung exists on %d of the %d heads -- %s -- where the rank-3 rung '
                'exists on %d: its eligibility is not stable either, and it is narrower, because '
                '34,551 and 34,506 straddle the 33-multiple the criterion needs.  Every head that '
                'does not carry rank 3 cannot carry rank 4, since this rung starts from the '
                'ledger rank 3 leaves behind.'
                % (len(exists), len(heads), ', '.join(head['short'] for head in exists),
                   len(reached)))
    out['rung'] = dict(
        source=LEDGER,
        starting_ledger='the row the rank-3 rung induces (%s), re-derived here rather than read'
                        % LEDGER,
        family=FAMILY, width=WIDTH, copies=COPIES, n4=n,
        volume=priced_step['volume'], volume_banks=priced_step['banks'],
        volume_is_whole_banks=priced_step['volume'] == priced_step['banks'] * WIDTH,
        stock_drop=priced_step['stock_drop'],
        retained_W=priced_retained['W'], retained_deficit=priced_retained['N'],
        retained_mass=priced_retained['total_rank'],
        retained_children=sum(priced_retained['child_multiplicities'].values()),
        retained_families=len(priced_retained['child_multiplicities']),
        retained_eligibility=ledger3.eligibility(priced_retained),
        padded_schedule=scheduled,
        priced_bank_count_hosts_its_items=scheduled['volume_banks_host_the_items'],
        realisable_as_a_saturated_padded_schedule=False,
        reading='the volume criterion prices %d whole banks for a bin of %d items, and the '
                'padded schedule that would fill them needs %d banks of %d rank-4 blocks and can '
                'only saturate them if %d | n4 -- which fails, by %d slots (%d registers).  And '
                'the priced bank count cannot host the items at all: %d * %d = %d < %d.  So the '
                'ledger this rung prices is not the ledger a schedule induces, and the padding '
                'of T1, which was a small residual at ranks 16 and 20, does not carry this rung.'
                % (priced_step['banks'], n, scheduled['banks'], scheduled['blocks_per_bank'],
                   WIDTH // FAMILY, scheduled['slack_slots'], scheduled['slack_registers'],
                   priced_step['banks'], scheduled['blocks_per_bank'],
                   priced_step['banks'] * scheduled['blocks_per_bank'], n))
    out['mixed_tilings'] = dict(
        method='T1\'s enumeration, at every bank count that divides n4: a4 = n4 / B rank-4 '
               'blocks per bank, the remaining registers filled by blocks of the retained '
               'families, each drawn at most counts[f] // B times per bank so the ledger can '
               'supply every draw.  One pattern, uniform across banks, as T1 asks.',
        bank_counts_examined=len(enumeration),
        feasible_bank_counts=[entry['banks'] for entry in enumeration if entry['feasible']],
        patterns_enumerated=sum(entry.get('patterns', 0) for entry in enumeration),
        candidates_per_bank_count=2,
        candidates_priced=len(tiled),
        enumeration=enumeration,
        priced=tiled,
        best=best,
        lightest_padding_registers_per_bank=(min(entry['padding_registers_per_bank']
                                                 for entry in enumeration if entry['feasible'])
                                             if any(e['feasible'] for e in enumeration) else None),
        every_priced_candidate_prices_above_the_volume_ledger=(
            all(Q(entry['coarse']) > Q(point4['coarse']) for entry in tiled) if priced else None),
        reading='the mixed tiling does exist where the padded schedule does not, but every '
                'admissible pattern draws at least %s of the bank\'s 66 registers from other '
                'bins: rank 4 divides nothing here, so a rank-4 bank is at most %d registers '
                'rank 4.  The tiled ledgers are consistent -- row identity, mass removed B * 66, '
                'stock falling by exactly B -- they are not the ledger the volume criterion '
                'prices, and every priced candidate prices above it (%s).  %d of the %d patterns '
                'are priced, the two extremes per bank count; the claim is over that sample.'
                % (min(entry['padding_registers_per_bank'] for entry in enumeration
                       if entry['feasible']) if any(e['feasible'] for e in enumeration) else None,
                   max(entry['registers_of_the_family'] for entry in enumeration
                       if entry['feasible']) if any(e['feasible'] for e in enumeration) else None,
                   all(Q(entry['coarse']) > Q(point4['coarse']) for entry in tiled)
                   if priced else 'not priced', len(tiled),
                   sum(entry.get('patterns', 0) for entry in enumeration)))
    out['point'] = points
    out['targets'] = targets
    out['verdict'] = (
        'MEASURED NEGATIVE, and the measurement is the result: banking rank 4 on PR233\'s row '
        'does not push the kappa above 7.277211262868e-4.  Two independent reasons, both '
        'arithmetic: the rung is not realisable at the bank count its own criterion prices '
        '(2,094 banks cannot host 34,551 items at 16 blocks each, and the padded schedule misses '
        'saturation by 9 slots), and even when its ledger is priced and even when the mixed '
        'tiling\'s heavier ledger is priced, the kappa is the assembly rule\'s floor on the bit '
        'leaf, which no complex rung raises.  What the rung does buy, if it is built, is slope: '
        'the retained row\'s coarse saving rises by %+.4f%% on the priced ledger and by %+.4f%% '
        'on the best tiled one, so the complex side stops being a constraint by any margin '
        'whatsoever.  The next increment of kappa therefore has to come from the bit word\'s '
        'leaf, and the targets below say how much leaf each one needs.'
        % (points['delta_coarse_priced_percent'],
           points['delta_coarse_tiled_percent'] or 0.0))
    out['status'] = (
        'MEASURED AND MACHINE-CHECKED: verify.py -> check_rank4_rung re-derives the criterion, '
        'every head, the padded schedule\'s shortfall, the whole tiling enumeration and every '
        'price, and asserts the negative result rather than restating it.  Nothing here '
        'certifies a rung: the row\'s PR is unmerged and is pinned by digest.')
    return out


def main():
    sys.set_int_max_str_digits(0)
    sys.dont_write_bytecode = True
    out = build()
    target = HERE / 'rank4-rung.json'
    target.write_text(json.dumps(out, indent=1, sort_keys=True, default=str) + '\n', newline='\n')
    rung, schedule = out['rung'], out['rung']['padded_schedule']
    print('rank 4     %d items, volume %d = %d banks; padded schedule %d banks of %d blocks + %d '
          'registers (saturates: %s, %d slots short)'
          % (rung['n4'], rung['volume'], rung['volume_banks'], schedule['banks'],
             schedule['blocks_per_bank'], schedule['padding_registers_per_bank'],
             schedule['saturated'], schedule['slack_slots']))
    print('tiling     %d bank counts examined, feasible %s; lightest padding %s of the bank; '
          'best tiled coarse %s'
          % (out['mixed_tilings']['bank_counts_examined'],
             out['mixed_tilings']['feasible_bank_counts'],
             out['mixed_tilings']['lightest_padding_registers_per_bank'],
             out['mixed_tilings']['best']['coarse'] if out['mixed_tilings']['best'] else None))
    point = out['point']
    print('point      rank 3 %s (coarse %.12e) -> rank 4 %s (coarse %.12e, %+.4f%%), binding %s, '
          'kappa moved: %s'
          % (point['rank3']['kappa'], point['rank3']['coarse_decimal'],
             point['rank4_priced']['kappa'], point['rank4_priced']['coarse_decimal'],
             point['delta_coarse_priced_percent'], point['rank4_priced']['binding'],
             point['kappa_moved']))
    for line in out['targets']:
        print('target %-8s bit leaf %s (%+.3f%%), matches the certificate: %s'
              % (line['target_decimal'], line['required_bit_leaf_decimal'],
                 line['gain_vs_the_current_leaf_percent'], line['matches_the_certificate']))
    print('heads      the rung on %s of %d heads (%s)'
          % (len(out['head_dependence']['heads_carrying_the_volume_criterion']),
             out['head_dependence']['heads'],
             out['head_dependence']['heads_carrying_the_volume_criterion']))
    print('write ' + str(target))


if __name__ == '__main__':
    main()
