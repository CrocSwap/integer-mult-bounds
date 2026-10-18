# P112 rank-six directions close one beta cell

For any two six-dimensional P112 label flats, directions that reach residual
binary rank six after at most eight separately chosen line deletions number
at most **three**. The bound also applies to one common deletion set and to
characteristic-zero coefficients.

Together with the pinned fundamental-circuit lemma, this excludes all four
weight shapes listed for TWOSIDE's `(b,t)=(5,3)` beta residue. The newly closed
shape is `4,5,6^6`: choose quotient-basis weights `4,6,6`, whose support fits
two six-flats plus eight lines. It requires five independent directions where
at most three are possible. The other three shapes already follow from the
predecessor's separate finite results; the stale four-shape list is not a
claim that all four were previously open.

This is a scoped improvement to the P112 decoder-floor proof. It does not
settle full C5, `C(P112)>=64`, other cells, supplier admission or kappa. The
selected conditional kappa stays `0.001672660197076918`.

## Evidence

[PROOF.md](PROOF.md) states the hypotheses, complete-direction argument,
dual-code deletion lemma and mixed-rank transfer. The new C++ implementation
checks all 788,035 annihilators, 776,805 distinct nonempty flat masks, 159
orbits and 123,511,995 representative pairs. The rank-six eight-deletion
maximum is three, with a literal independent three-direction witness.
Its deletion sets are separate; common-set sharpness is not claimed.

[RESULT.json](RESULT.json) retains every orbit row, positive certificates and
source hashes. The rank-six four-deletion control independently reproduces
maximum one. All 36,864 small oracle comparisons use literal exhaustive
deletions. Python checks the positive certificates by a separate XOR-span
calculation. [CHECKS.json](CHECKS.json) records execution and review limits.

## Reproduce

Requires Python 3.12 or later and a C++17 compiler. No third-party Python
packages, Git or network are needed by the direct mathematical replay.
Run from the repository root with the two declared predecessor inputs present:

```sh
RUN="$HOME/.cache/integer-mult-bounds-runs/p112-mixed-$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$RUN/tmp"
TMPDIR="$RUN/tmp" PYTHONPYCACHEPREFIX="$RUN/bytecode" \
  uv run --python 3.12 --no-project python -W error -B \
  research/p112-mixed-rank-reduction/verify.py --work "$RUN/replay"
TMPDIR="$RUN/tmp" PYTHONPYCACHEPREFIX="$RUN/test-bytecode" \
  uv run --python 3.12 --no-project python -O -W error -B \
  research/p112-mixed-rank-reduction/test_verify.py
TMPDIR="$RUN/tmp" uv run --python 3.12 --no-project python -B \
  scripts/research_package.py --package research/p112-mixed-rank-reduction
```

Without `--work`, temporary replay files are removed beneath `TMPDIR`.
`--work` requires a new external directory and preserves diagnostics there.
[SOURCES.json](SOURCES.json) pins live inputs and base provenance;
[UPSTREAM.json](UPSTREAM.json) binds byte-identical excerpts from DreamingOfClouds's
PR3154 at `708f0ad8928c383de8294aea3c126e9461d2066d`. The generic provenance check
also needs the source-import ancestor recorded in SOURCES.json. Native compilation uses warnings as
errors. The dedicated workflow supplies the compiler environment.

## Open next questions

Can the same mixed-rank inequality eliminate a named survivor in a different
beta cell? Start with its actual quotient-basis cover and count of nonbasis
weight-seven pieces. A uniform rank-seven bound or another local fixture does
not supply that cover. Other cells have not been enumerated here.

What exact shared-deletion bound is needed for a remaining C5 cell? Pin its
support budget and numerical target before running a full rank-seven census.
This package neither settles that census nor establishes common-set sharpness.
Structured relevance, first steps and blockers are in [TASK.json](TASK.json).

## Credit

Nick Petalas contributed the eight-deletion theorem, dual-code replay and
mixed-rank application. DreamingOfClouds supplies PR3154's reduction, TWOSIDE
filters, fundamental-circuit lineage and earlier finite work. The retained
E8, P112 and decoder contributors keep their credit. PR3158 and PR3160 supply
adjacent quantifier and fixed-space controls, not this all-flat eight-deletion
result. No priority is claimed for the elementary dual-code identity.

Frozen predecessors are unchanged. The vendored excerpts retain their notice
and Apache-2.0 license. New work is Apache-2.0. Development and internal
read-only review used substantial automated assistance. No independent human
or proof-kernel review is claimed.
