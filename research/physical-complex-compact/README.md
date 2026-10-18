# Encoded physical compact operations

I implement the complete dirty compact operation from
[PR2250](https://github.com/CrocSwap/integer-mult-bounds/pull/2250) with encoded
numerical controls, fixed physical tape roles and the actual binary ordinary
backend from [PR2899](https://github.com/CrocSwap/integer-mult-bounds/pull/2899).
I include the raw rotations, exceptional-record repair and final selected-bit
operation. I support either source order and constant toggles, preserve borrowed
input and descriptors, and concatenate arbitrary positive outer rows in order.

Under the pinned ordinary-callee arguments, I obtain the existing compact bound
`O(V*(1+((f-1)*G)^tau))` in the retained long-record domain, with
`tau=99830289/100000000`. I give the complete pre-absorption charge and workspace
bound in [PROOF.md](PROOF.md). I add the physical execution and ownership
boundary; Douglas Colkitt supplied the compact identity, guard and repair method.

I keep the complex layer's recursive caller, Gaussian phase/arithmetic execution
and analytic transfer outside this package. I leave the selected frontier
unchanged. B1 suffices for the current selected consumer, but I do not claim its
rate suffices for the higher candidate bound in PR2979.

## Physical boundary

`CompactEngine` compiles a fixed field schema, source/target names and source
order. At runtime I supply n, K, G, rho, field widths, record width and outer-row
count as canonical Count tapes. I use no decoded numerical layout, indexed
payload oracle or dynamically allocated physical tape during a call.

For each complete outer row I execute four binary swaps and four rotations
for an earlier source or toggle, or twelve swaps and ten rotations for a later
source. I extract exceptional records with encoded keys for `T(S^-1(q))`, sort
them by literal stable binary partitions, and refill exactly their marked holes.
I then handle the highest selected bit. I restore dirty compact labels and
unselected bits before returning the complete owner packet.

I suspend the compact allocation scope during each binary call, copy its
protected return into a caller-owned lease, then clear its output port. I erase
owned work on successful return. The caller consumes the protected compact
output before reuse. I make no interrupted-macro rollback claim.

The simulator keeps blank backing arrays after erasure. For reuse I bound their
extent by each role's largest preceding use; I do not claim that a later smaller
input shrinks them. I separate this bound from blank contents and head restoration.

## Evidence and reproduction

I check the following boundaries with Python 3.12 and the standard library:

| Check | Coverage |
|---|---|
| Encoded controls | 151 states and 904 offsets; both guard regimes, signed offsets, current inverse controls and a repair crossing a dirty-field slice |
| Complete small rectangles | Early, late and toggle operations; multiple outer rows, output reuse and q=3 binary padding |
| Complete two-digit rectangles | 4,096 records in each source order, including q=3 padding |
| Complete mixed guard | 8,192 records: 2,048 guarded and 6,144 exceptional, through actual raw movement and repair |
| Fitted binary boundary | 1,024 independent input columns through two preceding-stage roots, with live parent numerical roles preserved |
| Failure controls | Changed archives, namespace collision, omitted repair/inverse, reversed key order, premature output reuse and physical allocation |

I track each payload input bit with a separate checker-only provenance mask.
I disable the indexed reference oracle during physical payload execution and
compare results afterward. The complete Compact fixtures use B1's elementary
branch; the separate handoff fixture forces a declared reduced fitted body.
I have not executed the selected GL64 or O(73,2) payload, or a formal refinement.

```sh
python3.12 scripts/research_package.py --package research/physical-complex-compact
```

I preserve both source archives and their notices. [SOURCES.json](SOURCES.json)
pins the transitive ordinary inputs and the compact/row proof sources;
[VERIFY.json](VERIFY.json) registers the cold commands and
[RESULT.json](RESULT.json) records complete typed-result hashes.

## Open next questions

1. Bind the physical compact engine to fixed Gaussian monomials. Start with the
   actual selected recipe and preserve forward phase-before-affine and inverse
   affine-before-phase order. The remaining work includes encoded phase
   accumulation and signed-component traversal on the root precision grid.
2. Implement the complete complex caller on those primitives. Start with one
   actual local invocation and its private lifetime, then proper-width child
   dispatch and whole-row restoration. The written PR2287/2298 compositions
   remain dependencies; the present compact endpoint does not execute them.

I coordinate in [Discussion2238](https://github.com/CrocSwap/integer-mult-bounds/discussions/2238#discussioncomment-18971213).
[TASK.json](TASK.json) records the revision-6 overlap check and decision to
avoid repeating the existing PR2979 group/native-cone audits.

## Attribution

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance in
mathematics, implementation, source analysis and prose, including analysis
subagents. Apache-2.0; I claim no independent human or proof-assistant review.

I retain Douglas Colkitt's compact construction and the guard-audit lineage in
PR2250's unchanged NOTICE. I retain David Arias's caller, Nick Petalas's ordinary
wrapper and q-adic work, Adam Gall's borrowing boundary, Aakash Thakkar's stock
fit, and the remaining BIT source credit in PR2899's archives. I credit ywz65's
PR2534 for the earlier complete selected-child/outer-row fixture. I retain the
PR2378/2422 formal phase results and PR2476/2700/2756 repair boundaries; I do not
repackage those results as this physical implementation.
