# Phase 2 independent mathematical review: T29 capacity realization

**Outcome: supports hypothesis `q_b6cf2a2ce15a43ed:e10`.** An independently
derived ten-pattern integer witness realizes the proposed residual profile
with every capacity quota and helper demand exactly. This is an audit of the
historical fixed-U8 inventory relaxation, not a physical owner construction.
No defect in the predecessor claim was found: PR992 explicitly left this
realization question outside its scope.

Reviewer: Astra mathematical/scope reviewer, with substantial OpenAI assistance.
New reviewer material is Apache-2.0. Base:
`ba82555c64e1879e4b7decce28186f208fcb8262`, branch
`contribution/seed69-adversarial-audit`. Only the leader's CLAIM, inherited
sources, and reviewer-owned files were read for this phase; the implementer's
code/artifacts and Gemini's output were not inspected. No solver, producer
module, native replay, or other package checker was imported.

## Source interpretation

- `research/complex-t37-owners/ALL-T-PROOF.md`, fixed-family section: each
  replica has 672 bins of capacity 8 and 448 each of capacities 16, 32, 48;
  each of its nine calls contributes helper counts `(80,32,54,122,216)` at
  widths `(4,5,7,8,9)`.
- `research/complex-t21-owner-bound/PROOF.md`: the per-replica unused mass
  is 14382 and total signed price is -3892. Whole helpers are the units;
  signed dual constraints are necessary and are not asserted sufficient.
- `research/t37-integrality-audit/PROOF.md`, lines 76–80: at T29 the sharp
  relaxation witness is `{1:4,2:1,48:8689}` with zero signed-price slack.
  Its README explicitly excludes bin-type inventory realization.
- Restoring omitted zero ranks gives `2016*29 - (4+1+8689) = 49770`.
  Rank-zero bins still consume a capacity quota. Width demands are multiplied
  by `9*29`, not just by 29. These are bins indexed by an idle child and port,
  not a count of distinct physical families throughout execution.

The four exact source SHA-256 pins are embedded in `review.py` and checked
before calculation. No current selected certificate is used as a floating
input. The base selects PR1042, whose changed supplier is outside this audit.

## Exact proof and independently derived witness

For a bin of capacity C and width-count vector h, let
`sigma = bonus(C) + p.h`, `r = C - w.h`, with inherited
`p=(-1,-20,-8,-2,4)` and bonuses `(2,4,8,-13)`.
By definition `sigma <= u(r)`. The target satisfies

```
sum u(r)*n_r = 4*19 + 13 - 8689*13 = -112868 = -3892*29.
```

The capacity and helper quotas force the actual sum of sigma to the same
number. Consequently all nonnegative bin slacks `u(r)-sigma` must vanish.
This is a necessary equality condition, not an inference that arbitrary
aggregate witnesses are realizable.

An independent reachable-state closure enumerates all 1163 legal patterns,
45 attained ranks, and 22 tight patterns with ranks in `{0,1,2,48}`. Adding
one helper at a time covers every legal vector: removing any present helper
strictly decreases its fill and leaves another legal vector. Duplicate states
are eliminated by their full five-component multiplicity vector. This is
neither the inherited Cartesian product enumeration nor its value-only
unbounded-knapsack recurrence.

A useful elimination identity for hand construction is

```
25*(h9-h7-3*h5) = C-r + 4*(sigma-bonus(C)).
```

It is checked on every legal pattern. A full tight cap-48 bin can be chosen
as `4+8+4*9`; all 8689 rank-48 bins are empty cap-48 bins, leaving 4303 such
full bins. Place each of the 8352 width-5 helpers in a cap-32 bin with three
width-9 helpers. The four rank-one bins use `4+3*9`, and the rank-two bin
uses `3*4+2*9`. Fill the other 4635 cap-32 bins with `2*7+2*9`, leaving
4824 width-7 helpers for cap-16 bins of type `7+9`. The remaining widths
4 and 8 then give the following complete witness, without optimization:

| Capacity | Bin count | h4 | h5 | h7 | h8 | h9 | Residual |
|---|---:|---:|---:|---:|---:|---:|---:|
| 8 | 8285 | 2 | 0 | 0 | 0 | 0 | 0 |
| 8 | 11203 | 0 | 0 | 0 | 1 | 0 | 0 |
| 16 | 4824 | 0 | 0 | 1 | 0 | 1 | 0 |
| 16 | 8168 | 0 | 0 | 0 | 2 | 0 | 0 |
| 32 | 8352 | 0 | 1 | 0 | 0 | 3 | 0 |
| 32 | 4635 | 0 | 0 | 2 | 0 | 2 | 0 |
| 32 | 4 | 1 | 0 | 0 | 0 | 3 | 1 |
| 32 | 1 | 3 | 0 | 0 | 0 | 2 | 2 |
| 48 | 4303 | 1 | 0 | 0 | 1 | 4 | 0 |
| 48 | 8689 | 0 | 0 | 0 | 0 | 0 | 48 |

