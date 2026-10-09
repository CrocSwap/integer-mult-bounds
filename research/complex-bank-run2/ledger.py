#!/usr/bin/env python3
"""Rung 2 of the bank ladder: the complex supplier's rank-11 family, absorbed into banks.

PR219 (`research/residual-bank-run1`, head `237067f`) built **rung 1**: the bit word's
rank-22 bin leaves the ledger, its 440,352 three-copy registers of dirt become 6,116
width-72 banks, and the composition then binds on the **complex** supplier.  PR207's
frontier certificate records the same thing from the other side: its complex coarse
saving `700918443859411/10^18` is what caps the assembly once the bit side is raised.

That cap is the whole story of rung 2.  #219's rung 1 does not merely take the bit
side above the complex budget, it lands on the complex branch's own ceiling: with
`C = 7.00918443859411e-4`, `C/(1+C) = 7.0042750130515981e-4`, and rung 1's
`kappa = 700427501305159/10^18` sits one grid step below it.  So no rung above rung 1
can be taken on the bit word at all, whatever its ledger: the complex supplier's coarse
saving has to rise first.  This module builds the ledger that would raise it -- and
`obligations.json` states what is missing to make it physical.

On the pinned complex profile (`m = 66`, one copy `W = 12,052`, deficit `1,320`,
ledger bin 11 = 1,062 children per vertex):

* the family's three-copy volume is `11 * 3 * 1062 = 35,046 = 66 * 531`: an exact number
  of banks, so the whole-bank volume condition holds (one copy: 177 banks);
* the retained ledger satisfies the row identity, and the stock falls by exactly the bank
  count (`36,156 -> 35,625`), which is what makes the absorption free rather than a
  re-labelling;
* the family's rank divides the bank width (`66 = 6 * 11`), so a bank admits a uniform
  six-block tiling of the new family alone: the new blocks need no mixture with the
  word's older families.  That is a necessary condition, not a construction -- see
  `obligations.json` C1.

Prices come from the pinned engine (PR200's exact interval moment), used on the complex
side exactly as #219 uses it there: `bit=False`, i.e. without the bit branch's rare-class
fallback, on the `10^-18` grid.
"""
import importlib.util
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUN1 = HERE / 'references' / 'pr219-run1'
COPIES = 3
RANK = 11
GRID = 10 ** 18


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def engine():
    """The pinned interval-moment engine, as #219 vendors it."""
    return load('run2_interval_moment', RUN1 / 'interval_moment.py')


def run1():
    """#219's own schedule and arithmetic, imported from the vendored package."""
    return load('run2_run1_schedule', RUN1 / 'schedule.py'), load('run2_run1_arithmetic', RUN1 / 'arithmetic.py')


def profile(row):
    """#219's profile form, from either certificate spelling of the same fields."""
    hist = {int(r): int(n) for r, n in
            (row.get('child_multiplicities') or row['child_histogram']).items() if n}
    W = int(row.get('W', row.get('W_per_vertex')))
    D = int(row.get('N', row.get('deficit_per_vertex')))
    return dict(m=int(row['m']), W=W, N=D, L=int(row.get('L', 0)),
                child_multiplicities=hist,
                total_rank=int(row.get('total_rank', sum(r * n for r, n in hist.items()))),
                maxchild=int(row.get('maxchild', max(hist))))


def check_row(row):
    m, W, D, hist = row['m'], row['W'], row['N'], row['child_multiplicities']
    mass = sum(r * n for r, n in hist.items())
    assert m * W - mass == D, 'row identity'
    assert mass == row['total_rank'], 'declared rank mass'
    assert max(hist) == row['maxchild'], 'declared largest child'
    return mass


def three_copies(row):
    """The supplier's row over its three copies: integral stock, same saving."""
    m, W, D, hist = row['m'], row['W'], row['N'], row['child_multiplicities']
    hist = {r: COPIES * n for r, n in hist.items()}
    return dict(m=m, W=COPIES * W, N=COPIES * D, L=row['L'],
                child_multiplicities=hist, total_rank=sum(r * n for r, n in hist.items()),
                maxchild=max(hist))


