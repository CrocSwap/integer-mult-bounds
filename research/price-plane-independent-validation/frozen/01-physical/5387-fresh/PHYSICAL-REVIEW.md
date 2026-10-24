# PR5387 fresh independent physical gate

**Decision: PASS for a fresh bounded physical audit at exact head `b1ab650d36f59e5be682a813145b7c67e219e341`.** Runtime was 10.661 seconds. This is an independently executed new-head proof, rather than inheritance based on equal rank histograms. No candidate evaluator was imported. Complete cost, precision/stock, exact funding and registered cold replay retain their separate gates.

The immutable source capsule manifest is `b0b7eaeef8895264f33e86d87c1bf63fba495d6ac2f50e1414ee3eae775a1594`. All 38 source/head rows were checked for SHA256 and Git blob equality. New word compressed SHA256 is `6412632c28e265597fb088087048091d81c19500fb28a0c9c9d2a48f61b8665b`; decompressed SHA256 is `9aa0d7112b4e13f1aa13a93dab0af6f4435ffe99b842aad841685becdafee492`; Git blob is `c62fcb59643f87919208100517a2fbc4b57cb7d7`. The canonical main and accepted final4610 source payload are unchanged.

The initial ordering-only transfer check was correctly stopped. PR5387 changes the eighth source relation and the physical helper inventory. Its owned pivot L261 replaces PR5383's owned pivot L288. Its eighth snapshot is L256 immediately after source event 11296 in exact frame281, replacing L288 after 11306. Its zero replacement is source event 17233 on L256; the original paid rank-one transition on L288 at 17580 is retained. Final cleanup erases L261. The first seven sites are unchanged. These differences are recorded in the sibling `5387-delta/NARROW-TRANSFER-STOP.json`; that diagnostic is not a counterexample to the new candidate.

The source-specific new eighth relation is

```text
D8new = h225 - h257 + h259 + h261 - h263 - h268 + h269 + h270
        - h271 - h324 + h326 + h328 - h333 - h384 - h388
        + h390 + h391 + h392 - h397.
```

Fresh reverse functional propagation through the unrestricted original 632-input source word proves

```text
C0 at 11514 - L256 just after 11296 = -D8new/4,
L256 at 17233 = D8new/4.
```

These are exact rational equalities over noncommuting free invertible operator words, not numerical samples. The source snapshot has 75 terms before subtraction. The same independent reverse interpreter freshly verifies the fourteen source identities for the seven unchanged sites as well. Changing the relation sign or snapshot source rejects each respective identity.

Rational elimination of the eight published relation rows independently derives exact rank eight and pivots `225,227,229,230,241,245,257,261`. Its reduced basis matches the published RELATIONS rows exactly, has the identity pivot block, and contains only integer/half-integer coefficients. Every preparation ADD reads a retained nonpivot independent helper. The new preparation has 64 events, consisting of 8 clears and 56 ADDs. Its event multiset equals the independently generated RREF preparation; its within-row ordering differs. Distinct pivot blocks write different owned destinations and read only untouched nonpivots, while ADD order on each destination is exact-linear and commutative. No cyclic preparation or independent productive input erasure is introduced. The actual chronology is additionally executed on all entry columns, so no unsafe movement of a CLEAR is inferred from a multiset alone.

The independent checker reconstructs the new complete source delta from its own RREF and source event sites. After the preparation boundary, the entire literal event list agrees exactly with that independently generated word. Forward is literally identical to the accepted source. Every canonical ordered frame, native map, gauge and main chart is identical.

A fresh forward evaluation executes source and candidate in both orientations. New candidate backward includes all **624 independent retained fields plus17 independent arbitrary owned entry fields**. L288 is now a fully arbitrary retained helper and has its exact source physical endpoint; L261 is an arbitrary dirty owned entry, cleared before preparation and erased after its final use. C0 through C8 and the seven other owned pivots also return zero. All 224 main and 400 retained helper endpoints pass, with no owned-entry dependence. Every scalar/native/paid frame, nested paid rank, zero-site complete row and final gauge passes.

