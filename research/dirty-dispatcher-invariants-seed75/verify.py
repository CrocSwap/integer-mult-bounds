#!/usr/bin/env python3
"""Scoped all-prefix formalization and bounded PR628 dispatcher binding.

Hanson Sun, with substantial OpenAI Codex assistance. Apache-2.0.
No predecessor verifier or numerical leaf implementation is imported.
"""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
from types import SimpleNamespace

PACKAGE = Path(__file__).resolve().parent
REPO = PACKAGE.parents[1]
SOURCE = "research/dirty-prefix-precision/vendor/pr628/dirty.py"
TOOLCHAIN = "leanprover/lean4:v4.28.0"
FORMAL = ("emit_ports", "emit_bounded", "prefix_preserves", "prefix_shift",
          "prefix_fixes_axis", "inverse_preserves", "four_phase_invariants")
DOMAIN = (*range(1, 33), 75)
KERNEL_DOMAIN = (*range(1, 9), 75)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def check_sources(repo=REPO):
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    pins = {}
    for row in manifest["files"]:
        if row["usage"] != "input":
            continue
        raw = (repo / row["path"]).read_bytes()
        require(sha(raw) == row["sha256"], "source SHA256: " + row["path"])
        blob = hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()
        require(blob == row["git_blob"], "source Git blob: " + row["path"])
        pins[row["path"]] = row["sha256"]
    require(SOURCE in pins, "dispatcher source not declared")
    return pins


EXPECTED_CORE = '''
if len(factors) == 1:
    return leaf(x, y, factors[0], phases, beta, bits, d, sign, stats)
mid = len(factors) // 2
B, A = factors[:mid], factors[mid:]
z = scratch[0]
rest = scratch[1:]
operations = [(x,z,B,1), (z,y,A,1), (x,z,B,-1), (z,y,A,-1)]
if sign == -1:
    operations = [(src,dst,fs,-sgn) for src,dst,fs,sgn in reversed(operations)]
for src,dst,fs,sgn in operations:
    compose(src,dst,fs,rest,phases,beta,bits,d,sgn,stats)
'''


def extract(raw, check_shape=True):
    nodes = [n for n in ast.parse(raw).body
             if isinstance(n, ast.FunctionDef) and n.name == "compose"]
    require(len(nodes) == 1, "ambiguous compose definition")
    node = nodes[0]
    if check_shape:
        # Preceding guards are pinned and alias/depth failures are exercised.
        actual = ast.Module(body=node.body[7:], type_ignores=[])
        require(ast.dump(actual, include_attributes=False) ==
                ast.dump(ast.parse(EXPECTED_CORE), include_attributes=False),
                "dispatcher recursive AST differs from the formal schedule")
    scope = {"c": SimpleNamespace(need=require, norm2=lambda z: sum(v*v for v in z))}
    exec(compile(ast.Module(body=[node], type_ignores=[]), "authenticated-compose", "exec"), scope)
    return scope, sha(ast.get_source_segment(raw, node).encode())


def source_trace(scope, n, positive, *, alias=None, short_scratch=False, direction=1):
    arrays = [[0] for _ in range(2 + (n-1).bit_length())]
    if alias == "target":
        arrays[2] = arrays[1]
    elif alias == "source":
        arrays[2] = arrays[0]
    elif alias == "ports":
        arrays[1] = arrays[0]
    addresses = {id(v): i for i, v in enumerate(arrays)}
    trace = []

    def leaf(x, y, factor, phases, beta, bits, d, sign, stats):
        trace.append([addresses[id(x)], addresses[id(y)], factor, sign == 1])

    scope["leaf"] = leaf
    scratch = arrays[2:-1] if short_scratch else arrays[2:]
    scope["compose"](arrays[0], arrays[1], list(range(n)), scratch,
                     [(1, 0)], 1, 32, direction, 1 if positive else -1)
    return trace


def balanced(n, first=0):
    require(n >= 1, "positive factor count")
    if n == 1:
        return first
    mid = n//2
    return balanced(mid, first), balanced(n-mid, first+mid)


def height(tree):
    return 0 if isinstance(tree, int) else 1 + max(map(height, tree))


def inverse(word):
    return [[s, d, f, not sign] for s, d, f, sign in reversed(word)]


def model(tree, positive=True, x=0, y=1, fresh=2):
    """Build the positive word then invert; Lean instead recurses on both signs."""
    if isinstance(tree, int):
        out = [[x, y, tree, True]]
    else:
        a = model(tree[0], True, x, fresh, fresh+1)
        b = model(tree[1], True, fresh, y, fresh+1)
        out = a + b + inverse(a) + inverse(b)
    return out if positive else inverse(out)


