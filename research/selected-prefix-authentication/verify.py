#!/usr/bin/env python3
"""Exact conformance checks for the new prefix validator, produced by Nick Petalas."""

from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
import tempfile
from types import SimpleNamespace


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
FAST = run_path(str(PACKAGE / "fast.py"), run_name="prefix_adapter")
require = FAST["require"]


def outcome(function, root, name):
    try:
        return (True, str(function(root, name)))
    except (ValueError, OSError, TypeError):
        return (False, None)


def path_controls(original, scratch):
    root = scratch / "paths"
    root.mkdir()
    (root / "a" / "b").mkdir(parents=True)
    (root / "a" / "b" / "x").write_bytes(b"x")
    (root / "a" / "y").write_bytes(b"y")
    (root / "unicode-\u03bb").write_bytes(b"z")
    outside = scratch / "outside"
    outside.write_bytes(b"outside")
    links = {"inside-file": root / "a/y", "outside-file": outside,
             "inside-dir": root / "a", "outside-dir": scratch,
             "dangling": root / "absent", "loop": root / "loop"}
    for name, target in links.items():
        (root / name).symlink_to(target)
    names = ["a/b/x", "a/y", "unicode-\u03bb", "a", "a/b", "missing",
             "a/y/x", "", ".", "./a/y", "a//y", "a/./y", "a/../a/y",
             "a/y/", "/a/y", "../outside", "a\\y", None, 17,
             "inside-file", "outside-file", "inside-dir/y", "outside-dir/outside",
             "dangling", "loop", "a/\x00"]
    compared = 0
    for reverse in (False, True):
        validator = FAST["PrefixValidator"](root, original)
        order = list(reversed(names)) if reverse else names
        for name in order:
            require(outcome(original, root, name) == outcome(validator, root, name),
                    "Path predicate differs: " + repr(name))
            compared += 1
    require(outcome(original, root, "a/y")[0], "Positive path was not exercised")
    require(not outcome(original, root, "inside-file")[0], "Alias foil accepted")
    return compared


def make_fixture(root):
    root.mkdir()
    (root / "data").mkdir()
    (root / "data/a").write_bytes(b"alpha")
    (root / "data/b").write_bytes(b"beta")
    (root / "claim.json").write_text('{"kappa":"1/4"}\n')
    (root / "proof").write_bytes(b"proof")
    (root / "validation").write_bytes(b"validation")
    inventory = {p: sha256((root / p).read_bytes()).hexdigest()
                 for p in ("data/a", "data/b", "proof")}
    (root / "manifest.json").write_text(json.dumps({
        "format": "repository-files-sha256-v1", "files": inventory}))
    return {"kappa": "1/4", "decimal": "0.25", "certificate": "claim.json",
            "certificate_sha256": sha256((root / "claim.json").read_bytes()).hexdigest(),
            "source_manifest": "manifest.json", "proof": "proof", "review": "proof",
            "validation": "validation", "proof_supplements": {"proof": inventory["proof"]}}


def check_fixture(root, record, fast):
    baseline = FAST["load_baseline"](ROOT)
    checker = baseline["check"]
    if fast:
        original = checker.__globals__["explicit_file"]
        checker.__globals__["explicit_file"] = FAST["PrefixValidator"](root, original)
    try:
        checker(record, root)
        return True
    except (ValueError, OSError):
        return False


