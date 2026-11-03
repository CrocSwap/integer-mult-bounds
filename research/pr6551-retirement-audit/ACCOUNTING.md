# Independent accounting of the retirement tree rebalance

At candidate PR6551 head `11ca568cd1a16776ade02b4df09ea04a784cc674`, relative to predecessor PR6545 head `775722aa94a5e85b05d1d704d7dca10cbf016f0c`, direct counts of the literal callers give

```
ΔT = −104 H16 + 104 H40 + 208 H41 − 208 H57,
ΔP = −104 H16 + 312 H40 − 208 H56,
Δ(T−P) = 208[(H41−H40) − (H57−H56)].
```

The caller counts agree with the predecessor's claimed change. The checker does not import or execute either author's invoice, pricing, constructor, native or caller code, and does not read their RESULT.json files. The first direct event/endpoint count was derived before reading the candidate proof's complete signed invoice. The written physical semantics and literal data are shared inputs; this is independent accounting implementation, not independent derivation of the native tariff.

## Two representations and the exact count

For one port, a declared endpoint `q^a ∏ D_s` has positive Gaussian rank `|a|+8·#{s}` in this caller. There are no stage-zero targets. The central exponent −1 is normalized by an ordinary q² translation; zero means no central axis. Each binary whole IDLE pays for two jobs of rank eight times its stage-set cardinality, IDLE_ONE pays one, and QUERY pays one rank-one job. Each LOCAL expands into the shared native subprogram.

The checker first traverses every literal child tree, assigning the eighteen fresh stages to leaves. It obtains internal-node sizes `{2:8,3:2,4:2,7:2}` before and `{2:8,3:2,4:2,5:1,7:1}` after. The entire root outside `children` and `child_sizes` is identical. The first two children retain sizes seven and two; C,D change from two,seven to five,four. The masks AB and CD still contain nine stages.

The root-mask count, the two productive outputs of every internal node, and the independent retirement split give an expected histogram. It must equal a separate count of all 35 serialized endpoint rows. The checker also verifies the actual retired field 4 and fresh suffix field 34, so exchanging their targets cannot hide behind an unchanged histogram.

Separately, all literal events are classified. The fourteen binary IDLE stage sets must equal the actual tree-node stage sets, including multiplicity. The two IDLE_ONE stage sets must equal children B and C. All seventeen binary/root thin queries and all eighteen ordered LOCAL stage calls must be present. Unrecognized event kinds fail. Q_POWER exponents must be ±2, the inherited ordinary translation case.

Per port, excluding the identical native contribution:

| Rank | Old productive | New productive | Old paid | New paid |
|---|---:|---:|---:|---:|
| 1 | 2 | 2 | 17 | 17 |
| 16 | 1 | 0 | 18 | 17 |
| 17 | 17 | 17 | 0 | 0 |
| 24 | 0 | 0 | 4 | 4 |
| 25 | 4 | 4 | 0 | 0 |
| 32 | 0 | 0 | 4 | 4 |
| 33 | 4 | 4 | 0 | 0 |
| 40 | 0 | 1 | 0 | 3 |
| 41 | 0 | 2 | 0 | 0 |
| 56 | 0 | 0 | 4 | 2 |
| 57 | 4 | 2 | 0 | 0 |
| 73 | 2 | 2 | 0 | 0 |
| 145 | 1 | 1 | 0 | 0 |

The rank-40 paid coefficient three consists of two binary-node idles and the third child's additional root idle. Dropping that last job would produce a false improvement.

The exact retained native archive contains 104 distinct ports, 770 public fields (562 productive helpers plus 208 main fields), and 3,456 MOVE events. The candidate source archive contains a native archive whose SHA256 matches the independently obtained exact PR6545 native archive, plus byte-identical copies of the predecessor caller and retirement witness; its external WITNESS.json is also identical. There are eighteen native invocations in both callers. Thus the common native paid and helper terms cancel. On the retained structural contract, both complete invoices have 13,756 productive fields and 67,096 paid jobs. Both target and paid rank mass change by −832; their difference is unchanged. Two extra Q_POWER translations are explicitly reported as ordinary events, rather than silently dropped from the event inventory.

## Strict gain for every 0<t<1

Set H_r=r^t. For 0<t<1, `f'(x)=t x^(t−1)` is strictly decreasing on positive x. For every s in [0,1], `f'(40+s)>f'(56+s)`. Integrating gives `41^t−40^t > 57^t−56^t`. Multiplication by 208 proves strict positive Δ(T−P). The difference is zero at t=0 and t=1; neither endpoint is claimed strictly positive. This proof establishes a complete recursive Gaussian invoice improvement in the retained model, not the new numerical κ or physical supplier admission.

## Evidence and controls

`accounting.py` is standard-library Python and has seven input-sensitive rejection controls:

- Delete the third child's extra whole idle.
- Give the fresh suffix an unearned central Gaussian factor.
- Delete a fresh stage from that suffix target.
- Delete one rank-one query.
- Delete one native invocation, invalidating cancellation.
- Replace an ordinary Q² translation with a paid odd Gaussian exponent.
- Exchange the retired/fresh field targets, preserving their histogram but violating their interface.

Both actual sources are positive fixtures. Normal and optimized Python 3.12.14 executions passed with byte-identical JSON. Measured subprocess times were approximately 0.08 s and 0.21 s; maximum child RSS was below 35 MiB. Exact commands, status and timings are in `evidence/accounting-normal-run.json` and `evidence/accounting-optimized-run.json`; the deterministic scientific result is `RESULT.json` (the accounting subsection in this integrated package).

From a checkout with the frozen directories staged under the indicated paths:

```sh
python -I -B accounting.py --predecessor PATH/gaussian-root-retirement --candidate PATH/retirement-rebalanced-query-tree
python -I -O -B accounting.py --predecessor PATH/gaussian-root-retirement --candidate PATH/retirement-rebalanced-query-tree
```

## Exact dependencies and limits

Runtime reads:

- Predecessor: `CONTROLLER.json`, `WITNESS.json`. The native archive is read in memory from the candidate's exact retained `source.tar`, and its independently observed predecessor SHA256 is checked.
- Candidate: `CONTROLLER.json`, `ROOT.json`, `WITNESS.json`, `source.tar`.
- Nested old ROOT: `native-source.tar!research/p104-scaled-transport-fusion/source.tar!research/p104-third-anchor-clean-mixed-root/root-source.tar!research/mixed-projector-query-root/ROOT.json`.
- Nested native word: `native-source.tar!research/p104-scaled-transport-fusion/WORD.json.gz`.

No archive paths are extracted. Source-pin authentication should surround this checker in the integrated package. The native archive is checked against the independently observed predecessor hash; the other reported SHA256 values identify bytes actually read and need the integrated source pins to bind GitHub heads.

The caller identity is a separate obligation: this checker assumes the physical meaning of the serialized endpoint rows, and checks accounting/interface consistency rather than proving those endpoints from gate composition. It does not replay native phase maps, verify the retirement prefix/dual-pair identity, prove arbitrary-input restoration, certify the numerical root, validate changed completion decay, implement a uniform compiler, price total ordinary work, or resolve any of the five framework assumptions. Those obligations must remain separately labelled even if this delta check passes.

Credit Ali Romman for PR6551 and PR6545, the PR6398 mixed-root and PR6529 native-source lineage, and all inherited source notices. This independent accounting implementation and explanation were prepared for DLamdata with substantial OpenAI Codex assistance. Apache-2.0; no independent human or proof-kernel verification is claimed.
