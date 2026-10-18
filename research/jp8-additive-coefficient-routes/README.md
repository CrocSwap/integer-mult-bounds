# JP8 cleanup: one positive source read between dyadic shifts

**Finite circuit construction: 2,784 additional real-component primitives
saved beyond power-of-two coefficient reuse; no new kappa.**

In the selected #626 JP8 forward cleanup, 269 transitions can retain the
existing private coefficient stream even when consecutive magnitudes have
different odd numerators. A paid source read changes the numerator, with
dyadic shifts before and after it. Target order, live-register boundaries,
frames, helpers and recursive calls remain unchanged.

| Complete scalar projection | Selected #626 | Power-only reuse (#739 class) | This construction |
|---|---:|---:|---:|
| Forward | 257,232 | 227,206 | **224,422** |
| Backward / inverse-transpose | 257,280 | 257,280 | 257,280 |

These are finite operation counts, not timing measurements. The total
forward saving is 32,810; the new contribution beyond the independently
reconstructed #739 comparator is 2,784. All 269 new transitions change odd
numerator. This construction has 1,091 shared-work blocks. It retains the
original binary-Horner lowering outside those blocks and excludes unit
coefficient macros from the search.

The backward orientation still determines the maximum primitive count.
Even optimistically substituting the new counts into the existing invoice
while retaining all 437,040 adapter allowances and the 25,934,336 compiler
charge leaves the local bound **11,334,342,462,720** unchanged. This is a
useful forward-circuit improvement, not an admitted supplier-bound or
exponent improvement. At the research base, the selected conditional kappa was
**0.001635527380375392**. During submission, main advanced to #741/#589 at
**0.001661202643272239**. This package remains a historical #626 circuit
result; no saving is transported to #741. Its source pins use the immutable
#626 assembly, so advancing the selected-result pointer does not break replay.

## Reproduce

From the repository root, using Python 3.11+ and its standard library:

```sh
python3 -I -B research/jp8-additive-coefficient-routes/verify.py
```

Expected final line:

```text
PASS_JP8_ADDITIVE_ROUTES extra_saved=2784 total_saved=32810 columns=725 orientations=2 controls=12
```

This checks pinned inputs and selected SPEC bindings, regenerates the finite
route certificate in memory, and literally executes every scalar primitive
in both complete programs. It checks all **716 native and nine arbitrary
private input columns**, both shear endpoints, dirty-helper restoration,
private clearing, costs and paid recursive profiles. The complete positive
prefix bounds remain exactly the selected **64-bit forward / 101-bit
backward** values, below the inherited 192-bit allowance. Twelve controls
include source/target aliasing, wrong signs, omitted clears, a wrong source,
phase/frame crossing and an endpoint-neutral prefix excursion.

The independent checker imports neither the constructor nor the verifier
and uses integer arithmetic on an explicitly sufficient dyadic grid:

```sh
python3 -I -B research/jp8-additive-coefficient-routes/independent.py
```

It prints `PASS_INDEPENDENT_ADDITIVE_ROUTES pairs=780 exponent_pairs=849420
saved=32810 controls=4`. It exhausts the full exponent square for all 780
distinct adjacent magnitude pairs, confirms the occurrence census, and
checks every replacement block on its arbitrary source, target and work
columns: **6,776 block input columns** total. Four additional mutation
controls test endpoint, dirty-work clearing and prefix detection.

The unchanged native frame/wrapper auditor can be run in a new directory:

```sh
python3 -I -B research/jp8-additive-coefficient-routes/native_replay.py --output /tmp/jp8-additive-native
```

It prints `PASS_UNCHANGED_NATIVE_JP8_REPLAY columns=716 controls=25`.
This rechecks the original macro word's frame and wrapper obligations; the
new primitive substitution is checked by the first two commands. The
semantic receipt comparison ignores regenerated gzip-container hashes.

`verify.py --write NEW_DIRECTORY` explicitly regenerates the two main
artifacts without replacing existing files. Ordinary verification writes
nothing. `independent.py --write NEW_FILE` generates its separate receipt.

