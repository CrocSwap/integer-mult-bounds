# five-stage-gen4-kernel-pairs

**Conditional κ = 180985932153783 / (25·10¹⁶) = 7.23943728615132·10⁻⁴** (+0.1485% over PR #276's
7.22869827347495·10⁻⁴; +0.0514% over PR #279's 7.23571590007464·10⁻⁴). Without PR #279's retiming, the kernel pairs
alone on PR #276's word give 7.23241244294406·10⁻⁴ (+0.0514% over PR #276).

PR #276 (DreamingOfClouds) ships a new paired-cube bit word, gen4, in eumemic's source527 five-stage completed-bank
package; it carries none of the entrance levers developed on the older PR #249 word. This package adds the first of
them, the response-kernel twin pairs of PR #254/#268, to the gen4 word, composed with PR #279's 880-gate
concave-descent retiming (rohanarun), both as stages of the same six-int transcript pipeline:

* **424 twin dirty-helper pairs with per-pair cuts.** On gen4 the compensation reads are chronological (each
  helper's reads precede its first other use, by at least 41,247 records), so there is no single prefix cut; each
  pair gets its own cut at the later of its two helpers' last zero-frame reads. The pivot's initial reads (about 22
  each, 9,120 in all) are deleted, it enters at a nondegenerate rank-one line E of both first frames, the donor pays
  b += a at E after the cut and b −= a at the full frame. Of 568 admissible pairs, the 424 with negative φ-gain
  (first-frame dims (2, 2) × 220, (3, 3) × 180, (3, 5) × 24) are selected; the ledger model is maximal there.
* **Checks.** `kernel_transform.replay` runs every formal column (19,930) forward and inverse on the emitted word
  with both omitted-gate controls rejected; the stream frame paths are rebuilt independently of the MOVEs; then all
  of #276's stages run fresh: virtual, raw, bit, scalar (with its eleven controls), primes (512 charts, at most 576
  factors), banks (rank-23 residuals tiled by 6,360 (23⁴, 4⁷) banks per stage, every bank width 120 and full),
  complex, math and finite. Every #276 literal that the rewrite changes is a recomputed pinned value in
  `expected/kernel-pins.json` asserted by `pins.pin`; no check is dropped ([KERNEL-PROOF.md](KERNEL-PROOF.md)).

| one invocation, m = 120 | PR #276 | PR #279 | this package |
| --- | ---: | ---: | ---: |
| entrances (ranks) | 2,466 (20, 21) | 2,466 | **2,890 (1 × 424, 20 × 2200, 21 × 266)** |
| one-stage paid rank mass | 425,742 | — | 425,318 |
| literal stock, 60 replicas | 1,283,035 | — | **1,281,975** (banks per stage 172,127 → 171,915) |
| κ | 7.22869827347495·10⁻⁴ | 7.23571590007464·10⁻⁴ | **7.23943728615132·10⁻⁴** |

Conditional, finite construction under the retained public all-size hypotheses of the source527 lineage (no Lean
certificate). The bit side binds (bit coarse 7.24468·10⁻⁴, complex 7.47455·10⁻⁴). PR #279 is a draft at the time of
writing; its stage is vendored unchanged and its correctness claims are inherited, not re-proved (one composition
detail: the used-frame inventory passed to the prime check keeps the inherited producer inventory, a superset).

## Verify

    python -m pip install -r research/five-stage-gen4-kernel-pairs/requirements.txt    # sympy 1.14.0
    python3 -B research/five-stage-gen4-kernel-pairs/verify.py --output /tmp/gen4-kernel-pairs-verification   # about 5 minutes; not under -I
    python3 -B research/five-stage-gen4-kernel-pairs/gen4bit/producer/regenerate.py --work /tmp/gen4-regeneration   # PR #276's generator check

`verify.py` is #276's with the kernel stage required (`REQUIRED += 'kernel'`), its receipt saved and κ pinned; it
refuses pin-recording mode. The workflow `.github/workflows/five-stage-gen4-kernel-pairs.yml` runs both commands on
Ubuntu with Python 3.11 and 3.13.

## Files

#276's package with: `kernel_transform.py`, `kernel-selection.json`, `pins.py`, `expected/kernel-pins.json`,
`KERNEL-PROOF.md`, `descent_transform.py` and `descent-selection.json` (#279), the modified `portable_bit.py`,
`raw_ledger.py`, `code/global_lowering.py`, `bank_template.py`, `bank_check.py`, `scalar_check.py`,
`prime_check.py`, `math_check.py`, `finite_check.py`, `verify.py`, `discovery/` (census, selection, pin generation,
manifest; not run by the verifier), `README.md`, `PROOF.md`, `NOTICE.md`, `MANIFEST.json`; #276's README/PROOF
kept as `README-PR276.md`, `PROOF-PR276.md`.
