# H2-sem admission of the PR848 copy-path helper-sharing wrap (no new kappa)

**Scoped interface audit; no circuit pricing, no supplier adoption.** The selected
result, the selected bit supplier and `upstream/` are unchanged. The exact
replacement contract is woklerx's H2-sem (PR1194,
`research/r439-semantic-d-contract-seed10/PROOF.md`); this package decides one
precise implication of it on one precise family of words and tries to falsify
that implication on dirty inputs and chronological cuts.

## Object and question

PR848 (`research/r439-copy-path-sharing-barrier`) priced source-read sharing
inside the frame-zero D section of the selected R439 word
(`research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz`, v=111, R=439,
111 D gates, 18,085 helper reads). Its oriented-pair census over the 430
non-retained helper operands found 41,404 arithmetically positive pairs (best
277 -> 434, saving 65) and one seed-42 greedy disjoint matching of 205 pairs for
6,231 source reads. PR848 recorded the figure as an arithmetic upper bound only:
the inherited gate-local H2 (`H2_D_frame0_targets_from_helpers`) requires every D
gate to write a target, so every helper-writing preparation/restoration pair is
rejected (its control C1 preserves the scalar operator and fails H2).

**Question (card `bit-helper-contract`, first experiment).** Write one
replacement H2/K implication for a helper-mixing word and try to falsify it on
dirty inputs. The replacement is H2-sem: D gates at the zero frame with distinct
operands drawn from targets and helpers, the retained no-target-feedback
prohibition, and the full boundary equation `(x,y,h) -> (x,y+N h,h)`, with the K
check comparing the *semantic* N against raw A/scatter/B instead of gate-local
source reads.

**Implication (I), the audited statement.** If a wrapped D section satisfies
H2-sem conditions 1-3 with semantic N unchanged, and the unchanged predecessor
checker passes every inherited H1-H5 and U/J/K/C flag on the PR1194 virtual
splice (literal A/scatter/B/C with the original D), then the PR1194 chronological
substitution bridge transfers the interleaved-lemma conclusion to the wrapped
word, on arbitrary dirty inputs.

## Result: implication (I) holds on the tested instances

| wrap | H2-sem 1-3 | boundary op. on 661 cols | frames at cut | semantic K | inherited flags failing | D source reads |
|---|---|---|---|---|---|---:|
| C1: pair 277 -> 434 | pass | exact | equal | N = K | exactly H2, K_equals_D | 18,085 - 65 = 18,020 |
| seed-42 matching (205 pairs) | pass | exact | equal | N = K | exactly H2, K_equals_D | 18,085 - 6,231 = 11,854 |
| C2: PR848 target-temp (control) | pass | exact | equal | N = K | none | 18,087 (+2) |

All 661 basis columns are replayed exactly; by F2 linearity (PR1194's module
argument) coefficient equality on those columns is equality on every F2 module,
so this covers arbitrary finite and infinite dirty streams in the stated
interpretation. The virtual splice is the pinned baseline word itself, which
passes all inherited flags; the continuation state and frames at the D/A cut are
byte-equal between each wrap and the baseline.

