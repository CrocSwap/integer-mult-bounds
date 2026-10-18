#!/usr/bin/env python3
"""Failure-sensitive checks for the mathematical scope and replay boundary."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


primary = module('primary_full_occupancy', 'verify.py')
oracle = module('regular_full_occupancy', 'independent.py')


class PackageTests(unittest.TestCase):
    def copied(self, directory):
        out = Path(directory) / 'renamed-package'
        shutil.copytree(HERE, out, ignore=shutil.ignore_patterns('__pycache__'))
        return out

    def run_check(self, package, script):
        return subprocess.run([sys.executable, '-I', '-O', '-B', str(package / script)],
                              cwd=package.parent, capture_output=True, text=True,
                              timeout=30, env={**os.environ, 'PYTHONOPTIMIZE':'2'})

    def test_scope_and_chronology(self):
        direct = [[g, 1 << i, 1 << i] for i in range(4) for g in 'aba']
        self.assertEqual(primary.replay(direct,4), primary.target(4,4))
        self.assertEqual(oracle.replay(direct,4), oracle.target(4,4))
        ordinary_rotation = direct[1:] + direct[:1]
        self.assertNotEqual(primary.replay(ordinary_rotation,4), primary.target(4,4))
        self.assertNotEqual(oracle.replay(ordinary_rotation,4), oracle.target(4,4))
        self.assertEqual(primary.replay(primary.rotate(direct,1),4), primary.target(4,4))
        # Partial-target conjugation is outside the alphabet, not just a different N.
        r,t,call = 5,4,['a',17,1]
        transformed = oracle.bm(oracle.bm(oracle.target(r,t),oracle.operator(call,r)),oracle.target(r,t))
        self.assertTrue(all(transformed != oracle.operator([g,u,v],r)
                            for u,v in oracle.scalar_projectors(r) for g in 'ab'))

    def test_domains_and_natural_alias(self):
        for word in ([['a',True,1]],[['b',1.0,1]],[['s',1,1]],[['a',3,3]],[['a',0,1]]):
            with self.assertRaises((primary.Invalid, TypeError, ValueError)):
                primary.replay(word,2)
            with self.assertRaises((oracle.Failure, TypeError, ValueError)):
                oracle.replay(word,2)
        # Sum of all six group elements is invisible naturally but not regularly.
        natural = [0]*4
        regular = [0]*6
        for g in oracle.GROUP:
            natural = [x ^ y for x,y in zip(natural,g)]
            regular = [x ^ y for x,y in zip(regular,oracle.regular(g))]
        self.assertEqual(natural,[0]*4)
        self.assertNotEqual(regular,[0]*6)
        self.assertEqual(regular,[63]*6)

    def test_corrupt_receipts_rejected_by_both(self):
        changes = [
            lambda d: d['claim'].__setitem__('minimum',10),
            lambda d: d['claim'].__setitem__('extra_dirty_roles',True),
            lambda d: d.__setitem__('cut_checks',288.0),
            lambda d: d['fixtures'][12]['word'][0].__setitem__(1,3),
            lambda d: d['label_screen']['rows'][-1].__setitem__('after_cuts',-1),
            lambda d: d['workspace_boundary'].__setitem__('alphabet_size',991),
            lambda d: d.__setitem__('fixtures',[]),
        ]
        original = json.loads((HERE/'RESULT.json').read_text())
        with tempfile.TemporaryDirectory() as temp:
            package = self.copied(temp)
            for change in changes:
                data = json.loads(json.dumps(original))
                change(data)
                (package/'RESULT.json').write_text(json.dumps(data))
                for script in ('verify.py','independent.py'):
                    with self.subTest(change=changes.index(change), script=script):
                        self.assertNotEqual(self.run_check(package,script).returncode,0)

    def test_source_and_json_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            package = self.copied(temp)
            source = package/'inputs/PR1722-PROOF.md'
            old = source.read_bytes()
            source.write_bytes(old+b'\nchanged\n')
            for script in ('verify.py','independent.py'):
                self.assertNotEqual(self.run_check(package,script).returncode,0)
            source.unlink()
            for script in ('verify.py','independent.py'):
                self.assertNotEqual(self.run_check(package,script).returncode,0)
            source.write_bytes(old)
            result = package/'RESULT.json'
            for text in ('{"claim": {}, "claim": {}}', '{"claim": NaN}'):
                result.write_text(text)
                for script in ('verify.py','independent.py'):
                    self.assertNotEqual(self.run_check(package,script).returncode,0)
            result.unlink()
            self.assertNotEqual(self.run_check(package,'verify.py').returncode,0)
            self.assertFalse(result.exists())

    def test_read_only_relocation_and_determinism(self):
        with tempfile.TemporaryDirectory() as temp:
            package = self.copied(temp)
            paths = [p for p in package.rglob('*') if p.is_file()]
            before = {p.relative_to(package).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
            for p in paths:
                p.chmod(0o444)
            dirs = [p for p in package.rglob('*') if p.is_dir()]+[package]
            for p in dirs:
                p.chmod(0o555)
            try:
                for script in ('verify.py','independent.py'):
                    completed = self.run_check(package,script)
                    self.assertEqual(completed.returncode,0,completed.stderr)
                after = {p.relative_to(package).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in package.rglob('*') if p.is_file()}
                self.assertEqual(before,after)
            finally:
                for p in dirs:
                    p.chmod(0o755)
                for p in paths:
                    p.chmod(0o644)
        self.assertEqual(primary.canonical(primary.compute()), primary.canonical(primary.read_json(HERE/'RESULT.json')))


if __name__ == '__main__':
    unittest.main()
