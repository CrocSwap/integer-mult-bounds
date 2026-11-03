# Length-4 G20 conjugations do not emit after one moved correction

**Negative result. No new κ.** The selected conditional exponent stays
`781451/250000000` (`0.003125804`) in
[certificates/selected-result.json](../../certificates/selected-result.json).
The baseline binding check returned `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`.
That command is not a supplier replay.

On the emitted local word of
[PR #5708](https://github.com/CrocSwap/integer-mult-bounds/pull/5708),
every length-4 A2 conjugation keeps its scalar endpoint when exactly one of
its four corrections is moved onto a different frame of the published
one-edge route table. All 302,260 such assignments fail to emit: 301,756
fail at the contact-correction meeting, and 504 meet and then miss a later
published edge. No assignment lowers the paid-query moment on `(0, 1)`.
The argument is in [PROOF.md](PROOF.md).

## Task and overlap

Base `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8. Card
`bit-helper-contract`, scope **refined**. The card says to review the
#5679/#5708 chain and stop when a proposed cut does not improve the paid
moment. This package is the length-4 one-move clause left open by the
length-1..3 moved-frame screen.

Ordered eligible list for session r89, rebuilt on 2026-11-03 against that
main. The 19 October handoff-index items are already delivered or closed, as
recorded by the length-1..3 package. Discussion #1166 through 2026-11-03 has
no newer finite handoff index. The newest posts are completed claims and
three individual handoffs (compressed-word drops, a stopped modular-inverse
draft, and a review request for open PR #6551). Those do not replace the
priority table. The table is the revision-8 "Next bounded decisions" table.
A row stays while that table still states the decision. Catalogue cards not
named by the table follow, in catalogue order. Dropped before the cut: work
this account already delivered, results closed on current main, questions
covered by an open pull request, and topics already on a fork `cursor/*`
branch.

1. Complex helpers (`p104-side-correction`, `coverage-law-change`).
2. **This package.** BIT (`bit-helper-contract`): one correction of a
   #5708 length-4 conjugation, moved off its contact frame.
3. New decoders and interfaces.
4. Supplier audit (`supplier-boundary-audit`).
5. All-size audit (`uniform-transfer-audit`).
6. Verification tooling (`replay-runtime`).
7. `bit-new-register-model`.
8. `r437-carrier-integration`.
9. `complex-rank-shape-decoder`.
10. `complex-new-helper-inventory`.

[#6305](https://github.com/CrocSwap/integer-mult-bounds/pull/6305) keeps
every correction on its contact frame for length 4 and above.
[#6337](https://github.com/CrocSwap/integer-mult-bounds/pull/6337) moves one
correction only for lengths 1..3.
`research/g20-one-contact-free-frame` allows catalogue paths, and only for
one contact. `research/g20-neutral-two-step-obstruction` keeps correction
frames fixed. The local overlap search does not find a replay of this
length-4 one-move domain.

## Census

| Domain | Missing meeting | Later missing edge | Emitted | Saving |
|---|---:|---:|---:|---:|
| One moved correction, length 4 | 301,756 | 504 | 0 | 0 |

The contact-frame slice of the same 119 intervals is 118 missing routes and
one unchanged histogram, at zero-based scalar positions 9,399 and 10,815 of
`ADD(560, 315)`. A separate control recounts all 1,503 lengths of four or
more at the contact frame and matches the published #6305 totals: 1,450
missing, 14 unchanged, and 39 strict losses in the seven published shapes.
That control does not replace the #6305 proof.

## Reproduce

Python 3.12 and the standard library, from the repository root. The census
finishes in about ten seconds here.

```sh
python3 -I -B research/g20-length4-moved-frame/verify.py
python3 -I -O -B research/g20-length4-moved-frame/verify.py
python3 -B scripts/research_package.py --package research/g20-length4-moved-frame --check-only
python3 -B scripts/research_package.py --package research/g20-length4-moved-frame
```

The direct verifier prints

```text
PASS_G20_LENGTH4_MOVED_FRAME intervals=119 fixed_missing=118 fixed_neutral=1 moved_assignments=302260 local_fail=301756 local_feasible=504 missing_edge=504 emitted=0 savings=0 long_control=1503/1450/14/39 no_new_kappa=true
```

Checks raise exceptions, so `-O` does not disable them. Not run: the #5708
integration replay, the 18-call caller, adjoint columns, moduli 101 and
10201, ordinary admission, Lean, Docker, and `make frontier6030-verify`.
`check_research_commit.py --check-source-history` needs full Git history.
This checkout's upstream pin is shallow, so that ancestry check was not run.
The pinned input blobs are objects of the recorded base commit.

## Open next questions

1. Can two corrections in one length-2, length-3 or length-4 interval lower
   the paid moment when both frames move? This certificate moves exactly one
   correction. The first step is one two-move pair on this word and route
   table. No saving seed is supplied by the one-move census.
2. Can one moved correction at length 5 or more lower the paid moment?
   #6305 excludes those lengths only while every correction stays on its
   contact frame. The first step is one length-5 interval with one moved
   frame. The length-4 assignments do not provide a seed that emits.
3. Do the six neutral one-step neighbors and the 645 common-frame expansions
   in the #5708 README have an executable rule? That sentence is still
   local-only. The blocker is that the published package does not contain
   the search.

## Credit

The emitted word, route table, A2 relation, and the local-only conjugation
count are Ali Romman's `research/g20-conjugation-admission`, following
Dugongue, ai-nanachi, and the retained G20 lineage named there. The
length-1..3 contact-frame census is unpaidmoon's #6290. The length-4-and-above
contact-frame obstruction is Nick Petalas's #6305. The length-1..3 one-move
obstruction is unpaidmoon's #6337. The one-contact free-frame obstruction
and the fixed-frame neutral two-step obstruction are separate packages and
are not imported.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
