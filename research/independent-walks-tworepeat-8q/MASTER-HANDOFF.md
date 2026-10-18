# Master handoff — independent-walks-tworepeat-8q

## Deliverable

| Field | Value |
|---|---|
| Branch | `cursor/independent-walks-tworepeat-8q-60b9` |
| Tip SHA | branch HEAD (`git rev-parse cursor/independent-walks-tworepeat-8q-60b9`) |
| Package | `research/independent-walks-tworepeat-8q/` |
| Claim | Freestanding `#840`-style priced alphabet: **two-repeat** (excess-2) partitioned independent dual at Q=8 under PR1898 `(b,a,x)=(38,2,2)` |
| Result | Exact covering census **0** on `(2,6)` / `(3,5)` / `(4,4)`; cannot undercut tariff **436** |
| Kappa | none |

## Answers

- Preferred next17 / onerepeat-35-44 OQ1: named third alphabet beyond same-walk /
  dirty-shadow / partitioned dual / one-repeat.
- onerepeat-35-44 OQ2: two-repeat does not undercut distinct floors (in fact
  never covers).

## Exact census

| Shape | Valid | Covering | Structural bound |
|---|---:|---:|---|
| `(2,6)` | 26970 (`{2,2,1}` 13485 + `{3,1,1}` 13485) | 0 | span ≤8 ⇒ coset ∪ ≤16 |
| `(3,5)` | 465 `{2,2}` multisets | 0 | sumset ≤16 |
| `(4,4)` | 0 (`{d:3}` never restores) | 0 | — |

## Leave-alone respected

Through #2851; pending `cursor/independent-walks-onerepeat-8q-60b9@b07bc1e1` and
`cursor/independent-walks-onerepeat-35-44-60b9@8bd3d298`; #2846/#2840/#2836/#2817/
#2779/#2764/#2761; deferred soft-overlaps untouched.

## Verify gate

```sh
python3.12 -I -B research/independent-walks-tworepeat-8q/verify.py
python3.12 -I -O -B research/independent-walks-tworepeat-8q/verify.py
python3.12 -I -B research/independent-walks-tworepeat-8q/independent.py
python3.12 -I -B research/independent-walks-tworepeat-8q/test_package.py
python3.12 -B scripts/research_package.py --package research/independent-walks-tworepeat-8q
```

## Attribution

Author: Wentao Li \<wentaol4@illinois.edu\>
Disclosure: Prepared by Wentao Li with substantial AI assistance.
`TASK.json` `ai_assistance` without product/model names.
Never `Co-authored-by: Victor Li`.

## Next open

1. Fourth priced alphabet under PR1898 at Q=8 beyond two-repeat?
2. Shared-dirt dual on distinct partitioned walks (soft-overlap check vs shared-XOR)?
