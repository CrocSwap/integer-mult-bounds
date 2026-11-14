# Independent B12 source, workload and complete cost review

**PASS in this complementary scope**, at final PROOF.md SHA256 `3167e19209a8fee4e5095b7c5914661163c7d038b5f745b64dd8713a6a9252ac`. The combined graph and alias/finite-flag/owner semantics receive separate independent review in `worker-c/review-current-arithmetic`; this report does not duplicate its physical interpreter.

## Reviewed result and exact pins

Canonical base is `e54523517d0f03e58352e647c403a5af3e525a57`; retained all-division dependency is published `9700fc89e2582a1fb358a4c6d0d0387076192adc`, based on B10 `c4ab5dab6914a04cb86d1fe54eb763b35cc7eeb1`. JOIN-RESULT.json pins the final arithmetic constructor, binder, source checker, proof and author source receipt. The observed graph is1,304,162 states with digest8911a498e8e36409ca3b48395e7d754f49b4e452c273db821756867cea95a045.

The exact source closure contains only compare/add/divmod/subtract_exact at its16 raw sites per direction; the finite subtract_exact wrapper calls subtract. No further numerical provider is reached after the old division body is removed. Fault-only branches remain outside admission. I independently derived every H/J term from the original source. The proof's original-success premise and finite-trace induction establish replacement termination; success of the replacement is not assumed. The new instrumentation-erasure paragraph correctly preserves actual owner/source/acquisition state and the finite halt tag while removing transcripts, observer-only counts and the bounded replay watchdog.

## Independent source and meter evidence

`independent_source_check.py` imports only four pinned original files. It runs14 exact forward/inverse source fixtures, including nonleaf groups, boundary widths, invalid/padded coordinates, aliased doubling and dirty unrelated guard heads. A separate integer prefix-inverse oracle verifies every numerical output and serialized record. All borrowed source data and protected Words remain unchanged; final owned numerical histories are blank.

The checker labels each actual Word read/write/move by provider nesting depth, independently of the interval deltas around old provider methods. The two counting surfaces agree for6,189 outer raw calls and4,519,473 Word actions. The correct removed total is3,946,547. Inclusive nested-provider summation would remove4,639,829 and is explicitly detected. Later output retirement stays outside the removed intervals; two returned P-bit Words incur exactly2(5P+8) retained source actions. Normal and optimized receipts are byte-identical at `9ee37a5773be6bf80f06f022681db8c86dc491eb2e55f6f5349c284d68e694a0`.

SOURCE-REVIEW.md gives the universal proof of

    H <= (6P+3)E + m(10P+7) + t(8P+6) <12(P+2)^3,
    J =3m+2t+v+2E <=(P-2)(4P+5).

## Final binder and paired-run cost join

I read final binding.py and verify_source.py. The old spy increments its nesting depth before invoking an original provider and accumulates only depth0 intervals in its finally clause. Saved providers are used only for scope restoration, separate baselines/counterfactuals or the deliberate negative control; no positive new-source fallback occurs. The new numeric actions flow through arena.meter once, while selectors use their own marker owners. Source and marker overlaps are subtracted once before literal instructions are included once.

The final author source receipt covers1135 comparisons,1510 additions,107 subtractions and192 divisions, with1258 aliased simple calls and22,179,316 literal instructions. I independently checked all recorded arithmetic identities and the full vector in JOIN-RESULT.json. Exact aggregate simple-entry counts follow because the distinct-versus-alias difference is122P+214 for all three entries; thus aggregate alias counts suffice to verify every per-producer instruction total including four setters. Each leg contains exactly one89-instruction ACQUIRE, and metadata equals256+32I+16400J+16408H.

The four residual source equalities are:

- Full source forward:694658−568719=125939.
- Full source inverse:694736−568719=126017.
- Payload forward:115384−79636=35748.
- Payload inverse:348654−267496=81158.

Both retained payload marker equalities also hold. These are static checks of the frozen author receipt; the separate original-source experiment above supplies independent action-level metering evidence. I did not rerun the heavy combined graph/source packet.

The claimed literal subset bound follows from the proved primitive formula401P+1073 and the inherited division bound. The inherited2^20(P+2)^4 source-operation ceiling applies **only to the framed numerical producer body**. It cannot price an arbitrarily long caller prefix, Entry/frame preparation, external source construction or a larger earlier history by the current child's P. Those charges remain separate, together with grant acquisition, all unlowered Word lifecycle/controller work, finite metadata and actual per-owner history maxima. Output Word retirement is retained source work; selector retirement is already literal. No H-free old-history claim or common unit conversion is introduced.

## Scope and reproduction

The source-only checker is read-only and uses the standard library:

    python3 -I -W error -B independent_source_check.py --source-root PATH
    python3 -I -O -W error -B independent_source_check.py --source-root PATH

PATH must contain the four pinned original source paths (the B12 inputs tree does). The universal result relies on the written source/loop proof and the separately reviewed primitive theorem; bounded fixtures are corroboration. Existing source admission, output framing, finite allocation/controller and full supplier/global compiler obligations remain. No new kappa or full foundational-assumption removal is inferred.

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance. Credit the original #5053/#7388 source and the B10/B11 packages; this review is independent of the B12 author implementation/oracle in its declared source/action-partition experiment. No human or formal-kernel acceptance is claimed.
