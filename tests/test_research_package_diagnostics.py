"""CLI regressions: diagnostics name keys, paths, caps and found shapes.

Each regression fails on the unmodified scripts/research_package.py and passes
after the fix. Prepared for navinor with opencode assistance. Apache-2.0.
"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import new_research_package as scaffold
import research_package as package
sys.path.pop(0)

CARD = {
    "id": "fixture",
    "question": "Can the checker name the field that differs?",
    "acceptance_gate": "Name every difference",
    "methods": ["mutate one field", "read the error"],
    "starting_points": ["certificates/selected-result.json"],
}


class ResearchPackageDiagnosticTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        for key, value in (("user.name", "Fixture"), ("user.email", "fixture@example.invalid"),
                           ("core.autocrlf", "false")):
            package.git(self.root, "config", key, value)
        (self.root / "docs/research").mkdir(parents=True)
        (self.root / "certificates").mkdir()
        (self.root / "docs/research/agent-task-catalog.json").write_text(json.dumps({
            "priority_revision": 4, "tracks": [{"tasks": [CARD]}]}), encoding="utf-8")
        (self.root / "certificates/selected-result.json").write_text("{}", encoding="utf-8")
        (self.root / "input.txt").write_text("pinned fixture\n", encoding="utf-8")
        package.git(self.root, "add", ".")
        package.git(self.root, "-c", "gc.auto=0", "commit", "-qm", "base")
        self.base = package.git(self.root, "rev-parse", "HEAD").decode().strip()
        scripts = self.root / "scripts"
        scripts.mkdir()
        for name in ("research_package.py", "new_research_package.py"):
            shutil.copy(ROOT / "scripts" / name, scripts / name)
        self.target = scaffold.create(self.root, "fixture", "fixture", "Fixture", ["input.txt"])
        self.ready()

    def ready(self):
        task = self.load("TASK.json")
        task.update(bottleneck_link="Names the offending key", stop_rule="One exact fixture",
                    outcome="partial", evidence="Exact CLI diagnostics", ai_assistance="Test fixture only",
                    open_questions=[dict(question="Which key differs?", why_it_matters="Fast repair",
                                         first_step="Read the error", blocked_by="Nothing")])
        self.save("TASK.json", task)
        manifest = self.load("VERIFY.json")
        manifest["status"] = "ready"
        manifest["commands"][0]["checks"] = "Scoped diagnostic fixture"
        self.save("VERIFY.json", manifest)

    def load(self, name):
        return json.loads((self.target / name).read_text(encoding="utf-8"))

    def save(self, name, value):
        (self.target / name).write_text(json.dumps(value), encoding="utf-8")

    def run_cli(self):
        return subprocess.run(
            [sys.executable, "-B", str(self.root / "scripts/research_package.py"),
             "--package", "research/fixture", "--check-only"],
            cwd=self.root, capture_output=True, text=True)

    def test_generator_output_round_trips_through_the_checker(self):
        # Alignment contract: the generator writes the exact catalogue card
        # object, so a trim on either the generator or the checker side fails here.
        self.assertEqual(self.load("TASK.json")["original_card"], CARD)
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_trimmed_card_error_names_keys_and_states_the_requirement(self):
        task = self.load("TASK.json")
        del task["original_card"]["methods"]
        task["original_card"]["acceptance_gate"] = "Reworded by hand"
        task["original_card"]["scope_key"] = "copied from a chooser suggestion"
        self.save("TASK.json", task)
        result = self.run_cli()
        self.assertNotEqual(result.returncode, 0)
        for expected in ("missing keys: methods", "unexpected keys: scope_key",
                         "acceptance_gate differs", "original card", "pinned catalogue card object",
                         "docs/research/agent-task-catalog.json", self.base):
            self.assertIn(expected, result.stderr)

    def test_unknown_task_id_names_the_id_and_card_count(self):
        task = self.load("TASK.json")
        task["task_id"] = "no-such-task"
        self.save("TASK.json", task)
        result = self.run_cli()
        self.assertNotEqual(result.returncode, 0)
        for expected in ("no-such-task", "matches 0 cards", "docs/research/agent-task-catalog.json"):
            self.assertIn(expected, result.stderr)

    def test_undeclared_input_pin_names_the_path_and_declaring_file(self):
        manifest = self.load("VERIFY.json")
        manifest["inputs"] = []
        self.save("VERIFY.json", manifest)
        result = self.run_cli()
        self.assertNotEqual(result.returncode, 0)
        for expected in ("input.txt", "SOURCES.json", "VERIFY.json"):
            self.assertIn(expected, result.stderr)

    def test_head_qualified_pin_pins_a_pr_head_vendored_file(self):
        (self.root / "vendored").mkdir()
        (self.root / "vendored/helper.txt").write_text("vendored from a PR head\n", encoding="utf-8")
        package.git(self.root, "add", "vendored")
        package.git(self.root, "-c", "gc.auto=0", "commit", "-qm", "pr head")
        head = package.git(self.root, "rev-parse", "HEAD").decode().strip()
        pinned = package.git(self.root, "show", head + ":vendored/helper.txt")
        rows = self.load("SOURCES.json")
        rows["files"].append({"path": "vendored/helper.txt", "usage": "input",
                              "pin": "head:" + head + ":vendored/helper.txt",
                              "git_blob": package.git(self.root, "rev-parse",
                                                      head + ":vendored/helper.txt").decode().strip(),
                              "sha256": hashlib.sha256(pinned).hexdigest()})
        self.save("SOURCES.json", rows)
        manifest = self.load("VERIFY.json")
        manifest["inputs"].append("vendored/helper.txt")
        self.save("VERIFY.json", manifest)
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_malformed_pin_forms_fail_closed_naming_the_row(self):
        rows = self.load("SOURCES.json")
        row = next(r for r in rows["files"] if r["path"] == "input.txt")
        for bad in ("head:" + self.base[:39] + ":input.txt",
                    "tag:v1:input.txt",
                    "head:" + self.base + ":other.txt"):
            row["pin"] = bad
            self.save("SOURCES.json", rows)
            result = self.run_cli()
            self.assertNotEqual(result.returncode, 0, bad)
            for expected in ("input.txt", "base_commit:", "head:", "40-hex"):
                self.assertIn(expected, result.stderr)
        row["pin"] = "base_commit:input.txt"
        self.save("SOURCES.json", rows)
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)


    def test_later_head_cannot_replace_originating_catalogue_card(self):
        name = "docs/research/agent-task-catalog.json"
        path = self.root / name
        catalog = json.loads(path.read_text(encoding="utf-8"))
        catalog["tracks"][0]["tasks"][0]["acceptance_gate"] = "Replacement later gate"
        path.write_text(json.dumps(catalog), encoding="utf-8")
        package.git(self.root, "add", name)
        package.git(self.root, "-c", "gc.auto=0", "commit", "-qm", "later catalogue")
        head = package.git(self.root, "rev-parse", "HEAD").decode().strip()
        sources = self.load("SOURCES.json")
        row = next(row for row in sources["files"] if row["path"] == name)
        row.update(pin="head:" + head + ":" + name,
                   git_blob=package.git(self.root, "rev-parse", head + ":" + name).decode().strip(),
                   sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        self.save("SOURCES.json", sources)
        task = self.load("TASK.json")
        task["original_card"] = catalog["tracks"][0]["tasks"][0]
        self.save("TASK.json", task)
        result = self.run_cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("originating task catalogue must be pinned at base_commit", result.stderr)

    def test_nonstring_explicit_pins_have_a_named_rejection(self):
        sources = self.load("SOURCES.json")
        row = next(row for row in sources["files"] if row["path"] == "input.txt")
        for pin in (17, [], {}):
            row["pin"] = pin
            self.save("SOURCES.json", sources)
            result = self.run_cli()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("SOURCES.json pin for input.txt", result.stderr)
            self.assertNotIn("TypeError", result.stderr)

    def test_timeout_over_cap_names_key_value_and_cap(self):
        manifest = self.load("VERIFY.json")
        manifest["commands"][0]["timeout_seconds"] = 1800
        self.save("VERIFY.json", manifest)
        result = self.run_cli()
        self.assertNotEqual(result.returncode, 0)
        for expected in ("VERIFY.json.commands[0].timeout_seconds", "1800", "600 s per-command cap"):
            self.assertIn(expected, result.stderr)

    def test_timeout_type_error_names_expected_shape(self):
        manifest = self.load("VERIFY.json")
        manifest["commands"][0]["timeout_seconds"] = "120"
        self.save("VERIFY.json", manifest)
        result = self.run_cli()
        self.assertNotEqual(result.returncode, 0)
        for expected in ("timeout_seconds", "integer", "str", "120"):
            self.assertIn(expected, result.stderr)

    def test_total_budget_names_declared_total_and_cap(self):
        manifest = self.load("VERIFY.json")
        command = dict(manifest["commands"][0])
        command["timeout_seconds"] = 600
        manifest["commands"] = [command, dict(command), dict(command)]
        self.save("VERIFY.json", manifest)
        result = self.run_cli()
        self.assertNotEqual(result.returncode, 0)
        for expected in ("timeout_seconds", "1800", "1200 s total cap"):
            self.assertIn(expected, result.stderr)

    def test_wrong_shaped_task_field_names_key_path_and_found_shape(self):
        # The recorded instance was a Python 1-element tuple; the JSON list is
        # its on-disk analog and both must name the found type, not read as
        # missing content.
        task = self.load("TASK.json")
        task["actual_scope"] = ["one element"]
        self.save("TASK.json", task)
        result = self.run_cli()
        self.assertNotEqual(result.returncode, 0)
        for expected in ("TASK.json.actual_scope", "a non-empty string", "list", "one element"):
            self.assertIn(expected, result.stderr)
        with self.assertRaisesRegex(ValueError, "found tuple"):
            package.require_text({"actual_scope": ("one element",)}, "actual_scope", "TASK.json")

    def test_missing_required_keys_name_key_and_expected_shape(self):
        pristine = self.load("TASK.json")
        for key in ("base_commit", "author", "scope_status", "outcome"):
            with self.subTest(key=key):
                task = dict(pristine)
                del task[key]
                self.save("TASK.json", task)
                result = self.run_cli()
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("TASK.json." + key + " is missing", result.stderr)
                self.assertIn("expected", result.stderr)

    def test_missing_original_card_names_the_key(self):
        task = self.load("TASK.json")
        del task["original_card"]
        self.save("TASK.json", task)
        result = self.run_cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("TASK.json.original_card is missing", result.stderr)

    def test_undeclared_input_error_states_the_requirement(self):
        manifest = self.load("VERIFY.json")
        manifest["inputs"] = []
        self.save("VERIFY.json", manifest)
        result = self.run_cli()
        self.assertNotEqual(result.returncode, 0)
        for expected in ('usage "input"', "VERIFY.json inputs", "CI invalidation", "undeclared: input.txt"):
            self.assertIn(expected, result.stderr)

    def test_print_card_emits_the_pinned_card_for_hand_authors(self):
        printed = subprocess.run(
            [sys.executable, "-B", str(self.root / "scripts/research_package.py"),
             "--package", "research/fixture", "--print-card", "fixture"],
            cwd=self.root, capture_output=True, text=True)
        self.assertEqual(printed.returncode, 0, printed.stderr)
        self.assertEqual(json.loads(printed.stdout), CARD)
        task = self.load("TASK.json")
        del task["original_card"]["methods"]
        self.save("TASK.json", task)
        self.assertNotEqual(self.run_cli().returncode, 0)
        task["original_card"] = json.loads(printed.stdout)
        self.save("TASK.json", task)
        self.assertEqual(self.run_cli().returncode, 0, "pasted --print-card output must validate")
        unknown = subprocess.run(
            [sys.executable, "-B", str(self.root / "scripts/research_package.py"),
             "--package", "research/fixture", "--print-card", "no-such-task"],
            cwd=self.root, capture_output=True, text=True)
        self.assertNotEqual(unknown.returncode, 0)
        self.assertIn("no-such-task", unknown.stderr)

if __name__ == "__main__":
    unittest.main()
