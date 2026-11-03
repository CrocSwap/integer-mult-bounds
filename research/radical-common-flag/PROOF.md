# Exact reachability through a common invariant flag

This contribution was produced by Nick Petalas. Apache-2.0.

## Contract and theorem

Let K be any field, n>=1, s>=0, and

```text
R = K[t_0,...,t_s]/(t_i t_j : 0<=i,j<=s).
```

There are exactly n roles. A paid factor is `I+uv^T`, where u is in R^n
and v is in K^n. Singular paid factors are allowed. Arbitrary GL_n(K)
maps are free and may occur anywhere in a finite word. Products specify
the complete action on arbitrary elements of R^n. There are no additional
roles, input promises or ring-valued free maps.

For matrices C_0,...,C_s over K, with C_0 invertible, put

```text
M = sum_(j=0)^s t_j C_j,
A_j = C_0^-1 C_j,  1<=j<=s.
```

**Theorem.** M is reachable exactly when the A_j have a common complete
invariant flag over K. Equivalently, they are simultaneously upper
triangularizable over K. When reachable, its exact paid cost is n.
Otherwise no finite word reaches M.

For s=0 the flag condition is vacuous. A complete flag is
`0=V_0<V_1<...<V_n=K^n` with dim V_k=k. Invariance means each A_j maps
each V_k into itself. Choosing an adapted basis proves the equivalence
with simultaneous triangularization. Commutation is not required.

This settles Open next question 1 of Nick Petalas's PR5854, source head
`e70246e3aabe63aacbddb41dfa2253e865798d1d`. Its first-zero argument gives
one common eigenrow. The new step uses every chronological cut and gives
the entire flag. PR4776 already classifies two-generator pencils by
characteristic-polynomial splitting. Neither predecessor is replayed here.

## The cut lemma

Split an alleged word at any chronological cut as M=QP, with P the
executed prefix and Q the remaining suffix. Include all free maps. Write
their unique square-zero expansions as

```text
P = H + sum_j t_j D_j,
Q = S + sum_j t_j E_j.
```

Comparing constant and linear coefficients gives

```text
SH=0,
C_j = S D_j + E_j H,  0<=j<=s.                 (1)
```

Let V=ker H and k=dim V. Equation (1) gives `C_0 V` contained in im S.
Invertibility of C_0 makes this image k-dimensional. Also SH=0 gives
`im H` contained in ker S, so `rank S<=n-rank H=k`. Therefore

```text
rank S=k,
C_0 V=im S.                                   (2)
```

Every C_j maps V into im S by (1). Equation (2) implies
`C_0^-1 C_j V` is contained in V. Each scalar-prefix kernel is consequently
a common invariant subspace of all normalized coefficients.

This lemma imposes no further restrictions on D_j or E_j. It covers
arbitrary feedback, free maps, extra paid factors and singular intermediate
matrices. It divides by no singular prefix or suffix and requires no
quotient word in the paid alphabet.

## Every kernel dimension occurs

The scalar prefix starts at I and ends at zero. A free map leaves its
kernel unchanged. A paid factor changes H to `(I+av^T)H`, where a is the
constant coefficient of u. Its kernel can only grow. Rank drops by at
most one, since `rank(I+av^T)>=n-1` and
`rank((I+av^T)H)>=rank H-1`.

The nested scalar-prefix kernels thus include every dimension 0 through n.
Choose one cut per dimension. The cut lemma gives a common complete
invariant flag, proving necessity. The same rank-drop bound forces at
least n paid factors in every realizing word.

## An attaining word

Given a common flag, choose G in GL_n(K) with
`T_j=G^-1 A_j G` upper triangular for every j. Set T_0=I and

```text
U=sum_j t_j T_j,
c_i=column i of U,
F_i=I+(c_i-e_i)e_i^T,  1<=i<=n.
```

Every F_i is legal. Execute F_1 through F_n in that order. The only changed
columns of `P_(i-1)=F_(i-1)...F_1` have indices below i and support in
rows of indices below i. Thus `e_i^T P_(i-1)=e_i^T`, and

```text
F_i P_(i-1)=P_(i-1)+(c_i-e_i)e_i^T.
```

Precisely column i changes from e_i to c_i. Induction gives
`F_n...F_1=U`. The complete word is

```text
M=(C_0 G) F_n...F_1 G^-1.
```

The outer maps are free. Exactly n paid factors attain the lower bound.
This is a matrix identity on every input over R, including arbitrary
initial radical coefficients. The alphabet permits singular operations;
no reversible physical implementation is asserted.

## A strict separation from the common-row test

Over every field, define

```text
J=[[0,1,0],[0,0,1],[0,0,0]],
B=[[0,0,0],[1,0,0],[0,-1,0]],
A'=diag(0,J),  B'=diag(0,B).
```

The four-role target `t_0 I_4+t_1 A'+t_2 B'` has homogeneous determinant
X^4, a common left eigenrow and a common right eigenline. Nevertheless
it is unreachable. Both coefficients are nilpotent, so any common
eigenline lies in their common kernel. That kernel is exactly the first
coordinate line. In the quotient by it, the coefficients are J and B,
whose kernels are the first and third coordinate lines. They have no
common eigenline, so the forced first line cannot extend to a complete
common flag. The theorem excludes every finite word.

The determinant follows from `det(XI_3+YJ+ZB)=X^3`, the credited PR5854
example. The new four-role consequence shows that supplying a common
eigenrow still does not suffice. The verifier checks its forced line
and quotient over F3. The written argument covers every field.

## Boundaries and credit

The statement requires an invertible distinguished coefficient and
normalization by its left inverse. Targets without such a coefficient,
nonzero scalar endpoints, higher nilpotency, restored additional roles
and broader alphabets remain outside scope. No native realization,
physical coefficient preparation, restoration bill, precision, stock,
complete recursive invoice, supplier admission or new kappa follows.
All five selected framework assumptions remain separate. Independent
human and formal proof-kernel review are unclaimed.

Rank-nullity, rank-one perturbation bounds and adapted bases are classical.
The new contribution is their chronological-cut application proving the
multi-coefficient criterion and exact cost. Retain the alphabet and
normal-form credit to Nick Petalas / PR4243, PR4773 and PR4776; Wentao Li /
PR4099 following PR2513; and ToikY / PR4334.
