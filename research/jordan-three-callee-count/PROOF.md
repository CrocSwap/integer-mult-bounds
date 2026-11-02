# Regular three-dimensional Jordan second callees

This contribution was produced by Nick Petalas. Apache-2.0.

## Statement and inherited interface

Let K=F_q be any finite field. Let lambda be nonzero with lambda^2 != 1,
and put P=lambda I+N, where N is the three-by-three Jordan nilpotent with
ones immediately above the diagonal. For the fixed ordinary wrapper, call
an invertible Q optimal if its error relative to interchange has minimum
rank. The chronological wrapper is

```text
D -= H; F_P; D += H; F_Q; D = -D; D += H,
F_T(H,D) = (T D, T^-1 H).
```

The general characterization in Nick Petalas's PR5228 states that, when
A=P^2-I is invertible, the optimal second callees are exactly

```text
Q = P + A S,    S^2=0,    det(Q) != 0.
```

Different S give different Q. This is a cited premise. Jerry Chen /
CubeJerry's PR2950 supplies the minimum error rank and Q=P attainer.
Nicholas Stone's PR5556 computes the two-dimensional Jordan count and
explicitly poses the three-dimensional case, suggesting rank-one
factorization. This proof supplies the new three-dimensional count and
complete determinant distribution, without replaying those predecessors.

**Theorem.** The number of optimal invertible second callees is

```text
q^4-q             if lambda^2=-1,
q^4-q^2-q         otherwise.
```

The first case is considered only under the standing condition
lambda^2 != 1. It therefore cannot occur in characteristic two.
For all square-zero parameters before filtering, let M(delta) count those
with det(P+A S)=delta. Then

```text
                         delta=lambda^3        every other delta in K
lambda^2=-1              2q^3-q                 q^3
lambda^2!=-1             q^3+q^2-q               q^2(q+1).
```

This is an exact all-finite-field scoped counting theorem. It does not
assert an exact interchange on every input: minimum error rank is three,
and each optimal map agrees with interchange on q^3 of q^6 input pairs.
The rank and agreement implication are inherited from the wrapper
characterization. No physical supplier or new kappa follows.

## Determinant reduction

Since N^3=0,

```text
P^-1 = lambda^-1 I - lambda^-2 N + lambda^-3 N^2,
B = P^-1 A = P-P^-1
  = (lambda-lambda^-1)I + b N + c N^2,
b = 1+lambda^-2,    c=-lambda^-3 != 0.
```

Every nonzero square-zero three-by-three matrix has rank one: its image is
contained in its kernel, so twice its rank is at most three. Thus it is
S=u v^T with u,v nonzero and v^T u=0. Conversely these conditions imply
S^2=0. For each S the pairs (u,v) are precisely
(a u,a^-1 v) for the q-1 nonzero scalars a.

The rank-one determinant identity gives

```text
det(P+A u v^T) = lambda^3 (1 + v^T B u)
              = lambda^3 (1 + v^T T u),
T = b N + c N^2.
```

For completeness, det(I+w v^T)=1+v^T w follows by multilinearity in its
columns. A term using w in two columns vanishes; the term using w in
column j contributes v_j w_j. Thus the identity holds in every
characteristic and also when the determinant is zero. The scalar part
of B drops out because v^T u=0.

## Count every determinant fiber

The matrix T is nilpotent. Its kernel has dimension k=1 when b!=0 and
k=2 when b=0. Indeed its first superdiagonal is b, its top-right entry
is c, and c is nonzero. The condition b=0 is exactly lambda^2=-1.

Fix t in K and count pairs u,v nonzero satisfying

```text
v^T u=0,    v^T T u=t.
```

If u is in ker(T), there are q^k-1 choices for u. Only t=0 is possible,
and the nonzero v in the annihilator of u number q^2-1.

If u is outside ker(T), then u and T u are linearly independent. Otherwise
T u=a u with a!=0, contradicting nilpotence. There are q^3-q^k such u.
The two independent equations on v have exactly q solutions for each t.
When t=0 one solution is v=0 and must be excluded; for t!=0 all q are
nonzero. Divide the pair counts by q-1 to count S. Finally add S=0 to
the t=0 fiber. Hence

```text
n(0) = 1 + [(q^k-1)(q^2-1) + (q^3-q^k)(q-1)]/(q-1),
n(t) = q(q^3-q^k)/(q-1)                  for every t!=0.
```

For k=1 these are q^3+q^2-q and q^2(q+1). For k=2 they are
2q^3-q and q^3. In either case their total is q^4+q^3-q. Independently,
there are q^3-1 possible nonzero u, each with q^2-1 nonzero annihilating
v, so the total is also 1+(q^3-1)(q^2-1)/(q-1).

The affine bijection delta=lambda^3(1+t) identifies t=0 with
delta=lambda^3 and t=-1 with delta=0. As -1 is nonzero in every field,
subtracting the ordinary fiber n(-1) from the total proves the claimed
invertible counts and the full determinant distribution.

## Scope

The theorem fixes one regular three-dimensional Jordan first map and the
ordinary wrapper. It also holds for a similar first map, since simultaneous
conjugation bijects the optimal Q and preserves determinants. Resonant
lambda^2=1 and several Jordan blocks require different parameter spaces
and are outside this result. No claim is made about arbitrary nonscalar P.
The finite checker supports the written proof; it does not replace its
all-field argument or establish proof-kernel acceptance.

This is an algebraic side result. It resolves the first regular J3 case
left open by PR5556, within the exact wrapper used in the retained ordinary
supplier discussion. It does not discharge a selected framework assumption.
Native coefficients, implementation, movement, precision, ownership,
restoration, stock, compiler and complete outer costs are unpriced.

Credit Nicholas Stone / PR5556 for the question, determinant-filter method
and rank-one suggestion; Nick Petalas / PR5228 for the general
parameterization; Jerry Chen / CubeJerry / PR2950 for the minimum and
attainer; and the retained ordinary/native lineage. Rank-nullity,
rank-one determinants and finite-field linear counting are classical.
No general literature-priority claim is made.
