# The factor-3 gate absorbs one heavy slice

**Claim type:** an explicit absorption bound for one tensor slice.
**No new κ.** The trailing bound `p^{10}`, the section error, and the
ceiling `9 p^2` stay hypotheses. The selected record is `60403/20000000`.
The coefficient-9 monomials keep the published gate `16 g L ≤ p`.

## Question

#4676 absorbs the `g` copies under `4 g L ≤ p`, and asks whether one heavy
slice already fits under `3 g L ≤ p`. The exponent spends `10 g L`. The
named step is the thirds identity `240 g L = 80 · 3 g L`, then the test of
`12 p^2 - 80 p - 48` at `p = 64`.

This `3` is the coefficient of `g L`. It is not a three-bit majorant of
the ceiling `9`. #4495 still rejects three bits for that ceiling, because
`9 > 8`, and it still uses four bits because `9 < 16`.

## Lemma

Let `p ≥ 2`, `g ≥ 1`, `K ≥ 0` and `C ≥ 0` be integers, and let
`L = ceil(log2 p)`. If

```text
p ≥ max(64, 4K + 2C)    and    3 g L ≤ p,
```

then

```text
(p^{10})^{g-1} p^6 (1 + p^4) exp(K p - p^2)
```

is strictly below `2^{-C p}`. The case `K = 0` is the slice in the
question. The exponent is at most `-C p - 1`.

This hypothesis is wider than the factor-4 gate. At `p = 84` and `g = 4`,
`L = 7`, so `3 g L = 84 ≤ 84` while `4 g L = 112 > 84`. The exponent
there is `-6775`. The factor-4 comparison `320 g L ≤ 80 p` fails at that
point: `8960 > 6720`.

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

Clear `24 (E + C p)`, which is three times `8 (E + C p)`. The new gate
gives `240 g L = 80 · 3 g L ≤ 80 p`. The identity
`24 (2 K + C) = 12 (4 K + 2 C)` gives a linear contribution of at most
`12 p^2` once `p ≥ 4 K + 2 C`. The constant `1` contributes `24`. The
sum is at most

```text
-(12 p^2 - 80 p - 24).
```

The polynomial `12 p^2 - 80 p - 48` equals `43984` at `p = 64` and then
increases by `24 p - 68`. Thus `12 p^2 - 80 p - 24 ≥ 24` for every
integer `p ≥ 64`, so `24 (E + C p) ≤ -24` and `E ≤ -C p - 1`.

At `p = 2` and `g = 1`, `3 g L = 3 > 2`. The series of `e` through
`1/6!` is `13699/5040`. Terms after that have ratios at most `1/8`, so
the tail is strictly below `8/(7 · 5040)`. The gap up to `3` is
`1421/5040`, and `8 < 1421 · 7`, so `e < 3` and `exp(4) < 81`. The slice
equals `1088 exp(-4)`, and `81 < 1088`, so the slice is larger than `1`.

## Not covered

- The `g` copies of this slice under `3 g L ≤ p`.
- A gate factor smaller than `3`.
- A proof that `||H^{-1}||_2 ≤ p^{10}`. HALO assumes it.
- The section error `p^6 exp(-p^2)` and the leading ceiling `9 p^2`.
- Editing the #4100 notes, or the #4495 gate.
- Any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/gaussian-slice-three-gate --check-only
python3.12 -B scripts/research_package.py --package research/gaussian-slice-three-gate
```

Base `b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`, priority revision 7.
Upstream was fetched at 2026-10-22T15:31:12Z and was that commit. The
pre-submit fetch at 2026-10-22T15:32:46Z was the same commit. The pinned
blobs for the selected record, the catalogue, both source READMEs, and
HALO.md match that main. The selection is κ = `60403/20000000`.

Overlap snapshot: open PRs fetched 2026-10-22T15:31:50Z (446 records) and
discussions fetched 2026-10-22T15:32:39Z (3604 records). Terms
`12 p^2 - 80 p - 48`, `slice-three-gate`, and `6775` reported 20 matches
and showed 8. The first two were this README and this TASK. One shown hit
is the #4676 DONE (discussioncomment-19126711). The other shown hits
contain the digits `6775` inside timestamps, job ids, comment URLs, or
commit hashes. A second search of the same cache, offline, dropped
`6775`. It returned this README, this TASK, and that #4676 DONE. That
note leaves this one-slice question open and names the test at `p = 64`.
The handoff thread, reread at the pre-submit fetch, still ends at that
#4676 DONE. The open-PR list at that time still starts at #4676. No
matches is not a novelty certificate.

## Open next questions

1. **Do the `g` copies stay below `2^{-C p}` under `3 g L ≤ p`?** The
   one-slice thirds spend `80 p`. Copies add one `L`, and `8 L ≤ p`
   turns `24 L` into `3 p`. The first step is to test
   `12 p^2 - 83 p - 48` at `p = 64`. Do not change the coefficient-9
   monomial gate.

## Credit

- The factor-4 copies, and this question, are #4676's.
- The factor-4 slice is #4673's.
- The unequal factor `1 + p^4` is #4524's.
- The published gate `16 g L ≤ p` is #4495's. It is unchanged.
- The ceiling `9 p^2` is #4493's.
- The written tail `p^{10} exp(-p^2)` is #4100's.

Prepared by James Reed with substantial Cursor Grok 4.7 assistance. Apache-2.0.
