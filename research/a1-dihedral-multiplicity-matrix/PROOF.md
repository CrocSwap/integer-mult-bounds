# A concrete multiplicity operator for the dihedral component

This contribution was produced by Nick Petalas. New material is Apache-2.0.
Claim type: scoped written proof with an exact finite matrix certificate.

## Input and predecessor boundary

Use the signed-orbit basis of the historical c=1, joint (+1,+1) space E and
its integer matrix B=4A_1 from unpaidmoon #6964. They are the two live JSON
inputs under `research/a1-joint-216-charpoly/evidence/`. E has dimension 216.
This package takes that representation and B as inputs. It does not rebuild
its characteristic polynomial or certify its origin as a physical operator.

The question and dihedral generators are unpaidmoon
[#7065](https://github.com/CrocSwap/integer-mult-bounds/pull/7065), head
`ee0202a8eafa4c0b84bef97ecfb5691f6affc9c6`. Its PROOF.md, sections "Operator
and group" and "The isotypic component", fixes the following convention.
The coordinate signed permutation has output i equal to eps[i] times input
inv[i]. Its label map sends each query port to the port of the corresponding
canonical root. Extend that map linearly to F2^9. On the 4096 coordinates
(i,a), it acts by the coordinate permutation, its sign, and that label map.

For R use inv=(0,1,6,7,3,2,5,4) and minus signs at 0,7. For U use
inv=(0,1,2,3,7,6,5,4), with all signs positive. In the pinned E basis they
are signed permutation matrices. The new checker derives those matrices
from the pinned query and the supplied orbit vectors, without importing any
predecessor executable.

Put

    P6 = 2I + R - R^2 - 2R^3 - R^4 + R^5,
    W = image_Q(P6).

The checker verifies P6^2=6P6 and trace(P6)=768. Since an idempotent over Q
has eigenvalues zero and one, rank(P6)=128. This identifies exactly the
component named W in #7065; no census of the full signed stabilizer is needed.

## Explicit construction

All indices below are zero based. For each j=0,...,215 form the integer column

    v_j = (I+U) P6 e_j.

Scan j in increasing order. Retain a column precisely when it is independent
over Q of the previously retained columns. The rule is unambiguous and the
checker finds 64 retained columns. Let V be their 216-by-64 matrix. Every
column has two or three nonzero entries. Thus this is a concrete basis
specified by fixed input bytes and rational arithmetic, without a search seed
or an arbitrary choice of a complement.

Express each Bv_j in this basis. Define the 64-by-64 matrix K by

    2 B V = V K.                                      (1)

The checker performs exact rational elimination for this construction. Every
entry of K is an integer. Define T=K/8, so A_1 V=V T.
The `--matrix` command emits every entry of K and every retained column of V,
together with the selected source-column indices and a canonical SHA256.
No predecessor polynomial is used to select or compute an entry of K.

Let C=[V,RV]. The exact identities checked on every column are

    U V = V,
    R^2 V = RV - V,
    U RV = V - RV,
    P6 V = 6V,
    2 B RV = RV K.                                    (2)

They imply P6 RV=6RV because P6 is a polynomial in R. Consequently image(C)
is contained in W. A separate dense modular elimination finds rank(C)=128;
a nonzero minor modulo 1000003 is also nonzero over Q. Thus C is an
isomorphism Q^128 -> W. In its coordinates,

    C^-1 (A_1|W) C = [[T,0],[0,T]],
    C^-1 (R|W) C   = [[0,-I],[I,I]],
    C^-1 (U|W) C   = [[I,I],[0,-I]].                   (3)

Here C^-1 means the inverse onto W, not an inverse of a rectangular map on
all of E. Equations (1)-(3) construct the multiplicity-space operator and
its actual intertwiner, rather than infer its existence from a squared
characteristic polynomial. The dihedral action is the usual rational
2-dimensional representation on the displayed two blocks. The commutant
therefore has the displayed two equal copies of T.

## Exact claim and remaining arithmetic question

The output T is dyadic. Its least positive common denominator in this basis
is exactly eight, certified by 8T=K integral and an odd entry of K. This is
an explicit rational answer to the matrix part of #7065's question. It does
not provide the integer matrix of T requested there. In particular, the
integral matrix K represents 8A_1, not A_1. No normalization factor is free.

As a consequence of (3), chi_(A_1|W)=chi_T^2. If the characteristic-polynomial
result of #7065 is used as a cited premise, uniqueness of the monic square
root in Q[x] gives chi_T=q, with q exactly as published there. This package
neither recomputes q nor independently verifies that predecessor result.
Likewise it computes no new zero-eigenspace or shifted rank of B.

## Certificate and verification scope

The replay constructs the matrix, verifies all exact identities, and checks
rank with an independently encoded dense modular elimination. A further dense
integer product checks both operator blocks directly. The output receipt binds
all six package files and all three live inputs by SHA256. `--matrix` includes
the complete executable certificate. The receipt is computed, never handwritten.

Controls change an entry of K, omit or duplicate a basis column, rescale K
incorrectly, or change its domain basis without changing K. They distinguish
one 64-dimensional block from the required 128-dimensional component, and
verify that the component is proper in E. These are finite certificate controls,
not an exhaustive perturbation census.

The result is exact linear algebra on the stated pinned inputs. It supplies no
native decoder, physical realization, changed recursive invoice, new kappa,
selected-frontier change or complete multiplication theorem. Numerical rounding,
source access, dirty restoration, ownership, frames, storage/tapes, compiler
closure and outer recovery remain separate obligations. Independent human and
formal proof-kernel review are unclaimed. No Lean, Docker, selected cold replay,
degree-881 replay or predecessor characteristic-polynomial suite is run.
