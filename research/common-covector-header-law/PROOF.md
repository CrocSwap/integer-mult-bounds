# A common-covector pair has a different dependence law

This contribution was produced by Nick Petalas. Apache-2.0.

## Statement

Let K=F_q be any finite field, m>=2, and let a,c be independent columns
in K^m. Let b be a row with ba=bc=1. Put U=ab, V=cb, P=I-U, Q=I-V.
Thus U,V are distinct rank-one idempotents with UV=U and VU=V. Both
products are nonzero. Their complementary projectors P,Q have a common
image ker(b). This is outside the orthogonal and one-way coupling hypotheses.

For a complete header G chosen uniformly from GL_m(K), let E_P mean that
every leading principal minor of GPG^-1 of orders 1 through m-1 is
nonzero. Define E_Q in the same way. Write n=m-1 and

```text
alpha = q^2-q+1,
delta = q^2+(q-1)^3.
```

Then the exact joint passing probability is

```text
                 (q-1)(delta^n-alpha^n)
J(q,m) = ----------------------------------------- .             (1)
         (q^m-1)(q^m-q) q^(m-2)
```

In particular, over F_2 the events are strictly positively correlated for
every m>=2. At m=2 the joint probability is 1/3 and each marginal is 1/2.
This refutes extension of the known negative-correlation statements to
arbitrary two-way coupled rank-one kernels. It does not contradict their
stated hypotheses.

Claim type: scoped counting proof with finite corroboration.

## Header orbit and the guard

Conjugation takes the triple to (Ga,Gc,bG^-1). GL_m(K) acts transitively
on all triples (a,c,b) satisfying independence and ba=bc=1. To see this,
take a,c-a as the first two basis vectors. The second lies in ker(b).
Extend it to a basis of ker(b), and b has coordinates (1,0,...,0).
The same construction for any other triple gives the required change of
basis. Every triple therefore has the same number of complete-header
preimages, by the stabilizer coset bijection.

There are (q^m-1)(q^m-q) ordered independent pairs a,c. For each pair,
the two independent linear equations ba=bc=1 have q^(m-2) solutions b.
Consequently the denominator in (1) is the number of triples in this orbit.

The rank-one determinant identity gives

```text
det(P[1:k,1:k]) = 1 - sum_(i=1)^k b_i a_i,
det(Q[1:k,1:k]) = 1 - sum_(i=1)^k b_i c_i.
```

This is the marginal guard identity of Nick Petalas #4227. We use its
partial-sum method, also used in #4261, and count the new common-covector
orbit directly. For every proper prefix, both partial sums must avoid 1;
at the final coordinate both sums equal 1.

## Count first, subtract dependent pairs

Temporarily allow all a,c, retaining ba=bc=1. At one coordinate the
increment is (b_i a_i,b_i c_i). A zero increment has q^2+q-1 preimages:
q^2 choices with b_i=0, and q-1 with b_i nonzero and a_i=c_i=0.
Every nonzero increment has q-1 preimages, one for each nonzero b_i.
Thus the increment weight is q^2 times the zero indicator plus the
constant q-1 on K^2.

The safe state set S=(K minus {1})^2 has N=(q-1)^2 elements. Its weighted
transition matrix is q^2 I+(q-1)11^T. Every row sum is
q^2+(q-1)N=delta. Start at (0,0) in S. After n safe transitions the
total path weight is delta^n. The terminal state (1,1) is outside S,
so the last increment is nonzero from every safe state and has weight
q-1. The number of all passing triples before enforcing independence is
(q-1)delta^n.

If a,c are dependent, the endpoint conditions force c=a. Indeed a is
nonzero, write c=t a, and 1=bc=t ba=t. Conversely every diagonal pair
c=a with ba=1 is a dependent triple. There are no other dependent cases.

For these diagonal triples the scalar increment b_i a_i has 2q-1
preimages at zero and q-1 at every nonzero element. On K minus {1},
the safe transition matrix is q I+(q-1)11^T, with row sum
q+(q-1)^2=alpha. The last step again has weight q-1. Therefore exactly
(q-1)alpha^n of the passing triples have dependent columns. Subtracting
them gives the numerator of (1). Dividing by the independent-triple orbit
count proves (1), in every characteristic and every finite field.

## Binary positive correlation in every dimension

The cited single-request law #4227 gives

```text
p(q,m) = (q-1)alpha^n / ((q^m-1)q^(m-1)).
```

At q=2, alpha=3 and delta=5, and direct cancellation yields

```text
J(2,m) / p(2,m)^2
 = [2^(n+1)(2^(n+1)-1)/(2^(n+1)-2)] (5^n-3^n)/9^n.       (2)
```

Since 5>9/2, replacing 5^n by (9/2)^n strictly decreases (2). The
resulting lower bound is

```text
2(2^(n+1)-1)/(2^(n+1)-2) * (1-(2/3)^n).
```

This is at least 1 exactly when 3^n>=2^(n+1)-1. The latter inequality
holds for every n>=1. It is equality at n=1; if it holds at n then
3^(n+1)>=3*2^(n+1)-3>=2^(n+2)-1, since 2^(n+1)>=2.
The replacement of 5^n was strict even at n=1, so J(2,m)>p(2,m)^2
for every m>=2. This is a written dimension-uniform proof, rather than
an inference from a finite census.

## Credit and limits

The two-way-coupling question is Open next question 1 of Nick Petalas
[#4778](https://github.com/CrocSwap/integer-mult-bounds/pull/4778), following
#4769/#4274's one-way law. The marginal identity and probability are from
#4227; #4261 supplies the predecessor partial-sum/header counting method.
The common-covector orbit, its dependent-pair subtraction, formula (1),
and the binary positive-correlation proof are the new contribution here.
Cinna Davis supplied the BIT request context. source527, commdata2338 and
Jose Manuel retain the normalizer and recursive-closure lineage credit.

Only this common-covector pair and complete uniformly weighted headers are
covered. The proof does not classify arbitrary two-way pairs, larger
families, restricted header catalogues, or odd-field correlation signs.
Selection, emission, dispatch, dirty restoration, stock, precision and the
physical caller bill remain unknown. No supplier admission, new kappa,
selected-frontier change or complete multiplication theorem follows.
Independent human and formal proof-kernel review are unclaimed.
