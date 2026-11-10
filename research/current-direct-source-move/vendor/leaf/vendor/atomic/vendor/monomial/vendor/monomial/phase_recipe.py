"""Finite monomial compilation and encoded tensor-phase accumulation."""
import phase_sources
_native,_compact,reference = phase_sources.activate()
from cardinal_counts import Count
from compact_counts import bit_at
from stream import Counter
from words import need


class Recipe:
    def __init__(self,literal,vectors):
        self.vectors = tuple(vectors)
        m = len(self.vectors)
        need(0 < m <= 73 and len(set(self.vectors)) == m, "fixed monomial coordinate vocabulary")
        self.matrix = tuple(literal["matrix_rows"])
        self.linear = tuple(literal["linear_Z4"])
        rows = tuple(literal["quadratic_rows"])
        self.offset,self.constant = literal["offset"],literal["phase"]
        need(len(self.matrix) == len(self.linear) == len(rows) == m, "complete fixed recipe")
        need(all(type(row) is int and 0 <= row < 1<<m for row in (*self.matrix,*rows)),
             "fixed binary recipe rows")
        need(type(self.offset) is int and 0 <= self.offset < 1<<m and
             type(self.constant) is int and 0 <= self.constant < 4 and
             all(type(value) is int and 0 <= value < 4 for value in self.linear), "fixed affine and phase constants")
        self.quadratic = tuple((i,j) for i in range(m) for j in range(i+1,m) if rows[i]>>j&1)
        self.word = reference.binary_word(dict(matrix_rows=self.matrix,offset=self.offset))

    def phase(self,state,columns,spacing,residue,inverse=False):
        remaining = Counter(columns)
        repetition,position = Count(columns),Count(residue)
        value = self.constant*repetition.divide_small(4) % 4
        repetition.close()
        try:
            while not remaining.finished:
                # One bit per compiled coordinate is a fixed finite state.
                bits = tuple(bit_at(state[name],position) for name in self.vectors)
                for coefficient,bit in zip(self.linear,bits):
                    value = (value+coefficient*bit) % 4
                for i,j in self.quadratic:
                    value = (value+2*bits[i]*bits[j]) % 4
                position.add(spacing)
                remaining.decrement()
            return (-value)%4 if inverse else value
        finally:
            position.close()
            remaining.close()
