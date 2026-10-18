"""Exercise real ADD quotas, source admission, relocation and failure cleanup."""

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

PACKAGE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "count_phase_verifier", PACKAGE / "verify.py"
)
V = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V)


def relocate(root):
    target = root / "research" / PACKAGE.name
    shutil.copytree(PACKAGE, target, ignore=shutil.ignore_patterns("__pycache__"))
    for source in json.loads((PACKAGE / "VERIFY.json").read_text())["inputs"]:
        destination = root / source
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(V.REPO / source, destination)
    return target


def command(package, *options):
    return subprocess.run(
        [sys.executable, *options, "-B", str(package / "verify.py")],
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )


class ReplayTests(unittest.TestCase):
    def test_literal_peaks_and_actual_one_cell_short_failure(self):
        with V.source_modules() as m:
            ordinary = V.fixture(m, index_bits=8)
            self.assertEqual(
                [ordinary[k] for k in ("K", "E", "R", "C", "H", "peak")],
                [9, 21, 12, 18, 0, 30],
            )
            callback = V.fixture(m, callback_bits=32)
            self.assertEqual([callback["H"], callback["peak"]], [68, 80])
            padded = V.fixture(m, index_bits=256)
            self.assertEqual([padded["preparation_peak"], padded["peak"]], [267, 267])
            alias = V.fixture(m, alias=True)
            self.assertEqual([alias["K"], alias["peak"]], [3, 30])
            with self.assertRaisesRegex(ValueError, "count backing quota"):
                V.fixture(m, index_bits=8, quota=29)

    def test_cleared_direct_array_capture_breaks_the_bound(self):
        with V.source_modules() as m:
            row = V.fixture(m, callback_bits=32, escape=True)
        self.assertEqual(
            [row[k] for k in ("R", "C", "H", "bound", "peak")],
            [12, 18, 68, 80, 166],
        )

    def test_complete_origin_planes_reject_wrong_coefficient(self):
        with V.source_modules() as m:
            action = m.action

            def wrong_action(source, event, layout, coefficient):
                return action(
                    source, event, layout, lambda _request: layout.ring.arena.literal(0)
                )

            with patch.object(m, "action", wrong_action):
                with self.assertRaisesRegex(ValueError, "complete ADD endpoint"):
                    V.fixture(m, origin=3, coefficient=1)

    def test_modules_and_observers_restore_on_success_and_failure(self):
        absent = object()
        previous = {name: sys.modules.get(name, absent) for name in V.MODULES}
        sentinels = {name: types.ModuleType(name) for name in V.MODULES}
        try:
            sys.modules.update(sentinels)
            with V.source_modules() as m:
                tape, extents = m.stream.Tape, m.layout.Layout.extents
                with self.assertRaisesRegex(RuntimeError, "injected"):
                    with V.counted(m):
                        raise RuntimeError("injected")
                self.assertIs(m.stream.Tape, tape)
                self.assertIs(m.layout.Layout.extents, extents)
            self.assertTrue(
                all(sys.modules[name] is value for name, value in sentinels.items())
            )
            with patch.object(
                V, "extract", side_effect=ValueError("extraction failure")
            ):
                with self.assertRaisesRegex(ValueError, "extraction failure"):
                    with V.source_modules():
                        self.fail("failed extraction yielded modules")
            self.assertTrue(
                all(sys.modules[name] is value for name, value in sentinels.items())
            )
        finally:
            for name, old in previous.items():
                if old is absent:
                    sys.modules.pop(name, None)
                else:
                    sys.modules[name] = old

    def test_relocated_cli_normal_and_optimized(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = relocate(Path(tmp))
            for options in ((), ("-I", "-O")):
                result = command(target, *options)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("fixtures=70 controls=8", result.stdout)

    def test_changed_executable_source_rejects_before_replay(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = relocate(root)
            source = root / V.SOURCE / "stream.py"
            source.write_bytes(
                source.read_bytes() + b"\nraise RuntimeError('unadmitted code')\n"
            )
            result = command(target)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("source hash", result.stderr)
            self.assertNotIn("RuntimeError: unadmitted code", result.stderr)

    def test_typed_receipt_corruption_rejects(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = relocate(Path(tmp))
            path = target / "RESULT.json"
            result = json.loads(path.read_text())
            result["no_new_kappa"] = 1
            path.write_text(json.dumps(result))
            replay = command(target, "-I", "-O")
            self.assertNotEqual(replay.returncode, 0)
            self.assertIn("exact typed replay receipt", replay.stderr)


if __name__ == "__main__":
    unittest.main()
