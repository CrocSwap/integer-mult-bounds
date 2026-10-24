# A strict characteristic-two fitting-rank bound

This is a scoped proof with exact finite corroboration. Let `K` be any field
of characteristic two and let the labels lie in `F2^5`. Put `j=(1,1,1,1,1)`.
A label is odd when its coordinate sum is one. The complete type set is

```text
T = {(q,w): q,w are odd and w dot q = 1}.
R = {(q,w) in T: q != j and w != j}.
```

Each type occurs once. A matrix `N` indexed by a type set is fitting when
its diagonal entries are nonzero and, for distinct positions `s,t`,

```text
w_s dot q_t = 1 implies N[s,t] = 0.
```

No symmetry, prescribed off-diagonal values, factorization or positivity
is assumed. Binary entries embed in the prime subfield of `K`.

**Theorem.** Every fitting matrix on `R` has rank at least 22. Every
fitting matrix on `T` has rank at least 53. These are lower bounds;
neither is asserted to be the exact minimum.

Jose Manuel's PR3512 introduced this odd-type fitting boundary and proved
all-field inequalities. His PR3544 strengthens the odd-dimensional
inequalities and leaves optimal fitting rank open. We use that model,
but do not rely on or recheck either inequality. The characteristic-two
restriction below is essential to the proof and supplies no new rational
fitting-rank bound.

## 1. Equality in the elementary Hadamard bound

We first give the elementary linear-algebra argument in any field. Let
`B=W Q^T`, where row `i` of `W` is `w_i^T`, row `i` of `Q` is `q_i^T`,
and the label dimension is `d`. Suppose a fitting matrix has been
normalized to diagonal one, so that its entrywise product with `B` is
the identity. Row scaling by the inverses of the original diagonal
entries makes this normalization without changing rank or zero entries.

If `N=L H` has rank `r`, define matrices with the indicated entries:

```text
U[i,(a,k)] = w_i[a] L[i,k],
V[(a,k),i] = q_i[a] H[k,i].
```

Here `1 <= a <= d` and `1 <= k <= r`. Their product has entry
`(UV)[i,j] = (w_i dot q_j) N[i,j]`, so `UV=I_n`. In particular `n<=dr`.
This is the usual Hadamard rank inequality, proved here directly.

If `n=dr`, both matrices are square and `VU=I_(dr)`. Its `(a,b)` block
has entries

```text
sum_i q_i[a] w_i[b] H[k,i] L[i,l] = delta_(a,b) delta_(k,l).
```

Take its trace over `k=l`. Because
`sum_k H[k,i] L[i,k] = N[i,i] = 1`, this forces

```text
sum_i q_i w_i^T = r I_d.                              (1)
```

Thus (1) is a necessary condition for saturation. The argument does
not assume that `N` has binary entries. It holds over the full field `K`.
It is an elementary consequence of tensor factorization and cyclic
trace; no claim of worldwide novelty for that general observation is made.

## 2. The regular type sum

There are sixteen odd vectors, fifteen different from `j`. For fixed
odd `q != j`, the two equations

```text
j dot w = 1, q dot w = 1
```

are independent, so they define an affine three-space of eight vectors.
It contains `j`, since `q` is odd and `j dot j=1`. Removing `j` leaves
seven regular sinks. Consequently `|R|=15*7=105`.

The sum of the vectors in any affine three-space over `F2` is zero.
Removing `j` therefore makes the seven-vector fiber sum equal to `j`.
Likewise the sum of all sixteen odd vectors is zero, so the sum of
the fifteen odd `q != j` is `j`. In characteristic two this gives

```text
sum_((q,w) in R) q w^T
  = sum_(odd q != j) q j^T
  = j j^T
  = J_5,                                             (2)
```

where `J_5` is the all-ones matrix. The verifier independently enumerates
all 105 types and all 25 entries of (2), as well as the seven-element
fibers. The preceding affine-space argument proves the formula without
depending on extrapolation from that enumeration.

## 3. The strict lower bound

For `R`, the binary matrix `B[s,t]=w_s dot q_t` factors through `K^5`,
because the field has characteristic two. Section 1 gives
`rank N >= 105/5 = 21`. If its rank were 21, equation (1) would force
the sum in (2) to be `21 I_5 = I_5`. But `J_5 != I_5` over every field:
each off-diagonal entry is one on the left and zero on the right.
Thus rank 21 is impossible, and integrality proves `rank N >= 22`.

## 4. Adding the special types

There are sixteen types with `q=j`, sixteen with `w=j`, and one in
both sets. Thus `|T minus R|=31` and `|T|=136`.

For a type with `q=j`, the corresponding column of `B` is all ones.
Its column of a fitting `N` is zero except at its nonzero diagonal.
For a type with `w=j`, the same statement holds for its row. Deleting
any such row and its matching column reduces rank by exactly one:
expand around that isolated nonzero column or row, or perform ordinary
invertible elimination. Deletion does not change any remaining entry.
Repeat for all 31 special positions. This proves the exact identity

```text
rank N = 31 + rank N[R,R].
```

The bound from section 3 now gives `rank N >= 31+22=53`.

## 5. Scope and verification

The universal quantifier covers arbitrary entries in every
characteristic-two field. The type domains are the complete finite sets
defined above, with one occurrence per type. No bound for arbitrary
nonuniform multiplicities, characteristic-zero matrices or a native
supplier follows. The claim is a scoped obstruction, not a failed-search
extrapolation, a sharp optimum or a multiplication theorem.

The replay enumerates the new moment certificate and checks exact tensor
inverses and their block traces in F2, F4 and F8. The tight controls use
one or two disjoint five-port coordinate classes, including repeated
types and nonunit diagonal values before normalization. Two nontrivial
fitting fixtures of ranks 132 and 101 corroborate the special-port rank
addition, including allowed entries between special and regular positions. These
finite checks support the written proof; they do not enumerate all
fitting matrices or replace the proof over arbitrary fields.
