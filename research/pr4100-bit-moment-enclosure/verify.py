#!/usr/bin/env python3
"""Certified rational enclosure of #4100 BIT.md's recurrence moments at c = 8667/5000000.

Standard library only; no code from the audited package. ln is enclosed by its
atanh series with a geometric tail bound, exp by Taylor with a Lagrange remainder.
Also checks the stage exponent algebra and the body-word exchange.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent

# The selected record as of this package's base commit (git blob b1fea0c9), vendored after main reselected it.
SELECTED_AT_BASE_SHA256 = "bb2eaa58647b353f88d0aec2eafb9d30df1be53589231b23e12ceef3e4bad129"


def selected_at_base_path():
    path = HERE / "SELECTED-AT-BASE.json"
    if hashlib.sha256(path.read_bytes()).hexdigest() != SELECTED_AT_BASE_SHA256:
        raise AssertionError("vendored selected record")
    return path
BIT = ROOT / "research/unconditional-batched-crt/BIT.md"
LEDGER = ROOT / "research/unconditional-batched-crt/evidence/composition-controls.json"

H = {1: 381024, 2: 400416, 3: 22752, 4: 26880, 5: 29376, 6: 17376, 7: 26784, 42: 288}
W, C, ETA = 28416, Q(8667, 5000000), Q(1, 10**16)
F = 32 * 64**2 * sum(H.values())
PHRASES = [
    "    H={1:381024,2:400416,3:22752,4:26880,5:29376,6:17376,7:26784,42:288}.",
    "With F=32*64^2*sum_r(H_r)=118606528512, t=1-c and eta=10^-16, normalized runtime",
    "    mu_x=(sum_r H_r (r/64)^x+eta F (1/64)^x)/W.",
    "Let W=28416, N=|GL_64(F_q)| and",
    "    c=8667/5000000,",
    "    D-=H; F_I; D+=H; F_I; D=-D; D+=H.",
    "(x-y,y), (Ry,Rx-Ry), (Rx,Rx-Ry), (x-y,x), (y-x,x), (y,x).",
    "      = O_q(V e^(1-c+c^2-ca)).",
]


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def atanh_ln(x, terms=40):
    """1 <= x <= 2: ln x = 2 atanh(z), z = (x-1)/(x+1) <= 1/3; tail <= 2 z^(2N+3) / ((2N+3)(1-z^2))."""
    z = (x - 1) / (x + 1)
    s = sum(z ** (2 * k + 1) / (2 * k + 1) for k in range(terms + 1)) * 2
    return s, s + 2 * z ** (2 * terms + 3) / ((2 * terms + 3) * (1 - z * z))


def ln_bounds(x):
    """x >= 1 rational: ln x = k ln 2 + ln(x / 2^k) with x / 2^k in [1, 2)."""
    k = (x.numerator // x.denominator).bit_length() - 1
    two_lo, two_hi = atanh_ln(Q(2))
    rest_lo, rest_hi = atanh_ln(x / 2 ** k)
    return k * two_lo + rest_lo, k * two_hi + rest_hi


def exp_bounds(y, terms=30):
    """0 <= y <= 1 rational: partial sum, plus remainder <= 3 y^(N+1)/(N+1)!."""
    s, term = Q(0), Q(1)
    for k in range(terms + 1):
        s += term
        term = term * y / (k + 1)
    return s, s + 3 * term


def power_bounds(r, c):
    """(r/64)^(1-c) = (r/64) exp(c ln(64/r)), enclosed for 1 <= r < 64."""
    lo, hi = ln_bounds(Q(64, r))
    return Q(r, 64) * exp_bounds(c * lo)[0], Q(r, 64) * exp_bounds(c * hi)[1]


def mu_bounds(c, h=H):
    lo = hi = Q(0)
    for r, n in h.items():
        a, b = power_bounds(r, c)
        lo, hi = lo + n * a, hi + n * b
    a, b = power_bounds(1, c)
    return (lo + ETA * F * a) / W, (hi + ETA * F * b) / W


def main():
    text = BIT.read_text()
    pins = {row["path"]: row["sha256"] for row in json.loads((Path(__file__).parent / "SOURCES.json").read_text())["files"]}
    for rel in pins:
        if rel != "docs/research/agent-task-catalog.json":
            need(hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == pins[rel], f"pin {rel}")
    need(all(phrase in text for phrase in PHRASES), "BIT.md phrases")
    need(F == 118606528512, "F as printed")

    # 0. H and W are the selected BIT supplier's: selected record -> certificate -> supplier EXPECTED.json.
    selected = json.loads(selected_at_base_path().read_text())
    cert_path = ROOT / selected["certificate"]
    need(hashlib.sha256(cert_path.read_bytes()).hexdigest() == selected["certificate_sha256"], "selected certificate")
    supplier = json.loads(cert_path.read_text())["bit_supplier"]
    need(supplier["path"] == "research/e8-bit-p111-tuned/tune/EXPECTED.json", "selected BIT supplier path")
    exp_path = ROOT / "research/e8-bit-p111-tuned/tune" / "EXPECTED.json"
    blob = b"blob %d\0" % exp_path.stat().st_size + exp_path.read_bytes()
    need(hashlib.sha1(blob).hexdigest() == supplier["git_blob_sha1"], "supplier Git blob")
    nine = json.loads(exp_path.read_text())["nine"]
    need({int(r): n for r, n in nine["profile"].items()} == H, "H is the selected nine-stage profile")
    need(nine["bit"]["live"] == W and nine["bit"]["maxchild"] == max(H), "W is the selected live role count")
    need(nine["bit"]["rank_mass"] == sum(r * n for r, n in H.items()), "rank mass")
    # mu_x is the selected BIT moment, surcharge eta F included: its root is the selected bit_lower to 1e-20,
    # which pins W given H. Without the surcharge the root moves by about 2e-12.
    need(json.loads(cert_path.read_text())["surcharge_model"]["bit"] is True, "selected BIT moment carries a surcharge")
    root = Q(nine["bit_lower"])
    need(mu_bounds(root)[1] < 1 < mu_bounds(root + Q(1, 10**20))[0], "selected BIT root reproduced")
    need(C < root, "c sits below the selected BIT saving")

    # 1. mu_1 is exact and matches #4100's ledger; mu_(1-c) is enclosed below 1.
    mu1 = (sum(r * n for r, n in H.items()) + ETA * F) / (64 * W)
    need(mu1 == Q(json.loads(LEDGER.read_text())["bit_linear_moment"]) and mu1 < 1, "mu_1 exact")
    lo, hi = mu_bounds(C)
    need(hi < 1, "mu_(1-c) < 1, certified")
    need(hi - lo < Q(1, 10**30), "enclosure tight")

    # 2. Headroom: the root c* where mu_(1-c) = 1, bracketed by certified signs.
    c_lo, c_hi = Q(17334270, 10**10), Q(17334271, 10**10)
    need(mu_bounds(c_lo)[1] < 1 < mu_bounds(c_hi)[0], "root bracket")
    need(C < c_lo, "c sits below the root")

    # 3. One more rank-1 child (or W one smaller) would break mu_(1-c) < 1 at this c.
    need(mu_bounds(C, {**H, 1: H[1] + 1})[0] > 1, "one extra rank-1 child exceeds the margin")

    # 4. Stage algebra: w = e^c, n = e^(1-c) gives n^(1-c) w^(1-a) = e^(1-a_next).
    a1 = C * (1 - C)
    a2 = C * (1 - C) + C * a1
    need(a1 == Q("0.00173039532444") and a2 == Q("0.001733394791695384296") == C * (1 - C * C), "a1, a2")
    for a in (Q(0), a1):
        a_next = C * (1 - C) + C * a
        need((1 - C) ** 2 + C * (1 - a) == 1 - a_next, "n^(1-c) w^(1-a) exponent")
        need(1 - C <= 1 - a_next and C <= 1 - a_next, "the n and w terms are no larger")

    # 5. Body word exchanges D and H componentwise in Z/q^w, with R the atom reversal.
    rng, q = random.Random(4100), 7 ** 3
    for _ in range(200):
        n = rng.randrange(1, 9)
        x = [rng.randrange(q) for _ in range(n)]
        y = [rng.randrange(q) for _ in range(n)]
        R = lambda v: v[::-1]
        sub = lambda u, v: [(s - t) % q for s, t in zip(u, v)]
        add = lambda u, v: [(s + t) % q for s, t in zip(u, v)]
        D, Hh = x, y
        states = []
        D = sub(D, Hh); states.append((D, Hh))
        D, Hh = R(Hh), R(D); states.append((D, Hh))
        D = add(D, Hh); states.append((D, Hh))
        D, Hh = R(Hh), R(D); states.append((D, Hh))
        D = [(-s) % q for s in D]; states.append((D, Hh))
        D = add(D, Hh); states.append((D, Hh))
        expected = [(sub(x, y), y), (R(y), sub(R(x), R(y))), (R(x), sub(R(x), R(y))),
                    (sub(x, y), x), (sub(y, x), x), (y, x)]
        need(states == expected, "printed successive states")

    print(json.dumps({
        "status": "PASS_PR4100_BIT_MOMENT_ENCLOSURE",
        "mu_1": str(mu1),
        "mu_1_minus_c_upper": f"{float(hi):.17f}",
        "margin_lower": f"{float(1 - hi):.6e}",
        "root_c_bracket": [str(c_lo), str(c_hi)],
        "c_below_root_by_at_least": f"{float(c_lo - C):.3e}",
        "extra_rank1_child_breaks_margin": True,
        "H_W_bound_to_selected_supplier": "research/e8-bit-p111-tuned/tune/EXPECTED.json (nine)",
        "selected_bit_root_reproduced": str(root),
        "new_kappa_claimed": False,
    }, indent=1))


if __name__ == "__main__":
    sys.exit(main())
