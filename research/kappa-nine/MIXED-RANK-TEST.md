# Minimal mixed-rank patterns are impossible in uniform mode 3

**New scoped conclusion:** in uniform mode 3, at least **four** of the
seven anchored two-dimensional blocks must contain a Y-label factor
restriction of rank zero or two. This improves the previous lower bound
of three exceptional blocks. All seven three-block exception patterns
are excluded by an exact algebraic argument.

This does **not** exclude the whole uniform mode-3 branch. The 103 complete
branch representatives retained earlier are still open. There is no new
finite network, multiplication witness, or publication change.

## Bounded searches and a useful normalization

The seven minimal exception sets are equivalent under permutations of
the fixed Fano plane. The audit supplies an explicit permutation for
each. We tested the representative with exceptional blocks {0,1,2},
retaining rank-one restrictions in the other four blocks.

After independent coordinate changes in the regular blocks, the line
alignment argument from `LOCAL-RANK-TEST.md` fixes the supported coordinate
of every regular Y restriction. The remaining system tests all 42 Y
labels, their 420 mutual edges, the anchor support constraints and their
rank-two normalizations. It is only a necessary subsystem: the 35 X
labels still require extension.

The initial system has 720 real unknowns. A legitimate change of internal
basis on 24 labels reduces that to 552. Both bounded Z3 runs returned
UNKNOWN/timeout, after about 24 seconds each with a requested 20-second
limit. Neither timeout is used in the conclusion below.

The normalization comes from a saturated three-label clique. If a label
has its singleton color on one regular block and its other allowed line
on a second regular block, those two A rows are independent. The matching
B columns are independent as well. To see this, let c be its singleton
coordinate and r its coordinate in the other block. Since no other label
in the clique has coordinate c, the clique identity sum A_i B_i=I gives

    A_T[c,:] B_T[:,c] = 1,
    A_T[r,:] B_T[:,c] = 0,
    A_T[c,:] B_T[:,r] = 0.

Regularity makes both the second row and second column nonzero. Thus the
rows and columns are independent. Set the A rows to (1,0) and (0,1) by
an internal basis change. The B columns must then be (1,0)^T and
(0,z)^T, with z nonzero. This removes seven unknowns per label.

## Complementary-block lemma

Consider one Y_j three-label clique, supported on three anchor blocks.
Suppose precisely one of those blocks is exceptional and the other two
are regular. Call the exceptional block E_0 and the regular blocks E_1,
E_2. Let T_0 be the label singled out by E_0, and T_1,T_2 the labels
singled out by E_1,E_2.

**Both A_(T_0)|_(E_0) and B_(T_0)|_(E_0) are invertible.**

Here is the proof. Concatenate the three A factors into a 6-by-6 matrix A
and stack the B factors into B. Normalization and mutual annihilation
give BA=I_6, so B=A^{-1}. Order the first row block as E_0 and the first
column block as T_0.

Delete that first row block and column block from A. On the remaining
four-by-four matrix, the regular-block color pattern separates the rows
into the two independent A rows of T_1 and those of T_2. After permuting
rows, the matrix is block diagonal with two invertible two-by-two
blocks. Thus A's lower-right four-by-four block is invertible. The same
argument, using the independent B columns, shows that B's lower-right
four-by-four block is invertible.

For an invertible block matrix with invertible lower-right block D,
block elimination gives the upper-left block of its inverse as

    (X - Y D^{-1} Z)^{-1}.

It is therefore invertible. Apply this first to A and then to B: the
upper-left blocks of both are invertible, proving the claim. No symmetry,
positive form or numeric approximation is used.

An explicit rational 6-by-6 control checks that these local hypotheses
are consistent and verifies all four block ranks. The contradiction
below requires connecting two different cliques.

## Why all three-exception patterns fail

For each ground point j, the associated Y_j class uses the three anchor
blocks whose Fano lines pass through j. The previous rank-one argument
requires every such triple to meet the exception set. A minimum exception
set consists of the three lines through a common point p.

Pick one exceptional line {p,j,l}. Points j and l each meet exactly one
exceptional line. The complementary-block lemma forces invertible
restrictions on that line for both labels

    T = {p,l,7},    U = {p,j,8}.

These labels are adjacent: their intersection is {p}. Their allowed
anchor supports intersect only in the chosen exceptional block; neither
has a remainder coordinate in mode 3. Thus B_T A_U is the product of two
invertible two-by-two matrices on that block. It cannot be zero, contrary
to the required annihilation.

`mixed_rank_obstruction.py` records the two labels, their clique witnesses,
regular blocks, singleton colors and shared block for each of the seven
minimal patterns. Its replay checks all the combinatorial hypotheses.
The mathematical argument is the elementary block-inverse calculation
above, not an inference from a solver's UNSAT report.

## Scope and next checkpoint

Enumerating all 128 exception sets gives:

| Exception-set size | Sets not excluded by these two arguments |
|---|---:|
| 0–3 | 0 |
| 4 | 28 |
| 5 | 21 |
| 6 | 7 |
| 7 | 1 |

These are surviving descriptions, not constructions. The next bounded
test is the four-exception case. The useful new rule is that a Y class
with only one exceptional block forces two invertible restrictions on
that block; their neighbors must have zero restrictions there. Propagate
those forced zeros before spending more time on nonlinear solving.

## Validation and reproduction

Four focused tests pass, including JSON round-trip replay of every
exclusion and rejection of a deliberately wrong shared block. A rational
coordinate-coloring control validates the full 42-Y-label checker when
all seven blocks are unrestricted. The local 6-by-6 control validates
the complementary-block rank calculation.

    python3 research/kappa-nine/mixed_rank_obstruction.py --output /tmp/mixed-rank-obstruction.json
    python3 -m unittest discover -s research/kappa-nine -p test_mixed_rank.py -v

Those checks use the standard library and run in under a second here.
To reproduce the inconclusive nonlinear runs, with Z3 installed:

    python3 research/kappa-nine/mixed_rank_search.py --timeout-ms 20000 --output /tmp/mixed-rank-search.json
    python3 research/kappa-nine/mixed_rank_search.py --normalize --timeout-ms 20000 --output /tmp/mixed-rank-normalized.json

Earlier receipts and the selected multiplication witness are unchanged.
