# Why the scalar shear rank bound does not extend to operator-valued gathers

2026-10-23. Elementary read/derive boundary, not a new paper result, a successful released endpoint, or a paid-query saving. No source/native program or search was executed. The main packed candidate is unchanged.

The source-bound scalar screen is `outputs/released-operator-intersection-20261023/PAID-SHEAR-SCREEN.md`, SHA256 `81fefcf4a1be0be04076e7cba0e27ba4afe732d4810a13b0a76dbe827967c10c`. It proves at least 112 updates for products of scalar-owner rank-one X-Gaussian shears because extracting the identity address coefficient from the telescoping sum preserves scalar owner rank at most one per update. Its stated exclusion of operator-valued gather/scatter is essential.

## A one-update counterexample to the proposed rank extension

Use n=112 owners and choose n distinct fixed Pauli-X translations P_i on the existing 17 one-column address bits. There are more than n available; no new axis is needed. Use their exact columnwise lifts at every positive width. Distinct translations remain nonproportional, and P_i P_j^-1 is projectively the identity exactly when i=j.

Define an operator column U and row V by

    U_i=P_i,     V_i=c_i P_i^-1,

where 56 coefficients c_i are +1 and 56 are -1. Then

    VU=(sum_i c_i) I=0.

Consequently (UV)^2=0 and the single operator-valued shear

    S=I+UV

has exact inverse I-UV. The projective-identity coefficient of its (i,j) entry is

    B0(S-I)[i,j] = c_i if i=j, and 0 otherwise.

Thus rank(B0(S-I))=112, despite there being only one operator-valued update. In particular the scalar inequality rank(B0-I)<=m cannot be applied with m=1 here, even with the nilpotence condition that makes the inverse explicit.

The ordinary physical interpretation is gather g=sum_i c_i P_i^-1 x_i before overwriting any x_i, then scatter x_i <- x_i+P_i g. All reads, copied source fields, Pauli maps, additions, owner routing and cleanup must be charged. No Gaussian call appears in this example. Since Vx'=Vx, the gathered value can also be recomputed from the final bank for an exact reversible cleanup outline. This statement supplies no measured finite Tape bill or precision/width implementation.

## Even B0=0 alone does not identify a solution

For a separate algebraic example let V_i=P_i^-1, so VU=112 I. Then

    T=I-UV,        T^-1=I-(UV)/111.

The inverse identity follows from (UV)^2=112 UV. Here B0(T)=0 exactly: every diagonal identity contribution cancels and all off-diagonal translations are nonidentity. The inverse coefficient 1/111 adds a real fixed-precision/ordinary-cost obligation; it is not declared free by this algebraic formula.

This example shows that removing the identity coefficient is only a necessary endpoint condition in the scalar screen. It does not show that all other nonmonomial endpoint classes disappear.

## Why neither example is a released construction

Both examples are finite scalar sums of columnwise monomial Clifford operators. They commute with the Pauli-X Gaussians Q and D3, so their first three control expressions stay in that declared free algebra. The independently reviewed full Clifford obstruction still excludes their fourth endpoint from the required monomial span.

Specifically, the source-bound proof `outputs/released-operator-intersection-20261023/PROOF.md`, SHA256 `c20b2f13e875d9e1fb6d0743693f9deccc4f7d68dcdc55ec241324ed3d7de7bc`, has independent PASS review at `outputs/released-operator-independent-review-20261023/REVIEW.md`, SHA256 `23b5aa5df049cb4a8fe3349c054e27d84ca151e29e263c658670639bad082428`. It forces the entire endpoint to vanish if it belongs to that fixed columnwise monomial-Clifford class, contradicting invertibility. S and T are therefore examples of a failed proof extension, not candidate t0 solutions.

The always-valid ambient factorization inequality rank(S-I)<=dim(one gathered field) does not restore the scalar owner bound: extracting the identity group coefficient can increase scalar owner rank. To derive a useful paid-query lower bound for a changed gather model, one needs an additional whole-endpoint or information constraint tied to the actual queried field, width, source access and restoration. To claim a constructive saving, one needs an actual native/query observation and a complete mixed sandwich and inverse bill. Neither follows from naming an operator-valued gather.
