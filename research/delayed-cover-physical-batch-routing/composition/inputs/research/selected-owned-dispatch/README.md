# Signed-query suspension and return on 23 fixed tapes

This package connects the actual 243/248-instruction signed-query routines to
the retained continuation and output-return machines. Seven-symbol query tapes,
including internal logical blanks, are encoded as binary segments. The caller
can suspend a nonzero private stream, execute nested calls, recover the output
before child erasure, restore its counters, add to the original destination,
and erase its private work. The same 23 physical tapes serve every depth.

The written induction covers every finite depth and record width satisfying the
stated signed headroom and input-format contracts. The executable grammar uses
a supplied unary depth and a named identity leaf; it is **not** the selected
Gaussian implementation or the full compiled caller. Its equal-sized child
fields use O((depth+1)N) backing under bounded encoded entry extents. We do not
claim the selected root-volume bound from this test grammar.

The new bridge has the exact additional action bill
`34Lz + 21Lp + 21Lm + 13L + 283`, beyond the unchanged continuation invoice.
Lengths include encoded markers and materialized logical blanks. Erased cells
remain in retained backing. Arbitrary warm **physical** blank capacity is
charged to entry K0; arbitrarily long **coded logical** blank tails cannot be
silently treated as free when copied into descendants.

Independent source checks also bind PR5811's complete raw P104 caller to 13,444
productive fields and a safe 626 private banks, and the retained BIT caller to
11,454 productive fields and a safe 129 private banks. These are raw allocations,
not the final uniform compiler's inventory. No private field receives productive
credit. The numerical words and paid profiles are unchanged.

**All five project assumptions remain retained.** [BINDING-STATUS.md](BINDING-STATUS.md)
identifies the unresolved delayed-cover BIT fiber/row mapping and old
atom-interchange space binding. [ALLOCATION-THEOREM.md](ALLOCATION-THEOREM.md)
gives a noncircular all-size ownership implication under explicit local-machine
and row-geometry premises; it does not assert those application gaps solved.

## Evidence and reproduction

```sh
python3.12 -B scripts/research_package.py --package research/selected-owned-dispatch
```

Expected: `PASS_SELECTED_QUERY_DISPATCH` in normal and isolated optimized modes.
The replay is read-only and authenticates working source bytes before importing
them. It checks 114 nested-chain cases, nine unequal-size subjob boundaries,
27 exact invoices, eight coded-tail cost cases, six physical mutations, seven complex owner mutations, one
BIT mutation and six compiler-name controls. Finite replay corroborates the
written [boundary proof](PROOF.md); it is not a formal proof of multiplication.

The new artifacts are `RESULT.json`, `BOUNDARY-INVOICE.json`, `CONTROLS.json`,
`OWNERSHIP.json`, and `BIT-OWNERSHIP.json`. [FRESH-NAMES.md](FRESH-NAMES.md)
binds the compiler's existing logical allocation result without assuming the
physical erasure that is being investigated. Human and proof-kernel review
remain open.

## Open next questions

- Represent the input-dependent delayed GL cover on fixed streams, with its
  exact child fiber, common weight descriptor, return mapping and space bill.
- Instantiate the complete selected finite continuation and complete-row split
  using actual admitted child implementations.
- Bind global signed headroom and the fresh expanded storage constants.

[TASK.json](TASK.json) gives the first step and blockers for each. This completes
a scoped part of the [released physical-dispatch handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/5009#discussioncomment-19172867),
not its entire production gate. Canonical [claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/5009#discussioncomment-19206017).

## Attribution and source scope

Mason Hale with substantial OpenAI Codex assistance; Apache-2.0. Base
`de5ec2e7a6074068452f45b1a191b5c72832df4a`. The P104 input word is from
[PR5811](https://github.com/CrocSwap/integer-mult-bounds/pull/5811), exact head
`883ab9ca680906a0df88fb74ff51d634868af363`; its full notices remain in
`source/NOTICE`. It is separate from the selected PR5599 record.

JoyboyBrian supplied the signed query, David Arias the finite assembler and
counters, Ali Romman the delimited continuation/output return and P104 caller,
and zxv the retained-backing result and native/compiler work. Matarener supplied
the logical lifetime/completion audits; Jacob Alan Sussman supplied the mixed
integer flow. Cinna Davis, Joel Pulikkan, Gareth Davidson and the retained
P104/BIT contributors keep their source credit. We reuse PR5116, PR5356,
PR5368, PR5404 and PR5443; the contribution is the actual representation/return
connection, its charged implementation and the current raw ownership bindings.
