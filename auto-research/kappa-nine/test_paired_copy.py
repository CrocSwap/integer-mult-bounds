from copy import deepcopy
import json
import unittest
from paired_copy_obstruction import audit,verify_witness


class PairedCopyTests(unittest.TestCase):
    def test_all_json_certificates_and_complete_cover(self):
        result=json.loads(json.dumps(audit()))
        self.assertEqual(len(result['paired_copy_certificates']),56)
        patterns={tuple(x) for x in result['previous_regular_star_exclusions']}
        for witness in result['paired_copy_certificates']:
            self.assertTrue(verify_witness(witness))
            self.assertNotIn(tuple(witness['exception_blocks']),patterns)
            patterns.add(tuple(witness['exception_blocks']))
        for pattern in result['surviving_exception_sets']:
            self.assertNotIn(tuple(pattern),patterns);patterns.add(tuple(pattern))
        self.assertEqual(len(patterns),128)
        self.assertEqual(sorted(map(len,result['surviving_exception_sets'])),[6]*7+[7])

    def test_wrong_outside_copy_breaks_the_edge(self):
        witness=deepcopy(audit()['paired_copy_certificates'][0])
        step=witness['forced_zeros'][0]
        step['source']=next(w['vertex'] for w in witness['full_rank_sources'] if w['vertex']!=step['source'])
        with self.assertRaises(AssertionError):verify_witness(witness)

    def test_missing_deletion_is_not_a_certificate(self):
        witness=deepcopy(audit()['paired_copy_certificates'][0])
        witness['forced_zeros'].pop()
        with self.assertRaises(AssertionError):verify_witness(witness)


if __name__=='__main__':unittest.main()
