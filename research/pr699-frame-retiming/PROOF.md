# The finite change and its cost

Fix PR699 commit `03e8d7ca494a083e5053cd6b1228f66b98414479` and raw word
`d232183f233899961bf55cac67a18545ed33548d9a7ca7078990d1a83d557c59`.
At zero-based B indices 856, 860, 868, 873, 876, 953, 961 and 965, replace the
rank-four frame by the rank-six frame in `construction/FRAME-RAISES.json`.
The resulting raw word is
`e78047028c7dcd25fb1b6216c2b53eda76d2f91292b21d43f5d1903cc13a5c6c`.

For each changed operation, the union of the previous operand frames is
contained in its new frame, which is contained in each operand's next frame.
The unchanged center and endpoint constraints are also checked. The recipe
builder restores the old annotations and report and compares the entire input
JSON, so there are no unaccounted scalar, boundary or cleanup edits. The
independent checker constructs each subspace as a subset of the 512 points of
GF(2)^9 and checks inclusion directly. Cardinalities give exact dimensions.

Recounting the complete A/B/early-cleanup/final chains, including center
copies, gives the per-operation change

    H_new - H_old = {1:+1, 2:-1, 3:-1, 4:+1}.

The eight changes add to `{1:+8,2:-8,3:-8,4:+8}`. The rank mass is unchanged,
since `1 - 2 - 3 + 4 = 0`. Start and final frames are unchanged, so all 504
helper widths are identical, and the original 72 complete calls, source
access, physical owners, copies, idle suffixes and restoration work are
retained. Global admission independently recomputes the unchanged geometry,
all 36,288 footprints and complete finite invoice; a width-only argument is
not substituted for these checks.

For any 0 < b < 1, set f(r)=r^(1-b). Strict concavity gives

    f(2)-f(1) > f(4)-f(3),
    f(1)+f(4) < f(2)+f(3).

Consequently the complete recurrence moment strictly decreases by this
profile change for every such b. This argument explains the direction of the
improvement without a floating-point search. The two independent rational
moment engines certify the numerical complex endpoint; the bit endpoint and
all 47 outer constraints certify the displayed rational κ.

The finite scalar, frame, phase, native and owner checks validate this
particular conditional witness. They do not establish the inherited all-size
realization or analytic-transfer assumptions. Nor does this note claim a
joint frame-schedule optimum. The finite discovery domain and stopping rule
are recorded separately in the search receipt.
