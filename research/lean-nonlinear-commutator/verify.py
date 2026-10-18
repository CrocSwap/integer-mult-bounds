#!/usr/bin/env python3
"""Lean semantics proof and bounded source binding for PR628's binary dispatcher.

Copyright 2026 Gareth Davidson (@bitplane). Apache-2.0.
Prepared with substantial OpenAI Codex assistance. Python 3.12+, stdlib only.
"""

from __future__ import annotations

import argparse
import ast
from functools import cache
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent
FORMAL_NAMES = (
    "run_eq", "scratch_restored", "positive_increment", "exact_inverse",
    "inverse_then_forward", "product_additive", "delta_eq_product",
    "ideal_execution", "full_execution", "nonlinear_dirt_counterexample",
    "inverse_involutive", "negative_node_order",
)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def pins():
    manifest = json.loads((ROOT / "SOURCES.json").read_text())
    hashes = {}
    for item in manifest["files"]:
        data = (ROOT / item["vendored_path"]).read_bytes()
        need(sha(data) == item["sha256"], f"source hash mismatch: {item['vendored_path']}")
        blob = hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()
        need(blob == item["git_blob"], f"source blob mismatch: {item['vendored_path']}")
        hashes[item["vendored_path"]] = sha(data)
    return manifest, hashes


class Dispatcher:
    """Execute only the authenticated compose AST, with a completed-leaf stub.

    No arithmetic leaf, factor preparation, or module initialization is imported.
    """

    def __init__(self):
        raw = (ROOT / "vendor/pr628/dirty.py").read_text()
        nodes = [node for node in ast.parse(raw).body if isinstance(node, ast.FunctionDef) and node.name == "compose"]
        need(len(nodes) == 1, "missing or ambiguous compose function")
        node = nodes[0]
        # ast.dump's formatting changed across Python releases. Bind the exact
        # extracted source text instead of version-specific debug serialization.
        self.compose_sha256 = sha(ast.get_source_segment(raw, node).encode())
        self.scope = {"c": SimpleNamespace(need=need, norm2=lambda z: z[0]**2 + z[1]**2)}
        exec(compile(ast.Module(body=[node], type_ignores=[]), "pinned-pr628-compose", "exec"), self.scope)
        self.compose = self.scope["compose"]

    def call(self, n, positive, x, y, dirt, function=None):
        arrays = [list(x), list(y), *(list(row) for row in dirt)]
        addresses = {id(array): i for i, array in enumerate(arrays)}
        trace = []

        def leaf(source, target, factor, phases, beta, bits, orientation, sign, stats):
            trace.append([factor, addresses[id(source)], addresses[id(target)], sign == 1])
            if function is not None:
                increment = function(factor, tuple(source))
                target[:] = [a + sign*b for a, b in zip(target, increment)]

        self.scope["leaf"] = leaf
        self.compose(arrays[0], arrays[1], list(range(n)), arrays[2:], [(1, 0)]*len(x),
                     1, 128, 1, 1 if positive else -1)
        return tuple(tuple(row) for row in arrays), trace


def balanced(n, start=0):
    if n == 1:
        return start
    a = n//2
    return balanced(a, start), balanced(n-a, start+a)


def depth(tree):
    return 0 if isinstance(tree, int) else 1 + max(map(depth, tree))


def invert(word):
    return [[factor, source, target, not positive] for factor, source, target, positive in reversed(word)]


def model_word(tree, positive, source=0, target=1, fresh=2):
    if isinstance(tree, int):
        forward = [[tree, source, target, True]]
    else:
        a = model_word(tree[0], True, source, fresh, fresh+1)
        b = model_word(tree[1], True, fresh, target, fresh+1)
        forward = a + b + invert(a) + invert(b)
    return forward if positive else invert(forward)


def add(a, b):
    return tuple(x+y for x, y in zip(a, b))


def sub(a, b):
    return tuple(x-y for x, y in zip(a, b))


