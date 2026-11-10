"""Pinned public Reference and authenticated physical word cohort.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
The Reference import adapter follows the separately reviewed halo package's
source adapter: only imports are rebound; numerical bodies are unchanged.
"""
import ast
from contextlib import contextmanager
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
from types import ModuleType

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
REFERENCE = "research/rational-unitary-fft/gaussian_reference.py"
EXACT = "research/rational-unitary-fft/exact.py"
GAUSSIAN = "research/rational-unitary-fft/gaussian.py"
INTERVALS = "research/certified-gaussian-recovery/intervals.py"
PHYSICAL = ROOT / "research/physical-gaussian-core"


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def authenticated_inputs():
    raw = {}
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    for item in manifest["files"]:
        if item["usage"] == "input":
            path = ROOT / item["path"]
            need(path.is_file() and not path.is_symlink(), "regular run source: " + item["path"])
            content = path.read_bytes()
            need(sha256(content).hexdigest() == item["sha256"], "pinned run source: " + item["path"])
            raw[item["path"]] = content
    need(all(p in raw for p in (REFERENCE, EXACT, GAUSSIAN, INTERVALS)), "complete Reference input set")
    return raw


def module(name, statements, namespace=None):
    result = ModuleType(name)
    if namespace:
        result.__dict__.update(namespace)
    sys.modules[name] = result
    tree = ast.Module(body=statements, type_ignores=[])
    exec(compile(ast.fix_missing_locations(tree), "<authenticated fine-gap adapter>",
                 "exec", optimize=0), result.__dict__)
    return result


def make_reference(raw, parameters):
    exact = module("_fine_gap_source_exact", ast.parse(raw[EXACT]).body)
    helpers = [node for node in ast.parse(raw[GAUSSIAN]).body
               if isinstance(node, ast.FunctionDef) and node.name in {"rational", "load_intervals"}]
    need({node.name for node in helpers} == {"rational", "load_intervals"}, "unchanged Reference helper interface")
    gaussian = module("_fine_gap_source_helpers", helpers,
                      {"Q": Q, "need": need, "sha256": sha256, "sys": sys, "ModuleType": ModuleType})
    body = [node for node in ast.parse(raw[REFERENCE]).body if not (
        isinstance(node, ast.ImportFrom) and node.module in ("exact", "gaussian"))]
    reference = module("_fine_gap_source_reference", body,
                       {"Mat": exact.Mat, "ceil_log2": exact.ceil_log2, "need": exact.need,
                        "INTERVALS": INTERVALS, "load_intervals": gaussian.load_intervals,
                        "rational": gaussian.rational})
    return reference.Reference(raw, *parameters)


@contextmanager
def physical_runtime():
    """Call the unmodified predecessor's complete nested-source authenticator."""
    need("gaussian_sources" not in sys.modules, "cold physical Gaussian namespace")
    old_path = sys.path[:]
    sys.path[:0] = [str(PHYSICAL), str(PACKAGE)]
    spec = importlib.util.spec_from_file_location("gaussian_sources", PHYSICAL / "gaussian_sources.py")
    source = importlib.util.module_from_spec(spec)
    sys.modules["gaussian_sources"] = source
    try:
        spec.loader.exec_module(source)
        with source.opened() as state:
            yield state
    finally:
        sys.path[:] = old_path
