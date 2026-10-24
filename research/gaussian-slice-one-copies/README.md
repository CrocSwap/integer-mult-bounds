# The factor-1 gate absorbs g copies of the heavy slice

**Claim type:** an explicit absorption bound for one tensor sum.
**No new κ.** The trailing bound `p^{10}`, the section error, and the
ceiling `9 p^2` stay hypotheses. The selected record is `60403/20000000`.
The coefficient-9 monomials keep the published gate `16 g L ≤ p`.

## Question

#4693 puts one heavy slice below `2^{-C p}` under `g L ≤ p`. It leaves
the `g` copies open. Those copies add one `L` once `g ≤ 2^L`. The
one-slice eighths spend `80 p`, and `8 L ≤ p` turns the new term `8 L`
into `p`. The named step is to test `4 p^2 - 81 p - 16` at `p = 64`.

This `1` is the coefficient of `g L`. It is not a one-bit majorant of the
ceiling `9`, and it is not a two-power majorant of `C`. #4495 still
rejects three bits for that ceiling, because `9 > 8`, and it still uses
four bits because `9 < 16`.

## Lemma

Let `p ≥ 2`, `g ≥ 1`, `K ≥ 0` and `C ≥ 0` be integers, and let
`L = ceil(log2 p)`. If

```text
p ≥ max(64, 4K + 2C)    and    g L ≤ p,
```

then `g` copies of

```text
(p^{10})^{g-1} p^6 (1 + p^4) exp(K p - p^2)
```

are strictly below `2^{-C p}`. The exponent is at most `-C p - 1`.

The gate is wider than the factor-2 gate. At `p = 84` and `g = 12`,
`L = 7`, so `g L = 84 ≤ 84` while `2 g L = 168 > 84`. The copies
exponent there is `-6208`.

At `p = 2` and `g = 1` the factor holds, `g L = 1 ≤ 2`, but `p < 64`.
That one copy is larger than `1`, so the floor `p ≥ 64` is part of the
hypothesis.

## Proof

#4693 puts one slice strictly below `2^{E_0}` for

```text
E_0 = 10 g L + 1 + 2 K p - p^2.
```

The same gate forces `g ≤ 2^L`. Indeed `p ≤ 2^L`. If `g ≥ 2^L + 1`,
then `g L ≥ (2^L + 1) L ≥ 2^L + 1 > p`. It does not always force the
stricter `g < 2^L`: at `p = 2` and `g = 2`, `L = 1` and `g = 2^L`. The
slice inequality is already strict, so `g` copies are still strictly
below `g · 2^{E_0} ≤ 2^{E_0 + L}`. The copies are strictly below `2^E`
for

```text
E = 10 g L + L + 1 + 2 K p - p^2.
```

Clear `8 (E + C p)`, one times the eighths. As in the one-slice
argument, `80 g L ≤ 80 p` and the linear term contributes at most
`4 p^2`. The new piece is `8 L`. For every integer `p ≥ 64`,
that piece is at most `p`. The base of that comparison is
`8 · 7 = 56 ≤ 64 = 2^6`. If `8 (m + 1) ≤ 2^m`, then

```text
8 (m + 2) = 8 (m + 1) + 8 ≤ 2^m + 8 ≤ 2^{m + 1},
```

because `8 ≤ 2^6`. Thus `8 (m + 1) ≤ 2^m` for every integer `m ≥ 6`.
When `2^m ≤ p < 2^{m + 1}`, the level is `m` at the power of two and
`m + 1` after it, and both are at most `p`.

`8 (E + C p)` is therefore at most

```text
80 p + p + 8 - 4 p^2 = -(4 p^2 - 81 p - 8).
```

The polynomial `4 p^2 - 81 p - 16` equals `11184` at `p = 64` and
then increases by `8 p - 77`. Thus `4 p^2 - 81 p - 8 ≥ 8` for every
integer `p ≥ 64`, so `8 (E + C p) ≤ -8` and `E ≤ -C p - 1`.

At `p = 2` and `g = 1`, the series of `e` through `1/6!` is
`13699/5040`. The later ratios are at most `1/8`, so the tail is
strictly below `8/(7 · 5040)`. The gap up to `3` is `1421/5040`, and
`8 < 1421 · 7`, so `e < 3` and `exp(4) < 81`. The one copy is the slice
`1088 exp(-4)`, and `81 < 1088`, so it is larger than `1`.

## Not covered

- A gate factor smaller than `1`. Factor `1` is the smallest positive
  integer coefficient of `g L`. The coefficient-9 monomials still use
  `16`.
- A proof that `||H^{-1}||_2 ≤ p^{10}`. HALO assumes it.
- The section error `p^6 exp(-p^2)` and the leading ceiling `9 p^2`.
- Editing the #4100 notes, or the #4495 gate.
- Any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/gaussian-slice-one-copies --check-only
python3.12 -B scripts/research_package.py --package research/gaussian-slice-one-copies
```

Base `b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`, priority revision 7.
Upstream was fetched at 2026-10-22T16:11:48Z and was that commit. The
pinned blobs for the selected record, the catalogue, both source READMEs,
and HALO.md match that main. The selection is κ = `60403/20000000`.

Overlap snapshot: open PRs fetched 2026-10-22T16:14:04Z (462 records) and
discussions fetched 2026-10-22T16:14:51Z (3620 records). Terms
`4 p^2 - 81 p - 16`, `slice-one-copies`, and `6208` reported 31 matches and
showed 31. The first two were this README and this TASK. One shown hit is
the #4693 DONE (discussioncomment-19127704). The other shown hits contain
the digits `6208` inside a commit hash, a κ decimal, or a local digit run.
A second search of the same cache, offline, dropped `6208`. It returned
this README, this TASK, and that #4693 DONE. That note leaves these copies
open and names the test at `p = 64`. No matches is not a novelty certificate.

## Open next questions

No further positive integer coefficient of `g L` remains below `1`. A
fractional coefficient is a different gate and is not posed here. The
tail `p^{10}` and the section error stay hypotheses.

## Credit

- The factor-1 slice, and this question, are #4693's.
- The factor-2 copies are #4687's.
- The unequal factor `1 + p^4` is #4524's.
- The published gate `16 g L ≤ p` is #4495's. It is unchanged.
- The ceiling `9 p^2` is #4493's.
- The written tail `p^{10} exp(-p^2)` is #4100's.

Prepared by James Reed with substantial Cursor Grok 4.7 assistance. Apache-2.0.
