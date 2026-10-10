# multicut-kernel-composition

**Conditional κ = 711482139228173 / 10¹⁸ = 7.11482139228173·10⁻⁴** (+0.0637% over PR #259's 7.11029386054035·10⁻⁴;
+0.0034% over PR #270's 7.11457853376510·10⁻⁴, the best kernel-condensation rung before this one).

PR #259 (Dugongue) condenses response kernels of the PR #249 bit word with 518 pivot families at four cuts. This
package composes, on that word and with PR #259's seven native checkers and pricer unchanged:

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

| | PR #259 | PR #270 | this package |
|---|---|---|---|
| pivot families / entrance rank | 518 / 1,344 | 887 / 1,716 | **890 / 1,719** |
| normalized stock W / child calls / rank mass | 173,435 / 3,956,840 / 20,777,000 | 173,311 / 3,970,720 / 20,762,120 | **173,310 / 3,970,400 / 20,762,000** |
| literal bank stock / exact charts | 867,175 / 518 | — | 866,550 / 919 |
| κ | 7.11029386054035·10⁻⁴ | 7.11457853376510·10⁻⁴ | **7.11482139228173·10⁻⁴** |

The deficit 120·W − mass = 35,200 per replica is invariant under all of these rewrites (a pivot's residual 24 → 23
shrinks the bank capacity by exactly the mass it saves), so the exponent moves through the log-weighted mass
Σ r·n·ln(120/r) alone; every family and every retiming is admitted or rejected by PR #259's exact pricer on the whole
word, never added as an estimate. [PROOF.md](PROOF.md) states the delta and the checks; PR #259's notes are kept
unchanged as `README-PR259.md`, `PROOF-PR259.md`, `KERNEL-PROOF.md`, `BANK-PROOF.md`, `COPY-PROOF.md`, `FINITE-PROOF.md`,
`REVIEW.md`.

Conditional, finite construction under the same retained public all-size hypotheses as PR #249/#254/#259 (no Lean
certificate, no unconditional theorem). κ is the bit-bound value: the complex supplier of this lineage stands at
7.5474·10⁻⁴ five-stage (PR #256, Lean-checked in jacobalansussman/wht-power-saving-lean#2), so the bit supplier binds.
Two other levers on the same word are not composed here: eumemic's target-prefix compression (PR #268, PR #273 on
#269, PR #272 on collective kernels) and evmckinney9's cleanup sandwiches (PR #271); PR #272 stands above this package.

## Verify

    sudo apt-get install -y g++ libboost-dev            # Linux; macOS: brew install boost, --cxx clang++ with a bits/stdc++.h shim
    python -m pip install -r research/multicut-kernel-composition/requirements.txt    # sympy 1.14.0
    python3 -I research/multicut-kernel-composition/verify.py --output /tmp/mkc-replay      # fresh directory outside the package; about 3 minutes

PR #259's verifier with the two retiming stages inserted between its transform and its checkers (stages 02b–02e,
each gated by the sha256 of the transcript it consumes): package hashes against `MANIFEST.json`, regeneration of the
pinned PR #249 word from `vendor/pr249-source.zip` (SymPy), the seven checkers compiled and run, the descent and
plateau stages with their own audits (operand source spans, frame tables), every receipt compared with `expected/`
(platform-independent fields), then `PASS: kappa = 0.000711482139228173`. `--snapshots-only` skips the upstream
regeneration. `.github/workflows/multicut-kernel-composition.yml` runs it on Ubuntu (Python 3.11 and 3.13).

## Files

PR #259's package (`code/cohort-*.cpp`, `code/export249.py`, `inputs/249-*`, `inputs/frames.json.gz`,
`inputs/SNAPSHOTS.json`, `vendor/`, the proof notes, `requirements.txt`, `LICENSE`) with the frozen selection
`inputs/candidates.json.gz` (PR #259's 518 items, then ours with `round` = `union-early-cut`, `headroom-2`,
`shared-donor`), PR #263's and PR #270's stages (`code/descent_retiming.py`, `code/plateau_retiming.py`,
`code/verify_frames.py`, `code/verify_plateau_spans.py`, `code/verify_frame_tables.py`; `inputs/descent-selection.json`,
`inputs/plateau-selection.json`, rebound to this transcript), `verify.py` (PR #259's with the stages and three
sha gates), `expected/` (eleven receipts), `RESULT.json`, `MANIFEST.json`, `discovery/` (the censuses, merges and
the rebinding chain; not run by the verifier), `README.md`, `PROOF.md`, `NOTICE.md`.
