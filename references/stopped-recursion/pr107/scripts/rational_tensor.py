"""Exact Kronecker products for finite rational frame certificates."""


def kron(A, B):
    return tuple(tuple(x*y for x in a for y in b) for a in A for b in B)
