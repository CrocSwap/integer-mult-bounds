"""Independent controls for finite arithmetic and the scope of the screen."""
from fractions import Fraction as Q
from itertools import combinations, product
import sys
import unittest
import screen as s


def modular_rank(rows, p=101):
    rows=[list(x) for x in rows]
    if not rows:
        return 0
    rank=0
    for j in range(len(rows[0])):
        pivot=next((i for i in range(rank,len(rows)) if rows[i][j]%p),None)
        if pivot is None:
            continue
        rows[rank],rows[pivot]=rows[pivot],rows[rank]
        inv=pow(rows[rank][j]%p,-1,p)
        rows[rank]=[a*inv%p for a in rows[rank]]
        for i in range(rank+1,len(rows)):
            c=rows[i][j]%p
            rows[i]=[(a-c*b)%p for a,b in zip(rows[i],rows[rank])]
        rank+=1
    return rank


class ScreenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=s.audit()

    def test_every_support_rank_has_independent_modular_lower_bound(self):
        for c in self.data['candidates']:
            for v in c['factor']['rowspace_catalog']:
                mask=int(v['mask'],16)
                rows=[x for j,x in enumerate(c['labels']) if mask>>j&1]
                self.assertEqual(modular_rank(rows),v['span_dimension'])

    def test_selected_factors_reconstruct_each_entry(self):
        for c in self.data['candidates']:
            factor=c['factor']
            for i,u in enumerate(factor['U_rows']):
                result=0
                for j,v in enumerate(factor['chosen_forms']):
                    if u>>j&1:
                        result ^= int(v['mask'],16)
                self.assertEqual(result,int(c['core_rows'][i],16))

    def test_greedy_matches_exhaustive_toy_bases(self):
        labels=[(1,0),(0,1),(1,1),(1,-1)]
        core=[0b0011,0b0101,0b1001]
        out=s.weighted_basis(labels,core)
        catalog=out['rowspace_catalog']
        optimum=min(sum(v['span_dimension'] for v in forms)
                    for forms in combinations(catalog,3)
                    if len(s.binary_basis(v['selector'] for v in forms)) == 3)
        self.assertEqual(out['minimum_basis_loss'],optimum)

    def test_e8_is_the_earlier_odd_quadratic_family_as_lines(self):
        sys.path.insert(0,str(s.ROOT/'scripts'))
        from experiments.quadratic_affine import family,vector
        f=family(3,False,1)
        def normalize(x):
            lead=next(a for a in x if a)
            return tuple(Q(a,lead) for a in x)
        old=set()
        for i in range(f['n']):
            support,lo,hi=vector(f,i)
            self.assertEqual(lo,0)
            old.add(normalize(tuple((1-2*((hi>>j)&1)) if support>>j&1 else 0 for j in range(8))))
        self.assertEqual(old,{normalize(x) for x in s.e8()[0]})

    def test_hamming_gram_factorization(self):
        labels,gram,_=s.hamming4()
        H=[[0]*10 for _ in range(10)];H[0][0]=2
        for i in range(1,10):
            H[0][i]=H[i][0]=-1
            for j in range(1,10):
                if (i-1)//3 == (j-1)//3:
                    H[i][j]=1+int(i == j)
        self.assertEqual(s.rational_rank(H),10)
        for i,x in enumerate(labels):
            for j,y in enumerate(labels):
                self.assertEqual(sum(x[a]*H[a][b]*y[b] for a in range(10) for b in range(10)),gram[i][j])

    def test_hamming_module_ranks(self):
        self.assertEqual(s.hamming_module_rank(3,2)['binary_rank'],8)
        out=s.hamming_module_rank(7,4)
        self.assertEqual([t['block_rank'] for t in out['summands']],[1,2,8,16])
        self.assertEqual(out['binary_rank'],576)
        self.assertGreater(out['n'],out['binary_rank']*out['d'])

    def test_exact_decisions_and_loss_thresholds(self):
        e,h=self.data['candidates']
        self.assertEqual(e['factor']['minimum_basis_loss'],72)
        self.assertEqual(h['factor']['minimum_basis_loss'],66)
        self.assertEqual(e['necessary_maximum_integer_loss_per_equal_axis_at_target'],43)
        self.assertEqual(h['necessary_maximum_integer_loss_per_equal_axis_at_target'],19)
        self.assertEqual(h['factor']['cumulative_rank_by_cost'],{8:7,9:7,10:8})
        for c in (e,h):
            self.assertLess(c['gross_gain_fraction_after_central_cost'],0)
            self.assertLess(c['optimistic_residual'][1],0)
        self.assertLess(self.data['hamming_next_named_instance']['residual'][1],0)
        self.assertFalse(self.data['construction_candidate_selected'])


if __name__ == '__main__':
    unittest.main()
