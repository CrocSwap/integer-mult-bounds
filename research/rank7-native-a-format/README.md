# A sufficient native format for the complete rank-seven A stage

Both pinned PR3076 providers admit an **84-bit common arithmetic capacity**
for 64-bit normalized input components, under the explicit exact-adapter
endpoint hypothesis. The common grid has seven fractional bits. Separate
forward and inverse-transpose layouts need 82 and 81 bits. The conservative
control constructed here needs 92 common bits.

The eight-bit improvement comes from cancellation between canonical Fourier
factors and a specified pair-first order for C numerators. This extends
[PR3086](https://github.com/CrocSwap/integer-mult-bounds/pull/3086)'s single
boundary to all ordinary A-stage conversions. [PROOF.md](PROOF.md) states
exactly which arithmetic values are covered and proves the uniform formulas.
These are sufficient bounds, not sharp minimum widths.

## Scope and evidence

Each provider and orientation covers 5,964 prelude scalars and 72 prelude
warps, followed by 4,028 A scalars, 24 A warps and 1,020 climbs. Exact Fraction
rows and a separately written fixed-denominator integer engine agree on every
changed normalized row. The replay validates all 1,124 canonical frames in
each word. Thirty-six exact local controls cover pair-first C arithmetic at
ranks 1 through 9, both signs and both directions.

[RESULT.json](RESULT.json) preserves deterministic hashes, capacity witnesses,
all three comparison bounds and the inherited fresh complete emitter checks.
The native producer is reused as a pinned source generator; the new format
and integer engines do not import its propagation functions. This is internal
automated checking, not independent human or proof-kernel verification.

The arithmetic contract covers scalar endpoints and exact ADD increments,
canonical frame/warp endpoints, and the specified native C numerator partials.
The adapter endpoints and Gaussian-monomial interpretation are hypotheses.
Residual adapter interiors, scalar coefficient-construction microstates,
recursive approximation, centres/later phases, ownership, clean stock,
routing and the complete physical invoice remain open. The dual uses
conjugated frames. No new kappa, supplier admission or selected-frontier
change is claimed.

## Reproduce

Python 3.12, standard library only. From the repository root, set RUN to a fresh
external session-owned directory:

```sh
mkdir -p "$RUN/tmp"
TMPDIR="$RUN/tmp" uv run --python 3.12 --no-project python -W error -B \
  research/rank7-native-a-format/verify.py --work "$RUN/replay" > "$RUN/result.json"
cmp "$RUN/result.json" research/rank7-native-a-format/RESULT.json
TMPDIR="$RUN/tmp" uv run --python 3.12 --no-project python -O -W error -B \
  research/rank7-native-a-format/test_format.py
TMPDIR="$RUN/tmp" uv run --python 3.12 --no-project python -B \
  scripts/research_package.py --package research/rank7-native-a-format
```

Without `--work`, verification removes its temporary outputs beneath TMPDIR.
The registered replay runs both the verifier and optimized behavioral controls.
[SOURCES.json](SOURCES.json) pins baseline provenance; [VENDOR.json](VENDOR.json)
pins every reused source byte. Runtime needs no Git or network access.
[CHECKS.json](CHECKS.json) records verification and its limits.

## Open next questions

Can the exact adapter endpoint hypothesis be supplied with a paid fixed-point
implementation? Start with one actual residual adapter and its dirty-state
range in these providers. The current capacity result leaves those interiors
and their cost unbounded.

Can scalar coefficient construction fit this capacity, or does it need more
working bits? Start with the actual `7/8`, `3/8`, `3/2` and `-7/4` ADDs and bind
one materialized lowering from PR3078 to this source grid. Increment endpoints
alone do not price or bound that construction's microstates.

Can the consumer release guards after A? Start with its centre conversion and
the three fractional bits retained by the normalized A exit. Later physical
conversions, approximation, ownership and complete caller costs are blockers.
This package supports narrowing to these obligations rather than another
lowering census.

## Credit

Nick Petalas contributed this conditional format bound and replay. The source
lineage includes PR3086/3083/3084, PR3076/3078/3060/3056, dcharb78/PR3042,
Jeremy Kothe/PR3015, Marius-Paul Dumitrean/PR2979, Cinna Davis/PR2226,
DLamdata's exact Clifford kernel, icekylinx, Tekalign and the retained native,
geometry and owner contributors. Frozen credit and license notices are
unchanged. No priority is claimed for generic Fourier coefficient identities.
New work is Apache-2.0. Development used substantial automated assistance;
no independent human review is claimed.
