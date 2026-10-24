"""This word's bit side composed with PR #433's complex supplier, with PR #433's own bit pricing, finite invoice and
outer tail (icekylinx's code/bit_price.py and code/combined.py, ported line by line onto this package's receipts).

Bit price (#433 bit_price.py): PR #315's moment.certify with the inherited 10^-16 bad-branch allowance; c is its
  10^-24-grid lower endpoint; the second engine (base_two_moment, same allowance) must put the lower endpoint below 1
  and the upper endpoint above 1.
Finite invoice (#433 combined.py): #386's coefficient with the fresh prefix bound charged at the next multiple of 64
  bits (at most 256), two-level coefficient below 2^512, row coefficient 18,355 < 20,161.
Tail (#433 combined.py): eta = beta = 10^-18, seed s = min(c, (1 - beta) b) - 10^-24, six bootstrap levels with the
  512-bit cutoff, kappa = the last 10^-18 grid point below (1 - eta) q / (1 + q), q = a_6 (1 - 2 eta); PR #315's outer
  assembly with its 47 strict inequalities; next grid point, zero eta, zero beta and unit beta rejected.
Controls: PR #433's stated R758 profile must price to PR #433's bit c, and (that c, PR #433's b) must give PR #433's
  kappa, before this word is composed.
usage: compose433.py --pricing DIR --out DIR --cited FILE --receipt CERTIFICATE.json
Prepared by eumemic with Anthropic Claude assistance; Apache-2.0."""
import argparse
import hashlib
import importlib.util
import json
from fractions import Fraction as Q
from pathlib import Path


def load(path, name):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


ap = argparse.ArgumentParser()
ap.add_argument("--pricing", type=Path, required=True)
ap.add_argument("--out", type=Path, required=True)
ap.add_argument("--cited", type=Path, required=True)
ap.add_argument("--receipt", type=Path, required=True)
a = ap.parse_args()
M = load(a.pricing / "moment.py", "c433_moment")
Other = load(a.pricing / "base_two_moment.py", "c433_other")
Outer = load(a.pricing / "outer.py", "c433_outer")
cited = json.loads(a.cited.read_text())
cert = json.loads(a.receipt.read_text())
assert cert["status"] == "PASS_CONDITIONAL_SPLIT_CENTRE_ASSEMBLY" and cert["binding_component"] == "bit"
assert (cert["complex_lower"], cert["bit_lower"], cert["kappa"]) == (cited["b"], cited["bit_c"], cited["kappa"])
grid = Q(1, 10 ** 18)


def price(P, m, W):
    """#433 bit_price.py: 10^-24 lower endpoint of PR #315's certify (bad-branch allowance), second engine check"""
    root = M.certify(P, m, W, True)
    lo, hi = Q(root["lower"]), Q(root["upper"])
    fb = 32 * m * m * sum(P.values())

    def other(x):
        l, u = Other.moment(m, W, list(P.items()), x)
        p, q = Other.moment(m, W, [(1, fb)], x)
        return l + p / 10 ** 16, u + q / 10 ** 16
    assert other(lo)[1] < 1 < other(hi)[0]
    lo2, hi2 = Other.moment(m, W, list(P.items()), lo)
    bl, bh = Other.moment(m, W, [(1, fb)], lo)
    assert hi2 + bh / 10 ** 16 < 1                      # #433 combined.py's check at c
    return lo, hi


