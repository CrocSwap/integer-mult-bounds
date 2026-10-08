#!/usr/bin/env python3
"""Exact checks for a weighted Neumann estimate and conditional assembly.

No floating point is used for acceptance.  These checks support the written
proof; they do not certify the upstream multiplication theorem or the
transcendental Gaussian identity.  The upstream checkout is read-only.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
import json
from math import comb, isqrt
from pathlib import Path
import subprocess
import time


UPSTREAM_COMMIT = "bcd4ebde8692383539f8a48734e5fbf3a18a32c2"
CAMPAIGN_START = "2026-10-07T22:25:21Z"
CAMPAIGN_DEADLINE = "2026-10-08T08:25:21Z"
BASELINE_KAPPA = Q(1, 2**59)
BASELINE_MARGIN = Q(272158569, 156250000000000000000000000)
LOG_M_UPPER = Q(11737, 1000)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def ceil_q(value: Q) -> int:
    return -(-value.numerator // value.denominator)


def nearest_numerator(index: int, s: int, t: int) -> tuple[int, int]:
    """Return q_j and the integer numerator of beta_j, including negative j."""
    q = (2 * t * index + s) // (2 * s)
    return q, t * index - s * q


def similarity_identity(s: int, t: int, j: int, step: int) -> dict:
    require(2 <= s < t and step != 0, "Invalid matrix transition")
    rho, theta = Q(t, s), Q(t - s, s)
    qj, bj = nearest_numerator(j, s, t)
    ql, bl = nearest_numerator(j + step, s, t)
    beta_j, beta_l = Q(bj, s), Q(bl, s)
    require(-Q(1, 2) <= beta_j < Q(1, 2), "Wrong rounding interval")
    require(-Q(1, 2) <= beta_l < Q(1, 2), "Wrong rounding interval")
    g = ql - qj - step
    phi = (rho * step + beta_j) ** 2 - beta_l**2
    potential_change = (beta_l**2 - beta_j**2) / theta
    residual = phi - potential_change
    exact = rho * (step**2 + g * (g + 2 * beta_l) / theta)
    require(residual == exact, "Weighted exponent identity failed")
    require(g * (g + 2 * beta_l) >= 0, "Integer-gap positivity failed")
    require(residual >= rho * step**2, "Gaussian weighted bound failed")
    _, periodic_b = nearest_numerator(j + step + s, s, t)
    require(periodic_b == bl, "Periodicity failed")
    return {"g": g, "residual": residual, "lower_bound": rho * step**2}


def check_similarity(max_s: int = 64, max_gap: int = 15, radius: int = 16) -> dict:
    count = 0
    gap_values: set[int] = set()
    minimum_slack = None
    alias_checks = 0
    boundary_rows = 0
    for s in range(2, max_s + 1):
        for t in range(s + 1, s + min(max_gap, s) + 1):
            steps = sorted(set(range(-radius, radius + 1)) | {s, -s, 2*s, -2*s})
            for j in range(s):
                _, bj = nearest_numerator(j, s, t)
                boundary_rows += abs(2 * bj) == s
                for step in steps:
                    if step == 0:
                        continue
                    result = similarity_identity(s, t, j, step)
                    count += 1
                    alias_checks += step % s == 0
                    gap_values.add(result["g"])
                    slack = result["residual"] - result["lower_bound"]
                    minimum_slack = slack if minimum_slack is None else min(minimum_slack, slack)
    # The elementary tail bound r < exp(-u) for u >= 4 uses only pi > 3
    # and exp(1) > 2: 2 exp(-2u) + exp(-3u) < 1.
    require(Q(2, 2**8) + Q(1, 2**12) < 1, "Exponential-tail comparison failed")
    return {
        "status": "PASS exact finite checks supporting the universal algebraic identity",
        "max_s": max_s, "max_t_minus_s": max_gap, "local_step_radius": radius,
        "transition_checks": count, "periodic_alias_checks": alias_checks,
        "tie_boundary_rows": boundary_rows,
        "integer_gap_min": min(gap_values), "integer_gap_max": max(gap_values),
        "minimum_exact_slack": str(minimum_slack),
        "scope": "Rational exponent identities and positivity; finite checks supplement the written all-size proof.",
    }


def alpha_width(b: int) -> int:
    n = 32 * b
    root = isqrt(isqrt(n))
    return root if root**4 == n else root + 1


def check_cutoff() -> dict:
    checks = []
    for b in [17, 32, 64, 256, 4096, 2**20, 2**40, 2**80]:
        alpha = alpha_width(b)
        u, p = alpha**2, 6*b
        # This maximum integer d covers every epsilon <= 1/4.
        d = isqrt(isqrt(b))
        require(alpha**4 >= 32*b, "Gaussian width below definition")
        require(u > 2*d and u*u - 4*d*u - p > 0, "Cutoff quadratic failed")
        require(u < p and u > 4*d, "Numerical resampling conditions failed")
        # theta > 1/(4d).  This computes a conservative upper cutoff,
        # valid even when the exact theta has much smaller numerator.
        k_upper = 4*d + ceil_q(Q(p, u))
        require(k_upper <= u < p, "New cutoff exceeds old numerical bounds")
        checks.append({"b": str(b), "p": str(p), "d_upper": str(d),
                       "alpha": str(alpha), "alpha_squared": str(u),
                       "new_cutoff_upper": str(k_upper)})
    require(184**4 < 2**40, "Retained gamma cutoff failed")
    return {"status": "PASS", "cases": checks, "retained_gamma_cutoff": "b>=2^40",
            "scope": "Exact sample cases plus universal inequalities in the written proof."}


def network_counts(h: int, side_roles: int) -> dict:
    v, m = comb(h, 3), h**3
    N = v**3
    W = 2*N + 2*v*v*(side_roles+h)
    L = 3*v*v*h*h
    D = N-2*L
    require(D > 0, "Nonpositive bit deficit")
    return {"h": h, "v": v, "m": m, "side_roles": side_roles,
            "N": N, "W": W, "L": L, "D": D, "s": W*m-D,
            "eta": Q(D, W*m)}


def log_ratio_bounds(x: Q, terms: int = 24) -> tuple[Q, Q]:
    require(1 <= x <= 2, "Invalid atanh logarithm domain")
    z = (x-1)/(x+1)
    lower = 2*sum((z**(2*j+1)/Q(2*j+1) for j in range(terms)),Q(0))
    tail = 2*z**(2*terms+1)/((2*terms+1)*(1-z*z))
    return lower,lower+tail


def log_integer_bounds(n: int) -> tuple[Q, Q]:
    power = n.bit_length()-1
    lo2,hi2 = log_ratio_bounds(Q(2))
    lo,hi = log_ratio_bounds(Q(n,2**power))
    return power*lo2+lo,power*hi2+hi


def assembly_witness(side_roles: int, bit_saving: Q, label: str,
                     epsilon: Q = Q(249, 1000), beta: Q = Q(999, 1000),
                     kappa: Q = Q(5, 2**61),
                     gaussian_model: str = "weighted-neumann") -> dict:
    require(gaussian_model in {"weighted-neumann","blocked-chirp"},
            "Unknown replacement Gaussian proof model")
    gaussian_limit = Q(1,4) if gaussian_model == "weighted-neumann" else Q(1,2)
    a, ac, delta = bit_saving, Q(1, 10**11), Q(1, 10000)
    tau, sigma = 1-a, 1-ac
    c = beta*a
    lam = 1-(1+beta)*a*a/2
    lamp = 1-beta*a*a
    counts = network_counts(50, side_roles)
    log_lower,log_upper = log_integer_bounds(counts["m"])
    require(log_upper < LOG_M_UPPER, "Logarithm enclosure failed")
    require(counts["eta"] > a*LOG_M_UPPER, "Insufficient finite bit saving")
    # Retained h50 complex counts, independently reconstructed.
    v, m, N = counts["v"], counts["m"], counts["N"]
    zc = comb(47, 3)+3*47
    Wc = 2*N+3*v*v*(v*zc+51)
    Lc = 3*v*v*51*50
    sc = Wc*m-2*N+2*Lc
    eta_c = Q(Wc*m-sc, Wc*m)
    require(eta_c > ac*LOG_M_UPPER, "Insufficient retained complex saving")
    require(2*Lc < N, "Complex spare-coordinate construction does not apply")
    require(2 <= sc < m**5, "Stopped guard proof does not apply")
    slacks = {
        "bit_exponent": counts["eta"]-a*LOG_M_UPPER,
        "complex_exponent": eta_c-ac*LOG_M_UPPER,
        "lambda_above_tau": lam-tau,
        "lambda_above_sigma": lam-sigma,
        "packed_recurrence": lam-tau*(1+c/beta),
        "lambda_prime_above_lambda": lamp-lam,
        "leaf_cost": lamp-(sigma+beta*(1-sigma)),
        "guard": 1-2*epsilon,
        "replacement_gaussian_cost": gaussian_limit-delta-epsilon,
        "gamma_sublinear": Q(1,2)-epsilon,
        "prime_interval_growth": 1-2*epsilon,
        "prefix_cost": 1-epsilon*(1+c),
        "scalar_cost": 1-delta-epsilon,
        "K_smaller_than_ell": 1-epsilon-epsilon*c,
    }
    require(Q(9,10) <= beta < 1, "Stopped guard beta range failed")
    require(0 < epsilon < gaussian_limit, "Dimension violates replacement Gaussian range")
    require(0 < delta < Q(1,8), "Scalar evaluation delta range failed")
    for name, value in slacks.items():
        require(value > 0, f"Nonpositive assembly slack {name}: {value}")
    margins = {
        "g1": 1-epsilon*(1+c), "g2": epsilon*c*a,
        "g3": epsilon*(1-lamp), "g4": a*(1-epsilon),
        "g5": gaussian_limit-delta-epsilon, "g6": 1-delta-epsilon,
        "g7": epsilon,
    }
    G = min(margins.values())
    require(G > kappa > BASELINE_KAPPA, "No strict improved certificate")
    return {
        "label": label,
        "gaussian_model": gaussian_model,
        "status": "CONDITIONAL assembly witness under the new written weighted Gaussian proof and retained upstream interfaces",
        "finite_construction_status": "Upstream certificate" if side_roles == 509194 else "Requires separate campaign circuit/frame certificate",
        "counts": {name: str(value) for name, value in counts.items()},
        "complex_counts": {"W": str(Wc), "s": str(sc), "eta": str(eta_c)},
        "log_m_enclosure": [str(log_lower),str(log_upper)],
        "parameters": {"a_bit": str(a), "a_complex": str(ac), "tau": str(tau),
                       "sigma": str(sigma), "beta": str(beta), "epsilon": str(epsilon),
                       "delta": str(delta), "C1": 2, "c": str(c), "lambda": str(lam),
                       "lambda_prime": str(lamp), "kappa": str(kappa)},
        "constraint_slacks": {name: str(value) for name,value in slacks.items()},
        "margins": {name: str(value) for name,value in margins.items()},
        "minimum_margin": str(G), "absorption_gap": str(G-kappa),
        "kappa_ratio_to_advertised_baseline": str(kappa/BASELINE_KAPPA),
        "margin_ratio_to_actual_baseline_margin": str(G/BASELINE_MARGIN),
        "mechanism": "Changed Neumann power estimate and Gaussian width" +
                     (" plus local blocked Gaussian convolution" if gaussian_model == "blocked-chirp" else "") +
                     f"; epsilon increases from199/1000 to{epsilon}.",
        "proof_obligations": ["Weighted similarity lemma and Neumann tail", "Revalidated ordered Gaussian numerical algorithms",
                              "Retained finite network/frame/rank transfer", "Retained fixed-tape upstream multiplication interfaces"],
    }


def check_sources(upstream: Path) -> dict:
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=upstream, text=True).strip()
    require(commit == UPSTREAM_COMMIT, "Unexpected upstream revision")
    subprocess.run(["git","diff","--quiet","HEAD","--"],cwd=upstream,check=True)
    files = ["notes/paired-note.tex", "notes/stopped-guard.tex",
             "upstream/build/sections/07-resampling.tex", "upstream/build/sections/08-assembly.tex",
             "scripts/certify.py", "scripts/paired_network.py"]
    return {"commit": commit, "files": {p: hashlib.sha256((upstream/p).read_bytes()).hexdigest() for p in files}}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-s", type=int, default=64)
    args = parser.parse_args()
    started = time.monotonic()
    provenance = check_sources(args.upstream)
    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "campaign_start": CAMPAIGN_START, "campaign_deadline": CAMPAIGN_DEADLINE,
        "provenance": provenance,
        "similarity": check_similarity(args.max_s), "cutoff": check_cutoff(),
        "witnesses": [assembly_witness(509194,Q(296,10**11),"weighted Gaussian with unchanged upstream paired graph"),
                      assembly_witness(494250,Q(305,10**11),"weighted Gaussian plus aligned global pair ordering",kappa=Q(133,100)*BASELINE_KAPPA)],
        "elapsed_seconds": None,
    }
    result["elapsed_seconds"] = time.monotonic()-started
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print(f"PASS {result['similarity']['transition_checks']} exact similarity transitions")
    for witness in result["witnesses"]:
        print(witness["label"])
        print("kappa", witness["parameters"]["kappa"], "margin", witness["minimum_margin"])


if __name__ == "__main__":
    main()
