# The factor-9 gate absorbs g copies of the heavy slice

**Claim type:** an explicit absorption bound for one tensor sum.
**No new κ.** The trailing bound `p^{10}`, the section error, and the
ceiling `9 p^2` stay hypotheses. The selected record remains `23/10000`.
The coefficient-9 monomials keep the published gate `16 g L ≤ p`.

## Question

#4530 puts one heavy slice below `2^{-C p}` under `9 g L ≤ p`. It leaves
the `g` copies open. Those copies add one `L`. The one-slice ninths spend
`80 p`, and `8 L ≤ p` turns the new term `72 L` into `9 p`. The named step
is to test `36 p^2 - 89 p - 144` at `p = 64`.

This `9` is the coefficient of `g L`. It is not the ceiling `9` in
`9 p^2`. #4495 still needs four bits for that ceiling, because `9 > 8`
and `9 < 16`.

## Lemma

Let `p ≥ 2`, `g ≥ 1`, `K ≥ 0` and `C ≥ 0` be integers, and let
`L = ceil(log2 p)`. If

```text
p ≥ max(64, 4K + 2C)    and    9 g L ≤ p,
```

then `g` copies of

```text
(p^{10})^{g-1} p^6 (1 + p^4) exp(K p - p^2)
```

are strictly below `2^{-C p}`. The exponent is at most `-C p - 1`.

The gate is wider than the factor-10 gate. At `p = 128` and `g = 2`,
`L = 7`, so `9 g L = 126 ≤ 128` while `10 g L = 140 > 128`. The copies
exponent there is `-16236`.

At `p = 2` and `g = 2` the hypothesis fails, and the two copies are larger
than `1`.

## Proof

#4530 puts one slice strictly below `2^{E_0}` for

```text
E_0 = 10 g L + 1 + 2 K p - p^2.
```

The same gate forces `g < 2^L`. Indeed `p ≤ 2^L` and `9 L > 1`, so
`9 g L ≤ p` implies `g < 2^L`. Multiplying by `g` therefore adds one
`L`. The copies are strictly below `2^E` for

```text
E = 10 g L + L + 1 + 2 K p - p^2.
```

Clear `72 (E + C p)`, nine times `8 (E + C p)`. As in the one-slice
argument, `720 g L ≤ 80 p` and the linear term contributes at most
`36 p^2`. The new piece is `72 L`. For every integer `p ≥ 64`,
`8 L ≤ p`, so `72 L = 9 · 8 L ≤ 9 p`. The base of that comparison is
`8 · 7 = 56 ≤ 64 = 2^6`. If `8 (m + 1) ≤ 2^m`, then

```text
8 (m + 2) = 8 (m + 1) + 8 ≤ 2^m + 8 ≤ 2^{m + 1},
```

because `8 ≤ 2^6`. Thus `8 (m + 1) ≤ 2^m` for every integer `m ≥ 6`.
When `2^m ≤ p < 2^{m + 1}`, the level is `m` at the power of two and
`m + 1` after it, and both are at most `p`.

`72 (E + C p)` is therefore at most

```text
80 p + 9 p + 72 - 36 p^2 = -(36 p^2 - 89 p - 72).
```

The polynomial `36 p^2 - 89 p - 144` equals `141616` at `p = 64` and
then increases by `72 p - 53`. Thus `36 p^2 - 89 p - 72 ≥ 72` for every
integer `p ≥ 64`, so `72 (E + C p) ≤ -72` and `E ≤ -C p - 1`.

At `p = 2` and `g = 2`, `9 g L = 18 > 2` and the formal exponent is
`18`. The series of `e` through `1/6!` is `13699/5040`. The later ratios
are at most `1/8`, so the tail is strictly below `8/(7 · 5040)`. The gap
up to `3` is `1421/5040`, and `8 < 1421 · 7`, so `e < 3` and `exp(4) < 81`.
One slice at this point has polynomial part `2^{10} · 1088`, so two copies
have polynomial part `2 · 2^{10} · 1088 > 81`. The copies are larger than `1`.

## Not covered

- A gate factor smaller than `9`. The one-slice exponent still spends
  `10 g L`. The coefficient-9 monomials still use `16`.
- A proof that `||H^{-1}||_2 ≤ p^{10}`. HALO assumes it.
- The section error `p^6 exp(-p^2)` and the leading ceiling `9 p^2`.
- Editing the #4100 notes, or the #4495 gate.
- Any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/gaussian-slice-nine-copies --check-only
python3.12 -B scripts/research_package.py --package research/gaussian-slice-nine-copies
```

Base `f9f85c1e4fa1e955ff39f10fca447e3e2a4e4adc`, priority revision 7, selection
refresh κ = `23/10000`. Upstream was fetched at 2026-10-22T03:53:24Z and was
that commit. The pre-submit fetch, reread at 2026-10-22T03:54:40Z, was still
that commit, with the same four pinned blobs. The #1166 reread at that time
still has #4530 as the latest note on this slice. pinterbanget's 03:49:08Z
note is an independent check of #4483.

Overlap snapshot: open PRs fetched 2026-10-22T03:53:37Z (315 records) and
discussions fetched 2026-10-22T03:54:31Z (3410 records). A search for
`36 p^2 - 89 p`, `nine-copies` and `9 g L` returned this draft, #4528, and
#4530. #4530 absorbs one slice under the factor-9 gate and leaves the copies
open. A search miss is not a novelty certificate. The open-PR list at
2026-10-22T03:54:40Z still starts at #4530.

## Open next questions

1. **Does `8 g L ≤ p` already absorb one heavy slice?** The exponent
   spends `10 g L`. Under `8 g L ≤ p` the eighths give `80 g L ≤ 10 p`.
   The first step is to test `4 p^2 - 10 p - 16` at `p = 64`. Do not
   change the coefficient-9 monomial gate.

## Credit

- The factor-9 slice, and this question, are #4530's.
- The factor-10 copies are #4528's.
- The unequal factor `1 + p^4` is #4524's.
- The published gate `16 g L ≤ p` is #4495's. It is unchanged.
- The ceiling `9 p^2` is #4493's.
- The written tail `p^{10} exp(-p^2)` is #4100's.

Prepared by James Reed with substantial Cursor Grok 4.7 assistance. Apache-2.0.
