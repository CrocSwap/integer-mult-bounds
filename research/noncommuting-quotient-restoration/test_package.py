#!/usr/bin/env python3
"""Semantic, admission, relocation and on-disk corruption controls."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import model as m
import oracle as o
import verify as v


class Contracts(unittest.TestCase):
    def test_noncommuting_kernel(self):
        self.assertNotEqual(m.compose(m.A,m.B),m.compose(m.B,m.A))
        p = m.compose(m.B,m.A)
        self.assertNotEqual(p,m.IDENTITY)
        self.assertEqual(m.character(p),1)
        word,cuts = m.batch()
        prefix = o.columns(word[:cuts[1]],13)
        self.assertEqual(prefix[12],o.expected_batch(1,2)[12])
        self.assertNotEqual(prefix[6:12],o.expected_batch(1,2)[6:12])

    def test_admission_is_enforced(self):
        with self.assertRaisesRegex(ValueError,'equivariance'):
            m.batch(reader=(1,0,0,0,0,0))

    def test_observer_prices(self):
        self.assertEqual(m.plan(output_cuts=(2,))[0],6)
        self.assertEqual(m.plan(output_cuts=(1,))[0],28)
        self.assertEqual(m.plan(workspace_cuts=(2,))[0],30)
        self.assertEqual(m.plan(output_cuts=tuple(range(1,7)))[0],72)

    def test_source_need_not_commute(self):
        f = v.source_matrix(1,True)
        p = m.pull(m.A)
        pf = [f[p[i]] for i in range(6)]
        fp = [[f[i][p.index(j)] for j in range(6)] for i in range(6)]
        self.assertNotEqual(pf,fp)
        self.assertEqual(o.columns(m.echo(matrix=f),13),o.expected_echo(1,f))

    def test_literal_inverse_and_dirty_sources(self):
        word = m.echo()
        initial = [(-1)**i*(i+1) for i in range(13)]
        result = o.run(word,initial)
        self.assertEqual(result[:12],initial[:12])
        self.assertEqual(result[12],initial[12]+6*sum(o.R[j]*initial[j] for j in range(6)))
        self.assertEqual(o.run(m.invert_word(word),result),initial)

    def test_semantic_failures(self):
        self.assertEqual(len(v.failure_controls()),12)

    def test_invalid_ports_and_prices(self):
        for call in (lambda:m.echo(width=0),lambda:m.batch(corrections=(m.IDENTITY,)),
                     lambda:m.echo(corrections=(m.A,)+(m.IDENTITY,)*6),
                     lambda:m.plan(output_cuts=(0,)),lambda:m.plan(add_price=0),
                     lambda:m.source_word(1,[[1]]),lambda:m.validate_word([('ADD',0,0,1)],13)):
            with self.assertRaises(ValueError):
                call()

    def test_source_corruptions(self):
        with tempfile.TemporaryDirectory(prefix='quotient-pins-',dir=os.environ.get('IMB_TEST_TMPDIR')) as name:
            directory = Path(name).resolve()
            shutil.copytree(HERE/'references',directory/'references')
            shutil.copy2(HERE/'PREDECESSORS.json',directory/'PREDECESSORS.json')
            self.assertEqual(v.source_bindings(directory),2)
            note = directory/'references/PR1287-README.md'
            original = note.read_bytes()
            note.write_bytes(original+b'\ncorruption\n')
            with self.assertRaises(ValueError):
                v.source_bindings(directory)
            note.write_bytes(original)
            pins = json.loads((directory/'PREDECESSORS.json').read_text())
            pins[0]['commit'] = '0'*40
            (directory/'PREDECESSORS.json').write_text(json.dumps(pins))
            with self.assertRaises(ValueError):
                v.source_bindings(directory)

    def test_relocated_and_certificate_corruption(self):
        with tempfile.TemporaryDirectory(prefix='quotient-relocation-',dir=os.environ.get('IMB_TEST_TMPDIR')) as name:
            directory = Path(name).resolve()
            relocated = directory/'package'
            shutil.copytree(HERE,relocated,ignore=shutil.ignore_patterns('__pycache__'))
            result = subprocess.run([sys.executable,'-I','-O','-B',str(relocated/'verify.py')],cwd=directory,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            certificate = relocated/'CERTIFICATE.json'
            data = json.loads(certificate.read_text())
            data['word']['records'][0]['invoice']['NEG'] -= 1
            certificate.write_text(json.dumps(data))
            failed = subprocess.run([sys.executable,'-I','-O','-B',str(relocated/'verify.py')],cwd=directory,capture_output=True,text=True)
            self.assertNotEqual(failed.returncode,0)
            self.assertIn('certificate changed',failed.stderr)


if __name__ == '__main__':
    unittest.main()
