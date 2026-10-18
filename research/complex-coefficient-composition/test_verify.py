"""Independent coefficient columns, pricing and provenance failure controls.

Prepared for Gareth Davidson (@bitplane) with substantial OpenAI Codex
assistance. Apache-2.0. Run with python3 -B -I test_verify.py.
"""

import gzip
import importlib.util
import json
import shutil
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("signed_horner_verify", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)
lowering = verify.load_lower()
TARGET, SOURCE, WORK = ("T", 0), ("S", 0), ("W", 0)


def flat_column(chain, initial, registers=(TARGET, SOURCE, WORK)):
    """A separate scalar-column interpreter; no sparse-row checker imports."""
    slots = {r: i for i, r in enumerate(registers)}
    vector = list(map(Fraction, initial))
    peak = max(map(abs, vector))
    for instruction in chain:
        tag, register = instruction[:2]
        i = slots[register]
        if tag == "clear":
            vector[i] = Fraction(0)
        elif tag == "copy":
            vector[i] = vector[slots[instruction[2]]]
        elif tag == "double":
            vector[i] *= 2
        elif tag == "halve":
            vector[i] /= 2
        elif tag == "negate":
            vector[i] = -vector[i]
        elif tag == "add":
            vector[i] += vector[slots[instruction[2]]]
        elif tag == "subtract":
            vector[i] -= vector[slots[instruction[2]]]
        else:
            raise ValueError(tag)
        peak = max(peak, abs(vector[i]))
    return vector, peak


def macro(q):
    return ["add", list(TARGET), list(SOURCE), q.numerator, q.denominator]


class CircuitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.expected = verify.read(HERE / "EXPECTED.json")

    def test_all_selected_coefficients_by_separate_columns(self):
        certificates = self.expected["coefficient_certificates"]
        self.assertEqual(len(certificates), 686)
        for entry in certificates:
            q = Fraction(entry["coefficient"])
            chain = lowering.lower(macro(q))
            for initial, expected in [
                ((1, 0, 0), (1, 0, 0)),
                ((0, 1, 0), (q, 1, 0)),
                ((0, 0, 1), (0, 0, 0)),
            ]:
                actual, _ = flat_column(chain, initial)
                self.assertEqual(actual, list(expected), str(q))

    def test_signed_expansion_and_power_boundaries(self):
        domain = set(range(1, 513))
        for bits in range(2, 65):
            domain.update((2**bits - 1, 2**bits, 2**bits + 1))
        for n in sorted(domain):
            digits = lowering.signed_digits(n)
            self.assertEqual(sum(d * 2**k for k, d in enumerate(reversed(digits))), n)
            self.assertEqual(digits[0], 1)
            self.assertTrue(all(d in (-1, 0, 1) for d in digits))
            self.assertTrue(all(not (a and b) for a, b in zip(digits, digits[1:])))
            for sign, denominator in ((1, 1), (-1, 8)):
                q = Fraction(sign * n, denominator)
                chain = lowering.lower(macro(q))
                actual, _ = flat_column(chain, (7, 3, 11))
                self.assertEqual(actual, [7 + 3*q, 3, 0])
                self.assertLessEqual(len(chain), len(lowering.reference.lower(macro(q))))

    def test_independent_cost_census(self):
        # Recount binary costs from its closed formula, not vendor.lower.
        for provider in ("ck", "jp8"):
            programs = verify.read(verify.ROOT / verify.PROVIDERS / provider / "LOCAL-PROGRAMS.json.gz")
            for orientation, events in programs.items():
                baseline = saving = changed = 0
                for event in events:
                    if event[0] != "scalar":
                        continue
                    op = event[1]
                    if op[0] in ("clear", "copy"):
                        cost = 1
                    else:
                        q = Fraction(*op[-2:])
                        a, b = abs(q.numerator), q.denominator
                        if op[0] == "scale":
                            cost = abs(a.bit_length() - b.bit_length()) + int(q < 0)
                        elif abs(q) == 1:
                            cost = 2
                        else:
                            cost = a.bit_length() + a.bit_count() + b.bit_length()
                    candidate = len(lowering.lower(op))
                    baseline += 2*cost
                    saving += 2*(cost-candidate)
                    changed += cost > candidate
                result = self.expected["programs"][provider + "/" + orientation]
                self.assertEqual(baseline, result["real_component_primitives"]["pr696"])
                self.assertEqual(saving, result["saved_beyond_pr696"])
                self.assertEqual(changed, result["changed_macros"])

    def test_ties_keep_binary_and_signed_wins_are_real(self):
        for q in (Fraction(1), Fraction(-1), Fraction(7, 8), Fraction(8)):
            self.assertEqual(lowering.lower(macro(q)), lowering.reference.lower(macro(q)))
        q = Fraction(2**25 - 1)
        chain = lowering.lower(macro(q))
        self.assertEqual(len(lowering.reference.lower(macro(q))) - len(chain), 22)
        self.assertIn(("subtract", WORK, SOURCE), chain)

    def test_endpoint_neutral_peak_is_rejected_for_peak(self):
        q = Fraction(31, 8)
        word = lowering.lower(macro(q))
        i = next(i for i, e in enumerate(word) if e[0] == "subtract")
        bad = word[:i] + [("double", WORK), ("halve", WORK)] + word[i:]
        self.assertEqual(len(bad), len(lowering.reference.lower(macro(q))))
        for initial in ((1, 0, 0), (0, 1, 0), (0, 0, 1)):
            self.assertEqual(flat_column(bad, initial)[0], flat_column(word, initial)[0])
        self.assertGreater(flat_column(bad, (0, 1, 0))[1], 2*31+1)
        with self.assertRaisesRegex(ValueError, "prefix allowance"):
            verify.coefficient_check(q, bad, len(bad))

    def test_mathematical_negative_controls(self):
        self.assertEqual(len(verify.negative_controls(lowering)), 21)

    def test_shared_blocks_by_independent_columns(self):
        counts = {}
        for provider in ("ck", "jp8"):
            programs = verify.read(verify.ROOT / verify.PROVIDERS / provider / "LOCAL-PROGRAMS.json.gz")
            for orientation, events in programs.items():
                count = 0
                flattened = []
                for _, block in lowering.blocks(events):
                    flattened.extend(block)
                    if len(block) < 2:
                        continue
                    count += 1
                    registers = sorted({tuple(e[1][i]) for e in block for i in (1, 2)} | {WORK})
                    slots = {r: i for i, r in enumerate(registers)}
                    chain = lowering.lower_block(block)
                    for column in range(len(registers)):
                        initial = [Fraction(int(i == column)) for i in range(len(registers))]
                        expected = initial.copy()
                        for _, op, _ in block:
                            expected[slots[tuple(op[1])]] += Fraction(*op[-2:]) * expected[slots[tuple(op[2])]]
                        expected[slots[WORK]] = 0
                        self.assertEqual(flat_column(chain, initial, registers)[0], expected)
                self.assertEqual(flattened, events)
                counts[provider + "/" + orientation] = count
        self.assertEqual(counts, {"ck/forward": 946, "ck/backward": 0,
                                  "jp8/forward": 999, "jp8/backward": 0})

    def test_separate_grouping_and_nonadditive_bill(self):
        # Reconstruct maximal runs directly from the event text, independently
        # of lower.blocks, and price sharing by deleting repeated preparations.
        for provider in ("ck", "jp8"):
            programs = verify.read(verify.ROOT / verify.PROVIDERS / provider / "LOCAL-PROGRAMS.json.gz")
            for orientation, events in programs.items():
                expected = self.expected["programs"][provider + "/" + orientation]
                indices, run, previous, phase = [], [], None, None
                saving = selected_saving = 0
                for i, event in enumerate(events + [["phase", "end"]]):
                    key = None
                    if event[0] == "phase":
                        phase = event[1]
                    if phase == "full_frame_cleanup" and event[0] == "scalar" and event[2] == 1:
                        op = event[1]
                        if op[0] == "add" and abs(Fraction(*op[-2:])) != 1:
                            key = (tuple(op[2]), abs(Fraction(*op[-2:])))
                    if key is None or key != previous:
                        if len(run) >= 2:
                            first = events[run[0]][1]
                            indices.append((run[0], len(run)))
                            saving += 2*(len(run)-1)*(len(lowering.lower(first))-1)
                            selected_saving += 2*(len(run)-1)*(verify.selected_cost(first)-1)
                        run = []
                    if key is not None:
                        run.append(i)
                    previous = key
                self.assertEqual(indices, [(r[0], r[1]) for r in expected["sharing_groups"]])
                self.assertEqual(saving, expected["saved_by_sharing_after_signed"])
                self.assertEqual(selected_saving-saving, expected["naive_additive_overstatement"])
        jp = self.expected["programs"]["jp8/forward"]
        self.assertEqual(jp["real_component_primitives"]["selected_shared"], 237544)
        self.assertEqual(jp["naive_additive_overstatement"], 4194)

    def test_event_boundaries_prevent_sharing(self):
        a = ["scalar", ["add", ["T", 0], ["S", 0], 31, 8], 1]
        b = ["scalar", ["add", ["T", 1], ["S", 0], -31, 8], 1]
        for gap in (["climb", "full_frame_cleanup", 0, 0, 1, 9],
                    ["phase", "done"], ["scalar", b[1], 0]):
            events = [["phase", "full_frame_cleanup"], a, gap, b]
            self.assertTrue(all(len(block) == 1 for _, block in lowering.blocks(events)))

    def test_recompressed_sources_and_corrupted_source(self):
        pins = verify.read(HERE / "SOURCE-PINS.json")
        with tempfile.TemporaryDirectory(prefix="signed horner sources ") as tmp:
            root = Path(tmp)
            for entry in pins["files"]:
                path = root / entry["path"]
                path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(verify.ROOT / entry["path"], path)
                if entry["encoding"] == "gzip-payload":
                    path.write_bytes(gzip.compress(gzip.decompress(path.read_bytes()), compresslevel=1, mtime=17))
            verify.source_check(root)
            path = root / verify.PROVIDERS / "jp8" / "LOCAL-PROGRAMS.json.gz"
            data = json.loads(gzip.decompress(path.read_bytes()))
            data["forward"].pop()
            path.write_bytes(gzip.compress(json.dumps(data).encode()))
            with self.assertRaisesRegex(ValueError, "source hash"):
                verify.source_check(root)


if __name__ == "__main__":
    unittest.main(verbosity=2)