def identity(size):
    return [[int(i == j) for j in range(size)] for i in range(size)]


def phase_matrix_checks(word, width):
    """Independent scalar matrix instances: left row and inverse column updates."""
    digest = hashlib.sha256()
    counts = 0
    for side in ("left", "right"):
        forward, backward = identity(width+1), identity(width+1)
        remap = {0: 0 if side == "left" else 2, 1: 2 if side == "left" else 1}
        for src, dst, factor, positive in word:
            src, dst = remap.get(src, src+1), remap.get(dst, dst+1)
            c = (1, -1, 2)[factor % 3] * (1 if positive else -1)
            forward[dst] = [a+c*b for a, b in zip(forward[dst], forward[src])]
            for row in backward:
                row[src] -= c*row[dst]
            require([row[1] for row in forward] == [int(i == 1) for i in range(width+1)],
                    "phase column invariant")
            require(backward[0] == [int(i == 0) for i in range(width+1)],
                    "inverse source row invariant")
            counts += 2
        for i in range(width+1):
            for j in range(width+1):
                require(sum(forward[i][k]*backward[k][j] for k in range(width+1)) == int(i == j),
                        "full-matrix inverse control")
        digest.update(encoded([side, forward, backward]))
    return counts, digest.hexdigest()


def nonlinear_prefix_checks(word, width):
    base = [7*i-9 for i in range(width)]
    shifted = base.copy()
    shifted[1] += 23
    initial_source = base[0]
    for src, dst, factor, positive in word:
        require(src != dst, "self-shear")
        for state in (base, shifted):
            value = (state[src]**2 + (factor+1)*state[src]) % 17
            state[dst] += value if positive else -value
        require(base[0] == shifted[0] == initial_source, "dirty source changed")
        require(all(b-a == (23 if i == 1 else 0)
                    for i, (a, b) in enumerate(zip(base, shifted))), "target translation dependence")
    return sha(encoded([base, shifted]))


def audit_axioms(output, expected):
    found = {}
    for line in output.splitlines():
        match = re.fullmatch(r"'([^']+)' depends on axioms: \[(.*)\]", line)
        if match:
            name, raw = match.groups()
            axioms = sorted(s.strip() for s in raw.split(",") if s.strip())
        else:
            match = re.fullmatch(r"'([^']+)' does not depend on any axioms", line)
            if not match:
                continue
            name, axioms = match[1], []
        require(name not in found, "duplicate theorem audit")
        require(set(axioms) <= {"propext", "Quot.sound"}, "unapproved axiom: " + name)
        found[name] = axioms
    require(set(found) == set(expected), "missing or unexpected theorem audit")
    return found


def controls(raw):
    names = []
    for name, before, after in (
        ("source_port_read", "(z,y,A,1)", "(y,z,A,1)"),
        ("source_port_write", "(x,z,B,1)", "(z,x,B,1)"),
        ("reused_parent_scratch", "rest=scratch[1:]", "rest=scratch"),
        ("negative_order", "in reversed(operations)", "in operations"),
        ("factor_partition", "factors[mid:]", "factors[:mid]"),
    ):
        require(raw.count(before) == 1, "mutation target: " + name)
        changed = raw.replace(before, after)
        try:
            extract(changed)
        except ValueError:
            pass
        else:
            raise ValueError("AST mutation accepted: " + name)
        altered, _ = extract(changed, check_shape=False)
        rejects = False
        try:
            for n in (2, 3, 5):
                for sign in (True, False):
                    if source_trace(altered, n, sign) != model(balanced(n), sign):
                        rejects = True
        except ValueError:
            rejects = True
        require(rejects, "mutation not observed semantically: " + name)
        names.append(name)
    actual, _ = extract(raw)
    for alias in ("source", "target", "ports"):
        try:
            source_trace(actual, 2, True, alias=alias)
        except ValueError as e:
            require("ancestor arrays distinct" in str(e), "wrong alias failure")
        else:
            raise ValueError("alias accepted")
        names.append("reject_alias_"+alias)
    try:
        source_trace(actual, 3, True, short_scratch=True)
    except ValueError as e:
        require("dirty depth" in str(e), "wrong depth failure")
    else:
        raise ValueError("missing scratch accepted")
    names.append("reject_short_scratch")
    # Concrete omitted-premise witnesses, rather than alleged source defects.
    def one_leaf(state, f, reads_target=False):
        out = state.copy()
        out[1] += f(state[1] if reads_target else state[0])
        return out
    axis = [0, 7]
    require(one_leaf(axis, lambda v: v) == axis, "valid leaf axis positive control")
    require(one_leaf(axis, lambda v: v, reads_target=True) != axis, "target-read axis control")
    names.append("target_reading_leaf_axis_fails")
    require(one_leaf(axis, lambda v: v+1) != axis, "nonzero-at-zero axis control")
    names.append("zero_preservation_needed")
    add = lambda a, b: 2*a+b
    require(add(add(3, 5), 1) != add(add(3, 1), 5), "translation law control")
    names.append("translation_law_needed")
    for bad in ("sorryAx", "Lean.ofReduceBool", "custom_axiom"):
        try:
            audit_axioms(f"'test' depends on axioms: [{bad}]", ["test"])
        except ValueError:
            names.append("reject_axiom_"+bad)
        else:
            raise ValueError("axiom control accepted")
    return names


