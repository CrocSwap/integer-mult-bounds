# Independent review of the source-geometry annex

Accepted on 2026-10-22. No material finding remains in the four stated
theorem families, source closure, portable replay, or final description.
This is a fresh review by a separate OpenAI Codex agent. It is not human
review or proof-assistant verification. The four results have different
models. Their bounds must not be added as one cost invoice.

The accepted annex is `actual-query-information-bounds/annexes/source-geometry`.
Its `ANNEX-MANIFEST.json` SHA256 is
`cc7279ee48a7751a57f59a98f991ba879cf6e63144fcb7885ed1e4b69b432663`.
The accepted supplemental description SHA256 is
`6a77b8b0d00506b09f2a11262c39ca9f576be968a5c261bc3f0a4c6cbb783d15`.
The description standard at
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`
was read before this check. This review made no Git or PR action and
changed no package or prior review file.

The review read the complete proofs, their prior independent reviews,
the source dependencies that support the adopted claims, all seven
portable checkers, and the complete portability diff. The source pins are
in [REVIEWED-SOURCE-PINS.json](REVIEWED-SOURCE-PINS.json). The proof checks
and their limits follow.

1. **Binary support geometry and direct capture.** Each of the eight row
   supports has rank seven. They form four equal-space pairs. Distinct
   spaces intersect in dimension six; all eight intersect in dimension
   five and span dimension eight. The shared-port graph is
   `K_(2,2,2,2)`. In the stated direct-capture model, a rank-seven capture
   must equal its row support. A shared unwarped carrier on an increasing
   subspace chain cannot visit two distinct rank-seven support spaces.
   Thus the rank-seven rows form an independent set of size at most two,
   and the capture-rank sum is at least `2*7+6*8=62`. The proof needs one
   carrier per source and one complete direct common-frame capture per
   row. Partial queries, extra carriers, and operator-valued codes are
   outside this class. Pair coding does not satisfy the one-carrier
   premise. The result is not a construction at 62 or a native-cost bound.
   The producer's binary elimination and the reviewer's XOR spans and
   nullspaces agree in the cold replay.

2. **Dyadic fixed-observation separation.** The residue argument is valid
   for every log `M` with a two-sided unit `MD`, not only `MD=I`. From
   `alpha B+beta M=0`, multiplication by `D` and reduction modulo 13 force
   `beta=0`, then `alpha=0`. The actual `B` has a dyadic unit minor, so
   `rank[B;M]=16`. The full-null family works for general `M`; its ordered
   cancellation uses `Qq=qQ=I`. The mixed-source unit criterion reduces
   to `diag(I,-MD)`. With fixed linear `N` as the only further observation
   of retired ordinary Y, `ker N` must lie in `ker B` intersect `ker M`.
   Nonlinear postprocessing cannot distinguish equal observations. This
   bounds total observation rank, not concurrent scratch or native
   children. The rank-eight alternative `M=B/13` is outside the dyadics.
   The stronger coefficient-ring statement uses an integral domain, an
   invertible minor of `B`, and fraction-field rank eight. Under `MD=I`,
   that rank-eight log is uniquely `B/13`. The finite routed extension
   needs the stated ordered identities and Gaussian-dyadic two-sided
   inverses after flattening. Its two-coordinate test is only a fixture.
   Cold checks include 24 logs with nonidentity unit `MD`, a determinant
   `1/8`, the full-null correction, and a noncommuting route fixture of
   rank 32. No cheap query, scatter, decoder, or odd-grid implementation
   follows from these checks.

3. **Constant scalar centre mixing.** The physical-support proof applies
   to the fixed source/Y-tail one-way insertion class. The separate
   canonical-interval extension covers cuts 7502 through 17249 with a
   fixed exterior, fixed wrappers, and the stated support and endpoint
   conditions. The basis-state support test justifies 6,608 forbidden
   off-diagonal equations on all 64 entries of `A`. A 63-row minor has
   determinant `-2^71`. Since `I8` satisfies the equations, their kernel
   is exactly `A=cI8`; the diagonal response is the same `c` at every
   port. A nonzero response therefore cannot factor through seven
   constant scalar centre channels. This conclusion does not cover new
   native paths, new query/scatter spaces, arbitrary wrapper edits, or
   operator-valued centre entries. The second proof uses two actual
   orthogonal bases and a connected overlap graph. Its ring extension
   needs units on the nonzero overlap entries. The independent checker
   rebuilt both complete interval inventories and all 4,276 products,
   checked physical views, and recomputed the determinant and overlap
   graph. It uses reverse operator order. The old producer's forward
   loop is valid for this packet because all consumed X histories have
   length zero or one. That limit is checked. It must not be assumed for
   longer histories. A dense rank-seven projection fails 2,534 equations;
   a repeated determinant row gives zero; another actual basis pair has
   two overlap components.

4. **Payload-query source and response spans.** Both ordered
   factorizations remain valid for arbitrary noncommuting payload maps:
   scalar gates are `B tensor I`, queries are `I+uQv` with scalar `u,v`,
   and the initial and final interfaces are scalar. Scalar COPY and
   CLEAR need not be invertible. An `r`-direction block counts `r` times.
   Every non-scalar payload map counts, including rank-zero address maps.
   The simultaneous scalar source and response spans have dimension at
   most the counted query total. Separating functionals give source rank
   112 for the actual line query and the proposed matched-plane query.
   Tensor compression proves the same result at every positive depth.
   The mixed-plane endpoint on `n` fields has a separate `n`-query lower
   bound without a common negative eigenvector. These are not native
   invoices. Prior port-dependent input encoding changes the premise.
   The prior source-domain review is present and its pins agree. The
   frozen proof's old pending-review note is superseded by the retained
   handoff and review. Cold replay reconstructed `R` from 10,851 scalar
   events and checked 28,672 Fourier columns, 802,816 functional
   contributions, all 56 pair Gram determinants, and the exact block
   minor determinant 8. Reversing one plane changes the expected sign.

The source and dependency audit passed. All 72 source and notice files
are byte-equal to their originals. All 129 older package files and all 94
prior review files are unchanged. The full historical query-span archive
has 6,095,634 bytes and SHA256
`f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6`.
Its three consumed members are unique regular files and match the parent
members exactly. The portable replay needs those members, not the full
archive. Four parent runtime inputs are pinned. All 47 non-main function
ASTs in the seven portable checkers equal their originals. The complete
diff changes only input/output handling and two archive reads. The main
functions and driver were also read; AST equality alone was not used to
approve them. All 36 local README and notice links resolve. These checks
are recorded in
[SOURCE-AND-DEPENDENCY-CHECKS.json](SOURCE-AND-DEPENDENCY-CHECKS.json), with
the repeatable source audit in [check_annex_sources.py](check_annex_sources.py).

The independent cold run copied the full parent package to a new temporary
directory. It ran from a separate empty working directory with
`PATH=/no-external-tools`, one-process thread settings, and Python 3.14.7
under `-I -O -B`. All seven checks passed in 5.114940 seconds. All eight
receipts match in value and type. Four are byte-equal; the other four
change only `checker_sha256` to the actual portable checker hash. All 229
relocated package files remained equal to the original files. Free disk
space exceeded 3 GiB before and after the run. See
[COLD-REPLAY-CHECKS.json](COLD-REPLAY-CHECKS.json),
[TYPED-RECEIPT-CHECKS.json](TYPED-RECEIPT-CHECKS.json), and
[cold.stdout.txt](cold.stdout.txt).

From a checkout with the full parent package at its published path, use a
new output directory:

```sh
python3 -I -O -B research/actual-query-information-bounds/annexes/source-geometry/replay.py --out /tmp/source-geometry-replay
```

Expected final output:

```text
PASS_SOURCE_GEOMETRY_ANNEX
```

The normal and optimized producer runs are retained in the annex. This
fresh review independently ran the optimized cold check. It did not rerun
the old mixing emitters or modular checker, the native recipe generator,
plane routes, an odd-grid implementation, the parent/cache mathematics,
or a complete supplier. The counterexamples and fixtures above are not
claims that every input-mutation class was rejected.

The final description states the four models, the cost limits, the
executed checks, the known history-order limit, omitted checks, source
credit, and substantial AI assistance. The historical source base is
`bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. The publication base is
`b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`, with selected conditional
kappa `60403/20000000`. Transfer of these historical results to that
selected construction is unproved. No complete kappa improvement follows.
The description's local template targets and credit evidence are recorded
in [PR-DESCRIPTION-CHECK.json](PR-DESCRIPTION-CHECK.json). The publication
coordinator must replace `COMMIT`, verify GitHub objects, inspect rendered
Markdown, and read back the published body and HTML. This review does not
claim those publication steps are complete.
