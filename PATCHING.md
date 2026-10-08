# Applying the inherited manuscript patch

This patch is the PR #10 baseline. The current partial-swap extension is
presented in `notes/partial-swap-note.tex` and its PDF; it is not included
in this historical combined manuscript patch.

`patches/batched-23.patch` applies to the original manuscript snapshot at
`adc7f1241b42e322a6451854ab7e4b4c146bf78a`, retained under `upstream/`.
It includes the PR7 dependencies, batched construction, and corrected Gaussian
input error enclosure.

To generate a complete copy for review, choose a new destination:

```sh
python3 scripts/make_batched_patch.py --materialize /tmp/integer-mult-batched-review
```

The entry point is `/tmp/integer-mult-batched-review/build/main.tex`.
The bundled `upstream/` stays unchanged. With pdfLaTeX installed, compile from
that copy's `build/` directory, including BibTeX and the usual reference reruns.

Check applicability without modifying the source:

```sh
git apply --check --directory=upstream patches/batched-23.patch
```

The combined patch starts from the original snapshot; historical patches are
alternatives for the same base. PR7 is pinned at
`6725c6a17b17871a35353fd29157f4ed851bc114` for the retained producer sources.
The old uniform recurrences keep their original exponents. The active consumers
use `lem:batched-chunk-swap` and `prop:batched-simultaneous-layer`.
