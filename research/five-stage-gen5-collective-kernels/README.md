# Compatible gen5 retiming and collective kernels

Conditional κ = **0.000744719882668682**, from the exact composition of 65
kernel-disjoint PR289 retimings with all 450 PR290 kernel entries.
See [COMPOSITION-PROOF.md](COMPOSITION-PROOF.md) for the selection, accounting,
reproducibility repair, credits, and unchanged conditional scope.

The original PR290 description below is retained as historical context; its
κ = 0.000744714499357628 is the parent baseline.

---

# five-stage-gen5-collective-kernels

**Conditional κ = 186178624839407 / (25·10¹⁶) = 7.44714499357628·10⁻⁴** (+0.0798% over PR #287's 7.44120696397042·10⁻⁴;
+0.259% over PR #285's gen5 word).

PR #285 (DreamingOfClouds) ships the gen5 bit word; PR #287 (rohanarun) adds a 904-gate concave-descent retiming and
220 target-prefix squares as stages of its pipeline. This package adds the collective response-kernel stage of #282/#284
after them, re-derived on the gen5 word: **450 entries with per-entry cuts** — 260 twin pairs (244 entering on a line,
16 on a rank-3 entrance) and 190 multi-donor families (151 quadruples, 39 triples; the pivot's complete F₂ target
response is the XOR of its donors', all members share a nondegenerate common entrance of dimension 1–18; 33 donors serve
several entries on nested chains). The pivot's compensation reads are deleted, it enters at the common entrance, each
donor pays its shear there after the cut and the inverse at the full frame.

* **Census on gen5** (after #287's stages): 13,332 plain dirty helpers, every compensation read before the helper's
  first other use; responses of F₂ rank 1,760 (nullity 11,572); 1,220 twin classes; low-weight circuits 2,402 triangles
  and 20,003 quadruples at class level; with a common cut and a nondegenerate common entrance: 292 pairs, 276 triples,
  1,103 quadruples. Greedy packing under the deficit-fixed φ ledger (φ(r) = r·ln(120/r)) keeps 450; total entrance rank
  1,022. The ledger model reproduces #287's κ exactly and predicted this package's κ exactly.
* **Rewrite and checks.** 11,584 compensation reads removed, 1,582 setup/restore gates paid; `kernel_transform.replay`
  runs all 19,406 formal columns forward and inverse with both omitted-gate controls rejected (2,405 / 757 wrong rows)
  and checks the prefix relation for every entry; then every stage of #287's verifier runs fresh — virtual, raw, bit
  (with #287's descent and target stages), scalar, primes (545 charts ≤ 576 factors), banks (pivot residual widths tiled
  by (r⁴, 4³⁰⁻ʳ) banks on top of gen5's own patterns; literal stock 1,247,070 → 1,244,515), complex, math and finite —
  with ten omitted-stage negative controls; the geometry stage samples an actual entrance basis for every rank present.
  Every #287 literal the rewrite changes is a recomputed pinned value in `expected/kernel-pins.json`; no check is dropped
  ([KERNEL-PROOF.md](KERNEL-PROOF.md)).

| one invocation, m = 120 | PR #285 | PR #287 | this package |
| --- | ---: | ---: | ---: |
| entrances | 2,554 | 2,554 | **3,004** |
| literal stock, 60 replicas | 1,247,070 | 1,247,070 | **1,244,515** |
| bit coarse saving | 7.43338·10⁻⁴ | — | **7.45270·10⁻⁴** |
| κ | 7.42785663120535·10⁻⁴ | 7.44120696397042·10⁻⁴ | **7.44714499357628·10⁻⁴** |

Conditional, finite construction under the retained public all-size hypotheses of the source527 lineage (no Lean
certificate). The bit side binds, 0.29% below the complex supplier (coarse 7.47455·10⁻⁴, #193's word in the five-stage
layout); #233's complex word (7.547·10⁻⁴ in that layout, Lean-checked via #256) is the drop-in that keeps further bit gains
from being capped. #285 and #287 are open PRs; their stages are inherited unchanged and not re-proved.

## Verify

    python -m pip install -r research/five-stage-gen5-collective-kernels/requirements.txt    # sympy 1.14.0
    python3 -B research/five-stage-gen5-collective-kernels/verify.py --output /tmp/gen5-collective-kernels-verification   # about 4 minutes; not under -I

`verify.py` is #287's with the kernel stage required and κ pinned; it refuses pin-recording mode. The workflow
`.github/workflows/five-stage-gen5-collective-kernels.yml` runs it on Ubuntu.

## Files

#287's package with: `kernel_transform.py`, `kernel-selection.json`, `pins.py`, `expected/kernel-pins.json`,
`KERNEL-PROOF.md`, the modified `portable_bit.py`, `raw_ledger.py`, `code/global_lowering.py`, `code/geometry527.py`,
`bank_template.py`, `bank_check.py`, `scalar_check.py`, `prime_check.py`, `math_check.py`, `finite_check.py`,
`verify.py`, `discovery/` (censuses, selection, pin generation, manifest; not run by the verifier), `README.md`,
`PROOF.md`, `NOTICE.md`, `MANIFEST.json`; #287's README/PROOF kept as `README-PR287.md`, `PROOF-PR287.md`.
