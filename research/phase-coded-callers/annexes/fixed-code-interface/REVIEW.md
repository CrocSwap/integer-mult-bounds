# Independent review of the fixed-code criterion

Verdict: accept the projector graph criterion and its fixed ker R application
as a scoped appendix. The historical note states that its proof had no
independent review. This file provides that review separately and leaves
the note unchanged. The reviewer read PR-DESCRIPTION-STANDARD.md.

The necessity proof is valid over the complex numbers. Apply the quotient
map C^W -> C^W/E to D(e tensor v). Expanding A_i in a linearly independent
operator basis gives a zero linear combination in
(C^W/E) tensor End(V). Each diagonal coefficient map therefore preserves E.
A finite diagonal matrix has finitely many distinct eigenvalues. Lagrange
polynomials give its coordinate spectral projections. These projections
are orthogonal, even when the diagonal entries are not real. Their ranges
split E and E perpendicular. Thus invariance implies commutation with P.
This argument does not require any A_i to be normal or invertible.

The entry equation (c_i-c_j)P_ij=0 forces equality on graph edges and then
on connected components. Conversely, componentwise operator equality makes
D commute with P tensor I and preserves its range. Isolated coordinates,
zero coordinate projections, the full code, and the zero code cause no
exception: each isolated component imposes no relation with another port.

The source cover checker was read. Its graph test uses the Gram R^T R and
a breadth-first traversal. The new small checker independently forms the
rational projector from the pinned interface, checks R R^T=56I and RP=0,
and uses disjoint-set unions to find its components. The projector formula
then gives P^2=P and dimension 104. It finds one component of size 112.
A scalar operator that acts only on port zero gives a nonzero (I-P)DP
entry and supplies a concrete unequal-operator control. Normal Python and
-O give identical complete receipts. The broader 73-axis cover trace replay
is not needed or repeated here. Its unchanged receipt is retained for the
source lineage only.

The theorem is useful because it states the precise invariant-code
condition. Full individual coordinate projections do not imply independent
native cost. The example (u,v,u+v) is valid; the independent input dimension
is two. The example (u,u,v,v) correctly permits one common operator on each
pair. Neither example grants free preparation or borrowed-field restoration.

The later boundary-gauge argument in the original note is consistent with
commutation of the local shear, but it is already covered by the fixed-word
gauge package. It is not an additional result of this appendix. This review
makes no claim of literature-wide novelty. It excludes neither changing
codes nor joint native operators, and it supplies no new native program,
recursive admission, precision result, or complete kappa improvement.
