"""Semantic controls for the precise fixed-snapshot claim.

Gareth Davidson with OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
import copy
import json
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import independent
import verify
from common import HERE, REPO, certificate, read, sources


class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = sources()
        cls.cert = certificate(read(HERE / "WITNESS.json"))
        cls.expected = read(HERE / "RESULT.json")
        cls.trace = verify.replay(cls.data, cls.cert["terms"])

    def test_41_essential_coefficients(self):
        for i in range(len(self.cert["terms"])):
            bad = copy.deepcopy(self.cert)
            bad["terms"][i][3] = str(-verify.Q(bad["terms"][i][3]))
            with self.subTest(term=i), self.assertRaisesRegex(ValueError, "right inverse"):
                verify.verify_witness(self.trace, bad)

    def test_contact_and_own_target(self):
        for checker in (verify.run, independent.run):
            bad = copy.deepcopy(self.cert)
            bad["terms"][0][1] = 4058
            with self.assertRaisesRegex(ValueError, "contact.*frame|chart contact"):
                checker(self.data, bad)
            bad["terms"][0][1] = 0
            bad["terms"][0][2] = "Y0"
            with self.assertRaisesRegex(ValueError, "live.*register"):
                checker(self.data, bad)

    def test_arbitrary_dirty_endpoints(self):
        for event in (0, 4057):
            data = copy.deepcopy(self.data)
            data["LOWRANK-WITNESS.json"]["program"][event][3] = "0"
            for checker in (verify.run, independent.run):
                with self.subTest(event=event, checker=checker.__module__), \
                        self.assertRaisesRegex(ValueError, "endpoint"):
                    checker(data, self.cert)

    def test_geometry_and_rank_guards(self):
        data = copy.deepcopy(self.data)
        data["P104-FIXTURE.json"]["section4_explicit_P104"]["F0"].pop()
        for checker in (verify.run, independent.run):
            with self.assertRaisesRegex(ValueError, "puncture|root enumeration"):
                checker(data, self.cert)
        data = copy.deepcopy(self.data)
        event = next(e for e in data["LOWRANK-WITNESS.json"]["program"] if e[0] == "transport")
        event[4] += 1
        for checker in (verify.run, independent.run):
            with self.assertRaisesRegex(ValueError, "rank"):
                checker(data, self.cert)

    def test_frame_basis_order_positive(self):
        data = copy.deepcopy(self.data)
        word = data["LOWRANK-WITNESS.json"]
        for key in ("initial_frames", "final_frames"):
            for frame in word[key].values():
                frame.reverse()
        for e in word["program"]:
            indices = {"add": (4,), "transport": (2, 3), "copy": (3,),
                       "zero": (2,), "erase": (2,)}[e[0]]
            for i in indices:
                e[i].reverse()
        for checker in (verify.run, independent.run):
            self.assertEqual(checker(data, self.cert), self.expected)

    def test_schema(self):
        for field in (0, 1):
            bad = copy.deepcopy(self.cert)
            bad["terms"][0][field] = True
            with self.assertRaisesRegex(ValueError, "index"):
                certificate(bad)
        bad = copy.deepcopy(self.cert)
        bad["terms"].append(bad["terms"][0])
        with self.assertRaisesRegex(ValueError, "duplicate contact"):
            certificate(bad)
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "bad.json"
            for raw in ('{"a":1,"a":2}', '{"a":NaN}'):
                path.write_text(raw)
                with self.assertRaises(ValueError):
                    read(path)

    def test_source_export_and_receipt(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package = root / "research/p104-minimum-shared-space"
            shutil.copytree(HERE, package, ignore=shutil.ignore_patterns("__pycache__"))
            pins = [p for p in read(HERE / "SOURCES.json")["files"] if p["usage"] == "input"]
            for pin in pins:
                dest = root / pin["path"]
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(REPO / pin["path"], dest)
            saved = {p: p.read_bytes() for p in root.rglob("*") if p.is_file()}
            for path in saved:
                path.chmod(0o444)
            for checker in ("verify.py", "independent.py"):
                command = [sys.executable, "-I", "-O", "-B", str(package / checker)]
                result = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=90)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("minimum=96", result.stdout)
                result = subprocess.run(command + ["--out", str(package / "RESULT.json")],
                                        capture_output=True, text=True, timeout=90)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("output already exists", result.stderr)
            self.assertEqual(saved, {p: p.read_bytes() for p in root.rglob("*") if p.is_file()})
            bad_source = root / pins[0]["path"]
            bad_source.chmod(0o644)
            bad_source.write_bytes(bad_source.read_bytes() + b" ")
            with self.assertRaisesRegex(ValueError, "source bytes changed"):
                sources(root)
            # Independently mutate the expected result without changing any input.
            for p, raw in saved.items():
                p.chmod(0o644)
                p.write_bytes(raw)
            receipt = dict(self.expected, minimum_dimension=95)
            (package / "RESULT.json").write_text(json.dumps(receipt))
            result = subprocess.run([sys.executable, "-I", "-O", "-B", str(package / "independent.py")],
                                    capture_output=True, text=True, timeout=90)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("receipt differs", result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
