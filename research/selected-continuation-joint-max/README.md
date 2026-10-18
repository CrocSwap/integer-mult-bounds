# Exact joint continuation maxima for a fixed selected program

The unchanged PR2697 coefficient evaluator has a sharper continuation-backing
bound when residue records are larger than VALUE requests. At depth two with
index/residue digit lengths I=14,R=32, the sharp level-uniform grammar bound
is **349 cells**, improving PR2925's allowance of 352. A bottom two-constant
PAIR followed by a two-real PAIR attains 349. The previously reported binary
example's 343 cells do not attain the maximum.

For A=2I+4 and B=R+3, the total lengths of the four continuation arrays are
bounded by

```text
h = 0                 2A + 2B + 2
h >= 1, A >= B        (h+2)A + (2h+2)B + 2
h >= 1, B > A         (h-1)A + (2h+5)B + 2.
```

The B>A saving is `(h-1)(B-A)`. The A>=B and depth-zero results retain
PR2758/PR2925 credit. The new step is a joint historical-maximum induction
and exact per-program recurrences. The general pending coordinate remains
individually sharp. [PROOF.md](PROOF.md) states the quantified contract and
derives every recurrence from the literal push/pop order.

The bound assumes a successful call, fixed program/fields and fresh arrays
or repeated calls preserving the same level grammar. Fixed source metadata
and deterministic preparation make branch types uniform at each ancestor
level, even when numerical coordinates differ. For arbitrary restored-head
warm lengths K_j, use `sum(max(K_j,c_j))`, where the exact per-grammar lengths
c are computed by `capacities` in [verify.py](verify.py).

Two controls show why these restrictions matter. A different prior grammar
leaves `(176,35,71,35)`; reusing that history for the attaining trace leaves
`(176,35,106,35)`, total 352. Deliberately changing metadata between equal-level
requests reaches 850 against a uniform envelope of 827 at depth three.
Neither example refutes the stated fixed-program result.

## Evidence and reproduction

[RESULT.json](RESULT.json) records author-checked source execution:

- All 518 level-homogeneous histories through depth three at residue widths
  4 and 32 match every predicted array length, with 604844 observed writes.
- Twelve attaining grammar traces cover both regimes through depth six.
  Three existing literal GL64 fixtures preserve their expected coefficients,
  source data, numerical ownership, blank stacks and restored heads. Their
  fixture recipes and prior observations remain PR2758's contribution.
- A real 348-cell quota rejects the 349-cell trace before growth. Successful
  same-program repetition, arbitrary warm arrays, changed-grammar history and
  nonuniform metadata controls exercise the entry and grammar boundaries.
- Nine behavioral tests check those endpoints, corrupt-source rejection,
  input limits and observer restoration after both entry and interior failure.

From the repository root, with standard-library Python 3.12:

```sh
python3.12 -I -Werror -B scripts/research_package.py \
  --package research/selected-continuation-joint-max
```

The registered replay checks normal and optimized acceptance and runs the
behavioral tests. `verify.py --emit` prints a receipt without replacing it;
ordinary replay compares the complete typed receipt and writes no package
artifact. All external execution inputs have SHA256 and Git-blob pins in
[SOURCES.json](SOURCES.json), checked before compilation. The optional package
runner also authenticates historical provenance. [VALIDATION.md](VALIDATION.md)
records exact commands, environments and engineering limits.

## Scope and research decision

This takes the released
[PR2925 handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-18972425)
under priority revision 5. The selected-stock-envelope draw is refined to
one reserve component, not a complete selected-stage stock coefficient.
[TASK.json](TASK.json) records assignment, overlap, source heads,
[canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-18973186),
entry history, stopping rule and next questions. Decision: finish this bounded
proof and hand off composition. No dependent construction round is proposed.

The all-depth statement rests on the written induction, not finite enumeration.
Grammar sharpness is conditional, not selected-catalogue realizability at every
depth. Numerical arenas, program/field arrays, caller counters, physical
reuse/movement, recursive grants and the outer wrapper remain separate.
This is one successful-call array-backing component, not total private reserve,
supplier admission, a new kappa or a complete multiplication theorem.

## Open next questions

1. Join this exact per-grammar coordinate vector to numerical/program/field
   backing at actual callback cuts. Start with one pinned successful callback
   and its real entry history. This would reduce the remaining total-reserve
   gap; missing common-cut ownership and physical reuse/movement block it.
2. Does a selected catalogue program realize an attaining residue-dominant
   trace at its admitted numerical widths? Start by classifying its fixed
   level metadata and fallback permutations, then evaluate this recurrence.
   Grammar sharpness alone does not establish those source-bound extents or
   a complete successful execution. No larger abstract census is needed.

## Credit

Nick Petalas. New work is Apache-2.0. Jose Manuel/jmbarrancoml supplied the
unchanged PR2697 callback and tape implementation. Nick Petalas's PR2758
supplies the fixture recipes, prior live/backing proof and literal GL64
observations; PR2925 supplies the value-stack bound and this open question.
The unchanged [source notice](../selected-continuation-storage/vendor/NOTICE.md)
retains the full implementation lineage. Numerical and native-action storage
results, including Ross Richardson's PR2831 and PR2923's distinct join,
retain separate credit. Substantial automated assistance was used for analysis,
proof drafting, implementation and internal review.
