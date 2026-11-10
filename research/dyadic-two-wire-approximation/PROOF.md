# Sharp approximation by exact Gaussian-dyadic two-wire gates

This scoped proof and its application were produced by Nick Petalas.
New material is Apache-2.0.

Put D = Z[i,1/2]. Norms below are Euclidean operator norms on complex
coordinate vectors. The target U is any real 2 by 2 orthogonal matrix;
in particular it can be a real rotation or a normalized real butterfly.
Write m = max over i,j of |U_ij|.

## The approximation theorem

For every such U,

    min { ||V-U||_op^2 : V* V = I_2, V in D^(2 by 2) } = 2(1-m).       (1)

A real signed permutation attains the minimum. Complex coefficients and
arbitrarily large dyadic denominators cannot improve it. Consequently the
worst minimum over real O(2) is 2-sqrt(2), attained by balanced butterflies.

### Classical dyadic unit-vector lemma

A unit vector in D^2, regarded as a real four-coordinate vector, is either
a signed coordinate vector or has all four coordinates equal to +/-1/2.

Choose its least common denominator 2^k. Its integer numerators satisfy

    x_1^2 + x_2^2 + x_3^2 + x_4^2 = 4^k.

If k>=1, the number of odd numerators is divisible by four, by reduction
modulo four. Minimality excludes zero odd numerators, so all four are odd.
For k>=2 their squares sum to 4 modulo eight, whereas 4^k is 0 modulo
eight, a contradiction. For k=1 the four odd squares sum to four, forcing
each numerator to be +/-1. For k=0 only a signed coordinate vector is
possible. This is the classical small-dimensional dyadic-unitary argument,
not a new group-classification claim.

### Lower bound

Let u=(a,c) be the first column of U, and v the first column of V.
Real two-dimensional orthogonality gives

    a^2+c^2=1,     max(|a|,|c|)=m.

If v is a signed coordinate vector in its four real components, then
Re(u* v) <= m. If its four real components are all +/-1/2, then

    Re(u* v) <= (|a|+|c|)/2 <= m.

Both vectors have norm one. Thus

    ||V-U||_op^2 >= ||v-u||_2^2 = 2-2 Re(u* v) >= 2(1-m).

This lower bound concerns the full complex operator norm, even though the
target is real. It does not discard imaginary leakage into either output.

### Attainment

Let delta=det U, which is +/-1. Choose p to be the signed coordinate
vector with u dot p = m. Set

    J = [[0,-1],[1,0]],      P = [p, delta Jp].

Then P is a real signed permutation and has the same determinant as U.
The matrix P^T U is a real rotation with both diagonal entries equal to m.
Therefore

    (P-U)* (P-U) = 2I - P^T U - U^T P = 2(1-m) I.

This proves (1), including the endpoints m=1 and m=1/sqrt(2). The latter
endpoint gives the worst-case statement because m>=1/sqrt(2).

## Arbitrarily many exactly restored dirty helpers do not help

Allow any finite h and any finite circuit of exactly unitary linear gates
over D on two active coordinates and h additional complex coordinates.
Every helper input is arbitrary and independent. Require the completed
linear map W to return every helper exactly to its initial value for every
input. There is no measurement, postselection, data-dependent control or
unobserved output outside this declared space.

Closure under multiplication gives W in U_(2+h)(D). Exact helper return
gives the block form

    W = [[A,B],[0,I_h]].

The bottom-right block of W*W is B*B+I_h, so unitarity forces B*B=0
and hence B=0. The top-left block gives A*A=I_2. Thus W=A direct-sum I_h
with A in U_2(D), and (1) applies without change. Its attaining P can simply
leave all helpers untouched. This is an all-size block-matrix argument;
the finite one-helper checks only corroborate it.

## Consequence for the rational-unitary FFT interface

Jose Manuel's PR4205 uses exactly unitary rational coefficient gates with
stored adjoint inverses. PROOF.md sections 2 and 3 specify rational phases
and butterflies [[a,bw],[b,-aw]], with a^2+b^2=|w|^2=1. Its dyadic data
rounding is a separate operation. Taking w=1 yields the real family covered
by (1). This is a self-posed denominator-elimination question about that
boundary, not a defect in the predecessor's rational construction.

For the explicit rational member of this algebraic family

    U = [[3/5,4/5],[4/5,-3/5]],

the optimum squared operator error is exactly 2/5. For any unit-scale real
butterfly with m<=4/5, the same model cannot meet error below sqrt(2/5),
regardless of the precision parameter, circuit length or count of exactly
restored helpers. At input radius R the corresponding worst-case absolute
error is R sqrt(2(1-m)). The operator-norm extremizer proves that statement;
it is not an assertion about every input.

Rational butterflies approaching a balanced Hadamard gate have optimum
squared error approaching 2-sqrt(2), rather than zero. Hence exact
Gaussian-dyadic unitarity at this restored two-coordinate boundary cannot
replace the rational coefficient approximation as its requested error
tends to zero.

Removing exact unitarity changes the question. For example the dyadic real
rotation-shaped matrix (5I+6J)/8 has norm square 61/64, while its squared
operator distance to (3I+4J)/5 is only 1/320. Nonunitary dyadic lifting or
rounded gates need their own stability and restoration budget. Joint gates
with additional non-restored active coordinates, global cancellation among
changed gates, Gaussian natives on large address spaces and other endpoint
contracts are outside this obstruction. No physical cost, recursive saving,
supplier admission or selected framework assumption is proved here.

## Classical credit and proof status

Alexis De Vos, Raphael Van Laer and Steven Vandenbrande,
[The Group of Dyadic Unitary Matrices, 2012, section 5](https://backoffice.biblio.ugent.be/download/2069554/2069555),
already describe the finite group U_2(D) of order 96. This package supplies
an elementary proof of the unit-vector fact needed for the approximation
formula. The new contribution claimed here is (1), its sharp gate-interface
consequence and the exact-restored-helper extension, in this repository's
arithmetic setting. No worldwide literature priority is claimed.

The all-real and arbitrary-helper quantifiers rest on this written proof.
The exact finite checker is corroboration and checks of the formula's
implementation. Independent human and formal proof-kernel review are
unclaimed.
