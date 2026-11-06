# Exact eight-input rank-21 four-stage root

Independent worker D construction, seed78, sealed 2026-11-06 about10:00UTC before reading worker B. Prepared with substantial OpenAI Codex assistance. Apache-2.0; human/proof-kernel review unclaimed.

## Result

There is a shortest five-query root on eight arbitrary independent inputs with rank-two square-zero queries and four pairwise commuting full-stage projectors at sites0,1,3,4, of ranks **(4,6,6,5), total21**. All stages support their query and commute with the actual chronological prefix. Over every field of characteristic different from two the full formal identity is

    H^-1 L(S,A,B,C,D) H
      = S diag(ABCD,ABCD,AB,AB,BCD,BC,CD,CD).

S is central with S²=1; stage variables commute. Together with #6773's exclusion of total20, this establishes the exact q2,n4 minimum21. A universal11q lower bound under that coefficient-space contract is false. No input is initialized, identified or discarded.

## Explicit construction

Use four two-dimensional coordinate blocks W,X,Y,Z. Put I=I₂, E=diag(1,0), F=I−E. Query factors are:

|i|U_i, vertical blocks|V_i, horizontal blocks|
|---|---|---|
|0|(I,I,0,0)^T|(-I,I,0,0)|
|1|(I+E,E,E,-E)^T|(-E,I+E,-F,-F)|
|3|(I,0,0,I)^T|(I,0,-2I,-I)|
|4|(I,0,I,0)^T|(I,0,-I,0)|

Set U₂=−U₀+U₁+U₃−U₄, V₂=−V₀+V₁+V₃−V₄, and R_i=U_iV_i. Exact integer multiplication gives V_iU_j=sign(i−j)I₂, R_i²=0, and (I−2R₄)…(I−2R₀)=−I₈.

On the last four coordinates define

    T = [[0,1,-1,1],       D0 = [[1,0,0,0],
         [0,0, 0,0],             [0,1,0,0],
         [0,0, 1,0],             [0,0,0,0],
         [0,1, 0,1]],            [0,0,-1,1]].

The stages are P_A=diag(I,I,0,0), P_B=diag(I,I,T), P_C=diag(I,0,I,I), P_D=diag(I,0,D0). T,D0 are commuting idempotents of ranks2,3. P_B supports both R₀,R₁; P_C supports both R₃,R₄. Thus the first two actual prefixes commute directly; the full endpoint gives B₃=−I−2R₄ and B₄=−I for the other two.

Take H=diag(I,I,H0), where

    H0 = [[1,0,1,-1],
          [0,0,0, 1],
          [0,1,0, 0],
          [1,1,0,-1]].

Its determinant is−1. The last four columns have masks BCD,BC,CD,CD; W has maskABCD, X has maskAB. The full inventory follows.

## Independent derivation

The #6773 endpoint-minimum branch permits ranks(A,C)=(4,6),(B,D)=(6,5). The A,C joint dimensions are AC=2,A-only=2,C-only=4. Reducing endpoints to AB,DC preserves support, so A≤B,D≤C can be imposed. On C-only normalize endpoint factors to J=(I,0)^T,K=(-I,0). The other odd site has residual U₃=(0,I)^T,V₃=(-2I,-I). The first odd residual factors can be P=(E,-E)^T,Q=(-F,-F), so QP=0.

Let F0=[[1,0],[1,0]], G0=I−F0=[[0,0],[-1,1]], D0=diag(I,G0), p=(1,0,0,1)^T,q=(0,1,-1,1). Then qp=1,D0p=p,qD0=q, and T=diag(0,F0)+pq. These are orthogonal rank-one idempotents in kerD0 and imD0. Therefore T commutes with D0, while TP=P,QT=Q. The remaining query blocks are forced by the sign Gram. This is a coupled construction, not a decomposition into scalar roots.

## Certificate

The standalone check_rank21.py uses Fraction arithmetic without importing predecessor code. It verifies all25 sign Gram blocks, all ranks, square-zero identities, projector identities, actual prefixes, complete−I endpoint, joint masks, and all16 formal monomial coefficients at S=±1. Five query-omission and four stage-omission controls detect malformed words. Character interpolation requires char≠2; integral formal verification is being added separately.

First sealed fixture SHA256: b22d9085b8b0112b94b80ab807a11564e9a515dc8559c60b1f4a5a08ff04bb43. Later verification metadata may change, not the mathematical fixture.

## Pins, scope and credit

Base:7c49fe32c55de02c2c873655c804b16e4c3fef0a. Predecessor @CubeJerry#6773, research/p104-four-stage-rigidity, head10ecaad298e6a6af7416fbd2baca15674fcadf5b. Its note/README were read; no executable/fixture was imported. Ali Romman and original query/controller authors retain normal-form/rank-method lineage credit; thu-nmrc#6717 and ToikY#6721/#6734 retain leakage/rank context. The explicit rank21 construction is new here.

No native phase, physical ports, helper ownership, complete paid invoice, precision/compiler/analytic/all-size admission, or kappa improvement is established.

## Open next questions

1. Price legal unit-pair retirement opportunities with a complete native invoice; rank alone does not prove profit.
2. Determine sharp all-q n4 bounds. Direct sums attain21q/2 for evenq; a matching lower bound is not asserted.
3. Audit physical basis maps and all native obligations while preserving arbitrary independent inputs.

## Integral formal strengthening and verifier hardening

The verifier now also multiplies the literal word directly in Z[S,A,B,C,D]/(S²−1), checking all32 reduced formal coefficient matrices. This proves the formal identity over every commutative coefficient ring after specialization, including characteristic two. The characteristic-not-two lower-bound theorem and its negative-character shortest-root contract remain separately scoped. No native bit phase or physical supplier follows merely from this integral identity.

H has determinant−1 and H inverse is integral. Maximum absolute entries are U,V:2; R:4; P,H,H inverse:1. These small coefficients may simplify ordinary basis operations; no physical instruction budget has been certified.

Default verification is read-only and compares the unchanged committed fixture bytes with independent reconstruction. Explicit `--emit PATH` is required for generation. Five fixture-corruption controls modify U,R,P,H or an output mask and are rejected. Both normal and optimized isolated Python pass. The original fixture SHA256 remains unchanged.
