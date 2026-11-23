# Independent review of the production binary capacity corollary

## Decision and exact target

**ACCEPT_BINARY_PRODUCTION_CAPACITY_COROLLARY.** No change to the frozen author corollary was required. For every successful invocation of the installed binary production recipe, the source-bound census and accepted numerical enclosure imply that its fresh `OwnerBanks.capacity` is strictly less than `2B`, where `B=N^92`.

Reviewed `COROLLARY.md`: SHA-256 `0170a085fb126ae4e2ab556cd41a446241e42bf9f602aac5418ae5b6a87d16f3`.

Imported binary census `PROOF.md`: SHA-256 `672289a9a52ffdc710b4ff037c03c7149097fb99a9083ba9da62021edc77c97f`.

Its separate independent census acceptance is `work-binary-owner-review/CROSS-REVIEW.md`, SHA-256 `a9c1a7116946e388e6cf43afe1c6ea20cc25f9f9dc2cd666fa65f736aceea47a`; its receipt is SHA-256 `0490b61c59dfa07353e4865389266ee5910018ae7502d7f1a120cf60ded1298d`. I read that completed acceptance, including its distinction between completed allocator calls and intermediate allocation/retirement statements.

The numerical dependencies were published in #8091 at `de02b59fa9a74d4958d0d114d25e9083ab91b022`:

| Imported result | SHA-256 |
| --- | --- |
| Uniform numerical mass proof | `b92516aaa39192c6713654fa6f41b4c4f8367b1f71c7e374b95fd31687464c1b` |
| Its independent acceptance | `281ad36f151c2e63620a2a08a9eaf099615de47e71e180fd24de32a4f9e236ad` |
| Its actual production binding | `43cb6abd4b90e11d28129fbcd449affccccf7c95a2b62d75d8b0444bcb94e683` |

Both census and numerical theorem use exactly the #8042 `transport.py`, SHA-256 `98bdb540233794338b426d1b0d0e72cff7fcbbd08be702af0d81e237dbecaae9`, at scientific source head `dfd25d553a843a946ca0b94130a5ff8943e98fdd`. No similar implementation or different exponent is substituted.

This is a separate model-assisted review with independent exact checks, not human or proof-assistant certification. The imported numerical proof, its review, the census, and Ali Romman's implementation retain their attribution.

## Independent source correspondence

I read the literal transport, binary receiver, raw binary stage, labelled-source construction, relevant raw source, installed constants and complete census proof. The production chain has no extra count or delay parameter between these files:

1. `binary_receiver.Receiver` dispatches at height at least 3000 and requires the selected dimension to be exactly the corresponding power of two.
2. `binary_recipe(height)` passes the raw `BinaryWord` tuples and installed `BINARY_C` to `Recipe`.
3. `Recipe.open` supplies `N=2^h`, `L=32768`, `U=2*floor(N/(2048*134))`, volume `N^6`, width `N^92`, and the specified delay base.
4. `Plan` counts unpowered paid labels, constructs the exact dyadic grid, and uses the increasing band loop with scale step `6/5`.

The actual exponent is `t=1148436507037532395/1152921504606846976`, with reduced denominator `2^60` and `3/4<t<1`. Independent reconstruction from the authenticated graph and caller gives 18,906 targets and 104,904 paid labels, largest target 127 and smallest paid grade 1. I also applied the unmodified `binary_ports` declaration and compared its entire ordered labelled lists with that reconstruction.

Ambient 134 is independently bound to the actual inherited `bit_word` declaration. I extracted `powered.py` by authenticating both nested immutable source archives and the requested member, without installing the predecessor runtime. Its SHA-256 is `2cd55d3cd17e5f4ad10fcc1d534393d0ca9c709dd1b08f9e43d223ea15ba19f7`, at retained predecessor commit `3f7c3c1f2a9a0963736562037e01fe41aec46b8c`. The declaration stores ambient 134 and unchanged input tuples. Reading those fields does not execute its powered methods. The reviewer export retains these bytes and their archive provenance; the author retained identical dependency copies.

For `q=104904`, `(q-1).bit_length()=17`, so the actual expression chooses `D0=2^19=524288`. The larger Gaussian delay base is not silently substituted into this binary construction.

## Numerical premise and replica sum

The accepted mass theorem applies directly. Its exponent, positive-volume and nonnegative-precision conditions are met. Every bin lies in `[L,U]` with `L>1`. The actual maximum grade ratio is 127, within the imported conservative `2064N` endpoint envelope. The literal precision is `max(256,64*N.bit_length())`, making its grid strictly larger than `N^64`.

The imported proof establishes one-sided endpoint error `Delta<1/4`. The actual ceiling of a bin's upper enclosure is therefore less than its ideal integral plus 2. The direction matters; an arbitrary approximation would not provide this count premise. The ideal bin integrals telescope over the even partition of `[L,U]`, and there are fewer than U bins. Hence

`sum_e count[e] < N^6/(t*L^t) + 2U`.

