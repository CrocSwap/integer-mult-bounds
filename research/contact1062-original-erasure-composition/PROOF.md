# Literal composition on the original 74 erasures

The common word is Ali Romman's #7605. DreamingOfClouds supplied the main-46 edit used by #7642 and the role-82/185 repair underlying #7644. Clear1nsight supplied the 134/329 contact used by #7643. The signed caller is Rohan Arun's #7113. The input files, head identifiers and raw SHA-256 pins are bound by `construction/gate.py`.

## Clocks and construction

A surviving #7605 instruction keeps its integer origin. An insertion has origin `[42 or 44, #7605 anchor, index within insertion]`. Each of the five #7643 replacements retains its #7642 origin, except the deleted MOVE. The #7642 source edit has a five-instruction shift at its positive source anchors and zero shift at entrance. The #7644 edits already use #7605 clocks. Append each #7644 insertion immediately before its surviving #7605 anchor on #7643, after the eleven #7642 prefix operations at anchor zero. Check the old opcode and operands for every deletion. This reconstructs all three supplied peer words byte-for-byte after canonicalization. The final full gate emits the complete clock map with inclusive affine intervals and explicit exceptions.

| Origin in #7605 | #7642 | #7643 | Combined | Instruction |
|---:|---:|---:|---:|---|
| 41038 | 41049 | 41049 | 41065 | MOVE 134 from 3 to 373 in #7643 |
| 41039 | 41050 | deleted | deleted | Old MOVE 329 from 373 to 618 |
| 41040 | 41051 | 41050 | 41066 | ADD 134 from 329 at chart 373 |
| 41131 | 41142 | 41141 | 41157 | Return 329 to chart 733 |
| 42075 | 42086 | 42085 | 42101 | Return 134 to chart 913 |
| 42110 | 42121 | 42120 | deleted | Old MOVE 185 into 1062 |
| 42111 | 42122 | 42121 | deleted | Old MOVE 82 into 1062 |
| 42112 | 42123 | 42122 | deleted | Old ADD 185 from 82 at 1062 |
| 42194 | 42205 | 42204 | 42217 | Direct MOVE 82 to 1071 replaces the second leg |
| 43584 | 43595 | 43594 | 43607, 43608 | Direct MOVE 185 to 922, then subtract one quarter of 779 |
| 43586 | 43597 | 43596 | 43610, 43611 | Subtract five quarters of 7, then retain original ADD of 7 |

## Operand streams at chart 922

The admitted first gate examined all 24 incident events in #7605 and #7643 and all 26 in #7644 and the combination. The five literal #7643 edits themselves operate on 3, 373, 618, 733 and 913. They shift clocks at 922. The two extra scalar observations at 922 enter through #7644. Checking only the intersection of the named roles would miss the carrier chains and the destination-before-update values.

At chart 3 the repair adds the same linear form to 196 and 185. In original public-input coordinates it is

    -x991/16 + 3*x988/16 + 5*x599/4 - x453/4 - x415 + x367/4 - 4*x350 - x311/2.

In the combined word, 779 receives twice 521 at clock 41306 in chart 743, then subtracts 949 at 41311 in chart 922. The 949 operand itself comes from the chart-3 exchange with 960. Role 7 receives twice 717 at 41021 in chart 264 and reaches 922 at 43609. Role 587 receives from 985 in chart 790 and subtracts 960 at 42056 before 196 reads it at 43659. The 185 and 196 inputs also have intermediate writers. For example, 185 receives from 83 at 40522, and 196 receives from 518 at 42332. These paths are included even when the source or writer is outside chart 922.

The full late donor rows actually share inputs with the entrance repair. Restricted to its eight columns, the 779 row is

    x311/2 - 16*x350 + x367 - 4*x415 - x453 + 3*x988/4 - x991/4,

and the 7 row is −x311/2 + x599. Thus one quarter of the first restriction plus five quarters of the second exactly reproduces the entrance form, including the net −x311/2 from the two paths. The donors also have coefficients outside these eight columns. The gate compares those columns as well. A role-number disjointness argument could establish neither identity.

At 43608 the receiver 185 subtracts one quarter of the complete 779 row. At 43610 it subtracts five quarters of the complete 7 row. Its value immediately before the retained ADD at 43611 has the same exact row as #7643 at 43596. The next exchanges between the repaired roles occur at 43718 and 43879. The first reads 196 into 185 and the second reads 185 into 196. Their pre-operation receiver and sender rows match the corresponding #7643 rows at 43703 and 43864. Replaying the intervening chart-922 operations is necessary to establish these identifications.

