# P104 source-lifetime floor: 216 in the widened X-only model

**Result.** The source-bound proof review and pinned replay support the claim
that a complete word correcting all 104 rows of `C = I - G/2` needs at least
216 helper lifetimes in the stated widened grammar `G′`. This grammar permits
arbitrary rational linear mixing among helpers at the same frame, including
singular maps. The bound is conditional on the frozen P104 source and target
frame paths and the X-only monotone access rules below.

This is the lower-bound lane assigned to macbook-04. It studies the complete
104-row side-correction matrix. It does not construct a word for the other
worker's named 208-flag endpoint collection and does not repeat its static
matching.

## Proof and evidence

The mathematical argument and finite census are reviewed in
[PROOF-REVIEW.md](PROOF-REVIEW.md). The exact upstream proof source is
[commit `743640530229e1821ae11dc104798871272d6f00`](https://github.com/thakrarsagar/integer-mult-bounds/tree/743640530229e1821ae11dc104798871272d6f00/research/p104-rank1-mixer-correction).
The source-package file hashes are recorded in [UPSTREAM-PINS.json](UPSTREAM-PINS.json).

The pinned upstream replay was run from an isolated copy with the canonical
P104 inputs. It ended with:

```text
PASS_P104_RANK1_MIXER_TOP floor_full=219 floor_final_frame=234 floor_full_singular_mixing=216 pairs_passing_T_final_frame=288 pairs_passing_T_full=414 both_halves_T=0 demo_lifetimes=4974 controls=7 lemma_max_ST=48
```

The replay reports 84 certified targets, 20 permissive targets, and 12
full-model singular-mixing exceptions (target IDs 1, 3, 6, 7, 12, 14, 41, 46,
54, 74, 81, 83). It reports 1,038 pairs satisfying the singular-mixing test
and no geometric full-model pair passing that test for both complementary
halves outside those 12 targets.

To reproduce the complete upstream replay, retrieve the package files at the
pinned commit, stage them as `research/p104-rank1-mixer-correction/`, and stage
the two frozen inputs and `ceiling.py` at the paths and hashes in
[SOURCES.json](SOURCES.json). Then run, from the staged repository root:

```sh
flock /home/user/int-bounds-pass/20261018-luna-xhigh/compute.lock \
  python3.12 -I -B research/p104-rank1-mixer-correction/verify.py
```

The package-local `verify.py` checks the fixed source hashes and recomputes
the integer floor from the recorded replay counts. It is an arithmetic check,
not a replacement for the upstream geometric replay or the written proof.
From the repository root, run it with:

```sh
python3.12 scripts/research_package.py --package research/p104-source-lifetime-216-review
```

## Scope limits

`G′` uses the PR1972/PR1991 P104 source and target paths, X-only source reads,
monotone helper lifetimes, and target writes to the frozen Y paths. It permits
arbitrary rational operations among helpers sharing one frame, including
copies, clears, rescalings, source-independent helper births and early helper
ends. It has no Y reads, root-code reads, or original-helper reads. The proof
does not use dirty restoration or cut order, so it also holds when those are
relaxed within this grammar.

The result does not establish an executable correction, a physical hosting
bill, a supplier, an all-size theorem, or a new `κ`. The floor is below the
source handoff's first decision-relevant threshold of 333 lifetimes and below
its fixed-template allowances 431, 478 and 482. The two-history relaxation
therefore still passes its optimistic screen; this review changes no budget or
frontier decision. See [PR #2924](https://github.com/CrocSwap/integer-mult-bounds/pull/2924)
for the price under the imported floor.

## Open next questions

No next construction or larger census is justified by this floor alone. The
upstream proof identifies a concrete reopening condition: a source-bound
gathering or mixing charge below seven-dimensional frames that could raise the
floor past 333. Until such a charge or a changed source/consumer contract is
available, stop this line.

## Credit

The 216/219/234 theorem and checker are by Sagar Thakrar, with substantial
Claude assistance, at the pinned upstream commit. Retain Philippe Van Velzen's
relay grammar and geometry contributions, PR #2353 and its predecessors, and
the Rohan Arun / Chafik Boukhalfa / Adam Gall P104 native-channel lineage. This
review was prepared by GPT-6 Luna xhigh (macbook-04) with substantial OpenAI
Codex assistance. No independent human or proof-assistant review is claimed.
