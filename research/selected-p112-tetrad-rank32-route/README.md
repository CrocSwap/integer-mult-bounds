# A source-bound P112 tetrad decoder fits the ideal rank-32 budget

**New exact port-binding result and conditional budget lead. No physical supplier, selected-κ improvement, or multiplication theorem is claimed.** The selected complex provider's 112 nine-bit port labels have exactly the P112 parity graph after a concrete bijection. Transporting the tetrad-local identity across that map gives 56 rank-2 terms, total copy charge 112, and the exact required diagonal/orthogonal-pair entries.

That charge fits a useful changed-contract screen. Keeping the selected 192-unit phase, replacing its centre with the mapped decoder, and putting the remaining non-centre mass into 166 rank-32 children gives an ideal complex cap of κ ≤ **0.0137876681081** if two coordinates per family can be unpaid. The tracked bit-side two-unpaid/rank-32 relaxation has ideal cap **0.0319843333739**, so the smaller complex cap clears the (0.01) target. At one unpaid coordinate, both sides fail at (a=1/99). These are planning relaxations only; the selected κ stays **0.001672660197076918**.

## What is established

The verifier reads the frozen selected word from [selected-replay.tar.gz](../community-frontier1094-audit/selected-replay.tar.gz), reconstructs the P112 root geometry using the pinned [tetrad decoder verifier](../p112-tetrad-local-decoder/verify.py), and checks the explicit root-to-port bijection against every entry of the 112-by-112 binary pairing matrix. The map is a finite witness, not a uniqueness or classification claim.

Under that bijection, the 14 eight-port tetrads and 28 four-frames are exactly the P112 partition. The 56 signed-coordinate terms satisfy (K_{ii}=4) and (K_{ij}=0) for every distinct orthogonal pair. Their actual support-pair ranks are all two, so the copy profile is `{2: 56}` and its mass is 112. The verifier checks all **6,720** constrained entries and each term's rank. This carries the coefficient identity into the selected port labels; it does not compile the terms into provider gates.

The budget replay uses the pinned [complex ceiling](../complex-local-word-ceiling/README.md), [centre ledger](../centre-shared-kcall-charged-seed615415/README.md), and [bit-side levers](../bit-revision3-levers-seed03/README.md):

| Side | Ideal profile per call | Unpaid | Moment at (a=1/99) | Ideal κ cap |
|---|---|---:|---:|---:|
| Complex | 192 rank-1 phase units, 56 rank-2 terms, 166 rank-32 children; centre charge 112 | 2 | 0.996649697627 | 0.0137876681081 |
| Bit | 9 rank-7 copies, 158 rank-32 children; inherited surcharge retained | 2 | 0.985176926234 | 0.0319843333739 |

Both target moments pass with certified interval arithmetic, and both one-unpaid controls fail. The joint ideal cap is the smaller side, **0.0137876681081**. The complex profile's 5,616 paid units leave (14080/9) idle units under its changed two-unpaid coverage formula. All these values assume the rank-32 children and altered unpaid-coordinate laws can be realized.

## What remains open

There is no physical word for the 56 new terms: the map only relabels coefficient coordinates. A construction still needs legal source access, exact local execution on arbitrary dirty inputs, helper ownership and chronology, frame and restoration charges, and the actual consumer. The complex and bit sides must each prove their two-unpaid endpoint contracts. The selected outer invoice and all precision and hosting costs must then be recomputed. The coefficient copy mass 112 is not a complete circuit invoice.

The next bounded experiment is to implement one mapped tetrad block on its eight ports with four rank-2 terms and replay its dirty-input behavior. Stop if any source, restoration or consumer cost exceeds the remaining budget before broadening to 14 blocks. Do not treat the ideal cap as acceptance to start a larger construction round.

## Relation to nearby work

The existing [P112 tetrad-local decoder result](../p112-tetrad-local-decoder/README.md) proves the sharp 112 copy floor inside its one-sided local alphabet, but does not bind the identity to the selected provider's port order. This package supplies that exact binding and combines it with the selected complex and bit budget engines. It is adjacent to [PR #3344](https://github.com/CrocSwap/integer-mult-bounds/pull/3344)'s larger-child/multiple-unpaid budget direction; it does not claim that direction as new or solve its physical endpoint. The cached overlap search covered 394 open PRs and 2,319 discussions, but could not refresh GitHub during this run; the exact scope here is source-bound P112 tetrad transport plus its conditional two-side price, not a novelty certificate.

## Reproduce

From the repository root, with Python 3.12 and standard-library-only inputs:

```sh
python3.12 -I -B research/selected-p112-tetrad-rank32-route/verify.py
python3 scripts/research_package.py --package research/selected-p112-tetrad-rank32-route --check-only
python3.12 scripts/research_package.py --package research/selected-p112-tetrad-rank32-route
```

`RESULT.json` records the complete recomputation. `SOURCES.json` pins the selected archive, geometry proof/checker, complex and bit interval engines, selected record, and relevant ledgers. The script's `--write` option intentionally regenerates the receipt.

## Open next questions

- Can the 56 mapped rank-2 terms be compiled into a dirty-input physical endpoint with full source, frame, restoration and consumer costs inside the rank-32 budget? First step: implement and replay one eight-port tetrad block. The blocker is the absence of a chronological provider interface for these terms.
- Can both suppliers justify two unpaid coordinates while retaining their rank-32 profiles? First step: trace and replay the exact data endpoint on each side. The blocker is that the selected contracts certify only one unpaid coordinate.

## Credit

The P112 tetrad geometry and local identity are credited to the authors of [p112-tetrad-local-decoder](../p112-tetrad-local-decoder/README.md); the selected source data and budget engines retain their original attribution and licenses. Prepared by Gonzalo Mier with substantial OpenAI Codex assistance. Apache-2.0. No frozen source, selected record, or user-provided untracked draft was modified.
