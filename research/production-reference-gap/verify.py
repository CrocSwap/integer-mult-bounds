#!/usr/bin/env python3
"""Actual for_cap admission, independent transcendentals, and scope controls.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from source import authenticate, opened, need
from independent import actual_alpha, ceil_log2, decay_box


def reject(function, text):
    try:
        function()
    except ValueError as error:
        need(text in str(error), "expected rejection: " + text)
        return 1
    raise ValueError("negative control accepted: " + text)


def cap_for(p):
    k = 0
    while 1 << (16 * (k + 1)) <= p ** 15:
        k += 1
    return 1 << k


def fixture(source, raw, p, near_upper, cap, radius, target):
    N = 1 << max(12, ceil_log2(32 * p * p))
    if near_upper:
        e = N // (p * p + 1)
    else:
        e = -(-N // (4 * p * p + 1))
    S, alpha = N - e, actual_alpha(p)
    theta = Q(e, S)
    need(Q(1, 4 * p * p) <= theta <= Q(1, p * p), "actual original fine-prime relative-padding domain")
    ref = source.Reference.for_cap(raw, S, e, alpha, cap, radius, target)
    allocation = ref.allocation
    E, b_e = allocation["error_bits"], ref.spec.entry_bits
    G, H, Qstar = (Q(allocation[name]) for name in ("gauge_bound", "normalized_bound", "inverse_bound"))
    qbar = H / 2
    need(G >= (1 << 8) * alpha and qbar >= 16 * p * cap,
         "actual previous normalized conditioning allocation funds the narrow gap")
    need(Qstar == G * G * H and Qstar >= (1 << 21) * alpha * alpha * p * cap,
         "literal complete source inverse bound")
    need(E == target + ceil_log2(8 * (radius + 1) * Qstar * Qstar)
         and E >= target + 46 + ceil_log2(p * p), "unchanged source e has the derived minimum")
    need(ref.errors["narrow"] <= Q(1, 1 << E) and b_e >= E + 3,
         "actual complete narrow tail/entry allowance")
    J = 2 * (b_e + (-(-(8 * alpha * alpha * ref.rho * ref.rho).numerator //
                        (8 * alpha * alpha * ref.rho * ref.rho).denominator)) + 16) + 32
    width = Q(512 * J * J, 1 << J)
    need(J >= 2 * b_e + 64 and width <= Q(1, 1 << b_e), "literal outward interval width budget")
    a, b = decay_box(2 * alpha * alpha * theta), decay_box(2 * alpha * alpha)
    ideal_lo, ideal_hi = 1 - a[1] - 5 * b[1], 1 - a[0] - 5 * b[0]
    need(ideal_lo >= Q(1, 8 * p * p), "independent actual ideal row-majorant gap")
    need(ideal_lo - 6 * width <= ref.narrow_gap + ref.errors["narrow"] <= ideal_hi,
         "independent direct-series bound agrees with literal certified gap")
    strong = (Q(1, 8) - Q(1, 1 << 46)) / (p * p)
    need(ref.narrow_gap >= strong > Q(1, 16 * p * p), "actual for_cap certificate clears the production gap")
    need(ref.narrow_inverse_bounds is not None and ref._holes is None and
         not ref.weights and not ref.kernel and not ref.entries,
         "conditioning returned without enumerating the full axis or preparing weight pages")
    return dict(p=p,source_size=S,excess=e,target_size=N,theta=str(theta),alpha=alpha,cap=cap,
                radius=str(radius),target=target,error_bits=E,entry_bits=b_e,working_bits=J,
                source_halfwidth=ref.spec.source_halfwidth,target_halfwidth=ref.spec.target_halfwidth,
                weight_precision=ref.weight_precision, gap_scaled_lower_pass=True,
                gap_sha256=sha256(str(ref.narrow_gap).encode()).hexdigest(),
                allocation_sha256=sha256(json.dumps(allocation,sort_keys=True).encode()).hexdigest())


def run():
    inputs = authenticate()
    rows = []
    with opened() as (source, raw):
        for p in (2, 3, 7, 19, 73, 74, 257, 1024, 65536):
            for high in (False, True):
                for cap in sorted({1, cap_for(p)}):
                    rows.append(fixture(source, raw, p, high, cap, Q(1), 1))
        for p, radius, target in ((2, Q(3, 2), 17), (19, Q(1 << 16), 38), (74, Q(3), 74)):
            rows.append(fixture(source, raw, p, False, cap_for(p), radius, target))
        controls = 0
        # The theorem is about for_cap's actual allocation, not every Reference.
        p, N = 257, 1 << 22
        e = -(-N // (4 * p * p + 1))
        direct = source.Reference(raw, N - e, e, actual_alpha(p), 4, 20, 8)
        need(direct.narrow_gap < 0, "underfunded arbitrary Reference negative control")
        controls += 1
        # for_cap alone does not supply the source alpha/theta inequalities.
        bad_alpha = source.Reference.for_cap(raw, 4093, 3, 1, 1, 1, 1)
        need(bad_alpha.narrow_gap < 0, "underfunded source alpha negative control")
        controls += 1
        bad_theta = source.Reference.for_cap(raw, (1 << 100) - 1, 1, 3, 1, 1, 1)
        need(bad_theta.narrow_gap < 0, "missing theta lower bound negative control")
        controls += 1
        controls += reject(lambda: source.Reference.for_cap(raw, 7, 1, 3, 4, 1, 1), "uniform reference cap")
        controls += reject(lambda: source.Reference.for_cap(raw, 7, 1, 3, 1, 1, 1000), "unique retained periodic lifts")
        controls += reject(lambda: source.Reference.for_cap(raw, 4093, 3, 3, 1, Q(1, 2), 1), "uniform reference radius")
    # Independent integer checks of the two induction bases/steps in the proof.
    for b_e in range(8, 513):
        J = 2 * b_e + 64
        need(512 * J * J <= 1 << (b_e + 64), "interval budget induction instances")
        need((J + 2) ** 2 < 2 * J * J, "interval budget induction step")
    need((Q(1, 8) - Q(1, 1 << 46)) > Q(1, 16), "strict uniform production threshold")
    need(192 ** 16 < 1 << 200, "explicit sufficient cap-allocation onset")
    return dict(status="PASS_PRODUCTION_REFERENCE_GAP",source_inputs=inputs,actual_for_cap_cases=len(rows),
                independent_interval_budget_cases=505,negative_controls=controls,fixtures=rows,
                scope='Actual canonical for_cap constructor and literal gap certificate; no physical/native or complete Gaussian replay.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    args = parser.parse_args()
    result = run()
    encoded = json.dumps(result,indent=2,sort_keys=True)+"\n"
    if args.output:
        Path(args.output).write_text(encoded)
    else:
        need(json.loads(encoded) == json.loads((HERE / "evidence/REPLAY.json").read_text()),
             "complete frozen production-reference-gap receipt")
    print(json.dumps({k:v for k,v in result.items() if k!='fixtures'},sort_keys=True))


if __name__ == "__main__":
    main()
