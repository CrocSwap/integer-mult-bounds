# SPDX-License-Identifier: Apache-2.0
"""Behavioral controls on actual regenerated native artifacts."""
import copy
import gzip
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify as v


class EventBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="v45-event-tests-")
        cls.addClassCleanup(cls.temp.cleanup)
        cls.work = Path(cls.temp.name)
        cls.blobs = v.sources()
        cls.fixtures = {}
        for tag in ("base", "extra"):
            folder = cls.work / tag
            folder.mkdir()
            output = v.generate(cls.blobs, tag, folder)
            cls.fixtures[tag] = (json.loads(gzip.decompress(cls.blobs[v.WORDS[tag]])),
                                 v.read(output / "CANONICAL-WORD.json.gz"),
                                 v.read(output / "LOCAL-PROGRAMS.json.gz"),
                                 v.read(output / "RESIDUAL-ADAPTERS.json"))

    def variants(self):
        for tag in ("base", "extra"):
            word, canonical, programs, adapters = self.fixtures[tag]
            for name in ("forward", "backward"):
                yield word, canonical, programs[name], name == "backward", adapters

    def test_genuine_inventory_and_source_clocks(self):
        for word, canonical, stream, back, _ in self.variants():
            result = v.events.check(word, canonical, stream, back)
            self.assertEqual((result["events"], result["covered_events"]), (22748, 73))
            rows = result["inventory"]
            self.assertEqual(sum(r[2][0] == "scalar" for r in rows), 63)
            self.assertEqual([r[2][3] for r in rows if r[2][0] == "climb"],
                             [1, 1, 1, 1, 2, 1])
            self.assertEqual(rows[0], ["entry_adapters", 0,
                                      ["wrapper", "pre", [], v.events.W]])

    def test_event_mutations_without_checksum_shortcut(self):
        for word, canonical, stream, back, _ in self.variants():
            binding = v.events.check(word, canonical, stream, back)
            indices = binding["event_indices"]
            pre, post = indices[0], indices[-1]
            climb = next(i for i in indices if stream[i][0] == "climb")
            cleanup = next(i for i in indices if stream[i][0] == "scalar"
                           and ["Z", 249] in stream[i][1][1:3])
            cases = {
                "missing pre": lambda s, i=pre: s.pop(i),
                "missing post": lambda s, i=post: s.pop(i),
                "missing terminal": lambda s, i=pre: s[i].pop(),
                "FULL terminal": lambda s, i=pre: s[i].__setitem__(4, 1),
                "duplicate pre": lambda s, i=pre: s.insert(i, s[i].copy()),
                "ordinary entry": lambda s, i=pre: s.__setitem__(i, ["adapter", "old_to_new", 249, 0]),
                "rank": lambda s, i=climb: s[i].__setitem__(5, 9),
                "wrong old frame": lambda s, i=climb: s[i].__setitem__(3, 1),
                "cleanup omission": lambda s, i=cleanup: s.pop(i),
                "scalar sign": lambda s, i=cleanup: s[i][1].__setitem__(3, -s[i][1][3]),
                "direct warp": lambda s, i=pre: s.insert(i + 1, ["warp", ["L", 249], 1, 0, 0]),
                "unknown": lambda s, i=pre: s.insert(i + 1, ["unknown"]),
            }
            for name, mutate in cases.items():
                with self.subTest(back=back, name=name):
                    altered = copy.deepcopy(stream)
                    mutate(altered)
                    with self.assertRaises(ValueError):
                        v.events.check(word, canonical, altered, back)

    def test_moving_across_uncovered_scalar_is_rejected(self):
        for word, canonical, stream, back, _ in self.variants():
            touched = v.events.check(word, canonical, stream, back)["event_indices"]
            i = next(i for i in touched if stream[i][0] == "scalar"
                     and stream[i + 1][0] == "scalar" and i + 1 not in touched)
            altered = copy.deepcopy(stream)
            altered[i], altered[i + 1] = altered[i + 1], altered[i]
            with self.assertRaisesRegex(ValueError, "chronology mismatch"):
                v.events.check(word, canonical, altered, back)

    def test_integer_and_private_lifetime_controls(self):
        for word, canonical, stream, back, _ in self.variants():
            indices = v.events.check(word, canonical, stream, back)["event_indices"]
            scalar = next(i for i in indices if stream[i][0] == "scalar" and stream[i][2] == 0)
            altered = copy.deepcopy(stream)
            altered[scalar][2] = False
            with self.assertRaisesRegex(ValueError, "frame ID"):
                v.events.check(word, canonical, altered, back)
            alloc = next(i for i in indices if stream[i][:2] == ["zero_buffer", "alloc"])
            free = next(i for i in indices if stream[i][:2] == ["zero_buffer", "free"])
            altered = copy.deepcopy(stream)
            altered.insert(alloc + 1, altered.pop(free))
            with self.assertRaises(ValueError):
                v.events.check(word, canonical, altered, back)

    def test_selected_recipe_and_inverse_wrapper_controls(self):
        kernel = v.load(self.blobs[v.KERNEL], "v45_test_kernel")
        for tag in ("base", "extra"):
            word, canonical, programs, adapters = self.fixtures[tag]
            key = v.events.check(word, canonical, programs["forward"], False)["recipe_key"]
            recipe = adapters["recipes"][key]
            actual = v.native.wrappers(kernel, recipe, v.events.W, v.require)
            self.assertEqual(actual["columns_per_orientation"], 512)
            for side in ("left", "right"):
                altered = copy.deepcopy(recipe)
                altered[side]["phase"] = (altered[side]["phase"] + 1) % 4
                with self.assertRaisesRegex(ValueError, "phase-exact"):
                    v.native.wrappers(kernel, altered, v.events.W, v.require)
            full_recipe = copy.deepcopy(recipe)
            full_recipe["rank"] = 9
            with self.assertRaisesRegex(ValueError, "rank difference"):
                v.native.wrappers(kernel, full_recipe, v.events.W, v.require)

    def test_optimized_cli_rejects_real_omitted_cleanup(self):
        root = self.work / "cli"
        for tag in ("base", "extra"):
            dest = root / tag
            dest.mkdir(parents=True)
            source = self.work / tag / "local"
            for name in ("CANONICAL-WORD.json.gz", "LOCAL-PROGRAMS.json.gz", "RESIDUAL-ADAPTERS.json"):
                (dest / name).write_bytes((source / name).read_bytes())
        path = root / "base/LOCAL-PROGRAMS.json.gz"
        programs = v.read(path)
        i = next(i for i, e in enumerate(programs["backward"])
                 if e[0] == "scalar" and ["Z", 249] in e[1][1:3])
        programs["backward"].pop(i)
        path.write_bytes(gzip.compress(json.dumps(programs).encode()))
        result = subprocess.run([sys.executable, "-I", "-O", "-B", str(v.PACKAGE / "verify.py"),
                                 "--run", str(root)], capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 1)
        self.assertIn("direct event inventory/chronology mismatch", result.stderr)

    def test_json_and_capacity_boundaries(self):
        path = self.work / "duplicate.json"
        path.write_text('{"a":1,"a":2}')
        with self.assertRaisesRegex(ValueError, "duplicate JSON"):
            v.read(path)
        path.write_bytes(b" " * (v.MAX_BYTES + 1))
        with self.assertRaisesRegex(ValueError, "capacity"):
            v.read(path)

    def test_equal_operator_gauge_does_not_supply_source_binding(self):
        tag = "base"
        output = self.work / tag / "local"
        adapters = copy.deepcopy(self.fixtures[tag][3])
        recipe = adapters["recipes"]["0:275"]
        recipe["left"]["phase"] = (recipe["left"]["phase"] + 1) % 4
        recipe["right"]["phase"] = (recipe["right"]["phase"] - 1) % 4
        kernel = v.load(self.blobs[v.KERNEL], "v45_gauge_control")
        self.assertEqual(v.native.wrappers(kernel, recipe, v.events.W, v.require)
                         ["columns_per_orientation"], 512)
        dest = self.work / "gauge"
        dest.mkdir()
        shutil.copy2(output / "LOCAL-CHECKS.json", dest / "LOCAL-CHECKS.json")
        (dest / "RESIDUAL-ADAPTERS.json").write_text(json.dumps(adapters))
        with self.assertRaisesRegex(ValueError, "native receipt RESIDUAL"):
            v.bind_receipt(self.blobs, tag, dest)

    def test_corrupt_export_rejected_before_execution(self):
        root = self.work / "export"
        package = root / "research" / v.PACKAGE.name
        shutil.copytree(v.PACKAGE, package, ignore=shutil.ignore_patterns("__pycache__"))
        for name, raw in self.blobs.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
        target = root / v.ENGINE / "bw_emit.py"
        target.write_bytes(target.read_bytes() + b"\nraise RuntimeError('must not execute')\n")
        result = subprocess.run([sys.executable, "-I", "-B", str(package / "verify.py"), "--emit"],
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn("input SHA256", result.stderr)
        self.assertNotIn("must not execute", result.stderr)


if __name__ == "__main__":
    unittest.main()
