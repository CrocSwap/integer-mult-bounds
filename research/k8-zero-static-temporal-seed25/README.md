# Exact temporal-gauge census on PR1263 zero-static helpers

**Finite scalar construction; no new κ.** On the frozen 218-helper scalar word from [PR1263](https://github.com/CrocSwap/integer-mult-bounds/pull/1263), an exact one-coordinate temporal gauge on L359 saves **484 complex scalar primitives per invocation** over PR1263 in each orientation. L359 was one of the 19 eligible helpers whose static exponent was zero. The search checked every one of those 19 helpers in both orientations; it did not compose independent coordinate minima.

| Complex scalar word | Forward | Backward |
|---|---:|---:|
| Original PR1094 word | 149,002 | 149,018 |
| PR1263 218-helper static word | 136,002 | 136,018 |
| L359 temporal word | 135,518 | 135,534 |
| Additional saving over PR1263 | 484 | 484 |
| Total saving over original | 13,484 | 13,484 |

The selected conditional κ at the exact base `bce54fb3f895cbe5cd4c0eb477c3afeed100190f` remains `836330098538459/500000000000000000` (`0.001672660197076918`). The paid recursive profile is unchanged. This result does not claim a new supplier admission, hosted improvement, or κ.

## Exact price and schedule

For one helper `h` and one orientation, list its incident ADDs in chronological order. At ADD `i`, let `q_i = p_i 2^{e_i}` with `p_i` positive odd, and let `s_i` be `+1` if `h` is the target and `-1` if it is the source. The integer exponent `d_i` changes the coefficient to `q_i 2^{s_i d_i}`. PR1263's other 218 exponents remain fixed; all existing non-incident events remain as recorded.

With the exact PR696 copy-initialization price

```text
P(p 2^e) = 1 + bit_length(p) + popcount(p) + |e|
           - 1[p = 1 and e = 0],
```

the complete real-component change is

```text
Δ(d) = Σ_i (P(q_i 2^(s_i d_i)) − P(q_i))
       + |d_1| + Σ_(i>1) |d_i − d_(i−1)| + |d_m|.
```

The final terms charge the entry pulse from exponent zero, every phase change, and the exit pulse back to zero. No boundary scale is omitted. The exact DP finds `Δ = -242` in each orientation. The schedule changes L359 at 147 incident ADDs and inserts 33 scale macros, with total scale work 62 real primitives. The resulting complete invoice is 135,518 forward and 135,534 backward complex primitives, exactly 484 below PR1263.

## Search and coverage

PR1263 identifies 237 eligible cold-entry/FULL-exit, unwrapped, non-center helpers with no incident COPY or clear. Its static gauge support has 218 coordinates. This search took the complementary **19 eligible zero-static coordinates** `{272, 288, 348, 359, 381, 440, 444, 446, 447, 469, 478, 479, 491, 503, 507, 514, 515, 519, 542}`.

OS seed **25** assigned the complex-supplier track and selected the first scan coordinate as `25 mod 19 = 6`, L444. The finite census then covered all 19 helpers in both orientations, starting at L444 and wrapping once. Each one-coordinate objective was minimized over every integer schedule. The best constant exponent for each of the 19 coordinates has change zero; the unique lowest temporal minimum is L359 at `-242` real primitives in both orientations. The certificate records every helper's incident ADD count, exact finite interval, DP transition count, temporal minimum, and constant-gauge control.

The finite interval is exact. For each incident coefficient, price changes only through `|e_i + s_i d_i|` and the isolated unit-coefficient discount at `e_i + s_i d_i = 0`. Let `[L,U]` contain zero and every such integer root. Clamping each exponent to `[L,U]` cannot increase the total variation (interval projection is 1-Lipschitz), cannot increase any coefficient's absolute exponent, and retains every possible unit discount point. Therefore an optimum over all integer schedules lies in this interval. For L359, the forward interval is `[-3,7]` and the backward interval is `[-7,3]`; each DP has 11 exponent states and 17,677 exact edge evaluations, followed by an 11-state terminal scan.

This is a one-coordinate result. Shared ADDs mean the 19 separate minima cannot be added to claim a combined saving. The finite replay checks the candidate against all 712 source/helper/center input columns, confirms the paid profile and non-scalar event stream, and checks the inherited 192-bit local charge. That replay is evidence for this construction, not a formal proof of the full multiplication theorem.

## Open next questions

Can this L359 schedule be emitted by the native supplier and admitted by the full hosted recursive construction? The next step is to add the exact phase schedule to the source-bound native provider and replay both orientations with the existing hosted cost model. This package does not resolve that admission step.

## Reproduction

With Python 3.11 or newer and the repository's pinned source files:

```sh
python3 -I -O -B research/k8-zero-static-temporal-seed25/verify.py
```

Expected final lines:

```text
PASS_ZERO_STATIC_TEMPORAL_CENSUS
forward helpers 19 winner 359 delta_real -242 complex 135518 saved_vs_PR1263 484 columns 712
backward helpers 19 winner 359 delta_real -242 complex 135534 saved_vs_PR1263 484 columns 712
```

The independent small controls are:

```sh
python3 -I -O -B research/k8-zero-static-temporal-seed25/test_package.py
```

Expected: `PASS_TEMPORAL_DP_CONTROLS exhaustive=27 zero_identity=1 incomplete_schedule_rejected=1`.
The registered repository replay is `python3.12 scripts/research_package.py --package research/k8-zero-static-temporal-seed25`.

## Pins, scope, and credit

The base, selected certificate hash, PR1263 head `5fbaca13028846bddbb001e8e07addc2ab8e5816`, temporal-gauge method head PR1259 `61367611154266a982fe25e1a6243a8aad77227d`, source Git blobs, and vendored SHA-256 values are recorded in `DEPENDENCIES.json` and `SOURCES.json`. Related concurrent work varies nonzero-static coordinates: PR1350 head `64b8a55c6933ffb6d9e30fa19f85d05b572d4aa5` studies L253, and PR1353 head `efc6bfc3302a966ac0e1f5f4656e94b4cabeb9ca` studies L248. This result adds a complete census of the 19 eligible zero-static coordinates, including the independently checked L359 schedule; it does not compose the other temporal results.

The inherited all-size/compiler, native realization, hosting, precision/tape, analytic, and bit-interface assumptions remain. No runtime or whole-hosted result is claimed.

Prepared by **Cinna Davis / @1337isnot1337** with substantial **OpenAI Codex** assistance in research, exact cost analysis, implementation, verification, and writing. No independent human review is claimed. Credit Philipp / @mightyOil's PR1263 many-helper construction; Sagar Thakrar's PR1259 temporal-gauge method and PR696 lowerer; and the retained PR1094 supplier lineage. Apache-2.0; predecessor notices and source pins are retained.
