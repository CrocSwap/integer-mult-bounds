# Compatible-group projection supplement

The independent audit INDEPENDENT-GROUP-AUDIT.json confirms the following
necessary forward-frame argument, with all 32 pairs recomputed on each provider.
For compatible pairs, all host and borrower labels are distinct. Each new warp
has input U equal to the removed old cold-host end frame, and output E of the
same dimension 4. Existing scalar gate incidence and existing warp pins are fixed.

Given any joint frame assignment, split each physical host chain at its new warp.
Its prefix becomes the old cold-host chain: its frame at the split is U, hence
it satisfies the old end pin. Its suffix becomes the old borrower chain: its
first frame contains E and therefore contains the old zero start; its FULL end
is the old borrower end. This split restores every original gate incidence and
existing warp input/output pin, even for gates shared by different chains.
Thus it projects to an assignment of the original forward constraint graph.
That graph forces the first borrower frame below a dimension-three upper.
Containing the dimension-four E is impossible. Cleanup need not be projected:
this forward-frame model is already a necessary condition for any full word.

There are only two original eligible borrower labels, so compatible groups have
at most two pairs. The explicit counts are recorded in GROUP-SCOPE.json. This
argument covers every image and arbitrary reassignment of gate frames within
the fixed contracts, not just the failed taint-repair trials. It does not cover
changing existing warp interfaces, changing added warp input U, new scalar
topology, entering borrowers or other pre-life grammars.
