# Lean owner matching, full ownership and controller windows

This package starts a proof effort around the recent whole-owner constructions.
It proves the arithmetic of width shrinking and offset compaction in Lean 4.21.0,
and proves executable complete matching from sorted width domination. It checks
every distinct packing template from PR527 and the currently reviewed PR531,
and certifies every selected PR531 owner row and its finite controller window.
The active full-theorem objective and remaining proof obligations are recorded
in [FULL-PROOF-STATUS.md](FULL-PROOF-STATUS.md). No full multiplication theorem
or new value of kappa is proved yet.

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
The compaction theorem assumes pointwise assignment domination. The separate
`WidthMatching.lean` module now proves that sorted domination supplies a complete
assignment: its executable merge-sort/first-fit allocator succeeds and preserves
every owner identity. Its threshold-count exchange lemma permits ANY fitting
choice for a largest remaining demand. A further theorem handles arbitrary
stateful choice policies satisfying explicit local soundness and availability
contracts. This proves the mathematical greedy-matching argument; connecting
the exact Python implementation and its sorting/ledger representation remains
separate. No allocation runtime bound is asserted.

`PR527Templates.lean` contains 29 distinct `(capacity, widths)` templates extracted
from 40,320 roles in 15,898 owner/child/port groups across 72 calls. Lean proves
all 29 capacity inequalities by ordinary `decide`, then derives their in-bounds,
nonaliasing, gap-free occupied-prefix guarantees from the general theorems.
`PR531Templates.lean` similarly checks all five shapes extracted from 36,288
roles in 15,302 groups and 72 calls in the selected PR531 package.

`OwnerTable.lean` proves soundness of a full-row Boolean checker. Its witness
contains actual rows and auxiliary group/family indexes; the checker verifies
both inverse links. `PR531TableData.lean` contains the literal 36,288-row witness,
including all 16,128 possible groups (15,302 are occupied). The chunk certificates
in `PR531TableCertificate.lean` establish acceptance of every row, group and call.
The resulting theorems give a complete call/helper census, exact source widths,
declared-window membership and capacity, nonaliasing within each owner group,
and injective helper ownership. No correctness of the witness generator is
assumed by these Lean theorems.

`OwnerSeparation.lean` proves that helpers in admissible windows cannot share a
family with either active data bank. `PR531DataWindows.lean` checks all 144
selected windows against the active data pairs. `PR531InvocationOwners.lean`
therefore establishes distinct owners for all 224 data wires and 504 helpers
in each of the 72 selected invocations.

`BorrowSchedule.lean` gives a sound checker for a finite controller trace.
`PR531Controller.lean` certifies the actual projected 242-event controller:
its indexed calls, idle deadlines, untouched window interiors, exact admitted
call sets and separated windows on the same replica/lane. The trace contains
160 child deadlines; 144 windows are selected for borrowing. Unknown event
kinds conservatively block their replica, or every replica if unscoped.
`PR531ScheduledOwners.lean` derives the full one-owner interface from this
controller certificate and places every actual helper inside its traced window.
Its injective finite owner map lands in the declared 7,168-family live stock.
The trace's interpretation as physical machine execution remains unproved.

`OwnerTableControls.lean` checks a valid fixture and rejects nine corruptions.
`BorrowScheduleControls.lean` checks a valid window and rejects six corruptions,
including unknown effects, conflicting touches, bad deadlines and missing calls.

There is no Mathlib dependency, no proof placeholder, no custom axiom and no
native evaluation proof shortcut. The verifier audits every local theorem.

## Exact source and trust boundary

PR527 is frozen at `2080903b9e6bd01e3f64cc4c7c62ea1b3af0aa6a`.
`SOURCE.json` records immutable input SHA-256 hashes. The files in `source/` are
byte-identical excerpts of `research/ranksector112-async/` at that commit:
`data/PLAN.json`, `data/OWNERS.json.gz`, `code/transport_owners.py`, and
`validation/audit/OWNERS-AND-PROFILE.json`. The last is retained context; its
reported PASS is not used to establish this package's conclusions.

