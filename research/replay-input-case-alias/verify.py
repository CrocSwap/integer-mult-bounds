#!/usr/bin/env python3
"""Replay-input spelling audit; Arham Tahir, Codex assistance. Apache-2.0.

Native reproduction requires a case-insensitive working volume. Portable
controls run wherever Git and the retained runners are supported.
"""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import types

PACKAGE = Path(__file__).resolve().parent
CANONICAL = "src/dep.json"
ALIASES = ("SRC/dep.json", "src/DEP.json", "SRC/DEP.json")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate(raw, row):
    require(hashlib.sha256(raw).hexdigest() == row["sha256"], "source SHA256 mismatch")
    blob = b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw
    require(hashlib.sha1(blob).hexdigest() == row["git_blob"], "source Git blob mismatch")


def load_runner(raw, path):
    # Compile authenticated source directly: -B still permits stale .pyc reads.
    module = types.ModuleType("case_alias_runner")
    module.__file__ = str(path)
    exec(compile(raw, str(path), "exec"), module.__dict__)
    return module


def sources():
    metadata = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    main = next(row for row in metadata["files"] if row["path"] == "scripts/research_package.py")
    previous = metadata["external_sources"][0]
    result = []
    for label, path, row in (
        ("main", PACKAGE / main["vendored_path"], main),
        ("pr2986", PACKAGE / previous["vendored_path"], previous),
    ):
        raw = path.read_bytes()
        authenticate(raw, row)
        for mutant in (raw + b"\n", raw[:-1]):
            try:
                authenticate(mutant, row)
            except ValueError:
                pass
            else:
                raise ValueError("changed source escaped authentication")
        wrong_blob = dict(row, git_blob="0" * 40)
        try:
            authenticate(raw, wrong_blob)
        except ValueError as exc:
            require("Git blob" in str(exc), "blob control failed at the wrong boundary")
        else:
            raise ValueError("wrong Git blob escaped authentication")
        result.append((label, raw, load_runner(raw, path)))
    return result


class Fixture:
    def __init__(self, root, raw, alias):
        self.root = root
        root.mkdir()
        self.git("init", "-q")
        for key, value in (("user.name", "Replay fixture"),
                           ("user.email", "fixture@example.invalid"),
                           ("core.autocrlf", "false"), ("commit.gpgsign", "false"),
                           ("core.fsmonitor", "false"),
                           ("core.hooksPath", str(root / "disabled-hooks"))):
            self.git("config", key, value)
        self.write(CANONICAL, '{"value": 1}\n')
        self.write("other.txt", "unrelated input\n")
        self.write("scripts/research_package.py", raw)
        self.card = {"id": "fixture", "question": "Audit replay dependency spelling"}
        self.write("docs/research/agent-task-catalog.json",
                   json.dumps({"tracks": [{"tasks": [self.card]}]}))
        self.write("certificates/selected-result.json", "{}\n")
        self.commit()
        source_base = self.git("rev-parse", "HEAD").strip()
        rows = []
        for name in ("docs/research/agent-task-catalog.json", "certificates/selected-result.json"):
            content = (root / name).read_bytes()
            rows.append({"path": name, "usage": "provenance",
                         "git_blob": self.git("rev-parse", source_base + ":" + name).strip(),
                         "sha256": hashlib.sha256(content).hexdigest()})
        self.write("research/alpha/TASK.json", json.dumps({
            "schema_version": 1, "task_id": "fixture", "base_commit": source_base,
            "original_card": self.card, "scope_status": "unchanged",
            "actual_scope": self.card["question"], "bottleneck_link": "Replay invalidation",
            "stop_rule": "One fixture", "outcome": "completed", "evidence": "Git target-only diff",
            "author": "Fixture", "ai_assistance": "Automated fixture generation",
            "open_questions": [], "no_open_questions_reason": "Regression control only",
        }))
        self.write("research/alpha/SOURCES.json", json.dumps({
            "schema_version": 1, "base_commit": source_base, "files": rows,
        }))
        self.write("research/alpha/README.md", "Fixture\n\n## Open next questions\n\nNone.\n")
        self.set_input(alias)
        self.write("research/beta/VERIFY.json", json.dumps({"inputs": ["other.txt"]}))
        self.commit()
        self.base = self.git("rev-parse", "HEAD").strip()
        self.write(CANONICAL, '{"value": 2}\n')
        self.commit()
        require(self.changed(self.base) == [CANONICAL], "fixture diff is not target-only")
        self.output = root.parent / (root.name + "-github-output.txt")

    def write(self, name, content):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content if isinstance(content, bytes) else content.encode("utf-8"))

    def git(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.root, timeout=20).decode("utf-8")

    def commit(self):
        self.git("add", "--all")
        self.git("-c", "maintenance.auto=false", "-c", "gc.auto=0", "commit", "-qm", "fixture")

    def changed(self, base):
        return self.git("diff", "--no-renames", "--name-only", "-z", base, "HEAD").split("\0")[:-1]

    def set_input(self, name):
        self.write("research/alpha/VERIFY.json", json.dumps({
            "schema_version": 1, "status": "ready", "python": "3.12", "requirements": [],
            "inputs": [name], "commands": [{"argv": ["{python}", "-c", "pass"],
            "timeout_seconds": 10, "checks": "Fixture metadata only; no proof execution"}],
        }))

    def cli(self, *args):
        return subprocess.run(
            [sys.executable, "-B", str(self.root / "scripts/research_package.py"), *args],
            cwd=self.root, capture_output=True, text=True, encoding="utf-8", timeout=30,
        )

    def selected(self, expected, base=None):
        self.output.write_text("existing-output\n", encoding="utf-8")
        result = self.cli("--changed-since", base or self.base, "--github-output", str(self.output))
        require(result.returncode == 0, "planner CLI failed: " + result.stderr)
        matrix = {"include": [{"package": name} for name in expected]}
        require(json.loads(result.stdout) == matrix, "unexpected CLI matrix")
        lines = self.output.read_text(encoding="utf-8").splitlines()
        require(lines[0] == "existing-output", "planner overwrote existing output")
        fields = dict(line.split("=", 1) for line in lines[1:])
        require(json.loads(fields["matrix"]) == matrix and fields["count"] == str(len(expected)),
                "workflow output disagrees with stdout")


