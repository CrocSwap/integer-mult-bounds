# Independent review of the private-query concave cost bound

Result: PASS for the fixed source-frame model. The submitted proof gives
the exact minimum `8*8^(1-b)` for every real `0 <= b <= 1`. It applies
to every finite scalar factorization over Q, R or C. It does not give
a circuit, a physical copy-cost theorem, or a complete kappa improvement.

This is an independent OpenAI Codex agent review. It is not human review
or formal proof checking. The reviewer read the PR description standard
at `/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
No new research direction was used to complete this review.

## Exact model

The prototype has 120 root rows of length eight. The matrix `R` consists
of rows 8 through 119, so it has size 112 by 8. The correction
`G=R R^T/4` has size 112 by 112. The exact identity `R^T R=56 I_8`
proves that its rank is eight over each stated field. There is no
transpose conflict with other packages that store roots as columns.

For each nonzero query row `f_j`, a private binary linear subspace
`F_j <= F_2^9` must contain all source labels in its support. The charge
uses `r_j=dim_F2(F_j)`, with `1 <= r_j <= 9`. A frame may contain more
vectors than the minimal support span. This permission is part of the
historical model and is now explicit in the package README.

This rank is not the rank of a source-target pairing submatrix.
A pairing can have a nonzero kernel on the source span. The proof does
not subtract that kernel dimension. It also does not assign a shared
carrier's chronological cost to several queries.

## The six premises

All required finite inputs are in the package. The following written
arguments were checked, as well as their fresh exact computations.

1. **Code rank and support.** The simple-root certificate checks every
   signed-root reflection, every one-sign integral root expansion, and
   all 256 simple subsets. The finite chamber argument is valid. It
   gives the stated generalized support bounds. The unique short
   fundamental ray is a root direction. Thus the retained minimum
   support is 53; a non-root real direction has support at least 70.
   Real and imaginary parts give the stated complex-field extension.
2. **Frame ranks.** Nonzero rows require a positive rank. All frames
   lie in the fixed nine-dimensional binary source space. Enlarged
   frames are permitted; minimal frames are not required.
3. **Source capacities.** The positive quadratic character sum is
   checked from the literal labels. On a minimum-rank coisotropic
   slice, exactly one coset has nonzero character sum. Its sum equals
   the positive full sum. The remaining polar ranks give the bounds
   12, 20 and 36. This proves the low-rank capacities used by the
   profile argument. All 43,435 rank-seven frames are also checked.
4. **Total rank at least 64.** Independent query reduction preserves
   the correction and keeps the retained frames. The incidence bound
   uses pairwise nonproportional correction columns. The balanced
   incidence bound follows from decreasing discrete increments of
   subset coverage; it does not assume disjoint supports. The fresh
   enumeration covers all 1,735,600 profiles with total rank at most
   63 and leaves exactly the two profiles stated in the proof.
   Both final closures are valid. Nine rank-seven rows force a root
   simplex; its separating labels contradict the frame ranks.
   The ten-query profile forces eight independent root directions to
   have the same self port, which is impossible.
5. **No rank-nine frame at total 64.** The independent multiplicity
   recursion covers all 195,666 partitions of 64. It rejects all
   79,403 partitions with a rank-nine part by valid necessary
   conditions. The root-pair test is necessary and its omission
   control produces the recorded survivor. This screen does not
   assert that each remaining partition is realizable.
6. **Attainment.** The eight coordinate rows of `R^T`, with decoder
   `R/4`, factor `G`. Each coordinate support has binary span rank
   eight. A separate review calculation constructs those eight spans
   and checks an explicit rank-nine enlargement of each one.

The rank-five and rank-six capacity bounds use a written quadratic
argument. A second large census is not needed or claimed. The two
final query-profile contradictions are written proofs, not conclusions
of the profile enumeration alone.

## The new scalar and weighted arguments

For `F(a)=7*9^a+2-8*8^a`, the ratio of the two positive derivative
terms increases strictly. It crosses one at a unique critical point.
The five integer inequalities in the proof give `0<a0<7/10`,
`8*log(9/8)/log(9)<4/9`, and `8^(7/10)<13/3`. At that point,
`F(a0)>2-(4/9)*(13/3)=2/27`. This proves the strict inequality on
the whole real interval `[0,1]`. No numerical sample is a proof input.

Deleting a dependent query removes a strictly positive charge, even
at the endpoints. Its decoder column can be absorbed into the retained
query columns. This reduction handles any finite number of terms.
For an independent query basis, exactly eight queries span the Gram
code and must each have frame rank at least eight. At total rank 64,
the no-rank-nine premise gives the weighted bound. All other cases
have at least nine queries and rank sum at least 65. The chord for
`r^a` on `[1,9]` has nonnegative slope and intercept for `0<=a<=1`.
The stated lower bounds on query count and rank sum can therefore
be used separately. They give `7*9^a+2`, strictly above the reference.

For `0<b<1`, equality requires exactly eight independent queries,
all of rank eight. At `b=0`, the proof only forces total rank 64;
it does not assert uniqueness. At `b=1`, each nonzero query costs
one, so every eight-query factorization has bill eight. Its frame
ranks can be eight or nine. For `b>1`, enlarging the eight coordinate
frames to rank nine is legal and gives a strictly smaller bill.
The separate exact check at `b=2` gives bills `1` and `8/9`.
No physical circuit claim follows from that cost-law example.

## Current public context and credit

The all-m decoder note was read at commit
`4c32ac3b88d63ad06d2b30e526aa07a12929db36`, including its source-rank
lift and the distinction between uncorrected and corrected pairing
cost. It already proves an unweighted floor and a unique cost-64
decoder in its stated characteristic-zero model. The submitted note
does not claim that unweighted floor as new. It retains its own fixed
root and label dependency proof; no unproved identification of the
two coordinate systems is required.

The current saved open-PR records for PR #3074 and PR #2985 concern
one-sided padding and corrected-decoder residue closures. Their stated
claims do not provide the present full concave weighted cost law.
A search of README and PROOF files at current main
`cef4b52f2a59009865bf8eabde1be3f159063703` found no copy of the new
scalar inequality or a claim of this full range. This is a targeted
overlap check, not a claim to have reviewed all public mathematics.

The prototype, source notice and credit record are byte-identical to
their Git objects at `e07a8a3f9f79c22113398a0c5dbbc7601f489b3e`.
The notice verifies the credit to icekylinx. The README at commit
`9c94857bbaee886f8649edee0bc2d3c738f9555e` in the source project
identifies Jacob Sussman as its author and records its E8 construction.
The later decoder note's notice credits DreamingOfClouds and Claude
Opus 5.5. No file from that later proof is used as a computation input.
Live GitHub link and rendered-description checks remain the
coordinator's publication checks.

## Runs, controls and final binding

`REPLAY-COMMAND.json` records the first fresh six-stage replay.
`FINAL-REPLAY-COMMAND.json` records the final wrapper replay with
ambient `PYTHONOPTIMIZE=1` and an isolated parent interpreter. Each
child now uses `-E`; the explicit optimized scalar check still uses
`-O`. The final run passed in 7.952 seconds with one process at a time.
The time is a run record, not a performance claim.

Both runs printed:

```text
PASS_PRIVATE_QUERY_CONCAVE_RANGE_INPUTS 2/27 1735600
```

`review_checks.py` imports no submitted checker. It checks the exact
source bindings, coordinate frame ranks and frame enlargements.
`controls-final/RESULT.json` records seven rejection controls:
optimized runner use, an existing output directory, a false scalar
comparison in normal and optimized Python, prototype manifest drift,
an altered root norm, and a duplicate binary source label. Every
control failed with the expected diagnostic. The historical replay
also passed its quadratic-sign and rank-nine premise-omission controls.

The final README defines both the matrix orientation and permitted
frame enlargement. The saved package replay receipt and log now come
from the final run and bind the current source manifest. These changes
resolve the review's packaging findings. No material finding remains.
`FINAL-HASHES.json` records every final package file and the review
scripts. The original proof and historical sources were not changed.

The optional fitting-rigidity extensions were not reverified and are
not part of the new claim. No physical supplier, phase, restoration,
hosting, recursive-cost or complete exponent check was run, because
the submitted result claims none of those operations or costs.
