# Independent proof and overlap review: coupled five-query rank budget

Scope: read-only author-side review, 2026-11-05. No modular grid, coefficient search, native/pricing suite or external post was run.

## Mathematical assessment

The proposed rank budget is valid under the explicit hypotheses below.

For a shortest five-query tuple on4q fields, let the rank-q square-zero queries have product of I-2R_i equal to-I. Suppose exactly three selected sites carry pairwise commuting compatible idempotents P_i, each also commuting with its actual complete chronological query prefix B_i. Over any commutative field of characteristic different from two,

    sum of the three projector ranks >= 7q.

No minimum-rank assumption on individual full projectors is needed. This is a stage-dimension/rank-inventory lower bound, not a paid-call or kappa theorem.

More generally, for any even n>=4 the same7q bound holds for a commuting compatible triple containing endpoint-adjacent sites(0,1) or(n-1,n). It is NOT proved for an arbitrary triple of sites at general n.

## Independent derivation

1. By the credited complete block shortest-query normal form, factor R_i=U_i V_i with V_i U_j=sign(i-j)I_q. Any three selected U blocks and V blocks have ranks3q, while their3-by-3 block Gram has rank2q.

2. If P_1 commutes with its prefix B_1=T_1 T_0 and is compatible with R_1, then it commutes with T_1 and hence T_0. Thus it commutes with R_0. Applying this identity to U_1 and V_1, and using invertible cross-Gram blocks, gives P_1 U_0=U_0 and V_0 P_1=V_0. Hence P_1 is also compatible with R_0.

3. Since P_0 and P_1 commute, their product is an idempotent compatible with R_0. Any idempotent compatible with a rank-q square-zero operator has rank>=2q: it must contain q independent columns and q independent rows whose mutual product is zero. Consequently rank(P_0 P_1)>=2q. Endpoint minimality is unnecessary.

4. Let A=im(P_0)+im(P_1). Then dim A<=r_0+r_1-2q. For the third full projector P_j, the invertible cross-Gram block V_1 U_j factors through P_1 P_j, so rank(P_1 P_j)>=q. The commuting product has image inside A intersect im(P_j). Therefore

    dim W, W=A+im(P_j), <= r_0+r_1+r_j-3q.

5. All three U images lie in W. The three V blocks vanish on its joint complement, so their restriction to W retains rank3q. Sylvester's inequality, together with the rank2q Gram, gives dim W>=4q. Combining the bounds proves total rank>=7q. Reversal gives the endpoint pair(n-1,n).

6. For n=4, a full site2 alone needs rank4q. In the scalar canonical basis,

    B2 = [[1,2,2,2],[-2,-3,-2,-2],[2,2,1,2],[0,0,0,1]],
    A  = [u2,B2u2] = [[0,2],[0,-2],[1,1],[0,0]],
    C  spans [[1,1,0,-1],[0,0,0,-2]].

The two column and two row spaces have ranks2,2 and pairing rank zero. Tensoring these fixed matrices with I_q gives2q,2q,0, so the elementary image/row bound forces rank(P_2)>=4q. Adding two other compatible projectors gives total>=8q. If no selected full site is2, three sites from{0,1,3,4} necessarily contain(0,1) or(3,4), already handled.

## q=2 rank13 consequence

The controller's only surviving layouts(0,1,4)/(0,3,4), ranks(4,5,4), fail before any H-completion search: total13<7q=14. The current local atom pattern[7,3,5,6,1,2,4,4] has an additional quick failure: the rank4 endpoint image is not contained in the rank5 middle image. No modular or rational grid is needed.

The rank13 local Gram example remains valid WITHOUT actual prefix compatibility. It is therefore a useful scope control rather than a counterexample to this theorem.

## Targeted predecessor audit

- PR6398, Ali Romman, dee2663ba0918be86993fd9d63c8d64b020f4c83, mixed-projector-root-headroom/PROOF.md section2: already proves at most two scalar rank-two commuting full projectors for every even n>=4. Thus the q=1 total-rank>=7 consequence is old, even without the prefix hypothesis. Do not claim its scalar priority.
- Its section3 supplies the image/row-space lower bound r>=a+c-rank(CA), used in the site2 argument. The present proof uses elementary Sylvester rank inequalities, not a new rank theorem.
- Canonical five-call-projector-rigidity/PROOF.md and COUPLED.md provide the complete scalar/block query normal forms, endpoint normalization and block-width semantics. Their finite thin-call exclusions require rank2q full stages and n=4,6,8; the located text does not state this arbitrary-rank7q budget.
- PR6168, current exact head2defc4f2f74acae1d6b49dfbcf2140570a09b381, includes those earlier packages and later cyclic tariffs/alternating closure. Its located claims concern rank2q/full-only or fixed-interior/cyclic contracts, not this commuting mixed-rank three-FULL budget.
- PR5617/5631/5649 are characteristic-two rank/intersection, paired-stage or fixed-star chronology results, with different query/field hypotheses. No matching7q coupled prefix-compatible theorem was located.
- Current targeted public PR searches for7q+prefix/projector and coupled stage rank-sum/budget did not locate an exact statement. This is bounded repository coverage, not proof of world mathematical priority or absence of unpublished work.

## Defensible new contribution

A coupled-width extension for the ACTUAL chronological stage contract: the adjacent-prefix condition upgrades one pairwise overlap from q to2q, restoring the7q stage budget at every q despite the genuine rank13 local q=2 Gram example.

A focused no-kappa package may claim this block-width/prefix application, its n=4 all-position consequence and carefully attributed sharpness if a literal attaining word is separately checked. No general n arbitrary-site theorem, physical supplier gain, rank13 profitable operator or q=1 discovery is established by this review.
