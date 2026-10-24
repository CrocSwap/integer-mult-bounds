# Exact rank-pair multiplicities for Schur-header counting

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped counting proof with exact finite corroboration. For every
finite field F_q, [PROOF.md](PROOF.md) gives a double-sum formula for the number
of d-by-d matrices H with prescribed nullities of H and I-H. It preserves their
dependence and replaces the 2^(d*d)-matrix sum in **ssafwann's #4678** binary
sharp Schur-header law with polynomially many explicit arithmetic summands.
The inclusion-exclusion method is classical. No historical novelty claim is
made for finite-field enumeration beyond this repository.

The new formula is proved by counting two disjoint eigenspaces and their
super-subspaces, including the graph-lift factors q^(ab) and q^(bi+aj).
For a fixed nullity pair it has at most (d+1)(d+2)/2 summands. The entire joint
distribution has O(d^4) summands. This is an algebraic evaluation improvement,
not a measured runtime speedup. Binary header counting remains conditional
on the cited predecessor theorem and concerns one deletion only.

At d=4 with four equal dimension-four sectors, the sharp split-pair count is
**962018618785136640000** and the identity-pivot split-pair count is
**8291457123053721102581760**. Multiply either by |GL_12(F2)| for its complete
ordered-header count. These are formula evaluations, not exhaustive counts
of the GL_16(F2) header space. No new kappa or supplier admission is claimed.

## Evidence and reproduction

From the repository root, use CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/schur-rank-pair-law/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/schur-rank-pair-law/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/schur-rank-pair-law
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/schur-rank-pair-law --check-source-history
```

Any CPython 3.12 interpreter may replace the local path. The standalone verifier
has no imports from another package and writes no files. Its output includes
`PASS_SCHUR_RANK_PAIR_LAW` and a generated receipt bound to all six package
files. The publication check requires full Git history. The verifier also runs
from a Git-free export containing these six files.

The direct matrix implementation uses ordinary Gaussian elimination, separately
from the subspace counting formula. Its literal censuses cover all dimensions
0 through 4 over F2, 0 through 3 over F3, and 0 through 2 over F4 and F5.
There are **86,727 matrix/context cases in 15 contexts**. F4 is represented by
F2[t]/(t^2+t+1), so the nonprime-field check uses field operations, not arithmetic
modulo four. The empty matrix and impossible a+b>d pairs are included.

Fifteen weighted binary header contexts compare the new grouped formula to
the literal sum over every compressed product at d=1,2,3. They include the
three numerical examples credited to #4678, with sharp/identity split-pair
counts (3,172), (9,100) and (2592,1932288). The weighted comparisons share the
credited U/A factors; they check the new regrouping, not those factor formulas
or the predecessor's Schur criterion. No predecessor verifier is replayed.

There are also 63 formula-only distribution checks through dimension eight
over q=2,3,4,5,7,8,9, checking nonnegativity, total mass and shift symmetry.
These are consistency checks rather than new exhaustive censuses. Eleven
controls cover omitted disjointness/lift factors, independent marginals,
the impossible-eigenspace boundary, six malformed inputs and the literal
census capacity limit. Explicit exceptions keep every check active under -O.

## Scope, sources and obligations

Base is canonical main `624de9dc66858af0945e5f8a0942488d62280d43`, priority
revision 7. The `formal-interface-lemma` card is changed to this algebraic
side result answering the evaluation gap explicitly stated in #4678. The
current-priorities selected source-binding command passes; it is metadata
orientation only. The original card's historical balanced baseline is not the
selected construction, so the current source-bound first step is used.

Advance [CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19132030)
was posted after a local question reservation, live PR/body and Discussion
checks, and distinctive main/merged searches. The overlap helper covered 325
open PRs and 3,742 Discussion records with complete pagination. Its sparse
local inventory searched 72 of 6,319 tracked notes; relevant source notes were
then materialized and all-main README searches were performed. Arbitrary code
diffs, unpublished work and a complete closed-PR body census are outside that
coverage. No absence-of-matches claim proves novelty.

The proof of the joint distribution is self-contained. The binary header
application cites ssafwann's #4678 at
`af9cf805c501e4e9e947c98c0b97b2281b6b6e97`, including its U/A factors and
complete-header completion multiplicity. Its unchanged archived README and
the catalogue/selected record are source-hashed provenance, not runtime inputs.
The new implementation transcribes the credited displayed U/A formulas; no
predecessor source code is copied. Exact Git blobs and hashes are in SOURCES.json.

Credit ssafwann #4678/#4671/#4657 for the header theorem, six-map method and
sector construction, Nick Petalas #4597/#4278 and the earlier header lineage
for Schur factorizations, Ryanson Jonathan #4609/#4617 and lee-phys #4634 for
sharpness/dimension context, and Cinna Davis for the BIT setting. source527,
commdata2338 and Jose Manuel retain the normalizer lineage credit. All existing
predecessor notices remain unchanged.

The universal claims rest on the written proof. Independent human and formal
proof-kernel review are unclaimed. Lean, Docker and the selected scientific
cold replay were not run. Later full guards and noncommuting residual states
are outside this result. Restricted production covers, selection/emission,
physical reads, dirty compensation/restoration, dispatch, precision, stock and
the complete consumer bill remain unknown. Unknown costs are not zero.

## Code bounds and diagnostics

Only the new verifier is executed. It has no recursion, subprocesses, network,
mutation of shared state, dynamic code or callback registration. Formula entry
points enforce d<=32 and prime-power q<=64; sectors have size at most 64.
The direct census enforces q^(d*d)<=65536. Each matrix is processed once and
discarded; the histogram has at most 25 entries. The larger formula histogram
has at most 1,089 entries. All calls are direct and returned values are consumed.
Functions stay below 60 physical lines. Warnings are errors in both registered
commands; repository metadata and publication-byte checks also run. No external
static analyzer is installed or claimed.

Power of Ten rule 3 deviation: CPython allocates integers, tuples and dictionaries
during arithmetic and elimination. Fixed preallocation cannot prevent those
runtime allocations. Live memory is bounded by the enforced dimensions, one
current matrix, one histogram and bounded-size integer sums. No matrix list or
unbounded cache is retained. Ordinary and optimized full replays exercise these
bounds. A larger executable domain would require a new capacity review; this
deviation does not weaken the all-d mathematical formula.

## Open next questions

Can joint nullities at three distinct affine shifts be counted without matrix
enumeration? Equal-scalar nonbinary Schur pivots can require more than two
different shifted ranks, so the present two-eigenspace law is insufficient.
Begin by counting prescribed three eigenspaces and their super-subspace lifts.
The blocker is an exact multiple-shift dependency formula, not extra binary
samples. This question is unclaimed here.

Can a named producer use these exact counts to supply a smaller paid header
cover? Begin with its actual request ensemble and selection/emission contract.
The complete physical bill remains the blocker; a positive density alone does
not remove paid work.
