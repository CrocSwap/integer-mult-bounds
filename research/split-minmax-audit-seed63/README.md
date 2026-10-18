# Audit: the decoder split min–max has the stated form

**Research note / mathematical audit; no new κ.** The identity quoted from
memory in [PR2162 §3](https://github.com/CrocSwap/integer-mult-bounds/pull/2162)
follows from A. Schrijver's *Matroids and Linking Systems*,
[Theorem 3.6, pp. 363–364](https://ir.cwi.nl/pub/9901/9901D.pdf#page=15).
[PROOF.md](PROOF.md) gives the exact construction: block diagonal matrices on
color copies, partition matroids on the original rows and columns, then
saturation of the dual deletion sets. It also establishes the stated
equivalence of the **universal** cost bound with perfect splits, using closure
under principal restrictions. Target (A) itself remains open.

This replaces one unspecified literature dependency with a precise theorem
application and independent finite evidence. It supplies no physical decoder,
supplier admission, or selected-frontier change. The statement being audited
is frozen in [SOURCE-STATEMENT.md](SOURCE-STATEMENT.md); no predecessor code is
imported or modified.

## Reproduce

From the repository root, using only the Python standard library:

```sh
python3 -I -B research/split-minmax-audit-seed63/verify.py
```

Expected: JSON with `status: PASS_SPLIT_MINMAX_AUDIT`, `input_cases: 70337`,
`unique_block_tuples: 4656`, `principal_cost_premise_cases: 8701`, twelve
controls, and exact equality to [EXPECTED.json](EXPECTED.json). The local run
takes about one second; environment and additional checks are in
[VALIDATION.md](VALIDATION.md).

The registered checks run this again with `-O`, using explicit exceptions for
all acceptance predicates:

```sh
python3 scripts/research_package.py --package research/split-minmax-audit-seed63
```

No external package, compiler, network access or predecessor checkout is needed
for the finite check. The package launcher additionally checks Git provenance.
`--write-expected` deliberately regenerates the receipt; ordinary replay does
not write artifacts.

## Exact finite coverage

The primal enumerates nonsingular minors and combines disjoint row/column
masks. The dual exhausts all pairs of cuts. Each attaining packing and equal
cut is checked again by permutation determinants and ranks defined by
exhaustive minors. Weak duality proves these are finite optimality certificates
without assuming the general identity under audit.

- **65,665 common-matrix parameterizations:** every binary `v × v` matrix and
  every row/column support mask in three colors, for `v = 0,1,2`, including
  empty supports. Counts are `1`, `128`, `65,536` respectively.
- **4,096 arbitrary three-block inputs at `v = 2`:** all `16^3` triples of
  binary `2 × 2` matrices. These blocks need not share a common matrix.
- **576 sampled inputs at `v = 3,4,5`:** respectively `160`, `96`, `32` common
  matrix/support inputs and the same numbers of arbitrary three-block inputs.
  Sampling is `SHA256("split-minmax:63:counter") mod limit`, with the counter
  starting at zero and the draw order specified by `verify.py`.

The `70,337` count is of input parameterizations, not distinct matrices:
identical resulting block tuples are cached, leaving `4,656` distinct
certificate problems. No case is pruned from the declared domains. Larger
sizes are sampled, not exhausted, and rational decoder realizability is not
tested. With empty supports the checker verifies the partial-partition
extension; in the decoder model nonempty supports allow completion to full
partitions, as explained in the proof.

The checker also tests the sufficient principal-restriction cost premise in
every case. All `8,701` cases satisfying it have a perfect split. Controls
include reused original rows, incorrect certificate values, a nonsharp cut,
out-of-universe cuts, rational rank versus binary rank, term matching versus
nonsingularity, forcing equal row/column choices, overcounting shared capacity,
a bad finite-field specialization, omitted cut penalties, forcing `S = T`,
and using only the full cost instead of all principal-restriction costs.
The last control is an algebraic masked-matrix example, not a counterexample
to the exact rational decoder conjecture.

The stopping rule was completion of these declared domains and the named
proof audit. The general written argument relies on the cited standard
linking-system theorem; finite replay is not a formal proof of that theorem
or of the full multiplication bound.

## Pins, scope and overlap

Base: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
The selected conditional κ at that base is `0.001672660197076918`, through
PR1094 with PR589/PR555 on the bit side. Its construction and maintainer review
were inspected; this package does not alter them or rerun their cold replay.
The audited PR2162 head is
`113a718265c62aec301c5695f4bfb9c421bef7ab`. Git blobs, SHA256 pins, the selected
record's historical pin and the literature reference are in
[SOURCES.json](SOURCES.json).

Assignment seed **63** was the first OS-random draw. The explicit donor's
adversarial-audit track overrides the catalogue default. The changed scope
relative to the generic `uniform-transfer-audit` card, three candidate tasks,
time budget and stopping rule are recorded in [TASK.json](TASK.json).

The pre-claim complete overlap snapshot contained 539 open PRs and 1,036
Discussions. It found PR2162, PR2293 and the latter's handoff: PR2293 explicitly
leaves this min–max unchecked. PR2193's anti-Fano audit and the pool121
jet-rigidity claim address other implications. The
[sprint claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18941432)
and final freshness check are recorded with the validation evidence.

## Open next questions

1. Extract perfect splits and obstructing cuts for larger pairings using the
   polynomial matroid-intersection construction, rather than this deliberately
   small exhaustive checker. Start with PR2162's pinned `tied_min` full pairing;
   a separately reviewed implementation and its source-bound input are needed.
2. Formalize the copy-saturation and principal-restriction implications in
   Lean. Start with the finite partition-rank identity and matrix-rank
   monotonicity; a formal linking-system/min–max dependency remains a blocker.

Their relevance, first steps and blockers are structured in `TASK.json`.

## Attribution and license

DreamingOfClouds supplied PR2162's split statement and polynomial coefficient
argument, building on the PR1590/PR2111 decoder model. A. Schrijver supplied
the standard theorem used here. Aaron Wang's PR2293 is a complementary
independent audit of CR2/B2, rather than this split implication. Their work
is credited without treating pending submissions as selected suppliers.

Prepared by Charan (@theon199), with substantial OpenAI Codex assistance for
research, proof, code and verification. Parent-only execution; no independent
human review is claimed. The retained source excerpt and all new material
are Apache-2.0 under the repository license. The cited paper is linked, not
redistributed.
