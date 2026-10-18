# Shared coefficient work in the selected JP8 cleanup

**Finite complex-supplier circuit improvement / research note; no new kappa.**

The selected JP8 cleanup contains 999 maximal contiguous runs with a common
source and a common non-unit coefficient magnitude. Preparing that coefficient
once per run saves **19,688 real-component primitives**. All 3,022 affected
target updates retain their original order. The existing coefficient-work
stream is cleared at each run boundary; no additional stream is introduced.

| Selected JP8 program | Original primitives | Shared-work primitives | Saving |
| --- | ---: | ---: | ---: |
| Forward, entire scalar program | 257,232 | 237,544 | 19,688 |
| Forward, final cleanup alone | 116,176 | 96,488 | 19,688 |
| Backward, entire scalar program | 257,280 | 257,280 | 0 |

The complete forward scalar count decreases by about 7.65%. These are exact
operation counts under the inherited primitive convention, not runtime
benchmarks. The backward word has no eligible run. Recursive children,
adapters, source/helper registers, final restoration, and the paid profile
remain unchanged. The selected conditional saving remains
`51110230636731/31250000000000000`.

## Reproduce

From the repository root, with Python 3.11+ and its standard library:

```sh
python -B research/complex-jp8-cleanup-fusion/verify.py
```

Expected final line:

```text
PASS_JP8_SHARED_COEFFICIENT_CLEANUP groups=999 saved=19688 columns=716 orientations=2 controls=10
```

The command is offline and does not write files. It checks the source pins,
reconstructs all runs and their exact primitive circuits, replays every one of
the 716 arbitrary data/helper input columns in both emitted orientations,
checks all private output rows, recounts the fixed paid profile, and compares
every field of [EXPECTED.json](EXPECTED.json). At changed blocks it executes
the replacement primitives explicitly; unchanged scalar macros use exact
rational semantics. Each block is additionally checked on independent formal
input rows, including arbitrary incoming coefficient work. This combination
does not claim a primitive-level replay of unchanged macro lowerings.

An independent flat-vector column interpreter and frame/child controls run with:

```sh
python -B research/complex-jp8-cleanup-fusion/test_verify.py
```

This checks all 999 block maps without using the main checker's row interpreter,
and tests the inverse-transpose ordering with a noncommuting example.

`verify.py --write-receipt NEW_PATH` writes a newly computed receipt using
exclusive creation, refusing to replace an existing file. Ordinary verification
always compares with the committed receipt. Compressed inputs are bound by
their complete decompressed bytes, so recompression does not affect acceptance.

## Construction, cost, and prefix bound

For a block of `m >= 2` updates, write the common reduced magnitude as
`q = a / 2^b`, where `a > 0`. Every update is
`x[t_i] += sign_i * q * x[s]`, and `t_i != s`. Thus the source stays unchanged.
Clear the existing work stream `W`, form `a*x[s]` by the inherited binary
Horner circuit, halve it `b` times, perform the signed target accumulations in
their original order, and clear `W`. Repeated targets and opposite signs are
allowed. Unit coefficients, scales, mismatched sources/magnitudes, and all
non-scalar events end a run. No operation is reordered.

Let `H = (bit_length(a)-1) + popcount(a) + b`. Each source-bit addition,
doubling, halving, signed accumulation, and initial/final clear costs one
primitive per real component. Original cost is `m*(H+3)`; shared cost is
`H+m+2`. The saving is therefore `2*(m-1)*(H+2)` for both real components.
The certificate records the exact start, length, source, magnitude, and both
costs for every run. It contains 36 distinct non-unit magnitudes; run lengths
range from 2 through 13.

The block preserves every live row for arbitrary inputs, and discards arbitrary
incoming `W` exactly as the old cleared-work lowering did. At each target
update, the nonnegative envelope of every live row is identical to the original.
During preparation and retention, work magnitude is at most `a*N[s]`, already
charged by the first original preparation. The exact entire-program prefix
envelopes therefore remain:

