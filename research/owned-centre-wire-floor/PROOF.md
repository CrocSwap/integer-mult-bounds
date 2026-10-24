# Floor for the owned-centre wire of #4470

## Setting

Frames are subspaces of F_2^9; a register in frame U is physically in the chart of U. As in `native.synthesize`, the chronological scalar word, every coefficient, every native warp (with its fixed input and output frames) and every helper entrance and exit stay fixed. A persistent L role may change frame only by a nested ascent U ⊂ V, priced at rank dim V − dim U. Following #4534's owned-wire retiming theorem (`research/frame-aware-native/OWNED-C-RETIMING.md`), the frame of every scalar contact, including every contact of the owned register C, may be retimed. Every C transition must be paid. Here C may move along nested frames in either direction, priced |dim V − dim U|. The original centre transport is such a move (frame of dimension 8 to frame 0 forward, the reverse backward). After CLEAR, the frame of C is free. A two-register contact needs both registers in one common frame.

Non-nested C transitions (a general Clifford transport priced by its actual Fourier rank) are outside this model.

## Lemma 1 (interval propagation)

Process the word forward. Start each L role at its start frame, take the join of the participants' running bounds at every scalar contact, and reset at each warp output. The result is a frame Low(i) contained in the chart of contact i under every legal retiming. Process the word backward, take the meet of running bounds, and reset at warp inputs and final frames. The result is a frame Up(i) containing that chart.

*Proof.* Along an L role, frames only ascend between contacts and warps. A contact's chart therefore contains the role's chart at its previous contact, or the fixed output frame of its previous warp, or its start frame. It is contained in the role's next chart, next warp input or final frame. Both participants of a contact share its chart. Induction over the chronology gives both claims. ∎

`verify.py` checks Low(i) ⊆ Up(i) at every contact in both orientations, and that every warp input and final frame lies above its running lower bound.

## Lemma 2 (path bound)

For nested moves g_0 → g_1 → … → g_n with move cost |dim g_j − dim g_{j+1}|, the total cost is at least dim g_0 − dim(g_0 ∩ g_1 ∩ … ∩ g_n).

*Proof.* Let I_k = g_0 ∩ … ∩ g_k. Then I_k/(I_k ∩ g_{k+1}) injects into g_k/(g_k ∩ g_{k+1}). So dim I_k − dim I_{k+1} ≤ dim g_k − dim(g_k ∩ g_{k+1}), and the right side is at most the cost of a nested move between g_k and g_{k+1}. Sum over k. ∎

Moreover, if A ⊆ g_0 then dim g_0 − dim(g_0 ∩ X) ≥ dim A − dim(A ∩ X), because A/(A ∩ X) injects into g_0/(g_0 ∩ X).

## Theorem

In every one of the 8 centre blocks of #4470, in both orientations, the owned C wire pays rank mass at least 8 under every retiming in this model. Its moment is therefore at least 8^t for 0 < t ≤ 1, which is the current charge of one rank-8 job.

*Proof.* In a block, the C wire visits the source contact (forward COPY, or its dual ADD) and the 22 target contacts in some chronological order. Its frames there satisfy g_src ⊇ Low(src) and g_i ⊆ Up(t_i). Forward, the path starts at g_src. Backward, it ends there, and reversing a path leaves its cost unchanged. By Lemma 2 and the remark after it, the cost is at least dim Low(src) − dim(Low(src) ∩ Up(t_1) ∩ … ∩ Up(t_22)). `verify.py` computes dim Low(src) = 8 and a zero intersection in all 16 cases. Splitting a mass of 8 into several jobs only raises the moment, because r^t is subadditive. ∎

The joint intersection is essential. For any single target, dim(Low(src) ∩ Up(t_i)) is 1 or 2, so a one-target bound gives only 7. A nonzero line of Low(src) lies in Up(t_i) for at most 8 of the 22 targets.

## Consequence for #4534's rejected candidate

The candidate replaces, in each of the 18 full calls, 56 rank-1 and 56 rank-4 paid jobs by 56 rank-5 jobs, with unchanged rank mass. On #4470's complete invoice (`research/joint-helper-lattice/RESULT.json`) its certified raw root is 0.0030511780, against the baseline 0.0030201659 (+1.03%). Adding 0.42 rank-1 C jobs per full call keeps the root above the baseline; adding 0.43 drops it below. A net extra C charge of half a rank unit per call removes the gain. By the theorem, the C wire cannot give back any mass to pay for it. Any such shape gain must come entirely from L-side merges with an unchanged C wire. The search in `search/` found none.
