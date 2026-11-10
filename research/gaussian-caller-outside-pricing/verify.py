#!/usr/bin/env python3
"""The Gaussian caller outside the selected pricing assembly has no bit_saving input.

The selected PR6030 verifier loads research/p104-productive-controller/caller.py
and calls physical(word, local) before pricing.run. That function checks the
idle Gaussian axes and the Gaussian pair. Its parameters are word and local.
Neither it, nor the controller object the verifier labels the physical caller,
carries bit_saving. It therefore cannot consume the recorded PR5679 component.

This verifier does not execute physical, the pricing assembly, or the ledger.
"""
from fractions import Fraction
import ast
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CALLER = ROOT / "research/p104-productive-controller/caller.py"
CONTROLLER = ROOT / "research/p104-productive-controller/CONTROLLER.json"
ASSEMBLY_VERIFY = ROOT / "research/p104-helper470-twin-rung-removal/verify.py"
PRICING = ROOT / "research/p104-helper470-twin-rung-removal/pricing.py"
COMPONENT = ROOT / "research/g20-helper-split/ORDINARY-RESULT.json"
SELECTED = ROOT / "certificates/selected-result.json"
TASK = HERE / "TASK.json"
C_VALUE = Fraction(3507410738409, 1000000000000000)
CALLER_PY = (
    "research/bit-carrier-owner-admission/caller.py",
    "research/bit-compact-carrier-retirement/provider/caller.py",
    "research/bit-stage-mixedwidth-packing/provider/caller.py",
    "research/crt-repair-query-budget/caller.py",
    "research/literal-complete-row-parking-caller/caller.py",
    "research/native-involutive-dual/caller.py",
    "research/p104-caller-independent-audit/capsule/outputs/p104-contact-reassessment-20261025/sources/predecessor/caller.py",
    "research/p104-contact-independent-audit/capsule/outputs/p104-contact-reassessment-20261025/sources/predecessor/caller.py",
    "research/p104-coupled-helper-bases/caller.py",
    "research/p104-cut-stability/whole-caller/inputs/caller.py",
    "research/p104-productive-controller/caller.py",
    "research/p104-retained-operand-independent-audit/caller.py",
    "research/physical-boundary-rhs-caller/caller.py",
    "research/rank7-boolean-scalar-caller/caller.py",
    "research/selected-complex-layer-closure/caller.py",
)
GAUSSIAN_MARKERS = (
    "Multiply the Gaussian pair twice with exact real and imaginary parts.",
    "All idle Gaussian axes",
)
GAUSSIAN_CALLER_PY = (
    "research/native-involutive-dual/caller.py",
    "research/p104-caller-independent-audit/capsule/outputs/p104-contact-reassessment-20261025/sources/predecessor/caller.py",
    "research/p104-contact-independent-audit/capsule/outputs/p104-contact-reassessment-20261025/sources/predecessor/caller.py",
    "research/p104-coupled-helper-bases/caller.py",
    "research/p104-cut-stability/whole-caller/inputs/caller.py",
    "research/p104-productive-controller/caller.py",
    "research/physical-boundary-rhs-caller/caller.py",
)


def need(ok, message):
    if not ok:
        raise SystemExit("FAIL: " + message)


def contains_bit_saving(text):
    return "bit_saving" in text


def ordered(text, marks):
    position = 0
    for mark in marks:
        found = text.find(mark, position)
        if found < 0:
            return False
        position = found + len(mark)
    return True


def git_text(revision, path):
    raw = subprocess.check_output(
        ["git", "-C", str(ROOT), "show", revision + ":" + path],
        stderr=subprocess.DEVNULL,
    )
    return raw.decode("utf-8")


def tree_paths(revision):
    raw = subprocess.check_output(
        ["git", "-C", str(ROOT), "ls-tree", "-r", "--name-only", revision],
        stderr=subprocess.DEVNULL,
    )
    return raw.decode("utf-8").splitlines()


def argument_names(function):
    names = [item.arg for item in function.args.args]
    names += [item.arg for item in function.args.posonlyargs]
    names += [item.arg for item in function.args.kwonlyargs]
    if function.args.vararg is not None:
        names.append(function.args.vararg.arg)
    if function.args.kwarg is not None:
        names.append(function.args.kwarg.arg)
    return names


def walk_keys(value, found):
    if isinstance(value, dict):
        for key, item in value.items():
            found.append(str(key))
            walk_keys(item, found)
    elif isinstance(value, list):
        for item in value:
            walk_keys(item, found)


