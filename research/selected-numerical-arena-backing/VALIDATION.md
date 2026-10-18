# Validation and interpretation

The written allocator proof is all-parameter under its canonical legal-history
contract. Its finite corroboration and conditional caller consequence have
different domains. No formal-kernel or independent human proof is claimed.

## Exact checks

- CPython 3.12.12, registered replay:
  `/opt/homebrew/bin/python3.12 -I -Werror -B scripts/research_package.py --package research/selected-numerical-arena-backing`.
  All three commands and package provenance checks passed.
- The primary source checker covers all 1,078 reachable canonical zero/free
  states and 2,106 outgoing legal transitions in the stated capacities/widths,
  plus ten inventory-guard checks, literal/copy/rollback, warm history,
  two-phase retention, and 23 constructed-array/write cuts. Its separate
  full-sized synthetic rectangle schedule retains 151,015 cells, including
  nonzero borrowed parents. It is not a selected caller execution.
- Nine optimized behavioral/integrity controls pass: omitted erasure, lost
  reusable slots, omitted template/LEFT, one-slot-underbudget and exact-capacity
  reuse, source SHA256/Git blob corruption, effective malicious unchecked-hash
  bytecode, and actual verifier rejection of Boolean/integer receipt substitution.
- The independent implementation imports only its hard-pinned runtime bytes.
  It covers 10,164 histories, 52,862 operations, 317,005 intermediate samples
  and 5,930 pending-array observations, with all warm entry states/orders in
  its finite domain. It separately tests suspended live heads and the
  history/phase/inventory counterexamples. Normal and optimized runs pass.
- All three commands passed on CPython 3.14.6 under `-I -O -Werror -B`, from
  `/private/tmp`, with empty PATH, against a Git-free export whose files and
  directories were mode 0444/0555. All 15 original exported file hashes were
  unchanged. This validation note and subsequent freshness metadata were added
  afterward; no replayed proof, runtime, verifier or fixed receipt changed.
- `make selected-record-check` passed. The selected cold construction replay
  was not run; no selected input or predecessor implementation was changed.
- Exported runtime bytes were directly compared with original PR2697
  `a53fdf4bcbe33c6732f0bec1badc8c023380f9d1` and the PR2825 export. Source
  authentication runs on every primary and independent replay.

## Separate review and corrections

A separate math-storage-lifetimes AI worker owned only `INDEPENDENT.md` and
`independent.py`, deriving its model before reviewing the primary proof.
It identified and corrected two prose defects: reuse may increase the interval
live high water below the entry backing count; and the capacity equivalence
requires positive integer capacity. It also prompted explicit pending-array,
suspended-head and reference-trace premises. Its final review found no further
substantive error. The worker completed before preservation.

## Limits and upstream freshness

Scientific pins remain the exact original allocator and PR2825 conditional
proof. The inherited 37,672/41 caller bounds were not re-derived here. No actual
selected catalogue membership, full GL64 payload/coefficient execution, general
failure rollback, unconditional caller inventory admission, total physical
reserve, supplier admission or stronger exponent follows.

Entry canonical main was `da4f4fec60a88d9187f8ffa02f0f787b8b2da527` at
2026-10-16 00:24:52 UTC. Submission refresh found
`b1f581c373c1b2c579100f2ba2109ce9936b0676` at 00:37:35 UTC. Priority revision 5,
guidance/selected-record hashes, generic runner and workflow bytes were unchanged;
the new package had no path collision. Frozen scientific pins were retained.
Current PR2825/2697 heads were independently re-read before publication.
Freshness/overlap details are in `TASK.json`. Complete metadata pagination is
not coverage of arbitrary diffs, unpublished research or closed work missing
local notes/ledger. Hosted CI is distinct from these local checks.

Submission metadata overlap completed at 2026-10-16T00:41:18.230407+00:00: 679 open PRs including drafts, 1475 Discussion/comment/reply records, and 2139 local records; complete pagination, no warnings. The relevant matches were the credited predecessor scopes and this claim. No absence-of-novelty claim follows.
