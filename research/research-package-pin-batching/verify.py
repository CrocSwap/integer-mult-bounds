#!/usr/bin/env python3
"""Same-fixture source validation benchmark and failure controls.

Arham Tahir, with substantial OpenAI Codex assistance. Apache-2.0.
No mathematical replay or kappa improvement is claimed.
"""
import argparse
from contextlib import closing
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import tempfile
import time
import types
from unittest.mock import patch

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
PINS = json.loads((PACKAGE / "SOURCES.json").read_bytes())
BASE = PINS["base_commit"]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def git(root, *args):
    return subprocess.check_output(["git", *args], cwd=root)


def load_modules():
    source = git(ROOT, "show", BASE + ":scripts/research_package.py")
    row = next(r for r in PINS["files"] if r["path"] == "scripts/research_package.py")
    require(hashlib.sha256(source).hexdigest() == row["sha256"], "predecessor source changed")
    old = types.ModuleType("pin_batch_predecessor")
    old.__file__ = str(ROOT / "scripts/research_package.py")
    exec(compile(source, old.__file__, "exec"), old.__dict__)
    spec = importlib.util.spec_from_file_location("pin_batch_current", ROOT / "scripts/research_package.py")
    new = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(new)
    sys.path.insert(0, str(ROOT / "scripts"))
    import new_research_package as scaffold
    sys.path.pop(0)
    return old, new, scaffold


def make_fixture(root, scaffold):
    # Real committed bytes in synthetic registered-package inventories.
    # Setup time is excluded from all validation timings.
    names = [p for p in git(ROOT, "ls-tree", "-r", "--name-only", BASE, "scripts").decode().splitlines()
             if p.endswith(".py")][:128]
    require(len(names) == 128, "fixed source inventory differs")
    subprocess.run(["git", "clone", "--shared", "--no-checkout", "-q", str(ROOT), str(root)], check=True)
    subprocess.run(["git", "restore", "--source", BASE, "--worktree", "--",
                    "docs/research/agent-task-catalog.json", "certificates/selected-result.json", *names],
                   cwd=root, check=True)
    for size in (8, 128):
        p = scaffold.create(root, "fixture-" + str(size), "replay-runtime", "Benchmark", names[:size], base=BASE)
        task = json.loads((p / "TASK.json").read_bytes())
        task.update(bottleneck_link="Measure source validation", stop_rule="One fixed inventory",
                    outcome="partial", evidence="Same-fixture benchmark and controls",
                    ai_assistance="OpenAI Codex assistance", open_questions=[],
                    no_open_questions_reason="Benchmark fixture only")
        (p / "TASK.json").write_text(json.dumps(task), encoding="utf-8")
        manifest = json.loads((p / "VERIFY.json").read_bytes())
        manifest["status"] = "ready"
        manifest["commands"][0]["checks"] = "Source validation fixture"
        (p / "VERIFY.json").write_text(json.dumps(manifest), encoding="utf-8")
    return names


def controls(old, new, root, names):
    package = "research/fixture-128"
    directory = root / package
    files = {n: (directory / n).read_bytes() for n in ("SOURCES.json", "TASK.json")}
    source = json.loads(files["SOURCES.json"])
    task = json.loads(files["TASK.json"])
    require(old.validate(root, package) == new.validate(root, package), "positive validation differs")
    rejected = []

    def reject(label, filename, value):
        (directory / filename).write_text(json.dumps(value), encoding="utf-8")
        try:
            for module in (old, new):
                try:
                    module.validate(root, package)
                except (ValueError, subprocess.CalledProcessError):
                    pass
                else:
                    raise ValueError(module.__name__ + " accepted " + label)
        finally:
            (directory / filename).write_bytes(files[filename])
        rejected.append(label)

    for field, label, value in (("git_blob", "last-row blob substitution", "0" * 40),
                                ("sha256", "last-row SHA256 substitution", "0" * 64)):
        mutation = copy.deepcopy(source)
        mutation["files"][-1][field] = value
        reject(label, "SOURCES.json", mutation)
    mutation = copy.deepcopy(source)
    mutation["files"].append(dict(path="missing-source", usage="provenance", git_blob="0" * 40, sha256="0" * 64))
    reject("missing Git source", "SOURCES.json", mutation)
    mutation = copy.deepcopy(source)
    mutation["base_commit"] = "0" * 40
    (directory / "TASK.json").write_text(json.dumps(dict(task, base_commit="0" * 40)), encoding="utf-8")
    try:
        reject("wrong base commit", "SOURCES.json", mutation)
    finally:
        (directory / "TASK.json").write_bytes(files["TASK.json"])
    mutation = copy.deepcopy(source)
    mutation["files"] = [r for r in mutation["files"] if r["path"] != "docs/research/agent-task-catalog.json"]
    reject("omitted catalogue provenance", "SOURCES.json", mutation)
    mutation = copy.deepcopy(task)
    mutation["original_card"]["acceptance_gate"] = "Altered acceptance gate"
    reject("changed original card", "TASK.json", mutation)
    mutation = copy.deepcopy(source)
    mutation["files"][0]["path"] = "../outside"
    reject("escaping source path", "SOURCES.json", mutation)

    live = root / names[-1]
    before = live.read_bytes()
    live.write_bytes(before + b"\n# changed live input\n")
    try:
        for module in (old, new):
            try:
                module.validate(root, package)
            except ValueError as exc:
                require("source drift" in str(exc), "wrong live-input rejection")
            else:
                raise ValueError("live mutation accepted after successful validation")
    finally:
        live.write_bytes(before)
    rejected.append("live-input drift after successful validation")
    require(old.validate(root, package) == new.validate(root, package), "restored live source rejected")
    catalogue = root / "docs/research/agent-task-catalog.json"
    before = catalogue.read_bytes()
    catalogue.write_bytes(b'{"later":"priority revision"}')
    try:
        require(old.validate(root, package) == new.validate(root, package), "historical provenance became live")
    finally:
        catalogue.write_bytes(before)
    mutation = copy.deepcopy(source)
    mutation["files"].append(copy.deepcopy(mutation["files"][-1]))
    (directory / "SOURCES.json").write_text(json.dumps(mutation), encoding="utf-8")
    require(old.validate(root, package) == new.validate(root, package), "duplicate valid row differs")
    mutation["files"][-1]["sha256"] = "0" * 64
    reject("invalid duplicate last row", "SOURCES.json", mutation)
    return rejected


