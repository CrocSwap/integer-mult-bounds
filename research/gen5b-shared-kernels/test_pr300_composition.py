import unittest
from check_pr300_composition import run
class CompositionTests(unittest.TestCase):
 def test_exact_disjoint_composition(self):
  r=run();self.assertEqual(r['new_descent_gate_count'],89);self.assertEqual(r['final12_broader_scalar_closure'],84);self.assertEqual(r['kernel72_streams'],165)
 def test_histograms_add(self):
  r=run();H=r['combined_local_histogram_delta_over299'];self.assertEqual(sum(k*v for k,v in H.items()),-78)
 def test_unchanged_following_stages(self):
  r=run();self.assertEqual((r['unchanged_restore_entries'],r['unchanged_sink_entries']),(440,7))
 def test_reject_final12_overlap(self):
  with self.assertRaises(AssertionError):run('frame_overlap')
 def test_reject_kernel_overlap(self):
  with self.assertRaises(AssertionError):run('kernel_overlap')
if __name__=='__main__':unittest.main()
