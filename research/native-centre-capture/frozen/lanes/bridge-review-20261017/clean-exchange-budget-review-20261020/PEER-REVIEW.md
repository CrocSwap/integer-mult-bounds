# Peer check of the sharp mixed-rank bounds

On 2026-10-20, the budget-geometry producer independently checked
the final section of `REVIEW.md`. It found no material defect.
It checked these points:

- \(c_1<c_2<2c_1\). Thus the maximum and minimum H1/H2 bills
  have the stated forms. The minimum increases at both
  parity transitions.
- The concavity transfer is valid with \(f(0)=0\). It sends
  rank from one partial child to another until one is full
  or the other is empty.
- The four packed profiles have total ranks 197, 198, 181,
  and 182. Rank 17 is the correct size cap.
- Both of the producer's pinned exact engines give the
  claimed strict sign for all eight extremal witnesses.

The peer requested one clarification: the packed minimum
must be stated to increase with total rank, including at
a multiple of 17. That sentence was added before this
review was frozen. It makes the exclusion of all larger
total ranks explicit.

The peer check concerns the new mixed-rank consequence.
It does not independently admit the proposed routed
caller or cleanup.

No publication is authorized. Before any future PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
