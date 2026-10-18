# The complex canonical-frame rank obligation

All vector spaces in this note are over F2. This is a written algebraic proof
for the pinned complex canonical-frame convention, together with finite
implementation evidence. It is not a Lean proof or a full multiplication theorem.
The rank formula is standard symplectic linear algebra; no discovery priority is
claimed. The contribution is its source-bound independent verification.

Let the Pauli label space be `E = F2^n x F2^n`, with coordinates `(x,z)` and
symplectic pairing `x.z' + z.x'`. Let `Z = {(0,z)}`. Write the symplectic matrix of
a Clifford operator as `S = [[A,B],[C,D]]`. Then

```
rank(B) = n - dim(Z intersect S^-1 Z).                 (1)
```

Indeed, the kernel of the restriction of the x-coordinate projection to `S Z`
is exactly `S Z intersect Z`; its dimension is that of `Z intersect S^-1 Z`.
No phase information appears in (1).

## Canonical frame preimage

For any subspace U, define

```
L(U) = {(u,u+w) : u in U, w in U^perp}.
```

The two parameters are independent, so `dim L(U)=n`. It is isotropic: the
pairing of `(u,u+w)` and `(v,v+t)` is `u.t + v.w = 0`. Thus it is Lagrangian.
No nondegeneracy or nonalternating assumption on U is required.

The pinned `canonical_frame` constructs a full invertible matrix G whose first
r columns are the input basis of U. Put `E_r=diag(I_r,0)` and
`Q=I+G^-T G^-1`. Its monomial conjugating operator K has action

```
K(x,z) = (Gx, QGx + G^-T z).
```

The r active C gates have action `(x,z) -> (x+E_r z,z)`. Ignoring phases, their
inverse has the same action. The compiler frame F_U is `K C_r K^-1`.
Since K^-1 preserves Z, the preimage `F_U^-1 Z` is the set of vectors

```
K(E_r t,t) = (G E_r t, Q G E_r t + G^-T t)
           = (u, u + G^-T (I-E_r)t).
```

As t varies, u ranges over U and the second parameter ranges independently
over U^perp. This proves `F_U^-1 Z=L(U)`. It also covers the compiler's empty
and full-space shortcuts directly. Different basis extensions can alter the
frame operator while retaining this preimage and the rank conclusions below.
The literal implementation checks this preimage for every finite frame used.

## Arbitrary ordered transitions

For the ordered transition `S=F_V F_U^-1`, apply the invertible map `F_U^-1`
to the intersection in (1). This gives

```
rank(B(S)) = n - dim(L(U) intersect L(V)).
```

A vector in the intersection has `u in U intersect V` and
`w in U^perp intersect V^perp = (U+V)^perp`. Therefore

```
dim(L(U) intersect L(V)) = dim(U intersect V) + n - dim(U+V),
rank(B(S)) = dim(U)+dim(V)-2 dim(U intersect V).        (2)
```

For nested spaces this is exactly `abs(dim(U)-dim(V))`, the obligation asserted
by the retained `phases_full.py`. For nonnested spaces the absolute dimension
difference undercounts by twice the smaller space's dimension outside the
intersection. For example, `U=<1>` and `V=<2>` both have dimension one, but their
transition has B-rank two.

The same formula does not by itself certify global phases, monomial adapters,
operator equality, real-prime residual interfaces, physical tape, numerical
precision, or supplier admission. In particular, it must not be transplanted to
the binary residual model audited in PR911/920 without its own derivation.

## Why the finite census is complete

Start from the zero subspace and repeatedly adjoin every ambient vector.
Every subspace is reachable by adjoining the elements of one of its bases.
Deduplicating complete vector sets therefore enumerates exactly all subspaces.
For n=5 the dimension counts are `1,31,155,155,31,1`, independently agreeing
with the Gaussian-binomial numbers. All `374^2=139876` ordered pairs are checked,
including degenerate spaces, empty/full spaces, both directions and nonnested
pairs. There is no random sample, search cutoff or omitted admission shortlist.

The geometric engine uses explicit vector-set intersections. The other engine
reconstructs each frame's elementary P/D/C action on all 2n Pauli generators,
forms the ordered transition, extracts its B columns and eliminates them. It
imports no producer compiler, Pauli tableau or stored rank implementation.
All ranks agree. Only the selected recipe rank fields are compared: the recipe
phase fields are retained source data, not checked by this package. An explicit
in-memory phase mutation preserves the rank result and documents this boundary.
