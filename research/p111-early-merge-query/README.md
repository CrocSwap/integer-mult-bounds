# Draft: P111 early-merge query transport

**No new kappa is claimed. Physical/native, owner/hosting, precision and complete
supplier admission are pending. The selected frontier is unchanged.**

For puncture 0 in the current PR1297 base word, a pinned 16-value query expression
can be gathered using binary merges at smaller common frames. Directly moving
each value to the final hyperplane costs 10 H5 + 6 H6, transport rank 86. This
explicit tree uses 23 H1 + 6 H2 + H4, transport rank **39**. This changes the
no-early-carrier-mixing premise of PR1134; it does not contradict that theorem.

The standalone verifier replays every original input and helper coefficient to
the selected values, checks all union frames, reconstructs the punctured query,
and retains all 42 dirty coefficients. Their initial frames are zero, but a
complete compensated decoder has not yet been emitted. All 16 values and their
frames remain unchanged through the end of A, so the query tree can be inserted
there. The historical eager schedule uses eight temporary streams; a four-stream
depth-first schedule is only a planning observation, not yet an emitted native
or host receipt. The original source streams remain read-only during the tree.

A favorable volume calculation at PR1485's complex endpoint gives approximately
0.99999742289562176847, below one. It deletes the puncture's old data paths,
replaces H8 by H7, grants entrance frames, compensation, adapters, temporary work
and target-interface changes free, and allows fractional rank-48 idle packing.
These credits need not be jointly realizable. **This is budget headroom in a
relaxation, not a certified new supplier profile or a new kappa.**

Reproduce with standard-library Python, assertions enabled:

```
python3 -B research/p111-early-merge-query/verify.py
```

The verifier checks source hashes and exact rational/binary arithmetic. It does
not compile or execute native Clifford operations. The included C++ subset-DP
search and its input reproduce the nominated tree; no global optimality claim
is made for query expressions, merge trees, or the complete construction.

Remaining work: emit the complete compensated P111 decoder and its transpose,
verify phases, account for every temporary lifetime and physical disposal,
reconstruct whole-call owners and idle volume, and check full moments/outer
witnesses. Keep this PR draft until those obligations establish an improvement.
All inherited all-size/compiler, common-label/mutable-source, precision/tape,
exact recovery, analytic-transfer, PR559 and PR589 H1-H5 caveats remain.

Sources and credits are in NOTICE.md and SOURCES.json. This is AI-assisted finite
research, with no independent human review or formal multiplication theorem.
