"""Independent dyadic/nullspace replay and CLI evidence-integrity tests."""
from fractions import Fraction
from pathlib import Path
from tempfile import TemporaryDirectory
import copy
import gzip
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("complement_check", HERE / "verify.py")
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


def nullspace(rows):
    reduced = list(rows)
    pivots = []
    offset = 0
    for bit in range(9):
        candidates = [i for i in range(offset, len(reduced)) if reduced[i] >> bit & 1]
        if not candidates:
            continue
        pivot = candidates[0]
        reduced[offset], reduced[pivot] = reduced[pivot], reduced[offset]
        for i in range(len(reduced)):
            if i != offset and reduced[i] >> bit & 1:
                reduced[i] ^= reduced[offset]
        pivots.append(bit)
        offset += 1
    return tuple((1 << bit) | sum(((reduced[i] >> bit) & 1) << pivot
                                  for i, pivot in enumerate(pivots))
                 for bit in range(9) if bit not in pivots)


def independent_complement(frame, iso):
    dual = iso["compressed_dual_gram"]
    transform = []
    for v in iso["orthonormal_basis_compressed"]:
        transform.append(sum(((row & v).bit_count() & 1) << i for i, row in enumerate(dual)))
    physical = [sum(((v & row).bit_count() & 1) << i for i, row in enumerate(transform))
                for v in frame]
    return nullspace(physical)


