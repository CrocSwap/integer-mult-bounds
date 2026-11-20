# Reproduction and proof boundaries

The registered finite suite requires CPython 3.12 and its standard library. Run it from the repository root.

```sh
python3.12 -B scripts/research_package.py --package research/direct-circulant-fourier
```

The last two markers are `PASS_DIRECT_CIRCULANT_PRODUCT` and `PASS_REGISTERED_RESEARCH_PACKAGE`. The last product group recovers every base-256 coefficient, signs, zero, and carry. It includes the composite orders 4 and 9, and the equal-target-width orders 5 and 7. A separate larger execution uses **two odd squares**, 9 and 25, in 512 records. Run the following to repeat it. The extra run is outside the default CI timeout budget.

```sh
python3.12 -IBO research/direct-circulant-fourier/check_product.py --odd-squares
```

Expected output includes `423488` H calls per transform and the five nonzero coefficients followed by 220 zeros. To supply different operands to the compiled word directly, run the following command. Without a diagnostic geometry the command uses the uniform length selector and its elementary finite branch.

```sh
python3.12 -IB research/direct-circulant-fourier/product.py --sides 3 5 -- 741503 466013
```

The reference interpreter evaluates each emitted matching, both input transforms, pointwise multiplication, the opposite transform, exact rescaling, CRT and carry. Elementary signed sums interpret a whole-field H call. The written price uses the separately specified native implementation of that call, along with the priced controlled BIT implementation of the CRT rows. No native template of astronomical rank was benchmarked. The fixed-tape construction stores recursion frames on tape. The Python diagnostic inherits the host's recursion, memory and integer-formatting limits.

## What the checks can falsify

| Check | Independent comparison or negative control |
| --- | --- |
| Root compiler and pair word | Exact rational action on both basis columns of every distinct emitted pair. The old Toeplitz test rejects the padded input. A cyclic shift with a singular first section, and equality at an asserted strict margin, fail admission. |
| Spectral input and compensation | Cartesian and rational-polar endpoints are checked against the supplied spectrum. Removing the branch scalar fails. Odd-grid, near-zero, repeated and negative-real phases are included. |
| Joint filter | A separate geometric-sum kernel checks the rank-eight projection on two independently generated nonseparable inputs. Each of the 17 dirty padding words is compared exactly. |
| Heterogeneous CRT | The row selector is checked across variable widths. A separate address map checks all 16384 padded addresses in one caller. A finite-field character calculation on 9 × 25 detects using the previous dyadic character weight on one leg. |
| Product | The physical root pipeline produces the integer and its coefficients. Independent integer arithmetic checks the result. On a second data set the largest real or imaginary pre-round coordinate discrepancy is 165/268435456. |
| Full cost | The square selector and rational power margins have finite checks. The asymptotic resource claim depends on the all-size proofs and lower supplier realization. |

## Lean

Use Lean 4.34.1. Lake pins mathlib at `d13f23b723b8a846827a245b89c10fc7d3f11612` and the predecessor decoder at `343f7b1817e26ad3f89d2ddad313b12741d53602`. From the `lean` directory in this package, run the following commands. The first run needs the pinned dependencies. A matching mathlib cache is optional.

```sh
lake --wfail build
lake env leanchecker -v CirculantOperators AccretiveFactors ChirpTransform PaddedDisplacement TensorStability HeterogeneousRows Coordinates Recovery Integrated PublicGrid GridBridge TraceProduct PaddedGrid
```

- The cyclic multiplier theorem uses arbitrary nonzero complex eigenvalues. It proves existence with a finite set of candidate rotations. The padded rank theorem proves that the actual nilpotent-shift commutator factors through two columns. [Accretive factors and sections](lean/AccretiveFactors.lean) · [Physical commutator](lean/PaddedDisplacement.lean)
- The two-pass Fourier identity uses original physical indices for all positive moduli, both parities and both signs. The proof computes the size of the Gauss sum. [Fourier identities](lean/CirculantOperators.lean) · [All-moduli chirp](lean/ChirpTransform.lean)
- The row theorem checks significance and order when shorter axes idle in a common schedule. The perturbation theorem bounds every computed prefix and the endpoint from local defects and bounded contiguous intervals. [Row schedule](lean/HeterogeneousRows.lean) · [Numerical stability](lean/TensorStability.lean)
- The bridge expands the recursively applied one-axis operators, proves the scaled-CRT address equivalence, and identifies both signs with the direct product character. Its endpoint uses the predecessor's actual public grid, round, carry and pack operations. [Tensor and decoder](lean/GridBridge.lean)
- The final theorem samples the actual padded CRT addresses of a fused numerical trace. It combines the local defect bound, the rational-word endpoint bias, and the norm of each contiguous interval with the public decoder. The compiler-to-stage estimates that instantiate these hypotheses are written proofs. [From fused stages to the carried product](lean/TraceProduct.lean)
- The padded tensor maps the exact zero-filled input to the zero-fill of the original-coordinate transform. Public truncation returns exact zeros in all holes after a represented forward call with the proved residual. The pointwise full-field packet entering the inverse therefore agrees with the formal word decoder. [Zero-filled physical operator and packet](lean/PaddedGrid.lean)

The written part proves the elementary coprime-square count, rational phase and gate generation, lowered prefix and local rounding bounds, movement and native resource estimates. The Python interpreter and tape implementation are outside the Lean operational semantics. The printed axioms and source hashes are recorded in the receipt. These checks and the author-side adversarial reviews do not establish independent scientific acceptance. [Precision theorem](PROOF.md) · [Growing-family machine and dependencies](COMPOSITE-OUTER.md) · [Receipt](EVIDENCE.json)
