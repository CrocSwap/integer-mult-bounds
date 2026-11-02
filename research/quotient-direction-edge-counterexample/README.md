# Distinct directions do not repair the B2 acyclic-edge bound

A six-line rational configuration has six distinct projective directions in
**each** factor family, exact minimum binary pairing cost **6**, and maximum
acyclic edge count **9**. Collapsing proportional `q` directions therefore
leaves a false lower bound. This refutes the repair proposed as the first step in
Open next question 1 of
[Aaron Wang's PR2340](https://github.com/CrocSwap/integer-mult-bounds/pull/2340).

Claim type: a finite counterexample with an exact scoped proof and exhaustive
finite corroboration. No new kappa, physical supplier or selected-frontier
change follows. This contribution is produced by Nick Petalas.
Independent human and formal proof-kernel review are unclaimed.

## Model and proposed repair

Use DreamingOfClouds's rank-three decoder model from
[PR2162](https://github.com/CrocSwap/integer-mult-bounds/pull/2162).
There are rational vectors `p_i,q_i` in `Q^3`, with `p_i.q_i != 0`.
An admissible binary matrix `B` has diagonal one and can have an off-diagonal
one at `(i,j)` only when `p_i.q_j=0`. Its cost is

```text
cost(B) = sum_(a=0)^2 rank_F2 B[R_a,A_a],
R_a = {i : p_i[a] != 0},  A_a = {j : q_j[a] != 0}.
```

A wild edge `i -> j` is a zero off-diagonal dot product using all three
coordinates. `F` consists of lines with both supports full; `H` consists of
the harmonic lines with two equal diagonal coordinate contributions.
PR2340 distinguishes the valid maximum induced acyclic **vertex** count from
the false maximum acyclic **edge** count. Its proposed repair is to collapse
proportional `q` directions before counting edges, and ask whether

```text
cost(B) >= v - |H| - |F| + masE_quotient.
```

For definiteness, quotient vertices are the equivalence classes under rational
proportionality of `q`; an edge exists if a wild edge connects those classes,
and loops are discarded. Every class below is a singleton, so representative,
edge-multiplicity and loop conventions cannot affect this counterexample.

## Literal witness

All coordinates are nonzero. Indices start at zero.

| i | p_i | q_i |
|---:|---|---|
| 0 | (6,-5,1) | (1,1,1) |
| 1 | (-6,8,-2) | (1,2,4) |
| 2 | (2,-3,1) | (1,3,9) |
| 3 | (-2,6,-2) | (2,3,5) |
| 4 | (-10,10,-2) | (2,5,13) |
| 5 | (14,-16,4) | (2,4,10) |

Direct multiplication gives the complete dot matrix

```text
      q0 q1 q2 q3 q4 q5
p0     2  0  0  2  0  2
p1     0  2  0  2  2  0
p2     0  0  2  0  2  2
p3     2  2 -2  4  0  0
p4    -2  2  2  0  4  0
p5     2 -2  2  0  0  4
```

Its leading three-by-three block is `2I`, so the factorization has rank
exactly three. Divide `p0,p1,p2` by 2 and `p3,p4,p5` by 4 if a unit rational
diagonal is desired. This changes no support, direction, zero or admissible
binary pairing.

For `q`, normalization to first coordinate one gives

```text
(1,1,1), (1,2,4), (1,3,9), (1,3/2,5/2), (1,5/2,13/2), (1,2,5).
```

These are distinct. Primitive signed integer normalization of the `p` rows
gives `(6,-5,1),(3,-4,1),(2,-3,1),(1,-3,1),(5,-5,1),(7,-8,2)`, also distinct.
Thus there are no repeated projective points in either family. Since every
support is full, `F` has size six, `H` is empty, and all three cost blocks
are the entire matrix `B`.

Choose `B=diag(J3,J3)`, with `J3` the three-by-three all-ones binary matrix.
Its literal rows are

```text
111000
111000
111000
000111
000111
000111
```

Each off-diagonal one lies at a displayed zero dot product. Its two disjoint
nonzero row types are independent over `F2`, so `rank(B)=2` and `cost(B)=6`.
This is also the exact minimum. A binary rank-one matrix with every diagonal
entry one must be the all-ones matrix: writing it `u v^T`, every `u_i=v_i=1`.
That matrix is inadmissible, since `p0.q3=2 != 0`. Rank zero is incompatible
with the diagonal. Every admissible pairing therefore costs at least six.

## Exact quotient edge count

The complete wild graph consists of two bidirected triangles on `{0,1,2}`
and `{3,4,5}`, together with three additional edges

```text
0 -> 4,  1 -> 5,  2 -> 3.
```

An acyclic edge set contains at most one orientation of each triangle pair,
for at most three edges per triangle. There are only three other edges,
so its size is at most nine. Put the first triangle before the second in a
total order and keep every forward edge. This retains all three extra edges
and three internal edges per triangle, attaining nine.

The direction quotient changes nothing. Consequently

```text
minimum cost = 6 < 0 + masE_quotient = 9.
```

The valid vertex bound is unaffected. An induced acyclic vertex set contains
at most one vertex per bidirected triangle, and any one from each triangle
is acyclic, giving vertex count two. The example also satisfies `cost(B)>=v`.
It does not refute that separate decoder target or the printed vertex theorem.

The extra wild edges are absent from the attaining `B`. This identifies a
failure of the proposed direction-only repair that does not use duplicated
vectors. It is not a counterexample to an additional restriction that counts
only wild edges selected by `B`, with both factor families distinct.

## Verification

The standalone standard-library verifier imports no predecessor code and
executes no predecessor scientific suite. It checks every dot product,
actual coordinate support, primitive projective direction and selected pairing.
It enumerates all `2^15=32,768` admissible pairings and compares binary pivot
elimination with explicit row-space generation for every one. The exact cost
histogram is

```text
cost       6    9    12     15    18
pairings   1  119  4260  19140  9248
```

All 720 vertex orders independently corroborate a 64-subset dynamic program
for the acyclic-edge optimum. Their forward-edge counts have histogram
`6:90, 7:270, 8:270, 9:90`. Ten controls reject seven malformed witnesses,
check sensitivity to removing a cross-triangle edge, and check identity and
all-ones ranks. Acceptance uses explicit exceptions and remains active under
optimized Python.

From the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/quotient-direction-edge-counterexample/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/quotient-direction-edge-counterexample/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/quotient-direction-edge-counterexample
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/quotient-direction-edge-counterexample --check-source-history
```

Use any CPython 3.12 executable in place of the absolute interpreter elsewhere.
Direct runs print `PASS_QUOTIENT_DIRECTION_EDGE_COUNTEREXAMPLE` and a generated
exact summary. Optional `--receipt /absolute/external/path.json` creates a new
receipt with the result, interpreter version and hashes of all package files.
No receipt is hand-written or committed.

The proof is self-contained. The runner authenticates the exact historical
source documents through [SOURCES.json](SOURCES.json); they are provenance,
not imported executable dependencies. Selected-source metadata orientation
passed. No selected scientific replay, native caller, dirty restoration,
compiler/hosting/precision/tape construction, supplier admission, Lean or
complete multiplication theorem was run or established.

Managed Python allocations are bounded by this fixed six-line domain; a
row space has at most 64 elements, the census has 32,768 iterations, and graph
checks have 720 orders and 64 subsets. Every function is under 60 lines.
The verifier uses no recursion, dynamic code loading or third-party package.
Warning-strict normal and optimized runs provide the available diagnostics.

## Open next questions

Does the edge inequality hold when both factor families are projectively
distinct and the wild graph is restricted to off-diagonal ones of `B`?
This witness needs its three unselected edges for the gap. First derive a
rank-sensitive constraint for that changed graph; direction collapsing alone
is insufficient. PR2334 already rules out unrestricted selected-edge bounds
when repeated directions are allowed, so that predecessor must be retained.
A proof or a new counterexample for the combined restrictions remains absent.
PR2340's broader request for the strongest rank-aware replacement remains open.
This package stops at the first explicit quotient-repair counterexample.

## Provenance and credit

Scientific base: canonical main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`,
priority revision eight. [TASK.json](TASK.json) records the change from a
current-supplier decoder experiment to the explicit historical repair question.
This is a decoder-bound side result, with no current paid-profile improvement.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19361606)
records the precise scope and checked overlap limits.

Aaron Wang / navinor posed the quotient-direction question in PR2340 and
identified the edge/vertex distinction in PR2293. DreamingOfClouds supplies
the rank-three model and valid B2 vertex theorem in PR2162, following the
retained PR2111/PR1590 lineage. ROTl24's PR2334 supplies a separate repeated-
direction family with unbounded gaps and a selected-edge counterexample.
The new six-line witness, exact minimum and quotient-edge calculation are
produced by Nick Petalas. No predecessor credit or frozen source is changed.
Apache-2.0.
