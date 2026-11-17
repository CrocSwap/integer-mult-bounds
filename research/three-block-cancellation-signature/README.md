# Cancellation adds a three-block decoder signature

A six-by-six integer unimodular basis realizes a source/reader signature
absent from every generic support pattern. It works over every field,
including F2. This answers Open next question 1 of SHIN09-git's
[#6708](https://github.com/CrocSwap/integer-mult-bounds/pull/6708).
The new contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped written proof with exact finite corroboration.
No decoder price, native word, supplier admission or new kappa is claimed.

## Result

Divide the six port rows into A={0,1}, B={2,3}, C={4,5}. Every column of
the explicit basis P uses all three blocks. The six rows of its inverse
use exactly BC, BC, AC, AC, AB, AB. All entries are 0, 1 or -1 and both
inverse products are integer identities.

In contrast, a generic support matrix on b >= 2 nonempty row blocks,
with every column using all b blocks, must have at least b inverse rows
using all b blocks. The bound is sharp for every choice of block sizes.
The proof chooses a source strongly connected component in the directed
graph of a determinant matching. It excludes every generic support,
not just the entry support of P. [PROOF.md](PROOF.md) gives the matrices
and the full argument.

This is the first improvement being delivered. The remaining signature
classification and any physical use are left below.

## Reproduce

From the repository root, with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/three-block-cancellation-signature
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/three-block-cancellation-signature/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/three-block-cancellation-signature/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/three-block-cancellation-signature --check-source-history
```

Another CPython 3.12 path may replace the local interpreter. Direct replay
prints a generated receipt bound to the package hashes, followed by
`PASS_THREE_BLOCK_CANCELLATION_SIGNATURE`. It writes no files. No receipt
is handwritten or stored as an asserted output.

The verifier checks both integer products, independently solves both
inverses with rational elimination, and checks the signature over F2, F3,
F5, F7 and F11. It rejects all 27 single-nonzero-entry omissions from P.
It enumerates all 59,131 full-source supports at block sizes (1,1,1),
(2,1,1) and (2,2,1). The 58,081 structurally invertible supports pass
independent cofactor-matching and graph-reachability checks. Two six-port
patterns corroborate sharpness and the difference between the numerical
witness and its generic support. Five invalid-input controls pass.
The all-size theorem and all-field witness use the written proof;
this is not an exhaustive six-port census.

## Scope, sources and decision

The `coverage-law-change` card changes scope to this square-basis
algebraic question. Base main is
`e54523517d0f03e58352e647c403a5af3e525a57`, priority revision 8,
selected #7000. The selected source-binding orientation passes; no
selected scientific replay is performed. The result does not change
the selected record or any of its five inherited assumptions.

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19538530)
states the same target. Live handoffs, current PRs, recent account work,
local reservations, main README searches, merged searches and the overlap
helper were consulted. The source-reference search found no recent
account PR using #6708. The overlap helper's working-note inventory is
sparse; explicit main-tree searches supplement it. Arbitrary historical
diffs, nested notes and unpublished work remain coverage limits.

SHIN09-git's two-block classification is cited without auditing or
replaying its scientific checker. It proves rational generic equality
for two blocks and explicitly asks the three-block question settled here.
Its proof and README are pinned in [SOURCES.json](SOURCES.json). The
source/reader model and earlier screens retain Gonzalo Mier's #3990/#3997
and Nick Petalas's #6691 credit. Structural determinant/cofactor matchings
and the inverse-path description are classical. The new steps are the
sharp block-mask consequence and the field-uniform six-port separation.

No complete physical producer or consumer is supplied. Preparation,
delivery, arbitrary dirty-state restoration, routing, precision, stock,
compiler closure and a signed invoice remain unpaid obligations. Unknown
costs are not zero. Independent human and formal proof-kernel review,
Lean, Docker and supplier admission are unclaimed. The decision is to
retain this settled algebraic question and stop.

## Open next questions

1. Which other three-block signatures lie outside the generic census?
   Start with supports of inverse bases having a zero diagonal block;
   a complete cancellation-sensitive classification is the blocker.
2. Can a physical caller exploit this signature after all preparation,
   delivery and restoration costs? Start with these literal matrices and
   one source/reader schedule. No favorable full invoice is supplied.

## Implementation bounds

All matrix dimensions are at most six. Matching lists have at most 720
terms; each cofactor has at most 120. The replay enumerates exactly the
three stated support domains and two six-port patterns. There is no
recursion, subprocess, network access or dynamic source generation.
All functions are below sixty physical lines and internal checks remain
active under optimized Python. The only module dispatch loads the fixed
local model file; the invalid-input table has five fixed call targets.

Power-of-Ten rule 3 deviation: Python and Fraction allocate during
execution. Fixed dimensions, coefficient fixtures, one support processed
at a time and bounded matching lists limit live memory. A fixed local
module loader is the rule 9 dispatch deviation needed by isolated Python;
the target is `model.py`, with lifetime equal to this process. Rule 10
uses warning-strict normal/optimized execution; no additional Python
static analyzer is claimed. These are mathematical checks, not physical
memory or tape tariffs.
