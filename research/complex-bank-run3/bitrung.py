#!/usr/bin/env python3
"""The bit-side rung: a second absorption on #219's rung-1 word, and what it does to kappa.

This ladder has been **bit-bound since rung 2**.  The assembly's floor is a function of the budget,
the budget is `min(bit leaf, complex branch)`, and the complex branch has carried room it could not
spend: on #233's row the complex side reaches `417325324839139/5*10^17` = 8.346506496783e-4 while
the bit leaf stays at 7.282510899902e-4, so the rank-3 rung prices 7.277211262868e-4 and the rung
above it (`rank4rung.py`) shows that no further *complex* rung moves the kappa by one grid step.
The lever the package kept naming is the one measured here: **the bit word's own retained ledger**,
one absorption further.

What the bit leaf is, re-derived rather than quoted.  #219's rung 1 absorbs the rank-22 family of
the PR200/PR205 packed bit word into 6,116 whole width-72 banks, leaving a retained row of
`W = 50,286` roles, rank mass 3,614,784, deficit 5,808 and 857,622 children over 21 ranks.  The
leaf is that row's certified paid saving, bootstrapped through #185's three-level chain.  Every
family of the retained row whose **own volume fills whole banks** (`72 | r * n_r`) can leave the
same way, and each one lowers the retained mass, so the leaf rises.

The measurement, exhaustively over rungs of up to three families: thirteen of the retained row's
21 families can leave into whole banks or into the padded schedule a bank admits, so 13 + 78 + 286
= **377 rungs**, every one priced by the vendored interval-moment engine:

| absorb | banks | retained W | bit leaf | kappa | gain over the rank-3 rung |
| --- | ---: | ---: | ---: | ---: | ---: |
| rank 20 | 5,280 | 45,006 | 7.957727174054441e-4 | 7.95139966713414e-4 | +9.2644% |
| ranks 4, 20 | 6,878 | 43,408 | 8.337650404202950e-4 | 8.33070455398376e-4 | +14.4766% |
| **ranks 7, 8, 20** | **7,342** | **42,944** | **8.349765438523530e-4** | **8.33954588938818e-4** | **+14.5981%** |

so the package's point moves from `1819302815717/25*10^14` to
**`416977294469409/500000000000000000` = 8.339545889388e-4**, on the same pinned words -- and it
stops being bit-bound: the leader's leaf `8.349765438523530e-4` is *above* the complex branch
`(1-beta) * 8.346506496783e-4 - weak`, so the budget is the complex side and every further bit
absorption is spent on a wall it no longer moves.  That is not a property of the leader: **108 of
the 377 rungs land on the same kappa**, the whole plateau that clears the complex branch.  The
plateau is why the rung is quoted as a kappa rather than as a construction: only the bank count
distinguishes the rungs on it, and the cheapest one (7,342 banks against 15,018 for rank 21 alone)
is the one recorded.

Two things this module reads as data rather than asserting:

* **the padding of T1, one word over.**  Rank 8 divides the width (9 blocks per bank, 838 banks,
exactly filled, `n_r == capacity * banks`); ranks 7 and 20 do not: rank 7's schedule is 10 blocks
and 2 registers of padding in every bank over 1,224 banks, rank 20's is 3 blocks and 12 registers
over 5,280 banks, and the bank count each family's *own* volume criterion prices (1,190 and 4,400)
cannot host its items at that capacity (11,900 < 12,240 and 13,200 < 15,840) -- the same shortfall
`rank4rung.py` found on the complex side, here measured with the singleton supply that makes it a
positive rather than a gap.
* **where this rung stops.**  The bit leaf is no longer the wall, so the complex branch caps this
  ladder's point at its ceiling -- the next increment has to come from the complex side, not from
  this word.

Nothing here is built: the absorbed families need the new residual types the suppliers' proofs
reserve, the rows are pinned by digest to unmerged branches, and C1-C7 and R1-R4 stand exactly as
the rest of the package states them.  This is a **priced target**, one rung deeper into the only
side that still binds.
"""
import itertools
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import instantiate_rank3  # noqa: E402
import ledger3  # noqa: E402
import run3  # noqa: E402

