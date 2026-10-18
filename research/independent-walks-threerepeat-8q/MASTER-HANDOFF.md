# Master handoff — independent-walks-threerepeat-8q

## Deliverable

| Field | Value |
|---|---|
| Branch | `cursor/independent-walks-threerepeat-8q-60b9` |
| Tip SHA | branch HEAD (`git rev-parse cursor/independent-walks-threerepeat-8q-60b9`) |
| Package | `research/independent-walks-threerepeat-8q/` |
| Claim | Freestanding `#840`-style priced alphabet: **three-repeat** (excess-3) partitioned independent dual at Q=8 under PR1898 `(b,a,x)=(38,2,2)` |
| Result | Exact covering census **0** on `(2,6)` / `(3,5)` / `(4,4)`; cannot undercut tariff **436** |
| Kappa | none |

## Answers

- Preferred next19 / shared-dirt OQ1: named fifth alphabet beyond same-walk /
  dirty-shadow / partitioned dual / one-repeat / two-repeat / shared-dirt.
- Soft-overlap with pending shared-dirt: safe (independent excess axis; no
  dirt coupling; package path and census disjoint).

## Exact census

| Shape | Valid | Covering | Structural bound |
|---|---:|---:|---|
| `(2,6)` | 930 (`{3,2}` only; `{4,1}` never restores) | 0 | span ≤4 ⇒ coset ∪ ≤8 |
| `(3,5)` | 0 (`{d:4}` never restores) | 0 | — |
| `(4,4)` | 0 (excess 3 impossible on L4) | 0 | — |

## Leave-alone respected

Through #2867 / #2861 / #2860 / #2858 / #2851; #2846/#2840/#2836/#2817/#2779/
#2764/#2761; deferred soft-overlaps untouched.

## Verify gate

```sh
python3.12 -I -B research/independent-walks-threerepeat-8q/verify.py
python3.12 -I -O -B research/independent-walks-threerepeat-8q/verify.py
python3.12 -I -B research/independent-walks-threerepeat-8q/independent.py
python3.12 -I -B research/independent-walks-threerepeat-8q/test_package.py
python3.12 -B scripts/research_package.py --package research/independent-walks-threerepeat-8q
```

## Attribution

Author: Wentao Li \<wentaol4@illinois.edu\>
Disclosure: Prepared by Wentao Li with substantial AI assistance.
`TASK.json` `ai_assistance` without product/model names.
Never `Co-authored-by: Victor Li`.

## Next open

1. Sixth priced alphabet under PR1898 at Q=8 beyond three-repeat?
2. Q=9 partitioned independent dual companion (vs #2677 same-walk floor 466)?
