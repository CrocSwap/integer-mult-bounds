# Static nomination: #7622 splice against #7623

**Disposition: adapt and requalify; not an unchanged executable port and not an admitted improvement.** The ten source literals survive in #7623 and the local role-902/1091 incident sequence survives, so there is a concrete literal-level nomination. However, the #7622 construction and verifier are bound to a different source, its clocks, 167 lifetimes, evidence and invoice. In particular, requiring #7623's original owned-observation/CLEAR equality is incompatible with carrying over #7622's *previously observed* changed interfaces and owner-1557 erased row without a new, explicit contract. Those previous observations are not themselves a replay result for #7623. This is static inspection, not construction, symbolic replay, execution of imported source, or a gain/admission claim.

Source inspected: #7623 head `2ee2f0b61f7d123e8862482b966699cca578be6d`, local `inputs/pr7623/research/p104-loan-snapshot-engine-on7621` under `outputs/kappa-research-20261116`; #7622's source #7620 head `b1356c84a0733843ce59855f02511c49c6a44133`, its actual generated `outputs/kappa-research-20261115b/compose7620/run/case/built/edit-manifest.json`, `compose7620/build.py:14-49,83-113`, and published `outputs/kappa-research-20261115b/publication/export/research/p104-contact902-1091-on7620/PROOF.md:3-50`. #7623 claims κ 0.0036624027915 under its own stated premises; compare a new complete raw upper, not the rounded displayed number.

## Literal mapping and incident boundary

Static decompression and exact event matching in the bounded window gave the following **zero-based** mappings; each old event had exactly one literal match in the tested ±250/+500 neighborhood. No full semantic correspondence was assumed. New literals/deletions are the #7622 manifest, unchanged as event values:

| #7620 clock | #7623 clock | Original event | #7622 change |
|---:|---:|---|---|
|38486|38582|MOVE 902 3→595|replace 3→373|
|38487|38583|ADD 1532 += 2·902 @595|delete|
|38785|38881|ADD 1479 += −1/2·902 @595|delete|
|38786|38882|ADD 1255 += −1·902 @595|delete|
|38787|38883|ADD 1495 += −3/2·902 @595|delete|
|38788|38884|MOVE 1091 373→618|delete|
|38789|38885|MOVE 902 595→618|delete|
|38790|38886|ADD 1091 += 1/2·902 @618|replace chart with 373|
|38813|38909|MOVE 1091 618→733|replace 618→733 with 373→733|
|41448|41544|MOVE 902 618→913|replace 618→913 with 373→913|

The 19 role-incident literals of `build.py:29-49` also occur in the same order through the first exterior 902 observer. The first boundary maps 37803→37867 (+64); the two incidents 38941→39041 and 38943→39043 map +100; the remaining 16 map +96, ending 41449→41545. This rules out a direct collision with the 14 listed #7623 instances on the specified roles in that incident window; it does **not** prove equality of the rows feeding that window or of downstream effects. Changes in #7623 before the splice and after the first exterior observer remain in the complete dependency graph. The offset is not globally constant: old owner1532 CLEAR 40314→40414 (+100), old owner1557 CLEAR 43229→43314 (+85). Regenerate a validated full origin map; do not apply +96 to a suffix.

The old route change is 902 `3→595→618→913` to `3→373→913`; 1091 `373→618→733` to `373→733`. The predecessor first gate covered 13 derived route pairs and its full application covered 837 union pairs (`PROOF.md:11-13`). #7623 says its 14 side-A instances change 28 other routes and introduce 24 pairs while removing 14 (`README.md:61-84`; `check.py:707-725`). The combined source/candidate/predecessor affected-pair union must be derived and rechecked; neither 13 nor 837 nor #7623's 964 alone proves its coverage. Validate chart bases, strict nesting, phase, signed generators, full forward and adjoint columns and inherited all-width/compiler assumptions.

## Private lifetimes and the contract conflict

