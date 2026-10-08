"""Independent scalar and rank controls for the new label-family screens."""
from itertools import combinations
from math import comb
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts/experiments'))
from label_family_motifs import coordinate_block_case, parity_cube_case, parity_cube_audit


def modular_rank(matrix, p):
    a = [row[:] for row in matrix]
    row = 0
    for col in range(len(a[0])):
        pivot = next((i for i in range(row, len(a)) if a[i][col] % p), None)
        if pivot is None:
            continue
        a[row], a[pivot] = a[pivot], a[row]
        inverse = pow(a[row][col] % p, p-2, p)
        a[row] = [x*inverse % p for x in a[row]]
        for i in range(row+1, len(a)):
            multiplier = a[i][col] % p
            a[i] = [(x-multiplier*y) % p for x,y in zip(a[i],a[row])]
        row += 1
        if row == len(a):
            break
    return row


class LabelFamilyMotifs(unittest.TestCase):
    def test_parity_identity_and_fourier_rank_against_explicit_matrices(self):
        for h in (6,7):
            p = 3
            vertices = [x for x in range(1 << h) if x.bit_count() % 2 == 0]
            matrix = []
            for x in vertices:
                row = []
                for y in vertices:
                    distance = (x^y).bit_count()
                    scalar = (1-(distance//2)**(p-1)) % p
                    expected = int(x == y or distance == 2*p)
                    self.assertEqual(scalar, expected)
                    gram = sum((1-2*((x>>i)&1))*(1-2*((y>>i)&1)) for i in range(h))/4+p-h/4
                    self.assertEqual(gram, p-distance/2)
                    if x != y and scalar:
                        self.assertEqual(gram, 0)
                    row.append(scalar)
                matrix.append(row)
            check = parity_cube_case(p,h)
            self.assertGreater(check['form_last_diagonal'], 0)
            self.assertEqual(modular_rank(matrix,p), check['exact_scalar_center_rank'])

    def test_higher_rank_coordinate_blocks_scalar_identity(self):
        for p in (2,3,5):
            h = p+2
            subsets = [set(x) for x in combinations(range(h),p)]
            for s in subsets:
                for t in subsets:
                    intersection = len(s&t)
                    value = sum((-1)**d*comb(intersection,d) for d in range(min(intersection,p-1)+1)) % p
                    self.assertEqual(value, int(s==t or not intersection))
            case = coordinate_block_case(p,h)
            self.assertLess(case['deficit_numerator'], 0)
            self.assertLessEqual(case['terminal_gain'],case['center_loss_per_invocation'])

    def test_global_optimistic_parity_cube_bound(self):
        result = parity_cube_audit()
        best = result['best']
        self.assertEqual((best['p'],best['h']), (11,43))
        self.assertEqual(best['vertices'],4398046511104)
        self.assertEqual(best['exact_scalar_center_rank'],2665685155)
        self.assertLess(result['tail_kappa_upper'],best['kappa_lower_for_relaxation'])
        self.assertLess(result['factor_over_current_upper'],26)


if __name__ == '__main__':
    unittest.main()
