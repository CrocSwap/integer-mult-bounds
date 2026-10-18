# Faster exact quadratic-affine witness replay

**Verification tooling; no new kappa or new negative result.** This optional
adapter constructs all rows of Douglas Colkitt's twelve frozen quadratic-affine
rank witnesses using column-parallel integer arithmetic. It retains every
column, the diagonal, row order, binary elimination and source-hashed
certificate. It leaves the original checker and default commands unchanged.

The base is `66849e1475c930fd7732b1a0067ffee7e1e95f60`. At that base the selected
conditional result is #626 with #543, kappa `0.001635527380375392`; the historical
certificate's `2^-31` retained-kappa field is not the current frontier.
The selected audited #626 source is `660de893d27bb7abd1d5b01b1640207528a5c851`,
with #543 at `2065fe4f72a914d907f1046603f5a36f17018535`; neither is a new code
dependency of this historical replay.

## Reproduce

Python 3.11+ and its standard library are sufficient. From the repository root:

```sh
python3 -I -B research/quadratic-affine-packed/verify.py
```

Expected final line:

```text
PASS_QUADRATIC_AFFINE_DIFFERENTIAL all_frozen_rows_equal=true cases=12
```

This runs the new arithmetic and failure controls, all four unchanged original
test groups, then compares each of **14,662 complete rows** directly with the
original pairwise calculation. The declared minors contain **161,333,572 matrix
entries**, including their diagonals. It then performs the original elimination
and rational span checks and compares the entire serialized certificate with
the frozen source. The largest minor has 12,623 claimed independent rows and
12,687 columns. No row or column is sampled or removed.

For ordinary optimized replay without the deliberately costly differential
oracle:

```sh
python3 -I -B research/quadratic-affine-packed/replay.py
```

Expected: `PASS_QUADRATIC_AFFINE_PACKED cases=12`, with certificate SHA-256
`b55506bcf2334eebc07ce31078edb33282ff7d9bb57c40a9e4d5209d749dcd7f`,
`engine=packed`, and `compare_rows=false`. An optional `--out` must name a fresh
file. The default writes no certificate into the checkout. `--engine original`
runs the original audit through the same source and certificate guards.

Reproduce the complete-audit A/B measurement with:

```sh
python3 -I -B research/quadratic-affine-packed/benchmark.py \
  --pairs 3 --out /tmp/quadratic-affine-benchmark.json
```

The output path must not already exist. Each child uses identical frozen inputs
and starts a fresh interpreter. Order alternates original/packed, packed/original,
original/packed. Interpreter startup, imports, source checks, all twelve
witnesses, rational span checks, certificate comparison and output are included.
Every generated certificate must match the same bytes. Timing has no pass
threshold; OS caches are not flushed. This measures this historical audit,
not the selected construction or the whole repository suite. Raw observations
and environment details are retained in `BENCHMARK.json`.

On CPython 3.14.2 / macOS 26.3 arm64, the three alternating pairs measured
**73.411 seconds original versus 10.959 seconds packed** by median, an observed
**6.70x speedup** (85.1% less elapsed time). The six individual observations are
preserved; the packed times range from 9.666 to 11.063 seconds. This is a local
measurement, not a hardware-independent performance guarantee.

## Exact arithmetic argument

Write a sampled vector's coordinate as `w[j,k] = a[j,k] + i*b[j,k]`, where the
coordinate is zero or a Gaussian unit. For `N` columns and `D <= 32`, set
`B = 256`, `U = sum(B**j for j in range(N))`, and construct the signed integers

```text
R[k] = sum(a[j,k] * B**j for j in range(N))
I[k] = sum(b[j,k] * B**j for j in range(N)).
```

For query `v[k] = x[k] + i*y[k]`, compute

```text
P = D*U + sum(x[k]*R[k] + y[k]*I[k] for k in range(D))
Q = D*U + sum(x[k]*I[k] - y[k]*R[k] for k in range(D)).
```

These are integer polynomial identities: each final digit is `D` plus the real
or imaginary part of `conj(v) dot w[j]`. Each component has absolute value at
most `D`, so every digit lies in `[0, 2D]`, a subset of `[0, 64]`. Thus the final
base-256 digits are exactly those sums, with no carry between columns. The
signed intermediate integers may be negative; intermediate borrowing does not
change the final polynomial identity. No floating point, modular approximation
or probabilistic identity test is used.

Set `Z = (P xor D*U) or (Q xor D*U)`. Every digit of `Z` is below 128 and is zero
exactly for a zero Hermitian product. Adding `127*U` gives digits at most 254,
so again there is no carry. Its byte high bit is one exactly for a nonzero
digit. Therefore

```text
((128*U) xor ((Z + 127*U) and (128*U))) >> 7
```

has bit `8*j` set exactly for orthogonality. This uses carry-free addition;
the familiar subtract-ones zero-byte trick can misclassify adjacent lanes and
is an explicit negative control.

