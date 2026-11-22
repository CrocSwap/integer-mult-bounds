# Proof and verification boundaries

## Scalar domain and source

The pinned native graph is the literal #8027 111-port tape: 39,600 instructions, 630 public field owners, 2,803 MOVE occurrences and 3,433 private clears. Its source and the original one-export readout lists are pinned to #8027 and #8036 in `SOURCES.json`. A public field can be restricted to an arbitrary constant binary field. Impossibility on those binary inputs is therefore a necessary obstruction for any proposed word required to serve all original arbitrary field inputs. Clocks below are zero-based original instruction indices.

## A parity unaffected by every surviving payload

For either one-export branch, direct forward propagation gives

`T = M + s r`,

where rows of `M` are the original public-output forms, `s` selects affected outputs and `r` is the missing input parity. The reverse interpreter independently checks the transpose of each 630-by-630 matrix. The native operator is an involution. Set `ℓ = r M⁻¹`; the checked helper support gives `ℓ = r` and `ℓs = 1`. Therefore

`ℓT = ℓM + (ℓs)r = r + r = 0`,

while `ℓM = r ≠ 0`. Thus `T` omits an output parity required by the original operator. Both branch maps have rank 629.

Freeze the remaining local instructions, MOVE positions and endpoints, and the final readout. Insert an independent formal symbol `z_e` into each surviving pre-MOVE payload. Linearity of the fixed suffix gives

`y = T x + Σ_e d_e z_e`.

The forward replay inserts all 2,802 independent symbols at once; its exact rank of `[T D]` is 629 and `ℓ[T D] = 0`. The reverse replay independently reconstructs each `d_e`, verifies `ℓd_e = 0` for every one, and checks the 630×630 transpose. Any collection of causal additive payload substitutions is represented by choosing the corresponding `z_e` as a function of the inputs and earlier choices. They cannot change `ℓy = 0`; the native map has `ℓMx = rx`, which is nonzero for some input. This proof allows simultaneous substitutions of any values at those MOVE slots. It does not allow new free ADDs, altered terminal reads, new contacts or new chart/owner bindings.

The verifier checks rank 629 both for `T` and for the full span of reverse MOVE sensitivities. It also rejects a corrupted source and checks a deliberately faulty native carrier that a legal live cocharted ADD repairs; the wrong donor fails. The forward oracle places `r` at the synthesized register immediately before its first true reader and restores the original 630 rows. This deliberately supplies information for free and is not a physical repair.

## Cut allowing changed decoding

At chart 1 the original graph starts with no public inputs and ends with 505 independent public target fields. The checked native ingress counts are 323 rank-one, 180 rank-two and two rank-four MOVEs. Deleting either rank-one export leaves 504 incoming scalar fields. Regardless of the order or content of those retained arrivals, a binary transcript of 504 values has at most `2^504` states. A chart-1 decoder with no other initial side information has no way to produce the original 505 independent target bits, which attain `2^505` values. This argument permits arbitrary encodings and arbitrary terminal local decoding, including access to local history. It keeps the contact count and chart endpoints; additional messages, preloaded information or changes to the output domain are outside it.

The executable control confirms that the native target and history ranks are 505, each hybrid chart-1 history and public-output rank is 504, and the union of all changed public outputs with changed chart-1 history has rank 629. The rank observations are finite linear controls; the transcript-count argument gives the stated arbitrary-encoding conclusion on binary fields.

## Fixed-history cheaper ingress exclusion

At an original chart-1 ingress of rank two or four, let `f` be the native
normalized received form. Let `H` contain every chart-1 field observed before
that exact clock and the full preclock native history of every existing chart
whose nested edge to chart 1 has strictly smaller rank. Grant the receiver all
of `H` for free, simultaneously and without charging the donor transfers.
For each of the 182 ingresses, the executable certificate gives a vector `q`
with `q·H = 0` and `q·f = 1`. Hence two original inputs differing by `q` are
indistinguishable from this entire granted stock but require different values
of `f`. No combination of those original-history senders, even with arbitrary
local decoding and unlimited free pooling, can reproduce that receipt at its
original clock. This fixes native preclock source histories and the original
receipt requirement; changed producers, later information or a different
terminal code may escape the screen.

The census covers 180 rank-two and two rank-four original ingresses and checks
21,600 plus 600 donor combinations separately. Rational projector arithmetic
checks all 300 eligible lower-rank source charts against the identity chart.
Each case includes a separating vector, an actually live native-sender
positive control and a deliberately corrupted vector. The full native forward
and reverse operators and all 3,433 private dirty clears are also checked.
For the earliest case at clock 6908, the destination field is `e47 + e328`,
and `q = e47 + e48 + e52 + e58` is one certificate.

## Literal two-contact relay and its displaced output

The original tape sends owner 2326 from 326 to 531 at clock 8072 and sends
owner 2327 from 326 to 1 at clock 8075. On the diagnostic tape, omit the two
source XORs that add native owners 1857 and 2224 to 2326; send the resulting
field to 531 at the original 8072 contact. Create 2327 as a copy of that
field at 531 and use 531 → 1 at clock 8075. The native 2327 receipt is
preserved. Both contacts are nested on the exact rational projectors, and the
second has rank one rather than rank two. This is a literal incomplete
operator, not an admitted supplier.

The displaced residual is the original `x1857 + x2224` at the source. The
replay checks the exact 27 input coordinates in `RELAY.json`. Just before the
first reader at 10137, the original and diagnostic live charts agree and
only owner 2326's field differs. Injecting the residual there restores the
complete live state and, consequently, all 630 public rows and the symbolic
values at all 3,433 private clears. Without that oracle nine named output rows
fail. The actual source and charge of the residual remain unproved.

For the retained old-export contract, the native 2327 receipt and the two
531 → 1 fields at clocks 10138 and 10141 are three independent binary forms.
Chart 531 starts with no public information and has exactly two ingress slots
through 10141. Two binary messages have at most four possible values, whereas
these three independent demands attain eight. Therefore arbitrary recoding of
those two arrivals cannot supply all three original forms; changing one of the
old exports or adding another receipt is outside the argument.

## Conditional price

The binary source inventory is rebuilt from the pinned native graph, its 36 LOCAL calls and the pinned outer caller. Replacing `paid[1]` by `paid[1]-1`, with every other paid and productive count unchanged, is an explicit **hypothetical one-net-rank-one deletion across the complete 36-call word**. The directed log/exp calculation and the distinct integer-root calculation enclose the same raw and 268-factor surplus. With the stated histogram, the surplus is positive and exceeds `2/2^50`; stage and signed-gate controls pass under the retained #8035 numerical positive profile.

This calculation does not show a legal one-net deletion, a compatible 268-factor physical owner schedule, or a replacement for the positive/outer physical proofs. The two literal one-export tapes are singular. The tariff must be recomputed after any additional paid change or altered productive inventory.

A second family keeps the total paid count unchanged and replaces exactly one
rank `r > 1` by `r − 1` in the entire caller histogram. All 13 native paid
ranks above one pass both directed raw and 268-factor checks under the same
unchanged-productive-inventory premise. This is an arithmetic condition, not
a construction of a legal lower-rank destination.
