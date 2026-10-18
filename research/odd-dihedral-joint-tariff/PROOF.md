# Odd finite dihedral groups: separate cuts and a sharp joint tariff

This is an all-parameter written proof for the formal operation model below.
Finite executable checks corroborate its implementation; they do not replace
the proof, and no formal-kernel verification is asserted. This result supplies
no physical BIT supplier, recursive child profile, precision estimate, or new
multiplication exponent.

## Statement and exact operation model

Let `n=2m+1`, where `m>=1`, and let

```
G = D_(2n) = <r,x | r^n=x^2=1, xrx=r^-1>,
y = r^-1 x, so that xy=r.
```

The coefficient ring is the full, generally noncommutative group algebra
`F2[G]`. There are any finite number `R>=W` of scalar register roles. A paid
unit call has the form

```
D_N(g) = I_R + ([g]+1) N,
g in {x,y},
N = u v^T over F2, with v^T u = 1.
```

Thus `N` is any binary rank-one idempotent, including non-coordinate ones.
Arbitrary scalar `GL_R(F2)` maps are free and may be interleaved anywhere.
They act on roles, not on group addresses. There are no additional free
address operations, clean inputs, resets, erasures, or COPY operations.
All inputs, including all spectator inputs, are arbitrary. The required
complete formal endpoint is

```
T = diag([r^k_1 x^e_1], ... , [r^k_W x^e_W], 1, ... , 1),
e_i in {0,1}.
```

In particular, every spectator is restored and every off-diagonal role
coupling vanishes. Every paid call used for preparation or restoration is
included in the bill.

Define, for integers `k`,

```
d_n(k) = min(k mod n, n-(k mod n)),
A = sum_i d_n(k_i+e_i),
B = sum_i d_n(k_i),
t = #{i : e_i=1 and k_i=m mod n}.
```

The unique exceptional group element is the longest reflection `r^m x`.
If a circuit has `X` paid x calls and `Y` paid y calls, then

```
X >= A,
Y >= B,
X+Y >= A+B+t.                                      (1)
```

For every integer `j` with `0<=j<=t`, the pair

```
(X,Y) = (A+j, B+t-j)                               (2)
```

is attained by a literal coordinate-projector circuit with no extra roles
and no scalar basis changes. Every feasible count pair componentwise
dominates at least one pair in (2). These statements do not characterize
every feasible pair away from that boundary.

Consequently, for arbitrary nonnegative real prices `alpha,beta`, the exact
minimum weighted cost is

```
alpha*A + beta*B + t*min(alpha,beta).                (3)
```

This includes zero prices. The exact minimum unweighted number of calls is
`A+B+t`. The bounds hold uniformly over all finite `R`, all word lengths, all
allowed rank-one idempotents, and all interleavings with free scalar maps.

## The common cut-rank argument

Given a permutation action of `G` on a finite address set `Omega`, extend it
linearly to `F2[G]` and entrywise to register matrices. Choose a partition
`Omega=H disjoint_union K`, and include every scalar role in each side. For
an operator `M` on the represented space define

```
q_H(M) = rank_F2 M[K,H].
```

Here the block takes inputs supported on `H` to outputs supported on `K`.
Block multiplication gives

```
(UV)[K,H] = U[K,H] V[H,H] + U[K,K] V[K,H],
q_H(UV) <= q_H(U) + q_H(V).                         (4)
```

No invertibility is needed for this inequality. A free scalar map is
`S tensor I_Omega` and has crossing rank zero. For a paid call the crossing
block is

```
N tensor rho(g)[K,H],
```

so its rank is `rank(N)*q_H(rho(g))=q_H(rho(g))`.
For a permutation `g`, the crossing block is a partial permutation matrix,
and its rank is the number of elements of `H` mapped into `K`.

The endpoint is diagonal in roles, so its crossing blocks are direct sums
of the target crossing blocks. Their ranks add; identity spectators
contribute zero. Formal equality of circuits implies equality under every
representation used here. The proof never takes represented equality as a
sufficient certificate of formal equality.

This directly handles interleaved free scalar operations. Equivalently,
one can normalize them by

```
S D_N(g) S^-1 = D_(SNS^-1)(g).
```

Conjugation preserves binary rank-one idempotence. Applying augmentation
`[g] -> 1` to the full formal endpoint shows that the product of all free
scalar factors must be `I_R`. Thus normalization leaves no unpriced scalar
endpoint. This observation is consistent with, but not needed for, (4).

## The two separate-letter cuts