Finally compress the spaced bits. At a step with `k` a power of two, each
block's `k` low bits sit at positions `8*k*g`. Shifting by `7*k` places an odd
block directly above the preceding even block; OR and a mask keeping `2*k`
bits at positions `16*k*g` merges each pair. Induction doubles the compact
block length until all columns occupy consecutive bits. The final `N`-bit mask
discards padding. Adding bit `i` makes row `i` of **I plus the full
orthogonality relation**, exactly as in the original checker.

The original ordered GF(2) elimination and independence rejection are retained.
Its row digest is computed before elimination and includes the same byte
padding. The family construction, support counts, rational real span controls,
Gaussian coordinate basis checks, source verification, deficit inequalities and
receipt fields run unchanged in the original audit. `rank_witness` copies its
short validation/elimination/receipt routine with attribution; only row
construction changes. No successful rank result is cached.
`zero_lanes` is an internal decoder for the bounded digits returned by
`products`; arbitrary integers outside that contract are not supported.

## Coverage, negative controls and limits

The independent component oracle uses literal integer pairs, without the
original packed inner-product function. It covers all 125 vectors with three
coordinates in `{0, 1, i, -1, -i}` (15,625 products), all 60 Gaussian labels at
`t=2`, both signed extremes at `D=32`, and deterministic seed-92 samples for
every dimension 1 through 32. The fixed stopping rule is completion of these
tests and all twelve shipped witnesses; this is not a mathematical search.

Additional controls cover all 4,225 allowed offset-digit pairs at `D=32`,
sample sizes around byte and power-of-two boundaries through 257, nonmonotone
sample/row order, and original rejection messages for invalid or dependent
witnesses. Deliberate errors in conjugation, imaginary-part checking, diagonal
insertion and zero-byte detection are detected. The diagonal control preserves
the small example's rank but changes the row digest, demonstrating why rank
alone is insufficient. Changed source, fixture, certificate or upstream
manifest, disabled assertions, and preexisting output are rejected.

This preserves the existing negative result's exact scope: the twelve specified
full-orthogonality central matrices fail the positive-deficit condition. It
does not exclude other supported matrices, subfamilies, phase families or
compilers. It is not a formal proof of the full multiplication theorem. The
current construction's all-size/compiler/common-label/mutable-basis, hosting,
precision/tape/recovery and analytic assumptions remain untouched.

## Provenance and concurrent work

`SOURCES.json` pins all 37 predecessor files loaded or consumed by the replay,
including the complete imported local Python closure, frozen fixture, original
certificate and documentation, and the original upstream manifest and files.
The historical kernel first appears at
`d55bcd62ceb8f322bcf311a5a66e94c3ac7724f0`; upstream is
`adc7f1241b42e322a6451854ab7e4b4c146bf78a`. The adapter refuses source drift before
importing the audit. No predecessor file, `upstream/` file, selected record,
certificate or global Makefile is changed.

OS-random assignment seed **92** selected verification engineering. Three
candidates, the selection-time claim, time budget and overlap checks are in
`SELECTION.json`. The live local sprint claim is retained beside the checkout
and updated with the final PR link after submission.
No pinned coordination issue existed. The initial check covered 544 open PRs.
PR154 by eumemic identified `quadratic_affine.inner` as an unchanged costly
kernel; this contribution follows that useful profiling lead. PR154's parallel
scheduling, PR367's frame algebra, PR452's E8 replay, PR662's Clifford helper
check, PR667/672's interval engines, PR707's Gram prefixes, PR709's R420 geometry
cache, and PR721's archive streaming concern different mechanisms. No pending
implementation is imported or required.
The final refresh covered 565 open PRs through #746. New tooling #727 uses
owner-footprint masks and #736 skips cyclic-inverse zero row updates; neither
changes the quadratic-affine rank-witness replay.
The immediate pre-submission arrival check through #748 also found no overlap.

Local validation passed all 19 test groups, the complete direct row comparison,
all six timed complete audit replays, the selected source-inventory check and
whitespace validation. `VALIDATION.json` preserves commands and observations.
The repository-wide `make verify`, selected supplier cold replay, Lean and
remote Linux CI were not run for this isolated optional adapter. Their results
are not inferred from these local checks.

Original quadratic-affine families, witnesses, finite obstruction and audit:
**Douglas R. Colkitt**, with the original OpenAI Codex assistance disclosure.
New packed arithmetic, adapter, evidence and tests: **Curtis Dransfield
(@Curtis-D), with substantial OpenAI Codex assistance**, including a separate
scoped AI arithmetic reviewer and test author. AI review is not independent
human review. Apache-2.0; see the repository `LICENSE` and `NOTICE` for retained
attribution. The original work motivates its families with Dehaene and De Moor;
that background is not a new claim of this optimization.
