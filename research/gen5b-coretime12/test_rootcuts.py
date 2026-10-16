import unittest
import check_rootcuts as c
class TestCutScreen(unittest.TestCase):
    def test_rank_empty(self): self.assertEqual(c.rank([]),0)
    def test_rank_dependent(self): self.assertEqual(c.rank([[1,2],[2,4]],2),1)
    def test_rank_independent(self): self.assertEqual(c.rank([[1,2],[2,5]],2),2)
    def test_all_actual_roles(self): self.assertEqual(c.run()['count'],34)
if __name__=='__main__': unittest.main()
