# Independent coefficient enumeration

This verifier checks the claimed nonempty-star deletion budgets for prescribed
three-edge target sets at `p=5,6`. It has its own target-orbit enumeration and
searches decoder coefficients directly. It does not import, invoke, or assume
the primary four-block optimizer. Cases `p=2,3,4` are additional finite boundary
controls; this evidence does not assert a uniform theorem at those parameters.

## Reproduction

From this directory, with Python 3.10+ and a C++17 compiler:

```sh
python run_independent.py
```

`CXX` selects the compiler; its default is `c++`. The executable is created in a
temporary directory and removed afterward. The command compares its full
computed evidence with the retained `INDEPENDENT.json` and does not write into
the source directory. `python -O run_independent.py` performs the same checks.
To generate a separate receipt, use `--output /path/to/new.json`; existing files
are never overwritten. `--check /path/to/receipt.json` checks another receipt.

Expected census, followed by `PASS`:

| p | Target triples | Orbits | Feasible orbit budgets | Impossible orbits |
|---|---:|---:|---|---:|
| 2 | 4 | 1 | 1 on 1 orbit | 0 |
| 3 | 220 | 9 | 6 on 7 orbits; 7 on 1 orbit | 1 |
| 4 | 2,024 | 16 | 12 on 14 orbits; 13 on 1 orbit | 1 |
| 5 | 9,880 | 18 | 18 on 16 orbits; 19 on 1 orbit | 1 |
| 6 | 34,220 | 19 | 24 on 17 orbits; 25 on 1 orbit | 1 |

The exceptional orbit has representative `{02,03,12}`, with vertices `0,1`
and `2,3` the two original opposite pairs. Its orbit sizes at `p=5,6` are
40 and 60. The impossible orbit is a triangle, represented by `{02,04,24}`;
its sizes are 80 and 160. Every other orbit has the lower budget.

## Why the finite search is complete

Vertices are numbered `0,...,2p-1`, with mates `v xor 1`. A decoder obtained
from the binary vertex-star observations has one coefficient per vertex.
Place the coefficients of three decoder rows into a label
`lambda(v) in F_2^3`. The three-bit column at an edge `uv` is exactly
`lambda(u) xor lambda(v)`.

Three prescribed target rows can be normalized to the three unit vectors.
Thus, ordering the targets `t_0,t_1,t_2`, their constraints are
`lambda(u_i) xor lambda(v_i) = 1 << i`. Every nontarget edge whose column is
nonzero must be deleted; deleting exactly those edges suffices. Minimizing
this number therefore optimizes the decoder in the stated observation model.

For a target triangle the three constraints are inconsistent, since their
left sides sum to zero and their right sides do not. Every other three-edge
target graph is a forest. Its three constraints leave `2p-3` components,
including isolated vertices. Labels inside each component are determined by
one free three-bit label. Translating all vertex labels by a common label
changes no edge column, so the first component's label may be fixed to zero.
The search enumerates all `8^(2p-4)` assignments of the other components.
It permits all eight labels and uses no four-block restriction.

The C++ objective counts equal-label graph edges incrementally. Assigning
vertex `v` label `x` adds the number of already assigned vertices labelled
`x`, minus one if its mate already has label `x`. Therefore the deleted-edge
count is `2p(p-1) - equal_edges - 3`. The C++ receipt includes the leaf count,
and Python requires exactly `8^(2p-4)` leaves for each feasible target orbit.
There is no branch pruning, sampling, randomness, or early stopping.

Orbit enumeration considers every three-edge subset. To canonicalize it,
Python enumerates all six edge orders and eight endpoint orientations, then
renames original pairs and their signs in order of first occurrence. This
exactly removes the action of pair permutations and independent pair sign
flips. Every target triple is counted once in the resulting census.

Completed assignment counts across all feasible orbits are 4,456,448 for
`p=5` and 301,989,888 for `p=6`. All orbit keys, sizes, and minima agree with
the primary partition census; that comparison was made only after completing
the independent enumeration.

## Checks and limitations

Each attaining deletion set is checked by a separate Python Gaussian
elimination of the surviving vertex-incidence rows. This checker does not use
the labels or a graph-component rank formula. For each witness, restoring each
single deleted edge must make simultaneous decoding fail. There are 307 such
controls at `p=5` and 433 at `p=6`. Rank-zero coefficient rows are rejected.
For the infeasible orbit, Gaussian elimination confirms failure even when
only the target edges survive.

A third method enumerates every possible nontarget deletion mask and checks
its rowspace, for all 4 target triples at `p=2` and all 220 at `p=3`.
These exact minima agree with the coefficient search.

All main results exclude the empty star, which would grant the all-one edge
observation. The retained control at `p=3` finds that a prescribed triangle
is impossible with nonempty stars but can be decoded after exactly five
deletions with the empty star. The model distinction is therefore material.
This program does not classify the larger observation model at `p=5,6`,
price the observations, construct a paid supplier, or establish any new
multiplication bound.

The source dependency is the binary cut-code model in Sam Sung's pending
PR 669, pinned at `7d526020fc368ce4157cd436995c2f4fcf683318`, especially
`HIGHER-GRAPH.md` and the prescribed-target discussion in `HIGHER-WEIGHTS.md`.
The finite search itself does not rely on its optimum or equality formulas.
Base repository commit: `91a2094f2e022930069e8cfdc810a3ea1b81cd09`.
Prepared for DLamdata with substantial OpenAI Codex assistance; Apache-2.0.
