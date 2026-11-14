# Productive helper 315: two rank-one moves become one rank-two move

This proof starts from the already published two-contraction word in SYLforge's PR7603
at `3f031ccb7ae7229a7323b1601877f24a46dfcf57`. That predecessor, including
its contractions on roles 166 and 134, receives the credit for those edits.
In particular, PR7603 cancels the adjacent opposite ADDs from 315 into 134;
removing those reads exposes the further opportunity proved here. The sole
new edit is the following contraction on helper 315. The native word retained
as `retained/two-contractions/word.json.gz` has compressed SHA256
`b3b991e9fc8d9eb684d2ee80ca477a04ad72106d6eee3f41f7b2284800c25d22`
and canonical uncompressed SHA256
`fd32412a33cd72b557f474223c7bcd669b20a0aeaabf8d7040f396e7070dddbf`.
All event indices below are zero-based in this exact PR7603 word.

## 1. Exact edit and non-observation premise

| Event | Operation | Frame dimensions |
| --- | --- | --- |
| 42077 | `MOVE 315, 729 -> 789, public` | 4 -> 5 |
| 42156 | `MOVE 315, 789 -> 808, public` | 5 -> 6 |
| 42158 | `ADD 315 += 331 @808` | first later access |

The respective frame bases over `F2^9` are `[6,24,42,385]`,
`[6,24,42,192,321]`, and `[1,6,24,42,192,320]`. Their spans are strictly
nested. Register 315 is a productive public helper, not a main or an owned
temporary. Its initial and final charts remain 3 and 127.

None of the **78** intervening operations references 315. The reference scan
checks both operands of ADD/COPY and the register operand of
MOVE/SCALE/INIT/CLEAR; those are all six opcodes in this source. Reads of 315,
not merely writes, are excluded. The cancelled reads of 315 were part of the
published predecessor; this change deletes no scalar instruction.

Delete event 42077 and replace original event 42156 with
`MOVE 315, 729 -> 808, public`. Every other event keeps its relative order.
The direct move executes at the later position, leaving 315 in its original
chart until just before its next access. The replacement has new index 42155;
the later ADD has index 42157. No new initialization, clear or workspace
owner is introduced. There are 76,637 instructions instead of 76,638.

## 2. Physical equality, including absolute phase

Let `F_A`, `F_B`, `F_C` be the actual invertible native frame operators for
charts 729, 789, 808, including their prescribed permutations and quadratic
phases. With column-vector convention a MOVE `A -> B` is
`M_AB = F_B F_A^{-1}`. The two original completed moves compose as

```
M_BC M_AB = (F_C F_B^{-1})(F_B F_A^{-1}) = F_C F_A^{-1} = M_AC.
```

This is operator equality with the absolute scalar phase retained. Taking
adjoints gives the reverse-order adjoint equality. The intervening
instructions operate on fields other than 315, so they commute with the
completed map on 315. This uses the inherited distinct-owner and
completed-call contracts, including restoration of shared scratch space.
It does not identify fields whose values happen to coincide. Correlations
with other fields do not prevent operators on distinct factors commuting.

All physical fields therefore agree at the second move's exit, before the
next access to 315. Earlier observations are unchanged, and there is no
observation while 315's temporary chart differs. In particular the
productive helper's terminal map from chart 3 to 127 and its independently
available output are unchanged. Its target credit is retained exactly once;
no new target or helper is asserted.

For every positive tensor multiplicity `f`,
`(M_BC M_AB)^(tensor f) = M_BC^(tensor f) M_AB^(tensor f)`.
The spectator factors are unchanged. This lifts a product identity; no
tensor power is distributed over an ADD or matrix sum. Admission and
recursive implementation at all multiplicities remain inherited premises.

`physical.py` checks all 512 forward basis columns and all 512 adjoint columns
by exact Gaussian dyadic arithmetic. It checks the new rank-two support and
equal-modulus contract on all 512 columns. Removing the target quadratic
phase and inserting a nontrivial global phase are rejecting controls. The
interpreter is explicitly retained from DreamingOfClouds' PR7601; it is not
claimed to be a separately implemented interpreter. The algebra above does
not infer the general identity from finitely many sampled inputs.

An additional exact sparse rational replay against PR7603 verifies all 1,569
rows, all end charts, owned MOVE multiplicities, 74 owned lifetimes, peak 50,
and coefficient-grid statistics. The complete non-MOVE instruction sequence
is literally unchanged. Thus the same scalar rows are erased at every
owned CLEAR, in the same order; MOVE changes charts rather than normalized
rational row coefficients.

## 3. Complete signed invoice and strict price improvement

The old child ranks are `5-4=1` and `6-5=1`; the new nested child has rank
`6-4=2`. The unchanged signed caller invokes the native word 17 times. Hence

```
Delta P_1 = -34,  Delta P_2 = +17,
Delta T_r = 0 for every r.
```

Paid positions fall from 110,400 to 110,383. Productive positions remain 22,461.
Paid rank mass is unchanged because `1+1=2`; the complete rank surplus
`sum_r r(T_r-P_r)` remains 1,424. Initial/final helper maps, owned rises, and
empty-root credits are unchanged.

