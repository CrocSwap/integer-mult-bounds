# SPDX-License-Identifier: Apache-2.0
"""Semantic controls for the independent fixed-inventory certificate.

The mutable fixtures deliberately bypass source-byte authentication so each
negative control reaches a mathematical or typed-input obligation.  Predecessor
implementations are never imported.  unittest assertions remain active under -O.
"""

from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from itertools import product
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
import uniform
import verify


class UniformCertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.certificate = json.loads((PACKAGE / "inputs/RELAX-CAP.json").read_text())
        cls.profile = json.loads((PACKAGE / "inputs/PROFILE.json").read_text())

    def reject(self, certificate=None, profile=None, message=None):
        with self.assertRaisesRegex(ValueError, message or "."):
            uniform.verify_certificate(
                self.certificate if certificate is None else certificate,
                self.profile if profile is None else profile,
            )

    def test_pinned_positive_certificate(self):
        result = uniform.verify_certificate(self.certificate, self.profile)
        self.assertEqual(result["status"], "PASS_UNIFORM_PAIRED_CAP_OPTIMALITY")
        self.assertEqual((result["patterns"], result["tight_count"], result["strict_count"]),
                         (1163, 11, 1152))
        self.assertEqual(result["primal"]["complete_profile"], self.profile)
        self.assertGreater(Q(result["minimum_uniform_slack_lower"]), 0)
        self.assertLess(Q(result["endpoint_moments"]["lower"]["moment_upper"]), 1)
        self.assertGreater(Q(result["endpoint_moments"]["upper"]["moment_lower"]), 1)

    def test_catalogue_by_independent_cartesian_enumeration(self):
        # The production enumeration spends remaining capacity recursively.
        # This deliberately larger Cartesian box filters only at the end.
        widths = (4, 5, 7, 8, 9)
        expected = set()
        for capacity in (8, 16, 32, 48):
            for counts in product(*(range(capacity // width + 1) for width in widths)):
                used = sum(width * count for width, count in zip(widths, counts))
                if used <= capacity:
                    expected.add((capacity, counts, capacity - used))
        actual = uniform.enumerate_patterns()
        self.assertEqual(len(actual), len(set(actual)))
        self.assertEqual(set(actual), expected)
        self.assertEqual(Counter(capacity for capacity, _, _ in actual),
                         {8: 6, 16: 27, 32: 215, 48: 915})

    def test_symbolic_rank_mass_conservation(self):
        # At b=0, H_r(0)=r and every allocation has the same idle rank mass.
        # Thus every symbolic reduced cost vanishes after substituting H_r=r.
        _, costs = uniform.reduced_costs(self.certificate)
        self.assertEqual(len(costs), 1163)
        for pattern, coefficients in costs:
            with self.subTest(pattern=pattern):
                self.assertEqual(sum(rank * value for rank, value in coefficients.items()), 0)

    def test_capacity_and_width_domain(self):
        for width, message in ((4, "basis capacity exceeded"),
                               (6, "basis width domain")):
            certificate = deepcopy(self.certificate)
            certificate["basis_patterns"][0]["widths"].append(width)
            with self.subTest(width=width):
                self.reject(certificate, message=message)

    def test_duplicate_and_distinct_singular_basis(self):
        duplicate = deepcopy(self.certificate)
        duplicate["basis_patterns"][1] = deepcopy(duplicate["basis_patterns"][0])
        self.reject(duplicate, message="duplicate basis pattern")
        singular = deepcopy(self.certificate)
        # All four capacity classes and all nine distinct patterns remain.
        # These nine columns have rank eight, independent of stored counts.
        singular["basis_patterns"][1] = {
            "capacity": 32, "widths": [], "count_per_replica": "1"
        }
        self.reject(singular, message="basis matrix is singular")

    def test_declared_multiplicity_controls(self):
        for count in ("673", "1/2", "-1", -1, True, 672.0):
            certificate = deepcopy(self.certificate)
            certificate["basis_patterns"][0]["count_per_replica"] = count
            with self.subTest(count=repr(count)):
                self.reject(certificate)

    def test_profile_identity_stronger_than_rank_mass(self):
        changed = deepcopy(self.profile)
        changed["3"] -= 1
        changed["1"] += 1
        changed["2"] += 1
        mass = lambda profile: sum(int(rank) * count for rank, count in profile.items())
        self.assertEqual(mass(changed), mass(self.profile))
        self.reject(profile=changed, message="literal complete profile equals primal profile")

    def test_histogram_and_pattern_integer_types(self):
        for value in (True, 1.5, "1", 0, -1):
            certificate = deepcopy(self.certificate)
            certificate["local_per_call"]["1"] = value
            with self.subTest(field="local", value=repr(value)):
                self.reject(certificate, message="integer domain")
            profile = deepcopy(self.profile)
            profile["1"] = value
            with self.subTest(field="profile", value=repr(value)):
                self.reject(profile=profile, message="integer domain")
        for field, value in (("capacity", True), ("widths", [True]),
                             ("widths", [8.0])):
            certificate = deepcopy(self.certificate)
            certificate["basis_patterns"][0][field] = value
            with self.subTest(field=field, value=repr(value)):
                self.reject(certificate)

    def test_brackets_excluding_root(self):
        for displacement, message in ((-Q(1, 10**8), "upper root endpoint sign"),
                                      (Q(1, 10**8), "lower root endpoint sign")):
            certificate = deepcopy(self.certificate)
            for endpoint in ("cap_lower", "cap_upper"):
                certificate[endpoint] = str(Q(certificate[endpoint]) + displacement)
            with self.subTest(displacement=displacement):
                self.reject(certificate, message=message)

    def test_root_bracket_alone_does_not_certify_uniform_dual(self):
        certificate = deepcopy(self.certificate)
        certificate["cap_lower"], certificate["cap_upper"] = "1/1000000", "1/2"
        self.assertLess(Q(certificate["cap_lower"]), Q(self.certificate["cap_lower"]))
        self.assertGreater(Q(certificate["cap_upper"]), Q(self.certificate["cap_upper"]))
        self.reject(certificate, message="uniform reduced-cost sign")

    def test_positive_binomial_against_exact_rational_powers(self):
        for base, root in ((Q(1), Q(1)), (Q(121, 100), Q(11, 10)),
                           (Q(9, 4), Q(3, 2)), (Q(4), Q(2)), (Q(64), Q(8))):
            with self.subTest(base=base, exponent="1/2"):
                lower, upper = uniform.binomial_power(base, Q(1, 2))
                self.assertIsInstance(lower, Q)
                self.assertIsInstance(upper, Q)
                self.assertLessEqual(lower, root)
                self.assertGreaterEqual(upper, root)
                self.assertLess(upper - lower, Q(1, 10**44))
        for exponent, expected in ((Q(0), Q(1)), (Q(1), Q(73))):
            lower, upper = uniform.binomial_power(Q(73), exponent)
            self.assertLessEqual(lower, expected)
            self.assertGreaterEqual(upper, expected)

    def test_power_input_domains(self):
        # Warm equivalent numeric keys first: memoization must not bypass the
        # public type gate because bool/int/float compare equal in Python.
        uniform.binomial_power(Q(1), Q(1, 2))
        uniform.binomial_power(Q(4), Q(1, 2))
        uniform.binomial_power(Q(2), Q(1))
        for base, exponent in ((True, Q(1, 2)), (Q(2), True),
                               (4.0, Q(1, 2)), (Q(4), 0.5),
                               (Q(1, 2), Q(1, 2)), (Q(74), Q(1, 2)),
                               (Q(2), Q(-1, 2)), (Q(2), Q(3, 2))):
            with self.subTest(base=base, exponent=exponent):
                with self.assertRaises(ValueError):
                    uniform.binomial_power(base, exponent)


class SourceBindingTests(unittest.TestCase):
    @staticmethod
    def mutable_copy(package):
        # Mutation fixtures are writable even when the source export is read-only.
        shutil.copytree(PACKAGE, package, ignore=shutil.ignore_patterns("__pycache__"))
        package.chmod(0o700)
        for path in package.rglob("*"):
            path.chmod(0o700 if path.is_dir() else 0o600)

    def test_frozen_bytes_and_manifest_reject_changes(self):
        for name in ("INPUTS.json", "inputs/RELAX-CAP.json", "inputs/root.py"):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                package = Path(tmp) / "package"
                self.mutable_copy(package)
                target = package / name
                target.write_bytes(target.read_bytes() + b" ")
                with self.assertRaisesRegex(ValueError, "changed"):
                    verify.authenticate(package)

    def test_closed_input_inventory_and_symlinks(self):
        for action in ("extra", "missing", "file_link", "directory_link"):
            with self.subTest(action=action), tempfile.TemporaryDirectory() as tmp:
                package = Path(tmp) / "package"
                self.mutable_copy(package)
                if action == "extra":
                    (package / "inputs/extra.json").write_text("{}")
                elif action == "missing":
                    (package / "inputs/PROFILE.json").unlink()
                elif action == "file_link":
                    target = package / "inputs/PROFILE.json"
                    target.unlink()
                    target.symlink_to(PACKAGE / "inputs/PROFILE.json")
                else:
                    shutil.rmtree(package / "inputs")
                    (package / "inputs").symlink_to(PACKAGE / "inputs", target_is_directory=True)
                with self.assertRaises(ValueError):
                    verify.authenticate(package)

    def test_strict_json(self):
        for payload in ('{"x":1,"x":2}', '{"x":NaN}', '{"x":Infinity}',
                        '{"x":1.0}', '{"x":1e999}'):
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                verify.read_json(payload)

    def test_cli_emit_is_one_complete_json_document(self):
        command = [sys.executable, "-I", "-B", str(PACKAGE / "verify.py"), "--emit"]
        if sys.flags.optimize:
            command.insert(2, "-O")
        run = subprocess.run(command, text=True, capture_output=True, timeout=20, check=True)
        self.assertEqual(run.stderr, "")
        emitted = verify.read_json(run.stdout)
        stored = verify.read_json((PACKAGE / "RESULT.json").read_bytes())
        self.assertEqual(verify.canonical(emitted), verify.canonical(stored))

    def test_cli_rejects_equal_numeric_value_of_wrong_type(self):
        # Python equality treats True == 1; receipt equality must preserve types.
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp) / "package"
            self.mutable_copy(package)
            result_path = package / "RESULT.json"
            result = json.loads(result_path.read_text())
            self.assertEqual(result["schema_version"], 1)
            result["schema_version"] = True
            result_path.write_text(json.dumps(result))
            command = [sys.executable, "-I", "-B", str(package / "verify.py")]
            if sys.flags.optimize:
                command.insert(2, "-O")
            run = subprocess.run(command, text=True, capture_output=True, timeout=20)
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("complete typed receipt differs", run.stderr)


if __name__ == "__main__":
    unittest.main()
