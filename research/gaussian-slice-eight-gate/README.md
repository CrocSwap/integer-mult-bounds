# The factor-8 gate absorbs one heavy slice

**Claim type:** an explicit absorption bound for one tensor slice.
**No new κ.** The trailing bound `p^{10}`, the section error, and the
ceiling `9 p^2` stay hypotheses. The selected record is `60403/20000000`.
The coefficient-9 monomials keep the published gate `16 g L ≤ p`.

## Question

#4531 absorbs the `g` copies under `9 g L ≤ p`, and asks whether one heavy
slice already fits under `8 g L ≤ p`. The exponent spends `10 g L`. The
named step is the eighths bound `80 g L ≤ 10 p`, then the test of
`4 p^2 - 10 p - 16` at `p = 64`.

This `8` is the coefficient of `g L`. It is not a three-bit majorant of
the ceiling `9`. #4495 still rejects three bits for that ceiling, because
`9 > 8`, and it still uses four bits because `9 < 16`.

## Lemma

Let `p ≥ 2`, `g ≥ 1`, `K ≥ 0` and `C ≥ 0` be integers, and let
`L = ceil(log2 p)`. If

```text
p ≥ max(64, 4K + 2C)    and    8 g L ≤ p,
```

then

```text
(p^{10})^{g-1} p^6 (1 + p^4) exp(K p - p^2)
```

is strictly below `2^{-C p}`. The case `K = 0` is the slice in the
question. The exponent is at most `-C p - 1`.

This hypothesis is wider than the factor-9 gate. At `p = 112` and
`g = 2`, `L = 7`, so `8 g L = 112 ≤ 112` while `9 g L = 126 > 112`. The
exponent there is `-12403`.

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

Clear eight times `E + C p`. The new gate gives
`80 g L = 10 · 8 g L ≤ 10 p`. The constant `1` contributes `8`. The
identity `8 (2 K + C) = 4 (4 K + 2 C)` gives a linear contribution of at
most `4 p^2` once `p ≥ 4 K + 2 C`. The sum is at most

```text
-(4 p^2 - 10 p - 8).
```

The polynomial `4 p^2 - 10 p - 16` equals `15728` at `p = 64` and then
increases by `8 p - 6`. Thus `4 p^2 - 10 p - 8 ≥ 8` for every integer
`p ≥ 64`, eight times `E + C p` is at most `-8`, and `E ≤ -C p - 1`.

At `p = 2` and `g = 1`, `8 g L = 8 > 2`. The series of `e` through
`1/6!` is `13699/5040`. Terms after that have ratios at most `1/8`, so
the tail is strictly below `8/(7 · 5040)`. The gap up to `3` is
`1421/5040`, and `8 < 1421 · 7`, so `e < 3` and `exp(4) < 81`. The slice
equals `1088 exp(-4)`, and `81 < 1088`, so the slice is larger than `1`.

## Not covered

- The `g` copies of this slice under `8 g L ≤ p`.
- A gate factor smaller than `8`.
- A proof that `||H^{-1}||_2 ≤ p^{10}`. HALO assumes it.
- The section error `p^6 exp(-p^2)` and the leading ceiling `9 p^2`.
- Editing the #4100 notes, or the #4495 gate.
- Any new κ. The selected record changed upstream, to `60403/20000000`,
  and this package leaves it there.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/gaussian-slice-eight-gate --check-only
python3.12 -B scripts/research_package.py --package research/gaussian-slice-eight-gate
```

Base `b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`, priority revision 7.
Upstream was fetched at 2026-10-22T14:29:21Z and was that commit. The
selection on it is κ = `60403/20000000`. The pre-submit fetch, reread at
2026-10-22T14:31:01Z, was still that commit, with the same four pinned
blobs. The #1166 reread at that time has no claim of this slice. The
latest notes there are other tasks.

Overlap snapshot: open PRs fetched 2026-10-22T14:29:46Z (426 records) and
discussions fetched 2026-10-22T14:30:34Z (3588 records). A search for
`4 p^2 - 10 p`, `slice-eight-gate` and `8 g L` returned this draft and
the #4531 handoff, which leaves the factor-8 gate open. That handoff
still quotes the older selection `23/10000`. A search miss is not a
novelty certificate. The open-PR list at 2026-10-22T14:31:01Z starts at
#4655 and does not contain this slice.

## Open next questions

1. **Do the `g` copies stay below `2^{-C p}` under `8 g L ≤ p`?** The
   one-slice eighths spend `10 p` from `80 g L`. Copies add one `L`, and
   `8 L ≤ p` turns that piece into one more `p`. The first step is to
   test `4 p^2 - 11 p - 16` at `p = 64`. Do not change the coefficient-9
   monomial gate.

## Credit

- The factor-9 copies, and this question, are #4531's.
- The factor-9 slice is #4530's.
- The unequal factor `1 + p^4` is #4524's.
- The published gate `16 g L ≤ p` is #4495's. It is unchanged.
- The ceiling `9 p^2` is #4493's.
- The written tail `p^{10} exp(-p^2)` is #4100's.

Prepared by James Reed with substantial Cursor Grok 4.7 assistance. Apache-2.0.
