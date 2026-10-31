# SPDX-License-Identifier: Apache-2.0
"""Check invoice extraction, missing charge classes and real source corruption.

Ali Romman with substantial OpenAI Codex assistance.
"""

from collections import Counter
from copy import deepcopy
import gzip
from hashlib import sha256
import importlib.util
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/export_selected_invoice.py"
SPEC = importlib.util.spec_from_file_location("selected_invoice", SCRIPT)
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class InvoiceOutputTests(unittest.TestCase):
    def test_stdout_bytes_ignore_text_encoding_and_newline_policy(self):
        invoice = {"paid": {"1": 2}, "targets": {"2": 1}}
        expected = b'{\n  "paid": {\n    "1": 2\n  },\n  "targets": {\n    "2": 1\n  }\n}\n'
        for encoding, newline in (("utf-8", "\n"), ("utf-8", "\r\n"), ("utf-16", "\n")):
            with self.subTest(encoding=encoding, newline=newline), io.BytesIO() as raw:
                with io.TextIOWrapper(raw, encoding=encoding, newline=newline) as output:
                    with patch.object(M, "export", return_value=(invoice, {})), \
                            patch.object(sys, "argv", [str(SCRIPT)]), \
                            patch.object(sys, "stdout", output):
                        self.assertEqual(M.main(), 0)
                    output.flush()
                    self.assertEqual(raw.getvalue(), expected)


class SelectedInvoiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.word = json.loads(gzip.decompress((ROOT / M.WORD).read_bytes()))
        cls.controller = json.loads((ROOT / M.CONTROLLER).read_bytes())
        cls.receipt = json.loads((ROOT / M.RESULT).read_bytes())
        cls.invoice, cls.components = M.extract(cls.word, cls.controller)

    def test_independent_path_length_bill(self):
        # This count uses the two controller path lengths, not physical events
        # or the emitted main diagonal. The local receipt is a separate oracle.
        paid = Counter({int(r): 18 * n for r, n in self.receipt["local"]["paid"].items()})
        targets = Counter({int(r): 18 * n for r, n in self.receipt["local"]["helpers"].items()})
        paid[1] += 15 * 104
        targets[145] += 208
        for length in (7, 8):
            for j in range(1, length + 1):
                paid[8 * (j + 1)] += 208
                targets[1 + 8 * (j + 1)] += 208
        self.assertEqual(self.invoice["paid"], M.histogram(paid))
        self.assertEqual(self.invoice["targets"], M.histogram(targets))
        self.assertEqual((sum(paid.values()), sum(targets.values())), (66726, 13048))
        self.assertEqual(sum(r * n for r, n in targets.items())
                         - sum(r * n for r, n in paid.items()), 760)
        M.compare_receipt(self.invoice, self.components, self.receipt)

    def test_each_physical_charge_class_is_required(self):
        for op in ("LOCAL", "QUERY_SHEAR", "IDLE"):
            controller = deepcopy(self.controller)
            events = controller["physical_events"]
            del events[next(i for i, e in enumerate(events) if e[0] == op)]
            invoice, components = M.extract(self.word, controller)
            with self.subTest(op=op), self.assertRaisesRegex(ValueError, "Receipt mismatch"):
                M.compare_receipt(invoice, components, self.receipt)

    def test_every_paid_rank_and_target_debit_is_checked(self):
        for field in ("paid", "targets"):
            for rank in self.invoice[field]:
                bad = deepcopy(self.invoice)
                bad[field][rank] -= 1
                with self.subTest(field=field, rank=rank), self.assertRaisesRegex(ValueError, field):
                    M.compare_receipt(bad, self.components, self.receipt)

    def test_component_and_native_receipts_cannot_hide_in_total(self):
        for field in ("local_paid", "local_helpers", "idle_paid", "main_targets"):
            bad = deepcopy(self.components)
            bad[field][next(iter(bad[field]))] -= 1
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, field):
                M.compare_receipt(self.invoice, bad, self.receipt)
        bad = deepcopy(self.receipt)
        bad["native"]["helpers"]["9"] -= 1
        with self.assertRaisesRegex(ValueError, "local_helpers"):
            M.compare_receipt(self.invoice, self.components, bad)

    def test_local_chronology_and_unknown_opcodes_fail(self):
        for change in ("move", "private", "unknown", "exit", "basis", "owned"):
            word = deepcopy(self.word)
            event = next(e for e in word["program"] if e[0] == "MOVE")
            if change == "move":
                event[2], event[3] = event[3], event[2]
            elif change == "private":
                event[4] = not event[4]
            elif change == "unknown":
                word["program"][0][0] = "UNPRICED"
            elif change == "exit":
                word["final"][0] = (word["final"][0] + 1) % len(word["frames"])
            elif change == "basis":
                word["frames"][event[2]].append(0)
            else:
                word["program"].append(["INIT", word["public"], 0])
            with self.subTest(change=change), self.assertRaises(ValueError):
                M.extract(word, self.controller)

    def test_physical_semantic_changes_fail(self):
        for change in ("unknown", "reverse", "idle", "diagonal", "controller"):
            controller = deepcopy(self.controller)
            if change == "unknown":
                controller["physical_events"].append(["UNPRICED", 0])
            elif change == "reverse":
                next(e for e in controller["physical_events"] if e[0] == "LOCAL")[3] = True
            elif change == "idle":
                next(e for e in controller["physical_events"] if e[0] == "IDLE")[2] = [0, 0]
            elif change == "diagonal":
                controller["diagonal"][0][1] = 2
            else:
                controller["ambient_rank"] = 146
            with self.subTest(change=change), self.assertRaises(ValueError):
                M.extract(self.word, controller)

    def test_authenticated_cli_and_comparator(self):
        record = json.loads((ROOT / M.SELECTED).read_bytes())
        if record.get("source_certificate") != M.RESULT:
            self.skipTest("The selected source has moved beyond the opt-in P104 exporter")
        manifest = json.loads((ROOT / record["source_manifest"]).read_bytes())
        names = set(manifest["files"]) | set(record["proof_supplements"])
        names.update([M.SELECTED, record["source_manifest"], record["certificate"],
                      record["review"], record["validation"]])
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in names:
                dest = root / name
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, dest)
            evidence = root / "evidence.json"
            command = [sys.executable, "-I", "-O", "-B", str(SCRIPT), "--root", str(root),
                       "--evidence", str(evidence)]
            # Keep actual transport bytes: text=True hides Windows CRLF output.
            run = subprocess.run(command, capture_output=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(json.loads(run.stdout), self.invoice)
            self.assertEqual(json.loads(evidence.read_bytes())["components"], self.components)
            self.assertEqual(json.loads(evidence.read_bytes())["invoice_sha256"],
                             sha256(run.stdout).hexdigest())
            invoice_path = root / "invoice.json"
            invoice_path.write_bytes(run.stdout)
            compare = subprocess.run([sys.executable, "-I", "-B",
                str(ROOT / "scripts/compare_recursive_invoices.py"), str(invoice_path), str(invoice_path)],
                capture_output=True, text=True)
            self.assertEqual(compare.returncode, 0, compare.stderr)
            self.assertEqual(json.loads(compare.stdout)["classification"], "equal")
            for name in (M.WORD, M.CONTROLLER, M.RESULT):
                path = root / name
                original = path.read_bytes()
                path.write_bytes(original + b"changed")
                bad = subprocess.run(command, text=True, capture_output=True)
                self.assertEqual(bad.returncode, 2, name)
                self.assertEqual(bad.stdout, "")
                self.assertIn("bytes changed", bad.stderr)
                path.write_bytes(original)
            # A manifest which omits an input must not leave a trusted receipt
            # pointing to an unauthenticated word.
            del manifest["files"][M.WORD]
            (root / record["source_manifest"]).write_text(json.dumps(manifest), encoding="utf-8")
            bad = subprocess.run(command, text=True, capture_output=True)
            self.assertEqual(bad.returncode, 2)
            self.assertIn("Unbound invoice input", bad.stderr)


if __name__ == "__main__":
    unittest.main()
