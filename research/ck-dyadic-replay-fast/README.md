# Faster Exact CK Dyadic Replay

**Tooling improvement; no new kappa.** Two exact sparse-row kernels accelerate
the integer-dyadic replay of Ross Richardson's incorporated [PR917](https://github.com/CrocSwap/integer-mult-bounds/pull/917).
The adapter changes only `_normal_row` and `_sum_rows` in memory. It runs the
complete unchanged historical verifier; no predecessor file is edited.

Five paired runs on Python 3.14.5/macOS arm64 reduce the median four-stream
integer replay from **1.03788 s to 0.68973 s (1.50x)**. Both modes execute the
same **374,606 primitives**, with every one of the **725 arbitrary input
columns**, in the original and candidate forward/backward circuits. This is a
stage timing, excluding input construction, the Fraction oracle and native
frame audit. It is not a whole-verifier or multiplication-runtime speedup.
[BENCHMARK.json](BENCHMARK.json) records all five pairs, one warmup pair,
alternating order, environment and full input/output hashes.
An independent paired run on Python 3.12.13 gives **0.90050 s to 0.62027 s
(1.45x)**, with identical stream/result hashes in
[BENCHMARK-PY312.json](BENCHMARK-PY312.json). Timings describe this host; the
functional verifier does not impose a machine-dependent speed threshold.

## Reproduce

Python 3.10+ and the standard library suffice. From the repository root:

```sh
python3 -I -B research/ck-dyadic-replay-fast/verify.py
```

Expected: `PASS_CK_DYADIC_REPLAY_FAST streams=4 primitives=374606 columns=725 controls=10+25 no_new_kappa`.
This compares every kernel return against the frozen arithmetic, checks all
complete result fields, runs seven focused test groups (including the six
inherited arithmetic groups), and replays the complete PR917 construction,
Fraction oracle, native frame/wrapper audit and all **10+25** original controls.
[RESULT.json](RESULT.json) is deterministic; timings are separate. Normal runs
do not regenerate committed artifacts. `verify.py --record` explicitly records
only this package's receipt.

The accelerated historical replay alone is available via `run.py`. To repeat
the paired stage benchmark, run `benchmark.py --repeats 5`; `--output PATH`
explicitly writes a timing report. The generic Python 3.12 CI hook is:

```sh
python3.12 scripts/research_package.py --package research/ck-dyadic-replay-fast
```

## Exactness Argument

A row `(terms,e)` denotes `sum terms[j]*input[j] / 2**e`, with `e >= 0`.
The pinned executor maintains a zero-free numerator dictionary: its initial
rows, CLEAR, COPY and NEGATE preserve the invariant; DOUBLE and HALVE use the
normalizer; ADD uses the sum kernel. COPY may share a dictionary, so neither
kernel may mutate its inputs.

Addition aligns denominators to `2**max(e_left,e_right)` by exact integer
shifts, copies the left map, adds each signed right numerator, and immediately
deletes cancellations. This equals the original addition followed by removal
of zero entries. No scalar instruction or coefficient is omitted.

Normalization divides by `2**min(e,min_j v2(terms[j]))`. Encountering one odd
nonzero numerator proves that the common valuation is zero, so the scan can
stop exactly. If every numerator is even, the scan computes the same minimum
as the original. Division by right shift is exact for signed integers because
each numerator is divisible by the selected power. The empty row remains
`({},0)`. Thus both kernels return the same canonical row, and the unchanged
executor keeps the same endpoint, every transient denominator, positive prefix
allowance, first maximum instruction, private erasure and price.

Evidence includes 729 small signed normalization cases, 328,050 signed sums,
input immutability, wide denominator differences, complete cancellations,
a separate 3,000-step Fraction oracle, dirty-private/COPY/transient/domain
controls, source-drift rejection for every live input, and restoration of the
adapter after exceptions. Finite checks support this kernel argument; they are
not a formal proof of the full multiplication theorem.

## Pins And Scope

Exact base: **`bce54fb3f895cbe5cd4c0eb477c3afeed100190f`**. Assignment seed **89**;
the three candidates, OS draw, overlap evidence and local claim are in
[CLAIM.md](CLAIM.md). [SOURCES.json](SOURCES.json) records every live external
input with Git blob and SHA256, plus predecessor heads. The original task card
and selected certificate are historical provenance; live source drift rejects
the adapter before importing or executing the predecessor.

PR917's reviewed head is `085c32a25e2a09b029fa816195b97fa93d6f0788`; its retained
CK provider is PR626 `660de893d27bb7abd1d5b01b1640207528a5c851` on PR622
`f69477f4f6d3c7eb1f740b166881bffed4ffa9f6`. The selected conditional result at
the base remains PR1094, kappa `0.001672660197076918`, with bit supplier PR589.
No selected cold replay, supplier adoption, paid-profile change or stronger
bound is claimed. All-size/compiler, realization, hosting, precision/tape and
analytic transfer obligations remain inherited.

Nearest concurrent tools include PR1234's rational frame normalization,
PR1217's ternary-frame replay and PR1184's emitted local audit. This targets a
different pinned executor and preserves its full receipt. PR1184 introduces
mutable shared-denominator rows for the scalar-macro native auditor; its
`Row` does not canonicalize after each operation. This contribution accelerates
the already-integer, immutable, canonical primitive rows of PR917, preserving
transient denominator reporting and dirty coefficient work. The incorporated
`scalar-fused-dyadic` tool instead fuses ordinary Fraction updates in PR799's
native macro auditor. These predecessor tools retain credit for exact dyadic
arithmetic and opt-in adapters; no code from them is imported and their
performance figures are not combined.

The final complete overlap snapshot covered **787 open PRs** at 2026-10-14
00:37:24 UTC and **146 discussion/comment/reply records** at 00:37:49 UTC,
alongside local notes and the review ledger. The nearest PR heads were checked
explicitly; no same-target claim was observed. Main advanced to
`410026dc5513b87db92ae98571d1d5984c69a983`; none of the live input paths changed.
The original base and source pins remain exact. See the claim for search limits.

## Open next questions

Profile one other source-bound dyadic replay whose arithmetic dominates its
cost. Check its immutable, zero-free row invariant and complete failure
coverage before applying these kernels. A separately pinned target and coverage
review are prerequisites; no other verifier is automatically modified.
Structured relevance, first step and blockers are in [TASK.json](TASK.json).

## Credit

Prepared for **Sricharan Vagvala (@theon199)** with substantial **OpenAI Codex
assistance** for selection, implementation, analysis, verification and writing.
Parent-only work; no independent human review is asserted. Apache-2.0.

Credit **Ross Richardson/PR917** for the complete circuit and independent
dyadic checker, **David Awad/PR807** for restored CK helper pairs,
**@dd-hemant/PR816** for signed target forests, and the PR749/759 mechanisms.
The retained icekylinx/PR425/433, DreamingOfClouds, Jeremy Kothe/PR622 and Chafik
Boukhalfa/PR626 compiler/construction lineage retains its original notices.
The inherited Fraction, native and combinatorial checks are still executed.
