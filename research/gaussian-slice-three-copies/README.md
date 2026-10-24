# The factor-3 gate absorbs g copies of the heavy slice

**Claim type:** an explicit absorption bound for one tensor sum.
**No new κ.** The trailing bound `p^{10}`, the section error, and the
ceiling `9 p^2` stay hypotheses. The selected record is `60403/20000000`.
The coefficient-9 monomials keep the published gate `16 g L ≤ p`.

## Question

#4677 puts one heavy slice below `2^{-C p}` under `3 g L ≤ p`. It leaves
the `g` copies open. Those copies add one `L`. The one-slice thirds
spend `80 p`, and `8 L ≤ p` turns the new term `24 L` into `3 p`. The
named step is to test `12 p^2 - 83 p - 48` at `p = 64`.

This `3` is the coefficient of `g L`. It is not a three-bit majorant of
the ceiling `9`. #4495 still rejects three bits for that ceiling, because
`9 > 8`, and it still uses four bits because `9 < 16`.

## Lemma

Let `p ≥ 2`, `g ≥ 1`, `K ≥ 0` and `C ≥ 0` be integers, and let
`L = ceil(log2 p)`. If

```text
p ≥ max(64, 4K + 2C)    and    3 g L ≤ p,
```

then `g` copies of

```text
(p^{10})^{g-1} p^6 (1 + p^4) exp(K p - p^2)
```

are strictly below `2^{-C p}`. The exponent is at most `-C p - 1`.

The gate is wider than the factor-4 gate. At `p = 84` and `g = 4`,
`L = 7`, so `3 g L = 84 ≤ 84` while `4 g L = 112 > 84`. The copies
exponent there is `-6768`.

At `p = 2` and `g = 2` the hypothesis fails, and the two copies are larger
than `1`.

## Proof

#4677 puts one slice strictly below `2^{E_0}` for

```text
E_0 = 10 g L + 1 + 2 K p - p^2.
```

The same gate forces `g < 2^L`. Indeed `p ≤ 2^L` and `3 L > 1`, so
`3 g L ≤ p` implies `g < 2^L`. Multiplying by `g` therefore adds one
`L`. The copies are strictly below `2^E` for

```text
E = 10 g L + L + 1 + 2 K p - p^2.
```

Clear `24 (E + C p)`, three times `8 (E + C p)`. As in the one-slice
argument, `240 g L ≤ 80 p` and the linear term contributes at most
`12 p^2`. The new piece is `24 L`. For every integer `p ≥ 64`,
`8 L ≤ p`, so `24 L = 3 · 8 L ≤ 3 p`. The base of that comparison is
`8 · 7 = 56 ≤ 64 = 2^6`. If `8 (m + 1) ≤ 2^m`, then

```text
8 (m + 2) = 8 (m + 1) + 8 ≤ 2^m + 8 ≤ 2^{m + 1},
```

because `8 ≤ 2^6`. Thus `8 (m + 1) ≤ 2^m` for every integer `m ≥ 6`.
When `2^m ≤ p < 2^{m + 1}`, the level is `m` at the power of two and
`m + 1` after it, and both are at most `p`.

`24 (E + C p)` is therefore at most

```text
80 p + 3 p + 24 - 12 p^2 = -(12 p^2 - 83 p - 24).
```

The polynomial `12 p^2 - 83 p - 48` equals `43792` at `p = 64` and
then increases by `24 p - 71`. Thus `12 p^2 - 83 p - 24 ≥ 24` for every
integer `p ≥ 64`, so `24 (E + C p) ≤ -24` and `E ≤ -C p - 1`.

At `p = 2` and `g = 2`, `3 g L = 6 > 2` and the formal exponent is
`18`. The series of `e` through `1/6!` is `13699/5040`. The later ratios
are at most `1/8`, so the tail is strictly below `8/(7 · 5040)`. The gap
up to `3` is `1421/5040`, and `8 < 1421 · 7`, so `e < 3` and `exp(4) < 81`.
One slice at this point has polynomial part `2^{10} · 1088`, so two copies
have polynomial part `2 · 2^{10} · 1088 > 81`. The copies are larger than `1`.

## Not covered

- A gate factor smaller than `3`. The one-slice exponent still spends
  `10 g L`. The coefficient-9 monomials still use `16`.
- A proof that `||H^{-1}||_2 ≤ p^{10}`. HALO assumes it.
- The section error `p^6 exp(-p^2)` and the leading ceiling `9 p^2`.
- Editing the #4100 notes, or the #4495 gate.
- Any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/gaussian-slice-three-copies --check-only
python3.12 -B scripts/research_package.py --package research/gaussian-slice-three-copies
```

Base `b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`, priority revision 7.
Upstream was fetched at 2026-10-22T15:41:13Z and was that commit. The
pre-submit fetch at 2026-10-22T15:42:49Z was the same commit. The pinned
blobs for the selected record, the catalogue, both source READMEs, and
HALO.md match that main. The selection is κ = `60403/20000000`.

Overlap snapshot: open PRs fetched 2026-10-22T15:41:50Z (449 records) and
discussions fetched 2026-10-22T15:42:40Z (3608 records). Terms
`12 p^2 - 83 p - 48`, `slice-three-copies`, and `6768` reported 98 matches
and showed 8. The first two were this README and this TASK. The other
shown hits contain the digits `6768` inside κ decimals near `0.0016768`.
A second search of the same cache, offline, dropped `6768`. It returned
this README, this TASK, and the #4677 DONE
(discussioncomment-19126786). That note leaves these copies open and names
the test at `p = 64`. The handoff thread, reread at the pre-submit fetch,
ends at a lee-phys claim on the #4628 block-3 small-unit question
(discussioncomment-19126887). The slice note before it is the #4677 DONE.
Open PRs #4679 and #4678 are a Windows export test and a Schur count.
No matches is not a novelty certificate.

## Open next questions

1. **Does `2 g L ≤ p` already absorb one heavy slice?** The exponent
   spends `10 g L`. The first step is the halves identity
   `160 g L = 80 · 2 g L`, then the test of `8 p^2 - 80 p - 32` at
   `p = 64`. Do not change the coefficient-9 monomial gate.

## Credit

- The factor-3 slice, and this question, are #4677's.
- The factor-4 copies are #4676's.
- The unequal factor `1 + p^4` is #4524's.
- The published gate `16 g L ≤ p` is #4495's. It is unchanged.
- The ceiling `9 p^2` is #4493's.
- The written tail `p^{10} exp(-p^2)` is #4100's.

Prepared by James Reed with substantial Cursor Grok 4.7 assistance. Apache-2.0.
