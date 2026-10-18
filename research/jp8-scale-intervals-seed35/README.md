# A paid JP8 backward accumulator rescaling

**Research note / finite scalar construction; no new kappa.** In the historical
PR626 JP8 backward word, defer the halving of `L109` across its next 55
accumulations and halve once afterward. Adjusting every addition coefficient
preserves the arbitrary-input endpoint. Composed with PR751's credited
equal-magnitude fan-in and the same work-clear elision on both words, it saves
**66 further real primitives** on this one block: **135 to 102 per component**.
Every source read, preparation, clear and final halving is charged.

This is a historical local block, not the currently selected U8 supplier.
The accepted conditional result is PR942's T37 witness,
`kappa = 1661960547713947/10^18`. No selected artifact or `upstream/` file changes.

## Exact object and comparison

The witness is the half-open event interval **[23533,23589)**, frame **1**, in
both immutable PR626 JP8 orientations. It contains one scale and 55 additions,
touching 56 logical registers plus one existing coefficient-work register.
In the backward word all 55 sources are distinct and the target is `L109`.

| Comparison, per real component | Before | After | Saving |
| --- | ---: | ---: | ---: |
| Best PR837/eligible PR882 per-macro circuit | 230 | 174 | 56 |
| Same conservative clear elision, incoming work arbitrary | 224 | 150 | 74 |
| Same clear elision, incoming work zero | 223 | 150 | 73 |
| Equal-magnitude fan-in, raw | 142 | 126 | 16 |
| Equal-magnitude fan-in, same elision, dirty work | 136 | 102 | 34 |
| Equal-magnitude fan-in, same elision, zero work | 135 | 102 | 33 |

Real and imaginary components each use the stated word. The last row gives
66 real primitives after the credited fan-in composition. Incoming work is zero at the historical per-macro
boundaries because each preceding addition clears it; the arbitrary-dirty
variant is checked separately. Elision only removes a clear already known
zero; every nonunit preparation still ends with a paid clear.

The comparator takes the shortest of all four PR837 circuits and any strict
PR882 bounded-grid improvement in its published numerator/denominator domain.
The same selection rule applies before and after. All witness coefficients
are signed powers of two, so no extrapolation of PR882's domain is needed.
The raw backward count changes from `{halve:71, double:1, copy:48, clear:55,
add:31, subtract:24}` to `{halve:24, double:9, copy:31, clear:55,
add:31, subtract:24}`. The last of the 24 halvings is restoration.

The forward transpose companion has the same raw and clear-elided counts.
PR755's adjacent equal-source/equal-magnitude preparation sharing prices this exact
forward block at 142 primitives, already below the unshared 174. PR751's
common-target dual also prices the backward block at 142. This evidence drove
one bounded pivot: apply those existing equal-magnitude cohort circuits to
both versions, then compare 142 to 126 (135 to 102 after fair elision).
The checker regenerates and independently replays all four literal words.
PR830's varying-magnitude work sharing and PR975's X4 multi-source words
are related larger classes; no superiority or composed global bill is claimed.

## Reproduce

Python 3.9+ and the standard library, from the repository root:

```sh
python3 -I -B research/jp8-scale-intervals-seed35/verify.py
```

Expected final line:

```text
PASS_JP8_SCALE_INTERVALS starts=221 intervals=557559_per_orientation backward_real_saving=66_beyond_equal_magnitude_fanin no_new_kappa
```

The offline command binds every consumed predecessor input, recomputes the
complete finite cost census, regenerates the frozen block words, prices the
fair comparisons, and runs the separate dense rational checker and controls.
No output files are written. `BLOCKS.json` holds literal input macros and
paid words; `CENSUS.json` freezes the complete cost histogram and chosen
minimum. `AUDIT.json` freezes the independent replay and prefix receipt.

## Search class and proof

