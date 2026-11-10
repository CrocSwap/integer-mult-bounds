# Conditional κ 0.003640102187396 from a newly available rank-eight split

The paid helper lowering in #7117 changed role 231’s target to chart 246. On exact **#7120**, that permits a common boundary basis with roles 449 and 707 and a new **rank 8→3+5 split with the entire paid profile unchanged**. The complete conditional claim is **0.003640102187396**, gain **0.000000838081114** over #7120. Added scalar work and every changed caller/physical/precision cost are charged.

At source cut 31847/chart 259/pivot 231, the exact witness is a=e448ᵀ, b=e448+e1205/16−e995/16, c=e231ᵀ−4e707ᵀ, d=e449/8−e707/4. The full prefix/suffix checks establish aP=c, Sb=d and ab=cd=1. The boundary/cut bases have 7/6 instructions. [PROOF.md](PROOF.md) gives the arbitrary-input replacement argument. No retiming is needed. The emitted word adds **20 ADDs + 6 SCALEs**, no MOVEs, and one independent helper.

| Complete signed 17-stage application | #7120 | This construction |
|---|---:|---:|
| Paid positions |110723|110723|
| Productive fields |22257|22274|
| Rank surplus |1424|1424|
| Empty-root credits |0|0|

ΔP={} and ΔT={3:+17,5:+17,8:−17}. Native signed gain H3+H5−H8 is strictly positive for 0<κ<1. The new word has 73,698 events, 1,490 public inputs and 1,090 independent helpers; all 54 owned lifetimes, peak 43 and 23 rises of mass 56 remain unchanged. Ordinary work is **777,785,464<10⁹**. Fresh precision gives height 405, mass exponent 1172 and **c=2344**. Native grid 1125/F24 and caller grid 675 are derived separately and charged together. Regenerated gates use gap `1/100000000000000000` and H=`16487800000000000000000`.

Both exact engines reject #7120’s invoice at the new claim. The independent raw crossing is

```
(0.00364010218739649072410851912941669,
 0.0036401021873964907241085191294167).
```

This is the emitted invoice’s ceiling, with more than 0.9999999999998 realized. The retained BIT cap 0.00376669 leaves 0.000126587812604 headroom, without asserting attainability. The old hosted nine-stage `complex-local-word-ceiling/ceiling.py` coverage law does not apply to this signed 17-stage caller with independent helper targets. The complete signed-invoice crossing is the applicable bound for this word/caller; it does not bound other constructions. Selected #7000 remains unchanged.

## Frozen sources and reproduction

`INPUTS.json` authenticates the complete 26-file #7120 export at `b3d68cf1db9bf493ded2d8f4cb922939edc0ef95`, retaining every nested source and notice. Every source native byte is reconstructed. Source SHA256: `4f19c6ee57b74d7c3ea1863df0b33fe275a3a7511f77084f05726ee216ebdc34`. New native SHA256: `0a27f1224fdb196602d52d4170bc12b8bde0b9818809e73ecdbdaaa5d3b7adbc`. Rohan Arun’s #7113 signed 17-stage caller remains byte-identical, SHA256 `255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc`, from head `07a76c5e2738882c0cb322278e56f6cae3c9885d`.

```sh
python3.12 -B scripts/research_package.py --package research/p104-unlocked-rank8-split
```

The first command checks source/candidate reconstruction, exact arbitrary-input forward/adjoint, declared target/paid deltas, fresh grid, the separate 18-stage ingredient invoice/precision, three 512-column chart maps and full finite native/signed routes. The second reconstructs both complete 17-stage invoices and the unchanged rational/integer Laurent caller, then checks the source-specific application. All **3,050 paid/helper maps and 104 main boundaries** receive exact signed-Pauli/absolute-phase checks. Fifteen native corruption controls, owner/grid/phase/BIT controls, a crossing-probe rejection and 54 strict+4 functional outer conditions remain active. Every frozen receipt field is compared.

The standard-library replay needs neither Git nor network, rejects optimized Python, and writes a fresh receipt only with `--out UNUSED_PATH`. [VALIDATION.md](VALIDATION.md) records completed runs and [APPLICATION.md](APPLICATION.md) supplies the complete physical, ownership, grid, precision and fixed-tape substitutions. `DISCOVERY.json` labels the finite local nomination evidence; only the selected witness was constructed, with no exhaustive rational cost optimum claimed.

## Remaining obligations and credit

The five assumptions remain: `native_all_columns`, `owned_erasure`, `compiler`, `precision_tape`, `analytic_recovery`. Owned erasure retains its nonzero-content premise. Independent human/formal review, maintainer admission and compiled top-level execution remain open.

Credit **Ali Romman** for helper bases and the split identity; **Jerry Chen/CubeJerry** for causal/native/invoice/compiler tools; **Matarener** for complete discovery kernels/pairing; **Rohan Arun** for the 17-stage caller/application; **ToikY** for the retained chart 120 pattern and signed predecessors; **DreamingOfClouds**, **Douglas Colkitt/#7000 reviewers**, the preceding dillona/OpenAI Codex chain and all retained notices. This exact current-source construction was prepared for dillona with substantial OpenAI Codex assistance; no subagents. Apache-2.0.

## Open next questions

- Independently review this exact native and complete application with its source export and registered replay.
- After a fresh upstream/overlap checkpoint, test whether subsequent changed helper endpoints support another fully priced construction; no further gain is established here.

[Canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19520521).
