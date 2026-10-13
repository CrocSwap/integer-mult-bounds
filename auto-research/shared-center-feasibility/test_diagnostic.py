"""Independent finite controls for the shared-center diagnostic."""
from fractions import Fraction as Q
from itertools import combinations
import json
import unittest
import diagnostic as d


def rank_mod(rows,p=101):
    pivots={}
    for row in rows:
        row=[int(x)%p for x in row]
        for j,b in sorted(pivots.items()):
            c=row[j]
            row=[(a-c*v)%p for a,v in zip(row,b)]
        j=next((i for i,x in enumerate(row) if x),None)
        if j is not None:
            inv=pow(row[j],-1,p);pivots[j]=[a*inv%p for a in row]
    return len(pivots)


class DiagnosticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cert=json.loads((d.HERE/'certificate.json').read_text())
        cls.labels,cls.gram,cls.core=d.e8()

    def test_every_extended_support_rank_modular_control(self):
        for case in self.cert['e8']['extension_orbits']:
            for row in case['expanded_factor']['rowspace_catalog']:
                mask=int(row['mask'],16)
                self.assertEqual(rank_mod([x for j,x in enumerate(self.labels) if mask>>j&1]),row['span_dimension'])

    def test_orbits_are_disjoint_complete_and_preserve_core(self):
        catalog,closures=d.low_rank_catalog(self.labels)
        orbits=self.cert['e8']['extension_orbits']
        union=[int(x,16) for c in orbits for x in c['orbit_members']]
        self.assertEqual(sorted(union),catalog)
        self.assertEqual(len(set(union)),8380)
        self.assertEqual(closures,{2:3780,3:1120})
        for p in self.cert['e8']['reflection_generators']:
            for i,row in enumerate(self.core):
                self.assertEqual(d.permute(row,p),self.core[p[i]])

    def test_joint_core_factors_and_minima_replay(self):
        for c in self.cert['e8']['extension_orbits']:
            result=d.variable_core(self.gram,c['expanded_factor'])
            self.assertEqual(d.encode(result),c['jointly_variable_core'])
            self.assertEqual(result['exact_minimum_loss'],72)
            for sub in result['checked_subspaces']:
                if not sub['viable']:continue
                forms=[int(x['mask'],16) for x in sub['chosen_forms']]
                space=d.span(forms)
                for i,raw in enumerate(sub['admissible_core_rows']):
                    row=int(raw,16)
                    self.assertIn(row,space)
                    self.assertTrue(row>>i&1)
                    for j in range(120):
                        if i!=j and row>>j&1:self.assertEqual(self.gram[i][j],0)

    def test_quotient_search_matches_two_label_exhaustive_case(self):
        labels=[(1,0),(0,1)]
        factor=d.weighted_basis(labels,[1,2])
        result=d.variable_core([[1,0],[0,1]],factor)
        self.assertEqual(result['quotient_dimension'],2)
        self.assertEqual(len(result['checked_subspaces']),5)
        # All nonzero forms are 01,10,11. Try every independent center subset.
        best=99
        for size in range(1,3):
            for forms in combinations([1,2,3],size):
                space=d.span(forms)
                if all(any(v>>i&1 for v in space) for i in range(2)):
                    best=min(best,sum(v.bit_count() for v in forms))
        self.assertEqual(result['exact_minimum_loss'],best)

    def test_private_inputs_are_orthogonal_and_incidence_inequality(self):
        for case in self.cert['e8']['extension_orbits']:
            for sub in case['jointly_variable_core']['checked_subspaces']:
                if not sub['viable']:continue
                forms=[int(x['mask'],16) for x in sub['chosen_forms']]
                counts=[sum(v>>i&1 for v in forms) for i in range(120)]
                self.assertTrue(all(counts))
                private_total=0
                for row in sub['chosen_forms']:
                    v=int(row['mask'],16)
                    private=[i for i in range(120) if counts[i]==1 and v>>i&1]
                    private_total+=len(private)
                    for i,j in combinations(private,2):self.assertEqual(self.gram[i][j],0)
                    self.assertLessEqual(len(private),row['span_dimension'])
                incidences=sum(counts)
                self.assertGreaterEqual(incidences,240-private_total)
                self.assertGreaterEqual(incidences+sub['minimum_cost'],240)
        self.assertEqual(Q(self.cert['e8']['jointly_variable_core_low_rank_screen']['necessary_loss_lower']),96)

    def test_positive_control_is_real_but_not_a_network_gain(self):
        c=d.positive_control()
        self.assertEqual((c['old_centers'],c['new_centers']),(3,4))
        self.assertEqual((c['old_loss'],c['new_loss']),(6,4))
        self.assertLess(c['new_gross_two_axis_gain'],0)
        new=c['new_factor']
        forms=[int(x['mask'],16) for x in new['chosen_forms']]
        for i,raw in enumerate(c['core_rows']):
            decoded=0
            for j,v in enumerate(forms):
                if new['U_rows'][i]>>j&1:decoded ^= v
            self.assertEqual(decoded,int(raw,16))


if __name__=='__main__':
    unittest.main()
