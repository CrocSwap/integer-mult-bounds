import unittest
import check_coretime as c

class TestCoretime(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.result=c.run()
    def test_selected_and_lost(self):
        self.assertEqual((self.result['selected'],self.result['undone_old_restorations']),(32,26))
    def test_exact_integer_identity(self):
        self.assertTrue(self.result['exact_integer_root_schedule_identity'])
        self.assertTrue(self.result['missing_restoration_control_rejected'])
    def test_net_histogram(self):
        self.assertEqual(self.result['local_histogram_delta'],{1:-46,2:20})
        self.assertEqual(self.result['residual_rank_count_delta'],{2:32,3:-58,4:26})
    def test_conflicts_explicit(self):
        self.assertEqual({z['helper']for z in self.result['rejected']},{16485,16709})
    def test_exact_source_spans(self):
        self.assertTrue(all(z['source_union_size']==180 for z in self.result['candidates']))
    def test_wrong_promoted_frame_rejected(self):
        with self.assertRaisesRegex(AssertionError,'Promoted delivery outside target cap'):
            c.run('wrong_promoted_frame')
    def test_missing_old_undo_rejected(self):
        with self.assertRaisesRegex(AssertionError,'Missing old restoration undo'):
            c.run('omit_old_restoration_undo')
    def test_shared_blocker_rejected(self):
        with self.assertRaisesRegex(AssertionError,'Shared blocker'):
            c.run('shared_blocker')
    def test_incompatible_prefix_rejected(self):
        with self.assertRaisesRegex(AssertionError,'Prefix closing frame outside common frame'):
            c.run('incompatible_prefix')
    def test_kernel_donor_overlap_disclosed(self):
        self.assertEqual({r['donor']for r in self.result['kernel_donor_contracts']},
                         {12649,12678,8811,11313,11329})

if __name__=='__main__':unittest.main()
