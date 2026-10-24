# Complete headers for a common nonidentity scalar pivot

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.

## Retained results and the new consumer

Nick Petalas's [PR #4785](https://github.com/CrocSwap/integer-mult-bounds/pull/4785)
proves the six-map sharpness criterion for every common scalar pivot.
Its [proof](https://github.com/CrocSwap/integer-mult-bounds/blob/7c472563474e60185e6ca101a17622133d047e56/research/scalar-block-schur-dimension/PROOF.md)
and [open question 2](https://github.com/CrocSwap/integer-mult-bounds/blob/7c472563474e60185e6ca101a17622133d047e56/research/scalar-block-schur-dimension/README.md)
supply the exact consumer used here. Nick Petalas's
[PR #4803](https://github.com/CrocSwap/integer-mult-bounds/pull/4803)
already gives the two-shift distribution. Ali Romman's
[Discussion #5261](https://github.com/CrocSwap/integer-mult-bounds/discussions/5261)
already gives the distribution for any number of distinct scalar shifts.
The distribution and the criterion are not new here.

The new result combines these results with the factor weights from ssafwann's
[PR #4678](https://github.com/CrocSwap/integer-mult-bounds/pull/4678)
to count complete headers for every common nonzero scalar pivot. It resolves
the named F5 caller and treats the collisions among the three scalar shifts.
The code checks actual nonbinary Schur complements as well as matrix counts.

## Ensemble and formula

Let q be a prime power, d >= 1, and lambda in Fq be nonzero. Fix four
joint-sector dimensions r00,r10,r01,r11 with total n >= d. The two fixed
commuting projectors P0,Q0 have these sectors. A header is a complete
ordered basis M in GL_n(Fq). Count headers for which the leading d blocks
of M^-1 P0 M and M^-1 Q0 M are both lambda I. Call this count C. Let B be
the number of these headers whose Schur commutator has rank 2d.
There is no quotient by basis changes, sector orbits or residual orbits.

Write I(r,k)=product_(j=0)^(k-1)(q^r-q^j), with value zero when k>r or
k<0. Let G(r,k) be the Gaussian binomial coefficient. For a fixed d by d
matrix T of rank rho, the number of factors X:Fq^r -> Fq^d and
Y:Fq^d -> Fq^r with XY=T is

```text
U(r,d,rho) = sum_(k=rho)^min(r,d) G(d-rho,k-rho) I(r,k) q^[d(r-k)].
```

If X must be onto and Y must be injective, the count is

```text
A(r,d,rho) = I(r,d) q^[rho(r-d)] I(r-d,d-rho), for r>=d;
A(r,d,rho) = 0, for r<d.
```

These are the retained factor-count arguments. For U, choose im X containing
im T, choose the onto map to it, then choose all lifts of T. For A, choose
X onto. Modulo ker X, Y is fixed by T. On ker T it must inject into ker X;
on a complement it has q^[rho(r-d)] lifts. This proves the formulas over
all finite fields, with no assumption on the Jordan form of T.

For H=pi P0 Q0 i, the sector products are

```text
T00 = H-(2lambda-1)I,  T10=T01=lambda I-H,  T11=H.
```

Let rho_j=rank T_j. For each fixed H the common-pivot split count is
product_j U(r_j,d,rho_j). The sharp split count is
U(r00,d,rho00) times product_(j=10,01,11) A(r_j,d,rho_j).
This follows directly from the retained six-map criterion. The four products
sum to I, so the stacked maps always satisfy pi i=I. In particular i is
injective and pi is onto. Every such pair (i,pi) has exactly GL_(n-d)(Fq)
complete headers: choose any ordered basis of ker pi after the columns of i.
Thus the complete counts are

```text
C = |GL_(n-d)| sum_H product_j U(r_j,d,rho_j(H)),
B = |GL_(n-d)| sum_H U(r00,d,rho00(H)) product_(j=10,01,11) A(r_j,d,rho_j(H)).
```

The unconditional sharp probability is B/|GL_n|. The conditional probability
is B/C only when C>0. The implementation returns None when C=0.

## Three shifts and their collisions

Only the nullities at 0,lambda,2lambda-1 enter these weights. Since lambda
is nonzero, the first two shifts are distinct. If lambda=1, the third shift
is lambda. If 2lambda=1, it is zero; this case requires odd characteristic.
In every other case all three shifts are distinct. The implementation takes
this equality class as a supplied premise. It does not interpret integer
labels as extension-field elements. Its verifier computes the class from
actual field arithmetic.

Use the retained multi-shift incidence law. For t distinct shifts and a tuple
k with K=sum k_i<=d, let s_i=sum_(j<i) k_j. Then

```text
M(k)=q^[d(d-K)] product_i G(d-s_i,k_i) q^[s_i k_i]
    =sum_(e>=k) N(e) product_i G(e_i,k_i).
```

The first formula chooses disjoint subspaces on which H has each specified
eigenvalue, then its arbitrary extension. The second counts those subspaces
inside the actual eigenspaces. Descending componentwise subtraction gives
N(k) exactly, because the diagonal coefficient is one. Replace the sums over
H above by sums over N(k) and the corresponding ranks. This preserves the
joint distribution. It does not assume independence of the ranks.

For fixed t<=3 there are binomial(d+t,t) tuples and O(d^(2t)) arithmetic
summands in this direct implementation. All integer bit lengths are polynomial
in d and log q. This is an application of the predecessor incidence law,
not a new counting shortcut. The supplied q must be a prime power.

## Named F5 caller

Take lambda=2, d=2, profile (1,2,2,2). The source asks about H=J2(3).
Then the four ranks are (1,2,2,2). U(1,2,1)=4 and A(2,2,2)=480, so
there are exactly 4*480^3=442368000 sharp splits for this fixed H.
Multiply by |GL5(F5)| for complete headers.

For the full profile, sharpness requires H and 2I-H invertible and
rank(H-3I)<=1. H=3I has U(1,2,0)=49. For H-3I of rank one, there are
24 nonzero nilpotent matrices and 30 matrices of each allowed nonzero trace
1 and 3. Traces 2 and 4 would make H or 2I-H singular. Thus there are 84
rank-one matrices and the full sharp split count is

```text
(49+84*4)*480^3 = 42577920000.
```

The independent census checks all 625 matrices H, including the common-pivot
count without the full-rank conditions. RESULT.json gives the exact integers
and reduced fractions. These counts distinguish the Jordan and scalar cases
which have the same nullities at 0 and lambda. Omitting the third shift loses
that distinction.

## Actual nonbinary Schur check and limits

Over F4=F2[x]/(x^2+x+1), take lambda=x, d=1 and profile (0,1,1,1).
The verifier checks all 4032 pairs of a nonzero inclusion column and a
projection row. Exactly 27 have the required common pivot. For each it forms
an actual header with a kernel basis, conjugates both projectors, takes the
Schur complements with lambda^-1, and obtains commutator rank two.
There are 27*|GL2(F4)|=4860 complete headers, or probability 3/112.
The verifier checks all split pairs, not all 181440 complete headers.

The algebraic result is one-block only. It does not give a later-guard
transition, residual-orbit law, physical cover, header generator, paid
consumer, native theorem or complete multiplication theorem. The selected
kappa and all its open assumptions remain unchanged. No independent human
or proof-kernel acceptance is claimed.