The finite permutation representations and separate-letter cut idea are
inherited from Adam Gall's even-period result in
[PR1941](https://github.com/CrocSwap/integer-mult-bounds/pull/1941), pinned at
`5938ce3e91bbb8b5c2227af7976d444b2fbac7d4`. The argument is checked here for
the changed odd period and its unequal sides.

On addresses `a in Z/nZ`, for any integer `c`, put

```
rho_c(r)(a) = a+1,
rho_c(x)(a) = c-a,
rho_c(y)(a) = c-1-a.
```

These permutations satisfy the displayed presentation of the actual finite
group. Use `H={0,...,m-1}` of size `m`; its complement has size `m+1`.
For any interval of length `m` or `m+1` on the `(2m+1)`-cycle, translation
by `k` sends exactly `d_n(k)` of its points outside the interval. To see
this, it suffices to take `0<=k<=m`, for which precisely `k` points leave;
negative translations give the same count and exhaust the other residues.

For `c=m`, the letter y preserves H while x sends H to `H+1`. The per-call
crossing ranks are therefore `(1,0)` for `(x,y)`. For `c=m-1`, x preserves
H while y sends it to `H-1`, giving `(0,1)`. A rotation translates H by k.
A reflection `r^k x` sends H to

```
H + (k+c-m+1).
```

The endpoint crossing ranks are therefore

```
c=m:    sum_i d_n(k_i+e_i) = A,
c=m-1:  sum_i d_n(k_i)     = B.
```

Applying (4) proves the first two inequalities in (1). These unequal cuts
alone miss one call for each longest reflection: its two ranks are `(m,m)`.
The next cut supplies the joint constraint without a parity relaxation.

## A regular-action cut gives the full alternating-word length

Use the faithful left regular action on the `2n` addresses

```
(a,e) <-> r^a x^e,  a in Z/nZ, e in {0,1}.
```

In these coordinates,

```
r(a,e)       = (a+1,e),
x(a,e)       = (-a,1-e),
y(a,e)       = (-a-1,1-e),
(r^k x)(a,e) = (k-a,1-e).
```

Let `I={-m,...,0}` and `J={0,...,m-1}`, interpreted modulo n. Choose the
balanced regular-address cut

```
H = (I x {0}) union (J x {1}),
K = (G-addresses) minus H.
```

Both sides have size `n`. Write `q(g)` for the crossing rank of the left
regular permutation of g at this cut.

For a rotation, each layer is simply translated. The two intervals have
lengths `m+1` and `m`, respectively, so the interval calculation above yields

```
q(r^k) = 2 d_n(k).                                 (5)
```

A reflection interchanges the layers, and

```
(r^k x) H = ((k-J) x {0}) union ((k-I) x {1}).
```

The two intersection sizes `|I intersect (k-J)|` and
`|J intersect (k-I)|` are equal under `a -> k-a`. Since H has n points,

```
q(r^k x) = n - 2 |I intersect (k-J)|.               (6)
```

Choose the unique representative `k' in {-m,...,m}`. For `0<=k'<=m`, the
intersection in (6) has `m-k'` points: it is the part of
`{k'-m+1,...,k'}` lying in `{-m,...,0}`. No additional modular intersection
occurs because the positive endpoints are at most m. For `k'=-j` with
`1<=j<=m`, the intersection is `{-m,...,-j}`, of size `m-j+1`. The part
below `-m` wraps to positive residues at most m and adds no points of I.
It follows that

```
q(r^k x) = 2k'+1,   if 0<=k'<=m,
            -2k'-1, if -m<=k'<=-1.                 (7)
```

In particular, `q(x)=1` and `q(y)=1`. At the longest reflection `k'=m`,
the rank is `2m+1=n`: it interchanges H and K completely. For every other
reflection it is `d_n(k+1)+d_n(k)`. Equations (5)--(7) can thus be written
uniformly as

```
q(r^k x^e) = d_n(k+e)+d_n(k)
             + 1_{e=1 and k=m mod n}.              (8)
```

The quantities in (5)--(7) also equal the lengths of the shortest
alternating x/y words. This equality does not need an independent word
metric theorem: subadditivity and `q(x)=q(y)=1` give a lower bound on any
literal word, and the attaining words below have exactly these lengths.

By additivity over roles, the endpoint has regular-cut crossing rank
`A+B+t`. Each paid call has crossing rank one at this cut, and each free
scalar operation has rank zero. Equation (4) proves

```
X+Y >= A+B+t,
```

the remaining inequality in (1). It applies to arbitrarily many longest
reflections simultaneously, without limiting the number of restored dirty
spectators.

## Attaining formal circuit and complete invoice

Let `E_i` be the coordinate projector onto role i. In the full formal group
algebra, directly multiplying the two factors gives

```
D_(E_i)(g) D_(E_i)(h) = D_(E_i)(gh).                (9)
```

Indeed `E_i^2=E_i`, and in characteristic two the coefficient of `E_i`
reduces to `[gh]+1`. No permutation representation is used to certify (9).
Calls on distinct coordinate roles commute.

For rotations, take the representative `k' in {-m,...,m}` and the literal
word `(xy)^k'`, interpreting negative powers as repetitions of `yx`. Its
counts are `(d_n(k),d_n(k))`.

For a reflection other than `r^m x`, choose `k' in {-m,...,m-1}` and freely
reduce `(xy)^k' x`. If `k'>=0`, its counts are `(k'+1,k')`; if `k'=-j<0`,
they are `(j-1,j)`. In either case the counts are exactly
`(d_n(k+1),d_n(k))`.

The longest reflection has the two formal words

```
(xy)^m x = r^m x,
(yx)^m y = r^(-m-1) x = r^m x,
```

with counts `(m+1,m)` and `(m,m+1)`. Choose the first word on exactly j of
the t longest-reflection roles and the second on the remainder. Equations
(9) and the group relation `r^n=1` prove the complete formal endpoint with
the counts in (2). With column-vector conventions, the rightmost displayed
factor acts first, so each displayed product is executed right to left.

For any feasible counts write `X=A+u`, `Y=B+v`. By (1), the integers u,v
are nonnegative and `u+v>=t`. There is an integer

```
max(0,t-v) <= j <= min(t,u),
```

so `(X,Y)` componentwise dominates `(A+j,B+t-j)`. Nonnegative weights
therefore have minimum (3), attained by selecting the cheaper extra letter
on each longest-reflection role. Equal weights permit every choice of j.

| Resource | Complete attaining implementation |
| --- | --- |
| Arbitrary-input target roles | W |
| Extra roles required | Zero; any added spectators remain untouched |
| Paid x/y calls | `(A+j,B+t-j)` for chosen `0<=j<=t` |
| Scalar changes of basis | Zero |
| Clean inputs, COPYs, resets, erasures | None |
| Extra preparation or inverse restoration | None hidden or deferred |
| Endpoint verification | Equality in the full formal group algebra |
| Physical supplier or recursive adoption | Not supplied |

The lower-bound argument also applies to arbitrary-rank binary idempotent
calls if each call is charged its scalar rank: (1) then bounds x rank mass,
y rank mass, and their sum. This is not an invocation-count optimum for
batched calls and does not price recursive children by their rank.

## Scope, predecessor credit, and remaining obligations

The separate-letter construction and the explicit odd-period gap come from
Adam Gall's [PR1941](https://github.com/CrocSwap/integer-mult-bounds/pull/1941),
at the pinned head above. Adam Gall's
[PR1911](https://github.com/CrocSwap/integer-mult-bounds/pull/1911), head
`712593f82739203639d0a169b88c6bcac6f0590c`, supplies the infinite-dihedral
predecessor and its finite-torsion question. The new mathematical step here
is the regular-action cut (6)--(8) that closes the joint odd-period tariff;
the general subadditive cut-rank principle is not claimed as new.

Relevant overlapping evidence also includes the coordinate/CNOT setting of
[PR1414](https://github.com/CrocSwap/integer-mult-bounds/pull/1414) and
Cinna Davis's [PR1953](https://github.com/CrocSwap/integer-mult-bounds/pull/1953),
head `4f3bdf7c3bdd7033180c9d8c41245023cc402bc6`, with its finite D10
inverse-rotation special case. Those special cases are credited, not claimed
as previously unsettled instances. This proof allows every binary rank-one
idempotent, arbitrary free scalar mixing, and any finite number of restored
dirty spectators. Overlap review and publication status belong to the package
metadata; this mathematical proof is not a novelty certificate.

The covered domain is odd `n>=3`, any finite `R>=W`, and complete diagonal
formal endpoints of the displayed kind. The proof uses no integer lift,
analytic approximation, or precision assumption: the historical scalar
mixing permission is an optimistic formal relaxation. Moving to a physical
supplier would require independently admitting and pricing the native group
actions, all frame/compiler and hosting work, precision/tape behavior, and
the full recursive profile. None of those obligations follows from the
formal tariff. Other free address maps, other paid labels, partial endpoint
contracts, clean ancillas, or nonlinear operations are outside this theorem.

Prepared with substantial OpenAI Codex assistance. Apache-2.0.
