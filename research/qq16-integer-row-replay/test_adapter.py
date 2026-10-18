"""Dependency invalidation and exact-domain controls, active under -O."""
from fractions import Fraction
from pathlib import Path
import json
import shutil
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import adapter


class Tests(unittest.TestCase):
    def test_every_live_input_invalidates(self):
        pins = json.loads((HERE / 'SOURCES.json').read_bytes())
        with tempfile.TemporaryDirectory(prefix='qq16-pin-control-') as temp:
            root = Path(temp)
            inputs = [e for e in pins['files'] if e['usage'] == 'input']
            for entry in inputs:
                target = root / entry['path']
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(adapter.ROOT / entry['path'], target)
            captured = adapter.authenticate(root)
            self.assertEqual(len(captured), len(inputs))
            for entry in inputs:
                target = root / entry['path']
                original = target.read_bytes()
                try:
                    target.write_bytes(original + b'\n')
                    with self.assertRaisesRegex(ValueError, 'Source pin differs'):
                        adapter.authenticate(root)
                finally:
                    target.write_bytes(original)
            # Catalogue/selected records are historical provenance, not runtime.
            for entry in pins['files']:
                if entry['usage'] == 'provenance':
                    target = root / entry['path']
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text('unrelated later provenance\n')
            self.assertEqual(adapter.authenticate(root), captured)

    def test_exact_input_domain(self):
        scalar = adapter.load('verify_scalar', adapter.authenticate())
        for unsupported in (0.5, True, complex(1)):
            with self.assertRaisesRegex(ValueError, 'exact integers or Fractions'):
                adapter.replay([], [{0: unsupported}], scalar.register, scalar.need)
        self.assertEqual(adapter.replay([], [{1: 1 << 500, 2: Fraction(1, 3)}],
                                        scalar.register, scalar.need),
                         [{1: Fraction(1 << 500), 2: Fraction(1, 3)}])

    def test_zero_key_and_input_alias_semantics(self):
        scalar = adapter.load('verify_scalar', adapter.authenticate())
        initial = [{} for _ in range(712)]
        shared = {4: Fraction(2, 7), 8: Fraction(0)}
        initial[0] = initial[1] = shared
        events = [['scalar', ['scale', ['L', 0], 0, 1]],
                  ['scalar', ['add', ['L', 0], ['L', 1], 0, 1]]]
        actual = adapter.replay(events, initial, scalar.register, scalar.need)
        self.assertEqual(actual, scalar.replay(events, initial))
        self.assertEqual(actual[0], {})
        self.assertEqual(actual[1], shared)
        self.assertIs(initial[0], initial[1])


if __name__ == '__main__':
    unittest.main()
