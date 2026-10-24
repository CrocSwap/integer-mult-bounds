# Peer check of the multi-target schedule

On 2026-10-20, the bridge-access producer checked the proposed
multi-target schedule independently. The producer confirmed
the following points:

- Keep the 96 ordinary source fields in the old s FULL views
  between target queries. Enter and restore them once, for
  192 map calls.
- For each target bank, make the sixteen selected copies in
  global FULL before entering its sixteen old target views.
  Run the complement query, then restore those target views.
  This costs 32 maps per target bank.
- The selected X fields stay in global FULL. They remain
  available for the same-port copies.
- The complete query costs \(6552+1888k\) scalar primitives
  and \(640+32k\) maps.
- The target banks must be distinct and have paid FULL
  hosting. This calculation does not provide that host.

The peer check concerns the new schedule theorem. It does
not replace the independent replay of the producer's actual
one-target word in `REVIEW.md`.

No publication is authorized. Before any future PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