Because `t>1/2` and `L>=16`, `t*L^t>(1/2)*sqrt(L)>=2`. Also `U<N` and `2N<=N^6` for `N>=2`. These loose estimates suffice for the strict universal bound

`sum_e count[e] < 2N^6`.

This review imports the accepted numerical theorem; it does not claim a new numerical oracle or use finite fixtures to establish that enclosure. Successful Plan construction and funding remain distinct from this upper bound.

## Delay envelope and inclusive lifetime

The source starts at `level=0, limit=L` and retains those variables across increasing bands. It multiplies the limit by `6/5` while the next limit is at most the current band. After each band,

`L*(6/5)^level <= e < L*(6/5)^(level+1)`.

The exact integer comparison `6^76 > 2^19*5^76` implies

`D0^level <= (6/5)^(76*level) <= (e/L)^76`.

The level-zero equality case is included. Since `e<U<N`, the source delay is strictly less than `(N/L)^76<=N^76`. At the least permitted Recipe height, `h=1024`, already `q+1<N`. Consequently

`q*delay[e]+1 < q*N^76+1 <= (q+1)*N^76 < N^77`.

The added 1 has not been dropped: the origin interval includes both opening and final close ticks. These inequalities persist for larger heights by monotonicity. No floating-point logarithm or estimated level is used.

Combining with the nonnegative count table gives

`C_* = sum_e count[e]*(q*delay[e]+1) < 2N^83`.

If all counts were zero, this conclusion would hold directly; successful productive Plan construction excludes that degeneracy. No extra positive-sum hypothesis is needed.

## Joining the census and retaining custody scope

The census supplies `capacity<=B+22339*C_*` for the fresh bank. Its coefficient includes input zero owners and the maximum simultaneous private raw owners, with opening/closing microsteps included. An independent register scan corroborates private peak 3,433 and `18906+3433=22339`; the census and its separate review supply the fuller alias, suspension, clone and custody proof.

The arithmetic here does not weaken that lifetime argument. The constructor rejects a link whose child delay is not strictly smaller. Both delays are powers of common `D0`, and `q<D0`, so `q*D_child<D_parent`. Descendants finish before their parent resumes, including a loan issued at the parent's final paid cut. Source close-before-open order and pending-loan checks retain their roles. Selecting an existing owner is an alias, not a fresh allocation. Physical leaf work may enter other bank instances; the separate ancestor composition accounts for those instances.

The upper bounds alone do not establish funding, numerical field correctness, valid source return or cleanup. They apply under exactly the successful-call and custody contracts of the retained census, as the corollary states.

Finally, `22339<2^15` and `N^9=2^(9h)>2^16` give

`22339*C_* < 2^16*N^83 < N^92=B`.

Thus `capacity<2B`. At completed allocator calls, free-first allocation makes capacity equal to the maximum completed live count. At intermediate statements, the census separately charges the in-flight allocation or retirement to its origin context; it does not assert a live/vacant partition at every statement. No logical reset discards physical reservation history. The arithmetic covers Recipe's entire range `h>=1024`; actual binary dispatch begins at `h>=3000`. A reused head still requires `max(K0,V_field*capacity)` bytes.

This local beta=2 result does not bound all heads, header storage, recursive banking, compilation cost or the complete multiplier.

## Independent executable evidence and replay

`check.py` imports neither author checker nor the numerical proof's checker. It authenticates both source/dependency manifests, the frozen corollary and imported mathematical files. Its independent labelled-grade construction is compared with literal source declarations. It captures actual `binary_recipe` and `Recipe.open` arguments at heights 1024, 3000, 5610 and 9100. A replacement Plan function records arguments and never constructs a production calendar. The exact original Measure expression is evaluated on those bindings.

For the level loop, it executes the original two source statements with a controlled mass fixture. Even integer bands are chosen around 241 rational scale thresholds for each of two lower endpoints, including six exact threshold cases. Independent interval-membership tests establish the levels. This passes **1,926 critical even bins** and **1,926 literal upper-ceiling count expressions**. The fixture tests source binding; it does not replace the accepted mass theorem.

Exact integer/rational certificates cover the universal inequalities at the least height. Controls reject an insufficient delay exponent, a reversed delay comparison, inclusive-endpoint slack at a small rank, the owner margin at a tiny rank, and the production exponent estimate outside its domain. Explicit exceptions keep every check active under optimized Python.

Normal and optimized runs both passed with byte-identical evidence. `RECEIPT.json` records exact hashes and `REPLAY.json` records the commands. Portable replay is:

```sh
python3 -I -B check.py --author /path/to/binary-owner-census --output /tmp/binary-capacity-review.json
python3 -I -O -B check.py --author /path/to/binary-owner-census --output /tmp/binary-capacity-review-optimized.json
```

Integration must retain the source census, imported numerical proof and review, original attribution, scientific pin and successful-call scope. This derives the local binary capacity premise. It leaves the complete `owned_erasure`, `precision_tape`, `analytic_recovery`, supplier-admission and selected exponent obligations unchanged.
