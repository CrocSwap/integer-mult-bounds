# PR6030 precision envelope uses the complete paid rank mass

**Scoped identity; no new κ.** Assumption ID `precision_tape`, card
`uniform-transfer-audit`. On the selected PR6030 invoice, the application
review's coordinate envelope `2^(10^9+240152f)` is `2^(B + R f)` where
`R = 240152` is the complete paid rank mass and `B = 10^9` is the recorded
raw budget. The recounted caller bound is not the exponent that sentence uses.

This does not prove the majorants, so it does not discharge `precision_tape`.

## Scope and evidence

Original card: `uniform-transfer-audit`. Scope status: **refined**. The card
asks for one assumption and one caller-bound implication. The implication
checked here is the published envelope's exponent, not a universal precision
theorem. [#5625](https://github.com/CrocSwap/integer-mult-bounds/pull/5625)
row reentry and [#5707](https://github.com/CrocSwap/integer-mult-bounds/pull/5707)
root-prefix lowering stay partial interfaces; neither is treated as a
discharge of the five selected assumptions.

The proof is in [PROOF.md](PROOF.md). Pins are in [SOURCES.json](SOURCES.json).

The complete histogram `complete_cost.paid` in
`research/p104-helper470-twin-rung-removal/RESULT.json` has rank mass
`240152` and `66834` calls. `complete_cost.targets` has rank mass `240912`
and `13444` fields. The surplus is `760`. Those are the figures named in
`docs/research/pr-intake-evidence/pr6030-audit/PROOF-REVIEW.md`.

`nonrecursive.local_paid_rank_mass` is `5952`. The nonrecursive growth note
tells a reader to use that local mass for the whole word. That coefficient
does not reproduce the published envelope. The envelope matches the expanded
histogram.

`nonrecursive.raw_budget` is `10^9`. The review's caller bound
`126,626,680` and allowance `184,647,552` are strictly smaller. Spending the
budget instead of the caller bound leaves an exponent slack of `873373320`,
so the published envelope is larger by `2^873373320` than the same lemma
with the caller bound in the exponent. The review states the caller bound
and still writes `10^9`.

## Reproduce

Python 3.12, standard library, from the repository root:

```sh
python3 -I -B research/pr6030-precision-envelope-mass/verify.py
python3 -I -O -B research/pr6030-precision-envelope-mass/verify.py
python3 -B scripts/research_package.py --package research/pr6030-precision-envelope-mass
```

The verifier prints `PASS_PR6030_PRECISION_ENVELOPE_MASS` with
`paid_rank_mass=240152`, `caller_slack=873373320`,
`precision_tape_discharged=false`, and `no_new_kappa=true`. Checks raise
exceptions, so `-O` does not disable them.

`python3 -B scripts/research_selected_baseline.py` is orientation only. It
is not a supplier replay. No Lean, Docker, or `make frontier6030-verify`
run was part of this package.

## Open next questions

1. Do the selected caller's scalar and dyadic factors have row-l1 majorant
   at most 2, and its rank-`r` Gaussians majorant at most `2^(r f)`, with
   every majorant at least 1? The exponent identity applies to the caller
   only under those bounds. First step: one scalar ADD and one rank-`r`
   Gaussian, including a COPY into a nonzero residual. Blocked by the
   inherited `precision_tape` and `owned_erasure` premises.
2. Can `10^9` in this sentence be replaced by `126626680`? That would shrink
   the envelope by `2^873373320` for every `f`. First step: count
   non-Gaussian elementary factors in the admitted caller. Blocked because
   the pinned invoice does not contain that count.

## Credit

The invoice is DreamingOfClouds' PR6030 package
`research/p104-helper470-twin-rung-removal`. The envelope sentence is the
PR6030 application review by Douglas Colkitt with OpenAI Codex assistance.
Ali Romman, Mason Hale, Pierre-Loic Doulcet, Matarener, Chris R /
Clear1nsight, and the retained native, compiler, and analytic lineage keep
the credit recorded in that review.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
