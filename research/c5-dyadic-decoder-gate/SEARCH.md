# Exact finite-search scope and completeness

The scientific source pins and row menu are fixed in README/RESULT. Enumerating
all 56-choose-5 subsets whose induced degrees are two recovers 23 C5s. On five
vertices, a simple graph with every degree two must be a single five-cycle.
A separately implemented path enumeration gives the identical sets and orders.

For each cycle, all 32 plane-subset tariffs are computed by binary elimination
on the complete two-vector bases. Rotations and reversal preserve the scalar
cycle mask. Cases are grouped only when one such permutation makes their entire
tariff tables identical. All 23 cases are represented by 16 tables; the C++
checker skips this reduction and checks all 23 directly.

The E8 row domain has two coordinate-symmetry orbits: axes and affine
hyperplane-supported rows. Affine permutations of F2^3 are transitive on points
and hyperplanes. Coordinate sign changes realize all sign choices, and whole-row
sign changes preserve the forced zeros, diagonals and supports. These operations
permute or sign the eight coordinate factors, leaving their summed tariff
unchanged. Therefore the first port can be anchored to root 0 (an axis) or root
8 (the first signed hyperplane root).

The two scalar ports within each plane can also be interchanged: the required
mask and complete plane tariff are unchanged. We enforce increasing root indices
within a plane. To justify this with the anchor reduction, choose an axis port
first when the first plane contains one; this maps to root 0. If both are
hyperplane roots, either can be mapped to root 8, the lowest index of that orbit.
Other planes can then be sorted freely. Equal roots on one plane cannot fit its
zero off-diagonal, so no equality case is omitted.

A state contains exact bitsets of still-possible roots and the current set of
planes using each coordinate. Adding a root enlarges each relevant binary
space. Pairing rank on a subspace cannot decrease when the subspace grows,
because its Gram matrix is a submatrix of the larger Gram matrix (or a pulled
back restriction in redundant bases). Hence the current price is a lower bound
on every completion. The search removes a root only if that lower bound exceeds
19, an already assigned forced scalar inner product is nonzero, or the proved
within-plane ordering is violated. It branches over every remaining root of a
chosen unassigned port. Empty domains reject; complete assignments are checked
as witnesses. There is no floating point, random stopping, timeout or heuristic
exclusion in this replay. Seed24 selected the initial object; the final census
is deterministic and exhaustive in its declared finite domain.

All branches finish without a cost-19 witness. Five axis columns always give a
cost-20 fitting matrix: assign the two ports of plane i to axes i-1 and i modulo
five. Every axis touches two orthogonal planes and costs four. The fitting rank
is five, crediting the predecessor's C5 construction rather than claiming a new
minrank. The exact complete cost is 20.

The generic replay uses only the Python search. The optional independent C++
search is separately written and derives each constrained pair from the ten
actual binary labels, whereas the Python search uses the verified abstract C5
mask. Both retain every plane dimension and agree on exclusion and a cost-20
positive control. Neither establishes an impossibility for arbitrary rational
factors, changed row menus or other matchings.
