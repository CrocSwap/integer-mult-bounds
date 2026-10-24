# An optimal affine projector at odd tensor width

This note extends `STREAM.md` and `AMENDMENT.md`. It does not change
their frozen bytes. It gives the same arbitrary-input shear at every
odd tensor width. One binary coordinate remains in the compressed leaf.
A completed native frame acts on this coordinate by a fixed two-point
kernel. Thus different completed frames can be matched on the leaf,
without a full-field native child.

The result is a local stream construction. Its affine sector is still
an exponentially small part of the full address space. It does not give
a new controller, a finite supplier invoice, or a kappa improvement.

## 1. The sector and its projector

Let `n>=2`, `lambda=2f+1`, and `omega=(1,...,1)` in `F_2^n`.
For each Fourier address, write its columns as `chi_j`. Use the affine
sector

    chi_(j+f) = chi_j + omega,  0<=j<f,
    chi_(2f) = t omega,  t in F_2.

Its dimension is `nf+1`. This attains the affine dimension bound from
the reviewed correlated-access theorem. Its codimension is

    k = nf+n-1 = n ceil(lambda/2)-1.

Every odd native line has phase `i^(f+t)` on this sector. The phase can
have two values; this is not a fixed-phase sector.

Let `h_(i,j)` translate the two selected bits in pair `(j,j+f)` of
native row `i`. In the last column, let `l_i` translate rows `0` and
`i`, for `1<=i<n`. The orthogonal projector is

    Pi = product_(i,j) (I-X_(h_(i,j)))/2
         product_(i=1,...,n-1) (I+X_(l_i))/2.

The `k` translations are independent. The projector has rank fraction
`2^-k` and infinity norm one. The signs in the second product are
positive. A negative sign there gives a different affine sector.

## 2. Fixed address maps and the reversible code

Each old native slot has `2f+1` consecutive chunks of `K` bits. Name its
first `f` chunks, its next `f` chunks, and its last chunk separately.
Empty first and second parts are omitted when `f=0`. This changes no
record order. The selected offset remains `rho` in every chunk.

On each pair of equal-width parts, apply the same selected-bit row
addition as in `STREAM.md`. On the `n` last chunks, apply `n-1` row
additions to the selected bit of row zero:

    (x_0,x_1,...,x_(n-1)) ->
    (x_0+x_1+...+x_(n-1), x_1,...,x_(n-1)).

Call the full address map `P`. It fixes every unselected bit. It sends
each `h_(i,j)` to its second-half selected bit and each `l_i` to last
column bit `i`. The last-column bit of row zero remains. Call it `u`.
There are at most `2n-1` row additions. Their count is independent of
`lambda`. The original compact fields suffice for the shorter parts;
the last-column additions have slot width one.

Use the signed two-point code

    H_s(v_0,v_1) = ((v_0+s v_1)/2,(v_0-s v_1)/2),
    H_s^-1(a,d) = (a+d,s(a-d)),  s in {1,-1}.

Recurse only on the first output, and retain each detail output.
Use `s=-1` for a paired-column bit and `s=1` for a last-column bit.
If `B` is the resulting code and `E` selects its leaf, then

    B^-1 E B = P Pi P^-1.

Encode both arbitrary owner fields, add the source leaf to the target
leaf, invert both codes, and undo `P`. The exact map is

    (x,y) -> (x,y+Pi x).

Every source value restores. The target keeps its arbitrary complement.
All detail coordinates remain available until the inverse code uses
them. No extra independent owner, clean input, or discarded borrowed
value is required. All row, compact, spectator, and polynomial indices
remain outside the projector address.

## 3. The remaining native action is a two-point leaf action

Write `L=E B P` for the leaf map. Its zero-detail inverse is
`J=P^-1 B^-1 E^T`. Then `JL=Pi` and `LJ=I` on the leaf.
Let `C_u` be the original one-bit complex native kernel on `u`, with
Fourier eigenvalues `1,i`. In spatial coordinates,

    C_u(v_0,v_1) =
      (((1+i)v_0+(1-i)v_1)/2,
       ((1-i)v_0+(1+i)v_1)/2).

For every odd `q` and every translation `delta` of the `n`-space,

    L C_q^tensor(lambda) = i^f C_u L,
    L X_delta^tensor(lambda) =
      (-1)^(f omega.delta) X_u^(omega.delta) L.

