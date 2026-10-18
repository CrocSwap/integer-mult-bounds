"""Acceptance-boundary controls; no full tensor replay is duplicated here."""
import copy
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import verify as v


class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw, cls.word, cls.records = v.source_inputs()
        cls.recipe = v.bind(cls.word, cls.records)[0]
        cls.plans = tuple(v.plan(cls.recipe[side], 1) for side in ("left", "right"))

    def test_literal_event_and_native_binding(self):
        for index, field, replacement in ((2032, 2, "D31"), (2034, 3, "1"), (2039, 1, "D31")):
            word = copy.deepcopy(self.word)
            word["program"][index][field] = replacement
            with self.assertRaisesRegex(ValueError, "fifteen-event"):
                v.bind(word, self.records)
        records = copy.deepcopy(self.records)
        row = next(x for x in records["transports"] if 2031 in x["events"])
        row["events"].remove(2031)
        with self.assertRaisesRegex(ValueError, "unique native"):
            v.bind(self.word, records)

    def test_predecessor_lambda1_calibration(self):
        # Explicitly credited source execution, only for this control. Neither
        # independent multiplicity-two evaluator imports predecessor code.
        old = {}
        source = self.raw["research/p104-reversible-lifting/lifting.py"]
        exec(compile(source, "authenticated PR3025 lifting.py", "exec"), old)
        for mode in ("rounding", "promoted", "cancellation", "zero"):
            sources, query, f, beta = v.fixture(1, mode)
            expected = old["collector"](sources, query, f, beta,
                                         old["plan"](self.recipe["left"]), old["plan"](self.recipe["right"]))
            actual = v.execute(sources, query, f, beta, self.plans, 1)
            for key in ("grid", "query", "sent", "private", "entrance"):
                self.assertEqual(actual[key], expected[key], (mode, key))

    def test_query_promotion_is_observable(self):
        sources, query, f, beta = v.fixture(1, "cancellation")
        got = v.execute(sources, query, f, beta, self.plans, 1)
        self.assertGreater(got["grid"], f)
        wrong = [(a+c, b+d) for (a, b), (c, d) in zip(query, got["sent"], strict=True)]
        self.assertNotEqual(wrong, got["query"])

    def test_corrupted_private_return_rejected(self):
        # The return is tested against the entire gathered input, not a digest.
        original = v.native
        def corrupt(values, plans, rank, inverse=False, order=None):
            out = original(values, plans, rank, inverse, order)
            if inverse:
                a, b = out[0]
                out[0] = (a+1, b)
            return out
        v.native = corrupt
        try:
            sources, query, f, beta = v.fixture(1, "cancellation")
            with self.assertRaisesRegex(ValueError, "paired return"):
                v.execute(sources, query, f, beta, self.plans, 1)
        finally:
            v.native = original

    def test_signed_floor_and_wrong_phase(self):
        # Replacing floor by truncation changes an actual negative-odd pair.
        a, b = (-1, 0), (0, 0)
        dr, di = -1, 0
        sr, si = int(dr/2), int(di/2)
        dr, di = -di, dr
        br, bi = sr-int(dr/2), si-int(di/2)
        self.assertNotEqual(((br+dr, bi+di), (br, bi)), v.pair(a, b))
        values = [(j+1, 0) for j in range(512)]
        wrong = copy.deepcopy(self.recipe["right"])
        wrong["phase"] = (wrong["phase"]+1) % 4
        self.assertNotEqual(v.apply_plan(values, v.plan(wrong, 1)), v.apply_plan(values, self.plans[1]))

    def test_typed_receipt_and_duplicate_keys(self):
        expected = dict(grid=3, private_zero=True, query_sha256="first")
        v.compare_receipt(dict(reversed(list(expected.items()))), expected)
        for key, value in (("grid", 4), ("private_zero", 1), ("query_sha256", "second")):
            changed = dict(expected, **{key: value})
            with self.assertRaisesRegex(ValueError, "typed receipt"):
                v.compare_receipt(changed, expected)
        with self.assertRaisesRegex(ValueError, "duplicate"):
            v.read_json('{"value": 1, "value": 1}')

    def test_source_corruption_rejects_before_execution(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for path, raw in self.raw.items():
                target = root/path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(raw)
            changed = root/"research/p104-rounded-collector/inputs/WORD.json"
            changed.write_bytes(changed.read_bytes()+b"\n")
            original = v.ROOT
            v.ROOT = root
            try:
                with self.assertRaisesRegex(ValueError, "source hash"):
                    v.source_inputs()
            finally:
                v.ROOT = original

    def test_actual_optimized_cli(self):
        result = subprocess.run([sys.executable, "-I", "-O", "-B", str(HERE/"verify.py"), "--quick"],
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS_P104_TENSOR_COLLECTOR_AUDIT", result.stderr)


if __name__ == "__main__":
    unittest.main()
