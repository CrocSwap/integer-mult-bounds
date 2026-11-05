# Post-first cross-review: factorial/pair oracle and actual controls

**Verdict: PASS for the nine complete finite cases and the six retained actual-source mutations; no material mathematical defect found.** This reviewer read the new peer model/results only after both independently authored models and actual-source firsts had completed. No scientific code, import, constructor, compilation, checker or replay was executed during this cross-review. Pure primary mathematics and all firsts remain unchanged.

Reviewed `oracle.py.PURE.txt` SHA256 `388e5a539e463fb6ddedfc1882e8a397a84cf410192da33a8a50f613fe97ca84`, integrated public oracle SHA256 `4a8ec05d6953a0d6ccb1b8e208da8f891a3d5a944f07d95e8c6e97ac6a378df2` and its shared wire tail, actual `source_eval` invocation, actual mutation builder and first packets/receipts. The three healthy packets are identically14,578 bytes, SHA256 `617b7a1cb0fd950ed97f5694d455bb2b4d6c4665b5744d969c076ac2368f882d`; metadata-only hashing confirms all three actual packet files. Controls first is2,471 bytes, SHA256 `ba4529b8c58f29f06224167c29f012f50866012580e89311036a362664236293`. Runtime/RSS figures remain coordinator measurements, not new measurements by this reviewer.

## 1. Factorial lattice and the signed pair law

The oracle enumerates multisets of target-support indices using combinations_with_replacement, then computes `h!/product(a_i!)*product(T_i^a_i)` exactly. Integer division is justified by the multinomial coefficient, and degree zero gives one empty multiset, coefficient1,column1. This differs from the primary's weighted ordered-target-word enumeration and the source's binomial coordinate recursion. No source Flow class is imported into either expected model.

Although oracle lattice rows retain only numerical column and coefficient, losing the explicit count tuple does not corrupt its pair method. For a degree-h tuple b, partition its complete parent supply by its possible last target letter i. The part indexed by a=b-e_i has weight `T_i*u_(h-1)(a)`; their sum is exactly u_h(b). For fixed path rho and paid rank r, put z=rho*c(a). The oracle tests

`parent_present: k_i*z<=cap`, `child_present: r*z<=cap`,

and gives the pair weight `path_multiplicity*P_r*T_i*u_(h-1)(a)` at rank k_i*r*z. Parent presence is the same for every i contributing to this fixed b, while child presence selects exactly the capped Pascal terms. Thus:

- both present contributes exactly the matched job count;
- parent-only contributes the unmatched paid/boundary residual;
- child-only contributes the missing source residual;
- neither present contributes nothing.

When parent exists, capped child demand is a subset of the Pascal partition, so these contributions equal min(supply,demand) and its correct integer residuals. When parent is absent, child-only terms sum to the full missing demand. Summing all prefix multisets and target letters gives exactly the source's full tuple matching, without assuming scalar column-product uniqueness. Coincident products of different tuples simply contribute additive histogram rows. This is a whole-integer partition, not a fractional matching shortcut.

`matched_jobs` uses this same both-present pair weight, so it counts all matched occurrences, not rank-weighted mass or only distinct classes. Paid paths are ordered support words with exact product multiplicities. Different orders with the same product remain separate words. No multiplicity is replaced by a presence Boolean.

## 2. Presence, floors, revival and terminal edges

The oracle computes default G by the same mathematical threshold min_target^G<=floor(n/max_target), without floating logarithms. Raw cases at121/604/605/3024/3025 straddle cap/height thresholds: with raw max121 and min5,604-to605 changes G0-to1 and3024-to3025 changes G1-to2. Complete packets cover the whole returned fields, rather than checking only these threshold flags.

Unlike the source's merged path Counter, the oracle enumerates all paid-support words. A path with rho>cap has no present unit or pair, since both target/paid ranks are positive; it contributes zero. Crucially an empty current unit batch with rho<=cap is not used to skip its lower-degree pair analysis. The pair loop therefore retains missing-parent/present-child sources and revival. At terminal depth it checks only rho<=cap, then emits **every** paid rank with its multiplicity; it does not apply a new_rho cap to terminal exits.