#7623's `check.py:679-699,991-1004` requires each old CLEAR content as an ordered subsequence and all 1,018 old owned observations equal after excluding its 13 new lifetimes. Its 13 additional snapshot lifetimes, identified by INIT/CLEAR in its literal edit data and #7623 word, are all finished before the first nominated splice event:

| field @ chart | INIT → CLEAR in #7623 |
|---|---|
|1533 @452|28768 → 34297|
|1534 @413|28816 → 34382|
|1527 @451|28850 → 34379|
|1538 @415|28896 → 35149|
|1551 @416|29323 → 37912|
|1550 @417|29328 → 37923|
|1549 @419|29334 → 37937|
|1548 @420|29338 → 37948|
|1532 @453|29584 → 35077|
|1525 @455|30505 → 33948|
|1533 @433|34468 → 35152|
|1527 @492|34618 → 35562|
|1526 @438|34717 → 35722|

Field labels are reused: the older 1532 lifetime implicated by the splice is INIT 38573 @595 to CLEAR 40414 @529; the later 1557 lifetime is INIT 39974 to CLEAR 43314 @595. The earlier #7622 replay found twelve changed owned scalar interfaces, owner1557's erasure row changed, and regenerated relation coefficients for owners1532 and1557 (`PROOF.md:17-32`). It also required propagation of later 902 feedback and owned1548 read. Whether the corresponding 180-lifetime composition has exactly those differences, additional differences, or failure is **unmeasured**. The 13 new snapshot certificates concern earlier CLEARs and cannot establish later comparison equality; their reused-field lifetimes and all 180 CLEAR/certificate obligations must be distinguished by lifecycle and recomputed. #7623 certificate checking (`check.py:733-754`) verifies algebraic live-row relations, not an implementation of private erasure.

#7622 explicitly assumes the unimplemented common whole-private-extent service U and a common finite tariff for the union of state envelopes (`PROOF.md:44-50`). It covers dirty prior state, complete INIT/CLEAR including numerical residuals and blanks, atomic return, no alias, spectator preservation and all admitted widths/columns. No implication from #7620/#7623 original owned-erasure premise to U is established. Extending U and its finite tariff to the 180-lifetime source/candidate envelopes is a new obligation, including all lifetime, tape, storage and precision costs. Do not describe a hypothetical successful splice as same-original-premise dominance.

## Reuse and decisive next checks

- **#7622 ten-event device: adapt.** Values and route window are plausible; original `build.py` rejects #7623's source shape, pins, clocks and lifecycle (`build.py:11-25,83-93`). Carry predecessor controls, full incident closure, origin mapping, private ownership and resource/error-ordering contracts; no unchanged-script claim.
- **#7622 first-gate exact/rank-one method: adapt, not reuse its old result.** The old entrance `c=e902+e985`, injection and cancellation certificate are specific to #7620. Re-derive the reverse prefix and propagate all interfaces/guards/CLEARs on #7623 under stated U, including new lifetimes, with independent paired literal replay. Preserve the 13-pair controls and full-application independent coverage.
- **#7623 instance engine/checker: review-only for this combined candidate.** It enforces its fixed 14-instance source-to-word construction, 77,196→77,277 length and unchanged old observations/CLEARs (`check.py:975-1017`); its acceptance is not composition acceptance. Its snapshot certificates and checks are useful controls but must be freshly bound and extended to the actual combined candidate.
- **#7622 prior price: not relevant as an acceptance result.** Its signed 110,145→110,111 profile and conditional κ 0.003661727792 apply to its #7620 comparison (`PROOF.md:34-42`). Derive the complete changed native and signed paid profiles from the actual #7623 candidate, independently recompute all costs and strict directed bounds against the complete #7623 upper, and requalify physical/compiler/caller/precision/tape/outer predicates. A local delta or forecast is not a full invoice.

Original acceptance remains a **new full changed paid profile and exact replay** giving conditional κ above the complete #7623 upper, with complete costs and independently reviewable PR. Static compatibility and completed predecessor publications are prerequisites only; no current candidate, gain, implementation of U, independent acceptance, or publication has been established here.