- Forward: `4536094588619580433782972610869617/281474976710656`.
- Backward: `16753412757380464429924108070201913461/8388608`.

The checker verifies these rational values against the selected SPEC. Ten
arithmetic controls reject wrong signs, missing initial/final clears, omitted
halving, source/magnitude changes, source aliasing, and three endpoint-neutral
prefix excursions, including one hidden behind negations and one on a live
register. The additional test
suite rejects an emitted-frame mutation, use of a non-FULL helper, and omission
of a paid child. These controls address restoration and prefix growth even when
checking only a final live-register identity would be insufficient.

## Source pins, search coverage, and scope

Exact base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`. Reviewed source heads:

- #626: `660de893d27bb7abd1d5b01b1640207528a5c851`.
- #622: `f69477f4f6d3c7eb1f740b166881bffed4ffa9f6`.
- Retained #543 bit supplier: `2065fe4f72a914d907f1046603f5a36f17018535`.

[SOURCE-PINS.json](SOURCE-PINS.json) binds the exact consumed files; both program
payloads and event lists are additionally bound to #626's SPEC. The actual
selected construction and its limitations are documented in the
[maintainer review](../../docs/research/community-k492-review.md).

OS assignment seed **31** selected the complex track and, by odd parity, JP8.
The initial hypothesis scanned every starting addition in its 9,006-gate final
cleanup for an equal directed addition before the first noncommuting operation.
It found zero eligible pairs; the command reproduces this finite census. That
does not exclude general circuit resynthesis. The single evidence-driven pivot
was to shared coefficient preparation. Both orientation scans exhaust their
entire final cleanup once, with no sampling or timeout. Completed coverage is
999 forward runs and zero backward runs; no optimality is claimed.

The public supplier/emitter and selected frontier are unchanged. In particular,
the inherited receipt says coefficient work is cleared after **each scalar
macro**. This package defines a **fanout block** and proves clearing at that
block's boundary instead. The original receipt does not certify the new primitive
count. This standalone implementation and exact checks provide a local circuit
substitution; transporting it into the production emitter, updating its private
lifetime contract, and rebuilding global invoices/admission are not supplied.
All replacements stay after exit adapters and before post wrappers at the FULL
frame. The 120-gate early cleanup and all other phases are untouched.

All-size compiler/common-label/mutable-basis realization, pooled hosting,
normalized residuals, precision/tape/exact recovery, analytic transfer, and the
bit supplier's inherited assumptions remain. This is neither a complete formal
proof of integer multiplication nor a new recurrence or kappa certificate.

## Attribution and overlap

Credit belongs to icekylinx's direct-delivery/factory and scalar-emitter lineage,
Jeremy Kothe/AtomScout's #622 and preceding JP8 construction, DreamingOfClouds'
cold-helper and native-verification work, Chafik Boukhalfa's #626 package,
eumemic's retained #543 supplier, and the earlier contributors and notices in
[the selected package](../complex-k492-owner-repair/NOTICE.md).

Concurrent [#696](https://github.com/CrocSwap/integer-mult-bounds/pull/696)
improves individual dyadic macro lowerings; this contribution instead shares
preparation across a non-unit multi-target run and retains the original Horner
preparation. Its reported savings are against the selected base, not additive
to #696 without a composed recount. [#681](https://github.com/CrocSwap/integer-mult-bounds/pull/681)
changes a raw factory's scalar word; this preserves the selected scalar word.
[#698](https://github.com/CrocSwap/integer-mult-bounds/pull/698) concerns CK B-phase
frames, and #651/#683/#687 study delivery or reorder restrictions. None is an
implementation dependency. The local [claim](CLAIM.md) records selection and
coordination; [REVIEW.md](REVIEW.md) records a separate scoped AI source review.

Prepared for **@ellipsi2** with substantial **OpenAI Codex assistance** in research,
implementation, mathematical analysis, verification, and writing, including one
scoped AI reviewer. This is not independent human review. New files use the
repository's Apache-2.0 license; all predecessor notices remain in place.
