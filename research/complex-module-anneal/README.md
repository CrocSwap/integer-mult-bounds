# complex-module-anneal

**A stronger complex supplier from re-annealed complex modules (no new κ).** The source-assisted complex word of PR
#184/#194 calls three query modules: PR #168 v4's pair module (n = 10), all-but-one module (n = 9) and
disjoint-triple module (p = 11). This package replaces the three module files by re-annealed ones, annealed against
the exact compile ledger of the aligned word, and compiles the word with one frozen recipe. With PR #233's
maximum-weight reuse pairs the word is one explicit gcert/1 program of 11,800 numbered registers (R = 9,160 slots
instead of 9,412) that Jacob Sussman's reference checker `gx.check1` and his Python mirror of the two Lean checks
(`gxcore.py`, both vendored unchanged) accept. Priced in his bridged five-stage layout (Lean-checked there for his
certificate of #193; these programs are checked by the two Python checkers and exact rational bounds, with no Lean
build) it is certified at

**a = 7635/10⁷ (7636/10⁷ rejected), against 7547/10⁷ for PR #233's word (PR #256): +1.17%.**

The same recipe applied to PR #168 v4's own modules is the control: 7522/10⁷, so the modules alone add +1.50% on the
certified grid points (+1.51% on the numerical roots), apples to apples. With PR #193's parity-avoiding pairs the
result is 7586/10⁷ against a control of 7469/10⁷ (+1.57%). **No new κ by itself:** on the current frontier (PR
#299, chafreaky: κ = 7.49899215319498e-4) the bit supplier (coarse, 7.50462e-4) is 0.57% below the complex price of
PR #233's word (7.54736e-4) and below both re-annealed prices (7586/10⁷ and 7635/10⁷), so this package raises the
complex cap from 7.547e-4 to 7.635e-4 (+1.17%). The five-stage ledger formula is applied at R = 9,160, as the bit
packages apply their layout at several R; confirmation is left to the layout's authors. [PROOF.md](PROOF.md) states
the claim and the chain of checks.

| program (gcert/1, five-stage layout m = 110, W = 4v + R) | modules | pairs | R | blocks | N | gx.check1 and gxcore | saving a |
|---|---|---|---|---|---|---|---|
| PR #194 word (anchor = PR #256's certificate, Sussman's #193 histogram) | PR #168 v4 | PR #193's | 9,412 | 70,169 | 262,944 | accepted | 7474547/10¹⁰ (Sussman, Lean; not repriced here) |
| control, parity recipe | PR #168 v4 | PR #193 recipe | 9,412 | 70,295 | 262,944 | accepted | 7469/10⁷ |
| control, mw recipe | PR #168 v4 | PR #233 recipe | 9,412 | 69,827 | 262,944 | accepted | 7522/10⁷ |
| **result, parity recipe** | **re-annealed** | PR #193 recipe | **9,160** | 69,384 | 257,400 | accepted | **7586/10⁷** |
| **result, mw recipe** | **re-annealed** | PR #233 recipe | **9,160** | 68,942 | 257,400 | accepted | **7635/10⁷** |

The recipe (fresh carrier arcs, PR #200's descended operation frames) is slightly weaker than PR #168's inherited
physical layer on PR #168's own modules (7469 vs 7474.5 and 7522 vs 7547 per 10⁷: −0.07% and −0.33%), which is why
the control, not the official numbers, measures the modules. The re-annealed modules are not uniformly smaller: the
all-but-one module is (29 additions against 31), but the total is larger (2,462 against 2,353; pair module 366 vs
356, triple module 2,067 vs 1,966). They are cheaper to compile: the frame flow keeps 252 fewer slots.

## Verify

    python -m pip install numpy==2.3.5 scipy==1.17.0        # for the pinned regeneration and the checkers
    python3 -B research/complex-module-anneal/verify.py      # about 12 minutes; -O is refused

The script checks every pin of `SOURCE.json`, rebuilds the 308 pinned files of PR #202 from the vendored PR #233
package and regenerates the producer word and the source-aligned word (PR #194's pipeline). Two anchors follow:
`aligned_word.py` reproduces the seven output files of `source_aligned_local_v4.py` byte for byte, and PR #194's word
run through this package's chain is PR #256's certificate (same sha256) with Sussman's #193 histogram. Then, for each
module set and pair recipe, it installs the modules and the frozen layer, re-checks the pairs with `paircheck.py`
(five mutation controls), admits the layer with PR #200's complete complex checker, runs PR #184's flow and exact
lift and PR #194's contract, emits the gcert/1 program with PR #256's `gcert_emit.py` (unchanged), runs `gx.check1`,
checks the ledger, writes the scatter as the star rule with `normalize_scatter.py` and runs `gx.check1` and
`gxcore.py`'s mirror on that program, certifies the five-stage moment at the claim of `SOURCE.json` with the next
10⁻⁷ grid point rejected, and compares the four committed programs byte for byte (uncompressed JSON) with
`certificates/` and the run with `certificate/expected.json`. `--temp-root` chooses scratch storage.

The emitter writes the two re-annealed programs with a scatter table: the exact lift leaves the retained totals of
coordinates 20 and 21 in registers whose unit is −1. `normalize_scatter.py` flips the sign convention of those two
registers over the whole program (50 coefficients change sign) and writes the star rule, which is what the five-stage
packages' complex code reads; registers, frames, gates, blocks and N are unchanged, and both forms pass `gx.check1`.
The control programs are already in star form and are committed as emitted.

To check a certificate with Sussman's other tools (not run for this package):

    python3 -B tools/gx/refcheck.py <this package>/certificates/gcert1-p11-cmod-mw-flow.json.gz   # in his repository
    python3 -B tools/gx/gxdry.py    <this package>/certificates/gcert1-p11-cmod-mw-flow.json.gz   # mirror and price

## Re-pinning after a module changes

    python3 -B research/complex-module-anneal/discovery/make_layer.py --set cmod --tmod <new tmod.json>   # ~5 min
    python3 -B research/complex-module-anneal/verify.py --write
    python3 -B research/complex-module-anneal/verify.py

`make_layer.py` (discovery, never run by `verify.py`) applies the same recipe to the new module set, copies a module
given from outside into `modules/`, writes `layers/cmod/` and records the set's module files in `SOURCE.json`.
Delete the superseded module file from `modules/` before `--write` (otherwise it stays pinned, harmless but
confusing). `--write` re-pins `modules/` and `layers/` (no other pin), sets every claim to the largest 10⁻⁷ grid
point its exact bounds certify, and rewrites `certificates/` and `certificate/expected.json`; the numbers in this file
and in PROOF.md are then updated by hand.

## Files

`verify.py`; `aligned_word.py` (PR #194's source-aligned word with the module files and a frozen layer as inputs);
`paircheck.py` (independent re-check of the reuse pairs, five mutation controls); `normalize_scatter.py` (the star
scatter by re-signing retained-total registers); `modules/` (the three re-annealed module files:
`pmod_cmod_dropin.json`, `qmod_cmod.json`, `tmod_cmod_v2.json`); `layers/pr168-v4/` and `layers/cmod/` (frozen carrier
arcs, operation frames, reuse pairs of both recipes, kernel pairs);
`certificates/gcert1-p11-{pr168-v4,cmod}-{parity,mw}-flow.json.gz` (the four committed programs, star form, about
0.5 MB each); `certificate/expected.json`; `gcert_emit.py`, `gx/gx.py`, `scripts/moment.py` and `references/`
vendored byte for byte from PR #256 (PR #233's package with the PR #202 baseline, Sussman's #193 histogram);
`gx/gxcore.py` (Sussman's `tools/gx/gxcore.py` at `f010392c`, unchanged); `discovery/` (how the layers were found;
not run by `verify.py`); `SOURCE.json`, `PROOF.md`, `NOTICE`. `.github/workflows/complex-module-anneal.yml` runs the
verifier on Python 3.11 and 3.13.
