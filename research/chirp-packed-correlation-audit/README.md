# Sharp guard for the rounded chirped-correlation envelope

**Mathematical audit / scoped refinement; no new kappa.** The eight guard bits
in the retained Gaussian block's sign-separated integer packing are sufficient.
For its stated rounded-data envelope, the least uniform guard is **one bit at
every precision P >= 6**, including the source's P = 3p and P = 34p with p > 100.
This saves seven bits per slot in that relaxed interface. It establishes no
measured speedup, new supplier, or change to the multiplication exponent.

Removing that last guard admits a coefficient alias even when integer
recomposition and terminal-carry checks pass. The package supplies the exact
witness, an all-length coefficient argument, and separate packed-product and
direct-correlation implementations. No defect in the retained eight-bit choice
is claimed. Sharpness concerns the stated error envelope, not the narrower
outputs a particular exponential implementation might actually produce.
The guard is uniform over all positive A,B and F >= 1; fixed dimensions can
have additional slack from the ceiling of log2(AF).

## Precise obligation and proof

The source is the **One block** paragraph of
[fast-gaussian-resampling.tex](../../notes/fast-gaussian-resampling.tex), after
forming the rounded g and K and before the final expanding factor or output
rounding. Put A = L_A, B = L_B, Q = 2^P. Assume:

- P is a nonnegative integer; A and B are positive integers; F >= 1.
- Ideal g_a is complex with |g_a| <= F, and ideal K_r is real with 0 <= K_r <= 1.
- Rounded g and K lie on the Q^-1 grid and satisfy
  |g_tilde_a - g_a| <= 32F/Q and |K_tilde_r - K_r| <= 2/Q.
- The desired inner output is c_tilde_b = sum_a g_tilde_a K_tilde_(a-b),
  for 0 <= b < B. It remains on the Q^-2 grid.

Allowing K = 0 closes the source's strictly positive interval and only enlarges
the audited domain. Each scaled real or imaginary input component has magnitude
at most F(Q+32), and each scaled kernel entry has magnitude at most Q+2. Split
both sequences into positive and negative parts. Every coefficient in each
nonnegative product has at most A summands, hence is at most

`A F (Q+32)(Q+2)`.

Write C = 2^ceil(log2(AF)). The width `w = 2P + ceil(log2(AF)) + b` prevents
carry into the next coefficient whenever

`(Q+32)(Q+2) < Q^2 2^b`.

This also bounds every input digit strictly below the radix. Therefore the
least guard sufficient **uniformly over this envelope** is

`b(P) = floor(log2((2^P+32)(2^P+2))) + 1 - 2P`.

For P = 0,...,5 the guards are 7, 6, 4, 3, 2, 2. For Q >= 64,
`Q^2 < Q^2+34Q+64 < 2Q^2`, so b(P) = 1. In particular b(P) <= 7 for all
P >= 0, and the retained eight-bit guard is safe with strict slack.

To verify extraction, use the formal polynomials
`G(x) = sum_a g_a x^a` and `H(x) = sum_r K_r x^(A-1-r)`, now for the scaled
integer components. The coefficient of x^(A-1+b) is exactly
`sum_a g_a K_(a-b)`. The kernel occupies A+B-1 slots and the product occupies
2A+B-2 slots. Decode each of the four nonnegative products separately and then
combine their signs. Repeat for both complex components: at most eight integer
multiplications, with O((A+B)w)-bit operands and linear packing/extraction work.
This is the source's constant-product arithmetic step; it is not a physical
multitape implementation or a benchmark of the cited fast multiplier.

For necessity, take A=1, B=2, F=1, scaled g_tilde=Q+32, and scaled kernel
`(K_tilde_-1, K_tilde_0)=(0,Q+2)`. Valid ideals are g=1, K_0=1, and
K_-1=1/Q, so even strict positivity can be retained. Let
`R=2^(2P+b(P)-1)` and `M=(Q+32)(Q+2)`. Then R <= M < 2R. The unsafe decoder
returns `(M-R,1)` instead of `(M,0)`. Both digits fit, the integer recomposes
to M, and no carry remains after the two allocated slots. Yet both requested
coefficients are wrong. Thus a terminal-carry check alone does not certify the
inner block. The verifier exhibits this at P=101 and twelve other precisions.

The independent numerical enclosure also follows under the stated premises:

