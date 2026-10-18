# One-stream reverse-Horner batching for JP8 cleanup

This finite complex-supplier circuit result saves **19,688 real-component
primitives in the backward JP8 program**. It replaces 999 contiguous
common-target cleanup runs containing 3,022 additions. The program uses one
existing coefficient-work stream, preserves every live register's boundary map,
and clears arbitrary incoming private work. The complete scalar prefix envelope
stays unchanged at 101 bits, within the inherited 192-bit allowance.

Status: **research construction / finite circuit improvement, no new kappa**.
The selected #626 conditional result remains
`51110230636731/31250000000000000 = 0.001635527380375392`.

| JP8 orientation | Original real primitives | Replacement | Saving |
| --- | ---: | ---: | ---: |
| Forward | 257,232 | 257,232 | 0 |
| Backward | 257,280 | 237,592 | 19,688 |

Every source read, signed accumulation, halving, doubling, and both scratch
clears is included. Recursive children, wrappers, adapters, scalar macro
boundaries outside each batch, and paid frame profiles retain their original
charges. This is an arithmetic invoice reduction, not a runtime benchmark.

## Reproduce

From the repository root, using Python 3.11+ and the standard library:

```sh
python3 -I -B research/complex-jp8-fanin/verify.py
```

Expected:

```text
PASS_JP8_REVERSE_HORNER_FANIN batches=999 additions=3022 real_saved=19688 columns=716 controls=12
```

The check is offline and writes no files. It checks all source payload hashes,
the selected SPEC's semantic identities, full-frame source lifetimes, every
block's exact map including arbitrary work input, and both complete scalar
projections on 716 input columns plus eight centre inputs and one work input.
It recomputes exact costs and positive prefix envelopes and compares
[EXPECTED.json](EXPECTED.json). `--receipt` prints the independently
recomputed evidence without comparing that aggregate receipt.

An additional implementation uses independent grouping and a flat-vector
column interpreter:

```sh
python3 -I -B research/complex-jp8-fanin/check_columns.py
```

It checks every local input column of all 999 blocks and rejects an omitted
final clear in every block. The main verifier's twelve controls cover missing
initialization/restoration/source reads/halving/doubling/target accumulation,
wrong sign, aliases, frame mismatches, non-dyadic coefficients, inflated cost,
and an endpoint-neutral prefix excursion.

## Construction and coverage

For a run `y += sign_i * n/2^k * x_i`, clear `W` and collect the signed sources
in it. Halve `W` `k` times, scan numerator bits from low to high, add `W` to
`y` at each set bit, and double `W` between bit positions. Finally clear `W`.
The [proof](PROOF.md) gives exact maps, frame conditions, costs and prefix bounds.

The complete domain is maximal contiguous runs of at least two additions in
`full_frame_cleanup`, frame 1, with one live target and equal non-unit
coefficient magnitude. Each source must differ from the target. Every event
outside this class ends a run. Enumeration is exhaustive with no timeout or
sampling; the forward domain is also scanned and has no eligible run.
Other phases and coefficient-sharing classes are outside the claim. No
optimality or impossibility claim follows from this finite enumeration.

The assignment seed is **27**, generated using OS randomness. The local
[claim](CLAIM.md) records the three candidates, selection and stopping rule.
The exact base is `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
[SOURCES.json](SOURCES.json) records eight payload SHA-256 pins and Git blobs,
the #626 and #622 heads, and the inherited #543 bit dependency. Gzip equality
uses decompressed payload bytes, so container recompression is harmless.

## Prior work, attribution and limits

This construction follows the sharing idea in ellipsi2's [#722](https://github.com/CrocSwap/integer-mult-bounds/pull/722),
whose reported forward common-source grouping saves 19,688 primitives and finds
no backward common-source run. This package supplies the backward common-target
dual and its distinct accumulated-source prefix argument. It imports no pending
implementation. The equal saving comes from the transposed run structure;
it is not a claim of independently inventing forward coefficient sharing.
No combined receipt with #722, [#696](https://github.com/CrocSwap/integer-mult-bounds/pull/696)
or [#723](https://github.com/CrocSwap/integer-mult-bounds/pull/723) is asserted.
Concurrent [#739](https://github.com/CrocSwap/integer-mult-bounds/pull/739)
extends forward common-source sharing across coefficient magnitudes; its
reported backward scan has no join in that class. This package adds backward
common-target batching. [#734](https://github.com/CrocSwap/integer-mult-bounds/pull/734)
changes single-coefficient preparation, and [#745](https://github.com/CrocSwap/integer-mult-bounds/pull/745)
independently audits the original JP8 private-centre inputs by reverse replay.
Their descriptions and metadata were inspected, with no imported code or
combined cost claim. Private-input checking here is a verification obligation,
not a priority claim over those contributions.
[#681](https://github.com/CrocSwap/integer-mult-bounds/pull/681) changes factory
macros, and [#719](https://github.com/CrocSwap/integer-mult-bounds/pull/719)
proves a different CK fixed-middle obstruction.

Credit to Jeremy Kothe's #622 construction and Claude Code contributors,
Chafik Boukhalfa's #626 package, icekylinx's scalar/factory/direct-delivery
lineage, DreamingOfClouds' compiler and cold-helper work, Dugongue, eumemic,
and the retained predecessor notices. Prepared for **Sagar Thakrar,
@thakrarsagar**, with substantial **OpenAI Codex assistance**, including two
separate scoped AI checks. No independent human review is claimed.
New contributions are Apache-2.0 under the repository license.

The private coefficient stream is zero at each new batch boundary, rather than
after each replaced macro. This is the explicit local interface change.
The package freshly verifies scalar projections, local full-frame access,
costs and envelopes. Native frame/wrapper/phase correctness outside the blocks
is inherited from the pinned supplier evidence. Production-emitter integration,
global invoice/admission regeneration, and any future supplier promotion remain
separate work. All inherited compiler, common-label/mutable-basis realization,
hosting, residual, precision/tape/recovery, bit-supplier and analytic assumptions
remain. This is not a formal proof of the multiplication theorem.

See [VALIDATION.md](VALIDATION.md) for executed checks and explicit omissions.
