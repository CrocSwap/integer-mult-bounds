# Exact statement and independent finite proof

## 1. Coordinates and graph

Let C be the binary length-24 Turyn code

    C = {(a+x, b+x, a+b+x): a,b in H, x in H'},

where H is the evaluation code of affine functions on F₂³ and H' is H
permuted by `(0,1,2,4,3,6,7,5)`. The verifier constructs C as the span of
twelve explicit binary generators, checks its size 4096, and checks its
weight distribution `{0:1, 8:759, 12:2576, 16:759, 24:1}`.

The 24 coordinate rows in `WITNESS.json` belong directly to the predecessor's
two full-port shell families:

1. Eight entries ±2 on a weight-eight codeword, all other entries zero,
   with an even number of minus signs
2. A sign vector from a codeword, with one coordinate multiplied by −3

The verifier checks these family conditions directly. It also checks the
coordinate-sum, parity, and mod-four residue-code conditions, and squared
norm 32. Every row has block squared norms `(16,8,8)` and is normalized so
the first nonzero coordinate of each block is positive. The generator's
different implementation reconstructs the complete sorted canonical port
array and matches the predecessor's immutable array digest before selecting
the original 24 indices.

If x is an integer row, its real lattice vector is x/√8. The tensor scalar
kernel between two ports is therefore

    K(x,y) = (x₀·y₀)(x₁·y₁)(x₂·y₂) / 8³.

Only its nonzero pattern is used. No square roots or floating-point
calculations occur: two distinct vertices are adjacent exactly when all
three integer block dots are nonzero. The complete 24-vertex graph has
171 edges: 21 within the seven anchors, 79 anchor-to-variable edges, and
71 between the remaining seventeen vertices.

## 2. Standard-dot fitting and anchor normalization

A width-h fitting assigns each vertex a vector p(v) in F₂ʰ satisfying

    p(v)·p(v) = 1,
    p(v)·p(w) = 0 whenever v and w are adjacent.

The seven anchors form a clique, so in a width-eight fitting their labels
are an orthonormal set. Their span U has dimension seven and is
nondegenerate. Since F₂⁸ with its standard dot product is nondegenerate,
U's orthogonal complement is one-dimensional and nondegenerate. Its
nonzero vector thus has self-dot one. The seven anchors together with this
vector form an orthonormal basis. A dot-product-preserving change of basis
can consequently put the anchors at e₁,…,e₇ without loss of generality.

Each other label must have odd Hamming weight, and coordinate j must be
zero if its port is adjacent to anchor j. This leaves the complete domain
sizes

    2, 2, 8, 2, 8, 16, 2, 2, 16, 16, 8, 8, 8, 2, 8, 2, 8.

No possible eight-bit label is omitted. A lower-dimensional fitting could
be padded with zero coordinates to width eight, so disproving width eight
also excludes every smaller width.

## 3. Exact Boolean encoding

For each vertex v and each remaining label ℓ introduce X(v,ℓ). Include:

- A disjunction of all X(v,ℓ) for each vertex
- A clause `¬X(v,ℓ) ∨ ¬X(v,m)` for every distinct pair of its labels
- For each retained graph edge vw, the clause
  `¬X(v,ℓ) ∨ ¬X(w,m)` whenever ℓ·m = 1

The first two conditions select exactly one label. The last is exactly
orthogonality on retained variable edges. Thus CNF satisfiability is
equivalent to a fitting of the graph with all anchor constraints fixed.
The producer and verifier implement the encoding separately and their
full clause arrays are compared in tests.

The original graph gives 118 variables and 1,999 clauses. One deterministic
deletion pass, with edge order shuffled using seed 78, leaves 57 of the
71 variable edges. Its CNF has the same 118 variables and 1,837 clauses.
Deleting constraints cannot turn a satisfiable graph into an unsatisfiable
one, so a contradiction for this reduced graph also excludes a fitting
of the original graph.

## 4. Local verification of the contradiction

`PROOF.json` is a binary decision tree. A node contains zero or more unit
deductions, each citing an original clause index. Each deduction is
accepted only when all the reason clause's other literals are assigned
false and its sole unassigned literal is exactly the deduced one.

A terminal node cites a clause and is accepted only when every literal
of that clause is assigned false. An internal node names an unassigned
Boolean variable and contains **both** children, for its true and false
values. Their inherited assignments are checked separately.

Induction on this finite tree proves that no extension of a node's incoming
assignment satisfies the CNF: unit deductions preserve every satisfying
extension, a falsified clause has none, and the two branches exhaust the
values of their unassigned variable. At the root the incoming assignment
is empty, proving unsatisfiability. This induction, not the SAT producer's
return status, justifies the result.

The checked tree has 85 nodes, 43 contradicted-clause leaves, and 1,042
unit deductions. All checks use explicit conditions and remain active
under Python optimization. The verifier imports no SAT solver, producer,
original arc-consistency search, or predecessor geometry module.

## 5. Tight finite boundary and core scope

`CONTROLS.json` gives a width-eight label assignment for each of the 57
single-edge deletions from the **reduced** variable-edge graph, retaining
all anchor edges. The verifier checks every label's diagonal, every
anchor constraint, every remaining core edge, and a violation on the
deleted edge itself. Hence no proper subset of these 57 variable edges
is unsatisfiable under the fixed anchor constraints: removing any edge
already yields a fit, and further deletions preserve it.

This is inclusion minimality, not a claim that no different smaller core
exists. In particular, it says nothing about deleting anchor edges or
vertices. These positive assignments need not satisfy edges discarded
earlier from the original 71-edge variable graph.

A separate explicit width-nine assignment satisfies all 171 original
graph edges, so the exact standard-dot fitting dimension of this finite
graph is nine. The same coordinates cyclically permuted among blocks are
checked to remain in the Turyn code. Norms, diagonal conditions and
products of block pairings are unchanged, so each other profile contains
an isomorphic witness.

These three lower bounds do **not** add for arbitrary global labels:
different profile spans need not be mutually orthogonal. No unrestricted
global fitting lower bound of 27 is claimed. The predecessor already
established the nine-dimensional profile obstruction; the contributions
here are an independent proof architecture, explicit replayable local
deductions, and the edge-critical reduced certificate with positive controls.
