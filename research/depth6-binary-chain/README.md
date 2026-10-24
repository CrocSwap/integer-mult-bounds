# Exactly ten shortest binary depth-six chain schedules

This contribution was produced by Nick Petalas. The new result is an
**exhaustive finite classification** of shortest unsigned dirty-chain
schedules at depth six in characteristic two:

```text
There are exactly ten shortest words.
They are the ten distinct cyclic rotations of (1234565432)^2.
None has adjacent commuting calls.
```

The length 20 is already implied by Yifan Kang's
[CNOT-Optimal Circuit Synthesis, Proposition 3.1](https://math.mit.edu/documents/rsi/2023KangY.pdf),
which proves the directed-path minimum `4n-8` on n registers. It is credited
prior work, not the original result here. The new classification shows that
this minimal interface has only cyclic starting-position freedom. No local
swap of commuting neighbors can retime a shortest schedule.

## Interface and algebraic reduction

A letter l means the complete call `z_l += B_l z_(l-1)`, for l = 1,...,6.
The source `x = z_0` is immutable. The five intermediates `z_1,...,z_5` and
the target `y = z_6` hold arbitrary initial data. The maps `B_1,...,B_6` are
arbitrary compatible linear maps over a nonzero unital ring of
characteristic two. Every intermediate must be restored, and the only
output change must be

```text
y += B_6 B_5 B_4 B_3 B_2 B_1 x.
```

There are no inverse, fused, scaling, copy or extra-storage calls. Length
counts complete calls with equal unit prices. This is the chain model of
[#4263](https://github.com/CrocSwap/integer-mult-bounds/pull/4263) and
[#4281](https://github.com/CrocSwap/integer-mult-bounds/pull/4281), with one
additional stage. This package provides no new kappa or supplier admission.

Use #4281's interval-count reduction. For `1 <= i <= j <= 6`, let `N[i..j]`
count scattered copies of `i(i+1)...j` in the chronological word. The
coefficient of the initial `z_(i-1)` in the final `z_j` is

```text
N[i..j] B_j B_(j-1) ... B_i.
```

Induction on calls proves this formula without commuting maps. The word is
universally correct precisely when `N[1..6]` is odd and every other interval
count is even. The expansion proves sufficiency. For necessity, take all
maps to be identity and vary the initial registers independently over F2.
Any wrong interval coefficient changes a wrong register or source
coefficient.

Equivalently, multiply the adjacent transvections `g_l = I + e_(l-1,l)`
chronologically in `UT7(F2)`. Their strict upper-triangular coordinates are
exactly the interval parities. The target is `I + e_(0,6)`. Thus universally
correct shortest schedules are exactly the labelled shortest paths to this
target in a graph of `2^21 = 2,097,152` possible states. Arbitrary-map
correctness does not require the actual maps to commute.

## Complete shortest-path classification

[RESULT.json](RESULT.json) lists all ten words, the exact path count, the
minimum distance and every BFS layer size through level 20. The verifier
starts only at identity and applies all six generators to every state in
each layer. It uses no symmetry or interval-based pruning. A visited array
removes only states reached at no greater distance.

The target is absent in layers 0 through 19, which contain **1,197,817
distinct states**, and first appears at level 20. The full layer 20 has
**338,668** states. These are states, not word counts; later group states are
not explored.

The new counting step keeps `ways[s]`, the exact number of shortest labelled
paths to state s. Initially only identity has count one. Every edge from
level d-1 to level d contributes its source count, including edges to a
state already discovered in that same level. Edges to earlier levels do
not contribute. Induction on d proves that this counts every shortest word
once. Counts fit in uint64 because `6^20 < 2^64`. The target count is **10**.

A separate backward traversal starts at the target and follows every edge
that decreases the BFS distance. It uses full 7-by-7 matrix multiplication,
rather than the vectorized transition formula. An explicit bounded
worklist enumerates the ten actual words, independently agreeing with the
forward count. The sorted set equals the ten distinct cyclic rotations of

```text
12345654321234565432
```

Every word has call-count vector `(2,4,4,4,4,2)`. Every adjacent pair of
letters differs by one. As universal call operations, distinct chain
generators commute exactly when their indices differ by at least two, so
no shortest word permits a local commuting-neighbor swap. There is one
cyclic-rotation class and ten classes
under commuting-neighbor swaps.

## Verification and reproduction

The verifier checks each of the ten words by integer chronological subword
counts and by full binary matrix products. Across all ten words, it also
checks **81,920** scalar combinations of six binary maps and seven arbitrary
dirty values, plus **8,960** two-coordinate replays. The latter use fourteen
initial basis vectors for each of 64 deterministic map tuples per word,
including noncommuting and singular maps. The universal statement rests on
the algebraic reduction, not this finite map sample.

A full-matrix oracle checks each generator on zero and all 21 coordinate
basis states, giving **132 comparisons**. Both transition formulas are
affine over F2, so these determine every transition on the whole state space.
Six rejection controls cover a dropped final call, dropped first call,
changed final call, unrestored forward-only word, swapped noncommuting
neighbors, and unknown generator.

From the repository root, with CPython 3.12 and NumPy 2.5.4:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/depth6-binary-chain/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -W error -B research/depth6-binary-chain/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/depth6-binary-chain
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/depth6-binary-chain --check-source-history
```

Any CPython 3.12 interpreter with the declared NumPy version can replace the
local path. Both registered commands perform the complete count and path
enumeration. No opt-in mathematical replay is needed. The verifier writes
nothing. It prints a generated JSON receipt bound to every package file and
live input SHA-256, then

```text
PASS_DEPTH6_BINARY_CHAIN shortest_words=10 rotation_classes=1 distance=20 oracle=132 scalar=81920 matrix=8960 controls=6
```

## Limits

This classifies only shortest depth-six schedules in characteristic two
under the stated complete-call alphabet. It does not classify longer words,
other characteristics or depths, extra storage, or a different target.
No universal multiplication barrier follows from this finite rigidity.

BFS allocates fixed main buffers at initialization: a 2 MiB visited array,
a 16 MiB path-count array and two 8 MiB state arrays. Each temporary
transition processes at most `2^18` states. BFS has at most 20 levels, six
generators and eight chunks per generator. Backward enumeration has at most
20 levels, at most 100 retained paths and six predecessors per path. The
actual target has ten paths. No recursion, subprocess, network access or
file write occurs. Bounded Python/NumPy temporary allocation is a
managed-runtime deviation from fixed-allocation operation. Warning-strict
normal/optimized replays, the matrix oracle and explicit exception
contracts supply local diagnostics; no compiled-language type checker is used.

No physical caller, routing, dispatch, precision, tape/storage, recursive
supplier or outer multiplication proof is supplied. Independent human and
formal proof-kernel review are unclaimed.

## Open next questions

1. Can a structural proof classify all shortest schedules without the
   finite state search? Start with Kang's minimum count vector and derive
   the forced chronological constraints. This could explain the rigidity
   and determine whether it persists at other depths.
2. What is the least extra call budget that permits a nontrivial commuting
   retiming freedom after cancelling adjacent equal calls? Begin with
   length 22, since correct words have even length. This could quantify the
   cost of chronology flexibility; a redundant cancelling pair alone would
   not answer the question.
3. Does a fully paid supplier consumer use this six-stage composition?
   Name actual maps and routing/restoration costs before interpreting the
   abstract schedules as recursive savings.

## Credit

Yifan Kang supplies the known directed-path minimum and bridge construction
in Proposition 3.1. The original finite contribution here is the complete
ten-schedule classification and its retiming consequence. Nick Petalas's
#4249/#4263/#4281 supply the chain model, earlier depth results and
interval-count/UT reduction used here. Ryanson Jonathan's
[#4418](https://github.com/CrocSwap/integer-mult-bounds/pull/4418) settles
the separate eleven open depth-five residues. Those results are cited, not
re-audited. Ross Richardson's #943/#934 lineage supplies the complete-call
dirty-connector interface. BFS and shortest-path counting are classical
tools. Apache-2.0.
