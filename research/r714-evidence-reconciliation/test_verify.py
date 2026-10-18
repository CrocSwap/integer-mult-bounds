"""Independent checks of the exact algebra used by the reconciliation."""
from copy import deepcopy
from fractions import Fraction
import gzip
import itertools
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify


def fraction_rank(rows, width):
    rows = [[Fraction(x) for x in row] for row in rows]
    rank = 0
    for col in range(width):
        pivot = next((i for i in range(rank, len(rows)) if rows[i][col]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        denominator = rows[rank][col]
        rows[rank] = [x / denominator for x in rows[rank]]
        for i in range(len(rows)):
            if i != rank:
                factor = rows[i][col]
                rows[i] = [x - factor * y for x, y in zip(rows[i], rows[rank])]
        rank += 1
    return rank


def forward_sets(word, clean_helpers=False):
    """Independent forward representation as sets of input coordinates."""
    v, n = word["v"], 2 * word["v"] + word["R"]
    values = [{i} if not clean_helpers or i < 2 * v else set() for i in range(n)]

    def run(phase):
        for _, dest, sources in word[phase]:
            for source in sources:
                values[dest].symmetric_difference_update(values[source])

    run("D")
    run("A")
    copies = [values[i].copy() for i in word["ret"]]
    for target, indices in enumerate(word["scatter"]):
        for index in indices:
            values[v + target].symmetric_difference_update(copies[index])
    run("B")
    run("C")
    return values


class ExactAlgebraTests(unittest.TestCase):
    def test_integer_span_against_fraction_rank(self):
        vectors = list(itertools.product((-1, 0, 1), repeat=2))
        for pair in itertools.product(vectors, repeat=2):
            basis = verify.rational_basis(pair)
            rank = fraction_rank(pair, 2)
            self.assertEqual(len(basis), rank)
            for vector in vectors:
                self.assertEqual(verify.contains(basis, (vector,)),
                                 fraction_rank(pair + (vector,), 2) == rank)
        # Integer elimination must preserve Q-span, not just an F2 shadow.
        self.assertEqual(len(verify.rational_basis(((1, 1), (1, -1)))), 2)
        self.assertTrue(verify.contains(verify.rational_basis(((2, 0),)), ((1, 0),)))

    @classmethod
    def setUpClass(cls):
        verify.check_sources(verify.ROOT)
        cls.raw, _, _ = verify.check_archive(verify.ROOT)
        cls.mixed = verify.read_json(verify.ROOT / verify.FOLLOWUP / "precursor/MIXED.json")

    def test_both_words_by_independent_forward_sets(self):
        for word in (self.raw, self.mixed):
            v, n = word["v"], 2 * word["v"] + word["R"]
            expected = [{i, i - v} if v <= i < 2 * v else {i} for i in range(n)]
            self.assertEqual(forward_sets(word), expected)
            self.assertEqual(verify.check_adjoint(word), 954)

    def test_dirty_compensation_control_would_escape_clean_only_replay(self):
        word = deepcopy(self.raw)
        word["D"] = []
        v, n = word["v"], 2 * word["v"] + word["R"]
        expected_clean = [{i} if i < v else {i, i - v} if i < 2 * v else set()
                          for i in range(n)]
        self.assertEqual(forward_sets(word, clean_helpers=True), expected_clean)
        self.assertNotEqual(forward_sets(word), forward_sets(self.raw))
        with self.assertRaisesRegex(verify.Rejected, "F2 adjoint: input register 240"):
            verify.check_adjoint(word)

    def test_zero_move_retiming_means_two_distinct_words(self):
        packed = verify.ROOT / verify.FOLLOWUP / "precursor/PRECURSOR.json.gz"
        retimed = verify.json.loads(gzip.decompress(packed.read_bytes()))
        self.assertEqual(self.mixed, retimed)
        self.assertNotEqual(verify.canonical_sha(self.raw), verify.canonical_sha(self.mixed))


if __name__ == "__main__":
    unittest.main()
