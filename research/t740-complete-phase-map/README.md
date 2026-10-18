# The complete T740 residual-phase map is injective

For the pinned T740 owner-0/port-0 word, the complete eight-stream operator
determines all **20 nonzero residual phase multipliers separately**. This
includes the 12 children whose current residual rank is zero. Hosted prefixes,
translations, stream charts and event order are fixed throughout.

This closes the coupled residual-site question left by
[PR3272](https://github.com/CrocSwap/integer-mult-bounds/pull/3272), whose
five-site calculation fixed the other children. The new result classifies
equality between any two residual-phase assignments on this whole word. It
does not merely test more rank allocations or add one donor to a finite census.

## Exact statement and consequence

Fix a character `x` of the 73-dimensional binary source space. Let `M_x(z)`
be the normalized eight-stream operator after multiplying the residual phase
of child `j` by `z_j`, for all `j=0,...,19`. The inherited completed-call model
and all other physical events are unchanged. Then

```text
z, w in (C*)^20:  M_x(z) = M_x(w)  if and only if  z = w.
```

The proof recovers all 20 variables successively from 20 matrix entries and
one known ambient phase. Every denominator is a product of nonzero input
phases. The exact symbolic matrix retains the full character dependence;
checking a few characters or fourth-root assignments is not the proof.
[PROOF.md](PROOF.md) gives the recovery identities and their source boundary.

Applying this statement at every character forces each residual phase
function to remain unchanged in any operator-preserving replacement. For an
independent binary family of `r` residual axes, its phase function has squared
mean magnitude `2^-r`. Hence each residual rank is fixed separately. For
replacements whose combined hosted-plus-residual bases remain independent,
each full child rank is fixed too. In particular, opening an initially empty
residual site cannot be compensated by simultaneous residual changes elsewhere
in this fixed word.

This is phase-function uniqueness, not uniqueness of the literal axes.
Different orthonormal bases can represent the same phase function. Dependent
axis lists also fall outside the rank consequence: four repetitions of one
axis give a trivial phase despite nonzero list length.

## Sources and independent checking

[SOURCES.json](SOURCES.json) pins the unchanged canonical provider/fill,
exchange journal, allocation, plan/template, port recipes and source helper.
The primary checker authenticates the source closure before using the
predecessor's complete fill/context checks, then derives the new symbolic
matrix and inverse identities. The independent checker reconstructs the
context directly from authenticated JSON without importing the primary or
predecessor executables. Neither checker depends on an unmerged package.

[RESULT.json](RESULT.json) is the complete deterministic receipt and
[VERIFY.json](VERIFY.json) registers both derivations and behavioral controls.
From the repository root, with standard-library Python 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/t740-complete-phase-map
```

The complete registered replay passes on CPython 3.12.15 / Linux x86_64.
Both implementations agree on all 72 matrix terms and the 20 recovered
coordinates; the independent certificate checks 21 divisions. Eight control
groups pass in isolated optimized mode, covering quadratic character terms,
missing hosted/bridge actions, source and polynomial corruption, zero phases,
exact nontrivial specializations, a distinct equal-phase basis and an actual
rank-changing mutation. One of these controls compares simultaneous changes at
all 20 sites with the frozen numerical source replay at five exact characters.
These finite controls supplement the symbolic proof.

The theorem is conditional on the inherited completed-call phase model. It
does not re-prove native implementation or physical ownership of those calls.
It covers this owner/port and these 20 existing cuts. Changes to hosted
phases, translations, charts, event order or the set of insertion cuts require
a different operator calculation. No all-owner theorem, native replay,
selected cold replay, complete supplier admission or new kappa is claimed.
The selected result and frozen sources are unchanged.

## Open next questions

Can a concrete change to a hosted phase, chart or insertion cut permit a
useful rank reduction? A new proposal must specify the altered word first,
derive its exact common-boundary operator and pay for the altered physical
interface. The present inverse only addresses the fixed word, so searching
more residual rank assignments within it has no remaining justification.

Can a rank-preserving, phase-equivalent basis replacement reduce a fully
charged producer or consumer cost? First exhibit an actual equal-phase
replacement and invoice its implementation, hosting and restoration. Equal
phase functions alone provide no cost improvement.

## Attribution and coordination

Canonical investigation:
[Discussion2612 comment19004159](https://github.com/CrocSwap/integer-mult-bounds/discussions/2612#discussioncomment-19004159).
Base canonical main and synchronized fork:
`463113d675af7410ac91d53a4fed51ec6494eb9a`, priority revision 6.
[TASK.json](TASK.json) preserves the original audit card, scope refinement,
overlap coverage and remaining obligations.

The five-site symbolic method and coupled-site question come from
thakrarsagar/PR3272 (`2d349d6b8c26c308665f85222b447da07271e026`). Retain
Gonzalo Mier's PR3263/3199 candidate replay and four-idle-site work, Tekalign's
PR3204 theorem, and Nick Petalas/PR3187's physical-stream criterion. Ross
Richardson's PR3254/3275 address a distinct one-child absorption interface;
they are not superseded by this fixed-interface theorem. Rohan Arun's
PR3200/3251 supply the rank-only candidate context, not operator admission.

Retain Jeremy Diviney/PR3148's T740 fill and 145-row journal, dcharb78/PR3133's
providers and notices, Gonzalo Mier/PR1252, Guéorgui Maissouradze's star
construction, Marius-Paul Dumitrean/PR2979, Ali Romman/PR1043, Sagar
Thakrar/PR2423 and the selected-supplier source lineage. Existing notices and
licenses are unchanged.

Copyright 2026 thakrarsagar. Apache-2.0. Substantial OpenAI Codex assistance in
derivation, implementation, independently written reconstruction, controls
and review. Separate AI executions are not independent human or formal review.

## Engineering constraints

Build the Lever is the explicit inverse, which resolves the complete fixed-word
interface without a new allocation census. Prove It Works is the exact source
replay, independent reconstruction and behavioral controls. New functions are
at most 60 lines and checks remain active under `-O`. The domain is fixed to
73 character bits, 20 variables and eight streams; replay deadlines are explicit.

Power-of-Ten rules 3, 8 and 9 need the usual managed-runtime/authenticated-source
deviations: Python allocates the fixed fixture objects and the primary executes
one authenticated predecessor module. The independent checker imports neither
that module nor the primary. Exact input pins, bounded fixtures and the scoped
certificate contain these deviations; frozen source loops remain unchanged.