def corruption_controls(scratch):
    root = scratch / "fixture"
    record = make_fixture(root)
    require(check_fixture(root, record, False) and check_fixture(root, record, True),
            "Complete fixture rejected")
    failures = 0
    for name in ("data/a", "data/b", "claim.json", "proof", "manifest.json"):
        target = root / name
        raw = target.read_bytes()
        target.write_bytes(raw + b"changed")
        require(not check_fixture(root, record, False)
                and not check_fixture(root, record, True), "Corruption accepted: " + name)
        target.write_bytes(raw)
        require(check_fixture(root, record, True), "Fresh invocation retained stale bytes")
        failures += 1
    target = root / "data/a"
    raw = target.read_bytes()
    target.unlink()
    target.symlink_to(root / "data/b")
    require(not check_fixture(root, record, False)
            and not check_fixture(root, record, True), "Fresh invocation retained alias facts")
    target.unlink()
    target.write_bytes(raw)
    require(check_fixture(root, record, True), "Restored fixture rejected")
    directory = root / "data"
    saved = root / "data-saved"
    directory.rename(saved)
    directory.symlink_to(saved, target_is_directory=True)
    require(not check_fixture(root, record, False)
            and not check_fixture(root, record, True), "Fresh invocation retained directory facts")
    directory.unlink()
    saved.rename(directory)
    require(check_fixture(root, record, True), "Restored directory rejected")
    return failures + 2


def capacity_controls(original, scratch):
    root = scratch / "capacity"
    root.mkdir()
    (root / "x").write_bytes(b"x")
    validator = FAST["PrefixValidator"](root, original)
    for _ in range(FAST["MAX_INPUTS"]):
        require(validator(root, "x") == root / "x", "Capacity boundary rejected")
    require(not outcome(validator, root, "x")[0], "Call capacity not enforced")
    validator = FAST["PrefixValidator"](root, original)
    require(not outcome(validator, root, "/".join(["a"] * 129))[0],
            "Depth capacity not enforced")
    calls = []
    fake = lambda path, name: calls.append((path, name)) or path / name
    validator = FAST["PrefixValidator"](root, fake)
    globals_ = FAST["PrefixValidator"].__call__.__globals__
    saved = globals_["os"]
    try:
        globals_["os"] = SimpleNamespace(name="nt")
        require(validator(root, "x") == root / "x" and calls == [(root, "x")],
                "Windows did not delegate to the original validator")
    finally:
        globals_["os"] = saved
    return 3


def full_report():
    reference, _ = FAST["report"](ROOT, reference=True)
    candidate, validator = FAST["report"](ROOT)
    require(candidate == reference, "Complete selected report changed")
    require(candidate["status"] == "PASS_RESEARCH_BASELINE_BINDINGS_ONLY",
            "Full checker did not run")
    record = json.loads((PACKAGE / "selection.json").read_bytes())
    manifest = json.loads((ROOT / record["source_manifest"]).read_bytes())
    names = manifest["files"]
    directories = {Path(name).parts[:i] for name in names
                   for i in range(1, len(Path(name).parts))}
    if FAST["os"].name != "nt":
        require(validator.calls == validator.file_checks == len(names),
                "An explicit file check was skipped")
        require(validator.directory_checks == len(directories),
                "A directory prefix was skipped or repeated")
    expected = json.loads((PACKAGE / "SOURCES.json").read_bytes())["files"][0]["sha256"]
    require(candidate["selected_record_sha256"] == expected, "Captured selection changed")
    return {"manifest_files": len(names), "directory_prefixes": len(directories),
            "report_sha256": sha256(json.dumps(candidate, sort_keys=True).encode()).hexdigest()}


def main():
    baseline = FAST["load_baseline"](ROOT)
    original = baseline["check"].__globals__["explicit_file"]
    with tempfile.TemporaryDirectory(prefix="prefix-conformance-") as name:
        scratch = Path(name).resolve()
        evidence = {"path_comparisons": path_controls(original, scratch),
                    "corruption_controls": corruption_controls(scratch),
                    "capacity_and_fallback_controls": capacity_controls(original, scratch)}
    evidence.update(full_report())
    evidence["package_sha256"] = {p.name: sha256(p.read_bytes()).hexdigest()
                                  for p in sorted(PACKAGE.iterdir()) if p.is_file()}
    print(json.dumps({"status": "PASS_SELECTED_PREFIX_AUTHENTICATION",
                      "evidence": evidence}, sort_keys=True))


if __name__ == "__main__":
    main()
