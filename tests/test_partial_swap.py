"""Small exact algebra controls for the new frame compiler."""
from fractions import Fraction as Q
import unittest


def mul(a, b):
    return [[sum((x*y for x,y in zip(row,col)),Q(0)) for col in zip(*b)] for row in a]


def eye(n):
    return [[Q(i==j) for j in range(n)] for i in range(n)]


def sub(a,b):
    return [[x-y for x,y in zip(ar,br)] for ar,br in zip(a,b)]


def block(a,b,c,d):
    return [x+y for x,y in zip(a,b)]+[x+y for x,y in zip(c,d)]


def transpose(a):
    return list(map(list,zip(*a)))


def swap(p):
    complement=sub(eye(len(p)),p)
    return block(complement,p,p,complement)


class PartialSwapAlgebraTests(unittest.TestCase):
    def test_conjugation_with_nonsymmetric_projector(self):
        # Nontrivial lower-lower factorization P = L Pi R, with nonzero K.
        # Verify D_P G = G S, avoiding a numerical inverse altogether.
        L=[[Q(2),Q(0)],[Q(1),Q(1)]]
        R=[[Q(1),Q(0)],[Q(0),Q(1)]]
        Pi=[[Q(0),Q(1)],[Q(0),Q(0)]]
        P=mul(mul(L,Pi),R)
        self.assertEqual(mul(P,P),P)
        C=mul(R,L)
        Qx=mul(Pi,transpose(Pi)); Qy=mul(transpose(Pi),Pi)
        K=sub(mul(Qy,C),mul(C,Qx))
        zero=[[Q(0)]*2 for _ in range(2)]
        G=mul(block(L,zero,zero,eye(2)),block(eye(2),zero,K,eye(2)))
        S=block(sub(eye(2),Qx),Pi,transpose(Pi),sub(eye(2),Qy))
        self.assertEqual(mul(swap(P),G),mul(G,S))
        self.assertEqual(mul(swap(P),swap(P)),eye(4))
        self.assertEqual(mul(swap(sub(eye(2),P)),swap(P)),swap(eye(2)))

    def test_nested_frame_transition(self):
        U=[[Q(1),Q(0)],[Q(0),Q(0)]]
        V=eye(2)
        self.assertEqual(mul(swap(V),swap(U)),swap(sub(V,U)))

if __name__=='__main__':
    unittest.main()
