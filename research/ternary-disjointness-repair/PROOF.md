# Full-rank ternary identity repair in every odd dimension

Let F be any field of characteristic three. For an odd integer h >= 3,
let A_h have rows and columns indexed by the nonempty proper subsets of [h],
with (A_h)_{U,V} = 1 when U and V are disjoint and zero otherwise. Put
v = 2^h-2 and B_h = I_v-A_h.

**Theorem.** B_h is invertible. Thus rank_F(B_h) = 2^h-2. The minimum
number of additive scalar rank-one terms repairing A_h to I_v is exactly
2^h-2.

This is a characteristic-three statement. Ali Romman's binary theorem in
[#4962](https://github.com/CrocSwap/integer-mult-bounds/pull/4962) concerns
I+A_h over F2 and has a different rank. The tensor representation and the
need to analyze the deletion of two endpoints come from that predecessor.
The new step here is the characteristic-three inverse and its nonsingular
two-endpoint block.

## The full tensor inverse

Include the empty and full subsets, and write the resulting disjointness
matrix as T = K tensor ... tensor K, with h factors and

```text
K   = [1 1]     K² = [2 1]     K³ = [0 2]     K⁴ = -I₂.
      [1 0]          [1 1]          [2 1]
```

These identities hold in the prime subfield F3, hence in F. Tensor
multiplication gives T⁴ = (-1)^h I = -I because h is odd. Consequently
M = I-T is invertible, with

```text
R = M⁻¹ = (I+T+T²+T³)/2 = 2(I+T+T²+T³).
```

Indeed, (I-T)(I+T+T²+T³) = I-T⁴ = 2I. Both matrices are polynomials
in T, so the same multiplication works in the other order.

Let E denote the ordered two indices (empty, full). The entries of a
tensor power at these two indices are the h-th powers of the corresponding
local entries. Since 2^h = 2 in F3 for odd h, the principal block of R is

```text
R_EE = 2 [1+1+2^h+0   0+1+1+2^h] = [2 2].
         [0+1+1+2^h   1+0+1+1  ]   [2 0]
```

Its determinant is -4 = 2 in F3, so it is invertible over F. Its inverse is

```text
Q = [0 2].
    [2 1]
```

## Deleting the two endpoints

Write P for the proper nonempty indices. The principal block M_PP is
exactly B_h. Suppose B_h x = 0. Extend x to a full vector z by giving it
zero coordinates at both endpoints. The P coordinates of Mz vanish,
so Mz is supported on E. Write Mz = i_E t, where i_E inserts the two
endpoint coordinates. Multiplying by R gives z = R i_E t. Taking the E
coordinates, which are zero in z, gives R_EE t = 0. Invertibility of
R_EE implies t = 0, hence z = 0 and x = 0. Thus B_h is invertible.

The proof also gives an explicit inverse without solving another system:

```text
B_h⁻¹ = R_PP - R_PE Q R_EP.
```

To verify this formula directly on an arbitrary interior right-hand side y,
start with z = R i_P y. Subtract R i_E Q z_E. The new vector has zero E
coordinates, while its image under M still has P coordinates y. Its P
coordinates therefore solve B_h x = y. This proves the formula over F.

## Exact additive repair count

If A_h + sum_{j=1}^ell u_j w_j^T = I_v for arbitrary input vectors, then
the sum equals B_h. Subadditivity of rank gives v = rank(B_h) <= ell.
Conversely, B_h = sum_{j=1}^v (B_h e_j)e_j^T supplies v nonzero rank-one
terms because B_h is invertible. Hence the algebraic minimum is exactly v.

This is an additive decomposition count. It supplies neither a physical
realization nor permission to reuse a binary supplier's cost ledger.

## Necessary hypotheses and limits

Odd h is essential to this argument and to the stated conclusion as a
uniform claim: at h=2, the proper-set repair is

```text
[ 1 -1],
[-1  1]
```

which has rank one and kernel vector (1,1) over F3. The h=1 proper-set
matrix is empty and is excluded. Even dimensions above two, other
characteristics and nonadditive repairs are not settled here.

The theorem is a written algebraic proof with bounded exact corroboration.
It does not establish a complete multiplication theorem, a supplier,
a physical COPY tariff, a new kappa or formal proof-kernel acceptance.
