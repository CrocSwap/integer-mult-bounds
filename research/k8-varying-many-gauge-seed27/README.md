# Temporal L253 gauge on the 218-helper k8 word

**Finite scalar construction; no new κ.** A seed-selected time-varying dyadic gauge on helper L253 saves another **182 complex scalar primitives per invocation in each orientation** over the simultaneous 218-helper constant-gauge candidate in [PR1263](https://github.com/CrocSwap/integer-mult-bounds/pull/1263). The total saving against the original PR1094 complex word is 13,182 complex primitives per orientation. The paid recursive profile is unchanged, so the selected conditional κ remains `0.001672660197076918`.

| Complex scalar word | Forward | Backward |
|---|---:|---:|
| Original PR1094 | 149,002 | 149,018 |
| PR1263 simultaneous constant gauges | 136,002 | 136,018 |
| This L253 temporal schedule | 135,820 | 135,836 |
| Total saving vs original | 13,182 | 13,182 |
| Additional saving vs PR1263 | 182 | 182 |

The exact repository base is `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. The frozen predecessor is Philipp / @mightyOil's PR1263 head `5fbaca13028846bddbb001e8e07addc2ab8e5816`; the temporal schedule method follows Sagar Thakrar's [PR1259](https://github.com/CrocSwap/integer-mult-bounds/pull/1259) head `61367611154266a982fe25e1a6243a8aad77227d`. Both heads and every vendored input are pinned in `DEPENDENCIES.json`. The accepted selected result and its sources are pinned in `SOURCES.json`.

Concurrent [PR1310](https://github.com/CrocSwap/integer-mult-bounds/pull/1310) (head `b9ca10f02fca37c8214d880c244ac14ead6bae7a`) checks coupled two-coordinate **constant** gauges around PR1263's vector and explicitly excludes composition with phase-varying gauges. This package extends the schedule class instead: it varies one seed-selected helper across its uses while holding the remaining 217 static gauges fixed. It neither imports nor combines PR1310's candidate.

## Exact schedule price

Seed 27 selects the zero-based index `27 mod 218` in PR1263's sorted forward gauge support, namely L253. Its constant exponent in that candidate is −1 forward and +1 backward. The proof changes only L253's exponent between its uses; the other 217 helper gauges, all paid frame and recursive events, original SCALEs, COPYs, clears and ADD order remain fixed.

For orientation `o`, list the 96 incident ADDs in chronological order. In the frozen PR1263 word, ADD `i` has coefficient `q_i` and L253 sign `s_i` (+1 when L253 is the target, −1 when it is the source). A temporal schedule is an integer sequence `d_i`; its coefficient becomes `q_i 2^(s_i d_i)`. With `P(q)` the exact real-primitive price of one ADD under PR696's copy-init lowerer, the complete change in one real component is

```text
Δ(d) = Σ_i [P(q_i 2^(s_i d_i)) − P(q_i)]
       + |d_1| + Σ_{i>1}|d_i − d_(i−1)| + |d_96|.
```

The last three terms charge every inserted scale from the initial zero gauge through each transition and back to zero. The existing static L253 entry/exit scales stay in the frozen word and are already included in the baseline invoice. No scale or coefficient work is omitted.

The verifier minimizes this chain cost exactly by dynamic programming over the exponent at each use. Coefficient-cost breakpoints are `0` and the integer zeros of `q_i 2^(s_i d_i)`. Let `[L,U]` be the smallest interval containing all these points. Coordinatewise clamping a schedule to `[L,U]` cannot increase total variation because interval projection is 1-Lipschitz and both endpoint gauges are zero. Every coefficient exponent's absolute value also cannot increase under this clamp; a unit-coefficient discount can occur only at an included zero. Thus the finite domains `[-2,4]` forward and `[-4,2]` backward cover every integer schedule. Each has seven states and the exact recurrence checks `7 + 95·7² = 4,662` state transitions per orientation. The independent implementation recomputes the optimum and its price. It returns −91 real primitives in each orientation, matching the complete stream invoice.

## Reproduce

With Python 3.11 or newer and the standard library:

```sh
python3 -I -O -B research/k8-varying-many-gauge-seed27/verify.py
```

Expected final lines:

```text
PASS_L253_TEMPORAL_GAUGE_ON_218_HELPER_WORD
forward helper 253 incremental_real -91 complex 135820 saved_vs_original 13182 columns 712
backward helper 253 incremental_real -91 complex 135836 saved_vs_original 13182 columns 712
```

The package controls are:

```sh
python3 -I -O -B research/k8-varying-many-gauge-seed27/test_package.py
```

Expected: `PASS_L253_PACKAGE_CONTROLS controls=7 orientations=2 seed=27 helper=253`.
The repository's registered replay is `python3.12 scripts/research_package.py --package research/k8-varying-many-gauge-seed27`.

The replay checks the predecessor's 218-helper construction, all 712 formal data/helper/center columns in both orientations, paid-profile equality, the local 192-bit charge, exact scalar invoices, source pins and both schedule receipts. The tests independently recompute the all-integer optimum, compare a three-use case with exhaustive enumeration, confirm the zero schedule changes nothing, and reject a word with an inserted L253 transition scale omitted.

This is a scalar-word construction and an exact one-coordinate conditional optimum with the other 217 constant gauges fixed. It does not establish a native supplier, frame or hosted admission, a new recursive profile, a new κ, a new runtime result, a global multi-coordinate optimum, or a formal multiplication theorem. The inherited all-size/compiler, realization, hosting, precision/tape, analytic and bit-interface assumptions remain.

Prepared by **Cinna Davis / @1337isnot1337** with substantial **OpenAI Codex** assistance in research, exact cost analysis, implementation, verification and writing. No independent human review is claimed. Credit Philipp / @mightyOil's [PR1263](https://github.com/CrocSwap/integer-mult-bounds/pull/1263) many-helper candidate; Sagar Thakrar's [PR1259](https://github.com/CrocSwap/integer-mult-bounds/pull/1259) temporal gauge and PR696 lowerer; @woklerx's [PR1161](https://github.com/CrocSwap/integer-mult-bounds/pull/1161) constant gauge; Hanson Sun / @bbMisk's [PR1214](https://github.com/CrocSwap/integer-mult-bounds/pull/1214) two-helper result and PR1310's independent two-coordinate constant-gauge study; and the retained PR1094 supplier lineage. Apache-2.0; all predecessor notices are retained.

## Open next questions

1. Does the exact L253 word pass native provider emission and whole-call hosting admission? This is required before adopting the scalar candidate; the next step is to emit only the certified schedule and replay both orientations in the source-bound native supplier.
2. Can a two-coordinate temporal schedule lower the bill further? This result only optimizes L253 with the other 217 constant gauges fixed; the next step is a joint dynamic program for L253 and one seed-selected neighboring helper with every shared ADD priced once.
