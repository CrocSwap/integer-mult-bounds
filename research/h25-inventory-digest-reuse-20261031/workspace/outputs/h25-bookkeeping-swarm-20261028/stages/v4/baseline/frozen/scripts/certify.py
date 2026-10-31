#!/usr/bin/env python3
"""Exact certificates for the numerical implications in manuscript #109.

These checks do not certify the upstream algorithm or its time bounds.
No floating-point arithmetic is used in a certificate.
"""
from dataclasses import dataclass
from fractions import Fraction as Q
import hashlib
import json
from math import comb, factorial
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def dyadic(k):
    return Q(1, 2**k)


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
    beta: Q = Q(1, 2)
    delta: Q = Q(1, 16)
    C1: int = 20


def proposed(k):
    """The user's family: k=50,42,36 gives kappa=2^-154,-130,-112."""
    return Parameters(1-dyadic(k), 1-dyadic(k), dyadic(k+1),
                      dyadic(k+1), 1-dyadic(2*k+1),
                      1-dyadic(2*k+2), dyadic(3*k+4))


def balanced(k):
    """Balance g2 and g3, gaining a factor two with the same epsilon and c."""
    a = dyadic(k)
    return Parameters(1-a, 1-a, a/2, a/2, 1-3*a*a/4,
                      1-a*a/2, a**3/8)


def near_supremum(k, relative_gap=Q(1, 100)):
    """Approach the strict-constraint supremum while retaining 2*kappa slack."""
    require(0 < relative_gap < 1, "Choose a positive gap smaller than one")
    a = dyadic(k)
    q = (1-relative_gap)*a*a/(2-a)
    c = q/a
    e = a/(1+a+q)
    lamp = 1-q
    lam = (lamp+(1-a)*(1+2*c))/2
    return Parameters(1-a, 1-a, e, c, lam, lamp, e*q/2)


BASELINE = Parameters(1-dyadic(50), 1-dyadic(50), dyadic(75),
                      dyadic(56), 1-dyadic(52), 1-dyadic(54), dyadic(182))

A = Q(9, 500000000000)
LOG_BOUND = Q(5743, 500)


def pushed(variant):
    """Strict-margin witnesses; variable beta uses the generalized layer proof."""
    a = A
    if variant == "109":
        return Parameters(1-a, 1-a, 3*a/4, a/2, 1-3*a*a/4,
                          1-a*a/2, dyadic(109))
    if variant == "108":
        return Parameters(1-a, 1-a, 3*a/4, 3*a/4, 1-7*a*a/8,
                          1-3*a*a/4, dyadic(108), beta=Q(3, 4))
    require(variant == "rational", "Unknown pushed variant")
    beta, e, c = Q(999, 1000), Q(999, 1000)*a, Q(998, 1000)*a
    lamp = 1-a*c
    lam = (lamp+(1-a)*(1+c/beta))/2
    return Parameters(1-a, 1-a, e, c, lam, lamp, Q(58, 10**34), beta=beta)


def layout_degree(layout_model):
    require(layout_model in ("adjacent", "nonadjacent"), "Unknown layout model")
    return 2 if layout_model == "adjacent" else 1


