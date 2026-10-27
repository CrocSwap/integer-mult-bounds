# Overlap audit and target selection

The audit preceded implementation. The full initial record is in
`../lean-multi-host-framework/overlap-audit.json`; the final read-only refresh
is recorded in `overlap-final-refresh.json` and `overlap-final-trees.json`.

Main, PR397, PR442, and PR448 remained at their previously inspected exact
heads. `source-versions.json` pins them and Jacob Sussman's linked
`wht-power-saving-lean` repository. The initial audit inspected the existing
dirty-wrapper, framed-XOR, address-gauge, localization, and scheduling work.
Generic conjugation and scheduling algebra are existing work.

The latest PR448 discussion still includes its author's acknowledgement
(comment 6113842081, updated 2026-10-11 21:15:52 UTC): the proposed split action
presupposes an unstated multi-stream register interface; using a second
register changes the local word and requires charging its frame chain. This
contribution assumes neither that interface nor the advertised gain.

The refresh screened the latest 100 updated PRs. Complete, untruncated trees
of changed PR473 and PR477 and new PR508 and PR510 each contained the same
154 Lean blobs as pinned main. Their newer Python/C++ constructions do not
provide a new Lean instantiation of this source obligation. This bounded
search does not assert that every historical branch or external repository
has been searched.

## New overlapping Lean work: PR509

PR509, *Lemma G of #484: clean proof and Lean 4 formalisation of its core*,
was reviewed at `7b9c720ecc9f483c383e7cd9c2ab81f06ee5df59`. All 195 changed
paths were inspected for the relevant subtree; all 18 new subtree files
were fetched by exact commit and checked against its manifest. Six are Lean
files. This was a source review, not an independent build of its Lean 4.21.0
package or replay of its Python instance checks.

Its `LemmaG.Stream.conj` and `conj_matrix` establish common-frame transport
for labelled streams given well-labelledness and exact relabel recipes.
`scalRun_eq_sum` and `S_rowform` establish the arbitrary-input interpretation
of symbolic scalar execution. `row_unit` derives helper behavior from an
assumed unit endpoint row. `BitEntrance` proves doubled-address identities.
These substantially overlap with the generic principles supporting this
package; no novelty for those principles is claimed here.

The concrete target remains open in that head. It contains no embedded
19,002-event PR442 word, computed 987-row endpoint, checked 944-frame matrix
table, actual 747-helper ownership map, or original 172-bank ownership
certificate. Its emitted-word labels, transition recipes, matrix endpoint,
accounting, and adapter hypotheses remain Python checks. Its selected word
is the complex PR484 variant with 800 live columns.

Its copy/clear linear semantics also do not supply the clean-private guards
required here: copy overwrites and clear assigns zero, while admissibility
tracks labels. That is a different abstraction boundary, not a criticism of
its stated theorem. It has no concrete cover-class aliasing model.

The useful target is therefore the additional concrete PR442 word, frames,
owners, and dirty-input obligations, followed by their explicit connection
to the separately checked multi-host theorem.

## Closing refresh at 23:26 UTC

`overlap-closing-refresh.json` rechecks the latest 100 updated PRs and the
pinned main, PR397, PR442, PR448, PR509, and Jacob Sussman heads. All those
pinned heads are unchanged, and PR448's latest discussion remains the same
interface acknowledgement. The changed PR473/477 heads and new PR512/514
each still have precisely main's 154 Lean blobs; the complete tree evidence
is in `overlap-closing-trees.json`.

Two new Lean PRs required source review. PR513
(`005dd3f4e3cba8d1761abc4ab391aaf6d14d6f73`) adds a sequential completed-bank
theorem and concrete five-stage route/schedule bindings. Its generic
completion algebra substantially overlaps with Task A. It still assumes the
universal local physical endpoint as a supplier premise and does not certify
the actual PR442 word, frames, owner functions, or dirty-input endpoint.
PR511 (`79f7c03c7f820ab89955b75ef239cbaccc627e6e`) concerns a fixed-width
binary count dispatcher. Neither resolves this selected concrete obligation.

`closing-lean-overlap.md` records the exact statement review and its limits.
All 37 changed files were fetched by exact head and checked against Git blob
hashes; PR513's eight Lean manifest hashes also matched. This was a source
review, not an independent rebuild of their Lean 4.21 packages. The concrete
source obligations remain the contribution; generic composition principles
are not presented as new.
