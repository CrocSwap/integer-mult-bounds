# Formalization inventory

Checked with Lean 4.31.0 and its bundled `Std` library. No mathlib or additional
packages are required. The proofs use the Lean kernel, integer arithmetic, and
`omega`. There are no added axioms and no omitted proofs. Printed dependencies
are standard Lean foundational axioms (`propext`, `Classical.choice`, `Quot.sound`).

`GInt` is an integer-coordinate model of the Gaussian integers. The operations
in this module are addition, the phase rotation i, and multiplication/division
by pi = 1+i. We do not formalize the entire Gaussian ring or its embedding into
the complex numbers.

| Declaration in `GaussianParity` | Mathematical content |
| --- | --- |
| `residue_zero_iff` | rho(z) = (re(z)+im(z)) mod 2 vanishes iff pi divides z |
| `dividePi_exact_iff` | Implemented integer quotient reconstructs its input exactly iff the pi divisibility guard passes |
| `dividePi_mulPi` | Division reverses multiplication by pi |
| `butterfly_integral_iff` | Both numerators of C=(iI+X)/pi are pi-divisible iff rho(u)=rho(v) |
| `butterfly_exact` | The division certificate reconstructs both butterfly numerators |
| `butterfly_sameResidue` | The admissible pair lattice is stable under the same pair's butterfly |
| `butterfly_square` | C squared is swap on an admissible pair |
| `butterfly_fourth` | C to the fourth power is the identity on an admissible pair |
| `inverseButterfly_eq_swap` | The wrapper -i Z C Z implements X C on an admissible pair |
| `inverseButterfly_after` | The inverse wrapper undoes the butterfly |
| `residue_mulI`, `residue_add`, `residue_mulPi` | Parity transfer rules for phase, addition, and pi factors |
| `cross_parity_example` | The pair (1,i) passes the Gaussian guard despite differing component parity |
| `changed_pairing_obstruction` | Re-pairing can invalidate the next stage, even when the first stage was admissible |
| `doubleButterfly_joint_parity` | The four integer coordinates of 2C(u,v) share the parity of the sum of four input coordinates |
| `sharedDefect_is_bit`, `sharedDefect_zero_iff` | The common defect is one bit and vanishes exactly when the Gaussian guard passes |
| `shared_defect_reconstruction` | All four integer numerators N satisfy N=2(N/2)+epsilon with the same retained bit, including negative inputs |
| `doubleButterfly_exact` | Those coordinates equal twice the exact butterfly outputs when its guard passes |
| `halfHadamard_exact_iff` | The real half-Hadamard requires both coordinate parities to agree |
| `cross_parity_fails_halfHadamard` | The pair (1,i) fails the real half-Hadamard guard |
| `piIter_add`, `piIter_commute`, `piIter_injective` | Exact denominator iteration and cancellation |
| `SameValue.refl`, `.symm`, `.trans` | Cross-multiplication defines an equivalence for exact fractions z/pi^e |
| `certifiedButterfly_contract` | Success divides pi exactly; failure retains numerators and increments the denominator tag |
| `certifiedButterfly_refines` | Both branches represent the same exact normalized butterfly outputs |
| `certifiedButterfly_exponent_bound` | One step keeps or increments the denominator exponent by one |
| `raiseTo_sameValue` | Raising a denominator tag with a matching pi factor preserves exact value |
| `alignedButterfly_input_exact`, `alignedButterfly_refines` | Unequal input tags can be aligned and passed through the total exact step |

The fraction semantics is the explicit cross-multiplication relation
`pi^f z = pi^e w`; its cancellation and equivalence laws are checked. The total
algorithm charges no machine cost in this formalization. Aligning denominator
tags requires multiplication by pi powers, and quotienting pi requires integer
arithmetic. Neither operation should be described as free. No claim about an
asymptotic multiplication exponent or a full recursive-network theorem is
formalized here.

`GaussianLattice.lean` adds the pi-power/binary-power ideal hierarchy, arbitrary
depth conversion to binary denominator 2^ceil(D/2), a sharp impulse obstruction
at one coarser binary bit, and the odd-level parity constraint that supplies a
full binary factor when two such numerators are multiplied. These are exact
arithmetic/lattice statements, not a formalization of the whole tensor network.

From PowerShell, run `verify.ps1 -LeanExe <path-to-lean.exe>`.


## Lattice module

| Declaration in GaussianParity | Mathematical content |
| --- | --- |
| mulPi_square, repeatPi_even, repeatPi_odd | pi^2 = 2i and even/odd powers |
| pi_even_ideal, pi_odd_ideal | Exact positive ideal hierarchy |
| even_binary_conversion, odd_binary_conversion | Explicit inverse-lattice conversion via integer cross multiplication |
| binary_grid_conversion | Universal binary grid with ceil(D/2) extra bits |
| odd_binary_numerator_parity | Odd converted numerators retain the Gaussian parity constraint |
| even_grid_sharp, odd_grid_sharp | The immediately coarser binary grid cannot represent the impulse numerator 1 |
| gaussianMul_pi_pi, two_pi_factors_binary | Two pi factors give one full binary cancellation |

The tensor coefficient formula is a written tensor-product derivation. The
lattice theorem is fully formalized for arbitrary Gaussian numerators and
denominator exponents, without assuming a multiplication complexity theorem.
