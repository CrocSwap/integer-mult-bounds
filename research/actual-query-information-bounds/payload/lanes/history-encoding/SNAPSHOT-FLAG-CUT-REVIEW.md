# Independent review of the shared snapshot cut bound

The proof in `../cover-algebra/SNAPSHOT-FLAG-CUT.md` passes review. It
proves a lower bound of 42 native rank units in the stated scalar
network model. It does not prove 64, and it gives no circuit below 64.

The proof uses one ordered binary basis. For any subspace, the set of
leading positions is the set of leading positions of its nonzero
vectors. Thus inclusion of subspaces gives inclusion of these sets.
An increasing frame edge enters exactly as many pivot cuts as its
dimension increase. This fact holds for any nested frames, not only
the retained edges checked in the receipt.

The shell for position `i` has zero dual coordinates above `i` and
dual coordinate one at `i`. A vector with leading position `i` has
zero coordinates below `i`. Their dot product is one. The reviewed
snapshot support law therefore excludes every shell input from all
free observations inside its cut. On the valid input family
`X=JY`, with all helper and private inputs zero, the final free
baselines also vanish.

The required output on that shell has rank `rank(R_shell)`. If each
payload field has dimension `d`, its output rank is
`d*rank(R_shell)`, while one entering field carries at most `d`
dimensions. This gives the cut inequality for full payload arrays.
It permits scalar fanout, reuse, and cancellation. It does not sum
separate output-tree costs. Summing the nine cuts charges each
monotone edge only its dimension increase.

## Independent calculation

`review_snapshot_flag_cut.py` imports no producer or reviewed checker.
It reads the pinned interface, snapshot source, and clean backward
word. It builds all 512 flag coordinates by direct enumeration. It
derives each pivot set by enumerating the frame span. It obtains the
shell ranks from exact rational elimination of the eight-dimensional
Gram matrices. These methods differ from the producer's echelon
calculation.

The check covers all 1004 frames, 23279 shell separation cases, and
2880 distinct retained native edges. It gives the exact shell ranks
`[0,1,1,2,8,6,8,8,8]`. Reversing the shell order causes 6293 separation
failures. Reducing a positive edge charge by one also fails.

Run:

```text
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/history-encoding/review_snapshot_flag_cut.py
```

The result is `PASS_INDEPENDENT_SHARED_SNAPSHOT_FLAG_BOUND_42` in
`SNAPSHOT-FLAG-CUT-REVIEW.json`. The receipt pins both reviewed proof
and candidate receipt. It also pins the independent exact snapshot
support review. That premise is inherited; this small check does not
repeat the full 712-input core replay.

## Scope

The bound applies to increasing frame transitions that preserve the
logical field content, with scalar mixing at each frame. It grants
all recorded times and arbitrary cache storage. It does not cover a
change of logical address code, a changed core, or new cross-parent
child access. A positive construction still needs literal phases,
time order, arbitrary-state cleanup, private lifetimes, and a full
supplier invoice. No such construction is part of this review.
