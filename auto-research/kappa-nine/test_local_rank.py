from copy import deepcopy
import unittest
from local_rank_test import (Y,rank_profile,verify_profile,line_obstruction,
                             verify_line_obstruction,local_block_control)


class LocalRankTests(unittest.TestCase):
    def test_both_abstract_profiles_and_destroyed_full_rank(self):
        for mode in (2,3):self.assertTrue(verify_profile(mode,rank_profile(mode)))
        profile=rank_profile(2)
        profile[Y[0]]=[int(bool(x)) for x in profile[Y[0]]]
        with self.assertRaises(AssertionError):verify_profile(2,profile)

    def test_line_obstruction_and_corrupted_color(self):
        data=line_obstruction();self.assertTrue(verify_line_obstruction(data))
        bad=deepcopy(data);block=bad['blocks'][0];v=block['vertices'][0]
        block['colors'][str(v)]=1-block['colors'][str(v)]
        with self.assertRaises(AssertionError):verify_line_obstruction(bad)

    def test_isolated_blocks_really_are_feasible(self):
        for block in line_obstruction()['blocks']:self.assertTrue(local_block_control(block))


if __name__=='__main__':unittest.main()
