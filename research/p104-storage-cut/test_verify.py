#!/usr/bin/env python3
"""Behavioral boundary tests for the finite cut certificate."""
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

P = Path(__file__).resolve().parent
ROOT = P.parents[1]


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


V = module(P/'verify.py', 'cut_primary_test')
O = module(P/'oracle.py', 'cut_oracle_test')


class CutBehavior(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.word = V.load_sources()

    def run_checker(self, package, *options, optimized=False):
        argv = [sys.executable, '-I', '-B']
        if optimized:
            argv.append('-O')
        result = subprocess.run(argv+[str(package/'verify.py'), *map(str, options)],
                                capture_output=True, text=True, timeout=30)
        return result

    def export(self, root):
        package = root/'research/p104-storage-cut'
        shutil.copytree(P, package, ignore=shutil.ignore_patterns('__pycache__'))
        for item in json.loads((P/'SOURCES.json').read_text())['files']:
            if item['usage'] == 'input':
                dst = root/item['path']; dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT/item['path'], dst)
        return package

    def test_partition_comparison_detects_count_preserving_corruption(self):
        primary = V.analyze(self.word)
        oracle = O.analyze(self.word)
        V.compare_oracle(self.word, primary, oracle)
        # Preserve counts, span size and dimension census: swap one complete
        # one-dimensional frame for another, rather than editing a count.
        bad = deepcopy(oracle)
        index = next(i for i, x in enumerate(bad['reachable_frames']) if len(x) == 2)
        alternative = next(x for x in bad['coreachable_frames'] if len(x) == 2)
        bad['reachable_frames'][index] = alternative
        with self.assertRaisesRegex(ValueError, 'independent source partition'):
            V.compare_oracle(self.word, primary, bad)
        bad = deepcopy(oracle); bad['transport_event_signatures_sha256'] = '0'*64
        with self.assertRaisesRegex(ValueError, 'independent every-transport signature'):
            V.compare_oracle(self.word, primary, bad)

    def test_equivalent_subspace_presentations(self):
        word = deepcopy(self.word)
        for field in ('initial_frames', 'final_frames'):
            for role, b in word[field].items():
                word[field][role] = list(reversed(b))+[0]+b[:1]
        for e in word['program']:
            for i in {'transport':(2,3),'add':(4,),'copy':(3,),'zero':(2,),'erase':(2,)}[e[0]]:
                b=e[i]; e[i]=list(reversed(b))+[0]+b[:1]
        self.assertEqual(V.analyze(word), V.analyze(self.word))
        self.assertEqual(O.analyze(word), O.analyze(self.word))

    def test_actual_cut_guard_removal_is_detected(self):
        code=(P/'verify.py').read_text()
        guard="    need(not r & targets, 'static source-target cut failed')"
        self.assertEqual(code.count(guard), 1)
        with tempfile.TemporaryDirectory(prefix='p104-cut-guard-') as td:
            path=Path(td)/'without_guard.py'
            path.write_text(code.replace(guard, '    pass  # intentionally removed separation guard'))
            broken=module(path, 'deliberately_removed_cut_guard')
            with self.assertRaisesRegex(RuntimeError, 'negative control unexpectedly accepted'):
                broken.controls(self.word)

    def test_relocated_readonly_normal_and_optimized(self):
        with tempfile.TemporaryDirectory(prefix='p104-cut-export-') as td:
            root=Path(td); package=self.export(root)
            def inventory():
                return {str(f.relative_to(root)):hashlib.sha256(f.read_bytes()).hexdigest()
                        for f in root.rglob('*') if f.is_file()}
            before=inventory()
            for optimized in (False, True):
                result=self.run_checker(package, optimized=optimized)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('PASS_P104_STORAGE_CUT_no_new_kappa', result.stdout)
            self.assertEqual(before, inventory())

    def test_source_pin_and_missing_evidence(self):
        with tempfile.TemporaryDirectory(prefix='p104-cut-source-') as td:
            root=Path(td); package=self.export(root); source=root/V.WITNESS
            data=source.read_bytes(); source.write_bytes(data+b'\n')
            result=self.run_checker(package)
            self.assertNotEqual(result.returncode, 0); self.assertIn('source pin:', result.stderr)
            source.unlink(); result=self.run_checker(package)
            self.assertNotEqual(result.returncode, 0); self.assertIn('FileNotFoundError', result.stderr)

    def test_fixed_receipt_and_exclusive_generation(self):
        with tempfile.TemporaryDirectory(prefix='p104-cut-receipt-') as td:
            root=Path(td); package=self.export(root); receipt=package/'RESULT.json'
            original=receipt.read_bytes(); receipt.unlink()
            result=self.run_checker(package)
            self.assertNotEqual(result.returncode, 0); self.assertIn('FileNotFoundError', result.stderr)
            bad=json.loads(original); bad['added_whole_array_transport_floor']=95
            receipt.write_text(json.dumps(bad)); result=self.run_checker(package)
            self.assertNotEqual(result.returncode, 0); self.assertIn('fixed receipt mismatch', result.stderr)
            output=root/'new-receipt.json'; result=self.run_checker(package, '--write', output)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(output.read_bytes()), json.loads(original))
            result=self.run_checker(package, '--write', output)
            self.assertNotEqual(result.returncode, 0); self.assertIn('FileExistsError', result.stderr)
            self.assertEqual(json.loads(output.read_bytes()), json.loads(original))


if __name__ == '__main__':
    unittest.main(verbosity=2)
