# Produce, consume and retire the current flat guide

This package emits the current native flat guide from physical binary
record count N and signed component width W. The actual emitted guide
drives the retained INIT and CLEAR graphs, then is completely retired.
All seven heads return. No host-decoded dimension controls execution.
There is no new kappa or complete recursive allocator.

The source format and reset graph are from
[PR #7663](https://github.com/CrocSwap/integer-mult-bounds/pull/7663), exact
head `b81f40997de646de30749d367484d89e59fc3013`. The local selector in
[PR #7666](https://github.com/CrocSwap/integer-mult-bounds/pull/7666) starts
with a correct immutable guide. This result supplies that distinct local
producer/consumer connection. No code from PR7666 is imported.

[PROOF.md](PROOF.md) gives the all-size loop and cost arguments.
[TABLES.json](TABLES.json) contains every emitted instruction, and
[RESULT.json](RESULT.json) records the exact executions and controls.
[program.py](program.py) builds tables before runtime descriptors exist.
[verify.py](verify.py) checks them with two different interpreters.

## Exact contract and result

The preserved inputs are positive canonical binary N and W. The output
has N complete records of W real bits, a separator, W imaginary bits,
a separator and one represented blank. Put L=N(2W+3). For the current
native view N=R*2^(9f), including all spectators; this package does not
produce that root descriptor or derive the root width.

Three conversion work tapes start blank. The owned guide and target
windows may contain arbitrary old symbols. Every cell of the guide's
exact L+2-cell window is overwritten and later erased. INIT writes a
complete scientific-zero target, and CLEAR blanks its L payload cells
while preserving both guards. Borrowed exterior cells stay unchanged.

The producer has 210 literal instructions, INIT and CLEAR each have 40,
and guide retirement has 16. All use seven fixed tapes and the retained
seven-symbol alphabet. With
`c(x)=24x-7 popcount(x)+15 bitlength(x)+12`, the exact counts are:

| Phase | Instructions executed |
| --- | --- |
| Production | c(N)+c(W)+22NW+36N+7W+36 |
| Each reset | 9L+11 |
| Guide retirement | 7L+10 |
| Complete lifecycle | c(N)+c(W)+72NW+111N+7W+68 |

The complete lifecycle costs at most 72L instructions. Its exact visited
capacity, including cells that were erased, is
`2L+N+W+bitlength(N)+bitlength(W)+max(bitlength(N),bitlength(W))+14`,
which is at most 7L for the stated fresh windows. On reused tapes, each
prior reserved span remains charged through `max(old_span,current_span)`.
No erased backing is released for free.

## Evidence

Forty-two shapes cover binary shrink boundaries, widths 1,2,3,17 and
complete native views. Every phase agrees with a separate dense opcode
interpreter on all cells, heads and instruction counts. The complete
N=512,W=1 lifecycle takes exactly 106258 instructions and retains 5668
visited cells. The N=1024,W=3 case checks a second complete view.

Five literal instruction faults detect wrong zero output, skipped blank
writes on a dirty guide, a premature boundary, a missing head return and
incomplete guide retirement. A sixth control rejects a redundant high
zero in a binary input. Failure atomicity and full recognition of every
malformed global state are not claimed.

The unchanged source guide producer supplies the expected-format oracle.
The unchanged machine, assembler and binary-to-unary emitter come from
[PR #6719](https://github.com/CrocSwap/integer-mult-bounds/pull/6719)'s
retained source closure. The emitted program performs all loop control,
counter work, writes, head movement and cleanup on physical tapes.

## Reproduce

Use Python 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/current-flat-guide-lifecycle
```

Normal and optimized isolated replay must print
`PASS_CURRENT_FLAT_GUIDE_LIFECYCLE` and
`PASS_REGISTERED_RESEARCH_PACKAGE`. No Git, network or solver is used by
scientific replay. Normal replay writes no files. The explicit `--write`
option creates initial receipts and refuses to replace existing ones.

## Limits

This result assumes distinct tapes, canonical binary descriptors, blank
conversion workspace and exact granted guide/target windows. A larger old
private tail needs its own complete-extent treatment. Numerical work
between reset calls is a separate service that must preserve the guide
and return the required heads.

Root descriptor production, adapter permutations, the actual compiled
owner map, numerical children, cross-depth workspace and common physical
pricing remain open. The source's full conditional application and the
selected multiplier were not replayed. All five framework assumptions
remain; the selected frontier is unchanged.

## Open next questions

Connect the output to one actual compiled owner map and charge guide
provisioning, storage and retirement at each occurrence. Use the earlier
root producer only after its different delayed-cover geometry has an
explicit consumer map. [TASK.json](TASK.json) records these boundaries.

## Source and credit

David Arias supplied the unchanged machine, assembler and counter, with
its exact counter proof. The [retained notice](../../research/delayed-cover-physical-batch-routing/NOTICE)
and file headers preserve that credit. thu-nmrc supplied the delayed-cover
physical/root package that retains those sources. This work does not
repeat its root or recursive shape theorem.

Ali Romman supplied the PR7663 guide/reset construction with substantial
OpenAI Codex assistance. CubeJerry supplied its selected primitive and
prior typed reset. [source/NOTICE](source/NOTICE) and the copied notices
preserve the native lineage. The copied word module supplies only helper
imports here; no native word is loaded or numerically executed.
[SOURCES.json](SOURCES.json) and [VENDORED.json](VENDORED.json) bind every
consumed source. Original files are unchanged.

Ali Romman directed this new emitted lifecycle, proof and verification
with substantial OpenAI Codex assistance. New work is Apache-2.0. The
canonical base is `e54523517d0f03e58352e647c403a5af3e525a57`.
