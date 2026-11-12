#!/usr/bin/env python3
"""Certify the historical admission gap for the selected-result checker.

The frozen historical bytes stay in place. This verifier does not add an
accepted live hash and does not replay the selected scientific construction.
"""
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INSPECTED = "2485805a6d47f36ea83ddde6327d453ac82d44dc"
PARENT = "01885346d4e78083b0a41786f977f71c73e3ffa2"
SELECTED_PATH = "scripts/verify_selected_result.py"
SELECTED_PIN = "d7fd929726b326aeeaf0a3996475adec88eee9aac09ae0bebeeaa0bc1fc8f199"
SELECTED_ACCEPTED = "c0cc23a8534d91c8d272195315c725213f13279815750ffdef055ec3adfbe911"
SELECTED_LIVE = "d6b305eac5b9bdb8172c469ad30a1655a60fa0aceac8b1bf610e1b73f51babd8"
CI_PATH = "docs/ci-verification.md"
CI_LIVE = "c7d3027e9ad8bcbff68f07aa9576b30fb2f3c76c44d876d40c7fdbf4a3e2228a"

# Distinct live paths rejected by authenticated_input at INSPECTED, with the
# number of CONFIG entries that name each path.
REJECTIONS = {
    "Makefile": (1, "Historical Makefile prefix changed"),
    "scripts/partial_swap/shared.py": (13, "Unrecognized live source update: scripts/partial_swap/shared.py"),
    "certificates/partial-swap-network.json": (1, "Unrecognized live source update: certificates/partial-swap-network.json"),
    "docs/ci-verification.md": (1, "Unrecognized live source update: docs/ci-verification.md"),
    "scripts/run_isolated_tests.py": (1, "Unrecognized live source update: scripts/run_isolated_tests.py"),
    "tests/test_isolated_test_runner.py": (1, "Unrecognized live source update: tests/test_isolated_test_runner.py"),
    SELECTED_PATH: (1, "Unrecognized live source update: scripts/verify_selected_result.py"),
}
PLAN_PACKAGES = [
    "research/archive-2979-receipt",
    "research/archive-2980-2981-receipt",
    "research/frontier-source-retention",
    "research/intake-closure-omission",
    "research/intake-initial-heads",
    "research/ledger-evidence-drift",
    "research/pr1-retention-receipt",
    "research/pr5427-hold-head-receipt",
    "research/pr636-family-witness-manifest-receipt",
]
CHANGED = [
    "docs/research/pr-intake-checkpoint.json",
    "docs/research/pr-intake-decisions.json",
    "docs/research/pr-intake-evidence/queue-oct30-ending.json",
    "docs/research/pr-intake-evidence/queue-oct30b-closures.json",
    "docs/research/pr-ledger.json",
]
UNMATCHED = [
    "docs/research/pr-intake-checkpoint.json",
    "docs/research/pr-intake-evidence/queue-oct30-ending.json",
    "docs/research/pr-intake-evidence/queue-oct30b-closures.json",
]


def require(ok, message):
    if not ok:
        raise SystemExit(message)


