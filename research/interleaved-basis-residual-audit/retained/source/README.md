# Conditional κ ≥ 0.00378751509478 from interleaved P104 helper bases

This construction raises the conditional lower bound to **0.00378751509478**. It exceeds the upper endpoint 0.00376313686062 of the stronger pending comparison by **0.00002437823416**, or **0.64782%**. This increment is **15.24% larger** than the preceding increment of 0.00002115478655. The directed interval for the new raw crossing is **[0.00378751509486, 0.00378751509487]**. The compiler uses a strictly smaller point. [Previous complete proposal](https://github.com/CrocSwap/integer-mult-bounds/pull/7717) · [Preceding increment](https://github.com/CrocSwap/integer-mult-bounds/pull/7713) · [New price and compiler receipt](results/application.json)

| Complete count | PR 7717 | This construction |
| --- | ---: | ---: |
| Public fields per native call | 1,470 | 1,260 |
| Independent helpers per native call | 1,070 | 860 |
| Paid native instructions per call | 6,054 | 5,810 |
| Paid recursive jobs across 16 calls and the caller | 100,416 | 96,512 |
| Productive recursive jobs across 16 calls and the caller | 20,656 | 17,296 |
| Productive rank mass less paid rank mass | 1,328 | 1,328 |

## Construction

Start from the compact 1,468-field graph in PR 7713. The journal removes 220 helper targets and their 230 dependent paid returns, splits 12 helpers and applies 14 paid pivots and nine hub reroutes. It can make an edit in either orientation. The fixed 400 main fields retain the port contract throughout. Every surrendered helper is debited. Every fresh helper has its own arbitrary input and output. [Source graph](data/BASE-GRAPH.json.gz) · [Exact journal](EDITS.json) · [Construction proof](PROOF.md)

Three choices matter near the end. The alternatives retire the same helpers and paid instructions. Changing their local equations makes two splits at chart 288 and one at chart 306 possible. A separate restriction enables the split at chart 2. All four coexist in one causal graph. In the forward chart-288 split, five local banks read the new input, one bank supplies the calibration and three local instructions carry the pulse. With the earlier role-1400 restriction, that same readout has an unwanted coefficient of one on input 10. The two transposed controls give incorrect pulse responses at the terminals. [Alternative equations](data/RESTRICTION-CONTROLS.json) · [Exact differences](results/witness.json)

At unit rank price the old and new bills have the same surplus. At the exponent used by the compiler, the changed distribution of paid and productive ranks increases the margin. The exact comparison also gives weak dominance over PR 7717 for every increasing concave rank price that vanishes at zero. The directed power and compiler checks establish the stated strict improvement. [Complete signed comparison](results/application.json)

## Replay

Use CPython 3.12 and run the following command at the repository root. The five registered checks use the standard library.

```sh
python3.12 -B scripts/research_package.py --package research/p104-interleaved-helper-bases
```

The application rebuilds the compact graph, checks all 1,260 public rows and prices the full signed caller. It checks 10,483,566 scalar products and 5,586,926 nontrivial exact divisions. The reverse sweep checks all 1,260 input columns using a further 10,218,280 exact products. The witness verifies all 230 receiver equations, all 12 split equations and one altered pulse per split. It reconstructs the signed bill again from the journal. The three catalogue checks cover all 2,938 surviving phased chart pairs and all 1,664 port-stage contacts. [Replay manifest](VERIFY.json) · [Forward receipt](results/application.json) · [Reverse and witness receipt](results/witness.json) · [Chart receipts](results)

To export the canonical graph, run `python3.12 -I -B research/p104-interleaved-helper-bases/construction.py > /tmp/p104-interleaved.json`. Its SHA-256 is `ba59d5db17c40185c8608a734ced10135d8c041e432c3840e9034868781c31a2`. The package contains the pending source inputs and authenticates their bytes. [Source pins](SOURCE-PINS.json) · [Base manifest](SOURCES.json)

The 54 strict and four functional compiler predicates pass under the selected framework. The five inherited assumptions cover native all-column application, owned erasure, the recursive compiler, precision and tape accounting, and analytic recovery. Independent scientific review and practical multiplication timings remain open. The physical replay uses a sufficient scalar grid. The minimum grid for this graph remains open. [Assumptions](vendor/selected-claim.json) · [Prior finite-scale work](https://github.com/CrocSwap/integer-mult-bounds/pull/7718)

## Open next questions

- Can an independent implementation recover all three failed equations when it restores the alternate restrictions, then derive the corrected splits using its own bank bases?
- Which other equal-rank helper restrictions can preserve two independent readouts or pulse directions at different charts? Count both owner changes and the complete signed price on the same graph.

Ali Romman prepared this contribution with substantial OpenAI Codex assistance. The source inventory and notices identify the prior constructions, authors and engines. [Credit](CREDITS.md) · [Canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/7111#discussioncomment-19712230)
