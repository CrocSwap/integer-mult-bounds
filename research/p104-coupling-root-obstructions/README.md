# Coupling-idle obstructions for shortest rank-one roots

**No new κ.** This package proves limitations of a natural multi-coupling extension of the pending chain-root construction in CrocSwap/integer-mult-bounds#6833. It does not contradict that two-arm construction or alter the selected result.

The proposed extension has four disjoint chain arms and two coupling fields. Its attractive invoice merges the coupling idle across each left/right arm pair. The missing question is whether a caller with that invoice can have the required arbitrary-input endpoint. A necessary algebraic condition answers this for hub-only transport of the stated pure coupling carriers.

## Exact result

For any product of `N` rank-one square-zero queries `I−2 x_i y_i` equal to `−I` on an `n`-dimensional space, put `G_ij=y_i x_j` and `A=I+2 lower(G)`. The ordered-product identity implies `rank(A−G)=N−n`.

In a shortest root, `N=n+1`, every off-diagonal pair obeys `G_ij G_ji=−1`. Actual alignment of the entire coupling idle projector of an opposite-sign left/right pair makes its active coupling rank-one matrices negatives. Their cross-Gram products with any third disjoint arm are then negatives, so both cannot equal `−1`. Such a caller needs at least `n+2` queries.

For the even-stage four-arm proposal with `e` empty spectator fields, at least `4+e` thin queries are necessary. The `e` rank-one spectator targets compensate only `e` charges. Adding empty fields therefore cannot recover the original three-thin invoice.

[PROOF.md](PROOF.md) gives the general identity, exact common-gauge hypothesis, physical `Q=±1, D=1` specializations, spectator accounting, and exclusions. For the unmodified full-query vectors, the independent [support-cut proof](support-cut/PROOF.md) rules out three thin queries for the proposed coordinate stage supports even without the carrier-alignment premise. Its [reduced-hub supplement](support-cut/REDUCED-HUB.md) checks the immediate rank-one hub-support variant.

The [complete price certificate](PRICE-CEILING.md) grants an even more favorable relaxation: all four hub idles may be billed as one whole job. Nevertheless, every declared aligned four-arm invoice, including arbitrary binary child partitions, has negative margin for every saving `C≥1/310` (`≈0.003225806`). Exact integer-root bounds and discrete concavity cover all positive arm lengths. This threshold is below the pending CrocSwap/integer-mult-bounds#6833 crossing near `0.0033718004755`, but above the selected `0.003125804` frontier; it rules out this route to improving the pinned pending result, not every possible supplier.

Under the stronger hypothesis that **all** arm carriers agree in the actual common gauge, [the exact cyclic-sign theorem](all-aligned/PROOF.md) gives `N−n≥k−r≥ceil(k/2)`, where `r` counts cyclic plus-to-minus sign transitions. The [all-arm price extension](ALL-ARMS-PRICE.md) uses that growing query charge to prove the same `C<1/310` necessary price ceiling for every arm count `k≥3`, every positive arm-size tuple, and arbitrary binary children. This stronger result requires one common carrier for all arms; partial sharing remains outside it.

The complementary [hub-carrier audit](hub-carrier/PROOF.md) identifies the exact discarded operator when equal carrier images have different duals. Its explicit `U=1,V=−1` counterexample rejects naive fusion; the specified copied-query repair costs more than retaining the two jobs. This is distinct from the complete-root obstruction.

## Reproduction and executed checks

From the repository root, run the complete package without regenerating evidence:

```bash
python3 -B scripts/research_package.py --package research/p104-coupling-root-obstructions
```

Expected final marker: `PASS_REGISTERED_RESEARCH_PACKAGE`, together with `PASS_COUPLING_ROOT_OBSTRUCTIONS` in normal and optimized replay. The registered hook validates the revision-8 task and canonical provenance, authenticates both retained scientific source files, and runs all six checkers. A self-contained export runs `python3 -B research/p104-coupling-root-obstructions/verify_all.py` directly. Each constituent checker also runs directly; child interpreters use a fresh bytecode namespace.

The shortest-root checker prints `"status": "PASS"`, 20 exact shortest-root cases, 1,650 cross-Gram products, 625 exact alignment-grid cases, and five controls. The support-cut checker validates 224 minors, three spectator embeddings, 1,330 query placements, and six scope controls. The aggregate and component checks also pass with `python3 -O -B`; explicit exceptions preserve every check under optimization. The hub-carrier checker verifies 18 active planes, 324 pairings, two residual coefficient tables, and five controls. The price checker authenticates its native profile and certifies the global envelope maximum at total 38, with six controls. The all-aligned rank checker exhausts 2,040 sign words through ten arms, with exact-rank and scope controls. The all-arm price checker adds an infinite affine-envelope proof and finite corroboration through 24 arms and total 96. Only the standard library is required.

