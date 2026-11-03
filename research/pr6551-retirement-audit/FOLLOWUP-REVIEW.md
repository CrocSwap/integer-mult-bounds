# Independent review of the expanded audit integration

**Verdict: no unresolved blocking finding within the finite caller, cut, source-contract binding and Gaussian invoice-delta scope.** This verdict was derived from code, source objects and receipts before reading any response to the external review. The existing source/native assumptions are unchanged. This is separate AI review, not independent human review, formal verification, a new numerical kappa certificate or supplier admission.

## Snapshot

Reviewed contribution baseline: `13e880a734cc03f2a52c82a412a9a0e6ac2b1f0c`. Construction sources remain PR6551 `11ca568cd1a16776ade02b4df09ea04a784cc674`, PR6545 `775722aa94a5e85b05d1d704d7dca10cbf016f0c`, and PR6398 `dee2663ba0918be86993fd9d63c8d64b020f4c83`. The following working-file hashes identify the reviewed expanded code and receipts; a new publication commit must bind them.

| File | SHA256 |
|---|---|
| `check_source_objects.py` | `793b5eba68ff87deb137c2b07f24b434790538fca76701bb80ab271088420a9f` |
| `pricing_binding.py` | `a0362e2bfb29ef38f914e8d6d89784a6078a0e24a8f7cc2ea07385d071c113f9` |
| `verify.py` | `ec190aa7e13c2d73ec871e9f2cc4ffdfe031ee7ec4722538f648127d786d5bdb` |
| `cut_four_fibers.py` | `3b15f6c17d2e7a941c97a29cd4269388cd07f824a4d8df16fc22a62c1515fcf8` |
| `caller.py` | `667dfc0b99b194dd4213f44596f8a7de4916022517a63da589fc2f201a8fcd2b` |
| `accounting.py` | `c032bab18b8fe8763fec40958a8f6ae09d7e973755005347cec4e74f86128605` |
| `RESULT.json` | `8c6a7c6fc8872b8de465ebd3101428c9344aed3d93bf82a1a930f183802c8c13` |
| `RETAINED.json` | `4dadc39c1e4b65f74ab1874107c64ebe58ba10018062f74eaad8c4b551381cb8` |

The package root is `research/pr6551-retirement-audit/`. Documentation and publication evidence were still being updated by the lead and are not included in this code-snapshot verdict.

## Full independent endpoint extension

The integrated four-fiber script has exactly the same hash as the independently developed and tested extension. The integrated `four_fiber_cut` receipt is exactly equal, as parsed JSON, to the independently sealed normal/optimized receipt. It retains all earlier cut/lifetime checks and adds every coefficient of both complete 35 by 35 endpoints at q=`1,-1,i,-i`, with formal stage variables. The CRT justification supplies exact coverage of the full q quotient ring, rather than probabilistic testing. Both source callers and a valid inverse half-ADD suffix edit pass.

The four new suffix mutants are required to pass the original cut checks and to raise `EndpointMismatch` from the complete transfer comparison. This avoids confusing source-schema rejection with actual suffix coverage. Explicit first disagreement polynomials are retained. Maximal common prefix 358 and suffix 67, the changed event slices, and nine changed diagonal-role records are computed from literal data. The earlier shared 345-event cut is not presented as sufficient evidence for the changed suffix.

The independent full-caller engine remains unchanged and uses a different polynomial organization. Shared assumptions include the declared opcode meanings, Gaussian physical rank interpretation, factorwise tensor convention and Python rational arithmetic. These engines do not independently establish physical native maps or all-width implementation.

## Pricing-source binding and ordinary arithmetic

`pricing_binding.py` parses, but never executes, the two exact pinned pricing sources. Its copied AST tariff clauses are explicitly labeled a **source contract**, not an independently derived physical law. The independent accounting implementation remains separate. The source hashes bind the entire file, while the AST checks identify the precise clauses that were reviewed. The changed-source, query-tariff and raw-tariff controls reject; the two actual source files are positive fixtures.

