# multicut-kernel-composition

**Conditional κ = 142805349285993 / (2·10¹⁷) = 7.14026746429965·10⁻⁴** (+0.4216% over PR #259's 7.11029386054035·10⁻⁴;
+0.0510% over PR #271's 7.1366215638961·10⁻⁴ and +0.0472% over PR #275's 7.13690108083058·10⁻⁴, the best rungs on
PR #249's word before this one). With the seven native checkers alone (before the sandwich stage):
κ = 7.12005174354669·10⁻⁴. PR #276's new bit word (gen4, 7.2287·10⁻⁴) stands above every rung on this word.

PR #259 (Dugongue) condenses response kernels of the PR #249 bit word with 518 pivot families at four cuts. This
package composes, on that word, with PR #259's seven native checkers and pricer unchanged, four levers published
by five authors:

1. **372 more kernel families at its earliest cut** (record 676,559, the last initial compensation read): a census of
   the twin dirty helpers live at that cut — helpers untouched before it whose complete F₂ target responses coincide
   — gives 985 twin pairs; the net-positive ones disjoint from PR #259's helpers (first round 333, second round 32),
   two e = 2 planes of PR #270, and **54 shared-donor families** (a new pivot whose twin partner is already a donor of
   another family, lifted once on a nested entrance chain, as the 24 reuse pairs of PR #270 and the chronological donor
   sharing of PR #267; 26 plain pairs are dissolved where a shared-donor family is strictly better). Result: **890
   families, entrance rank 1,719, 1,903 helpers, 96 donors shared by two or more families**, cuts {676,559: 488;
   680,080: 89; 700,582: 63; 727,593: 250}; 60,520 initial reads removed, 2,286 basis gates paid, raw rank mass
   434,177 → 432,458.
2. **PR #263's 25 concave-descent gate retimings** (rohanarun; stage `code/descent_retiming.py`, selection rebound to
   this transcript by full scalar-core alignment; −1 local call) and **PR #270's 29 connected-block plateau
   retimings of 57 ADDs** (utcorvusvolat-dotcom; stages `code/plateau_retiming.py`, `verify_plateau_spans.py`,
   `verify_frame_tables.py`; calls and mass unchanged, rank distribution improved).
3. **eumemic's target-prefix compression** (PR #268) as rohanarun's native stage of PR #273 (`code/target_prefix.py`,
   verbatim): 209 squares of four targets whose prefix responses are F₂-dependent; the dependent target's 1,057
   frame-20 reads are omitted and replaced by a zero-frame setup at the cut and a restoration at the square's
   common 21-dimensional frame (+5.23·10⁻⁷).
4. **evmckinney9's cleanup sandwiches** (PR #271): kernel pivots whose only gates after their cut are the full-frame
   cleanup t += a; a += b; t += a are rewritten to stop at dimension 4 instead of climbing to the full frame
   (rank-23 banked endpoints become rank-3 partial swaps). On this word the pivot role of 83 two-member families is
   assigned to the member with the sandwich shape (cost-neutral for the kernel transform), which raises the count of
   admissible sandwiches from 45 to 128, of which 126 are retired (the bank re-tiling needs a multiple of 3): +2.02·10⁻⁶,
   the largest single lever here.

| stage (each on the previous word) | pivot families / entrance rank | normalized stock W | κ |
|---|---|---|---|
| PR #259 | 518 / 1,344 | 173,435 | 7.11029386054035·10⁻⁴ |
| kernel families: twins, headroom, shared donors | **890 / 1,719** | 173,310 | 7.11462218·10⁻⁴ |
| + PR #263 descent (25 gates) + PR #270 plateau (29 blocks) retimings | 890 / 1,719 | 173,310 | 7.11482139228173·10⁻⁴ |
| + target-prefix compression (209 squares) — seven native checkers' word | 890 / 1,719 | 173,310 | **7.12005174354669·10⁻⁴** |
| + 126 cleanup sandwiches (pivot roles swapped in 83 families) | 890 / 1,719 | **172,470** | **7.14026746429965·10⁻⁴** |

For comparison, PR #270 (887 families, rank 1,716) is 7.11457853·10⁻⁴, PR #273 (target squares on #269) 7.11948954·10⁻⁴,
PR #271 (99 sandwiches on #272's word) 7.13662156·10⁻⁴ and PR #275 7.13690108·10⁻⁴.

