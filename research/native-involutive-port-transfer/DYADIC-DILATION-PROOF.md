# Exact dyadic involution completion of the retained native port code

This is a universal sufficient coefficient theorem with an explicit circuit. It does not assert that the circuit is free between the physical entrance and exit charts of the native multiplier, and it supplies no new κ value.

Let R be an m×n matrix over a field in which 2 is invertible, with RRᵀ=56I_m. Set

    A = I_n − RᵀR/4,
    C = [[A, 3Rᵀ], [−R, 13I_m]].

Then C²=I_(n+m). All coefficients are dyadic whenever the entries of R are dyadic. In particular, the inverse is the same circuit, and no division by 13 or 7 is needed.

Indeed, put G=RᵀR. Then G²=56G, so A²=I_n+3G. Moreover ARᵀ=−13Rᵀ and RA=−13R. Multiplying the four blocks of C² gives I_n, 0, 0, and −3RRᵀ+169I_m=I_m, respectively. This proves the identity for arbitrary inputs, not only zero auxiliary data.

The completion has the following three-shear implementation. Let

    B=Rᵀ/4, Z=−R,
    Sx(B)=[[I_n,B],[0,I_m]],
    Sy(Z)=[[I_n,0],[Z,I_m]],
    J=diag(I_n,−I_m).

Then

    C = Sx(B) Sy(Z) Sx(B) J.

The order of execution is J, Sx(B), Sy(Z), Sx(B). The middle product has upper-right block 2B+BZB=−3Rᵀ and lower-right block I_m+ZB=−13I_m; J changes those two signs. Thus the circuit uses three scalar additions for each nonzero entry of R and m scalar negations. Each operation is a fixed dyadic linear operation. Running the same completed circuit twice restores every input exactly. The same proof holds for arbitrary payloads in any vector space W over the coefficient field: use C⊗Id_W and perform the 1344 scalar ADDs componentwise. The port coefficients remain outside tensor powers. Hence this is a universal common-chart construction at every payload width, not an inference from a finite numerical witness.

For the frozen native source, n=112 and m=8. The exact input receipt checks RRᵀ=56I_8 and A=I_112−RᵀR/4 against the public code matrix from PR #4929. R has 448 nonzero entries, all ±1, so the circuit uses 1344 scalar ADDs and 8 negations. The portable verifier checks all 120 basis inputs through the literal chronological three-shear program as well as the separate matrix-square identity.

Over characteristic zero, eight auxiliary coordinates are optimal for an involution whose upper-left block remains this A. For any completion [[A,B],[D,E]] with k auxiliary coordinates, its square identity implies BD=I−A²=−3RᵀR. The latter has rank eight because RRᵀ=56I_8. Hence k≥8, and the construction attains equality. This optimality supports the explicit sufficient construction; it is not a substitute for physical admission.

Over R or C, the completion has controlled, fixed conditioning. Decompose the first 112 coordinates into ker R and the eight orthogonal modes Rᵀe_i/√56. It is identity on ker R. Each remaining two-dimensional block is [[−13,3√56],[−√56,13]]. Its singular values are 15+4√14 and 15−4√14. Consequently ||C||_2=||C^-1||_2=15+4√14<30 and κ_2(C)=449+120√14<900. The ±1 eigenvalue multiplicities are 112 and 8. These are fixed constants, not growing precision losses or an asymptotic improvement by themselves.

A version with a common-chart monomial gauge M is immediate: replace R by RM and A by M^-1 A M when M is orthogonal and invertible. The primitive gather/scatter matrices must still be implemented in the actual physical charts; coefficient-level similarity does not make that implementation free.

Predecessor credit: the retained source word, eight center observations, and its paid profile come from Cao Yifan's PR #4610 and its upstream lineage; the center-free cache kernel was already present in PR #4694; PR #4929 supplies the autonomous coded offer A and its exact rank-eight Gram spectrum. The present delta is the explicit optimal eight-coordinate dyadic involution completion and division-free three-shear implementation. It does not claim novelty for the general block-matrix completion method or elementary shear factorization. The DAG search retrieved elementary-generation and projection entries as source-only, unelaborated precedents; none is represented as a newly checked Lean theorem here.

Closest prior overlap is explicit. [Rohan Arun's PR #1931](https://github.com/CrocSwap/integer-mult-bounds/pull/1931), head d043a01b222365a951853904c001761921bb843b, already gives an involutive eight-mode source reflection F=I−(K−12P)R and source-restored F-shears, with eight rank-one target repairs and no extra arrays on its older 712-column source. Its proof expressly leaves changing-chart native composition open. [Ali Romman's PR #1862](https://github.com/CrocSwap/integer-mult-bounds/pull/1862), head bb29ea73ad9be9a0c3d53cdcb1d22b2ee9ffe42f, supplies the broader ordered-ring source-code family, order-six specialization, and native-cut eight-row repairs. It already states the same Gram geometry K=Rᵀ/4, RRᵀ=56I. Thus neither involutive E8 source coding nor that Gram identity is new here. Our construction instead keeps A as an unchanged principal block and adds eight auxiliary coefficient coordinates; its three-shear implementation is an additional common-chart interface, not an improvement on either predecessor's native repair price.

The completion also preserves an explicit indefinite form. With W=diag(I_112,−3I_8), the matrix WC=[[A,3Rᵀ],[3R,−39I_8]] is symmetric. Hence CᵀW=WC, and CᵀWC=W because C²=I. Thus this is an exact dyadic element of the orthogonal group of a form of signature (112,8), although it is not Euclidean orthogonal. Its usual contragredient lift S=diag(C,Cᵀ) is a 240-dimensional symplectic involution: for Ω=[[0,I_120],[−I_120,0]], direct multiplication gives SᵀΩS=Ω using C²=(Cᵀ)²=I. This is the standard block symplectic lift, not a new tensor-isomorphism reduction. The transpose shear program is obtained by reversing the shear factors and transposing their coefficient matrices; two copies cost 2688 scalar ADDs and 16 negations on common-chart coordinates. Physical native admission remains separate.
