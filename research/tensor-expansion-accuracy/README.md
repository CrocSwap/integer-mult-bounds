# Accuracy of the actual five-stage Tensor expansion

This audits the accuracy question left by JoyboyBrian's
[PR5056](https://github.com/CrocSwap/integer-mult-bounds/pull/5056).
It derives an exact identity for all five signed rounding residuals in the
existing expansion program, then transports their error through the actual
sequence of tensor axes at the inputs the program computes. No numerical
owner, coefficient page, precision policy or selected frontier is changed.

PR5056 establishes the nonlinear norm invariant and source-coordinate binding.
That admits the computed inputs to a unit-disk accuracy contract, but does not
itself account for their rounding error. This package supplies that account.
[PR5081](https://github.com/CrocSwap/integer-mult-bounds/pull/5081) instead audits
the compression suffix after chirp; its result is not repeated here.

## Result and assumptions

For one block, let `p` be the input precision, `P` the work precision,
`sigma` the normalization scale, and `n` the source-window length. Put
`h=2^-p`, `eta=2^-P`, and `lambda=2^(2sigma)`. Let `W` be the exact linear
map made from the **stored** coefficient factors and the original crop.
[PROOF.md](PROOF.md) expresses the computed output minus `W x` as five
separately weighted residuals, evaluated at their actual signed operands.
It proves the stored-page bound

```text
||computed block - W x||_infinity
  < sqrt(2) [h + lambda eta (n+6)/4].
```

The final extraction contributes on the p-grid; earlier residuals retain
their work-grid scale and subsequent amplification. Neither linearity nor
Lipschitz continuity of the rounded program is assumed.

Comparison with the true Gaussian additionally requires the matching producer's
directed coefficient enclosures and original-coordinate factor identity.
The true and stored A/K/B factors must lie in `[0,1]`, their errors must be
below `4eta`, and the reciprocal normalization error must be below `eta`.
The certified interval upper endpoint, not stored positivity alone, supplies
the true-factor bound. Exact signed word and convolution semantics remain
inherited contracts.

Under the production window and tail hypotheses, and the actual guard
`P >= 2sigma+p+ceil(log2(32(n+1)))+12`, the argument independently recovers
the existing per-axis accuracy bound

```text
delta_i < (sqrt(2)+2^-11) 2^-p.
```

For the exact original-axis map `A_i`, retain the analytic norm bound
`beta_i = 1/2 + 1/(20^(alpha_i^2)-1) <= 21/38`. PR5056's computed norm
invariant supplies every next input's disk admission. The new telescope is

```text
e_(i+1) <= delta_i + beta_i e_i,
e_D <= e_0 product_j beta_j
       + sum_i delta_i product_(j>i) beta_j.
```

Blocks partition each target axis, so their errors combine by a maximum;
halo copies and coordinate permutations introduce no multiplicity factor.
The executed axis order is preserved. The Tensor uses common `p`; changing
grids would require separately charged conversions and error contracts.

## Evidence and reproduction

[verify.py](verify.py) reuses PR5056's unchanged physical observation fixture
and source-produced p48/P80 catalogue. The executed prefix covers two axes,
64 Tiles, 128 Blocks and 3,776 internal truncations, stopping before chirp.
This is predecessor execution evidence reused with new accuracy checks, not
a newly implemented physical expansion or a complete Tensor success run.

[accuracy_model.py](accuracy_model.py) derives signed stage arithmetic and
residual transport separately. The checker compares its outputs and traces
with the retained observations, checks the stored-map axis telescope, and
exercises omission and nonlinear-rounding controls. Every intermediate axis
record is decoded from the actual coarse/short layout, including untouched
padding, before its values enter the telescope. A permutation preserving all
norms must fail that full coordinate comparison; the second axis must carry
nonzero prior error. It also requires the
retained physical receipt to remain identical. The reduced halos establish
finite arithmetic conformance; they do not establish production tail accuracy.

From the repository root with Python 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/tensor-expansion-accuracy --check-only
python3.12 -I -W error -B research/tensor-expansion-accuracy/verify.py
python3.12 -I -O -W error -B research/tensor-expansion-accuracy/verify.py
python3.12 -B scripts/check_research_commit.py --package research/tensor-expansion-accuracy --check-source-history
```

Registered normal and optimized replays passed under Python 3.12.13, including
the full intermediate-coordinate checks. The receipt records exact rational
errors and bounds; no floating-point comparison decides a check.
The registered hook runs both modes with a 240-second cap per invocation;
schedule physical replays serially. Ordinary replay compares the frozen
`RESULT.json`; only explicit `--write-result` authors it. Source imports use
captured authenticated bytes or a fresh private bytecode-cache namespace.

## Sources, limits and next questions

[SOURCES.json](SOURCES.json) pins the input closure at canonical main
`ff3cc58e370d0f678e529246f8c73e8094e18fcf`, priority revision 7.
PR5056's exact head is `fe624453057b7f0cb42870a594d314a148b9fb84`;
the retained expansion export is `1a86a8fb73bb7a0982fff99852a031832c191902`.
The distinct PR5081 compression result has head
`4c49fff7fdfa4ddda6ef615575b6762b3f46f9cd`. The
[canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/3664#discussioncomment-19149256)
and [TASK.json](TASK.json) record scope and overlap coverage.

The family decision is narrow. Production coefficient/locality acceptance,
exact primitive correctness and complete physical costs retain their stated
dependency status. Chirp, compression, final scale restoration and CRT integer
recovery are outside this contribution. No supplier, new kappa, independent
human review or proof-kernel acceptance is claimed.

## Open next questions

The next questions are to validate the certified interval backend and complete
production-page admission at their exact producer, and to combine this defect with the actual
chirp/compression caller through restoration. Start by pinning one production
geometry and its interval endpoints, or the complete downstream operator and
scale contract, respectively. Consult existing compression and recovery work
and refresh overlap before taking either task; neither is reserved here.

Prepared by Hiroki KUMAZAKI (@kumagi), with substantial OpenAI Codex assistance.
Credit JoyboyBrian for PR5056's norm audit and physical observation fixture;
Jose Manuel (`jmbarrancoml`) for the expansion, Tensor and nested physical
sources; Dugongue for the Gaussian row bound; and the retained PR3910,
Artus Krohn-Grimberghe, Hanson Sun, Vlado, Chafik Boukhalfa, Mason Hale,
RaD/hipotures, Gaussian/chirp/word and manuscript lineage. Original archives
and notices remain unchanged. New work is Apache-2.0.
