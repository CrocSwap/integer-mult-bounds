# Symmetric phase forms enlarge the native contact grammar

Prepared for Dugongue with substantial OpenAI Codex assistance. Apache-2.0.

## Exact model and conventions

Let V=F2^n with the ordinary nondegenerate dot product. Write a Pauli exponent as (x,z), with symplectic pairing x·z'+z·x', and put y=x+z. Let L0={(0,z)}. The retained canonical frame C_U has involutive symplectic action and sends L0 to

    L_U={(x,z): x in U, x+z in U^perp}.

A frame gauge F is assigned its INVERSE image chart L(F)=F^-1(L0). This orientation matters: a physical paid edge is F_next F_prev^-1. Its Fourier rank is n-dim(L(F_prev) intersection L(F_next)). For canonical C_U the inverse and forward symplectic images coincide; this coincidence must not be assumed for an arbitrary new gauge.

For a subspace U and a symmetric bilinear form b:U×U→F2 define

    L(U,b)={(x,z): x in U, (x+z)·u=b(x,u) for every u in U}.

The old canonical-frame grammar is precisely b=0.

## Theorem 1: explicit gauges for every such chart

L(U,b) is an n-dimensional Lagrangian. Every Lagrangian whose x-projection is U has this form for a unique symmetric b.

Proof. For each x in U, the allowed y=x+z form an affine translate of U^perp, so total dimension is dimU+(n-dimU)=n. For two members (x,y),(u,t), the symplectic pairing is x·t+y·u=b(u,x)+b(x,u)=0. Conversely the vertical kernel of a Lagrangian with x-projection U is exactly U^perp; hence y·u is independent of the chosen y above x. It defines b, and isotropy proves symmetry.

The construction is an exact Clifford circuit. Choose basis columns B of U, extend them to an invertible n×n matrix H, write S for the symmetric matrix of b on B, and put

    Q = H^-T blockdiag(S,0) H^-1.

Then Q is symmetric and x^T Q u=b(x,u) on U. The retained diagonal Clifford D_Q acts symplectically as (x,z)→(x,z+Qx), equivalently (x,y)→(x,y+Qx). Choose

    F(U,b)=C_U D_Q.

Because D_Q has involutive symplectic action and C_U^-1(L0)=L_U, its inverse-image chart is D_Q^-1 L_U=L(U,b). In the retained Op.then convention this circuit is `diag(Q).then(canonical_frame(U))`: D_Q acts first. The diagonal's Z4 linear coefficients have parity equal to diag(Q), as in the retained exact implementation. This fixes an actual circuit and absolute phase, not just a projective tableau. Different extensions of b may give different gauges with the same chart; their relative operator is monomial and is not silently identified as an exact circuit.

## Theorem 2: complete paid rank formula

For charts (U,b),(W,c), put I=U intersection W and let D be the symmetric form (b+c) restricted to I. The exact Fourier rank of F(W,c) F(U,b)^-1 is

    r = dimU+dimW-2dimI + rank(D).

Proof. A vector in the intersection of the two Lagrangians has x in I. Its prescribed y-functional on U+W exists precisely when b(x,v)=c(x,v) for every v in I, that is, x lies in the radical of D. This radical has dimension dimI-rank(D). For each such x, allowed y form an affine space of dimension n-dim(U+W). Thus the intersection dimension is n-dimU-dimW+2dimI-rank(D). The B-block rank equals n minus this dimension, by applying F(W,c) to the inverse-image intersection. This proves the formula.

In particular, every old paid rank is preserved exactly if the two forms agree on I. These are linear equations over F2, not nonlinear rank constraints. Once a candidate is emitted, the retained exact Clifford normal form constructs and checks its two monomial adapters and rank-r Gaussian child, with absolute phase. Every adapter has the native volume-linear implementation already charged by the source-bound provider theorem. This is a sufficient physical realization of the proposed rank, not free nonmonomial motion.

## Theorem 3: native warp constraints are linear

For the retained monomial K_G, Q_G=I+G^-T G^-1 gives

    (x,y)→(Gx,G^-T y).

Therefore K_G sends L(U,b) to L(GU,b'), where

    b'(Gx,Gu)=b(x,u).

The physical fixed-logical-warp edge F_next K_G F_prev^-1 is monomial exactly when K_G L_prev=L_next. With the retained subspaces already satisfying GU=W, this is exactly the displayed bilinear transport equality. It is linear in the local form coefficients. Its exact monomial and absolute phase are emitted from the full retained Clifford circuit, rather than inferred from the chart alone.

## A sufficient positive profile mechanism

Keep the actual scalar chronological word, original subspaces and logical warp maps fixed. Assign one form to each shared scalar-contact gauge and to all role endpoints. Impose:

1. zero forms at all frozen main input/output endpoints;
2. equality of forms on every paid-edge intersection;
3. the bilinear transport equations for every fixed logical native warp;
4. one common actual gauge at each scalar contact;
5. zero forms at frozen owned-center and non-G adapter boundaries, unless their exact symplectic constraints are separately implemented.

Every equation is homogeneous over F2. Solve it exactly. For a helper entrance (U,b) and exit (W,c), its productive Gaussian rank becomes its old rank plus rank((b+c)|I). It remains an arbitrary independent input; no initialized storage or redundant productive credit has been introduced. If ANY helper difference is nonzero on I, its productive rank strictly increases while every paid rank is unchanged. All other helper ranks weakly increase. Hence the complete productive moment increases for every positive exponent, with the entire paid invoice unchanged. The controller's multiplicity must be retained when rebuilding its whole moment.

This is a genuine sufficient route to a changed supplier invoice. A numerical exponent additionally requires all-column endpoint reconstruction, absolute-phase lowering, actual whole-job adapters, exact critical-root/majorant and finite-compiler admission. The homogeneous equations alone are not a new multiplication theorem, and existence of a useful nonzero solution is not assumed.

The all-column semantic proof is ordinary gauge telescoping: replacing each logical operation M_j by F_j M_j F_(j-1)^-1 gives total F_final(M_s…M_1)F_initial^-1. Main gauges are frozen, scalar contacts use a common gauge, and helper relative endpoints are updated honestly. If helper entrance gauges vary, the retained independent-helper direct-sum endpoint contract is also used: helper input blocks have zero transfer to main outputs. This must be checked in the old all-column certificate. Under that explicit source fact, the old main ABI is preserved exactly; frozen main endpoint gauges alone do not imply it for an arbitrary globally coupled operator. No quotiented or missing main chart is substituted.

## Minimal exact coordinates for the solver

If U has basis B=(u1,…,ud), use d(d+1)/2 variables S_ij with i<=j. Express x=B a and u=B c. The coefficient of S_ii in b(x,u) is ai*ci; that of S_ij for i<j is ai*cj+aj*ci. A paid edge uses a basis of its intersection and imposes equality on all basis pairs. A native warp uses all source-basis pairs and their G-images at the target. There are no floating coefficients or optimization tolerances. An actual solution must be substituted back into every original equation before it is used to emit a witness.

## Credit and boundary

The Lagrangian description, symmetric-form coordinates and Clifford normal form are classical symplectic linear algebra. The contribution is their exact, source-convention-aware use as a constructive phase-flow extension of the current native contact search. Credit Cinna Davis's supplier interface, Cao Yifan's joint helper/native-map search, Dugongue's transported-frame and Word RAM work, zxv and all retained Clifford/whole-job compiler sources. No novelty priority is claimed for the constituent linear algebra. This note supplies a sufficient new search grammar and preserves exact admission obligations; it does not report an unobserved useful nullspace solution or a new kappa.