For saving `C`, write `t=1-C` and
`F(C)=sum_r (T_r-P_r) r^t`. The exact moment change is

```
F_new(C) - F_7603(C) = 17 * (2 - 2^t).
```

For `0<C<1`, one has `0<t<1`, so `2^t<2` and the gain is strictly positive.
At `C=0` it is zero, consistent with the unchanged rank surplus. With the
directed gate's strict decreasing-moment certificate, this yields a
strictly higher raw crossing, not additional printed digits of the same
crossing.

The predecessor's uniqueness also follows on the certified interval:
`F_7603'(C) = F_new'(C) - 17 log(2) 2^(1-C) < 0`. Thus the directed
negative predecessor moment at `0.003650000454084` certifies an upper
bound for its unique crossing, rather than merely a negative sample.

The directed pricing certificates enclose the raw crossing strictly between
`0.0036502223358272` and `0.0036502223358273`; the full application supplies a
narrower rational enclosure in `data/FINAL.json`. The conservative complete
conditional claim is `C = 0.0036502223357`, exceeding the predecessor's
certified upper comparison bound `0.003650000454084` by exactly
`0.000000221881616`. Restoring the two rank-one costs and deleting the fused
rank-two cost recovers the predecessor invoice exactly, and that invoice
rejects this new claim. These are directed interval results, not acceptance
based on rounded transcendental calculations.

## 4. Precise finite stopping scope

Fix every scalar instruction, owned lifetime, public endpoint and caller.
Allow only sequential fusion of two ascending MOVEs on one register when
no instruction between them references that register, placing the direct
MOVE at the original later position. Exhaustive scanning of the exact
PR7603 word finds one eligible pair: helper 315 above. After its replacement
there are none. Consequently this finite rewrite family has only two
reachable words, and its only improved invoice is the one above.

`ceiling.py` authenticates the retained integer interval engine and this
exact invoice, then bounds `F'(C)` strictly below zero throughout
`0 <= C <= 0.00376669`, the inherited completed BIT cap. For each positive
coefficient `T_r-P_r`, its negative derivative summand is largest at the
cap; for each negative coefficient it is largest at zero. Summing directed
upper bounds proves monotonicity over the whole interval. Opposite strict
signs at the two bracket endpoints prove a unique crossing there. The old
invoice is strictly worse throughout the positive interval by the formula
above. Thus neither reachable invoice admits a raw price at or above
`0.0036502223358273` within this BIT-admissible interval. The registered
`data/CEILING.json` retains the exact rational derivative and sign bounds.
This is the fixed family's certified pricing ceiling, with both its
rewrite rule and its admissible interval explicit.

This is not a ceiling for scalar cancellation, retiming with repairs,
changes to helper stock, joint-register operations, different callers, or
integer multiplication. In particular PR7603's earlier removal of opposite
ADDs is outside the fixed-scalar family used here. It is neither claimed as
new work nor silently included in the exhaustion theorem.

## 5. Complete-application obligations and attribution

The local equality and price gain do not prove the entire multiplier by
themselves. The freshly completed source-bound application is recorded in
`data/NATIVE.json`, `data/SIGNED.json`, and `data/FINAL.json`. It binds the
exact 17-call signed caller and all 110,383 paid positions and 22,461 targets
to canonical candidate hash
`35782aef9427df489cc57fef2f2b87cd51c46fc67f0ec2f4ed863923c33a687b`.
It checks all 3,039 distinct paid/helper chart maps, all 104 main boundary
pairs, and every changed public itinerary, including this productive helper.
The fresh ordinary upper bound is 782,716,348, below the inherited billion
allowance; the precision factor is 2,430. The finite tape bounds are
25,454,373,504 elementary records and 43,923,200 scalar services. Earlier
PR7601 scalar edits are included in these recomputed bounds.

The complete application passes at the stronger framework claim
`0.003650222335827`, so the published `0.0036502223357` follows by weakening.
A separate public-claim gate also verifies all 54 strict and four functional
outer predicates, with minimum margin `10^-15`. Its
`H = 14252700000000000000` independently passes the context/tape checks;
the conservative context bound has 14,085 bits. The recorded conditions
therefore support the stated complete conditional claim, while preserving
the five framework premises below.

A separately scoped agent review checked the counted adapters, changed
helper's identity/target exception, reverse CLEAR functionals, invoice
substitutions, physical phase conventions, ordinary/precision/tape
recomputation, and the finite-family derivative bound. This is disclosed AI
assistance, not independent human or formal-kernel acceptance.

The five framework assumptions `native_all_columns`, `owned_erasure`,
`compiler`, `precision_tape`, and `analytic_recovery` remain conditional.
Only completed source-bound checks recorded with this package support a
complete conditional claim. No selected-result change, compiled universal
multiplier, formal-kernel proof, or independent human acceptance is asserted.

Credit SYLforge/PR7603 for its published combined predecessor and the cancellation
that releases 315; DreamingOfClouds/PR7601 for the token-settled edits;
ToikY/PR7546 for the complete predecessor application; Rohan Arun/PR7113
for the signed caller; and all retained contributors. The additional
helper 315 contraction is by Hao Yan (@FanPUYen), with substantial OpenAI
Codex assistance and a separately scoped agent derivation check. Apache-2.0.
