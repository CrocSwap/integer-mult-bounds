# SW4 pre-read insertion slides: scoped negative result (seed 20)

**Result.** No placement of SW4's eight r2h compensation pre-reads beats the
pinned one. A complete census of all single slides, all pair slides and all
same-position tie-order swaps — 1,432 configurations — finds 1,060 legal
configurations, and **every legal configuration has exactly the pinned paid
profile** `{1:2548, 2:342, 3:438, 4:186, 5:56, 8:8}` and therefore exactly the
pinned complex endpoint. The other 372 configurations are refused by the
inherited frame cap checks. No κ change is claimed or possible from this
mechanism. This is a finite scoped negative result, not an impossibility
theorem.

## Object and question

SW4 (`research/complex-sw4-frame8/construction/sw4`, the complex word of the
selected frontier ancestry) exchanges B-phase reads between four entering
helpers `h` and their face registers `r`. Each r2h move converts a read
`add(t,r,c)` into `add(t,h,c)` and inserts a compensating pre-read
`add(t,h,-c)` at one fixed position, "right after h's last existing pre-read".
The construction record for SW4 enumerates which *subsets of reads* move
(602 single-pair candidates); #775 and #876 close the coupled partial and the
full pair/triple combination spaces. Nobody had moved the pre-reads themselves.
#775's scope list names exactly this gap: "alternative insertion positions".

A pre-read may sit anywhere before its helper's copy gate, where `h = E_h`:
the B-end state of every register is then unchanged, because B gates on a
target accumulate linearly and `h` is written only by its copy gate. Position
still matters to cost: it decides which gate pays the frame climb, and moving
a pre-read early can push helper frame content past a target's hyperplane cap.

## Domain (complete and deterministic)

On the pinned SW4 input word (content sha256 `0390ec65dc4d47df1887aabdc2ec5b6ddea3cfc8e65582873fdfeba81d100073`,
refused by `build_sw4.py` if different), with the 16 recipe moves otherwise
unchanged:

- each pre-read's window is `[0, copy_index(h)]` in the deletion-applied B
  list (windows of 637–830 positions);
- positions are identified up to *positional equivalence*: two positions
  between consecutive gates touching the moved target or helper see identical
  register states and frames. Each window collapses to **7 classes**;
- families: all 8 × 7 single slides (56), all class pairs over the 28 move
  pairs (1,372), and both orders when one helper's two pre-reads land at the
  same position (4, the recipe order already counted among the pairs);
- every candidate is checked for the exact B-end state mod p (sparse row
  replay of A + cut + B on all 728 registers), for the inherited frame refit
  (caps, tails, ends) and by the inherited profile replay;
- pricing: the exact complex endpoint functional of the pinned moment model,
  the root `a` of `sum_d n_d·d·(73/d)^a = 73·7168` over
  `H = 72·H_local + {1:1, 3:1, 44:1, 48:2396}` (rank mass 520,704, deficit
  2,560). On the frame8 profile this reproduces the selected record's complex
  endpoint `1663966829367501881629/10^24` to float precision (test T6), and
  the pinned exact mercator/exponential engine brackets every reported root
  within 2×10⁻¹⁵ (`EVIDENCE.json`, `pricing.exact_engine_crosscheck`).

## Numbers

| Quantity | Value |
|---|---:|
| configurations enumerated | 1,432 (56 singles + 1,372 pairs + 4 swaps) |
| exact B-end state preserved | 1,432 / 1,432 |
| legal under the inherited frame checks | 1,060 |
| refused (first refusals are frame-cap violations) | 372 |
| distinct paid profiles among legal rows | 1 |
| configurations strictly beating the pinned schedule | 0 |
| best root = pinned root | 0.0016634287545401745 |

The single distinct legal profile is the pinned profile
`{1:2548, 2:342, 3:438, 4:186, 5:56, 8:8}`, with local rank mass 5,634 and the
pinned width inventory `{4:80, 5:32, 7:54, 8:122, 9:216}` in every legal row.
So insertion position is invisible to cost whenever it is legal at all, in
this domain: the pinned "right after h's last pre-read" choice is not a tuned
parameter but one representative of a whole plateau.

