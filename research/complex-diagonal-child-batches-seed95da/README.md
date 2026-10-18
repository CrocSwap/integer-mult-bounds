# Cross-column diagonal batching has limited chronological coverage

**Scoped construction screen and bounded obstruction. No physical supplier or new κ is claimed.**

## Result

The selected #1094 gauge44 provider has 2,412 rank-one children per orientation. I tested a new
cross-column mechanism: replace sixteen adjacent rank-one child calls on distinct destination
columns by one rank-16 child. For input blocks (X_i,Y_i), place them on the diagonals of two
16-by-16 block matrices. Their product is

\[
\operatorname{diag}(X_1,\ldots,X_{16})
\operatorname{diag}(Y_1,\ldots,Y_{16})
=\operatorname{diag}(X_1Y_1,\ldots,X_{16}Y_{16}).
\]

The diagonal outputs are exactly the sixteen original rank-one child results; every off-diagonal
output is zero. This is an exact identity over any associative coefficient ring.

The hash-pinned forward and backward traces each contain exactly eight non-overlapping, uninterrupted
rank-one batches of size 16: one run of 16 calls and one run of 112 calls, partitioned into seven
batches. The batches serve 128 of 2,412 rank-one children. No other uninterrupted rank-one run has
length 16. No event is moved across a scalar, adapter, centre, or other-rank climb.

Replacing those batches preserves the paid rank mass:

| Per-call profile | Rank mass | Exact relaxed ceiling upper endpoint |
|---|---:|---:|
| Selected `{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}` | 5,586 | 0.001690054109089 |
| Eight ideal rank-16 batches `{1:2284, 2:418, 3:432, 4:142, 5:82, 8:8, 16:8}` | 5,586 | 0.001719107428154 |

The upper endpoint rises by **1.7191%**, below the task's required 5% gate (target 0.001774556814543).
This is already the most favorable screen: every new operand-copy, source-access, frame, interface,
hosting, output-storage, precision, and dirty-restoration charge is set to zero. The physical child
would expose 256 input slots per side and 256 output slots per batch, although only sixteen diagonal
inputs and outputs are useful. Its actual gathering and restoration contract has not been realized
or priced. Since the free-interface profile misses the declared gate, this chronology-constrained
family is stopped before physical rewriting.

This result does not rule out batching nonconsecutive children with stored operands, changing the
word or template, or using another block size. It supplies no supplier admission, κ, or selected-record
change.

## Source and overlap

The provider member is
`candidate/strict/global/base/providers/gauge44/LOCAL-PROGRAMS.json.gz` in
[`selected-replay.tar.gz`](../community-frontier1094-audit/selected-replay.tar.gz), archive SHA-256
`f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6` and member SHA-256
`241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a`. The selected-record SHA-256
is `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`; all live pins are listed
in [SOURCES.json](SOURCES.json).

Nearest predecessor work is Arham Tahir's [PR #1605](https://github.com/CrocSwap/integer-mult-bounds/pull/1605)
(head `488f2ecf1835c6d813e96543656dddf0062fdc9a`)
and Josie Elliston's [Discussion #1596](https://github.com/CrocSwap/integer-mult-bounds/discussions/1596),
which derive rank-one reblocking budgets and leave chronological physical batching open. Navinor's
[Discussion #1659](https://github.com/CrocSwap/integer-mult-bounds/discussions/1659) and [PR #1686](https://github.com/CrocSwap/integer-mult-bounds/pull/1686)
settle same-word per-column frame assignments. The present test changes the interface by batching
across sixteen distinct destination columns through a diagonal rank-16 child; it does not improve a
per-column frame assignment. The exact diagonal identity is elementary, while its physical input,
output, and restoration realization remains open.

## Reproduce

From the repository root, Python 3.12 and the standard library are sufficient:

```sh
python3 scripts/research_package.py --package research/complex-diagonal-child-batches-seed95da --check-only
python3.12 scripts/research_package.py --package research/complex-diagonal-child-batches-seed95da
```

The verifier checks both event orientations, every admissible contiguous batch, the unchanged rank
mass, the exact diagonal product identity, the rational ceiling bracket, and failure controls for
off-diagonal support, duplicate destinations, and wrong-rank events.

## Open next questions

Can nonconsecutive rank-one children be buffered into diagonal rank-16 batches with a fully charged
source, copy, frame, hosting, output, and arbitrary-dirty restoration schedule? This matters because
the available contiguous batches cover too little rank-one payload to pass the 5% screen. A feasible
first step is to pin operand-ready/use windows for the selected word and solve the resulting disjoint
16-way interval packing problem. The blocker is that the current local event trace records child
columns and frame changes, not a realized multi-column dirty-state memory contract.

## Credit

Credit Sagar Thakrar / PR1012 for the retained coverage identity, Douglas Colkitt / PR1240 for the
local-word ceiling model, Arham Tahir / PR1605 and Josie Elliston / Discussion #1596 for rank-one
reblocking budgets, Navinor / Discussion #1659 and PR1686 for same-word frame screens, and the
selected Rohan Arun / Jeremy Kothe / Hao Yan construction lineage. Prepared by Jose Manuel
(@jmbarrancoml) with substantial OpenAI Codex assistance in source analysis, proof, code, and prose.
New material is Apache-2.0; frozen source archives and licenses are unchanged.
