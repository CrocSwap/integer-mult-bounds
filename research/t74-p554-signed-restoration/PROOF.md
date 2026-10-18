# Signed-restoration kernel at pivot 554

## Statement and boundary

Fix the two raw words in Marius-Paul Dumitrean's PR1625, commit
`62092e96d2cb8f5751ce7d81b1ca774a0dd3827f`. Apply `RECIPE.json` to each.
The complete linear map of **B followed by its chronological early cleanup**
is unchanged over the rationals on all 704 arbitrary input registers. The
remaining cleanup and all other interfaces are unchanged. Every inherited
local frame/cone test accepts the new words. Their paid local child histograms
both change by H1 +1, H2 -2, H3 +1, with unchanged rank mass, child count and
ordered residual widths.

This is a finite exact construction at this boundary, not a proof of an
unconditional multiplication theorem. The complete T74 admission is separately
replayed by `replay_full.py`. Its numerical result must not be inferred from a
local scalar identity alone.

## Literal chronological replacement

All B positions below refer to the original PR1625 word, starting at zero.
Write q for register 554 and d for its arbitrary value at B entry. Delete
B342, `482 -= q`. Insert the following before the indicated original gates:

| Position | Inserted operations, in chronological order |
|---|---|
| B0 | `584 += 2*q`; `126 += q`; `186 -= q` |
| B38 | `584 -= 2*q` |
| B517 | `74 -= q` |
| early-cleanup position 84 | `74 -= q` |

Thus six actual ADDs replace one ADD. No added operation, correction or
restoration is free. No helper is allocated or reset. In particular, register
584 starts arbitrarily dirty and is not assumed zero. The frozen frame delta
is explicit: new B positions 0,1,2,41 use frame [24], new B520 uses
[419,67,24], and the inserted tail operation uses
[256,128,64,32,24,4,2,1]. All pre-existing frame annotations are retained.

The first five inserted reads see q=d. Immediately before the last inserted
read, the original early cleanup has instead made q=-d, with no contribution
from any other entry register. The verifier checks these six *row identities*
over Q, not just the value obtained from one numerical input.

Consequently the last operation's coefficient is **minus one**, just as at
B517. Replacing that final coefficient with plus one is not a restoration.
The repeated minus signs do not mean that all intermediate operations cancel:
the unchanged intervening word consumes the modified registers. The exact
comparison below is essential.

## Exact certificate and why all input dirt is covered

For an ADD `t += c*s`, the checker left-multiplies the current transformation
matrix by `I+c e_t e_s^T`; for SCALE it multiplies row t by its stated nonzero
rational factor. It starts at I_704 and executes every B operation and every
listed early-cleanup operation in the stored order. It compares the complete
old and new matrices, including every DATA and helper output. Equality of
these rational matrices proves equality for all 704-component inputs over any
Q-module, not just for clean helpers or random samples. The remaining cleanup
is compared literally and is the same continuation. A, cut, precondition,
ports, centers, center frames, entrance and terminal dictionaries, scatter and
target levels are unchanged.

A separate retained checker (`vendor/audit_local.py`, icekylinx/PR645 lineage)
reconstructs the full dirty compensation and verifies the complete forward
and dual maps, all 704 columns, dyadic coefficients, monotone frame climbs,
center interfaces, wrapper exclusions and terminal row/column cones. It is
used unchanged, with its attribution retained. It is separate from the
modular search and the substitution implementation, but no independent human
review or proof-assistant formalization is claimed.

The all-column matrix comparison is a finite exact certificate, not an
extrapolation from sampled widths. The compiler's passage from these legal
finite words to the all-size physical algorithm remains an inherited premise.

## Search class and departure from the predecessor's negative screens

The initial positive-restoration search assumed a pivot's returned row was
+d. It could recover PR1625's pivot566 kernel, but its one-write screen of
98 nominated pivots produced no new feasible gain: 46 algebraic models failed
frame pricing. That is a bounded search result only.

The evidence-driven revision admits a returned row lambda*d for a nonzero
dyadic lambda, adjusting the closing coefficient accordingly. The winning
lambda is -1. This is a changed restoration mechanism, not merely another seed
or a larger run of the previously closed single-hook class. PR1625 explicitly
lists pivot554 as an unsuccessful prior lead and asks about other written
cold pivots; the signed boundary is the distinction here.

The proposer transports a desired column difference through the inverse
unchanged prefix, and seeks up to two restored helper-window terms plus at
most two direct DATA corrections. It works modulo 2147483629 only to nominate
candidates; no modular equality is accepted as a rational proof. Coefficients
are restricted to +/- {1/4,1/2,1,2,4,8}; the direct-correction branch, candidates
and frame-pricing counts are bounded as recorded in SEARCH.json. At pivot554,
132 models were nominated, the first five were priced, and the fifth was the
first strict gain. The search stopped there. Neither exhaustive all-pivot
coverage, frame optimality nor a global lower bound is asserted.

## Complete paid profile and analytic direction

Including the eight rank-eight center children, the new local histograms are:

- base: {1:2348, 2:500, 3:416, 4:130, 5:82, 8:8};
- extra: {1:2340, 2:508, 3:420, 4:126, 5:82, 8:8}.

PR1319's T74 owner table, 249 base / 417 extra dispatch, 666 complete calls,
319680 helper roles, source-event chronology, actual pending axes, and idle
H48=22748 are retained. Combining the actual new local histograms with that
unchanged dispatch gives:

{1:1560432, 2:336336, 3:278724, 4:84912, 5:54612, 8:5328, 48:22748}.

Its rank mass is 4816512 = 73*66304 - 23680. The maximum child rank stays 48.
For 0<a<1 the paid normalized complex moment is

    F(a) = sum_r H_r * r/(73*66304) * (73/r)^a.

Its change from PR1625 is

    666 * 73^(a-1)/66304 * (1 + 3^(1-a) - 2*2^(1-a)) < 0,

by strict concavity of x^(1-a). This proves the direction of the child-budget
gain throughout the relevant interval, not its implementation or a numeric
kappa by itself. There are five more scalar ADDs per invocation, hence 3330
more over the entire dispatch. The native lowering and finite invoice must
charge these additions, their transports, every existing source access,
frame movement, dirty compensation, restoration, center operation, residual
adapter, recursive child, coefficient workspace and final correction.

No costs are subtracted for the unused output of a completed wrapper. No
cross-family axis move, source identification or disposable workspace is used.
The retained T74 precision charge is 2048 bits, not the insufficient old T37
1024-bit charge. The complete replay recomputes the physical prefix and row
bill and rejects undercharging. The bit supplier, stopped recurrence/ordinary
bootstrap and all 47 strict outer inequalities are then checked by the
unchanged PR1319 admission engines; no headline gains are added together.

## Failure controls and limitations

The local check rejects each omitted new B gate, omitted tail restoration,
wrong closing sign, prematurely scheduled tail, retaining the deleted old
read, a too-small new frame, and a missing recursive child charge, for both
providers. Tests also exercise source/certificate corruption and overwrite
protection. Full T74 controls remain separate and are counted only after the
actual replay succeeds.

Native and local checks are finite obligations. Inherited assumptions include
all-size compilation, common labels and mutable-source realization, complete
correlated-dirty whole-call hosting, precision and tape simulation, exact
recovery, analytic transfer, PR559 recurrence correction and PR589 H1-H5.
Neither selected-frontier adoption, unconditional multiplication, practical
speedup, proof-assistant certification nor global optimality follows here.
