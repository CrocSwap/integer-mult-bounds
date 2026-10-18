# Seven-query source-XOR floor is exactly six

**Scoped obstruction with sharp attainment; no new kappa.** In the five-source
common-B mutable-source alphabet of
[PR1898](https://github.com/CrocSwap/integer-mult-bounds/pull/1898), every
restored straight-line word with **exactly seven queries** needs **at least six
source XORs**. The bound is sharp: the credited path-lowered champion

```text
(0, 1, 2, 6, 12, 24, 16, 0)
```

attains `7 Q / 82 R / 6 X` (abstract tariff **442** at `(b,a,x)=(38,2,2)`).

This answers open question 1 of the path-lowered
`research/mutable-source-789q-invoice` lineage (beyond
[#2455](https://github.com/CrocSwap/integer-mult-bounds/pull/2455) /
[#1898](https://github.com/CrocSwap/integer-mult-bounds/pull/1898)): a non-path
XOR schedule at seven queries **cannot** reach `X≤2` with `R=82` (nor any `R`),
because already `X≤5` is impossible at `Q=7`.

| X length | Min interaction components | Query floor `5+c` | Admits `Q=7`? |
|---:|---:|---:|---|
| ≤2 | ≥4 (census; edges alone give ≥3) | ≥9 | no |
| 4 or 5 | 3 | 8 | no |
| **6** | **2** | **7** | **yes (sharp)** |

The component lemma (`Q ≥ n + c`) and the meet-in-the-middle restored-graph
census through length six are recorded in [PROOF.md](PROOF.md) and
[CERTIFICATE.json](CERTIFICATE.json). Graph digests for lengths 0–6 match open
PR2455's published `RESULT.json` (that PR proves `X≥8` at **six** queries;
this package uses the same census engine for the **seven**-query floor).

No claim that seven-query words cannot undercut tariff 436 by lowering `R`
below 82 while keeping `X≥6`. No physical supplier invoice or new κ.

## Reproduce

Python **3.12**, standard library only, from the repository root:

```sh
python3.12 -I -B research/seven-query-xor-floor/verify.py
python3.12 -I -O -B research/seven-query-xor-floor/verify.py
python3.12 -I -B research/seven-query-xor-floor/independent.py
python3.12 -I -B research/seven-query-xor-floor/test_package.py
python3.12 -B scripts/research_package.py --package research/seven-query-xor-floor
```

Expected:

```text
PASS_SEVEN_QUERY_XOR_FLOOR Q=7 min_X=6 sharp X<=5 blocked answers_789q_oq1 no_new_kappa
PASS_INDEPENDENT_SEVEN_QUERY_XOR_FLOOR min_X=6 floors_block_X_le_5 ... tariff=442 controls=2
PASS_SEVEN_QUERY_XOR_FLOOR_PACKAGE_TESTS groups=6
PASS_REGISTERED_RESEARCH_PACKAGE research/seven-query-xor-floor outcome=completed
```

Default verify is read-only and compares a fresh census to
[CERTIFICATE.json](CERTIFICATE.json). Use `--write` only to regenerate that
receipt. Admission uses `need()` (not `assert`); `-O` also passes.

## Scope and overlap

Base commit `0b1cccf86e2f5132ed286a26ef0a681a495740ea`. Direct predecessors:
PR1898 (minimum-query endpoint), open PR2455 (six-query XOR necessity), and the
fork path-lowered 789q invoice (OQ1). Leave-alone objects through
[#2593](https://github.com/CrocSwap/integer-mult-bounds/pull/2593) and the
pending `mutable-source-789q-invoice` R-spectrum repair are not edited.

Closest prior: PR2455 proves `X≥8` at `Q=6` and does not settle seven queries.
The 789q package prices path-lowered `Q∈{7,8,9}` bills and leaves non-path
`X≤2` open. This freestanding package closes that XOR-floor obligation at
`Q=7` for the full restored alphabet.

## Open next questions

1. What is the minimum readout count `R` among restored seven-query words with
   `X=6`? Why it matters: tariff `38·7 + 2R + 2·6` undercuts 436 iff `R≤78`.
   First step: search restored length-6 shear words whose query schedule admits
   even-subset (or cheaper) coverings with `R≤78`. Blocked by: no such covering
   census is claimed here.
2. Does the same component+census method give a sharp XOR floor at eight
   queries? First step: extend the restored-graph census to the first length
   with `n+c ≤ 8` and match an attaining word. Blocked by: larger search.

## Credit

Credit **Arham Tahir / PR1898** (alphabet, minimum-query endpoint, abstract
tariff), **ywz65 / PR2455** (component lemma and meet-in-the-middle restored
census at six queries; digests reused as cross-check), **PR1370** (path-local
shear lowering), the fork **789q invoice** lineage (path-class champion and
OQ1), **TennisBowling / PR1524**, **Ross Richardson / PR943**, and the retained
mutable-source lineage. Live input pin:
`research/mutable-source-shear-cost/CERTIFICATE.json` (ten-query four-X
context). Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance.
Apache-2.0. No independent human review or multiplication theorem is claimed.