def update(destination, source, coefficient):
    left, le = destination
    right, re = source
    need_den = coefficient.denominator
    if need_den & (need_den - 1):
        raise ValueError("non-dyadic test input")
    exponent = need_den.bit_length() - 1
    common = max(le, re + exponent)
    if common > 32:
        raise ValueError("dyadic denominator capacity exceeded")
    result = [(a << (common-le)) + coefficient.numerator * (b << (common-re-exponent))
              for a, b in zip(left, right)]
    for _ in range(common):
        if not all(v % 2 == 0 for v in result):
            break
        result = [v // 2 for v in result]
        common -= 1
    if any(v.bit_length() > 256 for v in result):
        raise ValueError("dyadic numerator capacity exceeded")
    return result, common


def dense_replay(source, ports):
    names = list(source["initial_frames"])
    indices = {name: i for i, name in enumerate(names)}
    rows = {name: ([int(i == j) for j in range(358)], 0) for i, name in enumerate(names)}
    erasures = 0
    for event in source["program"]:
        op, reg = event[:2]
        if op == "zero":
            rows[reg] = ([0] * 358, 0)
        elif op == "erase":
            if any(rows[reg][0]):
                raise ValueError("nonzero dense private erase")
            del rows[reg]
            erasures += 1
        elif op == "sign":
            rows[reg] = ([-v for v in rows[reg][0]], rows[reg][1])
        elif op == "add":
            rows[reg] = update(rows[reg], rows[event[2]], Fraction(event[3]))
        elif op != "transport":
            raise ValueError("dense event alphabet")
    for name, (numerators, exponent) in rows.items():
        expected = [Fraction(int(i == indices[name])) for i in range(358)]
        if name.startswith("X"):
            s = int(name[1:])
            for t in range(104):
                value = Fraction(int(t == s)) if t < 2 else Fraction(
                    sum(a*b for a, b in zip(ports[t], ports[s])), 8)
                expected[indices["Y"+str(t)]] = -value
        if [Fraction(v, 1 << exponent) for v in numerators] != expected:
            raise ValueError("dense logical endpoint " + name)
    if erasures != 8 or len(rows) != 358:
        raise ValueError("dense lifecycle boundary")
    return sum(len(row[0]) for row in rows.values())


def file_hashes(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file()}


def export(destination):
    package = destination / "research/p104-complementary-dual"
    shutil.copytree(HERE, package, ignore=shutil.ignore_patterns("__pycache__"))
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    for record in manifest["files"]:
        if record["usage"] == "input":
            target = destination / record["path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(check.ROOT / record["path"], target)
    return package


def command(package, *options):
    environment = dict(os.environ)
    environment.pop("PYTHONOPTIMIZE", None)
    return subprocess.run([sys.executable, "-I", "-O", "-B", str(package / "verify.py"), *options],
                          cwd="/", text=True, capture_output=True, timeout=120, env=environment)


class ComplementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = check.authenticate()
        cls.oracle = check.load_module(check.NATIVE / "vendor/native_verify.py", "test_native_oracle")
        convert, cls.ports, cls.labels = check.geometry(cls.oracle)
        cls.convert = staticmethod(convert)
        cls.word = check.lift(cls.source, cls.convert)

    def test_dense_dyadic_all_columns(self):
        self.assertEqual(dense_replay(self.source, self.ports), 128164)
        bad = copy.deepcopy(self.source)
        index = max(i for i, e in enumerate(bad["program"]) if e[0] == "add" and e[1] == "C")
        bad["program"][index][3] = "0"
        with self.assertRaisesRegex(ValueError, "nonzero dense private erase"):
            dense_replay(bad, self.ports)

    def test_independent_complements_every_literal_frame(self):
        packet = json.loads(gzip.decompress((check.NATIVE / "NATIVE-RECIPES.json.gz").read_bytes()))
        iso = packet["label_isometry"]
        pairs = list(zip(self.source["initial_frames"].values(), self.word["initial_frames"].values()))
        pairs += list(zip(self.source["final_frames"].values(), self.word["final_frames"].values()))
        for old, new in zip(self.source["program"], self.word["program"]):
            positions = (2, 3) if old[0] == "transport" else (-1,)
            pairs += [(old[i], new[i]) for i in positions]
        self.assertEqual(len(pairs), 7352)
        for old, new in pairs:
            independent = independent_complement(old, iso)
            self.assertEqual(check.span(independent), check.span(tuple(new)))
            self.assertEqual(len(independent), 9-len(old))

    def test_equivalent_source_bases(self):
        source = copy.deepcopy(self.source)
        for group in (source["initial_frames"], source["final_frames"]):
            for frame in group.values():
                frame.reverse()
        for event in source["program"]:
            for index in ((2, 3) if event[0] == "transport" else (-1,)):
                event[index].reverse()
        self.assertEqual(check.lift(source, self.convert), self.word)

    def test_optimized_git_free_read_only_export(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            package = export(root)
            for path in root.rglob("*"):
                if path.is_file():
                    path.chmod(0o444)
            before = file_hashes(root)
            result = command(package)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["rank_mass"], 3126)
            self.assertEqual(file_hashes(root), before)

    def test_reject_source_before_import(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            package = export(root)
            marker = root / "executed"
            interpreter = root / "research/p104-native-channel/vendor/native_verify.py"
            interpreter.write_text("from pathlib import Path\nPath(" + repr(str(marker)) + ").touch()\n")
            result = command(package)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("external source drift", result.stderr)
            self.assertFalse(marker.exists())

    def test_json_capacity_guards(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            raw = root / "oversize.json"
            raw.write_bytes(b" " * (2 * 1024 * 1024 + 1))
            with self.assertRaisesRegex(ValueError, "JSON input capacity"):
                check.read_json(raw)
            packed = root / "oversize.json.gz"
            packed.write_bytes(gzip.compress(raw.read_bytes(), mtime=0))
            with self.assertRaisesRegex(ValueError, "JSON payload capacity"):
                check.read_json(packed, compressed=True)

    def test_complete_recipe_regeneration(self):
        with TemporaryDirectory() as temporary:
            output = Path(temporary) / "native.json.gz"
            result = subprocess.run([sys.executable, "-B", str(HERE / "build.py"),
                                     "--out", str(output)], text=True, capture_output=True, timeout=180)
            self.assertEqual(result.returncode, 0, result.stderr)
            regenerated = json.loads(gzip.decompress(output.read_bytes()))
            frozen = json.loads(gzip.decompress((HERE / "NATIVE.json.gz").read_bytes()))
            self.assertEqual(regenerated, frozen)

    def test_missing_receipt_and_exclusive_output(self):
        with TemporaryDirectory() as temporary:
            package = export(Path(temporary))
            receipt = package / "RESULT.json"
            receipt.unlink()
            result = command(package)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("RESULT.json", result.stderr)
            output = package / "fresh.json"
            first = command(package, "--out", str(output))
            self.assertEqual(first.returncode, 0, first.stderr)
            before = output.read_bytes()
            second = command(package, "--out", str(output))
            self.assertNotEqual(second.returncode, 0)
            self.assertEqual(output.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
