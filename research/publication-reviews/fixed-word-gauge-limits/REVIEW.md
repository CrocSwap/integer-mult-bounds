# Independent review: fixed-word gauge limits

Accepted for the scope stated in the package. No blocking issue or required change was found. This review did not change the package.

The reviewed manifest is:

```text
82c3a08fdb3a5d90fd44d7da70c8b51b518723cf8f2325e10cffba896557d836
```

## Proof and scope

I read the package proof, the four retained source proofs and reviews, the source metadata, and the eight adapted checkers. I checked each adaptation against its pinned campaign source. The changes concern file access, output paths, and source metadata. The mathematical checks remain in place.

The exact boundary identity applies to the fixed scalar access grammar. ADD and COPY operands have the same gauge. CLEAR starts a new lifetime. The proof does not claim that these are all possible gauges for a different scalar schedule. Both original scalar endpoints are checked on all 712 input columns. The graph includes every native event, including the 1,570 old rank-zero wrappers.

The result over all 511 nonzero lines fixes one line for the entire word and permits binary choices on the scalar components. It proves that total native rank cannot decrease. Each even line also has a nondecreasing rank on each native edge. It does not prove every child-moment bound for the other odd lines.

The stronger concave-cost and equality-rigidity results have the stated smaller scope: the 16 common odd lines, the binary product `C_128 C_256`, and the four-state family. The exact flow/cut checks include every negative-cover branch. Their capacity, conservation, cut equality, and residual reachability checks prove the stated minima and rigidity. The capped-cost decomposition has nonnegative coefficients under the stated hypotheses.

The full-frame example is retained with its correct sign. It removes one paid child and adds 48 to total rank. Thus it defeats a general claim for every increasing concave cost. The restricted moment proof uses `0 <= b <= 2/5`. Its strict bound follows from the two stated integer fifth-power inequalities. The backward frame is the conjugate `F T_415 F^-1`.

The arbitrary common-product theorem is a local statement under `A subset U`. For a relative product, `B` has image in `A` and kills `U-perp`. The intersection formula gives rank `e-dim Fix(B|U)`. Each fixed vector is in the image of `B|A`, whose rank is at most the restricted Gram rank. This proves the lower bound `e-s`. The source has `e=8` and `s=2`, and the product `C_128 C_256` attains rank six at all eight centres. No full-graph cost result follows from this local bound.

## Executed validation

The independent replay used a separate copy of all 54 files. The files have separate inodes and were read-only. The command used isolated, optimized Python 3.14.7, one checker at a time, and an empty `PATH`. Git was unavailable to the replay. [COMMAND.json](COMMAND.json) records the exact command and environment.

The replay passed in 99.646 seconds:

```text
PASS_FIXED_WORD_GAUGE_LIMITS
```

The nine checks verified 1,609,650 pairing ranks, 10,488 integer paths, 3,384 common-line rank flow/cut cases, 800 common-line capped-cost cases, and 13 damage controls. The fresh output is in [cold-output/REPLAY.json](cold-output/REPLAY.json).

Five of the nine detailed receipts match the packaged receipts byte for byte. The other four differ only in the copied package path or measured memory use. All mathematical fields agree. [RECEIPT-COMPARISON.json](RECEIPT-COMPARISON.json) states the exact normalization; [RECEIPT-DIFFS.json](RECEIPT-DIFFS.json) retains the raw differences.

I read the historical archive from commit `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. Its hash and both compressed source members match the package. All 27 campaign source pins match. Eight checker changes were reviewed. The [independent scope check](scope_check.py) imports no package checker. It checks the two source profiles, the common intersection and Gram rank, the eight sharp rank-six descents, the full-frame cost change, and the rational moment gap. It passed. All package files remained unchanged. More than 3 GiB remained free.

## Limits

This is an independent agent review and exact replay of the submitted package. It is not a new mathematical search or a human review. The graph-specific claims use the historical source. They do not transfer to the changed selected construction at publication base `b58ad9ef4d4e861b0eaa5dba41742bdc072dca51` without a new source-bound proof.

No selected current-construction cold replay, changed native circuit emission, complete recursive repricing, or supplier construction was run. The package gives no new complete kappa bound.

The machine-readable result is [REVIEW.json](REVIEW.json).
