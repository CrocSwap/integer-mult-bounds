# Building PR208's priced target: rank-22 residual bank absorption

This package **builds the accounting construction** that PR #208 priced and left
unbuilt — the first certified-shape rung of its bank-absorption ladder: absorb the
bit word's **rank-22 residual family** into the banks — and states precisely what a
physical realization must still supply.

Under the retained multiplication interfaces, the certified accounting target is

$$
T(n)=O\left(n(\log n)^{1-\kappa}\right),\qquad
\kappa=\frac{700427501305159}{10^{18}}=0.000700427501305159,
$$

**conditional on the physical realization obligations R1–R4** in
[obligations.json](obligations.json). The binding branch is the unchanged complex
supplier: the absorbed bit word clears the complex cap, so κ sits at the complex
side's own value, exactly as PR #208's rung table predicts (`7004273/10^10` on its
10^-10 pricing grid; this package certifies the finer 10^-18 grid point).

| | κ | status |
| --- | --- | --- |
| main reviewed (#186) | 6.61885549259598e-4 | published |
| #205 packed diagonal bit | 6.83061299399923e-4 | verified this queue |
| #210 shared entrance gauges | 6.83883297459132e-4 | verified this queue |
| **this package, rank-22 absorption** | **7.00427501305159e-4** | **accounting certified; R1–R4 open** |
| #208's priced rung-1 target | 7.004273e-4 | model price (superseded by the exact grid above) |

That is **+2.42% over #210's frontier** (+2.52% over the #207 row #208 priced) and
**+5.82% over main** — the complex
supplier's own cap, with no complex-side work, exactly the move #208 priced.

## What is new and machine-checked

1. **The absorbed family, with provenance.** The rank-22 ledger bin is enumerated
   occurrence by occurrence from the pinned PR200 word
   ([inputs/absorbed-occurrences.json](inputs/absorbed-occurrences.json)):
   1,320 physical-chain frame jumps, 24 copied-centre children and 880 source-chain
   frame jumps per vertex — 2,224 × 3 = 6,672 ledger children. This is not the
   banked gauge-exterior species: non-gauge chains already bank their residual
   projectors and keep every increment child, so this family is the *"future
   genuinely different residual type"* PR #207's crossover notes reserve.
2. **The whole-bank schedule.** Dirt volume `22 × 20,016 = 440,352 = 72 × 6,116`
   fills whole banks; the stock drop equals the bank count exactly; the retained
   ledger (857,622 children, largest 21) satisfies the row identity
   `72·50,286 − 3,614,784 = 5,808` with the deficit unchanged
   ([schedule.py](schedule.py)).
3. **Exact arithmetic to the κ.** Both rational interval moment engines, the
   three-level finite ordinary composition and the unchanged 47-constraint
   balanced assembly, with the adjacent 10^-18 grid point **excluded**
   ([arithmetic.py](arithmetic.py)). The engine reproduces PR #205's certified
   packed coarse saving to the digit before the absorption is applied — the
   pipeline is validated against a published certificate, not just self-consistent.

## What is not built here

The physical realization of the new residual type: the banked word's formal
columns (F2 identity and defining-integer decoder) under the modified transitions,
the block assignment, charts, incidence colouring and prime witnesses. These are
stated one-to-one against the gauge-family precedent in
[obligations.json](obligations.json) (R1–R4, all OPEN). Until they verify, this is
an **accounting construction and a certified target**, not a completed finite
witness — the same distinction PR #208 draws ("priced target, not built"), moved
one full step forward: the target is now certified to the grid point, the family is
enumerated, and the remaining work is a closed checklist.

As every result in this repository: conditional on the retained analytic,
uniform-recursion, fixed-tape and finite-bridge interfaces; never an unconditional
multiplication theorem.

## Reproduce

```sh
python3 -B verify.py           # read-only replay, ~1 minute
python3 -B verify.py --write   # authoring only
```

Python 3.11+, assertions enabled. No network, no git, no scratch space.

## Credits

The absorbed word and its checkers: Chafik Boukhalfa (#200). Complex supplier:
ikeboy (#193/#202 lineage). Bank mechanism: Evan McKinney (#197), realized on this
word by rohanarun (#205); completed entrance banks: PR #186/#207 (Dugongue) and the
BANK-PROOF-PR200.md argument. The pricing model this builds: maxime-fleury (#204,
#208), whose rung-1 target is reproduced and sharpened here. Frame/ceiling context:
rohanarun (#211/#213), eumemic (#210), DaysSky (#192/#201/#212). All retained
upstream attributions of the PR168/PR184 lineage stand.

Prepared with OpenAI Codex assistance. Apache-2.0.