The Fourier support proves both identities, including their scalar
phases. In the last column, the address map has first output equal to
the sum of all input bits. Its dual sends `t omega` to `t e_0`, which
identifies the remaining character with the actual physical leaf bit
`u`. Thus the identities do not use an abstract mode with an unpaid
change of basis.

Suppose a completed physical owner frame is

    O = i^gamma (X_delta C_U)^tensor(lambda),

where `gamma` is the total tensor phase and `C_U` is a product on an
orthonormal basis of rank `r`. Put `epsilon=omega.delta`. Its exact leaf
action is

    L O = O_leaf L,
    O_leaf = i^(gamma+rf) (-1)^(f epsilon) C_u^(r+2epsilon).

In particular `O` commutes with `Pi`. Orthogonal conjugation of `C_U`
does not change this formula: every basis vector remains odd and every
orthogonal map fixes `omega`. This statement does not remove an extra
outer address permutation from an owner view.

For source and target frames of this form, the physical leaf update

    y_leaf += O_target,leaf O_source,leaf^-1 x_leaf

followed by the two inverse codes implements the logical shear
`y+=Pi x`. Indeed its physical added operator is

    J O_target,leaf O_source,leaf^-1 L
       = O_target Pi O_source^-1.

The leaf correction is one Gaussian unit times one of `I,C_u,X_u,C_u^-1`.
It can be applied by one fixed two-point coefficient pass on the leaf,
with the source operands saved in fixed registers. This is an explicitly
priced coefficient computation on the compressed leaf. It is not a
request for a full-field one-line native child.

## 4. Stream time, work area, and precision

The active stream sizes are `M,M/2,...,M/2^k`. The same geometric-volume
and fixed detail-stack proof as in `STREAM.md` applies to both signs.
The two arbitrary fields retain their full combined record count.
The leaf has `M/2^k` records, including the remaining bit `u`.

The row additions and their inverses cost

    O(V ((e log p)^tau+1)),  e=n lambda,  0<tau<1.

Both codes and inverse codes cost `O(V)`. The leaf correction costs
`O(V 2^-k)` when `V` uses the reserved full guarded record width.
The complete layer adds zero complex native children and zero owner
families. Its fixed work tapes are cleared before any next owner call.
These are asymptotic bounds from the pinned stream primitives; no new
explicit finite constant is claimed.

The untyped projector shear needs `k` added fractional bits and one
added magnitude bit, as in the even-width proof. For the frame-matched
leaf operation, one further fractional bit suffices: `C_u` and its
inverse have Gaussian half-integer coefficients. Their squares and
Gaussian unit phases need no additional fractional bit.

Use the maximum of the absolute real and imaginary input components.
Each code coefficient is an average or signed average. In a two-point
leaf kernel, each output component is a sum of four input components,
then divided by two. The temporary sum is at most four times the
source maximum. The target leaf is at most its old maximum plus twice
the source maximum. On inverse decoding the added leaf signal is a
signed constant on each selected-bit coset. The old target part is an
original partial average. Therefore two added magnitude bits suffice
for the whole frame-matched shear with saved local operands. The source
restores exactly. All arithmetic is exact on the enlarged dyadic grid;
there is no internal rounding.

The conditional recursive guard statement in `AMENDMENT.md` applies
with the local term `k+1=O(e)`. This does not verify a new dependency
path bound for an altered internal controller. At the two complete
provider boundary cuts in `OWNER-BINDING.md`, both frames are equal,
so the leaf correction is the identity. That boundary conjugation
extends to odd widths without a new native child.

## 5. Scope and checks

`check_odd_width.py` checks complete small arbitrary-input shears,
both code inverse orders, packed selected offsets, spectators,
polynomial coordinates, the explicit signed translation projector,
and the full two-point leaf identities. It also checks a frame-matched
physical shear against a direct physical operator. The exact finite
checks supplement the general proof; they do not prove the stream
machine primitives again.

This extension removes a tensor-parity restriction from the local
projector layer. It does not remove the affine coverage obstruction.
For example, a maximal odd-width affine sector still has fraction
`2^(-n ceil(lambda/2)+1)`.

Research and exact checks: OpenAI Codex under the user's direction.
The parent supplied the reversible Haar suggestion. The reviewed
correlated-access result supplies the sharp affine dimension bound.
Before any eventual PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
No PR, push, or commit was made.
