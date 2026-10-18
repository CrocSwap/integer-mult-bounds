# Uniform control work for the selected BIT caller

We give an explicit control compiler and a root-independent nonchild-work
bound for the pending PR2234 construction. We implement its generated weight
grammar with a stack and sequential frozen-table reads, retaining global
field slots after unit resets. Under the retained complete-stream pass and
parking contracts, we derive one `C_q V(n+w)` bound across the allowed roots.

For `w=ceil(e^(17/10000))`, our preparation allowance is `O_q(w^1800)`.
The all-integer inequality

    w^1800 / q^(w-1) <= 2^1800 * 1800!

absorbs that work into both body and high-header target fibres. We include
the width-one bypass. The compiler keeps arbitrary spectator counters
outside its compact ancestry scans; a repeated read of an unrelated long
prefix would invalidate this argument.

[PROOF.md](PROOF.md) traces the actual selected coefficient formulas and
preparation sites, gives the stack bound and specifies the counter lowering.
This addresses the physical-charge handoff from
[PR2289](https://github.com/CrocSwap/integer-mult-bounds/pull/2289) and
[PR2295](https://github.com/CrocSwap/integer-mult-bounds/pull/2295).
We claim no new recurrence, moment, exponent or full selected-machine proof.

## Evidence and reproduction

The checker exercises 82 generated-coordinate cases, including full binary
request trees through depth 10 and Good→unit reset→Good/Pair paths. It checks
2,916 complete small body records and 82,680 header fibres. Controls reject
field compaction without rebinding, a current-fresh-field capture, swapped
bindings and unused-stock reads. The constant's exact value has 18,675 bits.

Use Python 3.12 and the standard library:

```sh
python3.12 scripts/research_package.py --package research/selected-control-uniformity
```

The hook runs normal and optimized replays. `verify.py --emit` prints a fresh
receipt without writing files. [RESULT.json](RESULT.json) records the counts
and scope. We compare the iterative interpreter with an attributed recursive
reference for the same mathematical grammar. We test prepared unit tables,
not the complete selected matrix producers or a recursive payload dispatcher.
The bit-read/head counters measure the finite control model. The written
proof supplies schoolbook arithmetic and ripple-counter costs; we do not
treat Python runtime or list access as a Turing-machine time measurement.

## Open next questions

Review the uniform bound together with the pending physical caller. In
particular, check the separate spectator counters, one sequential vector
pass rather than a vector per grammar node, and cleanup before parking.
The next implementation step is to connect this control interpreter to
the retained full-ring preparation and complete payload dispatcher.
[TASK.json](TASK.json) records the concrete boundary and remaining work.

Jose Manuel ([jmbarrancoml](https://github.com/jmbarrancoml)) prepared this
contribution with substantial OpenAI Codex assistance. We claim no independent
human or new proof-assistant verification. [NOTICE.md](NOTICE.md) retains
predecessor credit. Coordination:
[Discussion2304](https://github.com/CrocSwap/integer-mult-bounds/discussions/2304).
