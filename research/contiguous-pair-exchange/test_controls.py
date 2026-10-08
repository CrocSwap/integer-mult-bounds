import sys
if sys.flags.optimize:
    raise ValueError("Assertions must remain enabled")
sys.dont_write_bytecode = True

import copy
import gzip
import json
import os
import shlex
import struct
import subprocess
import tempfile
import unittest
from pathlib import Path

import verify as v


class Controls(unittest.TestCase):
    def profiles(self, stage="B"):
        prefix = "" if stage == "B" else "stage-a-"
        return [
            json.loads((v.HERE / f"{prefix}profiles-23.json").read_text()),
            json.loads((v.HERE / f"{prefix}profiles-25.json").read_text()),
        ]

    def test_nonbijective_relabel_rejected(self):
        word = json.loads(gzip.decompress((v.HERE / "word-25.json.gz").read_bytes()))
        with self.assertRaises(AssertionError):
            v.relabel(word, [0] * 25)

    def test_relabel_roundtrip_both_axes(self):
        for h in (23, 25):
            word = json.loads(gzip.decompress((v.HERE / f"word-{h}.json.gz").read_bytes()))
            p = v.engine.FINAL_COORDS[h]
            inverse = [p.index(i) for i in range(h)]
            self.assertEqual(v.relabel(v.relabel(copy.deepcopy(word), inverse), p), word)

    def test_omitted_internal_rank_rejected(self):
        profiles = self.profiles("B")
        profiles[1]["blocks"][1] -= 1
        with self.assertRaises(AssertionError):
            v.parent.combine(profiles)

    def test_stale_width_rejected(self):
        c = json.loads((v.HERE / "certificate.json").read_text())
        c["bit"]["W"] -= 1
        with self.assertRaises(AssertionError):
            v.exact(self.profiles("B"), c, stage="B")

    def test_overstated_exponent_rejected(self):
        c = json.loads((v.HERE / "certificate.json").read_text())
        c["kappa"] = "1/100"
        with self.assertRaises(AssertionError):
            v.exact(self.profiles("B"), c, stage="B")

    def test_cached_oracle_matches_reference_oracle(self):
        with tempfile.TemporaryDirectory(prefix="oracle-eq-") as tmp:
            work = Path(tmp)
            cxx = shlex.split(os.environ.get("CXX", "c++"))
            inc = str(v.ROOT / "references/frame-compiler/pr48/scripts/partial_swap")
            ref_exe = work / "ref_oracle"
            cached_exe = work / "cached_oracle"
            subprocess.run(
                [*cxx, "-O3", "-std=c++17", "-I", inc,
                 str(v.ROOT / "references/frame-compiler/pr67/research/slot-cost-rank-pair/profile_oracle.cpp"),
                 "-o", str(ref_exe)],
                check=True,
            )
            subprocess.run(
                [*cxx, "-O3", "-std=c++17", "-I", inc,
                 str(v.HERE / "profile_oracle_cached.cpp"),
                 "-o", str(cached_exe)],
                check=True,
            )
            word23 = json.loads(gzip.decompress((v.HERE / "word-23.json.gz").read_bytes()))
            frames = word23["frames"][:40]
            inp = work / "input.bin"
            with inp.open("wb") as s:
                s.write(struct.pack("<6I2Q", 23, 1771, 0, len(frames) + 2, 0, 0, 23 * 22, 23 * 22))
                s.write(struct.pack("<2QI", 0, 0, 0))
                s.write(struct.pack("<2QI", 0, 0, 23))
                for core, cover in frames:
                    rk = 1 if core == cover else (cover.bit_count() - core.bit_count())
                    s.write(struct.pack("<2QI", core, cover, rk))
            queries = []
            for i in range(len(frames)):
                queries.append(f"0 {i+2}\n")
                queries.append(f"{i+2} 1\n")
            q_str = "".join(queries)
            out_ref = subprocess.run([str(ref_exe), str(inp)], input=q_str, capture_output=True, text=True, check=True).stdout
            out_cached = subprocess.run([str(cached_exe), str(inp)], input=q_str, capture_output=True, text=True, check=True).stdout
            self.assertEqual(out_ref, out_cached)

    def test_optimized_python_rejected(self):
        p = subprocess.run([sys.executable, "-O", str(v.HERE / "verify.py")], capture_output=True, text=True)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("Assertions must remain enabled", p.stderr)


if __name__ == "__main__":
    unittest.main()
