#!/usr/bin/env python3
"""Source-bound complete producer/leaf/XOR fixed-workspace certificates.

Krzysztof Wójt with substantial OpenAI Codex assistance; Apache-2.0.
The complete payload fixtures and their independent oracles are JoyboyBrian's.
"""

import argparse
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(value, message):
    if not value:
        raise ValueError(message)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def authenticate():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    rows = [row for row in manifest["files"] if row["usage"] == "input"]
    for row in rows:
        need(hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest() == row["sha256"],
             "source bytes " + row["path"])
    return len(rows)


def physical(tape):
    return tape.physical if hasattr(tape, "physical") else tape


def bind_bound(result, parameters):
    bounds = load("r437_workspace_bounds", HERE / "bounds.py")
    bound = bounds.workspace_bound(**parameters)
    observed = result["workspace"]
    need(observed["roles"] == bound["roles"], "source-derived role reserve")
    need(observed["largest"] <= bound["body_bound"] + 2 and
         observed["backing"] <= bound["fresh_retained_cells"],
         "source-derived retained backing reserve")
    result["bound_parameters"] = parameters
    result["uniform_bound"] = bound
    result["pooling_surcharge_bound"] = bounds.pooling_surcharge(
        observed["roles"], observed["prefixes"], observed["acquisitions"],
        observed["callback_closes"])


def omit_retirement(module):
    """A controlled in-memory defect in exactly one predecessor cleanup site."""
    source = module._source
    tree = ast.parse(Path(source.__file__).read_text(), filename=source.__file__)
    changed = 0

    class Omit(ast.NodeTransformer):
        def visit_Expr(self, node):
            nonlocal changed
            call = node.value
            if (isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute)
                    and isinstance(call.func.value, ast.Name)
                    and call.func.value.id == "left" and call.func.attr == "clear"):
                changed += 1
                return None
            return self.generic_visit(node)

    tree = Omit().visit(tree)
    need(changed == 1, "one deliberately omitted left-fibre retirement")
    scope = dict(source.__dict__)
    exec(compile(ast.fix_missing_locations(tree), source.__file__, "exec"), scope)
    source.run = scope["run"]


def generic(mode="normal"):
    """Retain the complete source fixture, guards and independent payload oracle."""
    path = ROOT / "research/r437-streaming-directory/verify.py"
    tree = ast.parse(path.read_text(), filename=str(path))
    changes = 0
    observations = []

    def adapter():
        module = load("r437_pooled_consumer", HERE / "pooled.py")
        if mode == "omitted-retirement":
            omit_retirement(module)

        def run(*args, **kwargs):
            evidence = load("r437_workspace_evidence", HERE / "evidence.py")
            workspace = module.Workspace(args[3].q, capacity=1 if mode == "capacity" else None)
            audit = evidence.Audit(workspace.pool)
            workspace.observe = audit.observe
            if mode == "raw-constructor":
                workspace.tape = module.Tape
            elif mode == "dirty-reuse":
                def dirty(pool):
                    audit.observe(pool)
                    pool.tapes[0].write(0)
                workspace.observe = dirty
            with audit.installed():
                result = module.run(*args, **kwargs, workspace=workspace)
            observations.append(audit.result())
            return result

        return SimpleNamespace(visit=module.visit, run=run)

    class Bind(ast.NodeTransformer):
        def visit_Assign(self, node):
            nonlocal changes
            if any(isinstance(target, ast.Name) and target.id == "streaming"
                   for target in node.targets):
                need(isinstance(node.value, ast.Call) and
                     isinstance(node.value.func, ast.Name) and node.value.func.id == "module",
                     "pinned fixture adapter load")
                changes += 1
                node.value = ast.Call(func=ast.Name(id="ADAPTER", ctx=ast.Load()), args=[], keywords=[])
            return self.generic_visit(node)

    tree = Bind().visit(tree)
    ast.fix_missing_locations(tree)
    need(changes == 1, "exact generic fixture adapter substitution")
    scope = {"__file__": str(path), "__name__": "r437_workspace_generic", "ADAPTER": adapter}
    exec(compile(tree, str(path), "exec"), scope)
    result = scope["run"]()
    need(len(observations) == 1 and observations[0]["prefixes"] == 243,
         "all complete high-cube consumer boundaries")
    final = observations[0]
    need(final["backing_constant_after_first_prefix"], "fixed fixture backing across all 243 prefixes")
    result["workspace"] = final
    bind_bound(result, dict(q=3, fibre=81,
                            prefix_body=result["producer"]["max_current_prefix_bytes"],
                            program_body=0, callback_depth=0, index_bits=8, residue_bits=5))
    result["status"] = "PASS_R437_STREAMED_LEAF_WORKSPACE_GENERIC"
    result["scope"] = "Complete q3/w2/d2 high cube with the same physical scratch pool; no production GL64 replay."
    return result


