# Complete balanced CRT state traversal with changing node precision

The actual numerical/ROM row pipeline now runs the whole balanced CRT
state tree on one source tape, using the same owned backing as its node
and precision change. This closes the changing-node composition left
explicitly outside [#5625](https://github.com/CrocSwap/integer-mult-bounds/pull/5625)
and [#6100](https://github.com/CrocSwap/integer-mult-bounds/pull/6100).
The contribution is a source-relative construction and quantified proof;
**no new kappa or full foundational-assumption discharge is claimed**.

The controller reuses the exact 118-role #6100 workspace and the unchanged
#5496 physical query. Eight additional owned zero words are physically
prepared and retired at the actual node precision, satisfying the original
numerical entry's width premise. One staging role keeps the original
retire-before-source-update order. There are 127 owned backing roles in
total, and every older retained tail remains counted after erasure.
The source is a separate supplied role. This is not a whole-machine tape
count: topology/control and source-generation storage remain separate.

## Exact result

[PROOF.md](PROOF.md) covers every power-of-two axis count, declared widths
`h_i in {ell-1,ell}`, pairwise-coprime admitted moduli, and every padded
coordinate tuple. Complete forward and reverse traversals use the same
physical source, retain all non-coordinate fields, and return every owned
role blank at its specified head. The only predecessor workspace change
is the authenticated geometry guard in [SEAMS.json](SEAMS.json).

The complete within-interface time is the **sum** of the inherited row
bills, with paid changing-precision word preparation. Geometric summation
gives the deliberately loose source-operation bound

`T <= 2^34 * 2^(3ell) * (p+2)^8` when `sum h_i <= p`.

At `p>=14` this is below the published `2^(4ell)(p+2)^16` envelope shape.
This does not identify source operations with binary TM steps. Compiled
topology production and encoded traversal, source production, the
variable-geometry exceptional key and
payload routing still have to be supplied and charged at their own
interfaces. A fast numerical address evaluator is not a fast permutation
of all payload records.

The retained-work envelope is `O(2^ell p ell^2+p^2)` and is independent of
the number of successful traversals. It bounds each role's historical
maximum separately, including the eight current-width numerical words
and the complete source/staging extents.

## Executed evidence

[RESULT.json](RESULT.json) freezes the exact deterministic observations:

- A complete four-axis forward/reverse traversal executes 30 node-row
  commands at precisions 7, 5 and 11, using 28 actual unchanged ROM
  producer calls and 500,394,012 producer instructions. The valid forward
  endpoint `(3,4,0,1)` also matches a separately implemented defining CRT
  formula. All source bytes return after reverse traversal.
- The same 127 owned roles plus source retain 7,176 finite-symbol tape
  cells. Larger and smaller numerical/ROM histories occur in one run.
- A second actual fixture exercises invalid-left disabling and padded
  target coordinates. All 40 executed node-row commands preserve their
  declared entry/retirement contracts.
- Eleven controls detect live-owner reentry, premature source mutation,
  changed global shape, stale retired tails, unretired word resizing,
  the old fixed-node boundary, invalid topology, an omitted subtree, and
  max-of-totals storage and a false geometric-series coefficient caught
  during independent review. 182 exact tariff cases corroborate the written
  geometric summation; they are not an all-parameter proof by testing.

The complete physical query, numerical arithmetic and ROM producer run;
the verifier's oracle supplies no runtime coordinate, table or branch.
Initial fixture serialization is explicit and occurs once per source.

## Reproduce

Python 3.12, standard library only, from repository root:

```sh
python3.12 -B scripts/research_package.py --package research/crt-whole-tree-state --check-only
python3.12 -B scripts/research_package.py --package research/crt-whole-tree-state
```

The registered normal and optimized runs each have a 300-second limit and
compare the same frozen receipt. Direct `verify.py` is read-only unless
`--write-result` is requested. The expected marker is
`PASS_CRT_WHOLE_TREE_STATE four_axis_rows=30 producer_calls=28 retained=7176 controls=11`.
[VALIDATION.md](VALIDATION.md) records actual executed checks and limits.
The separate [independent review](independent-review/REVIEW.md) includes
its own read-only tariff, source-seam and protected-word lifecycle checker;
it runs as the third registered command with a 30-second limit.

## Novelty, source pins and limits

Canonical base: `e54523517d0f03e58352e647c403a5af3e525a57`, selected
conditional kappa `.00363005817` from #7000/#7001. [SOURCES.json](SOURCES.json)
pins all 41 consumed predecessor files by SHA256 and Git blob. No frozen
predecessor or selected record is changed. The overlap review is in
[OVERLAP.md](OVERLAP.md).

#4195 already supplies CRT algebra, mixed-width synchronized rows and
whole-tree logical order. #5625 already installs a current row into its
same source. #6100 already reuses the actual row roles at one fixed node.
The new result composes that actual pipeline across all nodes and their
different precision while preserving its exact entry premises and paying
the whole tree. No generic historical-max identity or CRT algebra is
claimed as new.

The supplied topology is compiled data. A uniform binary topology
controller, initial descriptor/axis production, the three-epoch repair
key, actual payload layer, ordinary interchange, numerical/global
precision and the complete outer assembly remain separate obligations.
The predecessor numerical and ROM theorems remain inherited hypotheses.
No full multiplier, selected cold replay, Lean, Docker, independent human
review or formal-kernel acceptance is claimed.

## Open next questions

1. Produce and traverse the compiled level/node/row schedule from encoded
   geometry on fixed tapes, charging setup and metadata storage. Start
   with the precise `commands` order and the existing node entry ABI.
   This removes the supplied-topology boundary left by the present theorem.
2. Bind the variable-geometry three-epoch exceptional key to actual
   current-coordinate records, including their transport, role lifetimes
   and bit-step conversion. Whole-tree state composition does not itself
   instantiate the compact macro's three different epochs.
3. Connect a complete payload consumer using the same cost units and
   full fiber. The ordinary interchange and sparse repair premises
   remain blocking interfaces.

## Credit

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
Apache-2.0. Retain Ali Romman's #5353/#5625 row entry and source update;
JoyboyBrian's #5053/#5219 numerical lifecycle, #5092 ROM producer,
#5496 query and #6100 stable workspace; commdata2338's #5519 bank audit;
ToikY's #4195 mixed caller and #4192 arena work; Hiroki KUMAZAKI's
current-state/placement lineage; Cinna Davis's #4100 CRT construction;
and all pinned notices for Tekalign, Jose Manuel, Ryanson Jonathan,
unpaidmoon, Douglas Colkitt, John-Michael Smith and earlier contributors.