The wrapper recomputes the declared ordinary expression using the actually replayed 609/611 event counts and requires exact values 254699248/254932208. This establishes arithmetic under the copied source formula. It does not prove the physical 32-per-field rate, local 10^7 allowance, routing costs or ultimate 10^9 bound. The receipt key `declared_ordinary_bounds` and the pricing receipt's explicit scope keep that distinction visible. The complete Gaussian delta continues to cancel the exact same 18 native invocations under the shared native contract; the two extra ordinary translations are neither omitted nor declared free.

I ran the pricing binding directly under isolated optimized Python. It passed and produced exactly the integrated pricing receipt, so no stale clause-binding receipt was found. The aggregate now contains 29 internal rejection controls: 11 primary caller, 7 accounting, 4 retained cut, 4 full-endpoint and 3 pricing. External corruption/provenance controls are separate evidence and should not be silently included in that count.

## Integrity and the external trust anchor

`verify.py` now correctly names its portable source check **integrity**. It checks both hashes and the exact source-file inventory before importing only the new audit modules. It gives those imports a fresh bytecode-cache namespace and launches the separate endpoint checker with its own temporary cache. The default compares the freshly computed aggregate with RESULT; `--emit` is explicit. No source pricing code, constructor or predecessor scientific verifier executes.

`check_source_objects.py` adds a separate, optional provenance operation. It requires an externally supplied full publication commit, reads that commit's RETAINED manifest with replacement objects disabled, requires the working manifest to equal it, and compares working retained inputs with each declared source commit/path and blob identity. It never fetches. This is an appropriate narrow source-object check when the publication pin and checker are obtained through a trusted channel.

A material boundary is explicit: that optional check anchors the manifest and **working retained source files**. It does not by itself validate all source copies, audit code or RESULT stored in the publication commit, establish a GitHub repository's ownership of an object, or authenticate its own executable. The separate committed-byte preflight and trusted acquisition of the checker/publication pin remain necessary. I notified the lead to preserve this distinction in the documentation; no change to the code was needed.

The recorded positive 20-file check and consistent-substitution rejection use the old 13e880a publication manifest. That is a meaningful control of the external-anchor boundary: a joint harmless source/manifest substitution can pass portable integrity while failing the anchored comparison. It is not a recorded pass of the expanded 22-file manifest at a new publication commit. The lead must run the tool again with the new final publication pin before claiming that new pass.

Independently of that future publication step, I compared every current retained source directly to its exact original Git object with `--no-replace-objects`: all 22 match. In contrast to the first review, PR6398's original commit is now available locally and all four of its copies matched directly. The earlier retention-chain fallback is superseded for this source-comparison observation only; it did not change any source bytes.

## Actual review operations

All operations ran from the intended checkout after sourcing `/workspace/.integer-mult-env/activate`. I read the expanded scripts and current aggregate/input manifests, recorded the eight hashes above, inspected the source-comparison/provenance-control evidence, compared the integrated CRT JSON with the independently sealed JSON, and queried each exact source using:

```text
git --no-replace-objects show SOURCE_COMMIT:SOURCE_PATH
```

Each source command had a ten-second timeout and captured output; all 22 returned 0 and matched the corresponding copied bytes. I also ran:

```sh
python -I -O -B research/pr6551-retirement-audit/pricing_binding.py research/pr6551-retirement-audit/source/pr6545/pricing.py research/pr6551-retirement-audit/source/pr6551/pricing.py
```

It returned 0 in 0.182039 seconds; all three controls passed and the JSON equaled `RESULT.json`'s pricing section. Exact arguments and comparison outcomes are in the companion reviewer check record. No full registered replay, exporter, artifact regeneration, Git mutation, public write or nested agent was run during this final integration review. No additional source dependency was installed.

## Remaining publication and scientific work

The lead's serialized registered replay, export/cold replay, committed-byte check and new-publication source-object check must bind the integrated snapshot before publication. Code, source or receipt changes invalidate the corresponding hashes above and require targeted rechecking. Docs-only corrections do not establish or invalidate a new scientific theorem by themselves.

No numerical crossing, changed completion tail, compiler, outer theorem, physical native/operator tariff, all-width realization, erasure, precision or tape claim is added here. The five inherited framework assumptions remain. Construction and retirement credit remain with Ali Romman and the retained predecessor authors; new audit work is prepared for DLamdata with substantial OpenAI Codex assistance, Apache-2.0.
