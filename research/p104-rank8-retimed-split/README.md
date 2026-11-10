# Conditional κ = 0.00363233825: one rank-eight helper split

This changes the complete invoice of [#7105](https://github.com/CrocSwap/integer-mult-bounds/pull/7105), raising its conditional claim from **0.00363216151** to **0.00363233825**, a gain of **0.00000017674**. One paid retiming exposes an independent rank-eight helper direction that splits into ranks three and five. The emitted word adds one MOVE and fourteen integer ADDs. The caller and BIT inputs are the exact predecessor bytes.

This is an author-checked conditional construction, with source-aware reuse of attributed engines. It is not supplier admission, an unconditional multiplication theorem, or a selected-frontier update.

## Exact source and construction

The source is #7105 at public head `92b09a2bd2a8f6f2e0fb502068c1259350c2a8c8`, canonical word SHA256 `10b24ef20650bce0423c66abf5bd43a837e6d5dbe50c9ac973f17eae295ad62b`. Canonical main was refreshed at entry and before submission to `f16923d466a6aba912299882e0545564d2ba7bb2`; priority revision 8 and selected #6030 are unchanged. The exact predecessor package, including its source closure and notices, is archived in `inputs/pr7105.tar`. `INPUTS.json` authenticates every member by size, SHA256 and Git blob. The verifier reconstructs #7004, then #7105, before constructing this successor.

All indices below refer to the source word and are zero-based. Role 533 has no scalar contact in the half-open interval `[37411,39699)`. Its sole event there is `MOVE(533,3,747,false)` at index 38792. Replace it with 3→745→747 at cut 37420, immediately before source event 37420. The spaces strictly nest, with dimensions 0, 3 and 6. This replaces one rank-six payment with two rank-three payments. With chart operator C_f, normalized coordinates C_f^-1 v are unchanged by MOVE. No read or write of role 533 is crossed, so the retiming preserves the normalized scalar operator.

Let P be the full retimed prefix and S its suffix at the intermediate frame 745. The exact row and column vectors are:

| Vector | Nonzero coordinates |
|---|---|
| a | e533ᵀ − 2 e1454ᵀ |
| b | e533 + e1468 − e843 |
| c | e533ᵀ + 4 e1251ᵀ + e1468ᵀ − 2 e1454ᵀ |
| d | e1468 |

The verifier checks `aP=c`, `Sb=d`, and `ab=cd=1` over the rationals, including all other public inputs/outputs and every owned row. Roles 533, 843, 1454 and 1468 are at frame 745 at the cut. The support of c and d belongs entirely to the independent helper group with boundary frames `(3,245)`, of dimensions 0 and 8. The two productive ranks are therefore 3 and 5.

Apply Ali Romman's helper-split criterion with pivot 1468. The boundary basis G has row 1468 equal to c and sends d to e1468. It consists of three ADDs at frame 3: add roles 533, 1251 and 1454 into 1468 with coefficients 1, 4 and −2. The cut basis J has row 1468 equal to a and sends b to e1468. It consists of four ADDs at frame 745:

```
ADD(533,1468,−1), ADD(843,1468,+1),
ADD(1468,533,+1), ADD(1468,1454,−2).
```

Emit G^-1 at the input, J at the cut, and J^-1 followed by the complete suffix using new role 1481 wherever pivot 1468 formerly appeared. Emit G at final frame 245 with the same substitution. The old pivot now returns at 745; the new arbitrary helper starts at 745 and finishes at 245. This is fourteen explicit scalar instructions, with no implicit free basis operation. Owned labels shift by one; their logical lifetimes and rise inventory are preserved.

For completeness, after the input basis, the retained pivot coordinate at the cut is the independent input x1468. Replacing it by fresh input z changes the suffix input along b. Since Sb=d and Gd=e1468, the final boundary basis sends this difference only to the renamed successor output. That output returns z, the retained pivot returns x1468, and all other helper and main outputs remain unchanged. This uses two independent input coordinates; it does not duplicate productive credit from one input. Every correction occurs at one physical chart. The source all-column contract supplies the width lift, while this package checks exact phases and all 512 columns of every affected chart pair.

The complete emitted word has canonical SHA256 `a3bffcd29d5e7040d91a439d2fecfaa17a3c15a373da03099d44fd9c1261622a`.

## Complete accounting and fixed-invoice ceiling

Per LOCAL, the paid delta is `{3:+2,6:−1}` and the target delta is `{3:+1,5:+1,8:−1}`. Across the unchanged eighteen LOCALs, all counts multiply by eighteen. Thus for `0<p=1−κ<1`, the full margin gain is

```
18 (5^p + 6^p − 8^p − 3^p) > 0.
```

Strict concavity proves the inequality: the increment from 3 to 5 exceeds that from 6 to 8. Both rank-three payments are charged; one cancels the rank-three target in this displayed signed difference. This is a changed complete profile, not additional digits of the old root.

The word has 71,273 events, 1,482 public fields (400 main and 1,082 independent helpers), 51 owned labels, 54 owned lifetimes and peak 43. Its 23 owned rises have total mass 56. Complete rank surplus remains 1,520, and no empty-root credit is used. The conservative ordinary bill is **826,799,424 < 10^9**, including helper boundaries, input conversion and the inherited second LAMBDA charge.

Two rational interval engines certify the changed raw crossing. The independent enclosure is

```
(0.00363233825927247587361768759941604,
 0.00363233825927247587361768759941605).
```

The conservative claim is `14529353/4000000000 = 0.00363233825`. Tested price is `0.00363233825007`, compiler gap is `10^-14`, written logarithm power is 2229, and H is `14181100000000000000`. The fixed-invoice headroom above the claim is about `9.27e-12`; its negative derivative bound and exact brackets are in `RESULT.json`. Refining this root alone is not another construction step. The old complete invoice rejects the new claim.

## Verification and reproduction

The full verifier checks source reconstruction, exact cut identities, the complete arbitrary-input adjoint, an independently implemented forward integer-grid replay, the formal paired QUERY-only caller, both complete invoices, ordinary costs, two rational price engines, strictification, input lift, compiler and 54+4 outer inequalities. It reuses the attributed common-grid and rounded-envelope engines, checks the E-free paired BIT artifact binding, and runs the source's relaxed native and full width-512 finite physical replays. Five named chart pairs include the two new pairs 745→245 and 745→747; all 512 columns and absolute phases pass. Wrong phase, cut direction, contact window, deleted cut corrections, wrong successor frame, undersized grids and the new claim on the old invoice reject.

```
python3 -I -B research/p104-rank8-retimed-split/verify.py
python3.12 -B scripts/research_package.py --package research/p104-rank8-retimed-split
```

Expected final line: `PASS_P104_RANK8_RETIMED_SPLIT 14529353/4000000000`.
The standalone scientific command needs no Git or network. Ordinary replay compares every receipt field to `RESULT.json`; `--out UNUSED_PATH` emits a new receipt. Regenerated gzip artifacts are compared by their complete decompressed payload. Optimized mode is deliberately rejected because retained engines use assertions. `VALIDATION.md`, `REPLAY.txt` and `ENVIRONMENT.json` identify the execution evidence and its limits.

The optional discovery screen is separate from the verifier:

```
python3 research/p104-rank8-retimed-split/source.py --output /tmp/source7105.json.gz
python3 research/p104-rank8-retimed-split/discover.py /tmp/source7105.json.gz /tmp/rank8-hits.json 3 245
```

`SCREEN-HITS.json` contains three nominations, not three independent gains. The certificate takes the first with pivot changed from 533 to 1468, reducing the total basis length from ten to seven before inverse copies. Discovery uses floating arithmetic only as a filter; acceptance reconstructs the complete exact candidate. The initial whole-boundary `(3,127)` screen on #7105 found zero hits; its exact script pin, floating threshold and retained log are in `DISCOVERY.json`. That finite failure is not an optimality result. This rank-eight witness does not require claiming that #7105 newly created its entire boundary group.

## Scope and outstanding obligations

The five retained framework assumptions remain: `native_all_columns`, `owned_erasure`, `compiler`, `precision_tape`, and `analytic_recovery`. Retain the source's exact odd-scalar complete child returns, owned movement, hosted/per-port and one-field-idle caller, LAMBDA/ordinary tariff and paired BIT contracts. This edit adds only integer ADDs and no owned ascent. A materialized uniform word or complete rounded multiplier is not supplied.

The new canonical-main [#7000 admission review](https://github.com/CrocSwap/integer-mult-bounds/blob/f16923d466a6aba912299882e0545564d2ba7bb2/docs/research/pr-intake-evidence/pr7000-admission/PROOF-REVIEW.md) repairs BIT working ambient rank to 134 and logarithm power to 617 while preserving the available saving. Our frozen numerical source engines are unchanged and their BIT binding check is not a replay of that supplement or a complete BIT admission proof. That review discharges narrow owned-ascent and LAMBDA clauses for its exact source; it still requires the complete occurrence/interface map, physical upper-cost conversion, storage/root boundary and resulting outer-threshold application. Those outstanding obligations are explicitly retained here. The passing source-unit ordinary bill must not be identified with a literal machine-step count.

## Credit

Prepared for dillona with substantial OpenAI Codex assistance; no subagents. New work is this source-bound rank-eight retiming/split composition, parameterized discovery, choice of a shorter basis, and verification package. Apache-2.0.

Credit Ali Romman for independent-helper basis splitting; Jerry Chen / CubeJerry for counted inventories, paid retiming, shared wires, #7000 composition, paired BIT/caller and precision engines; DreamingOfClouds for #6931/#6936/#6937 and the native chain; ToikY for #7003/#7004; and #7105 for the immediate source and reusable source-bound replay. Retain the original notices and attribution to Cinna Davis, Pierre-Loic Doulcet, Mason Hale, Jacob Alan Sussman, zxv, thu-nmrc and all credited native/compiler/precision/analytic authors. Separate algorithmic implementations here are not independent human or kernel review.

## Open next questions

- Can the other two rank-eight nominations compose with this split? Recompute exact capacity on the emitted successor and price the joint corrections; overlapping boundary vectors prevent assuming independence.
- Can the exact source be admitted under the retained framework with an explicit physical upper-cost conversion? Start from the #7000 review's occurrence/interface and corrected BIT geometry requirements; finite replay leaves those supplier obligations open.

Structured questions and blockers are in `TASK.json`. The canonical [investigation post](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19520521) records the expansion decision, source pins, overlap coverage and final artifact. Existing frozen packages and the selected result remain unchanged.
