# Reuse private snapshots after their last complete read

## Result and exact contract

The final forward graph in [PR #7674](https://github.com/CrocSwap/integer-mult-bounds/pull/7674) has 6142 paid rows and 1501 terminal rows. Its source [proof, section 4](https://github.com/aliromman/integer-mult-bounds/blob/26b6c469aa6c4aa04322ce25a22150f90e5fb14e/research/p104-banked-transfer-pivots/PROOF.md) reserves 15290 private full-field homes per native occurrence. The construction below uses **2430**: a pool of 2425 snapshots, one shared source accumulator, and four scalar scratch fields. Sixteen disjoint occurrences need 38880 such homes instead of 244640. Public fields, child and adapter workspace, guides, guards, and compiler backing remain additional.

The snapshot pool size 2425 is exact for the following contract. This is not a lower bound on all implementations.

1. Use the exact final forward row order from the pinned `Network.schedule()`.
2. Copy all 1501 independent entrances into distinct private snapshots before the first row. Each graph token has its own immutable snapshot while live. Equal linear forms are not merged.
3. Reserve the new result bank before the row starts. Keep every donor through the completion of the whole row, its child and both adapters. Do not overwrite a last donor in place.
4. Do not recompute a token or change scalar donor order. Retain all terminal rows until all 1501 outputs can be installed.
5. Reuse a home only after full retirement of its old owner. Initialize its full extent for the new owner. A change of chart also needs the source's view preparation.

The source graph constructor is reused, not independently reimplemented. The new allocation and replay bind to all fifteen source pivots. They do not transfer to a later changed graph without a new check. The schedule hash is `bbcb021bdff9d4f205e327abba9a77480c487979eeabb27a481ec8919e570b8e` under the canonical JSON encoding in the verifier. [Source inventory](PREDECESSOR.json) · [Allocation](ALLOCATION.json) · [Receipt](RESULT.json)

## Closed lifetimes and an attaining allocation

Number the 7643 row events from 1. Event 0 contains all entrance copies. For a token v, let b(v) be 0 for an entrance, or its row event otherwise. Let e(v) be its last consumer row. If there is no consumer, use b(v). For a terminal token set e(v)=7644, the installation boundary. Its lifetime is the closed integer interval `[b(v),e(v)]`.

At row i, each donor with final use i must coexist with the new result bank. This is why both endpoints are closed. Retire those donors only after the row completes. An unused entrance can retire after the entrance-copy phase. A paid result with no consumer can retire after its return. A terminal output cannot retire at its birth.

Process tokens by increasing birth event, with increasing token as the tie rule for entrances. Reuse the least-numbered free slot. A slot is free only if its preceding owner's end is strictly less than the new birth. Otherwise create a new slot. `ALLOCATION.json` gives all 9144 token-to-slot pairs. This includes all entrances, all 6142 returned paid fields, and all 1501 terminal accumulators.

This allocation uses 2425 slots. An independent difference sweep adds one at every birth and subtracts one just after every end. Its maximum is 2425. The first maximum is event **5755**, row token **98194**. The allocation file lists all 2425 tokens live at that cut. They have distinct owners and occupy distinct slots. Any allocation under this contract needs at least that many slots at this cut. The construction attains the lower bound. Equivalently, the usual greedy interval allocation cannot need a new slot unless all prior slots have live owners at that same birth event. This elementary interval method is prior knowledge; the source-bound certificate is the contribution.

The lower bound does not apply to a changed order, early donor release inside a row, in-place accumulation, recomputation, sharing equal values, or use of public fields as working storage. The total 2430 is an upper bound for the full private reservation; only the 2425 snapshot component is proved minimum.

## Execute the allocation without losing an owner

Give each bank a physical occurrence tag and a current token and chart. At entry, initialize each entrance slot and copy the corresponding arbitrary public input. Public entrances stay intact until final installation.

For a paid row, reserve its pool slot at the return chart. Initialize the one shared source accumulator at the source chart. Read donors from their recorded slots in increasing token order. Perform each exact coefficient product and addition. Every donor keeps its value and chart. Apply the original complete child and both adapters to the accumulator, with the same source and destination charts as before. Store its completed return in the reserved pool slot. Finish all return and view work before retiring the accumulator or any final-use donor.

For a terminal row, use its reserved pool slot as the source accumulator itself. It needs no paid child. The donors all have that terminal chart. Keep this bank through installation. Thus a terminal row does not cause an extra source accumulator, copy, or lifetime.

The shared accumulator is never reused while a child is active. All other live snapshots and the parent tuple remain parked during the child. Its internal backing and adapter workspace remain separately charged, as in the source. Each bank gets its new chart only after full retirement and initialization. The proof does not infer a free chart conversion on a live field.

Induction over the row events proves correctness. Every read finds the intended unmodified token at the required chart. The new accumulator therefore has the same linear form as the source row at each scalar prefix. The unchanged complete native map returns that form at its specified chart. Retirement removes only values with no later consumer. All terminal forms remain available for simultaneous public installation. After installation, retire every terminal bank and all scratch. This proves the field-level allocation for all admitted field sizes under the same physical primitives as the source.

The replay uses a different lifetime mechanism from the allocation generator: live token owners and remaining consumer counts. It stores each formal scalar row in its assigned slot, checks every local chart, and executes all 8533666 coefficient products on the source sufficient grid 530841600. It verifies every division before addition and all 1501 endpoint rows against a separately built public specification. It finishes with no active private token and no remaining consumer. This is exact symbolic scalar execution, not a materialized physical Clifford or tape replay.

## Preserve the complete local reset count

Physical reuse changes the number of simultaneous homes, not the number of logical lifetimes. The count is:

| Kind | Lifetimes per native occurrence |
| --- | ---: |
| Entrance snapshots | 1501 |
| Returned paid snapshots | 6142 |
| Terminal accumulators | 1501 |
| Uses of the shared paid-row accumulator | 6142 |
| Scalar scratch fields | 4 |
| Total | 15290 |

Each lifetime has one full-extent initialization and one full-extent retirement. The total is 30580 reset services per native occurrence. It equals the source reservation's initialization/retirement allowance, although several services now touch the same physical home at different times. No reset is omitted because a bank was used before.

There are still 169343 scalar terms and 7643 rows. Keep the source's additional four reset services per term or row. Across sixteen native occurrences the same conservative reset allowance is:

```text
16 * (2 * 15290 + 4 * (169343 + 7643)) = 11816384.
```

Every paid source/return copy, entrance copy, terminal installation, scalar operation and recursive call has a corresponding source operation. Direct terminal accumulation avoids an additional output copy. The 6142 paid calls and complete productive invoice do not change. Reuse requires the same full view preparation on each new lifetime; it does not supply free setup, zero scratch, or dirty erasure.

For equal views of extent L, the source selector argument can reserve K=2430 homes and charge each complete selection, scan and return at `O(K*(L+1))`. Charge changed views at their actual packed extent. Keep guides, guards, child/adapter backing and suspended owners separately. In a finite compiled template with J native occurrences, `2430*J` replaces `15290*J` only in this native-home term. All other stock terms remain. The selected compiler and fixed-tape hypotheses still supply the physical primitives and asymptotic absorption. No concrete transition table, runtime reduction, root precision change or kappa improvement is proved here.

## Verification limits and controls

The checker independently compares intervals within each assigned slot and sweeps all endpoint counts. A second pass executes the allocated owners and exact scalar values. Six controls reject a live-bank collision at the maximum cut, retirement before a last read, loss of terminal outputs, a pool one bank too small, a missing allocation token, and a sign error in a terminal row. The controls must fail at their named boundary.

The proof establishes one source-specific allocation under an explicit storage contract. Source input bytes are checked with Git-blob and SHA-256 identities. It does not recertify the source's pivot discovery, native operators, complete signed caller, compiler, precise scalar machine or all-size assumptions. The five selected assumptions and selected frontier are unchanged. Independent human and formal-kernel review are unclaimed.

## Credit

Ali Romman prepared this allocation, proof and verifier with substantial OpenAI Codex assistance. The graph, banked construction, physical reservation and sufficient arithmetic grid are prior work in [PR #7674](https://github.com/CrocSwap/integer-mult-bounds/pull/7674), scientific commit `26b6c469aa6c4aa04322ce25a22150f90e5fb14e`. Its parent is SYLforge's [PR #7669](https://github.com/CrocSwap/integer-mult-bounds/pull/7669). Preserve the [source notices](predecessor/NOTICE), [original parent credit](predecessor/source/7669-CREDITS.md), and [prior bank notice](predecessor/source/7663-NOTICE). They retain the DreamingOfClouds, Clear1nsight, Rohan Arun, Jerry Chen and selected-construction lineage. The separate minimum-grid audit in [PR #7680](https://github.com/CrocSwap/integer-mult-bounds/pull/7680) changes no allocation and is not an arithmetic dependency here. New work is Apache-2.0.
