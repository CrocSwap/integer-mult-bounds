#!/usr/bin/env python3
"""Failure-sensitivity checks for this audit, not an additional theorem proof.

Copyright 2026 Ross Richardson. SPDX-License-Identifier: Apache-2.0
Developed with substantial OpenAI Codex assistance.
"""

import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest


PACKAGE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("permutation_audit", PACKAGE / "verify.py")
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)
SOURCE = (PACKAGE / "verify.py").read_text()


def mutant(old, new):
    if SOURCE.count(old) != 1:
        raise ValueError("mutation target is not unique")
    namespace = {"__name__": "permutation_mutant", "__file__": str(PACKAGE / "verify.py")}
    exec(compile(SOURCE.replace(old, new), "<audit-mutation>", "exec"), namespace)
    return namespace


class FailureSensitivity(unittest.TestCase):
    def test_using_permutation_instead_of_inverse_in_matrix_entry(self):
        changed = mutant("self.phase[rho[x]][inverse[z]]", "self.phase[rho[x]][pi[z]]")
        with self.assertRaisesRegex(ValueError, "classification disagreement"):
            changed["census"]((5,))

    def test_treating_every_automorphism_as_admissible(self):
        changed = mutant("return True, symmetric", "return True, True")
        with self.assertRaisesRegex(ValueError, "classification disagreement"):
            changed["census"]((2, 2))

    def test_unweighted_symmetry_on_mixed_moduli(self):
        changed = mutant("columns[i][j] * self.moduli[i]\n"
                         "                        == columns[j][i] * self.moduli[j]",
                         "columns[i][j] == columns[j][i]")
        with self.assertRaisesRegex(ValueError, "classification disagreement"):
            changed["census"]((2, 4))

    def test_wrong_convolution_normalization(self):
        changed = mutant("factor = group.size if", "factor = group.size ** 2 if")
        with self.assertRaisesRegex(ValueError, "direct adjoint convolution failed"):
            changed["census"]((2,))

    def test_missing_forward_fourier_sign(self):
        changed = mutant("for x in u], -1)", "for x in u], 1)")
        with self.assertRaisesRegex(ValueError, "direct adjoint convolution failed"):
            changed["census"]((3,))

    def test_source_relocation_and_corruption(self):
        root = PACKAGE.parents[1]
        source = AUDIT.check_sources(root)
        with tempfile.TemporaryDirectory(prefix="permutation-source-control-") as tmp:
            isolated = Path(tmp)
            for name in source["files"]:
                destination = isolated / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(root / name, destination)
            self.assertEqual(AUDIT.check_sources(isolated), source)
            target = isolated / "upstream/build/sections/07-resampling.tex"
            target.write_bytes(target.read_bytes() + b"\n% mutation control\n")
            with self.assertRaisesRegex(ValueError, "source pin mismatch"):
                AUDIT.check_sources(isolated)

    def test_known_cyclotomic_polynomials_and_orthogonality(self):
        # Independent integer coefficients for every period used by the
        # census, plus the order-nine group's period-three controls.
        known = {2: (1, 1), 3: (1, 1, 1), 4: (1, 0, 1),
                 5: (1, 1, 1, 1, 1), 6: (1, -1, 1),
                 7: (1, 1, 1, 1, 1, 1, 1), 8: (1, 0, 0, 0, 1)}
        for period, polynomial in known.items():
            self.assertEqual(AUDIT.cyclotomic(period), polynomial)
            ring = AUDIT.ExactRoots(period)
            for frequency in range(period):
                total = ring.zero
                for j in range(period):
                    total = ring.add(total, ring.roots[frequency * j % period])
                expected = ring.scale(ring.one, period) if frequency == 0 else ring.zero
                self.assertEqual(total, expected)


if __name__ == "__main__":
    unittest.main(verbosity=2)
