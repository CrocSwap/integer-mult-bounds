# A sharp graph bound repairs the centre block argument

**A nonzero common-kernel perturbation in the inherited selected-centre model
needs at least 15 source owners.** Consequently every block of at most 14
owners still requires exactly `104 |B|` additional scalar linear observations
to determine the whole later query. This concerns the selected PR1094 calls
0/4 and the unchanged linear observation contract; it is not an implementation
tariff or a bound on arbitrary centre-sharing architectures.

This package answers the independent-check request in
[Discussion 3062](https://github.com/CrocSwap/integer-mult-bounds/discussions/3062#discussioncomment-18999248).
It identifies an incorrect triangle inequality in PR3147, then replaces the
affected argument with a stronger local path count. The seven-owner theorem
from PR3097/3168 remains valid. Frozen sources and the selected frontier remain
unchanged.

## The error and its consequence

For a graph on `m` vertices with `U` missing edges, let `W` be the number of
wedges in its complement. The exact identity is

```text
triangles(G) = C(m,3) - U(m-2) + W - triangles(complement(G)).
```

PR3147's `check_c4_free_degree_feasibility` substitutes the minimum possible
`W` but omits the last subtraction. The nine points of `F3²`, incident with
the nine lines in three parallel classes, give a genuine cubic bipartite
graph with no four-cycles. Its distance-two graph on the points is `K3,3,3`:
it has 27 triangles, while the predecessor's purported lower bound is 30.
There are nine claw triangles and 18 six-cycles, not the claimed lower bound
of 21 six-cycles.

The byte-exact predecessor function and its source identity are retained in
[PREDECESSOR.json](PREDECESSOR.json) and
[inputs/pr3147-degree-feasibility.py](inputs/pr3147-degree-feasibility.py).
The counterexample does **not** satisfy the physical braid capacities, and
therefore does not refute the final owner floor. It refutes the intermediate
graph inequality used to establish that floor.

## The replacement theorem

Let `(B,D,E)` be a nonempty finite simple bipartite graph of minimum degree
three, without four-cycles. Write `t(v)` for its number of six-cycles through
`v`. Assume, for every `d` in `D` of degree `k`,

```text
t(d) <= 1                  if k = 3,
t(d) <= floor(k*k/4)       if k >= 4.
```

Then **`|B| >= 15`**. A radius-three path count gives
`|B| >= 5k - t(d)`. If `|B| <= 14`, the capacities force every vertex in
both parts to have degree three. Sizes below 14 are then excluded. At size
14, every vertex in `D` would lie on exactly one six-cycle, but counting
cycle incidences would give `3 * number_of_six_cycles = 14`, impossible.
[PROOF.md](PROOF.md) gives the complete argument, including the path-count
injection and the cubic reduction.

The abstract bound is sharp. On six symbols, take the 15 unordered pairs
as `B` and the 15 perfect matchings as `D`, with containment as incidence.
This graph is cubic, has no four- or six-cycles, and meets every stated
hypothesis. No labeling by the selected physical routes is asserted.

## Binding the graph to the selected source

The inherited observations are `Sx(g)=R x(g)` and
`Tx(d)=sum_p H[:,p] x_p(d rho_p)`, with `H=R/4`. Owners are invertible
matrices under the regular right action; the argument is not valid for an
arbitrary action with stabilizers. The pinned source derives `R`, `H` and
the 112 involutory routes, and verifies the rank-eight and nonparallel-column
premises needed to turn a nonzero common-kernel vector into an incidence
graph of minimum degree three.

This retains the predecessor's constant-payload source model: compared
executions have equal ordinary target/helper dirt, repair rows stay inside
disjoint owner blocks, and no other source-dependent state is supplied.
The global decoder may be nonlinear. The native interpretation remains
conditional on the inherited common-frame, constant-endpoint and source-adapter
identities; this package does not reprove that adapter.

Unique ordered products exclude four-cycles. This alone does **not** classify
six-cycles. The full reduced-triple route census from PR3097, independently
implemented in PR3168, supplies the stronger premise: every cyclically
reduced length-six relation is one of the 50 binary braids. At a fixed owner,
an incident braid-label pair determines at most one six-cycle. The braid
graph is triangle-free, giving the `floor(k*k/4)` capacity. At a degree-three
vertex the three columns must be dependent; the exact census of all 227,920
port triples finds 896 dependent triples, each containing at most one braid
edge. This gives the sharper capacity one.

The predecessor reports 229,936 port triples, but `C(112,3)=227,920`; the
replayed enumeration and its 896 dependent triples use the complete domain.

The primary replay re-derives these source premises using the credited
canonical helpers, including the full reduced-triple census. The separate
checker and behavioral controls test the new combinatorial argument and its
counterexamples. The mathematical proof is ordinary written mathematics
supported by exact finite checks, not a proof-assistant theorem.

## Reproduction

Use Python 3.12 and the standard library from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/centre-block-moore-bound
python3.12 -B scripts/check_research_commit.py --package research/centre-block-moore-bound
```

`VERIFY.json` lists the primary replay, independent check and controls.
`RESULT.json` retains the deterministic certificate. Source hashes and Git
blobs are in `SOURCES.json`; the selected archive is read in place. The
registered run does not need a pending PR checkout or a foreign Git object.

## Scope

The result repairs one implication and strengthens its consequence within
the existing one-to-one block-repair observation model. It does not validate
PR3147's separate circle-cancellation or sharing-cost claims, establish a
15-owner physical kernel, change the local moment, or produce a new kappa.
Native implementation, nonlinear observations, final-output-only readers,
overlapping repair blocks, hosting, precision and all-size transfer are not
covered. The complete selected cold replay is not required for this scoped
source-bound proof and was not rerun.

## Open next questions

- Can the abstract 15-owner incidence graph satisfy the actual route labels
  and coefficient equations? The unlabeled graph alone is not a physical
  construction. A further construction round needs the repository's family
  budget and obligation gate, including a complete favorable cost screen.
- Does a different, explicitly stated consumer require less than the whole
  later query? That changes the observation contract and needs a new proof;
  it cannot be inferred from this lower bound.

## Attribution

Credit dcharb78/PR3147 for the dependent-triple braid census and the argument
audited here; Gonzalo Mier/PR3097 for the complete six-relation classification;
Sudarsh3301/PR3168 for its independent route and Fano check; Ross Richardson/
PR3071 for the selected block-repair observation model and source derivation;
Aaron Wang/navinor, ywz65 and the selected construction authors for the
centre-sharing, observation and frame lineage retained by those packages.
The source helpers and frozen archive retain their original notices.

New graph correction, sharp abstract bound, replay and documentation:
Sagar Thakrar, with substantial OpenAI Codex assistance. Apache-2.0.
