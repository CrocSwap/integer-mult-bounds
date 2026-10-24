# Independent narrow review of the corrected-centre p2 budget

2026-10-23. **PASS for the conditional accounting and uniform numerical bounds. The candidate's declared product placement has FAILED.** The positive raw relaxation below is therefore not evidence that the candidate supplies an admissible κ improvement. Substantial OpenAI Codex assistance; local review only.

The reviewed report is `outputs/new-approach-ceilings-20261023/centre0-p2/REPORT.md`, SHA256 `c5cea3ffb6f8fe129bb9207d619bb8d290e430fd6403532f8f2db52c32981c70`, with source manifest SHA256 `30f720c1debd63c091280752d340ca514987f1bfa789432be177291da65592b9`. All six frozen manifest inputs, the author result and the reviewed report are authenticated before and after the independent run. The exact corrected local producer matches the source packet independently audited here at SHA256 `d40187525bd50b77f277de46575097c6d34a18af96802e7aec7b4f49213465d4`.

The paid incidence is correctly reconstructed from two complete local profiles N plus three 112-query thin banks and 224 H8 IDLE jobs:

```
N={1:2209,2:412,3:510,4:127,5:40,8:1},
P=2N+336H1+224H8
 ={1:4754,2:824,3:1020,4:254,5:80,8:226}.
```

Both restored H8 calls are included. All sixteen H1 repairs across the two local invocations remain. The source's extra finite work is also correctly stated separately: helper ADDs grow by606 and repair ADDs by108 per local invocation, total714, hence1428 for two. Those ordinary operations are not silently translated into recursive H1 units.

The target grant is

```
T=2{4:28,7:7,8:47,9:326}+224H9+224H17
 ={4:56,7:14,8:94,9:876,17:224}.
```

This credits the original816 helpers once and assumes448 completed independent main jobs. Those main jobs are unproved. The frozen predecessor's failed h endpoint and the author receipt's `AUTHOR_DESIGN_OPTIMISM_ONLY_UNREALIZED_TARGET_GRANT` status remain explicit. Independently, the present exact diagnostic placement has already failed at e1 with coefficient-zero residual42. A favorable target grant cannot repair either missing endpoint.

Let `M(C)=sum T[r] r^(1-C)−sum P[r] r^(1-C)` on the exact closed domain a=.0030217758, b=.00339999. The reviewed derivative argument has the correct sign and interval orientation:

```
M'(C)=sum P[r] H_r(C) ln r−sum T[r] H_r(C) ln r,
M'(C) <= sum P[r] upper(H_r(a)) upper(ln r)
         −sum T[r] lower(H_r(b)) lower(ln r).
```

Each H_r decreases and each logarithm is nonnegative. Thus the paid endpoint at a supplies an upper positive contribution, and targets at b supply a lower quantity to subtract. This gives a uniform derivative upper bound, rather than endpoint extrapolation.

The new independent runner imports neither the author's positive-exponential engine nor the reviewed worker's negative-exponential engine. It implements a 48-term rational atanh logarithm series and a fresh 24-term **positive** exp series with a geometric upper tail, then reciprocates to bound `H_r=r/exp(C ln r)`. Its interval domain and signs are explicit checks that survive `-O`. The independent results are

```
M(a) ∈ [20.246364736386988059630937,
        20.246364736386988059630938],
M(b) ∈ [12.804117221917453035517808,
        12.804117221917453035517809],
M'(C) < -19660.823331812427897464928484 < 0.
```

Consequently M has its minimum at the included right endpoint. The sharp maximum **integer number of additional H1 calls** fitting the whole domain is12. Thirteen fail at b. Any thirteen added positive-integer-rank calls also cost at least13 in this additive rank invoice, so they fail there. A single rank12 child fits uniformly because `upper(H12(a))<lower(M(b))`; rank13 fails at b because `lower(H13(b))>upper(M(b))`. With 1−C>0, larger integer ranks cost more. Mixed correction bills still require their own pointwise inequality; these two integer bounds do not admit all bills assembled from smaller ranks.

The residual after twelve H1 calls is at least `.804117221917453035517808`. This is a raw rank-model remainder. It funds no finite scalar work, tape movement, storage, rounded suffix error, caller chronology, compiler reserve or completion/splitting tails. The report correctly invents no reserve epsilon and asserts no actual corrected caller invoice.

Reproduce with `python3 outputs/new-approach-verification-20261023/check_economic_reviews.py --p2-only`, then with `python3 -O` and compare `ECONOMIC-REVIEWS-P2-RESULT.json` to its `-OPTIMIZED` counterpart. Both modes produce byte-identical JSON. All arithmetic is rational; no root or parameter search, native/caller run, compiler or Lean work is performed.

Credit Astra's explicit design and unrealized target receipt, the primary construction worker's actual-centre source derivation, the ceilings worker's conditional budget proof and source-reused p19 interval method, Dugongue and the native/helper/compiler contributors, and the failed predecessor's retained credit. The independent source/product decision is in PRODUCER-AND-PRODUCT-REVIEW.md. No alternate placement search or new κ claim follows.
