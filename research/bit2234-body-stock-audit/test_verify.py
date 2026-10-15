#!/usr/bin/env python3
"""Independent bounded arithmetic and failure controls for the body-stock note.

The row and wrapper tests below are finite algebraic models of the conditional
contracts, not execution of PR2234's physical caller or a full theorem proof.
Sagar Thakrar, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import bisect
import importlib.util
import itertools
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


PACKAGE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("body_stock_verifier", PACKAGE / "verify.py")
verifier = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verifier)


def inverse_thresholds(count=80):
    """Invert the floor inequality; do not run the verifier's depth recurrence."""
    result = [64]
    for _ in range(count - 1):
        quotient, remainder = divmod(result[-1], 42)
        result.append(64 * (quotient + bool(remainder)))
    return result


THRESHOLDS = inverse_thresholds()


def inverse_depth(n):
    if n >= THRESHOLDS[-1]:
        raise ValueError("outside this independent finite threshold table")
    return bisect.bisect_right(THRESHOLDS, n)


def independent_required(n, w):
    d = inverse_depth(n)
    quotient, remainder = divmod(29 * d, 80)
    return 4096 * w * d + quotient + bool(remainder)


class ArithmeticTests(unittest.TestCase):
    def test_depth_against_all_children_and_inverse_thresholds(self):
        # Independently maximize over all permitted ranks, including the two
        # fallback widths, instead of assuming that rank 42 is the maximizer.
        maximum = [0] * 8192
        for n in range(64, len(maximum)):
            f = n // 64
            children = [r * f for r in range(1, 43)] + [f, f // 2]
            maximum[n] = 1 + max(maximum[child] for child in children)
        for n, expected in enumerate(maximum):
            self.assertEqual(verifier.depth(n), expected, n)
            self.assertEqual(inverse_depth(n), expected, n)
        for d, boundary in enumerate(THRESHOLDS, start=1):
            self.assertEqual(verifier.depth(boundary - 1), d - 1)
            self.assertEqual(verifier.depth(boundary), d)
            self.assertEqual(verifier.depth(boundary + 1), d)

    def test_exact_atom_ceiling_at_distant_integer_power_boundaries(self):
        self.assertEqual(verifier.atom_width(1), 1)
        self.assertEqual(verifier.atom_width(2), 2)
        # These are exact roots by construction, including points separated
        # from the root by one integer that floating arithmetic would erase.
        for base in (2, 3):
            original = base ** 10000
            atom = base ** 17
            self.assertLess((atom - 1) ** 10000, (original - 1) ** 17)
            self.assertGreater((atom + 1) ** 10000, (original + 1) ** 17)
            for delta, expected in ((-1, atom), (0, atom), (1, atom + 1)):
                with self.subTest(base=base, delta=delta):
                    self.assertEqual(verifier.atom_width(original + delta), expected)

    def test_selector_against_exhaustive_admissible_borrowing(self):
        # Exhaustive k, not a second bisection. This includes leaf-only
        # feasibility, infeasible widths, the sharp boundary, and a depth jump.
        widths = list(range(1, 257)) + [245772, 245773, 273158, 300542]
        for e in widths:
            w = 1 if e == 1 else 2  # All these widths have e < 2**20.
            first = None
            became_true = False
            for k in range((e - 1) // 2 + 1):
                expected = k >= independent_required((e - k) // w, w)
                actual = verifier.guard(e, k, w)
                if actual != expected:
                    self.fail(f"guard disagrees with inverse staircase: e={e}, k={k}")
                if became_true and not actual:
                    self.fail(f"feasibility is not an upper interval: e={e}, k={k}")
                if actual and first is None:
                    first = k
                became_true = became_true or actual
            choice = verifier.choose_borrow(e)
            if first is None:
                self.assertIsNone(choice, e)
            else:
                n = (e - first) // w
                self.assertEqual(choice, dict(e=e, w=w, k=first, n=n,
                                              depth=inverse_depth(n)))
                self.assertLessEqual(first, independent_required(e, w))

    def test_sharpness_and_rounding_negative_controls(self):
        e, w = 245772, 2
        maximum = (e - 1) // 2
        d = inverse_depth((e - maximum) // w)
        self.assertEqual((maximum, d), (122885, 15))
        # A weak fit test accepts exactly half the original width.
        weak_k = e // 2
        self.assertEqual(weak_k, independent_required((e - weak_k) // w, w))
        self.assertFalse(verifier.guard(e, weak_k, w))
        # Flooring the logarithmic allowance falsely accepts the strict maximum.
        floored = 4096 * w * d + (29 * d) // 80
        self.assertEqual(floored, maximum)
        self.assertEqual(verifier.upper(d, w), maximum + 1)
        self.assertFalse(verifier.guard(e, maximum, w))
        # n(kmax)=floor((e+2)/4), not floor(e/4), when w=2.
        e = 300542
        n = (e - (e - 1) // 2) // 2
        self.assertEqual(n, 75136)
        self.assertEqual(inverse_depth(n), 16)
        self.assertEqual(inverse_depth(e // 4), 15)

    def test_no_equality_fixed_point_and_strict_overborrowing(self):
        e, q, m = 273158, 15 * 2**78 + 1, 269241600
        depths = {inverse_depth((e - k) // 2) for k in range((e - 1) // 2 + 1)}
        self.assertEqual(depths, {15, 16, 17})
        # Product/Bernoulli bounds give 1/2<P(q)**d<1 at every encountered
        # depth; the integer inequalities certify the actual logarithm cell.
        cells = {}
        for d in depths:
            self.assertLess(2 * d, q - 1)
            self.assertLess(2 * q**5, m**d)
            self.assertLess(m**d, q**6)
            cells[d] = 8192 * d + 6
        for k in range((e - 1) // 2 + 1):
            if k == cells[inverse_depth((e - k) // 2)]:
                self.fail(f"unexpected actual-stock equality fixed point: {k}")
        self.assertEqual(cells[inverse_depth((e - 122886) // 2)], 131078)
        self.assertEqual(cells[inverse_depth((e - 131078) // 2)], 122886)
        choice = verifier.choose_borrow(e)
        self.assertEqual(choice["k"], 122887)
        self.assertEqual(cells[inverse_depth(choice["n"])], choice["k"] - 1)

    def test_prime_certificate_rejects_false_order_witness(self):
        certificate = verifier.prime_certificate()
        self.assertEqual(certificate["q"], 15 * 2**78 + 1)
        self.assertGreater(certificate["q"], 2**80)
        with self.assertRaisesRegex(ValueError, "order witness"):
            verifier.prime_certificate(base=1)
        with self.assertRaisesRegex(ValueError, "form"):
            verifier.prime_certificate(q=15 * 2**78 - 1)

    def test_invalid_integer_domains_are_rejected_under_optimization(self):
        for value in (0, -1, True, 1.5):
            with self.subTest(value=value), self.assertRaises(ValueError):
                verifier.choose_borrow(value)
        for value in (-1, True, 1.5):
            with self.subTest(value=value), self.assertRaises(ValueError):
                verifier.depth(value)


class ConditionalAlgebraTests(unittest.TestCase):
    def test_complete_row_divisibility_for_every_child_rank(self):
        # Reduced N,H keep this an explicit algebra fixture, not a claim to
        # enumerate GL64 or run a physical packet. The actual W,M are retained.
        w_live, m, low_count, high_count = 28416, 269241600, 48, 9
        stock_base = m * low_count * high_count
        self.assertEqual(m // w_live, 9475)
        for n in (64, 127, 128, 447, 448, 3904, 75136):
            d = inverse_depth(n)
            for multiplicity in (1, 2, 7):
                rows = multiplicity * stock_base**d
                packet_count = w_live * low_count * high_count
                unused, remainder = divmod(rows, packet_count)
                self.assertEqual(remainder, 0)
                self.assertEqual(unused, multiplicity * 9475 * stock_base**(d - 1))
                f = n // 64
                for child in [rank * f for rank in range(1, 43)] + [f, f // 2]:
                    child_stock = stock_base**inverse_depth(child)
                    self.assertEqual(unused % child_stock, 0, (n, child, multiplicity))
        # Keeping only a complete high field does not replace fresh row stock.
        self.assertNotEqual(high_count % stock_base, 0)
        # Padding need not divide the genuine row count, and its actual padded
        # multiplicity is allowed by the same row-uniform contract.
        for required in (1, 3, 7, 12, stock_base**2):
            genuine = 1
            while genuine < required:
                genuine *= 3
            padded = ((genuine + required - 1) // required) * required
            self.assertEqual(padded % required, 0)
            self.assertGreaterEqual(padded, genuine)
            self.assertLess(padded, 2 * genuine)

    def test_toy_full_ordinary_wrapper_with_remainder_and_restored_padding(self):
        # Binary toy: e=7, k=2, w=2, two 4-valued atoms and one remainder
        # digit per body. Row stock S=3 pads four genuine rows to six. This
        # checks endpoint algebra on every padded address; no tapes are run.
        radix, genuine_rows, padded_rows, body_size = 4, 4, 6, 32

        def atom_vector(value):
            return (value % radix, value // radix)

        def ordinary(row, head, tail, corrupt_rows=False):
            tail = tuple((y - x) % radix for x, y in zip(head, tail))
            head, tail = tail[::-1], head[::-1]  # F_I.
            row = (row + int(corrupt_rows)) % padded_rows
            tail = tuple((y + x) % radix for x, y in zip(head, tail))
            head, tail = tail[::-1], head[::-1]  # Second F_I, same stock.
            row = (row + int(corrupt_rows)) % padded_rows
            tail = tuple((x - y) % radix for x, y in zip(head, tail))
            return row, head, tail

        domains = (range(padded_rows), range(genuine_rows), range(body_size),
                   range(body_size), range(2))
        for row, tail_hi, head_body, tail_body, gap in itertools.product(*domains):
            head_atoms, head_rem = divmod(head_body, 2)
            tail_atoms, tail_rem = divmod(tail_body, 2)
            restored, head_out, tail_out = ordinary(
                row, atom_vector(head_atoms), atom_vector(tail_atoms))
            new_head_body = 2 * (head_out[0] + radix * head_out[1]) + tail_rem
            new_tail_body = 2 * (tail_out[0] + radix * tail_out[1]) + head_rem
            self.assertEqual((restored, new_head_body, new_tail_body),
                             (row, tail_body, head_body))
            if row < genuine_rows:
                # Restrict to the genuine subset, then exchange the high parts.
                completed = (tail_hi * body_size + new_head_body,
                             gap, restored * body_size + new_tail_body)
                self.assertEqual(completed, (tail_hi * body_size + tail_body,
                                             gap, row * body_size + head_body))
        # A permutation of padded rows alone is insufficient: a caller that
        # rotates rows at each return still permutes the full padded domain,
        # but its two-call wrapper sends some genuine rows into padded rows.
        corrupted = {ordinary(row, (0, 1), (2, 3), True)[0]
                     for row in range(genuine_rows)}
        self.assertNotEqual(corrupted, set(range(genuine_rows)))
        self.assertTrue(any(row >= genuine_rows for row in corrupted))


class PublicCLITests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="body-stock-tests-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.package = self.root / "research" / PACKAGE.name
        shutil.copytree(PACKAGE, self.package,
                        ignore=shutil.ignore_patterns("__pycache__", ".scratch"))
        source = PACKAGE.parent.parent / "certificates" / "selected-result.json"
        destination = self.root / "certificates" / "selected-result.json"
        destination.parent.mkdir()
        shutil.copyfile(source, destination)

    def run_cli(self, optimized, *arguments):
        command = [sys.executable, "-I", "-B"]
        if optimized:
            command.append("-O")
        command.extend([str(self.package / "verify.py"), "--package", str(self.package)])
        command.extend(map(str, arguments))
        return subprocess.run(command, cwd=self.root, capture_output=True, text=True,
                              timeout=20, check=False)

    def assert_failure(self, process, phrase):
        self.assertNotEqual(process.returncode, 0, process.stdout + process.stderr)
        self.assertIn(phrase, process.stdout + process.stderr)
        self.assertNotIn("PASS_BIT2234_BODY_STOCK", process.stdout)

    def test_positive_replay_and_external_receipt_are_exact(self):
        stored_path = self.package / "RESULT.json"
        original = stored_path.read_bytes()
        for optimized in (False, True):
            with self.subTest(optimized=optimized):
                process = self.run_cli(optimized)
                self.assertEqual(process.returncode, 0, process.stderr)
                self.assertIn("PASS_BIT2234_BODY_STOCK", process.stdout)
                external = self.root / f"fresh-{optimized}.json"
                process = self.run_cli(optimized, "--write-receipt", external)
                self.assertEqual(process.returncode, 0, process.stderr)
                self.assertEqual(json.loads(external.read_text()), json.loads(original))
                self.assertEqual(stored_path.read_bytes(), original)
                self.assert_failure(self.run_cli(optimized, "--write-receipt", external),
                                    "File exists")
                self.assert_failure(self.run_cli(optimized, "--write-receipt", stored_path),
                                    "external receipt path")
                internal = self.package / "new-receipt.json"
                self.assert_failure(self.run_cli(optimized, "--write-receipt", internal),
                                    "external receipt path")
                self.assertFalse(internal.exists())

    def test_source_corruption_is_rejected_before_receipt_acceptance(self):
        files = [(self.package / "sources" / "pr2234" / "PROOF.md", "retained source"),
                 (self.root / "certificates" / "selected-result.json", "live input")]
        for path, phrase in files:
            original = path.read_bytes()
            try:
                path.write_bytes(original + b"\ncorruption control\n")
                for optimized in (False, True):
                    with self.subTest(path=path.name, optimized=optimized):
                        self.assert_failure(self.run_cli(optimized), phrase + " SHA256 mismatch")
            finally:
                path.write_bytes(original)

    def test_receipt_corruption_and_type_drift_fail_closed(self):
        path = self.package / "RESULT.json"
        original = path.read_bytes()
        for field, value in (("cutoff", 245772), ("schema_version", True),
                             ("cutoff", 245773.0)):
            modified = json.loads(original)
            modified[field] = value
            path.write_text(json.dumps(modified))
            changed = path.read_bytes()
            for optimized in (False, True):
                with self.subTest(field=field, value=value, optimized=optimized):
                    self.assert_failure(self.run_cli(optimized), "stored receipt mismatch")
                    self.assertEqual(path.read_bytes(), changed, "replay rewrote a bad receipt")

    def test_missing_receipt_is_not_regenerated(self):
        path = self.package / "RESULT.json"
        path.unlink()
        for optimized in (False, True):
            with self.subTest(optimized=optimized):
                self.assert_failure(self.run_cli(optimized), "RESULT.json")
                self.assertFalse(path.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
