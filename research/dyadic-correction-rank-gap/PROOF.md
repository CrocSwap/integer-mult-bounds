# When a two-role field-rank optimum is dyadic

Put D=Z[1/2]. Let a=(a1,a2) be a row in D^2 and b=(b1,b2)^T a
column in D^2 with a*b=1. Seek P in GL_2(D) with a*P=e1^T and
P*e1=b. Rank means rank over Q. The objective is rank(P-I).

[PR #7654](https://github.com/CrocSwap/integer-mult-bounds/pull/7654)
proves the general minimum over a field and leaves dyadic attainment open.
[PR #6016](https://github.com/petalas/integer-mult-bounds/blob/d2df1a6e3caf20c47fff89e6064f3747016fb954/research/dyadic-basis-conditioning/PROOF.md)
already classifies the two-role completions by their unit determinant.
We use that parameterization to decide the different rank objective.
The parameterization and unit classification are credited source facts,
not new general algebra tools. The argument below is self-contained.

## Exact classification

Every compatible dyadic completion has the form

```text
P(t) = [ b1  -a2*t ]       t in D^* = { +/- 2^k : k in Z }.
       [ b2   a1*t ]

det P(t) = t,
det(P(t)-I) = (1-a1)*t + 1-b1.
```

The first endpoint fixes the first column. The second column is in the
one-dimensional kernel of a, so it is t*(-a2,a1)^T. Its determinant is
t*(a*b)=t. A dyadic matrix has a dyadic inverse exactly when its
determinant is a dyadic unit. This proves the parameterization in this
setting and its converse.

The complete rank table is:

| Condition | Minimum over Q | Minimum over D | Dyadic attaining t |
| --- | ---: | ---: | --- |
| a=e1^T and b=e1 | 0 | 0 | 1 |
| a1=b1=1, excluding the first row | 1 | 1 | 1 |
| Exactly one of a1,b1 equals 1 | 2 | 2 | 1 |
| a1!=1 and b1!=1, tau is a dyadic unit | 1 | 1 | tau |
| a1!=1 and b1!=1, tau is not a dyadic unit | 1 | 2 | 1 |

Here tau=(b1-1)/(1-a1). It is nonzero in the last two rows.
The zero-rank case requires P=I and hence both endpoints in the first
row. Outside that case, rank one is equivalent to det(P-I)=0.
If both first coordinates are one, the displayed determinant is zero
for every allowed t. If exactly one is one, it is nonzero for every
nonzero t. Otherwise its unique zero is tau. Over Q that zero is a
legal nonzero determinant. Over D it is legal exactly when tau is a
unit. This proves every row, with no bounded exponent search.

The field table also equals the specialization of PR #7654's formula:

```text
1[a != e1^T] + 1[b != e1] - min(1[a1 != 1], 1[b1 != 1]).
```

Here pi=a, g=e1^T and d(e1)=b-e1. Thus pi*d=1-a1 and
g*d=b1-1. The finite check compares this separate formula with the table.

## A strict gap with integral coefficients

Take a=e2^T=(0,1) and b=4e1+e2=(4,1)^T. Both are primitive and
a*b=1. The compatible matrices are

```text
P(t) = [ 4  -t ],       det(P(t)-I)=t-3.
       [ 1   0 ]
```

The unique field-minimum completion is P(3). It has integer entries,
is invertible over Q, and has correction rank one. But its determinant
is 3, so its inverse has an odd denominator. It is not in GL_2(D).
Every dyadic completion has correction rank two. P(1) attains two
and has determinant one. Thus legal dyadic completion exists, while
its minimum correction rank is strictly larger than the field minimum.
This is not an infeasible or nonprimitive input contract.

The fixed line of the rank-one candidate is F=Q*(e1+e2).
The modules D*e1, D*(4e1+e2), and D*(e1+e2) are each saturated.
However the source basis [e1,e1+e2] has determinant 1, while the target
basis [4e1+e2,e1+e2] has determinant 3. The latter spans a submodule
with quotient D/3D. Saturation of the individual modules does not make
their required sum saturated. This is the missing arithmetic step in
this example; a field basis extension alone cannot supply it.

## An unbounded gap, including coupled extra coordinates

Let m>=1 and n=2m+k with k>=0. Split the coordinates into X, Y and Z
of dimensions m, m and k. Impose only

```text
P*e_i = 4e_i+f_i,          f_i^T*P = e_i^T,        1<=i<=m,
P in GL_n(D),
```

where e_i is the i-th X vector and f_i is the i-th Y vector. The
other columns and rows are free except for these equations. The exact
minimum correction rank is m over Q and 2m over D. Thus the additive
gap can be arbitrarily large. Coupling different pairs or extra
coordinates does not remove it.

Over Q the prescribed displacement columns 3e_i+f_i are independent,
so rank(P-I)>=m. The matrix with blocks [[4I,-3I],[I,0]] on X+Y and
identity on Z attains m and has determinant 3^m.

For the dyadic lower bound reduce all coefficients modulo 3. This is
valid because powers of two are invertible modulo 3. A dyadic-unit
determinant remains nonzero, so the reduced matrix Pbar is invertible.
Let F=ker(Pbar-I). The dual equations imply F is contained in
H={ (x,y,z):x=y }, whose dimension is n-m. The reduced prescribed
image of X is B={ (x,x,0) }, an m-dimensional subspace of H.
If v in F lies in B, write v=Pbar*s with s in X. Then Pbar*v=v and
Pbar*s=v; injectivity gives s=v. But X intersects B only at zero.
Thus F intersects B only at zero. The dimension formula in H gives

```text
dim F <= (n-m)-m,          rank(Pbar-I) >= 2m.
```

Reduction modulo 3 cannot increase the rank of a dyadic matrix:
every minor that is zero over Q is zero in D and stays zero after
reduction. Hence rank_Q(P-I)>=rank_F3(Pbar-I)>=2m. This uses the
fixed-subspace method of PR #7654 at an odd-prime reduction; the
method and reduction principle are not claimed as new general tools.

The matrix with blocks [[4I,-I],[I,0]] on X+Y and identity on Z has
determinant one and correction rank 2m. It attains the dyadic lower
bound. The m=1 result above is its first case. The lower bound admits
arbitrary changes on the extra coordinates; the attaining word chooses
to leave them unchanged. No physical workspace is free in this theorem.

## Literal attaining word

For arbitrary values x,y in a common chart, execute:

```text
x <- x-y
y <- y+x
x <- x+3*y
```

The successive pairs are (x0-y0,y0), (x0-y0,x0), and
(4*x0-y0,x0). Thus the word is exactly P(1). It uses three ADDs,
with coefficients -1,1,3. Its inverse uses the reversed list with
negated coefficients. No extra field, zero input, SCALE, odd division
or native MOVE is used. Extra coordinates are unchanged in this
attaining construction. For m pairs, apply these three ADDs to each pair, for 3m ADDs in total.
The word is an algebraic operation list, not a fixed-tape service or
a scalar-instruction optimum.

## Verification and limits

The verifier examines all 6561 two-by-two matrices with entries in
{-2,-3/2,-1,-1/2,0,1/2,1,3/2,2}. Of these, 2480 have a dyadic-unit
determinant. It derives each matrix's endpoint pair from its inverse,
and no matrix has rank below the classification. It also enumerates
all 308 normalized integer pairs in [-5,5]^4. The combined set has
928 distinct contracts. A constructed completion attains the exact
classified minimum for every contract; 336 have a strict field/dyadic
gap. Exact elimination checks ranks, and literal row operations check
the word and inverse for m=1 through 4 and k=0 through 3. A separate
finite-field check enumerates all 11330 admissible reduced completions
for (m,k)=(1,0),(1,1),(1,2),(2,0), with counts 2,48,11232,48. It
checks the rank floor even when the free blocks couple pairs and extra
coordinates. Six controls reject
nonunit determinants, odd denominators and omitted endpoint conditions.
The proofs above establish the unbounded statements. The finite checks
do not substitute for those proofs.

This result answers a dyadic-attainment subcase of GQ08. General
higher-dimensional paired contracts, an actual helper cut, operation
optimality, coefficient/prefix range, physical delivery, native charts,
rounding, restoration in a full caller and the complete paid/target
invoice remain open. Correction rank is not itself an implementation
price. No kappa or selected-assumption change follows.

Prepared by Ali Romman with substantial OpenAI Codex assistance.
Credit Nick Petalas for PR #7654's question and field formula and
PR #6016's completion parameterization, Ali Romman for PR #5611's
dyadic helper interface, and Dugongue for GQ08 in PR #5803.
No predecessor code was copied or replayed. The exact cited sources
serve as context; every proof and executable check here is self-contained.
Apache-2.0. Independent human and formal-kernel review are unclaimed.
