# Independent review of explicit dyadic endpoint geometry

Result: **PASS for the geometric/address interface and its O(D) call form**.
Read [explicit-dyadic-geometry.md](explicit-dyadic-geometry.md) in full, compared its endpoint
requirements with the pinned source `build/interchange.tex`, and read and
replayed its exact checker in isolated `geometry-review-replay/`. This does
not certify the separate compact scalar/repair/call-grouping interfaces or
the complete multiplier.

## Algebra and complete bases

The hyperbolic form [[B,I],[I,0]] has the displayed inverse even if B is
singular. Its primal x_v,y_v have the source Gram blocks and are an
orthonormal pair. Projection of the coordinate complement C_v is injective
because C_v meets span(e,z_v) trivially. The individual basis and inverse
therefore exist with the explicit elementary construction.

For a product rectangle, the source and destination inner sides are
disjoint at differing outer coordinates. Thus all nonanchor star pivots
are distinct. The cross vector g has z coefficient -2; the distinguished
anchor has coefficient 1/2 when r_0 is formed. These facts prove the
complete basis and unit claim. Common outer coordinates contribute twice
their anchor to g and cancel from a, as required. The oriented differences
r_i-r_0 span the stars and g. Their common Gram value two makes E isotropic
and orthogonal to every pair. The source's E is the same space, because
differences of pair vectors are plus or minus half of r_i-r_0.

## Reserve-only transition

Equation (B2.6) uses primal coordinate coefficients, not bilinear pairings.
It sends p_i(c) to c, fixes each star, and sends g to a+2 sum s at a source
and -a+2 sum t at a destination. Consequently the change between complement
bases uses the occupied reserve coordinates alone. No query main field is
a temporary helper. The destination sign is essential.

After moving E late, write r_i=r_0+epsilon_i in its explicit E basis.
Projected early c differs from c by reference-pair and E components; the
main pair differs from the reference pair by E components. This gives
exactly the source lower triangular order. Its coefficients remain small
dyadics. Up to O(D^2) lower triangular shears are permissible ordinary work
with no extra recursive field swaps. This differs from the O(D)-length
lists for the complete endpoint layouts.

## Calls and numeric magnitudes

Complete lists use at most D stars, O(h) anchor additions, two projection
shears per retained coordinate, a fixed butterfly, and an O(D) coordinate
permutation. The reserve-only lists have the same bound. A conservative
16D elementary operations per layout, and 64D recursive swaps per layout
or inverse, cover their explicit constructions and spare-coordinate
ordering. A lower-target shear uses no swap, an upper-target shear uses
two, and an exchange uses one. Reversing the list gives its inverse.

Numerators are bounded fixed multiples of 1, 2 or 4; denominators divide a
fixed multiple of d, a power of two. Nontrivial diagonal pivots are bounded
powers of two. Inverses therefore retain small numeric magnitudes. A large
residue inverse modulo 3^f is never treated as an integer scaling with that
many increasing pieces: reverse the corresponding small scaling instead.

For a deliberately loose revised pencil constant, 1024 times
D(1+lambda)(1+m r_*/N) covers endpoint preparation/undo and both low-rank
conversion lists with the preceding allowance. This bounds the new lists;
it does not reuse the old source constant. The doubled ambient dimension
and revised constant must enter the new contraction check, although they
do not change its asymptotic parameter scale.
