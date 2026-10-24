"""Two-commit export fixtures; Ali Romman with OpenAI Codex, Apache-2.0."""
from pathlib import Path
from hashlib import sha256
import json
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import export_research_package as exporter


class HistoricalInputExportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.package = "research/fixture"
        self.output = self.root / "bundle.tar"
        self.git("init", "-q")
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "core.autocrlf", "false")
        self.write("input.bin", b"original\r\n")
        self.git("add", "input.bin")
        self.git("update-index", "--chmod=+x", "input.bin")
        self.git("commit", "-qm", "historical input")
        self.base = self.git("rev-parse", "HEAD").decode().strip()
        self.write(self.package + "/VERIFY.json", json.dumps({"inputs": ["input.bin"]}).encode())
        code = "from pathlib import Path\nfrom hashlib import sha256\n"
        code += "p=Path(__file__).resolve().parents[2]/'input.bin'\n"
        code += "if sha256(p.read_bytes()).hexdigest() != " + repr(sha256(b"original\r\n").hexdigest()) + ": raise SystemExit('source drift')\n"
        code += "print('PASS_FROZEN_FIXTURE')\n"
        self.write(self.package + "/verify.py", code.encode())
        self.write("input.bin", b"current input\n")
        self.git("add", "."); self.git("update-index", "--chmod=-x", "input.bin")
        self.git("commit", "-qm", "publication with changed input")
        self.head = self.git("rev-parse", "HEAD").decode().strip()

    def git(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.root, stderr=subprocess.PIPE)

    def write(self, name, body):
        p = self.root / name; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(body)

    def test_explicit_input_commit_replays_original_and_is_repeatable(self):
        receipt = exporter.export(self.root, self.package, self.head, self.output, self.base)
        self.assertEqual(receipt["input_commit"], self.base)
        self.assertEqual(receipt["commit"], self.head)
        self.assertEqual(next(r for r in receipt["files"] if r["path"] == "input.bin")["mode"], 0o755)
        self.write("input.bin", b"dirty input")
        other = self.root / "repeat.tar"
        exporter.export(self.root, self.package, self.head, other, self.base)
        self.assertEqual(other.read_bytes(), self.output.read_bytes())
        with patch.object(exporter, "git", side_effect=AssertionError("Git used offline")):
            self.assertEqual(exporter.check_bundle(other), receipt)
        target = self.root / "unpacked"; target.mkdir()
        with tarfile.open(other) as archive:
            archive.extractall(target, filter="data")
        result = subprocess.run([sys.executable, "-I", "-B", str(target / self.package / "verify.py")],
                                cwd=target, capture_output=True, text=True, check=True)
        self.assertEqual(result.stdout, "PASS_FROZEN_FIXTURE\n")

    def test_default_keeps_publication_input_and_no_extra_label(self):
        receipt = exporter.export(self.root, self.package, self.head, self.output)
        self.assertNotIn("input_commit", receipt)
        with tarfile.open(self.output) as archive:
            self.assertEqual(archive.extractfile("input.bin").read(), b"current input\n")
        self.assertEqual(next(r for r in receipt["files"] if r["path"] == "input.bin")["mode"], 0o644)

    def test_input_deleted_at_publication_can_be_exported_from_history(self):
        self.git("rm", "input.bin"); self.git("commit", "-qm", "remove live input")
        with self.assertRaisesRegex(ValueError, "missing declared input"):
            exporter.export(self.root, self.package, "HEAD", self.output)
        receipt = exporter.export(self.root, self.package, "HEAD", self.output, self.base)
        self.assertEqual(exporter.check_bundle(self.output), receipt)

    def test_bad_ref_or_package_local_input_creates_no_archive(self):
        with self.assertRaises(subprocess.CalledProcessError):
            exporter.export(self.root, self.package, self.head, self.output, "missing-ref")
        self.assertFalse(self.output.exists())
        self.write(self.package + "/VERIFY.json", json.dumps({"inputs": [self.package + "/verify.py"]}).encode())
        self.git("add", "."); self.git("commit", "-qm", "ambiguous input")
        with self.assertRaisesRegex(ValueError, "external declared inputs"):
            exporter.export(self.root, self.package, "HEAD", self.output, self.base)
        self.assertFalse(self.output.exists())

    def test_bad_input_commit_label_is_rejected_offline(self):
        exporter.export(self.root, self.package, self.head, self.output, self.base)
        with tarfile.open(self.output) as archive:
            files = [(item.name, archive.extractfile(item).read(), item.mode) for item in archive]
        for bad in (True, "main", "0" * 39, "0" * 41):
            target = self.root / (str(bad) + ".tar")
            with tarfile.open(target, "w") as archive:
                for name, body, mode in files:
                    if name == exporter.RECEIPT:
                        data = json.loads(body); data["input_commit"] = bad
                        body = json.dumps(data).encode()
                    archive.addfile(*exporter.member(name, body, mode))
            with self.assertRaisesRegex(ValueError, "invalid input commit label"):
                exporter.check_bundle(target)

    def test_replacement_ref_cannot_change_historical_input(self):
        old_blob = self.git("rev-parse", self.base + ":input.bin").decode().strip()
        new_blob = self.git("rev-parse", self.head + ":input.bin").decode().strip()
        self.git("replace", old_blob, new_blob)
        exporter.export(self.root, self.package, self.head, self.output, self.base)
        with tarfile.open(self.output) as archive:
            self.assertEqual(archive.extractfile("input.bin").read(), b"original\r\n")
        self.assertEqual(self.git("replace", "-l").decode().strip(), old_blob)
