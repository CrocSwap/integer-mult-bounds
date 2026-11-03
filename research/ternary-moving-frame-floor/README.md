# A moving-frame COPY floor for thirteen ternary lines

Every exact factorization of the Gram matrix on the thirteen projective
nonzero lines of {-1,0,1}^3 into at most four scalar outer products has
full-orthogonality binary COPY cost at least **14**. This settles the
below-thirteen question in Aaron Wang / navinor's
[PR2518](https://github.com/CrocSwap/integer-mult-bounds/pull/2518), Open next
question 2. Factors may move freely, leave the evaluation code on one side,
and use arbitrary coefficients over any characteristic-zero field.

Claim type: scoped written mathematical proof with an exact finite rank
certificate. The minimum with at most four terms lies between 14 and 18; no claim
of sharpness at 14 is made. Three terms have sharp cost 18. No new kappa,
physical decoder, supplier admission or selected-frontier change is claimed.
This contribution was produced by Nick Petalas. Independent human and formal
proof-kernel review are unclaimed. Apache-2.0.

[PROOF.md](PROOF.md) gives the full contract and argument. At four terms,
rank forces one factor side into the three-dimensional evaluation code.
All code supports reduce to 25 rational intersection directions. Their
complete restriction-rank envelope, combined with the thirteen pairwise
nonproportional Gram columns, forces the lower bound. No predecessor
census or scientific verifier is executed.

## Reproduce

Run from the repository root with the standard library only:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/ternary-moving-frame-floor/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/ternary-moving-frame-floor/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/ternary-moving-frame-floor
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/ternary-moving-frame-floor --check-source-history
```

Any CPython 3.12 interpreter can replace the absolute local path. The direct
verifier reads only these six package files, writes nothing and prints a
generated receipt binding their SHA256 hashes, followed by

```text
PASS_TERNARY_MOVING_FRAME_FLOOR four_term_cost>=14 three_term_cost>=18
```

The checker reconstructs the thirteen ports and independently enumerates the
25 intersection directions. It compares row and transposed-column binary
elimination on all 25*8192 restrictions. It then enumerates all 13^4 ordered
support-size tuples. Exact new factorization fixtures include three examples
whose non-code side has rank four, together with their transposes. The
coordinate fixture attains the three-term bill 18. Seven rejection controls
cover a zero direction, rank capacity, omitted direction, changed pairing,
underpriced envelope, failed scalar identity and excess term count. A
separate fixture distinguishes characteristic-zero scalar rank from binary
tariff rank. No enumeration of all coefficient tuples is claimed or needed.

Both normal and optimized registered commands use explicit exceptions, so
optimization does not disable the checks. The generic runner checks metadata
and source pins separately. The source-history preflight requires the
retained Git history; direct mathematical replay needs no Git or network.

## Scope and implementation bounds

The exact pairing has unit diagonal and off-diagonal one precisely when the
original port vectors are orthogonal. Changed pairings, masked exactness,
shared-copy prices, other geometries, positive characteristic and five or
more active factors are not covered. The support relaxation's attaining
size tuple is not asserted to be a realizable factorization.

The written reduction is a proof over all stated fields and decompositions.
The finite replay certifies its restriction-rank premise and corroborates
the algebraic fixtures. It is not a complete multiplication theorem or
independent human/proof-kernel acceptance. Physical acquisition, delivery,
native realization, arbitrary dirty-helper restoration, ownership, routing,
compiler closure, precision, stock, BIT compatibility and the outer bill
remain unpriced. No selected cold replay, Lean or Docker run was performed.

The standalone verifier has no recursion, subprocesses, network access,
writes or mutable global cache. Each function is below sixty physical lines.
Its main exact loop is bounded by 25 directions and 8192 subsets. The size
loop has 28561 tuples. Matrices have at most 13 rows and 13 columns; factor
fixtures have at most four terms. The registered command timeout is 120
seconds. Power of Ten rule 3 has a managed-runtime deviation: CPython
allocates integer, Fraction and collection objects while running. Live
mathematical state is bounded by these fixed dimensions, with one current
restriction retained at a time. Fixed-capacity storage would be required
for a native steady-operation implementation. The rejection helper has seven fixed local callable targets, a bounded
Power of Ten rule 9 deviation used only for failure controls.
Warnings-as-errors execution is the applicable diagnostic check; no external static analyzer is claimed.

## Sources, overlap and family decision

Base main is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8,
selected PR6030. [SOURCES.json](SOURCES.json) pins the question README,
catalogue and selected record as historical provenance. There are no live
external mathematical inputs. [TASK.json](TASK.json) retains the complete
card and explains the changed scope. The selected binding baseline passed
as orientation, without a supplier replay.

The [advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19362906)
followed checks of live handoffs, local reservations, open and recent-account
PRs, all-main README object/formula searches, merged/general-form searches
and the cached card report. The cached scan covered 406 open PRs and 6355
Discussion records but only 111 local note records of 8917 HEAD notes.
Explicit Git searches covered all main README paths for the distinctive
object and formula terms. Sparse notes, arbitrary historical diffs and
unpublished work remain coverage limits. This is bounded overlap evidence,
not a novelty certificate or a literature-priority claim.

Credit Aaron Wang / navinor's PR2518 and PR2272 for the exact open question
and fixed dense-polar contract; DreamingOfClouds's PR2125, PR2228, PR2111,
PR446, PR595 and PR1590 for the retained COPY/polar-law model; Cinna Davis /
1337isnot1337's PR2240 for the fixed-frame one-extra family; and joaqcoo's
PR1224 for the one-sided factorization context. Rank factorization,
projective intersections and binary elimination are classical. The new step
is the complete restriction-rank lemma and its all-moving-frame four-term
consequence on these thirteen ports. Predecessor results and credit lines
remain unchanged.

The family decision is to stop this below-thirteen four-term route at its
algebraic cost gate. An exact cheaper decoder under a changed term count,
pairing or delivery contract would reopen a different question. A new
physical construction campaign is not justified by this negative result.

## Open next questions

1. What is the exact minimum with at most four terms, between 14 and 18? First seek a
   complete exact factorization costing 14 through 17, allowing the other
   factor side to leave the code. The support-size relaxation alone need
   not be realizable.
2. Can five terms beat thirteen with this pairing? First specify the two
   rank-four factor spaces and enforce a rank-three product. Neither side
   must then equal the evaluation code, so the present reduction is not a
   five-term exclusion.
