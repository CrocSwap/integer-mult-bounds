#!/usr/bin/env python3
"""Focused mathematical-boundary and package rejection tests (stdlib only)."""

import copy
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('cnot_verify', PACKAGE/'verify.py')
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)


class CertificateTests(unittest.TestCase):
    def test_symbolic_rank_obstruction(self):
        d = VERIFY.INDEPENDENT
        checks = d.proof_checks()
        self.assertEqual(checks['symbolic_label_patterns_through_four'], 31)
        # The reverse-pair choice is essential: using ab for abab does not
        # give the single rank-one monomial used in the proof.
        poly = d.coefficient_polynomials((d.A, d.B, d.A, d.B))
        good = poly[d.S] ^ poly[d.multiply(d.B, d.A)]
        wrong = poly[d.S] ^ poly[d.multiply(d.A, d.B)]
        self.assertEqual(good, {(1, 2)})
        self.assertNotEqual(wrong, good)

    def test_dirty_boundary_and_scope_controls(self):
        controls = VERIFY.controls()
        self.assertEqual(len(controls), 14)
        self.assertEqual(len(set(controls)), 14)
        self.assertIn('clean_only_dirty_leakage', controls)
        self.assertIn('rank_two_projector_underpricing', controls)

    def test_complete_receipt_and_json_types(self):
        expected = VERIFY.read_json(PACKAGE/'EXPECTED.json')
        for mutate in (
            lambda x: x['censuses'][1].update(ball3_size=47202),
            lambda x: x['censuses'][0]['exact_distance_layers_0_to_3'].__setitem__(0, True),
            lambda x: x['censuses'][1].update(intersections_through_five=1),
            lambda x: x['controls'].pop(),
            lambda x: x.update(unchecked_extra_field=True),
        ):
            modified = copy.deepcopy(expected)
            mutate(modified)
            with self.assertRaisesRegex(ValueError, 'fresh receipt differs'):
                VERIFY.compare_receipt(modified, expected)

    def test_duplicate_json_rejected(self):
        with tempfile.TemporaryDirectory(prefix='cnot-json-') as work:
            path = Path(work)/'duplicate.json'
            path.write_text('{"minimum":6,"minimum":5}')
            with self.assertRaisesRegex(ValueError, 'duplicate JSON key'):
                VERIFY.read_json(path)

    def copied_package(self, root):
        package = root/'research'/'coordinate-cnot-register-bound'
        package.mkdir(parents=True)
        for name in ('verify.py', 'independent.py', 'EXPECTED.json', 'SOURCES.json'):
            shutil.copyfile(PACKAGE/name, package/name)
        source = root/'research'/'bit-three-register-lower-bound'/'README.md'
        source.parent.mkdir(parents=True)
        shutil.copyfile(PACKAGE.parents[1]/source.relative_to(root), source)
        return package, source

    def run_export(self, package, *flags):
        return subprocess.run([sys.executable, '-I', '-B', *flags, str(package/'verify.py')],
                              cwd=package.parents[1], capture_output=True, text=True,
                              timeout=120, check=False)

    def test_read_only_relocated_optimized_replay(self):
        with tempfile.TemporaryDirectory(prefix='cnot-relocate-') as work:
            root = Path(work)
            package, source = self.copied_package(root)
            paths = list(package.iterdir())+[source]
            before = {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in paths}
            try:
                for p in paths:
                    p.chmod(0o444)
                package.chmod(0o555)
                result = self.run_export(package, '-O')
                self.assertEqual(result.returncode, 0, result.stderr[-3000:])
                self.assertIn('PASS_COORDINATE_CNOT_REGISTER_BOUND', result.stdout)
                after = {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in root.rglob('*') if p.is_file()}
                self.assertEqual(before, after)
            finally:
                package.chmod(0o755)
                for p in paths:
                    p.chmod(0o644)

    def test_external_receipt_and_source_corruption_rejected(self):
        with tempfile.TemporaryDirectory(prefix='cnot-corruption-') as work:
            package, source = self.copied_package(Path(work))
            expected = VERIFY.read_json(package/'EXPECTED.json')
            expected['censuses'][1]['minimum_paid_calls'] = 5
            (package/'EXPECTED.json').write_text(json.dumps(expected))
            result = self.run_export(package)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('fresh receipt differs', result.stderr)
            shutil.copyfile(PACKAGE/'EXPECTED.json', package/'EXPECTED.json')
            source.write_text(source.read_text()+'\ncorrupted context source\n')
            result = self.run_export(package)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('source pin mismatch', result.stderr)


if __name__ == '__main__':
    unittest.main()
