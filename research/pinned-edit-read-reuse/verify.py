#!/usr/bin/env python3
"""Check complete pin reports and actual read counts; produced by Nick Petalas."""
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import statistics
import subprocess
import sys
import tempfile

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
BASE = "de5ec2e7a6074068452f45b1a191b5c72832df4a"
HEAD = "7c49fe32c55de02c2c873655c804b16e4c3fef0a"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def loader():
    spec = importlib.util.spec_from_file_location("pin_reuse_runner", PACKAGE / "run.py")
    require(spec is not None and spec.loader is not None, "missing runner")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
    exported = sources["predecessor_export"]
    require(hashlib.sha256((PACKAGE / exported["export"]).read_bytes()).hexdigest()
            == exported["sha256"], "changed predecessor export")
    for row in sources["files"]:
        if row["usage"] == "input":
            require(hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest()
                    == row["sha256"], "changed live helper")
    old = (PACKAGE / "predecessor.py").read_text()
    expected = old.replace(
        "independent delegated regression review.",
        "independent delegated regression review.\n"
        "Unchanged-head blob reuse produced by Nick Petalas.")
    expected = expected.replace(
        "        after = blobs(root, [head_commit + ':' + p for p in pinners])",
        "        # A merge-base pinner omitted from this immutable-tree diff has the\n"
        "        # same bytes at head. Read only changed pinners a second time.\n"
        "        after = blobs(root, [head_commit + ':' + p for p in pinners if p in changed])")
    expected = expected.replace(
        "            text_after = after[head_commit + ':' + pinner]",
        "            text_after = after[head_commit + ':' + pinner] if pinner in changed else text_before")
    require((PACKAGE / "optimized.py").read_text() == expected, "unexpected scanner delta")


def scan(module, root, base, head):
    calls = []
    original = module.blobs

    def observed(where, specs):
        result = original(where, specs)
        calls.append({"requests": len(specs), "bytes": sum(
            len(value) for value in result.values() if value is not None)})
        return result

    module.blobs = observed
    try:
        report = module.check(root, base, head)
    finally:
        module.blobs = original
    require(len(calls) in (1, 3), "unexpected scan phases")
    return report, calls


def git(module, root, *args):
    result = subprocess.run(["git", "--no-replace-objects", *args], cwd=root,
                            env=module.git_source_env(), capture_output=True,
                            timeout=30, check=True)
    return result.stdout.decode().strip()


def fixture(module, root):
    git(module, root, "init", "-q")
    git(module, root, "config", "user.name", "Fixture")
    git(module, root, "config", "user.email", "fixture@example.invalid")
    names = ["research/target.txt", "notes/living.txt", "research/same.txt"]
    for name in names:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"old payload\n")
    digest = hashlib.sha256(b"old payload\n").hexdigest()
    pinners = ["pins/unchanged.json", "pins/removed.json", "pins/repinned.json",
               "pins/changed-stale.json", "pins/line\nbreak.json", "pins/carriage\rreturn.json"]
    for name in pinners:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(digest + "\n")
    git(module, root, "add", ".")
    git(module, root, "commit", "-qm", "base")
    base = git(module, root, "rev-parse", "HEAD")
    for name in names[:2]:
        (root / name).write_bytes(b"new payload\n")
    (root / pinners[1]).unlink()
    (root / pinners[2]).write_text("new digest\n")
    (root / pinners[3]).write_text(digest + "\nchanged\n")
    (root / "pins/added.json").write_text(digest + "\n")
    git(module, root, "add", ".")
    git(module, root, "commit", "-qm", "head")
    return base, git(module, root, "rev-parse", "HEAD")


def compare(original, optimized, root, base, head):
    before, old_calls = scan(original, root, base, head)
    after, new_calls = scan(optimized, root, base, head)
    require(before == after, "complete report differs")
    require(old_calls[:2] == new_calls[:2], "base reads changed")
    require(new_calls[-1]["requests"] <= old_calls[-1]["requests"], "read count increased")
    return before, {"predecessor": old_calls, "optimized": new_calls}