The exact checked totals are:

- Capacities `(8,16,32,48)`: `(19488,12992,12992,12992)`; 58464 bins.
- Widths `(4,5,7,8,9)`: `(20880,8352,14094,31842,56376)`; 131544 helpers.
- Residuals `{0:49770,1:4,2:1,48:8689}`; mass 417078.
- Total capacity 1403136, used cells 986058, signed price -112868,
  and sum of nonnegative price slacks zero.

In addition to the weighted census, a separate unit-slot oracle expands every
bin and every indivisible helper, fills literal slots in each bin, and counts
unoccupied slots. All three inventories agree. This constructs a packing
in abstract bins only; the slot order has no controller or chart meaning.

## Adversarial controls and executed evidence

Eight invalid witness controls reject at their specified predicates:

1. In one cap-16 bin replace `7+9` by `4+4+4+4`. Capacity, residual profile,
   total bin count, fill and signed price all remain unchanged. The helper
   census changes by `(4,0,-1,0,-1)` and is rejected.
2. Replace three full cap-16 bins, each containing two width-8 helpers, by
   two cap-8 bins and one cap-32 bin, all filled with the same six width-8
   helpers. Residual profile, helper census, total capacity, total bin count,
   mass and signed price remain unchanged. The capacity census changes by
   `(2,-3,1,0)` and is rejected.
3. Omit the empty bins: rejected capacity census.
4. Put a width-9 helper in a cap-8 bin: rejected overflow.
5. Fractional helper: rejected whole-helper domain.
6. Negative multiplicity: rejected multiplicity domain.
7. Boolean multiplicity: rejected multiplicity domain.
8. Unknown capacity: rejected capacity domain.

The first two deliberately pass the implemented weak aggregate checker.
These are invalid-witness controls; they do not prove their residual profile
infeasible, since the valid witness above has that same profile. Reversing
row order and splitting a multiplicity into duplicate rows both preserve
the full valid receipt.

Executed on CPython 3.10.14 (conda-forge, GCC 12.3.0):

```
python -I -B research/t29-capacity-audit/review.py
python -I -O -B research/t29-capacity-audit/review.py
```

Both exited 0 with `PASS_INDEPENDENT_T29_CAPACITY_REVIEW`, all 1163 patterns,
22 target-support tight patterns, eight rejections and two positive controls.
Measured wall times were 0.3853 s and 0.4739 s; these are local observations,
not performance guarantees. Outputs were byte-identical, SHA-256
`de43d59347fb46e60943a98a4d1180c8938ceda249a7fdd7f1f76563caca5e56`.
Temporary receipts were retained in
`/kmh-nfs-ssd-us-mount/code/siri/tmp/t29-astra-review-7to23a8l/`.
Reviewed script SHA-256:
`1bee1e2785567a7fa70d87c0d5a5ff7ca83616a0da2def3a88805b94a418f59c`.

## Narrow overlap refresh and limits

Public GitHub REST checks at 2026-10-13 18:46 UTC:

- Open-PR searches for `T29` and `(8689 OR 49770 OR capacity-tagged)` returned
  zero matches. Search indexing and unpublished work remain limitations.
