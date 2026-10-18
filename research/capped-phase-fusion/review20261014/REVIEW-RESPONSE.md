# PR1673: supplier admission and original outer proof

This responds to [the review of head 2569871](https://github.com/CrocSwap/integer-mult-bounds/pull/1673#issuecomment-6172528048). The conditional headline remains **κ = 0.001677160151714381**. This update adds the missing evidence and makes the recurrence, row stock and normalization arguments explicit; it does not substitute a new supplier or claim an unconditional theorem.

The reviewer identified two separate obligations: the inherited T74/#1319 supplier admission, and a written audit of the new outer schedule, including precision, movement and the recursive interfaces. Positive arithmetic margins alone settle neither obligation.

## Existing review reused, with an exact source boundary

Relevant independent work already appears in PR2044. We reuse philippeVV's checks from `philippeVV/integer-mult-bounds@d1e01310b92e9a9af90b89efe4f3f9aad466b8b1`, rather than presenting those implementations as new. The six unmodified files and their Git blob SHA1 and SHA256 are recorded in [external/SOURCE-PINS.json](external/SOURCE-PINS.json).

The applicable external records are:

- [Supplier admission and semantic regeneration](https://github.com/CrocSwap/integer-mult-bounds/pull/2044#issuecomment-6181046525).
- [The original PR1673 fused-group, diagonal-tape and embedding audit](https://github.com/CrocSwap/integer-mult-bounds/pull/2044#issuecomment-6181466068).
- [Support-local complete H calls](https://github.com/CrocSwap/integer-mult-bounds/pull/2044#issuecomment-6181619058).
- [The mixed-width recurrence and corrected product-stock invoice](https://github.com/CrocSwap/integer-mult-bounds/pull/2044#issuecomment-6181752567).

Those comments concern several packages and later outer regimes. We import only the stated supplier/schedule checks and the applicable interface arguments. No later fine-prime exponent, precision choice, hybrid bound or claimed priority is imported. The optional NumPy deferred-call example is retained as a source, but the registered replay does not execute it or rely on it as a proof. The new written review and exact checker below concern PR1673's original capped/Strassen regime only.

## 1. Admission of the actual pinned supplier

The supplier is still PR1661 at `f852af5e178ce035cd46181a29d9330bcbcaa206`, with source-manifest SHA256 `d90d49eaa68e48c6992a07972e736ef4b9cd80274361cbbc1ec980d43f29ad7f`. Its 169 source files, retained parent and new provider words are unchanged. The publication already contains a binding to a complete cold native run: all 12 top-level stages and both five-stage native provider replays passed, without native-reuse flags. That run is reused here after checking its source manifest, stage logs, complete native word payloads and the capsule's 46 canonical JSON receipts. We do **not** describe this reuse as a newly repeated cold native computation.

The [new admission supplement](NATIVE-SUPPLEMENT.json) comes from [native_validation.py](native_validation.py). It then performs fresh work against that exact completed run:

| Obligation | New binding or replay |
| --- | --- |
| Controller | Checks actual audit status, provider counts and 23 distinct rejected mutations: `7 + 8*2`. One owner is bound to each complete invocation; all charts and provider bindings agree. |
| Owners, calls and charts | Independent counts agree with owner audit, controller, invoice and dispatch: 319680 roles, 666 calls, 11142 charts. Rank mass, deficit, live/physical widths, idle children, provider counts and global profile agree. |
| Invoice and assembly | Every invoice strict condition holds; owner/controller hashes bind the invoice, the assembly binds that invoice, and all 47 assembly inequalities are positive. Prefix 1441 is below charged 2048; physical row coefficient 19545 is below 20161. |
| Native provider contents | Seven canonical word/program/adapter/review families for each of the two provider directories bind semantically to the PLAN. Swapping the base and extra directories rejects. |
| Regenerated geometry | Reruns the actual owner and parent generators, then compares seven artifact families by canonical decompressed mathematical content. Every owner role, time and chart is included. |
| Gzip/container distinction | Recompresses the complete owner payload at a different compression level and timestamp, reruns the actual parent generator, and accepts the unchanged semantics. Only the two PLAN container references may differ, and each must match its actual file. A changed owner time rejects. Frozen source pins are never rewritten. |
| Geometry controls | Reruns all six original mutations: understated prefix, old call count, old idle charge, old stock, missing call and understated physical row. Records the actual owner, invoice, assembly and generator hashes consumed. |
| Geometry runtime | The consumed runtime SPEC must equal the pinned new SPEC byte for byte. The three consumed engine files must match the assembly's recorded hashes. Changed-SPEC and changed-engine fixtures reject. Discovery/record environment variables are cleared. |
| Ancestry and improvement | Retains 114 admission, 12 bit and 8 independent-owner rejecting controls from the source-bound cold run. A deliberately nonimproving parent comparison rejects. |

The historical top-level RESULT and binding label the controller controls as 15. That label was incorrect for two providers; 15 is the one-provider count. The actual controller list already contains 23 distinct rejected controls. Historical receipt bytes remain untouched; this supplement and the README correct the description. An external T37 regression is cited in the external review above; it was not newly run locally or counted as our native replay.

The independent final binding has **44** conjunctive checks. Its success and the new negative fixtures strengthen finite admission evidence; they do not discharge the inherited all-size arithmetic, common-frame, mutable-source or hosting assumptions.

## 2. Written proof of the original outer

The [complete independent written review](independent/ORIGINAL-OUTER-PROOF-REVIEW.md) gives the argument in eight parts: scales and address model; complete global H calls; local linear circuits and tensorization; both rounded Gaussian maps; capped five-factor elimination and two sparse windows; embeddings, halos and precision; the complete cost ledger; and the finite/all-size boundary. Its [independent exact checker](independent/check_original_outer.py) imports no published parameter checker. The [receipt](independent/ORIGINAL-OUTER-CONTROLS.json) binds the actual main note and 22 supporting sources. Six unmodified inherited notes/reports are bundled with a separate commit/hash pin for package-only replay.

The main note and supplier audit now make these previously implicit points explicit:

1. **Mixed widths require a weighted tree.** The uniform tree in `notes/compact-control-layout.tex` does not cover children of rank 48. Use `notes/endpoint-gauge-complex.tex` and `notes/batched-complex-rows.tex`. At width e, a rank-r child has width `r floor(e/73)` and relative volume `1/66304`; fewer than 73 remainder axes contribute fixed per-node overhead. Write

   `Ψ(t) = sum_r (H_r/66304) (r/73)^t`, `σ=1-b`, `τ=1-a`, `δ=10^-9`.

   The strict moment `Ψ(σ)<1` sums weighted σ-mass geometrically over all depths. Since `σ<τ<1-q`, internal work sums as `O(V h^τ polylog p)`. Stopped leaves have exponent `σ+δ(1-σ)<τ`. Unequal stopping depths are therefore covered. The checker independently encloses the T74 moment using rational Taylor bounds and rejects a rate above the endpoint.

2. **Reserve the full product row stock.** The longest child is `48 floor(e/73)` and `2*48^2<73^2`, so depth is `O(log e)`. The row divisor includes complex stock and nested bit stock at their actual depths. Even a conservative product over all nested depths has `log2 Q_rows=O(log^2(hG))`. With `G=Θ(log p)`, `K=128G` and `h<=p`, its complete-chunk cost is `O(log(h+1)+loglog(p+2))`. Thus the two front fields, back field and full row stock reserve

   `R(h)<=3h/128+O(log(h+1)+loglog(p+2))<=h/16`

   above a fixed polynomial in log p. Handle the tail elementarily; deferred widths then sum geometrically. The finite invoice's 2644 stock bits and coefficient 19545 are checked separately. Neither a one-chunk row prefix nor a particular constant chunk threshold is assumed.

3. **Scans and setup must be paid at their actual multiplicity.** A group has a polylogarithmic number of diagonal/full scans. Their normalized power remains `epsilon-beta`, with that polylogarithm included. Balanced groups have between g/2 and g axes, so there is no singleton final group whose setup amortization fails. Coefficient pages are regenerated sequentially from actual origins and amortized over their complete payload.

4. **Normalization uses the new inverse bound.** The narrow rounded inverse bound is 16p. Choosing `j_scale=ceil(log2(128p))` keeps the literal stronger contraction bound. Its extra two bits per axis are compensated by one `2^(2D)` shift and O(D) extra precision, already within the paid scalar scan and `o(p)` guard.

The supporting exact tests include 34 positive inequalities and six rejecting variants in each of the two published Strassen specializations, both five-factor orientations on 24 varied rational systems, exact q-image/order cases, sparse-union closure and dense leakage, halo volume identities, and mixed-depth/product-stock examples. [CONTROL-REPLAY.json](CONTROL-REPLAY.json) additionally reruns the pinned external product-diagonal tape, group embedding and five-factor models, together with [our recurrence/cost controls](check_recurrence.py). The latter include the conservative metadata fallback and all 12 cost rows. These are finite corroborations of the written argument.

## Reproduction and limits

The top-level `verify.py` now registers **23** bounded exact replays and runs them in a temporary copy. Python 3.12 with SymPy 1.14.0 is the registered environment. The native supplement additionally needs the exact external native source and a completed full run; commands are in the package README. It reruns owner/parent generation and geometry, and binds rather than repeats the expensive native run.

This update supplies reproducible finite admission checks and the written original-outer argument requested in the review. It remains a conditional result: the inherited all-size compiler, exact common-frame mutable-source realization, whole-call hosting, semantic guard with C1=1, fixed-tape/prime-packing interfaces, paid arbitrary-width equal-chunk interchange, exact recovery and analytic transfer are still assumptions. The separate `omega_C<=9/4` corollary has an extra premise and is outside the new original-outer signoff. Nothing here asserts human review, proof-assistant certification, a practical cutoff or a stronger κ.
