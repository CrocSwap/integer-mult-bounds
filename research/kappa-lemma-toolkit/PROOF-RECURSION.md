# Exact-grid recursion and exponent bootstrap

`Recursion.lean` supplies 24 universal sufficient theorems and two explicit
recurrence definitions. All imports are Mathlib; namespace
`IntegerMultBounds.Recursion`. No private project module is required.

## Active-child temporary exponents

The principal theorem `linear_bound_of_stopped_recursion` accepts arbitrary
natural widths, a stopping threshold `stop>=m>0`, a variable proper child rank
`r(e)<m`, and a cost or exact-grid exponent `A`. Its hypotheses are:

```
A(e) <= C*e                                  when e<stop,
A(e) <= A(r(e)*floor(e/m))+s*floor(e/m)+E      when stop<=e,
C*r(e)+s+E <= C*m                            at every e.
```

It proves `A(e)<=C*e` for every natural e. Proper rank gives strict progress
without discarding tails; the nonleaf quotient is at least one, so the fixed E
charge is absorbed. Strong induction follows the one active child's temporary
excess, rather than multiplying that excess by the number of completed siblings.
`child_le`, `child_lt`, `child_eq_zero_of_lt`, and `quotient_budget` expose these
interfaces for other schedules. The rank function may vary with actual width.

`standard_rank_budget` proves the required budget automatically for
`C=2*(s+E)` at every proper rank. `exact_grid_linear_bound` then combines the
retained leaf estimate `A(e)<=8e` and `s+E>=8`, giving
`A(e)<=2*(s+E)*e`. This is a theorem about any function satisfying the explicit
recurrence; it does not assert that a new child implementation meets it.

## Whole-layer and stopping assembly

`partition_linear_bound` adds independently bounded excesses over any finite
family whose actual selected widths sum to at most d. `layer_excess_bound`
then adds an arbitrary outer allowance, producing `(2B+outer)*d`.
`standard_C0_guard` proves `2B+18<32*m*B^2` for `m>=1,B>=8`, and
`common_grid_sufficient` turns any strict coefficient reserve into a strict
all-positive-dimension bound. Thus the traditional common grid is a checked
consequence of the recurrence and finite partition hypotheses, including
arbitrary selected-axis tails.

`descent` explicitly iterates an active width map. `descent_le_sub` and
`descent_terminates` prove finite depth for any map fixing zero and strictly
reducing every positive width. For the floor-rank child,
`descent_scaled_bound` proves

```
m^n * descent(r*floor(-/m),e,n) <= r^n * e.
```

`descent_eq_zero_of_scaled_lt` turns the checkable inequality
`r^n*e<m^n` into a sufficient stopping certificate. The proof does not require
divisible widths, an approximate real logarithm, or an unproved convergence
heuristic. Combining the short-tail and strict-child lemmas with the generic
termination theorem also gives the coarse depth-e bound for any proper rank.

## Exponent bootstrap

`bootstrap s a 0=a` and
`bootstrap s a (n+1)=(1-s)*s+s*bootstrap s a n`.
`bootstrap_gap` proves the exact closed form

```
s-bootstrap(s,a,n) = s^n*(s-a).
```

`bootstrap_le`, `bootstrap_lt`, and `bootstrap_nonnegative` preserve the
relevant exponent interval. `bootstrap_strict_progress` gives strict stage
improvement when `0<s<1` and `a<s`. `bootstrap_monotone` supports comparison of
arbitrary stage indices. `bootstrap_target_of_power_bound` converts an exact
power estimate into a finite target certificate.
`bootstrap_eventually_above` proves every target strictly below s is reached
in finitely many stages; `bootstrap_eventually_always_above` proves it remains
reached thereafter. This replaces a fixed number of sampled bootstrap rounds
with universal sufficient reachability. It does not supply a numerical input
cutoff or bound the sequential implementation constants. Any explicit cutoff
must separately dominate those constants; an example logarithmic constant512
cannot be asserted to do so automatically.

## Provenance and evidence

The active-depth interface is extracted from the retained exact Gaussian-dyadic
completed-child argument, including grouped variable widths, in RaD commit
`45d9b60355872041f9275f77c057514def0d45bc`, reports
`review-semantic-child-guard.md` and `review-whole-complex-transfer.md`.
Those reports retain the original CrocSwap manuscript interface and authorship.
This file provides fresh Lean proofs of the stated algebraic sufficient
conditions; it does not repackage their informal proof as kernel evidence.
The standard Mathlib finite-sum, natural-division, ordered arithmetic, and
Archimedean power lemmas are reused directly.

Discovery used bounded registered source-library lexical queries for
`recurrence` and `active depth`, a typed-DAG `IntegerKappa` query, and inspection
of existing feedback and Problem1.8 collision-recursion modules. The registered
query produced unrelated source-only hits; the typed query returned no matching
operations. The Problem1.8 module concerns ideal-component collision descent,
so it was not imported or claimed as this arithmetic recurrence proof. This is
not a claim of exhaustive semantic search over the entire DAG.

All 24 named theorems and both definitions require fresh kernel elaboration and
transitive axiom inspection. Allowed foundational dependencies are only
`propext`, `Classical.choice`, and `Quot.sound`; no unproved assumptions or
personal Lean imports are added. The companion audit receipt binds the exact
published source hash. These lemmas support admission of future finite words;
they alone do not establish a Turing-machine implementation, an analytic
transfer theorem, or a new multiplication exponent.
