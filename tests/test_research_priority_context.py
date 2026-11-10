"""Keep catalogue assessment provenance distinct from the selected result.

Sricharan Vagvala, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import copy
from contextlib import contextmanager
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import subprocess
import shutil
import sys
import tempfile
import unittest

from test_research_current_assignment import ROOT, frozen_cli_tree

SCRIPT = "choose_contextual_research_task.py"
SPEC = importlib.util.spec_from_file_location("contextual_picker", ROOT / "scripts" / SCRIPT)
current = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(current)


@contextmanager
def contextual_cli_tree():
    with frozen_cli_tree() as root:
        shutil.copyfile(ROOT / "scripts" / SCRIPT, root / "scripts" / SCRIPT)
        yield root


# The three differing fields at base 7c49fe32; these are metadata fixtures,
# not independently authenticated construction or admission evidence.
CATALOG_CONTEXT = {
    "kappa": "62009/20000000",
    "source_commit": "09dd0965711ca7eeb169057a420abab1c9052137",
    "review": "docs/research/pr-intake-evidence/pr5599-completion/PROOF-REVIEW.md",
}
SELECTED = {
    "kappa": "781451/250000000",
    "audited_source_head": "772dd10a5859a1d15f4851feb371519789213ad8",
    "review": "docs/research/pr-intake-evidence/pr6030-audit/PROOF-REVIEW.md",
}
NAMES = ("docs/research/agent-task-catalog.json", "certificates/selected-result.json")


def write_receipt(root, context, selected):
    receipt = {}
    for name, key, value in zip(
        NAMES, ("catalog_sha256", "selected_record_sha256"),
        ({"selection_context": context}, selected),
    ):
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        raw = json.dumps(value).encode("utf-8")
        path.write_bytes(raw)
        receipt[key] = sha256(raw).hexdigest()
    return receipt


class ResearchPriorityContextTests(unittest.TestCase):
    def compare(self, context=CATALOG_CONTEXT, selected=SELECTED):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            receipt = write_receipt(root, context, selected)
            before = copy.deepcopy(receipt)
            result = current.catalog_selection_context(receipt, root)
            self.assertEqual(receipt, before)
            return result

    def matching_context(self):
        return {"kappa": SELECTED["kappa"],
                "source_commit": SELECTED["audited_source_head"],
                "review": SELECTED["review"]}

    def test_actual_checkpoint_discrepancy_exposes_all_three_fields(self):
        result = self.compare()
        self.assertFalse(result["matches_selected"])
        self.assertEqual(result["context"], CATALOG_CONTEXT)
        self.assertEqual(set(result["differences"]), {"kappa", "source_commit", "review"})
        self.assertEqual(result["differences"]["kappa"],
                         {"catalog": "62009/20000000", "selected": "781451/250000000"})
        self.assertEqual(result["uncompared_fields"], [])

    def test_equal_rationals_are_not_a_false_discrepancy(self):
        context = self.matching_context()
        context["kappa"] = "0.003125804"
        result = self.compare(context)
        self.assertIs(result["matches_selected"], True)
        self.assertEqual(result["differences"], {})

    def test_same_kappa_does_not_hide_changed_source_or_review(self):
        for field in ("source_commit", "review"):
            with self.subTest(field=field):
                context = self.matching_context()
                context[field] = CATALOG_CONTEXT[field]
                result = self.compare(context)
                self.assertIs(result["matches_selected"], False)
                self.assertEqual(set(result["differences"]), {field})

    def test_absent_context_is_unknown(self):
        result = self.compare(None)
        self.assertIsNone(result["matches_selected"])
        self.assertIsNone(result["context"])
        self.assertEqual(set(result["uncompared_fields"]), set(CATALOG_CONTEXT))

    def test_missing_source_head_is_unknown_even_when_other_fields_match(self):
        for missing_side in ("catalog", "selected"):
            with self.subTest(missing_side=missing_side):
                context, selected = self.matching_context(), dict(SELECTED)
                if missing_side == "catalog":
                    context.pop("source_commit")
                else:
                    selected.pop("audited_source_head")
                result = self.compare(context, selected)
                self.assertIsNone(result["matches_selected"])
                self.assertEqual(result["uncompared_fields"], ["source_commit"])

    def test_known_difference_survives_incomplete_context(self):
        context = dict(CATALOG_CONTEXT)
        context.pop("source_commit")
        result = self.compare(context)
        self.assertIs(result["matches_selected"], False)
        self.assertEqual(result["uncompared_fields"], ["source_commit"])

    def test_change_after_child_receipt_is_rejected_for_each_input(self):
        for name in NAMES:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                receipt = write_receipt(root, CATALOG_CONTEXT, SELECTED)
                path = root / name
                # Even a semantically inert rewrite belongs to another snapshot.
                path.write_bytes(path.read_bytes() + b"\n")
                with self.assertRaisesRegex(ValueError, "input changed since task selection"):
                    current.catalog_selection_context(receipt, root)

    def test_malformed_context_is_rejected(self):
        for context in ([], "old context", {"kappa": 0.003125804},
                        {"kappa": "1/0"}, {"kappa": "not a rational"}):
            with self.subTest(context=context), self.assertRaises(ValueError):
                self.compare(context)

    def test_real_cli_preserves_choices_and_retains_original_context(self):
        with contextual_cli_tree() as root:
            path = root / NAMES[0]
            catalog = json.loads(path.read_bytes())
            context = {**CATALOG_CONTEXT, "scope": "Historical assessment; retain verbatim."}
            catalog["selection_context"] = context
            path.write_text(json.dumps(catalog), encoding="utf-8")
            (root / NAMES[1]).write_text(json.dumps({
                **SELECTED, "source_manifest": "fixture.json", "reproduce": "fixture replay",
            }), encoding="utf-8")
            args = ["--seed", "0" * 32, "--task", "portable-replay"]
            def invoke(script):
                return subprocess.run([sys.executable, "-B", str(root / "scripts" / script), *args],
                                      capture_output=True, text=True, encoding="utf-8")
            old = invoke("choose_current_research_task.py")
            new = invoke(SCRIPT)
            self.assertEqual(old.returncode, 0, old.stderr)
            self.assertEqual(new.returncode, 0, new.stderr)
            before, after = json.loads(old.stdout), json.loads(new.stdout)
            report = after.pop("catalog_selection")
            self.assertIs(report["matches_selected"], False)
            self.assertEqual(report["context"], context)
            # The existing current-command routes and all other output stay exact.
            self.assertEqual(after, before)
            self.assertEqual(invoke("choose_current_research_task.py").stdout, old.stdout)

    def test_real_cli_preserves_child_help_and_failure(self):
        with contextual_cli_tree() as root:
            for args in (["--help"], ["--unknown-option"], ["--seed", "bad"]):
                with self.subTest(args=args):
                    def invoke(script):
                        return subprocess.run(
                            [sys.executable, "-B", str(root / "scripts" / script), *args],
                            capture_output=True, text=True, encoding="utf-8")
                    old, new = invoke("choose_current_research_task.py"), invoke(SCRIPT)
                    self.assertEqual((new.returncode, new.stdout, new.stderr),
                                     (old.returncode, old.stdout, old.stderr))
