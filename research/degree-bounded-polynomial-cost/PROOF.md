# Uniform bounded-degree polynomial target costs

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped counting proof, conditional only on the cited exact
degree/cost theorem. Finite execution corroborates the formulas below.
No new multiplication exponent or native supplier is claimed.

## Contract and predecessor input

Let q be any prime power, K=F_q and R=K[t]. There are two data roles and
no auxiliary roles. A paid factor is I+u y^T with u in R^2 and y in K^2.
Arbitrary GL2(K) maps may occur freely anywhere in the word. Write C(M)
for minimum paid length and D(M) for the maximum entry degree of M.

The sampling measure here is uniform on

    S_N = {M in GL2(K[t]) : D(M)<=N},    N>=0.

Invertibility means that the determinant is a nonzero constant. Uniform
polynomial matrices without this condition are a different measure.

Nick Petalas's PR4784, exact head
4d0a6363fe4f45dd9a769f5b74d02fc5d9061ae3, proves the following input.
For g=|GL2(K)|=(q^2-1)(q^2-q), D>=1 and 1<=r<=D,

    #{M : D(M)=D, C(M)=r}
      = g (q+1)(q-1)^r q^(D-1) binom(D-1,r-1).

There are g degree-zero targets, all of cost zero, and |S_N|=g q^(2N).
Equivalently, conditional on positive degree D,

    C-1 has distribution Binomial(D-1,(q-1)/q).

Those statements and their normal-form proof are cited premises. This
package does not audit them or rerun their matrix census. Their original
proof text is pinned as the sole external mathematical input.

## The new probability-generating function

Put B(z)=q+q(q-1)z. Then the exact generating function for the present
uniform bounded-degree measure is

    G_N(z) = E[z^C]
           = q^(-2N) [1+(q^2-1)z (B(z)^N-1)/(B(z)-1)].

The quotient means the polynomial sum 1+B+...+B^(N-1). For N=0 it is
zero. At B(z)=1 its value is N, so no pole is part of the result. All
cost probabilities are the coefficients of this explicit polynomial.
In particular P(C=0)=q^(-2N), and costs above N have probability zero.

To prove the formula, sum the cited joint count over r at each D>=1:

    g^(-1) sum_r #{M:D(M)=D,C(M)=r} z^r
       = (q^2-1) z q^(D-1) (1+(q-1)z)^(D-1)
       = (q^2-1) z B(z)^(D-1).

Add the degree-zero contribution 1 and sum D=1,...,N. Division by
q^(2N) gives G_N. At z=1, B(1)=q^2 and the numerator is q^(2N), which
also confirms normalization. This is a finite polynomial identity.

## Closed first and second moments

Set e=q^(-2N). For every N>=0,

    E[C] = (q-1)N/q + (1-e)/(q+1),

    Var(C) = (q-1)N/q^2
             + 2(q-1)N e/[q(q+1)]
             - (1-e)(q-e)/(q+1)^2.

Here is a direct derivation that accounts for the exceptional degree-zero
case. Under the bounded-degree measure,

    P(D=0)=e,
    P(D=d)=(q^2-1)q^(2d-2-2N),    1<=d<=N.

Its tail is P(D>=j)=1-q^(2j-2-2N) for 1<=j<=N. Finite geometric sums give

    E[D] = N-(1-e)/(q^2-1),
    E[D^2] = N^2-2N/(q^2-1)+(q^2+1)(1-e)/(q^2-1)^2.

For example the second identity follows by summing
(2j-1)P(D>=j). Both identities also hold at N=0.

Write p=(q-1)/q. At D=d>=1 the cited binomial law gives

    E[C|D=d] = pd+1/q,
    E[C^2|D=d] = p^2 d^2+3p(1-p)d+(1-p)(1-2p).

At D=0, both conditional moments are zero. Therefore the constant terms
in these two expressions must be multiplied by 1-e when averaging.
Substituting the displayed moments of D gives the claimed mean and

    E[C^2] = (q-1)^2 N^2/q^2
              +(q-1)(3q+1)N/[q^2(q+1)]
              -(q-1)(1-e)/(q+1)^2.

Subtracting the square of the mean gives the stated variance. This uses
only rational finite-sum identities, so there is no limiting interchange.

For N>=1, the exact-degree-N mean exceeds the new mean by exactly

    1/[q(q+1)] + q^(-2N)/(q+1).

Thus replacing exact-degree sampling by bounded-degree sampling changes
even the constant term in typical cost. It does not change the alphabet,
the cost of any particular target, or the worst-case cost N.

## Evidence and scope

The verifier separately forms the finite mixture from the cited joint
count and the polynomial coefficients from the new geometric formula.
It measures the resulting first and second moments by integer sums and
compares them with the closed expressions. A weighted digit-string
enumeration checks a different realization of the new mixture. This is
not a new enumeration or independent validation of polynomial matrices.

The theorem covers every prime power q and every N>=0. Finite arithmetic
checks also use integer q that are not prime powers, solely as algebraic
substitutions. No nonexistent finite field is claimed for those q.

Uniform words, singular endpoints, more roles, restored auxiliary roles,
other coefficient algebras and native implementations are outside scope.
Preparation, conversion, routing, control, precision, restoration, stock
and complete supplier costs remain unpriced. All selected framework
assumptions retain their status. Independent human and formal proof-kernel
review are unclaimed.

PR4784's retained credit includes Nick Petalas's PR4763/4276/4243,
Wentao Li's PR4099 following PR2513, ToikY's PR4334, and the local/semilocal
comparisons. Nagao's polynomial-matrix presentation and degree method
remain classical predecessor work. The new contribution is the
bounded-degree sampling formula and its closed moments.
