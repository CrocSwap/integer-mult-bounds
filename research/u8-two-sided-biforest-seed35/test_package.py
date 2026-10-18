"""Focused provenance, pricing and corruption controls for the finite U8 bi-forest package.

Stephan Arrington (@steph4n-gh) with substantial Google DeepMind Antigravity
assistance. Apache-2.0.
"""
import copy
from fractions import Fraction as Q
import gzip
import io
from pathlib import Path
import shutil
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import experiment as e
import independent


class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.word, cls.programs, cls.checks = e.load()
        cls.panel, cls.recipe = e.construct(cls.word)

    def source_closure(self, root):
        pins = e.read(e.HERE / 'SOURCES.json')
        for item in pins['files']:
            source = e.ROOT / item['path']
            dest = root / item['path']
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, dest)
        arc_src = e.ROOT / pins['archive']['path']
        arc_dst = root / pins['archive']['path']
        arc_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(arc_src, arc_dst)

    def _rewrite_archive_member(self, archive_path, member_name, new_bytes):
        members = []
        with tarfile.open(archive_path, 'r:gz') as src:
            for info in src.getmembers():
                raw = src.extractfile(info).read() if info.isfile() else b''
                if info.name == member_name:
                    raw = new_bytes
                members.append((info.name, raw))
        with tarfile.open(archive_path, 'w:gz', compresslevel=1) as dst:
            for name, raw in members:
                info = tarfile.TarInfo(name=name)
                info.size = len(raw)
                dst.addfile(info, io.BytesIO(raw))

    def test_recompression_keeps_mathematical_input(self):
        with tempfile.TemporaryDirectory(prefix='u8 biforest closure ') as tmp:
            root = Path(tmp)
            self.source_closure(root)
            arc = root / e.ARCHIVE
            with tarfile.open(arc, 'r:gz') as tf:
                raw_word = tf.extractfile('native/local/CANONICAL-WORD.json.gz').read()
            recompressed = gzip.compress(gzip.decompress(raw_word), compresslevel=1, mtime=1234567)
            self._rewrite_archive_member(arc, 'native/local/CANONICAL-WORD.json.gz', recompressed)
            with patch.object(e, 'ROOT', root):
                self.assertEqual(e.load()[0], self.word)

    def test_changed_and_missing_source_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.source_closure(root)
            arc = root / e.ARCHIVE
            changed = copy.deepcopy(self.word)
            changed['compensation'][0][3] *= -1
            self._rewrite_archive_member(
                arc, 'native/local/CANONICAL-WORD.json.gz', gzip.compress(e.canonical(changed))
            )
            with patch.object(e, 'ROOT', root):
                with self.assertRaisesRegex(ValueError, 'archive member pin'):
                    e.load()
                arc.unlink()
                with self.assertRaises(FileNotFoundError):
                    e.load()

    def test_all_emitted_coefficients_exact_with_dirty_work(self):
        coefficients = set()
        for programs in (self.programs, e.replace_programs(self.word, self.programs, self.panel)):
            for events in programs.values():
                for event in events:
                    if event[0] == 'scalar' and event[1][0] == 'add':
                        coefficients.add(Q(event[1][3], event[1][4]))
        for q in sorted(coefficients):
            result = independent.replay(
                e.lower(['add', ['L', 1], ['L', 0], q.numerator, q.denominator]),
                n=2, centers=0,
            )
            expected = {
                'denominator_power': q.denominator.bit_length() - 1,
                'terms': [[0, q.numerator], [1, q.denominator]],
            }
            self.assertEqual(result['endpoint']['L'][1], expected)
            self.assertEqual(result['endpoint']['L'][0], {'denominator_power': 0, 'terms': [[0, 1]]})
            self.assertEqual(result['endpoint']['W'][0], {'denominator_power': 0, 'terms': []})
            cost = 3 + len(bin(abs(q.numerator))) - 3 + bin(abs(q.numerator)).count('1') + q.denominator.bit_length() - 1
            self.assertEqual(result['primitive_count'], cost)
        self.assertGreater(len(coefficients), 80)

    def test_non_scalar_and_other_scalar_segments_unchanged(self):
        changed = e.replace_programs(self.word, self.programs, self.panel)
        begin = 1 + len(self.word['precondition'])
        end = begin + len(self.word['compensation'])
        for name, original in self.programs.items():
            self.assertEqual(changed[name][:begin], original[:begin])
            self.assertEqual(changed[name][begin + len(self.panel):], original[end:])
            self.assertEqual([x for x in changed[name] if x[0] != 'scalar'],
                             [x for x in original if x[0] != 'scalar'])

    def test_repeated_helpers_fail_independent_recipe(self):
        bad = copy.deepcopy(self.recipe)
        bad['helper_forest'].append(bad['helper_forest'][0])
        with self.assertRaisesRegex(independent.ReplayError, 'invalid forest edge'):
            independent.check_recipe(self.word, bad)

    def test_tampered_cost_fails_independent_recipe(self):
        bad = copy.deepcopy(self.recipe)
        bad['two_sided_biforest_panel_price'] -= 1
        with self.assertRaisesRegex(independent.ReplayError, 'complete panel price'):
            independent.check_recipe(self.word, bad)

    def test_typed_json_comparison_distinguishes_bool(self):
        self.assertNotEqual(e.canonical({'price': 1}), e.canonical({'price': True}))


if __name__ == '__main__':
    unittest.main()
