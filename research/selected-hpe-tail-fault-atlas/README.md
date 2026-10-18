# Three selected tail omissions pass every proper-helper unit-row check

An independent exact replay of the selected PR1094 local word verifies all78 proper-ended helper unit rows and zero off-diagonal columns. A complete atlas of its116 tail-operation omissions finds **three faults that preserve every one of those unit rows but leak a helper input into other outputs**. The zero-column obligation detects all three. This confirms why proving a residual helper output is not the same as proving its dirt is absent elsewhere. It is not a bug in the retained complete endpoint checker, which requires both conditions.

| Fault class | Count |
|---|---:|
| Unit row and zero column both fail |16|
| Unit row only fails |97|
| Zero column only fails |3|

The three row-blind omissions are zero-based tail indices106 (`498 -= 311`),110 (`499 -= 498`) and115 (`511 -= 327`). Explicit unit inputs311,498,327 give output errors at register247,247,246 of -1/2,+1/2,+1/2 respectively. Full exact records are in CERTIFICATE.json. These are actual scalar omissions in the frozen word, not fabricated wrapper recipes or float-rank proposals.

## Source and formal scope

The source-bound canonical word is the selected1094 evidence snapshot retained by `two-accumulator-saved-arms`, with decompressed SHA256 `4ddb29fb9bc6f27e0c0fbfcf19a2a93a3496ad900d0f6d89059d0305c9576c0c`. Its source manifest records how the selected provider was rebuilt. This audit pins those exact bytes and provenance; it does not rebuild the supplier from its construction archives again.

The local word has704 independent scalar inputs,98 ADD and18 SCALE operations in its tail, and78 helpers ending at proper frames. Their residual-width histogram is {4:32,7:30,8:16}. `HyperplaneEnd.Multi.hpe_streams_multi` assumes each chosen helper has a unit scalar row. The retained proof separately names the zero-column condition needed by Lemma A's `endpoint_indep`. This audit connects those two different scalar obligations to actual current source columns and demonstrates their distinct fault coverage. It neither claims that the Multi theorem itself requires the zero column for its narrower helper-output conclusion nor that its Lean theorem is wrong.

The old `verify_hpe_lean_binding.py` binds three fixed38-helper wrapper recipes; the existing `hpe-lean-semantic-binding` independently evaluates those wrapper operators. Neither result is repeated here. This audit does not claim all78 current residual pairs are the three old certified pairs.

## Independent calculation

The verifier imports no producer, primary scalar engine or prior atlas. It executes every source operation over sparse rational rows, in the literal order precondition, compensation, A, cut, B, tail, cleanup. The entire result is checked against `(x,y,h)->(x,y+x,h)`, not only78 selected rows. The proper-helper set is independently reconstructed by binary frame rank, without trusting the stored local-profile aggregate.

For an ADD `d += q s`, write the full word as L G P, with P the prefix and L the suffix. Omitting it changes the matrix by `-q (L e_d)(e_s^T P)`. For SCALE `d *= q`, the difference is `(1-q)(L e_d)(e_d^T P)`. Both factors are computed exactly. The nonzero outer product gives the complete704-by704 difference, including every arbitrary dirty input. A helper row changes exactly when its left factor is nonzero; helper column j has an off-diagonal change exactly when the right factor at j is nonzero and the left factor has a nonzero coordinate outside j. This yields the complete classification.

A separate numeric path executes the original and each omitted word on a chosen literal unit input, without using the sparse-row map or the syndrome formula. Every resulting704-vector difference equals the predicted outer-product column and is nonzero. Normal and optimized Python run explicit exceptions rather than disableable assertions. The116 semantic mutations are the failure controls, and the unchanged complete map is the positive control.

## Reproduce and limits

`python -I -O -B research/selected-hpe-tail-fault-atlas/verify.py`

`python3.12 scripts/research_package.py --package research/selected-hpe-tail-fault-atlas`

This is a scalar hypothesis audit. It does not invoke a fresh Lean build, check every physical frame/operator equation, reprice mutated programs, rebuild source archives, run native/hosted supplier execution, or discharge all-size compiler, precision/tape, hosting and analytic assumptions. No current acceptance bug, new supplier, optimal circuit or kappa is claimed. A single omitted gate is not asserted to preserve physical frame legality.

## Open next questions

Bind all78 modern residual helpers to their concrete wrapper, chronological label and hosting obligations as one explicit artifact. Start with their actual per-pair recipes and keep unit-row and no-other-reader claims separate. This package lacks the current operator-level replay and Lean build needed for that wider conclusion. Structured questions are in TASK.json.

## Credit

Credit Jeremy Kothe/jeremykothe2 PR593 for the HPE Lean theorem and Multi extension; the retained Lemma A/G lineage; the selected PR1094 supplier and construction authors listed in its manifest; and the authors of `two-accumulator-saved-arms` for the source-bound canonical snapshot. No earlier finite boundary identity or wrapper theorem is claimed as new. The contribution is the independent modern scalar binding and complete116-fault coverage atlas. Prepared for woklerx with substantial OpenAI Codex assistance. Apache-2.0; no independent human review claimed.
