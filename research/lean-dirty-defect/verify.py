#!/usr/bin/env python3
"""Exact finite controls; --lean additionally runs the live kernel proof.

Prepared for ywz65 with OpenAI Codex assistance. Apache-2.0.
Python 3.12+, standard library; verification is read-only unless --write.
"""
import argparse
from functools import cache
from fractions import Fraction as Q
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

PACKAGE = Path(__file__).resolve().parent
REPO = PACKAGE.parents[1]
ROOTS = (
    "defect_decomposition", "commutator_bound", "delta_preserves",
    "product_lipschitz", "tree_recurrence", "budget_closed",
    "all_tree_error", "delta_lift", "execution_error",
    "budget_envelope", "envelope_closed_identity", "envelope_division",
    "comb_budget", "all_tree_envelope", "execution_envelope", "envelope_at_least_four",
    "nonlinear_example", "factor_two_needed", "lower_L_fails",
)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def authenticated_sources():
    manifest = json.loads((PACKAGE / "SOURCES.json").read_bytes())
    hashes = {}
    for item in manifest["files"]:
        if item["usage"] != "input":
            continue  # Historical provenance is checked by the registered runner.
        raw = (REPO / item["path"]).read_bytes()
        need(sha(raw) == item["sha256"], "source hash mismatch: " + item["path"])
        blob = hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()
        need(blob == item["git_blob"], "source blob mismatch: " + item["path"])
        hashes[item["path"]] = sha(raw)
    for item in manifest["external_sources"]:
        raw = (PACKAGE / item["vendored_path"]).read_bytes()
        need(sha(raw) == item["sha256"], "vendored source hash mismatch")
        blob = hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()
        need(blob == item["git_blob"], "vendored source blob mismatch")
        hashes[item["vendored_path"]] = sha(raw)
    return hashes


@cache
def shapes(n):
    if n == 1:
        return (None,)
    return tuple((a, b) for k in range(1, n) for a in shapes(k) for b in shapes(n-k))


def label(tree, offset=0):
    if tree is None:
        return offset, offset + 1
    a, offset = label(tree[0], offset)
    b, offset = label(tree[1], offset)
    return (a, b), offset


def leaf_count(t):
    return 1 if isinstance(t, int) else leaf_count(t[0]) + leaf_count(t[1])


def add(a, b):
    return tuple(x+y for x, y in zip(a, b))


def sub(a, b):
    return tuple(x-y for x, y in zip(a, b))


def matrix(j, x):
    return (x[0]+x[1], x[1]) if j % 2 == 0 else (x[0], x[0]+x[1])


def nonlinear(j, x):
    return add(matrix(j, x), tuple(Q(-1 if y <= 0 else 1) for y in x))


def delta(t, x, dirt, depth=0):
    if isinstance(t, int):
        return nonlinear(t, x)
    z = dirt[depth]
    b = delta(t[0], x, dirt, depth+1)
    return sub(delta(t[1], add(z, b), dirt, depth+1), delta(t[1], z, dirt, depth+1))


def product(t, x):
    return matrix(t, x) if isinstance(t, int) else product(t[1], product(t[0], x))


def budget(t, L=Q(2)):
    if isinstance(t, int):
        return Q(1)
    return L**leaf_count(t[1]) * budget(t[0], L) + 2*budget(t[1], L)


def finite_replay():
    cases = 0
    tree_count = 0
    profiles = ((Q(0), Q(0)), (Q(1, 2), Q(-3, 2)), (Q(10**12), Q(-10**12)))
    errors = []
    envelope_cases = 0
    envelope_checks = []
    for n in range(1, 8):
        maxima = {L: Q(0) for L in (Q(0), Q(1), Q(2), Q(7, 2), Q(4))}
        for shape in shapes(n):
            t, end = label(shape)
            need(end == n and leaf_count(t) == n, "tree labeling drift")
            tree_count += 1
            closed = n * Q(2)**(n-1)
            need(budget(t) <= closed, "all-tree numeric majorant failed")
            for L in maxima:
                value = budget(t, L)
                geometric = sum(L**(n-1-k)*2**k for k in range(n))
                need(value <= geometric, "geometric envelope failed")
                need(L == 2 or geometric == (L**n-2**n)/(L-2), "geometric formula failed")
                maxima[L] = max(maxima[L], value)
                envelope_cases += 1
            for z in profiles:
                dirt = tuple(add(z, (Q(k, 2), Q(-k, 2))) for k in range(n))
                x = (Q(3, 2), Q(-1, 2))
                error = max(map(abs, sub(delta(t, x, dirt), product(t, x))))
                need(error <= budget(t), "uniform defect recurrence failed")
                errors.append([n, str(error), str(budget(t))])
                cases += 1
        for L, maximum in maxima.items():
            geometric = sum(L**(n-1-k)*2**k for k in range(n))
            need(maximum == geometric, "claimed scalar recurrence maximum not attained")
            envelope_checks.append([n, str(L), str(maximum)])
    f = lambda k, x: k*x + (-1 if x <= 0 else 1)
    e2 = abs(f(2, f(2, 1)) - f(2, 0) - 4)
    e1 = abs(f(1, f(1, 1)) - f(1, 0) - 1)
    need(e2 == 4 and e2 > 2+1, "missing factor-two control ineffective")
    need(e1 == 3 and e1 > 2, "L=1 closed-bound control ineffective")
    quadratic = lambda z: (z+1)**2-z**2
    need(quadratic(10**6) > 10**6 * quadratic(0), "uniformity control ineffective")
    forward = matrix(1, matrix(0, (Q(1), Q(0))))
    reversed_order = matrix(0, matrix(1, (Q(1), Q(0))))
    need(forward != reversed_order, "factor-order control ineffective")
    return {
        "schema": 1, "trees": tree_count, "cases": cases,
        "finite_dimension": 2, "leaf_counts": [1, 7], "L": 2, "E0": 1,
        "errors_sha256": sha(canonical(errors).encode()),
        "envelope_cases": envelope_cases, "envelope_maxima": envelope_checks,
        "controls": {"factor_two_needed": e2, "L_one_fails": e1,
                     "local_only_defect": quadratic(10**6),
                     "order_forward": list(map(str, forward)),
                     "order_reversed": list(map(str, reversed_order))},
        "sources": authenticated_sources(),
        "formal_sources": {name: sha((PACKAGE / name).read_bytes())
                           for name in ("Bound.lean", "Examples.lean")},
        "scope": "Finite exact controls and source binding only; run --lean for the kernel proof.",
    }