def constraints(p, *, layout_model="adjacent", assembly_model="original"):
    """Positive slacks, transcribed from the cited labelled source statements."""
    require(assembly_model in ("original", "tight-gaussian"), "Unknown assembly model")
    tight = assembly_model == "tight-gaussian"
    e, c, t, s, b = p.epsilon, p.c, p.tau, p.sigma, p.beta
    return {
        # prop:simultaneous-layer and its recurrence proof.
        "tau_positive": t,
        "tau_below_one": 1-t,
        "sigma_positive": s,
        "sigma_below_one": 1-s,
        "c_positive": c,
        "epsilon_positive": e,
        "beta_positive": b,
        "beta_below_one": 1-b,
        "lambda_above_tau": p.lam-t,
        "lambda_above_sigma": p.lam-s,
        "lambda_below_one": 1-p.lam,
        "packed_overhead": p.lam-t*(1+c/b),
        "lambda_prime_above_lambda": p.lamp-p.lam,
        "leaf_cost": p.lamp-(s+b*(1-s)),
        "lambda_prime_below_one": 1-p.lamp,
        "guard_width": 1-e*p.C1,
        # eq:fixed-parameters and setup proof in sec:assembly.
        "dimension_upper_bound": (Q(1, 3) if tight else Q(1, 12))-e,
        "crt_layout": 1-t-e*(layout_degree(layout_model)-t),
        "gaussian_cost": Q(1, 4)-p.delta-(Q(5, 4) if tight else Q(3, 2))*e,
        "prefix_cost": 1-e*(1+c),
        "scalar_cost": 1-p.delta-e,
        "delta_positive": p.delta,
        "delta_below_one_eighth": Q(1, 8)-p.delta,
        # Derived conditions used outside the final displayed system.
        "prime_interval_growth": 1-2*e,
        "alpha_below_sqrt_p": Q(1, 4)-(e/4 if tight else e/2),
        "gamma_sublinear": Q(1, 2)-(Q(3, 2) if tight else 2)*e,
        "K_smaller_than_ell": 1-e-e*c,
        "K_dominates_log_p": e*c,
        "r_superpolynomial": 1-e,
        "kappa_positive": p.kappa,
    }


def margins(p, *, layout_model="adjacent", assembly_model="original"):
    require(assembly_model in ("original", "tight-gaussian"), "Unknown assembly model")
    e, c, t = p.epsilon, p.c, p.tau
    return {
        "g1": 1-e*(1+c),
        "g2": e*c*(1-t),
        "g3": e*(1-p.lamp),
        "g4": 1-t-e*(layout_degree(layout_model)-t),
        "g5": Q(1, 4)-p.delta-(Q(5, 4) if assembly_model == "tight-gaussian" else Q(3, 2))*e,
        "g6": 1-p.delta-e,
        "g7": e,
    }


def certify_parameters(p, *, generalized_beta=False, strict_margin=False,
                       layout_model="adjacent", assembly_model="original",
                       guard_model="original"):
    require(generalized_beta or p.beta == Q(1, 2),
            "Upstream layer proof fixes beta=1/2; select the audited generalization")
    require(0 < p.beta < 1, "Beta must lie strictly between zero and one")
    require(guard_model in ("original", "stopping"), "Unknown guard model")
    if guard_model == "original":
        require(p.C1 >= 20, "C1 must cover the upstream guard bound")
    else:
        # Caller must also certify m>=3 and 2<=s_c<m^5 for its complex network.
        require(p.C1 >= 2 and p.beta >= Q(9, 10),
                "Stopping guard requires C1>=2 and beta>=9/10")
    slacks = constraints(p, layout_model=layout_model, assembly_model=assembly_model)
    for name, slack in slacks.items():
        require(slack > 0, f"Failed strict constraint: {name} ({slack})")
    gs = margins(p, layout_model=layout_model, assembly_model=assembly_model)
    if strict_margin:
        require(min(gs.values()) > p.kappa, "Need a positive absorption gap")
    else:
        require(min(gs.values()) >= 2*p.kappa,
                "The proposed patch requires every g_i >= 2*kappa")
    result = {"parameters": {k: str(v) for k, v in vars(p).items()},
            "constraint_slacks": {k: str(v) for k, v in slacks.items()},
            "margins": {k: str(v) for k, v in gs.items()},
            "minimum_margin": str(min(gs.values())),
            "limiting_margins": [k for k, v in gs.items() if v == min(gs.values())],
            "all_margins_at_least_twice_kappa": min(gs.values()) >= 2*p.kappa,
            "absorption_gap": str(min(gs.values())-p.kappa),
            "slack_rule": "strict" if strict_margin else "half",
            "generalized_beta": generalized_beta}
    if assembly_model != "original" or guard_model != "original":
        result.update(assembly_model=assembly_model, guard_model=guard_model)
    return result


