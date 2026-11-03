#!/usr/bin/env python3
"""Test the new import boundary without replaying predecessor mathematics.

Produced by Nick Petalas. Apache-2.0.
"""

import ast
import builtins
from contextlib import contextmanager, redirect_stdout
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
from types import ModuleType, SimpleNamespace


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("jensen_lazy_entry", HERE / "run.py")
if SPEC is None or SPEC.loader is None:
    raise ValueError("adapter import specification")
ENTRY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ENTRY)


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


@contextmanager
def resource_import(replacement=None):
    """Model one absent module, or record the retained guard's arguments."""
    previous = builtins.__import__
    calls = []

    def intercepted(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "resource":
            calls.append(name)
            if replacement is None:
                raise ModuleNotFoundError("controlled missing resource", name="resource")
            return replacement
        return previous(name, globals, locals, fromlist, level)

    builtins.__import__ = intercepted
    try:
        yield calls
    finally:
        builtins.__import__ = previous


def original_module() -> ModuleType:
    module = ModuleType("retained_jensen_original")
    module.__file__ = str(ENTRY.SOURCE / "verify.py")
    raw = (ENTRY.SOURCE / "verify.py").read_bytes()
    exec(compile(raw, module.__file__, "exec"), module.__dict__)
    return module


def integrity(module: ModuleType, args=("--integrity-only",)) -> str:
    previous = sys.argv
    sys.argv = [module.__file__, *args]
    output = io.StringIO()
    try:
        with redirect_stdout(output):
            module.main()
    finally:
        sys.argv = previous
    return output.getvalue()


def import_controls() -> dict:
    with resource_import() as attempted:
        try:
            original_module()
        except ModuleNotFoundError as error:
            need(error.name == "resource", "original failed at another import")
        else:
            raise ValueError("original unexpectedly loads without resource")
    need(attempted == ["resource"], "original import attempt")
    with resource_import() as attempted:
        actual = integrity(ENTRY)
        adapted = ENTRY.load()
        need(attempted == [], "integrity requested resource")
        try:
            adapted.child_limits()
        except ModuleNotFoundError as error:
            need(error.name == "resource", "guard failed at another import")
        else:
            raise ValueError("guard accepted missing resource")
        need(attempted == ["resource"], "guard import count")
    expected = "PASS_P104_JENSEN_BENCHMARK_INTEGRITY_ONLY_NO_SCIENCE\n"
    need(actual == expected, "complete integrity stdout")
    with resource_import(SimpleNamespace()):
        need(integrity(original_module()) == actual, "original integrity differs")
    return {"original_missing_import_rejected": True, "adapted_integrity_passed": True,
            "missing_guard_import_rejected": True, "complete_stdout": actual}


def guard_and_ast() -> dict:
    calls = []
    marker = object()
    fake = SimpleNamespace(RLIMIT_AS=marker,
                           setrlimit=lambda kind, limits: calls.append((kind, limits)))
    with resource_import(fake):
        original_module().child_limits()
        ENTRY.load().child_limits()
    need(calls == [(marker, (536870912, 536870912))] * 2, "guard contract changed")
    raw = (ENTRY.SOURCE / "verify.py").read_bytes()
    source_tree = ast.parse(raw)
    adapted_tree = ast.parse(ENTRY.adapt(raw))
    imports = [n for n in source_tree.body if isinstance(n, ast.Import)
               and any(a.name == "resource" for a in n.names)]
    need(len(imports) == 1, "resource import inventory")
    source_tree.body.remove(imports[0])
    functions = [n for n in source_tree.body if isinstance(n, ast.FunctionDef)
                 and n.name == "child_limits"]
    need(len(functions) == 1, "child guard inventory")
    functions[0].body.insert(0, imports[0])
    need(ast.dump(source_tree) == ast.dump(adapted_tree), "unexpected AST change")
    return {"ast_change": "move one resource import into child_limits",
            "unchanged_address_space_limit_bytes": 536870912}


def failure_controls() -> list[str]:
    with resource_import() as attempted:
        for args in (("--unknown",), ("--integrity-only", "--extra")):
            reject(lambda: integrity(ENTRY.load(), args), "unsupported verifier arguments")
        need(attempted == [], "invalid arguments requested resource")

    def denied_limit(kind, limits):
        raise OSError("controlled setrlimit failure")

    fake = SimpleNamespace(RLIMIT_AS=object(), setrlimit=denied_limit)
    with resource_import(fake):
        try:
            ENTRY.load().child_limits()
        except OSError as error:
            need(str(error) == "controlled setrlimit failure", "wrong guard failure")
        else:
            raise ValueError("guard swallowed setrlimit failure")
    return ["unknown argument", "mixed arguments", "setrlimit failure"]


def reject(action, expected: str) -> None:
    try:
        action()
    except ValueError as error:
        need(str(error) == expected, "wrong rejection: " + str(error))
        return
    raise ValueError("control accepted: " + expected)


def custody_controls() -> list[str]:
    labels = []
    mutations = (("verify.py", "retained source hash: verify.py"),
                 ("PAYLOAD-INVENTORY.json", "retained source hash: PAYLOAD-INVENTORY.json"),
                 ("PROOF.md", "frozen package byte PROOF.md"),
                 ("extra-file.txt", "complete package inventory"),
                 ("expected/qualification.json", "complete package inventory"))
    with tempfile.TemporaryDirectory(prefix="jensen-lazy-controls-") as temporary:
        root = Path(temporary) / "retained source with spaces"
        shutil.copytree(ENTRY.SOURCE, root, copy_function=shutil.copyfile)
        for name, expected in mutations:
            path = root / name
            old = path.read_bytes() if path.exists() else None
            if name == "expected/qualification.json":
                path.unlink()
            else:
                path.write_bytes((old or b"") + b"\ncontrolled mutation\n")
            try:
                reject(lambda: ENTRY.load(root).authenticate(), expected)
                labels.append(name)
            finally:
                if old is None:
                    path.unlink()
                else:
                    path.write_bytes(old)
        with resource_import() as attempted:
            need(integrity(ENTRY.load(root)) == integrity(ENTRY.load()), "relocation")
            need(attempted == [], "relocated integrity requested resource")
    return labels


def main() -> None:
    pins = json.loads((HERE / "SOURCES.json").read_text())["files"]
    for row in pins:
        if row["usage"] == "input":
            raw = (HERE.parent.parent / row["path"]).read_bytes()
            need(hashlib.sha256(raw).hexdigest() == row["sha256"], "declared input hash")
    receipt = {"claim_type": "scoped implementation-preservation proof with finite conformance",
               "imports": import_controls(), "guard": guard_and_ast(),
               "custody_controls_rejected": custody_controls(),
               "failure_controls": failure_controls(),
               "predecessor_scientific_replay": False, "native_windows_execution": False}
    receipt["package_sha256"] = {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(HERE.iterdir()) if p.is_file()
    }
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":")))
    print("PASS_JENSEN_LAZY_RESOURCE")


if __name__ == "__main__":
    main()
