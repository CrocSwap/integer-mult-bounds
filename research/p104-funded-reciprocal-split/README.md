# Conditional κ 0.003639143435066 from a reciprocal residual split

This construction improves [#7118](https://github.com/CrocSwap/integer-mult-bounds/pull/7118) by **0.000000100503559**. It verifies a second residual helper mode on that exact changed word. One paid rank-five MOVE becomes ranks four and one; two neutral advances bring the required fields to chart 246. Another independent helper9 target then becomes helper8+helper1. The complete profile changes, with the same signed 17-stage caller. The selected frontier is unchanged.

The exact conditional claim is `1819571717533/500000000000000`. Both price engines reject #7118's invoice at this claim. The independent raw crossing is

```
(0.00363914343506692386360470011163804,
 0.00363914343506692386360470011163805).
```

This is the emitted invoice's ceiling; more than 0.9999999999997 of it is realized. The retained BIT cap 0.00376669 leaves 0.000127546564934 headroom, without asserting that it is attainable. The old `complex-local-word-ceiling/ceiling.py` assumes a hosted nine-stage coverage law. This signed 17-stage caller has independent productive helper targets and lies outside those hypotheses; the complete signed-invoice crossing above is the applicable replacement bound. It does not bound other words or callers.

## Concrete change and complete costs

[PROOF.md](PROOF.md) gives the exact identity. At source cut 44124, chart 246, role 17 pays the rank-five subdivision while roles 789 and 745 advance their rank-four and rank-one moves. Pivot 299 retires; fresh role 1487 receives an independent arbitrary input. The constructor checks all three actual contact-free intervals on #7118. In particular, role 789's move was introduced by the previous split, so its interaction is replayed rather than assumed.

The word adds **26 ADDs, eight SCALEs and one net MOVE**. It has 73,663 events, 1,488 public inputs, 1,088 independent helpers and 51 owned labels. All 54 owned lifetimes, peak 43 and 23 rises of mass 56 remain unchanged. The new exact native grid is 1125/F24. The fresh complete ordinary bound is **777,686,320 <10⁹**, and precision gives **c=2342**, context height 405 and mass exponent 1171.

| Complete 17-stage invoice | #7118 | This construction |
|---|---:|---:|
| Paid positions |110689|110706|
| Productive fields |22223|22240|
| Rank surplus |1424|1424|
| Empty-root credits |0|0|

The deltas are ΔP={1:+17,4:+17,5:−17} and ΔT={1:+17,8:+17,9:−17}. Native signed gain H8+H5−H9−H4 is positive by strict concavity for H_r=r^(1−κ), 0<κ<1. Full ordinary, precision, physical and outer costs are recomputed separately; predecessor gains are not added as decimals.

## Sources and reproduction

`INPUTS.json` authenticates the complete 25-file #7118 export at `3f6ff8c34b22af12b40c5a8bcee585cd1aafdb9c` by SHA256 and Git blob IDs, and preserves all nested sources and notices. Every source native byte is reconstructed before the edit. Source native hash: `cbce61015e22007f785474e2af2462a7d97ead1e105d71cd2d9cbc0a449580f3`. New native hash: `7a45d092b0bf8075e3d00242c72ac897be234e005cbcdfc47d06e9d2967359f0`. The literal caller remains byte-identical to Rohan Arun's #7113 at `07a76c5e2738882c0cb322278e56f6cae3c9885d`, SHA256 `255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc`.

```sh
python3.12 -B scripts/research_package.py --package research/p104-funded-reciprocal-split
```

The first command reconstructs the source and candidate, checks both arbitrary-input native orientations, derives the grid, checks the 18-stage ingredient invoice and runs the complete finite physical native/signed routes. The second command reconstructs both complete 17-stage invoices, emits the unchanged rational/integer Laurent caller and freshly checks the full application. All **3,048 paid/helper maps and 104 main boundaries** receive signed-Pauli/absolute-phase checks; five affected pairs additionally receive all 512 column checks. Sixteen native corruption controls, phase/owner/caller-grid/BIT controls and 54 strict+4 functional outer gates remain active. Every frozen receipt field is compared. [VALIDATION.md](VALIDATION.md) records the completed runs and limits.

The standard-library replay needs neither Git nor network, rejects optimized Python, and writes fresh receipts only through `--out UNUSED_PATH`. The separate 18-stage ingredient receipt is not the final 17-stage claim. [APPLICATION.md](APPLICATION.md) supplies all source-specific operator, owner/phase, grid, precision and fixed-tape substitutions.

## Remaining obligations and credit

The five assumptions remain: `native_all_columns`, `owned_erasure`, `compiler`, `precision_tape`, `analytic_recovery`. Owned erasure retains its nonzero-content premise. Independent human/formal review, maintainer admission and a compiled top-level multiplier are not supplied.

Prepared for dillona with substantial OpenAI Codex assistance; no subagents. Apache-2.0. Credit **Ali Romman** for helper bases and paid meetings; **Jerry Chen/CubeJerry** for retiming and native/invoice/compiler engines; **Matarener** for complete discovery kernels and pairing; **Rohan Arun** for the 17-stage caller/application; **ToikY** and **DreamingOfClouds** for the signed/native lineage; **Douglas Colkitt/#7000 reviewers** for the selected source-specific proof and BIT ambient 134 repair; all earlier dillona/OpenAI Codex contributions through #7118; and all retained source authors/notices. ToikY's pending chart 120 rank 8 lead remains distinct and unclaimed.

## Open next questions

- Independently review the actual interaction with #7118's changed role 789 path and the complete component application.
- Can a distinct published edit compose with this word? Pin and replay its exact identity and full costs; the local search provides no general independence or optimality theorem.

[Canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19520521). `DISCOVERY.json` distinguishes local nomination evidence from the exact public witness.
