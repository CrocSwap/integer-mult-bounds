from copy import deepcopy
import json
import unittest
from mixed_rank_search import (coordinate_control,verify_partial,equivalent_minimal_patterns,
                               normalization_positions)
from mixed_rank_obstruction import audit,check_conflict,local_control


class MixedRankTests(unittest.TestCase):
    def test_positive_partial_control_and_corruption(self):
        factors=coordinate_control()
        self.assertEqual(verify_partial(factors,range(7))['Y_edges'],420)
        bad=deepcopy(factors);next(iter(bad.values()))[0][0][0]+=1
        with self.assertRaises(AssertionError):verify_partial(bad,range(7))

    def test_seven_equivalent_patterns_and_basis_gauges(self):
        patterns=equivalent_minimal_patterns();self.assertEqual(len(patterns),7)
        for item in patterns:self.assertEqual(len(normalization_positions(item['exception_blocks'])),24)

    def test_exact_exclusions_and_wrong_shared_block(self):
        result=audit();self.assertEqual(result['minimum_exceptions_remaining'],4)
        self.assertEqual(len(result['new_complementary_block_exclusions']),7)
        for witness in result['new_complementary_block_exclusions']:self.assertTrue(check_conflict(witness))
        loaded=json.loads(json.dumps(result))
        for witness in loaded['new_complementary_block_exclusions']:self.assertTrue(check_conflict(witness))
        bad=deepcopy(result['new_complementary_block_exclusions'][0])
        bad['left']['exception_block']=(bad['left']['exception_block']+1)%7
        with self.assertRaises(AssertionError):check_conflict(bad)

    def test_local_complementary_block_control(self):
        result=local_control()
        self.assertEqual(result['complement_ranks'],[4,4])
        self.assertEqual(result['exceptional_distinguished_ranks'],[2,2])


if __name__=='__main__':unittest.main()
