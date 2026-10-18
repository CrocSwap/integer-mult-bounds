#!/usr/bin/env python3
"""Paureel's fixed-exponent refinement; exact arithmetic, conditional interfaces.

The standalone calculation is independent of certify.py. --upstream also checks
the paired circuit, frames, source hashes, and agreement with that verifier.
Prepared with assistance from OpenAI Codex; see docs/paired-tuned-parameters.md.
"""
import argparse
from dataclasses import dataclass
from fractions import Fraction as Q
import json
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_COMMIT = "bcd4ebde8692383539f8a48734e5fbf3a18a32c2"
A = Q(296, 10**11)
S = Q(1, 10**11)
KAPPA = Q(17523184, 10**25)
LOG_BOUND = Q(11737, 1000)


def require(condition, message):
    if not condition:
        raise ValueError(message)


@dataclass(frozen=True)
class Parameters:
    tau: Q
    sigma: Q
    epsilon: Q
    c: Q
    lam: Q
    lamp: Q
    kappa: Q
    beta: Q
    delta: Q
    C1: int


def parameters(a=A, s=S, beta=Q(99999912384, 10**11),
               epsilon=Q(1999999999999, 10**13), delta=Q(1, 10**14),
               kappa=KAPPA):
    return Parameters(1-a, 1-s, epsilon, beta*a,
                      1-(1+beta)*a*a/2, 1-beta*a*a, kappa, beta, delta, 2)


def evaluate(p):
    """Independent transcription of the thirty tight-Gaussian side conditions."""
    e, c, t, s, b = p.epsilon, p.c, p.tau, p.sigma, p.beta
    slacks = {
        "tau_positive": t, "tau_below_one": 1-t,
        "sigma_positive": s, "sigma_below_one": 1-s,
        "c_positive": c, "epsilon_positive": e,
        "beta_positive": b, "beta_below_one": 1-b,
        "lambda_above_tau": p.lam-t, "lambda_above_sigma": p.lam-s,
        "lambda_below_one": 1-p.lam,
        "packed_overhead": p.lam-t*(1+c/b),
        "lambda_prime_above_lambda": p.lamp-p.lam,
        "leaf_cost": p.lamp-(s+b*(1-s)),
        "lambda_prime_below_one": 1-p.lamp,
        "guard_width": 1-e*p.C1,
        "dimension_upper_bound": Q(1, 3)-e,
        "crt_layout": (1-t)*(1-e),
        "gaussian_cost": Q(1, 4)-p.delta-Q(5, 4)*e,
        "prefix_cost": 1-e*(1+c), "scalar_cost": 1-p.delta-e,
        "delta_positive": p.delta, "delta_below_one_eighth": Q(1, 8)-p.delta,
        "prime_interval_growth": 1-2*e,
        "alpha_below_sqrt_p": Q(1, 4)-e/4,
        "gamma_sublinear": Q(1, 2)-Q(3, 2)*e,
        "K_smaller_than_ell": 1-e-e*c, "K_dominates_log_p": e*c,
        "r_superpolynomial": 1-e, "kappa_positive": p.kappa,
    }
    require(p.C1 >= 2 and Q(9, 10) <= b < 1,
            "Stopping guard requires C1>=2 and 9/10<=beta<1")
    for name, slack in slacks.items():
        require(slack > 0, f"Failed strict constraint: {name}")
    gs = {"g1": 1-e*(1+c), "g2": e*c*(1-t), "g3": e*(1-p.lamp),
          "g4": (1-t)*(1-e), "g5": Q(1, 4)-p.delta-Q(5, 4)*e,
          "g6": 1-p.delta-e, "g7": e}
    minimum = min(gs.values())
    require(minimum > p.kappa, "Need a positive absorption gap")
    return dict(parameters={k: str(v) for k, v in vars(p).items()},
                constraint_slacks={k: str(v) for k, v in slacks.items()},
                margins={k: str(v) for k, v in gs.items()},
                minimum_margin=str(minimum), absorption_gap=str(minimum-p.kappa),
                limiting_margins=[k for k, v in gs.items() if v == minimum])


