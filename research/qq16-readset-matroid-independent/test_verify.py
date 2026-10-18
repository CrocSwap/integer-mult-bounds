"""Positive replay and rejecting controls for the independent QQ16 read-set check.

Run from the repository root:
    python3 -B -m unittest research/qq16-readset-matroid-independent/test_verify.py
Prepared by thakrarsagar with substantial AI assistance from Claude
(Anthropic, Claude Opus 5.5).  Apache-2.0.
"""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load_module():
    spec = importlib.util.spec_from_file_location("qq16_readset_verify", HERE / "verify.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ReadSetVerification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.v = load_module()

    def test_replay_matches_receipt(self):
        out = subprocess.run([sys.executable, "-I", "-B", str(HERE / "verify.py")],
                             cwd=ROOT, capture_output=True, text=True, timeout=300)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("PASS_QQ16_READSET_INDEPENDENT rank_H_V=66 optimal_sets=45 "
                      "mandatory=22 nuisance=29 swaps77=44 owner_minor=47x47 "
                      "pr2384_witness_unread_by_all=True controls=12",
                      out.stdout)

    def test_receipt_contents(self):
        rec = json.loads((HERE / "RESULT.json").read_text(encoding="utf-8"))
        res = rec["computed"]
        self.assertEqual(len(rec["rejected_controls"]), 12)
        self.assertEqual(res["pr2384_witness_check"]["optimal_sets_reading_support"], [])
        self.assertEqual(res["optimal_read_set_count"], 45)
        self.assertEqual(len({tuple(s) for s in res["optimal_read_sets"]}), 45)
        mandatory = set(res["mandatory_ports"])
        self.assertTrue(all(mandatory <= set(s) for s in res["optimal_read_sets"]))
        self.assertTrue(all(not set(s) & set(res["nuisance_coordinates"])
                            for s in res["optimal_read_sets"]))
        self.assertNotEqual(int(res["owner_minor_determinant"]), 0)

    def test_tampered_receipt_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            text = (HERE / "RESULT.json").read_text(encoding="utf-8")
            Path(tmp, "RESULT.json").write_text(text.replace('"optimal_read_set_count": 45',
                                                             '"optimal_read_set_count": 44'),
                                                encoding="utf-8")
            saved = self.v.PACKAGE
            self.v.PACKAGE = Path(tmp)
            try:
                with self.assertRaises(ValueError):
                    self.v.main([])
            finally:
                self.v.PACKAGE = saved

    def test_tampered_source_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp, self.v.PACKET)
            target.parent.mkdir(parents=True)
            data = bytearray((ROOT / self.v.PACKET).read_bytes())
            data[-1] ^= 1
            target.write_bytes(bytes(data))
            with self.assertRaises(ValueError):
                self.v.load_sources(root=Path(tmp))

    def test_wrong_claims_rejected(self):
        packet, phases = self.v.load_sources()
        res = self.v.compute(packet, phases)
        self.v.check(res)
        for key, bad in (("optimal_read_set_count", 44), ("H_on_V_rank", 67),
                         ("coloop_ports", [44]), ("port77_swap_count", 45)):
            with self.assertRaises(ValueError, msg=key):
                self.v.check(res, dict(self.v.CLAIMS, **{key: bad}))


if __name__ == "__main__":
    unittest.main()
