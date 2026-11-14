# A rounding margin for every order of two selected source factors

**Fixed two-axis source theorem; no new kappa.** This closes a quantitative part of A11's rounding limitation at a deterministic extremal phase. Arbitrary A11-good phases remain open.

For each of two original fine-prime source axes, choose the unique index with centered numerator `s beta_i=-(s-1)/2`. It is a legal, nonwrapping same-cell adjacent pair, and its literal source matrix is

    C_l = [[1,U_l],[V_l,1]],
    U_l=exp(-a(2delta_l+1)/s_l),
    V_l=exp(-a(2s_l-1)/s_l).

The source normalization, phase and chirp remain intact. For `p>=4096`, `s_l>=p^4`, the retained fine-prime interval and `a=pi alpha^2` with `alpha=ceil(sqrt((4/pi)ln(16p)))`, put `w=exp(-2a)`. The factors lie in the uniform asymmetric box `U_l in[1023/1024,1]`, `V_l in[w,2w]`, `w<=1/2048`.

For **every one of the 24 simultaneous vertex orders** of `C=C_1 tensor C_2`, the ordinary lower-shift Stein displacement has

    determinant magnitude >= w^2/16,
    smallest singular value >= 2^-10 w^2.

The displacement of the exact inverse has smallest singular value at least `2^-19 w^2`. These are nonsymmetric matrices; no SPD premise is used. [PROOF.md](PROOF.md) proves the continuous parameter statement, the source binding and all norm/error factors.

## Quantitative rounding and matched periodic aliases

An arbitrary matrix entry perturbation of size at most `2^-32 w^2` preserves full displacement rank in every order, for both the perturbed tensor and its exact inverse. Per-factor entry error at most `2^-34 w^2` suffices after charging tensor formation. Since `a<=9ln(16p)`, a sufficient factor precision is

    b >= ceil(34+36 log2(16p)) bits.

Thus `p` bits suffice for `p>=4096`; any fixed positive `Cp` suffices eventually. This is an explicit absolute entry-error contract, not production-program admission.

The exact matched source periodization `N_source=Pi(G)` has adjacent-pair alias error at most `4 exp(-a t^2/8)`. In the stated source range this is at most `2^-36 w^2`. A further periodic-factor entry error at most `2^-36 w^2` still preserves the margin, so `b>=ceil(36+36log2(16p))` suffices for that contract; `p` bits still suffice. The inverse is the inverse of the selected tensor of periodic sections, not a section of the full source inverse.

The named production theorem in #6099 cannot simply supply this contract. Its guards include `u d<=p` and `4d theta>1`, incompatible with `theta<=p^-2` for `p>=4,u>=1`. This excludes that particular admission theorem on this fine-prime family; it does not rule out every compatible producer. A current implementation must identify the matched matrix, prove its scalar/entry error and pay setup precision, coefficient construction and transport.

## Proof mechanism and limits

The 24 orders split into eight lex, eight Gray and eight opposite-first orders. The first two types have explicit factorizations and signed bounds. In the last type, the displacement determinant is close to an exactly computed `+1` or `-1` reference determinant. Singular-value bounds follow from determinant and norm bounds; a determinant Schur-complement identity handles inverses and a Neumann estimate pays for inversion of perturbed input. No transcendence argument is needed for this quantitative selector.

The whole-box result does **not** extend unchanged to three axes. For `B=[[1,1],[w,1]]` and order `(0,1,2,4,3,6,7,5)` of `B tensor B tensor B`, displacement columns 2 and 5 are identically equal for every w. These boundary factors lie in the same box. This is not a counterexample at actual distinct-prime source parameters, where the decays are strict.

The selector uses a modular inverse and logarithmic local arithmetic scratch, with both output indices charged. It does not produce a matrix page, inverse, generators or a full caller. Full rank forces four ordinary lower/upper Toeplitz generator products only for that specified representation. No general runtime or memory lower bound, larger-dimension result, full analytic-recovery theorem or improved kappa follows. All five framework assumptions and selected #7000 remain unchanged.

## Reproduction and evidence

Python 3.12 and standard library, from the repository root:

