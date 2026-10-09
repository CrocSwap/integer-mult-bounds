from copy import deepcopy
from fractions import Fraction as Q
import json
from pathlib import Path
import unittest
from one_regular_diagnostic import (FIXED,REMAINING,verify_partial,extension_test,
                                    verify_extension)
from mixed_rank_search import coordinate_control


class OneRegularDiagnosticTests(unittest.TestCase):
    def test_all_saved_candidates_and_extension_certificates(self):
        result=json.loads(Path(__file__).with_name('one-regular-diagnostic.json').read_text())
        self.assertEqual(len(result['candidates']),12)
        for candidate in result['candidates']:
            factors={item['vertex']:([[Q(x) for x in row] for row in item['A']],
                                     [[Q(x) for x in row] for row in item['B']])
                     for item in candidate['partial_factors']}
            self.assertTrue(verify_partial(factors))
            self.assertEqual(len(candidate['extension_tests']),24)
            for test in candidate['extension_tests']:
                self.assertTrue(verify_extension(factors,test))
                self.assertEqual(test['A_kernel_basis'],[])
                self.assertEqual(test['B_kernel_basis'],[])
                self.assertFalse(test['individually_attachable'])

    def test_extension_checker_accepts_known_extensions(self):
        # Auxiliary control with all blocks unrestricted, NOT a candidate
        # for the one-regular-block experiment. Remaining labels do not
        # touch block 0, so their support domains agree in this test.
        full=coordinate_control();partial={i:full[i] for i in FIXED}
        for target in REMAINING:
            test=extension_test(partial,target)
            self.assertTrue(verify_extension(partial,test))
            self.assertTrue(test['individually_attachable'])

    def test_forged_extension_rank_is_rejected(self):
        full=coordinate_control();partial={i:full[i] for i in FIXED}
        test=deepcopy(extension_test(partial,REMAINING[0]))
        test['normalization_pairing_rank']=0;test['individually_attachable']=False
        with self.assertRaises(AssertionError):verify_extension(partial,test)


if __name__=='__main__':unittest.main()
