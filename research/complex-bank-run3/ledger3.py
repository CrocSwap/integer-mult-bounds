#!/usr/bin/env python3
"""Rungs 3 and 4 of the bank ladder: the rest of the complex ledger that can be banked.

PR219 (``research/residual-bank-run1``, head ``237067f``) built **rung 1**: the bit word's
rank-22 bin leaves the ledger, its 440,352 three-copy registers of dirt become 6,116
width-72 banks, and the composition then binds on the **complex** supplier.  PR224
(``research/complex-bank-run2``) built **rung 2**: the complex word's rank-11 family leaves
into 531 of that word's own width-66 banks, and the assembly lands on the new complex
ceiling.

Rung 2 is not the end of the complex ledger.  Two further families fill whole width-66
banks on their own volume -- rank 16 (264 children per vertex) and rank 20 (66 per vertex)
-- and after them **nothing else does**: the criterion that makes an absorption free is
that the family's own volume is a whole number of banks, and among the remaining 17
families no volume satisfies it.  That makes the complex-side ladder finite, and this
module builds the ledger up to its top.

The criterion, stated once because everything here turns on it: a family of rank ``r`` with
``n`` children per vertex occupies ``r * n`` registers per copy, and it can leave the
ledger into whole banks only when that volume is a whole number of width-``m`` banks
(``m | r * n``).  That is what PR219's rank-22 absorption and PR224's rank-11 absorption
both satisfy, and what the certified entrance-bank proof satisfies on the bit word (2,200
rank-60 exteriors whose 396,000 three-copy registers fill 5,500 banks).  It is *necessary*
and it is the accounting criterion the built rungs use; it is not a construction -- see
``obligations.json`` T1 for the tiling that rank 16 and rank 20 additionally owe, since
neither rank divides the bank width (``66 % 16 = 2``, ``66 % 20 = 6``) whereas rank 11 does
(``66 = 6 * 11``).

Prices come from the pinned engine (PR200's exact interval moment), used on the complex
side exactly as PR219 uses it there: ``bit=False``, i.e. without the bit branch's rare-class
fallback, on the ``10^-18`` grid.
"""
import importlib.util
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUN1 = HERE / 'references' / 'pr219-run1'
COPIES = 3
GRID = 10 ** 18
# The complex ledger's bank width and the family every bank was measured against.
WIDTH = 66


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def engine():
    """The pinned interval-moment engine, as PR219 vendors it."""
    return load('run3_interval_moment', RUN1 / 'interval_moment.py')


def run1():
    """PR219's own schedule and arithmetic, imported from the vendored package."""
    return load('run3_run1_schedule', RUN1 / 'schedule.py'), \
        load('run3_run1_arithmetic', RUN1 / 'arithmetic.py')


def profile(row):
    """PR219's profile form, from either certificate spelling of the same fields."""
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


def bankable(row, family):
    """Does this family's own volume fill whole banks, and how many?"""
    m, hist = row['m'], row['child_multiplicities']
    if family not in hist:
        return None
    volume = family * hist[family]
    return dict(family=family, children=hist[family], volume=volume,
                banks=volume // m, whole=(volume % m == 0),
                uniform_tiling=(m % family == 0),
                blocks_per_bank=Q(m, family) if m % family == 0 else None)


def eligibility(row):
    """Every family of the row whose own volume is a whole number of banks."""
    m = row['m']
    return sorted(r for r in row['child_multiplicities']
                  if (r * row['child_multiplicities'][r]) % m == 0)


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
    """The complex side's paid moment, exactly as PR219 prices it: no bit fallback."""
    run1_arithmetic = load('run3_run1_arithmetic_certify', RUN1 / 'arithmetic.py')
    return run1_arithmetic.certify(interval, profile(row), False)


def ceiling(coarse):
    """The branch ceiling a coarse saving `C` can reach in the assembly: `C/(1+C)`."""
    return coarse / (1 + coarse)


def side(certificate_path, interval, rungs=()):
    """The complex half of the ladder: base row plus one entry per absorbed family.

    ``rungs`` is applied in order, each entry a family rank; every step is checked
    (whole-bank volume, retained row identity, stock drop equal to the bank count) and
    priced with the pinned engine.
    """
    certificate = json.loads(Path(certificate_path).read_text())
    row = profile(certificate['complex_profile'])
    mass = check_row(row)
    base = certify(interval, row)
    copied = three_copies(row)
    ladder, work = [], copied
    for family in rungs:
        step = absorb(work, family)
        work = step['retained']
        after = certify(interval, work)
        ladder.append(dict(
            family=family, volume=step['volume'], banks=step['banks'],
            banks_one_copy=Q(step['banks'], COPIES),
            stock_before=step['stock_before'], stock_after=step['stock_after'],
            stock_drop=step['stock_drop'], mass_before=step['mass_before'],
            mass_after=step['mass_after'], children_before=step['children_before'],
            children_after=step['children_after'], maxchild_before=step['maxchild_before'],
            maxchild_after=step['maxchild_after'],
            share_of_ledger=step['share_of_ledger'],
            rank_divides_width=step['rank_divides_width'],
            blocks_per_bank=(Q(step['retained']['m'], family)
                             if step['rank_divides_width'] else None),
            saving=after['saving'],
            next_excluded=after['next_excluded']['lower'] > 1))
    return dict(source=Path(certificate_path).name,
                one_copy=dict(m=row['m'], W=row['W'], deficit=row['N'], mass=mass,
                              children=sum(row['child_multiplicities'].values()),
                              maxchild=row['maxchild'],
                              families=len(row['child_multiplicities'])),
                three_copy=dict(W=copied['W'], deficit=copied['N'], mass=copied['total_rank'],
                                children=sum(copied['child_multiplicities'].values())),
                eligibility=[bankable(copied, r) for r in eligibility(copied)],
                base_saving=base['saving'],
                base_excluded=base['next_excluded']['lower'] > 1,
                ladder=ladder,
                ceilings=dict(base=ceiling(base['saving']),
                              **{'rung%d' % (i + 2): ceiling(step['saving'])
                                 for i, step in enumerate(ladder)}),
                final_eligibility=eligibility(work),
                final_row=dict(W=work['W'], deficit=work['N'], mass=work['total_rank'],
                               children=sum(work['child_multiplicities'].values()),
                               families=len(work['child_multiplicities']),
                               maxchild=max(work['child_multiplicities'])),
                final_saving=certify(interval, work)['saving'])


if __name__ == '__main__':
    sys.set_int_max_str_digits(0)
    sys.dont_write_bytecode = True
    part = side(HERE / 'references' / 'pr207-coordinated-crossover.certificate.json',
                engine(), (11, 16, 20))
    print(json.dumps(part, indent=1, sort_keys=True, default=str))
