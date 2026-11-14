## Result and why it matters

This establishes an explicit **global** integer bijection for `H4/2`, and by signed permutations for the ideal Gaussian pair `C+`, with error at most one and optimal **bilateral** radial slack `1/2`. Every input has strict radial change below `1/2`, while explicit forward and inverse sequences approach that value. The all-input lower bound applies to every total error-one integer map, without injectivity or a periodicity premise.

This is progress on the norm-rounding obligation behind an alternative precision/native interface. It is not a finite-search extrapolation, a completed selected supplier, or an unconditional multiplication theorem.

## What changed

- An explicit staggered matching of the half-integer grid, complete coset bijections, exact inverse and universal norm proof.
- A 16-corner unrestricted lower-bound sequence establishing optimal bilateral slack.
- A reusable exact integer kernel for the Hadamard and Gaussian forward/inverse maps.
- Separately written proof and implementation checks, a root implementation comparison, exact negative controls and a registered bounded replay manifest.
- Explicit counterexamples showing that this construction does not inherit conserved complex sum, global `i` covariance, inverse-by-conjugation or fourth-power identity.

The actual Gaussian inverse is `S F_H^-1 L`. It must not be replaced by conjugating the positive rounded operation.

## Novelty relative to prior work

Ali Romman's #6509 provides the earlier reversible conservative Gaussian rounding and stronger-invariant contract. Nick Petalas's #6619, building on ywz65's #2589, proves the zero-slack obstruction and asks for the least outward allowance. The earlier affine-period/conserved-center result restricts its lower bound to its stated family; this construction uses a different global matching.

The separate finite Hall package proves necessary forward lower bounds, most strongly `sqrt(78)-sqrt(73)`. This package supplies a constructive forward upper bound `1/2` and solves the **bilateral** problem. It does not prove a universal forward-only lower bound `1/2`. The exact predecessor heads, paths and hashes are retained in the package.

## Base and reproduction

Canonical base: `e54523517d0f03e58352e647c403a5af3e525a57`. All runtime code and evidence are in `research/global-bilateral-half-gaussian-rounding/`; Python 3.12 standard library, no solver or network dependency.

```sh
python3 -B scripts/research_package.py --package research/global-bilateral-half-gaussian-rounding --check-only
python3 -B scripts/research_package.py --package research/global-bilateral-half-gaussian-rounding
```

Standalone commands are listed in the README. The public verifier reports `PASS_GLOBAL_HALF_KERNEL`; the proof-role verifier reports `PASS_STAGGERED_BIJECTION_PROOF_IDENTITIES`. Exact independent checks cover half-grid involutions, complete finite balls, all sixteen lower corners, both inverse compositions, large integers, attaining sequences and deliberate failed designs. Normal and optimized executions are recorded. These checks corroborate the universal written proof; finite coverage is not offered as a substitute for it.

## Limitations and open obligations

The exact forward-only optimum remains between the finite Hall lower bound and `1/2`. No selected caller, tensor-stage commutation, dirty-port wrapper, fixed-width overflow bound, fixed-tape tariff, recursive precision budget or all-size compiler transfer is admitted. The arithmetic kernel has unbounded integer inputs; a machine-model implementation must pay its complete costs. The stronger native identities fail for this construction and require separate work.

## Kappa status

**No new kappa.** The pinned selected `kappa = 363005817/100000000000` and all five framework assumptions remain unchanged. The full multiplication bound remains conditional.

## Credit and assistance

Prepared for **@CubeJerry** with substantial OpenAI ChatGPT/Codex assistance. The root supplied the construction, a separate proof role developed and challenged the all-input proof, a separate implementation role tested the mechanism, and the root checked an independently written implementation and the actual Gaussian interfaces. Shared proposed formulas are disclosed; no blind, human or formal-kernel review is claimed.

Credit Ali Romman (#6509), Nick Petalas (#6619), ywz65 (#2589), and the earlier finite Hall and affine-period packages. The preserved notices and exact source pins identify predecessor contributions. Apache-2.0.
