#!/usr/bin/env python3
"""Two questions the width scan left open, answered by measurement.

The width scan (`widths66.py`) established that the bank width is the word's modulus and that
the pinned complex ledger admits exactly one -- 66, the smallest integer above its density
`rank mass / W = 65.8905...`.  It also showed that at a *narrower* modulus far more of the
ledger tiles (`w = 54`: nine families, 1,549,098 registers, 65% of the rank mass).  So the
constraint is the word's density, and two things follow that this module settles:

1. **Which suppliers already exist** (`corpus_scan`).  Every ledger-bearing certificate in the
   repository is read and scored on the same four numbers: modulus, density `mass / (m * W)`,
   the smallest modulus the row admits (`floor(mass / W) + 1`), and the mass share that tiles
   whole banks there.  If a less dense word is already pinned somewhere, this finds it; if not,
   the ranking says how far the pinned ones are from admitting a narrower modulus.
2. **What a word of a given width would have to look like** (`density_curve`).  Holding the
   pinned *shape* (the same bins and counts) and choosing a modulus `m`, the cheapest stock that
   makes the row poseable is `W_min = floor(mass / m) + 1`, and its density follows.  The curve
   reports, per modulus: the required stock, the density, the families that tile whole banks
   there, the mass that leaves, the retained row, and -- where the vendored certifier can price
   it -- the κ.  That is the design target in reverse: instead of asking what the pinned word
   reaches, it asks what a word would have to be to reach more.

Caveats, stated once and not blurred.  The corpus figures are read from other packages'
certificates, whose conventions may differ; the module reports what each file says, with its
path, and does not re-derive those packages.  The density curve is a **synthetic** construction:
same bin shape as the pinned word, different width and stock.  Its κ is the pinned engine
pricing a row that no supplier in the pins owns, so it is a specification, not a result about
any existing word -- and where the certifier's own bracket cannot reach the row, that is
recorded instead of quoted.
"""
import json
import os
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import ledger3  # noqa: E402

WIDTH = 66
COPIES = 3
GRID = 10 ** 18
ETA = BETA = Q(1, 10 ** 24)
WEAK = Q(1, 10 ** 30)
PINNED_KAPPA = Q(711599961413937, 10 ** 18)
CURVE_WIDTHS = (48, 54, 60, 66, 72, 84, 96)


def profile_of(node):
    """A ledger profile out of a certificate node, or None if it is not one."""
    if not isinstance(node, dict):
        return None
    hist = node.get('child_histogram') or node.get('child_multiplicities')
    if not isinstance(hist, dict) or not hist:
        return None
    try:
        hist = {int(r): int(n) for r, n in hist.items() if int(n)}
    except (TypeError, ValueError):
        return None
    m = node.get('m', node.get('width', node.get('M')))
    W = node.get('W', node.get('W_per_vertex'))
    D = node.get('deficit', node.get('deficit_per_vertex', node.get('N')))
    if m is None or W is None or D is None or not hist:
        return None
    try:
        return dict(m=int(m), W=int(W), N=int(D), child_multiplicities=hist,
                    total_rank=sum(r * n for r, n in hist.items()))
    except (TypeError, ValueError):
        return None


def walk_profiles(root):
    """Every ledger profile in a tree, labelled by file and JSON path."""
    found = []
    for path in sorted(Path(root).rglob('*.json')):
        if '/.git/' in str(path):
            continue
        try:
            data = json.loads(path.read_text(encoding='utf-8', errors='replace'))
        except (json.JSONDecodeError, OSError, UnicodeDecodeError):
            continue

        def visit(node, where):
            profile = profile_of(node)
            if profile:
                found.append((str(path.relative_to(root)).replace('\\', '/'), where, profile))
            if isinstance(node, dict):
                for key, child in node.items():
                    visit(child, where + '/' + str(key))
            elif isinstance(node, list):
                for index, child in enumerate(node[:4]):
                    visit(child, where + '/%d' % index)
        visit(data, '')
    return found


