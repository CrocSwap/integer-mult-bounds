# SPDX-License-Identifier: Apache-2.0
"""Behavioral controls for the necessary dependency test."""

import copy
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from itertools import combinations
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("completion_flow", PACKAGE / "verify.py")
flow = importlib.util.module_from_spec(spec)
spec.loader.exec_module(flow)


def tiny_spaces():
    spaces = {frozenset({0})}
    for size in range(1, 4):
        for basis in combinations(range(1, 8), size):
            points = {0}
            for vector in basis:
                points |= {p ^ vector for p in tuple(points)}
            spaces.add(frozenset(points))
    return sorted(spaces, key=lambda space: (len(space), sorted(space)))


def command(package, script="verify.py", *args):
    return subprocess.run(
        [sys.executable, "-I", "-O", "-Werror", "-B", str(package / script), *args],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )


def export(root):
    package = root / "research/p104-endpoint-completion-flow"
    shutil.copytree(PACKAGE, package, ignore=shutil.ignore_patterns("__pycache__"))
    for name in flow.INPUTS:
        destination = root / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(flow.ROOT / name, destination)
    return package


class FlowTests(unittest.TestCase):
    def test_contact_against_all_small_subspaces(self):
        spaces = tiny_spaces()
        self.assertEqual(len(spaces), 16)
        intervals = [(a, b) for a in spaces for b in spaces if a <= b]
        checked = 0
        for left in intervals:
            for right in intervals:
                for d in range(4):
                    expected = any(
                        len(v) == 1 << d
                        and left[0] <= v <= left[1]
                        and right[0] <= v <= right[1]
                        for v in spaces
                    )
                    self.assertEqual(flow.contact(left, right, d), expected)
                    checked += 1
        self.assertGreater(checked, 10_000)

    def test_relay_and_direct_source_access(self):
        bases = ([1, 2, 4, 8, 16, 32, 64, 128, 256], [2, 1, 4, 8, 16, 32, 128, 64, 256])
        planes = [{d: flow.span(basis[:d]) for d in flow.FIXED} for basis in bases]
        paths = {f"X{s}": [flow.span([256])] for s in range(104)}
        paths.update({f"Y{t}": [flow.span([])] for t in range(104)})
        paths["X0"] = [flow.span([1])]
        paths["Y0"] = [planes[1][7]]
        outputs, _ = flow.dependency_graph(planes, paths)
        self.assertEqual(outputs[0], 1)
        # A source at a later layer cannot flow backwards to a target line.
        paths["X0"], paths["Y0"] = [planes[0][8]], [flow.span([1])]
        outputs, _ = flow.dependency_graph(planes, paths)
        self.assertEqual(outputs[0], 0)
        # Include direct X-to-Y contacts, even without a usable helper contact.
        paths["X0"] = paths["Y0"] = [flow.span([256])]
        outputs, _ = flow.dependency_graph(planes, paths)
        self.assertEqual(outputs[0], (1 << 104) - 1)

    def test_real_inputs_and_changed_intermediate_basis(self):
        certificate, word, fixture = flow.inputs()
        result = flow.compute(certificate, word, fixture)
        self.assertEqual(result["unreachable_required_pairs"], 3095)
        self.assertEqual(
            result["witness"],
            {
                "source": 4,
                "target": 0,
                "required_coefficient": "-1/2",
                "optimistic_coefficient": "0",
            },
        )
        changed = copy.deepcopy(certificate)
        for row in changed["helpers"]:
            row["basis"][2], row["basis"][3] = row["basis"][3], row["basis"][2]
        self.assertEqual(flow.compute(changed, word, fixture), result)
        changed["helpers"][0]["basis"][0] = True
        with self.assertRaisesRegex(ValueError, "vector domain"):
            flow.compute(changed, word, fixture)

    def test_both_actual_clis_and_emitted_receipt(self):
        for script, marker in (
            ("verify.py", "PASS_P104_ENDPOINT_COMPLETION_FLOW"),
            ("independent.py", "PASS_P104_ENDPOINT_COMPLETION_FLOW_INDEPENDENT"),
        ):
            completed = command(PACKAGE, script)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn(marker, completed.stdout)
        emitted = command(PACKAGE, "verify.py", "--emit")
        self.assertEqual(emitted.returncode, 0, emitted.stderr)
        self.assertEqual(
            json.loads(emitted.stdout), flow.read_json(PACKAGE / "RESULT.json")
        )

    def test_git_free_export_receipt_and_source_controls(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = export(root)
            for script in ("verify.py", "independent.py"):
                self.assertEqual(command(package, script).returncode, 0)
            receipt = package / "RESULT.json"
            original = receipt.read_bytes()
            changed = json.loads(original)
            changed["target_source_masks_hex"][0] = "0x0"
            receipt.write_text(json.dumps(changed))
            for script in ("verify.py", "independent.py"):
                self.assertNotEqual(command(package, script).returncode, 0)
            receipt.write_bytes(original)
            source = root / flow.INPUTS[0]
            source.write_bytes(source.read_bytes() + b"\n")
            for script in ("verify.py", "independent.py"):
                failure = command(package, script)
                self.assertNotEqual(failure.returncode, 0)
                self.assertIn("SHA256", failure.stderr)

    def test_duplicate_keys_and_typed_receipt_reject(self):
        with tempfile.TemporaryDirectory() as directory:
            package = export(Path(directory))
            receipt = package / "RESULT.json"
            original = receipt.read_text()
            changed = json.loads(original)
            changed["schema_version"] = True
            receipt.write_text(json.dumps(changed))
            self.assertNotEqual(command(package).returncode, 0)
            receipt.write_text(
                original.replace('"helpers": 208,', '"helpers": 208, "helpers": 208,')
            )
            self.assertNotEqual(command(package).returncode, 0)
            invalid = command(PACKAGE, "verify.py", "--unknown")
            self.assertNotEqual(invalid.returncode, 0)
            self.assertIn("usage:", invalid.stderr)


if __name__ == "__main__":
    unittest.main()
