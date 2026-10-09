# Dirty readouts permit physical slot reuse

Base: rohanarun/integer-mult-bounds at6ec868e8568ca9a74b7245494de1b187c7be78fe (corrected PR118). The operand/root DAG and virtual role/frame profile are unchanged fromec862a5af51537495c745d9f2323e8a5736ee265. Under its retained analytic, exact-recovery, prime, whole-residual, complete-row and fixed-tape hypotheses, this construction gives

    T(n)=O(n(log n)^(1−kappa)),
    kappa=5519166047173/50000000000000000=0.00011038332094346.

This is an author-checked conditional draft; independent review remains pending. No upstream program is executed by the supplied checks.

## The new operation

In a linear virtual program, regard the initial value of each newly born register as an independent symbol g_a. Let D_a be its exact future contribution to output accumulators, cutting propagation at each subsequent birth on that storage. Then the output is Fx+sum(D_a g_a). A physical birth may leave any old value in its slot: read that value and add −D_a g_a to the output. The corrections cancel identically even if birth values contain source signals or are correlated with earlier dirt. Reverse every actual workspace/source gate chronologically to restore all original workspace.

Sources, workspace and output banks must be disjoint. Outputs are never later controls, sources, guards or addresses. Every correction is paid and must occur at a legal common frame. There is no physical dirty reset and no assumption that a fresh-signal relation is equality of dirty contents.

PR118 already reads each untouched deferred register B negatively at sigma_B after center phase one. Choose an old role A whose last forward gate and every terminal read are already finished, with final frame E contained in sigma_B. Raise A to sigma_B; use its actual value in B's existing negative readout; route B's future virtual life through A. The virtual program and D_B are unchanged. The new offset is canceled by the same readout. Selected pairs are disjoint, and all selected recipients have no source injection. The implementation nevertheless uses true reverse chronology for every inverse source gate.

Per matched local role, put e=dim E and s=dim sigma_B. Remove children24−e and552+s; add child s−e (record zero rank explicitly); remove one original physical role. Weighted rank drops by576. All target read frames, copied centers and response coefficients remain unchanged. Added positive residuals are checked nonalternating. For0<p<1,

    576^p+(s−e)^p < (24−e)^p+(552+s)^p,

by strict concavity and majorization, so each legal reuse improves the paid moment.

## Actual witness and costs

The original reconstruction checks every source support in the91,770-addition DAG, its ascending pair-star root order,71,185 legal carrier links,28,705 virtual roles and3,020 deferred frames, reproducing every base histogram bin. A deterministic containment matching finds2,106 legal reuses. The literal forward word and reversed/sign-negated/bank-exchanged/complemented word each check235,337 frame transitions and24 copied centers, across277,775 word blocks. Their complete paid histograms agree exactly:

    m=576, R=26599, W=115865904,
    weighted rank=66736898624, deficit=1862080, largest child=574.

Both rank529 connectors, source/target fronts, translated auxiliary endpoints, copied-center transforms and the inverse rank-one endpoint correction remain charged as in the base. The source and target terminal banks are unchanged, so the same inherited complete C/inverse and spectator interface applies. Arbitrary dirty cancellation follows from the birth-cut identity; no sampled modular identity replaces it.

Exact backward integer propagation gives11,862,912 nonzero old-readout terms with numerator L1 norm46,704,391 over42. The maximum is55/42 at virtual role22053. We do not assume coefficients have magnitude at most one. For each read, form one complete computed copy divided by42, perform the required signed unit additions, then discard that computed copy. Terminal numerator L1 is370,392. Copies/scans,120,475 forward source/workspace gates, their inverse, role bookkeeping, phase/sign wrappers and endpoint groups are covered by the explicit conservative

    G=3113921927424.

Set E=64(W+576+G+1)^3, B=rank+E, C0=32*576*B^2. Exact checks verify the literal-work and semantic induction inequalities with C1=1. Retain the common grid2^-P21^-K with K=G(D_complex+1); completed exact children preserve incoming odd-denominator exponent. No child rounding or free final conversion is added. All these are fixed constants; practical thresholds are not claimed.

## Assembly and scope

Use complex saving b=11040781/10^11, unchanged ordinary stopped-bit saving A=1240189553/10^13, beta=10^-6, eta=10^-8, and a=min(A,(1−beta)b−10^-12). The original exact checker verifies all three strict moments,47 inequalities and seven final margins above kappa. The simultaneous row-stock coefficient is15561; degree32000 has positive gap6389/25, and suffix slope128000 is retained. The next10^-17 grid point fails for these fixed parameters only.

Author checks include the complete graph/role/frame/profile reconstruction, exact integer old-readout responses, both literal frame directions, the arbitrary-dirty birth lemma, and exact assembly. The retained copied-stream, residual-to-child, translated-gauge, routing, all-size transfer and analytic hypotheses remain explicit. This is neither an unconditional theorem nor a practical-time or global-optimality claim.

Credit: Rohan Arun's PR118 integration and corrected unit readouts; eumemic's PR117 DAG; Swapnil Jain's deferred-readout/round-seven bit word; icekylinx's stopped-product/rational-center interfaces; Avi Eisenberg, Zhihao Chen and all preceding contributors named by the base NOTICE/SOURCES. This contribution is the compensated physical slot reuse and its original checks, developed with OpenAI assistance. No exclusive priority or official OpenAI endorsement is claimed.