```sh
python3 -I -W error -B research/extremal-phase-two-axis-margin/verify.py
python3 -I -O -W error -B research/extremal-phase-two-axis-margin/verify.py
python3 -B scripts/research_package.py --package research/extremal-phase-two-axis-margin
```

The direct commands are read-only and print `PASS_EXTREMAL_PHASE_TWO_AXIS_MARGIN`. [RESULT.json](RESULT.json) retains identical normal/optimized output. The primary verifier authenticates four inputs; checks all 16 factorized orders coefficient-by-coefficient and the eight remaining reference determinants; verifies 72 ordered rational cases with 288 exact Gram certificates, including recomputed perturbed inverses; and runs 11 failure/nonextension controls. No floating point is used.

Two finite source tuples at `p=4096`, common `t=2^64`, satisfy the declared fine-prime interval. Their primality is proved by exact certificates: `s=k*2^m+1`, odd `k<2^m`, and `a^((s-1)/2)=-1 mod s`. Every prime divisor must then have multiplicative order divisible by `2^m` and exceed `sqrt(s)`, proving primality. The verifier checks those powers, literal phase geometry, both source exponents, degree-four injection and 32 alias exponent inequalities. These tuples are not a complete production page or caller.

The primary polynomial/rational helpers adapt A11 with credit. Independent root review uses a separate exact continuous Bernstein certificate over the entire parameter box, not sampled values; its files are retained separately. The analytic class proof is independent of that certificate. No human/formal-kernel acceptance, supplier cold replay or hosted CI is claimed.

## Pins and credit

Canonical base `e54523517d0f03e58352e647c403a5af3e525a57`, priority revision 8. [SOURCES.json](SOURCES.json) and [DEPENDENCIES.json](DEPENDENCIES.json) pin provenance and exact inputs. Immediate predecessor: [A11 selected source-pair rank theorem](https://github.com/CubeJerry/integer-mult-bounds/commit/0a6315b71a47b37a4faa2a4f555c5bc4e9e87811). Also credit [A10 exact core specialization](https://github.com/CubeJerry/integer-mult-bounds/commit/da06a3d10e06870a0279e33dd5056ded8d7e7a38) and the [normalized generator margin](https://github.com/CubeJerry/integer-mult-bounds/commit/575491d5fc353eac26010e45e9ced60fc9870017), whose lexicographic and physical boundaries differ. [OVERLAP.md](OVERLAP.md) records bounded coverage and the approved narrowing.

Credit Chafik Boukhalfa / [#1786](https://github.com/CrocSwap/integer-mult-bounds/pull/1786), Vlado Vojdanovski / [#1673](https://github.com/CrocSwap/integer-mult-bounds/pull/1673), IdeaOuter's shift work credited in [#1758](https://github.com/CrocSwap/integer-mult-bounds/pull/1758), Jeremy Kothe and the retained bilateral source lineage, JoyboyBrian / [#6099](https://github.com/CrocSwap/integer-mult-bounds/pull/6099), Jose Manuel/jmbarrancoml / [#3851](https://github.com/CrocSwap/integer-mult-bounds/pull/3851), and the retained framework contributors. Classical determinant, norm, Neumann, Schur and Bernstein facts are not claimed as new.

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance. The worker proposed and proved the extremal-phase narrowing; the lead independently checked the proof, supplied the alias and three-axis nonextension observations, and produced the separate continuous certificate. Original source notices and Apache-2.0 terms remain unchanged.

## Open next questions

1. Can arbitrary A11-good phases have a useful source-specific margin?
2. Which actual fine-prime producer meets the matched periodic-factor error contract with complete setup costs?
3. What weaker source-specific rank margin survives at more than two axes, given the exact whole-box nonextension?

## Executed independent verification

`review/ROOT-REVIEW.md` proves the Bernstein conversion behind a separate exact checker: all19992 coefficients for all24 orders are positive on the continuous box. It also checks the exact three-axis nonextension. Run `python3 -I -W error -B research/extremal-phase-two-axis-margin/review/check_bernstein.py`, also with `-O`; both commands are in VERIFY.json. A separate agent's source/proof review in `review/CROSS-REVIEW.md` authenticates the normalization, source parameters, alias and inverse/error interfaces without duplicating that polynomial implementation.
