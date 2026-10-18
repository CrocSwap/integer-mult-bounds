# Aligned bit circuits for the rank-seven ADD layer

This package supplies explicit reversible Boolean circuits for an aligned
fixed-width ADD layer and a source-bound comparison of PR3060 with PR3076.
At 64 bits, PR3076's contractions plus signed-power lowering save **24,432
Toffolis and 24,528 CNOTs per word and orientation** against the parent's
binary-power lowering. This is a conditional local compiler result, not a
physical supplier or kappa improvement.

Both bit policies are constructed here. The binary policy is a comparison
control, not an existing or optimal upstream physical backend.

| Forward ADD layer, both real components | Shifted ADD circuits | Toffolis | CNOTs |
|---|---:|---:|---:|
| PR3060, binary powers | 32,682 | 8,164,884 | 8,197,566 |
| PR3060, signed powers | 32,674 | 8,162,708 | 8,195,382 |
| PR3076, signed powers | 32,586 | 8,140,452 | 8,173,038 |

Both providers give these counts. Backward counts add 16 shifted ADDs,
4,000 Toffolis and 4,016 CNOTs to each row, so the savings agree.
For every supported width `5 <= W <= 256`, the combined saving is
`384W-144` Toffolis and `384W-48` CNOTs. With signed powers on both sides,
the contractions alone save `352W-272` and `352W-184` respectively.

The same source comparison answers PR3076's previous materialization handoff.
Under PR3078's exact real-arithmetic recipes, the complete scalar count falls
from 83,430 to **83,394** unit instructions under either digit walk, or from
93,190 to 93,158 under the scratch policy. Each recipe is separately checked
on arbitrary target/source columns. The earlier conservative bound reduction
of 340 is not a materialized instruction saving of 340.

## Circuit and caller boundary

For a reduced dyadic coefficient `q=n/d`, the source and target are W-bit
signed integers at a common binary point. The source integer must be divisible
by d. The circuit implements `T += q*S mod 2^W` for every such source and
arbitrary target, preserving every source bit and restoring all W-1 initially
zero carry bits. If the signed endpoint fits, it also realizes the exact
signed ADD. These carries are owned clean space, not arbitrary dirty helpers.

A generic W-bit add or subtract uses `4W-6` Toffolis and `4W-5` CNOTs for W>=2.
Shifted source bits and sign extension are read-only controls. Left shifts
permit pruning low unchanged target bits. Signed powers such as
`7/4 = -1/4 + 2` can save an adder. Intermediate arithmetic is modular, so
there are **zero temporary arithmetic guard bits** on source or target.
Permanent source alignment and endpoint capacity are still required. The
[proof](PROOF.md) explains carry erasure, reversed subtraction, signed source
controls, the exact gate counts and the scope of this statement.

The actual native caller's permanent formats, dirty-state ranges and per-cut
alignment remain unresolved. The circuit does not prove physical routing or
clean-carry backing. SCALE/COPY/CLEAR, frames, climbs, centres, 240 native warp
events, ordered helper widths and 91 private buffers remain charged in the
source; their physical implementation is not supplied here. Every non-ADD
native event is unchanged, and the recursive paid profile is unchanged.
No full supplier admission, outer release, runtime gain or new kappa is claimed.

## Evidence and reproduction

[RESULT.json](RESULT.json) records four fresh native transport/emitter pairs,
both orientations, actual program hashes, coefficient histograms, exact
Boolean tariffs and unit-recipe counts. Explicit W=64 circuits are serialized
and read back before aggregation. A bit-packed interpreter checks **311,016
exhaustive cases across templates**: all aligned signed sources and arbitrary
modular targets for the actual coefficient alphabet through width six, plus
ordinary addition/subtraction through width eight. Each template's cases are
distinct; different templates reuse inputs. The all-width claim uses the
written induction, not exhaustive W=64 execution.

Eleven behavioral groups cover signed overflow versus modular wrap, alignment,
negative sources, all supported widths, an independent scalar-bit interpreter,
wrong signs, missing gates, source writes, dirty carries, malformed inputs,
source-byte changes and occupied-output preservation. Contracts remain active
under optimized Python. The inherited native compiler is reused, not an
independent implementation.

Python 3.12 is the registered environment; the system Python 3.9 is unsupported.
With `RUN` a session-owned directory outside the checkout:

```sh
mkdir -p "$RUN/tmp"
TMPDIR="$RUN/tmp" uv run --python 3.12 --no-project python -W error -B \
  research/rank7-aligned-bit-adders/verify.py --work "$RUN/bit-replay" \
  > "$RUN/result.json"
cmp "$RUN/result.json" research/rank7-aligned-bit-adders/RESULT.json
TMPDIR="$RUN/tmp" uv run --python 3.12 --no-project python -W error -B \
  research/rank7-aligned-bit-adders/test_bits.py
TMPDIR="$RUN/tmp" uv run --python 3.12 --no-project python -B \
  scripts/research_package.py --package research/rank7-aligned-bit-adders
```

`--work` refuses existing paths and preserves diagnostics. Without it, the
registered replay removes its private outputs under `TMPDIR`. No dependency
installation or network access is required by the verifier. Program hashes
describe canonical parsed JSON, not gzip containers. `VENDOR.json` binds all
17 frozen input files to exact Git source blobs and SHA256s; `SOURCES.json`
also records historical catalogue/selected provenance. `ENGINEERING.md`
records implementation and verification limits.

## Open next questions

Can one actual caller meet every alignment and signed-endpoint promise at its
paid permanent widths? Start with its half- and quarter-ADD source grids and
the exact emitted programs produced by the replay. A source-bound finite
format and dirty-state range ledger are the blockers.

Can that caller retain the Boolean saving after routing source/sign controls
and backing the W-1 clean carries? Place and price one half-ADD template in
its actual ownership contract first. No routing or clean-space tariff is
assumed here. Structured questions are in [TASK.json](TASK.json).

## Credit

Nick Petalas contributed this conditional bit-layer implementation and
source-bound comparison. The generic ripple adder and signed-binary identities
are elementary, with no algorithmic priority claim. PR3076 supplied the exact
commuting contractions; PR3078 supplied the unit recipes and the format/access
handoff; PR3060/3056 supplied the restore changes. Credit dcharb78/PR3042,
Jeremy Kothe/PR3015, Marius-Paul Dumitrean/PR2979, Cinna Davis/PR2226,
icekylinx, Tekalign and the retained native/emitter/geometry/owner lineage.
Frozen predecessor code and notices are unchanged in `vendor/parent/`.
New work is Apache-2.0. Development used substantial automated assistance;
no independent human or formal-kernel review is claimed.
