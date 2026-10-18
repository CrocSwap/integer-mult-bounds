#!/usr/bin/env python3
"""Exact, scoped audit of the pinned balanced assembly; no new multiplier.

BigCactusLabs, with substantial OpenAI Codex assistance.
Apache-2.0. See README.md for the proof, assumptions and predecessor credit.
"""
import argparse
import ast
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = "research/coordinated-frames-and-entrance-banks/arithmetic/balanced_shared.py"
SOURCE_SHA256 = "c3204e1758057f5ef10724014f38b91b8a01f6d8a3562b054263fc74795bfd90"
CAP = "b_below_one_over32"
GAUSSIAN = "alpha_below_one_fourth"
SEED = 60


def check(condition, message):
    if not condition:
        raise ValueError(message)


def pinned_source(raw):
    check(sha256(raw).hexdigest() == SOURCE_SHA256, "Pinned assembly source changed")
    tree = ast.parse(raw, filename=SOURCE)
    definitions = [node for node in tree.body
                   if isinstance(node, ast.FunctionDef) and node.name == "assembly"]
    check(len(definitions) == 1, "Expected one pinned assembly function")
    # Execute the original function body, with explicitly hypothetical bridge
    # data and an observing requirement callback. Never import the package or
    # modify its verifier. Only the normal (all negative switches off) formula
    # is studied. This observation is NOT production acceptance.
    return compile(ast.Module(body=definitions, type_ignores=[]), SOURCE, "exec")


def evaluate(code, a, t, kappa, *, b=None, beta=None, scalar_gap=Q(1), row_gap=Q(1)):
    b = (a + 1) / 2 if b is None else b
    beta = (b - a) / (2 * b) if beta is None else beta
    failures = []

    def observe(ok, message):
        if not ok:
            failures.append(message)

    namespace = dict(Q=Q, rational=Q, require=observe,
                     validate_shared_bridge=lambda bridge, row: bridge)
    exec(code, namespace)
    bridge = dict(bit_uniform=dict(ordinary_saving=a),
                  semantic=dict(C0=1, strict_literal_gap=scalar_gap),
                  rows=dict(degree_gap=row_gap))
    result = namespace["assembly"](bridge, {}, a, kappa, beta=beta,
                                   h=(1-t)/2, a_complex=b)
    slacks = result["constraints"]
    failed = {name: str(value) for name, value in slacks.items() if value <= 0}
    # Keep failures outside the displayed dictionary (notably h and kappa's
    # domain) separate. They must not be lost by inspecting the 47 rows alone.
    extra = [message for message in failures if message != str(failed)]
    return result, failed, extra


def factored_slacks(a, t, kappa, b, beta):
    """Independent t-coordinate evaluation of every displayed slack.

    The a < b branch and positive abstract bridge gaps are explicit. These
    factorizations credit PR294; t = 1-2h and the Gaussian factor are this audit.
    """
    check(a < b and 0 < t < 1, "Outside the factorization domain")
    h = (1-t)/2
    q = a*t
    eps = (1+t)/(2*(1+a*t))
    G = eps*q
    r = G+h/2
    c = q+h/4
    L = (1-beta)*b-a
    values = dict(
        a_positive=a, a_below_b=b-a, b_below_one_over32=Q(1,32)-b,
        beta_positive=beta, beta_below_one=1-beta, phase_leaf_above_bit=L,
        q_positive=q, q_below_internal=2*a*h, q_below_leaf=L+2*a*h,
        c_positive=c, c_below_one=1-c, q_below_reservations=h/4,
        lambda_above_tau=a*h, lambda_above_sigma=b-a+a*h,
        lambda_above_internal=a*h, lambda_prime_above_lambda=a*h,
        compact_leaf=L+2*a*h, compact_reservations=h/4,
        lambda_prime_below_one=q, epsilon_positive=eps,
        epsilon_below_one=G+h, guard_width=G+h,
        K_geometry=h*(1-eps/4), K_dominates_log=eps*c,
        record_suffix=G+h, phase_local=G+7*h/8, phase_boundary=G+3*h/8,
        gamma_sublinear=h/2, cell_above_band=eps-(1-r)/2,
        prime_interval_packing=G+h, alpha_positive=r, alpha_below_one=1-r,
        alpha_below_one_fourth=t*(1-a*(2+t))/(4*(1+a*t)),
        delta_positive=h/8, delta_below_one_eighth=(1-h)/8,
        short_record_fallback=eps-a, small_field_exposure=h,
        artificial_boundary=8-eps+3*h/8, literal_scalar_guard=Q(1),
        row_product_gap=Q(1))
    margins = (G+h, a, G, a, G+3*h/8, G+7*h/8, eps)
    values.update({"g%d_above_kappa" % i: margin-kappa
                   for i, margin in enumerate(margins, 1)})
    return values


