# Fixed-word gauge limits: publication handoff

The package is ready for separate package review and publication checks.
No commit, push, PR, merge, or selected-result change was made.

Package: `publication-wrap-20261022/packages/fixed-word-gauge-limits/`.
Recommended repository destination: `research/fixed-word-gauge-limits/`.
The package has 54 files and 14,663,858 bytes. Its manifest SHA-256 is
`82c3a08fdb3a5d90fd44d7da70c8b51b518723cf8f2325e10cffba896557d836`.
All files are frozen for review.

Before a PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
The package owner read that file and the current contribution rules at
`b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`. The coordinator must review the
final description, verify all public links, and inspect rendered Markdown.

## Contribution and scope

This is a scoped negative result and an exact boundary theorem. It does
not improve the complete kappa calculation or supply a new construction.
The consumed source remains historical commit
`bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. No result is asserted for the
changed PR #4470 selected scalar word or the PR #4610 word.

The package includes these reviewed results:

- The exact boundary condition `diag(G_out) P = P diag(G_in)` for the
  unchanged scalar word, including arbitrary helpers and phases.
- Minimum total rank change zero for all 511 fixed translation-line
  families, with each old rank-zero wrapper counted. Even lines are
  nondecreasing on each native edge.
- Increasing concave cost limits for the 16 common odd lines, binary
  `C_128 C_256`, and four-state product family. Their zero-rank choices
  are constant on all 1,971 native components.
- The full-frame `T_415` counterexample: one fewer child, rank increase
  48. Its changed cuts have moment increase greater than `47/9800` for
  `0<=b<=2/5`. In the backward word use `F T_415 F^-1`.
- The local rank-six floor for arbitrary products of lines from the
  common five-dimensional subspace, attained at each centre by
  `C_128 C_256`. This does not exclude a complete-cost gain.

The package excludes unreviewed palette and code-closure claims. It also
leaves geodesic normalization outside this focused extraction. No search
producer or floating optimizer is needed. Seven exact certificates and
two exact source archive members form the data closure.

`RELATED-WORK.md` compares PR #4700 at
`34434d4ea5d9edf58529eaf79b543cd6c58f3e41`. Its monotone-chart centre floor
uses a different scalar word, maps, boundary contract, and gauge class.
It is related work, not a consumed dependency or an exhaustive novelty
check. The refresh supplied its exact head, body, and proof.

## Verification

The first full replay passed under CPython 3.14.7 on macOS 26.6.1 arm64
in 104.674 seconds. The package includes all nine JSON receipts under
`evidence/replay/`. The aggregate status is `PASS_FIXED_WORD_GAUGE_LIMITS`.

Decisive counts: both scalar words on all 712 columns; 5,064 native events;
1,570 rank-zero wrappers; 511 lines; 1,609,650 independent pairing-rank
checks; 10,488 paths; 3,384 common-line rank flow/cut cases; 800 common-line
threshold cases; and 13 damage controls under optimized Python. The
product, full-frame, and four-state certificates also passed all their
rank and threshold cases.

A second full replay ran from an exact exported copy under `/tmp`, with
`PATH=/nonexistent` and an unrelated working directory. It passed in
72.088 seconds. All 54 exported files remained byte-identical, and the
source package matched the export before and after the run. The receipt
is `COLD-PORTABILITY.json`; the aggregate result is `COLD-REPLAY.json`.
The final source manifest integrity check passed. More than 8 GiB of free
disk space remained. Execution used one CPU process at a time.

Reproduce from the package directory:

```sh
python3 -I -O -B replay.py --out /tmp/fixed-word-gauge-replay
```

The output directory must be new. The last output line is:

```text
PASS_FIXED_WORD_GAUGE_LIMITS
```

The new package changes only source/input/output paths in the inherited
checkers, the associated source-reader hash, and output provenance paths.
The diff was inspected. Mathematical checks were retained. No fragile
workaround was introduced.

No current selected cold replay, changed native emission, complete
recursive repricing, or hosting construction ran. This package is not a
formal verification of the full multiplication theorem. The fresh replay
and exported replay are producer checks; final independent package review
remains with the coordinator.
