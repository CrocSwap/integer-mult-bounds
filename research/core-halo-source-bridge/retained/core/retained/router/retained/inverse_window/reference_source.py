"""Authenticated binding to the retained global Gaussian Reference.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
The executed Reference/interval algorithms belong to Jose Manuel and Mason
Hale, with the original geometry and mathematical lineage credited in README.
"""
import ast
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import sys
from types import ModuleType


def need(condition, message):
    if not condition:
        raise ValueError(message)


REFERENCE = "research/rational-unitary-fft/gaussian_reference.py"
EXACT = "research/rational-unitary-fft/exact.py"
GAUSSIAN = "research/rational-unitary-fft/gaussian.py"
INTERVALS = "research/certified-gaussian-recovery/intervals.py"


def authenticated_inputs(package):
    root = package.parent.parent
    manifest = json.loads((package / "SOURCES.json").read_text())
    raw = {}
    for item in manifest["files"]:
        if item["usage"] == "input":
            content = (root / item["path"]).read_bytes()
            need(sha256(content).hexdigest() == item["sha256"],
                 "changed pinned input: " + item["path"])
            raw[item["path"]] = content
    need(all(path in raw for path in (REFERENCE, EXACT, GAUSSIAN, INTERVALS)),
         "complete source dependency manifest")
    return raw


def _module(name, statements, namespace=None):
    module = ModuleType(name)
    if namespace:
        module.__dict__.update(namespace)
    sys.modules[name] = module
    tree = ast.Module(body=statements, type_ignores=[])
    exec(compile(ast.fix_missing_locations(tree), "<authenticated source adapter>",
                 "exec", optimize=0), module.__dict__)
    return module


def reference_class(raw):
    """Rebind only imports, leaving every executed numerical body unchanged.

    gaussian.py also imports a full circuit compiler unused by Reference's
    explicit constructor/entry interface. Extract exactly its three named
    helpers; no numerical source expression or loop is changed. for_cap is
    outside this adapter's domain and is not invoked.
    """
    exact_tree = ast.parse(raw[EXACT])
    exact = _module("_shrinking_source_exact", exact_tree.body)
    gaussian_tree = ast.parse(raw[GAUSSIAN])
    wanted = {"rational", "load_intervals"}
    helpers = [node for node in gaussian_tree.body
               if isinstance(node, ast.FunctionDef) and node.name in wanted]
    need({node.name for node in helpers} == wanted, "retained Gaussian helper shape")
    gaussian = _module("_shrinking_source_gaussian", helpers,
                       {"Q": Q, "need": need, "sha256": sha256, "sys": sys,
                        "ModuleType": ModuleType})
    tree = ast.parse(raw[REFERENCE])
    body = [node for node in tree.body if not (
        isinstance(node, ast.ImportFrom) and node.module in ("exact", "gaussian"))]
    reference = _module("_shrinking_source_reference", body,
                        {"Mat": exact.Mat, "ceil_log2": exact.ceil_log2,
                         "need": exact.need, "INTERVALS": INTERVALS,
                         "load_intervals": gaussian.load_intervals,
                         "rational": gaussian.rational})
    return reference.Reference


def make_reference(raw, parameters):
    return reference_class(raw)(raw, *parameters)


def source_entry(reference, row, column):
    return Q(int(row == column)) - reference.entry("narrow", row, column).value


def source_receipt(reference):
    """Diagnostic setup inventory; not an asserted exact Python heap count."""
    values = [entry.value for entry in reference.entries.values()]
    weight_values = [value for receipt in reference.weights.values()
                     for value in receipt.values() if type(value) is Q]
    height = max([1] + [max(abs(x.numerator).bit_length(), x.denominator.bit_length())
                        for x in values + weight_values])
    return dict(reference_sha256=reference.description_hash,
                parameters=list(reference.spec.__dict__.values()),
                stored_entries=len(reference.entries), stored_weights=len(reference.weights),
                stored_kernels=len(reference.kernel), maximum_rational_height=height,
                weight_precision=reference.weight_precision,
                kernel_error_bits=reference.kernel_error_bits)


def clear_reference(reference):
    """Release setup caches; physical erasure is separately charged in proof.

    This does not claim secure zeroization of Python immutable integers.
    """
    reference.entries.clear(); reference.weights.clear(); reference.kernel.clear()
    for name in ("pi_interval", "root_of_unity"):
        function = getattr(reference.exp.oracle, name, None)
        if function is not None and hasattr(function, "cache_clear"):
            function.cache_clear()
