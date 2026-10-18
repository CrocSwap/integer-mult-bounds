#!/usr/bin/env python3
"""Exact identities and a scoped outer-arithmetic extension; no supplier claim."""
from __future__ import annotations

import ast
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import subprocess

BASE = "997e6a9ca7b4f95d50e366f61412fd640d72a88a"
ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
ENGINE = "research/adaptive-kernel-demotion/vendor/engines/outer.py"
ENGINE_SHA = "c1ebb52163a7219504c728a5c2b098bf1e50bf20148a2879c5a74c3cadc7c03c"


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def blob(path):
    return subprocess.check_output(["git", "show", BASE + ":" + path], cwd=ROOT)


def walsh(values):
    out = list(values)
    width = 1
    while width < len(out):
        for start in range(0, len(out), 2 * width):
            for j in range(width):
                u, v = out[start+j], out[start+j+width]
                out[start+j], out[start+j+width] = u+v, u-v
        width *= 2
    return out


def parity(x):
    return x.bit_count() & 1


def operator_checks():
    # Each checked entry is the exact character sum in the written proof.
    character_entries = 0
    for f in range(1, 6):
        n = 1 << f
        for y in range(n):
            for z in range(n):
                basis = [int(t == z) for t in range(n)]
                stage = walsh(basis)
                stage = [v * (-1 if parity(t & y) else 1)
                         for t, v in enumerate(stage)]
                result = walsh(stage)
                require(result == [n*int(x == (z ^ y)) for x in range(n)],
                        "Walsh shear operator entry")
                character_entries += n

    # Literal Gaussian dyadic one-qubit C and S, with pairs (real, imag).
    def add(x, y): return (x[0]+y[0], x[1]+y[1])
    def mul(x, y): return (x[0]*y[0]-x[1]*y[1], x[0]*y[1]+x[1]*y[0])
    def mm(A, B):
        return [[add(mul(A[i][0], B[0][j]), mul(A[i][1], B[1][j]))
                 for j in range(2)] for i in range(2)]
    zero, one, unit_i = (Q(0), Q(0)), (Q(1), Q(0)), (Q(0), Q(1))
    plus, minus = (Q(1,2), Q(1,2)), (Q(1,2), Q(-1,2))
    C = [[plus, minus], [minus, plus]]
    S = [[one, zero], [zero, unit_i]]
    J = mm(mm(S, C), S)
    require(J == [[plus, plus], [plus, (-plus[0], -plus[1])]], "S C S")
    require(mm(J, J) == [[unit_i, zero], [zero, unit_i]], "J squared")

    swap_columns = 0
    for f in range(1, 5):
        n, dim = 1 << f, 1 << (2*f)
        for j in range(dim):
            v = [Q(int(k == j)) for k in range(dim)]
            # H_2f D, rightmost factor first, repeated three times.
            for _ in range(3):
                v = [value * (-1 if parity((k // n) & (k % n)) else 1)
                     for k, value in enumerate(v)]
                v = [value / n for value in walsh(v)]
            target = (j % n)*n + j // n
            require(v == [int(k == target) for k in range(dim)],
                    "three full Walsh transforms implement SWAP")
            swap_columns += 1

    # Same-target fusion holds for arbitrary independent control values.
    fused_cases = 0
    for f in range(1, 5):
        for x in range(1 << f):
            for y in range(1 << f):
                for z in range(1 << f):
                    require((x ^ y) ^ z == x ^ (y ^ z), "same-target fusion")
                    require(parity(x & y) ^ parity(x & z) == parity(x & (y ^ z)),
                            "bilinear diagonal multiplication")
                    fused_cases += 1
    # Changing-target CNOTs need not commute: (0,1) is a witness.
    xy = (0, 1)
    first_xy = (xy[0] ^ xy[1], xy[1])
    first_xy = (first_xy[0], first_xy[1] ^ first_xy[0])
    first_yx = (xy[0], xy[1] ^ xy[0])
    first_yx = (first_yx[0] ^ first_yx[1], first_yx[1])
    require(first_xy != first_yx, "changing-target control")
    return dict(character_entries=character_entries, swap_basis_columns=swap_columns,
                same_target_fusion_cases=fused_cases,
                gaussian_native_conversion=True, changing_target_control=True,
                all_f_proof="Character orthogonality and tensoring of exact one-pair identity")


def independent_outer(a, b, beta, eta, kappa):
    tau, sigma = 1-a, 1-b
    q = a*(1-2*eta)
    eps, c = (1-eta)/(1+q), q+eta/4
    G = eps*q
    r, delta = G+eta/2, eta/8
    lam, lp = 1-a+a*eta, 1-q
    internal, leaf = tau+(1-beta)*max(sigma-tau, Q(0)), sigma+beta*(1-sigma)
    margins = dict(balanced_prefix=G+eta, coordinate_movement=a,
                   compact_phase_layer=G, bulk_exposure=a,
                   Gaussian_arithmetic=G+3*eta/8,
                   scalar_work=G+7*eta/8, dimension=eps)
    slacks = dict(bit_positive=a, complex_above_bit=b-a,
        complex_below_one_over32=Q(1,32)-b, beta_positive=beta,
        beta_below_one=1-beta, leaf_saving_above_bit=(1-beta)*b-a,
        q_positive=q, q_below_internal=1-internal-q, q_below_leaf=1-leaf-q,
        c_positive=c, c_below_one=1-c, q_below_reservations=c-q,
        lambda_above_tau=lam-tau, lambda_above_sigma=lam-sigma,
        lambda_above_internal=lam-internal, lambda_prime_above_lambda=lp-lam,
        compact_leaf=lp-leaf, compact_reservations=lp-(1-c),
        lambda_prime_below_one=q, epsilon_positive=eps, epsilon_below_one=1-eps,
        guard_width=1-eps, K_geometry=1-eps*(1+c), K_dominates_log=eps*c,
        record_suffix=1-eps, phase_local=1-eps-delta, phase_boundary=r-delta,
        gamma_sublinear=1-eps-r, cell_above_band=eps-(1-r)/2,
        prime_interval_packing=1-eps, alpha_positive=r, alpha_below_one=1-r,
        alpha_below_one_fourth=Q(1,4)-r, delta_positive=delta,
        delta_below_one_eighth=Q(1,8)-delta, short_record_fallback=eps-a,
        small_field_exposure=1-eps-G, artificial_boundary=8-eps+r-delta-G,
        literal_scalar_guard=Q(1), row_product_gap=Q(1))
    slacks.update({key+"_above_kappa": value-kappa for key,value in margins.items()})
    return dict(slacks=slacks, margins=margins,
                parameters=dict(a=a,b=b,beta=beta,eta=eta,kappa=kappa,q=q,
                                epsilon=eps,c=c,r=r,delta=delta,G=G),
                gap=G-kappa)


def outer_checks(source):
    a, b, beta, eta, kappa = Q(14,125), Q(9,80), Q(1,1000), Q(1,100000), Q(1,10)
    eta_bounds = [Q(1,8), (9*a-1)/(28*a), (1-3*a)/(2*(1+a))]
    require(Q(1,9)<a<Q(1,3) and a<b<1 and 0<beta<1-a/b, "region")
    require(all(0<eta<bound for bound in eta_bounds), "eta region")
    expected = independent_outer(a,b,beta,eta,kappa)
    require(expected["gap"] == Q(83006669,115833100000), "exact target margin")
    require(len(expected["slacks"]) == 47, "complete list")
    failed = {k:v for k,v in expected["slacks"].items() if v<=0}
    require(failed == {"complex_below_one_over32":Q(1,32)-b}, "only domain guard fails")

    # Positive values are diagnostic premises, not a fabricated finite bridge.
    assumed_bridge = dict(semantic=dict(strict_literal_gap=Q(1), C0=1),
                          rows=dict(degree_gap=Q(1)))
    original = {}
    exec(compile(source, ENGINE, "exec", optimize=0), original)
    rejected = False
    try:
        original["assembly"](a,b,assumed_bridge,kappa,eta,beta)
    except AssertionError:
        rejected = True
    require(rejected, "unchanged production engine must reject expanded domain")

    # Observe the unchanged equations by replacing only their rejection with
    # a recording callback in an in-memory diagnostic; no file is patched.
    tree = ast.parse(source)
    recorded = []
    replaced = 0
    class Observer(ast.NodeTransformer):
        def visit_Assert(self, node):
            nonlocal replaced
            if (isinstance(node.test, ast.Call) and
                isinstance(node.test.func, ast.Name) and node.test.func.id == "all"):
                replaced += 1
                return ast.copy_location(ast.Expr(ast.Call(
                    func=ast.Name(id="record_slacks",ctx=ast.Load()),
                    args=[ast.Name(id="slacks",ctx=ast.Load())],keywords=[])), node)
            return node
    tree = Observer().visit(tree)
    ast.fix_missing_locations(tree)
    require(replaced == 1, "exactly one diagnostic rejection replaced")
    observed = {"record_slacks":lambda s:recorded.append(dict(s))}
    exec(compile(tree, ENGINE+":diagnostic-only", "exec", optimize=0), observed)
    result = observed["assembly"](a,b,assumed_bridge,kappa,eta,beta)
    require(recorded == [expected["slacks"]], "independent 47-slack equality")
    require(result["margins"] == expected["margins"], "independent margin equality")

    # These finite controls do not replace the all-parameter proof in README.
    controls = dict(endpoint_a_has_no_strict_target_margin=
                    independent_outer(Q(1,9),b,beta,eta,kappa)["gap"]<0,
                    target_above_G_rejected=expected["gap"]-Q(1,100)<0,
                    zero_eta_loses_strict_slack=
                    independent_outer(a,b,beta,Q(0),kappa)["slacks"]["gamma_sublinear"]==0,
                    leaf_ordering_is_required=
                    independent_outer(a,b,Q(1,10),eta,kappa)["slacks"]["leaf_saving_above_bit"]<0)
    require(all(controls.values()), "negative controls")
    return dict(**expected, eta_upper_bounds=eta_bounds, original_engine_rejects=True,
                only_failed_original_constraint=failed, controls=controls,
                bridge_status="Positive scalar and row slacks assumed; no bridge validated",
                theorem_scope="Displayed arithmetic only; no supplier or analytic domain extension")


def jsonable(value):
    if isinstance(value, Q): return str(value)
    if isinstance(value, dict): return {k:jsonable(v) for k,v in value.items()}
    if isinstance(value, (list,tuple)): return [jsonable(v) for v in value]
    return value


def main():
    paths = [ENGINE, "upstream/build/sections/05-layers.tex",
             "notes/general-clifford-frames.tex", "docs/research/assembly-domain-audit.md"]
    sources = {path:blob(path) for path in paths}
    hashes = {path:hashlib.sha256(data).hexdigest() for path,data in sources.items()}
    require(hashes[ENGINE] == ENGINE_SHA, "selected outer engine source hash")
    result = dict(status="LOCAL EXACT IDENTITIES AND ARITHMETIC; NO KAPPA CLAIM",
                  source_commit=BASE, source_sha256=hashes,
                  operators=operator_checks(), outer=outer_checks(sources[ENGINE]))
    (OUT/"RESULT.json").write_text(json.dumps(jsonable(result),indent=2)+"\n")
    print("PASS exact Walsh/shear, fused swap, and 46 relaxed-domain outer slacks")
    print("Unchanged production engine rejects the hypothetical inputs at b<1/32.")
    print("No finite supplier, paid bridge, or analytic extension has been verified.")


if __name__ == "__main__":
    main()