RUN1 = HERE / 'references' / 'pr219-run1'
WIDTH = 72
COPIES = 3
GRID = 10 ** 18
MAX_DEPTH = 3
SINGLETON = 1
COMPLEX_FAMILY = 3
CONTRACT = 'export-contract-rank3.json'


def rung1_state(schedule):
    """The rung-1 retained row, in the shape the vendored arithmetic works with."""
    kept = {int(r): int(n) for r, n in schedule['retained_profile']['histogram'].items()}
    state = dict(m=int(schedule['retained_profile']['m']),
                 W=int(schedule['retained_profile']['W_after']),
                 deficit=int(schedule['retained_profile']['deficit']),
                 mass=int(schedule['retained_profile']['rank_mass_after']),
                 histogram=kept)
    assert state['m'] == WIDTH, 'the bit word banks at width 72'
    assert sum(r * n for r, n in kept.items()) == state['mass'], 'row identity: rank mass'
    assert state['m'] * state['W'] == state['mass'] + state['deficit'], 'row identity: stock'
    return state


def absorption(state, rank, padding=False):
    """One family leaving the row into whole banks, or the reason it cannot.

    Two readings of the same criterion, distinguished because they are not the same rung.  The
    **volume** reading is the one every rung of this ladder prices: the family's own volume is a
    whole number of banks (`m | r * n_r`).  The **padded** reading is what a bank can actually
    host when the rank does not divide the width: `capacity = m // r` blocks of the family plus
    `m mod r` registers of padding in every bank, so it needs saturation (`capacity | n_r`) and a
    retained bin that can supply the padding.  Both keep the row identity
    `m * W = mass + deficit`, which is checked here rather than assumed.
    """
    n = state['histogram'].get(rank)
    if not n:
        return dict(rank=rank, present=False, why='the retained row holds no rank-%d family' % rank)
    volume = rank * n
    capacity = WIDTH // rank
    padding_registers = WIDTH - rank * capacity
    if not padding:
        if volume % WIDTH:
            return dict(rank=rank, present=True, items=n, volume=volume, banks=None,
                        why='volume %d is not a whole number of width-%d banks' % (volume, WIDTH))
        banks, drawn, drawn_registers = volume // WIDTH, {}, 0
    else:
        if n % capacity:
            return dict(rank=rank, present=True, items=n, volume=volume, banks=None,
                        capacity_blocks_per_bank=capacity,
                        padding_registers_per_bank=padding_registers,
                        why='the padded schedule must saturate: %d | n_%d fails' % (capacity, rank))
        banks = n // capacity
        drawn_registers = banks * padding_registers
        drawn = {SINGLETON: drawn_registers}
        volume = banks * WIDTH
    histogram = dict(state['histogram'])
    histogram[rank] = histogram[rank] - (capacity * banks if padding else n)
    assert histogram[rank] == 0, 'the absorbed family must leave whole'
    del histogram[rank]
    for filler, count in drawn.items():
        histogram[filler] = histogram.get(filler, 0) - count
        assert histogram[filler] >= 0, 'the retained ledger cannot supply the padding'
        if histogram[filler] == 0:
            del histogram[filler]
    mass = state['mass'] - volume
    if (mass + state['deficit']) % WIDTH:
        return dict(rank=rank, present=True, items=n, volume=volume, banks=banks,
                    why='the stock after the absorption is not integral')
    stock = (mass + state['deficit']) // WIDTH
    row = dict(m=WIDTH, W=stock, deficit=state['deficit'], mass=mass, histogram=histogram)
    assert sum(r * c for r, c in histogram.items()) == mass, 'rank mass after the absorption'
    assert max(histogram) >= 1, 'a ledger must remain'
    return dict(rank=rank, present=True, items=n, volume=volume, banks=banks,
                reading='padded' if padding else 'volume',
                capacity_blocks_per_bank=capacity, padding_registers_per_bank=padding_registers,
                padding_registers_banks=drawn_registers if padding else 0,
                stock_before=state['W'], stock_after=stock, stock_drop=state['W'] - stock,
                mass_before=state['mass'], mass_after=mass,
                children_after=sum(histogram.values()), maxchild_after=max(histogram),
                state=row, why=None)


