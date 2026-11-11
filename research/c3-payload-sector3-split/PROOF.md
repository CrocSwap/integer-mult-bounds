# Payload involutions that fix sector 3 and split its joint spaces

This note answers the second open question of the c=3 sign-character
certificate: whether a payload involution from the degree-881 one-slot
certificate fixes sector 3 and splits a joint space of the explicit pair.
The selected conditional kappa stays `781451/250000000`. Nothing here is a
characteristic polynomial, a basis, or a census of every operator outside
the signed-permutation group.

The claim is a **proof**. The trace formula is an identity for commuting
involutions. The port operators, the 512 addresses, and the 64-element
group below are finite sets, and the verifier evaluates the identities on
every element of each set. That is not a heuristic search, and it is not an
exhaustive census of a larger matrix group.

## Operators

The input is the pinned 8-by-112 query, SHA256
`5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3`.
Its columns lie in `{-1,0,1}^8`, each has weight 4, and `R R^T = 56 I_8`.
The 112 port labels are distinct odd-weight vectors in `F_2^9`.

Bell block `c=3` is the 4096-dimensional space `C^8 ⊗ C^{512}`. Write
`e=511` and

    B_3 = sum_q (r_q r_q^T) ⊗ P_q(3),

where the sum runs over the 112 ports and, on an address `a`,

    P_q(3) e_a = e_{a+q}                 if q·3 = 1,
    P_q(3) e_a = (-1)^{q·a} e_a          if q·3 = 0.

The degree-881 certificate attaches two payload involutions to this block:

    X_3 e_a = e_{a+3},
    Z_{508} e_a = (-1)^{(3+e)·a} e_a.

Both act as the identity on the eight coordinates. Here `3+e = 508` and
`3·508 = 0`, so the two operators commute and their product is an
involution. In the certificate's sector notation, the eigenvalue of `X_3`
is `s` and the eigenvalue of `Z_{508}` is `(-1)^t`.

The explicit pair from the c=3 certificate is

| name | permutation | minus signs |
|---|---|---|
| `u` | `(0 2)(4 6)` | coordinates 0 and 2 |
| `v` | `(0 4)(2 6)` | coordinates 0 and 4 |
| `uv` | `(0 6)(2 4)` | coordinates 0 and 6 |

`H` is the order-16 group of diagonal signs that are positive on the even
coordinates `{0,2,4,6}` and arbitrary on the odd coordinates `{1,3,5,7}`.
The 64 products of `{1,u,v,uv}` with `H` are the operators used below. Each
one is rebuilt from the query as a signed coordinate permutation whose
induced port map `T` is linear and orthogonal on `F_2^9`.

## They lie outside the signed-permutation representation

A symmetry coming from a signed coordinate permutation acts as `S ⊗ U_T`,
and `T` is linear, so `U_T` fixes the address `0`. Then

    (S ⊗ U_T)(e_0 ⊗ e_0) = ε[σ(0)] e_{σ(0)} ⊗ e_0.

`X_3` sends that same vector to `e_0 ⊗ e_3`. The address moved, so `X_3` is
not equal to any such symmetry. `Z_{508}` fixes every address and multiplies
`e_0` by `+1` but `e_4` by `-1`, because bit 2 of 508 is set. A coordinate
sign does not depend on the address, so `Z_{508}` is not a signed
permutation either. The same address translation shows that the product is
not one. This is why the order-3072 stabilizer census does not decide these
operators.

The certificate defines `X_c` and `Z_{c+e}` as operators on block `c`. For
`c ≠ 3` that block is a different summand of the Bell decomposition. Those
operators are not endomorphisms of sector 3. The Walsh transform sends label
3 to 508, so it does not fix the block either. The named payload involutions
from the certificate that fix sector 3 are exactly `X_3` and `Z_{508}`.
Their product is the remaining nontrivial word in those two operators. It
fixes the same block, and the trace table below shows that it splits every
joint space of this pair as well.

## They commute with B_3 and with the joint projectors

Every port has odd weight, so `q·e = 1` and `q·508 = q·3 + 1`. If `q·3 = 1`,
then `q·508 = 0`: translation by `q` commutes with the diagonal character
`Z_{508}`. If `q·3 = 0`, then `P_q(3)` is itself diagonal and commutes with
`Z_{508}`. Translations commute with `X_3`, and a diagonal `P_q(3)` has the
same sign at `a` and at `a+3` precisely because `q·3 = 0`. Thus both payload
involutions commute with every `P_q(3)`, and therefore with `B_3`. The
verifier also applies both sides to all 512 addresses for every port.

Each of the 64 signed permutations was rebuilt from the query. For each one,
`T(3) = 3`, `T(508) = 508`, and `T(511) = 511`. The transpose of `T` inverts
`T` on every address. Consequently `T(a+3) = T(a)+3` and
`508·T(a) = 508·a`, so `S ⊗ U_T` commutes with both payload involutions.

The same rebuild gives the conjugation identity on addresses,

    U_T P_q(3) U_T^{-1} = P_{Tq}(3),

