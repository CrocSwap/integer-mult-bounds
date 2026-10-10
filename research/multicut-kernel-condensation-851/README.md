# multicut-kernel-condensation-851

**Conditional κ = 177850930927433 / 250000000000000000 = 7.11403723709732·10⁻⁴** (+0.0526% over PR #259's
7.11029386054035·10⁻⁴; +0.0523% over PR #263's 7.11032238200698·10⁻⁴).

PR #259 (Dugongue) condenses response kernels of the PR #249 bit word at four cuts with 518 pivot families. Its
earliest cut, record 676,559 — the last initial compensation read — carries only 103 of them. A census of the
twin dirty helpers at that cut (helpers untouched before it whose complete F₂ target responses coincide) finds
985 twin pairs; 335 of them are disjoint from every helper PR #259 uses and have a nondegenerate rank-one common
entrance line, and 333 of those (two dropped to keep the entrance rank ≡ 0 mod 3, as the transform requires at
40 replicas) are net-positive under the fixed-deficit ledger. Added to PR #259's 518 families, verbatim, they give

| | PR #259 | this package |
|---|---|---|
| pivot families / entrance rank | 518 / 1,344 | **851 / 1,677** |
| initial compensation reads removed / basis gates paid | 27,772 / 1,542 | 52,752 / 2,208 |
| raw rank mass per invocation | 434,177 → 432,833 | 434,177 → **432,500** |
| literal bank stock / normalized | 867,175 / 173,435 | **866,620** / 173,324 |
| κ | 7.11029386054035·10⁻⁴ | **7.11403723709732·10⁻⁴** |

The 333 added entries use PR #259's own mechanism unchanged: the pivot starts at the common line E (its four
initial reads are deleted), the partner moves to E and absorbs the pivot there, and the inverse gate is paid at the
full frame. 319 of them have first frames (2, 2) and a line u = eᵢ − eⱼ (norm 2, cleared Gram 18 for G = I − J/9),
which PR #254's chart rule excluded (`norm == 4`) and PR #259's generic exact chart audit admits (prime
exclusion {2, 3}, the same as the ±1-four lines); the remaining 14 are (3, 5), (3, 3) and (3, 6) pairs with ±1-four
lines. **No checker, no C++ line and no proof note of PR #259 is changed**: the only inputs that differ are the
frozen selection `inputs/candidates.json.gz` (PR #259's 518 items byte for byte, then the 333 new ones in its
schema with `round = "union-early-cut"`) and the seven regenerated receipts in `expected/`; `RESULT.json` and
`MANIFEST.json` follow. PR #259's seven native checkers pass on the new word (all-column F₂ replay forward and
inverse with omitted-Q and omitted-Q⁻¹ controls; chronological legality with COPY/ERASE windows and source
owners; 1,497,760 per-cut target-kernel equalities; 851 exact projector charts, 3,317,400 bank assignments; the
five-stage F₂ columns; the exact rational price with 47 outer constraints, adjacent grid rejected; the finite
invoice). [PROOF.md](PROOF.md) states the delta; PR #259's own notes are kept unchanged as `README-PR259.md`,
`PROOF-PR259.md`, `KERNEL-PROOF.md`, `BANK-PROOF.md`, `COPY-PROOF.md`, `FINITE-PROOF.md`, `REVIEW.md`.

This is a conditional, finite construction under the same retained public all-size hypotheses as PR #249/#254/#259
(not a Lean certificate, not an unconditional theorem). κ is the bit-bound value: the complex supplier of this
lineage stands at 7.0991·10⁻⁴ three-stage (PR #233) and 7.5474·10⁻⁴ five-stage (PR #256, Lean-checked in
jacobalansussman/wht-power-saving-lean#2), so the bit supplier still binds.

## Verify

    sudo apt-get install -y g++ libboost-dev            # Linux; macOS: brew install boost, --cxx clang++ with a bits/stdc++.h shim
    python -m pip install -r research/multicut-kernel-condensation-851/requirements.txt    # sympy 1.14.0
    python3 -I research/multicut-kernel-condensation-851/verify.py --output /tmp/mc851-replay    # fresh directory outside the package; about 70 s

PR #259's verifier, unchanged: it checks every package hash against `MANIFEST.json`, regenerates the pinned PR #249
word from `vendor/pr249-source.zip` (SymPy), compiles the seven checkers, emits the new word from the frozen
selection, runs every check and compares each receipt with `expected/` (platform-independent fields only; see
PROOF.md, "Receipts"), then prints `PASS: kappa = 0.000711403723709732`. `--snapshots-only` skips the upstream
regeneration (about 20 s). `.github/workflows/multicut-kernel-condensation-851.yml` runs it on Ubuntu.

## Files

Everything of PR #259's package (`code/`, `inputs/`, `vendor/`, `expected/`, the proof notes, `verify.py`,
`requirements.txt`, `LICENSE`) with the two input changes above; `discovery/` (the census, the comparison with
PR #259's selection and the merge, not run by the verifier: `twins.py`, `chrono2.py`, `gain.py`,
`gen_candidates.py`, `compare259.py`, `merge259.py`); `README.md`, `PROOF.md`, `NOTICE.md`, `RESULT.json`,
`MANIFEST.json`.