def scheduled(state, rank):
    """The absorption a bank schedule can actually host: padded where the rank needs it."""
    volume = absorption(state, rank, padding=False)
    if volume.get('banks') and WIDTH % rank == 0:
        return volume, volume
    padded = absorption(state, rank, padding=True)
    return volume, padded


def chain_leaf(arithmetic, im, state):
    """#185's three-level bootstrap on a retained row, exactly as the vendored build runs it.

    The vendored `build()` asserts that the rank-22 absorption clears the complex cap, which is
    true of the rung-1 row and false of a row that has absorbed further -- the whole point here is
    that the extended leaf goes *above* the complex branch.  The chain is therefore re-run on the
    retained row with the same seed (`PR200`'s published ordinary saving) and the same recurrence,
    and `build()` calibrates it by reproducing the rung-1 leaf exactly.
    """
    bit = json.loads((RUN1 / 'references' / 'pr200-bit.certificate.json').read_text())['bit']
    seed = Q(bit['coarse']['ordinary_saving'])
    row = arithmetic.profile(WIDTH, state['W'], state['histogram'], state['deficit'])
    coarse = Q(arithmetic.certify(im, row, True)['saving'])
    chain = [seed]
    for _ in range(3):
        a = (1 - coarse) * coarse + coarse * chain[-1]
        assert chain[-1] < a < coarse < 1 - a, 'the bootstrap chain must stay strictly ordered'
        chain.append(a)
    return dict(seed=seed, chain=chain, leaf=chain[-1], coarse=coarse)