## Experiment and certificate

OS-random assignment seed **31** chose the complex track; `31 % 3 = 1`
selected JP8 from the three alternatives in [CLAIM.md](CLAIM.md).
There is no randomized mathematical search. The complete finite domain is
all consecutive, same-source, nonunit additions at frame 1 in the existing
`full_frame_cleanup`, with no reordering. There are **4,298 adjacent pairs**,
including **1,015 transitions between different odd numerators**. Backward
cleanup has no eligible adjacent pair under this same-source restriction.

For magnitudes `a` then `b`, enumerate

```text
w *= 2^u; w += x; w *= 2^v,       -16 <= u,v <= 16
```

and require `(a*2^u + 1)*2^v = b`. Every primitive shift, source read,
target accumulation and boundary clear is charged. The complete positive
envelope restriction and cost argument are in [PROOF.md](PROOF.md).
Power-only routes and reset remain available. Ties retain the simpler
route/reset and do not extend a lifetime without a strict saving.

The stopping rule was completion of this domain and its exact replay.
[CERTIFICATE.json](CERTIFICATE.json) records every distinct pair, every
admissible one-read route, every selected block and its literal primitive
hash. [EXPECTED.json](EXPECTED.json) records the full-program result;
[INDEPENDENT.json](INDEPENDENT.json) records the separate exhaustive check.
This does not optimize arbitrary arithmetic circuits, signed transitions,
multiple source reads, unit macros, source permutations or other phases.
Excluded or unprofitable pairs are not impossibility results for those
larger classes.

## Provenance and remaining obligations

Exact base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
[SOURCES.json](SOURCES.json) pins all consumed inputs by decompressed payload
hash and identifies source commits. The selected source #626 is
`660de893d27bb7abd1d5b01b1640207528a5c851`; its K-triangle construction #622 is
`f69477f4f6d3c7eb1f740b166881bffed4ffa9f6`. Jeremy Kothe supplied #622/#623;
Chafik Boukhalfa supplied #626's owner allocation. The attributed local
emitter/auditor retains the preceding PR514/PR433 and cold-helper lineage;
the selected review credits DreamingOfClouds, Rohan Arun and eumemic's
retained #543 bit supplier.

Jeffrey Cox (@namredips),
[#739](https://github.com/CrocSwap/integer-mult-bounds/pull/739), established
power-of-two reuse and explicitly counted the incompatible odd-numerator
transitions. Its reviewed comparison head is
`abb9825202dba6f9bc95c7df8d12d86088fdff1a`. @ellipsi2's
[#722](https://github.com/CrocSwap/integer-mult-bounds/pull/722) supplied the
equal-magnitude predecessor. This package independently reconstructs that
power-only class and extends it with a positive source read; no pending code
is imported.

[#793](https://github.com/CrocSwap/integer-mult-bounds/pull/793), by
Varun Mittal, instead permutes commuting frame-zero compensation and uses
a quarter-grid route. [#769](https://github.com/CrocSwap/integer-mult-bounds/pull/769)
studies CK power-of-two ladders. #734/#723 optimize individual coefficients;
#751 changes backward fan-in; #755 expands equal-magnitude reuse to other
phases; #787 composes other lowerings. The reported savings are not asserted
additive with those constructions. See the final overlap check in the claim.

Clearing the coefficient stream moves from each macro to each shared-work
block. Production lowering-contract integration, revised per-call invoices,
global admission and the inherited all-size/compiler, common-label/mutable-
basis, whole-call hosting, precision/tape/recovery and analytic obligations
remain separate. The original program, selected certificate and `upstream/`
are unchanged. Finite exact replays are not a formal proof of the full
integer-multiplication theorem.

Contributor: **Ryan Haines (@Ryan-Haines)**, with substantial **OpenAI Codex**
assistance in research, implementation, checking and writing. New material
is under the repository's Apache-2.0 license. No predecessor's code is
relicensed or replaced. Completed environment/check details are in
[VALIDATION.md](VALIDATION.md).
