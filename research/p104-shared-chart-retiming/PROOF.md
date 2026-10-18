# Shared-chart retiming across two early ADD stars

The source is commdata2338's PR2662, exact head
`b67542b2896c21106f3945673bbf5b6e131408cc`. Its 5,270-event word is retained
byte-for-byte. The construction/native correctness of all unchanged edges is
inherited from that pending source and ywz65's PR2586, rather than recertified.
This proof supplies a same-boundary replacement for two small source regions.

## 1. Boundary and source chronology

Use the source convention `Delta_W = conjugate(Gamma_W)`, with chronological
transport `Delta_B Delta_A^-1`. Logical fields are arbitrary arrays. The 358
public inputs comprise 104 X fields, 104 Y fields and 150 independent dirty
helpers. Eight owned private lifetimes initialize zero and erase exactly zero.
The source's complete physical input/output frames, public linear map and
private allocation/disposal contract are retained. This is still a partially
corrected P104 physical inverse-transpose; the other 102 forward rows have the
predecessor's Gram/2 contract, not an identity contract.

The following source event numbers are zero-based. They identify occurrences
in the retained literal word, not labels recalculated after editing.

| Source field | First transport | Early consumers | Subsequent transport |
| --- | --- | --- | --- |
| Y1 | event 105: ZERO to span(391) | N2 += 2 Y1 at 384; N33 += Y1 at 388 | event 980: line to rank-seven frame |
| Y0 | event 104: ZERO to span(386) | N4 += Y0 at 386; N34 += Y0 at 389 | event 981: line to rank-five frame |

N2 and N4 enter the corresponding line at events 380/381, then immediately
after their ADDs move to the same rank-two frame `span(386,5)` at 385/387.
N33 and N34 enter their lines at 382/383 and remain there after their ADDs.
Each field is otherwise untouched within its affected interval. The producer
checks this by enumerating every source and target use, not only writes.
N2, N4, N33 and N34 may contain arbitrary dirty data at these cuts.

## 2. The local identity, including dirty inputs

For any invertible linear chart T, scalar c, and arbitrary arrays a,b,

```
T(b+c*a) = T*b + c*T*a.
```

Therefore converting both operands by T before `b += c*a` is equivalent to
performing the ADD first and then converting both operands. The statement is
an operator identity for arbitrary arrays, not a clean-target or sample-input
argument. Several target ADDs sharing an unchanged source obey the same
identity simultaneously. A conversion on only the source cannot commute this
way; the negative control leaves the targets in the old chart and rejects.

Apply the identity to each complete three-register star `(Y1,N2,N33)` and
`(Y0,N4,N34)`. Perform its two scalar ADDs in ZERO. For N2 and N4, replace the
two original line transports by one ZERO-to-rank-two transport at the same
post-ADD event. For Y1 and Y0, postpone their line entries and combine them
with their next transports, giving ZERO-to-rank-seven and ZERO-to-rank-five.
For N33 and N34, move their ZERO-to-line transport immediately after their ADD;
these two children remain explicitly charged. By the checked no-use intervals,
all disjoint events between the replacements commute with the affected fields.

No extra field, temporary copy, ADD or disposal is introduced. All 3,104 ADD
operand/coefficient records remain in their original order; exactly four frame
annotations change. All 208 signs and 16 private zero/erase events are literal
and unchanged. At the end of each affected interval every field has precisely
its original physical value and frame, so the remainder of the source word
composes without a new consumer adapter or cleanup payment.

This differs from PR2662's role-local endpoint-run class: that class fixes ADD
frames and treats every ADD as a barrier. The shared-chart identity changes
four ADD frames jointly. Its scoped optimum is not contradicted.

## 3. New positive children, with exact phase

All four replacement edges start at ZERO. Three distinct target frames occur:

```
rank 2: (386,5), used twice;
rank 5: (273,145,96,12,2);
rank 7: (273,145,81,49,9,5,2).
```

The pinned canonical chart definition gives `Gamma_W = M F_r M^-1`, where M
is a Gaussian monomial and `F_r` is the positive rank-r child, a product of r
coordinate C gates. The gates satisfy `conjugate(C)=C^-1=X*C`. Hence

```
Delta_W = conjugate(M) * F_r * X_(2^r-1) * conjugate(M)^-1.
```

The displayed product uses ordinary right-to-left operator composition. The
implementation stores chronological lists: first `conjugate(M)^-1`, then X,
then F_r, then `conjugate(M)`. Here M is the operator executed by the chart's
chronological P,D list. `NATIVE.json` stores both monomial lists and the single
positive child rank; the checker compares their complete operator against
`conjugate(frame(W))` from the retained interpreter.

Only positive children occur; the conjugate inverse is not counted as free.
The X correction is part of the monomial wrapper. No compiler or predecessor
builder is imported. Exact signed Pauli images plus a nonzero state column fix
each operator including global phase; in addition all 512 Gaussian basis
columns of each of the three recipes agree (1,536 total). The Pauli mixing
block has rank r for every target, corroborating the declared child rank.
The identities tensor-lift formally to arbitrary payload depth, but this is
not an all-size physical compiler, precision or hosting theorem.

## 4. Whole-word induction and invoice

Maintain a rational row over all 358 independent initial logical arrays in
each live register, together with its exact binary frame. Every scalar ADD
requires equal frames; every transport is nested and preserves the logical
row; a sign negates it; owned initialization creates the zero row and erase
requires the zero row. Both source and candidate are replayed, including all
public output rows and frames. Their full 358-by-358 coefficient matrices
agree. All 150 dirty helper rows equal their initial rows, and all eight
private erasures are zero. This finite all-column check supports the local
operator proof and catches omitted compensation or a changed public update.

The candidate profile is

```
1498 H1 + 60 H2 + 74 H3 + 92 H4 + 58 H5 + 56 H6 + 92 H7 + 8 H8.
```

It has 1,938 positive transports, 5,266 total events and rank mass 3,542.
Relative to PR2662 the exact changes are two `H1+H1 -> H2`, one
`H1+H4 -> H5`, and one `H1+H6 -> H7`. For any fixed m>0 and 0<p<1, the local
child-sum difference is

```
[2*(2^p-2) + (5^p-1-4^p) + (7^p-1-6^p)] / m^p < 0.
```

Each term is strictly negative by strict subadditivity of x^p on positive
arguments. At p=1 the difference is zero, consistent with unchanged rank mass.
This comparison fixes the rest of the caller bill; no complete favorable
moment follows. It is not an optimum for other joint frame changes.

## 5. Family decision and costs left open

The narrow replacement has a constructive child profile, the same scalar
operations and storage inventory, and matching physical values at every exit
from an affected interval. Thus this local change needs no compensating
consumer operation. It does not price the unchanged whole consumer.

The full physical scalar/address work, chronological owners and windows,
idle/residual children, monomial movement, precision, approximate-child
defects/rounded erasure, remaining identity corrections and all-size admission
are unknown. They are not set to zero. The physical component bound for the
different PR2586 word (PR2674) is not silently transferred. Under revision 5,
the decision is to finish this finite interface and stop; no dependent search
or family expansion is justified by the four-child improvement alone.

Credit commdata2338/2662 for the exact source and explicit ADD-barrier handoff;
ywz65/2586/2497/2551, Nick Petalas/2550 and the full source lineage retained in
the byte-identical READMEs. Common-chart linearity and the C inverse identity
are standard, not newly claimed mathematics. Prepared for ywz65 with
substantial OpenAI Codex assistance, Apache-2.0.
