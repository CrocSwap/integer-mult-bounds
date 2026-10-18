# R420 target forests: 4,784 fewer XORs with a certified forest cost floor

**Finite bit-circuit construction and scoped optimum; no new κ.** This changes
only the frame-zero dirt compensation D of eumemic's PR543 R420 supplier.
Twelve rooted target trees reduce the complete native word from **26,916 to
22,132 binary XOR additions**, including all preparation and restoration.
The D section falls from **19,922 to 15,138** additions. Every arbitrary target
input is restored before leaving D, apart from the required dirt correction;
helpers are never modified in D.

The exact minimum D cost over the explicitly defined *rooted target forest*
class is **14,921**. A spanning-tree cycle certificate proves this floor, and
an independent Prim implementation reproduces it. The nominated minimum-cost
tree needs 106 payload bits, exceeding the inherited 104-bit allowance. Eight
cuts produce the submitted 15,138-addition forest, whose recomputed payload
fits below 2^104. **We do not claim that every minimum-cost tree exceeds the
allowance, or that the submitted forest is optimal subject to that allowance.**

| Quantity | Pinned PR543 | Submitted forest |
|---|---:|---:|
| D binary XORs, including preparation/restoration | 19,922 | 15,138 |
| Complete native ADDs | 26,916 | 22,132 |
| Exported records | 29,874 | 25,090 |
| Helpers / retained COPYs | 420 / 9 | 420 / 9 |
| Paid rank mass | 5,112 | 5,112 |
| Forward positive prefix bound | 144,651 | 144,651 |
| Reverse positive prefix bound | 2,270,064 | 9,640,706 |
| Payload allowance needed | 100 bits | 104 bits |

All per-register frame paths and the complete MOVE/COPY/ERASE subsequence are
unchanged. The local recursive histogram remains
`{1:1320, 2:1440, 4:60, 5:120, 8:9}`. This is a scalar circuit improvement,
not a changed recursive exponent or a practical multiplication benchmark.

## Reproduce

Python 3.10+ and the standard library, from the repository root:

```sh
python3 -I -B research/r420-target-forest/verify.py
python3 -I -B research/r420-target-forest/independent.py
```

Expected final lines:

```text
PASS_R420_TARGET_FOREST D=19922->15138 ADDs=26916->22132 saved=4784 forest_floor=14921 payload_bits=104 columns=660 controls=8 no_new_kappa
PASS_INDEPENDENT_FOREST minimum=14921 feasible=15138 preparation=108 restoration=108 dirty_columns=660
```

The first command verifies the source pins, all 672 E8 frames, full forward and
reverse arbitrary-input endpoints, all 7,260 spanning-tree cycle inequalities,
complete certificate equality, native exporter agreement, positive prefix
bounds and eight negative controls. It invokes the original unmodified PR543
checker for labels, frames and interface predicates. A separate set-valued
interpreter replays both directions of the actual exported record streams.
`independent.py` imports no package code: it uses Prim and set-valued target
algebra instead of Kruskal, cycle inequalities and integer-bitset algebra.
These are independently implemented algorithms by the same AI-assisted author,
not an independent human review.

For the unchanged C++17/Boost legality and 5/9/11-stage checks:

```sh
BOOST_INCLUDE=/path/containing/boost python3 -I -B research/r420-target-forest/verify.py --native
```

Omit `BOOST_INCLUDE` if the headers are in `/usr/include`. The optional run
checks both source and changed words on 900/1,380/1,620 columns, rejects all
96 omitted-bridge controls, rejects the nominated cheapest tree for its
106-bit payload and rejects missing restoration at every stage count.
It writes only to a temporary directory. The native receipt is printed.

The bounded nomination is reproducible separately:

```sh
python3 -I -B research/r420-target-forest/discover.py
```

This checks all 7,260 graph edges in each of 256 seed-ordered Kruskal runs
(seeds 5 through 260), chooses attempt 1 by the smallest reverse positive
bound, then considers 900 single-edge root cuts over eight greedy rounds.
Cuts are selected by exact rational prefix reduction per added XOR and stop
as soon as the 104-bit cap holds. The committed cuts are
`68,50,0,39,78,97,57,3`. No exhaustive coverage of spanning trees, admissible
linear bases, or precision-constrained forests is claimed. The *cost floor*
is proved by the certificate, not by failure to find a cheaper candidate.
`--write-certificate` deliberately regenerates the receipt; normal verification
never updates committed files.

## Mechanism and interface