def audit_axioms(output):
    expected = {"DirtyBound."+name for name in ROOTS}
    pattern = re.compile(r"^'([^']+)' (?:depends on axioms:\s*\[([^]]*)\]|does not depend on any axioms)\s*$", re.M)
    found = {}
    for match in pattern.finditer(output):
        name, body = match.groups()
        need(name in expected and name not in found, "unexpected/duplicate axiom root")
        axioms = [] if body is None else [part.strip() for part in body.split(',')]
        need(set(axioms) <= {"propext", "Quot.sound", "Classical.choice"},
             "unapproved kernel axiom: " + name + ": " + repr(axioms))
        found[name] = sorted(axioms)
    need(set(found) == expected, "missing kernel axiom roots")
    need(not pattern.sub('', output).strip(), "unexpected axiom audit output")
    return found


def live_lean(executable):
    lean = shutil.which(executable)
    need(lean, "Lean executable unavailable")
    version = subprocess.check_output([lean, "--version"], text=True, encoding="utf-8").strip()
    need("version 4.34.1" in version, "use tested Lean 4.34.1; got " + version)
    old = (REPO / "research/lean-nonlinear-commutator/NonlinearEcho.lean").read_bytes()
    formal = (PACKAGE / "Bound.lean").read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory(prefix="dirty-defect-") as scratch:
        directory = Path(scratch)
        env = os.environ.copy()
        env["LEAN_PATH"] = str(directory)

        def run(name, output=False):
            command = [lean, "-j1", "-DwarningAsError=true", name]
            if output:
                command += ["-o", name.replace('.lean', '.olean')]
            return subprocess.run(command, cwd=directory, env=env, text=True,
                                  encoding="utf-8", capture_output=True, timeout=120)

        (directory / "NonlinearEcho.lean").write_bytes(old)
        (directory / "Bound.lean").write_bytes(formal.encode())
        (directory / "Examples.lean").write_bytes((PACKAGE / "Examples.lean").read_bytes())
        for name in ("NonlinearEcho.lean", "Bound.lean", "Examples.lean"):
            result = run(name, True)
            need(result.returncode == 0, name + " failed:\n" + result.stdout + result.stderr)
        audit = "import Examples\n" + ''.join("#print axioms DirtyBound."+name+"\n" for name in ROOTS)
        (directory / "Audit.lean").write_bytes(audit.encode())
        result = run("Audit.lean")
        need(result.returncode == 0 and not result.stderr.strip(), "live axiom query failed")
        axioms = audit_axioms(result.stdout)
        mutations = (
            ("missing_second_defect", "(K * EB + 2 * EA)", "(K * EB + EA)"),
            ("weakened_L", "(hL : 2 ≤ L)", "(hL : 1 ≤ L)"),
            ("reversed_product", "compose (product s a) (product s b)", "compose (product s b) (product s a)"),
            ("missing_dirty_subtraction", "sub (a (add z (b x))) (a z)", "a (add z (b x))"),
            ("wrong_geometric_base", "L^n - (2 : Rat)^n", "L^n - (3 : Rat)^n"),
        )
        for name, before, after in mutations:
            need(before in formal, "mutation target missing: " + name)
            mutated = formal.replace(before, after, 1)
            (directory / "Mutation.lean").write_bytes(mutated.encode())
            result = run("Mutation.lean")
            need(result.returncode != 0 and "error" in result.stdout.lower(),
                 "kernel accepted changed claim: " + name)
        bad = "import Std\naxiom injected : False\n"
        bad += "theorem DirtyBound.defect_decomposition : False := injected\n"
        bad += ''.join("theorem DirtyBound."+name+" : True := by trivial\n" for name in ROOTS[1:])
        bad += ''.join("#print axioms DirtyBound."+name+"\n" for name in ROOTS)
        (directory / "BadAudit.lean").write_bytes(bad.encode())
        result = run("BadAudit.lean")
        need(result.returncode == 0, "forbidden-axiom control did not compile")
        try:
            audit_axioms(result.stdout)
        except ValueError:
            pass
        else:
            raise ValueError("accepted unexpected/forbidden axiom root")
    return {"version": version, "axioms": axioms, "rejected_mutations": [m[0] for m in mutations]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--lean", metavar="EXECUTABLE")
    args = parser.parse_args()
    result = finite_replay()
    destination = PACKAGE / "RESULT.json"
    if args.write:
        destination.write_bytes((json.dumps(result, indent=2, sort_keys=True)+"\n").encode())
    else:
        need(canonical(json.loads(destination.read_bytes())) == canonical(result), "receipt mismatch")
    if args.lean:
        evidence = live_lean(args.lean)
        print("PASS_LIVE_LEAN " + json.dumps(evidence, sort_keys=True))
    print(f"PASS_FINITE_CONTROLS: {result['trees']} trees, {result['cases']} cases; source pins verified")


if __name__ == "__main__":
    main()
