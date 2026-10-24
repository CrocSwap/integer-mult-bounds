# The factor-10 gate absorbs the heavy slice

**Claim type:** an explicit absorption bound for one tensor slice.
**No new κ.** The trailing bound `p^{10}`, the section error, and the
ceiling `9 p^2` stay hypotheses. The selected record remains `23/10000`.
The coefficient-9 monomials keep the published gate `16 g L ≤ p`.

## Question

#4526 absorbs the heavy slice under `16 g L ≤ p`, and asks whether
`10 g L ≤ p` already suffices. The exponent spends `10 g L`. The named
step is to replace `16` by `10` in the eighths and test
`4 p^2 - 8 p - 16` at `p = 64`.

The `10 < 16` sentence in #4495 is a different test. It says that four bits
majorize an older coefficient. This package's `10` is the power in
`p^{10 g}`.

## Lemma

Let `p ≥ 2`, `g ≥ 1`, `K ≥ 0` and `C ≥ 0` be integers, and let
`L = ceil(log2 p)`. If

```text
p ≥ max(64, 4K + 2C)    and    10 g L ≤ p,
```

then

```text
(p^{10})^{g-1} p^6 (1 + p^4) exp(K p - p^2)
```

is strictly below `2^{-C p}`. The case `K = 0` is the slice in the
question. The exponent is at most `-C p - 1`.

This hypothesis is wider than the published gate. At `p = 64` and `g = 1`,
`L = 6`, so `10 g L = 60 ≤ 64` while `16 g L = 96 > 64`. The exponent
there is `-4035`.

The factor `10` is a sufficient coefficient in this argument. At `p = 2`
and `g = 1` the hypothesis fails, and the slice itself is larger than `1`.

## Proof

Dropping the `1` in `1 + p^4` leaves exactly `p^{10 g}`. Since
`1 + p^4 < 2 p^4 ≤ 2^{4 L + 1}` and `p ≤ 2^L`,

```text
(p^{10})^{g-1} p^6 (1 + p^4) < 2^{10 g L + 1}.
```

The comparisons `exp(-p^2) < 2^{-p^2}` and `exp(K p) ≤ 2^{2 K p}` put the
slice strictly below `2^E` for

```text
E = 10 g L + 1 + 2 K p - p^2.
```

Clear eight times `E + C p`. The new gate gives `80 g L = 8 · 10 g L ≤ 8 p`.
The constant `1` contributes `8`. The identity
`8 (2 K + C) = 4 (4 K + 2 C)` gives a linear contribution of at most
`4 p^2` once `p ≥ 4 K + 2 C`. The sum is at most

```text
-(4 p^2 - 8 p - 8).
```

The polynomial `4 p^2 - 8 p - 16` equals `15856` at `p = 64` and then
increases by `8 p - 4`. Thus `4 p^2 - 8 p - 8 ≥ 8` for every integer
`p ≥ 64`, eight times `E + C p` is at most `-8`, and `E ≤ -C p - 1`.

At `p = 2` and `g = 1` the same formal exponent is `7`, and
`10 g L = 10 > 2`. The series of `e` through `1/6!` is `13699/5040`.
Terms after that have ratios at most `1/8`, so the tail is strictly below
`8/(7 · 5040)`. The gap from the partial sum up to `3` is `1421/5040`,
and `8 < 1421 · 7`, so `e < 3`. Then `exp(4) < 81`. The slice equals
`1088 exp(-4)`, and `81 < 1088`, so the slice is larger than `1`.

## Not covered

- The `g` copies of this slice under `10 g L ≤ p`. Those copies add one
  `L`. The coefficient-9 monomials still use `16`.
- A smaller gate factor than `10`.
- A proof that `||H^{-1}||_2 ≤ p^{10}`. HALO assumes it.
- The section error `p^6 exp(-p^2)` and the leading ceiling `9 p^2`.
- Editing the #4100 notes, or the #4495 gate.
- Any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/gaussian-slice-ten-gate --check-only
python3.12 -B scripts/research_package.py --package research/gaussian-slice-ten-gate
```

Base `f9f85c1e4fa1e955ff39f10fca447e3e2a4e4adc`, priority revision 7, selection
refresh κ = `23/10000`. Upstream was fetched at 2026-10-22T03:40:55Z and was
that commit. The pre-submit fetch, reread at 2026-10-22T03:44:15Z, was still
that commit, with the same four pinned blobs. The #1166 reread at that time
still has #4526 as the latest note on this slice. dillona's 03:34:38Z claim
is #4483's broader-admission question.

Overlap snapshot: open PRs fetched 2026-10-22T03:42:36Z (311 records) and
discussions fetched 2026-10-22T03:43:20Z (3406 records). A search for
`10 g L`, `4 p^2 - 8 p` and `slice-ten-gate` returned this draft and #4526,
which leaves the factor-10 gate open. A search miss is not a novelty
certificate. The open-PR list at 2026-10-22T03:44:15Z still starts at #4526.

## Open next questions

1. **Do the `g` copies stay below `2^{-C p}` under `10 g L ≤ p`?** The
   slice spends `8 p` from `80 g L`. Copies add one `L` and raise that
   coefficient from `8` to `9`. The first step is to test
   `4 p^2 - 9 p - 16` at `p = 64`. Do not change the coefficient-9 gate.

## Credit

- The heavy slice, and this question, are #4526's.
- The unequal factor `1 + p^4` is #4524's.
- The published gate `16 g L ≤ p` is #4495's. It is unchanged.
- The ceiling `9 p^2` is #4493's.
- The written tail `p^{10} exp(-p^2)` is #4100's.

Prepared by James Reed with substantial Cursor Grok 4.7 assistance. Apache-2.0.
