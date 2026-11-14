# Exact generator count for lexicographically flattened Gaussian tensors

**No new kappa. A scoped all-size representation theorem; no runtime lower
bound or foundational assumption discharge.**

For a tensor of invertible Toeplitz factors, ordinary displacement rank can
grow with all the nonfastest dimensions even though the tensor is separable.
This package determines that growth exactly for normalized shifted Gaussian
sections and their inverses, and converts it into the exact minimum number
of ordinary lower-times-upper triangular Toeplitz generator terms.

## Result and why it matters

Let `B_i[j,k]=q_i^((j-k)^2) v_i^(j-k)`, with `0<q_i<1`, `v_i>0`, and factor
dimensions `n_i>=2`. Put `H=B_1 tensor ... tensor B_g` and `T=product n_i`.
With the last tensor index fastest and Z the ordinary strict lower shift of
size T, each of

\[
 \operatorname{rank}(HZ-ZH),\quad
 \operatorname{rank}(H-ZHZ^{\mathsf T}),\quad
 \operatorname{rank}(H^{-1}Z-ZH^{-1}),\quad
 \operatorname{rank}(H^{-1}-ZH^{-1}Z^{\mathsf T})
\]

is exactly `2T/n_g`. The best lexicographic axis ordering therefore gives
`2T/max_i n_i`. Both H and its inverse require exactly that many terms in
an ordinary `sum L(u) U(v)` representation. In particular, two-point factors
have full displacement rank in every lexicographic axis order.

The stronger underlying theorem allows any invertible outer matrix A and
any Toeplitz fastest factor B: a selected `2m`-square boundary minor has
determinant `(-b_-1^2)^m det(A)^2` for the Sylvester displacement and
`(-b_-1 b_1)^m det(A)^2` for the Stein displacement. Thus the forward claims
need only the relevant nonzero adjacent coefficients. The inverse Stein
conclusion additionally uses tensor persymmetry. [PROOF.md](PROOF.md) gives
the complete all-size argument and a Vandermonde proof of Gaussian
invertibility.

The retained one-dimensional shallow inverse uses short ordinary Toeplitz
generator sums. The result identifies the exact representation cost of
transplanting that formula to a flattened tensor. It prevents confusing
tensor rank one with constant ordinary displacement rank. It leaves direct
separable circuits and different grouped algorithms available.

## Source binding and scope

Base: `e54523517d0f03e58352e647c403a5af3e525a57`. Exact Git blobs and SHA256
digests are in [SOURCES.json](SOURCES.json). These files are historical
provenance, not runtime inputs: the standalone verifier uses only its own
literal rational fixtures. The original task card and scope change are in
[TASK.json](TASK.json).

The normalized shifted kernel is from section 2 of
`research/capped-fusion-t74-k554/outer/GAUGEFREE-INTERIORS.md`; the ordinary
inverse generator formula is from section 5 of
`research/capped-phase-fusion/SHALLOW-TOEPLITZ.md`. The source's actual paid
gauges and conditioning requirements remain in force. The theorem also
applies to an exact truncated/rounded Toeplitz table if its invertibility and
nonzero adjacent coefficients are established separately; PROOF.md states
a sufficient structure-preserving perturbation test.

The selected #7000 record has conditional kappa
`363005817/100000000000` and five retained assumptions. All five remain.
This package is an analytic-recovery representation audit, not an admission
of a new grouped service or an unconditional multiplication result.

The following exclusions are substantive:

- No lower bound for recursive Full, separable circuits, arbitrary grouping,
  or complete multiplication runtime. A direct local-axis circuit coexists
  with maximal ordinary displacement rank.
- No minimum over arbitrary coordinate permutations. A four-coordinate Gray
  order reduces both ranks from four to two in a checked example.
- No approximate-rank or finite-precision lower bound from exact nonzero
  determinants alone.
- No automatic rank identity for diagonally gauged source blocks, the full
  periodic Reference, holes, or unstructured rounded matrices.

## Reproduce

