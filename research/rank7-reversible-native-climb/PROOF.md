# A guarded, in-place Gaussian C lift at the reached A13 boundary

## Boundary and scope

The scientific baseline is canonical main
`997e6a9ca7b4f95d50e366f61412fd640d72a88a`, priority revision 6.
The selected conditional kappa is unchanged at `0.001672660197076918`.
The live sources are pinned in SOURCES.json. This result uses the exact
native semantics retained in PR3086 and the scalar circuits retained in
PR3094. It does not independently reprove either entire predecessor package.

In both pinned PR3076 providers, forward native events 6683 through 6685 are:

```text
source83: physical warp from frame [382] to frame [45], logical operator K52
target126: climb from frame [] to frame [45]
target126 -= source83/2 in frame [45]
```

The fresh predecessor replay checks the complete native compiler receipt,
literal event addresses, free-warp prefix rows and all 512 complex columns.
Let the independent normalized input fields be `x126,x127,x164,x165,u`.
Their real and imaginary components are signed P-bit integers in `[-L,L-1]`,
where `L=2^(P-1)` and `3 <= P <= 128`. Define

```text
v = (x126 - x127 + x164 - x165)/2
E = [382], F = [45], K = K52
W = T_F K T_E^-1
```

The physical input is `(v,T_E u)`. The output is
`(T_F v - T_F K u/2, T_F K u)`.
The source is changed by its required warp and preserved by the subsequent ADD.
This theorem assumes that the producer has supplied these entrance arrays.
It does not implement the earlier residual adapters or the full prefix.

## The four-real-field lift

For sign `s` equal to +1 or -1, C acts on two complex coordinates by

```text
z0' = ((1+s*i)*z0 + (1-s*i)*z1)/2
z1' = ((1-s*i)*z0 + (1+s*i)*z1)/2.
```

Write `z0=a+i*b`, `z1=c+i*d`. Assume the encoded integers `a-c` and `b-d`
are even. Also require every following arithmetic endpoint to fit the signed
word. Execute the first listed operation first:

```text
a -= c;       b -= d
c += a/2;     d += b/2
(a,b) = (-s*b,s*a)
c -= a/2;     d -= b/2
a += c;       b += d
```

This is eight source-preserving additions, one word SWAP and one negation.
The rotation is a literal three-CNOT-per-bit SWAP, then negation of a for
`s=+1`, or b for `s=-1`. No field is discarded or overwritten without an
invertible instruction.

To verify the identity, put `x=a0-c0`, `y=b0-d0`,
`m=(a0+c0)/2`, `n=(b0+d0)/2`. Immediately before rotation the four values
are `(x,y,m,n)`. Rotation gives `(-s*y,s*x,m,n)`. The last four additions give

```text
a = m-s*y/2,  b = n+s*x/2
c = m+s*y/2,  d = n-s*x/2,
```

which are the real and imaginary parts of C's two outputs. The exact rational
row checker compares this with the literal four-by-four C matrix for both signs.

The first two differences are even by hypothesis. The four half-source reads
use only those differences, including their swap and sign changes, so every
division is exact. The final additions do not require even sources.
This guard is stronger than merely asking that the C endpoint be integral.
For example `(a,b,c,d)=(1,1,0,0)` has integral C(+1) output `(0,1,1,0)` but
fails this lift's half-source guard. The implementation rejects it.

## Literal Boolean implementation and clean return

Every ADD uses PR3080's read-only shifted-source ripple circuit. At active
width w it uses `4w-5` CNOTs and `4w-6` Toffolis and returns its `w-1`
clean carries. Half-source reads use source bits shifted right by one, with
the explicit repeated sign control. Source words are not physically shifted.
Subtraction reverses the ADD gates. The proved guard makes these modular
circuits exact signed arithmetic at each macro endpoint.

PR3094's prefix-OR negation uses `5w-7` CNOTs and `2w-4` Toffolis. Its
carry workspace returns to zero because the lower-prefix OR is invariant
under two's-complement negation. Signed range excludes an overflowing
negation of the minimum word. Each SWAP uses `3w` CNOTs. The same carry bank
is reused serially after every macro. These inherited circuit constructions
are executed here, rather than replaced by arithmetic assignments.

Thus one C pair costs exactly

```text
CNOT     = 40w-47
Toffoli  = 34w-52.
```

