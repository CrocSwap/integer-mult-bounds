# Independent review of the rank-five union cuts

The rank-five claim in `history-encoding/LOW-BIRTH-UNION-CUTS.md` passes
independent review. The reviewed proof has SHA256
`d85d71839a600f7d8d0cb511530ca2d1169f0efa543f8c342d2b2cbfe9396629`.
The reviewed certificate has SHA256
`caf4ea536cc79ec7cd585b9f3d4714efc86874785cf463dc215d0158caff5607`.

For each of the twelve listed rank-five merge frames, every subspace of
dimension `k` in its exact five-query overlap needs at least `9k` native
rank in the stated model. This result permits shared paths and scalar
cancellation. It does not give a bound for a network that shares work
between different merge spaces.

## Proof check

Fix a source-port test set `E`. A cut contains only nodes at which every
free observation is zero when Y is supported on E, X equals JY, and all
helper inputs are zero. The output query restricted to E must therefore
pass through the edges that enter the cut. Each carried field has at
most one field of rank. Thus the restriction rank is a lower bound for
the number of fields that enter the cut. This remains true when fields
split, merge, or cancel.

The five accepted cuts each have unit weight. Every actual inclusion
edge is charged at most its dimension increase. Each test restriction
is injective on the full five-query space. It is therefore injective
on every subspace of that space. The internal bound is `5k`. With no
new observations after the common rank-five merge, completion to FULL9
costs at least `4k`. These two bounds give `9k`.

For a payload of dimension N, each restriction rank and each carried
field capacity is multiplied by N. The same bound holds in field units.
The model retains the logical meaning of each frame. It does not permit
free changes to that meaning through address operators.

## Independent exact checks

Run from the repository root:

```text
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/cover-algebra/review_rank5_union_cuts.py
```

The checker imports no producer. It reads the pinned snapshot and
interface data and rebuilds the following facts with rational arithmetic:

- All twelve merge frames have dimension five.
- The complete 712-column observation quotient has query overlap of
  exactly five at each frame. The 78 helpers with non-FULL final frames
  remain in this quotient.
- The displayed five-query basis belongs to that overlap.
- All actual positive contained frames and all their inclusion edges
  agree with the certificate.
- Every used source-port test has zero observation at each inside node.
- Each of the five positive cuts is upward closed, has weight one, and
  has restriction rank five.
- Every edge charge is at most its native rank cost.

The exact check passes with assertions disabled. Its receipt is
`RANK5-UNION-CUTS-REVIEW.json`. The checker and source hashes are in that
receipt.

This review does not rerun a floating-point search. It does not check
the other displayed-space certificates in the source proof, chronological
native recipes, synthetic intermediate frames, cross-merge sharing, a
global bound of 64, or a complete supplier invoice. No material finding
remains in the reviewed rank-five claim.
