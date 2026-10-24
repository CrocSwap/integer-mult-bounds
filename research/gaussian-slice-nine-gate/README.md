# The factor-9 gate absorbs one heavy slice

**Claim type:** an explicit absorption bound for one tensor slice.
**No new κ.** The trailing bound `p^{10}`, the section error, and the
ceiling `9 p^2` stay hypotheses. The selected record remains `23/10000`.
The coefficient-9 monomials keep the published gate `16 g L ≤ p`.

## Question

#4528 absorbs `g` copies under `10 g L ≤ p`, and asks whether one heavy
slice already fits under `9 g L ≤ p`. The factor-10 proof spends `8 p`
from `80 g L`. The named step is the ninths identity
`720 g L = 80 · 9 g L`, then a polynomial test at `p = 64`.

This `9` is the coefficient of `g L`. It is not the ceiling `9` in
`9 p^2`. #4495 still needs four bits for that ceiling, because `9 > 8`
and `9 < 16`.

## Lemma

Let `p ≥ 2`, `g ≥ 1`, `K ≥ 0` and `C ≥ 0` be integers, and let
`L = ceil(log2 p)`. If

```text
p ≥ max(64, 4K + 2C)    and    9 g L ≤ p,
```

then

```text
(p^{10})^{g-1} p^6 (1 + p^4) exp(K p - p^2)
```

is strictly below `2^{-C p}`. The case `K = 0` is the slice in the
question. The exponent is at most `-C p - 1`.

This hypothesis is wider than the factor-10 gate. At `p = 65` and
`g = 1`, `L = 7`, so `9 g L = 63 ≤ 65` while `10 g L = 70 > 65`. The
exponent there is `-4154`. The factor-10 comparison `80 g L ≤ 8 p` fails
at that point: `560 > 520`.

At `p = 2` and `g = 1` the hypothesis fails, and the slice is larger
than `1`.

## Proof

Dropping the `1` in `1 + p^4` leaves exactly `p^{10 g}`. Since
`1 + p^4 < 2 p^4 ≤ 2^{4 L + 1}` and `p ≤ 2^L`, the polynomial part is
strictly below `2^{10 g L + 1}`. With `exp(-p^2) < 2^{-p^2}` and
`exp(K p) ≤ 2^{2 K p}`, the slice is strictly below `2^E` for

```text
E = 10 g L + 1 + 2 K p - p^2.
```

Clear `72 (E + C p)`, which is nine times `8 (E + C p)`. The new gate
gives `720 g L = 80 · 9 g L ≤ 80 p`. The identity
`72 (2 K + C) = 36 (4 K + 2 C)` gives a linear contribution of at most
`36 p^2` once `p ≥ 4 K + 2 C`. The constant `1` contributes `72`. The
sum is at most

```text
-(36 p^2 - 80 p - 72).
```

The polynomial `36 p^2 - 80 p - 144` equals `142192` at `p = 64` and
then increases by `72 p - 44`. Thus `36 p^2 - 80 p - 72 ≥ 72` for every
integer `p ≥ 64`, so `72 (E + C p) ≤ -72` and `E ≤ -C p - 1`.

At `p = 2` and `g = 1`, `9 g L = 9 > 2`. The series of `e` through
`1/6!` is `13699/5040`. Terms after that have ratios at most `1/8`, so
the tail is strictly below `8/(7 · 5040)`. The gap up to `3` is
`1421/5040`, and `8 < 1421 · 7`, so `e < 3` and `exp(4) < 81`. The slice
equals `1088 exp(-4)`, and `81 < 1088`, so the slice is larger than `1`.

## Not covered

- The `g` copies of this slice under `9 g L ≤ p`.
- A gate factor smaller than `9`.
- A proof that `||H^{-1}||_2 ≤ p^{10}`. HALO assumes it.
- The section error `p^6 exp(-p^2)` and the leading ceiling `9 p^2`.
- Editing the #4100 notes, or the #4495 gate.
- Any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/gaussian-slice-nine-gate --check-only
python3.12 -B scripts/research_package.py --package research/gaussian-slice-nine-gate
```

Base `f9f85c1e4fa1e955ff39f10fca447e3e2a4e4adc`, priority revision 7, selection
refresh κ = `23/10000`. Upstream was fetched at 2026-10-22T03:50:29Z and was
that commit. The pre-submit fetch, reread at 2026-10-22T03:51:50Z, was still
that commit, with the same four pinned blobs. The #1166 reread at that time
still has #4528 as the latest note on this slice. pinterbanget's 03:49:08Z
note is an independent check of #4483.

Overlap snapshot: open PRs fetched 2026-10-22T03:50:39Z (314 records) and
discussions fetched 2026-10-22T03:51:38Z (3409 records). A search for
`9 g L`, `36 p^2 - 80 p` and `slice-nine-gate` returned this draft and the
#4528 handoff, which leaves the factor-9 gate open. A search miss is not a
novelty certificate. The open-PR list at 2026-10-22T03:51:50Z starts with
#4529, the #4483 check, and does not contain this slice.

## Open next questions

1. **Do the `g` copies stay below `2^{-C p}` under `9 g L ≤ p`?** The
   one-slice ninths produce `80 p + 72 - 36 p^2` before the sign is
   flipped. Copies add one `L`, and `8 L ≤ p` turns `72 L` into `9 p`.
   The first step is to test `36 p^2 - 89 p - 144` at `p = 64`. Do not
   change the coefficient-9 gate.

## Credit

- The factor-10 copies, and this question, are #4528's.
- The factor-10 slice is #4527's.
- The unequal factor `1 + p^4` is #4524's.
- The published gate `16 g L ≤ p` is #4495's. It is unchanged.
- The ceiling `9 p^2` is #4493's.
- The written tail `p^{10} exp(-p^2)` is #4100's.

Prepared by James Reed with substantial Cursor Grok 4.7 assistance. Apache-2.0.
