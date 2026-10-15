# Heterogeneous paired-output events at a dirty connector

**Result.** At one connector boundary, an explicit event
`AP(i,k,z): y_i += A_i z; y_k += A_k z` can packetize two distinct output
readouts with arbitrary independent maps. The exact five-source, 31-output
schedule in the pinned universal-connector certificate has 64 output-map
readouts. Pairing targets that share a boundary gives 29 pair events and six
single events. Including the ten unchanged source events, the root event stream
shrinks from 74 events to 45. It still performs all 74 complete map-child
executions and all 64 target writes.

The maps are arbitrary binary-linear maps, including singular maps, with no
relation assumed between different `A_i`. The pair handler sequentially runs
both complete child calls at the current boundary; each leaves the connector
unchanged, and the target rows are distinct. The operation shares the
connector value and event packet only. It does not share either `A` evaluation.
A fixed descriptor encoding saves 58 bits. The complete-cost improvement is
conditional on the pair event's dispatch, decode, routing and transition bill.
No selected supplier or new `kappa` is claimed.

## Pins and reproduction

- Base commit: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`.
- Selected record: `836330098538459/500000000000000000`, SHA-256
  `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`. Its
  review is `docs/research/community-batch1099-review.md`, source manifest is
  `research/community-frontier1094-audit/SELECTED-SOURCE.json`, certificate is
  `research/community-frontier1094-audit/ASSEMBLY.json`, and canonical reproduction
  is `make frontier1094-verify` (not run for this connector-only contribution).
- Live schedule input: `research/universal-connector-boundary/CERTIFICATE.json`,
  SHA-256 `e733746ba3e5151c829b4e8728bfff5ae3ed24d8d203eb77c735d20758e8266a`.

Run from the repository root:

```sh
python3 -I -B research/heterogeneous-output-pair-seed7557/verify.py
python3 scripts/research_package.py --package research/heterogeneous-output-pair-seed7557 --check-only
python3 scripts/research_package.py --package research/heterogeneous-output-pair-seed7557
```

The first command should print:

```text
PASS_HETEROGENEOUS_OUTPUT_PAIR n2_scalar_cases=2048 n2_events=9 five_source_pairs=29 singles=6 root_events=45 child_calls=74 descriptor_bits=498->440
```

The source-pinned control separately passes as
`PASS_UNIVERSAL_CONNECTOR_BOUNDARY pairings=945 max_coverage=31 queries=74 leaves=182`.
The package verifier checks the control certificate hash and recomputes the
paired schedule from its contents.

## Exact dirty-state identity

Work over `F2` with arbitrary dirty source rows `x_j`, connector `z_0`, and
output rows `y_m`. The source events update

```text
z <- z + B_j x_j.
```

Let `q_t` be the five-bit parity vector of source toggles before boundary `t`.
Then `z_t = z_0 + sum_j (q_t)_j B_j x_j`. The fixed certificate assigns each
output mask `m` an even set `T_m` of readout boundaries (two boundaries for 30
masks and four for mask 21), with `xor_{t in T_m} q_t = m`. Therefore

```text
y_m(final)
 = y_m(initial) + sum_{t in T_m} A_m z_t
 = y_m(initial) + A_m sum_{j:m_j=1} B_j x_j.
