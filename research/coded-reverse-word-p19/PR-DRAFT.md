# PR draft: the p19 word without the coded overlay

**Draft. Conditional κ claim whose only remaining assumptions are inherited from the
selected construction.** Every obligation that is new to this word is discharged in the
package; the inherited interfaces are consumed unchanged and that is shown, not asserted.

## Status against the required bar

| obligation | status | evidence |
|---|---|---|
| finite arithmetic | discharged | `p19_claim.py`: invoice root 0.007578535, guards, BIT chain, ledger |
| uncoded trace/controller identity | discharged | `p19_plain.py`: p=19 trace == `controller()`, 241 gates, diagonalises with denominators `[1]` |
| zero field bill | discharged | `P19_CLAIM.json`: 0 recodings, 0 maps, 0 adds, 0 clears, 0 decoder |
| **p19 physical binding** | **discharged for this word** | `p19_lift.py`: `Φ` is a ring homomorphism on the monomial ring (multiplicativity on 24 sampled pairs, powers add, distinct axes commute), so the gate-list identity lifts to address operators for every block count; the p=2 replay is the implementation control, 2^17 addresses per role |
| compiler: rank completion, splitting | discharged on this census | `max target rank 153 < 256`, `20⁶⁴ < 21⁶³` |
| compiler: normalizers, owner allocation, rank-one surplus | inherited, interface unchanged | the word adds no job, no owner and no scratch; the T/D census is the source's own model |
| helper compatibility | discharged mechanically | the trace's roles are exactly `0…2p−1`; no gate reads or writes helper-owned state |
| helper materialisation (7,752 units) | inherited | PR4929 producer; priced on the T side, not rebuilt here |
| fixed-tape/precision/hosting/CI/kernel | inherited | caller-side compiler instance and maintainer pipeline |

## What changed since the last revision

- The claim artifact no longer contradicts the word: `field_level_bill` is emitted
  all-zero from the uncoded receipt, and the coded overlay is quarantined as
  `record_only_overlay` ("historical record, NOT the priced word"). `verify.py` asserts
  both, so they cannot drift apart again.
- **Physical binding** is now proved by a lifting lemma rather than asserted from a
  randomised p=2 replay, and the replay is labelled a control.
- The lemma exposed a real bug: monomial selection bits are **exponents**; applying one
  gate per selected stage is not multiplicative at exponent 2, which the p=19 word hits
  constantly. Both the lemma checker and the replay now use exponent powers.
- Compiler wording is a numerical instantiation plus an obligation table, not "exact".
- Helper autonomy is labelled inherited, with the mechanical disjointness check added.
- The frontier is reported against both baselines: the selected record
  `60403/20000000 = 0.00302015` (+12.58 %) and the maintainer-reported `0.00302728823`
  (+12.31 %), the former read from `certificates/selected-result.json` at run time.
- `SOURCES.json` declares its base as a historical canonical source snapshot pinned by
  commit and blob hashes.

## The claim

κ = 951999/280000000 = 0.0033999964 from a complex supplier of 0.007578535 and the
admitted BIT supplier 17/5000. The word is the p=19 controller trace: 241 gates, 39
stage letters, 36 retained idles of rank 198, 108 bridges, 19 closing swaps, and **no
code**, because the invoice takes no coding argument. The coded overlay is retained as a
record only: its terminal-gauge decoder costs 2,128 rank-1 units against a 1,103-unit
budget, which is why it was dropped.

## Reproduce

```sh
python3 -B research/coded-reverse-word-p19/p19_plain.py   # ~13 min: trace identity, diagonalisation, price
python3 -B research/coded-reverse-word-p19/p19_lift.py    # lifting lemma
python3 -B research/coded-reverse-word-p19/p19_bank.py    # p=2 address control
python3 -B research/coded-reverse-word-p19/p19_claim.py
python3 -B research/coded-reverse-word-p19/verify.py
python3.12 -B scripts/research_package.py --package research/coded-reverse-word-p19
```

## Reviewer's checklist

- Does the lifting lemma's hypothesis set (distinct-axis commutativity, additive powers,
  identity) suffice for the block decomposition you have in mind, including the shared
  centre?
- Is the interface-unchanged argument for the three producer-side compiler obligations
  sufficient, or does the word need its own normalizer/owner schedule checked?
- Should the randomised p=2 control be replaced by a spanning-set comparison?
