#!/usr/bin/env python3
"""Independent local matrix checks and bounded source/receipt tests."""
import copy
from fractions import Fraction
import importlib.util
import itertools
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location('composition_audit', HERE/'verify.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def matrix_identity(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def matrix_product(left,right):
    n = len(left)
    return [[sum(left[i][k]*right[k][j] for k in range(n)) % 2 for j in range(n)] for i in range(n)]


def small_gate_matrix(gates, roles):
    n = len(roles)
    indices = {r:i for i,r in enumerate(roles)}
    result = matrix_identity(n)
    for _,d,ss in gates:
        E = matrix_identity(n)
        for s in ss:
            E[indices[d]][indices[s]] ^= 1
        result = matrix_product(E,result)
    return result


def set_replay(word, reverse=False):
    """Independently construct phases and scatter snapshots using finite sets."""
    n,v = 2*word['v']+word['R'],word['v']
    rows = [{i} for i in range(n)]+[set()]
    phases = [('add',d,s) for section in ('D','A') for _,d,sources in word[section] for s in sources]
    for j,c in enumerate(word['ret']):
        phases.append(('save',n,c))
        phases.extend(('add',v+t,n) for t,sources in enumerate(word['scatter']) if j in sources)
        phases.append(('discard',n,c))
    phases.extend(('add',d,s) for section in ('B','C') for _,d,sources in word[section] for s in sources)
    for kind,d,s in (reversed(phases) if reverse else phases):
        if reverse:
            kind = {'save':'discard','discard':'save'}.get(kind,kind)
        if kind == 'add':
            rows[d].symmetric_difference_update(rows[s])
        elif kind == 'save':
            if rows[d]:
                raise ValueError('copy dirt')
            rows[d] = set(rows[s])
        else:
            if rows[d] != rows[s]:
                raise ValueError('invalid erase')
            rows[d] = set()
    if rows[-1]:
        raise ValueError('dirty scratch endpoint')
    return rows[:-1]


def fractional_rank(original):
    rows = [[Fraction(x) for x in row] for row in original]
    rank = 0
    for column in range(8):
        pivot = next((r for r in range(rank,len(rows)) if rows[r][column]),None)
        if pivot is None:
            continue
        rows[rank],rows[pivot] = rows[pivot],rows[rank]
        lead = rows[rank][column]
        rows[rank] = [x/lead for x in rows[rank]]
        for r in range(rank+1,len(rows)):
            scale = rows[r][column]
            if scale:
                rows[r] = [x-scale*y for x,y in zip(rows[r],rows[rank])]
        rank += 1
    return rank


class CompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.word,cls.original = audit.input_word()
        cls.built = audit.variants(cls.word)

    def test_all_local_conjugation_cases_by_dense_matrix_products(self):
        roles = [audit.A,audit.B,111,112,222]
        G = small_gate_matrix([audit.shear()],roles)
        for d in roles:
            eligible = [s for s in roles if s != d]
            for count in range(1,len(eligible)+1):
                for ss in itertools.combinations(eligible,count):
                    gate = [0,d,list(ss)]
                    expected = matrix_product(G,matrix_product(small_gate_matrix([gate],roles),G))
                    actual = small_gate_matrix(audit.conjugated_body({'D':[gate]}),roles)
                    self.assertEqual(expected,actual,(d,ss))

    def test_all_full_dirty_columns_both_directions_with_set_oracle(self):
        expected = [{r} for r in range(661)]
        for t in range(111):
            expected[111+t].add(t)
        for name,word in self.built.items():
            for reverse in (False,True):
                rows = set_replay(word,reverse)
                primary = audit.execute(audit.stream(word),661,reverse=reverse)
                self.assertEqual([sum(1 << x for x in row) for row in rows],primary)
                if name == 'naive_entry':
                    self.assertNotEqual(expected,rows)
                else:
                    self.assertEqual(expected,rows)

    def test_frame_ranks_by_separate_fraction_elimination(self):
        for frame in self.word['frames']:
            rows = [self.word['lines'][i] for i in frame]
            self.assertEqual(fractional_rank(rows),audit.integer_rank(rows))
        base,paths = audit.frame_bill(self.word)
        self.assertEqual(5129,base['mass'])
        for word in self.built.values():
            self.assertEqual((base,paths),audit.frame_bill(word))

    def test_exact_three_variant_bills_and_literal_controls(self):
        expected = {'baseline':(11500,5548,25717,5911840), 'naive_entry':(11503,5551,26097,5912595), 'whole_prefix':(11509,5557,28453,5913350), 'middle_wrap':(11503,5551,26173,5911840)}
        for name,word in self.built.items():
            bill = audit.price(word)
            self.assertEqual(expected[name],tuple(bill[k] for k in ('ADDs','D_ADDs','F','B')))
            self.assertEqual((9,9),(bill['COPYs'],bill['ERASEs']))
            self.assertTrue(bill['local_guard'] and bill['nine_stage_guard'])
        controls = audit.controls(self.word,self.built,audit.d_rows(self.word))
        self.assertEqual(7,len(controls))
        self.assertTrue(all(c['rejected'] for c in controls))
        overlarge = audit.precision(1 << 105,1)
        self.assertFalse(overlarge['local_guard'])

    def test_operator_naivety_and_virtual_splice_are_distinct(self):
        self.assertEqual(audit.d_rows(self.original),audit.d_rows(self.word))
        self.assertIsNotNone(audit.first_difference(audit.d_rows(self.built['naive_entry']),audit.d_rows(self.word)))
        virtual = copy.deepcopy(self.word)
        virtual['D'] = copy.deepcopy(self.original['D'])
        self.assertTrue(all(audit.virtual_flags(virtual).values()))

    def test_json_and_operand_alias_rejections(self):
        self.assertNotEqual(audit.typed(True),audit.typed(1))
        for raw in ('{"x":1,"x":2}','{"x":1.0}'):
            with self.assertRaises(audit.Reject):
                audit.load_json(raw)
        word = copy.deepcopy(self.word)
        word['D'][0] = [0,audit.A,[audit.A]]
        with self.assertRaises(audit.Reject):
            audit.d_rows(word)
        word = copy.deepcopy(self.built['whole_prefix'])
        word['D'][0][0] = 2
        with self.assertRaises(audit.Reject):
            audit.d_rows(word)
        word = copy.deepcopy(self.built['whole_prefix'])
        word['D'] = [[0,222,[111]],[0,222,[111]]] + word['D']
        # Unchecked exact scalar replay verifies this feedback pair is neutral.
        rows = [1 << r for r in range(661)]
        for _,d,ss in word['D']:
            for s in ss:
                rows[d] ^= rows[s]
        self.assertEqual(audit.d_rows(self.built['whole_prefix']),rows)
        with self.assertRaisesRegex(audit.Reject,'target-to-helper feedback'):
            audit.d_rows(word)

    def test_relocated_optimized_source_receipt_and_output_controls(self):
        with tempfile.TemporaryDirectory(prefix='r439-composition-test-') as directory:
            external = Path(directory)
            target = external/'repo'
            package = target/'research'/HERE.name
            shutil.copytree(HERE,package)
            manifest = json.loads((HERE/'SOURCES.json').read_bytes())
            for entry in manifest['files']:
                if entry['usage'] != 'input':
                    continue
                p = target/entry['path']
                p.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(ROOT/entry['path'],p)
            def run(*args):
                return subprocess.run([sys.executable,'-I','-O','-B',str(package/'verify.py'),*map(str,args)],text=True,capture_output=True,cwd=package)
            self.assertEqual(0,run().returncode)
            p = target/audit.WORD
            old = p.read_bytes();p.write_bytes(old+b'changed')
            self.assertNotEqual(0,run().returncode);p.write_bytes(old)
            sources = package/'SOURCES.json'
            old = sources.read_bytes()
            changed = json.loads(old);changed['base_commit']='0'*40
            sources.write_text(json.dumps(changed));self.assertNotEqual(0,run().returncode)
            changed = json.loads(old)
            next(e for e in changed['files'] if e['usage'] == 'input')['git_blob']='0'*40
            sources.write_text(json.dumps(changed));self.assertNotEqual(0,run().returncode)
            changed = json.loads(old)
            next(e for e in changed['files'] if e['path'] == audit.WORD)['usage']='provenance'
            sources.write_text(json.dumps(changed));self.assertNotEqual(0,run().returncode)
            changed = json.loads(old)
            next(e for e in changed['files'] if e['path'] == audit.WORD)['path']=audit.ORIGINAL
            sources.write_text(json.dumps(changed));self.assertNotEqual(0,run().returncode);sources.write_bytes(old)
            receipt = package/'RESULT.json';old = receipt.read_bytes()
            changed = json.loads(old);changed['variants']['naive_entry']['d_boundary_equal']=True
            receipt.write_text(json.dumps(changed));self.assertNotEqual(0,run().returncode);receipt.write_bytes(old)
            destination = external/'existing.json';destination.write_text('preserve me')
            self.assertNotEqual(0,run('--write-result',destination).returncode)
            self.assertEqual('preserve me',destination.read_text())
            internal = package/'must-not-exist.json'
            self.assertNotEqual(0,run('--write-result',internal).returncode)
            self.assertFalse(internal.exists())


if __name__ == '__main__':
    unittest.main()