def lean_tree(tree):
    return f"(.leaf {tree})" if isinstance(tree, int) else f"(.node {lean_tree(tree[0])} {lean_tree(tree[1])})"


def trace_module(traces):
    lines = ["import Dispatcher", "open DirtyDispatcher", "namespace SourceTrace", ""]
    names = []
    for n, sign, word in traces:
        name = f"n{n}_{'pos' if sign else 'neg'}"
        names.append("SourceTrace."+name)
        literal = ",\n".join(f"⟨{s},{d},{f},{str(b).lower()}⟩" for s, d, f, b in word)
        lines += [f"theorem {name} : emit {lean_tree(balanced(n))} {str(sign).lower()} 0 1 2 =",
                  f"[{literal}] := by rfl", f"#print axioms {name}", ""]
    lines += ["end SourceTrace", ""]
    return "\n".join(lines), names


def python_evidence():
    pins = check_sources()
    raw = (REPO / SOURCE).read_text()
    scope, source_function_sha = extract(raw)
    digest, mathematical = hashlib.sha256(), hashlib.sha256()
    leaves = obligations = 0
    traces = []
    for n in DOMAIN:
        for sign in (True, False):
            word = source_trace(scope, n, sign)
            require(source_trace(scope, n, sign, direction=-1) == word, "direction changes dispatcher word")
            tree = balanced(n)
            require(word == model(tree, sign), f"source/model mismatch n={n} sign={sign}")
            require(len(word) > 0, "empty trace")
            require(all(s != 1 and d != 0 and 0 <= s < 2+height(tree) and 0 <= d < 2+height(tree)
                        for s, d, _, _ in word), "protected ports or finite scratch bounds")
            leaves += len(word)
            digest.update(encoded([n, sign, word]))
            nonlinear = nonlinear_prefix_checks(word, 2+height(tree))
            checked, matrices = phase_matrix_checks(word, 2+height(tree))
            obligations += checked
            mathematical.update(encoded([n, sign, nonlinear, matrices]))
            if n in KERNEL_DOMAIN:
                traces.append((n, sign, word))
    generated, names = trace_module(traces)
    report = {
        "status": "PASS_BOUNDED_DISPATCHER_BINDING", "assignment_seed": 75,
        "base_commit": json.loads((PACKAGE/"SOURCES.json").read_text())["base_commit"],
        "source_pins": pins, "compose_sha256": source_function_sha,
        "domain": {"factor_counts": list(DOMAIN), "signs": [1, -1], "orientations": [1, -1]},
        "distinct_signed_traces": 2*len(DOMAIN), "source_executions": 4*len(DOMAIN),
        "leaves_in_distinct_traces": leaves, "phase_matrix_obligations": obligations,
        "source_trace_sha256": digest.hexdigest(), "matrix_and_nonlinear_sha256": mathematical.hexdigest(),
        "controls": controls(raw), "kernel_trace_equalities": len(names),
        "kernel_trace_factor_counts": list(KERNEL_DOMAIN), "generated_lean_sha256": sha(generated.encode()),
        "formal_source_sha256": sha((PACKAGE/"Dispatcher.lean").read_bytes()),
        "scope": "Bounded Python/source evidence; only separately compiled Lean theorems are universal. No kappa change."
    }
    return report, generated, names


def lean_run(lean, folder, file, output=None):
    env = dict(os.environ, LEAN_PATH=str(folder))
    command = [lean, "-j1", "-s65536", "-DwarningAsError=true", "-DmaxRecDepth=100000",
               "-DmaxHeartbeats=4000000"]
    if output:
        command.extend(["-o", output])
    command.append(file)
    return subprocess.run(command, cwd=folder, env=env, capture_output=True, text=True, timeout=180)


