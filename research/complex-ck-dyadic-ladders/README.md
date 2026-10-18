# Varying dyadic coefficient ladders in the selected CK supplier

The selected CK scalar program repeatedly prepares different powers-of-two
multiples of an unchanged source. This package retains one coefficient-work
value across contiguous additions and halves/doubles it when that costs less
than clearing and preparing the next value. It changes **743 runs containing
10,124 additions**, with exact arbitrary-input equivalence in both orientations.

**Finite local circuit improvement / research note; no new kappa.**

| CK scalar program | Selected primitive count | Ladder count | Saved | Reduction |
| --- | ---: | ---: | ---: | ---: |
| Forward | 224,938 | 211,168 | 13,770 | 6.12% |
| Backward / inverse-transpose | 224,986 | 157,840 | 67,146 | 29.84% |

Counts are real-component primitives per local program invocation. Every
source addition, work initialization, halving/doubling, signed target update
and final work clear is included. These are circuit counts, not timings.
The two directions execute their own compiled circuits and are checked against
their own arbitrary-input maps; reversing the forward implementation is not
assumed to produce the backward implementation.

## Reproduce

From the repository root, with Python 3.11+ and no external packages:

```sh
python3 -I -B research/complex-ck-dyadic-ladders/verify.py
python3 -I -B research/complex-ck-dyadic-ladders/check_columns.py
```

The check is offline and writes nothing. Expected final line:

```text
PASS_CK_DYADIC_LADDERS blocks=743 saved=13770,67146 columns=716+9 controls=13
PASS_CK_LADDER_COLUMNS blocks=743 columns=11610 missing_clear_rejections=743
```

`RESULT.json` records every half-open **zero-based emitted-event interval**,
source, frame, event hash, complete counts, and exact work-prefix bounds.
The original event streams are retained in the repository's selected #626
evidence. `SOURCES.json` pins their full decompressed payloads, their native
word, selected SPEC, receipts and original emitter/auditor. Gzip header or
compression-level changes do not invalidate an otherwise identical payload.
The code checks the additional binding from the native/program hashes to SPEC.

An optional `--write-receipt /new/path.json` writes the same regenerated receipt
to a new file with exclusive creation. Existing files are never overwritten.
Default verification compares every field of the freshly computed receipt.

## Exact local construction

Consider consecutive operations, in their existing order,

```text
t_i += q_i * s
```

The source `s` is never a target in the run. All operations have the same
frame, every `q_i` is nonzero and non-unit, and each ratio
`|q_(i+1) / q_i|` is a power of two. We restrict this contribution to live
registers `L`; center registers and every non-scalar event split the run.
Maximal runs containing no profitable change of magnitude are not selected.

Let `P(q)` be the number of real-scalar operations used by the original
positive binary-Horner preparation of `|q|s`, including its initial clear:

```text
P(q) = 1 + (bit_length(a)-1) + popcount(a) + log2(b),
where |q| = a/b in lowest terms.
```

The original addition costs `P(q)+2`: preparation, signed accumulation, clear.
After accumulating the previous coefficient, either retain the work value and
shift it by `k = log2(|q_next/q_previous|)`, or execute the original
clear-and-prepare transition. The transition cost is therefore

```text
min(|k|, 1 + P(q_next)).
```

The full run costs `P(q_0) + number_of_targets + 1` plus those transition
costs. The real-component invoice multiplies this count by two. No leading
copy shortcut, signed-digit preparation, reordered target updates or new
scratch register is used.

For example, forward events `[18860,18863)` read register 470 into registers
655, 97, 656 with coefficients `-2`, `-1/4`, `-1/2`, all at frame 1. Prepare
`2s`, accumulate, halve three times, accumulate, double once, accumulate and
clear. This costs **22 real-component primitives instead of 32**.

### Boundary map and prefix proof

The initial clear removes any incoming coefficient-work value. Inductively,
the work value at update `i` equals `|q_i|s`: preparation establishes the first
value, a power-of-two transition establishes the next, and a reset uses the
original preparation. The signed update is exactly the original target update.
Because the source is unchanged, repeated targets are allowed. Final clearing
gives the original block boundary for every live register and arbitrary initial
private work.

During a scale transition, the work magnitude lies between its two endpoint
magnitudes. Both endpoint values occur in the original binary-Horner traces.
The original preparation for a normalized coefficient `a/b` reaches `as`,
and `b>=1`. Thus every new work prefix is bounded by the original run's
maximum `max(a_i)|s|`. Target writes retain their original order and values,
so no new target prefix occurs. The source and all other registers are fixed.
The verifier checks the normalized work value at **every ordered target
write** and checks every intermediate work value against this bound.

The fresh full-program positive-envelope replay gives exactly the original
bounds: `920709848294` forward and `146068000389976309073/32` backward. Both
remain below the inherited 192-bit local allowance. This preserves the
existing numerical envelope; it does not establish an all-size tape theorem.

## Coverage and relation to concurrent work

The OS seed is 36; its parity selected CK. Both 27,256-event streams are
exhaustively scanned. There is no sampled parameter search or timeout.
An independent adjacent-edge census checks maximality, complete coverage and
the per-run cost formula without calling the circuit's grouping functions.