def load_module(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def checkout_snapshot(snapshot, sources, runner, env):
    paths = [runner.canonical_relative_path(row["path"]) for row in sources["files"]]
    git = ["git", "-c", "maintenance.auto=false", "-c", "gc.auto=0",
           "-c", "core.autocrlf=false"]
    subprocess.run([*git, "clone", "--quiet", "--shared", "--no-tags", "--no-checkout",
                    "--", str(ROOT), str(snapshot)], cwd=ROOT, env=env, check=True)
    subprocess.run([*git, "update-ref", "--no-deref", "HEAD", INSPECTED],
                   cwd=snapshot, env=env, check=True)
    # The pinned planner reads omitted manifests from the sparse HEAD/index.
    patterns = "".join(f"/{path.as_posix()}\n" for path in paths)
    subprocess.run([*git, "sparse-checkout", "set", "--no-cone", "--stdin"],
                   cwd=snapshot, env=env, input=patterns.encode("utf-8"), check=True)
    subprocess.run([*git, "read-tree", "-mu", "HEAD"], cwd=snapshot, env=env, check=True)
    for path, row in zip(paths, sources["files"], strict=True):
        require(hashlib.sha256((snapshot / path).read_bytes()).hexdigest() == row["sha256"],
                "historical checkout source digest changed: " + path.as_posix())


def entries(checker):
    for name, config in checker.CONFIG.items():
        for entry in [config, *config.get("additional_inputs", [])]:
            yield name, entry


def reject(root, checker, entry):
    try:
        checker.authenticated_input(root, entry)
    except ValueError as exc:
        return str(exc)
    raise SystemExit("historical input was admitted: " + entry["path"])


def check_snapshot(root, env):
    checker = load_module(root / "scripts/replay_historical_check.py")
    selected = [entry for name, entry in entries(checker)
                if name == "tooling-ledger" and entry["path"] == SELECTED_PATH]
    require(len(selected) == 1, "selected-result checker overlay is not unique")
    entry = selected[0]
    require(entry["sha256"] == SELECTED_PIN, "frozen selected-checker pin changed")
    require(entry["accepted_live_sha256"] == [SELECTED_ACCEPTED],
            "accepted selected-checker successors changed")
    frozen = (checker.INPUTS / entry["input"]).read_bytes()
    live = (root / SELECTED_PATH).read_bytes()
    require(hashlib.sha256(frozen).hexdigest() == SELECTED_PIN, "frozen selected checker bytes changed")
    require(hashlib.sha256(live).hexdigest() == SELECTED_LIVE, "live selected checker digest changed")
    require(SELECTED_LIVE not in (SELECTED_PIN, SELECTED_ACCEPTED), "live checker was already admitted")
    # The recorded pin would pass the same membership test. The failure is the
    # live successor, not a broken comparison.
    require(SELECTED_PIN in (SELECTED_PIN, *entry["accepted_live_sha256"]),
            "pin membership control failed")
    require(reject(root, checker, entry) == REJECTIONS[SELECTED_PATH][1],
            "selected checker rejection text changed")

    counts = {path: 0 for path in REJECTIONS}
    messages = {}
    for _name, item in entries(checker):
        if item["path"] not in REJECTIONS:
            continue
        message = reject(root, checker, item)
        counts[item["path"]] += 1
        messages.setdefault(item["path"], message)
    for path, (count, message) in REJECTIONS.items():
        require(counts[path] == count, "rejection count changed for " + path)
        require(messages[path] == message, "rejection text changed for " + path)
    require(sum(counts.values()) == 19, "rejection total changed")
    ci = [item for _name, item in entries(checker) if item["path"] == CI_PATH]
    require(len(ci) == 1 and hashlib.sha256((root / CI_PATH).read_bytes()).hexdigest() == CI_LIVE,
            "selected CI note digest changed")

    diff = subprocess.check_output(
        ["git", "diff", "--name-only", PARENT, INSPECTED], cwd=root, env=env, text=True)
    changed = sorted(name for name in diff.splitlines() if name)
    require(changed == CHANGED, "inspected commit diff changed")
    planner = load_module(root / "scripts/research_package.py")
    details = planner.plan_details(root, set(changed))
    require([row["package"] for row in details] == PLAN_PACKAGES, "helper plan selection changed")
    matched = {name for row in details for names in row["causes"].values() for name in names}
    require(sorted(set(changed) - matched) == UNMATCHED, "unmatched plan paths changed")
    require(planner.plan_details(root, set()) == [], "empty change set selected a package")


def main():
    require(not sys.flags.optimize, "assertions must stay enabled")
    sources = json.loads(Path(__file__).with_name("SOURCES.json").read_bytes())
    require(sources["base_commit"] == INSPECTED, "historical checkout base changed")
    runner = load_module(ROOT / "scripts/research_package.py")
    env = runner.git_source_env()
    with tempfile.TemporaryDirectory(prefix="historical-selected-replay-") as temporary:
        snapshot = Path(temporary) / "snapshot"
        checkout_snapshot(snapshot, sources, runner, env)
        check_snapshot(snapshot, env)
    print("PASS_HISTORICAL_SELECTED_REPLAY_GAP")
    print("selected_checker_live=" + SELECTED_LIVE)
    print("rejections=19 distinct_paths=7 plan_packages=9")


if __name__ == "__main__":
    main()