For parent map p, descendants first execute `y_t ^= y_p(t)`. Roots are unchanged.
Each target then reads helper row `K_t XOR K_p(t)` (roots read `K_t`). The target
operations are reversed to restore the original basis. There are 108 preparation
and 108 restoration XORs and 14,922 helper reads, totaling 15,138. The written
argument and graph certificate are in [PROOF.md](PROOF.md).

The original syntactic H2 requires D to read only helpers. Its literal K
extractor also assumes that syntax. **Both reject the changed representation**,
as the verifier explicitly checks; no predecessor checker is patched. The
replacement H2′ requires frame-zero D to have the complete semantic endpoint
`(x,s,y) -> (x,s,y+Ks)`. All other original H1–H5 hypotheses and decomposition
checks pass. Target-to-target operations in D use existing frame-zero rows,
with no new helper, COPY, source-access or recursive-child cost.

Full hosted-parent reconstruction, whole-owner and residual-host integration,
updated global finite invoices, adoption of the semantic H2′ interface, and a
changed-word outer assembly remain integration obligations. The increased local
positive prefix must not be substituted into an old global invoice without
replay. The selected construction remains #626/#543 at conditional
`κ = 51110230636731/31250000000000000`.

All-size compilation, common-label/mutable-basis realization, hosting, precision,
tape and analytic transfer remain inherited assumptions. F2 endpoint equality
and positive integer envelopes do not assert equality of the signed integer
endpoint, a full multiplication theorem, or a Lean proof. The unchanged selected
cold replay and repository-wide regeneration suite were not rerun for this
standalone package. Local Linux checks and remote CI are distinct; see
[VALIDATION.json](VALIDATION.json).

## Provenance, overlap and credit

Exact base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
PR543 source: `2065fe4f72a914d907f1046603f5a36f17018535`.
[SOURCES.json](SOURCES.json) pins every consumed repository implementation.
The compressed word is compared using its complete canonical JSON payload, so
recompression does not change mathematical identity. No pending PR code is
imported. [CLAIM.json](CLAIM.json) records the OS-random seed **5**, candidate
selection, local claim and final overlap refresh; no pinned coordination issue
existed when the scope was selected.

Scott Woolsey Biggart's [PR713](https://github.com/CrocSwap/integer-mult-bounds/pull/713)
and Sagar Thakrar's [PR716](https://github.com/CrocSwap/integer-mult-bounds/pull/716)
are direct predecessors for restored target-row factoring. PR716 proves the
3,250-saving disjoint-pair optimum. This contribution extends the circuit class
to arbitrary rooted forests, proves its scalar cost floor and supplies a
104-bit-feasible forest saving an additional 1,534 XORs. **No priority for
pair factoring is claimed.**

Concurrent [PR742](https://github.com/CrocSwap/integer-mult-bounds/pull/742),
prepared for @ellipsi2, appeared during the final refresh and independently
extends pairs to shared-donor stars, saving 3,288 XORs. It receives explicit
credit for the shared-donor extension. The present construction permits
multiple tree levels, adds an exact floor for the whole rooted-forest class,
and saves another 1,496 XORs while satisfying the 104-bit bound. No priority
for shared donors is claimed, and no PR742 code is used.

Greer Guthrie's [PR694](https://github.com/CrocSwap/integer-mult-bounds/pull/694)
and PR686 factor helper columns. PR694 has a larger reported scalar reduction;
this target-only class never modifies helpers during D and is not presented as
the best arbitrary D circuit. PR708 modifies separate decoder totals; PR710
modifies cleanup. Concurrent PR733 composes helper and target bases and reports 8,368 saved XORs;
that broader class is credited and is not superseded. PR731 independently
checks the original compensation matrix rank and kernel. Neither is imported.
None is composed here. Dugongue's PR476 and earlier PR450
supply target-mixing precedents.

Credit remains with eumemic for PR543/493 and the interleaved scalar interface;
Dylan Crow for the E8 word/record format and exporter; DreamingOfClouds for the
retained-totals/nine-stage lineage; Zhihao Chen for the scalar-interface
framework; DaysSky for bridged stages/hosting; and the complete cumulative
construction and realization lineage in the [original notice](../e8-bit-r420/NOTICE.md)
and [maintainer review](../../docs/research/community-k492-review.md).

Contributed by **Oscar Fennell (@ofennell-quipex)** with substantial
**OpenAI Codex assistance** in the mathematical analysis, bounded search,
implementation, verification and writing. New material is Apache-2.0, under the
repository license. Existing source files and notices are unchanged.
