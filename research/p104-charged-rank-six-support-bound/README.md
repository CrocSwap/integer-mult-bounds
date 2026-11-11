# Charged rank-six productive split support on the retained P104 word

**NO VERIFIED GAIN. Exact conditional κ change 0%.** On the exact
[#7277](https://github.com/CrocSwap/integer-mult-bounds/pull/7277)
word, all 83 charged rank-six endpoint extensions of type 3+4 and
all 83 of type 2+5 fail the necessary common-chart support test.
Each family includes 50 input extensions, 33 output extensions
and 73 endpoint-and-partition groups. Zero signatures or cut
incidences remain unresolved. The compatible saving upper after
support is zero. The complete comparable witness remains #7277
at κ = 0.003645669928698.

| Productive partition | Typed signatures | Representative cut incidences | Nonzero pure prefix | Nonzero pure suffix in independent replay | Price-only lower margin |
| --- | ---: | ---: | ---: | ---: | ---: |
| 3+4 | 83 | 714 | 0 | 24 | 0.1174506515937458 |
| 2+5 | 83 | 346 | 0 | 0 | 0.08102479309361352 |

## Complete price and scoped support

Each alternative adds one paid rank-one endpoint MOVE and replaces
one productive rank-six job by productive jobs of ranks 3 and 4,
or 2 and 5, in each of the 17 exact #7113 native copies. The replay
reconstructs the complete signed invoice and regenerates the frozen
endpoint price table before evaluating support. The positive
margins in the table are directed lower bounds at the pinned old
crossing upper, rounded for display. Other added ordinary and
physical costs are free in this price-only probe. Prices are
computed per alternative, and the exact rational endpoints are
in [SUMMARY.json](receipts/SUMMARY.json) and the emitted PRICE
receipts.

For a selected partition, fix the proposed endpoints and a strictly
intermediate chart at one of its two rank offsets. The enlarged
cohort is the existing helper cohort at the proposed endpoints
together with all allowed single extenders. Each individual
extension lies inside this enlarged domain. The #5599 split
requires a nonzero rational prefix image and an adjoint suffix
image supported on the same helper coordinates with nonzero
pairing. A zero pure prefix on the enlarged cohort excludes
the requirement for every individual extender.

Representative cuts are reconstructed from the literal contacts
of each chart. Between consecutive contacts, the bank and its
normalized prefix rows remain fixed. Operations on other charts
act trivially on a suffix perturbation supported on the bank.
The initial-bank guard is checked. The new rank-one endpoint
transport lies outside the eligible intermediate chart ranks, so
the fixed-chart, fixed-order representative census still applies.
Scalar operands, MOVE endpoints and owned lifetimes are checked
in the literal trace.

The primary gate checks the necessary pure prefix at all 1,060
representative incidences across the two disjoint typed partitions.
The independent replay separately reconstructs geometry, price and
cut coverage, runs the rational suffix sweep first, and then checks
the pure prefix. The 24 nonzero suffix incidences in 3+4 have no
pure prefix partner. The omitted-paid-MOVE and wrong-pairing
controls reject their mutations. A lawful cocharted basis fixture
and exterior-cancellation fixture provide positive controls.

This result concerns one charged endpoint extension at a time
under the original word's chart and ownership chronology. Changed
chronology, new chart labels, new endpoint mechanisms and smaller
ranks remain open. No physical candidate advanced to signed native,
ownership, precision, tape, caller or outer verification.

## Replay

From a clean checkout with CPython 3.12 and assertions enabled:

~~~sh
python3.12 -B scripts/research_package.py --package research/p104-charged-rank-six-support-bound
python3.12 -B scripts/check_research_commit.py --package research/p104-charged-rank-six-support-bound --check-modes --check-source-history
~~~

From a Git-free export, this command also emits all ten complete
receipts into a fresh output directory:

~~~sh
python3.12 -I -B research/p104-charged-rank-six-support-bound/replay.py --out fresh-receipts
~~~

[PROVENANCE.json](PROVENANCE.json) pins the public inputs by exact
commit, path, Git blob and SHA-256. [LOCAL-PINS.json](LOCAL-PINS.json)
pins the bundled replay sources and earlier campaign dependencies
by package-relative path. The replay authenticates the uncompressed
payloads of the bundled caller, crossing and price snapshots. It
verifies all ten deterministic plaintext receipts against the exact
hashes in [SHA256.json](receipts/SHA256.json) and can emit their full
proof-relevant fields. It uses only the standard library.

## Credit

[#7277](https://github.com/CrocSwap/integer-mult-bounds/pull/7277) at
`ed090b57ed88f8859e5ff4643645099e6ba856ea` supplies the word
and complete comparator. [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
at `07a76c5e2738882c0cb322278e56f6cae3c9885d` supplies the
signed caller. [#7142](https://github.com/CrocSwap/integer-mult-bounds/pull/7142)
supplies the charged endpoint precedent.
[#5599](https://github.com/CrocSwap/integer-mult-bounds/pull/5599)
and [#7130](https://github.com/CrocSwap/integer-mult-bounds/pull/7130)
supply the common-chart split identity and basis constructor lineage.
[#7299](https://github.com/CrocSwap/integer-mult-bounds/pull/7299)
supplies related split pricing. [#7308](https://github.com/CrocSwap/integer-mult-bounds/pull/7308)
supplies the bundled complete signed-invoice audit and directed
price helper. The earlier campaign priced all 777 typed signatures
in Round 37 and replayed the higher-rank eight and seven subsets
in Rounds 37 and 38. Those support certificates have different
rank scopes. [#7303](https://github.com/CrocSwap/integer-mult-bounds/pull/7303)
covers fixed-mass singleton splits under the retained word, whereas
this test charges a rank-one endpoint extension. OpenAI Codex and
subagents materially assisted.

## Open next questions

Can a changed chart chronology or endpoint basis supply a common
chart with pure prefix support at a favorable complete price?
Pin one distinct interface or partition and bound the full
compatible stock before building. A surviving proposal needs
arbitrary-input signed forward and adjoint action, ownership,
restoration and fully charged precision and tape.
