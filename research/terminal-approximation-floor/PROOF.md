# A robust scalar-ADD floor for two-stage terminal codes

This contribution was produced by Nick Petalas. Apache-2.0.
Claim type: scoped proof, conditional on the cited physical-code identity.
Independent human and formal proof-kernel review are unclaimed.

## Contract and cited premise

Use Cinna Davis's [PR5065 proof](../two-stage-coded-terminal/PROOF.md),
building on Dillon's PR4933 and Dugongue's PR4929. Its exact marker identity
is a premise here. We do not re-establish or independently validate it.

For two distinct stage blocks and signs epsilon, eta in {+1,-1}, write

```text
J_f = Q_f^-1 C_t,f^epsilon C_s,f^eta Q_f,
m = number of negative signs,
alpha_m = 1/(8*13^m),
R_f = 4^(f-1).
```

The cited proof restricts input digit column one to address zero and output
digit column one to address 2048, inside owner block (0,1). The resulting
submatrix is `-i alpha_m N^(tensor(f-1))`. Row zero of N has precisely the
four entries `(1,-i,i,1)/2`, on inputs `(0,1,16,17)`. Consequently the selected
row in the restriction has exactly R_f nonzeros, all of modulus
`alpha_m/sqrt(R_f)`, and squared Euclidean norm `alpha_m^2`.

The row statement follows directly by tensoring the cited row. It needs no
new code census or assumption that an owner-coefficient sum is tensorized.

The approximation model is a linear straight-line program using whole-field
scalar ADD/SCALE, monomial address maps and owned COPY/CLEAR. Its scalars may
be arbitrary complex numbers. It may use dirty helpers and owned scratch;
all arbitrary inputs are included as independent coordinates of its linear
map. Count every scalar ADD. No Gaussian transform, dense free linear map,
nonlinear rounding, intermediate measurement or free coordinate projection
is part of the alphabet. The projections above are proof devices only.

Let A_f denote the program's designated output map. Compare it with J_f on
the required bank coordinates, extended by zero coefficients on independent
scratch inputs. The norm below is the induced Euclidean operator norm. In
particular, the claim concerns a uniform linear approximation on arbitrary
inputs, not accuracy at a finite list of test inputs.

## The quantitative bound

For every integer f >= 1 and every such program using g >= 0 ADDs,

```text
||A_f - J_f||_(2->2)^2
    >= alpha_m^2 max(0, 1 - 2^g/R_f).                 (1)
```

Initially each scalar state coordinate depends on at most one independent
input coordinate. A monomial permutes those coordinates and multiplies them
by scalars; SCALE preserves their support; COPY and CLEAR cannot enlarge the
maximum support. One ADD forms a union of two supports, and hence at most
doubles that maximum. After g ADDs, every output row has support at most
2^g. Arbitrary coefficients, cancellations and dirty scratch do not invalidate
this upper bound.

Restrict A_f to the same input and output coordinates used in the cited
marker identity. A row restriction cannot increase its support. If 2^g<R_f,
at least R_f-2^g of the target row's nonzero positions are absent from the
approximating row. Each contributes exactly alpha_m^2/R_f to the squared
row error. Any errors on retained or extra positions are nonnegative. Thus
the squared row error is at least the right-hand side of (1).

Coordinate restrictions are orthogonal projections of norm one, and a row's
Euclidean norm is at most the induced operator norm. The full error therefore
dominates this restricted row error. If 2^g>=R_f, nonnegativity proves (1).
This also covers f=1, where the displayed lower bound is zero.

The sparse-row inequality used here is sharp: retain any s of the R_f exact
target coefficients, and set all other coefficients to zero. Its squared
error is exactly alpha_m^2(1-s/R_f). This is sharpness of the row argument.
It does not construct a full decoder or prove attainability of (1) by a word.

## A fixed positive tolerance preserves the exact floor

For f>=2, suppose g<2(f-1). Integrality gives
`2^g <= R_f/2`. Therefore (1) implies

```text
||A_f-J_f||_(2->2) >= alpha_m/sqrt(2).                (2)
```

Every error tolerance strictly less than alpha_m/sqrt(2), including
alpha_m/2, forces `g>=2(f-1)`. The strict endpoint matters: (2) does not
exclude equality at alpha_m/sqrt(2). For f=1, the ADD floor is zero.

The actual negative banks 0 and 8 in the cited proof have terminal codes
`C_32 C_31^-1` and `C_1^-1 C_0`. Their unique exact postdecoders reverse
the factors and invert them, so each still has exactly one negative sign.
For both actual postdecoder targets, m=1 and alpha_m=1/104. Thus even the
relaxed requirement

```text
||A_f - required_postdecoder_f||_(2->2) <= 1/208
```

requires at least `2(f-1)` ADDs at every positive width. This is the same
ADD floor previously available only for exact decoding.

For any fixed g, (1) also gives
`liminf_(f->infinity) ||A_f-J_f||_(2->2) >= alpha_m`.
The program and its scalar coefficients may vary with f while its ADD budget
stays fixed. Thus even width-dependent coefficients cannot supply a uniform
linear approximation with error bounded strictly below 1/104 for the two
actual postdecoders. The liminf assertion is a lower bound, not an optimum.

## Scope and evidence

The new step is (1), its quantitative tolerance and its actual-bank
specialization. The marker identity, physical bank labels and exact support
obstruction retain Cinna Davis's credit. Dillon, Dugongue, JoyboyBrian,
Cao Yifan, zxv, Jacob Alan Sussman, Ryanson Jonathan and the retained
native/controller/compiler lineage retain their predecessor credit.

The exact verifier checks the new sparse-row inequality using every support
through sixteen columns, Gaussian coefficient perturbations, bounded tensor
rows and integer corollary comparisons. These are finite corroboration of
the written proof. It authenticates, but never executes, the cited predecessor
proof. No predecessor result is audited or recertified by this contribution.

We do not prove a paid Gaussian decoder minimum, a bound for nonlinear rounded
programs, a relative error bound for the entire terminal operator, or a whole
controller obstruction. A changed entrance/exit, recursive job family or
operation alphabet requires a different argument. Physical precision, storage,
routing, native all-column correctness, compiler and outer admission remain
inherited or unresolved. The selected frontier is unchanged.
