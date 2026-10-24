# One retained workspace for the streamed R437 leaf and XOR

The complete repeated leaf/XOR consumer in [#5055](https://github.com/CrocSwap/integer-mult-bounds/pull/5055)
can use one inventory of **q²+136 physical record tapes**, including its copied
input fibres, nested counters, coefficient stacks and erasure. The same
inventory serves every emitted prefix. This supplies the persistent-workspace
part of the predecessor's explicit handoff at its successful, nonrecursive
leaf boundary, with a paid pooling interface. The source traffic T still needs
an all-parameter tariff; whole-caller admission and kappa are unchanged.

[PROOF.md](PROOF.md) derives the source-bound lifetime and retained-backing
bounds and charges the pooling interface. [pooled.py](pooled.py) specializes the
unchanged predecessor function bytecode, using the existing physical-caller
lease implementation. The producer runs outside the lease scope, preserving
its persistent prefix/reader roles. Every prefix returns the pool blank,
unleased and at its origins. Source Tape/Arena creation inside the consumer
is rejected.

For complete local fibre size v, complete prefix body D, largest (possibly
extended) Program body P, validated callback depth H and Word widths I,L, set

```
A = q²+136
s = max(2I+4, L+3)
M = max(v, D, P, (2H+3)s, I+3, L+3, bit_length(v)+3).
```

A fresh pool retains at most **A(M+2) cells**, independent of the number of
prefixes. For a previously used pool, its entry backing remains charged.
Relative to the original consumer traffic T, the added record-cell charge is
at most `K + 28J + 4AN`, where K is the number of leases, J the number of
temporary callback closes and N the emitted prefixes. The interval starts with
prepared LEFT markers and heads; preparing blank tapes at their origins costs
A writes and A unit moves once. Ordinary copies, movement, normalization and erasure
remain in T. The proof inherits the existing lexical q²+128 source-role bound;
the measurements below are corroboration, not its proof.

## Evidence and scope

[RESULT.json](RESULT.json) records two distinct tests:

| Replay | Complete small cube | Actual SOURCE87 calibration |
| --- | ---: | ---: |
| Prefixes executed | 243 (all 3×81) | 2 selected dimension-64 prefixes |
| Complete dirty payload bits | 19,683 | 13,122 |
| Physical pool inventory | 145 | 145 |
| Observed peak leases | 27 | 28 |
| Acquisitions, each uniquely retired | 261,468 | 134,854 |
| Retained pool cells after first and final prefix | 1,248 | 199,666 |
| Retained predecessor callback calls | 1,458 | 24 |

The small cube preserves duplicate physical prefixes, all nonzero high digits,
source order, every callback and the independent whole-payload permutation/XOR
oracle. The separate actual calibration uses request1676's source-produced
Program, nontrivial coefficient histories and complete local returns. Its
two-prefix restriction is explicit: it does not execute the 3^4096 high domain.

At **every** boundary, the verifier checks identical physical tape identities,
all backing blank, exact acquisition/retirement equality, and conservation of
all physical reads/writes/unit moves against lease, allocation and boundary
meters. Every physical scratch clear is checked against its exact head/body
tariff, including hidden nonblank-tail rejection. Checker scans and histories
do not drive runtime decisions. Four deliberate defects must fail for their
specified reasons: insufficient roles, omitted fibre retirement, a raw Tape
constructor, and a dirty role before reuse. Inherited payload/corruption checks
remain active under both ordinary and optimized Python.

Base main: `a5df48c55ea806d7952b65acc9c76d878ff09b13`; priority revision 7,
refined `r437-carrier-integration` card. The scoped claim is
[#4682 comment19144606](https://github.com/CrocSwap/integer-mult-bounds/discussions/4682#discussioncomment-19144606).
[TASK.json](TASK.json) records scope, value, stop conditions and follow-up.
[SOURCES.json](SOURCES.json) pins 414 live input files and three provenance
records. The loader uses the predecessor's explicitly retained historical
selected record; it does not admit today's selected #4470 frontier.

## Reproduce

Python 3.12, standard library only. From repository root:

```sh
python3.12 -B scripts/research_package.py --package research/r437-streamed-leaf-workspace --check-only
python3.12 -B scripts/research_package.py --package research/r437-streamed-leaf-workspace
```

The registered run executes ordinary and optimized modes, each bounded to
600 seconds. Direct commands, also usable in the committed Git-free export:

```sh
python3.12 -I -W error -B research/r437-streamed-leaf-workspace/verify.py
python3.12 -I -W error -O -B research/r437-streamed-leaf-workspace/verify.py
```

Each mode runs fixtures and failure controls in separate isolated processes,
then compares the complete deterministic receipt. `--write` intentionally
regenerates that receipt. `--mode generic` and `--mode actual` print diagnostic
JSON. All external inputs are explicitly declared in [VERIFY.json](VERIFY.json).
The generic registered runner additionally checks Git provenance.

## Limits

The uniform statement uses the default inventory. For an explicitly larger
pool, replace A by its actual capacity in the backing and boundary charges.
The statement requires the authenticated synchronous source callback,
sufficient supplied numerical arenas and the stated true source maxima. It
excludes arbitrary callback/event producers and exceptions. A failed callback
may leave leases live; there is no transactional rollback guarantee. The full
source/target/output packets, old directory, producer roles, arenas, Program,
codebook and suspended owners remain separately charged. This is a physical
record-tape bound, not a measurement of Python process memory.

## Open next questions

The substantive next step in [TASK.json](TASK.json) is to connect this successful
local boundary to a complete R437 node's canonical ownership and recursive
return contract, retaining the producer and full-packet residents and giving
the source traffic T an explicit parameter tariff. Start with the unchanged
call/return owners and the two source-bound ledgers; do not infer a smaller
global reserve from the local 27/28-lease observations. Context/codebook cost,
precision/stock and native/compiler/outer admission remain separate obligations.

## Attribution

Krzysztof Wójt, with substantial OpenAI Codex assistance, including Luna
supporting source, coordination and metadata audits; primary-agent integration
and verification. New work is Apache-2.0.

JoyboyBrian retains credit for #5055's streamed producer/consumer and #4981's
actual SOURCE87 fixtures and independent oracles. Jose Manuel retains credit
for the physical caller's ScratchPool and source-role proof; David Arias for
the logical caller; Chris R for the R437 integration bridge. All retained
predecessor author and licensing notices remain in the pinned source chain.