def score(profile):
    """The four numbers a supplier's ledger is scored on."""
    m, W, mass = profile['m'], profile['W'], profile['total_rank']
    if W <= 0 or m <= 0 or mass <= 0 or mass >= m * W:
        return None                     # not a poseable dense row: skip, do not misreport
    if max(profile['child_multiplicities']) > m:
        return None                     # a rank outside the width: another convention
    if m * W - mass != profile['N']:
        return None                     # the row identity must hold, or it is not this ledger
    density = Q(mass, m * W)
    smallest = mass // W + 1            # the smallest modulus with mass < w * W
    eligible, mass_out = {}, 0
    for rank, n in sorted(profile['child_multiplicities'].items(), reverse=True):
        if (rank * n) % smallest:
            continue
        capacity = smallest // rank
        if capacity == 0:
            continue
        banks = -(-n // capacity)
        eligible[rank] = dict(capacity_per_bank=capacity, banks=banks,
                              padding_registers=banks * smallest - rank * n)
        mass_out += banks * smallest
    if mass_out > mass:
        return None                     # bank volumes cannot exceed the ledger they come from
    return dict(m=m, W=W, deficit=profile['N'], rank_mass=mass, families=len(
        profile['child_multiplicities']), density=density, density_decimal=float(density),
        smallest_admissible_modulus=smallest, modulus_headroom=smallest - m,
        eligible_at_that_modulus=sorted(eligible),
        tiling_mass=mass_out, tiling_share=Q(mass_out, mass),
        tiling_share_decimal=float(Q(mass_out, mass)))


def relative_to_package(path):
    """A path the scan walked, as this package sees it.

    The certificate records the scan's root so that a reader can repeat it.  Recording it
    absolutely would make the record depend on where it was built -- it would not rebuild in a
    clone, and the commit would carry a local directory name -- so it is stored relative to this
    package instead.
    """
    try:
        return Path(os.path.relpath(Path(path).resolve(), HERE)).as_posix()
    except ValueError:                 # another drive on Windows: nothing relative to say
        return str(path)


def corpus_scan(root=REPO, limit=14, pinned_density=None):
    """Rank every poseable ledger in the tree, densest last.

    `pinned_density` is the density of the word this package prices against; when given, the
    scan reports every ledger *below* it, which is the only form of the question that decides
    whether a less dense supplier already exists to be reused.
    """
    rows, seen = [], set()
    for source, where, profile in walk_profiles(root):
        scored = score(profile)
        if not scored:
            continue
        key = (scored['m'], scored['W'], scored['deficit'], scored['rank_mass'])
        if key in seen:
            continue
        seen.add(key)
        rows.append({**scored, 'source': source, 'path': where})
    rows.sort(key=lambda row: (row['modulus_headroom'], -row['tiling_share_decimal']))
    by_density = sorted(rows, key=lambda row: row['density'])
    below = [row for row in by_density
             if pinned_density is not None and row['density'] < pinned_density]
    return dict(root=relative_to_package(root), profiles_scanned=len(rows), ranked=rows[:limit],
                pinned_density=str(pinned_density) if pinned_density is not None else None,
                least_dense_overall=(by_density[0] if by_density else None),
                below_pinned_count=len(below), below_pinned_sample=below[:limit])


def density_curve(profile, widths=CURVE_WIDTHS, interval=None, leaf=None):
    """Per modulus: the same shape and the same occupancy, at that width.

    The pinned row's occupancy is held fixed (`density = mass / (m * W)`) and the stock follows
    from it, `W = ceil(mass / (density * m))`.  Varying the stock instead would move the
    deficit -- the row's slack -- and the slack is what sets the saving, so a curve that moved
    both would confound the two.
    """
    mass = profile['total_rank']
    m0, W0 = profile['m'], profile['W']
    density = Q(mass, m0 * W0)
    interval = interval or ledger3.engine()
    curve = []
    for m in widths:
        stock_min = -(-mass * density.denominator // (density.numerator * m))
        deficit = m * stock_min - mass
        if deficit <= 0:
            continue
        row = dict(m=m, W=stock_min, N=deficit,
                   child_multiplicities=dict(profile['child_multiplicities']),
                   total_rank=mass, maxchild=max(profile['child_multiplicities']))
        eligible, removed, banks = {}, 0, 0
        for rank, n in sorted(profile['child_multiplicities'].items(), reverse=True):
            if (rank * n) % m:
                continue
            capacity = m // rank
            if capacity == 0:
                continue
            b = -(-n // capacity)
            eligible[rank] = dict(capacity_per_bank=capacity, banks=b,
                                 padding_registers=b * m - rank * n)
            removed += b * m
            banks += b
        entry = dict(modulus=m, stock_min=stock_min, density=Q(mass, m * stock_min),
                     density_decimal=float(Q(mass, m * stock_min)),
                     pinned_density=str(density), deficit=deficit,
                     eligible_families=sorted(eligible), banks=banks,
                     mass_removed=removed, tiling_share=Q(removed, mass),
                     tiling_share_decimal=float(Q(removed, mass)))
        if not eligible or stock_min - banks <= 0:
            curve.append({**entry, 'saving': None, 'kappa': None, 'priced': False,
                          'status': 'nothing tiles, or the stock cannot retire the banks'})
            continue
        kept = dict(profile['child_multiplicities'])
        padding = 0
        for rank in eligible:
            kept[rank] -= profile['child_multiplicities'][rank]
            del kept[rank]
            padding += eligible[rank]['padding_registers']
        if padding:
            if kept.get(1, 0) < padding:
                curve.append({**entry, 'saving': None, 'kappa': None, 'priced': False,
                              'status': 'the padding draw exceeds the kept rank-1 bin'})
                continue
            kept[1] -= padding
            if kept[1] == 0:
                del kept[1]
        mass_after = sum(r * n for r, n in kept.items())
        retained = dict(m=m, W=stock_min - banks, N=deficit, child_multiplicities=kept,
                        total_rank=mass_after, maxchild=max(kept))
        assert ledger3.check_row(retained) == mass_after, 'the synthetic row must be consistent'
        try:
            saving = ledger3.certify(interval, retained)['saving']
        except (AssertionError, ValueError) as exc:
            curve.append({**entry, 'saving': None, 'kappa': None, 'priced': False,
                          'status': 'not priceable: %s (the vendored certifier brackets the '
                                    'moment at 1%%)' % (str(exc) or exc.__class__.__name__)})
            continue
        kappa = None
        if leaf is not None:
            budget = min(leaf, (1 - BETA) * saving - WEAK)
            q = budget * (1 - 2 * ETA)
            z = ((1 - ETA) * q / (1 + q)) * GRID
            kappa = Q((z.numerator - 1) // z.denominator, GRID)
        curve.append({**entry, 'saving': saving, 'kappa': kappa, 'priced': True,
                      'retained_stock': retained['W'], 'retained_mass': mass_after,
                      'status': 'priced (synthetic row: same shape, this modulus and stock)'})
    return curve


def main():
    sys.set_int_max_str_digits(0)
    sys.dont_write_bytecode = True
    supplier = json.loads((HERE / 'references' / 'pr219-run1' / 'references'
                           / 'pr193-source-assisted-v4.certificate.json').read_text())
    base = ledger3.profile(supplier['complex_profile'])
    pinned_density = Q(base['total_rank'], base['m'] * base['W'])
    scan = corpus_scan(pinned_density=pinned_density)
    print('corpus scan: %d distinct poseable ledgers under %s' % (scan['profiles_scanned'],
                                                                  scan['root']))
    print('%6s %7s %9s %9s %6s %9s  %s'
          % ('modulus', 'W', 'rankmass', 'density', 'w_min', 'tiling', 'source'))
    for row in scan['ranked']:
        print('%6d %7d %9d %9.5f %6d %8.2f%%  %s'
              % (row['m'], row['W'], row['rank_mass'], row['density_decimal'],
                 row['smallest_admissible_modulus'], row['tiling_share_decimal'] * 100,
                 row['source'] + row['path'][:40]))
    least = scan['least_dense_overall']
    print('\nleast dense ledger overall: %d wide, density %.5f -> w_min %d, tiles %.2f%%  %s'
          % (least['m'], least['density_decimal'], least['smallest_admissible_modulus'],
             least['tiling_share_decimal'] * 100, least['source']))
    print('ledgers below the pinned density (%s): %d'
          % (scan['pinned_density'], scan['below_pinned_count']))
    for row in scan['below_pinned_sample'][:5]:
        print('  %6d %7d %9d %9.5f -> w_min %d  %s'
              % (row['m'], row['W'], row['rank_mass'], row['density_decimal'],
                 row['smallest_admissible_modulus'], row['source']))

    schedule, arithmetic = ledger3.run1()
    leaf = Q(arithmetic.build(schedule.build())['ordinary_leaf'])
    print('\ndensity curve (pinned shape, cheapest stock per modulus, kappa where priceable):')
    print('%8s %9s %9s %8s %10s %20s %19s' %
          ('modulus', 'stock_min', 'density', 'banks', 'removed', 'coarse saving', 'kappa'))
    for entry in density_curve(base, interval=ledger3.engine(), leaf=leaf):
        if not entry['priced']:
            print('%8d %9d %9.5f %8d %10d %20s %19s  %s'
                  % (entry['modulus'], entry['stock_min'], entry['density_decimal'],
                     entry['banks'], entry['mass_removed'], '', '', entry['status']))
            continue
        print('%8d %9d %9.5f %8d %10d %20s %19s  %+.4f%% vs the pinned top'
              % (entry['modulus'], entry['stock_min'], entry['density_decimal'],
                 entry['banks'], entry['mass_removed'], entry['saving'], entry['kappa'],
                 float(entry['kappa'] / PINNED_KAPPA - 1) * 100))


if __name__ == '__main__':
    main()
