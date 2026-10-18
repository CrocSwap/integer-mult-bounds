# Reusing the theorem library

The main contribution is a set of sufficient reusable interfaces for future
workers. There are 76 named theorem APIs in the three new modules and 11 retained
APIs from PR2260, all assembled in the38KiB standalone `Toolkit.lean`.
These counts include algebraic helper facts and extensions of retained results;
they are not a count of novel mathematical discoveries. All 87 theorems and 19
supporting definitions pass a fresh independent kernel/transitive-axiom audit.

## Start with one file

Copy `Toolkit.lean` into a compatible Mathlib project and run `lake env lean
Toolkit.lean`. It imports Mathlib only and needs none of the Python data or the
contributor's personal library. Lean 4.33.0/Mathlib v4.33.0 is the checked context.
Use either the standalone file or the individual modules: importing both would
redeclare the same constants. The three new individual modules are independently
self-contained and can be imported together. `build_toolkit.py --check` checks
the exact standalone assembly against the parts.

For a fresh full dependency audit, from a Mathlib checkout use:

```sh
lake env python3 /path/to/kappa-lemma-toolkit/audit_lean.py --out /unused/external/audit
```

This elaborates all source bodies and independently collects transitive axioms
for every theorem and definition. It permits only `propext`, `Classical.choice`
and `Quot.sound`. `LEAN-AUDIT.json` records the already completed source-bound
check. The Python supplier replay does not rerun Lean or turn that receipt into
an unconditional multiplication theorem.

## Which interface to use

| Work item | Useful theorem(s) | What must still be supplied |
|---|---|---|
| Native inverse or sign reversal | `IntegerKappa.Native.inverseStep_left`, `inverseStep_right`, `inverseStep_sign_wrapper` | Actual involutive address/character and cost of its implementation |
| Move an operator through a chart | `step_natural`, `step_chart_conjugation`, `step_monomial_natural`, `step_monomial_anticommuting` | Literal address map and phase condition; the anticommuting formula retains its factor i |
| Accumulate between different encoded data frames | `framed_add_decode`, `framedKernel_comp` | Actual source/target equivalences and typed adapter, priced as part of the program |
| Borrow an arbitrary dirty relay | `dirty_relay_restoration`, `framed_dirty_relay_restoration` | Complete chronological cleanup; no helper is assumed initially zero |
| Reorder pending Gaussian factors | `familyWord_perm` | A permutation retaining literal physical family and axis, plus untouched windows and chart witnesses |
| Bound exact recursive temporary grids | `IntegerMultBounds.Recursion.linear_bound_of_stopped_recursion`, `exact_grid_linear_bound` | Actual completed-child recurrence, proper child ranks, leaf bound and fixed nonchild work charge |
| Combine disjoint selected-axis blocks | `partition_linear_bound`, `layer_excess_bound`, `standard_C0_guard`, `common_grid_sufficient` | Actual axis-size sum and a strict positive-dimension reserve |
| Bound active recursion depth | `child_lt`, `descent_terminates`, `descent_scaled_bound`, `descent_eq_zero_of_scaled_lt` | A proper shrinking child; sibling work remains separately charged |
| Reach a new ordinary saving | `bootstrap_gap`, `bootstrap_target_of_power_bound`, `bootstrap_eventually_always_above` | The retained completed ordinary interface and actual finite constants at each stage |
| Replace a paid subprofile | `IntegerMultBounds.MomentTransfer.replacement_nonneg`, `admission_of_replacement`, `admission_with_reserve` | Nonnegative integer inventory and a cost comparison; physical validity is separate |
| Certify rational upper bounds on analytic costs | `rational_upper_certificate`, `normalized_admission` | Actual pointwise rational enclosures, nonnegative counts and strict rational sum bound |
| Concentrate residual ranks | `rpow_concentration`, `normalized_rpow_concentration`, `admission_of_batch_concentration` | For each accounted pair0<=d<=a<=b, exponent0<=p<=1, and a valid final physical placement |

Names in the native rows live in `IntegerKappa.Native`; recursion names live in
`IntegerMultBounds.Recursion`; moment names live in
`IntegerMultBounds.MomentTransfer`. Exact signatures and all supporting facts are
listed in `LEMMA-INDEX.json` and the three accompanying proof guides.

## Three concrete uses

For residual ranks(7,39)->(6,40), instantiate concentration with d=1 and
p=1-saving. It proves the moment comparison for every saving in[0,1], including
the zero-rank endpoint case handled by the general theorem. It does not prove
that these two physical owners may be exchanged. Check their families, windows,
capacity, source exclusion, normalized axes and full endpoint action separately.
A finite batch must account for the actual resulting profile: do not sum several
changes to the same bin as though they were independent simultaneous pairs.

For exact grids, take C=2(s+E), stop>=m and r(e)<m. The theorem supports arbitrary
integer e and its floor quotient, including tails and a larger stopping rule.
It bounds the single active child's temporary excess instead of concatenating
all sibling temporary peaks. Actual scalar/Horner and nonchild charges must be
included in E; a completed child boundary is essential.

For data updates with source chart A and target chart B, use the explicit
adapter B*U*A^(-1) before accumulating c times the result. `framed_add_decode`
then proves y+c*U*x for every x,y. The common-frame specialization does not
identify two distinct charts. This addresses exactly the kind of false bare
ADD inference exposed by PR #2252.

## Discovery and reuse

Discovery included bounded queries across registered source catalogs and the
shared DAG, plus the previous Gaussian/family, exact-grid, moment-certificate
and Problem 1.8 modules. Source-only hits were not proof evidence. The actual
checked dependencies include Mathlib's `Real.concaveOn_rpow`, natural division
and strong induction, finite sums, Archimedean power decay, complex arithmetic
and linear equivalences. The existing public Factors/Feedback APIs are retained;
the native module extends their phase-sensitive algebra. No incompatible
historical environment or personal Mathproof import is required. The Problem 1.8
collision recurrence was inspected and found to have a different mathematical
scope; it is not presented as a proof of this exact-grid recurrence.