def controls(original, optimized, runner):
    with tempfile.TemporaryDirectory(prefix="pin-read-reuse-") as directory:
        root = Path(directory)
        base, head = fixture(original, root)
        report, reads = compare(original, optimized, root, base, head)
        require(report["changed_files"] == 5, "changed-path fixture")
        require(len(report["pins"]) == 12, "duplicate-target fixture")
        require(report["frozen_stale"] == 4 and report["stale"] == 8, "stale fixture")
        require({row["state"] for row in report["pins"]}
                == {"stale", "repinned", "pinner_removed"}, "missing classification")
        require(reads["predecessor"][-1]["requests"] == 6, "original request fixture")
        require(reads["optimized"][-1]["requests"] == 3, "reuse request fixture")
        for strict in (False, True):
            outputs = []
            for mode in ("predecessor", "optimized"):
                args = [sys.executable, "-I", "-W", "error", "-B", str(PACKAGE / "run.py"),
                        mode, "--root", str(root), "--base", base, "--head", head, "--json"]
                if strict:
                    args.append("--strict")
                result = subprocess.run(args, capture_output=True, timeout=30, check=False)
                require(result.returncode == 1 and not result.stderr, "CLI failure state")
                outputs.append(result.stdout)
            require(outputs[0] == outputs[1], "complete CLI output differs")
        empty, _ = compare(original, optimized, root, head, head)
        require(empty["pins"] == [] and empty["changed_files"] == 0, "empty diff")
        for bad in ("", "unknown", "../predecessor"):
            try:
                runner.load(bad)
            except ValueError:
                continue
            raise ValueError("unsafe implementation accepted")
    return {"pin_rows": len(report["pins"]), "read_counts": reads,
            "cli_comparisons": 2, "invalid_modes_rejected": 3, "empty_diff": True}


def check_benchmark(report):
    receipt = json.loads((PACKAGE / "BENCHMARK.json").read_text())
    require(receipt["base"] == BASE and receipt["head"] == HEAD, "benchmark revisions")
    require(receipt["errors"] == 0 and receipt["pin_rows"] == len(report["pins"]),
            "benchmark incomplete")
    stdout = (json.dumps(report, indent=2) + "\n").encode()
    require(hashlib.sha256(stdout).hexdigest() == receipt["complete_stdout_sha256"],
            "benchmark report differs")
    names = ("predecessor.py", "optimized.py", "run.py", "benchmark.py")
    require(set(receipt["source_sha256"]) == set(names), "benchmark source inventory")
    for name in names:
        require(hashlib.sha256((PACKAGE / name).read_bytes()).hexdigest()
                == receipt["source_sha256"][name], "benchmark source changed")
    for name in ("predecessor", "optimized"):
        row = receipt["runs"][name]
        values = row["seconds"]
        require(len(values) == 5 and all(type(x) is float and math.isfinite(x) and x > 0
                                        for x in values), "benchmark run domain")
        require((row["minimum"], row["median"], row["maximum"])
                == (min(values), statistics.median(values), max(values)), "benchmark summaries")
    return receipt["verdict"]


def main():
    authenticate()
    runner = loader()
    original, optimized = runner.load("predecessor"), runner.load("optimized")
    result = {"controls": controls(original, optimized, runner)}
    report, reads = compare(original, optimized, ROOT, BASE, HEAD)
    require(report["changed_files"] == 39 and len(report["pins"]) == 154,
            "wrong canonical comparison domain")
    eliminated = reads["predecessor"][-1]["requests"] - reads["optimized"][-1]["requests"]
    require(eliminated > 0, "no read improvement")
    result.update({"status": "PASS_PINNED_EDIT_READ_REUSE", "base": BASE, "head": HEAD,
                   "benchmark_verdict": check_benchmark(report),
                   "pin_rows": len(report["pins"]), "read_counts": reads,
                   "eliminated_head_requests": eliminated,
                   "report_sha256": hashlib.sha256(json.dumps(report, sort_keys=True).encode()).hexdigest(),
                   "package_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                      for p in sorted(PACKAGE.iterdir()) if p.is_file()}})
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