def absorb(row, family):
    """Take one child family out of the ledger and into whole banks."""
    m, W, D, hist = row['m'], row['W'], row['N'], row['child_multiplicities']
    assert family in hist, 'the family must sit in the ledger'
    kept = {r: n for r, n in hist.items() if r != family}
    taken = family * hist[family]
    assert taken % m == 0, 'the absorbed volume must fill whole banks'
    mass = m * W - D - taken
    assert sum(r * n for r, n in kept.items()) == mass, 'row identity after absorption'
    stock, remainder = divmod(mass + D, m)
    assert remainder == 0, 'half-filled stock'
    assert kept, 'a ledger must remain after the absorption'
    assert taken // m > 0, 'the absorption must occupy at least one bank'
    retained = dict(m=m, W=stock, N=D, L=row['L'], child_multiplicities=kept,
                    total_rank=mass, maxchild=max(kept))
    assert check_row(retained) == mass
    return dict(family=family, volume=taken, banks=taken // m, retained=retained,
                stock_before=W, stock_after=stock, stock_drop=W - stock,
                mass_before=m * W - D, mass_after=mass,
                children_before=sum(hist.values()), children_after=sum(kept.values()),
                maxchild_before=max(hist), maxchild_after=max(kept),
                share_of_ledger=Q(taken, m * W - D),
                rank_divides_width=(m % family == 0))


def certify(interval, row):
    """The complex side's paid moment, exactly as #219 prices it: no bit fallback."""
    run1_arithmetic = load('run2_run1_arithmetic_certify', RUN1 / 'arithmetic.py')
    return run1_arithmetic.certify(interval, profile(row), False)


def ceiling(coarse):
    """The branch ceiling a coarse saving `C` can reach in the assembly: `C/(1+C)`."""
    return coarse / (1 + coarse)


def complex_ledger(certificate_path, interval):
    """The whole rung-2 half: base row, absorbed row, both prices, both ceilings."""
    certificate = json.loads(Path(certificate_path).read_text())
    row = profile(certificate['complex_profile'])
    mass = check_row(row)
    base = certify(interval, row)
    copied = three_copies(row)
    absorbed = absorb(copied, RANK)
    after = certify(interval, absorbed['retained'])
    return dict(source=Path(certificate_path).name,
                one_copy=dict(m=row['m'], W=row['W'], deficit=row['N'], mass=mass,
                              children=sum(row['child_multiplicities'].values()),
                              maxchild=row['maxchild'],
                              bin=RANK, bin_children=row['child_multiplicities'][RANK]),
                three_copy=dict(W=copied['W'], deficit=copied['N'], mass=copied['total_rank'],
                                children=sum(copied['child_multiplicities'].values())),
                base_saving=base['saving'], base_excluded=base['next_excluded']['lower'] > 1,
                absorbed=dict(family=absorbed['family'], volume=absorbed['volume'],
                              banks=absorbed['banks'], banks_one_copy=Q(absorbed['banks'], COPIES),
                              stock_before=absorbed['stock_before'], stock_after=absorbed['stock_after'],
                              stock_drop=absorbed['stock_drop'], mass_before=absorbed['mass_before'],
                              mass_after=absorbed['mass_after'], children_before=absorbed['children_before'],
                              children_after=absorbed['children_after'], maxchild_before=absorbed['maxchild_before'],
                              maxchild_after=absorbed['maxchild_after'],
                              share_of_ledger=absorbed['share_of_ledger'],
                              rank_divides_width=absorbed['rank_divides_width'],
                              blocks_per_bank=Q(absorbed['retained']['m'], RANK),
                              saving=after['saving'], next_excluded=after['next_excluded']['lower'] > 1),
                ceilings=dict(base=ceiling(base['saving']), absorbed=ceiling(after['saving'])))


if __name__ == '__main__':
    sys.set_int_max_str_digits(0)
    sys.dont_write_bytecode = True
    out = complex_ledger(HERE / 'references' / 'pr207-coordinated-crossover.certificate.json', engine())
    print(json.dumps({k: (str(v) if isinstance(v, Q) else v) for k, v in out.items()},
                     indent=1, sort_keys=True, default=str))
