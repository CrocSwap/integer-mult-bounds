# The factor-5 gate absorbs one heavy slice

**Claim type:** an explicit absorption bound for one tensor slice.
**No new κ.** The trailing bound `p^{10}`, the section error, and the
ceiling `9 p^2` stay hypotheses. The selected record is `60403/20000000`.
The coefficient-9 monomials keep the published gate `16 g L ≤ p`.

## Question

#4668 absorbs the `g` copies under `6 g L ≤ p`, and asks whether one heavy
slice already fits under `5 g L ≤ p`. The exponent spends `10 g L`. The
named step is the fifths identity `400 g L = 80 · 5 g L`, then the test of
`20 p^2 - 80 p - 80` at `p = 64`.

This `5` is the coefficient of `g L`. It is not a three-bit majorant of
the ceiling `9`. #4495 still rejects three bits for that ceiling, because
`9 > 8`, and it still uses four bits because `9 < 16`.

## Lemma

Let `p ≥ 2`, `g ≥ 1`, `K ≥ 0` and `C ≥ 0` be integers, and let
`L = ceil(log2 p)`. If

```text
p ≥ max(64, 4K + 2C)    and    5 g L ≤ p,
```

then

```text
(p^{10})^{g-1} p^6 (1 + p^4) exp(K p - p^2)
```

is strictly below `2^{-C p}`. The case `K = 0` is the slice in the
question. The exponent is at most `-C p - 1`.

This hypothesis is wider than the factor-6 gate. At `p = 70` and `g = 2`,
`L = 7`, so `5 g L = 70 ≤ 70` while `6 g L = 84 > 70`. The exponent
there is `-4759`. The factor-6 comparison `480 g L ≤ 80 p` fails at that
point: `6720 > 5600`.

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

Clear `40 (E + C p)`, which is five times `8 (E + C p)`. The new gate
gives `400 g L = 80 · 5 g L ≤ 80 p`. The identity
`40 (2 K + C) = 20 (4 K + 2 C)` gives a linear contribution of at most
`20 p^2` once `p ≥ 4 K + 2 C`. The constant `1` contributes `40`. The
sum is at most

```text
-(20 p^2 - 80 p - 40).
```

The polynomial `20 p^2 - 80 p - 80` equals `76720` at `p = 64` and then
increases by `40 p - 60`. Thus `20 p^2 - 80 p - 40 ≥ 40` for every
integer `p ≥ 64`, so `40 (E + C p) ≤ -40` and `E ≤ -C p - 1`.

At `p = 2` and `g = 1`, `5 g L = 5 > 2`. The series of `e` through
`1/6!` is `13699/5040`. Terms after that have ratios at most `1/8`, so
the tail is strictly below `8/(7 · 5040)`. The gap up to `3` is
`1421/5040`, and `8 < 1421 · 7`, so `e < 3` and `exp(4) < 81`. The slice
equals `1088 exp(-4)`, and `81 < 1088`, so the slice is larger than `1`.

## Not covered

- The `g` copies of this slice under `5 g L ≤ p`.
- A gate factor smaller than `5`.
- A proof that `||H^{-1}||_2 ≤ p^{10}`. HALO assumes it.
- The section error `p^6 exp(-p^2)` and the leading ceiling `9 p^2`.
- Editing the #4100 notes, or the #4495 gate.
- Any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/gaussian-slice-five-gate --check-only
python3.12 -B scripts/research_package.py --package research/gaussian-slice-five-gate
```

Base `b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`, priority revision 7.
Upstream was fetched at 2026-10-22T15:00:57Z and was that commit. The
pre-submit fetch at 2026-10-22T15:02:45Z was the same commit. The pinned
blobs for the selected record, the catalogue, both source READMEs, and
HALO.md match that main. The selection is κ = `60403/20000000`.

Overlap snapshot: open PRs fetched 2026-10-22T15:01:39Z (439 records) and
discussions fetched 2026-10-22T15:02:34Z (3595 records). Terms
`20 p^2 - 80 p - 80`, `slice-five-gate`, and `4759` reported 30 matches
and showed 8. The first two were this README and this TASK. The six shown
discussion hits are older BIT-stock notes whose commit text contains the
digits `4759`. A second search of the same cache, offline, dropped `4759`.
It returned this README, this TASK, and the #4668 DONE
(discussioncomment-19126212). That note leaves this one-slice question
open and names the test at `p = 64`. The handoff thread, reread at the
pre-submit fetch, still ends at that #4668 DONE. The open-PR list at that
time still starts at #4668. No matches is not a novelty certificate.

## Open next questions

1. **Do the `g` copies stay below `2^{-C p}` under `5 g L ≤ p`?** The
   one-slice fifths spend `80 p`. Copies add one `L`, and `8 L ≤ p`
   turns `40 L` into `5 p`. The first step is to test
   `20 p^2 - 85 p - 80` at `p = 64`. Do not change the coefficient-9
   monomial gate.

## Credit

- The factor-6 copies, and this question, are #4668's.
- The factor-6 slice is #4667's.
- The unequal factor `1 + p^4` is #4524's.
- The published gate `16 g L ≤ p` is #4495's. It is unchanged.
- The ceiling `9 p^2` is #4493's.
- The written tail `p^{10} exp(-p^2)` is #4100's.

Prepared by James Reed with substantial Cursor Grok 4.7 assistance. Apache-2.0.
