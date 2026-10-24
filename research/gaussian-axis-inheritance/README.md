# One core row inherits two of the three axis hypotheses

**Claim type:** an attribution of three hypotheses to earlier packages.
**No new κ.** The ideal-gap gauge stays a hypothesis. The selected record
remains `23/10000`.

## Question

#4509 asks which of

```text
||B|| ≤ 9 p^2,
||C|| ≤ 9 p^2 + ε,
||B - C|| < 2 ε,
```

with `ε = p^6 exp(-p^2)`, a core row past `ceil(p^{48})` inherits from
#4491 and from #4493.

## Lemma

Let `p ≥ 2` be an integer and let `A = ceil(p^{48})`. For an output kept at
distance `A` from every face, the inheritance is:

1. **Row identity, with no gauge.** #4491 proves `R < p^{26} < p^{48} = A`.
   The section-polynomial row is the global polynomial row.

2. **One section error, under the #4452 gauge.** #4491 then gives
   `||P - H_sec^{-1}||_2 < ε`. That is the input `||B - P|| < ε`, with
   `B = H_sec^{-1}`.

3. **Inverse ceiling, under the same gauge.** #4493 proves `U < 9 p^2` as a
   formula for every integer `p ≥ 2`. Under the gauge, the Neumann 1-norm
   and ∞-norm are strictly below `U`, hence strictly below `9 p^2`. That
   strict bound meets `||B|| ≤ 9 p^2`.

4. **Approximant norm, under the same gauge.** #4509 turns the ceiling and
   the one section error into `||P|| < 9 p^2 + ε`.

5. **Two-inverse difference.** One core row supplies one section error. The
   bound `||B - C|| < 2 ε` requires a second section inverse within `ε` of
   the same polynomial.

The ideal off-sums `1 - 1/(8 p^2)` remain a hypothesis. This package does
not re-prove the radius, the coefficient 9, or the triangle split.

## Proof

The distance comparison is the exponent gap already recorded by #4491:
`p^{48} = p^{26} p^{22}` and `p^{22} ≥ 2^{22} > 1`, so `p^{48} > p^{26}`.
HALO's sentence that a row at distance `A` has its polynomial row exactly
equal to the global row therefore applies. That sentence does not use the
ideal gaps.

The operator sentence in #4491 is conditional. It states
`||P - H_sec^{-1}||_2 < p^6 exp(-p^2)` when the section meets the #4452
gauge. That is one summand of the triangle

```text
B - C = (B - P) + (P - C).
```

The integer shadow `|(8 - 5)| = |(8 - 6)| + |(6 - 5)|` separates the pieces.
The single piece `|(8 - 6)|` is strictly smaller than the whole difference,
so one section error does not supply `||B - C|| < 2 ε`.

#4493's formula bound is strict: `U < 9 p^2`. A number strictly below
`9 p^2` satisfies the closed hypothesis `||B|| ≤ 9 p^2`. The same README
states that this operator reading holds when the #4452 gauge holds, because
the Neumann 1-norm and ∞-norm are already strictly below `U`. The formula
comparison itself does not use the gauge.

#4509 then adds that one error to the ceiling: `||P|| < 9 p^2 + ε`. The
polynomial, not a second inverse, is the approximant in that statement.

## Not covered

- A proof of the ideal gaps.
- A second section inverse within `ε` of the same polynomial.
- Editing the #4100 notes. They still say `g p^{10 g} exp(-p^2)`.
- Any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/gaussian-axis-inheritance --check-only
python3.12 -B scripts/research_package.py --package research/gaussian-axis-inheritance
```

Base `f9f85c1e4fa1e955ff39f10fca447e3e2a4e4adc`, priority revision 7, selection
refresh κ = `23/10000`. Upstream was fetched at 2026-10-22T02:57:30Z and was
that commit.

Overlap snapshot: open PRs fetched 2026-10-22T02:58:14Z (296 records) and
discussions fetched 2026-10-22T02:58:59Z (3384 records). A search for
`second section inverse`, `one core row inherits` and `H_sec` returned this
draft, #4491, the ceiling-10 bridge, and the locality audit. That audit adds
two `p^{10}` errors. It does not attribute the ceiling `9 p^2`. A search
miss is not a novelty certificate. #4491 is the row match. #4493 is the
coefficient 9. HALO is the row sentence.

## Open next questions

1. **Does a second core row supply the missing section error?** The
   two-inverse difference needs `||C - P|| < ε` for another section inverse
   against the same global polynomial. The first step is to apply the #4491
   reading to that second row and add the two errors.

## Credit

- The row identity and the one section error are #4491's.
- The formula `U < 9 p^2`, and its gauge-conditional operator reading, are
  #4493's.
- The triangle that turns one error and the ceiling into the approximant
  norm is #4509's.
- The three hypotheses are #4508's.
- The written error `g p^{10 g} exp(-p^2)` is #4100's.

Prepared by James Reed with substantial Cursor Grok 4.7 assistance. Apache-2.0.
