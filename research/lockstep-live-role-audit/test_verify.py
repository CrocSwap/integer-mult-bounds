#!/usr/bin/env python3
"""Rejecting controls for the live-role executor and the constant-C fit."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import constant_c  # noqa: E402
import live_roles as L  # noqa: E402


class Controls(unittest.TestCase):
    def rejects(self, rule, n, **kw):
        with self.assertRaises(L.Violation):
            L.audit(rule, n, **kw)

    def test_owned_centre_per_depth_aliases(self):
        self.rejects(L.toy(), 16, owned_policy="depth")
        self.rejects(L.bit_shaped(0), 400, owned_policy="depth")

    def test_eager_parent_breaks_lockstep(self):
        self.rejects(L.toy(), 16, eager=True)
        self.rejects(L.bit_shaped(0), 400, eager=True)

    def test_exit_batch_repeating_a_field(self):
        self.rejects(L.toy(), 28, bad_exit=True)

    def test_same_rules_pass_without_mutation(self):
        L.audit(L.toy(), 16)
        L.audit(L.bit_shaped(0), 400)

    def test_bit_share_alone_understates_threshold(self):
        c = constant_c.compute()
        self.assertGreater(c["fit_log2p"], c["fit_log2p_bit_share_only"])
        self.assertGreater(c["fit_log2p_4440_words"], c["fit_log2p"])


if __name__ == "__main__":
    unittest.main()