The OS-random assignment seed **35** selected the complex supplier track.
The domain is every original magnitude-2 or magnitude-1/2 logical-register
scale in a maximal nonzero-frame scalar run, in both frozen 27,909-event JP8
words. It permits one pending register gauge, every later flush cutoff,
absorption into a later same-register scale, or free reset at a clear.
Copies or swaps involving that register, frame changes and non-scalar events
are barriers. Exhaustion is the stopping rule: **221 starts, 557,559 priced
intervals and 81,869 strict cost improvements per orientation**. Only the
chosen minimum receives dense endpoint and prefix replay; the census is not
a census of physically admitted or precision-safe circuits.

Maintain `x_r = 2^h y_r`, with every other gauge zero. An addition
`x_t += q x_s` becomes `y_t += q 2^(h_s-h_t) y_s`. Keep the initial scale's
sign as a paid negation. A flush pays `|h|` shifts; a terminating scale with
exponent `k` pays `|h+k|` shifts and its sign; clear erases the gauge.
Induction proves the local logical endpoint. The coefficient words overwrite
arbitrary work, read their actual sources, and clear work on exit.

The credited fan-in cohort copies its first source to W, accumulates the
remaining sources with relative signs, shifts W once, updates the target once
and clears W. Its complete cost is `m + |k| + 2` for magnitude `2^k`.
The fan-out cohort similarly shares preparation. Unit additions stay direct.
No register or helper is added. This composition groups existing updates;
the original per-macro clearing interface requires explicit integration.

The independent checker imports no search or supplier code. It separately
interprets macros and literal primitives on all **57 independent input
columns**, including arbitrary helper and work dirt. It checks every prefix's
exact rational row L1 norm and coefficient denominator. Five mutation controls per witness
cover missing restoration, wrong sign, missing preparation copy, underpriced
cost and an endpoint-correct double/halve prefix excursion, for each of four
words (twenty controls total).

## Precision limitation and remaining work

The backward block's maximum exact row L1 norm **doubles from 109/4 to 109/2**.
Its coefficient denominator remains at most 4. The forward companion's row
peak stays 5 and denominator 2. The prefix excursion control specifically
shows why endpoint equality alone does not justify a precision charge.

These are local arbitrary-input row bounds, not the inherited whole-program
cancellation-free payload envelope or an approximate rounding proof. Native
frame/array admission, grouped-macro adapters, full scalar embedding, finite
invoice, selected cold replay, hosting and outer assembly remain unchecked.
All-size compilation, common-label/mutable-source realization, restoration
tapes, precision/exact recovery, analytic transfer and bit H1-H5 remain inherited.
No new supplier moment, kappa, global optimum, runtime speedup or formal
multiplication theorem is claimed. The next useful integration check is whether
the doubled backward accumulator fits the complete provider's payload budget.

## Provenance and credit

Exact base: `bbc600db2fc15007b7c914f4f2b2ed55fa909c87`.
`SOURCES.json` records predecessor heads, all consumed byte hashes, Git blob
identities and the immutable gzip payload hash. The base retains the source
files; no predecessor code is copied or changed.

Credit Jeremy Kothe's PR622 and Chafik Boukhalfa's PR626 historical supplier,
icekylinx's scalar lineage, Sagar Thakrar's PR696 copy/unit lowering, Gareth
Davidson's PR837 four-direction comparison, Philipp / mightyOil's PR882
bounded-grid synthesis, PR839's known-zero clear removal, taizaki69's PR755
and Jeffrey Cox's PR739 sharing, Sagar Thakrar's PR751 fan-in, Ryan Haines's
PR830 transposed work, Ross Richardson's PR919 sign gauges, and
the contributors to PR949's fixed-factory scale-gauge census. The latter fixes
another topology, adapters and lowering; this result does not reopen or refute
its negative theorem. PR969's deferred permutations change a different expense.

Contributed by **Eva Ayala / ToikY**, with substantial **OpenAI Codex assistance**
in mathematics, implementation, separate checking, review and writing.
No independent human review is claimed. New material is Apache-2.0; retained
source notices and licenses continue to apply.
