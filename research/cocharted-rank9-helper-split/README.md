# Cocharted rank-nine helper split on the signed certificate

Conditional κ = **0.003636447857731** versus **0.003635479112372** in [#7109](https://github.com/CrocSwap/integer-mult-bounds/pull/7109) at head `ae3f9d6a944ade32267fe5a94af853914a99d6aa`. The absolute gain is exactly `968745359/10^15 = 0.000000968745359`. The relative gain is exactly `(24218633975/908869778093)%`, approximately `0.026646979093%`. The independent directed interval for the new complex crossing is

```text
(0.00363644785773120955770150093800963,
 0.00363644785773120955770150093800964)
```

The previous upper endpoint is `0.00363547911237276261060913791895827`. The paired E-free BIT pin remains `0.00376669`.

## Exact construction

Helper 1285 crosses from chart 3 to chart 127. Before source event 35903 it is already in chart 117. Retain 1285 with boundary 3→117 and give fresh helper 1482 the boundary 117→127. These ranks are five and four. The emitter shifts owned labels by one, rebinds ten suffix contacts, and adds twelve scalar events. The normalized word has 71,265 events, 1,483 public fields, and SHA-256 `3d500210240a340b865e2df8ce93cd53ad797537c1f6297508d2bd6a9b863d78`.

For the normalized prefix P and suffix S, the witness checks

```text
a = -2e1285* - 2e1286* + 2e1287* + e1289*
b = -e1285/2
c = 2e1285* - 2e1286*
d = e1285/2
aP = c, Sb = d, ab = cd = 1
```

The boundary basis G has pivot row c and Gd = e1285. The cut basis J has pivot row a and Jb = e1285. Both pivot axes of the old endpoint T = SP are identity and `(c−e1285*)T = c−e1285*`, so GT = TG. Freezing the pivot after J retains the old input. Rebinding the suffix to fresh input z adds `(z−x1285)b` to the normalized cut state. The suffix and output basis send that difference only to the successor. The proof holds on every chart column.

The complete paid profile P is unchanged. The productive profile changes by +18 at rank four, +18 at rank five, and −18 at rank nine. Its signed moment gain is strictly positive by concavity. The rank surplus remains 1,520 and there are zero empty root credits. The signed caller is unchanged.

## Clean replay

```sh
python3.12 -B scripts/research_package.py --package research/cocharted-rank9-helper-split
```

The archive rebuilds the #7109 predecessor and emits the candidate from the exact witness. Replay checks the complete normalized endpoints independently, the physical endpoint probe, both changed maps on all 512 columns with wrong-phase controls, the signed caller and its 32 physical requests, the common grid, modeled ordinary work, the attributed precision envelope, and two directed price engines. The predecessor rejects the new claim and a corrupted scalar fails reverse replay.

The same native all-column, owned ascent and erasure, uniform compiler, exact child, precision and fixed-tape, analytic recovery, LAMBDA, one-field idle, per-port caller, paired BIT and modeled ordinary tariff premises apply. The physical fixed-tape realization, total rounded provider and #6998 tariff bridge remain open.

Credit to the #7109 and #7107 lineages, Ali Romman and CubeJerry for the helper-split construction, and the signed-caller and P104 contributors. OpenAI Codex assisted discovery, construction and verification.

## Open next questions

Can the fixed-tape provider and common-volume tariff bridge be certified on the retained source contract? The next source-bound check is to reconcile the #6998 conversion and A6 trace under one tape width model.
