# Executed validation

Research base: `ba82555c64e1879e4b7decce28186f208fcb8262`.
Submission refresh: `ce7ad1b6ab09452c3478723a2e96ed5ff212dc08`.
Seven replay input Git blobs are identical at both commits; five base-context
pins resolve to their recorded original blobs. During this run upstream
advanced the selected record from PR1042 to PR1094,
`836330098538459/500000000000000000 = 0.001672660197076918`.
This contribution changes neither selection; the historical source inputs
and scoped boundary result are unaffected.

Local execution on 2026-10-13 UTC, macOS arm64, Apple clang 17.0.0:

- CPython **3.14.6**: isolated optimized full replay passed, including fresh
  C++17 compilation and equality of every modular state/minimum distance.
- CPython **3.9.6**: the same full replay passed with the same entire receipt.
- Both versions passed all **10 package test groups**. These include 37 literal
  primitive omissions, seven input-file corruptions, a changed lower bound in
  the receipt, and a complete minimal offline relocated replay in a path with
  spaces. The relocated replay leaves all files byte-identical.
- Fresh `--record` output matches committed EXPECTED.json byte for byte.
- `make selected-record-check` and all **five selected-result tests** passed.
- Source/base pin checks, unchanged selected record, whitespace and focused
  package/workflow scope were checked before submission.

The complete modular balls contain 48, 3,938 and 505,171 matrices, respectively.
The five-register ball layers are `[1,45,1250,26830,477045]`; its translated
intersection for `(01)(234)` is empty. This completes the declared length-eight
search. No length-nine search or unrestricted optimality claim is made.

The exact historical source census matches all 168 retained PR971 boundaries,
including every event interval, frame, swap site, permutation and cycle. Source
bytes and declared semantic word hashes both pass. The seven source pins are
immutable inputs; no original archive is regenerated or overwritten.

The pre-submission overlap refresh reached PR1142, refreshed the nearest PR1095 at
`1db482a6cb63ae49cf156357ef98b8e4b676fcd9`, and searched open scratch-free
boundary/permutation work. PR1095 permits scratch and restricts prefixes to
monomial rows; this contribution removes scratch and permits mixed rows.
Its contribution is a different cost class, not another replay of PR1095.
PR1116/1118 remain unrelated helper-butterfly/grid-synthesis mechanisms.

A focused Linux workflow is included. Hosted CI status is reported separately
in the PR handoff; no local result is represented as a hosted pass.

Not run or claimed: repository-wide `make verify`, selected supplier cold
replay, whole historical primitive streams, native frame/phase/physical
admission, global hosting/invoice/assembly regeneration, rounded precision,
all-size/compiler/analytic proof or Lean. Those sources are unchanged.