checked for every port and every address. On coordinates, the signed
permutation sends each column to `±` a column, so it permutes the rank-one
tensors `r_q r_q^T`. The sum `B_3` is therefore invariant. The spectral
projections of `u`, `v`, and the elements of `H` are polynomials in those
symmetries, so they commute with `B_3`. The payload involutions commute with
those symmetries, so they preserve every joint eigenspace, and `B_3`
preserves each intersection of a joint eigenspace with an eigenspace of
`X_3` or `Z_{508}`.

`X_3` is diagonalizable because it is a fixed-point-free involution of the
addresses: each pair `{a, a+3}` contributes eigenvalues `±1`. `Z_{508}` is
already diagonal in the address basis. Their product is an involution on
each of those pairs because `3·508 = 0`, so it is diagonalizable as well.
The minimal polynomial of each restriction divides `x^2-1`, which has
distinct roots, so the restrictions to an invariant joint space remain
diagonalizable. For an involution of trace `τ` on a space of dimension `d`,
the eigenvalue dimensions are `(d+τ)/2` and `(d-τ)/2`.

## Traces

On a signed permutation `g = S ⊗ U_T`, the block trace of
`I ⊗ (τ_b χ_f) ∘ g` factors as the product of the coordinate trace and the
address trace. The coordinate trace is the signed count of fixed
coordinates. The address trace counts solutions of `(T+I)a = b`, weighted
by `(-1)^{f·T(a)}`. The verifier computes that count by enumerating all 512
addresses and, separately, by solving the affine equation and summing the
character on its kernel. The two counts agree on every element and every
operator used here.

Let `P_{χ,ε,δ}` be the projector onto the `χ`-isotypic component of `H` and
the `(ε,δ)` joint eigenspace of `(u,v)`. Since `H`, `u`, and `v` commute and
are involutions,

    tr(W P_{χ,ε,δ})
      = (1/64) sum_{h in H} χ(h)
        [tr(Wh) + ε tr(Wuh) + δ tr(Wvh) + εδ tr(Wuvh)].

The same formula with `W = I` reproduces the published joint dimensions,
including `216^4` on the trivial character and `8^4` on the unique
32-dimensional character. The character dimensions themselves are the
published histogram

    {864: 1, 432: 4, 192: 6, 80: 4, 32: 1}.

Summing the four `(s,t)` intersections over all 16 characters and all four
`(u,v)` eigenvalues rebuilds four blocks of dimension 1024, which are the
degree-881 sectors of this Bell block. The `+1` space of `X_3` on the whole
block has dimension 2048, matching its global trace 0.

## The split

`Z_{508}` and the product `X_3 Z_{508}` have trace 0 on every joint space of
this pair. Every joint dimension below is positive and even, so each of
those two involutions splits every joint space in half.

`X_3` does not act by a scalar on any of them. Its traces depend only on the
character weight and on the `(u,v)` eigenvalues:

| weight | dimensions `(++,+-, -+, --)` | traces of `X_3` |
|---:|---|---|
| 0 | 216, 216, 216, 216 | -48, 16, 16, 16 |
| 1 | 180, 84, 84, 84 | 36, -12, -12, -12 |
| 2 | 48, 48, 48, 48 | -24, 8, 8, 8 |
| 3 | 44, 12, 12, 12 | 12, -4, -4, -4 |
| 4 | 8, 8, 8, 8 | 0, 0, 0, 0 |

On the trivial character, the `(+1,+1)` space has dimension 216 and `X_3`
has trace `-48`. The eigenvalue `+1` therefore has dimension **84** and the
eigenvalue `-1` has dimension **132**. Both summands are `B_3`-invariant.
`Z_{508}` splits the same space as **108 + 108**. The address trace of
`Z_{508}`, and of the product, is already 0 on each of the 64 group
elements, so the joint traces vanish before the character average. Because
those traces are 0, `Z_{508}` halves each `X_3` eigenspace. The
intersections with the four degree-881 sectors `(s,t)` are

| `(s,t)` | dimension inside the 216-space |
|---|---:|
| `(+1, 0)` | 42 |
| `(+1, 1)` | 42 |
| `(-1, 0)` | 66 |
| `(-1, 1)` | 66 |

All four are positive, so this joint space meets every sector of the
degree-881 splitting of block 3. The same four-way count is positive on
every other joint space of this pair. In particular each 8-dimensional
weight-4 joint space meets all four sectors in dimension 2. That is a
dimension count. It is not the characteristic polynomial of an
8-dimensional joint space, and it is not the characteristic polynomial of a
16-dimensional sum of two of them.

The other three trivial joint spaces have `X_3` trace 16, hence split as
116 + 100, and their sector intersections are 58, 58, 50, and 50.

## What is not claimed

The argument uses this query, Bell block 3, the named operators `X_3` and
`Z_{508}`, the order-16 group `H`, and the explicit pair `(u,v)`. It does
not list a basis and does not compute a minimal or characteristic
polynomial. It does not say that an arbitrary operator outside the
signed-permutation group splits these spaces. It does not rerun the
degree-881 coefficient certificate. A 42-dimensional invariant subspace
does not replace that certificate. The selected conditional kappa is
unchanged.

The rejection controls are part of the verifier, not part of the theorem. A
translation by 1 does not commute with `u`. The address character of the
vector 1 does not commute with every port operator. Dropping one element of
`H` does not reproduce dimension 864. The identity trace on the 216-space is
216, not `-48`. The coordinate transposition `(0 1)` is not a symmetry of
the query.
