# The factor-6 gate absorbs g copies of the heavy slice

**Claim type:** an explicit absorption bound for one tensor sum.
**No new κ.** The trailing bound `p^{10}`, the section error, and the
ceiling `9 p^2` stay hypotheses. The selected record is `60403/20000000`.
The coefficient-9 monomials keep the published gate `16 g L ≤ p`.

## Question

#4667 puts one heavy slice below `2^{-C p}` under `6 g L ≤ p`. It leaves
the `g` copies open. Those copies add one `L`. The one-slice sixths
spend `80 p`, and `8 L ≤ p` turns the new term `48 L` into `6 p`. The
named step is to test `24 p^2 - 86 p - 96` at `p = 64`.

This `6` is the coefficient of `g L`. It is not a three-bit majorant of
the ceiling `9`. #4495 still rejects three bits for that ceiling, because
`9 > 8`, and it still uses four bits because `9 < 16`.

## Lemma

Let `p ≥ 2`, `g ≥ 1`, `K ≥ 0` and `C ≥ 0` be integers, and let
`L = ceil(log2 p)`. If

```text
p ≥ max(64, 4K + 2C)    and    6 g L ≤ p,
```

then `g` copies of

```text
(p^{10})^{g-1} p^6 (1 + p^4) exp(K p - p^2)
```

are strictly below `2^{-C p}`. The exponent is at most `-C p - 1`.

The gate is wider than the factor-7 gate. At `p = 84` and `g = 2`,
`L = 7`, so `6 g L = 84 ≤ 84` while `7 g L = 98 > 84`. The copies
exponent there is `-6908`.

At `p = 2` and `g = 2` the hypothesis fails, and the two copies are larger
than `1`.

## Proof

#4667 puts one slice strictly below `2^{E_0}` for

```text
E_0 = 10 g L + 1 + 2 K p - p^2.
```

The same gate forces `g < 2^L`. Indeed `p ≤ 2^L` and `6 L > 1`, so
`6 g L ≤ p` implies `g < 2^L`. Multiplying by `g` therefore adds one
`L`. The copies are strictly below `2^E` for

```text
E = 10 g L + L + 1 + 2 K p - p^2.
```

Clear `48 (E + C p)`, six times `8 (E + C p)`. As in the one-slice
argument, `480 g L ≤ 80 p` and the linear term contributes at most
`24 p^2`. The new piece is `48 L`. For every integer `p ≥ 64`,
`8 L ≤ p`, so `48 L = 6 · 8 L ≤ 6 p`. The base of that comparison is
`8 · 7 = 56 ≤ 64 = 2^6`. If `8 (m + 1) ≤ 2^m`, then

```text
8 (m + 2) = 8 (m + 1) + 8 ≤ 2^m + 8 ≤ 2^{m + 1},
```

because `8 ≤ 2^6`. Thus `8 (m + 1) ≤ 2^m` for every integer `m ≥ 6`.
When `2^m ≤ p < 2^{m + 1}`, the level is `m` at the power of two and
`m + 1` after it, and both are at most `p`.

`48 (E + C p)` is therefore at most

```text
80 p + 6 p + 48 - 24 p^2 = -(24 p^2 - 86 p - 48).
```

The polynomial `24 p^2 - 86 p - 96` equals `92704` at `p = 64` and
then increases by `48 p - 62`. Thus `24 p^2 - 86 p - 48 ≥ 48` for every
integer `p ≥ 64`, so `48 (E + C p) ≤ -48` and `E ≤ -C p - 1`.

At `p = 2` and `g = 2`, `6 g L = 12 > 2` and the formal exponent is
`18`. The series of `e` through `1/6!` is `13699/5040`. The later ratios
are at most `1/8`, so the tail is strictly below `8/(7 · 5040)`. The gap
up to `3` is `1421/5040`, and `8 < 1421 · 7`, so `e < 3` and `exp(4) < 81`.
One slice at this point has polynomial part `2^{10} · 1088`, so two copies
have polynomial part `2 · 2^{10} · 1088 > 81`. The copies are larger than `1`.

## Not covered

- A gate factor smaller than `6`. The one-slice exponent still spends
  `10 g L`. The coefficient-9 monomials still use `16`.
- A proof that `||H^{-1}||_2 ≤ p^{10}`. HALO assumes it.
- The section error `p^6 exp(-p^2)` and the leading ceiling `9 p^2`.
- Editing the #4100 notes, or the #4495 gate.
- Any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/gaussian-slice-six-copies --check-only
python3.12 -B scripts/research_package.py --package research/gaussian-slice-six-copies
```

Base `b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`, priority revision 7.
Upstream was fetched at 2026-10-22T14:56:27Z and was that commit. The
pre-submit fetch at 2026-10-22T14:59:04Z was the same commit. The pinned
blobs for the selected record, the catalogue, both source READMEs, and
HALO.md match that main. The selection is κ = `60403/20000000`.

Overlap snapshot: open PRs fetched 2026-10-22T14:57:49Z (438 records) and
discussions fetched 2026-10-22T14:58:48Z (3594 records). Terms
`24 p^2 - 86 p`, `slice-six-copies`, and `48 L` reported 56 matches and
showed 8. The first two were this README and this TASK. The other six
shown posts are older discussion notes whose text contains `48 l` inside
`48 later` or `48 late`. A second search of the same cache, offline, used
`24 p^2 - 86 p - 96`, `slice-six-copies`, and `6908`. It returned this
README, this TASK, the #4667 DONE
(discussioncomment-19126114), and digit runs in older local notes that
contain `6908`. The #4667 note leaves these copies open and names the
test at `p = 64`. The handoff thread, reread at the pre-submit fetch,
still ends at that #4667 DONE. The open-PR list at that time still starts
at #4667. No matches is not a novelty certificate.

## Open next questions

1. **Does `5 g L ≤ p` already absorb one heavy slice?** The exponent
   spends `10 g L`. The first step is the fifths identity
   `400 g L = 80 · 5 g L`, then the test of `20 p^2 - 80 p - 80` at
   `p = 64`. Do not change the coefficient-9 monomial gate.

## Credit

- The factor-6 slice, and this question, are #4667's.
- The factor-7 copies are #4663's.
- The unequal factor `1 + p^4` is #4524's.
- The published gate `16 g L ≤ p` is #4495's. It is unchanged.
- The ceiling `9 p^2` is #4493's.
- The written tail `p^{10} exp(-p^2)` is #4100's.

Prepared by James Reed with substantial Cursor Grok 4.7 assistance. Apache-2.0.
