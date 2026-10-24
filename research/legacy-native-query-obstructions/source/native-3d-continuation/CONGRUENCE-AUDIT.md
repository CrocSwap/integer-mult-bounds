# Independent congruence proof audit

Audit date: 2026-10-12. A read-only algebra review of CONGRUENCE-PROOF.md
found no gap in the stated bound q>=p*m. No search was run, and no
additional agent was used.

## Ring and group map

The ring O consists of rationals with odd denominators. Its reduction
map to F2 is a ring map. If g=I+2A and h=I+2B, with A,B in Mat_m(O),
then (gh-I)/2=A+B+2AB. Thus a(gh)=a(g)+a(h) after reduction modulo 2.
The matrices I+e a(g) multiply by this rule because e^2=0. Each is a
unit, with inverse I+e a(g). The inverse formula in the proof also
shows that the original congruence subgroup is closed under inverses.

Therefore rho is a group homomorphism into GL_m(F2[e]/(e^2)). Its linear
extension is a unital ring map from F2[G] to the matrix algebra over
the dual numbers. This target algebra need not be commutative. The
proof uses no determinant or commutativity assumption for this map.
Applying the map entry by entry gives a ring map on native block
matrices, with r*m binary coordinates.

## Rank argument

Each A_i=(g_i-I)/2 is in Mat_m(O) and has rational rank one. Its minors
of size two are zero in O. They remain zero after reduction, so the
binary matrix a(g_i) has rank at most one. Reduction can lower the
rank to zero; this does not harm the inequality.

The mapped query is I_rm+e(N_i tensor a(g_i)). All cross terms in a
product vanish because e^2=0. The mapped endpoint is
I_rm+e(D tensor I_m), since a(-I_m)=I_m over F2. Comparison of the e
coefficients gives an equality of matrices over the field F2:

    sum_i N_i tensor a(g_i) = D tensor I_m.

Each left term has rank at most one. The right side has rank p*m by
the tensor-product rank formula. Rank subadditivity proves q>=p*m.
No rank over the nonfield dual-number ring is used.

## Common basis and helpers

A common rational ADDRESS basis change gives a group isomorphism
g -> T^-1 g T. It fixes z=-I_m and preserves the rational rank of
g-I_m. Thus the bound applies when all query maps satisfy the stated
congruence condition in that one basis. The transformed generated
group remains in the congruence subgroup. Separate basis choices for
individual maps do not suffice. The proof does not establish that
such a common basis always exists.

The rank argument uses the full exact endpoint I_r+(z-1)D. It does not
require D to be orthogonal or the workspace to have dimension p.
Idempotence of D gives the decomposition into productive roles and
helpers; rank(D)=p supplies the bound. This covers arbitrary dirty
helper inputs restored at the endpoint. It does not cover initialized,
discarded, or partial helper contracts. Any free binary DATA maps must
first be absorbed into the effective native controls.

For p=m=3, the theorem gives q>=9 under the common congruence
hypothesis. This review does not certify the hypothesis for an
unstated rational family or any integer-multiplication consequence.
No literature priority or novelty claim was checked.
