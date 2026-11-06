# Independent forward-residence and dual-certificate review

Jerry Chen / @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0. This is a separate implementation and mathematical review in the same AI-assisted session, not external human or formal-kernel acceptance.

**No discrepancy found.** On the exact #6702 source, the independently reconstructed census has 631 helper intervals, 2,387 chronological systems and zero span nominations. This is a source-bound exclusion within the declared dyadic rewrite class, not a new κ or a global native optimum.

## Different construction method

`review.py` builds a forward static-single-assignment graph. Every destination change and source read creates a new register version; MOVE creates an identity version at its new frame. INIT creates a fresh live zero node, and CLEAR ends the lifetime. COPY becomes ADD plus an explicit pre-COPY destination observable. The live frame/residence census is computed forwards.

The final proper-output observations and COPY monitors are propagated through this immutable graph, rather than through the author's mutable register/frame reverse sweep. The resulting 33,455 forward residences exactly match the author's reverse census. Every eligible interval, extended movement bound, removed export, scale coefficient, target vector and carrier-response vector also agrees.

For every rejected current system the checker generates a separating functional λ with zero dot product against every candidate column and dot product one against the target. All 2,387 duals are retained in `PR6702-REVIEW.json`; 24,012 direct dot products validate them independently of the elimination procedure. Controls reject a zero witness, changed carrier inventory and changed target. Normal and optimized runs produce byte-identical receipts.

The historical #6453 control independently gives 634 intervals and all 2,413 candidate cuts. Its 35 successful systems belong to exactly the two published helper intervals 336 and 368. The author's two nominations stop at the first hit per interval; this review checks every cut. The other 2,378 systems have dual certificates in `PR6453-REVIEW.json`.

## Temporal and modular implication

The nearest preceding/following non-SCALE writes bound the held helper's constant-up-to-scale residence. Its last retained earlier read and first retained later read give `move_lo` and `move_hi`; these can extend outside the two original MOVE indices. The independent forward graph checks every endpoint-frame recipient segment, including source-read touches and owned lifetimes.

An E injection may use the earliest feasible cut in a constant-response segment; a G injection may use the latest. At the fused-MOVE cut, E additions can precede it and G additions follow it. Between consecutive retained thresholds, available columns are contained in the set at the earlier threshold. Endpoints and thresholds therefore cover every legal integer cut. The held helper has no non-SCALE write in that window and cannot be its own recipient, preventing feedback into its source row there. Later feedback is included in the suffix graph. COPY-zero observations remain constrained; dirty CLEAR erasure is allowed.

The checker proves that 65521 is prime, all source coefficients are dyadic and every source SCALE is a signed power of two. Earlier-cut inverse scales therefore remain dyadic. A deterministic public-input assignment with seed 27 gives a nonzero modular value at all 631 held rows; these exact values witness nonzero rows, rather than providing probabilistic confidence. The complete all-input source endpoint check remains the author's separately invoked check; one assignment is not presented as an all-input audit.

An allowed dyadic identity reduces under `Z[1/2] -> F_65521`. Because the held row is nonzero in the field, all-input preservation requires the response-vector span equation itself. Each retained dual certificate contradicts that equation. This does not exclude rational coefficients with denominators divisible by 65521 or any of the author's explicitly excluded changes: new input basis corrections, changed helper writes, new carrier transports, coupled interval edits, or changed target contracts.

## Reproduction and source boundary

The checker authenticates `search.py` SHA256 `fb09340a36be41e1ac0570556a1b5ff51e2dbb314c6d54a1318f29393c8795a9`, then executes only its generation prefix for comparison with a read-only residence trace inserted. It never invokes the author's elimination. Independent SSA construction, candidate generation, response propagation and dual checking are implemented here. The current compressed source is SHA256 `e8c7a9d54d98a4cfa27e15593016b3908afed303e0f480076ed3f596192e5a4d`; the historical control is `e64cc53ea0088191423045cb8563b5bc87a34f6b992baa1593c7917d95a07820`.

```sh
python3 -I -B review.py /path/to/p104-distributed-carrier-recoding PR6702 /tmp/current-review.json
python3 -I -O -B review.py /path/to/p104-distributed-carrier-recoding PR6702 /tmp/current-review-o.json
python3 -I -B review.py /path/to/p104-distributed-carrier-recoding PR6453 /tmp/control-review.json
```

Only the Python standard library is required. The optional third positional argument selects the output receipt; no author files are modified. The #6726/#6702/#6529/#6453 source authors and all preserved notices retain credit. Physical native action, supplier admission, compiler, precision/tape and analytic recovery are outside this review. The five framework assumptions remain unchanged.
