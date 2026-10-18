"""Independent word-level replay and paid profile for bitE8/1+mut words.

Written for this audit; it shares no code with `research/e8-bit-p111-tuned/tune/wlib.py`.  Frame
dimensions are ranks over the rationals (exact Fraction Gaussian elimination), not reductions modulo
a prime, so the two implementations agree only if the geometry really is what it is claimed to be.

The paid profile of a word is the multiset of *ascents*: every register is climbed between frames,
and an ascent of dimension d from frame a to frame b with dim b > dim a is one paid elementary climb
of rank d = dim b - dim a.  The certified saving depends on the word only through this multiset,
its modulus m and its live register count W.
"""
from collections import Counter
from fractions import Fraction as F


def rank_of(vectors):
    """rank over Q of a list of rational vectors"""
    rows = [[F(x) for x in v] for v in vectors]
    if not rows:
        return 0
    ncol = len(rows[0])
    rk = 0
    for c in range(ncol):
        piv = next((i for i in range(rk, len(rows)) if rows[i][c]), None)
        if piv is None:
            continue
        rows[rk], rows[piv] = rows[piv], rows[rk]
        inv = 1 / rows[rk][c]
        rows[rk] = [x * inv for x in rows[rk]]
        for i in range(rk + 1, len(rows)):
            if rows[i][c]:
                f = rows[i][c]
                rows[i] = [a - f * b for a, b in zip(rows[i], rows[rk])]
        rk += 1
    return rk


def frame_dims(word):
    return [rank_of([word['lines'][j] for j in f]) if f else 0 for f in word['frames']]


def contains(dims_ok, a, b):
    return dims_ok[a] <= dims_ok[b]


def replay_profile(word, dims=None, check_nesting=True):
    """paid profile (dict rank -> count) of the word, in the pipeline's accounting:
    D, A, then the retained-total snapshot, then B, then C, then the final climb."""
    dims = dims or frame_dims(word)
    n = 2 * word['v'] + word['R']
    mask = [sum(1 << j for j in f) for f in word['frames']]
    cur = list(word['start'])
    P = Counter()

    def climb(r, f):
        a = cur[r]
        if a == f:
            return
        if check_nesting and mask[a] & mask[f] != mask[a]:
            raise AssertionError('illegal frame descent: register %d, %d -> %d' % (r, a, f))
        d = dims[f] - dims[a]
        if d > 0:
            P[d] += 1
        elif d < 0:
            raise AssertionError('descending climb')
        cur[r] = f

    for sec in ('D', 'A'):
        for f, t, ss in word[sec]:
            for r in [t, *ss]:
                climb(r, f)
    tops = [dims[cur[q]] for q in word['ret']]
    for f, t, ss in word['B']:
        for r in [t, *ss]:
            climb(r, f)
    for f, t, ss in word['C']:
        for r in [t, *ss]:
            climb(r, f)
    for r, f in enumerate(word['final']):
        climb(r, f)
    P.update(tops)
    return dict(sorted(P.items())), dims


def live_count(word, replicas=32):
    """live port-register count of the nine-stage bit pipeline: replicas * 2 * K * v, K = 4."""
    return replicas * 8 * word['v']