- The `capacity` + `bin` open-PR search returned five results. The relevant
  recent one was [PR1034](https://github.com/CrocSwap/integer-mult-bounds/pull/1034),
  open at `a1aff126d9816cff75a5293675ae6e10f65377db`, a catalogue-scoped
  mixed-provider separating dual. It does not supply this T29 integer lift.
- [PR992](https://github.com/CrocSwap/integer-mult-bounds/pull/992) is closed,
  head `0efdfc28b1eb71c91c012ca1e1945baeeebce7bb`, and incorporated in the base
  ledger. Its sharpness and credit lattice are predecessor results, not new
  claims here. Credit remains with Chafik Boukhalfa (PR795/890 signed prices),
  Jonathan Capalbo (PR942), and woklerx (PR992).
- The two open issues were #913 (all-size/compiler) and #650 (Discussions).
  No open coordination/claim issue was identified; no pinned coordination
  issue ID was found. No GitHub writes were made.

Conditional on the inherited arithmetic lemma, the witness shows that its
sharp numerator penalty is also attained after imposing these four capacity
and five helper inventories. No logarithm/moment engine needed rerunning.
Chronology, invocation-specific matching, geometry, family nonaliasing, native
semantics, finite invoice, physical feasibility, a new kappa and the changed
PR1042 family remain excluded. This phase does not review the implementer's
final package; that review awaits explicit integration authorization.

## Authorized integration review (after the blind phase)

**Disposition: mathematical witness passes; actionable corrections required
before publication acceptance.** This section is post-hoc integration review,
not evidence that the reviewer or implementer remained blind after phase 2.
The preceding witness, commands and script hash retain their historical meaning.
The reviewer script now accepts `--witness PATH` for this separate phase.

The producer's ten-pattern witness differs from the blind witness: all 12992
cap-16 bins use `7+9`, versus 4824 in the blind construction. Passing that
actual JSON through the reviewer's independent census and full unit-slot
oracle gives exactly the same four capacity quotas, five helper demands,
four residual counts and zero signed-price slack. The full 45-entry `u`
table and every one of the 22 tight patterns match the independent reachable
closure. Consequently Lemmas 1 and 2 and the explicit existence proposition
are supported. The interval in Lemma 2 is a necessary interval only.

### Required corrections

1. **Unsupported inference, PROOF.md lines 112–113.** A necessary range of
   8169 integer values does not prove all or many of them feasible. Replace
   the justification for "far from unique" with the two independently
   checked explicit witnesses, claiming simply nonuniqueness, or supply
   a construction for additional values. No such range construction was
   established in this review.
2. **Incorrect control description, README.md lines 49–51 and the inventory
   control comment in verify.py.** Of the seven inventory mutations,
   `retag_empty_48_to_full_48_changes_profile` changes residual mass by -48;
   it does not preserve aggregate rank mass. The first four preserve residual
   mass, dual credit and actual signed price. The untight rank-one mutation
   preserves mass and dual credit but changes actual signed price by -25.
   The missing-bin mutation preserves mass and credit but reduces bin count.
   Describe these separate controls accurately; asserting that all seven
   preserve mass is false. The existing rejections themselves work.
3. **Unchecked witness metadata on regeneration, verify.py certificate().**
   `WITNESS.json.remainder_profile` is not compared with `PROFILE` or the
   counted witness. In an isolated copy I changed its rank-zero count to 1:
   default verification rejected the stale file hash, but `--write NEW_PATH`
   still returned PASS and generated a receipt containing the contradictory
   witness hash. Add an explicit declared-profile check and a control that
   reaches it. The actual packing is checked against the correct hardcoded
   profile, so this is a semantic metadata binding gap, not a false packing
   or a counterexample to H.
4. **Minor independence wording, README.md lines 38–39.** The producer uses
   one Cartesian pattern enumeration and an independent maximum-price DP.
   The DP reconstructs `u(r)`; it does not enumerate or count all 1163
   multiplicity vectors. State those two tasks precisely. The reviewer
   separately does enumerate every vector by reachable-state closure.

### Executed integration evidence

```
python -I -O -B research/t29-capacity-audit/review.py \
  --witness research/t29-capacity-audit/WITNESS.json
```

Independent witness, all-slot and tight-class comparison passed in 0.8368 s.
All five SOURCES pins match both working files and `git show` at the recorded
base. Source attribution in README is consistent with the predecessor roles;
no independent human review is claimed.

A minimal checkout at `/tmp/t29-final-review-9rhqj5pl/checkout with spaces/`
contains only the six producer files and the five pinned predecessor files.
From an unrelated working directory, `python -I -O -B` passes with both
default root detection and explicit `--repository ROOT`; each reports all
21 producer controls. Fresh `--write` regenerates an equal EXPECTED object.
An existing output is refused and its bytes remain unchanged. Stale EXPECTED,
malformed witness JSON, changed witness count, corrupt/missing source files,
and malformed SOURCES all fail nonzero under `-O`. Malformed JSON produces
a traceback rather than a formatted Reject diagnostic, but fails closed.
The false-profile default/re-generation distinction is recorded above.

Post-blind instrumentation captured the producer's actual seven inventory
mutations and independently recomputed their invariants using reviewer code:

| Mutation | Delta bins | Delta residual mass | Delta dual credit | Delta actual signed price |
|---|---:|---:|---:|---:|
| cap16 7+9 to 8+8 | 0 | 0 | 0 | 0 |
| cap32 9+9+9+5 to 9+9+7+7 | 0 | 0 | 0 | 0 |
| rank2 alternative | 0 | 0 | 0 | 0 |
| full cap8 to full cap16 | 0 | 0 | 0 | 0 |
| empty cap48 to full cap48 | 0 | -48 | 0 | 13 |
| rank1 untight pattern | 0 | 0 | 0 | -25 |
| one bin short | -1 | 0 | 0 | 0 |

Here dual credit means `sum (48*u(r)+13*r)*n_r`; it is distinct from
actual signed bin price. The positive- and negative-slack profile controls
also have the claimed common bin count and mass, with signed-price slacks
+25 and -50. These are deliberately rejected by the zero-slack theorem's
admission predicate, not assertions that every positive-slack profile is
physically infeasible.

Commands, exit codes, timings, invariant deltas and reviewed producer hashes
are preserved in `FINAL-REVIEW.json`. Scratch logs are under the temporary
directory above. Only reviewer-owned files were changed. The feasibility
result remains accepted mathematically; publication acceptance awaits the
listed corrections and their focused recheck.


## Narrow post-fix review: R1–R4 resolved

**ACCEPTED for publication of this scoped capacity-tagged packing audit.**
This section appends to, and does not replace, the original findings. The
original `FINAL-REVIEW.json` is preserved unchanged. This is AI review,
not an independent human review or a new physical-feasibility claim.

- **R1 resolved.** PROOF and README now claim nonuniqueness from two explicit
  checked realizations only. The necessary interval is labelled necessary;
  no interpolation or full-range feasibility is claimed. `SECOND_WITNESS`
  was compared entry for entry with the reviewer's original blind witness
  and agrees exactly. The producer and blind realizations differ in eight
  pattern counts, as stated.
- **R2 resolved.** The receipt and README now distinguish changes to bin
  count, residual mass, dual credit and actual signed price. The actual
  producer's seven mutations were captured and all four aggregate deltas,
  as well as their capacity/helper/profile inventory differences, were
  recomputed using reviewer code. Every recorded value agrees. In
  particular, the empty cap-48 replacement changes mass by -48 and signed
  price by +13; the untight rank-one replacement changes price by -25;
  removing a full cap-8 bin changes bin count by -1.
- **R3 resolved.** `admit_document` checks the actual packing census and then
  validates the declared profile before `certificate` returns, so both
  default comparison and fresh `--write` require semantic agreement. The
  profile requires canonical decimal keys and positive integer counts,
  explicitly excluding booleans. An isolated checkout with spaces was
  tested under `-I -O -B`: a false zero-rank count, missing profile, boolean
  count and noncanonical key each reject in both modes with the specific
  profile diagnostic, empty stdout, and no output file created by `--write`.
- **R4 resolved.** Documentation and code descriptions now correctly state
  one Cartesian enumeration of legal patterns and an independent
  maximum-price dynamic program reconstructing `u(r)`.

The relocated baseline passes all **31** controls with two realizations,
1163 patterns and 58464 bins. Explicit `--repository` also passes. A fresh
write is byte-identical to the committed EXPECTED.json. Commands, exit codes,
diagnostics, timings and exact reviewed hashes are in `POSTFIX-REVIEW.json`;
scratch evidence is `/tmp/t29-postfix-review-a6_slr_a/`. Typical individual
CLI runs took 0.23–0.25 seconds on the same Python 3.10.14 interpreter.

Before this append, WITNESS.json, SOURCES.json, review.py, REVIEW.md and
CLAIM.json matched their original reviewed hashes. All five predecessor
source pins still match. FINAL-REVIEW.json still has SHA-256
`73c73cc89f822d90f30ff1cc88e1dcc8f21a405a9d0d380a0409640705c25027`.
The unchanged `u`, quotas, demands, profile, mass and other mathematical
receipt fields were compared with the earlier snapshot; the unchanged
full mathematical derivation was not rerun.

CLAIM.json still scopes the result to the historical PR992/U8 capacity-tagged
integer realization and excludes chronology, geometry, physical scheduling,
new kappa and PR1042's changed supplier. OVERLAP.json is a dated keyword/body
review, explicitly limited rather than a guarantee of novelty; its PR1129
comparison distinguishes the changed R480 supplier from this fixed-U8
question. Those coordination records were reviewed, not modified. Attribution
and the distinction between blind derivation and later transcription are
retained. No remaining actionable finding was identified in this narrow
re-review. Only this append and POSTFIX-REVIEW.json were written.