def run(tree, positive, x, y, dirt, function):
    """Functional transcription of the proved Lean evaluator, not a trace runner."""
    if isinstance(tree, int):
        return (add if positive else sub)(y, function(tree, x)), dirt
    z, rest = dirt[0], dirt[1:]
    if positive:
        z1, s1 = run(tree[0], True, x, z, rest, function)
        y1, s2 = run(tree[1], True, z1, y, s1, function)
        z2, s3 = run(tree[0], False, x, z1, s2, function)
        y2, s4 = run(tree[1], False, z2, y1, s3, function)
    else:
        y1, s1 = run(tree[1], True, z, y, rest, function)
        z1, s2 = run(tree[0], True, x, z, s1, function)
        y2, s3 = run(tree[1], False, z1, y1, s2, function)
        z2, s4 = run(tree[0], False, x, z1, s3, function)
    return y2, (z2, *s4)


def delta(tree, x, dirt, function):
    if isinstance(tree, int):
        return function(tree, x)
    z, rest = dirt[0], dirt[1:]
    return sub(delta(tree[1], add(z, delta(tree[0], x, rest, function)), rest, function),
               delta(tree[1], z, rest, function))


def apply_word(word, arrays, function):
    state = list(arrays)
    for label, source, target, positive in word:
        state[target] = (add if positive else sub)(state[target], function(label, state[source]))
    return tuple(state)


@cache
def shapes(n):
    if n == 1:
        return (None,)
    return tuple((a, b) for k in range(1, n) for a in shapes(k) for b in shapes(n-k))


def label_shape(shape, first=0):
    if shape is None:
        return first, first+1
    left, end = label_shape(shape[0], first)
    right, end = label_shape(shape[1], end)
    return (left, right), end


def leaves(tree):
    return [tree] if isinstance(tree, int) else leaves(tree[0]) + leaves(tree[1])


def nonlinear(label, source):
    w = len(source)
    return tuple(((2*label+1)*source[i] - 3*source[(i+1)%w] + label + 5)//(label%5+2)
                 for i in range(w))


def bounded_nonlinear(label, source):
    w = len(source)
    return tuple(((label+3)*source[i] + source[(i+1)%w]**2 + 11*label + 7)%97 - 48
                 for i in range(w))


def linear(label, source):
    # Noncommuting integer shears on different coordinate pairs.
    w = len(source)
    out = list(source)
    i, j = label%w, (label+1)%w
    out[i] += (-1 if label%2 else 1)*source[j]
    return tuple(out)


def fixture(tree, width, offset):
    rows = depth(tree)+2
    return tuple(tuple((3*r-2*i+offset)*(-1 if (r+i)%2 else 1) for i in range(width)) for r in range(rows))


def lean_tree(tree, budget):
    if isinstance(tree, int):
        return f"(.leaf {budget} {tree})"
    return f"(.node {lean_tree(tree[0], budget-1)} {lean_tree(tree[1], budget-1)})"


def trace_lean(records):
    lines = ["import NonlinearEcho", "open NonlinearEcho", ""]
    names = []
    for n, positive, instructions in records:
        tree = balanced(n)
        sign = "true" if positive else "false"
        name = f"trace_{n}_{sign}"
        literal = ",".join(f"⟨{i},{s},{t},{'true' if p else 'false'}⟩" for i, s, t, p in instructions)
        lines += [f"theorem {name} : word {lean_tree(tree, depth(tree))} {sign} 0 1 2 =",
                  f"    [{literal}] := by rfl", f"#print axioms {name}", ""]
        names.append(name)
    return "\n".join(lines), names