The first gate computes the backward live operand slice for each word, then evaluates it forward on independent public inputs with exact integer numerators over a fixed grid. It rejects a nondivisible product. For a common event it tests the mixed difference combined − #7643 − #7644 + #7605 on each operand. For a one-sided insertion it directly compares the two words that contain it. The admitted result recorded 103 operand positions, 66 distinct full forms, and zero differences between #7643 and the combined word at every jointly observed operand. The complete coefficient lists, preceding writer clocks, event origins and recursive writer edges are in `receipts/first-provenance.json.gz`. A null preceding writer denotes the entrance value of that register. MOVE transports the normalized row unchanged. Physical MOVE maps are checked separately.

## Physical and private obligations

Write the normalized state of a role in chart c as x and its physical state as F_c x with the signed canonical frame. The 134/329 contact takes arbitrary normalized inputs x and y to x−y/2 and y. Recharting the coframe ADD from 618 to 373 gives the same exits in 913 and 733. The recipient's original contribution, the donor's contribution to the recipient, and the donor's retained return each have a separate exact forward and adjoint route check. The contractions through 1062 on roles 82 and 185 and through 245 on role 46 likewise compose to their direct maps. Exact Gaussian matrix comparison keeps absolute phase. A quarter-turn mutation exercises the distinction.

The full gate evaluates the entire words on independent public inputs. Every private instruction is paired by original event identity and order. Matching the complete operand tuple on entry and the identical instruction fixes the private destination on exit, including public destinations that read private sources. Each CLEAR compares its actual pre-erasure row. Each COPY requires a zero destination. All public outputs, arbitrary helper returns, private closures, lifetimes, and final charts are checked against #7605. The returned rows and exposed erasure rows specify the linear map on all public inputs, hence also its transpose. The exact finite checks in this construction do not price the combined word or certify a new multiplication exponent.

## Frozen candidate and transcript

The coordinator admitted both commands on 17 November 2026, with one thread per process. The first gate ran from 21:58:42 to 21:58:46 UTC and the full gate from 22:05:15 to 22:05:46 UTC. Both exited 0. The registered rows stage reconstructs the full word in a new temporary directory.

The generator uses sorted compact UTF-8 JSON, gzip level 6, an empty embedded filename and mtime zero. Its one output word has 76,660 events, canonical SHA-256 `58a045048c853c7f89c53b8b5542e127ba2d12d122a6551d107119bd63e4b067` and packed SHA-256 `991347e1e87b757671c55141f5c394dcc01d9a114ae0ef868a6c06e40addc2a3`. The exact operand provenance, clock map and both receipts are in `receipts/`.

The full replay matched 630 ordered private events, their 1,043 entry operand positions, all 74 erasures, all 1,501 public and 68 private endpoints, and 1,101 arbitrary helper identities. Peak private occupancy was 50. Seventy-three erased forms were nonzero. CLEAR44 on 1557 in chart 595 retained −x451 − 3x902/2 − 3x985/2 + x1495. COPY from 770 to 1525 in chart 115 saw a zero destination. The retained observations in the full receipt include the first exterior uses of 329 at combined clock 41158, 134 at 43540, 82 at 43355, and the chart-922 reads of 196 and 185 at 43718 and 43879.

Both coefficient controls rejected with exact output witnesses. Changing −1/16 to +1 at combined clock 11 changed the coefficient of input 991 at output 196 from zero to 17/16. Changing −5/4 to +1 at clock 43610 changed input 2 at output 185 from zero to 9/8. The signed route checks passed all 512 forward and 512 adjoint columns per tested route and rejected the wrong absolute phase.

## Signed application and directed comparison

The source-bound native engine compiled and checked 66 affected frame pairs, both directions of each 512-column physical action, both 1062 contractions, the role-46 composition, and the separate recipient, donor contribution and donor return at the 134/329 contact. All 22 native mutations were rejected. The separate modular physical exercise covered 2,958 ordered chart pairs. The comparable source applications, canonical input payloads and compiler implementations are pinned in the package.

For each concrete native call, reconstruct the rank of every charge from its source and destination frames. Enumerate the 17 native invocations, all static paid caller instructions and the productive diagonals for each caller port. Relative to #7643 the complete paid rank changes are −17 at rank 1, −34 at rank 2 and +17 at rank 5. Relative to #7644 they are −68 at rank 1, +51 at rank 2, −17 each at ranks 3 and 4 and +17 at rank 5. The complete signed bill is 110,298 paid and 22,461 productive positions, with surplus 1,424. All entrance and coframe corrections from both edits are charged directly from the combined instruction stream.

