# Selected HPE tail records satisfy the distinct-register premise

**Finite source-bound result. No new κ or selected-frontier change.**

## Question and exact scope

The formal theorem `HyperplaneEnd.hpe_labels` uses `h != p` for its cleanup
gate. Open PR [#3539](https://github.com/CrocSwap/integer-mult-bounds/pull/3539)
shows that the wrapper binding rules accept a synthetic self-partner tail.
This package checks the corresponding premise on the selected source word.

For each record in the selected `gauge44-slots-t16` canonical word whose
entrance and terminal frame rows equal one of `pair1`, `pair2`, or `pair3` in
`HyperplaneEnd/Exact.lean`, the check establishes:

- the gate is `h -= p` and `h != p`;
- the helper's recorded final frame is the gate's terminal frame;
- the corresponding residual adapter has rank 7 and both monomials equal the
  exact Lean pair literals, including phase.

The selected word has 94 tail records: 78 `add` gates and 16 `scale` gates.
Thirty-four `add` gates match these Lean pairs: 12 for pair1, 12 for pair2,
and 10 for pair3. All 34 have distinct target and partner registers and exact
adapter matches. The other 60 records (44 other `add` gates and 16 `scale`
gates) are outside this result. A self-partner mutation and a wrong-terminal
mutation are both rejected.

## Source binding and method

The selected record, source manifest, word, adapters, Lean pair file, the
`hpe_labels`/`hpe_word` declarations and HPE proof note are pinned in
[SOURCES.json](SOURCES.json). The word and adapters are listed in the selected
source manifest; the Lean pair file is a selected proof supplement. The
selected baseline command also verified the entire 13-root selected package
inventory and all digest-listed proof supplements.

The verifier parses only the three Lean pair literals and reads the selected
serialized word and adapters directly. Register-field interpretation follows
the pinned `check_hpe_pairs.py` layout, while the verifier independently checks
the actual indices and recipes. It does not use either existing checker's
matching logic or run Lean. The source word and adapter arrays are not copied
into this package.

## Limits

This establishes a data-level check of the distinct-register premise for the
34 matched records in one selected word. It does not prove that the producer's
serialization corresponds to the Lean `Event` constructors, bind the remaining
60 tail records to these pairs, prove the full `hpe_labels` well-labelled
chronology, establish the other HPE hypotheses, or replay the selected
construction. `make frontier1094-verify` and any Lean build were not run. The
synthetic checker-acceptance example in PR #3539 remains a checker gap; this
result says only that the cited self-partner case does not occur in the 34
records checked here.

## Reproduce

From the repository root:

```sh
python3 -B scripts/research_baseline.py
python3 -B research/hpe-selected-tail-binding/verify.py
python3 scripts/research_package.py --package research/hpe-selected-tail-binding --check-only
```

The baseline is source-binding verification only; it is not the selected full
replay. See [RESULT.json](RESULT.json) for the fixed-input receipt.

## Open next questions

Can the 34 matched tail records be instantiated as a source-bound Lean event
word satisfying the full `hpe_labels` sequencing hypotheses? Start by
translating one selected tail gate and its adjacent relabel events to the
existing Lean `Event` constructors. The full word's serialization-to-Lean
correspondence and the remaining label hypotheses are still required.

## Credit

The HPE lemma and its three pair literals retain the attribution in
`research/hyperplane-end-lean/PROOF.md`, including the Lemma A/G and Clifford
formalization lineage. PR #3539's synthetic counterexample is credited to its
author in that live PR. This check is a separate audit of the pinned selected
word and does not reuse its verifier. Prepared by OpenAI Codex (GPT-6 Luna
xhigh) with substantial AI assistance. Apache-2.0.