def capacity_polynomial(z, a=A, s=S):
    return a*z*z-(s+a*a)*z+a*a*s


def capacity_enclosure(a=A, s=S, steps=160):
    """Enclose the smaller root on an interval where the polynomial decreases."""
    require(0 < a < 1 and s > 0 and a*a < s/10,
            "Capacity enclosure requires 0<a<1 and a^2<s/10")
    require(isinstance(steps, int) and steps >= 1, "Need positive bisection count")
    lo, hi = Q(0), a*a
    require(2*a*hi < s+a*a, "Polynomial must decrease throughout interval")
    require(capacity_polynomial(lo, a, s) > 0 > capacity_polynomial(hi, a, s),
            "Missing root sign change")
    for _ in range(steps):
        mid = (lo+hi)/2
        value = capacity_polynomial(mid, a, s)
        if value > 0:
            lo = mid
        elif value < 0:
            hi = mid
        else:
            lo = hi = mid
            break
    return lo, hi


def supremum_enclosure(a=A, s=S, steps=160):
    lo, hi = capacity_enclosure(a, s, steps)
    return lo/(5+4*lo), hi/(5+4*hi)


def guard_checks(beta):
    """Recompute retained complex counts and stopped-depth constants independently."""
    h = 50
    v, m = comb(h, 3), h**3
    N, I = v**3, 3*v*v
    W = 2*N+I*(v*(comb(h-3, 3)+3*(h-3))+h+1)
    L = I*(h+1)*h
    sc = W*m-2*N+2*L
    E = 64*(W+m+1)**3
    B = sc+E
    depth = 5-4*beta
    require(m >= 3 and 2 <= sc < m**5, "Stopped guard count failed")
    require(Q(9, 10) <= beta < 1 and depth <= Q(7, 5) and depth+Q(1, 2) < 2,
            "Stopped guard exponent failed")
    require(sc*(8+E) <= 9*B*B, "One-piece depth constant failed")
    require(18*m*B*B+18 <= 36*m*B*B < 128*m*B*B,
            "Layer depth constant failed")
    require(2*L < N, "Complex residual deficit is nonpositive")
    require(Q(2*N-2*L, W*m) > S*LOG_BOUND, "Complex saving failed")
    return dict(h=h, m=m, complex_s=str(sc), E=str(E), B=str(B),
                C0=str(128*m*B*B), C1=2, beta=str(beta),
                one_piece_depth_exponent=str(depth),
                depth_with_piece_count_exponent=str(depth+Q(1, 2)),
                s_below_m_fifth=True)


def sufficient_role_budget(a):
    h = 50
    v, m = comb(h, 3), h**3
    budget = Q(v-6*h*h, 2*m*a*LOG_BOUND)-v-h
    return (budget.numerator-1)//budget.denominator


def design_target():
    a = Q(417, 10**11)
    p = parameters(a=a, beta=Q(999998, 10**6), epsilon=Q(1999999, 10**7),
                   delta=Q(1, 10**8), kappa=Q(1, 2**58))
    return dict(status="UNACHIEVED DESIGN TARGET; no qualifying circuit supplied",
                bit_saving=str(a), maximum_side_roles=sufficient_role_budget(a),
                witness=evaluate(p),
                scope="Requires the same circuit/frame interface with the stated role budget.")


