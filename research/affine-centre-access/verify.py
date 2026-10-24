"""Check the source bytes and replay the finite affine access checks."""

import argparse
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time


HERE = Path(__file__).resolve().parent
PHYS = "evidence/lanes/residual-syndrome/physical-algebra/"
CHECKS = (
    ("affine_bound", "REVIEW.json", "correlated-access-review/REVIEW.json"),
    ("rigidity", "CHECK.json", "review-gauss/maximal-affine-sectors/CHECK.json"),
    ("density", "RESULT.json", None),
    ("stream_review", "CHECK.json", "review-gauss/affine-projector-stream/CHECK.json"),
    ("odd_review", "CHECK.json", "review-gauss/odd-affine-projector/CHECK.json"),
    ("one_pass_turn", "ONE-PASS-TURN.json", "affine-projector-stream/ONE-PASS-TURN.json"),
    ("coverage", "COVERAGE.json", "affine-sector-cover/COVERAGE.json"),
    ("split_review", "CHECK.json", "review-gauss/affine-split-limit/CHECK.json"),
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def definitions(source):
    return {
        node.name: ast.dump(node, include_attributes=False)
        for node in ast.parse(source).body
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name != "main"
    }


def check_sources():
    manifest = json.loads((HERE / "MANIFEST.json").read_text())
    actual_names = {str(p.relative_to(HERE)) for p in HERE.rglob("*")
                    if p.is_file() and p != HERE / "MANIFEST.json"}
    require(actual_names == set(manifest["files"]), "Package file set differs")
    for name, expected in manifest["files"].items():
        path = HERE / name
        require(not path.is_symlink(), "Symbolic link in package: " + name)
        raw = path.read_bytes()
        require(len(raw) == expected["bytes"], "File size differs: " + name)
        require(sha256(raw) == expected["sha256"], "File hash differs: " + name)
    source_index = json.loads((HERE / "SOURCES.json").read_text())
    for name, expected in source_index["files"].items():
        require(sha256((HERE / name).read_bytes()) == expected["sha256"],
                "Source hash differs: " + name)
    porting = json.loads((HERE / "PORTABILITY.json").read_text())
    for name, record in porting["scripts"].items():
        original = (HERE / record["original"]).read_text()
        portable = (HERE / name).read_text()
        require(sha256(original.encode()) == record["original_sha256"],
                "Original checker hash differs: " + name)
        expected = original
        for change in record["changes"]:
            require(expected.count(change["old"]) == 1, "Porting source differs: " + name)
            expected = expected.replace(change["old"], change["new"])
        require(expected == portable, "Undeclared checker change: " + name)
        require(sha256(portable.encode()) == record["portable_sha256"],
                "Portable checker hash differs: " + name)
        require(definitions(original) == definitions(portable),
                "Mathematical function differs: " + name)
    return {"package_files": len(manifest["files"]),
            "source_files": len(source_index["files"]),
            "portable_checkers": len(porting["scripts"])}


def replay(output):
    sources = check_sources()
    checks = []
    for name, result_name, expected_name in CHECKS:
        folder = output / name
        folder.mkdir()
        started = time.monotonic()
        run = subprocess.run([sys.executable, "-I", "-B", str(HERE / "checks" / (name + ".py"))],
                             cwd=folder, text=True, capture_output=True)
        (folder / "stdout.txt").write_text(run.stdout)
        (folder / "stderr.txt").write_text(run.stderr)
        require(run.returncode == 0, name + " failed: " + run.stderr)
        result_bytes = (folder / result_name).read_bytes()
        result = json.loads(result_bytes)
        require(result["status"].startswith("PASS_"), name + " did not pass")
        if expected_name is not None:
            require(result_bytes == (HERE / PHYS / expected_name).read_bytes(),
                    name + " differs from the frozen receipt")
        checks.append({"name": name, "status": result["status"],
                       "result_sha256": sha256(result_bytes),
                       "byte_equal_to_frozen_receipt": expected_name is not None,
                       "seconds": round(time.monotonic() - started, 3)})
        print(name + ": " + result["status"], flush=True)
    require(check_sources() == sources, "Package changed during replay")
    result = {"status": "PASS_AFFINE_CENTRE_ACCESS", "source_check": sources,
              "checks": checks, "python": sys.version,
              "scope": "Finite exact checks and source binding; no complete supplier replay.",
              "not_replayed": ["Actual owner-boundary binding", "Actual 17-axis frame maximality",
                               "A complete fixed-tape implementation", "Recursive supplier admission"]}
    (output / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Save fresh receipts in a new directory.")
    parser.add_argument("--check-only", action="store_true", help="Check source bytes and portable changes.")
    args = parser.parse_args()
    if args.check_only:
        print(json.dumps(check_sources(), sort_keys=True))
        print("PASS_AFFINE_CENTRE_ACCESS_SOURCES")
    elif args.output is not None:
        args.output.mkdir(parents=True, exist_ok=False)
        replay(args.output.resolve())
    else:
        with tempfile.TemporaryDirectory(prefix="affine-centre-access-") as temporary:
            replay(Path(temporary))


if __name__ == "__main__":
    main()
