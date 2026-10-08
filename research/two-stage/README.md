# Two tensor stages beyond 2^-16

The final conditional multiplication saving is **κ=15536/10^9=1.5536×10^-5 > 2^-16**. The bit saving is 15537/10^9, with exact moment slack greater than 2.7×10^-10. The final assembly slack exceeds 5×10^-10.

The [proof](../../notes/two-stage-16-note.tex) and [six-page PDF](../../artifacts/two-stage-16-note.pdf) specifies all interfaces and dependencies. The result is conditional on the inherited analytic and fixed-tape arguments; it is not formal verification or a practical runtime claim.

## Construction and scope

Paureel's two-stage partial-swap topology retains its paid rank-one copy correction. PR24's retained-total producer is rebuilt at dimensions 55 and 53. A specialization of its controlled inner basis simultaneously gives both auxiliary small corners and ordinary local blocks. A modular nonzero determinant, lifted to a rational witness and combined with the finite-product argument, establishes the required data corner on the same basis family.

The complete physical list charges the auxiliary exits, both local producer orientations, interstage data transitions, both data growth families and all N correction calls. There are no uncharged gathers, extra role discounts, or independently chosen per-edge bases.

The PR21 complex circuit stays unchanged at saving 18×10^-6. PR23's literal scalar charge and semantic C1=1 remain source-pinned. New bit/complex product row accounting requires p^47000, and beta=1/10 leaves enough complex leaf saving. All 47 strict conditions and seven final margins are recomputed.

## Reproduce

```sh
python3 research/two-stage/producer.py
python3 research/two-stage/verify.py
python3 -m unittest discover -s tests -p test_two_stage.py -v
```

The producer command rebuilds both changed DAGs and exact integer label checks using Python and C++17. Its saved records include each support check, scalar identity, matching, role count and histogram. The verifier consumes those records and verifies source hashes; it does not silently rerun the large producers. The four focused tests cover new common-basis corners, dirty endpoint composition, correction accounting and the exact assembly. Inherited unchanged checks are preserved by hash.

## Attribution

Zhihao Chen (jacklightChen), with substantial OpenAI Codex assistance, contributed this unequal two-stage composition, compatibility proof, finite witnesses and new assembled result. Preserve the earlier GPT-6 Astra assistance attribution without inferring the current runtime model.

Credit Aurel Prosz (Paureel) for the two-stage topology and correction; Swapnil Jain for the linked two-stage batching development; icekylinx for PR24's producer and controlled inner family and PR18/10 predecessors; RaD/hipotures for the semantic/bulk analytic ingredients; eumemic for source frames and earlier resampling/complex work; and every preceding author retained in NOTICE. PR25 and PR27 are concurrent refinements, not claimed as this work. Future research using this contribution should explicitly acknowledge Zhihao Chen and cite it, together with all other dependencies used. This request imposes no additional license condition or global-priority claim.
