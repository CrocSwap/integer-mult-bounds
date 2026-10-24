# Exact shortest chart paths and literal axis words

This contribution is produced by Nick Petalas. New work is Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

This is a scoped algebraic proof with exact finite corroboration. For two binary
Lagrangian charts at distance r, the shortest chart-path count is

    P(r) = product_(j=1)^r (2^j - 1).

For charts in a 2n-dimensional ambient space, the number of shortest literal
nonzero-axis words is

    W(n,r) = 2^(r(n-1)) P(r).

Empty products are one. The minimum length is r. The new executable result is
an exact lexicographic rank/unrank bijection for these words, so a uniform
integer in [0,W(n,r)) gives a uniform shortest literal word. The implementation
accepts 1 <= n <= 6; the written theorem covers every n >= 1.

The contribution counts syntactically different axis sequences, and separately
counts chart paths. It does not count distinct full symplectic products or
phase-exact Clifford lifts. No native paid-profile improvement, supplier
admission, new kappa or complete multiplication theorem is claimed.

## Model and predecessors

Let E be a 2n-dimensional symplectic space over F2 with alternating form omega.
A chart is an n-dimensional isotropic subspace. For nonzero a in E, let
T_a(x) = x + omega(x,a)a. A literal word is an ordered tuple of nonzero axes,
applied from left to right to the current chart. Its endpoint requirement is
T_(a_r) ... T_(a_1) U = V; no action on other charts is prescribed.

Distance is d(U,V) = n - dim(U intersect V). Chart paths identify axes whenever
they produce the same next chart. Fixed steps and repeated axes are allowed in
the general word alphabet, but cannot occur in a minimum-length word unless
they decrease the remaining distance.

Dugongue's [PR #4841](https://github.com/CrocSwap/integer-mult-bounds/pull/4841),
head `6debdcdac8fe1c87958f8cd42ccb7db73c0a0eef`, supplies complete single and
paired transvection neighborhoods and the corrected one-step distance test in
`research/native-clifford-gauge-compiler/decoder/CROSS-REVIEW-DYNAMIC.md`.
Cinna Davis's [PR #4690](https://github.com/CrocSwap/integer-mult-bounds/pull/4690)
supplies the Gaussian contact-search setting. Cao Yifan's #4610 supplies its
round-three supplier context; Yiyang's #4710 and the retained native caller
#4713/#4630/#4635 supply the physical and phase obligations. Their constructions
and predecessor notices retain credit. No predecessor executable is imported or
replayed here. The underlying finite symplectic and dual-polar geometry is
classical; no literature-priority claim is intended. The repository contribution
is the explicit shortest-word multiplicity and its exact indexing algorithm.

## Proof

Put I = U intersect V and r = n - dim I.

First, one transvection changes distance to V by at most one. If a belongs to U,
it fixes U. Otherwise H = U intersect a-perp is a hyperplane fixed pointwise by
T_a, so U and T_a U share H. Intersecting this common hyperplane with V shows
that the two intersection dimensions with V differ by at most one. Thus every
word from U to V has length at least r.

We count distance-decreasing axes directly. If a is outside U+V = I-perp, then
I intersect a-perp has codimension one in I, and no new intersection vector can
appear: T_a x in V with omega(x,a)=1 would imply a = x + T_a x in U+V. Such an
axis increases the distance. For a in U+V, write a=u+v with u in U and v in V.
All of I is fixed. A vector x in U can produce a new intersection vector only
when omega(x,a)=1. Then x+a belongs to V exactly when x belongs to u+I, and on
that coset omega(x,a)=omega(u,v). Consequently a decreases the distance exactly
when omega(u,v)=1. The decomposition is unique up to adding an element of I to
both u and v; this value is independent of that choice.

The quotient I-perp/I is a symplectic space of dimension 2r. Its subspaces U/I
and V/I are complementary Lagrangians, with a nondegenerate pairing between
them. For each nonzero u-bar in U/I there are exactly 2^(r-1) choices of v-bar
with pairing one. Each quotient axis has 2^(n-r) lifts in I-perp. Therefore for
r > 0 the exact number of distance-decreasing literal axes is

    A(n,r) = (2^r-1) 2^(r-1) 2^(n-r)
           = 2^(n-1) (2^r-1).

This is positive, so repeatedly taking a decreasing axis constructs a word of
length r. Every word of length r reaching V must decrease the remaining distance
at every step. At remaining distance j, there are A(n,j) choices, each followed
by the same number of completions, since that number depends only on n and j-1.
Induction gives

    W(n,r) = product_(j=1)^r A(n,j) = 2^(r(n-1)) P(r).

