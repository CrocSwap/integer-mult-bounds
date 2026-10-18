# One clean connector for distinct five-source outputs

**New root mechanism and local charged cost reduction; no new κ.** A fresh, explicitly zeroed length-16 row lets each of the 31 nonzero five-source masks use one output-map call. It trades many extra source updates for fewer expensive output updates while retaining pairwise-distinct output maps.

## Contract and construction

Let `x_0,...,x_4`, the original connector `z`, and targets `y_m` be distinct length-`L` rows over F2. Their initial contents are arbitrary. The maps `B_j` and `A_m` are exact linear maps and stay read-only. The requested result is

```text
y_m += A_m(sum_{j in m} B_j x_j)     for every nonzero 5-bit mask m.
```

Admit one extra row `c`. It is not presumed clean: allocate/host it, clear all `L` coordinates, and charge those writes. For each mask in order, do:

```text
for each j in m: c += B_j x_j
 y_m += A_m c
for each j in reverse order: c += B_j x_j
```

In characteristic two, the reverse source updates return `c` to zero. The next mask starts clean. The original dirty `z`, all sources, and all other targets are untouched. Each target receives exactly its requested additive update. This identity holds for arbitrary linear maps; it needs no commutation, invertibility, or relations among the maps.

For all 31 masks, `sum popcount(m)=5*16=80`. The new schedule therefore uses 160 source updates and 31 output updates. As its named competitor, use the pinned five-source `five_extra_output` schedule in the universal connector certificate: 10 source updates and 64 output updates, with output 21 read four times and every other output twice. That schedule supports arbitrary distinct `A_m` and `B_j` in the unchanged dirty-connector alphabet.

## Exact fixture and complete root bill

Use `L=16`. Let each `B_j` be a distinct cyclic coordinate permutation. Define

```text
A(v)[i] = sum_{k=0}^{12} v[(i+k) mod 16]  over F2
A_m = A Q_m
```

Choose 31 distinct coordinate permutations `Q_m` from `Q_(a,b)(v)[i] = v[(a*i+b) mod 16]`, with odd `a`. These are permutations. `A` is invertible: its polynomial has value 1 at `x=1`, and `x^16-1=(x+1)^16` over F2. Thus the `A_m` are pairwise distinct. Each output row of each `A_m` has exactly 13 taps. The verifier checks the rank and distinctness directly as well.

The comparison uses one declared additive tariff. One unit is charged for each XOR update, stored table bit, hosted row coordinate, zero write, and scheduler descriptor. This is a transparent local model, not a physical hardware price. Let `a=208` XOR updates per `A_m` call, `b=16` per `B_j` call, and `d=13` per action/control descriptor. Source and target reads/writes and coefficient-index reads are included in the XOR-update units. Static map tables are charged separately.

| Charge | Direct dirty-connector schedule | Fresh-row schedule |
|---|---:|---:|
| `B` updates | 10 | 160 |
| `A` updates | 64 | 31 |
| Per-action descriptors | `74d` | `191d` |
| Mask-block control descriptors | 0 | `31d` |
| Allocation/release descriptors | 0 | `2d` |
| Extra row hosting | 0 | `L` |
| Zero-initialization writes | 0 | `L` |

Both schedules share 31 output-map tables, five source-map tables, and the existing data rows. The tables contain `31*16*13*4 + 5*16*4 = 26,112` address bits. The five sources, original connector and 31 targets use `37*16 = 592` row cells. Their shared charge is 26,704 units. The fresh-row schedule's 31 block descriptors are an additional conservative charge; each operation descriptor is also charged separately.

The direct and candidate totals are therefore

```text
direct    = 26704 + 10*(b+d) + 64*(a+d)                       = 41138
fresh row = 26704 + 160*(b+d) + 31*(a+d) + 31*d + 2*d + 2*L = 38656
saving    = 33*a - 150*b - 150*d - 2*L                        = 2482
```

At this fixture, the saving is positive for integer `d <= 29`. The result is conditional on this explicit tariff and on the listed maps. If the output maps are cheap relative to source updates, the construction loses. The calculation is a root-interface comparison; it does not include a recursive supplier, child restoration, frame changes, precision conversion, or a κ integration. No universal optimality claim is made.

## Reproduce and evidence

From the repository root:

```sh
python3 -B research/clean-connector-per-mask-seede54e/verify.py
python3 scripts/research_package.py --package research/clean-connector-per-mask-seede54e --check-only
python3 scripts/research_package.py --package research/clean-connector-per-mask-seede54e
```

Expected verifier line:

```text
PASS_CLEAN_CONNECTOR_PER_MASK basis_columns=608 controls=13 masks=31 candidate_B=160 candidate_A=31 direct_B=10 direct_A=64 common=26704 direct_cost=41138 candidate_cost=38656 saving=2482
```

The exact F2 replay checks all 592 data-bit basis columns across the five sources, original connector, and 31 targets; linearity establishes the data identity for every such state. It also checks each of the extra row's 16 pre-clear bit columns; the explicit reset clears the whole row regardless of its prior contents. A mixed nonbasis state is replayed as well. Four construction controls detect omitted initialization, omitted reverse updates, an omitted source update, and a misrouted target. Nine invoice controls remove each charged line in turn and ensure the exact invoice check rejects the undercharge. The verifier reads the exact direct schedule from the pinned certificate and checks its call multiplicities. Local replay used Python 3.14.7; registered CI is configured for Python 3.12.

## Overlap and attribution

The initial common-map variant was released after the refreshed scan found the stronger common-`A` broadcast in [PR #1707](https://github.com/CrocSwap/integer-mult-bounds/pull/1707), head `3d2e634e046ac4fbf07ddbfb0e59da4cf9907f4e`. This result keeps pairwise-distinct `A_m` and pays for a fresh row cleared separately for each batch. The broader neighborhood includes the atomic triple-sum construction in PR #1518, two-source DUO schedule in PR #1531, fixed-alphabet parity schedules in PR #1811, and paid invertible-frame analysis in PR #1915; none uses this clean-row tradeoff. The overlap scan is not a novelty certificate. Exact base, selected record, catalogue and predecessor source pins are in [SOURCES.json](SOURCES.json).

Ross Richardson's universal connector interface and five-source schedule supply the direct comparator. No predecessor code is copied. Prepared by Cinna Davis with substantial OpenAI Codex assistance; Apache-2.0.

## Open next questions

The structured next question in [TASK.json](TASK.json) is whether this root saving survives nested composition when every child, restoration step, frame transition, and per-level descriptor is charged. The first step is to bind the row and map tariffs to one concrete recursive supplier and evaluate its full recurrence. That integration is currently blocked because this synthetic length-16 fixture has no compatible supplier implementation or recursive cost profile.
