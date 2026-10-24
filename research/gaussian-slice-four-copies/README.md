# The factor-4 gate absorbs g copies of the heavy slice

**Claim type:** an explicit absorption bound for one tensor sum.
**No new κ.** The trailing bound `p^{10}`, the section error, and the
ceiling `9 p^2` stay hypotheses. The selected record is `60403/20000000`.
The coefficient-9 monomials keep the published gate `16 g L ≤ p`.

## Question

#4673 puts one heavy slice below `2^{-C p}` under `4 g L ≤ p`. It leaves
the `g` copies open. Those copies add one `L`. The one-slice fourths
spend `80 p`, and `8 L ≤ p` turns the new term `32 L` into `4 p`. The
named step is to test `16 p^2 - 84 p - 64` at `p = 64`.

This `4` is the coefficient of `g L`. It is not a three-bit majorant of
the ceiling `9`. #4495 still rejects three bits for that ceiling, because
`9 > 8`, and it still uses four bits because `9 < 16`.

## Lemma

Let `p ≥ 2`, `g ≥ 1`, `K ≥ 0` and `C ≥ 0` be integers, and let
`L = ceil(log2 p)`. If

```text
p ≥ max(64, 4K + 2C)    and    4 g L ≤ p,
```

then `g` copies of

```text
(p^{10})^{g-1} p^6 (1 + p^4) exp(K p - p^2)
```

are strictly below `2^{-C p}`. The exponent is at most `-C p - 1`.

The gate is wider than the factor-5 gate. At `p = 84` and `g = 3`,
`L = 7`, so `4 g L = 84 ≤ 84` while `5 g L = 105 > 84`. The copies
exponent there is `-6838`.

At `p = 2` and `g = 2` the hypothesis fails, and the two copies are larger
than `1`.

## Proof

#4673 puts one slice strictly below `2^{E_0}` for

```text
E_0 = 10 g L + 1 + 2 K p - p^2.
```

The same gate forces `g < 2^L`. Indeed `p ≤ 2^L` and `4 L > 1`, so
`4 g L ≤ p` implies `g < 2^L`. Multiplying by `g` therefore adds one
`L`. The copies are strictly below `2^E` for

```text
E = 10 g L + L + 1 + 2 K p - p^2.
```

Clear `32 (E + C p)`, four times `8 (E + C p)`. As in the one-slice
argument, `320 g L ≤ 80 p` and the linear term contributes at most
`16 p^2`. The new piece is `32 L`. For every integer `p ≥ 64`,
`8 L ≤ p`, so `32 L = 4 · 8 L ≤ 4 p`. The base of that comparison is
`8 · 7 = 56 ≤ 64 = 2^6`. If `8 (m + 1) ≤ 2^m`, then

```text
8 (m + 2) = 8 (m + 1) + 8 ≤ 2^m + 8 ≤ 2^{m + 1},
```

because `8 ≤ 2^6`. Thus `8 (m + 1) ≤ 2^m` for every integer `m ≥ 6`.
When `2^m ≤ p < 2^{m + 1}`, the level is `m` at the power of two and
`m + 1` after it, and both are at most `p`.

`32 (E + C p)` is therefore at most

```text
80 p + 4 p + 32 - 16 p^2 = -(16 p^2 - 84 p - 32).
```

The polynomial `16 p^2 - 84 p - 64` equals `60096` at `p = 64` and
then increases by `32 p - 68`. Thus `16 p^2 - 84 p - 32 ≥ 32` for every
integer `p ≥ 64`, so `32 (E + C p) ≤ -32` and `E ≤ -C p - 1`.

At `p = 2` and `g = 2`, `4 g L = 8 > 2` and the formal exponent is
`18`. The series of `e` through `1/6!` is `13699/5040`. The later ratios
are at most `1/8`, so the tail is strictly below `8/(7 · 5040)`. The gap
up to `3` is `1421/5040`, and `8 < 1421 · 7`, so `e < 3` and `exp(4) < 81`.
One slice at this point has polynomial part `2^{10} · 1088`, so two copies
have polynomial part `2 · 2^{10} · 1088 > 81`. The copies are larger than `1`.

## Not covered

- A gate factor smaller than `4`. The one-slice exponent still spends
  `10 g L`. The coefficient-9 monomials still use `16`.
- A proof that `||H^{-1}||_2 ≤ p^{10}`. HALO assumes it.
- The section error `p^6 exp(-p^2)` and the leading ceiling `9 p^2`.
- Editing the #4100 notes, or the #4495 gate.
- Any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/gaussian-slice-four-copies --check-only
python3.12 -B scripts/research_package.py --package research/gaussian-slice-four-copies
```

Base `b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`, priority revision 7.
Upstream was fetched at 2026-10-22T15:27:47Z and was that commit. The
pre-submit fetch at 2026-10-22T15:29:17Z was the same commit. The pinned
blobs for the selected record, the catalogue, both source READMEs, and
HALO.md match that main. The selection is κ = `60403/20000000`.

Overlap snapshot: open PRs fetched 2026-10-22T15:28:23Z (445 records) and
discussions fetched 2026-10-22T15:29:09Z (3600 records). Terms
`16 p^2 - 84 p - 64`, `slice-four-copies`, and `6838` reported 18 matches
and showed 8. The first two were this README and this TASK. One shown hit
is the #4673 DONE (discussioncomment-19126503). The other shown hits
contain the digits `6838` inside a comment URL, a local digit run, or
unrelated decimals. A second search of the same cache, offline, dropped
`6838`. It returned this README, this TASK, and that #4673 DONE. That
note leaves these copies open and names the test at `p = 64`. The handoff
thread, reread at the pre-submit fetch, still ends at that #4673 DONE.
The open-PR list at that time starts at #4674, a typed-quotient price.
No matches is not a novelty certificate.

## Open next questions

1. **Does `3 g L ≤ p` already absorb one heavy slice?** The exponent
   spends `10 g L`. The first step is the thirds identity
   `240 g L = 80 · 3 g L`, then the test of `12 p^2 - 80 p - 48` at
   `p = 64`. Do not change the coefficient-9 monomial gate.

## Credit

- The factor-4 slice, and this question, are #4673's.
- The factor-5 copies are #4670's.
- The unequal factor `1 + p^4` is #4524's.
- The published gate `16 g L ≤ p` is #4495's. It is unchanged.
- The ceiling `9 p^2` is #4493's.
- The written tail `p^{10} exp(-p^2)` is #4100's.

Prepared by James Reed with substantial Cursor Grok 4.7 assistance. Apache-2.0.