def main():
    task = json.loads(TASK.read_text(encoding="utf-8"))
    base = task["base_commit"]
    need(base == "7c49fe32c55de02c2c873655c804b16e4c3fef0a", "pinned base commit")
    need(task["scope_status"] == "refined", "scope stays the caller question")

    listed = tuple(path for path in tree_paths(base) if path.rsplit("/", 1)[-1] == "caller.py")
    need(listed == CALLER_PY, "caller.py census is the complete base-commit listing")
    hits = []
    gaussian_files = []
    for path in listed:
        text = git_text(base, path)
        if contains_bit_saving(text):
            hits.append(path)
        if "Gaussian" in text or "gaussian" in text:
            gaussian_files.append(path)
    need(hits == [], "no caller.py blob at the base commit contains bit_saving")
    need(tuple(gaussian_files) == GAUSSIAN_CALLER_PY,
         "Gaussian caller.py census matches the pinned list")

    caller_text = CALLER.read_text(encoding="utf-8")
    need(caller_text == git_text(base, "research/p104-productive-controller/caller.py"),
         "working caller.py matches the base blob")
    need(not contains_bit_saving(caller_text), "named caller source has no bit_saving")
    need(contains_bit_saving("def physical(word, local, bit_saving):"),
         "scanner control sees an added bit_saving parameter")
    for marker in GAUSSIAN_MARKERS:
        need(caller_text.count(marker) == 1, "Gaussian marker once: " + marker)

    tree = ast.parse(caller_text)
    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
    need([node.name for node in functions] == ["replay", "construct", "physical", "controls"],
         "caller.py function list")
    all_args = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            all_args.extend(argument_names(node))
    need("bit_saving" not in all_args, "no function argument is named bit_saving")
    physical = functions[2]
    need(argument_names(physical) == ["word", "local"], "physical parameters")
    need(physical.args.defaults == [] and physical.args.kw_defaults == [],
         "physical parameters have no hidden default")
    returns = [stmt for stmt in physical.body if isinstance(stmt, ast.Return)]
    need(len(returns) == 1 and isinstance(returns[0].value, ast.Dict), "one dict return")
    return_keys = []
    for key in returns[0].value.keys:
        need(isinstance(key, ast.Constant) and isinstance(key.value, str), "return keys are strings")
        return_keys.append(key.value)
    need("bit_saving" not in return_keys, "physical's return does not carry bit_saving")
    need("whole_idle_jobs" in return_keys, "physical reports the idle Gaussian jobs")

    controller_raw = CONTROLLER.read_text(encoding="utf-8")
    controller = json.loads(controller_raw)
    keys = []
    walk_keys(controller, keys)
    need("bit_saving" not in keys, "CONTROLLER.json has no bit_saving field")
    need(str(C_VALUE.numerator) not in controller_raw, "recorded controller does not contain C")

    component = json.loads(COMPONENT.read_text(encoding="utf-8"))
    admitted = Fraction(component["admitted"])
    need(admitted == C_VALUE, "recorded PR5679 component")
    need(component["whole_kappa"] is None, "component is not a whole kappa")
    need(str(C_VALUE.numerator) not in caller_text, "caller source does not contain C")

    assembly_verify = ASSEMBLY_VERIFY.read_text(encoding="utf-8")
    call = (
        "C = load(root / 'research/p104-productive-controller/caller.py', 'base_caller')",
        "caller = C.construct()",
        "need(caller == read(root / 'research/p104-productive-controller/CONTROLLER.json'), 'Exact physical caller')",
        "physical = C.physical(caller, word)",
        "P = load(HERE / 'pricing.py', 'edit_price')",
        "price = P.run(local, native, caller, physical)",
    )
    need(ordered(assembly_verify, call), "selected verifier calls physical before pricing.run")
    swapped = (
        "price = P.run(local, native, caller, physical)\n"
        "physical = C.physical(caller, word)\n"
    )
    need(not ordered(swapped, ("physical = C.physical(caller, word)", "price = P.run(local, native, caller, physical)")),
         "order control rejects pricing before the caller")

    pricing = PRICING.read_text(encoding="utf-8")
    need(pricing.count("def run(local,native,word,physical):") == 1, "pricing.run parameters")
    need("bit_saving" not in pricing.split("def run", 1)[0], "pricing has no bit_saving before run")
    need(pricing.count("'bit_saving':admitted") == 1, "assembly assigns bit_saving from admitted")
    need(pricing.count("atom > ordinary > admitted > TESTED") == 1, "assembly stock gate")
    need("def physical" not in pricing, "pricing.py does not define physical")
    run_args = ast.parse(pricing)
    run = next(node for node in run_args.body if isinstance(node, ast.FunctionDef) and node.name == "run")
    need(argument_names(run) == ["local", "native", "word", "physical"],
         "pricing.run does not take bit_saving")

    selected = json.loads(SELECTED.read_text(encoding="utf-8"))
    need(selected["kappa"] == "781451/250000000", "selected frontier unchanged")

    receipt = {
        "status": "PASS_GAUSSIAN_CALLER_OUTSIDE_PRICING",
        "caller": "research/p104-productive-controller/caller.py:physical",
        "parameters": ["word", "local"],
        "bit_saving_input": None,
        "named_caller_consumes_C": False,
        "component": str(admitted),
        "whole_kappa": None,
        "selected_kappa": selected["kappa"],
        "caller_py_files": len(listed),
        "caller_py_bit_saving_hits": hits,
        "gaussian_caller_py_files": gaussian_files,
        "physical_return_keys": return_keys,
        "controller_has_bit_saving": False,
        "assembly_bit_saving_assignment": "'bit_saving':admitted",
        "assembly_call_after_physical": True,
        "physical_executed": False,
    }
    print("PASS_GAUSSIAN_CALLER_OUTSIDE_PRICING")
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
