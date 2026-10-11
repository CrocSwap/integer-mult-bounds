# Disjoint target-prefix mixing and physical labels

## Frozen scalar construction

The parent is PR451's R740 bit word with entrance rank 149. During B, helpers
are constant and every target receives only helper registers along a nested
frame chain. For each frozen receiver u and donor w, choose a frame G on
w's chain. The F2 sums of helper registers delivered to u and w at frames
contained in G are equal and nonzero. Every retained later frame of u
contains G, and G is contained in u's final frame. The46 receivers and46
donors are disjoint, so no donor is changed by this construction.

After the parent's D gates, add y_u += y_w at frame zero. Replace the
receiver's scatter by its XOR with the donor's scatter. Remove the receiver's
B deliveries inside G, and insert y_u += y_w at G. Sort retained B deliveries
by frame dimension, placing mixes after ordinary deliveries of that dimension.
Thus w has received exactly its prefix inside G when the mix occurs. Helpers
are unchanged by this reordering. Donor and receiver labels are both G then;
the receiver can subsequently climb to all its retained later frames.

Let A_w be the donor's initial value plus its D compensation, S_w its centre
scatter, and H_w(G) its B prefix. The receiver's new terms are

```
A_w + S_w + (A_w + S_w + H_w(G)) = H_w(G) = H_u(G)
```

over F2. They replace precisely its removed prefix. Donor inputs, arbitrary
helper dirt and all other registers therefore have their old final values.
`rebuild.py` checks each set equality, containment, disjointness, ordering and
the complete emitted word, not just its histogram. Independent replays check
all 980 formal columns. The four controls omit the preconditioners, scatter
corrections or mix additions, or move a mix to the full frame; each fails.

## The bit label used here

For a frame F let P_F be its orthogonal projector. On two address halves,
the inherited bit address map is

```
D_F = [[I-P_F, P_F], [P_F, I-P_F]].
```

It is an involution because P_F is an idempotent. At every admissible odd
address modulus where the inherited rational frame data are defined, let
Λ_F act on an F2-valued stream by pullback along D_F. This definition has
no parameter for source, helper or target role. Those roles determine the
stream's start/final frames and its allowed operands, not this coordinate
map. In a routed invocation both operands also share the same surrounding
route conjugation, so equality of their physical labels is preserved.

This is the common-frame realization used for the parent's additions. Its
explicit definition extends unchanged to a target used as an operand. The
all-size compiler contract must realize that definition; finite tests alone
do not establish the compiler contract. The zero and final boundary labels
are left unchanged by this construction.

For any two bit streams f,g and any common address bijection D,

```
Λ(f XOR g)(x) = f(Dx) XOR g(Dx)
             = (Λf XOR Λg)(x).
```

Hence the shear `(f,g) -> (f XOR g,g)` commutes with `Λ ⊕ Λ`. A frame climb
acts as Λ_new Λ_old^(-1). By induction through climbs and additions, the
physical stream is the current block-diagonal label applied to the scalar
stream. Inserting either of the 92 new target additions preserves this
invariant because both operands have the same current frame. The other
instructions and inherited COPY/ERASE semantics are unchanged. This proves
the local scalar identity lifts within the stated shared-frame realization.

`labels.py` independently decodes every record and verifies the current
physical frame on both operands of all 46 frame-zero preconditioners and
all 46 mixes. It reconstructs the exact projectors and16×16 rational
involutions for all 47 distinct labels involved. As an independent control,
it enumerates81 addresses per family in F3^4 with bit values in F2. Across
zero, coordinate, diagonal and full projectors, all 648 scalar-basis
commutations pass. Giving the two operands unequal zero/diagonal labels
fails on54 columns. Address arithmetic over F3 and value arithmetic over F2
are intentionally distinct. These small finite controls illustrate and test
the formula; they are not an enumeration of the h=8 all-size compiler.
The stricter integer source-span check also verifies all 92 target operands.

## Whole-residual global composition

The frozen word changes only D, B and scatter. Starts, finals, frames, source
lines, helper ownership, all A/C gates and R are identical to PR451. Thus
the same18 checked residual isometries and complete hosting selection apply.
The complete PR451 parent is rebuilt first. Its emitter reads the new records;
its independent audit decodes those records separately and binds the resulting
streams, ownership and new physical instruction digest. Target additions
occur within the active pair and do not touch any idle host pair.

Every one of11×8×740=65,120 helper occurrences remains whole on one idle
data family. All windows, slots, capacities and complementary idle children
are checked again. No cross-family residual factorization is used. All9,340
unbanked global F2 columns,1,320 routes and24 omitted bridge controls are
checked. The paid profile is

```
rank       1      2      3      4     5    6    7   8  35  56
count 217576  93392  24064  31112  8624 5664 5168 792   8 440
```

Rank mass 745,536 gives78×9,600−745,536=3,264. The physical stock is9,609.
The prefix now takes 155 bits and the three-level envelope 520 bits; the
charges remain192 and1,024 bits. The bit row coefficient 19,431 and PR451's
uniform complex row bound below20,161 are unchanged. The complete finite
invoice is recomputed using the new instruction counts and prefix.

The unchanged complex local word and11-stage supplier are freshly rebuilt
and audited through PR451. Its two moment engines certify the interval
[0.001268142296690675830146,0.001268142296690675830147]. This release uses
that full rational lower endpoint; PR451 unnecessarily rounded it to18
places because its bit side bound the result. The new bit lower endpoint is
0.001275657818793753037875. The complex side now binds.

Six exact bootstrap levels and all 47 strict outer constraints produce

```
κ = 126653614863031 / 100000000000000000
  = 0.001266536148630310.
```

The next10^-18 grid point and zero-eta, zero-beta and unit-beta controls fail.
All inherited realization, hosting, finite-to-asymptotic and analytic
contracts remain as listed in the README. No finite replay discharges them.
