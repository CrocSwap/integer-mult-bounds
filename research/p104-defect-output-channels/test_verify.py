"""Behavioral controls for exact output channels and paid restoration."""

from pathlib import Path
import shutil
import tempfile
import types
import unittest


ROOT = Path(__file__).resolve().parent


def load(path, name, replacement=None):
    source = path.read_text()
    if replacement is not None:
        before, after = replacement
        if before not in source:
            raise ValueError("mutation target absent")
        source = source.replace(before, after)
    result = types.ModuleType(name)
    result.__file__ = str(path)
    exec(compile(source, str(path), "exec", optimize=0), result.__dict__)
    return result


MODEL = load(ROOT / "model.py", "model_tests")
VERIFY = load(ROOT / "verify.py", "verify_tests")


class Controls(unittest.TestCase):
    def test_complete_small_delivery_target_domain(self):
        for code in (-1, 0, 1):
            expected = MODEL.signed_bits(MODEL.decode([code], 1), 2)
            for target in range(256):
                work = [[0]*4 for _ in range(2)]
                self.assertEqual(MODEL.delivery_oracle([code], target, work, 1), target ^ expected)
                self.assertEqual(work, [[0]*4 for _ in range(2)])

    def test_missing_phase_or_channel_rejected(self):
        spectrum = MODEL.spectral([1, 0, 0, 0], 1)
        spectrum[1] = -spectrum[1]
        with self.assertRaisesRegex(ValueError, "phase line"):
            MODEL.pack(spectrum, 1)
        value = [((i*13) % 17)-8 for i in range(16)]
        channels = MODEL.encode(value, 3)
        with self.assertRaisesRegex(ValueError, "channel shape"):
            MODEL.decode(channels[:-1], 3)

    def test_forbidden_walsh_modes_rejected(self):
        for rank in range(1, 8):
            for mode in (0, (1 << rank)-1):
                spectrum = [0]*MODEL.shape(rank)
                spectrum[2*mode] = 1
                with self.assertRaises(ValueError):
                    MODEL.pack(spectrum, rank)

    def test_forward_invisible_cleanup_failure(self):
        broken = load(ROOT / "model.py", "missing_cleanup",
                      ("for operation in reversed(operations):",
                       "for operation in list(reversed(operations))[2:]:"))
        channels = MODEL.encode([1, 0, 0, 0], 1)
        with self.assertRaisesRegex(ValueError, "literal bank cleanup"):
            broken.delivery_oracle(channels, 0, [[0]*4 for _ in range(2)], 1)

    def test_unsigned_widening_changes_delivered_value(self):
        broken = load(ROOT / "model.py", "unsigned_widening",
                      ("return word-(1 << width) if word >> (width-1) else word", "return word"))
        value = next(value for label, value in MODEL.candidates(7) if "signed_sample" in label)
        channels = MODEL.encode(value, 7)
        work = [[0]*256 for _ in range(8)]
        correct = MODEL.signed_bits(MODEL.defect(value, 7), 12)
        self.assertTrue(broken.delivery_oracle(channels, 0, work, 7) != correct,
                        "signed widening mutation must change the delivered defect")

    def test_clean_bank_and_alias_boundaries(self):
        with self.assertRaisesRegex(ValueError, "clean"):
            MODEL.delivery_oracle([-1], 0, [[1, 0, 0, 0], [0]*4], 1)
        bank = [0]*4
        with self.assertRaisesRegex(ValueError, "alias"):
            MODEL.delivery_oracle([-1], 0, [bank, bank], 1)
        for bad in (True, 0, 8):
            with self.assertRaises(ValueError):
                MODEL.shape(bad)

    def test_pinned_source_and_typed_result_controls(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            (path / "vendor").mkdir()
            shutil.copyfile(ROOT / "PREDECESSOR.json", path / "PREDECESSOR.json")
            shutil.copyfile(ROOT / "vendor/lifting.py", path / "vendor/lifting.py")
            (path / "vendor/lifting.py").write_bytes((path / "vendor/lifting.py").read_bytes()+b"\n")
            with self.assertRaisesRegex(ValueError, "SHA256"):
                VERIFY.authenticate(path)
        self.assertFalse(VERIFY.typed_equal({"rank": 1}, {"rank": True}))
        self.assertFalse(VERIFY.typed_equal({"rows": [1, 2]}, {"rows": [1]}))


if __name__ == "__main__":
    unittest.main()