def certificate(upstream=False):
    p = parameters()
    witness = evaluate(p)
    old = evaluate(parameters(beta=Q(999, 1000), epsilon=Q(199, 1000),
                              delta=Q(1, 10000), kappa=Q(1, 2**59)))
    old_margin = Q(old["minimum_margin"])
    qlo, qhi = capacity_enclosure()
    glo, ghi = supremum_enclosure()
    require(KAPPA > old_margin, "No improvement over old supported margin")
    require(KAPPA/ghi > Q(99999996, 10**8), "Witness too far below supremum")
    require(ghi < Q(1, 2**58), "Unexpected crossing of next dyadic target")
    gamma_exp = Q(1, 2)+Q(3, 2)*p.epsilon
    require(gamma_exp < Q(4, 5) and 184 < 2**8 and 8**2*32 < 46**2,
            "Gaussian b>=2^40 cutoff failed")
    guard = guard_checks(p.beta)
    result = dict(status="CONDITIONAL PARAMETER-ONLY REFINEMENT",
                  author="Aurel Prosz (Paureel)", base_repository="CrocSwap/integer-mult-bounds",
                  base_commit=BASE_COMMIT, bit_saving=str(A), complex_saving=str(S),
                  log_m_upper=str(LOG_BOUND), witness=witness,
                  comparison=dict(previous_headline=str(Q(1, 2**59)),
                      previous_minimum_margin=str(old_margin),
                      relative_gain_over_headline=str(KAPPA*2**59-1),
                      relative_gain_over_previous_margin=str(KAPPA/old_margin-1)),
                  fixed_exponent_supremum=dict(capacity_interval=[str(qlo), str(qhi)],
                      margin_interval=[str(glo), str(ghi)], bisections=160,
                      polynomial="a*z^2-(s+a^2)*z+a^2*s", formula="z/(5+4*z)",
                      kappa_fraction_lower_bound=str(KAPPA/ghi),
                      scope="Fixed declared a,s,C1 and revised parameter inequalities only."),
                  stopped_guard=guard,
                  gaussian=dict(gamma_exponent=str(gamma_exp),
                      gamma_cutoff="b>=2^40 implies gamma<b/4, using 184<2^8",
                      gaussian_margin=witness["margins"]["g5"]),
                  design_target=design_target(),
                  integration=dict(paired_circuit_rechecked=False,
                      sufficient_side_role_budget=sufficient_role_budget(A),
                      scope="Standalone arithmetic only; paired circuit/frame interface assumed."),
                  scope="Inherits paired circuit/frame transfer, nonadjacent routing, stopped-depth guard, tight Gaussian setup, and upstream multiplication interfaces. No priority or practical speedup claim.")
    if upstream:
        import paired_network
        from certify import Parameters as UpstreamParameters, certify_parameters
        require(paired_network.H == 50 and paired_network.BIT_SAVING == A
                and paired_network.COMPLEX_SAVING == S, "Declared motif exponents changed")
        base = paired_network.certificate()
        checked = certify_parameters(UpstreamParameters(**vars(p)), generalized_beta=True,
                    strict_margin=True, layout_model="nonadjacent", guard_model="stopping",
                    assembly_model="tight-gaussian")
        for key in ("parameters", "constraint_slacks", "margins", "minimum_margin",
                    "absorption_gap", "limiting_margins"):
            require(checked[key] == witness[key], f"Upstream verifier disagrees: {key}")
        require(paired_network.guard_certificate(beta=p.beta) == guard | {
                    "scope": "Exact constants for the written stopped-depth proof; coefficient depth uses the unchanged h=50 complex motif, not the new bit motif."},
                "Upstream guard checker disagrees")
        roles = int(base["bit_counts"]["side_roles_per_invocation"])
        require(roles <= sufficient_role_budget(A), "Paired circuit exceeds sufficient budget")
        result["integration"] = dict(paired_circuit_rechecked=True,
            sufficient_side_role_budget=sufficient_role_budget(A), actual_side_roles=roles,
            upstream_commit=base["upstream_commit"], verifier_models=dict(
                layout="nonadjacent", guard="stopping", assembly="tight-gaussian"),
            all_parameter_slacks_and_margins_match=True,
            scope="Paired coefficients, frames, source hashes, guard and parameter agreement checked; full multiplication theorem still assumed.")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", action="store_true", help="Recheck complete paired construction")
    parser.add_argument("--output", type=Path, default=ROOT/"certificates/paired-tuned-parameters.json")
    args = parser.parse_args()
    result = certificate(upstream=args.upstream)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print("PASS conditional paired tuning; minimum", result["witness"]["minimum_margin"])
    print("Paired circuit rechecked:", result["integration"]["paired_circuit_rechecked"])
