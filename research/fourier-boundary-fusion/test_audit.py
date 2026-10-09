"""Exact checks of the star and of rectangular cut telescoping."""
from fractions import Fraction as Q
import unittest
import audit as a


def eye(n):return [[a.ONE if i==j else a.ZERO for j in range(n)] for i in range(n)]


def product(A,B):
    out=[]
    for row in A:
        new=[]
        for col in zip(*B):
            value=a.ZERO
            for x,y in zip(row,col):value=a.add(value,a.mul(x,y))
            new.append(value)
        out.append(new)
    return out


def matrix_add(A,B):return [[a.add(x,y) for x,y in zip(r,s)] for r,s in zip(A,B)]


def blockdiag(A,B):
    return [r+[a.ZERO]*len(B[0]) for r in A]+[[a.ZERO]*len(A[0])+r for r in B]


class BoundaryTests(unittest.TestCase):
    def test_star_on_complete_complex_basis(self):
        for kind,coeffs in [('D',[Q(-1,2),Q(1,32)]),('B',[Q(1,4),Q(-1,64)])]:
            for j in range(48):
                streams=[[(Q(0),Q(int(r*16+i==j))) for i in range(16)] for r in range(3)]
                self.assertEqual(a.star(streams,coeffs,kind),a.star(streams,coeffs,kind,encoded=True))

    def test_unaligned_target_counterexample(self):
        streams=[[a.ONE]+[a.ZERO]*15,[a.ZERO]*16,[a.ZERO]*16]
        self.assertNotEqual(a.star(streams,[Q(1,4),Q(-1,64)]),
                            a.star(streams,[Q(1,4),Q(-1,64)],encoded=True,align_targets=False))

    def test_scatter_dependency_counts(self):
        self.assertEqual(len(a.scatter_column('D')),2628)
        self.assertEqual(len(a.scatter_column('B')),2744)
        self.assertEqual(2*27*(2628+1)+1,141967)
        self.assertEqual(2*27*(2744+1)+1,148231)
        # Independent zero-coefficient counting, excluding the named center.
        from math import comb
        self.assertEqual(comb(28,3)-18*comb(9,2),2628)
        self.assertEqual(comb(28,3)-19*comb(8,2),2744)

    def test_full_and_child_cut_ranks(self):
        self.assertEqual(len(a.cut_checks()),6)

    def test_rectangular_copy_gate_delete_telescoping(self):
        I=eye(4)
        copy=I+I
        c0=a.operator_matrix(lambda v:a.c_direction(v,1),4)
        c1=a.operator_matrix(lambda v:a.c_direction(v,2),4)
        child0=blockdiag(c0,I)
        gate=[r+[a.ZERO]*4 for r in I]+[r+r for r in I]
        child1=blockdiag(I,c1)
        delete=[[a.ZERO]*4+r for r in I]
        ops=[copy,child0,gate,child1,delete]
        dims=[4,8,8,8,8,4]
        total=I
        for op in ops:total=product(op,total)
        for bit in (0,1):
            cuts=[[(i%4>>bit)&1 for i in range(dim)] for dim in dims]
            lhs=a.defect(total,cuts[-1],cuts[0])
            rhs=[[a.ZERO]*4 for _ in range(4)]
            ranks=[]
            for k,op in enumerate(ops):
                D=a.defect(op,cuts[k+1],cuts[k]);ranks.append(a.complex_rank(D))
                pre=eye(4)
                for A in ops[:k]:pre=product(A,pre)
                post=eye(dims[k+1])
                for A in ops[k+1:]:post=product(A,post)
                rhs=matrix_add(rhs,product(post,product(D,pre)))
            self.assertEqual(lhs,rhs)
            self.assertEqual(ranks,[0,4 if bit==0 else 0,0,4 if bit==1 else 0,0])
            self.assertEqual(a.complex_rank(lhs),4)

    def test_noncoordinate_movement_is_not_free_in_cut_model(self):
        # Address (source bit 1, target bit 0): controlled XOR.
        P=[[a.ONE if i==(j^(((j>>1)&1))) else a.ZERO for j in range(4)] for i in range(4)]
        p=[i&1 for i in range(4)]
        self.assertEqual(a.complex_rank(a.defect(P,p,p)),2)
        # Mixing role classes that encode an ACTIVE selected bit also fails.
        gate=[[a.ONE,a.ZERO],[a.ONE,a.ONE]]
        self.assertEqual(a.complex_rank(a.defect(gate,[0,1],[0,1])),1)

    def test_diagonal_phases_and_spectator_role_permutations_are_free(self):
        diagonal=[[((Q(0),Q(1)) if i==j and i%2 else a.ONE if i==j else a.ZERO) for j in range(4)] for i in range(4)]
        for bit in (0,1):
            p=[i>>bit&1 for i in range(4)]
            self.assertEqual(a.complex_rank(a.defect(diagonal,p,p)),0)
        swap=[[a.ONE if i==(j+4)%8 else a.ZERO for j in range(8)] for i in range(8)]
        p=[i%4&1 for i in range(8)]
        self.assertEqual(a.complex_rank(a.defect(swap,p,p)),0)


if __name__=='__main__':unittest.main()