| Orientation | Selected varying runs | Changed additions | Savings with equal-magnitude reuse alone on these runs | Additional saving from varying magnitudes |
| --- | ---: | ---: | ---: | ---: |
| Forward | 463 | 2,275 | 7,758 | 6,012 |
| Backward | 280 | 7,849 | 54,550 | 12,596 |

All 463 forward runs are in `full_frame_cleanup`. All 280 backward runs are
in `zero_frame_precondition`, an additional phase outside the cleanup-focused
scope of #722 and #739. The backward source remains fixed through
each run just as in the forward construction; no transposition shortcut or
common-target fan-in rewrite is used.

This credits and extends the same-magnitude reuse idea in
[#722](https://github.com/CrocSwap/integer-mult-bounds/pull/722), which studies
JP8 cleanup. The comparator above is freshly constructed on these exact CK
runs; it is not #722's JP8 result. Equal-only maximal runs are excluded, making
the varying-magnitude contribution explicit. Its incremental saving is
**18,608 real primitives across the two orientations**.

While this implementation was being verified, [#739](https://github.com/CrocSwap/integer-mult-bounds/pull/739)
published the same power-of-two rescaling mechanism for **JP8 forward cleanup**.
Credit Jeffrey Cox / @namredips for that concurrent contribution. This package
adds separately implemented **CK coverage in both orientations**, including
the zero-frame preconditioning phase, exact bound preservation and a fresh
11,610-column block verification. It claims no priority for the general
rescaling idea. #739's JP8 counts and restricted cleanup search are not
combined with the CK counts above.

The final pre-submission scan also found
[#755](https://github.com/CrocSwap/integer-mult-bounds/pull/755) by @taizaki69,
which independently covers JP8 equal-magnitude sharing in both orientations,
including backward preconditioning, combined with #696's copy initialization.
That broader phase coverage is credited. The present package covers CK and
varying magnitudes under the original binary-Horner preparation. It makes no
priority claim for backward-phase reuse, and imports no #755 code or counts.

[#696](https://github.com/CrocSwap/integer-mult-bounds/pull/696) changes the
single-macro preparation and unit cases; [#723](https://github.com/CrocSwap/integer-mult-bounds/pull/723)
uses signed-digit JP8 numerators; [#681](https://github.com/CrocSwap/integer-mult-bounds/pull/681)
resynthesizes a raw factory word. Their implementations are not imported and
their reported savings are not added here. [#719](https://github.com/CrocSwap/integer-mult-bounds/pull/719)
rules out specific CK macro-pair replacements; this retains every scalar macro
and changes its internal coefficient-work interface. [#698](https://github.com/CrocSwap/integer-mult-bounds/pull/698)
studies fixed B-frame costs. None is a dependency of this replay.
Concurrent [#734](https://github.com/CrocSwap/integer-mult-bounds/pull/734)
changes single-macro signed-Horner preparation;
[#750](https://github.com/CrocSwap/integer-mult-bounds/pull/750) relocates a
CK live-register scale; [#751](https://github.com/CrocSwap/integer-mult-bounds/pull/751)
uses a JP8 backward common-target reverse-Horner construction. They are
distinct from the unchanged-source CK runs here. No combined invoice is claimed.

## Verification and scope

- Sparse exact rational replay checks both original and lowered scalar
  projections on **716 live input columns**, including all 492 dirty helpers,
  plus **nine independent private input columns** for eight centers and work.
  Final centers/work are zero. Every live output matches the required shear.
- Every changed block is separately checked for source invariance, common
  frame, ordered target writes, exact coefficients, work clearing and prefix
  domination. The checker does not call the constructor's preparation or
  transition logic. Full-program primitive costs and positive prefix bounds
  are recomputed and compared with the pinned selected receipts.
- A separate flat-vector, column-oriented interpreter in `check_columns.py`
  checks all **11,610 touched-register/private-work basis cases** across the
  743 blocks. It also rejects omission of the final clear in every block.
  It shares only the candidate circuit constructor; it does not import the
  normalized proof checker, sparse interpreter or prefix machinery.
- Thirteen controls reject missing initialization/final clearing, wrong scale,
  sign, target order, undercharging, endpoint-neutral prefix inflation, frame
  or source changes, source writes, bad coefficient domains and phase crossing.
- Every non-scalar event remains at its existing boundary. The original paid
  child histogram is recounted in each orientation. This package uses the
  existing selected frame/wrapper evidence; it does not regenerate the native
  provider or reprove the Clifford/hosting layer.

The coefficient stream is clean at each fused-block boundary. Intermediate
original scalar-macro boundaries inside a block no longer require a clear;
the new block contract explicitly checks that no frame change, recursive call,
adapter, center lifetime event or other consumer is crossed. A production
emitter must adopt that contract and regenerate its invoice/admission receipts
before using these lower counts in an accepted supplier. That integration is
outside this isolated research package.

The scalar word, native frames, helper count, recursive profile and selected
kappa `51110230636731/31250000000000000` are unchanged. No optimality,
practical speedup, new asymptotic exponent or formal multiplication theorem
is claimed. Uniform compiler/common-label/mutable-basis realization,
whole-call hosting, precision/tape/recovery, bit-supplier and analytic-transfer
obligations remain inherited. See `NOTICE.md`, `CLAIM.md` and `VALIDATION.md`.
