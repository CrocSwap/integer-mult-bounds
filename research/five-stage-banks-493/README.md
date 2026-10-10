# Five-stage completed banks with PR210's newest 493-source helper

Under the retained multiplication interfaces, this finite witness certifies

$$
T(n)=O\left(n(\log n)^{1-\kappa}\right),\qquad
\kappa=\frac{28376976266399}{40000000000000000}=0.000709424406659975 .
$$

That is **+0.119%** over PR237 (0.000708582410781108, five-stage banks on PR234's 471-source helper) and **+0.813%** over PR234 (0.000703701743496697).

| Construction | Helper | Bit coarse | κ |
|---|---|---:|---:|
| PR234 | PR210 df95878 (471 sources), paid exteriors | 7.041973e-4 | 0.000703701743496697 |
| PR237 | same, width-120 banks | 7.090849e-4 | 0.000708582410781108 |
| **This** | **PR210 1331149 (493 sources, target aggregation/rank/echelon, PR230 frames), width-120 banks** | **7.099280e-4** | **0.000709424406659975** |

The bit side binds; PR234's five-stage complex supplier (7.47455e-4) is unchanged.

## What is new

PR234 builds its five-stage cover from PR210's older helper (`df95878`, 471 borrowed sources). PR210 has since added 22 more source entrances, 82 equal-response target aggregation groups, 7 integer rank-compression groups, 4 signed echelon target transforms and PR230's frame refinements (head `1331149`, 16,621 physical registers instead of 16,643). This package runs that newer helper through PR234's five-stage pipeline and then applies PR237's completed width-120 banks.

- **Helper (PR210's own code, unchanged).** The package assembles PR210's research package with PR234's pinned PR200 base inputs, derives the 34 terminal records exactly as PR234 does, prepares the helper with PR210's `targetagg/setup.py`, and runs PR210's replay: all 20,141 F2 columns, the literal majorant (24-bit digits), both defining-integer signs, and all 17 corruption controls.
- **Physical telescope.** PR234's frame-tag telescope, adapted to PR210's newer replay (22 tagged event kinds, including aggregation, rank and echelon setup/read/restore). 2,569,922 tagged events; an independent literal projection and its inverse reproduce the all-column F2 endpoint and the event digest.
- **Five-stage lowering and geometry.** PR234's global lowering and exact h24/m120 geometry, with only the helper-specific constants (register count, event count, call count, rank mass) rebound to the fresh values. The five-stage profile is m = 120, W = 23,661, 494,909 calls, rank mass 2,834,920, deficit 4,400.
- **Primes.** All 26,464 used bases have nonzero cleared Gram determinants whose factors outside {2,3,5,7} leave a residual below 2^80.
- **Finite bill.** PR234's formulas with fresh values; the payload-prefix lift needs 101 bits (PR234: 98), still a fixed finite constant.
- **Banks.** Same 231 entrance charts as PR237. 12 copies give 176,915 banks of width 120 (360×(8·11+8·4), 108×(10·12), 39×(20·6), 4,304×(30·4), 172,104×(5·24)) with a proper 60-colouring of 997,260 incidences. W = 12·4v + 176,915 = 261,395; deficit 52,800; largest child 50.
- **Arithmetic.** PR234's interval moment engine certifies coarse saving 709928047185833/10^18; three finite ordinary levels and PR234's outer-47 assembly give κ; the next 10^-18 grid point fails.

## Verify

```sh
git fetch https://github.com/CrocSwap/integer-mult-bounds pull/210/head pull/234/head
git worktree add --detach ../pr210 13311491eb74a3a9a443ba4e318c68c263f064f0
git worktree add --detach ../pr234 af3fe331ca60c936229e060681ffccbc1c208678
python3 -m pip install sympy==1.14.0
python3 -B research/five-stage-banks-493/verify.py --pr210-root ../pr210 --pr234-root ../pr234 --full
```

About 10 minutes: PR234's own fresh verifier (for the complex supplier, ~3.5 min), PR210's complete helper replay with controls (~3 min), telescope, lowering, geometry, primes, banks and arithmetic. It compares the result with `certificate.json`.

## Scope

Conditional, exactly as PR234/PR237: the five-stage physical program and complex symbolic theorems, weighted q-local compiler, complete-stream movement, copied-centre and restored-row interfaces, ordinary leaves, prime supply, precision/recovery and the all-size reduction remain retained hypotheses. PR234's helper-specific checks are reused with recomputed constants rather than re-derived. Not an unconditional multiplication theorem or a speedup claim.

Prepared by Rohan Arun with Anthropic Claude assistance. Apache-2.0.
