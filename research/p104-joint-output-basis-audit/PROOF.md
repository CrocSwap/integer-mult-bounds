# Independent finite rational audit of the PR6353 joint basis

## Exact claim

For the two frozen words in `SOURCE-PINS.json`, the rational public transfer
maps are equal on **every vector in `Q^770`**. Both literal words are replayed
with owned roles inactive initially, zero initialization at each `INIT`, and
discard at each `CLEAR`. `MOVE` is the identity in this scalar projection.
This claim concerns the complete 770 public outputs, not selected test vectors.

The input is the PR6349 word retained in canonical main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`. The output word and basis witness
are from PR6353 head `db2a20bc50bc7a8a4db931af85ce7f012ae7c3c3`.
The raw compressed word bytes, witness, predecessor proof and notice are
authenticated by both SHA256 and Git blob identifiers before use.

The audit also checks the nine anchor basis identities, their zero-specialized
dual preparation, exact inverse order, and the declared output-frame edits.
The original 1,094 frame coordinate lists and all input declarations are
unchanged. Exactly the following output declarations change:

| Public role | Output frame | Old dimension | New dimension |
|---|---:|---:|---:|
| 703 | 1094 | 9 | 5 |
| 393, 707, 484, 297, 485, 226 | 246 | 9 | 8 |
| 361, 451 | 245 | 9 | 8 |

The added frame is exactly `[7, 9, 35, 66, 400]`. Coordinate-span checks
establish the stated strict inclusions and dimensions; they do not establish
the associated native operator identities.

## Matrix convention and joint anchor identity

Write public scalar values as a column `x`. An operation `ADD(r,s,c)` means
`x_r <- x_r + c*x_s`. If the current symbolic row matrix is `R`, that event
left-multiplies `R` by its elementary matrix. Consequently a chronological
sequence `B2`, `B0`, `A`, `C` has matrix `C A B0 B2`.

The primary checker independently extracts `A` from the actual reversed
source word's zero-frame scalar operations and reads the three frozen blocks
of `C` from the witness. It checks one common actual first destination per block, a unique
zero-frame departure for each departing public field, and no public return
to the zero frame. These are the structural premises for moving those
zero-frame scalar operations to the front in their original order.

Let `P = (703,393,707,484,297,485,226,361,451)`, let `b_a` be row `a` of
`C A`, and let `e_a` denote the corresponding coordinate column. The full
row calculation checks

```
b_a B0 = e_a^T + d_a,       support(d_a) intersect P = empty.
```

Define `N = sum_{a in P} e_a d_a`. Every `d_a e_b` is zero, so `N^2=0`.
Thus `B2 = I-N` has exact inverse `I+N`. Moreover,

```
(e_a^T+d_a)(I-N) = e_a^T+d_a-d_a = e_a^T,
```

and therefore `b_a B0 B2=e_a^T` for all nine anchors. This is a coefficient
identity over `Q`, without floating point tolerances or a modular-rank
surrogate. The checker derives the serialized `B2` from the off-anchor rows,
checks all nine columns `B0 e_a` and every serialized response coefficient,
and verifies the elementary inverses.

There are 562 non-main public helper roles in this source. **381** have the
full zero-frame to full-frame boundary used by this basis. All anchors and
all roles touched by `B0` or `B2` belong to that 381-role subset. These two
inventories must not be conflated.

## Arbitrary inputs, dual scratch, and response insertion

Let `E_P = sum_{a in P} e_a e_a^T` and `T=I-E_P`. The dual preparation uses
zero owned scratch in the nine anchor positions and retains every other
independent public coordinate. Its scalar value is

```
u = C A B0 B2 T x.
```

The anchor identity implies `u_a=0` for each `a in P`, which justifies the
specific nine **dual preparation** zero rows. It does not set the nine
actual public inputs to zero. Since `N e_a=0`, `B2 e_a=e_a`, and the missing
responses are exactly

```
C A B0 B2 E_P x = C A B0 E_P x.
```

Adding them to `u` recovers `C A B0 B2 x` for arbitrary public input `x`.
The checker derives the 19 nonzero response rows from the actual source
preparation, independently of the author's constructor.

The dirty-carrier identity underlying a rank-one response group is valid
for arbitrary old carrier and recipient values. If the carrier response is
`s` and a recipient response is `lambda*s`, the three scalar updates give

```
recipient: u_r - lambda*u_c
carrier:   u_c + s
recipient: (u_r - lambda*u_c) + lambda*(u_c+s) = u_r + lambda*s.
```

This calculation requires the subtraction of the old carrier value.
The literal word checks below include a deletion control for that update.
Concretely, the actual first-destination-529 group has responses
`s_228=-x_451` and `s_744=4*x_451`. Taking carrier 228 gives `lambda=-4`:
preparing `u_744+4*u_228` and later adding `-4*(u_228-x_451)` leaves
exactly `u_744+4*x_451`. Dropping the preparation retains an unwanted
multiple of the arbitrary old carrier.
Frame equality and temporal role checks on this scalar word establish where
its updates occur. Native action, phase, and payment for the transports
remain outside this rational audit.

Chronologically applying `B0^-1` and then `B2^-1` has matrix
`B2^-1 B0^-1 = (B0 B2)^-1`. Reversing that order is not justified by the
elementary inverse identity. The primary checker checks the actual inverse
sequence and the complete literal endpoint, so endpoint restoration does
not rely solely on an assumed commutation with an unspecified native map.

The matrix witness is bound to the emitted word. The primary checker
replays its actual 4,708-event dual preparation, including all nine zero
scratch rows at their actual `CLEAR`s. The next 62 events recover every
public row of `A B0 B2` and the exact source first-departure frame labels.
Exactly 24 original first departures are replaced; the remaining 12,821
source events retain their literal order. The actual final 29 and 37
events implement `B0^-1` and `B2^-1`, respectively. A detached valid basis
witness would not satisfy these emitted-word checks.

## Independent literal evidence and controls

`verify.py` propagates sparse rational rows forward through both frozen
literal programs. `oracle.py` independently pulls each public output
functional backwards through the programs. Neither imports the predecessor
constructor, predecessor scalar checker, native checker or price engine.
`COPY` is independently interpreted as overwrite; `INIT` resets a role to
zero and lifetime reuse is tracked explicitly.
All 24 source `COPY` destinations are independently found to be scalar
zero immediately before copying, which checks the scalar premise for the
author's `COPY`-to-`ADD` transpose convention.

Each direction checks all 770 output rows over all 770 independent public
inputs: **592,900 coefficient positions**, with **874 nonzero coefficients**
in the common transfer matrix. The programs contain 17,452 and 17,657
events, respectively, and 32 and 41 owned lifetimes, both with peak 13 live
owned labels. The primary additionally derives 4,607 zero-frame preparation
gates, 584 first departures, and all nine dual preparation zero rows.

The backwards oracle removes four different actual scalar events. Each
mutated word changes a concrete public coefficient:

| Omitted mechanism | Output | Input | Correct coefficient | Mutated coefficient |
|---|---:|---:|---:|---:|
| Departure-basis inverse | 393 | 4 | 0 | -1 |
| Dirty-carrier subtraction | 228 | 0 | 0 | -1/2 |
| Input-basis correction | 549 | 1 | 0 | -1 |
| Output-basis inverse | 361 | 361 | 1 | 3/2 |

These are endpoint counterexamples to the mutated words, rather than
rejections caused only by a changed event count. The machine-readable
receipts retain their exact event indices and coefficients.

## Erasure distinction and remaining obligations

The nine added **forward** owned lifetimes have nonzero scalar rows before
their `CLEAR`s. In role order 770 through 778 their public-support sizes are
`116,4,110,106,8,109,100,4,110`. The complete source and output words have
31 and 40 nonzero scalar rows at `CLEAR`, respectively. The zero-row result
above applies specifically to the dual preparation, and cannot establish
zero erasure for these forward lifetimes. Permission to perform physical
erasure remains an explicit separate obligation.

This result certifies the frozen rational projection and stated basis
identities. It does not certify native all-column maps, absolute phases,
owned-erasure permission, the complete signed paid/productive invoice,
the nineteen-copy physical caller, ordinary or outer admission, a new
`kappa`, or a multiplication theorem. The five framework assumptions
`native_all_columns`, `owned_erasure`, `compiler`, `precision_tape`, and
`analytic_recovery` remain. The selected frontier is unchanged.

## Predecessor credit

Ali Romman, with substantial OpenAI Codex assistance, supplied the PR6353
joint-basis construction, literal word, witness and author proof. PR6349
supplies the input-lift source. PR6348 supplies the fixed binary-query-tree
consumer, and PR6350 supplies the released composition comparison; neither
consumer nor price is replayed here. Cinna Davis supplied the productive
caller, thin-query interface and exact Laurent factorization. The frozen
`sources/NOTICE` preserves the full earlier native, helper, recursion,
compiler, BIT and analytic lineage, including DreamingOfClouds' PR6314
source. The new contribution is an independent, source-bound finite
rational audit and its controls, prepared for ToikY with OpenAI Codex
assistance and separate checker, oracle and mathematical-review agents.
The elementary linear algebra identities and predecessor construction are
not claimed as new general results.
