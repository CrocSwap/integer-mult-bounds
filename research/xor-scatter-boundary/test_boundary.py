"""Behavior and rejection controls for xor-scatter-v1. Nick Petalas. Apache-2.0."""

import copy
import gzip
import json
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
import boundary
import verify


class BoundaryTests(unittest.TestCase):
    def test_complete_small_domain_and_aliases(self):
        self.assertEqual(
            verify.exhaustive(),
            {"rows": 1093, "alias_cases": 29511, "max_row_length": 6},
        )

    def test_nonmutating_canonical_form(self):
        word = {
            "v": 2,
            "R": 2,
            "ret": [4, 4, 5],
            "scatter": [[2, 0, 2, 1, 1], [1, 1, 1]],
        }
        before = copy.deepcopy(word)
        normal, count = boundary.normalize(word)
        self.assertEqual(word, before)
        self.assertEqual(normal["scatter"], [[0], [1]])
        self.assertEqual(normal["ret"], [4, 4, 5])
        self.assertEqual(count, 8)
        self.assertEqual(boundary.normalize(normal)[0], normal)

    def test_schema_rejections(self):
        good = {"v": 1, "R": 1, "ret": [2], "scatter": [[0]]}
        changes = [
            {"v": True},
            {"v": 257},
            {"R": -1},
            {"R": 4097},
            {"ret": [1]},
            {"ret": [True]},
            {"ret": [2] * 257},
            {"scatter": []},
            {"scatter": [[True]]},
            {"scatter": [[0.0]]},
            {"scatter": [[-1]]},
            {"scatter": [[1]]},
            {"scatter": [[0] * 4097]},
            {"scatter": [(0,)]},
        ]
        for change in changes:
            with self.subTest(change=str(change)[:60]), self.assertRaises(ValueError):
                boundary.normalize({**good, **change})
        oversized = {"v": 17, "R": 1, "ret": [34], "scatter": [[0] * 4096] * 17}
        with self.assertRaisesRegex(ValueError, "65536"):
            boundary.normalize(oversized)
        with self.assertRaises(ValueError):
            boundary.normalize([])
        self.assertEqual(boundary.normalize({**good, "ret": [], "scatter": [[]]})[1], 0)

    def test_size_and_compression_boundary(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "large.gz"
            path.write_bytes(gzip.compress(b"x" * (boundary.MAX_BYTES + 1), mtime=0))
            with self.assertRaisesRegex(ValueError, "5 MiB"):
                boundary.read_bounded(path, compressed=True)
            path.write_bytes(b"not gzip")
            with self.assertRaises(OSError):
                boundary.read_bounded(path, compressed=True)

    def test_validation_and_source_corruption_publish_nothing(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            word = verify.sources(boundary.ROOT)
            source = directory / "word.json"
            source.write_text(json.dumps(word), encoding="utf-8")
            for path in (boundary.CHECKER, boundary.EXPORTER):
                target = directory / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((boundary.ROOT / path).read_bytes())
            for path in (boundary.CHECKER, boundary.EXPORTER):
                target = directory / path
                original = target.read_bytes()
                target.write_bytes(original + b"\n# changed source\n")
                with self.assertRaisesRegex(ValueError, "source pin"):
                    boundary.execute(
                        "export", source, directory / "out", directory, directory
                    )
                self.assertFalse((directory / "out").exists())
                target.write_bytes(original)
            word["scatter"][0].append(True)
            source.write_text(json.dumps(word), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "invalid scatter slot"):
                boundary.execute(
                    "export", source, directory / "out", directory, directory
                )
            self.assertFalse((directory / "out").exists())

    def test_existing_output_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "occupied"
            output.mkdir()
            keep = output / "keep"
            keep.write_bytes(b"preserve")
            with self.assertRaisesRegex(ValueError, "already exists"):
                boundary.execute("export", boundary.ROOT / verify.WORD, output)
            self.assertEqual(keep.read_bytes(), b"preserve")
            link = Path(temporary) / "dangling"
            link.symlink_to(Path(temporary) / "missing")
            with self.assertRaisesRegex(ValueError, "already exists"):
                boundary.execute("export", boundary.ROOT / verify.WORD, link)
            self.assertTrue(link.is_symlink())

    def test_timeout_cleans_private_snapshots(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            with (
                patch.object(
                    boundary.subprocess,
                    "run",
                    side_effect=subprocess.TimeoutExpired("test", 60),
                ),
                self.assertRaises(subprocess.TimeoutExpired),
            ):
                boundary.execute(
                    "check", boundary.ROOT / verify.WORD, scratch=directory
                )
            self.assertEqual(list(directory.iterdir()), [])

    def test_actual_cli_checks_original_and_normalized(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            word = verify.sources(boundary.ROOT)
            word["scatter"][0].extend([0, 0])
            source = directory / "paired.json.gz"
            source.write_bytes(gzip.compress(json.dumps(word).encode(), mtime=0))
            command = [
                sys.executable,
                "-I",
                "-O",
                "-Werror",
                "-B",
                str(PACKAGE / "boundary.py"),
                "check",
                str(source),
                "--scratch",
                str(directory),
            ]
            run = subprocess.run(
                command, capture_output=True, text=True, timeout=90, check=False
            )
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(json.loads(run.stdout)["normalized_scatter_terms"], 527)
            body = boundary.scripts(boundary.ROOT)[boundary.CHECKER]
            boundary.delegate(body, source, directory, "original-checker.py")
            word["scatter"][0].append(False)
            source.write_bytes(gzip.compress(json.dumps(word).encode(), mtime=0))
            rejected = subprocess.run(
                command, capture_output=True, text=True, timeout=90, check=False
            )
            self.assertEqual(rejected.returncode, 2)
            self.assertIn("invalid scatter slot", rejected.stderr)

    def test_emitted_count_and_semantic_mutants(self):
        base = boundary.ROOT
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            output = directory / "out"
            boundary.execute("export", base / verify.WORD, output, scratch=directory)
            path = output / "249-records.bin"
            events = list(struct.iter_unpack("<6i", path.read_bytes()))
            position = next(i for i, e in enumerate(events) if e[0] == 1 and e[5] == 3)
            removed = events[:position] + events[position + 1 :]
            path.write_bytes(b"".join(struct.pack("<6i", *e) for e in removed))
            with self.assertRaisesRegex(ValueError, "invoice"):
                boundary.inspect_export(output, 527, 9)
            self.assertNotEqual(
                verify.record_action(path.read_bytes(), 661),
                verify.word_action(verify.sources(base)),
            )
            changed = list(events[position])
            changed[1] = 112 if changed[1] != 112 else 113
            events[position] = tuple(changed)
            path.write_bytes(b"".join(struct.pack("<6i", *e) for e in events))
            self.assertEqual(
                boundary.inspect_export(output, 527, 9)["scatter_adds"], 527
            )
            self.assertNotEqual(
                verify.record_action(path.read_bytes(), 661),
                verify.word_action(verify.sources(base)),
            )


if __name__ == "__main__":
    unittest.main()
