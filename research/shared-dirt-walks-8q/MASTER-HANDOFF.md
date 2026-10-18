# Master handoff — shared-dirt-walks-8q

## Deliverable

| Field | Value |
|---|---|
| Branch | `cursor/shared-dirt-walks-8q-60b9` |
| Tip SHA | branch HEAD (`git rev-parse cursor/shared-dirt-walks-8q-60b9`) |
| Package | `research/shared-dirt-walks-8q/` |
| Claim | Freestanding `#840`-style priced alphabet: **shared-dirt** (joint even live-read parity) partitioned dual at Q=8 under PR1898 `(b,a,x)=(38,2,2)` |
| Result | Exact covering min **R=82** on `(2,6)` / `(3,5)` / `(4,4)`; tariff floor **468>436**; beats independent floors 92/98/100; soft-overlap-safe vs shared-XOR |
| Kappa | none |

## Answers

- Preferred next18 / tworepeat OQ1: named fourth alphabet beyond same-walk /
  dirty-shadow / partitioned dual / one-repeat / two-repeat.
- tworepeat OQ2: shared-dirt undercuts independent-dirt floors (82 < 92/98/100)
  but still cannot undercut tariff 436; soft-overlap vs shared-XOR is safe
  (R-side dirt coupling only).

## Exact census

| Shape | Covering | Min R | Histogram |
|---|---:|---:|---|
| `(2,6)` | 3916416 | 82 | 82:583296 / 88:2916480 / 96:416640 |
| `(3,5)` | 10416000 | 82 | 82:1458240 / 88:7291200 / 96:1666560 |
| `(4,4)` | 14165760 | 82 | 82:1944320 / 88:9721600 / 96:2499840 |

Champions: `((0,16),(0,1,2,4,8,15))`, `((0,1,2),(0,4,8,15,16))`,
`((0,1,2,4),(0,8,15,16))` — each shared `R=82`.

## Leave-alone respected

Through #2858 / #2851; pending `cursor/independent-walks-onerepeat-8q-60b9@b07bc1e1`
and `cursor/independent-walks-tworepeat-8q-60b9@c4581aaf`;
#2846/#2840/#2836/#2817/#2779/#2764/#2761; deferred soft-overlaps untouched
(shared-XOR not opened).

## Verify gate

```sh
python3.12 -I -B research/shared-dirt-walks-8q/verify.py
python3.12 -I -O -B research/shared-dirt-walks-8q/verify.py
python3.12 -I -B research/shared-dirt-walks-8q/independent.py
python3.12 -I -B research/shared-dirt-walks-8q/test_package.py
python3.12 -B scripts/research_package.py --package research/shared-dirt-walks-8q
```

## Attribution

Author: Wentao Li \<wentaol4@illinois.edu\>
Disclosure: Prepared by Wentao Li with substantial AI assistance.
`TASK.json` `ai_assistance` without product/model names.
Never `Co-authored-by: Victor Li`.

## Next open

1. Fifth priced alphabet under PR1898 at Q=8 beyond shared-dirt?
2. Three-walk shared-dirt (e.g. `(2,2,4)`) vs two-walk floor R=82?