The shortest-root cases cover every even dimension from 2 through 20, including independently conjugated and nonunit-rescaled roots. Controls reject an uncompensated query change, an omitted query, and an incorrect product-formula coefficient. A valid four-query root in dimension two demonstrates the shortest-length assumption is essential. A nonaligned pair demonstrates the carrier-alignment assumption is essential. These finite checks corroborate identities and failure modes; universal conclusions rely on the written proofs.

Detailed replay, export, and mathematical review coverage is recorded in [VALIDATION.md](VALIDATION.md).

## Scope and assumptions

The carrier obstruction requires the **actual accumulated ordinary transport** to identify complete pure coupling idle projectors in one common gauge. Mere abstract conjugacy is insufficient. Additional ordinary maps can be any invertible coupling-only matrices, provided their complete endpoint is identity. Different arms' chain coordinates remain disjoint, and the endpoint is required on every input column.

The result does not exclude maps mixing chain and coupling coordinates, different stage supports, carriers involving chain information, a different endpoint, or more queries with a genuinely improved complete invoice. Initialized ancillas with a restricted input subspace or non-scalar restoration endpoint are outside this theorem. No native-supplier correctness assumption is discharged; the selected construction's five inherited assumptions remain unchanged.

## Provenance and review

Canonical base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.

The originating open direction is more than one coupling field in `research/p104-chain-nested-root/README.md`, Open next questions item 2, introduced in CrocSwap/integer-mult-bounds#6833 at exact head `ad24ad966b857dbfed50d9121624db84b2eccc92`. That pending package is mathematical context, not an accepted frontier. Exact source hashes are listed in [SOURCE-PINS.json](SOURCE-PINS.json). The retained result is an unchanged source pin, not a new certificate.

Credit to DreamingOfClouds for the chain-nested root and to thu-nmrc, zxv, Cinna Davis, Ali Romman, and preceding contributors for the callers, whole-idle mechanisms, and native interfaces. Contributed by **@CubeJerry**, with substantial OpenAI ChatGPT assistance in derivation, implementation, and coordinated research. Separate AI research workers independently derived and challenged the displacement/trace proof and inspected the checker; the lead independently checked that proof. The support-cut argument was developed independently of the carrier argument. These are mathematical/code reviews, not human acceptance or formal proof-assistant verification.


The corank-one Gram mechanism has characteristic-two predecessors: Cinna Davis's CrocSwap/integer-mult-bounds#4666 [minimum-query simplex proof](../productive-controller-basis-search/GLOBAL-PROOF.md) and Ali Romman's CrocSwap/integer-mult-bounds#5617 [query-frame and stage-capacity cuts](../shortest-controller-stage-capacity/PROOF.md). Those notes explicitly delimit their characteristic-two scope. Here `A=I+2 lower(G)` comes from the exact ordered characteristic-zero endpoint, and the opposite-arm trace contradiction applies to pure coupling-idle fusion. This extends that mechanism without reducing arbitrary complex callers modulo two. No worldwide priority is claimed for the elementary rank tools.

New material is licensed under the repository's Apache-2.0 license.


### Concurrent work

A publication checkpoint located DreamingOfClouds's concurrent CrocSwap/integer-mult-bounds#6836 at head `99b18108eda17764d55301aae12948b547b17635`. Its `research/p104-chain-idle-cover-optimal/PROOF.md`, Section 2, also derives the characteristic-zero shortest-root rank-one Gram identity and uses a three-site sign argument to constrain the largest productive targets. We credit that common identity and make no novelty claim for it. The distinct results here concern actual transport of pure coupling idle carriers, the resulting extra root-query charge, the independent stage-support cuts, the explicit discarded fusion operator, and an all-length complete four-arm price ceiling. No unmerged implementation from that submission is imported.

## Open next questions

1. **Can chain/coupling mixing evade the trace obstruction?** Such maps can make cross-arm pairings depend on chain coordinates. A useful first step is an exact arbitrary-input three-arm caller with a fully priced common carrier. The outstanding obligation is its complete stage and endpoint identity, not only a favorable histogram.
2. **Can a different carrier avoid opposite active coupling projectors?** The theorem addresses entire pure coupling complements. Carriers using both chain and coupling data may behave differently. A candidate must transport both the image and its dual through the literal intervening word.
3. **Can partial sharing or a changed cost model recover the query cost?** The fixed-profile all-common-carrier family is now excluded at every arm count for `C≥1/310`. A useful first step is an exact partially shared carrier graph, changed stage support, native profile, productive credit, or endpoint, followed by its complete invoice. Adding arms or queries while retaining the excluded common-carrier bill does not reopen it.
