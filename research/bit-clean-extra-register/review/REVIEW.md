# Independent agent review: clean extra register

Review scope: `bit-clean-extra-register`, in the publication staging area.
This review uses main commit `cef4b52f2a59009865bf8eabde1be3f159063703`.
The review is by a separate OpenAI Codex agent. It is not human review or
proof-assistant verification. The review did not start a new research search.

## Claims reviewed

The required endpoint is the upper-left active block of the product of paid
factors. There are three active inputs and one input set to zero. The fourth
output is not used. The three target frames are invertible, lower triangular
matrices over the rationals. Each paid address frame has nonzero rank one.
Each scalar coupling is a binary rank-one idempotent.

The statements do not cover arbitrary final free scalar maps after the paid
product. In this endpoint model, augmentation fixes only the active block.
The full-endpoint argument that removes a final free scalar map in PR #468
therefore cannot be imported without an additional proof.

The written and finite results are:

1. Paid-frame span at most four needs at least `3W` calls for `W` invertible
   lower-triangular targets, with any finite number of zero input registers
   whose outputs are not used.
2. Eight independent paid frames cannot serve three such targets. At span
   seven, every scalar projector has zero active off-diagonal entries.
3. For one extra register, all 24 projectors with that zero pattern are
   excluded at eight calls.
4. For one extra register, the union of the coordinate-basis projectors and
   one arbitrary binary basis is excluded at eight calls.

These results do not exclude all eight-call circuits with a clean input.
Frame spans five and six, a nonzero active off-diagonal pattern, and an
alphabet outside the coordinate-plus-one-basis class remain open here.
The package gives no complete supplier, new construction, or new kappa.

## Written proof checks

The compact factorization `P-I=XTY^T` remains valid after compression to
the active block. The nonzero projected factors give an invertible triangular
`T` over the Laurent fraction field. If that block is zero, Sylvester's
inequality gives the stated sum of the two active ranks. No assertion about
the fourth row or column is needed.

For the span-four reduction, the determinant expansion gives three paid
frames whose left vectors and right vectors are both independent. After
common row and column maps, the span has the form `D+tuv^T`. If `u` and `v`
have full support, the mixed minors force every rank-one member onto one
of the four basis lines. The sum of the projected active ranks gives `3W`.
Otherwise the directed support has blocks of size at most two. A rank-one
member has at most one nonzero diagonal block. The common rational flag of
the target ratios descends to each invariant subquotient. The compressed
two-dimensional flag bound and the one-dimensional rank bound then add to
`3W`. The lower-triangular target assumption is used in this step.

For the one-relation reduction, a primitive relation with an entry of
absolute value at least two gives no subset collision. In the remaining
case, the Laurent kernel is principal. Its derivative forces one common
active off-diagonal pattern on the relation support and diagonal active
compressions elsewhere. The classification of rank-one completions covers
the unique matrix, coordinate-plane, and common coordinate image or row
cases. Deleting outside variables is valid because the only relation has
support in the retained variables. The variable assignments outside that
support are disjoint between target roles. The one- and two-target bounds
then give the claimed contradiction for every nonzero common pattern.

The 24-projector classification uses all 120 binary rank-one idempotents
on four registers. The distance argument applies to both active image and
row codes even when the fourth output is discarded. If `d_i` counts the
three active-diagonal families, the necessary code distances force
`d=(2,2,2)` and one `(1,1,1)` helper contribution on each side. This gives
exactly the 216 stated multisets. The independent finite reconstruction
in `check_reductions.py` confirms this classification and all 28 nonzero
active rank-one completion patterns.

The relation search branches only on differences of original subset
indicators. A nonzero off-diagonal term needs a collision. If a diagonal
has more than one term, at least one of its first two terms needs a partner.
Thus the reduced branching rule covers every possible monomial completion.
There are at most three independent relations after the span-four bound.
The zero-frame, primitive-parity, and target-in-two-frame-span rejections
are necessary conditions. Adding further relations cannot remove a target
rank obstruction already present at a terminal.

