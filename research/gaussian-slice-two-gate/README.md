# The factor-2 gate absorbs one heavy slice

**Claim type:** an explicit absorption bound for one tensor slice.
**No new κ.** The trailing bound `p^{10}`, the section error, and the
ceiling `9 p^2` stay hypotheses. The selected record is `60403/20000000`.
The coefficient-9 monomials keep the published gate `16 g L ≤ p`.

## Question

#4680 absorbs the `g` copies under `3 g L ≤ p`, and asks whether one heavy
slice already fits under `2 g L ≤ p`. The exponent spends `10 g L`. The
named step is the halves identity `160 g L = 80 · 2 g L`, then the test of
`8 p^2 - 80 p - 32` at `p = 64`.

This `2` is the coefficient of `g L`. It is not a two-bit majorant of the
ceiling `9`, and it is not a two-power majorant of `C`. #4495 still
rejects three bits for that ceiling, because `9 > 8`, and it still uses
four bits because `9 < 16`.

## Lemma

Let `p ≥ 2`, `g ≥ 1`, `K ≥ 0` and `C ≥ 0` be integers, and let
`L = ceil(log2 p)`. If

```text
p ≥ max(64, 4K + 2C)    and    2 g L ≤ p,
```

then

```text
(p^{10})^{g-1} p^6 (1 + p^4) exp(K p - p^2)
```

is strictly below `2^{-C p}`. The case `K = 0` is the slice in the
question. The exponent is at most `-C p - 1`.

This hypothesis is wider than the factor-3 gate. At `p = 84` and `g = 6`,
`L = 7`, so `2 g L = 84 ≤ 84` while `3 g L = 126 > 84`. The exponent
there is `-6635`. The factor-3 comparison `240 g L ≤ 80 p` fails at that
point: `10080 > 6720`.

At `p = 2` and `g = 1` the factor holds, `2 g L = 2 ≤ 2`, but `p < 64`.
The slice there is larger than `1`, so the floor `p ≥ 64` is part of the
hypothesis.

## Proof

Dropping the `1` in `1 + p^4` leaves exactly `p^{10 g}`. Since
`1 + p^4 < 2 p^4 ≤ 2^{4 L + 1}` and `p ≤ 2^L`, the polynomial part is
strictly below `2^{10 g L + 1}`. With `exp(-p^2) < 2^{-p^2}` and
`exp(K p) ≤ 2^{2 K p}`, the slice is strictly below `2^E` for

```text
E = 10 g L + 1 + 2 K p - p^2.
```

Clear `16 (E + C p)`, which is two times `8 (E + C p)`. The new gate
gives `160 g L = 80 · 2 g L ≤ 80 p`. The identity
`16 (2 K + C) = 8 (4 K + 2 C)` gives a linear contribution of at most
`8 p^2` once `p ≥ 4 K + 2 C`. The constant `1` contributes `16`. The
sum is at most

```text
-(8 p^2 - 80 p - 16).
```

The polynomial `8 p^2 - 80 p - 32` equals `27616` at `p = 64` and then
increases by `16 p - 72`. Thus `8 p^2 - 80 p - 16 ≥ 16` for every
integer `p ≥ 64`, so `16 (E + C p) ≤ -16` and `E ≤ -C p - 1`.

At `p = 2` and `g = 1`, the series of `e` through `1/6!` is
`13699/5040`. Terms after that have ratios at most `1/8`, so the tail is
strictly below `8/(7 · 5040)`. The gap up to `3` is `1421/5040`, and
`8 < 1421 · 7`, so `e < 3` and `exp(4) < 81`. The slice equals
`1088 exp(-4)`, and `81 < 1088`, so the slice is larger than `1`.

## Not covered

- The `g` copies of this slice under `2 g L ≤ p`.
- A gate factor smaller than `2`.
- A proof that `||H^{-1}||_2 ≤ p^{10}`. HALO assumes it.
- The section error `p^6 exp(-p^2)` and the leading ceiling `9 p^2`.
- Editing the #4100 notes, or the #4495 gate.
- Any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/gaussian-slice-two-gate --check-only
python3.12 -B scripts/research_package.py --package research/gaussian-slice-two-gate
```

Base `b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`, priority revision 7.
Upstream was fetched at 2026-10-22T15:55:37Z and was that commit. The
pre-submit fetch at 2026-10-22T15:57:14Z was the same commit. The pinned
blobs for the selected record, the catalogue, both source READMEs, and
HALO.md match that main. The selection is κ = `60403/20000000`.

Overlap snapshot: open PRs fetched 2026-10-22T15:56:16Z (451 records) and
discussions fetched 2026-10-22T15:57:06Z (3613 records). Terms
`8 p^2 - 80 p - 32`, `slice-two-gate`, and `6635` reported 30 matches and
showed 8. The first two were this README and this TASK. One shown hit is
the #4680 DONE (discussioncomment-19126967). The other shown hits contain
the digits `6635` inside a stock total, a case count, a κ decimal, or a
local digit run. A second search of the same cache, offline, dropped
`6635`. It returned this README, this TASK, and that #4680 DONE. That
note leaves this one-slice question open and names the test at `p = 64`.
The handoff thread, reread at the pre-submit fetch, ends at a Windows
test-lifetime DONE (discussioncomment-19127249). The slice note before
the unrelated claims is the #4680 DONE. Open PR #4683 is that Windows
test. No matches is not a novelty certificate.

## Open next questions

1. **Do the `g` copies stay below `2^{-C p}` under `2 g L ≤ p`?** The
   one-slice halves spend `80 p`. Copies add one `L`, and `8 L ≤ p`
   turns `16 L` into `2 p`. The first step is to test
   `8 p^2 - 82 p - 32` at `p = 64`. Do not change the coefficient-9
   monomial gate.

## Credit

- The factor-3 copies, and this question, are #4680's.
- The factor-3 slice is #4677's.
- The unequal factor `1 + p^4` is #4524's.
- The published gate `16 g L ≤ p` is #4495's. It is unchanged.
- The ceiling `9 p^2` is #4493's.
- The written tail `p^{10} exp(-p^2)` is #4100's.

Prepared by James Reed with substantial Cursor Grok 4.7 assistance. Apache-2.0.