## Controls

- The pinned schedule through this package's placement code reproduces the
  pinned SW4 output word **byte for byte** (content sha256 `d232183f233899961bf55cac67a18545ed33548d9a7ca7078990d1a83d557c59`)
  and its pinned profile.
- An out-of-window slide (at the helper's copy gate + 1) is rejected: its
  exact B-end state differs (the pre-read then reads `h = E_h + r`). This is
  the negative control for the window boundary.
- `test_search.py` pins six behaviors: byte-exact pinned reproduction, the
  equivalence-class partition, out-of-window inexactness, the structural fact
  that no scale of a moved target sits in any window (the only in-window
  exactness hazard), in-window exactness, and the endpoint functional on the
  selected record's endpoint.
- The exact engine brackets each reported root from both sides with exact
  rational residuals (`residual_at_root_minus < 0 < residual_at_root_plus`).

## Reproduce

Python 3.11+ and the standard library only; no network, no optimizer; about
8 minutes:

```sh
python3 -B research/complex-insert-slides-seed20/verify.py
```

Expected final line:

```text
PASS_INSERT_SLIDES_SEED20 singles=56 pairs=1372 swaps=4 legal=1060 improving=0 best_root=0.001663428754540
```

`verify.py` re-runs the behavior tests, re-enumerates the complete census,
re-runs every control, and compares counts, roots, the exact-engine
cross-check and the canonical rows digest against `EXPECTED.json`.

## What is covered, and what is not

Covered: every placement of the eight compensation pre-reads within their
exactness windows, up to positional equivalence, singly and in pairs, plus
same-position tie orders, on the pinned SW4 word and its pinned frame policy.

Not covered: triples and larger slide groups; relocating the *deleted* h2r
entrance pre-reads (deletion is exactness-forced; the N1 control of
`build_sw4.py`); moving the converted reads themselves; alternative insertion
after the copy gate (inexact, control); relaxed frame floors or changed
helper boundaries; other decoders; the jp8/ck words; frame assignments of the
fixed program (closed negatively by #815's LP/CP-SAT optimum and #864's exact
duals at the next tick); read-set choice (#775, #876, SW4's own census);
owner, hosting and invoice changes; the bit supplier; and the outer theorems.
This is a finite census over a stated family, not a proof that no schedule
anywhere can improve the word, and not a formal proof of any theorem.

## Relation to prior and concurrent work

- SW4's own search (BRoute / Jeremy Kothe, PR #699; record in
  `research/pr699-frame-retiming/evidence/READ-EXCHANGE-SEARCH.json`) varied
  read *subsets*, not insertion positions.
- #775 (coupled partial read exchanges on P6k4, seed 21) excludes "alternative
  insertion positions" in its scope list; this package covers exactly that
  exclusion with a different method (complete positional-class enumeration).
- #876 (seed 29) covers simultaneous full pair/triple exchanges; its vendored
  P6K4 input word is byte-identical to the pin used here (acknowledged in
  `NOTICE.md`).
- #815 (Rohan Guliani) proves frame optimality of the *fixed* gate sequences
  and samples commuting reorders by annealing; the present census is complete
  over a precisely defined subfamily of reorders and agrees with #815's
  picture (no frame or position lever moves the word).
- #864 (seed 28) excludes frame reassignment of the selected X4 word by exact
  duals; it does not cover gate positions.

## Attribution

Prepared for the coordinated research sprint with help from opencode.
Apache-2.0. Construction credit for the SW4 mechanism and recipe: BRoute /
Jeremy Kothe (PR #699) and the retained lineage in
`research/complex-sw4-frame8/PROVENANCE.md`. The pricing functional follows
the pinned moment engines and #815's cost model. See `NOTICE.md` and
`SOURCES.json` for pins. No independent human review is claimed; no κ change
is claimed.