Unit/column totals use actual present lattice rows with their complete path weights. Root requests use all target letters on every capped root unit. The complete count bound uses total paid/target multiplicities Ptot/W, not support sizes. The oracle validates source/exit/boundary support and rank conservation; these are independent guards, not substitutes for whole histogram comparison.

## 3. Mirror and raw-inventory boundary

The oracle aggregates all exits plus every source complement n-s, permits rank0 in that paid histogram, and leaves source_count as the full sum of original source occurrences. Its `_add` accepts nonnegative rank and positive integer count. The source_count denominator is not reduced when a zero complement is omitted from positive rank mass. All14 frozen fields, including boundary histogram and mirror, are returned in exact sorted-integer encoding.

For raw cases it reads only the original full p7 JSON's strictification target/paid multiplicity dictionaries. This is a pinned input inventory, not verification of native matrices,6240-fold strictification, physical calls, moments or selected framework admission. The actual-source evaluator runs authenticated canonical Flow definitions and Flow.merged, then adds the mirror by its explicit complement rule; source Flow itself returns13 fields, and mirror is the additional standardized field. Source verify.py, literal and approximate_leaves are not invoked. The actual source execution is the program under test, not a third independently authored mathematical implementation.

## 4. Actual code controls and why mass alone is insufficient

The control builder requires each original source text patch site to be unique before replacing it. It executes the altered actual Flow via the same actual-source invoker, after healthy complete agreement. It does not mutate a receipt or a mock model. Generic syntax/runtime faults are not accepted as success; the guard-rejected cases catch the actual source ValueError checks. Three designated controls are additionally forbidden from passing merely by raising a source guard, requiring a returning altered full case.

Actual first receipts show:

| Actual-source mutation | Observed outcome | Evidence distinction |
| --- | --- | --- |
| unsafe empty-batch prune, revival16 | returns; seven fields change | Original scalar guards and rank-one mass identity still pass |
| terminal output cap, raw121 | source guard rejects | Exact rank-one telescoping identity |
| paid multiplicity drop, raw121 | source guard rejects | Exact rank-one telescoping identity |
| binomial coefficient removal, multiplicity18 | source guard rejects | Pascal demand cannot exceed present supply |
| zero-complement denominator drop, raw121 | returns; source_count alone changes | Scalar source/exits mass identity still passes; denominator loses224 source occurrences |
| boundary output histogram drop, partial50 | returns; boundary_exits alone changes | Source/exits mass identity and original internal guards still pass |

These outcomes are read from coordinator-run actual control receipts, not newly run here. In particular the unsafe prune changes column_mass,exits,minimum_source,mirror,source_count,sources,units while preserving its scalar balance. The zero-denominator case changes source_count7688-to7464 while mirror still retains[0,224]; the mass check in its receipt is the source/exits identity, **not** a claim that its broken mirror denominator still obeys the mirror identity. Dropping only the returned boundary histogram likewise escapes a source/exits mass-only comparison. This demonstrates why complete field equality is the acceptance gate.

## 5. Wire, independence and limits

The common coordinator-authored CLI/authentication tail is explicitly shared, not counted as mathematical independence. It hard-binds contract/manifest/canonical Flow/raw inventory hashes and source object length/SHA/Git identities before the actual mathematical build. Default checks freshly regenerate the complete packet and compare every canonical byte with FIRST, so changed histograms, boundary data, source denominator, added/missing fields or equivalent-but-noncanonical JSON cannot pass. Emit refuses to replace an existing first file. Earlier unexecuted wire/driver versions were retained separately and must not be described as scientific first failures.

New peer exposure begins with this post-first review. Historical S8 source-aware proof/raw-data exposure and shared wire are explicit; this is not source-blind or independent end-to-end execution. Three healthy packets are two dissimilar expected models plus the exact actual canonical program. The six mutations corroborate this **finite nine-case** boundary; they do not establish all n, a native census, physical ordering/coupling/ordinary-control bill, analytic hypotheses, all-rank induction, a proof-kernel theorem, full selected assumptions, kappa or a frontier change.

Credit zxv/source Flow and original checks; Jacob Alan Sussman's separated multinomial and retained notices; the fixed inventory/supplier lineage; and S8 for the separate written code-to-law implication. This work uses substantial OpenAI Codex assistance and claims no independent human or proof-kernel acceptance.
