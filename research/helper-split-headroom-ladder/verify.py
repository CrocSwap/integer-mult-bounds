"""Helper-split headroom ladder on the selected #7000 invoice (standard library only).

Model.  For productive-target counts T_r and paid-child counts P_r by rank r,
the raw margin is F(k) = sum_r (T_r - P_r) r^(1-k), and the raw crossing is
its first root in k.  The pinned invoice stores that crossing, and this file
recomputes it from T and P (a calibration of the model, not a review of the
source construction).

Helper structure read from the pinned data: every helper of rank r supplies
18 productive fields of rank r (T_r = 18 h_r for r <= 8 and T_9 = 18 h_9 + 416).
The 416 further rank-9 fields and every field of rank >= 16 are held fixed.
Splitting one helper into parts (a_i) changes F by 18 (sum a_i^p - r^p), p = 1 - k.

Usage:  verify.py          check everything and compare with RESULT.json
        verify.py --emit   print the generated receipt (redirect to RESULT.json)
"""
import hashlib
import json
import pathlib
import sys
from decimal import Decimal, getcontext
from fractions import Fraction
from itertools import combinations_with_replacement
from intervals import Oracle, Q, close

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE.parent / "shared-wire-split-composition"
FULL = SRC / "FULL-RESULT.json"
BIT = SRC / "data" / "bit-admission.json"
RESULT = HERE / "RESULT.json"
FULL_SHA = "d9ba709fa5dcefffe3f3abdcf34600ce188224703cfd743e6db8b58ba4816cb7"
BIT_SHA = "a46b6c6040f75184cab5467656811ad988c216e3bc8e44d595a5015b6e49620b"

getcontext().prec = 80
FIELDS = 18            # productive fields per helper (checked against the data)
KMAX = Decimal("0.02")  # all certificates live on [0, KMAX]
EPS = Decimal("1e-45")  # half-width of every root bracket
NEWTON_CAP = 60
RANK_CAP = 9            # helpers have ranks 1..9
DIGITS = Decimal("1e-40")


def fail(msg):
    raise SystemExit("FAIL: " + msg)


def check(cond, msg):
    if not cond:
        fail(msg)


# ---------------------------------------------------------------- inputs
def read_pinned(path, sha):
    check(path.stat().st_size <= 1000000, "input exceeds the one-megabyte limit")
    raw = path.read_bytes()
    check(hashlib.sha256(raw).hexdigest() == sha, "pinned input hash: " + path.name)
    return json.loads(raw)


def int_map(d):
    return {int(k): int(v) for k, v in d.items()}


def load_invoice(full):
    """T, P, helper counts, with the 18-field structure checked."""
    inv = full["invoice"]
    T, P, H = int_map(inv["T"]), int_map(inv["P"]), int_map(full["native"]["helpers"])
    check(sorted(H) == list(range(1, RANK_CAP + 1)), "helper ranks are 1..9")
    for r in range(1, RANK_CAP):
        check(T[r] == FIELDS * H[r], "18 fields per helper at rank %d" % r)
    extra = T[RANK_CAP] - FIELDS * H[RANK_CAP]
    check(extra == 416, "416 rank-9 fields beyond the helpers")
    check(all(r > RANK_CAP for r in T if r not in H), "fixed fields have rank > 9")
    mass = sum(r * n for r, n in T.items()) - sum(r * n for r, n in P.items())
    check(mass == int(inv["S"]) == 1520, "surplus S = sum r (T_r - P_r)")
    return T, P, H, extra


def frac(text):
    num, _, den = text.partition("/")
    return Fraction(int(num), int(den or 1))