The signed run checked 3,043 catalogue maps, 104 main boundaries, 54 strict inequalities and four functional outer predicates. It gives 782,642,228 ordinary operations, precision coefficient 2,430, 298,366 monomial map slots, 43,938,432 scalar services and 25,439,878,624 elementary tape records. Its public context bound is 14,085 bits. All three framework applications retain the exact signed #7113 caller and the five inherited premises.

The first blind check priced the 17 native invocations by scanning their sites and reconstructed the common caller remainder from two anchored predecessor invoices. Its separate direct tally assigned every idle instruction eight directions per listed stage. Four signed `IDLE_ODD` instructions carry a further central direction. At caller clocks 1339 and 1340, B roles 68 and 69 idle on stage 8 with sign −1. At 2970 and 2971, B roles 70 and 71 do the same on stage 9. Each event has eight B ports, contributing 32 charges at rank 9. Assigning those events rank 8 produces 688 rank-8 charges and zero rank-9 charges. The literal signed census gives 656 and 32, respectively.

Two intermediate verifier versions rejected assumed chart-922 comparison points. The final version sorts the three actual transfer events by their literal clocks, checks each destination-after row against the next destination-before row, and compares the original row after the entire contact. The combined rows after clocks 43608, 43610 and 43611 compare to that original final contact row as false, false and true, respectively. The frozen word was unchanged throughout these verifier repairs. The corrected blind checker (SHA-256 `106bbbcf2828903369af8a95980f001ff91e461a14f3e97fec9abd53bf36004a`) completed at 22:31:24 UTC, covering the concrete signed paid and productive debits, five literal words, private values and returns, changed physical maps, and directed fixed-invoice comparison. During primitive discovery, the verifier saw excerpts from retained predecessor wrappers. Its proof and implementation were derived before reading the combined builder’s argument. [Independent finite receipt](receipts/independent.json)

A second calculation uses the source-pinned #7644 independent checker, SHA-256 `b657117ba89a85b0cf2459236e0f117cff1c4c46b208449b2484c415e3136a3d`. It scans each of the three complete words and the authenticated signed caller. The caller contributes 416 productive fields at each rank 9, 17, 25, 33, 41, 49, 57 and 65, and 208 at ranks 73 and 137. Each of the three complete paid and productive histograms, ordinary bills and four tape counts equals its signed application receipt. On the combined word, the exact envelope gives context height 406 and mass exponent 1,215, hence precision coefficient 2,430. A control moves those 32 odd charges back to rank 8 and detects the resulting histogram difference. [Complete independently derived bills and precision](receipts/INDEPENDENT-BILLS.json)

The full signed framework admits **0.003651825042908**. The conservative public claim is **0.0036518250428**. The signed tariff moment changes sign between the two rational endpoints below. The complete application and an independent interval computation check the directed signs. The lower endpoint exceeds the upper crossing of #7644 and the upper crossing of #7643.

- `36518250429081943810952709292187/10000000000000000000000000000000000`
- `9129562607270485952738177323047/2500000000000000000000000000000000`

At the stronger #7645 peer’s public test point, a separate 256-bit directed comparison rejects this candidate and accepts the peer. Both invoices have the same targets and the same 110,298 paid entries. After cancellation and division by 17, the decreasing unmatched paid ranks are (6,3,1,1) for the peer and (5,2,2,2) here. The rank totals are both eleven and the first three partial sums are (6,9,10) versus (5,7,9). Therefore the peer has strictly lower cost at every power tariff with exponent strictly between zero and one. This ordering explains why adding precision to the price calculation cannot improve the result over that peer. [Complete signed result](receipts/FINAL.json) · [Directed crossing](receipts/DIRECTED-CROSSING.json) · [Peer arithmetic](receipts/PEER-7645.json)


The #7645 registered replay used CPython 3.12 on the clean scientific release at `32abeefff4d5fcc378ab3de1c1a8bf1c37737bdd`. Its terminal output was `PASS_REGISTERED_RESEARCH_PACKAGE research/p104-original74-main46-on7644 outcome=completed`, exit 0. The intermediate head `99f33bd8a8127751bb55d15c009f44be2d68e685` retains the same 41 scientific files and registered runner blob `091b4c8f58bac9a9580d76025b887dc5c873d05f`. Hosted run 44187293472 exited during the preparation control when reading an empty child process ID. The latest head `8ee7e6869b57ce445dbebd1d720366eab1f8ca40` changes five CI prerequisite files, the README and the child-process control. Its mathematical engines, frozen words and signed receipts match the locally cold-replayed release. That replay supplies the comparable incumbent. [Hosted peer job at 99f33bd](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/44187293472/job/134410025509) · [Hosted peer job at 8ee7e68](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/44189450326/job/134417303736)
