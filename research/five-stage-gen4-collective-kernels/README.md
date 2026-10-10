# five-stage-gen4-collective-kernels

**Conditional κ = 724733001963261 / 10¹⁸ = 7.24733001963261·10⁻⁴** (+0.258% over PR #276's 7.22869827347495·10⁻⁴;
+0.161% over PR #279's 7.23571590007464·10⁻⁴). The first version of this package (424 twin pairs, entrance rank 1)
gave 7.23943728615132·10⁻⁴ with PR #279's retiming and 7.23241244294406·10⁻⁴ without it.

PR #276 (DreamingOfClouds) ships a new paired-cube bit word, gen4, in eumemic's source527 five-stage completed-bank
package; it carries none of the entrance levers developed on the older PR #249 word. This package adds, as stages of
#276's own six-int transcript pipeline after PR #279's 880-gate concave-descent retiming (rohanarun, vendored
unchanged), **695 response-kernel entries with per-entry cuts**:

* **416 twin pairs entering on a line** (e = 1; PR #254/#268's mechanism): a pivot whose complete F₂ target response
  equals its donor's; the pivot's compensation reads are deleted, it enters at a nondegenerate rank-one line of both
  first frames, the donor pays d += p there after the cut and d −= p at the full frame.
* **24 twin pairs entering on their full 16-dimensional intersection** (e = 16): the same pairs cost almost nothing
  more and the pivot's first move falls by 16 ranks; each is worth more than ten line pairs.
* **255 multi-donor families** (208 quadruples, 47 triples): the pivot's response is the XOR of two or three donors'
  responses; all members share a nondegenerate common entrance E of dimension e (1 to 18; mostly e = r − 1 or
  r − 2 for equal first dimensions r), the pivot enters at E, each donor pays its shear at E and the inverse at the full
  frame; 59 donors serve several entries along nested entrance chains.

On gen4 the compensation reads are chronological, so each entry has its own cut, bound by content. The entries were
found by two censuses of the 13,944 plain dirty helpers (`discovery/`): the twin census (1,568 twin classes, 568
pairs with a nondegenerate common line) and the collective census (low-weight F₂ circuits of the 12,352 distinct
responses: 3,158 triangles and 23,421 quadruples; common-frame filter; φ-ledger packing with shared-donor chains;
quintuples are never net-positive). Total entrance rank 2,028; 12,520 compensation reads deleted, 2,316 setup and
restore gates paid; one-stage paid rank mass 425,742 → 423,714; literal stock 1,283,035 → 1,277,965 (banks per stage
172,127 → 171,113).

**Checks.** `kernel_transform.replay` runs every formal column (19,930) forward and inverse on the emitted word with
both omitted-gate controls rejected (2,713 / 1,061 wrong rows), checks the prefix relation (pivot response = XOR of
the donors' responses) on the literal prefix for every entry, rebuilds the stream frame paths independently of the
MOVEs and checks the nested donor chains; then all of #276's stages run fresh — virtual, raw, bit (with #279's
descent), scalar (eleven controls), primes (every entrance basis factored, 664 charts, at most 576 factors,
normalizer bound 815), banks (every residual width r tiled by (r⁴, 4³⁰⁻ʳ) banks, every bank width 120 and full;
20 pattern kinds; selector calls 963,705,578,400 < 2⁴⁰), complex, math and finite, with ten omitted-stage negative
controls; the geometry stage checks an actual entrance basis for every new rank. Every #276 literal the rewrite
changes is a recomputed pinned value in `expected/kernel-pins.json` asserted by `pins.pin`; no check is dropped
([KERNEL-PROOF.md](KERNEL-PROOF.md) lists them).

| one invocation, m = 120 | PR #276 | PR #279 | this package |
| --- | ---: | ---: | ---: |
| entrances (ranks) | 2,466 (20, 21) | 2,466 | **3,161** (1 × 476, 2 × 93, 4 × 29, 5–18 × 97, 20 × 2,200, 21 × 266) |
| one-stage paid rank mass | 425,742 | — | **423,714** |
| literal stock, 60 replicas / banks per stage | 1,283,035 / 172,127 | — | **1,277,965 / 171,113** |
| κ | 7.22869827347495·10⁻⁴ | 7.23571590007464·10⁻⁴ | **7.24733001963261·10⁻⁴** |

Conditional, finite construction under the retained public all-size hypotheses of the source527 lineage (no Lean
certificate). The bit side binds (bit coarse 7.25259·10⁻⁴, complex 7.47455·10⁻⁴). PR #279 is a draft at the time of
writing; its stage is vendored unchanged and its correctness claims are inherited, not re-proved. PR #283 and PR #284
compose further levers (terminal sinks, transported entrances, early restorations, target squares) on the same word
in Dugongue's native pipeline and stand above this package; this one is the standalone construction in #276's own
Python pipeline, with the collective families as its contribution.

## Verify

    python -m pip install -r research/five-stage-gen4-collective-kernels/requirements.txt    # sympy 1.14.0
    python3 -B research/five-stage-gen4-collective-kernels/verify.py --output /tmp/gen4-collective-kernels-verification   # about 8 minutes; not under -I
    python3 -B research/five-stage-gen4-collective-kernels/gen4bit/producer/regenerate.py --work /tmp/gen4-regeneration   # PR #276's generator check

`verify.py` is #276's with the kernel stage required and κ pinned; it refuses pin-recording mode. The workflow
`.github/workflows/five-stage-gen4-collective-kernels.yml` runs both commands on Ubuntu with Python 3.11 and 3.13.

## Files

#276's package with: `kernel_transform.py`, `kernel-selection.json` (695 entries), `pins.py`, `expected/kernel-pins.json`,
`KERNEL-PROOF.md`, `descent_transform.py` and `descent-selection.json` (#279), the modified `portable_bit.py`,
`raw_ledger.py`, `code/global_lowering.py`, `code/geometry527.py`, `bank_template.py`, `bank_check.py`,
`scalar_check.py`, `prime_check.py`, `math_check.py`, `finite_check.py`, `verify.py`, `discovery/` (censuses, selection
builders, pin generation, manifest; not run by the verifier), `README.md`, `PROOF.md`, `NOTICE.md`, `MANIFEST.json`;
#276's README/PROOF kept as `README-PR276.md`, `PROOF-PR276.md`.
