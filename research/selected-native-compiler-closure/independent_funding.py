"""Independent exact arithmetic for the selected joint compiler/native construction.

No contributor scientific module is imported.  Logarithms use a rational series
with an exact remainder; powers use alternating exponential series, rather than
the predecessor's 113 repeated squarings.  All scientific inequalities are over
integers and Fraction objects.  This is a certificate check, not a proof kernel.
"""

from fractions import Fraction as Q
from functools import cache
from copy import deepcopy
import json
from pathlib import Path

BITS = 352
SCALE = 1 << BITS


def need(value, message):
    if not value:
        raise ValueError(message)


def floor_q(x):
    return x.numerator // x.denominator


def ceil_q(x):
    return -((-x.numerator) // x.denominator)


@cache
def log_unit(x):
    """Exact rational enclosure of log(x), for 1 <= x <= 2."""
    need(Q(1) <= x <= Q(2), "unit logarithm domain")
    z = (x - 1) / (x + 1)
    z2 = z * z
    power = z
    value = Q(0)
    terms = 140
    for j in range(terms):
        value += 2 * power / (2 * j + 1)
        power *= z2
    # Every remaining denominator is >= 2*terms+1.  Sum its geometric powers.
    remainder = 2 * power / ((2 * terms + 1) * (1 - z2))
    return floor_q(value * SCALE), ceil_q((value + remainder) * SCALE)


@cache
def log_bounds(x):
    """Integer endpoints, in units SCALE^-1, for the natural logarithm."""
    x = Q(x)
    need(x > 0, "positive logarithm argument")
    if x < 1:
        lo, hi = log_bounds(1 / x)
        return -hi, -lo
    h = max(0, x.numerator.bit_length() - x.denominator.bit_length())
    while x < 1 << h:
        h -= 1
    while x >= 1 << (h + 1):
        h += 1
    lo, hi = log_unit(x / (1 << h))
    l2, u2 = log_unit(Q(2))
    return lo + h * l2, hi + h * u2


def exp_poly(x, degree):
    """Taylor polynomial of exp(-x), evaluated as an exact rational."""
    term = value = Q(1)
    for j in range(1, degree + 1):
        term *= -x / j
        value += term
    return value


@cache
def power_bounds(rank, saving):
    """Enclose rank^(1-saving), using monotonicity and an alternating series."""
    need(type(rank) is int and rank >= 1, "positive integer rank")
    saving = Q(saving)
    need(0 <= saving <= Q(1, 250), "supported saving interval")
    lo, hi = log_bounds(Q(rank))
    xlo, xhi = saving * Q(lo, SCALE), saving * Q(hi, SCALE)
    need(0 <= xlo <= xhi <= Q(1, 16), "alternating exponential domain")
    # On this domain consecutive term magnitudes decrease.  The odd partial
    # sum is a lower bound and the even partial sum is an upper bound.
    low = rank * exp_poly(xhi, 51)
    high = rank * exp_poly(xlo, 50)
    return floor_q(low * SCALE), ceil_q(high * SCALE)


def histogram(raw):
    result = {int(k): int(v) for k, v in raw.items()}
    need(len(result) == len(raw) and all(k >= 1 and v >= 1 for k, v in result.items()),
         "invalid rank histogram")
    return result


def selected_certificate(targets, paid, witness, expected_ambient):
    targets, paid = histogram(targets), histogram(paid)
    c = Q(witness["raw_saving"])
    u = Q(witness["uniform_saving"])
    ambient = witness["source_ambient"]
    need(ambient == expected_ambient, "source-specific complete working ambient")
    need(0 < u < c <= Q(1, 250), "uniform price order")
    need(max(max(targets), max(paid)) <= ambient, "true source ambient")
    need(sum(targets.values()) == witness["source_target_count"], "source target census")
    need(sum(paid.values()) == witness["source_paid_count"], "source paid census")
    weighted = {k: tuple(n * x for x in power_bounds(k, c)) for k, n in targets.items()}
    target_lo = sum(x[0] for x in weighted.values())
    paid_hi = sum(n * power_bounds(k, c)[1] for k, n in paid.items())
    paid_mass = sum(k * n for k, n in paid.items())
    delta1 = Q(target_lo - paid_hi, target_lo)
    lratio, _ = log_bounds(Q(target_lo, SCALE * paid_mass))
    l8, _ = log_bounds(Q(8))
    delta2 = Q(lratio, SCALE) + c * Q(l8, SCALE)
    delta = min(delta1, delta2)
    need(delta > 0, "raw/split funding margin")

    v = witness["v"]
    j = v.bit_length() - 1
    need(v == 1 << j, "power-of-two product length")
    counts = {int(k): n for k, n in witness["type"].items()}
    need(set(counts) == set(targets) and sum(counts.values()) == v
         and all(type(n) is int and n >= 0 for n in counts.values()), "type census")
    # Independent certificate of a mode for the ACTUAL real weights, not just
    # the predecessor's rounded weight vector.  Selected final priorities beat
    # all unselected next priorities.  This certifies a maximum product term.
    for i, ni in counts.items():
        for k, nk in counts.items():
            if nk:
                need(weighted[i][1] * nk <= weighted[k][0] * (ni + 1),
                     "the recorded type is not certified modal")
    needed = len(targets) * (j + 1) + 3
    need(v * delta >= needed, "modal/split exponential domination")
    log_k_lo = sum(n * log_bounds(Q(k))[0] for k, n in counts.items())
    need(log_k_lo >= v * log_bounds(Q(16))[1], "retained grade below 16^v")

    h = witness["H"]
    log_a_upper = (ambient - 1).bit_length()
    need(h % v == 0 and h >= 1 + v * log_a_upper, "root ambient and depth")
    threshold = 1 + c * (2 + v * log_a_upper)
    need(h * (c - u) > threshold, "complete root funding")
    width_degree = witness["batch_width_degree_upper"]
    visit_degree = witness["all_recursive_visits_degree_per_root_owner"]
    b0, q0 = sum(targets.values()), sum(paid.values())
    need(b0 <= 1 << width_degree, "productive width polynomial")
    need(2 * ambient * q0 <= 1 << visit_degree, "recursive visits polynomial")
    need(ambient >= 64 and b0 + q0 + ambient * q0 + 2 < 1 << 27,
         "macro syntax polynomial")
    # The proof permits at most 2v(D+1) unfinished raw contexts and D<=H/v.
    contexts = 2 * (h + v)
    precision_factor = 356 * contexts
    need(precision_factor.bit_length() <= h, "selected unfinished-context precision")
    need(width_degree + visit_degree + 6 + 1 + 1 <= 51,
         "full logical record count")
    return {
        "raw_saving": str(c), "uniform_saving": str(u),
        "true_ambient": ambient, "targets": b0, "paid": q0,
        "type_length": v, "mode_exchange_checks": len(counts) ** 2,
        "H": h, "mu_strict_upper": "3/8",
        "width_degree": width_degree, "record_degree_upper": 51,
        "unfinished_raw_context_bound": contexts,
        "precision_factor_bit_length": precision_factor.bit_length(),
        "uniform_price_gap": str(h * (c - u) - threshold),
        "modal_domination_margin_lower": str(floor_q((v * delta - needed) * 10**12) / Q(10**12)),
    }


def ordinary_closure(binary, complex_, claimed):
    rho = Q(1, 250)
    cover_loss = Q(1, 10**10)
    covered = Q(binary["uniform_saving"]) - cover_loss
    need(covered == Q(19262649, 5000000000), "covered selected price")
    need(Q(64, 2**45) < cover_loss / 4, "complete bad-leaf debit")
    stages = [Q(0), Q(17, 5000), Q(38507, 10000000), Q(12039, 3125000)]
    gaps = []
    for previous, following in zip(stages, stages[1:]):
        gap = (1 - rho) * covered + rho * previous - following
        need(min(gap, rho - following, 1 - rho - following) > 0,
             "cold predecessor closure")
        gaps.append(str(gap))
    need(stages[-1] > Q(376669, 100000000), "selected complex movement requirement")
    need(Q(complex_["uniform_saving"]) - claimed == Q(6, 10**14),
         "selected complex outer slack")
    return {"covered_saving": str(covered), "ordinary_stages": list(map(str, stages)),
            "strict_stage_margins": gaps, "complete_kappa": str(claimed)}


def arithmetic_calibration():
    """An algebraic oracle unrelated to the log/exp series implementation."""
    ranks = (1, 2, 3, 8, 16, 127, 134, 145, 153)
    for rank in ranks:
        lo, hi = power_bounds(rank, Q(1, 250))
        exact = rank**249 * SCALE**250
        need(lo**250 <= exact <= hi**250, "independent power enclosure calibration")
    return {"ranks": list(ranks), "saving": "1/250",
            "oracle": "lo^250 <= rank^249*SCALE^250 <= hi^250"}


def funding_controls(targets, paid, witness):
    """Perturb scientific inputs after authentication; require named failures."""
    def rejects(name, mutate, expected):
        t, p, w = deepcopy(targets), deepcopy(paid), deepcopy(witness)
        mutate(t, p, w)
        try:
            selected_certificate(t, p, w, 153)
        except ValueError as error:
            need(str(error) == expected, "wrong mutation gate for " + name + ": " + str(error))
            return {"mutation": name, "rejected_by": str(error)}
        raise ValueError("scientific mutation survived: " + name)

    def remove_paid(t, p, w):
        p["1"] -= 1

    def downgrade(t, p, w):
        t["1"] += t.pop("145")

    def nonmodal(t, p, w):
        w["type"]["1"] += 10
        w["type"]["145"] -= 10

    def stale_ambient(t, p, w):
        w["source_ambient"] = 127

    def insufficient_carrier(t, p, w):
        # Preserve divisibility by v and the ambient bound, fail the price gap.
        w["H"] = 16 * w["v"]

    def no_uniform_gap(t, p, w):
        w["uniform_saving"] = w["raw_saving"]

    return [
        rejects("omit_paid_occurrence", remove_paid, "source paid census"),
        rejects("downgrade_high_target", downgrade, "raw/split funding margin"),
        rejects("same_length_nonmodal_type", nonmodal, "the recorded type is not certified modal"),
        rejects("stale_working_ambient", stale_ambient, "source-specific complete working ambient"),
        rejects("insufficient_new_carrier", insufficient_carrier, "complete root funding"),
        rejects("no_uniform_price_gap", no_uniform_gap, "uniform price order"),
    ]


def main():
    here = Path(__file__).resolve().parent
    c = json.loads((here / "inputs/selected-complex.json").read_text())
    b = json.loads((here / "inputs/selected-bit.json").read_text())
    result = json.loads((here / "inputs/compiler/RESULT.json").read_text())
    cc = selected_certificate(c["invoice"]["T"], c["invoice"]["P"], result["selected_complex"], 9 + 18 * 8)
    bb = selected_certificate(b["targets"], b["paid"], result["selected_BIT"], 8 + 18 * 7)
    out = {"complex": cc, "binary": bb,
           "closure": ordinary_closure(bb, cc, Q(363005817, 100000000000)),
           "calibration": arithmetic_calibration(),
           "negative_controls": funding_controls(c["invoice"]["T"], c["invoice"]["P"],
                                                 result["selected_complex"])}
    print(json.dumps(out, indent=2))
    print("PASS_INDEPENDENT_SELECTED_JOINT_FUNDING")


if __name__ == "__main__":
    main()
