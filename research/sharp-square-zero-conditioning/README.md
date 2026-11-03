# Sharp Euclidean conditioning for square-zero error words

This contribution was produced by Nick Petalas. Apache-2.0.
Claim type: scoped written proof with exact finite corroboration. No new kappa.

For K square-zero coefficient-error factors with total Euclidean error norm
at most rho, the exact worst-case product norm and inverse norm are

```
E_K(rho) = ((sqrt((rho/K)^2+4)+rho/K)/2)^K.
```

The exact worst-case condition number is E_K(rho)^2. Alternating upper and
lower two-dimensional shears attain all three bounds simultaneously. The
result holds over R or C, in every dimension at least two, for arbitrary
square-zero ranks and noncommuting factors. It has no small-error threshold.
[PROOF.md](PROOF.md) gives the quantified statement, proof and boundary cases.

Ali Romman's [PR5288](https://github.com/CrocSwap/integer-mult-bounds/pull/5288)
supplies a sufficient bound `product(1+d_i)` at this interface. The new
Euclidean bound is `product Phi(d_i)`, where
`Phi(t)=(sqrt(t^2+4)+t)/2`. It is strictly smaller for any nonzero error word.
At fixed total error rho, the sharp length-independent norm supremum is
exp(rho/2), improving the sufficient exp(rho) envelope in this Euclidean
specialization. The conditioning result is new; the elementary single-shear
singular-value formula and concavity argument are classical.

For example, two factors of norm 3/2 have sharp norm and inverse norm 4,
compared with the prior sufficient product 25/4. Their sharp condition
number is 16, compared with the corresponding product estimate 625/16.
These are exact analytic bounds and rational witnesses, not runtime measurements.

## Reproduce

From the repository root with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/sharp-square-zero-conditioning/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/sharp-square-zero-conditioning/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/sharp-square-zero-conditioning
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/sharp-square-zero-conditioning --check-source-history
```

Any CPython 3.12 path can replace the displayed local interpreter. The direct
verifier prints `PASS_SHARP_SQUARE_ZERO_CONDITIONING` in a generated JSON
receipt that binds every package file by SHA256. It writes no files and imports
no predecessor implementation. Normal and optimized commands run the same checks.

Exact rational Gaussian elimination computes inverses. All principal minors
of rational Gram differences certify norm upper bounds, independently of the
new formula. Gram eigenvectors certify attainment. Varied error words include
noncommuting orientations, orthogonal rational changes of basis, square-zero
maps of rank two, complex shear realifications and total error above one.
A separate two-slot polynomial inequality checks strict budget smoothing.
Semantic controls delimit nilpotency, norm choice, singular-vector alignment,
product order, dimension, budget and the zero-error boundary.

The universal statement rests on the written proof. The finite checker does
not exhaust all real/complex matrices or use a formal proof kernel. No
predecessor census is rerun. There are no external mathematical runtime inputs.
[SOURCES.json](SOURCES.json) pins the credited source statements as provenance;
the selected record and catalogue are historical orientation metadata.

## Scope and limitations

The uniform-transfer-audit card changes scope to a sharp numerical-interface
result. This improves a conditioning envelope rather than providing the
card's complete all-size caller. The selected binding-only control passed at
canonical main 7c49fe32c55de02c2c873655c804b16e4c3fef0a, priority revision 8.
The selected record names PR6030 and kappa 0.003125804; it is unchanged.

Only the Euclidean norm has this factor. The previous arbitrary-induced-norm
theorem remains credited in its larger norm domain. Arbitrary errors that
change the shear structure are outside this theorem. The physical-prefix
corollary is an upper bound for a specified exact word; the sharpness claim
concerns the unrestricted square-zero interaction-error domain.

No actual coefficient storage/rounding policy, additive-noise precision guard,
operator-defect optimum, reversible rounded-grid kernel, physical caller,
native/compiler/tape/stock cost, signed supplier bill or multiplication theorem
is supplied. Independent human and formal proof-kernel review are unclaimed.
Lean, Docker and the selected scientific cold replay are unrun. All five
framework assumptions remain.

## Open next questions

- Apply the sharper suffix norms to one production word with a specified
  coefficient policy and additive-noise budget. First bind its Euclidean
  interaction errors and physical access/restoration costs. A computable
  production prefix envelope and actual arithmetic kernel remain blockers.
- Determine a sharp operator-defect bound for the same fixed K and total
  budget. Norm growth alone does not determine `||R-I||`; even the one-factor
  defect is d, while the norm increment is Phi(d)-1. No claim is reserved.

## Credit

Ali Romman [#5288](https://github.com/CrocSwap/integer-mult-bounds/pull/5288)
supplied the square-zero coefficient-error contract and sufficient ordered
product bounds. ywz65 [#2701](https://github.com/CrocSwap/integer-mult-bounds/pull/2701)
supplied interaction coordinates and the general simultaneous-error interface.
Vlado Vojdanovski [#1673](https://github.com/CrocSwap/integer-mult-bounds/pull/1673)
and the Gaussian/Toeplitz lineage credited there retain their circuit and
precision context. Nick Petalas #5153's separate endpoint refinement is
background, not a result claimed here. Singular-value decomposition, the
single-shear singular values and Jensen's inequality are classical.
The new total-budget theorem, attaining word and exact checker were produced
by Nick Petalas. Predecessor files and credit lines remain unchanged.

## Implementation constraints

The new checker has no recursion, subprocess, network, dynamic code execution
or external solver. Matrix dimension is at most four, word length at most 12,
and matrix entry numerator/denominator bit lengths at most 8192. All loops
have bounds from these limits or fixed finite alphabets. Explicit exceptions
retain every mathematical check under optimized Python. Each function fits
within 60 physical lines. Warning-strict normal/optimized execution and source
compilation supply the available diagnostics; separate lint/type analysis is
unrun. Python Fraction/integer allocation is a Power of Ten rule-3 deviation
within these bounded finite fixtures. The script is a certificate checker,
not a fixed-allocation runtime implementation.
