# Conditional κ 0.003639042931507 from a residual helper split

This construction improves [#7117](https://github.com/CrocSwap/integer-mult-bounds/pull/7117) by **0.000000100498024**. On its exact native word, one paid rank-five move becomes rank four plus rank one. Two neutral retimings then expose another independent rank-nine helper, which splits into ranks eight and one. The complete paid and productive profiles change; the signed 17-stage caller remains unchanged. The selected frontier is unchanged.

The conditional claim is `3639042931507/1000000000000000`. Both exact price engines reject #7117's invoice at this claim. The independent raw crossing is

```
(0.00363904293150729230234892845394584,
 0.00363904293150729230234892845394585).
```

This is the ceiling for the emitted invoice, with more than 0.9999999999999 of that ceiling realized. The retained BIT cap 0.00376669 leaves 0.000127647068493 headroom, without asserting that it is attainable. The older `complex-local-word-ceiling/ceiling.py` model assumes a hosted nine-stage template and its coverage law; this signed 17-stage caller has independent productive helper targets and does not satisfy those hypotheses. The complete signed-invoice crossing above is the applicable replacement bound, not a global bound on other words or callers.

## Exact edit and full bill

[PROOF.md](PROOF.md) gives the source-specific identity. At source cut 45209, chart 246, paid role 789 moves through the chart and roles 472 and 1359 delay their rank-one exits. Pivot 236 retires there; fresh role 1486 receives an independent arbitrary input. `WITNESS.json` contains all four short rational vectors and all three checked contact-free intervals.

The word adds **24 ADDs, four SCALEs and one net MOVE**. It has 73,628 events, 1,487 public inputs, 1,087 independent helpers and 51 owned labels. All 54 owned lifetimes, peak 43 and 23 rises of mass 56 remain unchanged. Native odd scale 1125 and fractional height 24 are derived afresh from every prefix coefficient and pre-ADD product. Full source-unit ordinary work is **777,622,672 < 10⁹**. Fresh precision gives **c=2338**, context height 405 and mass exponent 1169.

| Complete 17-stage invoice | #7117 | This construction |
|---|---:|---:|
| Paid positions |110672|110689|
| Productive fields |22206|22223|
| Rank surplus |1424|1424|
| Empty-root credits |0|0|

The changes are ΔP={1:+17,4:+17,5:−17} and ΔT={1:+17,8:+17,9:−17}. The native signed gain is H8+H5−H9−H4, strictly positive for H_r=r^(1−κ), 0<κ<1, by concavity. Acceptance also requires the full ordinary, precision and outer gates, which are recomputed.

## Source closure and reproduction

The complete 25-file input export is [#7117](https://github.com/CrocSwap/integer-mult-bounds/pull/7117) at `092255ac8e9ed07ea59fee87c9711a5d72b10750`. Its unchanged nested exports retain #7116, #7115, #7112 and **Rohan Arun's [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)** caller at `07a76c5e2738882c0cb322278e56f6cae3c9885d`, together with their complete predecessor sources and notices. `INPUTS.json` authenticates SHA256 and Git blob IDs before import. The replay reconstructs every source native byte before applying the new edit.

Source native: `954d64194222d5080cfc7ca860e78a59979c825e0c68632f5e4ce75ae496bab8`.

Candidate native: `cbce61015e22007f785474e2af2462a7d97ead1e105d71cd2d9cbc0a449580f3`.

Unchanged literal caller: `255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc`.

```sh
python3.12 -B scripts/research_package.py --package research/p104-funded-residual-split
```

The first command authenticates and reconstructs the source and candidate, checks both arbitrary-input native orientations, derives the grid, and runs the full finite physical native and signed-child checks. It also prices the retained 18-stage ingredient caller; that receipt is distinct from the final 17-stage application. The second command reconstructs both complete 17-stage invoices, emits the unchanged literal caller and freshly checks all affected components. All **3,048 paid/helper chart maps and 104 main boundaries** receive signed-Pauli and absolute-phase checks. Four affected pairs additionally receive all 512 column checks in the native command, including the new 232→246 pair.

Sixteen native corruption controls reject missing paths and corrections, wrong vectors or frames, unpaid subdivisions, incorrect path ranks, illegal contacts and insufficient grids. Phase, owner-alias, caller-grid and BIT controls remain active. Every frozen receipt field is compared. The standard-library replay requires neither Git nor network and rejects optimized Python. `--out UNUSED_PATH` writes a fresh receipt without overwriting a frozen one. [VALIDATION.md](VALIDATION.md) records completed runs and their limits.

## Scope and predecessor credit

[APPLICATION.md](APPLICATION.md) supplies the exact operator, owner/phase, grid, precision, physical upper-cost and fixed-tape substitutions. The five assumptions remain: `native_all_columns`, `owned_erasure`, `compiler`, `precision_tape`, `analytic_recovery`. Owned erasure retains its nonzero-content premise. Independent human/formal review and maintainer admission remain open. No compiled top-level multiplier or global optimum is claimed.

Prepared for dillona with substantial OpenAI Codex assistance; no subagents. Apache-2.0. Credit **Ali Romman** for helper bases and paid meetings; **Jerry Chen/CubeJerry** for retiming and native/invoice/compiler engines; **Matarener** for complete discovery kernels and pairing; **Rohan Arun** for the 17-stage caller and application; **ToikY** and **DreamingOfClouds** for the native/signed lineage; **Douglas Colkitt and the #7000 reviewers** for the selected source-specific proof and BIT ambient-134 repair; and all retained predecessor authors and notices. The preceding dillona/OpenAI Codex #7105/#7107/#7112/#7115/#7116/#7117 contributions remain credited. ToikY's pending chart-120 rank-eight lead is distinct and is not claimed here.

## Open next questions

- Independently review this residual split and full application using the exact source export and registered replay.
- Can a distinct published edit compose with this word? Pin its exact artifact and replay the combined identity and complete costs; adding advertised profile gains is insufficient.

The [canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19520521) records the bounded source change and overlap. `DISCOVERY.json` distinguishes the local nomination search from the public selected witness. No search optimum is asserted.
