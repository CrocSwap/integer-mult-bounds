#!/usr/bin/env python3
"""Behavioral and integrity controls, including optimized Python execution."""
import hashlib
import json
from pathlib import Path
import py_compile
import shutil
import tempfile
import types

ROOT = Path(__file__).resolve().parent
v = types.ModuleType("audit")
v.__file__ = str(ROOT / "verify.py")
exec(compile((ROOT / "verify.py").read_bytes(), v.__file__, "exec"), v.__dict__)


def reject(action, reason):
    try:
        action()
    except ValueError as error:
        v.need(reason in str(error), "wrong rejecting control: " + str(error))
    else:
        raise ValueError("defect escaped: " + reason)


def main():
    # Replay positive source before introducing source-level behavioral defects.
    v.graph(v.source(), 3, 4)
    controls = []
    w = v.source()
    w.Word.erase = lambda self: None
    reject(lambda: v.graph(w, 2, 3), "literal content/erasure")
    controls.append("omitted_erasure")

    w = v.source()
    original = w.Arena.zero

    def leaking_zero(a):
        a.available.clear()
        return original(a)

    w.Arena.zero = leaking_zero
    reject(lambda: v.graph(w, 3, 3), "allocation identity")
    controls.append("discarded_reusable_slots")

    original_cells = v.cells
    for name, bad_count in (
        ("omitted_template", lambda a: sum(len(x.cells) for x in a.words)),
        ("omitted_LEFT", lambda a: sum(len(x.cells)-1 for x in [a.template, *a.words])),
    ):
        v.cells = bad_count
        reject(lambda: v.graph(v.source(), 2, 3), "complete array cells")
        controls.append(name)
    v.cells = original_cells

    w = v.source()
    for cap in range(1, 6):
        a = w.Arena(2, cap)
        held = [a.zero() for _ in range(cap)]
        reject(a.zero, "fixed register inventory")
        a.free(held[-1])
        v.need(a.zero() is held[-1], "exact-capacity reuse")
    controls.append("one_slot_underbudget_and_exact_capacity_reuse")

    with tempfile.TemporaryDirectory(prefix="arena-source-controls-") as temp:
        export = Path(temp) / "package"
        shutil.copytree(ROOT, export, ignore=shutil.ignore_patterns("__pycache__"))
        # Controls mutate only their own scratch copy, including when the
        # submitted package is replayed from a read-only source export.
        for local in export.rglob("*"):
            local.chmod(0o755 if local.is_dir() else 0o644)
        export.chmod(0o755)
        path = export / "vendor/words.py"
        original_source = path.read_bytes()
        path.write_bytes(original_source + b"\n# corruption\n")
        reject(lambda: v.source(export), "source SHA256")
        path.write_bytes(original_source)
        pins = export / "INPUTS.json"
        original_pins = pins.read_bytes()
        bad = json.loads(original_pins)
        bad["files"][0]["git_blob"] = "0" * 40
        pins.write_text(json.dumps(bad))
        reject(lambda: v.source(export), "source Git blob")
        pins.write_bytes(original_pins)
        # A malicious unchecked-hash cache is effective for ordinary imports,
        # but our loader executes authenticated source bytes directly.
        malicious = Path(temp) / "malicious.py"
        malicious.write_text("raise RuntimeError('stale bytecode executed')\n")
        cache = Path(__import__("importlib.util", fromlist=["cache_from_source"]).cache_from_source(str(path)))
        cache.parent.mkdir(exist_ok=True)
        py_compile.compile(str(malicious), cfile=str(cache),
                           invalidation_mode=py_compile.PycInvalidationMode.UNCHECKED_HASH)
        need_cache = types.ModuleType("ordinary")
        loader = __import__("importlib.machinery", fromlist=["SourceFileLoader"]).SourceFileLoader("ordinary", str(path))
        try:
            loader.exec_module(need_cache)
        except RuntimeError as error:
            v.need(str(error) == "stale bytecode executed", "effective cache fixture")
        else:
            raise ValueError("malicious cache fixture was not effective")
        v.graph(v.source(export), 2, 3)
        v.need(hashlib.sha256(path.read_bytes()).digest() == hashlib.sha256(original_source).digest(),
               "source bytes changed by cache test")
        receipt = export / "RESULT.json"
        bad = json.loads(receipt.read_text())
        bad["schema_version"] = True
        receipt.write_text(json.dumps(bad))
        old_root = v.ROOT
        v.ROOT = export
        try:
            reject(v.main, "typed receipt mismatch")
        finally:
            v.ROOT = old_root
    controls.extend(["source_corruption", "Git_blob_corruption", "effective_stale_bytecode"])

    controls.append("boolean_integer_receipt_substitution")
    print(json.dumps({"status": "PASS_ARENA_BACKING_CONTROLS", "controls": controls}, indent=2))


if __name__ == "__main__":
    main()
