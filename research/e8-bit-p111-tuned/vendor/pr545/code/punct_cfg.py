# The one configuration of the punctured-word hosted chain: everything that was a hard-coded 120 / 72 / 9600 / 489 in
# PR #493's pipeline is derived here from the WORD (or, for scripts that never see the word, from the exported records).
# Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. Apache-2.0.
"""Config of a bitE8/1 word for the hosted chain.

  v           number of live ports (120 for PR #493 / #503, 111 for the punctured star unit)
  R           number of helper registers
  ports_geom  the live labels, as indices into the 120-line E8 system, in word order (absent for a full word)
  totals map  for each of the nine retained totals: the register, and the rank (frame dimension) it is COPYed from,
              replayed here from the gates alone (72 = 9 x 8 for #493 / #503, 63 = 9 x 7 for the star unit)

Nothing in here is read from the environment.  `copy_ranks(w)` is an independent replay of the word's gates; the
emitter and the audit derive the same number from the exported records, and the chain asserts the two agree."""
import gzip
import json
from fractions import Fraction as Fr
from pathlib import Path


def load(path):
    p = Path(path)
    return json.loads((gzip.decompress(p.read_bytes()) if p.suffix == '.gz' else p.read_bytes()))


def root120(pkg):
    """The 120 labelled E8 root lines of PR #493's package (the order every geometry and port route is indexed by)."""
    return load(Path(pkg) / 'data/bit/bitE8mut-r489.json.gz')['lines']


def check_word(w, pkg):
    """A full word (v = 120, no ports_geom) or a punctured one: live labels are a subsequence of the 120-line system."""
    v = w['v']
    if 'ports_geom' not in w:
        assert v == 120 and len(w['lines']) == 120
        return
    pg, r120 = w['ports_geom'], root120(pkg)
    assert v < 120 and len(pg) == v == len(w['lines']) and list(pg) == sorted(set(pg)) and 0 <= pg[0] and pg[-1] < 120
    assert all(r120[p] == w['lines'][i] for i, p in enumerate(pg)), 'live lines are not the labelled 120-system lines'
    if 'punctured' in w:
        assert sorted(w['punctured'] + list(pg)) == list(range(120))
    # the frame-zero residual isometry of PR #493 (data/eleven/residual-isometries.json) is the coordinate frame 2e_0..2e_7,
    # lines 0..7 of the 120-system; the stock validate_isometries(frames, lines) call needs them live at positions 0..7
    assert pg[:8] == list(range(8)), 'lines 0..7 must be live so the stock residual-isometry check applies unchanged'


def _rank(rows):
    rows = [[Fr(x) for x in r] for r in rows]
    r = 0
    for c in range(len(rows[0]) if rows else 0):
        p = next((i for i in range(r, len(rows)) if rows[i][c] != 0), None)
        if p is None:
            continue
        rows[r], rows[p] = rows[p], rows[r]
        for i in range(r + 1, len(rows)):
            if rows[i][c] != 0:
                f = rows[i][c] / rows[r][c]
                rows[i] = [a - f * b for a, b in zip(rows[i], rows[r])]
        r += 1
    return r


def copy_ranks(w):
    """Totals map: replay the gates D, A in order (a register stands at the frame of the last gate it was in) and read
    the dimension of the frame each retained total is COPYed from.  Frame 0 has dimension 0."""
    lines = w['lines']
    dims = [_rank([lines[i] for i in idx]) for idx in w['frames']]
    cur = list(w['start'])
    for gates in (w['D'], w['A']):
        for f, d, srcs in gates:
            for r in [d] + list(srcs):
                cur[r] = f
    return [dims[cur[q]] for q in w['ret']]


def config(w, pkg):
    check_word(w, pkg)
    cr = copy_ranks(w)
    assert len(cr) == 9 and len(w['ret']) == 9
    return dict(v=w['v'], R=w['R'], copy_ranks=cr, cst=sum(cr), punctured=('ports_geom' in w))
