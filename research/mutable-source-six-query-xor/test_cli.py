#!/usr/bin/env python3
"""Subprocess corruption and relocated replay controls; no predecessor imports."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def run(path, *flags):
    return subprocess.run([sys.executable, "-I", "-O", "-B", str(path / "verify.py"), *flags],
                          capture_output=True, text=True, timeout=60)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def main():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    with tempfile.TemporaryDirectory(prefix="six-query-xor-") as folder:
        export = Path(folder).resolve()
        need(export.parent == Path(tempfile.gettempdir()).resolve(), "unexpected scratch root")
        package = export / "research" / HERE.name
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns("__pycache__"))
        for rec in sources["files"]:
            if rec["usage"] == "input":
                dest = export / rec["path"]
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / rec["path"], dest)
        original = {p: p.read_bytes() for p in export.rglob("*") if p.is_file()}
        result = run(package)
        need(result.returncode == 0, "optimized relocated replay failed: "+result.stderr)
        need(all(p.read_bytes() == content for p, content in original.items()), "read-only replay changed input")
        receipt_path = package / "RESULT.json"
        receipt = json.loads(receipt_path.read_text())
        receipt["census"]["by_length"][7]["connected_identity_graphs"] = 1
        receipt_path.write_text(json.dumps(receipt))
        bad = run(package)
        need(bad.returncode != 0 and "receipt mismatch" in bad.stderr, "receipt mutation accepted")
        receipt_path.write_bytes(original[receipt_path])
        input_rec = next(r for r in sources["files"] if r["usage"] == "input")
        source_path = export / input_rec["path"]
        source_path.write_bytes(source_path.read_bytes()+b"\n")
        bad = run(package)
        need(bad.returncode != 0 and "source bytes mismatch" in bad.stderr, "source mutation accepted")
        source_path.write_bytes(original[source_path])
        generated = export / "regenerated.json"
        result = run(package, "--write-receipt", str(generated))
        need(result.returncode == 0, "explicit receipt export failed")
        need(json.loads(generated.read_text()) == json.loads(receipt_path.read_text()), "receipt regeneration differs")
    print("PASS_SIX_QUERY_CLI optimized_relocation read_only receipt_rejection source_rejection deterministic_export")


if __name__ == "__main__":
    main()
