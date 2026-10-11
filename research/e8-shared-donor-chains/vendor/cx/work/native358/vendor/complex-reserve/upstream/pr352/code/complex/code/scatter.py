"""The scatter of a gcert/1 program, read exactly as Sussman's gx.scat_row reads it: an explicit per-target table
(gx E2 checks it has v rows naming retained totals 0..len(ret)-1), or the star rule with one total per coordinate.

Added for the E8 complex supplier, whose 8 retained totals scatter through a table; with the star rule every
function below returns what the paired-cube checks computed inline (inside/outside by the port bit k)."""
from fractions import Fraction as Q


def row(c, t):
    """[(k, coefficient)] of target t, in the certificate's order."""
    sc = c["scat"]
    if "table" in sc:
        return [(k, Q(a, b)) for k, a, b in sc["table"][t]]
    sin, sout = Q(*sc["inside"]), Q(*sc["outside"])
    return [(k, sin if c["ports"][t] >> k & 1 else sout) for k in range(c["h"])]


def table(c):
    """{t: {k: coefficient}} for every target; a total a target does not read is absent."""
    out = {}
    for t in range(c["v"]):
        r = row(c, t)
        ks = [k for k, _ in r]
        if len(set(ks)) != len(ks):
            raise ValueError("scatter row %d names a total twice" % t)
        out[t] = dict(r)
    return out


def centre_ranks(c):
    """the rank of each retained total's frame, in total order 0..len(ret)-1"""
    dim = [len(f) for f in c["frames"]]
    return [dim[f] for _, _, f in sorted(c["ret"])]
