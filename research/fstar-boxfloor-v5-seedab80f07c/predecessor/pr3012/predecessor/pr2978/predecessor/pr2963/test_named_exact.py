#!/usr/bin/env python3
"""Tests for named_exact.py (KB5i).

RED before GREEN: test_exact_named_on_the_12 fails against the vendored
scan-only predecessor (named is not exact on those records); it passes once
named_exact.py settles them. The agreement tests pin the port to the
vendored engine's own mx_eval semantics on the whole small domain.

Run: python3 -B test_named_exact.py
"""
import json
import os
import random
import sys
import unittest

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import named_exact as ne  # noqa: E402

fg = ne.fg
DATA = os.path.join(HERE, "predecessor", "pr2914", "data")
PR2936 = os.path.join(HERE, "predecessor", "pr2936",
                      "receipt-tied_min-s11-deep.json")

TARGETS = [
    "tied_min|0,1,2,3,4,5,6,7,8,9,10",
    "tied_min|0,1,2,3,4,5,6,7,8,9,11",
    "tied_min|0,1,2,3,4,5,6,7,8,10,11",
    "tied_min|0,1,2,3,4,5,6,7,9,10,11",
    "tied_min|0,1,2,3,4,5,6,8,9,10,11",
    "tied_min|0,1,2,3,4,5,7,8,9,10,11",
    "tied_min|0,1,2,3,4,6,7,8,9,10,11",
    "tied_min|0,1,2,3,5,6,7,8,9,10,11",
    "tied_min|0,1,2,4,5,6,7,8,9,10,11",
    "tied_min|0,1,3,4,5,6,7,8,9,10,11",
    "tied_min|0,2,3,4,5,6,7,8,9,10,11",
    "tied_min|1,2,3,4,5,6,7,8,9,10,11",
]


def load_sub(label):
    fx = label.split("|")[0] + ".json"
    mod0 = fg.model(*fg.load_decoder(os.path.join(DATA, fx)))
    S = [int(x) for x in label.split("|")[1].split(",")]
    return fg.restrict(mod0, S)


def tables(sub):
    inm, _ = fg.digraph_tables(sub["v"], sub["arcs"])
    acyc = fg.acyclic_table(sub["v"], inm)
    mas = fg.mas_table(sub["v"], acyc)
    return mas, acyc


class TestPortAgreement(unittest.TestCase):
    def test_mx_exact_matches_engine_exhaustive(self):
        """mx_exact == the engine's own exhaustive mx_eval product max."""
        n = 0
        for fixture in ("tied_min.json", "cex_min_1.json"):
            mod0 = fg.model(*fg.load_decoder(os.path.join(DATA, fixture)))
            for size in (4, 5, 6):
                subs, _n, _t = fg.subsets_smallest_first(mod0["v"], size,
                                                         12, 3)
                for S in subs:
                    sub = fg.restrict(mod0, list(S))
                    ad = fg.anchor_data(sub)
                    mas, acyc = tables(sub)
                    ref, det = fg.named_exact_small(
                        sub, ad, mas, acyc, cap=3000000, scan_iters=0)
                    self.assertTrue(det["exhaustive"],
                                    "reference must be exhaustive here")
                    mine, mdet = ne.mx_exact(sub, ad, mas, cap=3000000)
                    self.assertEqual(mine, det["mx"],
                                     "mx mismatch at %s size %d" % (fixture, size))
                    n += 1
        self.assertGreaterEqual(n, 20)

    def test_random_decoder_agreement(self):
        rng = random.Random(777)
        pool = [0, 0, 1, -1, 1, -1, 3, -3, 2, -2, 6, -6]
        checked = 0
        while checked < 12:
            v = 4
            P = [tuple(rng.choice(pool) for _ in range(3)) for _ in range(v)]
            Q = [tuple(rng.choice(pool) for _ in range(3)) for _ in range(v)]
            try:
                mod = fg.model(P, Q)
            except (AssertionError, ValueError):
                continue
            ad = fg.anchor_data(mod)
            if not (fg.tie_parity(mod, ad) and fg.scope_identity(mod, ad)):
                continue
            mas, acyc = tables(mod)
            ref, det = fg.named_exact_small(mod, ad, mas, acyc,
                                            cap=3000000, scan_iters=0)
            self.assertTrue(det["exhaustive"])
            mine, _ = ne.mx_exact(mod, ad, mas, cap=3000000)
            self.assertEqual(mine, det["mx"], "mx mismatch on random decoder")
            checked += 1

    def test_cl3_equals_mp_at_even_tau(self):
        for label in TARGETS[:4]:
            sub = load_sub(label)
            ad = fg.anchor_data(sub)
            mas, acyc = tables(sub)
            mp, _m, exh, _p = fg.matched_pivot(sub, mas)
            self.assertTrue(exh)
            self.assertTrue(all(x % 2 == 0 for x in ad["tau"]))
            self.assertEqual(ne._cl3_brute(sub, ad), mp,
                             "CL3 != MP at even tau on %s" % label)


class TestTargets(unittest.TestCase):
    def test_scan_is_not_exact_on_the_12(self):
        """The recorded obstruction: the vendored scan cannot settle these."""
        with open(PR2936, encoding="utf-8") as fh:
            rec = json.load(fh)
        self.assertEqual(len(rec["records"]), 12)
        for r in rec["records"]:
            self.assertFalse(r["named_exhaustive"], r["label"])
            self.assertEqual(r["named"], 9, r["label"])

    def test_exact_named_on_the_12(self):
        """GREEN after named_exact.py: exact named + replayed witness."""
        with open(PR2936, encoding="utf-8") as fh:
            rec = json.load(fh)
        stored = {r["label"]: r for r in rec["records"]}
        out = {}
        for label in TARGETS:
            sub = load_sub(label)
            ad = fg.anchor_data(sub)
            mas, acyc = tables(sub)
            named, det = ne.named_exact(sub, ad, mas, acyc, cap=6000000)
            self.assertTrue(det["exhaustive"], label)
            self.assertGreaterEqual(named, 9, label)
            self.assertLessEqual(named, 11, label)
            wit = det["mx_detail"]["witness"]
            self.assertIsNotNone(wit, label)
            replayed = ne.replay_mx_witness(sub, ad, mas, wit)
            self.assertEqual(replayed, det["mx"],
                             "witness replay mismatch on %s" % label)
            r = stored[label]
            self.assertEqual(det["MP"], r["MP"], label)
            self.assertEqual(r["mx_product"], 1977326743, label)
            self.assertLessEqual(r["named"], named,
                                 "exact named must cover the scan value")
            out[label] = dict(named=named, detail=det,
                              cert_stored=r["cert"], box_stored=r["box"])
        print(json.dumps({k: v["named"] for k, v in out.items()},
                         indent=1, sort_keys=True))
        with open(os.path.join(HERE, "data", "named-v11-values.json"), "w",
                  encoding="utf-8", newline="\n") as fh:
            json.dump({k: dict(named=v["named"],
                               MP=v["detail"]["MP"],
                               reach=v["detail"]["reach"],
                               mx=v["detail"]["mx"],
                               cl3=v["detail"]["cl3"],
                               cl3_how=v["detail"]["cl3_how"],
                               mx_witness=v["detail"]["mx_detail"]["witness"],
                               mx_coarse_product=v["detail"]["mx_detail"]["coarse_product"],
                               cert_stored=v["cert_stored"],
                               box_stored=v["box_stored"])
                       for k, v in out.items()},
                      fh, indent=1, sort_keys=True)
            fh.write("\n")


if __name__ == "__main__":
    unittest.main(verbosity=2)
