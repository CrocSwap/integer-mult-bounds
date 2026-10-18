"""Authenticate source bytes, then compile the named literal functions."""

import ast
import hashlib
import json
import sys
import types
from pathlib import Path

from traffic import require

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
CORE = (
    "words",
    "records",
    "stream",
    "cardinality",
    "counts",
    "cardinal_counts",
    "bitstream",
)
PREFIX = "research/linear-sign-total-traffic/sources/"
ROUTES = "research/selected-route-live-volume/vendor/routes.py"
KERNELS = "research/selected-bit-fast-primitives/kernels.py"


def authenticated():
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    rows = [row for row in manifest["files"] if row["usage"] == "input"]
    require(0 < len(rows) <= 20, "bounded input inventory")
    data = {}
    for row in rows:
        path = row["path"]
        require(
            path not in data and not Path(path).is_absolute(), "unique relative source"
        )
        require(".." not in Path(path).parts, "contained source")
        target = ROOT / path
        require(target.stat().st_size <= 1024 * 1024, "source size limit")
        body = target.read_bytes()
        require(
            hashlib.sha256(body).hexdigest() == row["sha256"], "source digest: " + path
        )
        data[path] = body
    expected = {PREFIX + name + ".py" for name in CORE} | {
        ROUTES,
        KERNELS,
        "research/selected-bit-fast-primitives/PROOF.md",
        "research/linear-sign-total-traffic/PROOF.md",
        "research/linear-sign-total-traffic/EXPORTS.json",
    }
    require(set(data) == expected, "complete proof-relevant source inventory")
    return data


def literal_function(data, path, name, namespace, mutation=None):
    tree = ast.parse(data[path], filename=path)
    nodes = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == name
    ]
    require(
        len(nodes) == 1 and not nodes[0].decorator_list, "one literal source function"
    )
    node = nodes[0]
    if mutation is not None:
        node = mutation(node)
    code = compile(ast.Module(body=[node], type_ignores=[]), path, "exec")
    exec(code, namespace)  # noqa: S102 -- authenticated literal AST; see PROOF.md.
    return namespace[name]


def load(data, mutation=None):
    modules = {}
    for name in CORE:
        module = types.ModuleType(name)
        module.__file__ = str(ROOT / (PREFIX + name + ".py"))
        sys.modules[name] = modules[name] = module
        exec(  # noqa: S102 -- fixed authenticated source inventory; see PROOF.md.
            compile(data[PREFIX + name + ".py"], module.__file__, "exec"),
            module.__dict__,
        )
    words, stream, bitstream = (
        modules[name] for name in ("words", "stream", "bitstream")
    )
    namespace = {"Counter": stream.Counter, "copy_bits": bitstream.copy_bits}
    rows = literal_function(data, ROUTES, "copy_rows", namespace)
    namespace = {
        "Count": modules["cardinal_counts"].Count,
        "positive": modules["cardinal_counts"].positive,
        "Counter": stream.Counter,
        "copy_bits": bitstream.copy_bits,
        "copy_rows": rows,
        "BLANK": words.BLANK,
        "need": words.need,
    }
    return modules, literal_function(data, KERNELS, "doubled", namespace, mutation)