def tail(c, b):
    """#433 combined.py: six fixed bootstrap levels and the 47-inequality outer assembly"""
    eta = beta = Q(1, 10 ** 18)
    s = min(c, (1 - beta) * b) - Q(1, 10 ** 24)
    assert 0 < s < c and s < (1 - beta) * b
    chain = [Q(384599, 10 ** 10)]
    cutoffs = []

    def ceil(x):
        return -((-x.numerator) // x.denominator)
    for _ in range(6):
        old = chain[-1]
        z = (1 - s) * s + s * old
        gap = min(s - z, 1 - z - s, 1 - z - s * (1 - old), 1 - s)
        assert old < z < s < 1 - z and gap > 0
        cutoff = max(ceil(36 / gap ** 2), ceil(2 * (4 + 512) / gap))
        assert cutoff * gap ** 2 >= 36 and cutoff * gap >= 2 * (4 + 512)
        cutoffs.append(dict(gap=str(gap), cutoff_log2=str(cutoff)))
        chain.append(z)
    q = chain[-1] * (1 - 2 * eta)
    ticks = (1 - eta) * q / (1 + q) / grid
    k = grid * ((ticks.numerator - 1) // ticks.denominator)
    bridge = {"semantic": {"C0": {"base": 2, "exponent": 210000}, "strict_literal_gap": 1},
              "rows": {"degree_gap": Q(10 ** 6) - Q(51 * 20161, 25)}}
    asm = Outer.assembly(chain[-1], b, bridge, k, eta=eta, beta=beta)
    assert len(asm["strict_constraints"]) == 47 and all(x > 0 for x in asm["strict_constraints"].values())
    rejected = []
    for name, kk, ee, bb in [("next_grid", k + grid, eta, beta), ("zero_eta", k, Q(0), beta),
                             ("zero_beta", k, eta, Q(0)), ("unit_beta", k, eta, Q(1))]:
        try:
            Outer.assembly(chain[-1], b, bridge, kk, eta=ee, beta=bb)
        except AssertionError:
            rejected.append(name)
        else:
            raise AssertionError(name)
    binding = "bit" if c < (1 - beta) * b else "complex"
    return k, binding, rejected, cutoffs, asm


b = Q(cited["b"])
# control 1: PR #433's stated R758 profile, priced by the same code, gives PR #433's bit c
L433 = {int(r): n for r, n in cited["bit_local_profile"].items()}
R433 = cited["bit_R"]
P433 = {r: 72 * n for r, n in L433.items()}
for r, n in ((7, 48 * 120), (14, 32 * 120), (28, 32 * 120), (42, 32 * 120)):
    P433[r] = P433.get(r, 0) + n
W433 = 64 * 120 + 9 * R433
assert sum(r * n for r, n in L433.items()) == 8 * R433 + 72 + 2 * 120 * 7
assert 64 * W433 - sum(r * n for r, n in P433.items()) == 2496
c433, _ = price(P433, 64, W433)
assert c433 == Q(cited["bit_c"]), (str(c433), cited["bit_c"])
# control 2: PR #433's (c, b) through the tail gives PR #433's kappa
k433, bind433, _, _, _ = tail(c433, b)
assert k433 == Q(cited["kappa"]) and bind433 == "bit", str(k433)
print("   control: PR #433's R758 profile prices to c = %s (= PR #433 bit_lower); with b = %s the tail gives kappa = %s"
      " (= PR #433, bit-bound)" % (c433, b, k433), flush=True)
# this word: the compressed nine-stage receipts of global_word_g.py / audit_g.py, #433's invoice and tail
out = a.out
g = json.loads((out / "GLOBAL.json").read_text())
geo = json.loads((out / "GEOMETRY.json").read_text())
audit = json.loads((out / "AUDIT.json").read_text())
assert audit["template_sha256"] == g["template_sha256"] and len(audit["mutations_rejected"]) == 8
P = {int(r): z for r, z in audit["profile"].items()}
m, W = 64, g["live"]
E = sum(P.values())
T, L, R, V, K = 8, 9, g["R"], 120, 4
mass = sum(r * z for r, z in P.items())
assert m * W - mass == 2496 and W == 64 * V + 9 * R
physical = g["physical"]
d = m * m
N = 2 * m
unit = L * T * g["local_additions"] + g["bridge_additions"]
J = 8 * T * L * (2 * V + R) + 8 * (2 * K * V * T) + 2 * g["bank_assignments"] + 2 * g["copy_erase_episodes"]
high = 16 * (d + 1) ** 2
good = 8 * m * m + 8
compiler = 128 * N ** 3
selectors = 2 * L * T * ((W - 1) + R * m * (geo["max_route_factors"] + (m - 1) + m))
prefix = int(g["global_prefix_bound"])
charged_prefix = 64 * ((prefix.bit_length() + 63) // 64)
assert prefix < 1 << charged_prefix <= 1 << 256
coefficient = unit + J * high + J * physical + E * (good + compiler) + 16 * m ** 3 + g["copy_erase_episodes"] + selectors + prefix + 1
two = (coefficient + 1) ** 2 * (E + 1) ** 2
assert two < 1 << 512 and 2 * max(P) ** 2 < m * m
row = 2 * (m * m + 1) + 9909 + 252
assert row == 18355 < 20161
assert geo["bad_prime_factors"] == [2] and geo["route_denominators"] == [1, 2, 4]
c, chi = price(P, m, W)
k, binding, rejected, cutoffs, asm = tail(c, b)
result = dict(status="PASS_BIT_SIDE_COMPOSED_WITH_PR433_COMPLEX", bit_lower=str(c), bit_upper=str(chi),
              bit_lower_decimal=format(float(c), ".24f"), complex_lower=str(b), kappa=str(k),
              kappa_decimal=format(float(k), ".18f"), binding_component=binding,
              gain_over_pr433_percent=float(100 * (k / Q(cited["kappa"]) - 1)),
              bit_gain_over_pr433_percent=float(100 * (c / Q(cited["bit_c"]) - 1)),
              bit_invoice=dict(prefix_bits=prefix.bit_length(), charged_prefix_bits=charged_prefix,
                               coefficient_bits=coefficient.bit_length(), two_level_coefficient_bits=two.bit_length(),
                               charged_two_level_coefficient_bits=512, row_coefficient=row, live=W, physical=physical),
              strict_outer_constraints={n: str(x) for n, x in asm["strict_constraints"].items()},
              minimum_strict_constraint=str(min(asm["strict_constraints"].values())), outer_controls=rejected,
              bootstrap=cutoffs, bit_global_sha256=sha(out / "GLOBAL.json"), bit_audit_sha256=sha(out / "AUDIT.json"),
              controls=dict(pr433_bit_c=str(c433), pr433_kappa=str(k433)), source=cited["source"])
(out / "COMPOSED-433.json").write_text(json.dumps(result, indent=2) + "\n")
print("PASS this word with PR #433's bit engine and invoice: c = %s = %.24f (prefix %d bits, charged %d; two-level %d"
      " bits < 512)" % (c, float(c), prefix.bit_length(), charged_prefix, two.bit_length()), flush=True)
print("PASS composed with PR #433's complex b = %s: kappa = %s = %.18f (%s-bound; PR #433: %s, %+.6f%%; 47 strict"
      " inequalities, next grid point, zero eta, zero beta and unit beta rejected)"
      % (b, k, float(k), binding, cited["kappa"], result["gain_over_pr433_percent"]), flush=True)