`SOURCE531.json` pins the imported PR531 data to main commit
`db0e57bc7f36b5ac0fc844ad7ce1396165ee6647`, recording the original paths.
Its `source531/` files are unmodified owner/plan inputs and verification-scope
context from `research/direct-delivery504-global/`.

`generate.py --check` parses both source packages, checks their source census
and template associations, and compares regenerated template bytes.
`generate_table.py --check` reproduces every PR531 literal row and auxiliary
index. Lean independently checks their semantic relations and index links.
The generator is an untrusted supplier of a witness, not a premise of checker
soundness. Python's JSON parsing and its byte-to-literal projection remain an
external reproducibility boundary; the JSON decoder itself is not formalized.

`SOURCE531-HOSTING.json` pins the complete hosted template in `source531-hosting/`
to the same imported main commit. `generate_separation.py --check` verifies its
224-wire data-bank formula, call order, helper-family identities and routes
against the literal-table source, then reproduces the active-pair definition.
`generate_schedule.py --check` projects the controller events, call positions
and window boundaries. Lean proves the resulting trace and ownership properties.
The association of these definitions with the source JSON is independently
reproduced in Python, not assumed to be a verified parser.

The finite certificate does not reconstruct the old PR523 assignment or prove
the old-to-new Python allocator correct. The one-owner theorem concerns one
complete invocation. It does not alone prove cross-invocation semantics,
physical charts, exact recipes, scalar endpoints, atomic execution, running
time or the full multiplication theorem. The controller certificate proves
window facts in its explicit touch model; connecting that model to actual
physical operations remains an obligation.

## Reproduce

With Lean 4.21.0 installed:

```sh
python3 -B verify.py --lean /absolute/path/to/lean --build-dir /absolute/new/output
```

Use an SSD output directory locally. The directory must be new. The command
checks immutable sources, regenerates all literal witnesses and certificates,
freshly compiles all fifteen project modules, audits every theorem's axioms, rejects a
false Lean capacity claim, checks six mathematical matching regressions, ten owner-table control theorems,
and seven controller-window control theorems, and
rejects six corrupted source fixtures for each of the two input packages. It does
not reuse project objects or download dependencies. Output includes source
hashes, logs, source-binding counts and a receipt.

`lake build` is also supported, but does not perform source binding or the full
audit. The isolated GitHub workflow runs the full verifier.

## Proof roadmap

Freeze source versions at each milestone; the newest numerical PR is not itself
a theorem dependency. This first slice uses PR527 for the initial transport proof and now also includes the reviewed PR531
packing data. The full theorem target is the main-selected PR531/PR493
composition recorded in FULL-PROOF-STATUS.md.

| Next milestone | Required proof boundary |
| --- | --- |
| Source representation | Full literal-table and projected controller certificates are checked in Lean. Python still projects JSON bytes and verifies the source data-bank/helper-route association; the JSON decoder is not formalized. |
| Connect width assignment | The general matching and exchange proofs are complete. Connect old/new owner records and the actual source selector to the verified stateful-policy contract. |
| Connect physical owners | Instantiate incorporated PR509/PR516 semantics with the complete selected word: recipes, labels, row/column restoration, charts, injective owners and atomic invocation execution. Reuse PR528's endpoint adapter where applicable. |
| Compose physical execution | The finite controller windows and full per-call ownership are certified. Establish physical support/commutation, complete pending-piece gathering, boundary states and actual cost accounting for the same event sequence. |
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
The imported PR531 excerpts retain icekylinx's authorship and GPT-6 Astra
assistance disclosure, including the predecessors listed in its scope record.

The new arithmetic and matching proofs and verifier were prepared by Rohan Arun with substantial
OpenAI Codex assistance, under Apache-2.0. This is a machine-checked first milestone,
not an independent human audit or a claim of mathematical priority for prefix sums.
