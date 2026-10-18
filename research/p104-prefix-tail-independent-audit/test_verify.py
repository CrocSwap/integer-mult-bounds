"""Defect-sensitive controls for the independent audit; standard library only."""
from copy import deepcopy
from fractions import Fraction as Q
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import json
import unittest

HERE = Path(__file__).resolve().parent
spec = spec_from_file_location('independent_audit', HERE/'verify.py')
v = module_from_spec(spec)
spec.loader.exec_module(v)


class AuditControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = v.inputs()
        cls.word = cls.raw['LOWRANK-WITNESS.json']
        cls.cert = json.loads((HERE/'WITNESS.json').read_text())
        cls.ports = v.roots(cls.raw['P104-FIXTURE.json']['section4_explicit_P104'])
        cls.collected = v.replay(cls.word,cls.ports,cls.cert)

    def test_equivalent_frame_presentations(self):
        self.assertEqual(v.replay(self.word,self.ports,self.cert,reverse_basis=True),self.collected)
        # Same two-space via a shear, not merely a basis permutation.
        self.assertEqual(v.frame((1,2)),v.frame((3,2)))
        with self.assertRaisesRegex(ValueError,'dependent frame'):
            v.frame((1,2,3))

    def test_wrong_contact_coefficient(self):
        bad = deepcopy(self.cert['upper_witnesses'][1])
        bad['terms'][-1][-1] = '-3'
        with self.assertRaisesRegex(ValueError,'upper rank|explicit residual'):
            v.upper(bad,self.collected[1],self.ports)
        # Reordering and cancelling two presentation-only terms remain legal.
        good = deepcopy(self.cert['upper_witnesses'][1])
        good['terms'].reverse()
        self.assertEqual(v.upper(good,self.collected[1],self.ports),[2754,2,98])

    def test_future_and_self_contact(self):
        bad = deepcopy(self.cert['upper_witnesses'][1])
        bad['cut'] = 2753
        with self.assertRaisesRegex(ValueError,'future contact'):
            v.upper(bad,self.collected[1],self.ports)
        bad = deepcopy(self.cert)
        bad['upper_witnesses'][0]['terms'][0][2] = 'Y7'
        with self.assertRaisesRegex(ValueError,'contact frame'):
            v.replay(self.word,self.ports,bad)

    def test_nonzero_dirty_compensation_fault(self):
        bad = deepcopy(self.word)
        bad['program'][0][3] = '-1/8'
        with self.assertRaisesRegex(ValueError,'complete endpoint|own target dirt'):
            v.replay(bad,self.ports,self.cert)

    def test_nonzero_cleanup_fault(self):
        bad = deepcopy(self.word)
        bad['program'][-1][3] = -1
        with self.assertRaisesRegex(ValueError,'complete endpoint Q7'):
            v.replay(bad,self.ports,self.cert)

    def test_scalar_frame_and_private_lifetime_fault(self):
        bad = deepcopy(self.word)
        bad['program'][0][-1] = [1]
        with self.assertRaisesRegex(ValueError,'scalar frame'):
            v.replay(bad,self.ports,self.cert)
        bad = deepcopy(self.word)
        event = next(x for x in bad['program'] if x[0]=='erase')
        event[-1] = []
        with self.assertRaisesRegex(ValueError,'private discard'):
            v.replay(bad,self.ports,self.cert)

    def test_violated_lower_generator(self):
        pools = deepcopy(self.collected[0][2753])
        # A concrete forbidden generator, with target factor p.r_t != 0.
        p = self.cert['lower_vectors']['p']
        t = next(t for t,r in enumerate(self.ports) if v.dot(p,r))
        pools[t].add(tuple(map(Q,[1,0,0,0,0,0,0,0])))
        with self.assertRaisesRegex(ValueError,'lower functional'):
            v.lower(pools,self.ports,self.cert['lower_vectors'],True)

    def test_omitted_compression_premises(self):
        z = self.cert['lower_vectors']
        def outer(a,b):
            return [[x*y for y in b] for x in a]
        def compressed(n):
            return [[sum(l[i]*n[i][j]*r[j] for i in range(8) for j in range(8))
                     for r in (z['a'],z['b'],z['k'])] for l in (z['p'],z['q'],z['w'])]
        n = outer([0,1,1,0,0,0,0,-1],[-1,0,0,0,0,0,0,0])
        self.assertEqual(v.rank(n),1)
        self.assertEqual([r[:2] for r in compressed(n)[:2]],[[-1,-1],[-1,-1]])
        # All other rank-three fixed entries survive, but dropping q.N.k=0
        # admits the actual rank-two new witness.
        n = outer([0,0,-1,1,0,0,0,1],[0,1,0,0,0,0,0,2])
        n[1][2] -= 1
        self.assertEqual(compressed(n),[[0,-1,0],[-1,0,-2],[1,0,2]])
        self.assertEqual(v.rank(n),2)
        # Missing nuisance availability invalidates projection already in Q^2:
        # span(x+z) has projected rank1 but intersects the x-axis only at0.
        self.assertEqual(v.rank([[1,1],[1,0]]),2)


if __name__=='__main__':
    unittest.main()