So the PR848 obstruction ("any helper-writing preparation/restoration pair is
rejected") is scoped to the inherited gate-local H2 only: under H2-sem the C1
wrap and the whole greedy matching are interface-admissible helper-mixing words,
and the semantic K check passes exactly where the literal extractor fails.

## Falsification attempts (why the contract clauses matter)

| control | outcome |
|---|---|
| F1 unrestored helper temp | rejected at endpoints (boundary equation broken on helper columns) |
| F2 wrong restore operand | boundary equation broken on a dirty helper column |
| F3 restore at a mid-body chronological cut | boundary equation broken (the wrap must span every dependent read) |
| F4 target-feeding-helper wrap (span closed before the fed target's own gate) | **scalar operator exact, endpoint passes, frames equal** — rejected only by H2-sem condition 2 (the retained no-target-feedback clause; the checker's H1 also fails). A weaker replacement that drops that clause would admit it. |
| F5 source-feeding-helper wrap | scalar operator exact, but the framed replay rejects the frame-0 source read outright (`climb not nested: register 0 from frame 2 (dim 1) to frame 0 (dim 0)`): raw operator identity does not justify frame-sensitive execution |

F4 and F5 are the recorded boundary of the replacement: the exact boundary
equation alone is strictly weaker than H2-sem. F5 additionally confirms at one
concrete instance the warning in PR1194 and `r439-abc-semantic-bridge` that a
raw block identity must not be treated as a framed equivalence.

## Reproduce

Standard library only (Python 3.10+), from the repository root:

```sh
python3 -I -B research/r439-copyshare-h2sem-admission/verify.py
python3 -I -O -B research/r439-copyshare-h2sem-admission/test_package.py
python3 scripts/research_package.py --package research/r439-copyshare-h2sem-admission --check-only
```

Expected (about 40 s for the first command):

```text
PASS_R439_COPYSHARE_H2SEM_ADMISSION pair=277->434 saving=65 matching_pairs=205 matching_saving=6231 columns=661 controls=7 no_new_kappa
```

`CERTIFICATE.json` is compared field for field; `test_package.py` replays at a
fresh location and rejects a mutated source pin, a mutated certificate and a
missing pin block. The verifier recomputes PR848's complete pair census and
greedy matching deterministically (seed 42) and checks its recorded constants.

## Scope: what is not claimed

* **No priced construction.** The 6,231 figure remains a source-read arithmetic
  bound. The wrapped words are not billed: F/B positive envelopes, the 104/192-bit
  guards, COPY/ERASE accounting and the paid profile were not recomputed, and no
  word is proposed as a supplier. Intermediate integer envelopes can differ even
  at an identical binary endpoint (PR1194), so the precision guards are an
  explicit open obligation.
* **No kappa, frontier or native/hosted admission.** The all-size compiler,
  common-label realization, hosting, precision/tape, recovery and analytic
  obligations are untouched.
* **The bridge is PR1194's, applied.** The chronological substitution theorem and
  its module argument are credited to PR1194; this package contributes the exact
  instance-level admission and the falsification controls, not a new lemma.
* Greedy matching optimality is not claimed (PR848's matching is one seeded
  pass). F4 shows condition 2 is not redundant with the boundary equation at this
  instance; whether some target-feedback wrap is safe under a weaker replacement
  needs its own lemma and is not decided here.

## Overlap

The submission-time `find_overlap.py` snapshot (446 open PRs including drafts,
418 discussion records, complete pagination, 2026-10-14 09:50 UTC) for `H2-sem`,
`semantic zero-frame D`, `copy-path sharing`, `copyshare`, `helper-temp`,
`277 -> 434`, `pair sharing wrap` matches only this package, its claim
([discussion 1166](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18920693))
and PR848's own record; no open PR or discussion claim covers H2-sem admission of
copy-path sharing wraps. This is not a novelty certificate.

## Open next questions

* **Bill the admitted wrap.** Recompute F/B, the exact local/nine-stage bit
  expressions and the paid profile for the 205-pair wrapped word and check the
  precision guards. Why it matters: this is the only path from an
  interface-admissible 6,231-read reduction to an actual bit-circuit saving.
  First step: rerun `research/r439-bsection-stars-seed01/verify.py`'s bound
  machinery on the wrapped D. Blocked by: the envelope code lives in the
  predecessor packages and must be reused unchanged; the 192-bit nine-stage cap
  already sat at 99.996% on the helper-star word.
* **Is H2-sem condition 2 necessary at a framed level?** F4 preserves the full
  scalar operator yet is excluded by the retained no-target-feedback clause.
  Why it matters: a justified weakening would enlarge the admissible wrap class.
  First step: state the exact conclusion the interleaved lemma needs from H1 and
  test the F4-shaped word against it. Blocked by: the lemma's proof uses H1 in
  its block-triangular step; an operator-level check alone cannot replace it.

## Credit and disclosure

Prepared by **Aaron Wang** with help from opencode. Apache-2.0; no independent
human review is claimed. Credit **Aaron Wang, PR848**
(`research/r439-copy-path-sharing-barrier`: the pair census, the greedy
matching and the C1-C3 controls whose C1/C2 shapes are reused here), **woklerx,
PR1194** (`research/r439-semantic-d-contract-seed10/PROOF.md`: the H2-sem
contract and chronological substitution bridge), **Arham Tahir**
(`research/r439-abc-semantic-bridge`: the source-bound bridge-application
pattern), **eumemic PR555** and **DreamingOfClouds PR589** (the R439 word), and
the retained scalar-interface/xcheck lineage. The word, the unchanged
`xcheck_p.py` owner checker and PR848's census code are consumed as pinned
sources; no predecessor package is vendored or modified.