The field engine's rational reconstruction box is injective modulo 101.
State rank tests use at most three bounded generators. Each additional
collision or target test has, after expansion along coordinate rows, at
most four nonunit rows with entries in `{-1,0,1}`. The Hadamard bound is 16,
so a nonzero relevant minor cannot vanish modulo 101. The two field cores
in `field.cpp` and `two_bases.cpp` are identical apart from blank lines.
Their reuse is not a second independent arithmetic implementation.

The alphabet generator covers 840 unordered binary bases and 166 orbits
under permutations of the active coordinates. The helper coordinate stays
fixed. The independent dual-vector catalogue agrees with the saved rows.
Actual projector commutation preserves each formal factor word up to a
permutation of its paid-frame variables. The trace reduction keeps a least
representative of every class. No word-reversal reduction is used. Fixing
one basis to the coordinate basis is a restriction, not a normalization of
every pair of arbitrary bases.

## Publication overlap and source checks

All 23 entries in `SOURCE-MANIFEST.json` match both the package bytes and
their original local files. `SOURCE-REVIEW.json` records those checks,
the environment, the relevant current-main source hashes and the open-PR
snapshot hash.

The current-main packages `bit-clean-ancilla-registers` and
`bit-clean-workspace-compression` require all auxiliary outputs on data
columns to return to zero. They do not cover the discarded-output contract
here. `bit-one-relation-any-registers` and
`bit-mixed-target-register-compression` require full dirty endpoints.
`three-register-no-target-flag` has no extra register. The four-register
rational-frame-floor result fixes a rank-two address alphabet and four
active targets. None is the submitted claim. A body search of the saved
open PRs found no matching clean-helper, discarded-output, zero-pattern,
or coordinate-plus-one-basis claim. The title matches #4931 and #3893 concern
a native prefix and a non-abelian S3 result, respectively. This is a check
against the stated snapshots, not a claim of literature priority.

PR #468 is the material source for the formal model, span-four method and
exact relation search. Its pinned proof credits PR #288 for the scalar model
and flag/projection methods. It also credits PR #203 for the related
common-triangular-frame obstruction. Those credits must remain.
The source proof at `07a78bf335b0b5039a1fecd7cd74a0fe1d1605ea` was read.
The pinned PR #288 and PR #203 proof sources were retrieved from GitHub and
their relevant sections were read. The PR #203 author and body both identify
`huxint`, and its live head matches the stated pin. `REMOTE-PREDECESSORS.json`
records the source hashes and that attribution evidence. Remote link rendering
and final PR-body checks belong to the coordinator.

Historical prose names several paths that have moved to `expected/`.
The old 17,106-job layer census, its audit summary, and the returned-register
control script are not inputs to the new full replay. Their absence does
not leave a proof dependency missing. The runner generates the binary word
stream and the per-alphabet records from the included sources.

## Requested corrections

The first portable runner executed a historical three-worker driver.
The revised runner calls all 166 basis jobs in sequence and leaves that
historical source unchanged. The fresh review run uses the revised runner.
During that run, the author added `-E -B` to the Python generator child.
The completed census uses the preceding serial runner and the same frozen
sources. The final command change has a separate environment control; the
entire census was not repeated for this command-only change.

The package author was asked to state the final-free-map restriction,
retain PR #203 credit, and explain the relocated and omitted historical
inputs. The final reviewed manifest records the files after those edits.

## Execution record

The final execution status, exact commands, control outcomes and package
hashes are recorded in `REVIEW.json` and `REVIEWED-FILES.json`.
The full two-engine census of the zero-pattern class is separate from the
single-engine full basis census. The 48 selected Fraction comparisons do
not constitute a second complete basis census. No supplier-native or
selected-frontier replay is required or claimed for these scoped results.