def gain(a, t):
    return a*t*(1+t)/(2*(1+a*t))


def envelope(a):
    check(0 < a < Q(1,2), "Positive arithmetic saving requires 0 < a < 1/2")
    return a/(1+a) if a <= Q(1,3) else (1-2*a)/(4*a)


def construct(a, kappa):
    M = envelope(a)
    check(0 < kappa < M, "Target must lie strictly below the fixed-a envelope")
    T = min(Q(1), 1/a-2)
    # The proof shows 0 < G(T)-G(t) < T-t, so this explicit rational choice
    # attains every strict target. No optimizer or stopping tolerance is used.
    t = T-(M-kappa)/2
    check(0 < t < T <= 1 and gain(a,t) > kappa, "Construction failed")
    loss = a*(T-t)*(1+T+t+a*T*t)/(2*(1+a*T)*(1+a*t))
    check(M-gain(a,t) == loss and 0 < loss < T-t,
          "Monotonicity/loss identity failed")
    return t


def noncap_failures(failed):
    return {name: value for name, value in failed.items() if name != CAP}


def audit(code):
    a_values = sorted({Q(i,d) for d in (SEED-1, SEED, SEED+1) for i in range(1,d)})
    t_values = sorted({Q(i,d) for d in range(2,13) for i in range(1,d)})
    feasible = infeasible = 0
    transcript = sha256()
    for a in a_values:
        b = (a+1)/2
        beta = (b-a)/(2*b)
        for t in t_values:
            kappa = gain(a,t)/2
            result, failed, extra = evaluate(code, a, t, kappa, b=b, beta=beta)
            expected = factored_slacks(a,t,kappa,b,beta)
            check(len(expected) == 47 and result["constraints"] == expected,
                  "Source/factorization discrepancy at a=%s t=%s" % (a,t))
            check(not extra, "Unexpected non-slack failure")
            observed = not noncap_failures(failed)
            check(observed == (a*(2+t) < 1), "Gaussian region equivalence failed")
            feasible += observed
            infeasible += not observed
            transcript.update(json.dumps([str(a), str(t),
                {k: str(v) for k,v in sorted(expected.items())}],
                separators=(",", ":")).encode()+b"\n")

    # Exercise both branches and strict rational limits without floating point.
    edges = (Q(1,100), Q(1,32), Q(1,3), Q(2,5), Q(49,100))
    close = [Q(1,3)-Q(1,10**j) for j in (2,SEED)]
    close += [Q(1,3)+Q(1,10**j) for j in (2,SEED)]
    close += [Q(1,2)-Q(1,10**j) for j in (2,SEED)]
    construction_values = sorted(set([a for a in a_values if a < Q(1,2)] + list(edges) + close))
    witnesses = 0
    for a in construction_values:
        M = envelope(a)
        for ratio in (Q(1,SEED), Q(1,2), 1-Q(1,10**SEED)):
            kappa = ratio*M
            t = construct(a,kappa)
            result, failed, extra = evaluate(code,a,t,kappa)
            check(not noncap_failures(failed) and not extra,
                  "Constructed witness fails a retained condition")
            check(result["minimum_margin"] == gain(a,t), "Wrong controlling margin")
            # In the original domain there also exists a b satisfying the cap.
            if a < Q(1,32):
                _, strict_failed, strict_extra = evaluate(code,a,t,kappa,b=(a+Q(1,32))/2)
                check(not strict_failed and not strict_extra, "Retained-cap control failed")
            witnesses += 1

    controls = {}
    def rejected(name, a, t, kappa, expected, **kwargs):
        _, failed, extra = evaluate(code,a,t,kappa,**kwargs)
        check(expected in failed, "Negative control not rejected: "+name)
        controls[name] = dict(failed_slacks=sorted(failed), extra_requirements=extra)

    a, t = Q(2,5), Q(1,2)
    rejected("gaussian_equality",a,t,gain(a,t)/2,GAUSSIAN)
    rejected("gaussian_exceeded",a,Q(3,4),gain(a,Q(3,4))/2,GAUSSIAN)
    rejected("a_half",Q(1,2),t,gain(Q(1,2),t)/2,GAUSSIAN)
    rejected("target_equals_margin",Q(1,4),t,gain(Q(1,4),t),"g3_above_kappa")
    rejected("leaf_equality",Q(1,4),t,Q(1,100),"phase_leaf_above_bit",
             b=Q(1,2),beta=Q(1,2))
    rejected("zero_scalar_gap",Q(1,4),t,Q(1,100),"literal_scalar_guard",scalar_gap=Q(0))
    rejected("zero_row_gap",Q(1,4),t,Q(1,100),"row_product_gap",row_gap=Q(0))
    rejected("production_cap_equality",Q(1,64),t,Q(1,1000),CAP,b=Q(1,32))
    for name, a, t, kappa in (("zero_backoff",Q(1,4),Q(1),Q(1,100)),
                              ("zero_target",Q(1,4),Q(1,2),Q(0))):
        _, failed, extra = evaluate(code,a,t,kappa)
        check("positive backoff and saving required" in extra, "Lost scalar precondition")
        controls[name] = dict(failed_slacks=sorted(failed), extra_requirements=extra)

    # An audit that silently drops the Gaussian row would accept this exact
    # bad point. The other 45 retained displayed slacks are strictly positive.
    _, failed, extra = evaluate(code,Q(2,5),Q(3,4),Q(1,20))
    check(set(failed) == {CAP,GAUSSIAN} and not extra, "Omission control changed")
    controls["omit_gaussian_row"] = dict(would_pass_after_omission=True,
                                        detected_failure=GAUSSIAN)
    try:
        pinned_source((ROOT/SOURCE).read_bytes().replace(b"Q(1,4)-r",b"Q(1,3)-r"))
    except ValueError as error:
        controls["source_drift"] = str(error)
    else:
        raise ValueError("Changed Gaussian bound escaped source pin")

    examples = []
    for a in (Q(1,64),Q(1,3),Q(2,5),Q(49,100)):
        M = envelope(a)
        kappa = M*Q(59,60)
        t = construct(a,kappa)
        examples.append(dict(a=str(a),supremum=str(M),kappa=str(kappa),
                             t=str(t),h=str((1-t)/2),G=str(gain(a,t))))
    return dict(status="PASS_SCOPED_BALANCED_GAUSSIAN_ENVELOPE",assignment_seed=SEED,
                source_sha256={SOURCE:SOURCE_SHA256},
                scope="Rational inequalities with assumed bridge gaps; no new multiplication bound",
                grid=dict(a_denominators=[SEED-1,SEED,SEED+1],t_max_denominator=12,
                          distinct_a=len(a_values),distinct_t=len(t_values),
                          completed_cases=feasible+infeasible,feasible=feasible,infeasible=infeasible,
                          slacks_per_case=47,exact_slack_transcript_sha256=transcript.hexdigest()),
                construction=dict(completed_witnesses=witnesses,near_boundary_decimal_places=SEED),
                negative_controls=controls,examples=examples)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="Write a receipt instead of comparing EXPECTED.json")
    args = parser.parse_args()
    result = audit(pinned_source((ROOT/SOURCE).read_bytes()))
    if args.write:
        args.write.write_text(json.dumps(result,indent=2)+"\n")
    else:
        check(json.loads((HERE/"EXPECTED.json").read_text()) == result, "Receipt differs")
    print("%s cases=%d witnesses=%d controls=%d" % (
        result["status"], result["grid"]["completed_cases"],
        result["construction"]["completed_witnesses"],len(result["negative_controls"])))


if __name__ == "__main__":
    main()
