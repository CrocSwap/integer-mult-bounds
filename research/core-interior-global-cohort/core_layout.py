"""Complete original-coordinate gather, including arbitrary spectator axes.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
Support completion extends the retained global-boundary Layout construction.
"""
from dataclasses import dataclass
from cohort_sources import need


def address(value, mapping):
    result = value
    for old,new in mapping.items():
        result &= ~(1 << new)
        result |= ((value >> old) & 1) << new
    return result


@dataclass(frozen=True)
class Layout:
    lengths: tuple[int,...]
    selected: tuple[int,...]
    local_bits: int

    def __post_init__(self):
        need(type(self.lengths) is tuple and type(self.selected) is tuple,
             'immutable original axis and selected-axis tuples')
        need(bool(self.lengths) and all(type(x) is int and x >= 1 for x in self.lengths),
             'complete original positive axis widths')
        need(type(self.local_bits) is int and self.local_bits >= 1,'positive dyadic core width')
        need(bool(self.selected) and len(set(self.selected)) == len(self.selected)
             and all(type(a) is int and 0 <= a < len(self.lengths)
                     and self.lengths[a] >= self.local_bits for a in self.selected),
             'distinct actual selected axes containing complete cores')

    @property
    def n(self):
        return sum(self.lengths)

    @property
    def g(self):
        return len(self.selected)

    @property
    def size(self):
        return 1 << self.local_bits

    @property
    def labels(self):
        return 1 << (self.n-self.g*self.local_bits)

    @property
    def starts(self):
        total,answer = 0,[]
        for length in self.lengths:
            answer.append(total)
            total += length
        return tuple(answer)

    @property
    def positions(self):
        return tuple(self.starts[a]+b for a in self.selected for b in range(self.local_bits))

    @property
    def gather(self):
        source,target = self.positions,tuple(range(self.g*self.local_bits))
        mapping = dict(zip(source,target))
        mapping.update(zip(sorted(set(target)-set(source)),sorted(set(source)-set(target))))
        need(set(mapping) == set(mapping.values()) and len(mapping) <= 2*self.g*self.local_bits,
             'complete support-local original-coordinate permutation')
        return mapping

    @property
    def inverse(self):
        return {new:old for old,new in self.gather.items()}

    def original_base(self, label):
        need(type(label) is int and 0 <= label < self.labels,'complete packed coarse label')
        return address(label << (self.g*self.local_bits),self.inverse)

    def core_starts(self, label):
        raw = self.original_base(label)
        values = tuple((raw >> self.starts[a]) & ((1 << self.lengths[a])-1) for a in self.selected)
        need(all(x % self.size == 0 for x in values),'actual original complete-core starts')
        return values

    def coordinates(self, label):
        raw = self.original_base(label)
        return tuple((raw >> start) & ((1 << width)-1)
                     for start,width in zip(self.starts,self.lengths))

    def record(self):
        return dict(lengths=self.lengths,selected=self.selected,local_bits=self.local_bits,
            full_bits=self.n,labels=self.labels,gather=sorted(self.gather.items()),
            inverse=sorted(self.inverse.items()),support=len(self.gather))
