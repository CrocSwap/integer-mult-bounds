#!/usr/bin/env python3
"""Negative controls for the independent parser of the split literal program."""
from pathlib import Path
import shutil
import tempfile
import unittest

import check_sources


class SourceBindingMutants(unittest.TestCase):
    def test_rejects_changed_literals_and_suffix_graph(self):
        original_root = check_sources.ROOT
        with tempfile.TemporaryDirectory(prefix='source-binding-mutants-') as tmp:
            root = Path(tmp)
            shutil.copytree(original_root / 'inputs', root / 'inputs')
            shutil.copy2(original_root / 'source-versions.json', root)
            source = (original_root / 'MatrixData.lean').read_text()
            # Parsing precedes regeneration, so these failures cannot depend
            # on the generator or its symbolic-execution result.
            mutants = {
                'event value': source.replace('⟨1,960,978,true⟩', '⟨1,960,979,true⟩', 1),
                'event order': source.replace(
                    '⟨1,960,978,true⟩ ::\n  ⟨1,977,978,true⟩',
                    '⟨1,977,978,true⟩ ::\n  ⟨1,960,978,true⟩', 1),
                'cycle': source.replace('  chunk0_tail2\n', '  chunk0_tail1\n', 1),
                'missing suffix': source.replace('  chunk0_tail1\n', '  chunk0_tail99\n', 1),
                'cross chunk': source.replace('  chunk0_tail1\n', '  chunk1_tail1\n', 1),
                'unparsed syntax': source.replace('⟨1,960,978,true⟩', '(⟨1,960,978,true⟩)', 1),
                'unused suffix': source.replace('end SourceMatrix',
                    'def chunk95_tail1 : List Event := []\nend SourceMatrix'),
            }
            try:
                check_sources.ROOT = root
                for name, mutant in mutants.items():
                    with self.subTest(name=name):
                        self.assertNotEqual(mutant, source)
                        (root / 'MatrixData.lean').write_text(mutant)
                        with self.assertRaises(RuntimeError):
                            check_sources.check()
            finally:
                check_sources.ROOT = original_root


if __name__ == '__main__':
    unittest.main()
