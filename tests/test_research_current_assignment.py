"""Current orientation must preserve frozen task-selection evidence."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("current_picker", ROOT / "scripts/choose_current_research_task.py")
current = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(current)
LEGACY = current.LEGACY
legacy = current.runpy.run_path(str(LEGACY))
CATALOG = json.loads((ROOT / legacy["CATALOG"]).read_text(encoding="utf-8"))


class CurrentResearchAssignmentTests(unittest.TestCase):
    def test_every_frozen_card_and_other_fields_stay_exact(self):
        before = copy.deepcopy(CATALOG)
        resolved = 0
        for track in CATALOG["tracks"]:
            for task in track["tasks"]:
                result = legacy["select"](CATALOG, "a1" * 16, task_id=task["id"])
                original = copy.deepcopy(result)
                current.resolve_current_first_steps(result, ROOT)
                card = result["suggestions"][0]
                if task["first_step"]["command"] == ["python3", "-B", "scripts/research_baseline.py"]:
                    resolved += 1
                    self.assertEqual(card["catalog_first_step"], task["first_step"])
                    self.assertEqual(card["first_step"]["command"],
                                     ["python3", "-B", "scripts/research_selected_baseline.py"])
                    self.assertTrue(card.pop("first_step_resolution"))
                    card["first_step"] = card.pop("catalog_first_step")
                self.assertEqual(result, original)
        self.assertEqual(resolved, 16)
        self.assertEqual(CATALOG, before)

    def test_only_exact_generic_command_is_resolved(self):
        result = copy.deepcopy(legacy["select"](CATALOG, "0" * 32, task_id="portable-replay"))
        result["suggestions"][0]["first_step"]["command"].append("--historical-fixture")
        original = copy.deepcopy(result)
        self.assertEqual(current.resolve_current_first_steps(result, ROOT), [])
        self.assertEqual(result, original)

    def test_missing_current_helper_does_not_change_receipt(self):
        result = legacy["select"](CATALOG, "0" * 32, task_id="portable-replay")
        original = copy.deepcopy(result)
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "missing current first-step script"):
                current.resolve_current_first_steps(result, Path(directory))
        self.assertEqual(result, original)

    def cli(self, script, args):
        return subprocess.run([sys.executable, "-B", str(script), *args], cwd=ROOT,
                              capture_output=True, text=True, encoding="utf-8")

    def test_cli_preserves_legacy_output_and_emits_both_commands(self):
        args = ["--seed", "0" * 32, "--task", "portable-replay"]
        original = self.cli(LEGACY, args)
        output = self.cli(ROOT / "scripts/choose_current_research_task.py", args)
        self.assertEqual(original.returncode, 0)
        self.assertEqual(output.returncode, 0)
        old, new = json.loads(original.stdout), json.loads(output.stdout)
        card = new["suggestions"][0]
        self.assertEqual(card["first_step"]["command"],
                         ["python3", "-B", "scripts/research_selected_baseline.py"])
        self.assertEqual(card.pop("catalog_first_step"), old["suggestions"][0]["first_step"])
        self.assertTrue(card.pop("first_step_resolution"))
        card["first_step"] = old["suggestions"][0]["first_step"]
        self.assertEqual(new, old)
        self.assertEqual(self.cli(LEGACY, args).stdout, original.stdout)

    def test_help_and_error_preserve_child_status_and_output(self):
        for args, code in ((["--help"], 0), (["--unknown-option"], 2), (["--seed", "bad"], 2)):
            original = self.cli(LEGACY, args)
            output = self.cli(ROOT / "scripts/choose_current_research_task.py", args)
            self.assertEqual(output.returncode, code)
            self.assertEqual((output.stdout, output.stderr), (original.stdout, original.stderr))

    def test_sparse_helper_is_allowed_but_deletion_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            name = "scripts/research_selected_baseline.py"
            path = root / name; path.parent.mkdir(); path.write_text("print('fixture')\n")
            def git(*args):
                subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)
            git("init", "-q"); git("add", name)
            git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                "-c", "core.hooksPath=/dev/null", "commit", "-qm", "helper")
            git("update-index", "--skip-worktree", name); path.unlink()
            result = legacy["select"](CATALOG, "0" * 32, task_id="portable-replay")
            self.assertEqual(current.resolve_current_first_steps(result, root), [name])
            git("update-index", "--no-skip-worktree", name)
            result = legacy["select"](CATALOG, "0" * 32, task_id="portable-replay")
            with self.assertRaisesRegex(ValueError, "missing current first-step script"):
                current.resolve_current_first_steps(result, root)
