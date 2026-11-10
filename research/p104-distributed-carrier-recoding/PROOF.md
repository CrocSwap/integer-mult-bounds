# Scope and necessary-condition argument

This is a finite, source-bound obstruction to one restricted native rewrite.
It does not prove a new multiplication bound, optimize the native word globally,
or prohibit simultaneous changes of several transport intervals.

## Precisely allowed rewrite

Choose one arbitrary **public helper** (public, excluding both actual main role
sets `live` and `live+112`) and two consecutive MOVE instructions
`A -> B -> C`. Between them, every instruction writing that helper is a SCALE.
There must be at least one ADD reading the helper in that interval; the replay
asserts that no COPY is among the removed exports on either pinned input.
All those reads are removed. The two MOVEs are replaced by one `A -> C` MOVE,
placed at any cut in the maximal unchanged-value residence that preserves all
retained A and C reads. Original SCALE instructions on the helper are placed
at its held frame; their scalar action stays the same. Here cut t means before
source instruction t, with cut len(program) at the end.

Write i and j for the old first and second MOVE indices. Let lo be one cut
after the last preceding non-SCALE write or MOVE of this helper (or 0), and hi
the index of its first following non-SCALE write or MOVE (or len(program)).
The exact bounds are

```
move_lo = max({lo} union {s+1 : lo <= s < i and s is a retained helper read})
move_hi = min({hi} union {s   : j < s < hi and s is a retained helper read})
```

Every fused MOVE cut t with move_lo <= t <= move_hi is admitted. Injections at
A can occur from lo through t; injections at C can occur from t through hi.
Thus the fused MOVE may precede the old first MOVE or follow the old second
MOVE when retained source reads permit it. The old A reads remain before it;
the old C reads remain after it. Moving beyond these bounds would require
removing additional A/C exports or changing their schedule, which is excluded.

The replacement may add any finite number of dyadic ADDs **from this helper**
to any other public or live owned register at the same frame. Before the fused
MOVE that frame is A; afterwards it is C. These injections may extend backwards
through the immediately preceding A residence and forwards through the
immediately following C residence, stopping at the first other write or MOVE
of the helper. Existing SCALEs are allowed throughout those extensions.
Recipients, existing scalar instructions, and all other transports retain their
source schedule. Injections into the held helper itself are excluded.

An arbitrary ordinary correction using the public output bank at frame 127 is
allowed. Its implementability and invertibility are **relaxed away** in the
screen: no condition at all is imposed on those final output rows. Every other
public output must retain its exact old-input map, and the destination of every
future COPY must remain zero immediately before that COPY. Dirty erasure of
owned fields imposes no extra final constraint.

The test does not allow a new initial basis correction, a changed scalar write
to the held helper, a new carrier transport, a new independent input, an extra
retirement, non-dyadic coefficients, or a coupled change to another interval.
Those changes are outside this result. Local exploratory incoming-contact
pilots are not part of this obstruction.

## Why a suffix-column span is necessary

Write the actual held helper row at the first MOVE as `v`, a row on all old
independent public input coordinates. Throughout the permitted residence it
is `a(t) v`, where `a(t)` is the product of the retained SCALE factors (or its
inverse when comparing an earlier cut). No injected recipient feeds back into
the helper within this residence: by construction the helper has no other
write there.

Let `S(t,r)` be the column of the unchanged scalar suffix taking an additive
perturbation of register r at cut t to the constrained observations: all final
public rows outside frame 127, together with every zero-before-COPY observable.
Deleting the intermediate exports changes those observations by `-D v`, where
D is the sum of their suffix columns times their export and SCALE coefficients.
Adding the allowed injections changes them by

`sum_j b_j a(t_j) S(t_j,r_j) v`.

The value v is not identically zero. Therefore preservation on **every old
independent input** requires

`D = sum_j b_j a(t_j) S(t_j,r_j)`.

This argument allows arbitrarily many injections; no sparsity or one/two-term
bound is imposed. A successful span test is only a nomination. It does not
establish legal dyadic coefficients, full-frame output repair, absolute native
phases or a profitable complete invoice.

For a COPY, the backward computation treats COPY as an ADD and adds the
pre-COPY destination as a separate observable. On perturbations for which that
observable vanishes, this agrees exactly with overwriting a known-zero
owned destination. INIT and CLEAR kill the preceding suffix column. Thus dirty
erasure is allowed, while the actual COPY monitor is retained.

## Why reduction modulo 65521 is sound for this exclusion

All source and proposed coefficients are dyadic rationals. The homomorphism
`Z[1/2] -> F_65521` exists because 2 is nonzero in this field. The replay checks
that every source SCALE is a nonzero unit modulo 65521 and that each nominated
held old-input row v is nonzero modulo 65521. It also checks the entire pinned
source endpoint and every source COPY-zero condition modulo the same prime.
Consequently an allowed exact dyadic rewrite would induce a solution to the
finite-field span equation above. Failure of that equation excludes the
allowed exact dyadic rewrite.

This does **not** exclude arbitrary rational coefficients with denominator
divisible by 65521. No conclusion about that larger coefficient ring is claimed.
The field computations are exact modular arithmetic, not floating estimates.
The displayed transport ranks are diagnostic only and play no role in rejection.

## Chronological coverage

A suffix column of a recipient changes only when an instruction touches that
register as a source or destination; its current frame also changes only at a
touch. The reverse sweep records every resulting constant-column, constant-frame
residence segment and intersects it with every eligible helper interval.
For an A injection, the earliest feasible cut in a segment is retained. For a
C injection, the latest is retained. Since the held source differs only by a
nonzero SCALE factor, moving within such a segment changes only its permitted
coefficient, not membership in the available finite-field span.

For each helper interval, the search checks both end cuts and every retained
injection cut. At a retained cut, A injections at that cut can precede the
fused MOVE and C injections at that cut can follow it. Between two successive
retained cuts the available column set is contained in a set checked at an
endpoint. Thus the finite set of checked systems covers every legal placement
of the fused MOVE under the stated schedule.

## Recorded result and calibration

On #6702's exact native word, all **631** eligible helper intervals fail,
across **2,387** chronological systems. There are 200 constrained final public
rows and the one actual COPY-zero monitor. The largest encountered response
rank is 23. Of the 631 intervals, 629 have at least one available nonzero carrier
response. All 631 held rows are nonzero modulo 65521.

The identical algorithm, with only its pinned input bytes changed, nominates
exactly the two recorded #6529 scaled-fusion patterns on the earlier #6453 word:
helper 336 at cut 9048 into owned register 781, and helper 368 at cut 9101 into
owned register 782, each with modular coefficient 1. The published SPEC gives
these exact source event indices and injections. Those constructions retain
#6529's credit; they are positive controls for the broader span search. This
package verifies the event bindings and literal injections against the retained
SPEC; it does not re-audit the predecessor's full-output cleanup construction.

A second agent independently checked the expanded primary domain using
unnormalized max-pivot cross multiplication and cuts at each threshold and its
neighbors: 4,263 systems, maximum rank 23, no hits. That check deliberately
reuses this package's reviewed suffix/residence generator; it is an independent
elimination and boundary cross-check, not a second complete response generator.
The separate review package records its implementation and source pin.

The first exploratory current-word pilot used numeric helper IDs >=224 and
covered 621 intervals. That restriction omitted auxiliary helpers in unused
main-register slots. The final replay uses the actual role predicate and adds
the ten eligible omitted intervals; none is a nomination. No source-wide claim
uses the narrower pilot count.

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI Codex assistance.
Apache-2.0. Independent mathematical review remains separately recorded.
