# Scalar sector incidence and the seven first-pivot weights

Work over F2. Fix commuting idempotents P,Q on V with ordered joint sectors V00,V10,V01,V11 of dimensions r00,r10,r01,r11. A scalar split is a vector a and covector b with ba=1; the common first guard is bPa=bQa=1. Scalars, vectors and covectors are labeled; no quotient or division by any sector centralizer is taken in the count.

## General scalar incidence formula

Write a=(a_j), b=(b_j), and h=b11 a11. The three guard equations are equivalent to b00 a00=b10 a10=b01 a01=1+h, b11 a11=h. For a sector of dimension r, the simultaneous GL(r,2) action (a,b) -> (ga,bg^-1) has exactly these nonempty types:

| Type | Incidence | Weight w_r |
|---|---|---:|
| Z | a=0,b=0 | 1 |
| A | a nonzero,b=0 | 2^r-1 |
| B | a=0,b nonzero | 2^r-1 |
| N | a,b nonzero, ba=0 | (2^r-1)(2^(r-1)-1) |
| C | ba=1 | (2^r-1)2^(r-1) |

For r=0 only Z exists; for r=1 N does not exist. For positive r, count a first, then the covectors in its annihilator or affine complement to obtain these weights. Transitivity follows by extending a nonzero a to a basis, and, when b is nonzero, choosing the remaining basis in ker b (type C) or one vector outside ker b (type N). Types A and B are the single nonzero-vector and nonzero-covector orbits. Thus these are actual incidence orbits, not just ranks with a guessed multiplicity.

Let T_0(r)={Z,A,B,N} with zero weights omitted and T_1(r)={C}, also omitting zero weights. For every compatible tuple tau in T_(1+h)(r00) x T_(1+h)(r10) x T_(1+h)(r01) x T_h(r11), choose one canonical sector realization, assemble a,b, and form the ordered residual pair R(tau) on ker b. Then, for any simultaneous-conjugacy class O of residual pairs,

    B(O) = sum over h=0,1 and compatible tau with R(tau) in O of product_j w_(r_j)(tau_j).

This is an all-dimension binary scalar-pivot formula. It does not claim an efficient general residual-classification algorithm or an arbitrary-field theorem. The proof is a disjoint partition into sector orbits: each tuple has the displayed product size, and the product sector group commutes with P,Q and sends the residual pair by simultaneous conjugacy. The guard equations themselves imply ba=1, so there is no extra compatibility factor or completion gauge. Different tuples may reach the same residual class; their weights must be added, not quotiented.

For x in H=ker b the coordinate-free residual maps are

    Sx = Px + Pa (bPx),    Tx = Qx + Qa (bQx).

Both images lie in H. These are the usual Schur complements in any basis (a,N) with N a basis of H. They have image im P intersect H and kernel H intersect (ker P + <a>), and the analogous statements hold for Q. The image statement follows since bPa=1 and the displayed formula is the projection within im P onto its intersection with H. The kernel follows from Px in <Pa> and injectivity of P on <a>. This gives the promised image/kernel interpretation of the incidence types.

## Profile (1,1,1,2): start with weights 1 and 3

Use axes e0,e1,e2,e3,e4 with P=diag(0,1,0,1,1), Q=diag(0,0,1,1,1). For h=0, each one-dimensional sector is forced to C: a_i=b_i=1 for i=0,1,2. Write a=(1,1,1,u), b=(1,1,1,v), vu=0 on the two-dimensional 11 sector. Its four incidence types have weights 1,3,3,3.

The residual images are {(0,vz,0,z)} and {(0,0,vz,z)}. They coincide exactly when v=0; otherwise their intersection has dimension one. The kernels are spanned respectively by (1,1,0,u),(0,1,1,u) and by (1,0,1,u),(0,1,1,u). They coincide exactly when u=0; otherwise their intersection has dimension one. Consequently Z gives S=T (state 1) with weight 1. A gives equal images and distinct kernels (state 2) with weight 3. B gives distinct images and equal kernels (state 5) with weight 3. N gives both intersections of dimension one (state 6) with weight 3. Sector transitivity proves each is a single residual class. Their intersection dimensions distinguish them, and direct substitution of one canonical seed per type identifies the displayed representatives in the calibration table. For N, the commutator has rank two; hence it cannot merge with any h=1 case below.