`|c_tilde_b-c_b| <= AF(34/Q + 64/Q^2) <= 98AF/Q < 128AF/Q`.

This uses the complex triangle inequality and includes both perturbations and
their product. It supports the source's `2^(7-P) F L_A` **inner** error bound.
It does not justify the later p-grid error assertion identified in PR371.

## Reproduce and completed coverage

From the repository root, with Python 3.12+ and only its standard library:

```sh
python3 -I -O -B research/chirp-packed-correlation-audit/verify.py
python3 -I -O -B research/chirp-packed-correlation-audit/test_package.py
```

Expected: `PASS_CHIRP_PACKED_CORRELATION`, followed by ten passing test groups.
The opt-in registered command requires Python 3.12 and runs both:

```sh
python3.12 scripts/research_package.py --package research/chirp-packed-correlation-audit
```

[RESULT.json](RESULT.json) records the deterministic checks:

- 8,748 exhaustive packings: all {-1,0,1}^7 inputs for A=B=2, P=0,...,3.
- 5,280 basis packings: every source/kernel delta pair, both complex components,
  and all rectangular dimensions 1 <= A,B <= 8.
- 680 seed-68 packing stresses and 680 separate rational enclosure cases.
- 12 stress packings at the source's S/E dimensions and precisions, using
  p in {101,128,257} and alpha in {2,floor(sqrt(p-1))}.
- 13 unsafe-guard aliases and six mathematical failure controls, including
  reversed-kernel omission, a wrong output crop, lost negative kernel entries,
  premature inner rounding, and omitted perturbation terms.

Packing stresses deliberately cover the larger symmetric componentwise box;
they need not be realizable Gaussian blocks. Only the rational enclosure cases
enforce all the ideal complex-norm and approximation premises. The written
proof applies to all stated lengths and precisions; finite checks support it
and are not a formal proof. The experiment stops at the declared coverage; it
is not a search for a stronger kappa or a literature-priority claim.

The package tests independently compute guards by repeated doubling, check
admission boundaries, replay a minimal copy in a path with spaces, and reject
source drift, a missing source, a corrupted receipt, and an occupied output.
Default replay writes no artifacts. The optional `--write NEW_PATH` refuses
to overwrite a file. [SOURCES.json](SOURCES.json) pins the three live inputs
by SHA256 and Git blob at base `49b3157d1d89adcef16df8be98445451672be5ba`.
The selected record and task catalogue are historical provenance; the generic
package hook also checks their pinned Git objects.

## Scope, overlap, and inherited obligations

OS-random assignment seed 68 selected adversarial audit. [CLAIM.json](CLAIM.json)
records three candidates, the local claim and stopping rule. Domain/window
arithmetic was already audited in Effy Elden's PR684; endpoint-potential
refinement was already supplied by Alan Grillo's PR902. Sagar Thakrar's PR693
audits the different upstream two's-complement extraction interface. This
package instead checks the Gaussian block's sign-separated, error-enlarged
convolution and its precise guard threshold. No code from those pending PRs
is imported. Exact inspected heads are in the claim.

Gaussian tails, exponential generation, the expanding chirp factor, final-grid
rounding, full resampling, fixed-tape compilation, recursive hosting, and the
analytic multiplication transfer remain outside scope. In particular this
does not close PR371 or adopt a seven-bit saving into production. The selected
conditional kappa remains 0.001672660197076918 at the base. Existing source,
upstream files, and selected certificates are unchanged.

## Open next questions

Can an end-to-end rounded block implementation retain this guard while satisfying
the final-grid correction in PR371? That would connect this arithmetic result
to an executable resampling block. A first step is to pin that correction and
compare complete normalized outputs against an exact enclosure. It remains
blocked by the separate exponential and final-rounding interfaces, which this
audit does not implement. [TASK.json](TASK.json) records the same scope.

## Credit

Credit eumemic's PR5 chirped-correlation construction, icekylinx's shifted-input
enclosure, Artus Krohn-Grimberghe's PR371 rounding audit, and the Harvey–van der
Hoeven arithmetic and Gaussian-resampling lineage cited in the source. Credit
Effy Elden, Sagar Thakrar, and Alan Grillo for the adjacent audits distinguished
above, and Douglas Colkitt for the repository and retained construction.

Prepared for Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance in
the mathematical argument, implementation, verification, and writing. New work
is Apache-2.0; predecessor files and notices are unchanged. No independent human
review or proof-assistant verification is claimed.
