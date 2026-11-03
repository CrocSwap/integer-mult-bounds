"""Exact dot-product specialization for the complete retained E8 replay.

Produced by Nick Petalas. Apache-2.0. The authenticated source programs,
mathematics, checks and notices remain conorholds's PR3166 contribution.
"""

from __future__ import annotations

from contextlib import contextmanager
from hashlib import sha256
import json
from pathlib import Path
import sys
from types import ModuleType


PACKAGE = Path(__file__).resolve().parent
SOURCE = Path("research/e8-d0-root-swaps")
MODULES = ("geometry_audit", "algebra_check", "extension_check", "verify")
EXPECTED = (
    "PASS_E8_D0_ROOT_SWAPS geometry=two-exact-methods normal_families=5 "
    "root_remainders=120 parabolics=256 extension_models=2 f1_support=24 "
    "frame_plane_cases=57120\n"
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def dot8(a, b):
    """The source's left-associated exact sum on its eight-coordinate domain."""
    if len(a) != 8 or len(b) != 8:
        raise ValueError("dot8 requires eight coordinates")
    return (0 + a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
            + a[3] * b[3] + a[4] * b[4] + a[5] * b[5]
            + a[6] * b[6] + a[7] * b[7])


def authenticated_inputs(root):
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    rows = [row for row in manifest["files"] if row["usage"] == "input"]
    require(len(rows) == 10, "expected ten scientific inputs")
    result = {}
    for row in rows:
        path = row["path"]
        require(Path(path).parent in (SOURCE, SOURCE / "formal"), "input scope")
        raw = (root / path).read_bytes()
        require(len(raw) <= 2**20, "scientific input capacity")
        require(sha256(raw).hexdigest() == row["sha256"], "changed source: " + path)
        require(path not in result, "duplicate scientific input")
        result[path] = raw
    require(all(str(SOURCE / (name + ".py")) in result for name in MODULES),
            "missing scientific module")
    return result


def checked_dot(original, stats):
    def compare(a, b):
        actual = dot8(a, b)
        require(actual == original(a, b), "dot specialization disagrees")
        stats["calls"] += 1
        return actual
    return compare


@contextmanager
def source_modules(root, raw):
    """Compile only the four hash-authenticated modules, bypassing .pyc reads."""
    names = ("geometry_audit", "algebra_check", "extension_check", "e8_bound_source")
    previous = {name: sys.modules.get(name) for name in names}
    old_path, old_argv = sys.path[:], sys.argv[:]
    loaded = {}
    try:
        for filename, name in zip(MODULES, names):
            path = root / SOURCE / (filename + ".py")
            module = ModuleType(name)
            module.__file__ = str(path)
            sys.modules[name] = module
            exec(compile(raw[str(SOURCE / (filename + ".py"))], str(path), "exec"),
                 module.__dict__)
            loaded[filename] = module
        yield loaded
    finally:
        sys.path[:] = old_path
        sys.argv[:] = old_argv
        for name in names:
            if previous[name] is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = previous[name]


def run_replay(mode="fast", root=None):
    require(mode in ("baseline", "fast", "checked"), "replay mode")
    root = PACKAGE.parents[1] if root is None else Path(root)
    raw = authenticated_inputs(root)
    stats = {"calls": 0}
    with source_modules(root, raw) as modules:
        for name in ("verify", "extension_check"):
            module = modules[name]
            if mode == "fast":
                module.dot = dot8
            elif mode == "checked":
                module.dot = checked_dot(module.dot, stats)
        sys.argv[:] = [str(root / SOURCE / "verify.py")]
        result = modules["verify"].main()
        require(result == 0, "complete scientific replay failed")
    return stats


if __name__ == "__main__":
    require(len(sys.argv) in (1, 2), "usage: replay.py [baseline|fast|checked]")
    run_replay(sys.argv[1] if len(sys.argv) == 2 else "fast")