def exercise(label, raw, runner, temporary):
    results = []
    for index, alias in enumerate(ALIASES):
        fixture = Fixture(temporary / (label + str(index)), raw, alias)
        root = fixture.root
        tracked = fixture.git("ls-files", "-z").split("\0")[:-1]
        require(CANONICAL in tracked and alias not in tracked, "Git spellings not distinguished")
        native = (root / alias).is_file()
        if native:
            require((root / alias).samefile(root / CANONICAL), "alias refers to a different inode")
            require(not (root / alias).is_symlink() and not (root / alias).parent.is_symlink(),
                    "case fixture contains a symlink")
            runner.validate(root, "research/alpha")  # full provenance and file checks
            validation = fixture.cli("--package", "research/alpha", "--check-only")
            require(validation.returncode == 0 and "PASS_PACKAGE_METADATA_AND_PINS" in validation.stdout,
                    "native alias did not pass full CLI validation: " + validation.stderr)
        else:
            try:
                runner.validate(root, "research/alpha")
            except ValueError:
                pass
            else:
                raise ValueError("nonexistent case alias unexpectedly validates")
        require(runner.plan(root, fixture.changed(fixture.base)) == [], "alias planner behavior changed")
        fixture.selected([])

        # The manifest edit stays uncommitted: the same committed target-only
        # diff must select alpha when the dependency spelling is corrected.
        fixture.set_input(CANONICAL)
        runner.validate(root, "research/alpha")
        require(runner.plan(root, [CANONICAL]) == ["research/alpha"], "canonical input lost")
        fixture.selected(["research/alpha"])
        require(runner.plan(root, ["other.txt"]) == ["research/beta"], "unrelated input misrouted")

        # Malformed metadata must reject before publishing a partial matrix.
        fixture.set_input("./" + CANONICAL)
        fixture.output.write_text("existing-output\n", encoding="utf-8")
        failure = fixture.cli("--changed-since", fixture.base, "--github-output", str(fixture.output))
        require(failure.returncode != 0 and failure.stdout == "" and "canonical" in failure.stderr,
                "lexical alias was not rejected cleanly")
        require(fixture.output.read_text(encoding="utf-8") == "existing-output\n", "partial workflow output")

        fixture.set_input(CANONICAL)
        fixture.commit()
        deletion_base = fixture.git("rev-parse", "HEAD").strip()
        (root / CANONICAL).unlink()
        (root / "src").rmdir()
        fixture.commit()
        require(fixture.changed(deletion_base) == [CANONICAL], "deletion is not target-only")
        require(runner.plan(root, [CANONICAL]) == ["research/alpha"], "deleted input lost")
        fixture.selected(["research/alpha"], deletion_base)
        results.append({"alias": alias, "native_metadata_accepts": native,
                        "target_only_diff": [CANONICAL], "alias_matrix": [],
                        "canonical_matrix": ["research/alpha"],
                        "deleted_parent_matrix": ["research/alpha"],
                        "unrelated_control": "research/beta", "lexical_control": "rejected_no_output"})
    return {"runner": label, "cases": results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-native", action="store_true",
                        help="fail unless the native filesystem resolves ASCII case aliases")
    parser.add_argument("--receipt", type=Path, help="write observed evidence; not required for a check")
    args = parser.parse_args()
    runners = sources()
    with tempfile.TemporaryDirectory(prefix="replay-case-alias-") as temporary:
        results = [exercise(label, raw, runner, Path(temporary)) for label, raw, runner in runners]
    native = sum(case["native_metadata_accepts"] for result in results for case in result["cases"])
    require(native in (0, 6), "mixed filesystem semantics need a separate scope")
    report = {"schema_version": 1, "results": results, "native_reproductions": native,
              "environment": {"platform": platform.platform(), "python": platform.python_version(),
                              "git": subprocess.check_output(["git", "--version"], text=True, timeout=10).strip()},
              "scope": "ASCII case aliases on this volume; no production fix or supplier claim"}
    if args.receipt:
        args.receipt.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("PASS_CASE_ALIAS_PORTABLE_CONTROLS runners=2 variants=3 source_mutants=6")
    if native:
        print("PASS_CASE_ALIAS_NATIVE_REPRODUCTION full_validation=6 target_only_git_omissions=6")
    else:
        print("CASE_ALIAS_NATIVE_UNAVAILABLE case_sensitive_volume; native omission NOT reproduced")
    require(not args.require_native or native == 6, "native reproduction requires a case-insensitive working volume")


if __name__ == "__main__":
    main()
