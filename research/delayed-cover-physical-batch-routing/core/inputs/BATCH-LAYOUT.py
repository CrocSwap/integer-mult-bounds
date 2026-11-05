"""Exact reference addresses for whole-high-matrix child batches.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
This is a reference address model, not a physical tape implementation.
"""
from dataclasses import dataclass


def need(ok, message):
    if not ok:
        raise ValueError(message)


@dataclass(frozen=True)
class Layout:
    low: int
    high: int
    depth: int
    slabs: int = 1

    def __post_init__(self):
        need(all(type(x) is int for x in (self.low,self.high,self.depth,self.slabs)), 'integer dimensions')
        need(self.low >= 2 and self.high >= 1 and self.depth >= 0 and self.slabs >= 1, 'positive dimensions')

    @property
    def rows(self):
        return self.slabs * (self.low*self.high)**self.depth

    def split(self, index, level):
        need(0 <= level < self.depth and 0 <= index < self.rows//self.low**level, 'parent address')
        power = self.high**level
        stock, ancestors = divmod(index,power)
        tail, digit = divmod(stock,self.low*self.high)
        low, high = divmod(digit,self.high)
        return low, (tail*self.high+high)*power+ancestors

    def join(self, low, index, level):
        need(0 <= level < self.depth and 0 <= low < self.low, 'return low type')
        need(0 <= index < self.rows//self.low**(level+1), 'child address')
        power = self.high**level
        rest, ancestors = divmod(index,power)
        tail, high = divmod(rest,self.high)
        return (tail*self.low*self.high+low*self.high+high)*power+ancestors

    def descend(self, row, level):
        types = []
        for j in range(level):
            low,row = self.split(row,j)
            types.append(low)
        return tuple(types),row

    def return_address(self, types, index):
        for j in reversed(range(len(types))):
            index = self.join(types[j],index,j)
        return index

    def ancestors(self, index, level):
        values = []
        for _ in range(level):
            index,digit = divmod(index,self.high)
            values.append(digit)
        return tuple(values)

    def route(self, index, level, permutation):
        need(len(permutation) == self.low*self.high and
             set(permutation) == set(range(len(permutation))), 'whole cover permutation')
        power = self.high**level
        stock, ancestors = divmod(index,power)
        tail,digit = divmod(stock,self.low*self.high)
        return (tail*self.low*self.high+permutation[digit])*power+ancestors
