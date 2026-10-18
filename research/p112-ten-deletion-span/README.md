# A ten-deletion P112 bound removes one more beta shape

For any two six-dimensional P112 label spaces, all directions that reach
residual binary rank six after at most ten separately chosen line deletions
span at most **four** dimensions. The bound holds over every characteristic-zero
field and also applies to one common deletion set. Four is attained with
separate sets; common-set sharpness is not claimed.

This excludes `2,4,5,6^6` in TWOSIDE's `(b,t)=(5,4)` cell. Choose quotient
basis weights `2,4,5,6`, whose support cap is 42, below the code distance 53.
The five remaining weight-six pieces would supply five independent directions
inside the theorem's span of at most four. The eight-deletion predecessor
does not certify this cover. Its three surviving shapes become two:
`2,5^3,6^5` and `3,4^2,6^6`.

This is one additional exclusion in the P112 decoder-floor argument. It does
not settle the cell, full C5, `C(P112)>=64`, supplier admission or kappa.
The selected conditional kappa remains `0.001672660197076918`.

## Evidence

[PROOF.md](PROOF.md) gives the complete-direction argument, exact census and
quotient-basis application. [RESULT.json](RESULT.json) retains all 159 orbit
rows for both the eight-deletion control and the ten-deletion theorem, with
literal sharp witnesses and an exact weight-boundary receipt.

The replay covers all 788,035 annihilators, 776,805 nonempty flat masks and
123,511,995 representative pairs per budget. Weyl-chamber coverage checks
all 28 rank-six parabolics and all eight normal rays; two qualifying rays
generate 1,200 projective directions. The seventy-line support cutoff leaves
120 root and 128 D7 directions. The full census gives span four and at most
ten directions. Counting directions would not prove this span result.

All twelve orbit generators receive a new signed-Gram check, which certifies
that their action preserves rational span. Exact integer elimination is checked
against Python Fraction arithmetic and a determinant-minus-two control. The
dual-code deletion oracle has 45,056 exhaustive comparisons; Python independently
checks the positive cuts. [CHECKS.json](CHECKS.json) records local execution and
review limits. [ENGINEERING.md](ENGINEERING.md) records bounds and diagnostics.

## Reproduce

Requires Python 3.12 or later and a C++17 compiler. No third-party Python packages,
Git or network are needed by the direct mathematical replay when the two
declared data files are present. From the repository root:

```sh
RUN="$HOME/.cache/integer-mult-bounds-runs/p112-ten-$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$RUN/tmp"
TMPDIR="$RUN/tmp" PYTHONPYCACHEPREFIX="$RUN/bytecode" \
  uv run --python 3.12 --no-project python -W error -B \
  research/p112-ten-deletion-span/verify.py --work "$RUN/replay"
TMPDIR="$RUN/tmp" PYTHONPYCACHEPREFIX="$RUN/test-bytecode" \
  uv run --python 3.12 --no-project python -O -W error -B \
  research/p112-ten-deletion-span/test_verify.py
TMPDIR="$RUN/tmp" uv run --python 3.12 --no-project python -B \
  scripts/research_package.py --package research/p112-ten-deletion-span
```

Without `--work`, temporary replay files are removed beneath `TMPDIR`.
An explicit work directory must be new and outside the checkout; it preserves
diagnostics. `--output NEW_PATH` emits a fresh receipt instead of comparing the
committed one. The generic metadata check additionally uses Git provenance.
[SOURCES.json](SOURCES.json) and [UPSTREAM.json](UPSTREAM.json) pin the inputs,
source-import ancestor and byte-identical predecessor excerpts.

## Open next questions

Can the union of two actual small-piece supports give a stronger common-set
rank-six theorem? The remaining `3,4^2,6^6` shape has a twelve-line cover from
weights three and four; `2,5^3,6^5` has a fourteen-line cover from weights two
and five. First pin those pieces and their common deletion set. These unions
need not lie in a five-flat. A root-only, separate-twelve-deletion probe
already gives five independent directions, so an unstructured span-four
extension is false. That probe is not a complete twelve-deletion census or
a counterexample to the structured common-set question.

Can the span-four theorem be proved from a smaller geometric classification?
Start with the retained four-direction witness and the signed-Gram action.
A proof would reduce dependence on the all-pair computation; no such reduction
is claimed here. Structured questions are in [TASK.json](TASK.json).

## Credit

Nick Petalas contributed the ten-deletion span theorem, completeness and symmetry
checks, and the new beta application. DreamingOfClouds's PR3154 supplies TWOSIDE's
reduction, weight filters and fundamental-circuit lineage. PR3161 supplies the
eight-deletion predecessor, flat/orbit enumeration, dual-code oracle and root/label
reconstruction reused here. The retained E8, P112 and decoder contributors keep
their credit. Exact original heads and paths are in UPSTREAM.json.

Predecessor sources are unchanged. The byte-identical excerpts retain their notice
and Apache-2.0 license. New work is Apache-2.0. Development and internal read-only
checking used substantial automated assistance. No independent human or
proof-kernel review is claimed.
