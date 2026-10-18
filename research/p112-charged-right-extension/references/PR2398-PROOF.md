# Arbitrarily many terms inside the two minimal factor spaces

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.

This extends the **term-count scope** of Hanhong Zhao's [PR #2321](https://github.com/CrocSwap/integer-mult-bounds/pull/2321),
head `0665be26c2db1bd7f393d829e786698b34b626e4`. Its support catalogue and
attainer are credited premises reconstructed here from the root prototype.
The new argument is Sections 3–5: termwise coefficient duality is unavailable
for an overcomplete decomposition. Zero-COPY nonzero terms are allowed.

## 1. Statement and conventions

Remove the first eight frame rows from the pinned 120-root prototype. Write
`X` for the resulting 112-by-8 matrix and `lambda_i` for its 112 binary labels
in `F_2^9`. Set `B_ij = lambda_i dot lambda_j` over `F_2`.
The checker binds this convention to `(X_i dot X_j / 2 + 1) mod 2`.
Let `e=e_0`, `f=e_1`, `s=X[0,:]^T`, `t=X[1,:]^T`, and define

```
G = X X^T
K = G - (G e - 4 e)e^T + e f^T
L = [X, e]                         (112 by 9)
R = [(I - e e^T)X, 4e + f]         (112 by 9).
```

The exact finite checks give `K=L R^T`, `rank(L)=rank(R)=9`, and `K_ij=G_ij`
on every required pair `B_ij=1`. All transposes in this note are **ordinary**
transposes over `C`, never conjugate transposes. In particular,

```
s = (0,1,1,0,1,0,0,1),    t = (0,1,1,0,1,0,0,-1),
s^T s = 4,                s^T t = 2.
```

**Theorem.** Consider any finite decomposition

```
K = sum_i D_i T_i^T,       D_i in col_C(L), T_i in col_C(R).
```

For each term separately charge
`rho_i = rank_F2 B[supp(D_i), supp(T_i)]`. For every real `0<q<=1`,

```
                 sum_i rho_i^q >= 7*8^q + 7^q + 1.              (1)
```

The minimum is attained by the same rational nine-term factorization for
every `q`. Thus COPY has sharp minimum 64. For `0<q<1`, the minimum is strictly
greater than `8*8^q`.

This theorem requires **both** factor-space inclusions and separate billing.
It does not bound all factorizations of `K`, shared physical COPY work, or a
completed recursive supplier. Section 7 gives an exact ten-term factorization
outside the right space that violates (1) for every `0<q<1`.

## 2. Complete finite support premises

Because `L,R` have full column rank, write uniquely
`D_i=L m_i`, `T_i=R n_i`, with `m_i=(a_i,c_i)` and `n_i=(b_i,d_i)`, where
`a_i,b_i` are eight-dimensional. Left inverses of `L,R` give the equivalence

```
K = sum_i D_i T_i^T     iff     sum_i m_i n_i^T = I_9.          (2)
```

Terms with a zero physical factor contribute zero and may be removed. We do
**not** remove a nonzero term merely because its COPY rank is zero. Call a
remaining term *mixed* when both `a_i` and `b_i` are nonzero; otherwise call
it *pure*. This terminology concerns coefficient projections, not COPY rank.

Here is the fixed support catalogue from PR #2321. Put
`z=(0^8,1)`, `l=(s,-4)`, `v=(s,0)`, `u=(t,-4)`.

| Side/class | Coefficient vectors | Dimension of binary support span |
|---|---|---:|
| left Z | nonzero multiples of z | 1 |
| left E_r | alpha e_r + beta z, alpha nonzero; beta=0 if s_r=0 | 8 |
| left V | nonzero multiples of l | 8 |
| left F | all other nonzero vectors | 9 |
| right W | nonzero multiples of z | 2 |
| right E_r | alpha e_r + beta z, alpha nonzero; beta=0 if s_r=0 | 8 |
| right V | nonzero multiples of v | 8 |
| right U | nonzero multiples of u | 8 |
| right F | all other nonzero vectors | 9 |

The eight left/right E classes have binary support span perpendicular to
the corresponding removed-frame label. Left V and right V have span
`lambda_0^perp`; right U has span `lambda_1^perp`. Left Z spans `lambda_0`,
and right W spans `lambda_0,lambda_1`.