# ------------------------------------------------------- margin arithmetic
class Model:
    """Logarithm table for a fixed rank set; everything else is a pure function."""

    def __init__(self, ranks):
        self.ln = {r: Decimal(r).ln() for r in ranks}
        self.oracle = Oracle(ranks)

    def margin(self, c, k):
        p = 1 - k
        return sum(n * (p * self.ln[r]).exp() for r, n in c.items() if n)

    def slope(self, c, k):
        """G(k) = -F'(k) = sum c_r r^(1-k) ln r."""
        p = 1 - k
        return sum(n * (p * self.ln[r]).exp() * self.ln[r] for r, n in c.items() if n)

    def certify(self, c):
        """F strictly decreasing on [0, KMAX], F(0) > 0 > F(KMAX): unique root."""
        self.oracle.certify(c)

    def root(self, c):
        """Certified root of F on [0, KMAX] by Newton with a sign bracket."""
        self.certify(c)
        k = Decimal("0.004")
        for _ in range(NEWTON_CAP):
            step = self.margin(c, k) / self.slope(c, k)
            k += step
            if abs(step) < Decimal("1e-60"):
                break
        check(0 < k < KMAX, "Newton left the interval")
        self.oracle.bracket(c, k - EPS, k + EPS)
        return k


def invoice_diff(T, P):
    c = {r: T.get(r, 0) - P.get(r, 0) for r in set(T) | set(P)}
    return {r: n for r, n in c.items() if n}


# ------------------------------------------------------------- partitions
def partitions_table(nmax):
    """All integer partitions of n <= nmax (coin-change enumeration, no recursion)."""
    table = [[()] if n == 0 else [] for n in range(nmax + 1)]
    for s in range(1, nmax + 1):
        for n in range(s, nmax + 1):
            table[n] = table[n] + [q + (s,) for q in table[n - s]]
    return [[tuple(sorted(q, reverse=True)) for q in row] for row in table]


def balanced(r, m):
    """Balanced partition of r into min(m, r) parts."""
    parts = min(m, r)
    q, rem = divmod(r, parts)
    return tuple([q + 1] * rem + [q] * (parts - rem))


def majorizes(lam, mu, width):
    """Exact integer test: sorted lam majorizes sorted mu (zero padded)."""
    a = list(lam) + [0] * (width - len(lam))
    b = list(mu) + [0] * (width - len(mu))
    sa = sb = 0
    for x, y in zip(a, b):
        sa, sb = sa + x, sb + y
        if sa < sb:
            return False
    return sa == sb


def check_balanced_lemma(table):
    """Every partition with <= m parts majorizes the balanced m-part one."""
    count = 0
    for r in range(1, RANK_CAP + 1):
        independent = {tuple(reversed(parts))
                       for length in range(1, r + 1)
                       for parts in combinations_with_replacement(range(1, r + 1), length)
                       if sum(parts) == r}
        check(len(table[r]) == len(set(table[r])) and set(table[r]) == independent,
              "partition enumeration agrees with independent combinations")
    for r in range(2, RANK_CAP + 1):
        for m in range(1, r + 1):
            bal = balanced(r, m)
            for lam in table[r]:
                if len(lam) <= m:
                    check(majorizes(lam, bal, m), "balanced partition is minimal")
                    count += 1
    return count


# ----------------------------------------------------------- scenarios
def apply_split(T, r, lam, times):
    """Split `times` helpers of rank r into the parts lam (18 fields each)."""
    out = dict(T)
    out[r] -= FIELDS * times
    for a in lam:
        out[a] = out.get(a, 0) + FIELDS * times
    return out


def split_all(T, H, m):
    """Every helper of rank >= 2 into its balanced m-part partition."""
    out = dict(T)
    for r in range(2, RANK_CAP + 1):
        out = apply_split(out, r, balanced(r, m), H[r])
    return out


def gain(lam, r, p, model):
    value = FIELDS * (sum((p * model.ln[a]).exp() for a in lam) - (p * model.ln[r]).exp())
    coefficients = {r: -FIELDS}
    for a in lam:
        coefficients[a] = coefficients.get(a, 0) + FIELDS
    close(model.oracle.moment(coefficients, 1 - p - EPS, 1 - p + EPS), q(value))
    return value


def ceil_div(num, den):
    q = num / den
    n = int(q)
    return n if n >= q else n + 1


# ------------------------------------------------------------- receipt
def q(x):
    return str(x.quantize(DIGITS))


