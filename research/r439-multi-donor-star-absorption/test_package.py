#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Prepared by Aaron Wang, with help from opencode.
"""Unit tests and independent dual-functional oracle for r439-multi-donor-star-absorption."""
import copy
import gzip
import json
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


class MultiDonorStarAbsorptionTests(unittest.TestCase):
    def test_verify_and_certificate_match(self):
        mod = runpy.run_path(str(HERE / "verify.py"))
        rep = mod["run"](ROOT, check_expected=True)
        self.assertEqual(rep["status"], "PASS_R439_MULTI_DONOR_STAR_ABSORPTION")
        self.assertFalse(rep["new_kappa_claim"])
        self.assertEqual(rep["words"]["pr967"]["edges"], 221)
        self.assertEqual(rep["words"]["pr1062"]["edges"], 236)
        self.assertEqual(rep["words"]["pr1122"]["edges"], 236)
        for wname in ("pr967", "pr1062", "pr1122"):
            wrep = rep["words"][wname]
            for mode in ("same_path", "monotone_all"):
                mrep = wrep["modes"][mode]
                self.assertEqual(mrep["solvable_single_edges"], 5)
                self.assertEqual(mrep["solvable_two_leaf_pairs"], 0)
                self.assertEqual(mrep["chained_extra_solvable"], 0)
                self.assertEqual(
                    mrep["zero_bit_edges"] + mrep["nonzero_unsolvable_edges"] + mrep["solvable_single_edges"],
                    wrep["edges"],
                )
            self.assertEqual(wrep["composed_gain1_3"]["net_add_delta"], -3)
            self.assertEqual(wrep["composed_all_5"]["net_add_delta"], -3)
            self.assertEqual(wrep["composed_gain1_3"]["paid_mass"], 5129)
            self.assertEqual(wrep["composed_all_5"]["paid_mass"], 5129)
        by_name = dict(rep["controls"])
        self.assertGreaterEqual(len(rep["controls"]), 8)
        self.assertTrue(by_name["valid_dual_hyperplane_witness"].startswith("pass: target parity 1; orthogonal to"))
        self.assertEqual(by_name["corrupted_dual_hyperplane_witness"], "dual fails target parity")
        self.assertTrue(by_name["corrupted_dual_orthogonality_witness"].startswith("dual not orthogonal to donor ("))

    def test_independent_dual_hyperplane_oracle_all_three_words(self):
        cert = json.loads((HERE / "CERTIFICATE.json").read_text(encoding="utf-8"))
        word_paths = {
            "pr967": (ROOT / "research/r439-helper-stars-seed19/candidate.json.gz", 216 + 64),
            "pr1062": (ROOT / "research/r439-bsection-stars-seed01/candidate.json.gz", 231 + 74),
            "pr1122": (ROOT / "research/r439-abc-semantic-bridge/inputs/candidate.json.gz", 231 + 74),
        }
        for wname, (wpath, expected_duals) in word_paths.items():
            w = json.loads(gzip.open(wpath, "rt", encoding="utf-8").read())
            v, R = w["v"], w["R"]
            n = 2 * v + R
            fs = [frozenset(f) for f in w["frames"]]

            # Independently replay D and A using Python frozensets of column indices
            cur = list(w["start"])
            for f, d, ss in w["D"]:
                for r in (d, *ss):
                    cur[r] = f
            state = [frozenset([r]) for r in range(n)]
            a_states = []
            pre_frames = []
            for f, d, ss in w["A"]:
                pre_frames.append(list(cur))
                for r in (d, *ss):
                    cur[r] = f
                a_states.append(list(state))
                acc = frozenset()
                for s in ss:
                    acc = acc ^ state[s]
                state[d] = state[d] ^ acc

            nxt = list(w["final"])
            next_touch = [[0] * n for _ in range(len(w["A"]))]
            for sec in ("C", "B"):
                for f, d, ss in reversed(w[sec]):
                    for r in (d, *ss):
                        nxt[r] = f
            for i in range(len(w["A"]) - 1, -1, -1):
                f, d, ss = w["A"][i]
                next_touch[i] = list(nxt)
                for r in (d, *ss):
                    nxt[r] = f

            first_read = {}
            for a in range(2 * v, n):
                fr = len(w["A"])
                for i, (_, _, ss) in enumerate(w["A"]):
                    if a in ss:
                        fr = i
                        break
                first_read[a] = fr

            duals = cert["words"][wname]["modes"]["monotone_all"]["dual_witnesses"]
            self.assertEqual(len(duals), expected_duals)
            for item in duals:
                a = item["center"]
                leaves = item["leaves"]
                u_support = set(item["dual_support"])
                target_dot = sum(1 for b in leaves if b in u_support) & 1
                self.assertEqual(target_dot, 1, f"{wname} dual witness fails target dot for {a} {leaves}")
                writers = [i for i in range(first_read[a]) if w["A"][i][1] == a]
                for i in writers:
                    f_i = w["A"][i][0]
                    for r in range(n):
                        if r == a or (v <= r < 2 * v):
                            continue
                        if (fs[pre_frames[i][r]] <= fs[f_i]) and (fs[f_i] <= fs[next_touch[i][r]]):
                            donor_dot = len(a_states[i][r] & u_support) & 1
                            self.assertEqual(donor_dot, 0, f"{wname} dual witness not orthogonal at writer {i} donor {r}")

    def test_corruptions_rejected(self):
        mod = runpy.run_path(str(HERE / "verify.py"))
        cert = json.loads((HERE / "CERTIFICATE.json").read_text(encoding="utf-8"))
        bad = copy.deepcopy(cert)
        bad["words"]["pr1062"]["modes"]["monotone_all"]["solvable_single_edges"] = 6
        with self.assertRaises(ValueError):
            mod["check_certificate_matches"](cert, bad)

    def test_minimal_relocation_and_opt_mode(self):
        sources = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory(prefix="r439-mdonor-reloc-") as tmp:
            troot = Path(tmp)
            pkg_dst = troot / "research/r439-multi-donor-star-absorption"
            pkg_dst.mkdir(parents=True)
            for fname in ("README.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py", "CERTIFICATE.json"):
                shutil.copy2(HERE / fname, pkg_dst / fname)
            for entry in sources["files"]:
                if entry["usage"] == "input":
                    dst = troot / entry["path"]
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(ROOT / entry["path"], dst)
            res = subprocess.run(
                [sys.executable, "-I", "-O", "-B", str(pkg_dst / "verify.py")],
                cwd=str(troot),
                capture_output=True,
                text=True,
                check=True,
            )
            self.assertIn("PASS_R439_MULTI_DONOR_STAR_ABSORPTION", res.stdout)


if __name__ == "__main__":
    unittest.main()