def reader_controls(new, parent):
    root = parent / "binary"
    root.mkdir()
    git(root, "init", "-q")
    name = "binary space\nnewline.dat"
    data = b"\x00first\n" + bytes(range(256)) * 4096 + b"\x00last\n"
    (root / name).write_bytes(data)
    (root / "empty").write_bytes(b"")
    git(root, "add", "--", name, "empty")
    git(root, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
        "-c", "maintenance.auto=false", "-c", "gc.auto=0", "commit", "-qm", "binary fixture")
    results = list(new.git_blobs(root, ["HEAD:" + name, "HEAD:empty"]))
    require(results == [(git(root, "rev-parse", "HEAD:" + name).decode().strip(), data),
                        (git(root, "rev-parse", "HEAD:empty").decode().strip(), b"")],
            "binary framing, newline path or empty blob differs")
    popen = subprocess.Popen
    children = []
    def observe(*args, **kwargs):
        child = popen(*args, **kwargs)
        children.append(child)
        return child
    with patch.object(subprocess, "Popen", side_effect=observe) as calls:
        with closing(new.git_blobs(root, ["HEAD:" + name, "HEAD:missing"])) as blobs:
            next(blobs)
        # The context manager must reap the child even on early iterator close.
        require(calls.call_count == 1, "early-close process count differs")
        require(children[0].returncode is not None and children[0].poll() is not None,
                "early-close Git child was not reaped")
    try:
        list(new.git_blobs(root, ["HEAD:"]))
    except ValueError:
        pass
    else:
        raise ValueError("non-blob Git tree accepted")
    for label, reply in (("truncated binary reply", b"abc"),
                         ("nonzero exit after final reply", b"abc\n")):
        code = ("import sys; s=b''\nwhile not s.endswith(b'\\0'): s+=sys.stdin.buffer.read(1)\n"
                "sys.stdout.buffer.write(" + repr(b"1" * 40 + b" blob 3\n" + reply)
                + ");sys.stdout.flush();sys.exit(7)")
        def fake(*args, **kwargs):
            return popen([sys.executable, "-c", code], **kwargs)
        with patch.object(subprocess, "Popen", side_effect=fake):
            try:
                list(new.git_blobs(root, ["HEAD:empty"]))
            except ValueError:
                pass
            else:
                raise ValueError(label + " accepted")
    return ["non-blob tree", "truncated binary reply", "nonzero exit after final reply"]


def benchmark(old, new, root, iterations):
    rows = []
    popen = subprocess.Popen
    for size in (8, 128):
        package = "research/fixture-" + str(size)
        expected = old.validate(root, package)
        require(new.validate(root, package) == expected, "benchmark positive output differs")
        samples = {"before": [], "after": []}
        counts = {}
        for label, module in (("before", old), ("after", new)):
            with patch.object(subprocess, "Popen", wraps=popen) as calls:
                require(module.validate(root, package) == expected, "process-count validation differs")
                counts[label] = calls.call_count
        require(counts == dict(before=2 * (size + 2) + 1, after=1), "unexpected Git process count")
        for i in range(iterations):
            order = (("before", old), ("after", new)) if i % 2 == 0 else (("after", new), ("before", old))
            for label, module in order:
                start = time.perf_counter()
                result = module.validate(root, package)
                elapsed = time.perf_counter() - start
                require(result == expected, "timed validation differs")
                samples[label].append(elapsed)
        medians = {k: statistics.median(v) for k, v in samples.items()}
        rows.append(dict(input_files=size, source_rows=size + 2, git_processes=counts,
                         seconds=samples, median_seconds=medians,
                         median_speedup=medians["before"] / medians["after"]))
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark", action="store_true")
    parser.add_argument("--iterations", type=int, default=5)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    require(1 <= args.iterations <= 20, "bounded iteration count is 1..20")
    old, new, scaffold = load_modules()
    with tempfile.TemporaryDirectory(prefix="pin-batch-") as td:
        parent = Path(td)
        root = parent / "fixture"
        names = make_fixture(root, scaffold)
        rejected = controls(old, new, root, names) + reader_controls(new, parent)
        measurements = benchmark(old, new, root, args.iterations) if args.benchmark else []
    result = dict(status="PASS_RESEARCH_PACKAGE_PIN_BATCHING", base_commit=BASE,
                  source_inventory=names, rejected_controls=rejected,
                  positive_controls=["identical validation results", "restored live input", "historical catalogue drift",
                                     "duplicate valid row", "binary/empty blobs and newline path", "early iterator close"],
                  environment=dict(python=sys.version, platform=platform.platform(), git=git(ROOT, "--version").decode().strip()),
                  measurements=measurements, scope="Registered-package source validation only; no mathematical replay or new kappa.")
    if args.out:
        args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(result["status"], "controls=" + str(len(rejected)), "no_new_kappa")
    for row in measurements:
        print("source_rows=" + str(row["source_rows"]), "median_speedup=" + format(row["median_speedup"], ".2f"),
              "git_processes=" + str(row["git_processes"]))


if __name__ == "__main__":
    main()