def formal_evidence(lean, generated, trace_names):
    formal = (PACKAGE/"Dispatcher.lean").read_text()
    require(not re.search(r"\b(sorry|admit|axiom|native_decide)\b", formal), "forbidden Lean escape")
    with tempfile.TemporaryDirectory(prefix="dispatcher-lean-") as temp:
        folder = Path(temp)
        (folder/"lean-toolchain").write_text(TOOLCHAIN+"\n")
        version = subprocess.run([lean, "--version"], cwd=folder, capture_output=True, text=True, timeout=30)
        require(version.returncode == 0 and "version 4.28.0," in version.stdout and
                "7e01a1bf5c70" in version.stdout, "use pinned Lean 4.28.0: " + version.stdout + version.stderr)
        (folder/"Dispatcher.lean").write_text(formal)
        result = lean_run(lean, folder, "Dispatcher.lean", "Dispatcher.olean")
        require(result.returncode == 0, "formal proof failed:\n" + result.stdout + result.stderr)
        axioms = audit_axioms(result.stdout, ["DirtyDispatcher."+n for n in FORMAL])
        (folder/"SourceTrace.lean").write_text(generated)
        result = lean_run(lean, folder, "SourceTrace.lean")
        require(result.returncode == 0, "source trace theorem failed:\n" + result.stdout + result.stderr)
        trace_axioms = audit_axioms(result.stdout, trace_names)
        require(all(not a for a in trace_axioms.values()), "trace equality uses an axiom")
        rejected = []
        for name, before, after in (
            ("leaf_reads_target", "op g.factor g.positive (s g.src)", "op g.factor g.positive (s g.dst)"),
            ("leaf_writes_source", "if i = g.dst then", "if i = g.src then"),
            ("source_borrowed_as_scratch", "emit l true x d (d+1)", "emit l true x d x"),
        ):
            require(before in formal, "missing Lean mutation target")
            (folder/"Mutation.lean").write_text(formal.replace(before, after, 1))
            bad = lean_run(lean, folder, "Mutation.lean")
            require(bad.returncode != 0 and "error:" in bad.stdout+bad.stderr, "proof mutation accepted: " + name)
            rejected.append(name)
        altered = generated.replace("⟨0,1,0,true⟩", "⟨0,1,0,false⟩", 1)
        require(altered != generated, "missing trace mutation target")
        (folder/"BadTrace.lean").write_text(altered)
        bad = lean_run(lean, folder, "BadTrace.lean")
        require(bad.returncode != 0 and "error:" in bad.stdout+bad.stderr, "wrong trace equality accepted")
        rejected.append("source_trace_sign")
    return {"status": "PASS_KERNEL_CHECKED_DISPATCHER_INVARIANTS", "lean_version": "4.28.0",
            "lean_commit": "7e01a1bf5c70fc6167d49c345d3bf80596e9a79b",
            "formal_axioms": axioms, "trace_axioms": trace_axioms, "controls": rejected}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--python-only", action="store_true", help="bounded binding only; does not check Lean")
    parser.add_argument("--lean", default="lean", help="Lean 4.28.0 executable or elan proxy")
    parser.add_argument("--write", type=Path, help="write new Python receipt; never overwrite")
    parser.add_argument("--formal-write", type=Path, help="write new Lean receipt; never overwrite")
    args = parser.parse_args()
    require(not (args.python_only and args.formal_write), "formal receipt needs Lean")
    for output in (args.write, args.formal_write):
        require(output is None or not output.exists(), "refuse receipt overwrite")
    report, generated, names = python_evidence()
    if args.write:
        with args.write.open("x") as stream:
            stream.write(json.dumps(report, indent=2, sort_keys=True)+"\n")
    else:
        require(report == json.loads((PACKAGE/"EXPECTED.json").read_text()), "Python receipt mismatch")
    if args.python_only:
        print(f"PASS_DISPATCHER_BINDING_ONLY traces={report['distinct_signed_traces']} Lean=NOT_RUN kappa=unchanged")
        return
    result = formal_evidence(args.lean, generated, names)
    if args.formal_write:
        with args.formal_write.open("x") as stream:
            stream.write(json.dumps(result, indent=2, sort_keys=True)+"\n")
    else:
        require(result == json.loads((PACKAGE/"FORMAL.json").read_text()), "Lean receipt mismatch")
    print(f"PASS_DISPATCHER_INVARIANTS formal={len(FORMAL)} kernel_traces={len(names)} "
          f"python_traces={report['distinct_signed_traces']} controls={len(report['controls'])+len(result['controls'])} kappa=unchanged")


if __name__ == "__main__":
    main()
