# Master handoff — independent-walks-9q

## Deliverable

| Field | Value |
|---|---|
| Branch | `cursor/independent-walks-9q-60b9` |
| Tip SHA | branch HEAD (`git rev-parse cursor/independent-walks-9q-60b9`) |
| Package | `research/independent-walks-9q/` |
| Claim | Freestanding `#840`-style priced alphabet: **Q=9 partitioned independent dual** under PR1898 `(b,a,x)=(38,2,2)` |
| Result | Exact covering min **R=80** on `(2,7)`; `(3,6)` min 88; `(4,5)` min 92; tariff floor **502>436** (also above same-walk Q9 floor 466) |
| Kappa | none |

## Answers

- Preferred next20 / threerepeat OQ2: Q=9 partitioned independent dual companion
  on `(2,7)/(3,6)/(4,5)` does **not** undercut tariff 436 (floor 502), nor the
  same-walk Q=9 floor 466 of #2677.

## Exact census

| Shape | Covering | Min R | Histogram |
|---|---:|---:|---|
| `(2,7)` | 20512576 | 80 | 80:972160 / 82:2041536 / 86:6319040 / 88:8749440 / 92:972160 / 100:1458240 |
| `(3,6)` | 69370560 | 88 | 88:3749760 / 90:20623680 / 92:11249280 / 94:5624640 / 96:21873600 / 100:5624640 / 104:624960 |
| `(4,5)` | 122561600 | 92 | 92:4166400 / 94:37497600 / 96:43747200 / 98:3472000 / 100:31248000 / 104:2430400 |

Champions: `((0,19),(0,1,2,4,8,15,16))` R=80 X=26;
`((0,1,2),(0,4,8,13,16,22))` R=88 X=18;
`((0,1,2,4),(0,7,8,16,25))` R=92 X=22.

## Leave-alone respected

Through #2868 / #2867 / #2861 / #2860 / #2858 / #2851;
#2846/#2840/#2836/#2817/#2779/#2764/#2761; deferred soft-overlaps untouched.

## Verify gate

```sh
python3.12 -I -B research/independent-walks-9q/verify.py
python3.12 -I -O -B research/independent-walks-9q/verify.py --quick
python3.12 -I -B research/independent-walks-9q/independent.py
python3.12 -I -B research/independent-walks-9q/test_package.py
python3.12 -B scripts/research_package.py --package research/independent-walks-9q
```

## Attribution

Author: Wentao Li \<wentaol4@illinois.edu\>
Disclosure: Prepared by Wentao Li with substantial AI assistance.
`TASK.json` `ai_assistance` without product/model names.
Never `Co-authored-by: Victor Li`.

## Next open

1. Sixth priced alphabet under PR1898 at Q=8 beyond three-repeat / shared-dirt?
2. Mixed shared-dirt + excess at Q=8 vs shared-dirt floor R=82?