def build(full, bit):
    T, P, H, extra = load_invoice(full)
    ranks = sorted(set(T) | set(P) | set(range(1, RANK_CAP + 1)))
    model = Model(ranks)
    # Independent integer-power test of every rank's enclosure at k=1/100.
    for r, (low, high) in model.oracle.powers(Fraction(1, 100)).items():
        exact = r**99 * Q**100
        check(low**100 <= exact <= high**100, "rational-exponent control")
    c0 = invoice_diff(T, P)
    k0 = model.root(c0)
    stored = Decimal(full["invoice"]["raw_crossing"])
    check(abs(stored - k0) < Decimal("1e-60"), "stored raw crossing reproduced")
    pin = frac(full["gate"]["BIT_pin"])
    paired = frac(bit["ordinary_admitted"])
    check(pin == Fraction(376669, 10 ** 8) and paired == Fraction(12039, 3125000), "wall values")
    walls = {"pin": Decimal(pin.numerator) / Decimal(pin.denominator),
             "paired": Decimal(paired.numerator) / Decimal(paired.denominator)}
    for w in walls.values():
        close(model.oracle.moment(c0, w), q(model.margin(c0, w)))
    check(k0 < walls["pin"] < walls["paired"], "walls above the selected crossing")
    table = partitions_table(RANK_CAP)
    lemma = check_balanced_lemma(table)
    ladder = ladder_rows(T, P, H, model, k0)
    exch = exchange_rows(T, P, H, model, c0, k0, walls, table)
    mins = touched_rows(T, P, H, model, c0, walls)
    at_one = sum(split_all(T, H, RANK_CAP).values()) - sum(P.values())
    check(at_one == 24040, "full-split endpoint explains the interval restriction")
    return {
        "verifier_sha256": {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
                            for name in ("verify.py", "intervals.py")},
        "inputs": {"FULL-RESULT.json": FULL_SHA, "bit-admission.json": BIT_SHA},
        "helpers": {str(r): H[r] for r in sorted(H)},
        "fixed_rank9_fields": extra,
        "kappa0": q(k0),
        "kappa0_bracket": [str(k0 - EPS), str(k0 + EPS)],
        "walls": {k: q(v) for k, v in walls.items()},
        "wall_margin_F": {k: q(model.margin(c0, v)) for k, v in walls.items()},
        "lemma_partition_checks": lemma,
        "ladder": ladder,
        "exchange": exch,
        "min_touched": mins,
        "claim_interval": ["0", "0.02"],
        "numeric_error_bound": "1e-39",
        "full_split_margin_at_one": at_one,
    }


def ladder_rows(T, P, H, model, k0):
    rows, prev = [], k0 - 1
    for m in range(1, RANK_CAP + 1):
        km = model.root(invoice_diff(split_all(T, H, m), P))
        check(km > prev or m == 1, "ladder strictly increasing")
        prev = km
        rows.append({"m": m, "kappa": q(km), "gain": q(km - k0),
                     "root_bracket": [str(km - EPS), str(km + EPS)]})
    check(rows[0]["kappa"] == q(k0), "m = 1 is the selected invoice")
    return rows


def exchange_rows(T, P, H, model, c0, k0, walls, table):
    p0, rows = 1 - k0, []
    for r in range(2, RANK_CAP + 1):
        for lam in table[r]:
            if len(lam) < 2:
                continue
            one = model.root(invoice_diff(apply_split(T, r, lam, 1), P))
            row = {"r": r, "parts": list(lam), "gain_at_k0": q(gain(lam, r, p0, model)),
                   "single_split_dk": q(one - k0), "available": H[r],
                   "root_bracket": [str(one - EPS), str(one + EPS)]}
            for name, w in walls.items():
                g = gain(lam, r, 1 - w, model)
                count = ceil_div(-model.margin(c0, w), g)
                # These are algebraic counts; stock may be insufficient.
                for number, sign in ((count - 1, -1), (count, 1)):
                    c = invoice_diff(apply_split(T, r, lam, number), P)
                    interval = model.oracle.moment(c, w)
                    check(interval[1] < 0 if sign < 0 else interval[0] > 0,
                          "wall count is not minimal")
                row["need_" + name] = count
                row["available_" + name] = count <= H[r]
            rows.append(row)
    return rows


