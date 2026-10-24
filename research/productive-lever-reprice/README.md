# The #1240 lever table, re-priced on the productive-helper invoices

**Side result, no new κ.** [Priority revision 7](../../docs/research/current-priorities.md)
notes that its allocation and lever budgets predate the productive-helper
selection (#4359) and have not been reassessed. The one-at-a-time lever table
from [#1240](../complex-local-word-ceiling/README.md) (`levers.py`: centre free
2.80×, rank-16 children 2.31×, two unpaid coordinates 3.77×, combined 6.5×) was
computed on the old #1094 word. This package recomputes the same kind of ideal
budgets on the current complete invoices:

- complex: [#4470](../joint-helper-lattice/README.md) `RESULT.json` (κ = 0.00302015);
- BIT: [query-thinned-controllers](../query-thinned-controllers/README.md) `bit_invoice`,
  which #4470 retains unchanged.

The model is #4470's own fixed-profile root: a supplier's raw saving `C` solves
`Σ T_r r^(1−C) = Σ P_r r^(1−C)` over its complete target and paid profiles.
Every lever is an **ideal relaxation**: the named work is removed or merged and
nothing new is charged. Outer rows, strictification, tails and the BIT ordinary
conversion are not recomputed, so every figure is a raw ceiling, not a gain.

## 1. Where the paid moment goes

| Paid part | complex jobs | complex mass | complex share | BIT jobs | BIT mass | BIT share |
|---|---:|---:|---:|---:|---:|---:|
| whole-idle stages | 3,360 | 141,568 | **58.97%** | 3,330 | 122,766 | **56.38%** |
| small local jobs (18 full calls) | 59,436 | 94,734 | **39.84%** | 52,560 | 92,322 | **42.84%** |
| query-only shears (one rank-one job per port) | 1,680 | 1,680 | 0.71% | 1,665 | 1,665 | 0.77% |
| owned centre (rank 8) | 144 | 1,152 | 0.48% | — | — | — |

Both sides have the same shape and the same thin margin: target minus paid rank
mass is 752 (complex, `48·18 − 112`) and 753 (BIT). The owned centre, the
largest lever on the old word, is now under half a percent of the bill.

## 2. Ideal lever ceilings

Certified raw roots (brackets of width 1e-10 in `RESULT.json`):

| Lever (ideal) | old (#1240) | complex root | ×base | BIT raw root | ×base |
|---|---:|---:|---:|---:|---:|
| baseline | — | 0.0030201660 | 1 | 0.0034642490 | 1 |
| centre path free | 2.80× | 0.0076503 | 2.53 | n/a (no centre) | — |
| centre shared by two calls | 1.90× | 0.0053347 | 1.77 | n/a | — |
| rank-16 local children (small local jobs merged at equal mass) | 2.31× | 0.0173942 | 5.76 | 0.0332377 | 9.60 |
| two unpaid coordinates per idle family (each whole-idle job 2 ranks cheaper) | 3.77× | 0.0282012 | 9.34 | 0.0318657 | 9.20 |
| centre free and rank-16 children | 6.5× | 0.0478100 | 15.83 | 0.0332377 | 9.60 |
| query-only shears free | — | 0.0099146 | 3.28 | 0.0113100 | 3.27 |
| no rank-one local jobs (merged pairwise into rank 2) | — | 0.0034041 | 1.13 | 0.0037510 | 1.08 |
| whole-idle stages free | — | > 1/6 | — | > 1/6 | — |

"Two unpaid coordinates per family" has no literal counterpart in the new
invoice. The row above is one reading (each idle family pays two fewer ranks)
and should be taken as such.

## 3. What follows

1. **One-sided levers stop at the other side.** κ is limited by
   `min(complex, BIT)`. Any lever on the complex side alone is capped by the
   admitted BIT 0.0034 (+12.6% over 0.00302015); a BIT-only lever leaves complex
   binding. Every lever that matters must be built on both suppliers.
2. **Applied symmetrically, complex still binds** in every row of the table.
3. **The margin is thin, so mass matters more than shape.** Complex reaches the
   BIT level with about 94 units of paid moment removed (0.04% of 237,321), and
   0.005 / 0.01 with about 488 / 1,700. But the surplus `48·18 − 112` is set by the
   controller; repacking at fixed rank mass is weak, since pairing every one of
   the 40,266 complex rank-one local jobs only reaches 0.003404.
4. **The bill is in the controller.** Whole-idle stages (56–59%) and the 15
   query-only shears are fixed by the p16 controller of #4440/#4470, not by the
   local word, and #4546/#4567/#4581/#4585/#4587 already close local window
   rewrites of #4470. Controller-level changes on both sides are therefore the
   targets this screen points to. A companion package examines the query shears.

## Scope

Raw fixed-profile roots only. The levers are hypothetical; none is claimed to
be constructible, and costs that a real construction would add are not
charged. The root bisection proposes the first sign change and exact interval
moments certify the bracket; uniqueness is not certified (the rank-16 BIT case
turns positive again before C = 1). No selected-record change is proposed.

## Open next questions

- Can a changed controller reduce whole-idle mass or the 15 query-only shears on
  both suppliers at once? Screen any candidate with this verifier's `assemble`
  and `root` on both invoices before building it. No changed topology is known,
  and local window rewrites of #4470 are already closed (#4567, #4581).

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/productive-lever-reprice
```

The verifier is standard library only. Prepared by
Matarener (Mark) with Claude Code assistance. Apache-2.0.
