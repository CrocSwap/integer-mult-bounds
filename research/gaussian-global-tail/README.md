# The written global tail is p^{10} exp(-p^2)

**Claim type:** a comparison of three tail statements.
**No new κ.** The ideal-gap gauge stays a hypothesis. The selected record
remains `23/10000`.

## Question

#4520 asks whether `||P_glob - C_i||_2` is below `p^6 exp(-p^2)`, or only
the written `p^{10} exp(-p^2)`. The named step is to compare the identity
`P - H^{-1} = -Q^J H^{-1}` with the within-cell `p^6` bound, and not to put
`p^{10}` into the gate yet.

## Lemma

Under HALO's written hypotheses, the global majorant is
`p^{10} exp(-p^2)`. It is not the within-cell bound `p^6 exp(-p^2)`.

1. **The identity keeps the inverse factor.** The locality audit records

```text
P - H^{-1} = -Q^J H^{-1},
||P - H^{-1}||_2 ≤ (1 - p^{-40})^J p^{10} ≤ p^{10} exp(-p^2).
```

For an integer `p`, `J = ceil(p^{42}) = p^{42}`, so `J p^{-40} = p^2`.
That power fills the `exp(-p^2)` slot. It does not cancel any power of the
inverse factor. HALO states the same majorant,
`||P_i - H_i^{-1}||_2 ≤ p^{10} exp(-p^2)`.

2. **The written majorant is larger than `p^6 exp(-p^2)` by `p^4`.**
Since `10 - 6 = 4` and `p^4 ≥ 16 > 1` for every integer `p ≥ 2`,

```text
p^{10} exp(-p^2) = p^4 · p^6 exp(-p^2) > p^6 exp(-p^2).
```

The truncation exponent `2` and the leftover exponent `4` are different.
The series length does not turn the written majorant into the smaller one.

3. **The within-cell `p^6` bound is a different polynomial.** #4452 proves
`||P - A^{-1}||_2 < p^6 exp(-p^2)` for
`P = p^{-11} sum_{j < p^{24}} Q^j A^*` inside one cell, under the ideal-gap
gauge. That package does not move the global reference.

4. **The conditional `p^6` bound is not the written hypothesis.** #4406
proves `||P - H^{-1}||_2 < p^6 exp(-p^2)` for
`P = p^{-12} sum_{j < p^{26}} Q^j H^*`, and only if
`||H^{-1}||_2 ≤ 16 p^2`. It does not prove that ceiling for the rounded
reference. At `p = 2`, `16 p^2 = p^6`. For `p ≥ 3`, `16 p^2 < p^6`.
Equality at `p = 2` means the ceiling `16 p^2` is not by itself a strict
`p^6` bound.

This package does not put `p^{10}` into the #4520 gate.

## Proof

The audit derives the displayed identity from
`p^{-20} (I - Q)^{-1} H^* = H^{-1}` and commutation of `Q` with `H^* H`.
The factor `p^{10}` is the hypothesis `||H^{-1}||_2 ≤ p^{10}`. Multiplying
by `(1 - p^{-40})^J` and using `J p^{-40} = p^2` produces the written
majorant. Replacing `p^{10}` by `p^6` in that product would require
`||H^{-1}||_2 ≤ p^6`, which is not HALO's hypothesis.

The integer comparison is `2^{10} = 2^6 · 2^4` and `2^4 > 1`. The same
gap is `p^4` at every larger integer `p`. The conditional ceiling meets
`p^6` at `p = 2` and is smaller at `p = 3`, where `16 · 9 < 3^6`.

## Not covered

- A proof that `||H^{-1}||_2 ≤ p^{10}` or `||H^{-1}||_2 ≤ 16 p^2` for the
  rounded reference. Both remain hypotheses of the packages that use them.
- The ideal-gap gauge behind the within-cell bound.
- Absorbing `p^{10}` in the restricted gate.
- Editing the #4100 notes. They still say `p^{10} exp(-p^2)`.
- Any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/gaussian-global-tail --check-only
python3.12 -B scripts/research_package.py --package research/gaussian-global-tail
```

Base `f9f85c1e4fa1e955ff39f10fca447e3e2a4e4adc`, priority revision 7, selection
refresh κ = `23/10000`. Upstream was fetched at 2026-10-22T03:23:31Z and was
that commit.

Overlap snapshot: open PRs fetched 2026-10-22T03:25:01Z (308 records) and
discussions fetched 2026-10-22T03:25:44Z (3401 records). A search for
`global tail`, `does not move the global reference` and `p^10 exp(-p^2)`
returned #4520, which asks this question, the locality audit, and #4452.
The other hits use "global tail" for unrelated transforms. No result
replaces HALO's `p^{10}` majorant by the within-cell `p^6` bound. A search
miss is not a novelty certificate. The audit is the identity. #4452 is the
within-cell bound. HALO is the written tail.

## Open next questions

1. **Does the restricted gate absorb one section error `p^6 exp(-p^2)` and
   one global tail `p^{10} exp(-p^2)`?** The two errors are not the same
   `ε`. Their sum is `p^6 (1 + p^4) exp(-p^2)`, not `2 p^6 exp(-p^2)`. The
   first step is to place the factor `1 + p^4` in the exponent and clear
   the eighths. HALO already assumes `||H^{-1}||_2 ≤ p^{10}`; this question
   does not ask for a proof of that assumption.

## Credit

- The identity and the factor `p^{10}` are the locality audit's, applied to
  HALO's polynomial.
- The within-cell `p^6` bound, and the refusal to move the global reference,
  are #4452's.
- The conditional `p^6` bound under `||H^{-1}||_2 ≤ 16 p^2` is #4406's.
- The question is #4520's.

Prepared by James Reed with substantial Cursor Grok 4.7 assistance. Apache-2.0.
