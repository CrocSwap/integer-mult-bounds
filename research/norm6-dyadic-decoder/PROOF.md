# Integral norm-six cubic decoder

This is a proved algebraic component. It is not a
complete supplier or an improved multiplication exponent.

## Source geometry

Let L be an even integral positive definite unimodular lattice of dimension 48
and minimum 6. Choose one vector from each antipodal pair of minimum vectors.
Nebe's introduction to *A fourth extremal even unimodular lattice of dimension
48*, [arXiv:1312.3780](https://arxiv.org/abs/1312.3780), records the known
extremal48 lattices and their 52416000 minimum vectors. We use the exact Gram
matrix in the [Nebe-Sloane P48p catalogue](https://www.math.rwth-aachen.de/~Gabriele.Nebe/LATTICES/P48p.html).
The catalogue is retained byte for byte in sources/. Positive definiteness,
evenness, and determinant1 are checked locally. The minimum and complete shell
count remain dependencies on the published lattice result; no complete shell
enumeration is claimed.

For distinct antipodal representatives x,y, integrality and minimum 6 give

    ||x-y||^2 = 12-2<x,y> >=6,
    ||x+y||^2 = 12+2<x,y> >=6.

Consequently the possible pairings are the integers -3 through3. The diagonal
pairing is6. The kernel

    K(x,y) = (<x,y>^3 -4<x,y>)/192

has diagonal 1. Its off-diagonal values are0 at pairings -2,0,2; values1/64,
-1/64 at -1,1; and -5/64,5/64 at -3,3. Every entry is dyadic.

## Binary labels

Unimodularity makes the integral Gram matrix G invertible modulo2. Evenness
makes its reduction alternating. The even-weight subspace of F2^49 has a
nondegenerate alternating restriction of the standard dot product. A checked
symplectic congruence provides an isometry R from the lattice coefficient
space modulo2 to this even-weight subspace. Let w be the 49-coordinate all-one
vector and put

    q_x = w + R(x mod2).

Then q_x has norm 1 and

    q_x dot q_y = 1+<x,y> mod2.

Thus every forbidden distinct pair with binary pairing1 has K(x,y)=0. This is
the exact scalar fitting condition, rather than a parity claim about a
rational matrix with nonzero forbidden entries.

The labels are distinct on the minimum-vector lines. If x=y modulo2L, then
x-y=2z for a nonzero lattice vector z, so ||x-y||^2>=24. Distinct minimum
representatives have ||x-y||^2<=18. This is a contradiction. Choosing opposite
representatives does not create a second line port.

## Explicit dyadic factorization

Write t=x^T G y and v=Gy in integral lattice coordinates. Define the
integer-valued function f(u)=(u^3-u)/3. It is integral for every integer u.
Use the following source feature and target coefficient pairs:

| Source | Target | Number |
| --- | --- | ---: |
| f(x_i) | v_i^3 |48 |
| x_i | f(v_i)-v_i |48 |
| x_i^2 x_j, i!=j | v_i^2 v_j |2256 |
| x_i x_j x_k, i<j<k |2v_i v_j v_k |17296 |

For a_i=x_i v_i, the first two rows sum to

    sum_i (a_i^3-4a_i)/3.

The last two rows supply the mixed terms of (sum_i a_i)^3/3. The complete
scalar product is therefore (t^3-4t)/3. Scaling the target coefficients by
1/64 yields K exactly. All runtime coefficients belong to Z[1/2]; divisions
by3 only describe precomputed integral feature values. This avoids an
unproved assumption that a rational basis inverse is dyadic.

There are 19648 explicit terms. A rational cubic-feature rank bound of19600
also follows by absorbing the linear term into the trace of cubic tensors on
the norm-six sphere. We use the explicit 19648-term factorization, so no
dyadic lattice-basis reduction is needed for this component.

Each source support spans at most49 binary dimensions. The separate-copy
algebraic support bill is therefore at most49*19648=962752. This is an upper
bound on the labels a future centre program would need. It is not a checked
physical copy implementation, helper assignment, or precision proof.

## Verification scope

The package checks the exact48-dimensional Gram, reconstructs its positive
LDL factorization, checks the full binary coordinate isometry, and compares
all 19648 expanded polynomial monomials with an independently expanded cube.
It also checks676 pairings of26 actual norm-six vectors and38 additional
feature cases. Three corruptions reject an omitted cubic feature, wrong
normalization and a damaged binary chart. These finite checks support the
written identities; they do not enumerate the complete minimum shell.

## Next mathematical obligations

Construct the complete side map I-K using a bounded number of physical arrays
per port, with explicit common frames, arbitrary-dirty restoration, both
orientations, all transitions, and centre lifetimes. The useful construction
must fit a complete paid profile at the target rather than the favorable
model above. It must then receive a controller, ownership and precision proof.

The bit supplier also has to improve: its reviewed endpoint0.0017334270395898442
is below this campaign's final-kappa target. The candidate lattice kernel does
not settle that rail. Direct dualization would have a much larger rational
address dimension, so its cost must not be assumed to match the 49-bit complex
geometry.
