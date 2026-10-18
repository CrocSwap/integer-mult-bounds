"""Historical source identity survives selection updates without weakening pins."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest

import reproduce


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SELECTED = "certificates/selected-result.json"
CHECKPOINT = "certificates/checkpoints/k492626.json"


class SourcePins(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="r420-source-pins-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.pins = json.loads((HERE / "SOURCES.json").read_text())["repository_inputs_sha256"]
        for relative in self.pins:
            retained = CHECKPOINT if relative == SELECTED else relative
            target = self.root / retained
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / retained, target)
        (self.root / SELECTED).write_text('{"source_prs": [1094]}\n')

    def test_historical_checkpoint_accepts_new_selection_without_writes(self):
        before = {path: path.read_bytes() for path in self.root.rglob("*") if path.is_file()}
        self.assertNotEqual(before[self.root / SELECTED], before[self.root / CHECKPOINT])
        reproduce.check_source_pins(self.root)
        self.assertEqual({path: path.read_bytes() for path in before}, before)

    def test_missing_checkpoint_rejects_even_with_matching_live_selection(self):
        checkpoint = self.root / CHECKPOINT
        (self.root / SELECTED).write_bytes(checkpoint.read_bytes())
        checkpoint.unlink()
        with self.assertRaisesRegex(ValueError, "missing pinned input: .*k492626"):
            reproduce.check_source_pins(self.root)

    def test_corrupt_checkpoint_rejects_even_with_matching_live_selection(self):
        checkpoint = self.root / CHECKPOINT
        original = checkpoint.read_bytes()
        (self.root / SELECTED).write_bytes(original)
        checkpoint.write_bytes(original + b"\n")
        with self.assertRaisesRegex(ValueError, "pinned input changed: .*k492626"):
            reproduce.check_source_pins(self.root)

    def test_every_other_pin_still_rejects_changed_working_bytes(self):
        for relative in self.pins:
            if relative == SELECTED:
                continue
            with self.subTest(path=relative):
                path = self.root / relative
                original = path.read_bytes()
                path.write_bytes(original + b"\n")
                with self.assertRaisesRegex(ValueError, "pinned input changed:"):
                    reproduce.check_source_pins(self.root)
                path.write_bytes(original)


if __name__ == "__main__":
    unittest.main()
