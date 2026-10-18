# Nonlinear messages under the Hurwitz copy-charge model

**Scoped negative result; no new kappa.** Fixed-support, zero-error vector or
nonlinear messages cannot reduce the ten-line Hurwitz E8 copy floor **if a
q-bit message is charged q times its reader/source pairing rank**. For b
independent bits per port the minimum is 10b quaternionic units, or 40b
rational units. Unequal widths have minimum charge equal to their sum.

The width-pricing assumption is essential and is not established here for
arbitrary physical nonlinear suppliers. The [proof](PROOF.md) replaces the
scalar rank argument from [#703](https://github.com/CrocSwap/integer-mult-bounds/pull/703)
with a transcript-counting argument. It permits arbitrary nonlinear encoding
and joint decoding, any finite number of fixed-width messages, and free
mate-port side information. It does not cover cheaper shared copying between
coordinates, adaptive or interactive messages, correlated inputs, error,
additional nonorthogonal side information, or changed stage accounting.

This is an application of elementary zero-error counting, with no claim of
novelty for that general method. The contribution makes explicit which
vector/nonlinear extension of the predecessor's model still has its floor.

## Reproduce

From the repository root, with UV and CPython 3.10+ (standard library only):

```sh
uv run --offline python -B research/hurwitz-nonlinear-copy-floor/verify.py
```

Expected:

```text
PASS_HURWITZ_NONLINEAR_COPY: 1048576 support pairs; 3 attaining codes; 12 rejection controls; conditional floor 10b
```

The default command recomputes and checks [RESULTS.json](RESULTS.json). It
does not overwrite it. `--write /tmp/hurwitz-results.json` emits a separate
receipt for comparison. Neither network access nor another PR's files are
required at runtime. Source references and exact hashes are in
[SOURCES.json](SOURCES.json); the verifier binds that manifest to its receipt
but does not fetch or authenticate external GitHub content during replay.

The replay reconstructs all 240 roots, ten line bases, 100 singleton Gram
blocks, 45 two-line spans, and all 1,048,576 ordered support pairs. It checks
32 weighted transversals and three exact attaining truth tables: ten one-bit
ports with a nonlinear encoder, four two-bit ports with nonlinear coordinate
mixing and a free mate-only message, and unequal widths including zero.
There are 33,856 conditional transcript checks across those examples.

Twelve negative controls reject bad geometry/weights, underdeclared width,
missing sources/readers and corrupted transmissions. A boundary example
shows why the side-information premise matters: if every other input is
free, one global parity bit costs only 2 instead of 10 and decodes correctly.

Additional independent checks:

```sh
uv run --offline python -B research/hurwitz-nonlinear-copy-floor/test_verify.py
```

These compare every geometric obligation with a separate Fraction-based
column algorithm, explicitly invert the nonlinear codes on all 1,280 inputs,
exhaust all 65,536 one-bit encoders in a four-port instance, and reject receipt
and manifest mutations in a relocated optimized-mode replay. The finite
checks support the written proof; they are not its all-width justification.

## Budget, scope and attribution

Under the additional inherited Dfc accounting with k=4b, even the optimistic
complete budget is `D/T <= (s-1)40b - s40b = -40b`. All helper, source-access,
frame-change, restoration and recursive expenses were granted zero before
this screen. A paid construction cannot help under these premises, so none
was attempted. No selected certificate, supplier, `upstream/` file or
repository-wide generator changes.

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`. The selected conditional
result remains `51110230636731/31250000000000000`; none of its compiler,
realization, hosting, precision, tape or analytic obligations is discharged.
See [CLAIM.md](CLAIM.md) for seed 42, candidate selection and scope, and
[VALIDATION.md](VALIDATION.md) for the completed checks and overlap refresh.

Credit Douglas R. Colkitt / Mister-Meeseeks (#703) for the exact scalar floor
and weighted-transversal certificate, Joel Pulikkan / GamingPuzzled (#620)
for the extension-ring investigation, and DreamingOfClouds (#446 and the
corrected format note) for the inherited accounting framework. Sagar
Thakrar's concurrent #738 develops the related scalar weighted-clique method
on Gaussian E8; this package does not claim its geometry or numeric result.

Prepared by Alexander Templeton (@azide0x37) with substantial OpenAI Codex
assistance in proof development, implementation, verification and writing.
Apache-2.0. No independent human review or proof-assistant verification is
claimed.
