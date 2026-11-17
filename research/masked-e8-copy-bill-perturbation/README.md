# Scalar perturbation costs at one 93-line E8 puncture

This package proves that the coordinate completion in ToikY's
[PR #1609](https://github.com/CrocSwap/integer-mult-bounds/pull/1609)
has eight separate COPY ranks of nine for **every complex perturbation scalar**.
It also gives a bound for every fixed eight-term basis whose dual directions
are E8 roots. Its COPY bill can fall by at most one from its own all-pairs
comparator, and can fall only at `c = -2/3` or `c = 2/3`.

The claim type is a scoped written proof supported by exact finite
certificates. The root-direction classification below is finite evidence used
in that proof. No best completion, all-pairs optimum, physical supplier, new
kappa or complete multiplication theorem is claimed.

## Fixed object and accounting model

Represent the 120 E8 root lines by doubled roots `q_i` of squared norm eight,
with first nonzero coordinate positive. Representatives are lexicographically
sorted. Let `r_i = q_i/2`, and fix

```text
q_j = (2, 2, 0, 0, 0, 0, 0, 0)
v   = (1,-1, 2, 0, 0, 0, 0, 0).
```

Delete the 27 lines satisfying `q_i dot q_j = 0` and `q_i dot v != 0`.
Call the 93 remaining lines `L`, and let `R` have their rows `r_i`.
This is exactly the puncture and normal of #1609. Its sharp arbitrary-deletion
threshold and neighborhood-span theorem are credited predecessor results;
this package does not rerun the E7-flat census or prove that threshold again.

The required entries of `D T^T` are those of `2 R R^T` on the diagonal and
on orthogonal root pairs. The binary pairing matrix is

`N_it = 1` if `(q_i dot q_t)/4` is even, and `0` otherwise.

For term `k`, let `S_k = supp D_k`, `U_k = supp T_k`. Its price is
`rank_F2 N[S_k,U_k]`. The scalar COPY bill is the sum of those prices.
This is the separate-term model of DreamingOfClouds's #717. It does not
include gathering, restoration, frame changes, hosting or recursive costs.

## The perturbation family

Fix any invertible complex `8 x 8` matrix `A`, with columns `a_k`.
Write `b_k` for the columns of `A^{-T}`, so `a_l dot b_k = delta_lk`.
Use ordinary transpose throughout. Define

```text
D_ik    = r_i dot a_k
T_ik(0) = q_i dot b_k
T_jk(c) = (q_j + c v) dot b_k,
```

leaving all other rows of `T` unchanged. Then

`D T(c)^T = 2 R R^T + c (R v) e_j^T`.

Indeed, `A A^{-1} = I` gives the all-pairs identity at `c=0`, and the
changed row contributes `c R A A^{-1} v`. Every required entry in column
`j` has `r_i dot v = 0` by the deletion rule and `q_j dot v = 0`.
Thus every `c` gives masked exactness. For nonzero `c`, precisely 56
unmasked entries change, all in column `j`. The verifier checks this
annihilation directly and counts the 56 nonzero products. This extends the
source's `c=1` example; it is not a new construction of the puncture.

## Coordinate bill for every scalar

Take `A=I`. The only changing row is

`T_j(c) = (2+c, 2-c, 2c, 0, 0, 0, 0, 0)`.

Its support changes only at `-2,0,2`. The verifier checks these three values
and `1` as a representative of their complement, with exact rational
arithmetic and two different binary-rank computations.

| Scalar class | Nonzero coordinates of `T_j(c)`, numbered 1 to 8 | Eight COPY ranks | Total |
|---|---|---|---:|
| `c = -2` | 2, 3 | `9,9,9,9,9,9,9,9` | 72 |
| `c = 0` | 1, 2 | `9,9,9,9,9,9,9,9` | 72 |
| `c = 2` | 1, 3 | `9,9,9,9,9,9,9,9` | 72 |
| `c` outside `{-2,0,2}` | 1, 2, 3 | `9,9,9,9,9,9,9,9` | 72 |

These are all support classes over the complex numbers, since each coordinate
is a linear polynomial with its stated single root, or is identically zero.
All other factor entries are constant. Therefore the four exact finite
checks prove COPY72 for every `c`, and the power bill is `8*9^p` for every
positive `p`. Varying only this scalar cannot improve the coordinate bill.

## A column-deletion lemma

Fix a source support `S` and a target support `U`. Changing membership of
one target `j` changes `rank N[S,U]` by at most one. Adding a target cannot
lower rank. A loss from the comparator at `c=0` therefore requires

`q_j dot b_k != 0`, `v dot b_k != 0`, and
`c = -(q_j dot b_k)/(v dot b_k)`.

Moreover, if column `j` of `N[all 120 lines,U]` is in the span of the other
columns, it remains in that span after restriction to any `S`. Deleting it
then costs zero rank on every `S`. Equality of the ranks with and without
`j` is precisely this column-dependence test. This argument needs no
hypothesis on `S` or on the field of the complex factor coefficients.

## The root-direction certificate and its consequence

For each of the 120 root directions `z`, set
`U(z) = {i in L : q_i dot z != 0}`. The verifier computes both ranks using
all 120 source rows, including the deleted ones. This larger row set makes
the column-dependence conclusion valid for every possible source support.
The complete 120-row certificate is printed in its JSON receipt.

| Rank on `U(z)` | Rank on `U(z) \ {j}` | Root directions |
|---:|---:|---:|
| 8 | 8 | 27 |
| 9 | 8 | 3 |
| 9 | 9 | 90 |

The three critical directions and their cancellation scalars are exactly

| Direction `z` | `q_j dot z` | `v dot z` | Scalar cancelling the target coefficient |
|---|---:|---:|---|
| `(2,2,0,0,0,0,0,0)` | 8 | 0 | None |
| `(2,0,2,0,0,0,0,0)` | 4 | 6 | `-2/3` |
| `(0,2,-2,0,0,0,0,0)` | 4 | -6 | `2/3` |

**Consequence.** Suppose each `b_k` is a nonzero complex multiple of an E8
root. Let `C_A(c)` be the sum of the eight COPY ranks for the fixed `A`.
Then

```text
C_A(c) >= C_A(0)       if c is outside {-2/3, 2/3},
C_A(c) >= C_A(0) - 1   for every complex c.
```

Proof: each of the 117 noncritical root supports either omits the target
or has a redundant target column for every `S_k`. A cancellation therefore
cannot reduce its price. New support can only increase a price. The critical target-root direction has zero
perturbation coefficient and cannot cancel. At each of the two remaining
scalars only its corresponding critical direction can lose rank, and that
loss is at most one. The dual vectors form a basis, so no two terms use the
same root direction. This proves both inequalities.

This is a necessary bound, not attainment. A critical direction can still
have a redundant target column after restriction to its actual `S_k`, and
other terms can become more expensive. No lower bound for `C_A(0)` is
claimed, so these inequalities do not determine the best masked decoder.

## Reproduce and verification limits

From the repository root, using CPython 3.12 and the standard library:

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/masked-e8-copy-bill-perturbation/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/masked-e8-copy-bill-perturbation/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/masked-e8-copy-bill-perturbation
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/masked-e8-copy-bill-perturbation --check-source-history
```

The last command checks the committed package, so run it after committing.
The direct verifier emits a deterministic JSON receipt with all 120 direction
records and SHA256 hashes of its five package files, followed by
`PASS_MASKED_E8_COPY_BILL_PERTURBATION`. It writes nothing. All assertions
used for acceptance remain active under `-O`.

The verifier also checks all 512 binary `3 x 3` matrices and their 1,536
single-column deletions with both rank algorithms. It rejects three invalid
rank inputs, detects a diagonal error from perturbing by `q_j` instead of
`v`, and checks a restriction where a critical direction gives no saving.
The four coordinate representatives each check all 8,649 product entries.

No other deletion set, non-root dual-direction classification, extra-term
completion, physical word, native admission, selected cold replay, Lean or
Docker run is supplied. Independent human and formal proof-kernel review
are unclaimed. The optional selected-baseline orientation command failed
locally because this sparse checkout omits
`research/global-lambda-lowering/LICENSE`; it is outside this package's
self-contained mathematical inputs.

Implementation decisions: all loops range over fixed finite sets, at most
120 root lines, eight coordinates or 512 small matrices. Functions are below
60 lines. Python's managed runtime allocates dynamically, a deviation from
Power of Ten rule 3. Matrix dimensions and bit widths are bounded by these
constants, and the script has no solver, network or subprocess. If this is
extended to external inputs, enforce those capacities before allocation.

## Open next questions

Can the column-dependence test be characterized for every complex direction
`b`, rather than the 120 root directions? This would identify exactly where
the one-term rank-loss argument still permits scalar savings in a general
fixed basis. A feasible first step is to classify the hyperplane sections
`{i in L : q_i dot b = 0}` and test the target-column dependence of each
complement. The blocker is complete enumeration over complex directions;
a sampled list would establish only sampled coverage. This is a proposed
follow-up, not a result of this package. The structured question is in TASK.json.

## Credit

This contribution was produced by Nick Petalas. ToikY's #1609 supplies the
fixed puncture, normal, `c=1` witness and open scalar-variation question.
Philipp / mightyOil's #1191 supplies the local spanning mechanism.
DreamingOfClouds's #717 supplies the separate-term COPY model. The retained
E8 root/decoder lineage, including icekylinx, Joel Pulikkan / GamingPuzzled
and Douglas Colkitt, retains its predecessor credit. No predecessor executable
is imported or modified. New work is Apache-2.0.
