# Error contract for the mixed caller

## Domain and units

Use the exact `CONTROLLER.json` from PR6398. There are 34 arbitrary fields,
18 stages and 570 instructions. Each field is a complex Hilbert space H.
Q and D1,...,D18 are pairwise commuting unitary operators on H, and Q^4=I.
Use the maximum of the 34 field 2-norms. This is not the maximum coordinate
norm. The constants do not depend on the dimension of H.

Each scalar ADD or SCALE has one additive output error of norm at most e_s.
Each of the four ordinary operations inside a LAMBDA has an error of norm
at most e_s, measured on its updated half-field. Each LOCAL has two output
errors, each at most e_l. QUERY has one output error at most e_q. Each output
of IDLE or IDLE_ONE has error at most e_i. The error may depend on all prior
data. SWAP and Q_POWER are exact permutations. Initial field norms are at
most M. All errors are measured against the exact operation on the actual
approximate input. No independence or cancellation of errors is assumed.

This is an input contract for a native implementation. It does not prove
that a physical implementation meets these error bounds. In particular,
a bound on one rounded coordinate is not a bound on a complete field.
For n coordinates, coordinate error u gives only sqrt(n)*u in this norm.

## Exact operator bounds

The spectral projections of unitary Q for 1,i,-1,-i are orthogonal. Each
D_j preserves these projections. Restrict the caller to one projection.
Each matrix cell is now a polynomial in the commuting D_j, with exact
Gaussian rational coefficients. For a cell p, define

    b(p) = sum over monomials of (abs(real coefficient)+abs(imag coefficient)).

The operator norm of p is at most b(p). Take the maximum of this bound over
the four central projections for EACH CELL, then sum a row. This order is
needed: a maximum of four row sums alone would not justify the field norm.
The result bounds the row operator from the maximum field norm to H.

`bounds.py` computes all 571 prefix matrices by left multiplication. It
computes all 571 suffix matrices by left multiplication of transposed
instructions in reverse order, then transposes the matrices back. A
transpose, rather than an adjoint, preserves the exact polynomial cells.
All polynomial additions combine equal monomials before the norm bound.
Stage variables stay distinct; setting them all to one is not an upper
bound. The separate lower witness below makes that specialization only to
prove insufficiency.

The largest prefix row bound is 18, at boundary 279, field 0. The exact
endpoint is diagonal, with unitary monomials. The verifier checks every
endpoint cell in each of the four central projections. This repeats the
endpoint identity only as a premise of this error proof. PR6433 owns the
independent audit of that identity.

## Literal normalization and error injection

On a translation pair let a=(1+i)/2 and b=(1-i)/2. The four operations are

    x <- x-i*y; x <- a*x; y <- (1+i)*y; y <- y-i*x.

They give (a*x+b*y,b*x+a*y). Conjugate the coefficients for the inverse.
The four separate error columns have squared operator norms 1,2,1,1.
Thus the complete normalizer error is at most (3+sqrt(2))*e_s < 9*e_s/2.
The verifier computes all four real input columns and all error columns
for both signs. This includes the error from each ordinary operation; it
does not treat a normalizer as one free exact primitive.

Let S_t be the suffix after instruction t, and J_t its updated fields.
An injected error vector d_t gives final error S_t*d_t. Apply the cell
bounds to each updated field, with weight 9/2 for a normalizer, and sum
all instruction contributions. `RESULT.json` retains all 34 rows for four
separate error classes. The maximum coefficients are

| Error class | Maximum coefficient |
| --- | ---: |
| Ordinary scalar operations and normalizers | 795/2 |
| Native LOCAL outputs | 28 |
| Thin QUERY output | 18 |
| Whole idle outputs | 28 |

Consequently the final maximum field error is at most

    (795/2)*e_s + 28*e_l + 18*e_q + 28*e_i.

The row-specific arrays permit smaller budgets when the four tolerances
differ. With a common tolerance e, the largest row sum is 943/2 < 512.
To obtain final error below 2^-p, it is sufficient to set every primitive
tolerance to 2^(-p-9). These are nine guard bits in this field-error contract.

## Why eight guard bits do not suffice

Take H=C and Q=D1=...=D18=I, which is in the declared operator domain.
Set all normalizer errors to zero. A separate rational recurrence propagates
one output coordinate backwards through the literal instructions. At every
other allowed error site, choose error +e or -e with the sign of that site's
suffix coefficient. An independently executed forward recurrence injects
those errors. The resulting output error is exactly 307*e. Thus e=2^(-p-8)
can exceed 2^-p. This is an exact adversarial witness, not a random trial.
It proves that nine is the least uniform integer guard count for the
specified domain and error model. It does not prove that 943/2 is the best
real amplification constant, or that an actual native implementation can
realize the witness errors.

## Intermediate magnitudes

At a boundary t, let only errors up to t be nonzero. Their final error is
at most (943/2)*e. If P_t is the exact prefix and U the unitary diagonal
endpoint, then S_t=U*P_t^-1. The intermediate error is P_t*U^-1 times that
final error. The maximum field norm of U^-1 is one. Thus every caller
boundary has norm at most 18*M+8487*e. The partial normalizer operators
have norm at most two. Its at most four local errors contribute at most
8*e to an internal boundary. A conservative internal bound is therefore
36*M+16982*e. The native LOCAL, QUERY and IDLE interiors are outside this
contract. Their implementations must supply separate bounds.

## Scope

The proof gives dimension-independent constants under explicit unitary
and error hypotheses. It supplies no finite tape layout, rounding scheme,
coefficient producer, owned-erasure permission or full compiler admission.
It changes neither the signed recursion invoice nor kappa. The five
framework assumptions remain. A proof kernel and independent scientific
review have not checked this argument.