The deficit 120·W − mass = 35,200 per replica is invariant under all of these rewrites (a pivot's residual 24 → 23
shrinks the bank capacity by exactly the mass it saves), so the exponent moves through the log-weighted mass
Σ r·n·ln(120/r) alone; every family and every retiming is admitted or rejected by PR #259's exact pricer on the whole
word, never added as an estimate. [PROOF.md](PROOF.md) states the delta and the checks; PR #259's notes are kept
unchanged as `README-PR259.md`, `PROOF-PR259.md`, `KERNEL-PROOF.md`, `BANK-PROOF.md`, `COPY-PROOF.md`, `FINITE-PROOF.md`,
`REVIEW.md`.

Conditional, finite construction under the same retained public all-size hypotheses as PR #249/#254/#259 (no Lean
certificate, no unconditional theorem). κ is the bit-bound value: the complex supplier of this lineage stands at
7.5474·10⁻⁴ five-stage (PR #256, Lean-checked in jacobalansussman/wht-power-saving-lean#2), so the bit supplier binds.
The sandwich stage is certified as PR #271 certifies it (PROOF.md, section 5): PR #259's native bank review and
price driver assume every helper ends at the full frame, so that part rests on the native legality, prefix and
five-stage checkers on the new word, exact endpoint charts with the bank re-tiling, the unchanged price engine
through PR #271's histogram wrapper, and the native finite invoice; `RESULT.json` carries both κ values. Not composed:
PR #272's frame-filtered collective kernels, PR #275's zero-frame target restores, the fixed-prime refinement of
PR #261/#265 (+4·10⁻¹²).

## Verify

    sudo apt-get install -y g++ libboost-dev            # Linux; macOS: brew install boost, --cxx clang++ with a bits/stdc++.h shim
    python -m pip install -r research/multicut-kernel-composition/requirements.txt    # sympy 1.14.0
    python3 -I research/multicut-kernel-composition/verify.py --output /tmp/mkc-replay      # fresh directory outside the package; about 4 minutes

PR #259's verifier with the stages inserted (02b descent, 02c–02e plateau and its audits, 02f target prefix, then the
seven native checkers 03–08, then 09–17 the sandwich stage with its legality, prefix, five-stage, endpoint/bank,
price-wrapper and finite-invoice checks), every stage gated by the sha256 of the transcript it consumes: package
hashes against `MANIFEST.json`, regeneration of the pinned PR #249 word from `vendor/pr249-source.zip` (SymPy), the
checkers compiled and run, every receipt compared with `expected/` and `expected-sandwich/` (platform-independent
fields), then `PASS: kappa = 0.000714026746429965`. `--snapshots-only` skips the upstream
regeneration. `.github/workflows/multicut-kernel-composition.yml` runs it on Ubuntu (Python 3.11 and 3.13).

## Files

PR #259's package (`code/cohort-*.cpp`, `code/export249.py`, `inputs/249-*`, `inputs/frames.json.gz`,
`inputs/SNAPSHOTS.json`, `vendor/`, the proof notes, `requirements.txt`, `LICENSE`) with the frozen selection
`inputs/candidates.json.gz` (PR #259's 518 items, then ours with `round` = `union-early-cut`, `headroom-2`,
`shared-donor`, with `+pivot-swap` where the pivot role was moved), PR #263's and PR #270's stages
(`code/descent_retiming.py`, `code/plateau_retiming.py`, `code/verify_frames.py`, `code/verify_plateau_spans.py`,
`code/verify_frame_tables.py`; `inputs/descent-selection.json`, `inputs/plateau-selection.json`, rebound to this
transcript), PR #273's `code/target_prefix.py` with `inputs/target-selection.json` (rebound), PR #271's mechanism as
`code/cleanup_sandwich.py`, `code/sandwich_endpoints.py`, `code/sandwich/price-histogram.cpp` with
`inputs/sandwich-selection.json`, `verify.py` (PR #259's with the stages and sha gates), `expected/` (twelve receipts)
and `expected-sandwich/` (eight), `RESULT.json`, `MANIFEST.json`, `discovery/` (the censuses, merges, the rebinding
chain and the sandwich scan; not run by the verifier), `README.md`, `PROOF.md`, `NOTICE.md`.
