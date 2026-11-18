# A 2,106-bank order for the #7674 native graph

The forward graph of #7674 admits a legal serial row order using **2,106 snapshot banks**, 319 fewer than the 2,425 required by the order in #7681. The new order first reaches its peak at event 3,022, row token 94,904. The certificate supplies a bank for every entrance, paid return and terminal output. This answers the first open question in Ali Romman's fixed-order allocation. [#7681 proof and contract](https://github.com/aliromman/integer-mult-bounds/blob/1753a3ff56be34b09a217b12b590f51eba15defb/research/banked-native-snapshot-reuse/PROOF.md)

| Field-level reservation | #7681 order | New order |
| --- | ---: | ---: |
| Snapshot banks per forward occurrence | 2,425 | 2,106 |
| Private homes including the paid-row accumulator and four scratch fields | 2,430 | 2,111 |
| Private homes for 16 disjoint occurrences | 38,880 | 33,776 |

## Choose the next row

Copy all 1,501 public entrances into distinct private banks. A row becomes ready when every paid donor has returned. Among ready rows, choose the one with the most donors whose only remaining use is this row. Break ties by the smaller integer row token. The donor list contains each donor once. Its last use can release its bank after the row and its child return. The rule uses only the fixed graph and can be run before field data are available.

The generated order covers all 6,142 paid rows and all 1,501 terminal rows. A token's lifetime starts at its birth and ends at its last read, inclusively. An unread nonterminal may retire immediately after its birth. All terminal lifetimes extend through the common installation event. The allocator chooses the lowest free bank, releasing a previous owner only when its end precedes the next birth. The entrances use bank `i` for input role `i`.

## Why the order preserves the map

Induct on completed rows. At entry each bank holds its specified input at its original chart. Reserve the row's return bank before its first read. For each donor in the frozen order, the replay checks that its slot holds that exact token at the row's source chart. The coefficient travels with the donor in the frozen graph. The unchanged scalar operations therefore form the same sum, including every prefix, on arbitrary entrances. A paid row runs its original child and adapters between the same two charts. No other row starts until that return finishes. A terminal row accumulates directly into its reserved slot. Each donor stays live throughout the row.

Once every read of a donor is complete, the bank can undergo its full retirement and initialization before reuse at a new chart. At installation the replay reads every terminal owner in its final chart, then checks that retirement empties the pool. Thus a permutation of complete rows preserves the labelled operator under the source's field and child contracts. The argument needs no numerical samples or assumptions about equal snapshot values.

The verifier reconstructs lifetimes for allocation. A separate replay has no access to their end times. It counts unread donor occurrences, checks each bank's current owner and records simultaneous occupancy immediately after each new reservation. All 9,144 assignments fit and the replay reaches 2,106 simultaneous owners. This makes 2,106 exact for **this particular order** under distinct-snapshot ownership. Other legal orders may require fewer banks. Two controls check that aliasing a donor with its consumer's return slot and using the supplied assignment with one slot removed both fail. [Generated result](RESULT.json) · [Verifier](verify.py)

## Field-level costs and limits

Per forward occurrence there are 9,144 snapshot lifetimes, 6,142 uses of the shared paid-row accumulator and four scalar scratch lifetimes. Each of the resulting 15,290 lifetimes pays for full initialization and retirement. With 169,343 scalar terms and 7,643 rows, the source's conservative reset allowance for 16 occurrences is

```text
16 × (2 × 15,290 + 4 × (169,343 + 7,643)) = 11,816,384.
```

Each donor read, coefficient, paid transfer, entrance copy and public installation belongs to the same labelled row as before. Each bank reuse pays for view setup and full-extent reset. For equal extent `L`, the source's serial selector bound uses `O(2111 (L+1))` per selection, scan and return. Changed views pay their actual packed extent. Public fields, guides, guards, suspended parent storage, recursive child and adapter workspace, and compiler backing carry their separate source charges. [#7674 physical model, section 4](https://github.com/aliromman/integer-mult-bounds/blob/26b6c469aa6c4aa04322ce25a22150f90e5fb14e/research/p104-banked-transfer-pivots/PROOF.md)

This is a finite storage certificate with a scoped operator-preservation proof. It gives no global scheduling optimum or new κ. Physical operator correctness and the five framework assumptions are inherited. Physical operators, fixed-tape lowering, the complete caller, the selected cold replay and a formal proof were outside the verification scope.

## Reproduce

From the repository root with CPython 3.12 and its standard library:

```sh
python3.12 -B scripts/research_package.py --package research/banked-native-row-order
python3.12 -I -B -W error research/banked-native-row-order/verify.py
python3.12 -I -B research/banked-native-row-order/verify.py --certificate > /tmp/banked-native-row-order.tsv
```

The final command emits all assignments in event order. Event zero contains all entrance copies. Each later line identifies the row and its reserved bank. Its TSV SHA-256 is `16de610956122d9f2c68f05d955b5484a0ee31bf201b69546a092495bf97dd86`. The default replay checks the receipt against the graph, verifier and complete allocation hashes. Normal and optimized runs use the same owner checks.

## Inputs and credit

This construction and allocation certificate were produced by Nick Petalas. Ali Romman posed the changed-order question, proved the prior fixed-order minimum and supplied the bank contract in #7681. His #7674 supplies the fifteen-pivot graph, the row and child semantics, and the physical cost model. SYLforge supplied the #7669 native word and caller. The retained notices credit the underlying work by DreamingOfClouds, Clear1nsight, Rohan Arun, Jerry Chen, Douglas Colkitt and their predecessors. [#7681](https://github.com/CrocSwap/integer-mult-bounds/pull/7681) · [#7674](https://github.com/CrocSwap/integer-mult-bounds/pull/7674) · [#7669](https://github.com/CrocSwap/integer-mult-bounds/pull/7669) · [Source notices](notices/)

Clear1nsight supplied the canonical comparator encoding and its published digest in #7682. The bundled `PEER-GRAPH.json.gz` was materialized from the #7674 constructor with fifteen fixed pivots, using #7682's `record(..., "peer")`. The verifier pins the decompressed payload to `graphs.peer.canonical_sha256` in the published receipt. This identifies the graph separately from its gzip encoding and from #7682's role-230 candidate. [Graph constructor](https://github.com/aliromman/integer-mult-bounds/blob/26b6c469aa6c4aa04322ce25a22150f90e5fb14e/research/p104-banked-transfer-pivots/network.py) · [Comparator encoder](https://github.com/Clear1nsight/integer-mult-bounds/blob/1b4a4d6f9370b8c93b3f769a6229a9111ef3940e/research/p104-role230-banked/engines/graph.py) · [Published graph digest](https://github.com/Clear1nsight/integer-mult-bounds/blob/1b4a4d6f9370b8c93b3f769a6229a9111ef3940e/research/p104-role230-banked/evidence/WIRE-RESULT.json)

## Open next questions

What lower bound holds for *all* legal topological orders under the same distinct-snapshot and common-installation contract? One first step is to find a family of donors and terminal outputs that must coexist across every legal ordering. Such a bound would measure the remaining room below 2,106.

Can a concrete tape layout realize the 2,111-home reservation with the actual views, guards and suspended owners? A first step is to assign each bank its packed extent and charge its selection, initialization and return on consecutive uses. [Task record](TASK.json)
