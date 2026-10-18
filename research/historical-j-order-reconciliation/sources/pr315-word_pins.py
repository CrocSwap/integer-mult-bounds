"""Cube-size shape and pinned word-dependent constants of the p = 10 package.

shape() derives every p-dependent constant of the five-stage layout from the cube size p (h = 2p ports per
coordinate block, v = 8*C(p,3) sources, m = 5h). The PR234 five-stage layout is the same at every h: idle ranks
(2h-2, h-1, 2h+2, 4) at 2v each, h copied centres of rank h-2 each read by 3v/h targets, and five-stage deficit
4v - 5h(h-2).

Word-dependent observed values (register counts, histograms, digests, kappa, ...) are pinned in word-pins.json,
which MANIFEST.json pins like every other input. Every check calls expect(name, value), which asserts exact
equality with the pinned value (in the canonical form canon() below; dictionaries keep their key types), so each
check is exactly as strong as the literal it replaces. RECORD is None in every verification run; only
discovery/repin.py, in its own process, switches it to a dictionary to collect the values of a new word.
Prepared by DreamingOfClouds with Anthropic Claude assistance; Apache-2.0.
"""
from fractions import Fraction
from math import comb
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
P = 10
FILE = HERE / 'word-pins.json'
PINS = json.loads(FILE.read_text())
RECORD = None


def shape(p=P):
    h = 2 * p; v = 8 * comb(p, 3); m = 5 * h; ell = h * (h - 2)
    assert v * 3 % h == 0
    return dict(p=p, h=h, v=v, m=m, ell=ell, idle=(2 * h - 2, h - 1, 2 * h + 2, 4), center_rank=h - 2, centers=h,
                scatter_reads=3 * v // h, center_reads=3 * v, deficit=4 * v - 5 * ell,
                virtual_m=3 * h, virtual_deficit=2 * v - 3 * ell, replicas=60, stages=5)


def canon(x):
    """Injective JSON form: dicts become key-sorted [key, value] lists (key types kept), tuples become lists."""
    if isinstance(x, bool) or x is None or isinstance(x, (int, str)):
        return x
    if isinstance(x, Fraction):
        return ['Fraction', str(x)]
    if isinstance(x, dict):
        items = [[canon(k), canon(v)] for k, v in x.items()]
        return ['dict', sorted(items, key=lambda kv: json.dumps(kv[0], sort_keys=True))]
    if isinstance(x, (list, tuple)):
        return [canon(y) for y in x]
    raise AssertionError(('value type not pinnable', type(x)))


def expect(name, value):
    """Assert value equals the pinned value; returns value. (Records instead only inside discovery/repin.py.)"""
    c = canon(value)
    if RECORD is not None:
        assert RECORD.setdefault(name, c) == c, ('one pin, two values', name)
        return value
    assert name in PINS, ('unpinned value', name)
    assert PINS[name] == c, ('pinned value changed', name)
    return value


def pinned(name):
    """A pinned value already asserted by an earlier expect() (needed by module-level constants)."""
    table = PINS if RECORD is None else RECORD
    assert name in table, ('pin read before it was checked', name)
    return table[name]
