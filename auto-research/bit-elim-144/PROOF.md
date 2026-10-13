# Terminal elimination on #144's bit word: argument and scope

**Setting.** This is #144's bit branch. Its word is Swapnil Jain's round-seven PR97 word:

- the side program with its slots;
- non-deferred reads at frame 0;
- phase 1 and the copied centres;
- deferred reads at their sigma frames;
- late V gates;
- the rest of L, the output reads, then L^-1 and V^-1.

#144 keeps 9,543 selected deferred reads at their certified sigma frames, in inherited order. It moves the other 2,022
dirty reads to the zero prelude with the same exact coefficients. The resulting chains are then charged per vertex in
dimension m = 69: auxiliary chain steps, source and target chains and copied centres, each taken three times; a gauge
child 3*sigma per selected slot; and 2v endpoint children. W = 2v + R and the deficit is 2,024 per vertex.

**Operation.** Let u be a deferred output slot that is never a source: never the non-pivot of an addition and never
the pivot of a fan. Its only reader is its own output read into y_T, so its exact adjoint column is C_{T,u} = 1 and is
0 on every other target. Its total contribution to y_T is

    -z_u + (z_u + sum_j a_j) = sum_j a_j,

where the a_j are the values written into u. These are its start copy or V gate and every addition it pivots, each
at its actual time.

Delete u, together with its read, its output read, its inverse writes and V^-1. Apply each forward write to y_T at
the same time and frame. No other register reads u, so every other register evolves exactly as before, and the
scalar identity holds for arbitrary scratch and data over Z, hence over F2. `replay144.py` replays the whole reduced
word with exact integer coefficients and over F2. It also checks that a missing or sign-flipped redirected update
breaks the identity.

**Frames.** Every frame used is an original frame key of the PR97 word, so nondegeneracy and all old nestings are
inherited. The register paths of the remaining slots are unchanged. Each affected target y_T has the new path

    0, sigmas of the remaining selected reads on T (in order), frames of the redirected writes (in time order), t_T^perp.

The levels kept form a subsequence of #144's certified chain. Removing a level from a nested chain keeps it nested,
and #144 already uses positive Z support as a superset. The redirected frames are the eliminated slot's own chain
frames, so they are nested with each other and inside t_T^perp. Every new consecutive pair is checked exactly over Q,
using exact integer bases rebuilt by `check_lifted.py`. These pairs are:

- the last remaining level against the first redirected frame;
- the interleavings between two eliminated slots on the same target.

All 4,725 candidates are selected gauge slots. An eliminated slot's gauge is no longer used, so this is the
re-certification the selection needs.

**Accounting.** One eliminated slot removes its chain steps and its gauge child. Their total rank is
3 (23 - sigma) + 3 sigma = 69 = m, and W drops by one. The target chains keep total rank h - 1 per target, so the
deficit stays at 2,024. The reduced row is rebuilt with #144's `reconstruct()` arithmetic (`row144.py`) and priced
with #144's own `exact_moment`, rare-class contamination, complex certificate, finite bridge and 47-constraint
assembly (`price144.py`).

**Scope.** This is a finite conditional construction. Every interface that #144 retains stays an assumption. That
includes:

- the unchanged complete scalar word;
- the inherited rational frame audit;
- the paired source scheduling;
- completed-core sharing;
- the uniform recursion, analytic and tape contracts.

No new assumption is added. The selection is a deterministic search, and `verify.py` re-derives it from the pinned
sources.
