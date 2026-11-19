"""Uniform reversible bit programs for shared odd rational conversion. Apache-2.0."""
from collections import Counter
from dataclasses import dataclass

# Eight tracks per site; a gate acts on one site or a pair of adjacent sites.
X, D, C, Q, E, T, P = range(7)


def wire(site, track):
    return 8 * site + track


def swap(a, b):
    yield a, b
    yield b, a
    yield a, b


def majority(a, b, c, target):
    # Toggle target by majority(NOT a,b,c).
    yield (a,)
    yield a, b, target
    yield a, c, target
    yield b, c, target
    yield (a,)


def compare(lo, hi):
    """Toggle Q[lo] by the final carry in W + NOT(D) + C[hi+1]."""
    for sites in (range(hi, lo-1, -1), range(lo, hi+1)):
        for i in sites:
            yield from majority(wire(i,D), wire(i,X), wire(i+1,C), wire(i,C))
        if sites.step == -1:
            yield wire(lo,C), wire(lo,Q)


def step(lo, k):
    """Take one digit; [R on k sites,b] becomes [q,R' on k sites]."""
    hi = lo+k
    yield (wire(hi+1,C),)
    yield from compare(lo, hi)
    yield (wire(hi+1,C),)
    for i in range(lo,hi):
        yield wire(i,Q), wire(i+1,Q)
    for i in range(hi,lo-1,-1):
        yield wire(i,Q), wire(i,D), wire(i,E)
        yield from majority(wire(i,X), wire(i,E), wire(i+1,C), wire(i,C))
    for i in range(lo,hi+1):
        yield from majority(wire(i,X), wire(i,E), wire(i+1,C), wire(i,C))
        yield wire(i,E), wire(i,X)
        yield wire(i+1,C), wire(i,X)
        yield wire(i,Q), wire(i,D), wire(i,E)
    for i in range(hi-1,lo-1,-1):
        yield wire(i,Q), wire(i+1,Q)
    # The high remainder bit is zero. It receives q and clears the working flag.
    yield wire(lo,Q), wire(lo,X)
    yield wire(lo,X), wire(lo,Q)
    for i in range(hi,lo-1,-1):
        yield from swap(wire(i,D),wire(i+1,D))


def toggle_or(a,b,out):
    yield a, out
    yield b, out
    yield a, b, out


def rounded(m,k,s):
    """Keep the increment flag at Q[m], where m quotient bits precede k residue bits."""
    hi = m+k
    if s:
        # W = 2R + guard. A strict/inclusive comparison handles ties in one ripple.
        for i in range(hi+s-1,hi,-1):
            yield from toggle_or(wire(i,X),wire(i+1,T),wire(i,T))
        yield wire(m-1,X),wire(m,P)
        for i in range(m,hi+1):
            yield wire(i,P),wire(i+1,P)
        yield from toggle_or(wire(hi+1,P),wire(hi+1,T),wire(hi+1,C))
    yield from compare(m,hi)
    if s:
        yield from toggle_or(wire(hi+1,P),wire(hi+1,T),wire(hi+1,C))
        for i in range(hi,m-1,-1):
            yield wire(i,P),wire(i+1,P)
        yield wire(m-1,X),wire(m,P)
        for i in range(hi+1,hi+s):
            yield from toggle_or(wire(i,X),wire(i+1,T),wire(i,T))
    # Conditional increment, followed by carry uncomputation with the updated bits.
    yield wire(m,Q),wire(m,C)
    for i in range(m-1,-1,-1):
        yield wire(i+1,C),wire(i,X),wire(i,C)
        yield wire(i+1,C),wire(i,X)
    for i in range(m):
        yield (wire(i,X),)
        yield wire(i+1,C),wire(i,X),wire(i,C)
        yield (wire(i,X),)
    yield wire(m,Q),wire(m,C)


@dataclass(frozen=True)
class Layout:
    bits: int
    k: int
    e: int
    p: int

    def __post_init__(self):
        if min(self.bits,self.k)<1 or min(self.e,self.p)<0 or self.bits <= self.s:
            raise ValueError("Need positive widths, nonnegative scales, bits > max(e-p,0)")

    @property
    def s(self):
        return max(self.e-self.p,0)

    @property
    def m(self):
        return self.bits+self.p-self.e+1

    @property
    def sites(self):
        return self.m+self.k+max(self.s,1)+2


def program(layout, nearest=True):
    for i in range(layout.m):
        yield from step(i,layout.k)
    if nearest:
        yield from rounded(layout.m,layout.k,layout.s)
    # Return the supplied modulus to its original site positions.
    for lo in range(layout.m-1,-1,-1):
        for j in range(lo,lo+layout.k+1):
            yield from swap(wire(j,D),wire(j+1,D))


def word(value,width):
    if not 0 <= value < 1 << width:
        raise ValueError("value does not fit")
    return [(value >> i)&1 for i in reversed(range(width))]


def initial(layout, divisor, numerator):
    if divisor%2 != 1 or divisor.bit_length()!=layout.k:
        raise ValueError("expected a positive odd modulus of the declared length")
    state = [0]*(8*layout.sites)
    for i, b in enumerate(word(divisor,layout.k),1):
        state[wire(i,D)] = b
    for i, b in enumerate(word(numerator,layout.bits),layout.k+1):
        state[wire(i,X)] = b
    return state


def read(state,start,length,track):
    value = 0
    for i in range(start,start+length):
        value = 2*value+state[wire(i,track)]
    return value


def run(gates,state):
    head = 0
    counts = Counter()
    for gate in gates:
        sites = [w//8 for w in gate]
        anchor = min(sites)
        if max(sites)>anchor+1 or len(set(gate))!=len(gate) or min(gate)<0:
            raise ValueError("gate locality or alias")
        counts["moves"] += abs(head-anchor)
        head = anchor
        a = gate[-1]
        if len(gate)==1:
            state[a] ^= 1
        elif len(gate)==2:
            state[a] ^= state[gate[0]]
        elif len(gate)==3:
            state[a] ^= state[gate[0]] & state[gate[1]]
        else:
            raise ValueError("unknown gate")
        counts[len(gate)] += 1
    counts["moves"] += head
    return counts
