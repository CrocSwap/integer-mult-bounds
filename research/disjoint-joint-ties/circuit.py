"""Simultaneous tied root contractions; descendants stay pinned and unchanged.
Adapted from Curtis Dransfield, PR863 head6c0ed3975fda8f0190b34f1b1bbedb33a925d339. Apache-2.0.

Root tensor expansion adapted from Douglas R. Colkitt's Apache-2.0
scripts/experiments/disjoint_tensor.py. Substantial AI assistance: OpenAI Codex.
"""
from pathlib import Path
import sys
from math import comb
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from experiments.disjoint_tensor import DisjointTensor, plan, subsets
from certify import require

class JointTies(DisjointTensor):
    def __init__(self, h, root_split, flips=(), order=(0,1,2,3)):
        require(type(h) is int and h >= 8 and h % 2 == 0, 'even h >= 8 required')
        require(type(root_split) is int and 1 <= root_split <= h//2, "invalid root split")
        self.root_split = root_split
        self.flips = frozenset(flips)
        require(all(type(j) is int for j in order) and tuple(sorted(order)) == (0,1,2,3), 'invalid root channel order')
        self.order = tuple(order)
        channels = feasible_channels(h, root_split)
        require(len(self.flips) == len(flips) and all(f in tied_channels(h, root_split) for f in self.flips), "invalid or duplicate tied channel")
        super().__init__(h)

    def transform(self, points, a, b, values):
        n = len(points)
        if n != self.h:
            return super().transform(points, a, b, values)
        method = self.root_split
        outputs = subsets(points, b)
        left, right = points[:method], points[method:]
        l, r = len(left), len(right)
        terms = {T:[] for T in outputs}
        for j in self.order:
            if not max(0,b-r) <= j <= min(l,b): continue
            for i in range(max(0, a-r), min(l, a)+1):
                if i+j > l or a-i+b-j > r: continue
                A, B = plan(l, i, j)[0], plan(r, a-i, b-j)[0]
                left_first = comb(r, a-i)*A+comb(l, j)*B <= comb(l, i)*B+comb(r, b-j)*A
                if (i, j) in self.flips:
                    left_first = not left_first
                if left_first:
                    middle = {S:self.transform(left, i, j,
                              {R:values[R|S] for R in subsets(left, i)})
                              for S in subsets(right, a-i)}
                    for T in subsets(left, j):
                        row = self.transform(right, a-i, b-j, {S:M[T] for S,M in middle.items()})
                        for U, node in row.items(): terms[T|U].append(node)
                else:
                    middle = {S:self.transform(right, a-i, b-j,
                              {R:values[R|S] for R in subsets(right, a-i)})
                              for S in subsets(left, i)}
                    for T in subsets(right, b-j):
                        row = self.transform(left, i, j, {S:M[T] for S,M in middle.items()})
                        for U, node in row.items(): terms[T|U].append(node)
        return {T:self.total(nodes) for T,nodes in terms.items()}


def feasible_channels(h, left):
    right = h-left
    return [(i,j) for j in range(max(0,3-right), min(left,3)+1)
            for i in range(max(0,3-right), min(left,3)+1)
            if i+j <= left and 6-i-j <= right]


def recurrence_cost(h, left, flips=()):
    right=h-left
    total=0
    for j in range(max(0,3-right), min(left,3)+1):
        channels=[i for i,jj in feasible_channels(h,left) if jj==j]
        for i in channels:
            A=plan(left,i,j)[0]; B=plan(right,3-i,3-j)[0]
            lr=comb(right,3-i)*A+comb(left,j)*B
            rl=comb(left,i)*B+comb(right,3-j)*A
            total += max(lr,rl) if (i,j) in flips else min(lr,rl)
        if channels:
            total += comb(left,j)*comb(right,3-j)*(len(channels)-1)
    return total


def tied_channels(h, left):
    right=h-left
    result=[]
    for i,j in feasible_channels(h,left):
        A=plan(left,i,j)[0]; B=plan(right,3-i,3-j)[0]
        if comb(right,3-i)*A+comb(left,j)*B == comb(left,i)*B+comb(right,3-j)*A:
            result.append((i,j))
    return result
