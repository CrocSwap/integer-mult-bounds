# Independent forward audit of k8 helper 450

This package independently checks the scalar part of
[PR1611](https://github.com/CrocSwap/integer-mult-bounds/pull/1611) at
`156cc788b5a8122b19686f015e5654b117e4389d`: helper **450** of the pinned
seven-slot k8 word has a unit output row and an isolated input column in both
emitted local orientations. [RESULT.json](RESULT.json) records the passing exact
replay. No actionable discrepancy was found in the predecessor.

The starting main is `0b1cccf86e2f5132ed286a26ef0a681a495740ea`. The selected
PR1094 manifest pins the k8 slot record. Pinned ancestral transport and emitter
producers rebuild the canonical word and complete event lists, which match the
published slot hashes. The new checker
imports no PR1611 checker, pending package code or scalar replay function.
[SOURCES.json](SOURCES.json) records the consumed source pins.

## Exact coverage and independence

For each orientation, forward execution starts separately at every coordinate
vector of the **712-register** scalar domain: 704 local registers and eight
private centers. Each execution retains emitted ADD, SCALE, COPY and CLEAR
operations, using exact dyadic arithmetic. The checker records helper450's
output on every input basis vector, and every output coordinate for its own
input vector. Thus it checks all 712 entries of the helper's output row and its
complete dirt column, including arbitrary private inputs and their zero entries.
Across both orientations this is **1,424 input basis executions**; it is not a
comparison of every entry of the complete 712-by-712 scalar matrix.

PR1611 obtains the output row by reverse covector propagation over exact
rationals. Here the row is assembled from independent forward executions.
The source producers and emitted inputs are shared; the scalar algorithm and
dyadic implementation are independently written. Each orientation has 24,767
events and 19,693 scalar operations. Six semantic faults reject: dropping or
flipping the last helper ADD, and adding a dirt-leaking read. The extra read
preserves the row but leaks `1/2` to L230 forward and `1` to L27 backward.
The arithmetic check compares 4,624 dyadic operand pairs with `Fraction`; a
four-input dirty echo tests destructive COPY/CLEAR and inverse scales.

The checked row is `delta(j,450)` and the checked column is `e_450`.
Linearity proves scalar output restoration for every arbitrary input and no
scalar leakage of its initial dirt. Column isolation is an additional finite
restoration obligation; the retained `hpe_block` theorem needs the unit row.

## Conditional operator conclusion and replay

PR1611 separately binds the actual wrapper events and exact serialized recipe
`2:999` to `HyperplaneEnd.Exact.pair3`, including phase. Under exact relabel
recipes and a valid correspondence from the emitted events to the formal word,
the unit row gives `T_U T_E^-1`. Correct wrappers give
`L^-1 T_U T_E^-1 R^-1`, and retained `exact_N_pair3` makes this `C7 tensor I4`.
This audit adds no new Lean theorem, operator-kernel check or physical endpoint
admission. COPY/CLEAR translation and private lifetimes, exact recipes for other
events, ownership/footprints, whole-call hosting, all-size compilation,
precision/tape bounds, complete costs and analytic transfer remain obligations.
The selected frontier, paid profile and kappa are unchanged.

From the repository root, with standard-library Python 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/k8-hpe450-forward-audit
```

[TASK.json](TASK.json) records the revision-3 `formal-interface-lemma` refinement,
selection nonce and [claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1394#discussioncomment-18918131).
The source-bound baseline passed as orientation only. The session reserves its
last quarter for verification and handoff; construction stops at 07:38 UTC.
[AUDITED-PR.json](AUDITED-PR.json) pins the reviewed package, and
[VALIDATION.json](VALIDATION.json) separates local execution from unclaimed CI.

## Open next questions

- Can this one helper be connected to an actual Lean event word? First specify
  private COPY/CLEAR lifetimes and wrapper labels. The missing serialization
  correspondence remains the blocker; more scalar examples do not remove it.
- Can the local helper be traced through each selected T16 hosted invocation?
  Start with the pinned owner map and chart/route evidence; exact recipes and
  nonempty disjoint footprints remain separate physical premises.

Credit: Hanson Sun (@bbMisk), PR1611; Jeremy Kothe, HPE formalization and k8;
DreamingOfClouds, wrappers and Lemma A/G; icekylinx, compiler; Rohan Arun, packing;
Josie Elliston and Sagar Thakrar, word/audit lineage; @commdata2338, PR1415;
Chafik Boukhalfa, Zhihao Chen and all retained realization contributors.
New corroboration: @ToikY, with substantial OpenAI Codex assistance in analysis,
implementation, testing and writing. Apache-2.0; original notices retained; no independent human review claimed.
