# A maximal invariant guard on one complete two-digit quotient

This contribution was produced by Nick Petalas. Claim type: finite optimal-guard
certificate with a scoped written invariance and repair argument. Apache-2.0.

## Contract

Use the unchanged later-source compact word in Douglas Colkitt's
`notes/compact-control-movement.tex`, with the explicit packed semantics in
Arham Tahir's PR1603. Fix

```text
n=2, K=3, G=1, rho=2, B=2, C=B^n=4, Y=2^((n+1)K-rho)=128.
s=(y,t,u,c), 0<=y<128, 0<=t,u,c<4.
```

Here y is the target quotient after removing its two unchanged low bits.
Both processed source bits are in c, and t,u are the complete compact fields.
All upper target bits remain. In particular, equality modulo 16, the width
of the observed selected bits, is insufficient. The full target has nine
bits, the quotient has seven, and the omitted highest selected bit is retained
in the comparison. Source spectators and the arbitrary back field retain
the source note's unchanged swap-sandwich contract.

For two-bit z, define

```text
m(z) = z_0 + 8 z_1
p(y) = bit_0(y) + 2 bit_3(y).
```

The earlier-source map P_z on y,t consists of these four updates, in order:

```text
y += 2(z_0 t_0 + 8 z_1 t_1)              modulo 128
t += p(y)                                modulo 4
y += z_0(1-2t_0) + 8z_1(1-2t_1)         modulo 128
t -= p(y XOR m(z))                        modulo 4.
```

Every t digit is read from its current value. At radix two, the control
parities equal the two-bit integer u and loading c means u+c modulo four.
Thus S applies P_u and P_((u+c) mod 4), returning u,c unchanged. The intended
involution is T(s)=(y XOR m(c),t,u,c). Each elementary rotation is independent
of its destination, so S is a permutation on all 8,192 states.

Write H for PR1603's sufficient carry guard, specialized to this geometry.
The executable `carry_guard` is the direct specialization of that predicate.
Its all-size sufficiency and invariance remain predecessor results.

## New guard and exact finite theorem

Define

```text
B_extra = {s: c=0, t=1, u=2, y odd}
H_plus = H union B_extra.
```

On this entire quotient, H_plus is exactly the largest subset on which
S=T that is invariant under T. It is also the largest S-invariant subset
of agreement. Its size is 2,432, while H has 2,368 states. B_extra consists
of exactly 64 states and is disjoint from H. The good fraction increases
from 37/128 to 19/64. No other geometry or asymptotic optimum is asserted.

### Written proof of the added branch

Take y odd, t=1, u=2, c=0, and put a=bit_3(y). The temporary digits are
(1,0), and the controls are (0,1). The first target rotation is zero.
The temporary load is

```text
t_loaded = 1 + (1+2a) modulo 4 = 2+2a modulo 4.
```

The second target rotation is therefore -8 if a=0, and +8 if a=1.
It toggles bit 3 and preserves bit 0. The unload restores t=1 because
the selected bits of y_new XOR 8 are the original selected bits. Hence

```text
P_2(y,1) = (y+8(2a-1) modulo 128, 1).
```

The next P_2 sees 1-a and reverses the displacement exactly, including
wraparound. Since c=0, these are precisely S's two calls and T is identity.
Thus S=T on B_extra. T fixes this branch, so it is invariant.

The branch lies outside H: the inactive saturated low temporary digit and
odd low target produce carry d_1=1 into the active high digit. H excludes
that carry. At even y the same t,u,c triple is already in H, so dropping
the odd qualifier from the union changes no accepted state.

Combining this branch with the credited invariance and sufficiency of H
proves the improvement in writing. Its maximality is the finite theorem below.

### Finite completeness argument

Let E={s:S(s)=T(s)}. For any involution T, its largest invariant subset
contained in E is E intersect T(E). This general observation is already in
PR1603 and is not a new theorem claimed here. Equivalently, retain exactly
the complete cycles of the permutation S that lie inside E. Every
S-invariant subset is a union of complete S cycles. On a retained cycle,
S=T, so that cycle has length one or two and is T-invariant. This proves
that this cycle algorithm computes the unique largest admissible core.

The verifier builds S by ten literal rotations on full nine-bit targets.
It executes all 32,768 full-target states, including all four low-bit lifts
of every quotient state, and compares every output field to a separate
quotient implementation. Both S and T are checked to be permutations.
The cycle algorithm partitions all 8,192 quotient states. Its retained
bitmap equals the explicit H_plus predicate entry for entry. Every added
state is checked to have the displayed four field conditions, and the
entire explicit branch is present. This establishes finite maximality
without a conjectured extrapolation or a census of predecessor results.

The generated receipt hashes the core bitmap in the order
`index=(((c*4+u)*4+t)*128+y)`, with the lowest index in the low bit of each
byte. The bitmap is not handwritten. Normal verification writes no files.

## Current-address repair consequence

Since S and T preserve H_plus and agree there, the correction T S^-1 fixes
H_plus and permutes its complement. The retained extract/sort/reinsert
algorithm therefore has exactly 5,760 quotient records to repair, rather
than 5,824 with H. The finite checker installs a distinct payload tag at
every state, applies S, constructs all current-address keys T(S^-1(q)),
sorts all exceptional records and verifies every final destination tag.
It also checks that a wrong key T(q) produces an incorrect complete map.

With the predecessor notation V=MP, address width L and payload width P,
the declared repair bound stays

```text
O(V + M L^3 + delta M L(P+L)).
```

For this complete rectangle, delta changes from 91/128 to 45/64. The
64-record reduction is an exact counting consequence, not a measured
runtime saving. Every one of the twelve compact swaps, ten rotations,
source accesses, back-field returns and highest-bit completion remains paid.
The new predicate adds a constant number of field comparisons to H. The
finite sort replay is a logical record permutation, not a physical tape
implementation or a supplier admission.

## Limits

Maximality is proved by exhaustion only for the stated n=2 geometry. The
written branch argument also concerns precisely those parameters. No
all-n carry automaton, production predicate change, complete compiler,
native interface, recursive stock, precision, physical routing, analytic
transfer, new kappa or selected-frontier change is supplied. Independent
human and formal proof-kernel review are unclaimed.
