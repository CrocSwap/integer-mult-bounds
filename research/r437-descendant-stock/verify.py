#!/usr/bin/env python3
"""Source-bound stock proof checks using an explicit integer Count adapter.

Mihir Srivastava, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import ast
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
from types import SimpleNamespace
from stock import (DIMENSION, FAMILIES, MAX_RANK, STOCK_MULTIPLE, Node,
                   certify_path, depth, require, row_factor, stock_divisor)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FRESH = "research/selected-bit-physical-caller/inputs/pr2753/predecessor/fresh_rows.py"
MACHINE = "research/selected-bit-physical-caller/macro_machine.py"
NUMERICAL = "research/r437-carrier-integration/numerical.py"
CARDINALITY = "research/selected-bit-physical-caller/inputs/pr2753/predecessor/vendor/cardinality.py"


def authenticate():
    pins = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    checked = {}
    for row in pins["files"]:
        if row["usage"] == "input":
            data = (ROOT / row["path"]).read_bytes()
            require(sha256(data).hexdigest() == row["sha256"], "source hash: " + row["path"])
            checked[row["path"]] = row["sha256"]
    return checked


class IntegerCount:
    """Mathematical interface used by the unchanged quotient and next guard."""
    def __init__(self, value):
        self.value = value.value if isinstance(value, IntegerCount) else value

    def divide_small(self, divisor):
        self.value, remainder = divmod(self.value, divisor)
        return remainder

    def zero(self):
        return self.value == 0

    def close(self):
        pass


def positive(value):
    require(isinstance(value, IntegerCount) and value.value > 0, "positive Count")


def integer_ring(q, w):
    """Integer adapter for the retained radix_power Word interface."""
    arena = SimpleNamespace(literal=IntegerCount, copy=IntegerCount,
                            free_many=lambda *words: None)
    raw = SimpleNamespace(compare=lambda a, b: (a.value > b.value) - (a.value < b.value),
                          divmod=lambda a, b: tuple(IntegerCount(v) for v in divmod(a.value, b.value)))
    return SimpleNamespace(arena=arena, raw=raw, modulus=IntegerCount(q**w), one=IntegerCount(1))


def source_guard():
    tree = ast.parse((ROOT / FRESH).read_text(encoding="utf-8"))
    quotient = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "quotient")
    scope = {"Count": IntegerCount, "positive": positive, "need": require}
    cardinality = ast.parse((ROOT / CARDINALITY).read_text(encoding="utf-8"))
    radix = next(n for n in cardinality.body if isinstance(n, ast.FunctionDef) and n.name == "radix_power")
    exec(compile(ast.Module(body=[radix], type_ignores=[]), CARDINALITY, "exec"), scope)
    for q, w in [(3, 1), (3, 2), (5, 3)]:
        require(sum(1 for _ in scope["radix_power"](integer_ring(q, w), q)) == w,
                "literal radix_power iteration count")
    exec(compile(ast.Module(body=[quotient], type_ignores=[]), FRESH, "exec"), scope)
    machine = ast.parse((ROOT / MACHINE).read_text(encoding="utf-8"))
    cls = next(n for n in machine.body if isinstance(n, ast.ClassDef) and n.name == "Machine")
    method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "node")
    start = next(i for i, n in enumerate(method.body) if isinstance(n, ast.Assign)
                 and isinstance(n.targets[0], ast.Name) and n.targets[0].id == "unused")
    block = method.body[start:start + 4]
    require([type(n).__name__ for n in block] == ["Assign", "Expr", "Assign", "Try"],
            "literal quotient/save/stock/guard block")
    scope["fresh_rows"] = SimpleNamespace(quotient=scope["quotient"])
    code = compile(ast.Module(body=block, type_ignores=[]), MACHINE, "exec")

    def check(rows, q, w):
        order = 1
        for i in range(64):
            order *= q**64 - q**i
        counts = {"rows": IntegerCount(rows)}
        runtime = SimpleNamespace(context=SimpleNamespace(codes=SimpleNamespace(size=order),
            dimension=64, ring=integer_ring(q, w), q=q),
            topology=SimpleNamespace(families=FAMILIES),
            binding=SimpleNamespace(stock_multiple=STOCK_MULTIPLE),
            count=lambda name: counts[name],
            save_count=lambda value, name: counts.__setitem__(name, value))
        exec(code, dict(scope, self=runtime))
        return counts["unused"].value
    return check


def run():
    pins, guard = authenticate(), source_guard()
    predecessor = {"__name__": "pinned_numerical", "__file__": str(ROOT / NUMERICAL)}
    exec(compile((ROOT / NUMERICAL).read_bytes(), NUMERICAL, "exec"), predecessor)
    require((predecessor["W"], predecessor["M"]) == (FAMILIES, DIMENSION), "source constants")
    require(predecessor["STOCK_MULTIPLIER"] == FAMILIES * STOCK_MULTIPLE, "K = 9475 A")
    require(max(predecessor["PROFILE_D"]) == MAX_RANK, "declared maximum rank")
    require("cutoff, stock_multiple, child_mode = 64, 9475, 0" in
            (ROOT / "research/selected-bit-physical-caller/macro_binding.py").read_text(),
            "literal binding stock factor")
    require("replicas, pairs, ports, families, stride = 32, 4, 111, 28416, 888" in
            (ROOT / "research/r437-pooled-native-interface/replica_catalogue.py").read_text(),
            "literal pooled family count")
    transitions = 0
    for n in range(1, 1025):
        require(depth(n) == predecessor["depth"](n), "independent depth recurrence")
        if n >= 64:
            for c in range(1, 42 * (n // 64) + 1):
                require(depth(c) <= depth(n) - 1, "rank-ceiling depth monotonicity")
                transitions += 1
    abstract_cases = 0
    for a in range(1, 6):
        for s in range(1, 5):
            for d in range(5):
                minimum = s * a**d if d else 1
                for rows in range(1, 2 * minimum + 2):
                    value, valid = rows, True
                    for _ in range(d):
                        value, remainder = divmod(value, a)
                        if remainder or value <= 0 or value % s:
                            valid = False
                            break
                    require(valid == (rows % minimum == 0), "sharp abstract stock characterization")
                    abstract_cases += 1
    rejected = []
    def reject(name, callback):
        try:
            callback()
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("failed rejection control: " + name)
    fixtures, literal_nodes = [], 0
    for q, w, n in [(3, 1, 64), (3, 2, 128), (5, 2, 512), (3, 2, 2048)]:
        a, d = row_factor(q, w), depth(n)
        root = Node(n, stock_divisor(n, q, w), q, w)
        nodes = [root]
        while nodes[-1].width >= 64:
            p = nodes[-1]
            actual = guard(p.rows, q, w)
            require(actual == p.rows // a, "source quotient matches independent A")
            nodes.append(Node(42 * (p.width // 64), actual, q, w))
            literal_nodes += 1
        result = certify_path(root, nodes)
        require(len(nodes) - 1 == d and nodes[-1].rows == STOCK_MULTIPLE, "maximal path terminal stock")
        old_rows = predecessor["stock_unit"](q, w)**d
        require(old_rows == root.rows * STOCK_MULTIPLE**(d - 1), "old/new ratio")
        old_nodes = [replace(v, rows=v.rows * STOCK_MULTIPLE**(d - 1)) for v in nodes]
        certify_path(old_nodes[0], old_nodes)
        if d > 1:
            reject(f"old_guard_rejects_new_stock_n{n}",
                   lambda r=root: predecessor["check_stock_rows"](r.rows, r.width, r.q, r.w))
        fixtures.append({"q": q, "w": w, "widths": [v.width for v in nodes],
            "root_stock_bits": root.rows.bit_length(),
            "root_stock_sha256": sha256(root.rows.to_bytes((root.rows.bit_length()+7)//8, "big")).hexdigest(),
            "old_to_new_factor": str(STOCK_MULTIPLE**(d - 1)), "certificate": result})
    a = row_factor(3, 2)
    root = Node(128, stock_divisor(128, 3, 2), 3, 2)
    child = Node(84, root.rows // a, 3, 2)
    leaf = Node(42, child.rows // a, 3, 2)
    certify_path(root, [root, child, leaf])
    forged = replace(child, rows=2 * child.rows)
    require(forged.rows % stock_divisor(84, 3, 2) == 0, "forgery passes local test")
    reject("locally_valid_but_unrelated_descendant", lambda: certify_path(root, [root, forged]))
    reject("changed_precision", lambda: certify_path(root, [root, replace(child, w=1)]))
    reject("changed_field", lambda: certify_path(root, [root, replace(child, q=5)]))
    reject("missing_root", lambda: certify_path(root, [child]))
    reject("wrong_child_width", lambda: certify_path(root, [root, replace(child, width=85)]))
    reject("transition_below_cutoff", lambda: certify_path(root, [root, child, leaf, leaf]))
    reject("noninteger_rows", lambda: certify_path(replace(root, rows=1.0), [root]))
    reject("empty_path", lambda: certify_path(root, []))
    reject("lost_9475_factor", lambda: guard(a, 3, 2))
    reject("inexact_family_factor", lambda: guard(root.rows + 1, 3, 2))
    reject("empty_stock", lambda: guard(0, 3, 2))
    reject("lost_high_lift_factor", lambda: guard(row_factor(3, 1)*STOCK_MULTIPLE, 3, 2))
    reject("undivided_child_rows", lambda: certify_path(root, [root, replace(child, rows=root.rows)]))
    short = STOCK_MULTIPLE * a
    require(guard(short, 3, 2) == STOCK_MULTIPLE, "depth-one positive control")
    reject("one_missing_recursion_factor", lambda: guard(guard(short, 3, 2), 3, 2))
    require(stock_divisor(63, 3, 2) == 1, "leaf has no internal guard")
    return {"status": "PASS_R437_DESCENDANT_STOCK", "source_sha256": pins,
        "depth_widths": 1024, "bounded_child_transitions": transitions,
        "abstract_guard_cases": abstract_cases, "literal_internal_nodes": literal_nodes,
        "fixtures": fixtures, "rejected_controls": rejected,
        "scope": "Sharp row-guard arithmetic; integer Count adapter, no tape/payload replay, supplier admission or new kappa"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="explicit receipt regeneration")
    args = parser.parse_args()
    result, receipt = run(), HERE / "RESULT.json"
    if args.write:
        receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    else:
        require(json.loads(receipt.read_text(encoding="utf-8")) == result, "complete deterministic receipt")
    print(result["status"], "transitions=" + str(result["bounded_child_transitions"]),
          "abstract=" + str(result["abstract_guard_cases"]),
          "literal_nodes=" + str(result["literal_internal_nodes"]),
          "controls=" + str(len(result["rejected_controls"])))
