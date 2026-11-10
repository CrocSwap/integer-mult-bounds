"""Independent minor enumeration and complete-kernel rejection tests."""
import copy
from fractions import Fraction as Q
import itertools
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import certify_rational_rank as tool


def problem(a):return {'schema':'rational-rank-problem/v1','matrix':a}


def determinant(a):
    n=len(a);out=Q(0)
    for p in itertools.permutations(range(n)):
        term=Q((-1)**sum(p[i]>p[j] for i in range(n) for j in range(i+1,n)))
        for i,j in enumerate(p):term*=Q(a[i][j])
        out+=term
    return out


def oracle(a):
    m,n=len(a),len(a[0])
    for r in reversed(range(1,min(m,n)+1)):
        if any(determinant([[a[i][j] for j in js] for i in inds])
               for inds in itertools.combinations(range(m),r) for js in itertools.combinations(range(n),r)):return r
    return 0


def rational_pivots(a):
    """Independent Fraction representation of the original pivot policy."""
    rows=[row[:] for row in a];ids=list(range(len(a)));chosen=[];columns=[]
    for column in range(len(a[0])):
        rank=len(columns)
        pivot=next((i for i in range(rank,len(rows)) if rows[i][column]),None)
        if pivot is None:continue
        rows[rank],rows[pivot]=rows[pivot],rows[rank]
        ids[rank],ids[pivot]=ids[pivot],ids[rank]
        chosen.append(ids[rank]);columns.append(column)
        for i in range(rank+1,len(rows)):
            multiple=rows[i][column]/rows[rank][column]
            rows[i]=[x-multiple*y for x,y in zip(rows[i],rows[rank])]
    return chosen,columns


class RankTests(unittest.TestCase):
    def test_primitive_pivots_preserve_complete_certificates(self):
        rng=random.Random(5789)
        cases=[[[0]],[[0,0,0],[0,0,0]],[[0,0],[0,-3],[0,6]],
               [[0,0,0,0],[0,0,-2,1],[0,3,0,2],[0,6,-4,6]],
               [['-999999999/1000000000','1/999999937'],
                ['999999999/1000000000','-1/999999937']]]
        for m,n in itertools.product(range(1,7),repeat=2):
            for _ in range(4):
                cases.append([[str(Q(rng.randrange(-9,10),rng.randrange(1,30)))
                               for _ in range(n)] for _ in range(m)])
        for m,n,rank in ((64,64,0),(64,64,1),(48,64,8),(64,48,8),(16,24,16)):
            left=[[rng.randrange(-4,5) for _ in range(rank)] for _ in range(m)]
            right=[[rng.randrange(-4,5) for _ in range(n)] for _ in range(rank)]
            cases.append([[str(Q(sum(left[i][k]*right[k][j] for k in range(rank)),
                                 2**(i%5)*3**(j%4))) for j in range(n)] for i in range(m)])
        for raw in cases:
            value=problem(raw);a=tool.validate(value);unchanged=[row[:] for row in a]
            self.assertEqual(tool._pivot_minor(a),rational_pivots(a))
            self.assertEqual(a,unchanged)
            actual=tool.certify(value)
            with patch.object(tool,'_pivot_minor',rational_pivots):
                expected=tool.certify(value)
            self.assertEqual(actual,expected)

    def test_integer_products_keep_rational_and_empty_boundaries(self):
        a=[[Q(1,2),Q(-2,3)],[Q(5,7),Q(11,13)]]
        b=[[Q(3,17)],[Q(-19,23)]]
        c=[[sum((x*y[0] for x,y in zip(row,b)),Q(0))] for row in a]
        self.assertTrue(tool._product_equal(a,b,c,2,2,1))
        c[1][0]+=Q(1,1009)
        self.assertFalse(tool._product_equal(a,b,c,2,2,1))
        self.assertTrue(tool._product_equal([[],[]],[],[[Q(0)],[Q(0)]],2,0,1))
        self.assertFalse(tool._product_equal([[],[]],[],[[Q(0)],[Q(1)]],2,0,1))
        self.assertTrue(tool._product_equal([],[[Q(1)]],[],0,1,1))
        self.assertTrue(tool._product_equal(a,[[],[]],[[],[]],2,2,0))

    def test_all_binary_three_by_three_matrices(self):
        for values in itertools.product(range(2),repeat=9):
            a=[list(values[i:i+3]) for i in (0,3,6)];r=tool.certify(problem(a))
            self.assertEqual(r['rank'],oracle(a));self.assertTrue(tool.verify(problem(a),r))

    def test_rectangular_rational_oracles(self):
        rng=random.Random(607)
        for _ in range(60):
            a=[[str(Q(rng.randrange(-3,4),rng.randrange(1,5))) for _ in range(4)] for _ in range(3)]
            r=tool.certify(problem(a));self.assertEqual(r['rank'],oracle(a))
        r=tool.certify(problem([[1,0,1],[0,1,1],[1,1,2]]))
        self.assertEqual(r['right_kernel'],[['-1','-1','1']]);self.assertEqual(r['left_kernel'],[['-1','-1','1']])

    def test_each_certificate_component_is_checked(self):
        value=problem([[1,0,1],[0,1,1],[1,1,2]]);good=tool.certify(value)
        for key in ('minor_inverse','coefficients','right_kernel','left_kernel'):
            bad=copy.deepcopy(good);bad[key][0][0]=str(Q(bad[key][0][0])+1)
            with self.assertRaises(ValueError):tool.verify(value,bad)
        bad=copy.deepcopy(good);bad['right_kernel'][0]=['0','0','0']
        with self.assertRaises(ValueError):tool.verify(value,bad)
        bad=copy.deepcopy(good);bad['rows']=[0,0]
        with self.assertRaises(ValueError):tool.verify(value,bad)

    def test_zero_full_rank_and_limits(self):
        self.assertEqual(tool.certify(problem([[0,0,0],[0,0,0]]))['rank'],0)
        a=[[int(i==j) for j in range(64)] for i in range(64)]
        r=tool.certify(problem(a));self.assertEqual(r['rank'],64);self.assertEqual(r['left_kernel'],[])
        for a in ([],[[]],[[0]*65],[[True]],[[0.1]],[['1/1000000001']]):
            with self.assertRaises(ValueError):tool.certify(problem(a))

        with self.assertRaisesRegex(ValueError,'6000-bit'):
            tool.encode_rational(Q(1<<6001))

    def test_nonleading_pivot_minor(self):
        a=[[0,0,0,0],[0,0,2,1],[0,3,0,2],[0,6,4,6]]
        r=tool.certify(problem(a));self.assertEqual(r['rank'],2)
        self.assertEqual(r['rows'],[2,1]);self.assertEqual(r['columns'],[1,2])
        self.assertTrue(tool.verify(problem(a),r))

    def test_portable_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            p,c=Path(tmp)/'problem.json',Path(tmp)/'certificate.json';p.write_text(json.dumps(problem([[1,2],[2,4]])))
            cmd=[sys.executable,'-O','-B',str(ROOT/'scripts/certify_rational_rank.py'),str(p)]
            out=subprocess.run(cmd,cwd=tmp,capture_output=True,text=True);self.assertEqual(out.returncode,0,out.stderr)
            c.write_text(out.stdout);self.assertEqual(subprocess.run(cmd+['--check',str(c)],capture_output=True).returncode,0)
            p.write_text(p.read_text()+'\n');self.assertEqual(subprocess.run(cmd+['--check',str(c)],capture_output=True).returncode,2)


if __name__=='__main__':unittest.main()
