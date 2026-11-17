# Smallest failure of the two-pass width budget

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: finite certificate with a scoped combinatorial proof. The layout

```text
3,2,1,6,5,4,9,8,7,0
```

has decreasing-subsequence width four but requires exactly **three** stable
two-lane passes. A forced four-cycle excludes every possible two-pass
intermediate order. Three explicit passes attain the endpoint. Every layout
of at most nine records with width at most four does admit two passes, so
ten records is the minimum size of a failure of the width-product test.

A pass assigns each intact record to one of two order-preserving streams,
then merges them in any stable interleaving. Empty lanes and arbitrary
routing choices are allowed. No payload copies, deletions, extra lanes or
random access are supplied. This is an abstract pass count, with no physical
unit-time assertion about streams or tapes.

[PROOF.md](PROOF.md) gives the four-cycle argument and the exact finite
minimum-order reduction. It also gives the full attaining route:

```text
0 1 2 3 4 5 6 7 8 9
1 2 3 4 5 6 7 8 9 0
2 1 3 5 4 6 8 7 9 0
3 2 1 6 5 4 9 8 7 0
```

## Reproduction and evidence

From the repository root, using CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/two-pass-width-obstruction/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/two-pass-width-obstruction/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/two-pass-width-obstruction
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/two-pass-width-obstruction --check-source-history
```

Another CPython 3.12 path can replace the displayed interpreter. The direct
marker is `PASS_TWO_PASS_WIDTH_OBSTRUCTION`; the runner returns
`PASS_REGISTERED_RESEARCH_PACKAGE`. The verifier writes no files. Its stdout
receipt is generated from the actual calculations and hashes all six package
files. Normal and optimized executions perform the same checks.

The minimum-order certificate compares complete sets, not only counts.
It enumerates all 362,880 permutations of nine records, independently
identifies the 4,862 one-pass factors, composes all 23,639,044 ordered pairs,
and obtains exactly the 261,808 width-at-most-four layouts. Restriction of
those routes settles every smaller size. All ten single-record deletions
of the new obstruction also lie in that complete two-pass set.

Two different exclusion checks corroborate the written proof. Every one
of the 16,796 ten-record first factors has a unique residual second factor
of width greater than two. Separately, all 262,144 lane assignments normalized
at record 0 are considered; exactly 216 pass the necessary inverted-pair
condition. Each has the forced cycle, and an independently built directed
order graph is cyclic. The actual lane streams of all three upper-bound
passes are checked. Six malformed or unstable route controls reject, and
four-record reversal provides a width-four layout that does fit two passes.

## Credit and scope

Matarener's [#3825](https://github.com/CrocSwap/integer-mult-bounds/pull/3825)
supplies the abstract stable-lane pass obstruction in the bit-free complex
supplier context. James Reed / jwr404's
[#3839](https://github.com/CrocSwap/integer-mult-bounds/pull/3839) supplies the
earlier finite forward-composition evidence through seven records. Their
results are cited premises and context; their scientific code and counts
are not replayed as the deliverable. Retain their Walsh, native, adapter,
coverage and supplier predecessor credit.

Mark Karpilovskij's published
[Composability of Permutation Classes](https://www.combinatorics.org/ojs/index.php/eljc/article/view/v26i1p41),
Theorem 15 and Question 16, already establishes the general failure of
sufficiency of the product-width bound. That broad noninclusion is prior
work. The explicit smallest-order certificate, four-cycle proof in this
routing contract, and standalone checker are the new repository contribution.
No historical priority claim is made for the example or standard methods.
Nick Petalas's older reversal and Gray-layout packages are related background;
their constructions, formulas and scientific code are not used as the main step.

The `bit-new-register-model` card changes scope to this local layout side
result. Its register-algebra and supplier acceptance gate is not met here.
The source-binding first example passed at canonical base
`e54523517d0f03e58352e647c403a5af3e525a57`, priority revision 8, selected #7000.
The catalogue's assessed selection context is historical. The selected
frontier and its five assumptions are unchanged. The
[advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19541783)
records the bounded question. Live open/account PRs, recent claims, active
Discussions, local reservations, cached overlap, main README searches and
merged searches were checked. The cache covered 545 open PRs and 7,200
Discussion records, but only 218 of 10,178 main note paths. Main-tree searches
supplement that sparse coverage; unpublished work and arbitrary diffs remain
outside it. Search absence is not a novelty certificate.

Minimum order is established by a finite exhaustive computation. The
four-cycle exclusion and route correctness are written proofs, not formal
proof-kernel results. Independent human and formal proof-kernel review are
unclaimed. A complete forbidden-pattern basis, arbitrary-layout recognition
algorithm, actual physical caller, merge controller, movement, stock,
precision, native cost, reversible cleanup and complete supplier bill remain
outside scope. No new kappa or multiplication theorem is claimed. Selected
scientific cold replay, predecessor scientific suites, Lean and Docker are unrun.

[SOURCES.json](SOURCES.json) pins all source documents as historical
provenance. No predecessor implementation or live external mathematical
input is required by the direct verifier, including in a standalone export.

## Open next questions

- Which further minimal forbidden patterns characterize two stable two-lane
  passes? Test the displayed four-cycle against one named layout before
  seeking a constructive factorization. The complete basis and a general
  recognition algorithm remain missing.
- Does one current physical producer/consumer layout contain this obstruction
  as a record-order pattern? Pin its splitting and merging contract, then
  price its controller, movement and cleanup. No actual caller is bound here.

## Implementation bounds

The checker has no recursion, solver, subprocess, network access, dynamic
code execution or shared mutable state. Mathematical inputs are fixed.
Dimensions are at most ten. The largest pair loop has exactly 4,862 squared
iterations; the normalized lane loop has exactly four to the ninth. All
functions fit within sixty physical lines. Explicit exceptions preserve
all checks under optimized Python. Warning-strict execution and in-memory
AST compilation provide the available interpreter diagnostics. No separate
lint/type analyzer or shared build configuration is changed.

Power of Ten rule 3 requires a managed-runtime deviation. CPython allocates
integers, tuples, sets and bytes during this terminating certificate replay.
Two sets of at most 362,880 nine-byte layouts and catalogues of at most 16,796
ten-record tuples bound live collections. The joined hash payload has at
most 9 times 362,880 bytes. This is not a fixed-allocation online controller;
a native online implementation would require a separate capacity contract.
