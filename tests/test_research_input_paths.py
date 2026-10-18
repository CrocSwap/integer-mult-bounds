"""Reject file aliases that cannot match Git's canonical changed-path output.
Prepared for woklerx with OpenAI Codex assistance. Apache-2.0.
"""

import importlib.util, json, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "research_package_paths", ROOT / "scripts/research_package.py"
)
package = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(package)


class ResearchInputPathTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "fixtures").mkdir()
        (self.root / "fixtures/input.txt").write_text("original\n")
        (self.root / "research/alpha").mkdir(parents=True)
        self.manifest = self.root / "research/alpha/VERIFY.json"
        self.write_manifest("fixtures/input.txt")
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True, timeout=15)
        subprocess.run(["git", "add", "."], cwd=self.root, check=True, timeout=15)
        subprocess.run(["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                        "-c", "gc.auto=0", "commit", "-qm", "source"], cwd=self.root, check=True, timeout=15)

    def write_manifest(self, name):
        self.manifest.write_text(json.dumps({"inputs": [name]}))

    def test_metadata_resolution_requires_canonical_git_paths(self):
        self.assertEqual(
            package.relative_file(self.root, "fixtures/input.txt"),
            self.root / "fixtures/input.txt",
        )
        for alias in [
            "./fixtures/input.txt",
            "fixtures//input.txt",
            "fixtures/./input.txt",
            "fixtures\\input.txt",
        ]:
            with (
                self.subTest(alias=alias),
                self.assertRaisesRegex(ValueError, "canonical"),
            ):
                package.relative_file(self.root, alias)

    def test_planner_rejects_alias_instead_of_silently_skipping(self):
        for alias in [
            "./fixtures/input.txt",
            "fixtures//input.txt",
            "fixtures/./input.txt",
            "fixtures\\input.txt",
        ]:
            self.write_manifest(alias)
            with (
                self.subTest(alias=alias),
                self.assertRaisesRegex(ValueError, "canonical"),
            ):
                package.plan(self.root, ["fixtures/input.txt"])

    def test_deleted_canonical_input_still_invalidates(self):
        (self.root / "fixtures/input.txt").unlink()
        self.assertEqual(
            package.plan(self.root, ["fixtures/input.txt"]), ["research/alpha"]
        )

    def test_full_metadata_rejects_an_unpinned_input_alias(self):
        # External CI inputs need not also appear in SOURCES: provenance-only
        # packages and extra script dependencies are supported by the current schema.
        spec = importlib.util.spec_from_file_location(
            "new_package_paths", ROOT / "scripts/new_research_package.py"
        )
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            scaffold = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(scaffold)
        finally:
            sys.path.pop(0)

        def git(*args):
            return subprocess.check_output(
                ["git", *args], cwd=self.root, text=True
            ).strip()

        git("init", "-q")
        git("config", "user.name", "Fixture")
        git("config", "user.email", "fixture@example.invalid")
        git("config", "core.autocrlf", "false")
        (self.root / "docs/research").mkdir(parents=True)
        (self.root / "certificates").mkdir()
        (self.root / "docs/research/agent-task-catalog.json").write_text(
            json.dumps(
                {
                    "priority_revision": 3,
                    "tracks": [
                        {
                            "tasks": [
                                {"id": "fixture", "question": "Audit input binding"}
                            ]
                        }
                    ],
                }
            )
        )
        (self.root / "certificates/selected-result.json").write_text("{}")
        git("add", ".")
        git("-c", "gc.auto=0", "commit", "-qm", "source")
        target = scaffold.create(self.root, "full", "fixture", "Fixture")
        task = json.loads((target / "TASK.json").read_text())
        task.update(
            bottleneck_link="Input replay admission",
            stop_rule="One exact counterexample",
            outcome="completed",
            evidence="Path fixture",
            ai_assistance="Test fixture",
            open_questions=[],
            no_open_questions_reason="Regression test only",
        )
        (target / "TASK.json").write_text(json.dumps(task))
        manifest = json.loads((target / "VERIFY.json").read_text())
        manifest.update(status="ready", inputs=["fixtures/input.txt"])
        manifest["commands"][0]["checks"] = "Fixture input check"
        (target / "VERIFY.json").write_text(json.dumps(manifest))
        package.validate(self.root, "research/full")
        manifest["inputs"] = ["./fixtures/input.txt"]
        (target / "VERIFY.json").write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, "canonical"):
            package.validate(self.root, "research/full")

    def test_real_git_change_rejects_preexisting_alias_manifest(self):
        def git(*args):
            return subprocess.check_output(
                ["git", *args], cwd=self.root, text=True
            ).strip()

        git("init", "-q")
        git("config", "user.name", "Fixture")
        git("config", "user.email", "fixture@example.invalid")
        git("config", "core.autocrlf", "false")
        (self.root / "scripts").mkdir()
        (self.root / "scripts/research_package.py").write_bytes(
            (ROOT / "scripts/research_package.py").read_bytes()
        )
        self.write_manifest("./fixtures/input.txt")
        git("add", ".")
        git("-c", "gc.auto=0", "commit", "-qm", "before")
        base = git("rev-parse", "HEAD")
        (self.root / "fixtures/input.txt").write_text("changed\n")
        git("add", ".")
        git("-c", "gc.auto=0", "commit", "-qm", "after")
        self.assertEqual(git("diff", "--name-only", base, "HEAD"), "fixtures/input.txt")
        result = subprocess.run(
            [
                sys.executable,
                str(self.root / "scripts/research_package.py"),
                "--changed-since",
                base,
            ],
            cwd=self.root,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(
            result.returncode,
            0,
            "Noncanonical dependency produced a successful empty replay matrix: "
            + result.stdout,
        )
        self.assertIn("canonical", result.stderr)


if __name__ == "__main__":
    unittest.main()
