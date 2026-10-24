# The shared-row sum does not lift to the operator 2-norm

**Claim type:** a separation between a row sum and an operator norm.
**No new κ.** The ideal-gap gauges stay hypotheses. The selected record
remains `23/10000`.

## Question

#4512 adds two section errors on the shared global row and asks whether
that sum lifts to `||B - C||_2 < 2 ε`, with `ε = p^6 exp(-p^2)`. The named
step is to decide whether the two operators in the polynomial split are
these two section inverses, and whether their polynomials agree off the
matched rows.

## Lemma

They are not the same hypothesis.

1. **One polynomial, in the norm of the whole object.** #4490 states that
   the pair of inverses `(B, C)` meets `||B - C|| < 2 ε` once both are
   within `ε` of the same polynomial. #4509 repeats that sentence at
   ceiling `9 p^2`. The norm is the norm of `B - C`, not the norm of one
   row.

2. **Two polynomials, identified only on rows at distance `A`.** #4491
   gives `||P - H_sec^{-1}||_2 < ε` for each section that meets the #4452
   gauge, and it says the core row is a row of that operator. HALO's exact
   sentence applies to any row at distance `A = ceil(p^{48})` from a
   section boundary. It does not identify the section polynomial with the
   global polynomial on the other rows.

3. **A small row does not bound the operator 2-norm.** Let

```text
M = [ 3  0 ]
    [ 0  9 ].
```

The first row has squared Euclidean length `3^2 = 9`, and `9 < 8^2`.
The second standard basis vector is sent to `(0, 9)`, whose squared
length is `81`, and `81 > 8^2`. Since `||M||_2 ≥ ||M e_2||_2`, the
operator 2-norm is not strictly below 8. The shared-row sum can hold
while `||B - C||_2 < 2 ε` fails.

4. **A zero row does not force the operators to agree.** The matrix with
   rows `(0, 0)` and `(0, 2)` has first-row squared length 0 and sends
   `e_2` to a vector of squared length 4. Row agreement does not give
   `||P_B - P_C||_2 = 0`. The triangle then keeps an extra term. The
   integer upper bound `3 + 2 + 3 = 8` is not strictly below `2 · 4`.

The locality audit already says some row at distance exactly `(2J - 1) W`
differs from the global row, and it bounds a core row of the inverse
difference by `2 p^{10} exp(-p^2)`. That is a different split. It is not
this operator comparison.

## Proof

The bridge identity is `B - C = (B - P) + (P - C)` for one polynomial `P`
in one normed space. Substituting two section polynomials produces

```text
B - C = (B - P_B) + (P_B - P_C) + (P_C - C).
```

#4491 bounds the first and third terms in the operator 2-norm only under
the two gauges, and only against each section's own polynomial. HALO
removes `P_B - P_C` on a row at distance `A`. The displayed matrix shows
that removing it on one row does not remove it from `||·||_2`. Comparing
squared lengths avoids a square root: both vectors are integer, and the
Euclidean norm is strictly smaller exactly when the squared length is
strictly smaller.

This package does not assert that the Gaussian section polynomials differ
by the displayed matrix. It asserts that the rows inherited from #4491 do
not imply the operator hypothesis used by #4490 and #4509.

## Not covered

- A bound on `||P_sec - P_global||_2` off the rows at distance `A`.
- Either ideal-gap hypothesis `1 - 1/(8 p^2)`.
- The global-inverse summand `||P - H^{-1}||`.
- Editing the #4100 notes. They still say `g p^{10 g} exp(-p^2)`.
- Any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/gaussian-operator-lift --check-only
python3.12 -B scripts/research_package.py --package research/gaussian-operator-lift
```

Base `f9f85c1e4fa1e955ff39f10fca447e3e2a4e4adc`, priority revision 7, selection
refresh κ = `23/10000`. Upstream was fetched at 2026-10-22T03:07:14Z and was
that commit.

Overlap snapshot: open PRs fetched 2026-10-22T03:09:20Z (299 records) and
discussions fetched 2026-10-22T03:10:01Z (3390 records). A search for
`operator 2-norm`, `shared global row` and `same polynomial` returned #4512,
which asks this question, #4511, which still asks for one common polynomial,
and #4490, which states that hypothesis. The other hits use "the same
polynomial" for unrelated series. No result shows that a small row forces
`||B - C||_2 < 2 ε`. A search miss is not a novelty certificate. #4490 is
the one-polynomial triangle. #4491 is the operator section error. HALO is
the distance-A row sentence.

## Open next questions

1. **Is `||P_sec - P_global||_2` bounded off the rows at distance `A`?**
   The operator hypothesis needs one polynomial, and the matched rows do
   not determine the difference. The first step is to use the locality
   audit's sharp row at distance exactly `(2J - 1) W` as a witness that
   equality can fail, then look for an upper bound. Do not reuse the
   `2 p^{10}` inverse split as that bound.

## Credit

- The one-polynomial triangle is #4490's, repeated at ceiling 9 by #4509.
- The operator section error and the core-row sentence are #4491's.
- The shared-row sum that this package does not lift is #4512's.
- The sharp row at distance `(2J - 1) W`, and the two-term `p^{10}` bound,
  are the locality audit's.
- The exact-row sentence at distance `A` is #4100's.

Prepared by James Reed with substantial Cursor Grok 4.7 assistance. Apache-2.0.
