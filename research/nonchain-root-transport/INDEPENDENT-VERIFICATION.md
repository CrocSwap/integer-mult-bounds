# Independent mixed transport audit

Jerry Chen / @CubeJerry, with substantial OpenAI assistance. Apache-2.0.
The root and pricing retain the authorship in their pinned source files, including DreamingOfClouds with Claude Opus 5.5 and the credited native/caller lineage.

## Outcome and reproduction

**PASS. No discrepancy found.** The checker imports no model, primary verifier, numerical library or predecessor code. It independently checks finite algebra and complete signed budgets at the single rational value `C = 6743600951/2000000000000 = 0.0033718004755`.

- `independent_audit.py`: portable standard-library checker; all guards remain active under `-O`.
- The optional `--output PATH` report includes every explicit nullspace basis and pairing matrix.
- `independent-audit-summary.json`: compact report omitting only the interval basis records.

```sh
python -I -O -B research/nonchain-root-transport/independent_audit.py --package research/nonchain-root-transport --native-word research/nonchain-root-transport/retained/WORD.json.gz --output /tmp/transport-audit-report.json
```

`--native-word` is optional. Without it, the transport and power/dual checks still run and authenticate the retained inputs, but do not recount the native word. With it, the native census is independently reconstructed. The complete author-side run with controls passed in **13.63 seconds** and writes only the optional report; runtime is diagnostic.

The independent implementation was prepared by a separate OpenAI GPT-6 Astra Pro agent for Jerry Chen / @CubeJerry. The package integration changes only a monotonicity comment from restricting to enlarging an interval; no audit algorithm was changed. This is independent AI-assisted implementation, not human or upstream acceptance.

The root source is #6833 at `51f54e3c31f2f3a3e056a483b3ed66ae916ad06a`; retained SHA256 and Git blob pins are checked. Source pins moved from `SOURCES.json` to `retained/SOURCE-PINS.json` during integration; both layouts are supported. The package retains the original byte-pinned #6835 compressed native export for the registered census run.

## Interval capacities from explicit bases

The checker directly reconstructs all 21 query columns and rows from formulas in `retained/chain_root.py`, checks all 441 sign-Gram entries, and constructs each mask from its declared `(p,q)` rule.

For every interval it intersects the covered masks, includes every intervening query (including all bridge queries), and constructs a complete rational basis of the primal kernel and of the dual annihilator. It then computes the matrix of every dual/primal basis pairing and takes its exact rank. **The four-rank formula is never used.** Every basis vector is checked against its equations and basis independence is checked separately. Full bases in original field coordinates are retained in the report.

| Masks | Intervals | Sum of capacities | Positive capacities | Nonzero primal/dual spaces, zero pairing |
|---|---:|---:|---:|---:|
| Original `(0,0)` | 171 | 240 | 72 | 2 |
| `(1,2)` | 171 | 452 | 128 | 2 |
| `(4,4)` | 171 | 530 | 107 | 12 |

All **342 modified capacities**, plus **171 baseline capacities**, were independently reconstructed. Every one of the 81 original bridge-crossing intervals has zero capacity. The `(1,2)` interval `[1,15]` has capacity two; `(4,4)` interval `[4,13]` has capacity six.

Worker B subsequently compared every primary capacity against these independent records: **zero mismatches across all 513 intervals**, with identical key sets.

## Independent rational power enclosure and dual bills

This implementation uses a different enclosure from the primary verifier. For `0 <= z <= 1/2`, it bounds `-log(1-z)` with 120 terms of the positive series `sum(z^j/j)` and tail `z^(N+1)/((N+1)(1-z))`. It splits `log(r)=k log(2)+log(r/2^k)` so both arguments lie in that range. It bounds `exp(a)` by 20 positive Taylor terms, with a geometric bound on the omitted positive tail, then takes reciprocal bounds on `r/exp(C log(r))`. All proof-relevant arithmetic is rational; decimal output is rounded outward by integer division.

All **342 dual column inequalities** pass. Both certificates have minimum certified column slack greater than `0.000000027785146283758790091`.

| Masks | Exact idle-cost lower bound | Complete gain upper bound |
|---|---:|---:|
| `(4,4)` | `44185630669/50000000` = `883.71261338` | `-68.128920094767976716833715137` |
| `(1,2)` | `18743025909/25000000` = `749.72103636` | `-36.778560699518815455526506563` |

The bounds include eighteen native productive and paid profiles, all twenty outer targets, and all three thin-query debits. They agree with the primary report and are slightly tighter due to the smaller enclosure remainder.

Independent complete gain intervals:

- Source: `[-0.000000000734152088876528993, -0.000000000734152088876528992]`.
- Explicit mixed construction: `[-45.137633381995713388652988842, -45.137633381995713388652988841]`.

## Literal first-stage whole-idle execution

All 18 idle projectors were reconstructed from the displayed formulas. The checker verifies their support, annihilation of every covered query, and mutual dual orthogonality at every overlap. It reconstructs all 18 native active projectors, verifying idempotence, rank two, and the native query column and row identities. Every ordinary basis and its full inverse is independently recomputed: both are integral with maximum numerator bit length **two**.

The complete 21-query word is literally executed twice, at `S=+1` and `S=-1`, with 18 distinct nontrivial stage multipliers:

`2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61`.

At each full stage the native active factor is applied. Each whole idle factor, with the product of all its covered stage multipliers, executes **once at its first covered stage**. The resulting full matrix agrees with the expected diagonal target on **all twenty independent input columns**, at both signs. Exact execution stages and multipliers for all jobs are recorded.

The three mask systems also pass literal ungrouped-stage replay at both signs and on every column. These finite `D_i` specializations supplement exact projector and commutation checks; they are not called a formal polynomial verification for arbitrary stage variables.

## Native census, controls and limits

The optional native word has payload SHA256 `d3ccfce7bdbca3b79771844e6c9fee48f1a8066444a19218995648df96982821`. Independent boundary-rank and all-MOVE counts give **564 helpers** and **3,456 paid MOVEs**, with histograms identical to the retained `HELPERS` and `LOCAL_PAID` constants. This is a census check, not a native phase or compiler replay.

Controls pass under `-I -O -B`:

- Nonzero primal and dual nullspaces with zero pairing rank are distinguished.
- The unchanged source left idle fails on the right arm.
- The rank-one power enclosure is exactly `[1,1]`.
- Deleting a mixed carrier's dual hub coefficient is rejected by a query check.
- Omitting one whole crossing idle, while leaving active planes intact, is rejected by the **literal complete endpoint**.
- Inflating a dual variable is rejected by a column inequality.

This audit supports only the declared finite algebra and complete signed bills at fixed `C`. It gives no new kappa, arbitrary-mask barrier, or native/compiler/precision-tape/analytic-recovery theorem.
