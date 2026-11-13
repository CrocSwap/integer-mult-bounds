# Independent preflight: once-rounded MOVE at W

Source reviewed: /workspace/scratch/92c9920affc2/reference/sharp-rounded-move-PROOF.md

Pinned context: PR #7211, head 2b882fd2834303655f82d084e25dc551f67e9784.

Source SHA-256: b9dcc7361a05518f117c6e653ef8e5035e4fb5a296cbf54eb43b997f2f1db081.

## Decision

**Numerical pass** for the proposed width W=w+2k+1, with k=ceil(f/2), and for the nearest-up bit algorithm over every scaled exact return z within the derived tensor-prefix bound. The only numerical rejection needed is the post-round signed-w overflow check. I found no counterexample to the plan.

This uses the Gaussian denominator and row-norm facts stated in the pinned #7211 proof as premises; it does not independently review their source lineage. It is independent preflight evidence, not a selected-provider placement, physical Count/Tape proof, or tariff result.

## Universal prefix argument

Let M=2^(w-1). A signed-w input component lies in [−M,M−1], so its absolute value is at most M, including the most-negative input. The lift multiplies by 2^k, giving component bound 2^k M and divisibility by 2^k. The entrance monomial only permutes components and multiplies by Gaussian units, so it preserves both facts.

After j Gaussian axes, the cited denominator 2^ceil(j/2) divides the common scale because j<=f and k=ceil(f/2)>=ceil(j/2). Every completed prefix is therefore a Gaussian integer. The next fused half also has an integral result; its normalized numerator is even. This relies on the cited fused implementation storing/checking the normalized component rather than placing a potentially wider four-term numerator in a W-bit cell.

The cited component row norm gives, for every prefix,

    |prefix component| <= 2^ceil(j/2) * 2^k M
                       <= 2^(2k) M
                       = 2^(w+2k-1)
                       = 2^(W-2).

The bound includes the entrance and survives the exit monomial. A signed W-bit word ranges from −2^(W-1) to 2^(W-1)−1; the prefix bound is strictly inside both ends. Thus no widened prefix overflows, even when an original component is −2^(w-1). Also 2^k U(x) is integral, while U(x) itself need not be integral; for f=1, C(1,0)=((1+i)/2,(1−i)/2) is a simple example.

## Exact nearest-up bit algorithm

Write W=w+2k+1 and n=W−k=w+k+1. For a signed W-bit integer z, copying its high n two’s-complement bits gives

    qpre = floor(z/2^k),    r = z mod 2^k,    0<=r<2^k.

The first discarded bit is one exactly when r>=2^(k−1). Hence adding one to the full n-bit prefix iff that bit is one computes floor(z/2^k+1/2), including exact ties toward positive infinity. Lower discarded bits do not affect this rule. In particular, for z=−1 the all-one prefix increments to zero, which is the correct rounded result.

The prefix has k+1 more bits than the requested signed-w result. Checking those k+1 high bits against copies of the retained sign bit accepts exactly the values in [−2^(w−1), 2^(w−1)−1]. The tensor margin bounds |z| by 2^(w+2k−1); therefore qpre and qpre+1 remain representable in n bits, so the finite prefix addition cannot wrap into a false signed-w result. Only the final redundant-sign check may reject.

An early sign-extension check on qpre is invalid, even for a reachable C output. For any w>=2, set f=1, k=1, M=2^(w−1), and use two complex input components a=−M+i and b=−M. They are in signed-w range. The first component of 2C(a,b) is

    (1+i)a + (1−i)b = −(2M+1) + i.

Its real qpre is −M−1, outside signed w, while nearest-up gives

    floor(−(2M+1)/2 + 1/2) = −M,

the representable most-negative signed-w value. The post-round check accepts; a pre-round check would reject a valid call.

## Exact bounded checks

check_preflight.py uses Fraction and integer two’s-complement arithmetic only; it imports no provider or author verifier. It refuses optimized Python. Normal replay:

    PASS_ROUNDED_MOVE_PREFLIGHT z_values=20416 accepted=1800 ties=1800 tensor_rows=510 scaled_integral_entries=87380
    positive_half_target_vs_truncation=(1, 0)
    positive_half_target_vs_ties_even=(1, 0)
    reachable_early_precheck=(-5, -4)

The bit-level oracle exhausts every z in the tensor-derived radius for w=2..5 and k=1..4, comparing with exact Fraction/floor rounding and exact signed-w acceptance. The direct rational tensor-matrix check covers j=1..8, verifies every component-row norm and the stated binary denominator, and confirms scaled-integral matrix entries at k=ceil(j/2). The radius is checked against the W-bit signed limits for w=2..5. Three controls demonstrate failures of truncation, ties-to-even, and pre-round sign checking. Optimized mode exits with the explicit refusal message.

These finite checks corroborate the all-size norm/denominator argument; they do not replace it. The bound on fused internal arithmetic is inherited from #7211.

## Remaining implementation conditions

The prefix proof assumes the exact fused C-axis routine from the cited provider is used. A routine that materializes the unnormalized four-term numerator at W needs a separate scratch-width proof. Source/provider placement, physical lift/drop Count/Tape execution, atomic final commit and a faster complete tariff remain open. No standalone novelty or selected caller admission is claimed.
