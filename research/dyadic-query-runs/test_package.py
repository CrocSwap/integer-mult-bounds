#!/usr/bin/env python3
"""Relocate, regenerate and corrupt disposable copies of the complete package."""
from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def run(root, script, *args):
    return subprocess.run([sys.executable, "-I", "-O", "-B", str(root/script), *args],
                          cwd=root.parent, capture_output=True, text=True, timeout=120)


def edit_json(path, change):
    data = json.loads(path.read_text())
    change(data)
    path.write_text(json.dumps(data))


def main():
    with tempfile.TemporaryDirectory(prefix="dyadic runs package ") as tmp:
        root = Path(tmp)/"offline package with spaces"
        shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns("__pycache__"))
        certificate = (root/"CERTIFICATE.json").read_bytes()
        evidence = (root/"EVIDENCE.json").read_bytes()
        result = run(root, "build.py")
        need(result.returncode == 0 and (root/"CERTIFICATE.json").read_bytes() == certificate,
             "exact certificate regeneration: " + result.stderr)
        result = run(root, "verify.py")
        need(result.returncode == 0 and "PASS_DYADIC_QUERY_RUNS" in result.stdout,
             "isolated relocated replay: " + result.stderr)
        result = run(root, "verify.py", "--write-evidence")
        need(result.returncode == 0 and (root/"EVIDENCE.json").read_bytes() == evidence,
             "complete evidence regeneration: " + result.stderr)
        faults = [
            ("source", "SOURCES.json", lambda d: d["immutable_inputs"][0].update(sha256="0"*64),
             "source SHA256"),
            ("return", "CERTIFICATE.json", lambda d: d["cases"][54]["word"].pop(),
             "Laurent endpoint/restoration"),
            ("unpaid child", "CERTIFICATE.json", lambda d: d["cases"][54]["invoice"].update(children=11),
             "literal complete invoice"),
            ("removed child", "CERTIFICATE.json", lambda d: d["lowerings"]["1"].pop(3),
             "six affines and one paid child"),
            ("missing case", "CERTIFICATE.json", lambda d: d["cases"].pop(),
             "every declared mask once"),
            ("bool count", "CERTIFICATE.json", lambda d: d["cases"][0]["invoice"]["query_multiplicities"].update({"2": True}),
             "multiplicity integer type"),
            ("nonoptimal", "CERTIFICATE.json", lambda d: d["cases"][54].update(
                word=d["cases"][54]["baseline"], invoice=d["cases"][54]["baseline_invoice"]),
             "graph lower bound attained"),
            ("receipt", "EVIDENCE.json", lambda d: d.update(all_cases_fused_queries=495),
             "complete evidence receipt mismatch"),
        ]
        for name, filename, change, error in faults:
            path = root/filename
            old = path.read_bytes()
            edit_json(path, change)
            result = run(root, "verify.py")
            need(result.returncode != 0 and error in result.stderr,
                 "fault did not reject for the expected obligation: " + name + "\n" + result.stderr)
            path.write_bytes(old)
    print("PASS_DYADIC_QUERY_RUNS_PACKAGE relocation=1 regeneration=2 corruptions=8")


if __name__ == "__main__":
    main()
