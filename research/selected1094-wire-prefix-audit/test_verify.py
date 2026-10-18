#!/usr/bin/env python3
"""Exact interface models and fail-closed package checks. Apache-2.0.

OpenAI Codex (GPT-6 Astra), substantial AI assistance.
"""
import copy
from fractions import Fraction as Q
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

PACKAGE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("wire_prefix", PACKAGE / "verify.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def apply(matrix, vector):
    return tuple(sum(x*y for x, y in zip(row, vector)) for row in matrix)


def square(vector):
    return sum(x*x for x in vector)


class VerificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context = audit.load()

    def test_rational_hilbert_models(self):
        """Nonidentity, noncommuting within-family unitaries at every boundary."""
        matrices = [((Q(1), Q(0)), (Q(0), Q(1))),
                    ((Q(3, 5), Q(-4, 5)), (Q(4, 5), Q(3, 5))),
                    ((Q(5, 13), Q(12, 13)), (Q(12, 13), Q(-5, 13))),
                    ((Q(0), Q(1)), (Q(1), Q(0)))]
        vectors = [(Q(1), Q(0)), (Q(0), Q(-1)), (Q(3, 5), Q(4, 5)),
                   (Q(0), Q(0)), (Q(-5, 13), Q(12, 13))]
        for matrix in matrices:
            for i in range(2):
                for j in range(2):
                    self.assertEqual(sum(matrix[k][i]*matrix[k][j] for k in range(2)), int(i == j))
        parent = self.context["parent"]
        source = {e["stage"]: e for e in parent["recipe"] if e["kind"] == "local"}
        table = audit.matrix_boundaries(parent)
        comparisons = 0
        for seed in range(40):
            states = [vectors[(seed + 3*j) % len(vectors)] for j in range(8)]
            for index, event in enumerate(parent["execution_schedule"][:30]):
                # These may be nonidentity helper residuals. Only the norm
                # property is modeled, not the selected physical phase maps.
                states = [apply(matrices[(seed+index+j) % len(matrices)], value)
                          for j, value in enumerate(states)]
                if event["kind"] == "local_cover_sweep":
                    q = source[event["stage"]]
                    x, y = 2*q["pair"], 2*q["pair"]+1
                    unitary = matrices[(seed+index) % len(matrices)]
                    if q["reverse"]:
                        adjoint = tuple(zip(*unitary))
                        image = apply(adjoint, states[y])
                        states[x] = tuple(a-b for a, b in zip(states[x], image))
                    else:
                        image = apply(unitary, states[x])
                        states[y] = tuple(a+b for a, b in zip(states[y], image))
                elif event["kind"] == "bridge":
                    for side in range(2):
                        d, s = 2*event["dst"]+side, 2*event["src"]+side
                        states[d] = tuple(a+event["coefficient"]*b for a, b in zip(states[d], states[s]))
                elif event["kind"] == "terminal":
                    for pair in range(4):
                        x, y = 2*pair, 2*pair+1
                        states[x], states[y] = states[y], tuple(-v for v in states[x])
                for value, bound in zip(states, table[index]):
                    self.assertLessEqual(square(value), bound*bound)
                    comparisons += 1
        self.assertEqual(comparisons, 9600)

    def test_familywise_is_material(self):
        # A unitary on the concatenation of two scalar families need not
        # preserve their maximum individual norm. Same distinction as PR821.
        unitary = ((Q(3, 5), Q(4, 5)), (Q(-4, 5), Q(3, 5)))
        before = (Q(1), Q(1))
        after = apply(unitary, before)
        self.assertEqual(square(before), square(after))
        self.assertGreater(max(map(abs, after)), max(map(abs, before)))

    def test_borrow_witness_by_numeric_execution(self):
        context = self.context
        witness = audit.scalar_borrow_witness(context)
        initial = dict(witness["input_nonzero"])
        values = [Q(initial.get(j, 0)) for j in range(128)]
        recipe = {e["stage"]: e for e in context["parent"]["recipe"] if e["kind"] == "local"}
        for event in context["template"]["execution_schedule"][:witness["event"]]:
            replica = event["replica"]
            if event["kind"] == "local_cover_sweep":
                q = recipe[event["stage"]]
                x, y = 8*replica+2*q["pair"], 8*replica+2*q["pair"]+1
                if q["reverse"]:
                    values[x] -= values[y]
                else:
                    values[y] += values[x]
            elif event["kind"] == "bridge":
                for side in range(2):
                    values[8*replica+2*event["dst"]+side] += (
                        event["coefficient"]*values[8*replica+2*event["src"]+side])
        self.assertEqual(abs(values[witness["family"] // audit.V]), witness["helper_attained"])
        self.assertEqual(values[8*witness["replica"]:8*witness["replica"]+2], [0, 0])
        self.assertGreater(witness["helper_attained"], witness["active_upper"])

    def test_exact_strict_bit_boundary(self):
        self.assertEqual(audit.strict_bits(Q(2)**71 - Q(1, 2)**200), 71)
        self.assertEqual(audit.strict_bits(Q(2)**71), 72)
        self.assertEqual(audit.strict_bits(Q(2)**71 + Q(1, 2)**200), 72)
        with self.assertRaisesRegex(audit.AuditError, "positive envelope"):
            audit.strict_bits(0)

    def test_cosmetic_metadata_does_not_change_the_bound(self):
        template = dict(self.context["template"], note="cosmetic audit annotation")
        self.assertEqual(audit.recount(self.context), audit.recount(self.context, template))

    def test_missing_required_pin_rejected(self):
        pins = json.loads((PACKAGE / "SOURCES.json").read_bytes())
        pins["files"] = [p for p in pins["files"] if p["path"] != audit.CHECKER]
        with tempfile.TemporaryDirectory(prefix="wire-prefix-pins-") as temporary:
            package = Path(temporary)
            (package / "SOURCES.json").write_text(json.dumps(pins))
            with patch.object(audit, "PACKAGE", package):
                with self.assertRaisesRegex(audit.AuditError, "mandatory source inventory"):
                    audit.check_pins()

    def test_source_corruption_rejected(self):
        with tempfile.TemporaryDirectory(prefix="wire-prefix-source-") as temporary:
            root = Path(temporary)
            for name in audit.INPUTS:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(audit.ROOT / name, target)
            target = root / audit.CHECKER
            target.write_bytes(target.read_bytes() + b"\n# source mutation\n")
            with self.assertRaisesRegex(audit.AuditError, "source hash:"):
                audit.check_pins(root)

    def test_optimized_read_only_relocation_without_git(self):
        with tempfile.TemporaryDirectory(prefix="wire-prefix-export-") as temporary:
            root = Path(temporary)
            for name in audit.INPUTS:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(audit.ROOT / name, target)
            package = root / "research" / PACKAGE.name
            shutil.copytree(PACKAGE, package, ignore=shutil.ignore_patterns("__pycache__"))
            files = [p for p in root.rglob("*") if p.is_file()]
            directories = [p for p in root.rglob("*") if p.is_dir()]
            for path in files:
                path.chmod(0o444)
            for path in directories:
                path.chmod(0o555)
            before = {str(p.relative_to(root)): audit.sha(p.read_bytes()) for p in files}
            try:
                run = subprocess.run([sys.executable, "-I", "-O", "-B", str(package / "verify.py")],
                                     cwd=root, capture_output=True, text=True, timeout=240)
                self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
                self.assertIn("conditional_bits=397->112", run.stdout)
                self.assertEqual(before, {str(p.relative_to(root)): audit.sha(p.read_bytes()) for p in files})
                self.assertFalse((root / ".git").exists())
                self.assertFalse(list(root.rglob("__pycache__")))
            finally:
                for path in directories:
                    path.chmod(0o755)
                for path in files:
                    path.chmod(0o644)


if __name__ == "__main__":
    unittest.main(verbosity=2)
