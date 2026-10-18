# Validation receipt and handoff

Validated on macOS arm64 with standard-library CPython 3.9.6 and 3.12.14.
Exact base: `f567884aeb8851b6e794af1184119a3bfbe1e631`. OS assignment seed 29.
This package makes no runtime or memory-performance claim.

## Completed evidence

- Main integer census and separately written rational/primitive-word census:
  174,048 ordered cases, identical complete record SHA256
  `6a3cca7f992bba884e5662ae81923f59ffad2f3de824affe55a8920073fe073e`.
  All 149,184 finite nonunit cases lose. Both scripts check frozen typed receipts.
- All 162 affine-tail coefficient/direction families have the predicted price
  at exponents 3,4,5,8,29,64,127. Tests additionally compare explicit primitive
  lengths at 3,4,9,29,128. The written all-k argument is in PROOF.md; no finite
  test is presented as a proof of infinitely many cases.
- Independent literal lowering: 137 distinct coefficients and 548 boundary
  cases, including arbitrary dirty coefficient work. Forward and
  inverse-transpose restored-pair wrappers each pass 56 basis cases.
- Concrete controls: omitted preparation, omitted restoration, unpaid shears,
  reversed inverse-transpose order, wrong tail slope, source drift, missing
  archive, omitted file/member pins, and integer/Boolean/float receipt corruption.
  Profitable unit cases and a profitable synthetic nonunit case guard scope.
- Ten package tests pass on normal Python 3.9.6 and optimized Python 3.12.14.
  The suite also runs both standalone commands with `-I -O -B` in a minimal
  offline closure whose path contains spaces, compares both full receipts,
  rejects a corrupted receipt under `-O`, and verifies every file is unchanged.
- `make selected-record-check` and all five `test_selected_result.py` tests pass.
  All eight source files were independently compared with their exact base
  Git blobs. Staged whitespace and addition-only scope checks pass.

A bounded AI adversarial review found no mathematical defect. It found that
omitted manifest entries could weaken validation; this was repaired with exact
required file/member inventories and a source-manifest digest in EXPECTED.
The missing-pin regression controls pass. Separate AI work is disclosed;
there is no independent human review claim.

## Scope of checks not performed

This is a negative cost result and installs no candidate circuit. Full
`make verify`, selected cold supplier regeneration, global hosting/invoice/
assembly admission, native frame/phase operator replay, Linux/hosted CI and
Lean were not run. Original complete scalar invoices are recounted, not
substituted for those checks. The inherited full-theorem assumptions remain.

## Coordination and next step

Final upstream refresh found main unchanged at the stated base; recent PR
metadata was inspected through #904. All-state searches for scaled compensation
and nonunit multipliers found no duplicate within this inspection. PR901 is the
direct, credited unit-family comparator; #749 and #816 are related predecessor
families. PR883 changes the preceding X4 precondition and PR864 concerns frame
assignment. Their scope differs and no code or savings are combined.

Review the cost definition and tail proof, then run the two verifier commands.
The result rules out this specific family extension; it does not recommend
repeating a broader search or imply that a stronger supplier exists.
