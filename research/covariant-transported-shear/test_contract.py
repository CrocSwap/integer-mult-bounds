#!/usr/bin/env python3
"""Behavioral source/receipt controls and Git-free optimized replay."""
from hashlib import sha256
import importlib.util
from importlib._bootstrap_external import _code_to_timestamp_pyc
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, why):
    if not ok:
        raise ValueError(why)


def hashes(root):
    return {str(p.relative_to(root)): sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file()}


def main():
    with tempfile.TemporaryDirectory(prefix="covariant shear export ") as directory:
        root = Path(directory)
        package = root / "research/covariant-transported-shear"
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns("__pycache__"))
        for item in json.loads((HERE / "SOURCES.json").read_text())["files"]:
            if item["usage"] == "input":
                target = root / item["path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / item["path"], target)

        def command(script, *args, success=True, message=None):
            result = subprocess.run([sys.executable, "-I", "-O", "-B", str(package / script), *args],
                                    cwd=root, text=True, capture_output=True, timeout=180)
            need((result.returncode == 0) == success, "unexpected status: " + result.stderr)
            if message:
                need(message in result.stdout + result.stderr, "missing diagnostic: " + message)

        before = hashes(root)
        command("verify.py", message="PASS_READONLY_TRANSPORTED_SHEAR")
        command("independent.py", message="PASS_INDEPENDENT_TRANSPORTED_SHEAR")
        need(hashes(root) == before, "Git-free replays changed files")

        cache_files = []
        for path in (package / "vendor/pr2742/source.py",
                     root / "research/involutive-walsh-lift/native.py"):
            stat = path.stat()
            sentinel = compile("raise RuntimeError('STALE_BYTECODE_SENTINEL')", str(path), "exec")
            cache = Path(importlib.util.cache_from_source(str(path), optimization="1"))
            cache.parent.mkdir(exist_ok=True)
            cache.write_bytes(_code_to_timestamp_pyc(sentinel, int(stat.st_mtime), stat.st_size))
            cache_files.append(cache)
            code = ("import importlib.util; p=" + repr(str(path)) + ";"
                    "s=importlib.util.spec_from_file_location('sentinel',p);"
                    "m=importlib.util.module_from_spec(s);s.loader.exec_module(m)")
            positive = subprocess.run([sys.executable, "-I", "-O", "-B", "-c", code],
                                      cwd=root, capture_output=True, text=True, timeout=30)
            need(positive.returncode != 0 and "STALE_BYTECODE_SENTINEL" in positive.stderr,
                 "stale-cache control must actually execute through ordinary loader")
        command("verify.py", message="PASS_READONLY_TRANSPORTED_SHEAR")
        for cache in cache_files:
            cache.unlink()
        need(hashes(root) == before, "compiled-byte guards changed mathematical files")

        path = package / "vendor/pr2742/circuit.py"
        original = path.read_bytes()
        path.write_bytes(original + b"\n")
        command("verify.py", "--emit-words", success=False, message="changed predecessor")
        path.write_bytes(original)

        path = root / "research/involutive-walsh-lift/native.py"
        original = path.read_bytes()
        path.write_bytes(original + b"\n")
        command("verify.py", "--emit-words", success=False, message="changed input")
        path.write_bytes(original)

        path = package / "RESULT.json"
        original = path.read_bytes()
        receipt = json.loads(original)
        receipt["new_kappa"] = 0  # Python equality alone would confuse this with False.
        path.write_text(json.dumps(receipt))
        command("verify.py", success=False, message="complete typed receipt mismatch")
        path.write_bytes(original)

        code = ("import sys,types;sys.path.insert(0," + repr(str(package)) + ");"
                "import core;sys.modules['source']=types.ModuleType('source');core.load()")
        result = subprocess.run([sys.executable, "-I", "-O", "-B", "-c", code],
                                cwd=root, capture_output=True, text=True, timeout=30)
        need(result.returncode != 0 and "preloaded predecessor module" in result.stderr,
             "preloaded source guard")
        need(hashes(root) == before, "behavioral controls failed to restore export")
    print("PASS_TRANSPORTED_SHEAR_BEHAVIOR groups=7 optimized_git_free_unchanged")


if __name__ == "__main__":
    main()
