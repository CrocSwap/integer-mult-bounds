# Paid finite-control key at the actual CRT repair port

This package replaces the host-integer `evaluate_key` premise of
[the mask-driven repair bridge](../crt-mask-repair-bridge/README.md) with an
actual finite-control tape service for its retained u2,t2,y8 geometry. It
executes all ten inverse shears, three current-state source queries, the ideal
switch, and direct twelve-bit stream append. Borrowed counter/ROM cells are
preserved; scratch is erased and its heads returned. The append head advances
twelve cells as required by the existing interface.

The scoped [proof](PROOF.md) covers every 12-bit address and every
target-independent 32-bit source ROM, for target 0, 1 or 2, with a complete
instruction bound below **3,300,000 per key**. This is a fixed-geometry theorem
and an actual caller replay, not an all-size CRT theorem or an E(p,ell) closure.

## New result and predecessor boundary

[PR #4637](https://github.com/CrocSwap/integer-mult-bounds/pull/4637), exact head
`60d0b09f13a9f9ebdd93d98d83d16ce6907d70b6`, joins producer, scanner and repair
but leaves the address-to-key function in host integer arithmetic.
[PR #4739](https://github.com/CrocSwap/integer-mult-bounds/pull/4739), exact head
`26ccde014218f7d906d1251dc295fbc1437ede8a`, charges transported key bit work
in a different finite fixture without eliminating host control.
[PR #4752](https://github.com/CrocSwap/integer-mult-bounds/pull/4752), exact head
`e8bdf35809eecfb0b8db7b5e141cb1ba0f4f6a1c`, gives the uniform encoded ROM query
but explicitly leaves its caller descriptor adapter and remaining key work open.

The new [service](service.py) rebuilds descriptors from the current tape y at
all three epochs and inlines that query program. Its executor never decodes
an address/word or inspects head coordinates, tape lengths or a host key.
Assembly is finite for the three retained targets. Fifteen tape roles include
the original counter/stream, one borrowed ROM and twelve owned tapes.
[SOURCES.json](SOURCES.json) pins the complete live dependency closure to
base `624de9dc66858af0945e5f8a0942488d62280d43`; predecessors are reused unchanged.
The selected result is unchanged. Archive merging is not scientific approval.

## Evidence and cost boundary

[COMPONENT.json](COMPONENT.json) records 376 accepted cases across all five
actual source-layer ROMs plus a parity source. A separate event interpreter
replays **16,345,420 instructions**, checks all three source epochs, borrowed
contents, direct append and private erasure. Four malformed addresses reject;
four behavioral faults (stale descriptor, truncated carry, omitted erase,
omitted ROM return) and two incomplete event logs are detected. Sampled key
costs range from 41,395 to 44,928 instructions; the proof uses static charging,
not that sampled maximum.

[CALLER.json](CALLER.json) records the unchanged original middle-layer
producer→scanner→repair execution with only the key port replaced:

| Quantity | Exact value |
| --- | ---: |
| Protected payloads | 4,096 |
| Marked holes / service calls | 2,944 |
| Good addresses called / holes missed | 0 / 0 |
| Complete key-service instructions | 128,507,264 |
| Key-service cell actions | 39,360,192 |
| Interface cell actions already in repair invoice | 229,632 |
| Original repair cell invoice including interface | 13,314,027 |
| De-duplicated repair + key cell actions | 52,444,587 |
| Producer / scanner cell invoices | 841 / 454,830 |

The full protected output equals the source ideal layer and every required
caller/service scratch tape and head is restored. Only this middle layer was
fully replayed; component tests use all five source ROMs.

These instruction and cell ledgers are distinct. The raw macro S, supplied
ROM construction/layout, outer producer/scanner/repair Boolean control,
all-size parameter handling and total E(p,ell) remain external. No numerical
binary-action bound is claimed for the joined port: opaque payload symbols
need a wider encoding than the query component's five-symbol alphabet.
Verifier-only host arrays and address logs never feed back into the service.

## Reproduce

Python 3.12, standard library, one CPU; no Lean, Docker or historical suite.
From the repository root:

```sh
python3.12 scripts/research_package.py --package research/crt-paid-key-service --check-only
python3.12 scripts/research_package.py --package research/crt-paid-key-service
python3.12 -O -B research/crt-paid-key-service/verify.py
```

The registered hook compares both frozen receipts and authenticates all live
inputs. It runs components (60-second cap) and the one caller layer (120-second
cap) sequentially. The source caller producer run took 36.7 seconds locally;
runtime is environment-dependent, not a complexity claim. Receipts are only
rewritten with explicit `--write-result`. See [TASK.json](TASK.json) for the
refined scope and [VERIFY.json](VERIFY.json) for the commands.

## Open next questions

1. Supply the 32-bit source ROM through a physically costed producer, then
   generalize the encoded parameter and bit-word widths. Start by identifying
   the source ROM layout at the actual CRT caller; a larger finite census does
   not establish this uniform construction.
2. Price or lower all control in the joined producer/scanner/repair and its
   opaque-payload alphabet. Start from the exact interface subtraction above;
   counting only cell operations leaves a different obligation from the now
   complete key-service instruction census.

## Credit

JoyboyBrian, with substantial OpenAI Codex assistance. New work Apache-2.0.
Retain the upstream authorship and [source-specific notice](../unconditional-batched-crt/NOTICE.md)
for the original construction, the repair/tape packages and their pinned source
files. This package imports their code and preserves their source bytes.
