# Exact faithful width of an alternating binary space

Let V be an n-dimensional vector space over F2, and let B be an
alternating bilinear form on V. Alternating means B(x,x)=0 for every x;
in characteristic two this also implies symmetry. Write r=rank(B) and
k=n-r for its radical dimension. A faithful dot realization is an
injective linear map f:V -> F2^m satisfying f(x) dot f(y)=B(x,y).
The target has its ordinary coordinate dot product.

The exact minimum m is

```text
0        if n=0;
n+1      if n>0 and k=0;
n+k      if k>0.
```

This theorem preserves the entire input vector space, including its
radical. It does not prescribe a quadratic refinement or a native word.

## Lower bounds

Let W=f(V), and let R=f(rad(B)). Injectivity gives dim(W)=n and dim(R)=k.
The isometry condition gives R subset W-perp in the nondegenerate ambient
dot space. Thus k <= m-n, proving m>=n+k.

If k=0 and n>0, equality m=n would make f surjective. The ordinary dot
product would then be alternating, contrary to e_1 dot e_1=1. Hence
m>=n+1. For n=0 the empty map attains zero.

The first argument is the usual radical-completion bound. The
nonalternating instance in THU New Media Research Center's PR5464,
`research/odd-e8-polarized-native/EMBEDDING-PROOF.md` section 2, already
uses it. The new scope here is the exact alternating answer with arbitrary
radical, together with a constructor and the singular-trace corollary.

## An explicit minimum realization

The elementary hyperbolic splitting algorithm gives a basis in which

```text
B = H^(direct sum s) direct sum 0_k,
H = [[0,1],[1,0]],  r=2s.
```

For completeness, if B is nonzero choose u,v with B(u,v)=1. Replace any
other basis vector z by z+B(z,v)u+B(z,u)v. It becomes perpendicular to
u,v, and the changed vectors together with u,v are still a basis. Split
off this pair and repeat. When the remaining form is zero the remaining
basis vectors span the radical. This also proves r is even.

First realize the s hyperbolic pairs on coordinates 0 through r by

```text
u_i = e_(2i) + e_(2i+1),
v_i = sum_(j=2i+1)^r e_j,       0 <= i < s.
```

Each u_i has even weight, and each v_i has weight r-2i, also even.
Their pairings are u_i dot u_j=0, v_i dot v_j=0 and
u_i dot v_j=[i=j]. For the second equality, when i<j the intersection
of the two suffixes is v_j, whose weight is even. For the last equality,
both coordinates of u_i lie in v_j if i>j, neither if i<j, and exactly
one if i=j. Consequently these r vectors are independent.

When k=0, these vectors realize B in m=r+1=n+1 coordinates.

When k>0, append one coordinate and use

```text
z_0 = sum_(j=0)^(r+1) e_j.
```

It has even weight r+2 and is perpendicular to all u_i,v_i because they
have even weight. Its last coordinate proves independence from them.
For each 1<=j<k, append a disjoint coordinate pair and put

```text
z_j = e_(r+2j) + e_(r+2j+1).
```

Each z_j has zero self-pairing and is perpendicular to every other
displayed vector. Its private coordinates prove independence. The full
map has r+k=n independent images in exactly r+2k=n+k coordinates.
This also covers r=0, where all images are disjoint two-coordinate pairs.
Transporting this map through the adapted basis gives the required
realization in the original input coordinates. The lower bounds show
that every displayed width is optimal.

One radical direction absorbs the extra coordinate needed by a
nonsingular alternating space. Treating a nonzero H block and each
radical direction independently would instead use r+1+2k coordinates.
The construction removes precisely that unnecessary extra coordinate
when r>0 and k>0.

## F4 Hermitian trace corollary

Let h be a Hermitian form on an F4 space of dimension d and F4 rank a.
For B(x,y)=Tr_(F4/F2)(h(x,y)), Maximooch's PR831 proves that B is
alternating and that its radical is exactly the binary version of the
Hermitian radical. That identity is a cited premise here. Therefore

```text
n=2d,  r=2a,  k=2(d-a),

minimum faithful dot width = 0             if d=0;
                            2d+1          if a=d>0;
                            4d-2a         if a<d.
```

The singular case has an exact answer without assuming that a support
restriction or intersection is nondegenerate. No radical vector is
discarded or identified with another input vector.

For example h=diag(1,0) has trace Gram H direct sum 0_2 in the binary
basis (1,t) on each F4 coordinate, where t^2+t+1=0. The explicit images
3,6,15,48, written as six-bit integers with the low bit first, have that
Gram matrix and are independent. Width six is necessary and sufficient.
The three-bit H embedding alone loses both radical directions. Separately
adding two isotropic pairs would use seven bits; shared padding saves one.

## Exact limits

Preserving B does not preserve the ambient weight modulo four or an
arbitrary supplied quadratic phase. For H, the images 3 and 6 have weights
two, so they do not preserve a refinement that vanishes on both input
basis vectors. This theorem supplies binary vector identities and Gram
pairings only. It does not supply a compatible Gaussian/native phase,
source/read incidence, nested frame itinerary, physical owner schedule,
dirty restoration, paid caller, precision/tape bound or multiplication
theorem. Those costs and obligations remain unresolved.
