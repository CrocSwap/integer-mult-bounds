# Minimum scalar grids for the final banked native graph

This is a finite, source-bound arithmetic result for the final forward
DAG of PR #7674 at scientific commit
`26b6c469aa6c4aa04322ce25a22150f90e5fb14e`. Its 15 pivots act on the
parent word with SHA-256
`ee251f6005d2a92b887c5b804bd7aac05989d278b2c9ccb3c3091b50d533b08d`.
The current PR head `28b2af322a1fab01b3734365988930920f9dda48` adds
only the separate shared CI repair. The source graph is unchanged here.

The source's recursive denominator rule gives the sufficient integer
grid `2025 * 2^18 = 530841600`. Exact cancellation in the actual
independent-input coefficient rows gives the following sharp values.

| Required states | Minimum integer grid G | Minimum odd entrance factor M | Binary coefficient guard h |
| --- | ---: | ---: | ---: |
| Every literal scalar product, addition and stored row | 921600 | 225 | 12 |
| Stored snapshots only | 23040 | 45 | 9 |

Here `G=M*2^h`, with M a positive odd integer and h nonnegative.
Inputs are arbitrary independent normalized integer scalars. Scaling
all inputs by M and using binary fractional grid `2^-h` is equivalent
to representing every exact scalar coefficient in integer units G.
For inputs on `2^-p Z`, add p to the fractional width. The integer
part is unbounded in this audit; magnitude and overflow are separate.

The first line reduces the source's sufficient odd factor by nine and
its scalar coefficient guard by six bits. The sufficient integer grid
is 576 times the exact minimum. This is not a runtime, memory or kappa
claim. The second line cannot be used as a working grid for the source's
literal products. It is 40 times coarser than the required product grid.

## Exact execution being certified

Each independent entrance role r starts as a basis scalar z_r. A
snapshot is a rational linear form in these 1501 variables. At a node,
the graph computes the listed rational coefficient times each donor
snapshot, in sorted donor order, and adds the products into a fresh
zero accumulator. The returned or terminal snapshot is the completed
row. The source schedule fixes legal dependencies and chart locations.
A normalized paid transfer leaves these scalar variables unchanged.
The graph has 6142 paid nodes and 1501 terminal nodes, hence 7643 rows.

The audit covers those rational products, additions and snapshot
values. It does not evaluate physical Clifford matrix entries, native
internal butterflies, the signed caller, recursive descendants, root
depth or final unscalings as additional scalar steps. The source's
common-root proof must still supply those other precision contributions.
Its 16-stage caller has a separate bound; no replacement for that bound
is supplied here.

## Minimum-grid criterion

For each literal product q times a donor row, list the reduced rational
coefficients of the product in the independent entrance variables.
Let A be the least common multiple of all their denominators. Let B
be the least common multiple of the denominators of all completed rows.
The initial rows have integer coefficients. Then:

- Every product and addition is exact on integer grid G for every
  integer input if and only if A divides G.
- Every completed snapshot is representable on grid G for every
  integer input if and only if B divides G.

For sufficiency, each product coefficient times G is an integer. Every
partial sum is then integral as well. Induction over the schedule proves
exactness. For snapshot representability, apply the same argument to
completed rows without claiming that their products are representable.

For necessity, a reduced coefficient a/b evaluated on its named basis
input gives a/b. It is representable in integer units G only if b divides
G. Taking the least common multiple proves the claims. This is the
prefix-coefficient precision method used in Gareth Davidson's PR #866,
applied here to rational term products and completed snapshots of a
new pinned graph. The general method is prior work.

The computation starts from the source's sufficient grid Q. If its
integer coefficient values are v_i, the least common multiple of their
reduced denominators is

```text
Q / gcd(Q, v_1, v_2, ...).
```

Prime valuations prove the identity: the largest denominator valuation
is the valuation of Q minus the smallest valuation shared with all v_i.
The executable computes this quantity separately for products and rows.
It then executes the whole graph again at the smaller product grid,
checks every division and compares every row under exact rescaling.

