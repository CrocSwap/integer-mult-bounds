"""Behavioral and failure controls for the declared abstract boundary."""

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify


class CorrespondenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = verify.run()
        cls.semantics, _compiler = verify.load()

    def test_reconstructed_receipt(self):
        expected = json.loads((verify.HERE / "RESULT.json").read_text())
        self.assertEqual(self.result, expected)

    def test_selected_complete_separators(self):
        census = self.result["selected_owners"]["census"]
        self.assertEqual(census["owners"], 190368)
        self.assertEqual(census["same_family_pairs"], 181056)
        self.assertEqual(census["unique_chart_pairs"], 463)
        self.assertEqual(
            census["witness_differences"], {"-1": 32, "1": 19, "-1/2": 260, "1/2": 152}
        )
        self.assertEqual(
            self.result["selected_owners"]["rejected"],
            ["missing_separator", "zero_separator"],
        )

    def test_source_and_compiler_admission_differ(self):
        self.assertEqual(
            self.result["admission"],
            {
                "duplicate_owner": {
                    "compiled_instructions": 1155,
                    "source_rejection": "disjoint complete owned low packets",
                },
                "self_bridge": {
                    "compiled_instructions": 5,
                    "source_rejection": "native bridge scalar",
                },
            },
        )

    def test_private_trace_defect_survives_global_endpoints(self):
        self.assertEqual(
            self.result["controls"]["omit_cancelling_private_xors"],
            {"cuts": True, "final": True, "residuals": True, "xors": False},
        )
        self.assertEqual(self.result["controls"]["omit_copy"], "rejected_at_boundary")

    def test_direction_and_exchange_defects_change_outputs(self):
        for name in ("omit_bridge", "reverse_bridge", "omit_exchange"):
            with self.subTest(name=name):
                self.assertIs(self.result["controls"][name]["final"], False)

    def test_literal_dispatch_payload(self):
        s = self.semantics
        topology = s.Topology(1)
        machine = s.BoundaryMachine(topology, s.Residuals(), None)
        low = next(topology.catalogue.low_classes())
        machine.tape(("family", 0)).data = {low: (1, 2, 4, 8)}
        machine.tape(("family", 1)).data = {low: (16, 32, 64, 128)}
        machine.tape(("family", 2)).data = {low: (256, 512, 1024, 2048)}
        with s.kernels([]):
            self.assertEqual(machine.dispatch(("family_xor", 0, 2)), "next")
            self.assertEqual(
                machine.tape(("family", 0)).data, {low: (257, 514, 1028, 2056)}
            )
            self.assertEqual(machine.dispatch(("exchange", 0, 1)), "next")
            self.assertEqual(machine.tape(("family", 0)).data, {low: (16, 32, 64, 128)})
            self.assertEqual(
                machine.tape(("family", 1)).data, {low: (257, 514, 1028, 2056)}
            )
            self.assertEqual(machine.tape("swap").data, {})
            self.assertEqual(
                machine.dispatch(("copy", ("family", 0), ("stage", 0))), "next"
            )
            self.assertEqual(machine.tape(("stage", 0)).data, {low: (16, 32, 64, 128)})
            self.assertEqual(machine.tape(("family", 0)).data, {low: (16, 32, 64, 128)})

    def test_scatter_uses_latest_family(self):
        s = self.semantics
        topology = s.Topology(1)
        machine = s.BoundaryMachine(topology, s.Residuals(), None)
        first, second = tuple(topology.catalogue.low_classes())[:2]
        machine.tape(("family", 0)).data = {
            first: (1, 2, 4, 8),
            second: (16, 32, 64, 128),
        }
        with s.kernels([]):
            machine.tape("idle").data = {first: (3, 2, 4, 8)}
            self.assertEqual(machine.dispatch(("scatter", "idle", 0, first)), "next")
            machine.tape("idle").data = {second: (48, 32, 64, 128)}
            self.assertEqual(machine.dispatch(("scatter", "idle", 0, second)), "next")
        self.assertEqual(
            machine.tape(("family", 0)).data,
            {first: (3, 2, 4, 8), second: (48, 32, 64, 128)},
        )

    def test_source_hash_change_rejects(self):
        original = Path.read_bytes
        target = verify.PREDECESSOR / "macro_code.py"

        def changed(path):
            data = original(path)
            return data + b"\n" if path == target else data

        with (
            patch.object(Path, "read_bytes", changed),
            self.assertRaisesRegex(ValueError, "changed input: .*macro_code.py"),
        ):
            verify.authenticate()


if __name__ == "__main__":
    unittest.main()
