# Seven–nine query invoices cannot beat the six-query mutable-source endpoint

**Priced finite invoice under the PR1898 abstract complete-call tariff; no new κ.**
Answers open question 1 of
[CrocSwap/integer-mult-bounds#2455](https://github.com/CrocSwap/integer-mult-bounds/pull/2455)
/ the unequal-price handoff of merged
[PR1898](https://github.com/CrocSwap/integer-mult-bounds/pull/1898): bound attainable
`R`/`X` bills at seven, eight and nine queries for the explicit fixture
`(b,a,x)=(38,2,2)`.

Under **path-lowered even-subset schedules** on connector prefixes (the same
schedule class as PR1898's minimum-query word and PR1370's four-X path), no
word with `Q ∈ {7,8,9}` beats the sharp six-query endpoint tariff **436**.

| Q | Exact / bound | R | X | Abstract tariff | vs 436 |
|---|---|---:|---:|---:|---|
| 6 (PR1898 endpoint) | exact | 96 | 8 | **436** | — |
| **7 (this)** | **exact minimum** (R∈{82,88}) | **82** | **6** | **442** | **+6** |
| 8 | lower bound | ≥74 | ≥0 | **≥452** | +≥16 |
| 9 | lower bound | ≥62 | ≥0 | **≥466** | +≥30 |
| 10 (PR1370 four-X) | attained | 62 | 4 | 512 | +76 |

The seven-query minimum is certificate-closed. Every 6-subset of nonzero F₂⁵
points is scored for even-subset readout cost: covering sets attain only
`R∈{82,88}` (97,216 / 486,080; none in `{83..87}`). Under tariff
`38Q+2R+2X`, beating 436 needs `R+X<85`, so the excluded intermediate band
cannot undercut even at `X=0`, and `R=88` already forces tariff `≥442`. On the
`R=82` layer, every full-rank Hamiltonian closing is scored for path-local
source-XOR cost (no set has `X<6`; 14,595 attain `X=6`), so that layer is also
`≥442`. Champion path `[0,1,2,6,12,24,16,0]` attains `7 Q / 82 R / 6 X` and
replays on arbitrary dirty formal rows. The eight-query bound is the
exhaustive minimum `R=74` over all distinct 7-nonzero slot sets (`X≥0`). Nine
queries cannot undercut 436 because already `R≥62` forces tariff `≥466`.

This does **not** price arbitrary XOR-interleaved words outside path-local
compute/uncompute lowering, nor claim a physical supplier tariff or new κ.

## Reproduce

Python **3.12**, standard library only, from the repository root:

```sh
python3.12 -I -B research/mutable-source-789q-invoice/verify.py
python3.12 -I -O -B research/mutable-source-789q-invoice/verify.py
python3.12 -I -B research/mutable-source-789q-invoice/independent.py
python3.12 -I -B research/mutable-source-789q-invoice/test_package.py
python3.12 scripts/research_package.py --package research/mutable-source-789q-invoice
```

Expected:

```text
PASS_MUTABLE_SOURCE_789Q_INVOICE Q6=436 Q7=442 Q8_floor=452 Q9_floor=466 no_new_kappa
PASS_INDEPENDENT_789Q_INVOICE champion=442 floors=452,466 R_spectrum=[82, 88] controls=2
PASS_REGISTERED_RESEARCH_PACKAGE research/mutable-source-789q-invoice outcome=completed
```

First-time certificate generation (authoring only):

```sh
python3.12 -I -B research/mutable-source-789q-invoice/verify.py --write
```

Default verify is read-only and compares the fresh census to
[CERTIFICATE.json](CERTIFICATE.json). Admission uses `need()` (not `assert`);
`-O` also passes. The principal census takes on the order of a few minutes.

## Evidence map

| Claim | Where |
|---|---|
| 6Q/10Q comparator invoices | `model.minimum_word_6q`, `model.four_x_ten_q` |
| Exact min R at Q=7 | exhaustive `combinations(range(1,32),6)` in `verify.py` |
| Attainable R spectrum `{82,88}` | same census; histogram in `CERTIFICATE.json`; rechecked by `independent.py` |
| Exact min X among R=82 sets | exhaustive full-rank path orders; no `X<6` |
| Exact min tariff 442 / no beat 436 | spectrum floors + min-X layer; machine-checked in `verify.py` |
| Champion identity + tariff 442 | `path_word` + formal dirty replay; `independent.py` column image |
| Q=8 R≥74 | exhaustive distinct 7-nonzero slot sets |
| Q=9 tariff ≥466 | `R≥62` for 31 masks |

## Scope limits

No new kappa, frontier, native/hosted admission, or compiler/tape claim. The
schedule class is path-lowered even-subset readout words with the PR1898
abstract leaf/node/dispatch fixture. Global unequal-price optimality over all
XOR interleavings remains open. Physical common-B source access remains open.

## Open next questions

1. **Can a non-path XOR schedule at seven queries reach X≤2 with R=82 (tariff ≤436)?**
   Why it matters: shared shear preparation across edges might beat path-local
   compute/uncompute. First step: search restored source programs of X-length
   ≤2 that realize the champion prefix increments. Blocked by: no cheaper
   shared-XOR witness is known.
2. **What is the exact minimum R at eight queries allowing repeated prefix values?**
   Why it matters: the distinct-slot bound R≥74 already excludes beating 436,
   but repeats could matter for other tariffs. First step: meet-in-the-middle
   over 8-tuples. Blocked by: larger search.

## Credit

Credit **Arham Tahir / PR1898** (minimum-query endpoint, abstract tariff fixture,
unequal-price handoff), **PR1370** (four-X path and ten-query paired word),
**ywz65 / PR2455** (sharp eight XORs at six queries; open question answered
here), **TennisBowling / PR1524** (equal-price theorem / unequal handoff),
**Ross Richardson / PR943** (prefix framework), and the retained mutable-source
lineage. Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance.
Apache-2.0. No independent human review or multiplication theorem is claimed.
