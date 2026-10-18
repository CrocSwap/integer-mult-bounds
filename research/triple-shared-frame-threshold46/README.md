# Triple shared nodes need ten coordinates when both endpoint pairs degenerate

In the historical parity-side one-node model, the general norm-one bound of
eight ambient coordinates cannot be attained with four triple labels. If
both source and target pairs overlap in one coordinate, all cross intersections
are even, their signed scalar kernel has rank one, and their binary spans are
disjoint, the source and target supports must be entirely disjoint. Each pair
occupies five coordinates, so the sharp minimum is **ten**.

The new contribution is an all-dimension support classification and exact
count, with independent complete finite evidence. PR920 already supplied the
ten-dimensional positive fixture and the eight-dimensional general norm-one
fixture; this package proves why the gap between them is necessary for
triple labels and constructs legal frames for every rectangle in the class.

For a fixed unordered source pair, there are `15*C(h-5,5)` unordered target
pairs. With the source and target sides distinguished, the total is
`225*C(h,5)*C(h-5,5)`. The count is zero below ten. At ten, the 56,700 labeled
rectangles all use disjoint supports, and all 15 canonical target pairs admit
the predecessor's same dimension-four frame with legal incident residuals.

From repository root, Python 3.11+ and the standard library:

```sh
python -I -O -B research/triple-shared-frame-threshold46/verify.py
python -I -O -B research/triple-shared-frame-threshold46/independent.py
python -I -O -B research/triple-shared-frame-threshold46/controls.py
```

Expected: `PASS_TRIPLE_SHARED_FRAME_THRESHOLD`,
`PASS_INDEPENDENT_TRIPLE_THRESHOLD`, and `PASS_TRIPLE_THRESHOLD_CONTROLS`.
Together these take roughly seven seconds on this machine. All checks stay
active under optimized Python. The main checker exhausts canonical target
pairs for h=5..12; the independent set/Fraction checker exhausts all labeled
pairs for h=5..10: 6,930 source pairs and 615,060 eligible rectangles. These
are finite coverage statements; the separate written proof supplies the
all-dimension conclusion.

`CERTIFICATE.json` includes every canonical accepted target pair and all 60
orthonormal incident residual bases at h10. `INDEPENDENT.json` retains the
complete labeled census totals. Ten semantic checks preserve necessary
hypotheses, including the legal eight-dimensional non-triple example and
illegal alternating residuals. Six package rejections check exact source
inventory, source/snapshot tampering, typed output, coverage and overwriting;
relocation to a path with spaces passes.

This result concerns one scalar-shared node with two degenerate endpoint
pairs in the historical orthonormal-residual interface. It is not a restriction
on arbitrary labels, a multi-node DAG or the selected T16 supplier. It does
not supply a physical circuit, paid invoice, runtime gain or new kappa.

Fixed base `ba82555c64e1879e4b7decce28186f208fcb8262`, selected PR1042 with
kappa `1672188119205421/10^18`. The snapshot is frozen, so future selected
pointer changes do not affect replay. Prepared by @woklerx with substantial
OpenAI Codex assistance; Apache-2.0. See `PROOF.md`, `PROVENANCE.md` and
`NOTICE.md` for exact assumptions and predecessor credit.