```

The dirty connector term cancels because `|T_m|` is even. Every source label
appears twice, so the final connector is `z_0`. An `AP(i,k,z)` event is just
the two independent additions at the same `z_t`, grouped in one event packet;
expanding it restores the original readout order. The verifier checks that
expansion exactly matches all 64 readouts, and rejects any packet with a missing
row, a row at the wrong boundary, or an aliased pair of targets. These are exact
algebraic identities for arbitrary linear maps; the 2,048 scalar cases exercise
the smallest instance across every map, input and dirty-state choice.

For the minimal fixture, `B0 B1 B0 B1` has prefixes `0,1,3,2,0`. Masks 1, 2,
and 3 read at boundary pairs `(0,1)`, `(0,3)`, and `(0,2)`. Pairing masks 1
and 2 at boundary zero yields nine root events including the four source
updates; it still executes six A children and six writes. The verifier exhausts
every scalar `A/B` map, source value, dirty connector and dirty target for this
fixture.

## Fully charged event budget

Keep the complete child bill fixed:

```text
C_child = P + 2 * sum_j c(B_j) + sum_m r_m * c(A_m),
```

where `r_m` is the source schedule's readout count (two, except four for mask
21). Each `c(A_m)` includes its map computation, target read/write, private
scratch restoration, head return and required frames. All 64 output-map
executions remain in `C_child`; the ten source calls and one-time preparation
also remain unchanged.

The event stream uses implicit boundary order and a fixed 2-bit event tag:
`00` for a source event, `01` for a singleton output, and `10` for a paired
output. Source IDs use 3 bits and output IDs use 5 bits. A source event costs
5 bits, a single output event 7 bits, and a pair event 12 bits. Thus

```text
unpaired descriptors = 10*(2+3) + 64*(2+5) = 498 bits
paired descriptors   = 10*(2+3) +  6*(2+5) + 29*(2+5+5) = 440 bits.
```

Let `s` be the fully charged cost per stored/read descriptor bit. Let `d_B`
and `d_A` be the ordinary top-level source and output dispatch costs, excluding
their descriptors and complete children. Let `d_pair` include the pair handler,
decoding both IDs, routing both targets and every extra interface transition,
while excluding the 12 descriptor bits and the two complete A children. The
full invoices are

```text
C_unpaired = C_child + 10*(d_B + 5*s) + 64*(d_A + 7*s)
C_pair     = C_child + 10*(d_B + 5*s) +  6*(d_A + 7*s) + 29*(d_pair + 12*s).
```

Source events cancel, so

```text
C_pair - C_unpaired = 29 * (d_pair - 2*d_A - 2*s).
```

The pair is favorable exactly when `d_pair < 2*d_A + 2*s`. This fully charges
both output maps and target writes. At `d_pair = 2*d_A`, the descriptor saving
alone lowers the bill by `58*s`; a pair-specific surcharge above that must be
less than `2*s` per pair to preserve a gain. This is a parameterized interface
result, not a measured machine tariff. It does not reduce the paid recursive
moment unless an actual caller's `d_pair`, `d_A`, and `s` satisfy the inequality.

## Overlap and attribution

The nearest live connector claim is [Discussion #2221](https://github.com/CrocSwap/integer-mult-bounds/discussions/2221), which studies a seven-source mask family under the original single-output alphabet. [PR #2182](https://github.com/CrocSwap/integer-mult-bounds/pull/2182) concerns fixed-port and two-root/frame boundaries. [PR #2201](https://github.com/CrocSwap/integer-mult-bounds/pull/2201) adds a source-side arity-four call; [PR #2128](https://github.com/CrocSwap/integer-mult-bounds/pull/2128) adds source-side DUO calls. The local [common-A broadcast package](../common-a-broadcast-readout-seed4a52/README.md) shares one A evaluation across rows, which is unavailable for arbitrary independent `A_i`. The local [two-projection connector package](../two-projection-connector-seed51a5/README.md) changes a helper frame and does not add this output operation. This finite construction is distinct in its operation and hypothesis; the overlap scan is not a novelty guarantee.

The source contract and five-source schedule descend from the universal dirty-connector boundary work, which extends [PR934's three-by-three result](../universal-connector-boundary/references/PR934-README.md). This package changes the output event wrapper only and copies no predecessor implementation.

## Open next questions

- **Can a caller pay for the pair dispatcher below the break-even threshold?** This matters because the exact descriptor reduction reaches a recursive cost only with a real interface. First locate two independent output maps reading the same live connector at one selected-supplier boundary and invoice the pair handler and routing. Blocker: no selected supplier currently declares this dispatcher or its tariff.

Prepared by Cinna Davis with substantial OpenAI Codex assistance in mathematical scoping, construction, exact replay, cost accounting and writing. No independent human review, supplier admission, physical benchmark, selected-frontier change or `kappa` improvement is claimed.