def touched_rows(T, P, H, model, c0, walls):
    out = {}
    for name, w in walls.items():
        for label, pieces in (("any", RANK_CAP), ("binary", 2)):
            lam = balanced(9, pieces)
            best = gain(lam, 9, 1 - w, model)
            used = ceil_div(-model.margin(c0, w), best)
            check(0 < used <= H[9], "rank-nine stock suffices")
            for r in range(2, RANK_CAP):
                other = gain(balanced(r, pieces), r, 1 - w, model)
                check(Decimal(q(best)) - Decimal(q(other)) > Decimal("2e-39"),
                      "rank nine has the greatest certified gain")
            # Exact interval proof: no used-1 helpers can suffice even if all
            # receive the largest per-helper gain, while used rank-nine do.
            model.certify(invoice_diff(apply_split(T, 9, lam, used), P))
            for number, positive in ((used - 1, False), (used, True)):
                c = invoice_diff(apply_split(T, 9, lam, number), P)
                interval = model.oracle.moment(c, w)
                check(interval[0] > 0 if positive else interval[1] < 0,
                      "minimal touched-helper certificate")
            out[name + "_" + label] = {"helpers": used,
                                       "plan": [[9, used]]}
    return out


# ------------------------------------------------------------ controls
def run_controls(full, receipt):
    T, P, _, _ = load_invoice(full)
    model = Model(sorted(set(T) | set(P)))
    bad = json.loads(json.dumps(full))
    bad["native"]["helpers"]["4"] += 1
    expect_fail(lambda: load_invoice(bad), "helper count off by one")
    expect_fail(lambda: model.oracle.powers(Fraction(9, 10)), "outside certified range")
    c0 = invoice_diff(T, P)
    k0 = Decimal(receipt["kappa0"])
    check(model.margin(c0, k0 - Decimal("1e-6")) > 0 > model.margin(c0, k0 + Decimal("1e-6")),
          "wrong-root control brackets the real root")
    expect_fail(lambda: check_not_balanced((3, 1), 2, 4), "unbalanced partition is not minimal")
    expect_fail(lambda: model.oracle.bracket(c0, Decimal("0.004"), Decimal("0.005")),
                "a bracket missing the root")
    expect_fail(lambda: model.certify({r: -n for r, n in c0.items()}), "reversed monotonicity")
    return 6


def check_not_balanced(lam, m, r):
    check(majorizes(balanced(r, m), lam, m), "unbalanced partition is not minimal")


def expect_fail(fn, label):
    try:
        fn()
    except (SystemExit, ValueError):
        return
    fail("control did not reject: " + label)


def summary(receipt):
    lad = {row["m"]: row["kappa"] for row in receipt["ladder"]}
    return ("PASS_HELPER_SPLIT_HEADROOM_LADDER kappa0=%s m2=%s m9=%s "
            "pin_any=%d pin_binary=%d paired_any=%d paired_binary=%d"
            % (receipt["kappa0"][:14], lad[2][:12], lad[9][:12],
               receipt["min_touched"]["pin_any"]["helpers"],
               receipt["min_touched"]["pin_binary"]["helpers"],
               receipt["min_touched"]["paired_any"]["helpers"],
               receipt["min_touched"]["paired_binary"]["helpers"]))


def main(argv):
    check(argv in ([], ["--emit"]), "usage: verify.py [--emit]")
    full = read_pinned(FULL, FULL_SHA)
    bit = read_pinned(BIT, BIT_SHA)
    receipt = build(full, bit)
    text = json.dumps(receipt, indent=1, sort_keys=True) + "\n"
    if "--emit" in argv:
        sys.stdout.write(text)
        return
    check(RESULT.read_text() == text, "RESULT.json differs from the recomputed receipt")
    controls = run_controls(full, receipt)
    print(summary(receipt), "controls=%d" % controls)


if __name__ == "__main__":
    main(sys.argv[1:])
