# Compact controls on a recursive routing topology

Routing is combinatorial. A payload may be any object; its only operation is
exchange. A permutation p sends input x to output p(x). The network and its
switch count are classical Waksman results, Journal of the ACM 15(1), 159-163,
1968, [DOI](https://doi.org/10.1145/321439.321449). See also its
[corrigendum](https://doi.org/10.1145/321450.321465). No minimum among arbitrary
networks is asserted. This package adds its flat serialization, dense-row
address decoder and concrete implementation, produced by Nick Petalas.

## Topology

Let N=2^h, h>=1, m=N/2 and L=2h-1. Wires and layers are zero-indexed. At
layer t put `d=min(t,L-1-t)` and `b=2^d`. The layer pairs x with `x xor b`,
counting each switch once at its endpoint with bit d zero. Control one swaps
its values; zero leaves them unchanged.

A node of size n>2 has n/2 input switches, two children of size n/2, and
n/2-1 output switches. Its last local output pair bypasses an output switch:
its even output comes from the upper child, its odd output from the lower.
A size-two node has one switch. Upper/lower child wires interleave on even/odd
local indices. Their operations commute because their wire sets are disjoint.
The missing switches are fixed zeros of the full Beneš topology.

## Routing with the fixed bypasses

For a local permutation p, form a graph on its input indices. Join each input
pair. Also join the preimages of each output pair except the last one. These
are two matchings; parallel matching edges are allowed. All vertices except
p^-1(n-2) and p^-1(n-1) have degree two, and those two have degree one.
Thus the graph consists of even alternating cycles and one alternating path
between these two vertices. That path begins and ends with input edges, so
its length is odd, including the possible one-edge path.

Color the path alternately 0 and 1, starting with color zero at p^-1(n-2).
Its other endpoint has color one, as required by the bypasses. Color the
remaining even cycles alternately, starting each at its least uncolored input
with color zero. Every input pair and every non-bypass output pair now has
opposite colors.

Color zero selects the upper child; one selects the lower. Input switch i
has control color(2i). Non-bypass output switch j has control
color(p^-1(2j)). Both formulas send the desired inputs through their selected
child and then to their desired even/odd outputs. Each child receives exactly
one member of each input pair and sends one to each output pair. Its induced
permutation is

```text
p_color(x)[floor(x/2)] = floor(p(x)/2).
```

This is a bijection. Induction with the single-switch two-wire base proves
routing for every p and h. The implementation uses an explicit stack; the
binary tree has N/2 leaves and N-1 nodes. Each local graph vertex is enqueued
once. The bounds are finite and do not depend on a timeout or search heuristic.

Because swaps only move the payloads, the identity holds for all correlated
dirty values and every column multiplicity. A compiled inverse permutation
restores every value to its starting wire. This is logical wire restoration,
not physical allocator or tape-head restoration. The chosen controls can
differ from another compiler's choices even when final permutations agree.

## Exact payload count

Let S(N) count variable bits with h/topology external. The recurrence is

```text
S(2)=1,  S(N)=2 S(N/2)+N-1,  S(N)=Nh-N+1.
```

The full distinct-switch layout has m switches in each of L layers, for
`mL=Nh-N/2` bits. One output switch is omitted at each node above a size-two
leaf. Their number is `1+2+...+2^(h-2)=N/2-1`, with the sum empty at h=1.
These are structural records, not the number of nonzero controls of a given
permutation. Identical R-bit fixed-width records would save R(N/2-1) bits.
Framing, parameters and workspace are excluded equally. Neither entropy
optimality nor a physical runtime saving follows from this count.

## Flat row serialization and dense-row address

Order the switch pairs of each layer by the bit-deleted index

```text
j = floor(x/2^(d+1))*2^d + (x mod 2^d).
```

Both endpoints have the same j. For t<h all m controls are stored. For t>=h,
each depth-d node omits its last local output switch. Globally these are
exactly the final 2^d values of j. The row lengths are therefore

```text
ell_t = m                           for t<h,
ell_t = m-2^(2h-2-t)                 for h<=t<=2h-2.
```

Concatenate the rows without padding. Their start indices are

```text
o_t = t*m                           for t<h,
o_t = (t-1)*m + 2^(2h-1-t)           for t>=h.
```

For the second formula, the earlier omitted entries sum to the geometric
series `m-2^(2h-1-t)`. At t=h this sum is zero, as required. At the last
row the endpoint is exactly S. All earlier row intervals are adjacent.

The dense control at (t,x) is zero when `t>=h` and `j>=ell_t`; otherwise it
is compact bit `o_t+j`. Thus every returned index is in [0,S), each stored
index serves exactly two wire queries, and no omitted entry needs a stored
bit. At h=1 the single row has no omissions. This gives the address theorem
for every h>=1.

The address arithmetic uses a fixed number of shifts, masks, additions and
comparisons on O(h)-bit integers. That is a word-arithmetic statement, not a
unit-cost arbitrary-integer or finite-tape claim. Full input validation costs
O(S). `query` performs that validation per call; an admitted batch can use
`address` and the immutable ROM directly.

The canonical byte encoding puts bit i at byte floor(i/8), position i mod 8,
least-significant bit first. It uses ceil(S/8) bytes and sets all unused tail
bits to zero. A packed query validates the exact byte count and those final
padding bits, then reads the indexed bit. Every other byte value already
encodes eight legal bits, so no scan is needed for this structural validation.
It does not authenticate the requested permutation; endpoint correctness is
the compiler theorem. The decoder reads at most the last byte and the selected
byte, with h, layer and wire supplied externally. Physical seeks are unpriced.
Byte alignment is retained in comparisons: N=32 uses seventeen bytes here
versus eighteen for the full distinct-switch controls; N=4,8,16 saves bits but
not whole bytes.

## Finite evidence, resources and boundaries

The verifier independently expands recursive wire lists and enumerates every
stored switch and bypass. It checks all addresses at h=1,...,12 against this
list. Its endpoint oracle consumes the explicit switch list. The implementation
uses the arithmetic decoder. Both are compared with every requested permutation
at N=2,4,8 and with four specified permutations at each h=4,...,12. The all-h
claim follows from the proof, not this finite domain.

The executable enforces h<=12. Coloring and splitting at a size-n node use
O(n) word work: although component scans are nested, each vertex is processed
once in total. Summing node sizes over depths gives O(Nh) word operations.
Returned storage is O(Nh) words; pending child arrays and current scratch use
O(N) additional words. These bounds concern this Python algorithm. Its
managed allocations and one fixed-path module load are documented deviations
from the corresponding Power of Ten constraints.

The existing CRT producer's finite control, encoded input generation, framing,
scratch erasure, physical query and disposal are not replaced. Different
routing choices require rebuilding intermediate row keys before use in an
actual CRT repair caller. Complete native/caller/outer invoices and all five
selected framework assumptions remain open. This is a smaller routing-control
representation and adapter, not supplier admission or a multiplication theorem.
