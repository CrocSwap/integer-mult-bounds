"""Independent small-domain and tampering controls for the endpoint audit."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('endpoint_audit', HERE / 'verify.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def subspaces(n):
    """Enumerate subspaces as point sets without elimination or Gaussian counts."""
    seen = {frozenset({0})}
    pending = list(seen)
    while pending:
        space = pending.pop()
        for vector in range(1, 2**n):
            expanded = space | frozenset(point ^ vector for point in space)
            if expanded not in seen:
                seen.add(expanded)
                pending.append(expanded)
    return seen


class EndpointTests(unittest.TestCase):
    def test_small_complete_subspace_census(self):
        for n in range(1, 5):
            spaces = subspaces(n)
            for k in range(n + 1):
                self.assertEqual(sum(len(space) == 2**k for space in spaces), audit.gaussian(n, k))
            for space in spaces:
                canonical = audit.basis(sorted(space))
                self.assertEqual(audit.closure(canonical), space)
                self.assertEqual(len(space), 2**len(canonical))

    def test_quotient_counts_with_fixed_entrance(self):
        spaces = subspaces(4)
        for s in range(4):
            entrance = audit.closure([1 << i for i in range(s)])
            for d in range(s, 5):
                count = sum(len(space) == 2**d and entrance <= space for space in spaces)
                self.assertEqual(count, audit.gaussian(4-s, d-s))

    def test_endpoint_adversary_preserves_start_and_rank(self):
        word = audit.read(audit.ROOT / audit.WORD)
        for item in audit.trace(word):
            if len(item['end_basis']) == 9:
                continue
            _, replacement, missing = audit.replace_endpoint(word, item)
            self.assertEqual(len(replacement), len(item['end_basis']))
            self.assertTrue(audit.closure(item['start_basis']) <= audit.closure(replacement))
            self.assertNotIn(missing, audit.closure(replacement))
            self.assertIn(missing, audit.closure(item['end_basis']))

    def test_noncontaining_cap_rejected_by_new_span_certificate(self):
        word = audit.read(audit.ROOT / audit.WORD)
        item = next(item for item in audit.trace(word) if len(item['end_basis']) < 9)
        mutant, _, _ = audit.replace_endpoint(word, item)
        with self.assertRaisesRegex(ValueError, 'Endpoint has slack'):
            audit.trace(mutant)

    def test_corrupt_live_input_is_rejected(self):
        pin = next(pin for pin in json.loads((HERE / 'SOURCES.json').read_text())['files']
                   if pin['usage'] == 'input')
        with tempfile.TemporaryDirectory(prefix='k8-source-control-') as temporary:
            path = Path(temporary) / pin['path']
            path.parent.mkdir(parents=True)
            path.write_bytes((audit.ROOT / pin['path']).read_bytes() + b'\n')
            with self.assertRaisesRegex(ValueError, 'Source pin mismatch'):
                audit.check_inputs(Path(temporary))

    def test_labels_must_belong_to_ambient_space(self):
        for label in (-1, 512, True, 1.5):
            with self.assertRaisesRegex(ValueError, 'Label outside'):
                audit.basis([label])


if __name__ == '__main__':
    unittest.main()
