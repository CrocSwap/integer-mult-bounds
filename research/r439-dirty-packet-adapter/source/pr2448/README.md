# R439 interleaved-window packet routing

**Conditional interface result and finite routing construction; no new kappa.**
PR2407's live COPY window contains 303 target-to-target XORs and ten reads
of an immutable snapshot. It contains no logical MOVE, yet the explicit
packet implementation below requires **929 route actions**: three per target
XOR and two per snapshot tap. Those routes may themselves require recursive
children. The snapshot and parked ancestors must remain protected during
every such child.

This takes one bounded part of PR2437's physical-routing handoff. It supplies
an independently written conditional packet implication, a carry-aware finite
route compiler, exact symbolic execution of the literal window, and a
record-action ledger. It does not supply a uniform GL64 compiler, the complete
supplier invoice, or a stronger exponent. PR2195 already supplies the generic
three-route procedure; this is its source-bound application and finite test.

## Result and exact coverage

[REVIEW.md](REVIEW.md) proves the conditional implication for complete
local-ring packets with exact bijective routes, separated owners, a common
data gauge, complete spectators, fresh blank packet buffers and completed
child/parking contracts. All payloads may be arbitrary and correlated. The
rank-seven snapshot creation/ERASE transports remain external hypotheses.
This is a written proof, not a formal-kernel proof.

[verify.py](verify.py) authenticates and explicitly reuses the credited PR2407
constructor to rebuild its entire RAW6 stream. It binds the 313-event window
at records 9070 through 9384 (exclusive of its boundary operations), then
compares its abstract endpoint with the predecessor's separate 16-tap split
followed by all 303 undo gates. It does not repeat the complete native replay.

The new finite implementation uses `GL2(Z/9)`:

- All 3,888 matrix headers, 48 low classes and 81 high lifts per class.
- 111 distinct target families with fixed nonidentity unit charts; one common
  low invocation `d0=I` and an already aligned private snapshot. These are
  reduced-model charts, not the selected 64-dimensional owner charts.
- All 431,568 target records, including all 422,577 unowned records; each
  initial record is a distinct formal XOR atom representing an arbitrary
  complete payload vector. Equality therefore holds for all bit assignments
  and correlations on this finite domain. Record interiors are carried
  opaquely; this does not test a bit implementation's spectator ordering.
- Literal carry-aware high-fibre permutations compiled to adjacent record
  swaps, with forward and inverse route execution. The address oracle uses
  direct full-ring matrix multiplication, not the digit/carry compiler.
- 248,832 full-ring route comparisons across all low classes and the 64
  distinct fixture charts. The inverse *fragment* is also checked on arbitrary
  fresh inputs; this is not a check of reflected rank-seven COPY transport.
- Explicit clearing of every fresh packet buffer after each event and an
  unchanged snapshot at exit. An aligned comparison clear is a local guard
  check, not implementation of the external transported-source ERASE.

Five semantic controls reject omitted carries, a missing target-return route,
snapshot borrowing that is restored before exit, an unowned-packet write,
and a count-preserving tap moved to the wrong cut. Reordering the seven
same-cut initial taps is accepted. The route return check also accepts the
literal forward/inverse permutation on every tested low packet.

## Accounting and limits

The prescribed macro schedule has 313 packet XORs, 616 fresh packet copies
and disposals, and 929 routes. Its peak *outer interface* buffer reservation
is two fresh packets plus one live snapshot. Route-private scratch, merge
buffers, control tables, descriptors and parked ancestors are additional.
The finite swap interpreter uses one auxiliary record at the abstract swap
level; this is not a measured Python-memory or bit-tape bound.

[RESULT.json](RESULT.json) records executed swaps and symbolic operations,
plus declared record-level tariffs. A selector/replacement is a full family
scan, charged for a pass to the end sentinel and rewind. Each adjacent swap
charges two reads, two writes and the declared record path
`p -> p+1 -> p -> p+1`, plus positioning and return. XOR, snapshot read-head
returns, fresh buffer clearing and rewinds are separately counted. These are
explicit **record-action conventions**, not measured bit-head movement or
controller time. Route-table construction and symbolic-set bookkeeping are
outside this ledger; a complete bit-time invoice must add its actual costs.

The split comparator has 941 route actions. The difference of twelve is a
macro-action count, not necessarily a weighted work saving: the tap targets
and their route tariffs differ. No optimum, runtime speedup or positive
recurrence margin follows from these counts.

The finite route table has 81 entries and is compiled for a fixed small
ring. Its construction may grow badly with the high fibre. It cannot be
substituted for a uniform-in-width compiler or used to dispatch one recursive
child per high matrix. All selected GL64 route implementations, COPY/ERASE
costs, actual shared-family owners, full caller parking/scratch, precision,
hosting and outer transfer obligations remain separate. The use of fresh
blank copies and charged disposal follows the logical stream model; it does
not implement arbitrary dirty reversible ancillas.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/r439-interleaved-packet-routing
python3.12 -I -O -B research/r439-interleaved-packet-routing/verify.py
```

Expected marker: `PASS_R439_PACKET_ROUTING ... no_new_kappa finite_GL2_only`.
The registered command compares the deterministic receipt and runs all five
semantic faults under optimized Python. `--write` explicitly regenerates the
receipt. Local execution, hosted CI and full selected cold replay are distinct.

The exact source/input pins are in [SOURCES.json](SOURCES.json) and
[PREDECESSORS.json](PREDECESSORS.json). Source bytes are authenticated before
import. The constructor is inherited code, while the row-route implementation,
full-ring formula oracle and proof review are separate new work. The reviewer
inspected the implementation but is not an independent human or proof kernel.

## Open next questions

1. Implement one actual selected GL64 chart route with complete child,
   spectator and protected-snapshot contracts. Start from the PR2234 callee
   interface, expose every recursive call and prove its parking locality.
   The fixed-ring finite table is not that implementation.
2. Supply the full changed-supplier bit-time and precision invoice. Include
   COPY/ERASE transports, selector and merge work, descriptors, control
   preparation, exact child volumes, scratch, head returns and inherited
   fallback/hosting obligations. The 929-action fragment is only one term.

[TASK.json](TASK.json) records the relevance, first steps and blockers.

## Provenance and credit

Canonical base `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision4;
selected record SHA256
`10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
Canonical investigation:
[Discussion2401](https://github.com/CrocSwap/integer-mult-bounds/discussions/2401#discussioncomment-18946844).
PR2440's different multi-column word is outside this fixed-source result.

Credit Ross Richardson's PR2407 construction
`4944211cee666eb8631b990cb0f33cfa68666485` and PR2437 ideal binding
`4ac2b3826140b782020145a547f9b6692ebd3d32`; Jose Manuel's PR2195 packet,
carry, selection and route contract
`3a1cf78a1ba6322129e42d80c50d21765524d612`; alephnan's PR1627 and
cheesegrader's PR540 common-frame/whole-call arguments; starship-s's PR2421
native replay; and the retained PR589/555/425 supplier/exporter lineage.
PR2407's sources retain Sagar Thakrar PR1062/2115, Charles Bethin PR2279,
Sricharan Vagvala PR2356 and Gareth Davidson PR915/2373 credit.

Prepared by Ross Richardson with substantial OpenAI Codex assistance,
including a separate recursive-interface mathematical reviewer. New work and
retained sources are Apache-2.0; repository LICENSE applies. No independent
human review, complete multiplication theorem or selected-frontier change.
