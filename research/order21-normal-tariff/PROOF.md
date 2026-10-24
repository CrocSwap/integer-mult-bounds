# Exact normal-subgroup tariff in the order-21 algebra

This contribution was produced by Nick Petalas. Apache-2.0.

## Statement and model

Let G be the group C7 semidirect C3 with elements a^i b^j, where
0 <= i < 7, 0 <= j < 3, and b a b^-1 = a^2. Multiplication is

```text
(i,j)(k,l) = (i + 2^j k mod 7, j+l mod 3).
```

Work in the full formal algebra Mat_r(F2[G]). There are w active roles,
with 1 <= w <= r, and arbitrary exponents 1 <= e_t <= 6. The required
operator is

```text
T = diag([a^e_1], ..., [a^e_w], 1, ..., 1).
```

Every role has arbitrary input. The last r-w roles must be restored as
operators. A paid call is D_N(g) = I + ([g]+[1])N for any g != 1 in G
and any rank-one binary idempotent N in Mat_r(F2). Each call costs one.
Arbitrary GL_r(F2) scalar maps may be interleaved for free. No other
address maps, clean workspace, COPY or ERASE are free.

**Theorem.** The exact minimum number of paid calls is w, for every
finite r and every stated exponent list. In particular,
diag([a],[a^2],[a^4],[a],1,...,1) requires exactly four calls, regardless
of the number of restored dirty roles.

More precisely, if a word uses c7 paid labels in the normal subgroup
C7 minus identity, and c3 paid labels outside C7, then

```text
3 c7 + 2 c3 >= 3w.
```

Consequently an optimal w-call word uses only normal-subgroup labels.
This does not claim an exact optimum subject to a prescribed positive c3.

## Representation and rank budget

The polynomial x^3+x+1 has neither zero nor one as a root in F2.
A reducible cubic over a field has a linear factor, so this polynomial
is irreducible. Let F8=F2[alpha] with alpha^3=alpha+1. Its multiplicative
group has order seven. Since alpha is neither zero nor one, its order
is seven.

For g=a^i b^j, define the binary linear map on F8

```text
rho(g)(z) = alpha^i z^(2^j).
```

Frobenius is F2-linear and its third power is identity. Composing the
displayed maps gives the group multiplication above, so rho extends
linearly to an algebra homomorphism F2[G] -> Mat_3(F2). In the basis
1,alpha,alpha^2 its two generators, encoded as binary integer rows, are

```text
rho(a) = (4,5,2),    rho(b) = (1,4,6).
```

For 1 <= i <= 6, rho(a^i)+I is multiplication by the nonzero field
element alpha^i+1, hence has rank three.

For j=1 or 2, a nonzero fixed point of rho(a^i b^j) satisfies
z^(2^j-1)=alpha^-i. The exponents 2^j-1 are respectively one and three,
both coprime to seven. Raising to either power therefore permutes F8's
nonzero elements. There is exactly one nonzero fixed point, together
with zero. Its kernel as a binary linear map has dimension one, so
rank(rho(a^i b^j)+I)=2. This proves all represented ranks without a census.

Apply rho to every entry of an r-role operator, viewing the result as
an ordinary 3r by 3r binary matrix. One paid call has difference from
identity

```text
N tensor (rho(g)+I).
```

The rank of a tensor product over a field is the product of the ranks.
Thus each normal-subgroup call contributes rank three and every other
paid label contributes rank two. Meanwhile rank(rho(T)+I)=3w, since
its active diagonal blocks are invertible and its dirty blocks are zero.

For any equally sized matrices A and B,

```text
AB-I = (A-I)B + (B-I),
rank(AB-I) <= rank(A-I) + rank(B-I).
```

Induction over any finite paid word proves the stated rank budget.
It is a necessary condition for formal equality. Faithfulness of the
algebra homomorphism is unnecessary, and no equality in the represented
algebra is used to certify a formal endpoint.

## Free scalar maps and arbitrary dirty workspace

A scalar map S satisfies S D_N(g) = D_(S N S^-1)(g) S. Moving each free
scalar map to the right therefore conjugates the paid binary idempotents
and leaves them inside the declared alphabet. Augmentation [g] -> 1
sends every paid factor and T to identity. Hence the remaining product
of free scalar maps must be identity. The normalized word has the same
paid labels and number of calls, so the rank budget applies unchanged.

The proof holds for every finite r. Identity-target dirty roles add
zero to the represented target rank. No compression, clean-input
assumption or bound on the number of workspace roles is used.

Since 3 c7+2 c3 <= 3(c7+c3), the rank budget forces at least w calls.
If exactly w calls occur, any c3>0 would make the rank budget fail.

## Attainment in the full formal algebra

For each active role t, take N=E_tt and g=a^e_t. This call acts by
[a^e_t] on that role and identity on every other role. The product of
these w coordinate calls is exactly T coefficient by coefficient in
F2[G]. It uses no additional roles and restores every dirty role.
This establishes the upper bound in the full formal algebra and
completes the proof.

## Sources and limits

Cinna Davis's PR2011 fixes this group, paid alphabet and conjugacy-orbit
endpoint, and explicitly leaves four outputs open. The new statement
settles that question and removes both the fixed role count and the
restriction against free scalar maps. The original three-role finite
census is not rerun or claimed as new. Cinna Davis's PR3893 supplies an
S3 example of the classical representation-rank telescoping method.
The present contribution is its fixed-point-free F8 application and
uniform exact order-21 tariff. The F8 and rank facts are elementary
linear algebra, not new general methods.

Mixed order-three target profiles, nonuniform tariffs, native realization,
physical movement, precision, stock, recursive costs and the complete
multiplication theorem are outside this proof. The selected frontier
is unchanged. No proof-kernel or independent human review is claimed.
