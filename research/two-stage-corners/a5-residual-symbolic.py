"""Exact weight-independent zero-minor certificates for the A5 residual.

No numerical ranks are used: incidence-column ranks follow the forest lemma.
All files are confined to this existing SSD research directory.
"""
from collections import deque
from pathlib import Path
from fractions import Fraction
from functools import reduce
from math import gcd
import json

A, B = 28, 27
VERTICES = A+B
CONSTANT = 1 << VERTICES
ALL = (CONSTANT << 1)-1
LEFT = (1 << A)-1
RIGHT = CONSTANT-1-LEFT
ROW = list(range(A))+[0]+list(range(A-3))
COL = list(range(3,A))+[0]+list(range(A))


class Forest:
    def __init__(self, edges):
        parent = list(range(VERTICES))
        def root(x):
            while parent[x] != x:
                x = parent[x]
            return x
        for u,v in edges:
            u,v = root(u),root(v)
            assert u != v, 'The incidence rank lemma requires a forest'
            parent[u] = v
        groups = {}
        for v in range(VERTICES):
            groups[root(v)] = groups.get(root(v),0) | (1 << v)
        self.groups = tuple(groups.values())
        self.cache = {}

    def rank(self,mask):
        if mask in self.cache:
            return self.cache[mask]
        nodes = mask & (CONSTANT-1)
        rank = nodes.bit_count()-sum(nodes & g == g for g in self.groups)
        if mask & CONSTANT:
            missing = (CONSTANT-1)^nodes
            rank += any(missing & g & LEFT and missing & g & RIGHT for g in self.groups)
        self.cache[mask] = rank
        return rank


def elements(mask):
    while mask:
        bit = mask & -mask
        yield bit
        mask ^= bit


def common_basis_or_partition(f,g):
    # Linear matroid intersection with an exact combinatorial rank oracle.
    independent = 0
    for bit in elements(ALL):
        candidate = independent | bit
        if f.rank(candidate) == g.rank(candidate) == candidate.bit_count():
            independent = candidate
    while True:
        size = independent.bit_count()
        outside = ALL ^ independent
        starts = [e for e in elements(outside) if f.rank(independent|e) == size+1]
        targets = {e for e in elements(outside) if g.rank(independent|e) == size+1}
        parents = {e:None for e in starts}
        queue = deque(starts)
        finish = None
        while queue:
            e = queue.popleft()
            if e in targets:
                finish = e
                break
            if e & independent:
                neighbors = [v for v in elements(outside)
                    if f.rank((independent^e)|v) == size]
            else:
                neighbors = [v for v in elements(independent)
                    if g.rank((independent^v)|e) == size]
            for v in neighbors:
                if v not in parents:
                    parents[v] = e
                    queue.append(v)
        if finish is None:
            reachable = sum(parents)
            partition = ALL ^ reachable
            assert f.rank(partition)+g.rank(reachable) == size
            return independent, partition
        while finish is not None:
            independent ^= finish
            finish = parents[finish]
        assert f.rank(independent) == g.rank(independent) == size+1


def certificate(rows,cols):
    f = Forest([(ROW[i],A+i%B) for i in rows])
    g = Forest([(COL[j],A+j%B) for j in cols])
    independent,partition = common_basis_or_partition(f,g)
    size = len(rows)
    return dict(size=size,partition=partition,
        row_rank=f.rank(partition),column_rank=g.rank(ALL^partition),
        common_independent_size=independent.bit_count())


def integer_rank(matrix):
    """Independent exact rank, using integer row operations and gcd reduction."""
    matrix = [row[:] for row in matrix]
    height = len(matrix)
    width = len(matrix[0]) if height else 0
    rank = 0
    for col in range(width):
        pivot = next((r for r in range(rank,height) if matrix[r][col]),None)
        if pivot is None:
            continue
        matrix[rank],matrix[pivot] = matrix[pivot],matrix[rank]
        for row in range(rank+1,height):
            if not matrix[row][col]:
                continue
            d = gcd(matrix[rank][col],matrix[row][col])
            u,v = matrix[rank][col]//d,matrix[row][col]//d
            matrix[row] = [u*x-v*y for x,y in zip(matrix[row],matrix[rank])]
            common = reduce(gcd,matrix[row],0)
            if common:
                matrix[row] = [x//common for x in matrix[row]]
        rank += 1
        if rank == height:
            break
    return rank


def incidence(edges,mask):
    bits = list(elements(mask))
    return [[int(bit == CONSTANT or bit == 1 << u or bit == 1 << v)
        for bit in bits] for u,v in edges]


def verify_rational_witness():
    path = Path(__file__).with_name('a5-residual-rational.json')
    witness = json.loads(path.read_text())
    left = list(map(Fraction,witness['left_weights']))
    right = list(map(Fraction,witness['right_weights']))
    assert sum(left) == sum(right) == 1 and all(left) and all(right)
    matrix = [[Fraction(ROW[i]==COL[j])/left[ROW[i]]
        +Fraction(i%B==j%B)/right[i%B]-1 for j in range(54)] for i in range(54)]
    available = list(range(54))
    for row,col,value in witness['pivots']:
        assert col == next(j for j in reversed(available) if matrix[row][j])
        assert matrix[row][col] == Fraction(value) != 0
        available.remove(col)
        for r in range(row+1,54):
            if matrix[r][col]:
                ratio = matrix[r][col]/matrix[row][col]
                for c in available:
                    matrix[r][c] -= ratio*matrix[row][c]
                matrix[r][col] = 0
    return [(r,c) for r,c,_ in witness['pivots']]


def run():
    # Fixed proposed ordered pivot sequence. Four special pivots follow the
    # previously proved first singleton and 25-block.
    pivots = [(0,53)]+[(i,i+27) for i in range(1,26)]
    pivots += [(26,27),(27,26),(28,25),(29,24)]
    pivots += [(i,i-28) for i in range(30,52)]+[(52,1),(53,0)]
    selected_rows = []
    selected_cols = []
    zeros = []
    for row,pivot_col in pivots:
        if 30 <= row <= 51:
            for col in range(pivot_col+1,54):
                if col in selected_cols:
                    continue
                c = certificate(selected_rows+[row],selected_cols+[col])
                c.update(row=row,col=col)
                assert c['row_rank']+c['column_rank'] < c['size'],c
                # Verify each final rank bound independently of the forest
                # rank oracle and matroid-intersection search algorithm.
                row_edges = [(ROW[i],A+i%B) for i in selected_rows+[row]]
                col_edges = [(COL[j],A+j%B) for j in selected_cols+[col]]
                assert integer_rank(incidence(row_edges,c['partition'])) == c['row_rank']
                assert integer_rank(incidence(col_edges,ALL^c['partition'])) == c['column_rank']
                zeros.append(c)
        selected_rows.append(row)
        selected_cols.append(pivot_col)
    assert len(zeros) == 231
    assert verify_rational_witness() == pivots
    return dict(status='EXACT WEIGHT-INDEPENDENT ZERO-MINOR CERTIFICATES',
        dimensions=[A,B,57],pivots=pivots,zero_minor_certificates=zeros,
        nonzero_pivots='All54 checked over Q in a normalized rank-one projector witness',
        rank_verification='All462 partition ranks independently recomputed by exact integer elimination',
        limitation='Transfer to all actual motifs uses the separate written general argument; no network or exponent update.')


if __name__ == '__main__':
    output = run()
    Path(__file__).with_name('a5-residual-symbolic.json').write_text(json.dumps(output,indent=2)+'\n')
    print('PASS:',len(output['zero_minor_certificates']),'exact zero-minor certificates')
