# Independent agent review: local eight-form capture

Status: PASS after the scope correction below. This is an independent agent
review, not a human review or a formal proof-assistant check. The review covers
the staged local-eight-form-capture package and its exact frozen inputs.
It does not cover GitHub rendering or the final PR text.

## Result and useful scope

The package gives a complete forward local scalar program on 800 arbitrary
input fields: 120 X fields, 120 Y fields and 560 helper fields. It preserves X,
sends Y to Y+SX, and sends the eight helpers with indices 758 through 751 to
h_i+C_i(59X/4+Y). It preserves every other helper. The selected eight helpers
remain changed; the program does not restore them.

This gives an exact fixture for capture into existing, arbitrary dirty helper
values. Its initial owner inventory identifies those helpers with future Y data
owners. It does not treat the live owners as private workspace. The result can
be used to test a proposed local composition against the old owner values.
It does not establish that such a composition has a lower complete cost.

The exact C rows have entries in {0,+1,-1}, support 56 each, and C C^T=56I.
The identity S=I-C^T C/4 applies on the 112 code ports. The other eight ports
have zero S rows and zero C columns; the displayed S identity must not be
extended to all 120 ports.

The omitted-centre base word has map Y -> Y+SX+Dh and preserves h. Let P
insert the eight C rows into the selected helpers. The program first forms
h1=h+PY, then sets Y1=Y-Dh1, then applies the base word, and finally adds
(59/4)PX to those helpers. The base step sends Y1 to Y+SX. This proves the
stated boundary composition. The sparse-row checker and the separate full
column checker also test the complete map. Since the program is linear, an
exact check of every input column proves the local scalar map for arbitrary
input values, including all arbitrary old helper values.

## Full scalar count and unpriced obligations

The base word has 19,449 scalar operations. Dirt correction has 11,326
operations. Each of the two eight-row loads has 448 scalar additions.
Thus the implemented count is 19,449+11,326+448+448 = 31,671 scalar operations.
This is a scalar program count. It is not a native, physical or recursive
invoice, and it is not a claimed saving against another complete supplier.
The count of 11,326 was reproduced in the full historical receipts. The extra
boundary control independently recounts the base and both load supports.

The saved boundary labels place preload and dirt correction in the zero frame
and postload in the full frame. The extra control checks these frame entries.
This does not prove a paid native or phase realization for the new operations.
No backward program, routed global controller, endpoint decoder, restoration
of the eight data owners, or full recursive cost is supplied. The construction
does not change the complete kappa calculation.

## Resolved explanatory error

The frozen historical review warns that correction from old helper values
would leave an extra DPY term. That term is the correct generic comparison,
but it is zero for this fixed selection. The reviewer propagated all eight
selected helper basis columns through the base word. Each column has zero Y
output, so the corresponding columns of D are zero and DP=0.

The package README now states this fact and says that the historical warning
does not apply to these eight helpers. The frozen text remains unchanged.
The implemented updated-helper order is valid. It is not proved necessary
by a nonzero-error example here. This correction does not change the verified
endpoint or any executable input. The check source and exact result are
check_boundary_counts.py and BOUNDARY-COUNT-CONTROL.json in this review.

## Verification performed

The reviewer ran the driver in a fresh output directory with Python 3.14.7,
using isolated mode and PYTHONOPTIMIZE=1 in the environment. Each child uses
-E and runs sequentially, so the inherited environment does not disable its
assertions. The exact command, version, exit status and literal output are in
COMMAND.json, RESULT.json, stdout.log and stderr.log. The run exited 0 after
27.264490625006147 seconds. Its final line was:

```text
PASS_LOCAL_EIGHT_FORM_CAPTURE 800 8 11326
```

All four complete receipts matched their unchanged historical counterparts:

1. Sparse-row check of the base, boundary composition and captured endpoint.
2. Separate 800-column base check and symbolic boundary composition.
3. Separate 800-column check of the complete captured endpoint and owner map.
4. The endpoint and covariance limitations check.

The worker's separate fresh full replay produced the same complete aggregate
receipt. Both hashes in VALIDATION.json match the published candidate files.
All 17 frozen source/input files match their original workspace bytes, the
manifest hashes and the manifest sizes. SOURCE-AND-EVIDENCE-CHECK.json records
these comparisons. PORTABILITY.diff records the two portable script changes:
explicit input/output arguments replace absolute paths, and optimized-Python
guards were added. Their mathematical operations are unchanged. The other
two historical checkers are byte-exact copies.

The extra boundary check ran with this command from the workspace root:

```sh
python3 -I -B work/project-final-cleanup-20261022/reviews/local-capture/check_boundary_counts.py --package work/project-final-cleanup-20261022/early-projects-audit/packages/local-eight-form-capture --output work/project-final-cleanup-20261022/reviews/local-capture/BOUNDARY-COUNT-CONTROL.json
```

It returned PASS_BOUNDARY_COUNTS_AND_SELECTED_HELPER_D_COLUMN_CHECK. The
check uses the retained independent column interpreter on 120 centre-prefix
columns and eight helper columns. It is not an independent implementation
of that interpreter. The source and word hashes are in its receipt.

## Endpoint limits and relation to current work

The retained endpoint check establishes the stated binary chart covariance
with nonzero translations 15,15,23,39,71,135,263,15. It does not establish raw
commutation. It also rejects the proposed two-tap tensor inverse shortcut:
the tested Fourier character has true tensor inverse eigenvalue -1, while the
two-tap expression gives +1. The inherited geometry proof specifies the entry
X inverse frame as an interpretation, not a paid initial transform. These
facts prevent an unsupported physical endpoint or controller claim.

The current native-centre-capture package at main commit
cef4b52f2a59009865bf8eabde1be3f159063703 uses 640 inputs and 16 centre records,
with different native endpoints. It is distinct from this 800-input,
eight-mixed-form endpoint. Its costs or theorems cannot be transferred by
adding the two bills. A bounded search of current research sources found
other 800-input base checks, but did not find this 59X/4 mixed capture claim.
This is not an exhaustive claim about every historical or open PR. The useful
contribution is the exact closed local program and its limits, not a claim
of a new general capture principle.

## Attribution and publication boundary

The retained notices credit Ali Romman with OpenAI Codex assistance for the
changed R560 words and composition. They preserve DreamingOfClouds' kernel
scripts, chafreaky's paid adapters and distinct-host construction, icekylinx's
split centres, and the earlier geometry sources. The README cites the PR #495
lineage with a commit-pinned proof. The generated word and template are bound
by their own SHA256 values and are not claimed to equal a published generated
file. Original notices and source ledgers are unchanged. Agent assistance
and the absence of independent human review are stated.

The parent coordinator must check the final PR body, commit-pinned links,
GitHub rendering and published readback. No PR, commit, worktree, deletion or
new research direction was made by this reviewer. There are no unresolved
material findings within the local scalar claim stated above.