The constructed control first physically halves x and y, uses unit additions
to form m and n, rotates, subtracts, physically doubles the two rotated
differences, then performs the final additions. It implements the same map
under the same guard. Its four physical shifts add `4*(3w-2)=12w-8` CNOTs.
Both implementations use the same data fields and carry bank. This is a
specified constructive comparison, not a claim that either circuit is optimal.

## Actual native dispatch, width and alignment

The source operator W is a Gaussian monomial. The code rederives its complete
signed permutation from the pinned native operators. It realizes that
permutation by word SWAPs and then executes every required negation.
It does not substitute logical K for physical W.

The target's canonical rank-one frame consists of a Gaussian monomial,
one C factor and a second Gaussian monomial. The dispatch executes both
signed permutations and the 256 disjoint C pairs on all 512 complex
coordinates, then all 1,024 real half-ADDs. Real-word SWAPs, Gaussian phases
and source sign-fill reads are included in the tariff.

Each component of v lies in `[-2L+1,2L-1]`, and its quarter-grid encoding
`4v` is even. The first target monomial preserves evenness. Therefore every
pair satisfies the C lift's alignment guard. The rational microstate checker
finds row l1 norm at most 2 at every cut of both lifts, so all target-climb
encoded microstates have absolute value at most `16L-8`.

The inherited exact source bound is `abs(component(T_E u)) <= 2L-1/2`.
The physical source warp is a signed permutation, so every encoded source
microstate has absolute value at most `8L-2`. Every encoded final source
`4*T_F K u` is even, as checked coefficient by coefficient in the predecessor.
The final half-ADD is therefore aligned. Its exact target range is
`[-5L+9/4,5L-9/4]`, so its encoded magnitude is at most `20L-9`.

A signed word of width `w=P+5` has limit `2^(w-1)=32L`.
All three bounds are strictly below that limit. Thus every stated arithmetic
cut fits for every allowed P. These static input theorems supply the guards;
the gate tariff does not charge runtime hardware comparators. The predecessor's
attaining low/high fixtures show why width `P+4` does not suffice for the
whole endpoint at this fixed quarter grid.

## Complete local bill

The direct dispatch has 3,200 word SWAPs, 1,248 negations, 1,024 unit ADDs
and 2,048 half-unit ADDs, including the source warp, both target monomials
and the consumer.
The complete affine tariff is

```text
CNOT     = 28128w-24096
Toffoli  = 14784w-23424.
```

The physical-shift control adds 1,024 HALF/DOUBLE macros, giving
`CNOT = 31200w-26144` and the same Toffoli count. At w=69 the direct count is
1,916,736 CNOTs and 996,672 Toffolis; the control uses 2,126,656 CNOTs and
996,672 Toffolis. The saving is exactly 209,920 CNOTs.

The two existing complex arrays contain `2048w` bits. A separate owned clean
carry bank contains `w-1` bits. There is no component scratch. This is local
data accounting; it neither removes the inherited 91 private buffers nor
proves a new complete supplier stock bound. Arbitrary-wire CNOT/Toffoli gates
have unit cost here. Word SWAPs are charged, but physical backing, topology,
multitape access time, stock production, child arithmetic and later cleanup
are not supplied. The recursive histogram and kappa remain unchanged.

## Evidence and limits

The registered replay authenticates every live input before loading the
predecessor, then cold-rebuilds both native providers and reproduces the
predecessor receipt. It checks the new rational C identities and every
microstate row bound. Packed execution checks all parity-matched half-range
inputs at widths 3 through 6: 64, 1,024, 16,384 and 262,144 columns respectively,
for both signs, both implementations and their literal inverses.

The full direct dispatch executes zero, grid, dense, alternating and both
attaining endpoint fixtures at P=3,64,128. These are 18 complete native
fixtures. The dense P=64 fixture also executes the complete control and
inverse. A separate Gaussian operator evaluator determines the expected
outputs. Every macro verifies its signed/grid guards and literal data and
carry return. Nine behavioral groups check semantic mutants and boundary
failures, including a deliberately live carry mutation.

These finite checks support the uniform argument above. They are not
exhaustive over all native inputs or a full multiplication theorem. Both
reused providers are freshly bound, but they share the same local operator;
the new full bit dispatch is executed once per fixture, not counted twice.
An internal read-only review separately checked the identity, tariffs and
matched-parity cases at widths 3 through 5. No independent human review,
formal proof-kernel verification or supplier admission is claimed.
