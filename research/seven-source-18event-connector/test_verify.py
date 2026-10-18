"""Mathematical scope and independent on-disk failure controls. Apache-2.0."""
import importlib.util
from itertools import combinations
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("connector18", HERE / "verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class ConnectorTests(unittest.TestCase):
    def test_all_cyclic_starts_and_reversal(self):
        word = v.read(HERE / "CERTIFICATE.json")["source_word"]
        for direction in (word, word[::-1]):
            for shift in range(18):
                path = direction[shift:] + direction[:shift]
                points = [0]
                for j in path:
                    points.append(points[-1] ^ (1 << j))
                differences = {a ^ b for a, b in combinations(points, 2)}
                self.assertTrue(set(v.MASKS) <= differences)
                self.assertEqual(points[-1], 0)

    def test_weighted_complete_invoice(self):
        certificate = v.read(HERE / "CERTIFICATE.json")
        _, events = v.validate(certificate)
        shared, stars = v.invoice(events), v.invoice(v.baseline())
        prices = [2, 3, 5, 7, 11, 13, 17]
        actual = sum((x-y)*p for x, y, p in zip(shared["source_calls_by_map"], stars["source_calls_by_map"], prices))
        actual += 3*(shared["root_descriptor_bits"]-stars["root_descriptor_bits"])
        actual += 5*(shared["complete_calls"]-stars["complete_calls"])
        self.assertEqual(actual, -40*sum(prices[:2])-42*sum(prices[2:])-1160*3-290*5)
        self.assertTrue(all(sum(m >> j & 1 for m in v.MASKS) == 22 for j in range(7)))

    def test_nonlinear_readout_is_outside_scope(self):
        # f(a,b)=ab is not linear: a pair no longer evaluates the XOR difference.
        f = lambda x: ((x >> 1) & 1) & (x & 1)
        self.assertNotEqual(f(1) ^ f(2), f(1 ^ 2))

    def test_odd_characteristic_is_outside_scope(self):
        # In characteristic3, two equal positive readouts do not cancel dirt.
        dirt, increment = 1, 1
        self.assertNotEqual((dirt + dirt + increment) % 3, increment)

    def test_strict_certificate_types(self):
        c = v.read(HERE / "CERTIFICATE.json")
        c["events"][0][1] = bool(c["events"][0][1])
        with self.assertRaises(ValueError):
            v.validate(c)
        with self.assertRaises(ValueError):
            json.loads('{"x":1,"x":1}', object_pairs_hook=v.unique_object)

    def test_git_free_relocation_and_corruptions(self):
        with tempfile.TemporaryDirectory(prefix="replay-control-", dir=HERE) as folder:
            root = Path(folder)
            package = root / "research" / HERE.name
            package.mkdir(parents=True)
            for name in ["verify.py", "CERTIFICATE.json", "RESULT.json", "SOURCES.json"]:
                shutil.copy2(HERE / name, package / name)
            for item in v.read(HERE / "SOURCES.json")["files"]:
                if item["usage"] == "input":
                    target = root / item["path"]
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(v.ROOT / item["path"], target)

            def command(*extra):
                return subprocess.run([sys.executable, "-I", "-O", "-B", str(package / "verify.py"), *extra],
                                      capture_output=True, text=True, timeout=30)

            self.assertEqual(command().returncode, 0)
            receipt = package / "RESULT.json"
            original = receipt.read_bytes()
            bad = json.loads(original)
            bad["shared_invoice"]["complete_calls"] = 142
            receipt.write_text(json.dumps(bad))
            self.assertNotEqual(command().returncode, 0)
            receipt.write_bytes(original)
            certificate = package / "CERTIFICATE.json"
            original = certificate.read_bytes()
            bad = json.loads(original)
            bad["readout_pairs"]["1"] = [0, 0]
            certificate.write_text(json.dumps(bad))
            self.assertNotEqual(command().returncode, 0)
            certificate.write_bytes(original)
            self.assertNotEqual(command("--out", str(receipt)).returncode, 0)
            source = root / "research/universal-connector-boundary/README.md"
            source.write_bytes(source.read_bytes() + b"\nchanged source\n")
            self.assertNotEqual(command().returncode, 0)


if __name__ == "__main__":
    unittest.main()
