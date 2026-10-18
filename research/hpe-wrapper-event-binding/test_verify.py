# SPDX-License-Identifier: Apache-2.0
"""Real emitted positives and mutations that reach the new semantic check."""
import copy
import gzip
import importlib.util
import json
import os
import py_compile
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("hpe_event_verify", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)
binding = verify.binding


class EventBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        verify.sources()
        cls.temp = tempfile.TemporaryDirectory(prefix="hpe-event-tests-")
        cls.addClassCleanup(cls.temp.cleanup)
        cls.run_dir = Path(cls.temp.name) / "local"
        cls.word, cls.programs, cls.adapters, _ = verify.fixture_module().rebuild(cls.run_dir)
        cls.pairs = verify.literal_pairs()
        cls.good = {name: binding.check(cls.word, events, cls.adapters, cls.pairs)
                    for name, events in cls.programs.items()}

    def test_actual_emitted_positives(self):
        self.assertEqual(set(self.good), {"forward", "backward"})
        for row in self.good.values():
            self.assertEqual(row["events"], 24767)
            self.assertEqual(row["helpers"], 30)
            self.assertEqual(Counter(b["recipe"] for b in row["bindings"]),
                             {"3:998": 16, "2:999": 14})

    def rejected(self, events, message, adapters=None, word=None):
        with self.assertRaisesRegex(ValueError, message):
            binding.check(self.word if word is None else word, events,
                          self.adapters if adapters is None else adapters, self.pairs)

    def test_every_actual_helper_requires_both_terminal_specific_wrappers(self):
        controls = 0
        for name, row in self.good.items():
            events = self.programs[name]
            for b in row["bindings"]:
                for side in ("pre", "post"):
                    index = b[side]
                    with self.subTest(name=name, helper=b["helper"], side=side):
                        bad = events[:index] + events[index + 1:]
                        self.rejected(bad, "outside wrappers|missing wrapper")
                        bad = list(events)
                        bad[index] = events[index][:-1]
                        self.rejected(bad, "must name its terminal frame")
                        bad[index] = events[index][:-1] + [1]
                        self.rejected(bad, "wrong wrapper pair")
                        controls += 3
        self.assertEqual(controls, 360)

    def test_duplicate_and_misordered_wrappers(self):
        for name, events in self.programs.items():
            b = next(b for b in self.good[name]["bindings"] if b["helper"] == 450)
            for side in ("pre", "post"):
                i = b[side]
                self.rejected(events[:i] + [events[i]] + events[i:], side + " wrapper order")
            bad = list(events)
            post = bad.pop(b["post"])
            bad.insert(b["first_touch"], post)
            self.rejected(bad, "post wrapper order")
            extra = ["scalar", ["add", ["L", 230], ["L", 450], 1, 1], 999]
            self.rejected(events[:b["post"] + 1] + [extra] + events[b["post"] + 1:],
                          "helper touched outside wrappers")
            bad = list(events)
            bad[b["pre"]] = ["adapter", "old_to_new", 450, 2]
            self.rejected(bad, "ordinary adapter on an HPE helper")

    def test_event_selected_literal_fields_and_full_recipe(self):
        for events in self.programs.values():
            for key in ("3:998", "2:999"):
                for side in ("left", "right"):
                    bad = copy.deepcopy(self.adapters)
                    bad["recipes"][key][side]["phase"] ^= 1
                    self.rejected(events, "monomial differs from Lean", adapters=bad)
                    bad = copy.deepcopy(self.adapters)
                    phase = bad["recipes"][key][side]["phase"]
                    if phase in (0, 1):
                        bad["recipes"][key][side]["phase"] = bool(phase)
                        self.rejected(events, "monomial differs from Lean", adapters=bad)
                bad = copy.deepcopy(self.adapters)
                full = bad["recipes"][key.split(":")[0]]["right"]
                self.assertFalse(binding.same(full, bad["recipes"][key]["right"]))
                bad["recipes"][key]["right"] = full
                self.rejected(events, "monomial differs from Lean", adapters=bad)
                bad = copy.deepcopy(self.adapters)
                del bad["recipes"][key]
                self.rejected(events, "missing event-selected recipe", adapters=bad)

    def test_phantom_metadata_cannot_supply_a_missing_event(self):
        word = copy.deepcopy(self.word)
        word["pre_wrappers"] = [{"helper": 450, "recipe": "2:999"}]
        events = self.programs["forward"]
        b = next(b for b in self.good["forward"]["bindings"] if b["helper"] == 450)
        self.rejected(events[:b["pre"]] + events[b["pre"] + 1:],
                      "helper touched outside wrappers", word=word)
        word["pre_wrappers"][0]["recipe"] = "2:FULL"
        self.assertEqual(binding.check(word, events, self.adapters, self.pairs), self.good["forward"])

    def test_frame_unknown_event_and_capacity_failures(self):
        events = self.programs["forward"]
        b = next(b for b in self.good["forward"]["bindings"] if b["helper"] == 450)
        bad = list(events)
        bad[b["first_touch"]] = list(events[b["first_touch"]])
        self.assertEqual(bad[b["first_touch"]][0], "scalar")
        bad[b["first_touch"]][2] = 0
        self.rejected(bad, "helper frame mismatch")
        self.rejected(events[:2] + [["unrecognised", 450]] + events[2:], "unknown emitted event")
        with patch.object(binding, "MAX_EVENTS", len(events) - 1):
            self.rejected(events, "event capacity exceeded")
        with patch.object(binding, "MAX_REGISTERS", 600):
            self.rejected(events, "register capacity exceeded")
        with patch.object(binding, "MAX_FRAMES", len(self.word["frames"]) - 1):
            self.rejected(events, "frame capacity exceeded")
        word = copy.deepcopy(self.word)
        word["start"][450] = True
        self.rejected(events, "invalid integer index", word=word)
        word = copy.deepcopy(self.word)
        word["frames"][1] = [1]
        self.rejected(events, "wrong ZERO or FULL frame convention", word=word)
        pairs = dict(self.pairs)
        del pairs[((30,), (256, 128, 64, 32, 18, 10, 6, 1))]
        with self.assertRaisesRegex(ValueError, "pair absent from Lean"):
            binding.check(self.word, events, self.adapters, pairs)

    def command(self, run, *extra):
        return subprocess.run([sys.executable, "-I", "-B", *extra, str(HERE / "verify.py"),
                               "--run", str(run)], capture_output=True, text=True, timeout=30)

    def test_real_cli_positive_and_optimized_negative(self):
        result = self.command(self.run_dir)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS_HPE_WRAPPER_EVENT_BINDING", result.stdout)
        existing = Path(self.temp.name) / "existing-result.json"
        existing.write_bytes(b"keep")
        result = subprocess.run([sys.executable, "-I", "-B", str(HERE / "verify.py"),
                                 "--run", str(self.run_dir), "--write-result", str(existing)],
                                capture_output=True, text=True, timeout=30)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(existing.read_bytes(), b"keep")
        with tempfile.TemporaryDirectory(prefix="hpe-bad-event-") as tmp:
            run = Path(tmp)
            for name in ("CANONICAL-WORD.json.gz", "RESIDUAL-ADAPTERS.json"):
                (run / name).write_bytes((self.run_dir / name).read_bytes())
            programs = copy.deepcopy(self.programs)
            b = self.good["forward"]["bindings"][0]
            del programs["forward"][b["pre"]]
            (run / "LOCAL-PROGRAMS.json.gz").write_bytes(gzip.compress(json.dumps(programs).encode()))
            result = self.command(run, "-O")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("helper touched outside wrappers", result.stderr)
            self.assertNotIn("PASS_HPE_WRAPPER_EVENT_BINDING", result.stdout)

    def test_local_loader_uses_source_not_matching_timestamp_cache(self):
        with tempfile.TemporaryDirectory(prefix="hpe-pyc-") as tmp:
            path = Path(tmp) / "fixture.py"
            path.write_text("VALUE = 9\n", encoding="utf-8")
            stamp = path.stat()
            py_compile.compile(str(path), doraise=True)
            path.write_text("VALUE = 1\n", encoding="utf-8")
            os.utime(path, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
            self.assertEqual(verify.load_module(path, "hpe_cache_fixture").VALUE, 1)
            path.write_bytes(b" " * (1024 * 1024 + 1))
            with self.assertRaisesRegex(ValueError, "module exceeds 1 MiB limit"):
                verify.load_module(path, "hpe_oversize_fixture")

    def test_source_hash_failure(self):
        with tempfile.TemporaryDirectory(prefix="hpe-source-drift-") as tmp:
            root = Path(tmp)
            (root / "input.py").write_bytes(b"changed source")
            manifest = {"files": [{"usage": "input", "path": "input.py", "sha256": "0" * 64}]}
            with patch.object(verify, "ROOT", root), patch.object(verify, "read", return_value=manifest):
                with self.assertRaisesRegex(ValueError, "source hash changed: input.py"):
                    verify.sources()
                with patch.object(verify, "MAX_BYTES", 8):
                    with self.assertRaisesRegex(ValueError, "source exceeds 32 MiB limit"):
                        verify.sources()

    def test_json_duplicate_and_decoded_size_limits(self):
        with tempfile.TemporaryDirectory(prefix="hpe-json-") as tmp:
            path = Path(tmp) / "input.json.gz"
            path.write_bytes(gzip.compress(b'{"a": 1, "a": 2}'))
            with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                verify.read(path)
            path.write_bytes(gzip.compress(b" " * 65))
            with patch.object(verify, "MAX_BYTES", 64):
                with self.assertRaisesRegex(ValueError, "decoded limit"):
                    verify.read(path)


if __name__ == "__main__":
    unittest.main()
