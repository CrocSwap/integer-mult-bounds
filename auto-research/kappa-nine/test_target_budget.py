"""Independent controls for exact target screens, not construction tests."""
import copy
from fractions import Fraction as Q
import json
import unittest
from target_budget import HERE, audit, moment, profile_parts, root_bounds


class TargetControls(unittest.TestCase):
    def test_exact_roots_and_nonperfect_bounds(self):
        for value,degree in ((Q(1),511),(Q(8),3),(Q(1,8),3),(Q(575,529),511),(Q(7,3),5)):
            lo,hi=root_bounds(value,degree,10**8)
            self.assertLessEqual(lo**degree,value)
            self.assertGreaterEqual(hi**degree,value)
            self.assertEqual(hi-lo,Q(1,10**8))

    def test_same_rank_mass_has_different_moment(self):
        small=moment({1:8},16,1)
        large=moment({8:1},16,1)
        self.assertGreater(small[0],large[1])

    def test_invalid_or_noncontracting_children_rejected(self):
        for rows in ({0:1},{16:1},{2:-1}):
            with self.assertRaises(ValueError):moment(rows,16,1)

    def test_changed_profile_rejected(self):
        d=json.loads((HERE/'baseline/certificate.json').read_text())
        profiles=[json.loads((HERE/f'baseline/profiles-{h}.json').read_text()) for h in (23,25)]
        profiles=copy.deepcopy(profiles);profiles[0]['blocks'][1]+=1
        with self.assertRaises(ValueError):profile_parts(d,profiles)

    def test_target_and_all_affine_coefficients_excluded(self):
        data=audit()
        self.assertGreater(data['actual_target_moment_interval'][0],1)
        screen=data['arbitrary_role_compression_screen']
        self.assertGreater(screen['constant_moment_at_R_zero_interval'][0],1)
        self.assertGreater(screen['even_if_fixed_compiler_return_mass_erased_interval'][0],1)
        for entry in screen['role_coefficients'].values():
            self.assertGreater(entry['per_invocation_role_moment_interval'][0],1)
        self.assertEqual(data['fixed_mass_maxchild_screen']['necessary_maxchild_at_same_normalized_rank_mass'],568)
        ideal=data['ideal_whole_macro_screen']
        self.assertGreater(ideal['constant_moment_at_R_zero_interval'][0],1)
        for lo,hi in ideal['role_moment_coefficients'].values():
            self.assertGreater(lo,1)
        # Relaxation really leaves a possible escape when central loss changes.
        self.assertLess(ideal['no_central_overhead_constant_interval'][1],1)
        self.assertGreater(data['zero_center_loss_source_floor_screen']['moment_interval'][0],1)


if __name__=='__main__':unittest.main()