def bounded_checks(dispatcher):
    source_ns = [*range(1, 65), 83]
    trace_hash = hashlib.sha256()
    state_hash = hashlib.sha256()
    trace_records = []
    source_words = source_instructions = source_states = source_executed_leaves = 0
    unbalanced_states = 0
    functions = (("floor", nonlinear), ("square_mod", bounded_nonlinear), ("linear", linear))

    def check_state(tree, positive, original, function, result, tag):
        x, y, *scratch = original
        scratch = tuple(scratch)
        increment = delta(tree, x, scratch, function)
        expected_y = (add if positive else sub)(y, increment)
        need(result == (x, expected_y, *scratch), f"restoration/increment mismatch: {tag}")
        model_y, model_dirt = run(tree, positive, x, y, scratch, function)
        need(result == (x, model_y, *model_dirt), f"source/functional model mismatch: {tag}")
        if function is linear:
            product = x
            for label in leaves(tree):
                product = function(label, product)
            need(increment == product, f"ordered linear product mismatch: {tag}")
        state_hash.update((canonical([tag, original, result]) + "\n").encode())

    for n in source_ns:
        tree = balanced(n)
        need(depth(tree) == (n-1).bit_length(), "balanced scratch depth mismatch")
        for positive in (True, False):
            zero = fixture(tree, 1, 0)
            _, trace = dispatcher.call(n, positive, zero[0], zero[1], zero[2:])
            need(trace == model_word(tree, positive), f"source/model trace mismatch: n={n}, sign={positive}")
            source_words += 1
            source_instructions += len(trace)
            trace_hash.update((canonical([n, positive, trace]) + "\n").encode())
            if n <= 16 or n == 83:
                trace_records.append((n, positive, trace))
        for width in (1, 2, 3):
            original = fixture(tree, width, 83-n)
            for name, function in functions:
                for positive in (True, False):
                    result, trace = dispatcher.call(n, positive, original[0], original[1], original[2:], function)
                    check_state(tree, positive, original, function, result, ["source", n, width, name, positive])
                    restored, inverse_trace = dispatcher.call(n, not positive, result[0], result[1], result[2:], function)
                    need(restored == original, "source whole-word inverse failed")
                    need(inverse_trace == invert(trace), "actual inverse trace failed")
                    source_states += 1
                    source_executed_leaves += len(trace) + len(inverse_trace)

    census = []
    for n in range(1, 8):
        census.append(len(shapes(n)))
        for index, shape in enumerate(shapes(n)):
            tree, last = label_shape(shape)
            need(last == n, "tree labeling mismatch")
            for width in (2, 3):
                original = fixture(tree, width, index-83)
                for name, function in functions:
                    for positive in (True, False):
                        trace = model_word(tree, positive)
                        result = apply_word(trace, original, function)
                        check_state(tree, positive, original, function, result, ["all-trees", n, index, width, name, positive])
                        need(apply_word(invert(trace), result, function) == original, "unbalanced word inverse failed")
                        unbalanced_states += 1
    need(census == [1, 1, 2, 5, 14, 42, 132], "binary-tree census mismatch")

    # Explicit witnesses keep the contract limitations observable.
    square = lambda label, x: x if label == 0 else tuple(a*a for a in x)
    tree = (0, 1)
    dirt0 = ((1,), (9,), (0,))
    dirt1 = ((1,), (9,), (1,))
    out0 = apply_word(model_word(tree, True), dirt0, square)
    out1 = apply_word(model_word(tree, True), dirt1, square)
    need(out0 == ((1,), (10,), (0,)) and out1 == ((1,), (12,), (1,)), "missing dirt-dependence witness")
    wrong = [[f, s, t, not p] for f, s, t, p in model_word(tree, True)]
    wrong_out = apply_word(wrong, dirt1, square)
    correct_out = apply_word(model_word(tree, False), dirt1, square)
    need(wrong_out == ((1,), (10,), (1,)) and correct_out == ((1,), (6,), (1,)), "missing inverse-order witness")
    need(linear(1, linear(0, (1, 1))) != linear(0, linear(1, (1, 1))), "linear witness accidentally commutes")

    generated, trace_names = trace_lean(trace_records)
    return generated, trace_names, {
        "source_factor_counts": source_ns,
        "source_compose_sha256": dispatcher.compose_sha256,
        "source_words": source_words,
        "source_trace_instructions": source_instructions,
        "source_words_sha256": trace_hash.hexdigest(),
        "source_execution_cases": source_states,
        "source_execution_leaf_calls_including_inverse": source_executed_leaves,
        "all_binary_trees_by_leaves_1_to_7": census,
        "all_binary_trees_total": sum(census),
        "tree_execution_cases": unbalanced_states,
        "state_cases_sha256": state_hash.hexdigest(),
        "lean_trace_equalities": len(trace_names),
        "generated_lean_sha256": sha(generated.encode()),
        "nonlinear_dirt_witness": [out0, out1],
        "inverse_order_witness": {"wrong": wrong_out, "correct": correct_out},
        "noncommuting_product": [linear(1, linear(0, (1, 1))), linear(0, linear(1, (1, 1)))],
    }