def actual():
    """The #4981/#5055 actual SOURCE87 calibration, with explicit lease observers."""
    path = ROOT / "research/r437-prefix-consumer-fusion/verify.py"
    tree = ast.parse(path.read_text(), filename=str(path))
    edits = [0, 0, 0, 0, 0]
    observations = []
    parameters = []

    def capture_bound(volume, prefixes, program, child, ia, ra):
        parameters.append(dict(q=3, fibre=volume,
                               prefix_body=max(len(raw) - 1 for raw in prefixes),
                               program_body=len(physical(program).cells) - 1,
                               callback_depth=child.depth.inspect(),
                               index_bits=ia.bits, residue_bits=ra.bits))

    def configure(adapter):
        original = adapter.run

        def run(*args, **kwargs):
            evidence = load("r437_workspace_evidence_actual", HERE / "evidence.py")
            workspace = adapter.body.Workspace(args[3].q)
            audit = evidence.Audit(workspace.pool)
            workspace.observe = audit.observe
            with audit.installed():
                result = original(*args, **kwargs, workspace=workspace)
            observations.append(audit.result())
            return result
        adapter.run = run

    class Bind(ast.NodeTransformer):
        def visit_Assign(self, node):
            node = self.generic_visit(node)
            if any(isinstance(target, ast.Name) and target.id == "result"
                   for target in node.targets) and isinstance(node.value, ast.Call) and (
                       isinstance(node.value.func, ast.Name) and node.value.func.id == "dict"):
                edits[4] += 1
                capture = ast.parse("CAPTURE_BOUND(volume, prefix_bytes, copied, child, ia, ra)").body[0]
                return [node, capture]
            return node

        def visit_BinOp(self, node):
            if (isinstance(node.op, ast.Div) and isinstance(node.left, ast.Name)
                    and node.left.id == "HERE" and isinstance(node.right, ast.Constant)
                    and node.right.value == "adapter.py"):
                edits[0] += 1
                return ast.copy_location(ast.BinOp(ast.Name("CURRENT", ast.Load()), ast.Div(),
                                                   ast.Constant("actual_bridge.py")), node)
            return self.generic_visit(node)

        def visit_FunctionDef(self, node):
            if node.name == "run":
                start = next(i for i, value in enumerate(node.body) if isinstance(value, ast.With))
                block = node.body[start].body
                begin = next(i for i, value in enumerate(block) if isinstance(value, ast.Assign)
                             and any(isinstance(t, ast.Name) and t.id == "bad_count" for t in value.targets))
                end = next(i for i, value in enumerate(block) if isinstance(value, ast.Assign)
                           and any(isinstance(t, ast.Name) and t.id == "dirty" for t in value.targets))
                del block[begin:end]
                edits[1] += 1
            return self.generic_visit(node)

        def visit_Expr(self, node):
            node = self.generic_visit(node)
            if (isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute)
                    and node.value.func.attr == "exec_module" and len(node.value.args) == 1
                    and isinstance(node.value.args[0], ast.Name) and node.value.args[0].id == "adapter"):
                edits[2] += 1
                return [node, ast.Expr(ast.Call(ast.Name("CONFIGURE", ast.Load()),
                                                [ast.Name("adapter", ast.Load())], []))]
            return node

        def visit_Attribute(self, node):
            node = self.generic_visit(node)
            if node.attr == "cells":
                edits[3] += 1
                node.value = ast.Call(ast.Name("PHYSICAL", ast.Load()), [node.value], [])
            return node

    tree = Bind().visit(tree)
    ast.fix_missing_locations(tree)
    need(edits == [2, 1, 1, 28, 1], "exact actual64 adapter/guard/observer substitutions")
    scope = {"__file__": str(path), "__name__": "r437_workspace_actual64",
             "CURRENT": HERE, "CONFIGURE": configure, "PHYSICAL": physical,
             "CAPTURE_BOUND": capture_bound}
    exec(compile(tree, str(path), "exec"), scope)
    result = scope["run"]()
    need(len(observations) == 1 and observations[0]["prefixes"] == 2,
         "actual64 both complete prefixes use identical pool")
    final = observations[0]
    result["workspace"] = final
    need(len(parameters) == 1, "one source-parameter observation before cleanup")
    bind_bound(result, parameters[0])
    result["fixture_edits"] = edits
    result["status"] = "PASS_R437_STREAMED_LEAF_WORKSPACE_ACTUAL64"
    result["scope"] = "Two actual SOURCE87 prefixes and full computed leaf/XOR payload; not full high-domain execution or admission."
    return result


def main():
    parser = argparse.ArgumentParser()
    failures = {
        "capacity": "fixed scratch role inventory exhausted",
        "omitted-retirement": "completed macro closes all scratch leases",
        "raw-constructor": "physical Tape allocation inside a completed macro",
        "dirty-reuse": "empty scratch role before reuse",
    }
    parser.add_argument("--mode", choices=("all", "generic", "actual", *failures), default="all")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    inputs = authenticate()
    if args.mode in failures:
        try:
            generic(args.mode)
        except ValueError as error:
            need(str(error) == failures[args.mode], "exact workspace rejection reason: " + str(error))
            result = dict(control=args.mode, rejected=True, reason=str(error))
        else:
            raise ValueError("deliberate workspace defect accepted: " + args.mode)
    elif args.mode == "generic":
        result = generic()
    elif args.mode == "actual":
        result = actual()
    else:
        command = [sys.executable, "-I", "-W", "error", "-B"]
        if sys.flags.optimize:
            command.append("-O")
        cases = {}
        for mode in ("generic", "actual", *failures):
            completed = subprocess.run(command + [str(HERE / "verify.py"), "--mode", mode],
                                       capture_output=True, text=True, timeout=420)
            need(completed.returncode == 0, mode + " child verifier failed:\n" + completed.stderr)
            cases[mode] = json.loads(completed.stdout)
        result = dict(status="PASS_R437_STREAMED_LEAF_WORKSPACE", authenticated_inputs=inputs,
                      generic=cases.pop("generic"), actual64=cases.pop("actual"),
                      workspace_controls=list(cases.values()), numerical_admitted=False,
                      selected_frontier_changed=False,
                      scope="Uniform successful leaf/XOR workspace refinement, with separate complete small-cube and two-prefix actual64 evidence.")
        encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
        receipt = HERE / "RESULT.json"
        if args.write:
            receipt.write_text(encoded)
        else:
            need(receipt.read_text() == encoded, "typed deterministic complete workspace receipt")
        print(result["status"])
        return
    need(not args.write, "--write requires the complete all-mode receipt")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
