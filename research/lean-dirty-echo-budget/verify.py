#!/usr/bin/env python3
"""Kernel-check the resource theorem and a bounded bridge to pinned PR784.

Python 3.12+, standard library only. The default path writes only temporary files.
Copyright 2026 Gareth Davidson (@bitplane). Apache-2.0. AI assistance disclosed.
"""

from __future__ import annotations

import argparse
from collections import Counter
from functools import cache
import hashlib
import importlib.util
import itertools
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
THEOREMS = (
    "capacity", "lower_bound", "call_lower_bound", "feasibility_iff",
    "equality_family", "sharp_minimum", "exact_50_6", "no_reserved_59_5",
)
ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def pinned_source():
    manifest = json.loads((ROOT / "SOURCES.json").read_text())
    hashes = {}
    for item in manifest["files"]:
        data = (ROOT / item["vendored_path"]).read_bytes()
        actual = digest(data)
        need(actual == item["sha256"], f"source hash mismatch: {item['vendored_path']}")
        blob = hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()
        need(blob == item["git_blob"], f"source blob mismatch: {item['vendored_path']}")
        hashes[item["vendored_path"]] = actual
    spec = importlib.util.spec_from_file_location("pinned_pr784_schedule", ROOT / "vendor/pr784/schedule.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module, manifest, hashes


@cache
def compositions(n):
    """All ordered positive compositions, without reference to the source planner."""
    if n == 0:
        return ((),)
    return tuple((head, *tail) for head in range(1, n + 1) for tail in compositions(n - head))


@cache
def shapes(n):
    if n == 1:
        return ((),)
    return tuple(
        children
        for partition in compositions(n) if len(partition) >= 2
        for children in itertools.product(*(shapes(size) for size in partition))
    )


@cache
def metrics(tree):
    if not tree:
        return 0, 1, 1  # simultaneous scratch, factors, leaf calls
    children = [metrics(child) for child in tree]
    s = len(tree) - 1 + max(child[0] for child in children)
    n = sum(child[1] for child in children)
    N = 2 * children[0][2] + 2 * children[-1][2] + 4 * sum(child[2] for child in children[1:-1])
    return s, n, N


def from_plan(plan):
    return tuple(from_plan(child) for child in plan.children)


def path_prices(tree, price=1):
    if not tree:
        return [price]
    result = []
    for i, child in enumerate(tree):
        result.extend(path_prices(child, price * (2 if i in (0, len(tree) - 1) else 4)))
    return result


class ProofCases:
    """Emit constructor proofs, reusing subtrees with the proven weakening rule."""

    def __init__(self, module):
        self.module = module
        self.plans = {}
        self.names = {}
        self.lines = ["import EchoBudget", "set_option autoImplicit false", "open DirtyEcho", ""]
        self.rows = []
        self.band_proofs = []

    def plan(self, tree):
        if tree not in self.plans:
            self.plans[tree] = self.module.Plan(tuple(self.plan(child) for child in tree))
        return self.plans[tree]

    def add(self, tree):
        if tree in self.names:
            return self.names[tree]
        child_names = [self.add(child) for child in tree]
        name = f"case_{len(self.names)}"
        self.names[tree] = name
        plan = self.plan(tree)
        s, n, N = metrics(tree)
        need((plan.scratch, plan.factors, plan.calls) == (s, n, N), "source/model resource mismatch")
        self.rows.append([name, s, n, N, child_names])
        self.lines.append(f"theorem {name} : Fits {plan.scratch} {plan.factors} {plan.calls} := by")
        if not tree:
            self.lines.append("  exact Fits.leaf 0")
            return name
        budget = max(metrics(child)[0] for child in tree)
        child_proofs = [f"(weaken {child_name} {budget - metrics(child)[0]})"
                        for child_name, child in zip(child_names, tree)]
        middle = ", ".join(f"({self.plan(child).factors},{self.plan(child).calls})" for child in tree[1:-1])
        self.lines.append(f"  exact Fits.node [{middle}] {child_proofs[0]} {child_proofs[-1]} (by")
        if len(tree) == 2:
            self.lines.append("    intro x hx; cases hx)")
        else:
            self.lines.append("    intro x hx")
            self.lines.append("    simp only [List.mem_cons, List.not_mem_nil, or_false] at hx")
            self.lines.append("    rcases hx with " + " | ".join("rfl" for _ in tree[1:-1]))
            if len(tree) == 3:
                self.lines.append(f"    exact {child_proofs[1]})")
            else:
                for proof in child_proofs[1:-1]:
                    self.lines.append(f"    · exact {proof}")
                self.lines[-1] += ")"
        return name

    def text(self):
        # Balanced conjunctions reach every proof without thousands of nested tails.
        def join(items):
            if len(items) == 1:
                return items[0]
            middle = len(items) // 2
            a, pa = join(items[:middle])
            b, pb = join(items[middle:])
            return f"({a}) ∧ ({b})", f"⟨{pa}, {pb}⟩"

        for name, items in (
            ("all_cases", [(f"Fits {s} {n} {N}", name) for name, s, n, N, _ in self.rows]),
            ("all_source_optima", self.band_proofs),
        ):
            statement, proof = join(items)
            self.lines += ["", f"theorem {name} : {statement} := {proof}", f"#print axioms {name}", ""]
        return "\n".join(self.lines)


def bridge(module):
    cases = ProofCases(module)
    word_hash = hashlib.sha256()
    counts = []
    instructions = 0
    words = 0
    largest_scratch = 0

    def check_word(tree, label):
        nonlocal instructions, words, largest_scratch
        plan = cases.plan(tree)
        s, n, N = metrics(tree)
        forward = list(module.word(plan))
        backward = list(module.word(plan, -1))
        need(len(forward) == len(backward) == N, "literal word/call mismatch")
        need(backward == [(factor, src, dst, -sign) for factor, src, dst, sign in reversed(forward)],
             "literal inverse word mismatch")
        counter = Counter(factor for factor, _, _, _ in forward)
        need([counter[i] for i in range(n)] == path_prices(tree), "path multiplicity mismatch")
        need(set(counter) == set(range(n)), "factor range mismatch")
        addresses = set()
        for _, src, dst, sign in forward:
            need(src != dst and sign in (-1, 1), "bad literal instruction")
            need(0 <= src < s + 2 and 0 <= dst < s + 2, "scratch address outside declared pool")
            addresses.update((src, dst))
        need(max(addresses) - 1 == s, "actual address footprint differs from resource model")
        word_hash.update((canonical([label, forward, backward]) + "\n").encode())
        instructions += 2 * N
        words += 2
        largest_scratch = max(largest_scratch, s)

    for n in range(1, 9):
        trees = shapes(n)
        counts.append(len(trees))
        for i, tree in enumerate(trees):
            cases.add(tree)
            check_word(tree, ["exhaustive", n, i])
    need(counts == [1, 1, 3, 11, 45, 197, 903, 4279], "unexpected ordered-tree census")

    table = module.plan_table(64, 6)
    band = []
    for s in range(2, 7):
        for n in range(3 * 2**(s - 2), 2**s + 1):
            plan = table[s][n]
            tree = from_plan(plan)
            name = cases.add(tree)
            expected = 2**(s + 1) * n - 4**s
            need(plan.calls == expected and plan.scratch <= s, "source planner misses equality band")
            # This theorem states optimality for this actual source-produced call count.
            cases.lines += [f"theorem band_{s}_{n} : Fits {s} {n} {plan.calls} ∧",
                            f"    ∀ M, Fits {s} {n} M → {plan.calls} ≤ M := by",
                            f"  refine ⟨weaken {name} {s - plan.scratch}, ?_⟩",
                            "  intro M hm", "  have hb := lower_bound hm",
                            f"  change {2**(s+1)*n} ≤ M+{4**s} at hb", "  omega"]
            cases.band_proofs.append((f"Fits {s} {n} {plan.calls} ∧ "
                                     f"∀ M, Fits {s} {n} M → {plan.calls} ≤ M", f"band_{s}_{n}"))
            check_word(tree, ["equality-band", s, n])
            band.append([s, n, plan.calls, plan.scratch, name])
    cases.lines += ["#print axioms band_6_50"]
    source = cases.text()
    return source, {
        "ordered_trees_by_leaves_1_to_8": counts,
        "ordered_trees_total": sum(counts),
        "constructor_proofs": len(cases.names),
        "case_profiles_sha256": digest(canonical(cases.rows).encode()),
        "generated_lean_sha256": digest(source.encode()),
        "optimizer_equality_cases": band,
        "literal_words_checked": words,
        "literal_instructions_checked": instructions,
        "literal_words_sha256": word_hash.hexdigest(),
        "largest_scratch_in_finite_check": largest_scratch,
    }


def axiom_audit(output, expected_names):
    found = {}
    pattern = re.compile(r"^'([^']+)' depends on axioms: \[([^]]*)\]$", re.M)
    for name, body in pattern.findall(output):
        axioms = sorted(part.strip() for part in body.split(",") if part.strip())
        need(set(axioms) <= ALLOWED_AXIOMS, f"unapproved axiom in {name}: {axioms}")
        need(name not in found, f"duplicate axiom audit: {name}")
        found[name] = axioms
    need(set(found) == set(expected_names), f"missing or extra axiom audit: {sorted(found)}")
    return found


def lean_run(lean, directory, filename, output=None):
    env = dict(os.environ)
    env["LEAN_PATH"] = str(directory)
    command = [lean, "-DwarningAsError=true", "-DmaxRecDepth=20000", "-DmaxHeartbeats=2000000"]
    if output:
        command += ["-o", output]
    command.append(filename)
    return subprocess.run(command, cwd=directory, env=env, text=True, capture_output=True, timeout=180)


def controls(lean, directory, formal_source, model_source):
    mutations = {
        "underprice_endpoint": ("2 * ca + 4 * calls middle + 2 * cb", "ca + 4 * calls middle + 2 * cb"),
        "underprice_interior": ("2 * ca + 4 * calls middle + 2 * cb", "2 * ca + 2 * calls middle + 2 * cb"),
        "omit_parent_connector": ("s + middle.length + 1", "s + middle.length"),
        "wrong_50_factor_minimum": ("Fits 6 50 2304 ∧", "Fits 6 50 2303 ∧"),
        "extend_equality_band_past_capacity": ("(hi : n ≤ 4*2^d) :", "(hi : n ≤ 5*2^d) :"),
    }
    results = []
    for name, (before, after) in mutations.items():
        need(before in formal_source, f"missing mutation target: {name}")
        changed = formal_source.replace(before, after, 1)
        path = directory / "Mutation.lean"
        path.write_text(changed)
        result = lean_run(lean, directory, path.name)
        need(result.returncode != 0 and "error:" in result.stdout + result.stderr, f"Lean accepted mutation: {name}")
        results.append(name)
    # Alter only the asserted resource profile in a genuine source-derived proof.
    before = "theorem case_1 : Fits 1 2 4"
    need(before in model_source, "missing model correspondence mutation target")
    prefix = model_source.split("theorem case_2 :", 1)[0]
    (directory / "BrokenCases.lean").write_text(prefix.replace(before, "theorem case_1 : Fits 1 2 3", 1))
    result = lean_run(lean, directory, "BrokenCases.lean")
    need(result.returncode != 0 and "error:" in result.stdout + result.stderr, "Lean accepted wrong source profile")
    results.append("wrong_source_derived_profile")
    for axiom in ("sorryAx", "Lean.ofReduceBool", "user_assumption"):
        try:
            axiom_audit(f"'x' depends on axioms: [{axiom}]", ["x"])
        except ValueError:
            pass
        else:
            raise ValueError(f"axiom audit accepted {axiom}")
        results.append(f"reject_axiom_{axiom}")
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lean", default=os.environ.get("LEAN", "lean"), help="Lean 4.21.0 executable")
    parser.add_argument("--write", type=Path, help="create a new receipt; refuses to overwrite")
    parser.add_argument("--emit-cases", type=Path, help="save generated Lean cases for inspection; refuses to overwrite")
    parser.add_argument("--expected", type=Path, default=ROOT / "EXPECTED.json")
    args = parser.parse_args()
    if args.write:
        need(not args.write.exists(), f"receipt destination already exists: {args.write}")
    if args.emit_cases:
        need(not args.emit_cases.exists(), f"case destination already exists: {args.emit_cases}")
    lean = shutil.which(args.lean)
    need(lean, "Lean 4.21.0 was not found; pass --lean or set LEAN")
    version = subprocess.run([lean, "--version"], capture_output=True, text=True, check=True).stdout.strip()
    # The source commit and version are the pin; the host triple may differ.
    need(re.fullmatch(r"Lean \(version 4\.21\.0, [^,]+, commit 6741444a63ee, Release\)", version),
         f"unexpected Lean toolchain: {version}")
    sys.dont_write_bytecode = True
    module, manifest, hashes = pinned_source()
    formal_source = (ROOT / "EchoBudget.lean").read_text()
    need(not re.search(r"\b(sorry|admit|axiom|native_decide)\b", formal_source), "proof contains a forbidden declaration or escape")
    model_source, bridge_receipt = bridge(module)
    if args.emit_cases:
        with args.emit_cases.open("x") as output:
            output.write(model_source)
    with tempfile.TemporaryDirectory(prefix="lean-dirty-echo-") as temporary:
        directory = Path(temporary)
        (directory / "EchoBudget.lean").write_text(formal_source)
        formal = lean_run(lean, directory, "EchoBudget.lean", "EchoBudget.olean")
        need(formal.returncode == 0, "formal proof failed:\n" + formal.stdout + formal.stderr)
        formal_axioms = axiom_audit(formal.stdout, [f"DirtyEcho.{name}" for name in THEOREMS])
        (directory / "ModelCases.lean").write_text(model_source)
        generated = lean_run(lean, directory, "ModelCases.lean")
        need(generated.returncode == 0, "source correspondence failed:\n" + generated.stdout + generated.stderr)
        generated_axioms = axiom_audit(generated.stdout, ["band_6_50", "all_cases", "all_source_optima"])
        negative = controls(lean, directory, formal_source, model_source)
    receipt = {
        "schema": "lean-dirty-echo-budget-v1",
        "base_commit": manifest["base_commit"],
        "subject_head": manifest["subject_head"],
        "source_sha256": hashes,
        "lean_version": "4.21.0", "lean_commit": "6741444a63ee",
        "formal_source_sha256": digest(formal_source.encode()),
        "formal_axioms": formal_axioms,
        "generated_axioms": generated_axioms,
        "bridge": bridge_receipt,
        "negative_controls": negative,
    }
    if args.write:
        with args.write.open("x") as output:
            output.write(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    else:
        expected = json.loads(args.expected.read_text())
        need(canonical(receipt) == canonical(expected), "receipt mismatch")
    print(f"PASS: 8 universal statements; {bridge_receipt['constructor_proofs']} constructor proofs; "
          f"5440 ordered trees; 36 equality cases; {len(negative)} negative controls; exact 50/6 minimum 2304")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        sys.exit(1)
