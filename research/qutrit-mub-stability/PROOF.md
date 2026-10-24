# Square-root repair of a complete qutrit MUB family

This scoped written proof answers B096 in David Ganz's [PR2849 atlas](../pure-math-atlas-400/volumes/02-geometry.md#b096). The finite exact linear-algebra certificate below is part of the proof. The differential-geometric argument is written mathematics, not a proof-kernel result.

## Statement

For U=(U_0,U_1,U_2,U_3) in X=U(3)^4, write

$$
F(U)_{abij}=|(U_a^*U_b)_{ij}|^2-1/3,
\qquad \Delta(U)=\|F(U)\|_2^2,
$$

where 0<=a<b<=3 and 0<=i,j<=2. There are 54 real residual coordinates. Let O be the equivalence orbit of the standard complete qutrit family, using exactly B074's common unitary, basis permutations, within-basis column permutations and independent column phases. Define

$$
\operatorname{dist}(U,O)=\inf_{V\in O}
\left(\sum_{a=0}^3\|U_a-V_a\|_F^2\right)^{1/2}.
$$

There exists epsilon>0 such that

$$
\Delta(U)\le\epsilon\quad\Longrightarrow\quad
\operatorname{dist}(U,O)\le \frac{2}{\sqrt3}\sqrt{\Delta(U)}.
$$

Thus the exponent one-half suffices, strengthening B096's proposed one-quarter exponent. The neighborhood threshold epsilon is existential and is not computed. This concerns already unitary bases in fixed dimension three. It is not a rounding algorithm for arbitrary matrices.

## 1. Cited classification and standard family

Use the complete-family uniqueness theorem of Stephen Brierley, Stefan Weigert and Ingemar Bengtsson, [All Mutually Unbiased Bases in Dimensions Two to Five, section 2.2](https://arxiv.org/html/0907.4097v2#S2.SS2). It implies F^{-1}(0)=O. Its displayed dimension-three representative is the family below. Appendix A also allows complex conjugation, which does not enlarge this family's B074 orbit: conjugating replaces the chirp indices (a,b) by (-a,-b), hence only permutes its three noncoordinate bases and their columns. The classification is a cited premise and is not reproved or audited here.

Put omega=exp(2 pi i/3), s=1+2 omega=i sqrt(3), and

$$
U_0^0=I,\qquad
(U_{a+1}^0)_{xb}=3^{-1/2}\omega^{a x^2+b x},
\quad a,b,x\in\{0,1,2\}.
$$

Since x^2=(0,1,1) modulo three, these are exactly I,F_3,D F_3,D^2 F_3 with D=diag(1,omega,omega). They are the standard complete family in the cited classification. Exact arithmetic verifies unitarity and all 54 unbiasedness equations.

## 2. Exact differential certificate

Identify a real tangent vector with four skew-Hermitian matrices H_a by dot U_a=H_a U_a^0. For each H use the following nine real basis directions, in this order:

- s E_00, s E_11, s E_22;
- E_01-E_10, s(E_01+E_10);
- E_02-E_20, s(E_02+E_20);
- E_12-E_21, s(E_12+E_21).

The Frobenius metric in these coordinates has diagonal matrix

$$
W=\operatorname{diag}(3,3,3,2,6,2,6,2,6)^{\oplus4}.
$$

For M=U_a^{0*}U_b^0, direct differentiation gives

$$
(DF_{U^0}H)_{abij}=
2\operatorname{Re}\left(
\overline{M_{ij}}\,[U_a^{0*}(H_b-H_a)U_b^0]_{ij}
\right).
$$

Let J denote this 54-by-36 real matrix. It has rational entries, even though the bases are complex. In the checker all field elements are pairs (a,b) for a+b omega with a,b rational. Conjugation is (a,b)->(a-b,-b) and Re(a+b omega)=a-b/2. The unnormalized phase matrices remove every square root from J.

Order rows lexicographically by (a,b), then (i,j), and columns by role followed by the nine directions above. A nonzero minor has row indices

```
0,1,3,4,9,10,12,13,18,19,21,22,27,28,36,37
```

and column indices

```
3,4,5,6,7,8,9,10,12,13,14,15,18,19,21,22.
```

Its exact determinant is -64/2187. Hence rank J>=16. The checker also forms the 21 infinitesimal equivalence directions: nine common H directions and twelve individual column phases. Their rank is 20, and J annihilates every direction. Thus rank J<=36-20=16 and

$$
\ker J=T_{U^0}O,\qquad \operatorname{rank}J=16.
$$

There is a particularly short metric certificate. With K=J^T J, the checker verifies every entry of

$$
K W^{-1}K=3K,\qquad \operatorname{tr}(W^{-1}K)=48.
$$

The symmetric positive-semidefinite matrix W^{-1/2}K W^{-1/2} consequently has only eigenvalues 0 and 3, with multiplicities 20 and 16. Therefore, on the Frobenius-orthogonal normal space to O inside T_{U^0}X,

$$
\|DF_{U^0}n\|_2=\sqrt3\,\|n\|_F.
$$

This is finite exact linear algebra on the fully specified differential. It is not extrapolation from numerical samples. A second coordinate formula, dot M=-K_a M+M K_b for right tangent coordinates, independently checks all 972 affected derivative entries after adjoint transport.

## 3. From the differential to the error bound

Equip X with the product Frobenius Riemannian metric. The connected symmetry group U(3) times twelve column-phase circles acts isometrically. Its orbit is a compact smooth embedded submanifold. The finite basis and column permutations give a finite union of such orbits. Distinct connected orbits are disjoint compact submanifolds; duplicate components can be discarded. Thus O has a tubular neighborhood in X.

The action preserves the norm of F, permuting its coordinates when necessary. Its differential carries orbit tangent and normal spaces isometrically to the corresponding spaces at every other orbit point. Section 2 therefore gives the same normal singular value sqrt(3) everywhere on O.

In a sufficiently small tubular neighborhood, write U=Exp_p(n), where p is in O and n is normal to O inside T_p X. Compactness of O and smoothness of F give a uniform Taylor bound

$$
F(\operatorname{Exp}_p n)=DF_p n+R_p(n),
\qquad \|R_p(n)\|_2\le L\|n\|_F^2
$$

for one finite L and all sufficiently small normal n. Shrink the tube until L||n||_F<=sqrt(3)/2. Then

$$
\sqrt{\Delta(U)}\ge \frac{\sqrt3}{2}\|n\|_F.
$$

The ambient Frobenius chord from p to U is at most the length ||n||_F of this geodesic. Hence dist(U,O)<=2 sqrt(Delta(U))/sqrt(3) throughout the smaller tube.

Finally, X is compact, and the complement of that open tube is compact and contains no zero of F by the cited classification. If this complement is nonempty, Delta has a positive minimum eta there. Choose 0<epsilon<eta. If it is empty, any positive epsilon works. This puts every U with Delta(U)<=epsilon in the tube and proves the stated global small-residual implication.

## Scope, attribution and remaining obligations

This contribution was produced by Nick Petalas. David Ganz's atlas supplies B096, B074 and its qualitative compactness motivation. Brierley, Weigert and Bengtsson supply exact complete-family uniqueness and the standard representative. Infinitesimal rigidity and the tubular-neighborhood error-bound method are established methods; no global literature-priority claim is made. The new project contribution is the square-root resolution of the stated atlas question with an exact differential and metric certificate.

The constants L, tube radius and epsilon are not made effective. No claim concerns nonunitary inputs, other dimensions, an algorithm to find the nearest family, a native supplier, kappa or the complete multiplication theorem. Independent human and formal proof-kernel review are unclaimed. Apache-2.0.
