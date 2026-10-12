# Lean owner transport: first formalization milestone

This package starts a proof effort around the recent whole-owner constructions.
It proves the arithmetic of width shrinking and offset compaction in Lean 4.21.0,
and checks every distinct packing template extracted from PR527's published
owner table. It proves no multiplication theorem or new value of kappa.

## Completed

`OwnerTransport.lean` proves, for arbitrary natural-number widths and capacities:

- Pointwise shrinking cannot increase a prefix sum.
- Earlier compacted blocks end before later ones begin.
- Every block fits inside the total occupied width.
- Shrinking assigned blocks preserves an owner's capacity.
- Each occupied coordinate is in bounds and distinct block/coordinate pairs do
  not alias.
- Every address below the occupied total belongs to a block: there are no holes.
- `compaction_correct` assembles capacity, injectivity and occupied-prefix coverage.

Empty collections and zero widths are allowed in the general theorem. Coverage
is of the occupied prefix, not the unused capacity of a partly filled owner.
The pointwise assignment inequality is a hypothesis: this does not prove the
Python greedy matching algorithm succeeds from sorted width dominance.

`PR527Templates.lean` contains 29 distinct `(capacity, widths)` templates extracted
from 40,320 roles in 15,898 owner/child/port groups across 72 calls. Lean proves
all 29 capacity inequalities by ordinary `decide`, then derives their in-bounds,
nonaliasing, gap-free occupied-prefix guarantees from the general theorems.
There is no Mathlib dependency, no proof placeholder, no custom axiom and no
native evaluation proof shortcut. The verifier audits every local theorem.

## Exact source and trust boundary

PR527 is frozen at `2080903b9e6bd01e3f64cc4c7c62ea1b3af0aa6a`.
`SOURCE.json` records immutable input SHA-256 hashes. The files in `source/` are
byte-identical excerpts of `research/ranksector112-async/` at that commit:
`data/PLAN.json`, `data/OWNERS.json.gz`, `code/transport_owners.py`, and
`validation/audit/OWNERS-AND-PROFILE.json`. The last is retained context; its
reported PASS is not used to establish this package's conclusions.

`generate.py --check` independently parses those inputs and checks the full helper
census at each call, family uniqueness within each call, helper widths, declared
window membership, the `(stage, replica)` call order, exact prefix offsets and
per-group capacity. It then compares all generated Lean bytes to the committed
file. The Python parser, extraction and association of source roles with the
29 templates remain **outside Lean's trusted proof**. SHA-256 pins identify the
bytes; they do not prove the templates faithfully describe a physical machine.

The finite instance proves capacity directly for the final packing; it does not
reconstruct the old PR523 assignment or discharge the width-shrinking premise
between the original and new assignments. Distinct owner-group keys are not a
proof of disjoint physical streams. Declared windows are not a proof that the
machine's schedule realizes those windows.

## Reproduce

With Lean 4.21.0 installed:

```sh
python3 -B verify.py --lean /absolute/path/to/lean --build-dir /absolute/new/output
```

Use an SSD output directory locally. The directory must be new. The command
checks immutable sources, regenerates the exact template table for comparison,
freshly compiles both project modules, audits every theorem's axioms, rejects a
false Lean capacity claim, and rejects six corrupted source fixtures. It does
not reuse project objects or download dependencies. Output includes source
hashes, logs, source-binding counts and a receipt.

`lake build` is also supported, but does not perform source binding or the full
audit. The isolated GitHub workflow runs the full verifier.

## Proof roadmap

Freeze source versions at each milestone; the newest numerical PR is not itself
a theorem dependency. This first slice uses PR527 because its exact owner
transport is accessible and relevant to our contribution, not because it is
claimed to be the latest or strongest candidate.

| Next milestone | Required proof boundary |
| --- | --- |
| Internalize the source certificate | Replace the external JSON-to-template association with a verified certificate decoder/checker; derive family and window facts from the actual emitted schedule. |
| Prove width assignment | Derive a complete assignment from sorted dominance and prove the chosen matching implementation preserves a matching for remaining helpers. Connect old and new owner records. |
| Connect physical owners | Instantiate incorporated PR509/PR516 semantics with the complete selected word: recipes, labels, row/column restoration, charts, injective owners and atomic invocation execution. Reuse PR528's endpoint adapter where applicable. |
| Compose the whole schedule | Prove all invocation/replica windows, cross-invocation disjointness, pending-piece order, boundary states and actual physical cost accounting. |
| Build the uniform machine | Connect arbitrary finite input preparation/counting (PR488/511/519/526/530), layout, routing and scalar operations to a fixed-tape machine for every input size. |
| Establish numerical correctness | Formalize precision, error accumulation, recovery, prime supply and the recurrence hypotheses needed by the analytic transfer. |
| Finish the bound | Derive the chosen conditional certificate's exponent from the verified machine and discharged analytic hypotheses. Only then state a full integer-multiplication theorem. |

## Existing work and attribution

The base for this contribution is main
`db0e57bc7f36b5ac0fc844ad7ce1396165ee6647`. Its review ledger records PR509 and
PR516 as incorporated. They supply event/label semantics and abstract realization;
this package does not replace or reprove those results. PR528 connects the complete
bank endpoint. PR530 composes preparation/counting. PR540 checks a concrete PR442
invocation on Lean 4.33.0, a separate toolchain and source scope. Their reported
validation is not counted as a fresh replay here.

Sources reviewed for scope: [PR527](https://github.com/CrocSwap/integer-mult-bounds/pull/527),
[PR516](https://github.com/CrocSwap/integer-mult-bounds/pull/516),
[PR528](https://github.com/CrocSwap/integer-mult-bounds/pull/528),
[PR530](https://github.com/CrocSwap/integer-mult-bounds/pull/530), and
[PR540](https://github.com/CrocSwap/integer-mult-bounds/pull/540).
No claim of a comprehensive duplicate search or independent replay of those PRs.

PR527 credits Dugongue's PR522 rank-sector/whole-owner construction and icekylinx's
PR523 port restriction; retain those credits and all preceding source notices.
The new arithmetic proofs and verifier were prepared by Rohan Arun with substantial
OpenAI Codex assistance, under Apache-2.0. This is a machine-checked first milestone,
not an independent human audit or a claim of mathematical priority for prefix sums.
