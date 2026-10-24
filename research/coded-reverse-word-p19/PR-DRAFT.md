# PR draft: the p=19 word without the code (draft, verification open)

**Status: draft. Not proposed for merge.** The word, the price and the compiler are
exact; the items under "Still needs verification" are not, and the previous coded
draft's headline is withdrawn.

Title:

```
Certify conditional kappa 0.0033999964 via the p19 controller word (complex 0.007578535, BIT 0.0034, no recoding bill)
```

## Summary

The previous draft attached the p=19 invoice to a coded-reverse word. Two audits showed
that cannot work: the physical reverse call is `D(X − QCY)`, so its letter is `D` while
`[C,D] ≠ 0`, and every coded role leaves a `Q⁻¹BᵢQ` terminal gauge — one decoder per
owner per thick stage, 2,128 rank-1 units against a 1,103-unit root budget. No proper
subset of coded pairs diagonalises (checked at p=3, 4, 5), so the cost cannot be
diluted.

The invoice never needed the code. `invoice(p, pattern, thick, profile)` takes no
coding argument, so the same word without the overlay prices identically and carries
**no recoding bill at all**. This draft replaces the coded construction with that word.

## What is exact and checked

| item | value |
|---|---|
| word | the controller's own gate trace, replayed in the controller algebra and required to equal `controller()` exactly |
| diagonalisation | p=19 outputs `[(1,4)…(9,4),(19,2)]`, denominators `[1]` |
| census | 241 gates: 20 forward, 19 reverse, 39 stage letters, 36 retained idles (198 rank), 108 bridges, 19 closing swaps |
| invoice | root 0.007578535 (p16 published root reproduced); ambient target rank 153 |
| field bill | **0 recodings**, 0 field maps, 0 adds, 0 clears, **0 decoder** |
| guards | α 0.99579414, γ 0.963763, δ 0.951561 |
| compiler | shape-correct majorant `h = 1/64`, `B = (5+8h)·1024`, `H0 ≥ 8v` ⇒ **H0 = 5,170,423,668,736**, H1 = 49,224,448,837,637,726,209; a **numerical instantiation under an applicability premise**, not a proof |
| compiler premises | `20⁶⁴ < 21⁶³` ✓, `max target rank 153 < 256` ✓ |
| BIT | atom 0.004 > ordinary 0.0034363538 > admitted 0.0034 |
| ledger | 54 strict + 4 functional predicates positive at κ; at exactly 0.0034 only `actual_bit_above_effective` fails |

κ = 951999/280000000 = 0.0033999964, **+12.31 %** over 0.00302728823.

Reproduce (~6 min for the long one):

```sh
python3 -B research/coded-reverse-word-p19/p19_plain.py
python3 -B research/coded-reverse-word-p19/p19_claim.py
python3 -B research/coded-reverse-word-p19/verify.py
python3.12 -B scripts/research_package.py --package research/coded-reverse-word-p19
```

## Corrections carried into this draft

- **No hand transcription.** The word is the controller's own trace; a replayed trace
  must reproduce the controller's matrix, so the class of drift the earlier audit found
  cannot recur.
- **Compiler constants.** The p7 pair (`h = 1/7`, `B = (4+7h)v`, `H0 ≥ 7v`) requires
  `10 < 2⁴` and `121 < 2⁷`; here `20 < 2⁴`, `153 < 2⁷` and `20⁷ < 21⁶` all fail. The
  constants used are those `query-thinned-controllers::tail` derives for this shape.
- **SOURCES pin.** The old `base_commit` was a branch commit, which broke CI; it now
  points at canonical main, with the two package-local files pinned to the PR head.
- **Tail limit.** Settled rather than open: the source uses its limits only through
  "each bound to the power 128 is below 1/16", and `L = 0.97` closes that step
  (`0.97¹²⁸ < 1/16`, `0.97¹⁰²⁴ < 2⁻³²`), while gamma also meets the source's tighter
  `31/32`. The `19/20` guard is a stronger unused choice.

## Still needs verification (why this is a draft)

1. **Ambient rank 153.** A literal 512-address replay cannot host this word. It is
   certified as the controller's operator (trace identity + diagonalisation), not as a
   bank replay. A block-wise replay over 19 fresh eight-axis blocks plus the shared
   centre would close this.
2. **Helper block.** The 7,752 helper units on the invoice's T side are inherited, not
   materialised.
3. **Field-bill admission** under the caller's fixed-tape/precision ABI; precision, tape
   and hosting; hosted CI and kernel review.

## Reviewer's checklist

- Does the trace identity plus the diagonalisation suffice for a word whose ambient rank
  is 153, or is a block-wise replay required first?
- Is the helper block genuinely disjoint from the main roles?
- Does anything in the source tail lemma use `19/20` outside the 128th-power decay block?

Credit retained from PR4940/PR4933/PR4929/PR4433/PR4470 as credited in the package
README.
