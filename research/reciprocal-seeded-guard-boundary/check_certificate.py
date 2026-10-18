"""Check supplied rational floor witnesses without running Newton iteration.

Charles Bethin, with substantial OpenAI Codex assistance. Apache-2.0.
No dependency on the integer evaluator or discovery traversal.
"""
from fractions import Fraction as Q


def require(condition, message):
    if not condition:
        raise ValueError(message)


def floor_witness(value, rounded, precision):
    scale = 2**precision
    require((rounded * scale).denominator == 1, "off-grid rounded value")
    require(rounded <= value < rounded + Q(1, scale), "invalid floor witness")


def check(record, failure=True):
    c, g, p = Q(record["c"]), record["guards"], record["p"]
    require(1 <= c < 2 and type(p) is int and p >= 1, "invalid domain")
    require(type(g) is int and g >= 0, "invalid guards")
    require(Q(record["seed"]) == Q(5, 8), "wrong seed")
    # Closed-form schedule, separate from evaluator's capped-doubling loop.
    middle = [2**i for i in range(1, p.bit_length()) if 2**i < p]
    targets = [1] + middle + ([p] if p > 1 else [])
    rows = record["rows"]
    require([r[0] for r in rows] == targets, "wrong schedule")
    incoming = [Q(record["seed"])] + [Q(r[4], 2**r[1]) for r in rows[:-1]]
    residuals = []
    for index, (row, x) in enumerate(zip(rows, incoming, strict=True)):
        m, t, prefix, product, output = row
        require(t == (6 if index == 0 else m + g), "wrong stage precision")
        ct, u, y = (Q(n, 2**t) for n in (prefix, product, output))
        floor_witness(c, ct, t)
        floor_witness(ct*x, u, t)
        floor_witness(x*(2-u), y, t)
        residuals.append(1-c*y)
    y = Q(rows[-1][4], 2**rows[-1][1])
    require(y == Q(record["output"]), "output binding")
    require(residuals[-1] == Q(record["residual"]), "residual binding")
    bound = Q(1, 2**(p+1))
    require(abs(residuals[-1]) > bound if failure else abs(residuals[-1]) < bound,
            "false residual conclusion")
    stop = len(rows) if not failure else len(rows)-1
    require(all(abs(e) < Q(1, 2**(r[0]+1))
                for e, r in zip(residuals[:stop], rows[:stop], strict=True)),
            "intermediate residual bound")
    if "failure_interval" in record:
        lo, hi = map(Q, record["failure_interval"])
        require(1 <= lo < hi < 2 and c == lo, "bad interval")
        # Prefix constancy proves the entire supplied transcript for all real c.
        for _, t, prefix, _, _ in rows:
            require(Q(prefix, 2**t) <= lo and hi <= Q(prefix+1, 2**t),
                    "interval crosses input prefix")
        require(y > 0 and 1-lo*y > bound and 1-hi*y >= bound,
                "false interval failure")
        require(hi == (1-bound)/y, "interval endpoint is not exact")
    return residuals