The new eight physical zeros occur at shifted candidate indices15680,15966,15972,17329,17341,17352,17360,17818. Their complete rows are exactly zero on all641initial columns. Same-frame COPY into cleared C0 reproduces the complete source center operator with coefficient one and its inherited absolute gauge. Identity on zero needs no new phase operator and performs no runtime zero test. All eight snapshots are simultaneously live before the first center replacement; the last source snapshot 11296 precedes first center 11332. Eight distinct C1 through C8 fields are therefore charged and required.

A fresh source catalogue check confirms the signed warp occurrences are unchanged and all retained paid occurrences are exact source occurrences. Eight centers and eight rank-one jobs are removed in backward orientation; forward removes none. L288's restored paid transition belongs to the original exact catalogue. This is why accepted final4610/PR5241 phase evidence applies even though the particular removed rank-one site changed. The authenticated source PHASE-VALIDATION binds the same source payload; the full phase foundation remains the accepted PR5241 foundation. No fresh Gaussian phase lowering or all 5710 phase replay is claimed here.

The universal operator implication is the one stated fully in the parent5383 physical report, with the freshly proved new relations substituted: evaluate each free generator at the full actual oriented f-column source lift, keep rational scalar coefficients outside the substitution, and include identity on all spectator fields. This homomorphism preserves all sixteen new row equalities for every positive f, including correlated/nonseparable inputs. No tensor power is distributed over a sum. The physical tariff retains the original source geometry/record-fiber domain. Ideal exact zeros are not an assumption that numerical child errors disappear: fresh precision propagation for this changed word remains required separately.

The unchanged source controller has 16 backward calls, two forward calls and 15 queries. Every full call retains its fresh disjoint helper bank. Removing the new eight pivots at backward stages leaves `16*400 + 2*408 = 7216` distinct independent helper outputs, plus 3584 main outputs, for 10800 productive fields. Pivots, snapshots and scratch earn no productive credit. Every suspended recursive occurrence needs its own relevant owned banks. The independently counted backward paid profile remains `{1:2193,2:412,3:510,4:127,5:40}`; forward remains `{1:2201,2:412,3:510,4:127,5:40,8:8}`. The invoice is equal in rank moments to5383, while its changed preparation scalar and precision charges must be checked afresh.

Seven executable-word mutations reject: wrong preparation sign, omitted dirty pivot entry clear, wrong snapshot role, wrong zero frame, wrong retained paid rank, wrong COPY frame and omitted pivot output clear. The full correct all-column execution is their positive control. Independent output columns include every newly arbitrary field, rather than silently retaining5383's smaller domain.

The candidate remains within the same five selected assumptions: `native_all_columns`, `owned_erasure`, `compiler`, `precision_tape`, `analytic_recovery`. This physical gate identifies no extra primitive or candidate-specific premise. It does not independently prove the historical native/tape/BIT/analytic stack, fund the new compiler-margin κ, supply a new human/kernel acceptance or change selected metadata.

Reproduce from the project workspace:

```sh
python3 -B outputs/price-plane-swarm-20261024/01-physical/5387-fresh/independent_physical_check.py
```

The source code's final post-execution edit corrected a provenance comment only; executable logic is unchanged. `PHYSICAL-RECEIPT.json` is the actual 10.661 second execution. `ENGINE-FREEZE.json` binds all final files.

Credit Dugongue's5387 application and alternate eighth witness; Ali Romman's5383 public eight-relation mechanism and5377 predecessor; Cao Yifan's4610 word; Cinna Davis's controller/helper/free-word lineage; zxv's native/compiler/precision work; Jacob Alan Sussman's recursion; Chris R/Clear1nsight's5241/5384 independent admission; ToikY and all retained notices. The author explicitly makes no priority claim over5383 for the construction. This independent review used substantial OpenAI Codex assistance.