For an explicit coordinate check, the deterministic increasing-vector basis of H used by verify.py gives the following seeds and invertible intertwiners K (all matrices encoded by integer rows). Each row satisfies S_seed K=K S_rep and T_seed K=K T_rep; invertibility is independently checked. These four witnesses make the state identification concrete without an orbit search.

| Type | a,b | S_seed | T_seed | K |
|---|---|---|---|---|
| Z | 7,7 | (0,0,4,8) | (0,0,4,8) | (2,1,8,4) |
| A | 15,7 | (0,0,5,8) | (0,0,6,8) | (2,3,10,4) |
| B | 7,15 | (4,0,4,8) | (0,4,4,8) | (7,2,4,8) |
| N | 15,23 | (8,0,13,8) | (0,8,14,8) | (6,3,10,4) |

In particular, the first two weights are 1 and 3 before any centralizer enters. The credited stabilizers 36 and 4 give complete-header multiplicities per coordinate pair of 36 and 12, respectively. Orbit size alone does not encode how many input splits reach that orbit.

## The h=1 branch

The 11 sector is C, with weight (4-1)*2=6. Choose a11=e3, b11=e3*. Each of the three one-dimensional sectors is Z,A or B, each of weight one. This gives 27 incidence tuples, independently of the six realizations in sector 11. On H identify coordinates with (x0,x1,x2,x4) by x3=b0 x0+b1 x1+b2 x2. Since a_i b_i=0, the residual maps are the direct sum of the common identity on <e4> and the following rank-one projections on F2^3:

    S'=e1 (a1 b0, 1, a1 b2),
    T'=e2 (a2 b0, a2 b1, 1).

Their images are distinct. S'T' is nonzero exactly when sector 10 is A and sector 01 is B; T'S' is nonzero exactly in the opposite case. These cases are mutually exclusive. Each allows three choices for sector 00, hence has three tuples. The remaining 21 tuples have both products zero.

This is a sufficient three-way classification, not just a rank filter. When both products vanish, the two idempotents commute and simultaneously diagonalize with sector dimensions (1,1,1) on F2^3. When S'T' is nonzero and T'S'=0, write S'=u s and T'=v t. Then s(u)=t(v)=s(v)=1 and t(u)=0. The covectors s,t are independent, so a nonzero vector w spans their common kernel and is outside <u,v>. The basis (w,v,u) gives the same fixed ordered pair in every such case. Interchanging the roles proves the reverse-product case. Adding the common e4 line gives states 3,4,7 respectively. Their (rank ST,rank TS) are (1,1),(2,1),(1,2); their commutator ranks are 0,1,1. They cannot merge with the four h=0 classes: state 1 has equal maps; states 2 and 5 have equal images or equal kernels; state 6 has rank-two commutator.

Therefore, in published order, the split weights are

    (1, 3, 21*6, 3*6, 3, 3, 3*6) = (1,3,126,18,3,3,18).

The h=0 and h=1 contributions are 10 and 162, disjoint because h is an actual scalar attached to the split. They exhaust all common-guard splits by the sector equations. The remaining 496-172 splits fail a common first guard; there is no enumeration of those splits in this proof.

## Completion and credited continuation

Each split (a,b) extends to exactly |GL4(F2)|=20160 headers by choosing an ordered basis of H. All 31 nonzero vectors a have 16 covectors b with ba=1, so the total split count is 496 and the complete-header denominator is 9999360. Completion conjugates the residual pair; an orbit with stabilizer z is hit z times per split. Thus first-guard headers in a state number B(O)*20160, while each residual coordinate pair occurs B(O)*z times. These are distinct quantities.

Sagar Thakrar's retained exact README at commit 93bebe5e1ad3dd17a97ae79f27e1a35edd3630aa proves the complementary-plane continuation rule and reports stabilizers z=(36,4,1,1,4,4,1), depth-two orbit counts f=(100,468,366,816,468,270,816). These are credited premises, not a new continuation/centralizer calculation here. Combining the newly derived inputs with that rule gives sum B*z*f=93564. The per-state contributions are (3600,5616,46116,14688,5616,3240,14688). This recovers the published total without repeating its input census. The numerical continuation table is source-bound but not independently replayed by this package.
