# Batch the selected JP8 compensation by source

**Research construction: 80,150 fewer forward and 81,464 fewer backward
real-component primitives; no new kappa.**

The selected #626 JP8 program prepares coefficients separately for 8,800
frame-zero compensation additions. Their sources and destinations are
disjoint, so every addition in this panel commutes. Reordering by source
lets one private stream supply every requested coefficient magnitude to
all its destinations before clearing. The backward orientation is grouped
separately after transposition.

| Complete local scalar program | Selected bound | Replacement bound | Saved |
|---|---:|---:|---:|
| Forward | 257,232 | 177,082 | 80,150 |
| Backward / inverse-transpose | 257,280 | 175,816 | 81,464 |

Every source access, signed accumulation, doubling/halving and initial/final
clear is charged. The implementation uses the existing single coefficient
work stream. Exact full-local prefix bounds remain **64 and 101 bits**,
within the inherited 192-bit allowance. These are finite operation counts,
not wall-clock speedups. Helpers, recursive children and their paid profile
remain unchanged.

## Reproduce

From the repository root at the pinned base plus this package, Python 3.11+
and its standard library are sufficient:

```sh
python3 -I -B research/jp8-compensation-batching/verify.py
```

Expected final line:

```text
PASS_JP8_COMPENSATION_BATCHING additions=8800 saved=80150,81464 columns=716+9 controls=10
```

The command checks source pins and the selected SPEC bindings, reconstructs
both literal primitive panels, reproduces the committed candidate and
receipt, and executes both complete scalar projections on all **716 native
plus nine arbitrary private input columns**. It verifies both full shear
endpoints, dirty-helper restoration, private clearing, exact costs and
the unchanged prefix bounds. Ten controls include wrong signs, omitted
updates, missing clears, source writes, phase crossing and an unchanged
endpoint with excessive work-register growth.

The separate integer/dyadic implementation imports no construction code:

```sh
python3 -I -B research/jp8-compensation-batching/independent.py
```

It prints `PASS_INDEPENDENT_INTEGER_DYADIC_COMPENSATION_CHECK` in its JSON
receipt, verifies both panel matrices on **717 columns**, counts every
primitive, measures exact isolated-panel prefixes, and rejects twelve
additional controls. Its prefix measurement starts with independent panel
inputs; the full-program prefix check is in `verify.py`. The preserved
receipt is [INDEPENDENT.json](INDEPENDENT.json).

For the native scalar/frame/wrapper replay, choose a new scratch directory:

```sh
python3 -I -B research/jp8-compensation-batching/native_replay.py --output /tmp/jp8-native-batching
```

Expected final line:
`PASS_UNCHANGED_NATIVE_COMPENSATION_REPLAY columns=716 controls=25`.
The unchanged inherited emitter and auditor check the forward-reordered
canonical word and its dual. The primitive backward panel uses a different
source permutation, checked independently above. This native replay checks
the legal macro reordering; it does not integrate the new primitive lowering
or admit a changed global invoice. Its semantic receipt is [NATIVE.json](NATIVE.json).

Use `verify.py --write /path/to/new-output` to regenerate the candidate and
receipt explicitly. Normal verification reads files without changing them.
Compressed inherited artifacts are pinned by decompressed payload, so
recompression does not invalidate mathematical equality.

## Evidence and bounded search

- [PROOF.md](PROOF.md): commutation, inverse-transpose convention, one-stream
  substitution, complete cost and prefix argument.
- [CANDIDATE.json](CANDIDATE.json): executable forward/backward primitive panels.
- [EXPECTED.json](EXPECTED.json): every source group, its original gate indices,
  route, primitive interval and complete local recount.
- [SOURCES.json](SOURCES.json): exact source pins, including the selected SPEC.
- [CLAIM.md](CLAIM.md): assignment seed, alternatives, scope and overlap checks.
- [NOTICE.md](NOTICE.md): predecessor credit and AI-assistance disclosure.
- [VALIDATION.md](VALIDATION.md): completed checks and unrun suites.

OS-random assignment seed **27** selected the complex track and, by parity,
JP8. There is no randomized mathematical search. For each of 266 forward
and 112 backward source groups, breadth-first search uses states
`(k, visited magnitudes)`, with `-4 <= k <= 4` and coefficient `k/4`.
It stops at the first shortest route visiting every requested magnitude;
all 15 nonempty magnitude subsets are also recorded. The permitted steps
are signed unit source reads, doubling and exact halving within the grid.
Every requested target update and both boundary clears are added to that
cost. The direct lower bound for the occurring sets is in the proof.
This is complete coverage of this finite route class, not an optimum over
general arithmetic circuits, other grids or cross-source reuse.

## Provenance, differences from concurrent work, and limits

Exact base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
Selected #626 source: `660de893d27bb7abd1d5b01b1640207528a5c851`;
#622 construction: `f69477f4f6d3c7eb1f740b166881bffed4ffa9f6`.
The retained #543 bit supplier and full accepted source lineage are
identified by the unchanged selected record. Its conditional kappa remains
**0.001635527380375392**.

Concurrent [#722](https://github.com/CrocSwap/integer-mult-bounds/pull/722),
[#739](https://github.com/CrocSwap/integer-mult-bounds/pull/739),
[#755](https://github.com/CrocSwap/integer-mult-bounds/pull/755) and
[#769](https://github.com/CrocSwap/integer-mult-bounds/pull/769) are credited
for sharing coefficient work within the existing update order. This package
changes the commuting compensation order to share across targets. It also
uses a signed bounded route for the `3/4` coefficient.
[#749](https://github.com/CrocSwap/integer-mult-bounds/pull/749) instead
changes and restores the target basis, reducing the number of compensation
additions. No pending implementation is imported, and these savings are
not asserted additive with any of those contributions.

The final overlap scan also inspected
[#787](https://github.com/CrocSwap/integer-mult-bounds/pull/787), which
composes individual-coefficient lowering with order-preserving cleanup
sharing, and [#786](https://github.com/CrocSwap/integer-mult-bounds/pull/786),
which factors center coefficients and audits its extra macro costs. Neither
performs this compensation permutation. Their circuit savings are not
combined with this package.

The private-work clearing boundary moves from each original scalar macro
to each source group. The native word, production emitter, selected
certificate and global admission remain unchanged. Integrating this new
lowering contract and refreshing global invoices/admission are separate
obligations. All inherited all-size/compiler, common-label/mutable-basis,
whole-call hosting, precision/tape/recovery, bit-supplier and analytic
assumptions remain. This finite result is not a formal proof of the full
integer-multiplication theorem.