def apply_sequence(state, ranks, padded=()):
    """A rung: the families leave in order, each by the reading the schedule gives it."""
    steps, banks, rows = [], 0, []
    for rank in ranks:
        volume, chosen = scheduled(state, rank)
        assert chosen.get('banks'), 'the family cannot leave: %s' % chosen.get('why')
        state = chosen['state']
        banks += chosen['banks']
        steps.append(dict(rank=rank, reading=chosen['reading'], banks=chosen['banks'],
                          stock_after=chosen['stock_after'], mass_after=chosen['mass_after'],
                          padding_registers=chosen.get('padding_registers_banks', 0),
                          padding_registers_per_bank=chosen['padding_registers_per_bank'],
                          capacity_blocks_per_bank=chosen['capacity_blocks_per_bank'],
                          volume_reading_banks=volume.get('banks'),
                          volume_reading_hosts_the_items=(
                              None if not volume.get('banks') else
                              volume['banks'] * (WIDTH // rank) >= volume['items'])))
        rows.append(chosen)
    return state, steps, banks, rows


def build():
    """The whole measurement: the priced rungs, the leader, its schedule and its point."""
    schedule_module, arithmetic = ledger3.run1()
    schedule = schedule_module.build()
    im = ledger3.engine()
    base = rung1_state(schedule)

    # --- calibration: the unextended row must reproduce the vendored rung-1 leaf exactly
    published = json.loads((HERE / 'certificate.json').read_text())['calibrations']['run1']
    rung1 = chain_leaf(arithmetic, im, base)
    assert rung1['coarse'] == Q(published['bit_coarse_after']), \
        'the re-derived rung-1 coarse saving must be the published one'
    assert rung1['leaf'] == Q(published['bit_leaf']), 'the re-derived leaf must be the published one'

    # --- the families the retained row can hand to a bank, by both readings
    families = []
    for rank in sorted(base['histogram']):
        volume, padded = scheduled(base, rank)
        families.append(dict(
            rank=rank, items=base['histogram'][rank], volume=volume['volume'],
            volume_banks=volume.get('banks'), volume_is_whole=bool(volume.get('banks')),
            divides_the_width=(WIDTH % rank == 0),
            capacity_blocks_per_bank=WIDTH // rank,
            capacity_banks=padded.get('banks'), padding_registers_per_bank=WIDTH % rank,
            padded_saturates=(WIDTH % rank != 0 and padded.get('banks') is not None),
            padded_why=None if padded.get('banks') else padded.get('why')))
    absorbable = [entry['rank'] for entry in families
                  if (entry['volume_is_whole'] and entry['divides_the_width'])
                  or entry['padded_saturates']]

    # --- the complex branch, once: the side this ladder's bit work is spent against
    interval = ledger3.engine()
    contract = json.loads((HERE / CONTRACT).read_text())
    retained = ledger3.absorb(ledger3.three_copies(instantiate_rank3.row()),
                              instantiate_rank3.FAMILY)['retained']
    complex_coarse = Q(ledger3.certify(interval, retained)['saving'])
    assert complex_coarse == Q(contract['point']['coarse']), \
        'the complex branch must be the one this package already sells'
    complex_branch = (1 - run3.BETA) * complex_coarse - run3.WEAK

    # --- the exhaustive screen: every rung of up to MAX_DEPTH families, priced to the point
    priced = []
    for depth in (1, 2, 3):
        for combo in itertools.combinations(absorbable, depth):
            state, steps, banks, rows = apply_sequence(base, combo)
            leaf = chain_leaf(arithmetic, im, state)
            budget, bound, kappa = run3.frontier_kappa(leaf['leaf'], complex_coarse)
            priced.append(dict(ranks=list(combo), depth=depth, banks=banks, stock=state['W'],
                               mass=state['mass'], children=sum(state['histogram'].values()),
                               families_after=len(state['histogram']),
                               leaf=str(leaf['leaf']), leaf_decimal=float(leaf['leaf']),
                               coarse=str(leaf['coarse']), coarse_decimal=float(leaf['coarse']),
                               budget=str(budget), kappa=str(kappa), kappa_decimal=float(kappa),
                               binding='bit' if budget == leaf['leaf'] else 'complex',
                               readings=[step['reading'] for step in steps],
                               padding_registers=sum(step['padding_registers'] for step in steps)))
    leader = min((entry for entry in priced if Q(entry['kappa']) == max(Q(e['kappa'])
                                                                        for e in priced)),
                 key=lambda entry: (entry['banks'], entry['ranks']))
    at_the_cap = [entry['ranks'] for entry in priced if Q(entry['kappa']) == Q(leader['kappa'])]
    return dict(schedule=schedule, arithmetic=arithmetic, im=im, base=base, rung1=rung1,
                families=families, absorbable=absorbable, priced=priced, leader=leader,
                at_the_cap=at_the_cap, complex_coarse=complex_coarse,
                complex_branch=complex_branch, published=published)


def point(state, arithmetic, im, published_top, contract_point):
    """The rung's own price: the extended leaf, the complex branch, the 47-constraint assembly."""
    interval = ledger3.engine()
    row = instantiate_rank3.row()
    retained = ledger3.absorb(ledger3.three_copies(row), instantiate_rank3.FAMILY)['retained']
    complex_coarse = Q(ledger3.certify(interval, retained)['saving'])
    assert complex_coarse == Q(contract_point['coarse']), \
        'the complex branch must be the one this package already sells'
    leaf = chain_leaf(arithmetic, im, state)
    budget, bound, kappa = run3.frontier_kappa(leaf['leaf'], complex_coarse)
    supplier = json.loads(run3.PR193.read_text())
    supplier['assembly']['finite_bridge']['rows']['degree_gap'] = Q(
        supplier['assembly']['finite_bridge']['rows']['degree_gap'])
    assembly = run3.assemble(supplier, budget, complex_coarse, kappa)
    adjacent_rejected = True
    try:
        run3.assemble(supplier, budget, complex_coarse, kappa + Q(1, GRID))
    except AssertionError:
        pass
    else:
        adjacent_rejected = False
    complex_branch = (1 - run3.BETA) * complex_coarse - run3.WEAK
    assert adjacent_rejected, 'the adjacent 10^-18 point must be rejected'
    assert budget == min(leaf['leaf'], complex_branch), 'the budget must be the smaller branch'
    binding = 'bit' if budget == leaf['leaf'] else 'complex'
    # The tightest of the 47 constraints says which branch binds, exactly: at a bit budget it is
    # the design backoff `lambda - tau = a * eta`, and at a complex budget it is the weak haircut
    # `(1-beta) * complex - weak - a = weak` that put the budget there.  Asserted, not described.
    expected = budget * run3.ETA if binding == 'bit' else run3.WEAK
    assert assembly['minimum_constraint'] == expected, \
        'the tightest of the 47 constraints must be the binding branch\'s own haircut'
    assert assembly['minimum_constraint'] > 0
    assert kappa > Q(published_top), 'the extended rung must beat the point this package sells'
    return dict(complex_coarse=complex_coarse, complex_branch=complex_branch,
                complex_ceiling=ledger3.ceiling(complex_coarse),
                leaf=leaf['leaf'], chain=leaf, budget=budget, bound=bound, kappa=kappa,
                binding=binding, assembly=assembly, adjacent_grid_rejected=adjacent_rejected,
                leaf_headroom=leaf['leaf'] - budget,
                complex_ceiling_gap=ledger3.ceiling(complex_coarse) - kappa,
                headroom_to_the_complex_branch=complex_branch - leaf['leaf'],
                shares_of_the_complex_branch=leaf['leaf'] / complex_branch,
                gain_vs_the_rank3_rung=kappa / Q(published_top) - 1,
                rung1_leaf=Q(json.loads((HERE / 'certificate.json').read_text())
                              ['calibrations']['run1']['bit_leaf']))


def scheduled_reading(steps):
    """Why a bank hosts the schedule and not the volume criterion, read off the steps themselves.

    A family whose rank divides the width is exactly filled (`n_r == capacity * banks`, no padding),
    and a family whose rank does not is padded in every bank by `m mod rank` registers drawn from
    the singleton bin -- and the bank count its own volume criterion prices is too small to host its
    items.  Written from the measured steps rather than transcribed, so a different leader cannot
    leave a stale sentence behind.
    """
    exact = ['rank %d divides the width (%d blocks per bank, %d banks, no padding)'
             % (step['rank'], step['capacity_blocks_per_bank'], step['banks'])
             for step in steps if step['reading'] == 'volume']
    padded = []
    for step in steps:
        if step['reading'] != 'padded':
            continue
        line = ('rank %d does not: %d blocks and %d registers of padding in every bank, and its '
                'own volume criterion prices %d banks, which could host only %d of its items at '
                '%d per bank'
                % (step['rank'], step['capacity_blocks_per_bank'],
                   step['padding_registers_per_bank'], step['volume_reading_banks'],
                   step['volume_reading_banks'] * step['capacity_blocks_per_bank'],
                   step['capacity_blocks_per_bank']))
        padded.append(line)
    return ('the leader by family: ' + '; '.join(exact + padded) + '.  %d registers of padding in '
            'all, drawn as a partial removal from the singleton bin.  The rung prices the schedule '
            'a bank admits -- every bank exactly filled -- not the accounting the volume criterion '
            'alone gives.'
            % sum(step['padding_registers'] for step in steps))


def build_artifact():
    """The full artifact: the screen, the leader, its schedule reading and its price."""
    measured = build()
    base, leader = measured['base'], measured['leader']
    certificate = json.loads((HERE / 'certificate.json').read_text())
    contract = json.loads((HERE / CONTRACT).read_text())
    published_top = Q(contract['point']['kappa'])
    assert Q(certificate['top']['kappa']) < published_top, \
        'the point this rung builds on must be the package\'s top, above its ladder'
    state, steps, banks, rows = apply_sequence(base, leader['ranks'])
    assert state['W'] == leader['stock'] and banks == leader['banks'], 'the leader, re-applied'
    price = point(state, measured['arithmetic'], measured['im'], published_top, contract['point'])
    assert price['leaf'] == Q(leader['leaf']), \
        'the leaf priced here must be the one the screen measured for the leader'
    top_kappa = max(Q(entry['kappa']) for entry in measured['priced'])
    assert Q(leader['kappa']) == top_kappa, 'the leader must carry the best kappa of the screen'
    tied = [e for e in measured['priced'] if Q(e['kappa']) == top_kappa]
    assert leader['ranks'] == min(tied, key=lambda e: (e['banks'], e['ranks']))['ranks'], \
        'the leader must be the cheapest of the kappa-best rungs'

    out = {}
    out['analysis'] = (
        'the bit side is the only side that has bound this ladder since rung 2: this module '
        'enumerates every family of the rung-1 retained bit row whose own volume fills whole '
        'width-72 banks, prices every rung of up to three of them with the vendored engine, reads '
        'the block schedule each family needs, and prices the resulting point through the '
        "assembly rule -- so the kappa moves on the side that binds instead of on the side that "
        'has room')
    out['width'] = WIDTH
    out['copies'] = COPIES
    out['criterion'] = dict(
        volume='m | rank * n_rank: the family\'s own volume is a whole number of banks',
        padded='capacity = m // rank blocks per bank plus m mod rank registers of padding, drawn '
               'from the singleton bin, uniform across banks',
        saturation='the padded reading needs capacity | n_rank, and the bank count its own volume '
                   'criterion prices must be able to host the items: banks * capacity >= n_rank')
    out['rung1'] = dict(
        source='references/pr219-run1/schedule.py + arithmetic.py (the vendored rung-1 package)',
        retained_W=base['W'], retained_deficit=base['deficit'], retained_mass=base['mass'],
        retained_children=sum(base['histogram'].values()), retained_families=len(base['histogram']),
        retained_maxchild=max(base['histogram']),
        coarse_saving=str(measured['rung1']['coarse']), seed=str(measured['rung1']['seed']),
        bootstrap_chain=[str(a) for a in measured['rung1']['chain']],
        leaf=str(measured['rung1']['leaf']), leaf_decimal=float(measured['rung1']['leaf']))
    out['families'] = measured['families']
    out['absorbable'] = measured['absorbable']
    out['screen'] = dict(
        depth=MAX_DEPTH, rungs_priced=len(measured['priced']),
        engine='PR200\'s exact interval moment, vendored, on the bit branch (with the rare-class '
               'fallback)',
        leader_rule='highest kappa; ties broken by the fewest banks, then by the sorted ranks',
        rungs=measured['priced'],
        plateau=dict(rungs_at_the_cap=len(measured['at_the_cap']),
                     ranks=measured['at_the_cap'][:12],
                     why='once a rung\'s bit leaf clears the complex branch the budget is the '
                         'branch, so every such rung lands on the same point: the screen is not '
                         'choosing among them, the cap is'),
        by_depth={str(depth): [entry['ranks'] for entry in measured['priced']
                               if entry['depth'] == depth]
                  for depth in (1, 2, 3)})
    out['leader'] = leader
    out['leader_schedule'] = dict(
        ranks=leader['ranks'], banks=leader['banks'],
        steps=steps,
        retained_W=state['W'], retained_deficit=state['deficit'], retained_mass=state['mass'],
        retained_children=sum(state['histogram'].values()), retained_families=len(state['histogram']),
        retained_maxchild=max(state['histogram']),
        retained_histogram={str(r): n for r, n in sorted(state['histogram'].items())},
        volume_reading_only=[entry['rank'] for entry in steps
                             if entry['reading'] == 'padded'],
        reading=scheduled_reading(steps))
    out['point'] = dict(
        kappa=str(price['kappa']), kappa_decimal=float(price['kappa']),
        leaf=str(price['leaf']), leaf_decimal=float(price['leaf']),
        budget=str(price['budget']), binding=price['binding'],
        complex_coarse=str(price['complex_coarse']),
        complex_branch=str(price['complex_branch']),
        complex_ceiling=str(price['complex_ceiling']),
        headroom_to_the_complex_branch=str(price['headroom_to_the_complex_branch']),
        shares_of_the_complex_branch=str(price['shares_of_the_complex_branch']),
        gain_vs_the_rank3_rung=str(price['gain_vs_the_rank3_rung']),
        gain_vs_the_rank3_rung_percent=float(price['gain_vs_the_rank3_rung']) * 100,
        previous_top=str(published_top),
        tightest_constraint=str(price['assembly']['minimum_constraint']),
        tightest_constraint_rule=('the design backoff a * eta (bit-bound)' if price['binding'] == 'bit'
                                  else 'the weak haircut that put the budget on the complex branch'),
        adjacent_grid_rejected=price['adjacent_grid_rejected'],
        strict_constraints=47, margins=7)
    out['next_step'] = dict(
        cap=dict(rule='kappa <= assembly floor on the complex branch (1-beta)*complex - weak',
                 value=str(price['complex_ceiling']),
                 why='raising the bit leaf past the complex branch buys nothing, so every further '
                     'bit rung is capped by the complex side; the leader already reaches %s of '
                     'that branch' % float(price['shares_of_the_complex_branch'])),
        remaining_absorbable=[rank for rank in measured['absorbable'] if rank not in leader['ranks']],
        reading='the bit leaf is no longer the wall at this rung: the two branches meet, and the '
                'next increment is the complex supplier again -- or a new bit word that lifts the '
                'leaf without spending the complex branch.')
    out['status'] = (
        'MEASURED AND MACHINE-CHECKED: bitrung.py re-derives the rung-1 retained row, prices all '
        '%d rungs of up to %d families with the vendored engine, reads the schedule each family '
        'needs, prices the leader through the assembly rule and its unchanged 47 constraints with '
        'the adjacent 10^-18 point rejected, and asserts the gain over the point this package '
        'already sells.  Nothing here is built: the absorbed families need the new residual types '
        'the suppliers reserve, and the rows are pinned by digest to unmerged branches.'
        % (len(measured['priced']), MAX_DEPTH))
    return out


def main():
    sys.set_int_max_str_digits(0)
    sys.dont_write_bytecode = True
    out = build_artifact()
    target = HERE / 'bitrung.json'
    target.write_text(json.dumps(out, indent=1, sort_keys=True, default=str) + '\n', newline='\n')
    leader, point_out = out['leader'], out['point']
    print('bit word   retained row W=%d mass=%d deficit=%d children=%d families=%d'
          % (out['rung1']['retained_W'], out['rung1']['retained_mass'],
             out['rung1']['retained_deficit'], out['rung1']['retained_children'],
             out['rung1']['retained_families']))
    print('families   %d of the %d can leave into whole banks or a padded schedule: %s'
          % (len(out['absorbable']), len(out['families']), out['absorbable']))
    print('screen     %d rungs of up to %d families priced; leader %s (%d banks, W %d)'
          % (out['screen']['rungs_priced'], out['screen']['depth'], leader['ranks'],
             leader['banks'], leader['stock']))
    print('leaf       %.15e -> %.15e (%+.4f%%)'
          % (float(Q(out['rung1']['leaf'])), float(Q(leader['leaf'])),
             float(Q(leader['leaf']) / Q(out['rung1']['leaf']) - 1) * 100))
    print('point      kappa %s = %.15e (%+.4f%% over %s), binding %s, %d strict constraints, '
          'adjacent grid rejected %s'
          % (point_out['kappa'], point_out['kappa_decimal'], point_out['gain_vs_the_rank3_rung_percent'],
             point_out['previous_top'], point_out['binding'], point_out['strict_constraints'],
             point_out['adjacent_grid_rejected']))
    print('cap        the complex branch caps any further bit rung at %s; this rung reaches %s '
          'of it'
          % (point_out['complex_ceiling'], point_out['shares_of_the_complex_branch']))
    print('write ' + str(target))


if __name__ == '__main__':
    main()