From the repository root:

```sh
python3 -I -W error -B research/tensor-gaussian-displacement-rank/verify.py
python3 -I -O -W error -B research/tensor-gaussian-displacement-rank/verify.py
python3 scripts/research_package.py --package research/tensor-gaussian-displacement-rank --check-only
python3 scripts/research_package.py --package research/tensor-gaussian-displacement-rank
```

The first two commands were executed on Python 3.12.14 and return identical
JSON with `status: PASS`. The registered hook declares the repository's
Python 3.12 generic environment and has no third-party requirements.

The bounded domain is 48 rational generic cases with `1<=m<=3`,
`2<=n<=5`, four fixtures per size, seed 641; 47 have invertible B and also
check the inverse Sylvester identity. Eleven Gaussian tensors have dimensions
`(2)`, `(3)`, `(4)`, `(2,2)`, `(2,3)`, `(3,2)`, `(3,3)`, `(2,4)`, `(4,2)`,
`(2,2,2)`, `(2,2,3)`. All four ranks, Gaussian determinants, inverse residuals,
persymmetry and 22 minimum-generator reconstructions are checked. All six
axis orders of a distinct-factor `(2,3,2)` tensor are checked separately.

Ranks use exact rational row reduction. Selected minor determinants use
denominator-cleared integer Bareiss elimination. Literal shift-matrix
products are compared with independently indexed entry formulas. Six
negative/scope controls cover zero adjacent coefficients, singular outer
factors, the wrong axis shift, a Gray permutation, a direct tensor circuit,
and deliberate wrong-rank rejection. Checks use explicit exceptions and
remain active under optimized Python. These finite controls do not replace
the written universal proof, and no random or finite search is claimed
to cover all matrices.

## Relationship to predecessor work

The Beatty-run inverse in [#5566](https://github.com/CrocSwap/integer-mult-bounds/pull/5566),
fine-grid inverse in [#5571](https://github.com/CrocSwap/integer-mult-bounds/pull/5571),
and physical periodic inverse in [#6905](https://github.com/CrocSwap/integer-mult-bounds/pull/6905)
provide different one-axis application and error contracts. This package
does not duplicate or replace them. It adds the exact flattened ordinary
displacement calculation, matching generator minimum, and scope controls.
The previously familiar factor-of-axes serial scan budget is not claimed
as a new result. Bounded repository overlap searches and these selected
predecessor reads found no matching exact theorem; this is not a claim of
literature-wide priority.

Classical background: Olshevsky, Oseledets and Tyrtyshnikov,
[*Tensor properties of multilevel Toeplitz and related matrices*](https://www2.math.uconn.edu/~olshevsky/papers/tenprop_revision2.pdf).
Tensor structure and displacement structure are established concepts.

## Open next questions

1. Can retained source perturbations admit a quantitative lower bound for the
   selected minors? This would determine whether the exact obstruction has
   a useful approximate analogue. Start by bounding the inverse boundary
   minor or its smallest singular value; exact determinants alone do not
   provide a usable precision threshold.
2. Can a source-faithful grouped inverse exploit multilevel structure with a
   complete fixed-tape budget? Start with one grouped block and charge source
   generation, all gauge/frame changes, restoration, precision and movement.
   The ordinary generator obstruction does not rule out this route.
3. Can such a grouped operation compose with the actual periodic Reference
   and hole completion? First bind it to the exact #6905 physical consumer
   rather than substituting its normalized core. The source-to-consumer and
   full three-transform budgets remain open.

The structured versions of these questions are in TASK.json.

## Credit

Prepared for @CubeJerry with substantial OpenAI ChatGPT assistance. The
orchestrator and research worker independently derived the boundary-minor
argument; the orchestrator extended the initial two-point calculation to
arbitrary Toeplitz sections, and the worker independently checked and
packaged the extension. Retain the originating source authors' credit,
including Vlado Vojdanovski's capped-phase-fusion work and the cited
predecessor packages. New files are Apache-2.0.