def axiom_audit(output, names):
    found = {}
    for line in output.splitlines():
        match = re.fullmatch(r"'([^']+)' depends on axioms: \[([^]]*)\]", line)
        if match:
            name, body = match.groups()
            axioms = sorted(part.strip() for part in body.split(",") if part.strip())
        else:
            match = re.fullmatch(r"'([^']+)' does not depend on any axioms", line)
            if not match:
                continue
            name, axioms = match[1], []
        need(set(axioms) <= {"propext", "Quot.sound", "Classical.choice"}, f"unapproved axioms: {name}: {axioms}")
        need(name not in found, f"duplicate axiom audit: {name}")
        found[name] = axioms
    need(set(found) == set(names), f"missing or unexpected axiom audit: {sorted(found)}")
    return found


def lean_run(lean, directory, filename, output=None):
    env = dict(os.environ)
    env["LEAN_PATH"] = str(directory)
    command = [lean, "-j1", "-s65536", "-DwarningAsError=true",
               "-DmaxRecDepth=100000", "-DmaxHeartbeats=4000000"]
    if output:
        command += ["-o", output]
    command.append(filename)
    return subprocess.run(command, cwd=directory, env=env, capture_output=True, text=True, timeout=300)


def controls(lean, directory, formal, generated, dispatcher):
    changes = {
        "omit_scratch_restore": ("run f left false x z1 s2", "run f left true x z1 s2"),
        "wrong_final_target_sign": ("run f right false z2 y1 s3", "run f right true z2 y1 s3"),
        "target_dependent_leaf": ("add y (f label x)", "add y (f label y)"),
        "reverse_factor_order": ("product f right (product f left x)", "product f left (product f right x)"),
        "omit_inverse_reversal": ("xs.reverse.map flip", "xs.map flip"),
    }
    names = []
    for name, (before, after) in changes.items():
        need(before in formal, f"missing mutation target: {name}")
        (directory / "Mutation.lean").write_text(formal.replace(before, after, 1))
        result = lean_run(lean, directory, "Mutation.lean")
        need(result.returncode != 0 and "error:" in result.stdout + result.stderr, f"accepted proof mutation: {name}")
        names.append(name)
    prefix = generated.split("theorem trace_2_false", 1)[0]
    before = "⟨0,0,2,true⟩"
    need(before in prefix, "missing source literal mutation target")
    (directory / "BrokenTrace.lean").write_text(prefix.replace(before, "⟨0,0,2,false⟩", 1))
    result = lean_run(lean, directory, "BrokenTrace.lean")
    need(result.returncode != 0 and "error:" in result.stdout + result.stderr, "accepted incorrect source trace literal")
    names.append("wrong_source_trace_literal")
    for axiom in ("sorryAx", "Lean.ofReduceBool", "user_assumption"):
        try:
            axiom_audit(f"'x' depends on axioms: [{axiom}]", ["x"])
        except ValueError:
            pass
        else:
            raise ValueError(f"accepted forbidden axiom: {axiom}")
        names.append(f"reject_axiom_{axiom}")

    for name in ("source_target_alias", "scratch_source_alias", "scratch_target_alias", "insufficient_depth"):
        x, y, z = [1], [2], [3]
        scratch = [z]
        if name == "source_target_alias":
            y = x
        elif name == "scratch_source_alias":
            scratch = [x]
        elif name == "scratch_target_alias":
            scratch = [y]
        else:
            scratch = []
        touched = []
        dispatcher.scope["leaf"] = lambda *args: touched.append(True)
        try:
            dispatcher.compose(x, y, [0, 1], scratch, [(1, 0)], 1, 128, 1)
        except ValueError as error:
            expected = "dirty depth" if name == "insufficient_depth" else "all ancestor arrays distinct"
            need(expected in str(error) and not touched, f"wrong admission failure: {name}")
        else:
            raise ValueError(f"accepted source admission control: {name}")
        names.append(name)
    return names


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lean", default=os.environ.get("LEAN", "lean"))
    parser.add_argument("--expected", type=Path, default=ROOT / "EXPECTED.json")
    parser.add_argument("--write", type=Path, help="create a new receipt; refuses to overwrite")
    parser.add_argument("--emit-cases", type=Path, help="export generated Lean source trace equalities exclusively")
    args = parser.parse_args()
    for path in (args.write, args.emit_cases):
        if path:
            need(not path.exists(), f"output destination already exists: {path}")
    lean = shutil.which(args.lean)
    need(lean, "Lean 4.21.0 not found; pass --lean or set LEAN")
    version = subprocess.run([lean, "--version"], capture_output=True, text=True, check=True).stdout.strip()
    need(re.fullmatch(r"Lean \(version 4\.21\.0, [^,]+, commit 6741444a63ee, Release\)", version),
         f"unexpected Lean toolchain: {version}")
    manifest, hashes = pins()
    dispatcher = Dispatcher()
    formal = (ROOT / "NonlinearEcho.lean").read_text()
    need(not re.search(r"\b(sorry|admit|axiom|native_decide)\b", formal), "forbidden proof declaration or escape")
    generated, trace_names, finite = bounded_checks(dispatcher)
    if args.emit_cases:
        with args.emit_cases.open("x") as output:
            output.write(generated)
    with tempfile.TemporaryDirectory(prefix="nonlinear-echo-") as temporary:
        directory = Path(temporary)
        (directory / "NonlinearEcho.lean").write_text(formal)
        proof = lean_run(lean, directory, "NonlinearEcho.lean", "NonlinearEcho.olean")
        need(proof.returncode == 0, "formal semantics failed:\n" + proof.stdout + proof.stderr)
        proof_axioms = axiom_audit(proof.stdout, ["NonlinearEcho." + name for name in FORMAL_NAMES])
        (directory / "TraceCases.lean").write_text(generated)
        bound = lean_run(lean, directory, "TraceCases.lean")
        need(bound.returncode == 0, "source trace kernel check failed:\n" + bound.stdout + bound.stderr)
        trace_axioms = axiom_audit(bound.stdout, trace_names)
        negative = controls(lean, directory, formal, generated, dispatcher)
    receipt = {
        "schema": "lean-nonlinear-commutator-v1",
        "base_commit": manifest["base_commit"],
        "subject_head": manifest["subject_head"],
        "audit_head": manifest["audit_head"],
        "source_sha256": hashes,
        "formal_source_sha256": sha(formal.encode()),
        "lean_version": "4.21.0", "lean_commit": "6741444a63ee",
        "formal_axioms": proof_axioms, "trace_axioms": trace_axioms,
        "finite": finite, "negative_controls": negative,
    }
    if args.write:
        with args.write.open("x") as output:
            output.write(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    else:
        need(canonical(receipt) == canonical(json.loads(args.expected.read_text())), "receipt mismatch")
    print(f"PASS_NONLINEAR_ECHO: {len(FORMAL_NAMES)} formal statements; {len(trace_names)} kernel trace equalities; "
          f"{finite['source_execution_cases']} source cases; {finite['tree_execution_cases']} tree cases; "
          f"{len(negative)} controls; kappa unchanged")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        sys.exit(1)
