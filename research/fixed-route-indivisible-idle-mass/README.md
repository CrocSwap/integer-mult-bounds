# Whole-helper indivisibility forces at least 2,448 small idle-rank units

**Scoped packing obstruction; no new supplier or kappa.** On the selected T16
fixed route, every reassignment of the existing indivisible helper inventory
leaves at least **2,448 units of idle rank mass below rank 48**. Such positive
remainders have rank at most44. This holds even when chronology, active pairs
and per-call family uniqueness are relaxed.

The resulting primitive-saving ceiling is
`a < 0.001681977435447`, strictly below the rank-48 fractional cap
`a < 0.001682094870065` in [PR1783](https://github.com/CrocSwap/integer-mult-bounds/pull/1783).
This does not improve the selected construction. It answers that package's open
question about a capacity-aware strengthening by retaining indivisible helper
widths. Its source was inspected at `691534353b8c5172f5c157e79496686d8c80f196`.
The selected local word, capacities, live families and coverage law stay fixed.

## Exact source-bound model

The selected PLAN has10,752 bins of capacity8 and7,168 each of capacities16,
32 and48. Across144 calls the exact SPEC inventory is:

| Helper width | Count |
| --- | ---: |
| 4 | 8,064 |
| 5 | 4,608 |
| 7 | 4,320 |
| 8 | 17,568 |
| 9 | 34,560 |

All69,120 helpers must be assigned whole to bins; arbitrary within-bin order is
allowed. A bin containing counts n_w has remainder r=C-sum(w*n_w)>=0.
The inherited prefix rule in the pinned hosting proof gives precisely this
remainder. Total idle mass is237,024=4,938*48. Selected source-manifest hashes,
exact Git blobs and byte SHA-256 values bind the inputs in SOURCES.json.
No fact from the open PR's code is imported for acceptance.

## Short integer dual certificate

Give helper widths4,5,7,8,9 the weights1,41,15,2,-11. Give bin capacities8,
16,32,48 the constants-2,-4,-8,41. For each legal bin pattern define

`P = 48*(capacity_constant + sum(helper_weight*n_w)) - 41*r`.

Exhausting all1,163 nonnegative integer patterns with occupied width at most C
proves `P >= -1961*r` when0<r<48, and `P>=0` when r is0 or48. An independent
unbounded-coin dynamic program reproduces every minimum weight by occupied
width, so acceptance does not depend on an LP solver or numerical tolerance.
This is a finite exact lemma over the complete fixed bin alphabet.

Summing the constants and helper weights over the pinned inventories gives
`sum P = -4,767,456`. If S is total idle mass at ranks below48, then
`S >= 4,767,456/1961 = 89,952/37`.
Since total idle mass is divisible by48 and the remaining idle mass is at
rank48, S itself is a multiple of48. Therefore `S>=2448`.
Every nonempty capacity48 bin contains a helper of width at least4 and hence
has remainder at most44; all other capacities are at most32. Thus every unit
of the compulsory S mass costs at least the rank44 per-unit cost.

For0<a<1, per-unit child cost `(r/73)^(1-a)/r` decreases with r. The complete
optimistic moment is consequently at least

`[144*sum local[r]*(r/73)^(1-a) + (237024-2448)/48*(48/73)^(1-a) + 2448/44*(44/73)^(1-a)]/14336`.

The unchanged local profile is `{1:2412,2:418,3:432,4:142,5:82,8:8}`.
The pinned rational interval engine brackets the root between
0.001681977435446 and0.001681977435447. Its rank48-only control reproduces
PR1783's endpoints. The exact balanced-transfer kappa cap is recorded as a
rational in RESULT.json; it is a planning ceiling under inherited obligations.

## Verification and limitations

```sh
python3 -I -O -B research/fixed-route-indivisible-idle-mass/verify.py
python3.12 scripts/research_package.py --package research/fixed-route-indivisible-idle-mass
```

The selected idle histogram has3,456 sub48 mass units and passes the bound.
Two mutations lower a helper dual weight or the1961constant and are rejected
by actual bin witnesses. An explicit width1 helper would allow rank47 and
invalidates the44cap. A fractional-fill fixture attains all-rank48 idle mass,
showing that indivisibility is necessary. Exact source and certificate checks
also run with optimization enabled. SciPy proposed the dual during exploration;
reproduction uses only Python's standard library.

This dual is not claimed sharp or attainable. The work does not supply an
admitted owner map, change the word, redesign the route, replay the full native
supplier, discharge all-size/compiler obligations or alter selected kappa.

## Open next questions

Find the sharp capacity-and-indivisibility moment minimum using the complete
1,163-pattern column model. A rational dual and integer primal witness would
separate a tight relaxation from a merely favorable one. Chronology and family
constraints remain separate blockers to realizing any such witness. TASK.json
records the question and bounded first step.

## Credit

Josie Elliston's PR1783 supplies the fixed-route rank48 cap and capacity-aware
question; Douglas Colkitt and Claude supply the broader word-ceiling engine;
PR1012 supplies the coverage identity. Rohan Arun, Jeremy Kothe and the selected
review supply the T16 word/packing lineage. Prepared for woklerx with substantial
OpenAI Codex assistance. Apache-2.0. No independent human review is claimed.
