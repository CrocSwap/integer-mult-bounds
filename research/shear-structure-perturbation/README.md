# Shear structure removes the small-error invertibility restriction

**Scoped written proof with exact finite checks; no new kappa.**
If coefficient errors preserve each elementary shear, every changed linear
prefix remains invertible for every finite error size. The product bounds
below replace the small-total-error admission used for general gate errors in
[ywz65's PR #2701](https://github.com/CrocSwap/integer-mult-bounds/pull/2701).
They control forward prefixes, inverse prefixes, both operator defects, and
additive arithmetic noise. They do not assert that a rounded instruction
sequence is an invertible map of a finite grid.

The exact scientific base is `ff3cc58e370d0f678e529246f8c73e8094e18fcf`,
priority revision 7. The selected conditional kappa is 0.00302015 and is
unchanged. This changes the `uniform-transfer-audit` card to one numerical
interface lemma; no complete PR4100 caller is discharged.

## Theorem

Use an induced matrix norm and its compatible vector norm. Over R or C, let

```text
N_i^2 = 0,
A_i = I + a_i N_i,    Ahat_i = I + (a_i + e_i) N_i,
F_0 = Q_0 = I,
F_j = A_j ... A_1,    Q_j = Ahat_j ... Ahat_1,
D_i = e_i F_(i-1)^(-1) N_i F_(i-1),
d_i = ||D_i||,        P_j = product_(i=1..j) (1+d_i),
B >= max_j (||F_j||, ||F_j^(-1)||).
```

The coefficient errors are fixed. They need not be small, independent,
unbiased, or of one sign. The N_i need not commute. All Q_j are invertible,
and for every j,

```text
||Q_j||, ||Q_j^(-1)|| <= B P_j,
||Q_j-F_j||, ||Q_j^(-1)-F_j^(-1)|| <= B (P_j-1).
```

In particular, P_j <= exp(sum_(i<=j) d_i) is valid with no restriction on
that sum. The finite product can be evaluated with rational arithmetic when
the chosen norm data are rational.

For an arithmetic trajectory with arbitrary bounded or data-dependent noise,

```text
y_0 = x,
y_i = Ahat_i y_(i-1) + u_i,
||y_j-F_j x|| <= B [ (P_j-1)||x||
                   + sum_(i=1..j) (P_j/P_i)||F_i^(-1)u_i|| ].
```

One may replace each transformed noise norm by B||u_i||. Noise is evaluated
on the actual trajectory; no probabilistic cancellation is assumed.

## Proof

Since N_i^2=0, the exact and changed inverse gates are I-a_i N_i and
I-(a_i+e_i)N_i. Thus no finite coefficient error makes a gate singular.
Also A_i^(-1)N_i=N_i. With R_j=F_j^(-1)Q_j, multiplication in the given
order gives R_j=(I+D_j)R_(j-1). Conjugation preserves D_i^2=0, so
(I+D_i)^(-1)=I-D_i.

Submultiplicativity bounds both the forward ordered product and its reverse
inverse product by P_j. Expand either finite product and subtract its
constant term. The sum of the norms of all remaining ordered terms is at
most P_j-1. Multiplication by F_j or F_j^(-1) proves the four inequalities.
The exponential bound follows from 1+t <= exp(t) for t>=0.

For arithmetic noise, set z_j=F_j^(-1)y_j. Then
z_j=(I+D_j)z_(j-1)+F_j^(-1)u_j. An error inserted after step i is multiplied
only by later factors. Their norm product is P_j/P_i. Expand this recurrence,
subtract x, and multiply by F_j. This proves the trajectory bound.

The same proof applies to any square-zero N_i, including a block shear.
An elementary shear is the case N_i=E_(r,c), r!=c. If structural zeros or
diagonal ones may also change, the conclusion fails: perturbing I by
diag(-1,0) produces a singular matrix. The structure premise is essential.

## Exact evidence

The standalone checker uses Fraction arithmetic and Gaussian elimination for
the actual inverse matrices. It does not use the displayed inverse formula
to compute the tested inverses. It checks 24 noncommuting two- and three-row
circuits, 192 prefixes, 192 noisy steps, and 16 circuits with sum d_i>=1.
Five controls distinguish large supported errors, unsupported singular
errors, omitted higher-order terms, changed order, and an endpoint-only norm
bound. Finite checks support the written proof; they are not a formal proof.

With CPython 3.12 or later and no external packages:

```sh
python3 -I -W error -B research/shear-structure-perturbation/verify.py
python3 -I -O -W error -B research/shear-structure-perturbation/verify.py
python3 -B scripts/research_package.py --package research/shear-structure-perturbation
```

Both direct modes report `PASS_SHEAR_PERTURBATION`, 24 circuits, 192 prefixes,
192 noise steps, 16 large-budget circuits, and five controls. No selected
cold replay, native replay, compiler build, Lean build, or Docker run was used.

## Limits

The bound is sufficient and need not be sharp. Large P_j can make an error
estimate useless even though invertibility survives. This is not a numerical
accuracy guarantee at arbitrary precision. Gate coefficients and exact
prefixes are mathematical inputs. Overflow, integer bits, coefficient
generation, physical reads, movement, restoration, and the full outer bill
remain unpriced.

## Open next questions

The next useful task is to bind a production shear word and its actual
coefficient storage policy to N_i, e_i and the prefix norms, then compare
its finite error budget with the general bound. Start with one emitted local
tile. A specified arithmetic kernel and physical cost model are required.

## Credit

ywz65's PR2701 supplies the simultaneous-error interaction coordinates and
the general prefix/noise contract. Vlado Vojdanovski's
[PR #1673](https://github.com/CrocSwap/integer-mult-bounds/pull/1673) supplies
the Toeplitz circuit and precision context. Nick Petalas's
[PR #5153](https://github.com/CrocSwap/integer-mult-bounds/pull/5153) supplies
the separate endpoint-norm refinement and sharp B-power examples; that
refinement is not a result of this package. Nilpotent inverse formulas and
ordered-product estimates are classical. The contribution here is their
explicit structure-dependent contract at the retained rounding interface.

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
No independent human or proof-kernel acceptance is claimed.
