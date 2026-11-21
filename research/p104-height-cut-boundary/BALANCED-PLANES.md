# Every global x-versus-y paired chart cut still permits X = 28

This screen uses the pinned #7852 head and `pinned/` data documented in
`RESULT.md`. It strengthens the separate witnesses in `CHART-SCREEN.md` and
`MEMBERSHIP-SCREEN.md`. It is a relaxation result, not a legal word or full
`BankedGraph` instance.

For each of the 104 actual port labels, choose the x-path's intermediate
2-plane as the span of that label and the next label in the pinned port
order. Let `X_p` count the x-field path occurrences through plane `p`.
The checker builds a bipartite compatibility network: each of the 200
y-field units may use a plane `p` only if `p` is contained in that field's
actual hyperplane, and plane `p` has capacity `X_p`. An integer max-flow
finds all 200 units and the checker independently verifies the result, so
the y-path count `Y_p` equals `X_p` on each of the 104 planes. All 400
paths have nested actual field endpoints; the added four rank-2↔9 banks are
the flag moves from `MEMBERSHIP-SCREEN.md`.

Consider **any** chart predicate P in the following family: all 104 x-lines
and `top` lie inside P; `bottom` and all 104 y-hyperplanes lie outside P.
All other charts, including every intermediate 2-plane, may lie on either
side. Every x endpoint pair is inside, every y pair is outside, and the
full paired cut therefore requires at least 104 extra crossings in each
direction. For each plane p independently:

- If p is outside, its `X_p` x paths each leave and re-enter P.
- If p is inside, its `Y_p = X_p` y paths each enter and leave P.

The total is exactly 200 bank crossings each way from the field paths,
before the four additional banks. Thus **every** predicate in this family
satisfies the required 104 paired extras, with no enumeration of the plane
choices. Meanwhile every basic arbitrary-chart cut follows from the
400 path decompositions. The same witness also checks all 1022 directed
height cuts, all nine flag cuts in both directions, and all 104 natural
paired cuts `P_q(C) := q ∈ C` in both directions. It has 804 bank
occurrences, `D=14`, `R=14`, and `X=28`. The flag inequalities give the
matching lower bound for this named relaxation.

The construction still fails a different **single-port** paired chart
cut. The checker constructs one for port q=11, putting that port's two x
endpoints inside, its y endpoints outside, other port lines outside and
other port hyperplanes inside, and selecting intermediate chart sides to
minimize crossings. The measured `(bank out, bank in, field out, field in)`
is `(0,396,0,396)`, while the full model requires one additional bank in
each direction. This explicitly rules out the witness as a full banked
network. The example does not prove whether adding this cut raises the
relaxation's optimum.

Replay with `python3 -S verify_balanced_planes.py`; the output is saved in
`verify_balanced_planes.log`. It checks six source SHA-256 pins, integral
matching and plane capacities, all nested path containments, flag and
height counts, all q-membership cuts and the failing single-port cut.
The claim for all P in the specified global family follows from the
plane-by-plane counting argument above. No output transfer matrix,
chronological word, all-paired-cut proof, crossing, or Lean build is given.
