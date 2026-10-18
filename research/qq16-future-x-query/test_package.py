"""Source-integrity and independent phase/kernel controls. Apache-2.0."""
import importlib.util
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("future_query", HERE / "verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class NativeReadTests(unittest.TestCase):
    def test_handoff_copy_matches_exact_predecessor(self):
        pin = json.loads((HERE / "PREDECESSOR.json").read_text(encoding="utf-8"))
        raw = (HERE / pin["retained_copy"]).read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), pin["sha256"])
        blob = b"blob " + str(len(raw)).encode() + b"\0" + raw
        self.assertEqual(hashlib.sha1(blob).hexdigest(), pin["git_blob"])

    def test_every_live_source_corruption_rejected(self):
        import json
        pins = json.loads((HERE / "SOURCES.json").read_text())
        original = Path.read_bytes
        for item in pins["files"]:
            if item["usage"] != "input":
                continue
            target = v.ROOT / item["path"]
            with self.subTest(path=item["path"]):
                def bad_read(path, target=target):
                    data = original(path)
                    return data + b"corruption" if path == target else data
                with patch.object(Path, "read_bytes", bad_read):
                    with self.assertRaisesRegex(ValueError, "source hash"):
                        v.load_sources()

    def test_phase_polynomial_matches_direct_character(self):
        # Independent pointwise parity evaluation for a mixed signed example.
        terms = ((0b1101, -1), (0b1010, 1), (0b1111, 2), (0b10001, 3))
        linear, cross = v.phase(terms)
        for character in range(32):
            direct = sum(c * ((axis & character).bit_count() % 2) for axis, c in terms) % 4
            evaluated = sum(linear[i] for i in range(73) if (character >> i) & 1)
            evaluated += 2 * sum((row & character).bit_count() for i, row in enumerate(cross) if (character >> i) & 1)
            self.assertEqual(direct, evaluated % 4)

    def test_inverse_line_is_not_the_positive_line(self):
        q = 0b10101
        positive = v.line_recipe(q, 1)
        negative = v.line_recipe(q, -1)
        self.assertNotEqual(v.kernel(positive, 7), v.kernel(negative, 7))
        # Multiply the two explicit Gaussian kernels independently.
        composed = {}
        for middle, (a, b) in v.kernel(positive, 7).items():
            for out, (c, d) in v.kernel(negative, middle).items():
                old = composed.get(out, (0, 0))
                composed[out] = (old[0] + a*c-b*d, old[1] + a*d+b*c)
        self.assertEqual({x: z for x, z in composed.items() if z != (0, 0)}, {7: (4, 0)})

    def test_wrong_map_translation_changes_native_phase(self):
        identity = v.AXES
        self.assertNotEqual(v.phase(v.move_frame(v.START, (identity, 1))), v.phase(v.START))
        self.assertEqual(v.phase(v.move_frame(v.move_frame(v.START, (identity, 1)), (identity, 1))), v.phase(v.START))


if __name__ == "__main__":
    unittest.main()