def network(h):
    """Generalized counts only; these do not prove the network interface."""
    require(h > 6 and h != 9, "Need spare coordinates and nondegenerate rational form")
    v, m = comb(h, 3), h**3
    N, I = v**3, 3*v**2
    zb, zc = 3*comb(h-3, 2), comb(h-3, 3)+3*(h-3)
    Wb, Wc = 2*N+I*(v*zb+h), 2*N+I*(v*zc+h+1)
    Lb, Lc = I*h*h, I*(h+1)*h
    sb, sc = Wb*m-N+2*Lb, Wc*m-2*N+2*Lc
    eb, ec = Q(Wb*m-sb, Wb*m), Q(Wc*m-sc, Wc*m)
    E = 64*(Wc+m+1)**3
    B = sc+E
    nu = 1
    while m**nu < B:
        nu += 1
    return dict(h=h, v=v, m=m, N=N, I=I, zb=zb, zc=zc,
                Wb=Wb, Wc=Wc, Lb=Lb, Lc=Lc, sb=sb, sc=sc,
                eta_b=eb, eta_c=ec, B=B, nu=nu, C1=max(20, nu+3))


def certify_network(h, k, log_bound):
    n = network(h)
    # A positive Taylor partial sum below exp(log_bound) proves m<exp(log_bound).
    total = Q(0)
    terms = 0
    while total <= n["m"] and terms < 1000:
        total += Q(log_bound**terms, factorial(terms))
        terms += 1
    require(total > n["m"], "Could not certify the logarithm bound")
    for key in ("eta_b", "eta_c"):
        require(n[key] > log_bound*dyadic(k), f"Insufficient deficit: {key}")
    require(2*n["Lb"] < n["N"] and 2*n["Lc"] < n["N"],
            "The generalized residual lemma requires L<N/2 for both networks")
    require(n["C1"] == 20, "Changed network needs a revised guard exponent")
    return {"counts": {key: str(value) for key, value in n.items()},
            "exponent_deficit": str(dyadic(k)), "log_bound": log_bound,
            "exp_lower_bound": str(total), "exp_series_terms": terms,
            "scope": "Counts and exponent comparison; not a construction certificate"}


def verify_sources():
    manifest = json.loads((ROOT / "upstream/manifest.json").read_text())
    for local, info in manifest["files"].items():
        data = (ROOT / "upstream" / local).read_bytes()
        require(hashlib.sha256(data).hexdigest() == info["sha256"],
                f"Modified upstream source: {local}")
    return manifest["commit"]


def certify_rational_network():
    # Import here to avoid a module-level cycle with search_network.
    from search_network import log_integer_bounds
    n = network(46)
    lo, hi = log_integer_bounds(n["m"])
    require(hi < LOG_BOUND, "Log bound too small")
    require(all(n[key] > A*LOG_BOUND for key in ("eta_b", "eta_c")),
            "Rank deficit does not support the requested rational saving")
    certify_network(46, 36, 12)  # Residual and guard conditions.
    return {"h": 46, "saving": str(A), "log_bound": str(LOG_BOUND),
            "log_lower": str(lo), "log_upper": str(hi),
            "deficit_slacks": {k: str(n[k]-A*LOG_BOUND) for k in ("eta_b", "eta_c")}}


def certificates():
    return {
        "upstream_commit": verify_sources(),
        "scope": "Exact numerical certificates, conditional on the upstream proof interfaces",
        "cases": {name: certify_parameters(p) for name, p in {
            "baseline_182": BASELINE, "frozen_154": proposed(50),
            "same_network_130": proposed(42), "h46_112": proposed(36),
            "balanced_frozen_153": balanced(50),
            "balanced_same_network_129": balanced(42),
            "balanced_h46_111": balanced(36),
            "near_supremum_frozen": near_supremum(50),
            "near_supremum_same_network": near_supremum(42),
            "near_supremum_h46": near_supremum(36),
        }.items()} | {
            f"pushed_{v}": certify_parameters(pushed(v), generalized_beta=v != "109",
                                              strict_margin=True)
            for v in ("109", "108", "rational")
        },
        "networks": {
            "baseline_h100": certify_network(100, 50, 20),
            "improved_h100": certify_network(100, 42, 14),
            "improved_h46": certify_network(46, 36, 12),
            "rational_h46": certify_rational_network(),
        },
    }


if __name__ == "__main__":
    result = certificates()
    out = ROOT / "certificates/parameters.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    for name, case in result["cases"].items():
        print(f"PASS {name}: minimum {case['minimum_margin']} ({', '.join(case['limiting_margins'])})")
    print(f"Wrote {out.relative_to(ROOT)}")
