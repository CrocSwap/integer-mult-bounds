# An actual mixed-rank P112 counterexample at cut 40

Three rational pieces of binary support ranks 5, 5 and 6 span two independent
restricted P112 root-code words after ONE common cut of size 40.
[WITNESS.json](WITNESS.json) contains every coefficient and cut coordinate.
The supports have sizes 12, 12 and 20 and are disjoint, with union 44.
Their code plane has live union 84. [PROOF.md](PROOF.md) explains the identity.

This proves that PR3278's sufficient allowance 39 cannot increase to 40.
The combined sharp threshold 39 inherits that pending predecessor's sufficient
theorem and its stated dependencies. The new counterexample requires only
the pinned geometry and exact arithmetic. It works over every characteristic-zero
field. It supplies no literal caller, full C5, decoder floor, native program,
physical invoice, supplier admission or new kappa.

## Reproduction

From the repository root, with Python 3.12 and the standard library:

```sh
python3.12 -W error -B scripts/research_package.py \
  --package research/p112-mixed-sharp39
```

The three registered commands also work directly in a Git-free export:

```sh
python3 -W error -B research/p112-mixed-sharp39/verify.py
python3 -W error -B research/p112-mixed-sharp39/independent.py
python3 -W error -O -B research/p112-mixed-sharp39/test_verify.py
```

The primary check verifies all 144 retained coefficient equations, the actual
support ranks, the common cut and a nonzero minor. The independent implementation
rebuilds root coordinates and labels with an integral recurrence and uses span
cardinalities instead of binary elimination. Six control groups cover wrong
coefficients, missing or repeated cuts, dependent directions, rank mislabelling,
source corruption, extra inventory and input-to-provenance relabelling.
`SOURCES.json` has a fixed path, usage and schema inventory. Both source SHA256
and Git blob checks remain active with Python optimization.

PR3278 `67280b1da48a14435d7fde3ec81314c768a8dd3e` is retained verbatim as
`vendor/pr3278-PROOF.md` and `vendor/pr3278-RESULT.json`, with source paths and
exact hashes. No pending-PR Git object is needed in fresh CI or the direct
export. Authentication preserves its evidence; it does not independently prove
its sufficient theorem. Its historical capacity checks and Weyl argument are
not rerun. Selected cold replay, Lean, Docker, human and proof-kernel review
are unrun. Internal computational review is narrower than those obligations.

## Scope and implementation decisions

The revision-6 card's first local-word ceiling control passed. This package takes
the explicit PR3278 cut-40 realization handoff as a side result. It does not meet
or claim the card's 5% supplier target. The family decision is to finish this
missing implication and stop. Source access, physical frames, native restoration,
hosting and complete consumer costs remain unknown.

The old union-82 equality probe did not decide this boundary. At cut 40 the
permitted support sum allows union 84. Its large fibers have TWO frame punctures
each, leaving 31 sites, rather than the four-puncture 29-site fibers used in
PR3278's union-82 argument. The four-puncture capacity 18 does not apply here.
Concurrent analytic D6 capacity18 and A2 joint32 investigations are distinct
and unused. The uniform rank-five cut48 witness in PR3283 has a distinct rank
contract and retains credit for the related axis-splitting idea.

Separate Before Serializing Shared State gave the work its own package, branch,
cache and status, with brief shared Git and claim operations under OS locks.
Prove It Works required actual coefficient replay and the committed Git-free
export. Power of Ten deviations are limited to standard-library Python's
managed allocation and one source-authenticated geometry import. Files are
limited to 100,000 bytes, roots to 120, points to 112, binary spans to 512 and
minor checks to 2,556. Functions stay below 60 lines. Validation uses explicit
exceptions under optimization. Frozen geometry is unchanged; no compliance
claim is made about unrelated predecessor code.

## Open next questions

Which currently uncovered literal caller satisfies the sufficient cut-39
contract? Reconcile its source inventory and give one common cut with the
retained code dimension before applying the theorem. The counterexample is not
a fit of the full decoder or a global upper bound. No further task is reserved.
Structured scope and the stop rule are in [TASK.json](TASK.json).

Canonical investigation: [Discussion3156](https://github.com/CrocSwap/integer-mult-bounds/discussions/3156#discussioncomment-19003989).

Credit Nick Petalas/PR3278/3267/3260/3262/3269, PR3283's related uniform-rank
witness, DreamingOfClouds/PR3154 and the retained E8/P112 geometry lineage
including joaqcoo. The simple-root convention follows the pinned root-simplex
geometry and PR3161/3162. Frozen inputs and the selected result remain unchanged.
Apache-2.0.
