# Exact formats for the rank-seven scalar coefficient stream

This package closes the formal scalar-grid part of
[PR3080's format handoff](https://github.com/CrocSwap/integer-mult-bounds/pull/3080).
It derives intermediate ranges from both literal PR3076 emitted programs,
including the dual orientation and arbitrary dirty input columns. It does not
establish the ranges of intervening native transforms or a new kappa.

For independent signed 64-bit input atoms, the least common dyadic grid and
least signed endpoint width at that grid in the free-warp coefficient model are:

| Orientation, either provider | Fractional guard bits | Maximum row l1 norm | Common width |
|---|---:|---:|---:|
| Forward | 4 | 302 | 77 |
| Dual | 5 | 169 | 77 |

The initial input integers are encoded with respectively four or five trailing
zero bits. Every formal scalar endpoint then fits in 77 signed bits. Every
encoded ADD source has the divisibility needed by PR3080's aligned bit circuit.
The maxima include every scalar prefix. Each orientation has 17,635 changed-row
observations; there are 16,205 forward ADDs and 16,213 dual ADDs, per provider
and complex-component template.

The certificate includes a basis atom that makes one fewer fractional bit
fail and sign assignments that make one fewer endpoint bit fail. It also
executes PR3080's literal 77-bit ADD circuit at the two extremal ADD occurrences
per stream. Sharpness is in the independent formal-atom model. Actual monomial
operators can identify atoms, so physical sharpness does not follow.

## What changed

The retained compiler checks the final scalar operator and zero returns.
This package adds an independently implemented exact prefix ledger, denominator
and signed-range proofs, attaining fixtures and explicit ADD-alignment checks.
Native stream generation is reused with exact source pins.
The separate [integer checker](check_integer.py) uses no Fraction arithmetic
or production row helpers. All four streams agree on every summary field and
the complete prefix-ledger digest; rerunning it with one fewer grid bit fails
at an actual fractional operation.

A cancellation-blind control implemented here needs 44 fractional bits and
195 total bits forward, and 45 fractional bits and 202 total bits dual.
Collecting equal reduced-word coefficients lowers those sufficient bounds to
four/five fractional bits and 77 total bits. A third policy using exact signed
endpoints also gives 77 bits, tying the symmetric row-norm width at this input
precision. The control is a comparison analysis, not an existing physical
backend or a claim that upstream allocates 195/202 bits. No program is changed.

## Boundary and remaining costs

The object is the emitted compiler's scalar coefficient stream over atoms
`(original input, reduced warp word)`. A warp permutes these atoms; scalar
gates act by exact rational linear operations. All 632 live inputs start
independent and dirty; centre and private zero streams follow their literal
allocation and clear events. Both final operators and all zero returns pass.

Like the compiler's scalar identity check, this model does not apply the
native transformations at 978 adapter, 390 residual-adapter, 3,503 climb and
eight centre events per stream. The receipt lists those omissions. A physical
caller needs a separate interpretation showing that intervening native
operations preserve this atom grid and box, or a ledger of their additional
denominator/range losses. Their internal arithmetic is not bounded here.
See [the proof and exact contract](PROOF.md).

PR3081's guarded local half-ADD caller is complementary. SCALE/COPY/CLEAR
implementation, frame conversions, 240 native warp events, source routing,
clean carry backing, owner stock and precision/storage costs remain additional.
The paid recursive profile, supplier admission, outer release, selected result
and kappa are unchanged.

## Evidence and reproduction

[RESULT.json](RESULT.json) records source/program hashes, complete prefix
ledger digests, exact extrema, attaining rows, native omissions, comparison
bounds and literal bit-ADD outputs. Its ledger digest includes each changed
row and each ADD increment in order. Disposable native exports are regenerated
outside the checkout. All 19 frozen sources have exact Git blobs and SHA256s
in [VENDOR.json](VENDOR.json); historical provenance is in [SOURCES.json](SOURCES.json).

Python 3.12, standard library only. From the repository root, set `RUN` to a
fresh session-owned directory outside the checkout:

```sh
mkdir -p "$RUN/tmp"
TMPDIR="$RUN/tmp" uv run --python 3.12 --no-project python -W error -B \
  research/rank7-coefficient-grid/verify.py --work "$RUN/replay" \
  > "$RUN/result.json"
cmp "$RUN/result.json" research/rank7-coefficient-grid/RESULT.json
TMPDIR="$RUN/tmp" uv run --python 3.12 --no-project python -O -W error -B \
  research/rank7-coefficient-grid/test_rows.py
TMPDIR="$RUN/tmp" uv run --python 3.12 --no-project python -B \
  scripts/research_package.py --package research/rank7-coefficient-grid
```

`--work` refuses an existing path. Without it, registered replay removes its
outputs beneath `TMPDIR`. The verifier authenticates frozen source bytes before
native execution, checks both complete native emitter receipts and reconstructs
the providers from pinned words and declared edits. Thirteen behavioral groups
include exhaustive small signed boxes, cancellation, warp order, zero returns,
intermediate fractional excursions, wrong signs, malformed events, source
corruption and actual receipt witnesses. Optimized Python retains the checks.

## Open next questions

Can the actual native caller interpret this formal grid without extra losses?
Start with one emitted climb and its adjacent half-ADD, including both dirty
operands. Prove the coefficient-stream/native commuting relation and record
every new denominator and magnitude factor. That interpretation is the blocker.

Can the physical caller retain the bit saving after permanent guards, routing
and carry backing are priced? Start with a literal extremal ADD from the
receipt, charge all 76 clean carry bits and its actual placement, then include
non-ADD operations. A complete physical storage and execution invoice is
missing. Structured questions are in [TASK.json](TASK.json).

## Credit

Nick Petalas contributed this prefix-format certificate. PR3080 supplied the
aligned bit layer and format handoff; PR3076 the contractions; PR3078 the
coefficient-recipe and access boundary; PR3060/3056 the restore changes.
Credit dcharb78/PR3042, Jeremy Kothe/PR3015, Marius-Paul Dumitrean/PR2979,
Cinna Davis/PR2226, icekylinx, Tekalign and the retained native, emitter,
geometry and owner lineage. Frozen code and notices remain unchanged in
`vendor/`. New work is Apache-2.0. Development used substantial automated
assistance; no independent human or formal-kernel review is claimed.
