# Direct Boolean audit of the R420 block-4 replacement

**Independent finite circuit audit; no new circuit or κ.** This package checks the 51-XOR block-4 replacement from [PR1363](https://github.com/CrocSwap/integer-mult-bounds/pull/1363) with a direct Boolean truth-table engine that is separate from PR1363's basis-column replay. It derives the logical target from the exact 58-gate block in the frozen R420 source word, then checks all **4,096** inputs of both the source block and the candidate.

| Block at frame 546 | XOR gates | Local positive-norm peak | Boolean inputs checked |
|---|---:|---:|---:|
| Frozen source `B[313:371]` | 58 | 1,485 | 4,096 |
| PR1363 candidate `B[313:364]` | 51 | 1,227 | 4,096 |

The input register order is pinned in `CERTIFICATE.json`. Source and candidate use different output-to-wire permutations, so the audit first applies the source block to the twelve unit basis states and derives its logical output rows through the source assignment. The candidate is then checked against those same source-derived rows through its own output assignment. Its recorded target matrix is only used as a separate consistency check.

Two negative controls reject: omitting the first candidate gate and reversing its direction. The test file also checks the simulator on a two-wire XOR across all four input states.

## Scope

PR1363's full construction reports that changing this block and rebuilding its required literal cleanup changes the historical R420 word from 26,916 to 26,902 scalar ADDs, with the paid profile unchanged. This audit does **not** independently replay the full 660-column word, cleanup routing, hosted bill, or generator search; it verifies only the pinned local block map and local positive-norm receipt. The 14-ADD whole-word saving is inherited from PR1363 and is not a new saving established here.

The selected result at base `bce54fb3f895cbe5cd4c0eb477c3afeed100190f` remains κ `0.001672660197076918`, using PR589 on PR555 as its cited bit supplier. The R420 word is a historical alternative, below the selected bit supplier; this audit changes neither the selected construction nor κ. The current assembly and review chain are pinned in `SOURCES.json`.

## Reproduce

With Python 3.11 or newer and the repository's pinned source word:

```sh
python3 -I -O -B research/r420-block4-truth-audit-seed00/verify.py
python3 -I -O -B research/r420-block4-truth-audit-seed00/test_package.py
```

Expected verifier output:

```text
PASS_R420_BLOCK4_BOOLEAN_AUDIT
baseline gates 58 inputs 4096 source_map exact
candidate gates 51 inputs 4096 source_map exact
controls omitted_first_gate=rejected reversed_first_gate=rejected
```

The registered Python 3.12 replay is:

```sh
python3.12 scripts/research_package.py --package research/r420-block4-truth-audit-seed00
```

## Pins, credit, and next question

The exact base is `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. PR1363's head `2f80560e741f8255fd8023799bdfedae17a9bc12`, source Git blobs, candidate archive hash, and full-word canonical hashes are recorded in `DEPENDENCIES.json` and `SOURCES.json`. The source R420 archive and selected result, assembly, source manifest, and review are also pinned.

This audit does not prove that 51 gates is optimal. A useful next investigation is an exact-depth or meet-in-the-middle search in a clearly specified circuit class outside PR1363's sampled pivoted-LU class. Any such search needs its own domain and stopping rule; this receipt does not imply a lower bound.

Prepared by **Cinna Davis / @1337isnot1337** with substantial **OpenAI Codex** assistance in research, implementation, verification, and writing. The direct simulator is independent of PR1363's basis-column verifier, but no independent human review is claimed. Credit PR1363 for the 51-gate candidate and complete-word route; credit eumemic's retained PR543 R420 source and its Apache-2.0 license.

## Open next questions

Can a factorization outside the sampled pivoted-LU class realize this 12-wire target with fewer than 51 gates? A bounded exact-depth or meet-in-the-middle search on the pinned target is the next step. It should price the required cleanup and all downstream routing before making a whole-word claim.
