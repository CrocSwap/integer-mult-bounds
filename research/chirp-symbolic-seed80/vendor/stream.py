"""Exact modular chirp phases in lexicographic tensor order.

This executable reference uses adjacent odometer records and no per-output
scan of all axes. The fixed-tape cost is established separately in PROOF.md.
Metrics are verifier instrumentation, not part of the phase interface.
"""
from dataclasses import dataclass


@dataclass
class Axis:
    radix: int
    coefficient: int
    index: int = 0
    value: int = 0
    difference: int = 0


class ChirpStream:
    def __init__(self, r, radices, sources):
        assert r >= 2 and r & (r-1) == 0
        assert len(radices) == len(sources)
        assert all(t in (r//2, r) and t >= 2 for t in radices)
        assert all(0 < s < t for s, t in zip(sources, radices))
        self.r, self.modulus = r, 2*r
        self.axes = []
        for t, s in zip(radices, sources):
            a = (-s*(r//t)) % self.modulus
            self.axes.append(Axis(t, a, difference=a))
        self.phase = 0
        self.visits = self.wraps = self.rewinds = 0
        self.max_residue_bits = 0

    def advance(self, mutation=None):
        """Advance one address; return False after complete cyclic rollover."""
        i = len(self.axes)-1
        walked = 0
        while i >= 0:
            x = self.axes[i]
            self.visits += 1
            walked += 1
            if x.index+1 < x.radix:
                self.phase = (self.phase+x.difference) % self.modulus
                x.value = (x.value+x.difference) % self.modulus
                x.difference = (x.difference+(x.coefficient if mutation == 'wrong second difference'
                                               else 2*x.coefficient)) % self.modulus
                x.index += 1
                self.rewinds += walked-1
                self.max_residue_bits = max(self.max_residue_bits, self.phase.bit_length(),
                                            x.value.bit_length(), x.difference.bit_length())
                return True
            if mutation != 'omitted carry subtraction':
                self.phase = (self.phase-x.value) % self.modulus
            x.index = x.value = 0
            x.difference = 0 if mutation == 'zero wrap difference' else x.coefficient
            self.wraps += 1
            if mutation == 'stopped carry':
                self.rewinds += walked-1
                return True
            i -= 1
        self.rewinds += max(0, walked-1)
        return False

    def phases(self, mutation=None):
        while True:
            yield self.phase
            if not self.advance(mutation):
                return


def direct_phase(r, radices, sources, coordinates):
    """Independent original formula; not called by the streaming generator."""
    assert len(radices) == len(sources) == len(coordinates)
    return -sum(s*j*j*(r//t) for s, j, t in zip(sources, coordinates, radices)) % (2*r)
