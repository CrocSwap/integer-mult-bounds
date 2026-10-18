# Packing ceiling and target budget for the selected complex local word

**Scoped obstruction and planning tool. No new κ; the selected record is unchanged.**

The selected complex supplier (#1094) fixes a local word with this paid profile per call:
`{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}`, local mass 5,586. Everything else in the record is
idle-remainder packing on 896 live data families per nine-stage replica (2 × 4 pairs × 112 ports,
all 492 helpers hosted).

Under PR1012's coverage identity, paid mass is exactly `72·W + 64·N`, so each call carries 1,646 units
of idle mass. Every child of rank `r` costs `(r/73)^(1−a) = r·r^(−a)·73^(a−1)`, which is non-increasing
per unit of mass in `r`. So **no** idle histogram beats putting all idle mass into (fractional) children
of the largest rank allowed by the outer halving guard, `R = 51` (73² > 2·51²).

## Results (exact rational intervals, `verify.py`)

| Quantity | Value |
|---|---|
| Ceiling for any hosting, owner packing or idle-remainder change of this word | **a < 0.001690054109089** |
| Implied κ bound (`κ < a/(1+a)` when the complex side binds) | **κ < 0.001687202646** |
| Maximum gain over the selected κ 0.001672660197076918 | **+0.869%** |
| Selected endpoint / relaxation at the endpoint | below the ceiling; actual moment ≥ relaxation |
| Previous record #1042 | same paid local profile plus an admissible idle histogram (derived idle `{1:2249, 2:1, 3:400, 7:3, 16:47, 48:4850}` matches its README); endpoint below the same ceiling |

This updates the fixed-word ceilings computed for earlier words
([static44](../static44-packing-ceiling/README.md), PR525, PR643) to the selected hosted T16/T37 line. It
uses the coverage law instead of a dual certificate. At the level of this cost decomposition, #1042→#1094 keeps the local paid profile and changes the
idle contribution. This arithmetic check does not by itself establish identical circuits or attribute every
implementation change to packing. Less than 0.87% of packing headroom remains under the stated model.

### What a local word must pay for the planning target a = 1/99

Rewrite `relax(a) ≤ 1` as `Σ n_r p_r(a) ≤ B(a)`. Here `p_r(a) = (r/73)^(1−a) − r(51/73)^(1−a)/51` is the
excess of a local rank-r child over ideal idle mass, and `B(a) = w − (72w+64)(51/73)^(1−a)/51` is the
budget per call.

| a | Budget B | Selected word's excess spend | Ratio |
|---|---:|---:|---:|
| selected endpoint 0.0016755 | 0.42752 | 0.42330 | 0.990 |
| target 1/99 | 0.12753 | 2.59681 | **20.4** |

At a = 1/99, the selected word's excess spend is 20.4 times the budget. **Even deleting all 2,412 rank-1
children per call, with everything else fixed, cannot reach it.** The allowed rank-1 count is negative.
With 112 ports and this nine-stage template, a target-scale gain needs a local word whose fully priced
excess spend is about 95% lower. Otherwise the coverage law itself must change: more unpaid coordinates
per family, a smaller 64-per-call centre charge, or more families per call. Helper-inventory proposals
can be screened against these numbers before any network is built: `ceiling.ceiling(local, 73, 896, 9, 64)`
takes a per-call local profile.

### Ideal lever budgets

`levers.py` changes one premise at a time and reports the packing ceiling. These are favorable relaxations
that omit the costs of realizing each lever.

| Lever | Ceiling × | κ cap |
|---|---:|---:|
| Centre path free (no rank-8 copies, no 64-per-call charge) | 2.80 | 0.00472 |
| Centre path shared by two calls | 1.90 | 0.00320 |
| Local mass as rank-16 children | 2.31 | 0.00389 |
| Local mass as rank-8 children | 1.62 | 0.00273 |
| Two unpaid coordinates per live family | 3.77 | 0.00634 |
| Centre free and rank-16 children | 6.51 | 0.01089 |

## Scope and limits

- The bound holds for one fixed paid local profile (in particular, for a fixed local word), 112 ports, the nine-stage four-pair
  template, the coverage law and the outer halving guard. It allows fractional counts and every repacking,
  without checking physical realizability.
- It does **not** bound other local words. Many open claims above the selected κ (for example #1148's
  joint-entrance word and its descendants, all ≤ 0.0016759) change the local word, so they are outside it.
  Changed port counts, templates, coverage laws, centre charges or outer recipes are also outside it.
- `κ < a/(1+a)` is the retained balanced reduction's planning ceiling. The actual seven-step recipe gives
  slightly less.
- Four controls run:
  - an idle-rank cap of 52 is rejected;
  - a local mass beyond the coverage law is rejected;
  - one extra rank-1 child lowers the ceiling;
  - 25 sampled integer idle histograms all have exact moment above one at the ceiling.

## Reproduce

```sh
python3 -I -B research/complex-local-word-ceiling/verify.py          # ~10 s, PASS_COMPLEX_LOCAL_WORD_CEILING
python3 scripts/research_package.py --package research/complex-local-word-ceiling
python3 -I -B research/complex-local-word-ceiling/levers.py          # ~5 s, planning budgets
```

`verify.py --write` regenerates `RESULT.json`. The exact arithmetic in `ceiling.py` uses the standard
library only: atanh logarithm chains, Taylor exponentials with remainder, and outward rounding to 2⁻²⁵⁶.

## Open next questions

- **What is the ceiling of each pending local word?** The ceiling separates packing headroom from
  word gains in the review queue. A first step is to run `ceiling()` on the per-call local profiles of
  #1148/#1169/#1218, after subtracting their idle histograms. The blocker is that each claim's idle
  histogram must be extracted from its package.
- **How does the target budget scale with the port count V?** `B(a)` grows linearly with families per call.
  Whether a decoder's excess spend grows more slowly decides if wider words can help. A first step is to
  fit `Σ n_r p_r` against V across the recorded complex words (R439–R560 lineage). The blocker is per-call
  local profiles for different V on a comparable template.

## Credit

The coverage identity is PR1012's. The fixed-word packing-ceiling idea comes from the static44, PR525 and
PR643 lineage, and the catalogue mixture bound from Ali Romman's
[heterogeneous-owner-assembly](../heterogeneous-owner-assembly/README.md). The selected construction
credits are in its review. Prepared by Douglas Colkitt with substantial Claude (Anthropic) assistance.
Apache-2.0.
