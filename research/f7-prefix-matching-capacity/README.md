# Matching capacity for a partial hypercube cycle

**Enabling combinatorial proof with bounded exact checks; no new kappa.**
This package gives a necessary completion condition for a simple path in
`Q_n` when a linear functional omits one coordinate. It uses the unused
matching edges and the two path endpoints. It can reject a prefix that
passes the complete-cycle matching-balance bound and the return-distance
bound. It does not change a maintained census engine.

This answers Open next question 2 of
[PR #4907](https://github.com/CrocSwap/integer-mult-bounds/pull/4907).
[PR #4992](https://github.com/CrocSwap/integer-mult-bounds/pull/4992) gives the
related sharp five-label cap. That cap is not an assumption of this proof.
The selected kappa remains `60403/20000000`.

## Contract and theorem

Let `n >= 2`. Let `L` be even, with `4 <= L <= 2^n`.
The input is a simple path `q_0,...,q_(k-1)` in `Q_n`, with `2 <= k <= L`.
A completion adds `r=L-k` new vertices, then an edge to `q_0`, to form a
simple cycle. Repeated interior vertices are not permitted.
Let `v` be one coordinate. The functional `f` has coefficient zero at `v`
and coefficient one at every other coordinate. Thus only `v` edges stay
in a functional class. They form a matching on the cube.

Let `a,b` be the current class sizes; let `e_0,e_1` count existing stay
edges in each class; let `c` count existing crossing edges. If `r=0`,
check the closing edge directly. The statements below concern `r>0`.
For each class `j`, count:

- `p_j`: unused vertices whose `v` neighbor is a path endpoint;
- `q_j`: unordered `v` pairs with both vertices unused;
- `u_j`: all unused vertices in that class.

For a proposed number `x` of new vertices in class zero, require
`0 <= x <= u_0` and `0 <= r-x <= u_1`. Put

```text
x_0=x, x_1=r-x,       s_0=a+x, s_1=b+r-x,
t_j=min(p_j,x_j),
M_j(x_j)=t_j+min(q_j,floor((x_j-t_j)/2)),
lo=max(c, 2 if s_0*s_1>0 else 0,
       2s_0-2(e_0+M_0(x_0)), 2s_1-2(e_1+M_1(x_1))),
hi=min(c+r+1, 2s_0-2e_0, 2s_1-2e_1).
```

**Every simple completion has an even integer in `[lo,hi]`.**
Consequently, reject the prefix if no feasible `x` has such an integer.
The `+1` in `c+r+1` counts the final edge to the start. It is required.
The returned split set is an outer bound; membership does not prove that
a completion exists. Universality is not needed for the theorem.

## Proof

Every internal path vertex already has its two cycle edges. A new stay
edge can therefore join an endpoint to an unused vertex, or join two
unused vertices. A stay edge between the two endpoints would close the
cycle before the `r>0` new vertices enter. Such an edge is not available.
An endpoint whose stay edge is already used has no unused `v` neighbor.

All candidate stay edges are disjoint, since the `v` edges form a matching.
The first type costs one new vertex and the second costs two. With a
budget of `x_j` vertices, select as many one-vertex edges as possible,
then two-vertex edges. Exchanging a selected two-vertex edge for an
available one-vertex edge cannot decrease the edge count. This proves the
upper bound `M_j`. Ignoring other path constraints can only enlarge this
bound. Extra vertices need not contribute stay edges.

Let `S_j` be the final stay counts and `C` the final crossing count.
Cycle degrees give `2s_j=2S_j+C`. We have
`e_j <= S_j <= e_j+M_j`, and `c <= C <= c+r+1`.
The final cycle crosses a cut an even number of times. If both classes
are nonempty, it crosses at least twice. Combining these inequalities
proves the interval test. The complete `r=0` case is a direct edge check.

The input validation and proof explicitly exclude repeated vertices,
nonedges and the premature endpoint closure. The result applies to any
translated start vertex. The finite traversal fixes the start at zero,
which loses no cycle by cube translation.

## Evidence

The verifier visits every restricted-growth simple path through the target
length. It does not use the proposed condition to control traversal. At
each prefix it collects the exact set of final class splits from all
closed descendants, then checks containment in the proposed split set.
Every coordinate omission is checked. First-occurrence relabeling covers
every labeled word and preserves the complete family of these functionals.

The domains `(n,L)` are `(3,6)`, `(4,8)`, `(4,10)` and `(5,12)`.
Their closed-cycle counts are `4,29,110,3695`. A second method enumerates
all literal words in the first two domains and agrees after canonical
relabeling. Exact counts and strict rejection witnesses are in
[RESULT.json](RESULT.json). The strict test compares with matching balance
and return distance; it does not assert a gain over every existing prune.

An independent subset enumeration checks the greedy capacity formula.
Invalid-input controls test repeated vertices, a nonedge, an odd target,
an oversized target, an invalid coordinate, an out-of-cube vertex and a
one-vertex prefix. Both crossing and preserving closing edges pass, while
a nonedge closure fails. All checks use explicit exceptions under `-O`.

## Reproduce

Use CPython 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/f7-prefix-matching-capacity
python3.12 -I -W error -B research/f7-prefix-matching-capacity/verify.py
python3.12 -I -W error -O -B research/f7-prefix-matching-capacity/verify.py
```

Expected markers: `PASS_REGISTERED_RESEARCH_PACKAGE` and
`PASS_F7_PREFIX_MATCHING_CAPACITY`. Direct checks need no Git or network.
`--emit-receipt` writes regenerated JSON to standard output; ordinary
replay compares the exact receipt and writes no files. The receipt binds
all five source files by SHA-256. Source documents are provenance only.

## Limits

The written theorem is uniform in `n,L`; the exhaustive corroboration is
limited to the four listed domains. No formal proof kernel, independent
human proof review, seven-label census, supplier admission or selected
cold replay is claimed. The condition ignores most cross-edge adjacency
and can accept impossible completions.

## Open next questions

Does this condition reduce runtime in a maintained census? Start with an
opt-in implementation and compare full leaf receipts and measured time
against the unchanged traversal. The cost of the bound can exceed the
work saved. No performance or integration claim is made here.

## Credit and sources

Prepared for Ali Romman with substantial OpenAI Codex assistance.
New work is Apache-2.0. Nick Petalas supplied the matching-balance lemma in
[PR #4894](https://github.com/CrocSwap/integer-mult-bounds/pull/4894).
Mihir Srivastava supplied the explicit prefix-capacity question in
[PR #4907](https://github.com/CrocSwap/integer-mult-bounds/pull/4907).
Ross Richardson supplied the singleton-prefix model in
[PR #943](https://github.com/CrocSwap/integer-mult-bounds/pull/943), and
Nicholas Stone supplied the parity-prune correction in
[PR #2973](https://github.com/CrocSwap/integer-mult-bounds/pull/2973).
Their retained notices remain unchanged. Exact main-branch source pins
are in [SOURCES.json](SOURCES.json); no predecessor code is imported.
The base is `bee95ce88f9f19802f0613f92838895cd0e14a1f`, priority revision 7.