For completeness, the checker computes the exact rational kernel of the
rows of `L` (respectively `R`) indexed by `h dot lambda_i=1`, for **all 511
nonzero characters h on each side**. These are precisely the coefficient
vectors whose physical support annihilates `h`. It checks every kernel against
the displayed model spaces, and verifies that distinct nonzero kernels
intersect only in zero or the line `Cz`. Therefore a non-pure vector in a
proper binary support span has exactly one nonzero annihilator, so that span
has dimension eight. Every remaining nonzero coefficient vector has full
binary support span. Rational kernel identities extend to `C`; this is a
classification of all complex coefficients, including cancellations, rather
than a sampling of rational representatives.

The nullity histograms are `{0:251,1:256,2:4}` on the left and
`{0:378,1:129,2:4}` on the right. There are respectively 10 and 11 distinct
nonzero kernels. Once support spans are fixed, their bilinear pairing rank
is fixed. The complete 11-by-12 table in `CERTIFICATE.json` is recomputed by
two elimination methods, on actual supports and on their binary spans. Its
consequences used below are:

1. Every mixed term costs at least 7. A mixed term of cost 7 must have left
   class V, right class V, or right class U. Left V/right V costs 8.
2. The only zero-COPY class pair is left Z/right V.
3. Left Z costs 1 against every right class except V.
4. Right W costs 1 against left Z or V, and 2 against every left E or F.

These finite premises are inherited and rechecked. Sections 3–5 are the
extension to arbitrary term count.

## 3. Nine or more mixed terms: a rank bound

The top-left block of (2) is

```
                       sum_i a_i b_i^T = I_8.                 (3)
```

Only mixed terms contribute. Hence their number `n` is at least eight.
Partition all mixed cost-7 terms among the three possible types in item 1,
assigning a term satisfying multiple types to any one type. Their aggregate
contribution to (3) has the form

```
                       s x^T + y s^T + w t^T
```

for some eight-dimensional vectors `x,y,w`; its rank is at most three.
If `h` other mixed terms remain, each contributes a rank-one matrix and costs
at least eight. Rank subadditivity applied to (3) gives `8<=3+h`, so `h>=5`.
When `n>=9`, the mixed power bill is therefore at least

```
                         5*8^q + 4*7^q.                     (4)
```

This dominates the bill of `Q_many=(8,7,7,7,7,7,7,7,7)` term by term.
The desired profile `P=(8,8,8,8,8,8,8,7,1)` majorizes `Q_many`:
both sum to 64 and every descending partial sum of `P` is at least the
corresponding partial sum of `Q_many`. Concavity of `x^q` for `0<q<=1`
gives `sum Q_many^q >= sum P^q`, proving (1) in this case. Pure terms have
nonnegative bills and cannot lower it.

## 4. Exactly eight mixed terms: projection duality and compensation

Index the eight mixed terms by `1,...,8` and put their projections in square
matrices `A=[a_1 ... a_8]`, `B'=[b_1 ... b_8]`. Equation (3) gives
`A B'^T=I_8`, hence

```
                         b_i^T a_j = delta_ij.               (5)
```

This is **eight-dimensional projection duality**, not the generally false
nine-dimensional claim `n_i^T m_j=delta_ij`. Both projected sets are bases.
There is at most one left V projection (the line `Cs`), at most one right V
projection (`Cs`), and at most one right U projection (`Ct`). If a left V
occurs at index `j`, any right V or U must occur at the same index: otherwise
(5) contradicts `s^T s=4` or `s^T t=2`. As left V/right V costs eight, there
is then at most one cost-7 mixed term. If no left V occurs, at most the two
right exceptional lines can provide cost seven. Thus there are at most two
cost-7 mixed terms in all cases.

**Compensation costs at least one.** Suppose all pure terms cost zero.
By item 2 each is a multiple of `z v^T` in coefficient coordinates, and
contributes zero to the top-right and bottom-right blocks of (2). The
top-right block then says `A d=0`, where `d=(d_1,...,d_8)^T` lists the mixed
last coordinates. Thus `d=0`. The mixed contribution to the bottom-right
entry is also zero, contradicting that this entry of `I_9` is one.
Consequently the integer sum of the pure COPY ranks is at least one, and
its power bill is at least one.

**If two mixed terms cost seven, compensation costs at least two.** Suppose
instead the pure COPY sum is at most one. The previous paragraph makes it
exactly one: there is exactly one positive-COPY pure term, costing one,
and all other pure terms have type Z/V. The positive term has one of the
following forms by items 3–4:

