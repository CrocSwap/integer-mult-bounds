# Paired copies force at least six exceptional blocks

**New scoped conclusion:** a uniform mode-3 representation can have at
most **one regular anchor block**. Equivalently, at least six of its seven
blocks must contain an allowed Y-factor restriction of rank zero or two.
This strengthens the lower bound of four in `MIXED-RANK-TEST.md`.

The four-block experiment therefore closes exactly. The same argument
also closes all five-block patterns. It does not exclude the entire
uniform mode-3 branch or any additional complete branch representative:
all 103 complete cases remain open, and no new kappa is established.

## A stronger use of the complementary-block lemma

Recall that Y_j consists of six labels, formed by adjoining either 7 or
8 to the three pairs obtained from the Fano lines through j. Their
supports are the three anchor two-planes incident with j. In uniform
mode 3 there is no remainder coordinate on any Y label.

Suppose the star at j has exactly one exceptional block, corresponding
to the Fano line {j,l,p}. Its other two blocks are regular. The
complementary-block lemma from `MIXED-RANK-TEST.md` applies separately
to the two three-label cliques, one using outside point 7 and one using
outside point 8. It makes the restrictions of both factors invertible
on the exceptional block for **both** labels

    S_7 = {l,p,7},    S_8 = {l,p,8}.

The previous argument looked for another forced-invertible label. That
is unnecessary: these two copies already force a dimension contradiction.

## They delete a whole block from an adjacent clique

Choose the Y_l clique using outside point 7. Its member associated with
the same exceptional line is T_0={j,p,7}; the other two members have pairs
on the other Fano lines through l.

- T_0 is adjacent to S_8, since their intersection is {p}.
- Each of the other two members is adjacent to S_7. Its pair is disjoint
  from {l,p}, so their intersection consists just of 7.

The anchor supports of any Y_j and Y_l labels meet only in the unique
Fano line through j,l: the chosen exceptional block. Thus for each target
T in the Y_l clique, one of the required equations is

    B_(S_o),E A_T,E = 0,

where B_(S_o),E is an invertible two-by-two matrix. Hence A_T,E=0.

All three target images have therefore lost E. They now lie in the
remaining two anchor planes, a space of dimension four. But three
mutually annihilating rank-two projectors have independent image spaces
of total dimension six: their stacked B factors are a left inverse for
the concatenated A factors. This gives the contradiction **6 <= 4**.

No positivity, covariance or numerical rank decision is involved.

## Why this leaves at most one regular block

Every pair of anchor Fano lines meets at a point j. If two blocks were
regular, inspect the third block through j:

- If it were regular too, the earlier three-regular-block line-alignment
  obstruction would apply.
- If it were exceptional, the paired-copy argument above would apply.

Both alternatives are impossible. Therefore at most one block is regular.

## Exact finite audit

The script enumerates all 128 subsets of the seven blocks. Its results
are:

| Pattern class | Number |
|---|---:|
| Excluded by a completely regular three-block star | 64 |
| Excluded by the paired-copy argument | 56 |
| Remaining with six exceptional blocks | 7 |
| Remaining with seven exceptional blocks | 1 |

Of the 56 paired-copy exclusions, seven are the three-block patterns
already closed in the previous round. The new exclusions are the **28
four-block patterns and 21 five-block patterns**.

Each certificate records the two full-rank sources, the complementary-
block lemma hypotheses, the target clique, the source used for each
forced deletion, and the resulting four-dimensional support. The replay
checks every edge and support intersection. All 56 certificates survive
JSON serialization and replay. Negative controls reject using the wrong
outside copy or omitting a necessary deletion.

## Next decision

This eliminates the modest repairs of the uniform rank-one pattern.
The remaining six- and seven-exception regimes allow rank defects across
nearly the whole geometry. They remain possible, but this result gives
no positive construction or indication that a larger blind search will
succeed.

The next bounded diagnostic is the six-exception case, with only one
regular block. First use the paired-copy rules and exact local controls
to define the reduced subsystem. Any candidate still needs exact factor
matrices, all X labels, extension beyond nine points, and the charged
finite-network/complex-network interfaces before it can affect kappa.

## Reproduction

    python3 research/kappa-nine/paired_copy_obstruction.py --output /tmp/paired-copy-obstruction.json
    python3 -m unittest discover -s research/kappa-nine -p test_paired_copy.py -v

The standard-library checks pass; the three focused tests take about
four seconds here. No nonlinear solver result is used in this exclusion.
Previous receipts, the selected multiplication witness and publication
artifacts remain unchanged.
