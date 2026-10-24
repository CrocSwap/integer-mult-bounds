# Two core rows add their section errors

**Claim type:** a second application of the core-row reading, then a sum.
**No new κ.** Both ideal-gap gauges stay hypotheses. The selected record
remains `23/10000`.

## Question

#4511 asks whether a second core row supplies `||C - P|| < ε` for another
section inverse against the same global polynomial, and then whether the two
errors add. Here `ε = p^6 exp(-p^2)`.

## Lemma

Let `p ≥ 2` be an integer and let `A = ceil(p^{48})`. Take two outputs, each
kept at distance `A` from every face. The distance comparison in #4491 does
not name which output is chosen, so it applies to both: `R < p^{26} < A`.

For each output, #4491 gives two sentences:

1. **Row identity, with no gauge.** The section-polynomial row is the global
   polynomial row.
2. **One section error, under that section's own #4452 gauge.** Then
   `||P - H_sec^{-1}||_2 < ε`, and the core row is a row of that operator.

On those two matched rows the section polynomials equal the same global
polynomial row, so the polynomial cross term is zero there. Write `B` and
`C` for the two section inverses. The row difference splits as

```text
row(B) - row(C) = (row(B) - row(P)) + (row(P) - row(C)).
```

Each parenthesis is one section error. Two positive integers strictly below
4, namely 3 and 3, sum to 6, and `6 < 2 * 4`. Two strict errors therefore
add to a strict two-error bound on that shared row.

A polynomial gap of 2 between the rows spends the room: `3 + 2 + 3 = 8`,
and 8 is not strictly below 8. The row identity is what removes that gap.
One error alone is 3, which is not the two-error sum 6.

## Proof

#4491 proves `R < p^{26} < p^{48} = A` for every integer `p ≥ 2` and every
admissible bandwidth `W`. Nothing in that comparison depends on a row index,
so the second output clears the same radius. HALO's sentence that a row at
distance `A` equals the corresponding row of the global polynomial therefore
applies to each output. Where both rows equal that global row, they equal
each other, and the cross term in the split above is zero.

Each operator sentence remains conditional on its own section meeting the
#4452 gauge. One section's gauge does not cover the other section. This
package does not re-prove either sentence. It only adds the two errors
after both readings are granted.

The integer shadow uses a cap of 4 and two errors of 3. Their sum is
strictly below twice the cap. Inserting a gap of 2 makes the sum equal
twice the cap, so the strict bound fails. The same arithmetic shows that
dropping either error leaves a quantity other than the two-error sum.

## Not covered

- Either ideal-gap hypothesis `1 - 1/(8 p^2)`.
- The operator norm `||B - C||_2` of the two section inverses. Off the
  matched rows the section polynomials need not agree.
- The global-inverse summand `||P - H^{-1}||` on the same row. #4491 leaves
  that summand open.
- Editing the #4100 notes. They still say `g p^{10 g} exp(-p^2)`.
- Any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/gaussian-second-row --check-only
python3.12 -B scripts/research_package.py --package research/gaussian-second-row
```

Base `f9f85c1e4fa1e955ff39f10fca447e3e2a4e4adc`, priority revision 7, selection
refresh κ = `23/10000`. Upstream was fetched at 2026-10-22T03:04:25Z and was
that commit.

Overlap snapshot: open PRs fetched 2026-10-22T03:04:33Z (297 records) and
discussions fetched 2026-10-22T03:05:16Z (3385 records). A search for
`second core row`, `second section inverse` and `two core rows` returned
#4511, which asks this question. A search for `both pieces are strictly
below` returned the ceiling-10 split and the ceiling-9 split. Both leave
the two section errors as hypotheses. A search miss is not a novelty
certificate. #4491 is the reading applied twice. HALO is the row sentence.

## Open next questions

1. **Does the shared-row sum lift to `||B - C||_2 < 2 ε`?** The sum above
   holds where both section polynomials equal the same global row. #4509
   uses the two-error bound as an operator norm. The first step is to
   decide whether those two operators are these section inverses, and
   whether their polynomials agree off the matched rows.

## Credit

- The row identity and each section error are #4491's, applied once to
  each output.
- The triangle shape is #4509's. This package supplies the two row errors
  that triangle was missing.
- The question is #4511's.
- The core distance and the exact-row sentence are #4100's.
- The locality audit's two `p^{10}` errors are a different bound.

Prepared by James Reed with substantial Cursor Grok 4.7 assistance. Apache-2.0.
