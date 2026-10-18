# Dirty cyclic inverse with source reuse

**Status: research construction. No new kappa.**

This is a follow-up to [PR846](https://github.com/CrocSwap/integer-mult-bounds/pull/846).
It implements an arbitrary-stride inverse for a **constant** stable complex
coefficient. It adds the inverse to a dirty target and restores the source
exactly, with no extra data array inside the leaf. The implementation also
composes the leaves into the certified kernels from PR628, with the same
`ceil(log2(r-1))` borrowed arrays as its original dirty dispatcher.

The source prefix holds the recursive closure result temporarily. Two
opposite closure calls restore that prefix. Each closure input is the
disjoint source tail. The resulting recurrence has two children and total
weighted length at most `6L`. Coefficients at each level have only two
possible exponents, so they can be prepared in scalar storage.

Reversible block swaps use the existing dirty target as a carrier. A
causal conjugation expands the closure values without a clean queue.
The construction uses `O(L)` rounded scalar operations, `O(L)` data-record
movement on **two tapes**, and `O(1)` clean arithmetic registers per leaf.
The leaf index stack uses `O(log^2 L)` bits. The full kernel retains the original
logarithmic number of borrowed arrays and routes all of them over the same
two tapes. Every swap, child, inverse call, and head return is charged.

## Reproduce

Use standard-library Python 3.11 or later from any working directory:

```sh
python3 -I -O -B research/dirty-stride-source-reuse/verify.py
python3 -I -O -B research/dirty-stride-source-reuse/test_package.py
```

The first command compares every field with `EXPECTED.json`. It checks
8,256 stride geometries, 3,456 rounded generic leaves, and 80 original
kernel executions. All 3,456 leaf and 80 kernel executions have nonzero
rounding error.
The inputs, targets, and borrowed arrays all include an odd lowest working
bit. No clean low-bit storage is reserved. The second command checks
standalone use, exact regeneration, source and certificate corruption, and
faults in the arithmetic word. It runs two complete replays; the scoped CI
job uses this command on Python 3.11 and 3.14.

Expected primary marker:

```text
PASS_DIRTY_STRIDE_SOURCE_REUSE geometry=8256 generic=3456 kernels=80 controls=12
```

To write a new receipt, use an output path that does not exist:

```sh
python3 -I -O -B research/dirty-stride-source-reuse/verify.py --write /tmp/dirty-stride-replay.json
```

`PROOF.md` gives the all-length restoration, rounding, preparation, memory,
arithmetic, and tape arguments. `EXPECTED.json` is finite supporting evidence.
`VALIDATION.json` records the checks actually run. The exact-rational Python
implementation does not establish a measured fast-arithmetic runtime.

## Evidence and scope

- All lengths `1..128` and all residues `0..L-1` compare the return-time
  formula with explicit chain elimination: 8,256 cases and 29,642 levels.
- 2,322 rounded powers check the norm and the uniform error bound through
  exponent 129. This includes 2,178 cases with nonzero preparation error.
- Generic leaves cover lengths `1..24`, every integer stride in `[-L,L)`,
  both allowed output shifts, and margins `1/2`, `1/16`, and `1/4096`.
  A separate finite geometric sum
  supplies the exact result. All source restoration and inverse checks pass.
- All ten pinned PR628 fixtures through radix 16 run at both unit gauges,
  with zero, positive, and negative strides. A dense rational solve of the
  expanded polynomial is the numerical oracle. Scaled factor perturbation,
  128-bit target accuracy, the full leaf count, dirty restoration, and exact
  inverse cancellation are checked.
- An indexed bank rejects iteration and slicing inside the solver. The
  arithmetic and data-access counters check the written complete recurrence.
  The tape counter uses two physical heads, including when the kernel has
  several borrowed arrays. It includes validation, transport, reads, writes,
  restoration, and returns to the tape origins.

For one leaf the sufficient error is `64(B+1) 2^-W / beta^5`, with admission
`48(K+1) 2^-W <= beta^3`. The complete kernel uses the conservative PR628
perturbation argument with the new leaf constant. It does not claim the
stronger precision results of PR877 or PR905.

The proof gives loose bounds of `1280L` counted products/divisions and
`4096L` data-record moves per leaf. The complete kernel pays
`O(NL) M(W_total) + O(N(h+2)L W_total)`, plus coefficient/phase preparation
and descriptor access, where `N<=4(r-1)^2` and `h=ceil(log2(r-1))`.
These are proved operation bounds, not measured runtime speedups.

The rounded increment can depend on the initial target. The package has
a concrete length-three example. Inverse calls therefore reverse the
complete word; changing signs in the original order is not sufficient.
Variable site phases, complete-transform accounting, physical supplier
realization, and the multiplication reduction remain open.

## Pins, selection, and credit

Base: `47481c89fd30a43f8f882eb4b391e89c29273fd0`.
The selected conditional result at that base is PR890,
`kappa=1661957774647029/1000000000000000000`. At submission refresh, main
`407d52ff15b2217b6e22bce44728b4c3907b6515` selects PR942 at
`kappa=1661960547713947/1000000000000000000`. This package changes neither
certificate. `CLAIM.json` records both contexts.

The exact source heads, paths, Git blobs, and SHA256 values are in
`SOURCE.json`. Retained files are unchanged; some are context documents,
not standalone copies of their original packages. The baseline PR846
replay passed separately at head `4bdb3e755ea7118170a7a34764df955880dec282`.
No selected frontier or file under `upstream/` is changed.

OS assignment seed **36** selected the complex supplier track. The user
then selected the remaining dirty-array solver in PR846 explicitly.
`CLAIM.json` records the three scoped candidates, the chosen mechanism,
the local claim, and the overlap check. This is a construction, not a search
for a better kappa or an optimal algorithm.

Credit Rohan Guliani for PR846, Chafik Boukhalfa for PR628, Charles Bethin
for PR764, and the original PR621 and kernel lineage. The later PR862,
PR877, PR905, PR929, and concurrent PR951 results have different precision,
scalar storage, or neighboring-stride contracts. PR951 has two grouped
calls and no dirty connector, with larger clean scalar workspace. This
contribution makes no claim to improve that arithmetic count or its cubic
precision. PR977 improves PR846 to cubic precision and removes its length
admission, with the original clean scratch model. Its precision result is
not imported here. See `NOTICE.md` for attribution and the AI assistance
disclosure.
