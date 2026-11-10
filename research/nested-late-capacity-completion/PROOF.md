# Shared-map completion with nested late capacities

This proof and construction were produced by Nick Petalas. Apache-2.0.

## Contract and theorem

Let V and W have the same finite dimension n over any field F. A fixed
injective linear map h:U -> W has image U'. For i=1,...,k, let A_i be
arbitrary subspaces of V and let C_1 <= ... <= C_k be subspaces of W.
The requested map is an isomorphism g:V -> W extending h and satisfying
g(A_i) <= C_i for every i. Inclusions may be equal, sources may overlap,
and zero spaces, k=0 and n=0 are allowed.

Put

```
S_i = A_1 + ... + A_i,
u = dim U,  e_0 = 0,
e_i = dim(U+S_i) - u,
c_i = dim C_i,  b_i = dim(C_i intersect U').
```

Such a g exists if and only if, for every i,

```
h(U intersect S_i) <= C_i,             (compatibility)
e_i <= c_i - b_i.                     (quotient capacity)
```

Over F_q, if these conditions hold, the exact number of requested maps is

```
product_(i=1..k) [q^(b_i (e_i-e_(i-1)))
                 product_(j=e_(i-1)..e_i-1) (q^(c_i-b_i)-q^j)]
  * product_(j=u+e_k..n-1) (q^n-q^j).
```

For k=0, read e_k=0. Empty products equal one. If any condition fails,
the count is zero. The count covers distinct linear maps, without quotienting
by basis choices or charging any physical realization cost.

## Reduction to cumulative sources

If g(A_j) <= C_j for j<=i, nesting gives g(A_j) <= C_i, hence
g(S_i) <= C_i. Conversely A_i <= S_i, so the cumulative inclusions imply
the original ones. This equivalence permits arbitrary source intersections;
it requires nesting only on the target side.

If g exists, its restriction to U intersect S_i is h and has image in C_i.
The induced injection from (U+S_i)/U into W/U' sends the e_i-dimensional
source into (C_i+U')/U', whose dimension is c_i-b_i. This proves necessity.

## Compatible basis extension

Choose a basis of U. Extend it successively to bases of U+S_i by choosing
e_i-e_(i-1) new vectors in S_i. Such choices are possible because the
cumulative sources form a flag. This ordered domain basis is fixed for
the remainder of the proof and counting argument.

Suppose an injective extension has already been defined on U+S_(i-1),
and maps S_(i-1) into C_(i-1). Since S_(i-1) <= S_i,

```
(U+S_(i-1)) intersect S_i = (U intersect S_i) + S_(i-1).
```

The already prescribed image of this intersection lies in C_i, by
compatibility and nesting. Thus extending by any images in C_i for the
new independent domain vectors preserves the entire inclusion g(S_i)<=C_i.

Work modulo U'. Images of the previous new basis vectors span an
e_(i-1)-dimensional subspace of (C_i+U')/U'. The latter space has dimension
c_i-b_i >= e_i. Extend these independent images to e_i independent vectors
in this quotient, and lift each new vector to C_i. The resulting map on
U+S_i is injective. This induction works over every field. Finally extend
the domain and image bases to bases of V and W. It yields the required g.

The bounded reference implements this same constructive choice without
enumerating a field: an available member of a basis of C_i must lie outside
the current image span whenever another independent image is needed.

## Counting every completion

Over F_q, fix the domain basis chosen above. At stage i, after a total of
j new basis vectors have been assigned, where e_(i-1)<=j<e_i, the image
span consists of U' plus j independent vectors that all lie in C_i.
Its intersection with C_i therefore has dimension b_i+j. The next image
can be any member of C_i outside that span. The exact number of choices is

```
q^c_i - q^(b_i+j) = q^b_i (q^(c_i-b_i)-q^j).
```

Multiplying these choices gives the stage factor in the theorem. Their
number depends only on the stated dimensions, so all earlier choices
receive exactly the same number of continuations. After the last contact,
there are u+e_k independent assigned images. Each remaining domain basis
vector has q^n-q^j choices when the current image span has dimension j.
This gives the final factor.

Every map has exactly one sequence of images of the fixed domain basis,
and each allowed sequence produces exactly one map. Thus this counts all
requested maps exactly once. No generic-position or infinite-field
argument is used for the finite-field count.

## A missed compatibility obstruction

Over F_2, take V=W=F_2^3 with coordinate vectors x,y,z. Set

```
U = <x+y>,       h(x+y)=z,
A_1=<x>,        C_1=<x>,
A_2=<y>,        C_2=<x,y>.
```

The individual one-capacity contracts admit 4 and 12 isomorphisms,
respectively. The first sends x to x, then y to x+z, and has four choices
for the image of z outside their plane. The second has three nonzero
choices in C_2 for the image of y, then fixes the image of x through h,
and has four choices for the image of z. Yet no shared map exists:
U <= S_2 and h(U)=<z> is not contained in C_2. This is a new joint-contract
example, rather than a re-evaluation of PR5020's one-capacity examples.

The quotient condition also detects a different missed obstruction. Take
U=0, A_1=<x>, A_2=<y>, and C_1=C_2=<x>. Both individual contracts are
feasible but S_2 has dimension two against a one-dimensional capacity.
The exact reference and the separate literal GL census check both examples.

## Scope and attribution

Brian / JoyboyBrian's PR5020 supplies the one-capacity prescribed-map
contract and asks for a second late capacity. The theorem above settles
its nested-target case, and includes any finite number of nested targets.
The proof is self-contained and does not invoke or recheck PR5020's theorem.
Basis extension, quotient dimensions and finite-field independent-vector
counts are classical; no general literature-priority claim is made.

The unrestricted GL contract does not supply a symplectic native map,
an absolute phase, chronological contact realization, a changed emitted
word or a favorable complete paid/productive invoice. No helper credit,
physical saving, new kappa, selected-frontier change or complete
multiplication theorem follows. Nonnested targets require a different
compatibility argument; applying this theorem to a nonnested list is invalid.
