# Seven-query even-subset R floor among X = 6 is exactly 82

**Scoped obstruction with sharp attainment; no new kappa.** In the five-source
common-B mutable-source alphabet of
[PR1898](https://github.com/CrocSwap/integer-mult-bounds/pull/1898), every
restored straight-line word with **exactly seven queries** and even-subset
connector-state readout needs **at least 82 readouts**. Among words with
**`X = 6`**, that floor is sharp: the path-lowered champion

```text
(0, 1, 2, 6, 12, 24, 16, 0)
```

attains `7 Q / 82 R / 6 X` (abstract tariff **442** at `(b,a,x)=(38,2,2)`).

This answers open question 1 of
[#2643](https://github.com/CrocSwap/integer-mult-bounds/pull/2643)
(`research/seven-query-xor-floor`): the minimum `R` among restored seven-query
words with `X = 6` is **exactly 82** in the even-subset class. In particular
`R ≤ 78` is impossible, so tariff `38·7 + 2R + 2·6` cannot undercut the
six-query endpoint **436** by lowering `R` at `X = 6`.

| Covering walk class | Distinct nonzero labels | Attainable even-subset R |
|---|---:|---|
| Hamilton (distinct slots) | 6 | **{82, 88}** |
| One repeated vertex (GL basis census) | 5 spanning | **{96}** |
| Rank `< 5` label sets | ≤4 independent | none (image ≤16) |

The distinct-slot spectrum matches the path-lowered 789q invoice. Allowing
repeated prefixes cannot beat 82: the only additional covering layer is
`R = 96`. Combined with #2643's restored XOR floor `X ≥ 6`, every `X = 6`
word has `R ≥ 82`.

## Reproduce

Python **3.12**, standard library only, from the repository root:

```sh
python3.12 -I -B research/seven-query-r-floor/verify.py
python3.12 -I -O -B research/seven-query-r-floor/verify.py
python3.12 -I -B research/seven-query-r-floor/independent.py
python3.12 -I -B research/seven-query-r-floor/test_package.py
python3.12 -B scripts/research_package.py --package research/seven-query-r-floor
```

Expected:

```text
PASS_SEVEN_QUERY_R_FLOOR Q=7 min_R_among_X=6 is 82 sharp repeat_layer_R=96 answers_7qxor_oq1 tariff_floor=442 no_new_kappa
PASS_INDEPENDENT_SEVEN_QUERY_R_FLOOR min_R=82 ... tariff=442 answers_7qxor_oq1
PASS_SEVEN_QUERY_R_FLOOR_PACKAGE_TESTS groups=6
PASS_REGISTERED_RESEARCH_PACKAGE research/seven-query-r-floor outcome=completed
```

Default verify is read-only and compares a fresh census to
[CERTIFICATE.json](CERTIFICATE.json). Use `--write` only to regenerate that
receipt. Admission uses `need()` (not `assert`); `-O` also passes.

## Scope and overlap

Base commit `0b1cccf86e2f5132ed286a26ef0a681a495740ea`. Direct predecessors:
PR1898, open PR2455, fork path-lowered `mutable-source-789q-invoice` (distinct
slot spectrum; not edited), and open #2643 seven-query XOR floor (OQ1; leave
alone). Leave-alone through #2643 including #2593 triadic is respected.

Closest prior: 789q prices path-class distinct-slot `R ∈ {82,88}` but does not
classify repeated-prefix coverings; #2643 proves `X ≥ 6` and leaves min `R` at
`X = 6` open. This freestanding package closes that readout obligation.

## Open next questions

1. Can a readout alphabet strictly cheaper than even-subset connector-state
   combinations reach `R ≤ 78` at `Q = 7` with `X = 6`?
   Why it matters: only then could seven queries undercut tariff 436 at the
   #2643 XOR floor. First step: define one priced odd-cardinality or
   multi-connector readout model and re-run the walk census. Blocked by: no
   cheaper covering witness is known.
2. Does the same walk classification give an exact min `R` at eight queries
   with the #2643-style XOR floor?
   Why it matters: completes the intermediate-query unequal-price handoff.
   First step: extend covering censuses to length-8 walks (including repeats).
   Blocked by: larger search.

## Credit

Credit **Arham Tahir / PR1898** (alphabet, minimum-query endpoint, abstract
tariff), **ywz65 / PR2455** (six-query XOR necessity), **PR1370** (path-local
shear lowering), the fork **789q invoice** lineage (distinct-slot spectrum and
champion), open **#2643** (XOR floor; OQ1 answered here; not edited),
**TennisBowling / PR1524**, **Ross Richardson / PR943**, and the retained
mutable-source lineage. Live input pin:
`research/mutable-source-shear-cost/CERTIFICATE.json`. Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance.
Apache-2.0. No independent human review or multiplication theorem is claimed.
