#!/usr/bin/env python3
"""Mutation controls for the historical source-bound replay.

The full historical producer is deliberately not repeated here. Temporary
copies exercise input rejection; tiny producers test subprocess isolation.
"""
import copy
from fractions import Fraction
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import verify


class SourceBindingControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = verify.read_json(verify.MANIFEST.read_bytes())
        cls.blobs, cls.expected = verify.validate_inputs(verify.ROOT, cls.manifest)

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="bit-compression-control-")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        verify.stage_inputs(self.root, self.blobs)

    def old_pins_still_match(self):
        for name, expected_hash in self.expected["source_sha256"].items():
            self.assertEqual(verify.digest((self.root / name).read_bytes()), expected_hash)

    def test_complete_reference_inputs_are_accepted(self):
        blobs, certificate = verify.validate_inputs(self.root, self.manifest)
        self.assertEqual(len(blobs), 32)
        self.assertEqual(len(verify.import_graph(blobs)), 9)
        self.assertEqual(len(certificate["source_sha256"]), 2)

    def test_driver_helper_and_deep_helper_changes_rejected(self):
        for name in (verify.ENTRY, "scripts/shared_point_circuit.py",
                     "scripts/exclusion_circuit.py"):
            with self.subTest(source=name):
                target = self.root / name
                target.write_bytes(self.blobs[name] + b"\n# mutation control\n")
                self.old_pins_still_match()
                with self.assertRaisesRegex(ValueError, "Source hash mismatch"):
                    verify.validate_inputs(self.root, self.manifest)
                target.write_bytes(self.blobs[name])

    def test_changed_deficit_changes_exact_result_but_not_old_pins(self):
        code = """
import json, pathlib, sys, types
sys.path.insert(0, str(pathlib.Path(sys.argv[1]) / 'scripts'))
from shared_point_network import counts
c = types.SimpleNamespace(h=50, additions=450346, outputs=range(58800))
n = counts(50, c)
print(json.dumps({k: str(n[k]) for k in ('D', 'W', 'eta')}))
"""

        def evaluate():
            proc = subprocess.run([sys.executable, "-I", "-S", "-B", "-c", code,
                                   str(self.root)], check=True, capture_output=True,
                                  text=True, encoding="utf-8")
            return json.loads(proc.stdout)

        baseline = evaluate()
        name = "scripts/shared_point_network.py"
        source = self.blobs[name]
        self.assertEqual(source.count(b"D=N-2*L"), 1)
        (self.root / name).write_bytes(source.replace(b"D=N-2*L", b"D=N-2*L+1"))
        changed = evaluate()
        self.assertEqual(int(changed["D"]), int(baseline["D"]) + 1)
        self.assertEqual(changed["W"], baseline["W"])
        self.assertEqual(Fraction(changed["eta"]) - Fraction(baseline["eta"]),
                         Fraction(1, int(baseline["W"]) * 50**3))
        self.old_pins_still_match()
        with self.assertRaisesRegex(ValueError, "Source hash mismatch"):
            verify.validate_inputs(self.root, self.manifest)

    def test_upstream_manifest_and_payload_bytes_are_bound(self):
        for name in ("upstream/manifest.json", "upstream/LICENSE"):
            with self.subTest(source=name):
                (self.root / name).write_bytes(self.blobs[name] + b"\n")
                with self.assertRaisesRegex(ValueError, "Source hash mismatch"):
                    verify.validate_inputs(self.root, self.manifest)
                (self.root / name).write_bytes(self.blobs[name])

    def test_upstream_manifest_cross_check_survives_outer_repin(self):
        manifest = copy.deepcopy(self.manifest)
        name = "upstream/LICENSE"
        changed = self.blobs[name] + b"\nmutation control\n"
        (self.root / name).write_bytes(changed)
        manifest["files"][name] = verify.digest(changed)
        with self.assertRaisesRegex(ValueError, "Missing or changed upstream input"):
            verify.validate_inputs(self.root, manifest)

    def test_historical_source_cross_check_survives_outer_repin(self):
        manifest = copy.deepcopy(self.manifest)
        name = "docs/research/bit-compression-audit.md"
        changed = self.blobs[name] + b"\nmutation control\n"
        (self.root / name).write_bytes(changed)
        manifest["files"][name] = verify.digest(changed)
        with self.assertRaisesRegex(ValueError, "Historical source pin mismatch"):
            verify.validate_inputs(self.root, manifest)

    def test_missing_transitive_pin_rejected_even_with_edited_graph(self):
        for edit_graph in (False, True):
            with self.subTest(edit_graph=edit_graph):
                manifest = copy.deepcopy(self.manifest)
                missing = "scripts/exclusion_circuit.py"
                del manifest["files"][missing]
                if edit_graph:
                    del manifest["local_import_graph"][missing]
                    for dependencies in manifest["local_import_graph"].values():
                        if missing in dependencies:
                            dependencies.remove(missing)
                with self.assertRaises(ValueError):
                    verify.validate_inputs(self.root, manifest)

    def test_deleted_import_edge_is_rejected(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["local_import_graph"]["scripts/paired_exclusion_circuit.py"].remove(
            "scripts/exclusion_circuit.py")
        with self.assertRaisesRegex(ValueError, "Static local import inventory changed"):
            verify.validate_inputs(self.root, manifest)

    def test_unlisted_namespace_initializer_is_not_staged(self):
        initializer = self.root / "scripts/experiments/__init__.py"
        initializer.write_text("raise RuntimeError('unlisted initializer ran')\n",
                               encoding="utf-8")
        blobs, _ = verify.validate_inputs(self.root, self.manifest)
        with tempfile.TemporaryDirectory(prefix="bit-compression-clean-stage-") as directory:
            staged = Path(directory)
            verify.stage_inputs(staged, blobs)
            self.assertFalse((staged / "scripts/experiments/__init__.py").exists())
            self.assertTrue((staged / "scripts/experiments/bit_compression.py").exists())

    def test_changed_fraction_coverage_and_types_are_rejected(self):
        mutations = []
        changed = copy.deepcopy(self.expected)
        changed["target"] = "1/1073741825"
        mutations.append(changed)
        changed = copy.deepcopy(self.expected)
        changed["local_candidates"].pop()
        mutations.append(changed)
        changed = copy.deepcopy(self.expected)
        changed["best_global_frame_check"]["forward_frames_nested"] = 1
        mutations.append(changed)
        for number, changed in enumerate(mutations):
            with self.subTest(mutation=number):
                with self.assertRaisesRegex(ValueError, "Historical certificate payload differs"):
                    verify.compare_certificate(changed, self.expected)

    def test_json_reordering_is_allowed_but_duplicate_keys_are_rejected(self):
        equivalent = dict(reversed(list(self.expected.items())))
        verify.compare_certificate(equivalent, self.expected)
        with self.assertRaisesRegex(ValueError, "Duplicate JSON key"):
            verify.read_json(b'{"outer":{"x":1,"x":2}}')

    def test_nonlocal_paths_are_rejected(self):
        for name in ("../outside", "/outside", "C:/outside", "upstream/../outside",
                     "upstream\\LICENSE", "./upstream/LICENSE"):
            with self.subTest(path=name):
                with self.assertRaisesRegex(ValueError, "Nonlocal input path"):
                    verify.checked_path(self.root, name)


class IsolatedProducerControls(unittest.TestCase):
    @staticmethod
    def inputs(source):
        return {verify.ENTRY: source.encode("utf-8"), verify.CERTIFICATE: b'{"fresh":true}'}

    def test_worker_ignores_environment_and_preserves_assertions(self):
        source = """
import json, pathlib, sys
assert __debug__
assert sys.flags.isolated == 1 and sys.flags.no_site == 1
assert sys.flags.optimize == 0
root = pathlib.Path(__file__).resolve().parents[1]
(root / 'certificates/bit-compression-audit.json').write_text(
    json.dumps({'fresh': True}), encoding='utf-8')
"""
        with tempfile.TemporaryDirectory(prefix="bit-compression-poison-") as directory:
            poison = Path(directory)
            marker = poison / "site-ran.txt"
            (poison / "sitecustomize.py").write_text(
                "from pathlib import Path\nPath(" + repr(str(marker)) + ").touch()\n",
                encoding="utf-8")
            with patch.dict(os.environ, {"PYTHONPATH": str(poison), "PYTHONOPTIMIZE": "2",
                                         "PYTHONHOME": str(poison / "missing-home")}):
                result = verify.replay(self.inputs(source), {"fresh": True})
            self.assertEqual(result["status"], "PASS")
            self.assertFalse(marker.exists())

    def test_success_without_a_fresh_output_is_rejected(self):
        with self.assertRaises((ValueError, FileNotFoundError)):
            verify.replay(self.inputs("pass\n"), {"fresh": True})

    def test_failed_producer_cannot_pass_from_staged_reference(self):
        with self.assertRaisesRegex(ValueError, "Historical producer failed"):
            verify.replay(self.inputs("raise RuntimeError('control failure')\n"), {"fresh": True})

    def test_cli_rejects_optimized_python(self):
        proc = subprocess.run([sys.executable, "-I", "-S", "-B", "-O",
                               str(HERE / "verify.py"), "--check-only"],
                              capture_output=True, text=True, encoding="utf-8")
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("Historical assertions must remain enabled", proc.stderr)


class IndependentArithmeticControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.expected = verify.read_json((verify.ROOT / verify.CERTIFICATE).read_bytes())

    def test_all_historical_rows_pass_independent_arithmetic(self):
        result = verify.arithmetic_check(self.expected)
        self.assertEqual(result["local_rows_checked"], 73)
        self.assertEqual(result["global_rows_checked"], 18)
        self.assertEqual(result["paired_finite_rows_checked"], 36)

    def test_deleted_or_duplicated_coverage_is_rejected(self):
        for family, duplicate in (("local_candidates", False), ("local_candidates", True),
                                  ("global_candidates", False), ("global_candidates", True),
                                  ("paired_finite", False)):
            with self.subTest(family=family, duplicate=duplicate):
                changed = copy.deepcopy(self.expected)
                rows = (changed["paired_template_all_even_h"]["finite"]
                        if family == "paired_finite" else changed[family])
                if duplicate:
                    rows.append(copy.deepcopy(rows[0]))
                else:
                    rows.pop()
                with self.assertRaises(ValueError):
                    verify.arithmetic_check(changed)

    def test_changed_classification_and_role_counts_are_rejected(self):
        for field in ("unshareable", "mandatory_frontier_stars", "side_roles_lower",
                      "necessary_integer_role_budget"):
            with self.subTest(field=field):
                changed = copy.deepcopy(self.expected)
                changed["local_candidates"][0]["optimistic_merging_bound"][field] += 1
                with self.assertRaises(ValueError):
                    verify.arithmetic_check(changed)

    def test_changed_exact_log_derived_fractions_are_rejected(self):
        for field in ("bit_saving_upper", "kappa_upper", "fraction_of_target"):
            with self.subTest(field=field):
                changed = copy.deepcopy(self.expected)
                row = changed["local_candidates"][0]["optimistic_merging_bound"]
                row[field] = str(Fraction(row[field]) + Fraction(1, 10**30))
                with self.assertRaises(ValueError):
                    verify.arithmetic_check(changed)

    def test_changed_best_global_count_is_rejected(self):
        changed = copy.deepcopy(self.expected)
        changed["best_global"]["side_roles"] -= 1
        with self.assertRaises(ValueError):
            verify.arithmetic_check(changed)

    def test_changed_tail_endpoint_or_broadened_scope_is_rejected(self):
        for field, value in (("tail_cutoff", 114),
                             ("scope", "All pair-exclusion circuits at every ground size.")):
            with self.subTest(field=field):
                changed = copy.deepcopy(self.expected)
                changed["paired_template_all_even_h"][field] = value
                with self.assertRaises(ValueError):
                    verify.arithmetic_check(changed)

    def test_false_and_integer_frame_flags_are_rejected(self):
        for field in ("forward_frames_nested", "reverse_complement_frames_nested"):
            for value in (False, 1):
                with self.subTest(field=field, value=value):
                    changed = copy.deepcopy(self.expected)
                    changed["best_global_frame_check"][field] = value
                    with self.assertRaises(ValueError):
                        verify.arithmetic_check(changed)


if __name__ == "__main__":
    unittest.main(verbosity=2)
