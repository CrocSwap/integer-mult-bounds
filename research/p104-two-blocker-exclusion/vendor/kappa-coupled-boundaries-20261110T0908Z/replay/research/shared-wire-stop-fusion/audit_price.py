"""Independent directed rational price enclosure of the audited STOP invoice.

Prepared for ToikY with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from decimal import Decimal, localcontext
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG = HERE.parent / "shared-wire-split-composition"
GRID = 10**65
if not __debug__:
    raise RuntimeError("Run without -O; assertions are proof checks.")


def down(x):
    return Q((x * GRID).__floor__(), GRID)


def up(x):
    return Q((x * GRID).__ceil__(), GRID)


def log_series(x):
    z = (x-1)/(x+1)
    series = sum(2*z**(2*i+1)/(2*i+1) for i in range(80))
    tail = 2*z**161/(161*(1-z*z))
    return series, series + tail


@lru_cache(None)
def log(r):
    a = r.bit_length() - 1
    l1,h1 = log_series(Q(r, 2**a))
    l2,h2 = log_series(Q(2))
    return down(l1 + a*l2), up(h1 + a*h2)


def exp_pos(x):
    assert 0 <= x < 1
    term = total = Q(1)
    for i in range(1, 48):
        term *= x/i
        total += term
    # Terms after index 48 have ratio < 1/2.
    return total, total + 2*term*x/48


def raw_margin(hist, kappa):
    lower = upper = Q(0)
    for r,c in sorted(hist.items()):
        lo,hi = log(r)
        x = down(Q(kappa)*lo)
        y = up(Q(kappa)*hi)
        a,b = down(r/exp_pos(y)[1]), up(r/exp_pos(x)[0])
        lower += c*(a if c >= 0 else b)
        upper += c*(b if c >= 0 else a)
    return lower, upper


def crossing(hist):
    with localcontext() as ctx:
        ctx.prec = 66
        logs = {r: Decimal(r).ln() for r in hist}
        lo,hi = Decimal(0), Decimal(".00376669")
        for _ in range(145):
            mid = (lo + hi)/2
            m = sum(c*r*(-mid*logs[r]).exp() for r,c in hist.items())
            if m > 0:
                lo = mid
            else:
                hi = mid
        diagnostic = (lo+hi)/2
    unit = 10**35
    floored = (Q(diagnostic)*unit).__floor__()
    lo,hi = Q(floored,unit), Q(floored+1,unit)
    lower_margin = raw_margin(hist, lo)
    upper_margin = raw_margin(hist, hi)
    assert lower_margin[0] > 0 and upper_margin[1] < 0
    return str(diagnostic), (lo,hi), (lower_margin,upper_margin)


def main():
    full = PKG / "FULL-RESULT.json"
    raw = full.read_bytes()
    assert sha256(raw).hexdigest() == FULL_SHA
    source = json.loads(raw)
    audit = json.loads((HERE/"RESULT.json").read_text())
    assert source["word_canonical_json_sha256"] == "91429a6b96729292a8764836e00c87a6f7cd3b76f05159033f4867f69a98d097"
    assert audit["candidate_canonical_sha256"] == "d0de7804e56b2c8fe6db9d323560e53041810fd0377b91680cbed19b5176ebc0"
    assert audit["invoice"]["T"] == source["invoice"]["T"]
    hist = Counter({int(r): n for r,n in source["invoice"]["T"].items()})
    hist.subtract({int(r): n for r,n in source["invoice"]["P"].items()})
    new = Counter({int(r): n for r,n in audit["invoice"]["T"].items()})
    new.subtract({int(r): n for r,n in audit["invoice"]["P"].items()})
    assert {r: new[r]-hist[r] for r in new.keys() | hist.keys() if new[r] != hist[r]} == {1:126,2:-36,4:54,5:-54}
    old_d, old_interval, old_m = crossing(hist)
    new_d, new_interval, new_m = crossing(new)
    assert old_interval[1] < Q(audit["gate"]["claim"]) < new_interval[0]
    assert sum(r*n for r,n in hist.items()) == sum(r*n for r,n in new.items()) == 1520
    out = {
        "status": "PASS_INDEPENDENT_STOP_PRICE", "source_full_result_sha256": FULL_SHA,
        "baseline_diagnostic": old_d, "candidate_diagnostic": new_d,
        "baseline_bracket": list(map(str,old_interval)), "candidate_bracket": list(map(str,new_interval)),
        "baseline_bracket_margins": [list(map(str,row)) for row in old_m],
        "candidate_bracket_margins": [list(map(str,row)) for row in new_m],
        "strict_improvement_in_raw_crossing": str(new_interval[0] - old_interval[1]),
        "complete_signed_rank_mass_surplus": 1520,
    }
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    FULL_SHA = "d9ba709fa5dcefffe3f3abdcf34600ce188224703cfd743e6db8b58ba4816cb7"
    main()