For completeness, every changed chart edge U -> U' has exactly 2^(n-1) literal
axis lifts. Let H = U intersect U', of dimension n-1. An axis inducing U' fixes
H pointwise and belongs to H-perp. In the symplectic plane H-perp/H, the two
charts give distinct lines. Of the three nonzero vectors in this binary plane,
exactly the third line's vector induces their interchange; the other two fix
one of the lines. All 2^(n-1) lifts of that vector induce U', and there are no
other axes. Dividing each path's literal lifts by 2^(r(n-1)) gives P(r).

Finally, sort the decreasing axes by their packed integer labels. Every first
axis has exactly W(n,r-1) completions. Euclidean division of an index by that
block size chooses its first axis and the residual suffix index. Repeat r
times. Conversely, rank adds each chosen axis's position times its suffix block
size. This proves the lexicographic bijection and the uniform-integer sampling
contract. The code supplies the bijection, not a random-number source.

## Exact evidence and reproduction

The independent checker generates all isotropic RREF subspaces for n=1,2,3.
It builds chart adjacency by intersection cardinality, without using
transvections, then computes distances and shortest-path counts by breadth-first
dynamic programming. It covers 3, 15 and 135 charts, and all 9, 225 and 18,225
ordered pairs. Literal first-letter counts are separately enumerated for those
pairs. These finite checks corroborate the theorem; the proof is not an
extrapolation from them.

For n=1,2 the checker exhausts all 28,386 axis tuples at the minimum lengths and
finds 1,644 successful words. Every successful word is checked against its exact
lexicographic rank and unrank. There are 58 additional round trips through n=6
and eleven rejection controls. Counts come from the executable enumeration.
For example, transverse n=3 charts have 21 shortest chart paths and 1,344
shortest literal words; these are included in the all-pairs count certificate.

From the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/shortest-chart-axis-words
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/shortest-chart-axis-words/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/shortest-chart-axis-words/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/shortest-chart-axis-words --check-source-history
```

Expected verifier status is `PASS_SHORTEST_CHART_AXIS_WORDS`. Each run prints a
machine-generated receipt including all package-file SHA256 hashes. Receipts and
logs should be redirected outside the checkout. No receipt is handwritten or
committed. Python 3.12 and its standard library suffice; the exact local path
above can be replaced by a clean Python 3.12 interpreter.

The inherited card's historical first command fails at `KeyError:
'complex_profile'` against the current selected schema. The current
`research_selected_baseline.py` source-binding control passes. That failure is
orientation evidence only and is unrelated to this self-contained theorem.

## Scope, implementation bounds and remaining obligations

`TASK.json` records a changed scope from larger-rank supplier synthesis to an
exact chart-word counting and indexing result. Efficient exploration can use
these multiplicities to avoid biasing chart-path sampling toward a particular
axis encoding. A profitable supplier would still require a new complete word,
all other incident edge costs, literal phase lifts, dirty restoration, ownership,
compiler, precision and outer admission. Those obligations are unrun here.

The executable reference implementation intentionally enumerates at most 4^6-1
axes per step and at most six steps. Charts contain at most 64 vectors. Input
closure/isotropy validation uses at most 4^6 pairs. A choices list retains at most
4^6-1 charts of 64 vectors, so the Python allocation deviation is explicitly
bounded; fixed allocation is not claimed. Functions fit within 60 physical lines;
there is no recursion, dynamic evaluation, network or subprocess execution in
the verifier. Its eleven fixed rejection callbacks are the only varying call
targets. Warning-strict normal and optimized runs retain explicit exception-based
invariants. No external static analyzer or proof-kernel check is claimed.

Overlap searches included live open PR bodies, recent account publications,
recent handoffs, merged-title searches and distinctive all-main README terms.
Sparse local notes, arbitrary source diffs and unpublished work are outside
complete coverage. The separately reserved cycle-coherent coordinated-neighborhood
question is excluded. This package does not recheck or extend a recent result
from the same account as its target.

## Open next questions

1. Can exact indexing avoid scanning all ambient axes at each step? This would
   make the sampler usable in the actual nine-bit search. First construct the
   pairing-one quotient axes directly with a canonical basis and prove the same
   lexicographic or a newly declared ordering. The current implementation is a
   bounded reference, and arbitrary-chart basis selection remains to implement.
2. How many distinct full symplectic products occur among minimum chart words?
   This separates chart-path freedom from physical-map freedom. First enumerate
   the complete matrices for transverse n=2 charts and classify product fibers.
   The present endpoint contract does not identify products or their phase lifts.

These questions are recorded with relevance, first steps and blockers in
[TASK.json](TASK.json). They are not part of the delivered result.
