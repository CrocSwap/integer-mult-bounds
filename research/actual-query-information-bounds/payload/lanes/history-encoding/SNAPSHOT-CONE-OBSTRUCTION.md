# An exact obstruction for one monotone snapshot cone

The backward clean-J word has no nonzero centre query in a single positive
snapshot cone. This result covers all 1,002 positive proper frames in the
actual word. It permits every recorded snapshot in that cone, without a
time constraint. Thus time order is not the obstruction in this model.

This result does not cover a network that merges captures from different
cones. It also does not cover new internal cuts inside a native child, new
changes to the core, or transitions between incomparable frames.

## Source and exact check

`BACKWARD-SNAPSHOT-INTERVALS.json.gz` records the complete rational scalar
rows on 712 input coordinates. Its uncompressed SHA256 is
`3dd1d7388c7d3bca104a21e642b5fcafe175d83a2f1dfce1a3ee3e86b864276c`.
The producer is `emit_snapshot_intervals.py`. It checks every scalar frame
access and every native frame transition. It also checks the final map

\[
 (x,y,h,c)\longmapsto(x-Jy,y,h,0),\qquad
 J=I-R^TR/4.
\]

There are 12,271 distinct rows, 16,687 availability intervals, and 1,004
native frames. An interval `[a,b,j,f,r]` states that row `r` of wire `j`
is available after each event from `a` through `b`, inclusive, with frame
index `f`. The recorded boundary range is 8,106 through 24,913.

The scalar content uses the canonical frame coordinates. Before event
17,606, these are the literal native frames after the entry adapters.
After that event, a non-FULL field needs its specified inverse exit
monomial to expose that canonical view. This theorem grants those views.
It makes no claim that they are free in a constructive word. A zero
formal row is zero in both views, which is all that this proof needs.

Run the exact certificate with:

```text
python3 -I -B work/centre-encoding-campaign-20261014/lanes/history-encoding/check_snapshot_cone_obstruction.py
```

The result is `PASS_EXACT_SNAPSHOT_CONE_OBSTRUCTION`. The checker uses
rational arithmetic. It checks 16,023 distinct frame/row pairs and 98,056
nonzero reduced coefficients. For each of the 1,002 positive proper
frames, it emits an eight-column minor with a nonzero exact determinant.
The receipt is `SNAPSHOT-CONE-OBSTRUCTION.json`.

The two controls reject a wrong frame for a nonzero source coefficient
and a repeated column in a query minor. No sampled rank or numerical
tolerance is used in this certificate.

## Support identity

Write the old port labels as \(q_p\in\mathbb F_2^9\), for
\(0\leq p<112\). Use the following valid family of inputs:

\[
 x=Jy,\qquad h=0,\qquad c=0.
\]

Here all 480 helper inputs are zero. This includes the 78 helpers whose
final frame is not FULL. This choice is an input for an impossibility
proof. It is not a clean-helper assumption for a proposed construction.
On this family, all completed X fields and all final helper fields vanish.

For each actual snapshot in a frame \(U\), its remaining source row has
the form

\[
 \sum_{p:q_p\perp U} a_p y_p. \tag{1}
\]

The checker proves (1) directly from every exact row. It substitutes
\(x=Jy\), deletes the zero helper and private inputs, and checks the
support of each remaining coefficient. This includes data snapshots,
not only helper snapshots.

Fix an actual positive proper frame \(U\), and set

\[
 E_U=\{p:q_p\not\perp U\}.
\]

The exact minor certificate proves

\[
 \operatorname{rank} R_{E_U}=8. \tag{2}
\]

The eight normal lines \(42,7,25,52,82,127,97,76\) do not contradict (2).
Row \(k\) of \(R\) is supported exactly on the ports perpendicular to
normal \(n_k\). But none of these normal lines is an actual rank-one
frame. The actual rank-one frames consist of the 112 old port lines and
eight even lines. Their absence and the normal support identity are both
checked exactly.

## Cone theorem

For an actual positive proper frame \(U\), its snapshot cone consists of
all recorded frames \(V\) such that \(U\subseteq V\). Grant every
snapshot in that cone, without a time constraint. Also grant every final
X and helper field, with arbitrary linear operations on those granted
fields.

No nonzero scalar combination of the eight completed centre queries
\(F_9 R y\) can be formed from these observations.

To prove the statement, restrict \(y\) to the coordinates in \(E_U\).
If \(V\supseteq U\), then \(q_p\perp V\) implies
\(q_p\perp U\). Thus (1) makes every snapshot in the cone zero.
The final X and helper fields are also zero. Every linear operation on
these observations is zero, with every native phase and address map.
But (2) allows \(Ry\) to take any value in eight dimensions. Since
\(F_9\) is invertible, the required nonzero query cannot be zero on all
these inputs. This is a contradiction.

In particular, a cache that starts at zero, first captures content in a
positive actual frame, and then follows only increasing native frames
cannot produce a centre query. The same conclusion holds for any number
of caches restricted to that one cone. Allowing all cone snapshots is
stronger than any one chronological path. A cache that starts empty in
an unrecorded smaller frame must still make its first nonzero capture
in an actual frame; the theorem then applies from that frame onward.

The theorem does not rule out a cache with earlier nonzero captures from
an incomparable frame. That is the precise remaining escape for a
merged snapshot network. It gives no lower bound for such a network,
for a different core, or for the complete supplier.
