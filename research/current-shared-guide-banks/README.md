# One shared guide for the current native bank tuple

A seven-tape finite program uses one produced guide for every bank reset.
It binds the 468 reset events of the pinned PR #7663 word to a retained
234-parent/234-child tuple. Every selection crosses physical cells and
returns its heads. Address counters and the guide are fully retired.

At N=512 and W=1, the complete retained capacity is 1202130 cells. The
preceding two complete guide/data arrays require 2398032 cells. The new
bill includes 552 control cells. Selection takes more travel. Its exact
468-service bill is `2300688L + 10458512`, plus guide production and
retirement. No new kappa or speed gain is claimed.

Read [PROOF.md](PROOF.md) for the quantified boundary and complete cost
formulas. [RESULT.json](RESULT.json) records exact executions and six
instruction-fault controls. [TABLES.json.gz](TABLES.json.gz) contains the
94675-row fixed table and every source-clock block. [assembly.py](assembly.py)
emits this table; [verify.py](verify.py) checks its complete bytes and runs
both sparse and independent dense interpreters.

The full 468-event schedule passes at N=W=1: 21962186 instructions and
3780 retained cells. The last child bank passes at N=512, W=1:
33640158 instructions and 1202130 retained cells. Six other shapes check
counter and record boundaries. The proof covers all admitted positive
N and W. The verifier does not execute the full schedule at N=512.

## Scope and cost decision

This answers the guide-sharing question in
[PR #7667](https://github.com/CrocSwap/integer-mult-bounds/pull/7667).
The comparison is
[PR #7666](https://github.com/CrocSwap/integer-mult-bounds/pull/7666).
Both use the source plan from
[PR #7663](https://github.com/CrocSwap/integer-mult-bounds/pull/7663).
The copied sources have written scoped proofs and local execution checks.
They have no independent human admission here.

The construction has one benefit: a complete storage reduction after the
new control spans are included. Its time is larger than the local
per-bank-guide selector. Every ruler pass, counter conversion, return,
erasure, guide-production phase and guide retirement has a positive
charge. The fixed control table has a separate finite loading charge.
Root inputs, data allocation and numerical child work remain unpriced
obligations. This result does not discharge a selected assumption.

The entry contract requires canonical binary N,W, blank conversion work,
exact owned windows, same-format disjoint banks and canonical heads. A
numerical child must preserve the shared guide and parked banks and return
the specified heads and work tapes. This package does not implement that
child. The inventory is one RAW native plan, not the complete compiled
recursive tree. Native adapters, old work outside the windows, cross-depth
ownership, common physical pricing and outer recovery remain open.

The selected conditional kappa remains 0.00363005817 with the same five
assumptions. No selected file is changed. Source pins and the narrowed
card scope are in [SOURCES.json](SOURCES.json), [VENDORED.json](VENDORED.json)
and [TASK.json](TASK.json).

## Reproduce

From the repository root with Python 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/current-shared-guide-banks --check-only
python3.12 -B scripts/research_package.py --package research/current-shared-guide-banks
```

The registered normal and optimized commands must each print
`PASS_CURRENT_SHARED_GUIDE_BANKS` with the complete receipt summary.
They use only the package and the five declared current-main input files.
A full selected replay, Lean and Docker are outside this local check.

## Open next questions

Can a numerical child use the same guide without altering it, return all
service heads, and leave all three shared work tapes blank? The next step
is one literal compiled child with its complete live-parent inventory.
The blocker is the missing complete compiled boundary, not the reset
selector. Do not extend this local bank count into a recursive storage
bound without that inventory and a common cost model.

## Credit

Prepared by Ali Romman with substantial OpenAI Codex assistance.
The retained machine and binary counter were prepared for David Arias
with Codex assistance in
[PR #6719](https://github.com/CrocSwap/integer-mult-bounds/pull/6719),
submitted by thu-nmrc. The guide lifecycle is unchanged from PR #7667.
The PR #7663 word and bank sources retain the work of Ali Romman,
CubeJerry, Clear1nsight, DreamingOfClouds, SYLforge and RohanArun.
All source notices and exact copy origins remain in this package.
New work is Apache-2.0.