## Sharp product witnesses

The following exact coefficients occur before addition. Set the named
input to one and all other inputs to zero. Negative donor labels are
the source's bitwise-complement labels for entrance roles.

| Required prime power | Node | Donor | Input | Scalar factor | Product coefficient |
| --- | ---: | ---: | ---: | --- | --- |
| 3 squared | 87424 | -1344 | 1343 | -4/9 | -4/9 |
| 5 squared | 96681 | 90728 | 1226 | -4/5 | -4/25 |
| 2 to power 12 | 103161 | 88788 | 265 | 1/8 | 3/4096 |

Their denominators have least common multiple 921600. The complete
integer replay supplies the matching upper bound. Thus neither an
odd factor below divisibility by 225 nor a guard below 12 can work
for every normalized basis input under this literal execution.
This is a divisibility statement: some larger integers also fail if
they lack a required prime power.

A separate integer execution at each grid `921600/p`, for p=2,3,5,
stops at a real nonexact division. The first failures are:

| Grid | Input | First node | Numerator | Divisor | Remainder |
| --- | ---: | ---: | ---: | ---: | ---: |
| 460800 | 265 | 103161 | 2700 | 8 | 4 |
| 307200 | 1343 | 87424 | -1228800 | 9 | 6 |
| 184320 | 1226 | 96681 | -147456 | 5 | 4 |

No rounded endpoint error is claimed. These executions stop at the
first failed exact division instead of choosing a rounding convention.

## Snapshot witnesses and the temporary-product gap

The completed-row coefficients -4/9 at node 87424/input 1343,
7/1536 at node 95529/input 265, and 1/10 at node 87792/input 1319
have denominator least common multiple 23040. The full row scan gives
the same upper bound. These prove the snapshot-only minimum and all
three of its required prime valuations.

Nevertheless, at snapshot grid 23040 the basis input 265 first fails
at node 100778, donor 97562: numerator 180 divided by 24 leaves
remainder 12. Input 1226 first fails at node 96681: numerator -18432
divided by 5 leaves remainder 3. Thus a claim that every stored row fits
does not make the literal term-by-term implementation exact. A different
arithmetic lowering could change this requirement and is outside scope.

## Verification and source boundary

The package retains 15 exact predecessor files, their original notices
and an Apache-2.0 license. PREDECESSOR.json records their published
commit URLs, Git blobs, SHA-256 hashes and sizes. The verifier checks
those bytes before loading the retained source graph constructor.
The constructor authenticates the frozen word and its 12 parent edits,
applies the 15 published pivots and checks the final schedule. Reuse of
that constructor is explicit; this is not an independent graph compiler.

The new arithmetic evaluator checks all 8533666 scalar coefficient
products at the source grid and again at the minimum grid. Every row
agrees under rescaling; all 1501 public endpoint rows agree with the
specified normalized native map at both grids. A separate Fraction
interpreter evaluates the four named basis inputs without an integer
scale and confirms all six product/snapshot witnesses. Eight negative
controls check missing prime factors and misuse of the snapshot grid.

This finite theorem does not lower the selected root format or replace
the source's complete physical proof. Clifford factors, recursive debt,
integer magnitude, overflow, caller precision, physical service constants,
layout, restoration and the complete invoice remain separate obligations.
All five selected assumptions remain. No new kappa or supplier admission
is claimed. No predecessor scientific suite, selected cold replay, Lean
or Docker run is included. Independent human and formal-kernel review
are unclaimed.

Prepared by Ali Romman with substantial OpenAI Codex assistance.
Credit the banked graph and common-root source in PR #7674, SYLforge's
parent PR #7669 and its preserved lineage, and Gareth Davidson's PR #866
for the precision criterion and basis-witness method. The retained source
files keep their exact notices. New work is Apache-2.0.