- **Left Z.** Every pure term then has `a=0`. The top-right equation still
  gives `A d=0`, hence all mixed `d_i=0`. Mixed right U is impossible,
  since its last coordinate is nonzero. The remaining cost-7 possibilities,
  left V or right V, yield at most one such term by (5) and the V/V cost.
- **Left V/right W.** Its top-right contribution is `eta s` for some
  nonzero `eta`. All zero-COPY pure terms contribute zero there. Thus
  `A d=-eta s`, and (5) gives `d_i=-eta b_i^T s`. A mixed right V would
  have `b_i=gamma s`, `gamma!=0`, and `d_i=0`, contradicting
  `d_i=-4 eta gamma`. Hence right V is absent. Only left V and right U
  can give cost seven; if both occur they must share one index by (5) and
  `s^T t=2`. Again at most one mixed term costs seven.

Both alternatives contradict two cost-7 mixed terms. Therefore in that
case the pure COPY sum is at least two. Subadditivity of `x^q` gives
`sum_pure rho_i^q >= (sum_pure rho_i)^q >= 2^q`. This allows arbitrarily
many pure terms, including arbitrarily many nonzero zero-COPY terms.

## 5. Exhausting the eight-mixed-term cases

According as there are zero, one, or two cost-7 mixed terms, Section 4 gives
one of the following lower bills:

```
8*8^q + 1,
7*8^q + 7^q + 1,
6*8^q + 2*7^q + 2^q.
```

The first dominates (1) and the second equals it. For the third, set
`Q_two=(8,8,8,8,8,8,7,7,2)`. The descending partial sums are

```
P:      8,16,24,32,40,48,56,63,64
Q_two:  8,16,24,32,40,48,55,62,64.
```

Thus `P` majorizes `Q_two`, and concavity again gives the desired lower bound.
Together with Section 3 this exhausts all finite term counts. The verifier
checks the integer partial sums; no numerical sampling of real `q` is used.

## 6. Attainment and a genuine overcomplete fixture

As in PR #2321, let `N` be `I_9` with column 1 replaced by `v=(s,0)`.
Since `s_1=1`, it is invertible. Set `M=N^(-T)`, `D=L M`, `T=R N`.
The checker reconstructs these rational matrices and verifies all 12,544
entries of `D T^T=K` and the actual support ranks

```
                         (8,7,8,8,8,8,8,8,1).
```

For an eleven-term in-space example, append the coefficient pairs
`(z,v)` and `(-z,v)`. They are nonzero, cancel exactly, and both cost zero.
This attains the same bill and shows why excluding every zero-COPY term
by nine-term diagonal duality would be an invalid proof here. It also
shows that the result is not restricted to minimal-length decompositions.
For `0<q<1`, strict subadditivity gives `7^q+1>8^q`, proving the strict
comparison with eight rank-eight terms. At `q=1`, both totals are 64.

## 7. The right-space hypothesis is essential

The defining identity for `K` already gives ten terms:

```
K = sum_{r=0}^7 X[:,r] X[:,r]^T + (4e-G e)e^T + e f^T.       (6)
```

All ten left factors lie in `col(L)`. The two additional terms have COPY
rank zero, and the eight original terms have rank eight. Thus the profile
is `(8,8,8,8,8,8,8,8,0,0)`, whose power bill `8*8^q` is below (1) for
`0<q<1`. The checker verifies (6) entry by entry and computes
`rank([R,e])=rank([R,f])=10`. The two added right factors are outside
`col(R)`. All right factors of (6) lie in the single extra dimension
`col(R)+Ce`, since `f=(4e+f)-4e` and `X[:,r]=R[:,r]+s_r e`; the checker
also verifies that the combined right space has dimension ten. This is a boundary control derived from the predecessor matrix,
not a new physical decoder or an improved total COPY bound.

## Evidence status and remaining obligations

The result is a scoped written proof supported by exact finite algebra.
The support catalogue and nine-term witness are predecessor work; the new
contribution is the arbitrary-length rank/compensation argument and its
explicit scope controls. No Lean proof, independent human review, or
external-agent review is claimed. The verification program checks finite
premises and fixtures; it does not mechanically certify the written universal
argument. Native frames, arbitrary-dirty realization, shared costs, precision,
reserve, chronological hosting, and all-size transfer remain unaddressed.
