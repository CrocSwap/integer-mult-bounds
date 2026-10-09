"""Round-seven witness, bit side: PR #62's producer (interval strips, core-aware pair assembly) on our two-stage
interchange with retained totals, lifted frames and late copies, and the stage-1 word reordered (deferred readouts,
V leaves); notes/deferred-readout.tex.

The child-width histogram is rebuilt here from the frozen schedule (certificates/round7/): every slot's frame chain
from the nodes it holds, the deferred readout levels on every target from the garbage-coefficient supports of the
schedule, and the X_S chains from the V-gate order. Frame dimensions are taken from the data file;
independent/deferred-readout/check_frames.py re-derives each of them exactly, and check_word.py replays the word.
Two data-entrance corners are reported: the round-six corner (runs h-2, 1^(h+1)) and the staircase corner (runs h-2,
h-5, 1^6, independent/deferred-readout/check_stair.py).

Usage: python3 scripts/certificate_round7.py"""
import os, sys
from fractions import Fraction as Q
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(HERE, '..', 'independent', 'two-stage-bit'),
                os.path.join(HERE, '..', 'independent', 'deferred-readout')]
import moment
import deferred as dr
from certificate_round3 import evaluate

A_C, M_C, S_C = Q(36926111, 5 * 10**11), 576, 119453132304     # round-six complex interchange, h = 24

# Every round-seven bit witness: its frozen files and its claimed savings with the two entrance corners.
# The headline is the staircase variant of the last entry.
WITNESSES = [
    dict(name='PR #62 producer, lifted frames, late copies, deferred readouts, V leaves', h=23,
         witness='witness_23.json.gz', data='deferred_23.json.gz',
         plain=(Q(12599, 200000000), Q(6299103187973, 10**17)),
         staircase=(Q(31987, 500000000), Q(1599247689723, 25 * 10**15))),
]
HEADLINE = WITNESSES[-1]
CORNERS = (('plain', 'round-six entrance corner', dr.ROUND6_CORNER), ('staircase', 'staircase entrance corner', dr.STAIRCASE_CORNER))


def build(wit=HEADLINE):
    h = wit['h']; W, D = dr.load(h, wit['witness'], wit['data']); S = dr.Schedule(W, D)
    cov = S.adjoint(); ylev = S.ylevels(cov); rk = dr.chain_ranks(S); xd = S.xdata()
    assert all(sum(x) == h - 1 for x in xd)
    return S, rk, ylev, xd


def saving(S, rk, ylev, xd, corner):
    c = dr.histogram(S, rk, ylev, xd, corner)
    assert sum(w * n for w, n in c['hist'].items()) == c['s'] and max(c['hist']) < c['m'] and c['W'] * c['m'] > c['s']
    a, _ = moment.certify(c)
    return a, c


def kappa(a_b):
    return evaluate(a_b, A_C, Q(1, 1000), 'crude', m_c=M_C, s_c=S_C)


def certify(wit):
    """{'plain' | 'staircase': (a_b, kappa result, histogram)} for one witness, checked against its claims."""
    S, rk, ylev, xd = build(wit); out = {}
    for key, _, corner in CORNERS:
        a, c = saving(S, rk, ylev, xd, corner(S.h)); k = kappa(a)
        assert k['ok'] and (a, k['kappa']) == wit[key], (key, a, k['kappa'])
        out[key] = (a, k, c)
    return S, out


def main():
    for wit in WITNESSES:
        S, out = certify(wit)
        print('%s: h=%d R=%d, deferred slots %d, V-leaf slots %d' % (wit['name'], S.h, S.R, len(S.readout), len(S.vstart)))
        for key, label, _ in CORNERS:
            a, k, c = out[key]
            print('  %s: s = Wm - N + L = %d (rank sum exact), W = %d, a_b = %s (%.6e), kappa = %s (%.7e) ok=%s' % (
                label, c['s'], c['W'], a, float(a), k['kappa'], float(k['kappa']), k['ok']))


if __name__ == '__main__':
    main()
