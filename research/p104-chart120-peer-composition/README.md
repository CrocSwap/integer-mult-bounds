# Conditional κ 0.003639264106282 by composing ToikY's chart-120 pattern

**ToikY reported the chart-120 pattern** in [Discussion #7111](https://github.com/CrocSwap/integer-mult-bounds/discussions/7111): split a productive rank-eight helper into four plus four, while charging a paid rank-seven subdivision into four plus three. This package independently constructs and fully checks that pattern on exact **#7119**, improving its complete conditional claim by **0.000000120671216**. The peer's original #7115 artifact remains local-only and is not imported here. [PEER-CREDIT.json](PEER-CREDIT.json) records the finding and attribution.

The exact claim is `1819632053141/500000000000000`. Both price engines reject #7119's invoice at this claim. The independent raw crossing is

```
(0.00363926410628203626930823372185618,
 0.00363926410628203626930823372185619).
```

This is the emitted invoice's ceiling, with more than 0.9999999999999 realized. The retained BIT cap 0.00376669 leaves 0.000127425893718 headroom, without asserting attainability. The old `complex-local-word-ceiling/ceiling.py` hosted nine-stage coverage law does not apply to this signed 17-stage caller with independent productive helper targets; the complete signed-invoice crossing is the applicable replacement bound. It does not bound other words or callers. The selected frontier is unchanged.

## Exact composition and full costs

At source cut 39058, public role 962's rank-seven move 597→207 is subdivided through chart 120 into ranks 4+3. Its full contact-free interval is [39055,39094). Helper 1447, in boundary group 597→127, retires at 120; fresh role 1488 starts there with an independent arbitrary input. The boundary basis is identity. The middle basis has four unit-coefficient ADDs, given explicitly in [PROOF.md](PROOF.md); its inverse supplies four more.

The new word adds **eight ADDs and one net MOVE**, has 73,672 events, 1,489 public inputs, 1,089 independent helpers and 51 owned labels. All 54 owned lifetimes, peak 43 and 23 rises of mass 56 remain unchanged. The exact native grid remains 1125/F24. Full ordinary work is **777,741,264 <10⁹**. Fresh precision gives **c=2342**, height 405 and mass exponent 1171. The regenerated compiler gate uses gap `1/1000000000000000000` and H=`172444000000000000000000`; every affected outer/fixed-tape bound uses those new values.

| Complete 17-stage invoice | #7119 | This construction |
|---|---:|---:|
| Paid positions |110706|110723|
| Productive fields |22240|22257|
| Rank surplus |1424|1424|
| Empty-root credits |0|0|

The exact deltas are ΔP={3:+17,4:+17,7:−17} and ΔT={4:+34,8:−17}. With H_r=r^(1−κ), native signed gain H4+H7−H8−H3 is positive by strict concavity for 0<κ<1. The full ordinary, precision, physical and outer obligations are checked separately.

## Frozen sources and reproduction

`INPUTS.json` authenticates the complete 25-file #7119 export at `bd244b0e5034cb1b9f72641494c3421f757ec2e4` by SHA256 and Git blob IDs, preserving all nested sources and notices. Every source native byte is reconstructed. Source hash: `7a45d092b0bf8075e3d00242c72ac897be234e005cbcdfc47d06e9d2967359f0`. New native hash: `4f19c6ee57b74d7c3ea1863df0b33fe275a3a7511f77084f05726ee216ebdc34`. Rohan Arun's #7113 signed 17-stage caller remains byte-identical, SHA256 `255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc`, from exact head `07a76c5e2738882c0cb322278e56f6cae3c9885d`.

```sh
python3.12 -B scripts/research_package.py --package research/p104-chart120-peer-composition
```

The first command checks source/candidate reconstruction, arbitrary-input forward and adjoint, declared path/target deltas, grid, the 18-stage ingredient invoice/precision and complete finite native/signed routes. Its ingredient claim is separate from the final 17-stage result. The second command reconstructs both complete 17-stage invoices, emits the unchanged rational/integer Laurent caller and rechecks the complete application. All **3,049 paid/helper maps and 104 main boundaries** receive signed-Pauli/absolute-phase checks; five affected maps additionally receive all 512 column checks. Fourteen native corruption controls, owner/phase/caller-grid/BIT controls and 54 strict + 4 functional outer conditions remain active. Every frozen receipt field is compared.

The standard-library replay requires neither Git nor network, rejects optimized Python, and writes a fresh receipt only with `--out UNUSED_PATH`. [VALIDATION.md](VALIDATION.md) records completed runs. [APPLICATION.md](APPLICATION.md) supplies the exact operator, ownership, common-grid, precision and physical fixed-tape substitutions. The peer finding is credited provenance, not a runtime input or imported correctness receipt.

## Obligations and predecessor credit

The five assumptions remain: `native_all_columns`, `owned_erasure`, `compiler`, `precision_tape`, `analytic_recovery`. Owned erasure retains its nonzero-content premise. Independent human/formal review, maintainer admission and compiled top-level execution remain open.

Credit **ToikY** for the reported chart-120 pattern; **Ali Romman** for helper bases/paid meetings; **Jerry Chen/CubeJerry** for retiming and native/invoice/compiler engines; **Matarener** for complete discovery kernels/pairing; **Rohan Arun** for the 17-stage caller/application; **DreamingOfClouds**, **Douglas Colkitt/#7000 reviewers**, the earlier dillona/OpenAI Codex chain through #7119, and every retained source author/notice. This exact current-source composition was prepared for dillona with substantial OpenAI Codex assistance; no subagents. Apache-2.0.

## Open next questions

- Independently review the emitted composition and full application using its exact source export and registered replay.
- When ToikY's original artifact becomes public, pin and compare its word, witness and source. Matching profiles alone do not establish identical circuits or transfer verification.

The [canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19520521) and peer reply record the distinct scope. `DISCOVERY.json` labels the local nomination evidence; no search optimum is claimed.
