# Whole ordered Schur normal form for the H=1 primary component

This result determines the whole ordered Schur residual pair when the compressed matrix H has only eigenvalue one. It answers the H=1 primary part of the released [Discussion #5337](https://github.com/CrocSwap/integer-mult-bounds/discussions/5337). No additional sector00 factor invariant survives in this residual. Some original splits are inequivalent, but their ordered residuals are conjugate. The complete kappa calculation is unchanged.

**Contract.** Work over any field F. Let P0,Q0 be commuting idempotents, with ordered joint sectors V00,V10,V01,V11 of dimensions r00,r10,r01,r11. A split i:U->V, pi:V->U has pi i=I_d, pi P0 i=pi Q0 i=I_d, and H=pi P0Q0 i. Let S,T be the two identity-pivot Schur complements on ker pi. Require rank(ST-TS)=2d. Put W=I-H and suppose W is nilpotent; this is the H=1 primary hypothesis. Set a=nullity W. This domain differs from the nilpotent-H theorem in the cited source. General primary gluing is not asserted.

Write Y_j=E_j i and X_j=pi|V_j. The source's all-field sharp-sector criterion is retained as a cited premise: sharpness is equivalent to injectivity of Y10,Y01,Y11 and surjectivity of X10,X01,X11. Their products are W,W,H, while X00Y00=-W. The full-rank factor extension lemma is also a credited premise, with its application made explicit below.

**Profile and representative.** Sharp splits exist exactly when

    r00 >= rank W = d-a,
    r10 = d+a+s10,  r01 = d+a+s01,  r11=d+s11,   s10,s01,s11>=0. (1)

Choose N:F^a->U with image a complement of im W. Set E=U direct-sum F^a and

    A = [ W N ] : E -> E.
        [ 0 0 ]

On E direct-sum E define

    S_core = [ I A ],       T_core = [ 0 0 ].              (2)
             [ 0 0 ]                [ A I ]

Every admitted residual is simultaneously similar to (2), plus scalar pairs

    (0,0)^r00, (1,0)^s10, (0,1)^s01, (1,1)^s11.          (3)

In particular fixed H and the original ordered sector dimensions determine one ordered-pair orbit. The result does not claim that different H/profile data give different residual orbits. All choices of N give conjugate ordered pairs.

**Why (1) is exact.** A full-rank factorization XY=B with X onto and Y injective needs ambient dimension at least d+nullity B. Conversely [B,N] and [I;0], with N a complement to im B, attain that dimension. Apply this to W in sectors10,01 and to invertible H in sector11. In sector00 there are no full-rank requirements: an arbitrary factorization of -W exists in dimension r00 exactly when r00>=rank W. Adding zero directions gives all larger profiles. The four products sum to -W+W+W+H=I and supply both common identity pivots. The cited criterion then gives sharpness. Thus no full-rank constraint has been inserted into sector00.

**An explicit coordinate removal.** The credited factor extension lemma puts sectors10 and01 into X=[W,N], Y=[I;0], and sector11 into X=H,Y=I. Unused directions give the last three scalar summands in (3). Leave X00=X and Y00 arbitrary with XY00=-W. On the remaining space write coordinates (t,x,b,y,c,z) in V00, U, F^a, U, F^a, U. The equation for ker pi is

    z = -H^-1 (Xt+Wx+Nb+Wy+Nc).                          (4)

This is valid because H=I-W is invertible. The residual operator on ker pi is P0-P0 i pi P0, and likewise for Q0. Direct substitution in (4) gives

    S(t,x,b,y,c) = (0, x+Xt+Wy+Nc, b, 0, 0),
    T(t,x,b,y,c) = (0, 0, 0, y+Xt+Wx+Nb, c).            (5)

Y00 has disappeared already. Put C=(I+W)^-1, which exists over every field since W is nilpotent. Use the invertible change

    x_bar=x+CXt,        y_bar=y+CXt.                     (6)

Since (I+W)C=I, the coefficient of Xt in both transformed formulas is zero. The t directions become exactly (0,0)^r00. The remaining formulas are (2). Equations (4)--(6), composed with the sector factor intertwiners, give a concrete residual intertwiner for every admissible split. This proves ordered-pair equality, not only equality of central spectra.

For completeness, the used factor intertwiner is obtained as follows. For X,Y and X',Y' with equal product, X,X' onto and Y,Y' injective, send Yu to Y'u. Extend this map from im Y intersect ker X to an isomorphism ker X->ker X', and then extend by corresponding lifts of a complement to im(XY). The resulting g satisfies gY=Y' and X'g=X. This is the predecessor extension argument, not a new generic factor theorem.

**A check on the central operator.** Direct multiplication of (2) gives

    (S_core-T_core)^2 = diag(I-A^2,I-A^2).

If the Jordan block lengths of W are k_1,...,k_a, the block lengths of A are k_i+1. Indeed A^j has image im W^(j-1) for j>=1, because [W,N] is onto U. Thus at eigenvalue one the core has two blocks of length ceil((k_i+1)/2) and two of length floor((k_i+1)/2) for each i; omit length zero. Add eigenvalue-zero scalars r00+s11 and eigenvalue-one scalars s10+s01. This agrees with the prior whole-central classification. The new claim is the explicit whole ordered pair and the removal of sector00 data, not a second central-spectrum claim.

For d=1,H=1,r=(1,2,2,1), sector00 pairs (X,Y)=(0,0), (1,0), and (0,1) are inequivalent as factor systems, because their ranks differ. All three give the same residual (2)+(0,0). For H=J2(1), W has one block of length two; the core has dimension six and central blocks (2,2,1,1) at one over every field. The zero-sector parameter still disappears by (6).

**Evidence and limits.** The standalone checker constructs the original commuting projectors, complete headers and literal Schur complements. It compares both operators through the explicit invertible residual coordinate map, tests sharpness, and checks central power-rank sequences independently. It includes complete bounded sector00 factor domains, nontrivial sector basis changes and padded profiles. The complete bounded domains contain 2,577 candidate sector00 factor pairs and 360 admitted residual intertwiners. Eleven padded basis changes, 16 higher-block fixtures, three inequivalent-split controls and two rejected boundaries also pass. All counts are printed by the registered commands. The proof is dimension-uniform over every field under the cited sharp criterion. No general-H gluing, transition weights, physical header law, later-guard survival or complete consumer bill is supplied.

Credit ssafwann's [PR #5267](https://github.com/CrocSwap/integer-mult-bounds/pull/5267) supplies the nilpotent-H comparison, exact sector equations and explicit full-rank extension specialization in its [proof](https://github.com/CrocSwap/integer-mult-bounds/blob/8ab280c8a3ef0544f13ff23a1c69df4757cd4900/research/schur-nilpotent-extension/README.md). MatShep's [PR #4762](https://github.com/CrocSwap/integer-mult-bounds/pull/4762) supplies the arbitrary factor-system extension and realizability theorem in its [proof](https://github.com/CrocSwap/integer-mult-bounds/blob/3b4e0449262b0b1e07b80e009ef71cc0ca5bf816/research/idempotent-factor-invariant/README.md), extending codyw912's argument. Nick Petalas's [PR #4746](https://github.com/CrocSwap/integer-mult-bounds/pull/4746) sharp-sector criterion is used in exactly the form stated and credited in the pinned nilpotent proof. Ali Romman's [PR #5287](https://github.com/CrocSwap/integer-mult-bounds/pull/5287) already determines the whole central class in its [proof](https://github.com/aliromman/integer-mult-bounds/blob/d17a8b3d237a8cb8685cc108bf2bb17dfea0ca78/research/schur-whole-central-class/PROOF.md); it leaves the ordered pair open. The broader Schur and normalizer lineage retains its source credit. Basis extension and nilpotent Jordan methods are classical.

Prepared by Ali Romman with substantial OpenAI Codex assistance; Apache-2.0.

## Reproduce

```sh
python3 -B scripts/research_package.py --package research/unipotent-ordered-schur
```

Use Python 3.12 with the standard library. The normal and optimized commands must print `PASS_UNIPOTENT_ORDERED_SCHUR`. The launcher must print `PASS_REGISTERED_RESEARCH_PACKAGE`. The checker has no external runtime inputs.

## Open next questions

Prove a source-bound general-H gluing statement before using primary-component normal forms to identify arbitrary ordered residual states. The source binding and physical cost model are not supplied by this package. See `TASK.json` for the structured scope.
