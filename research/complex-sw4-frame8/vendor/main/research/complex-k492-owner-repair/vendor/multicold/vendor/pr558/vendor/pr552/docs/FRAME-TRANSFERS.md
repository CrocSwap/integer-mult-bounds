# Two exact cross-field transfers behind the frame improvement

The useful connection is structural, not a claim that disparate fields were historically unrelated. A frame history is literally a finite diagram of vector spaces with injective maps. Its admissible edits are order-preserving edits of that diagram. We use that identification to discover a construction that isolated gate edits miss.

## 1. Persistence diagrams of inclusions become frame histories

Let an acyclic event graph have a vertex for each scalar gate and immutable vertices for every register entrance, exit, retained-copy observation and target cut. Every register supplies directed edges between its successive occurrences. A vertex e carries a subspace F_e of a finite-dimensional vector space. The legal frame condition is exactly F_e <= F_f on every edge e -> f. A two-register gate is a shared vertex; its two histories must agree there.

Restricted to a register chain, this is a persistence module with injective structure maps. A basis adapted to its flag decomposes it into coordinates with birth times. A jump of rank r means r births at that point. The compiler's paid histogram counts these jumps. Its recurrence moment charges a concave function of the number born together. Delaying births so they occur in a larger group can therefore improve cost, provided all shared-event constraints are respected.

This is an identification of the finite linear objects, not an application of persistent-homology stability estimates. We do not assume that the entire branching diagram has an interval decomposition or that one common coordinate basis works for all frames. The explicit subspace updates below avoid both assumptions.

Fix a nonzero linear functional lambda and H=ker(lambda). On a chain, F -> F intersect H is a sub-persistence module, and the exact sequence

    0 -> F intersect H -> F -> lambda(F) -> 0

shows that each affected space loses exactly one dimension. The quotient is either zero or the one-dimensional field. Thus intersecting a chosen time region with H modifies a concrete birth history by a rank-one change. The algorithm uses the actual spaces, not just their dimensions or a guessed barcode.

## 2. Galois adjunction becomes a legality-closure algorithm

For the inclusion j:H -> V, image and preimage of subspaces form an adjunction:

    j(S) <= F  iff  S <= j^-1(F).

The counit in the ambient space is F intersect H. This is the same meet operation that appears in the modular subspace lattice underlying type-A flag geometry. It is monotone and deflationary. Its dual operation is adding a fixed line, a monotone inflationary operation. These order properties give a concrete compiler transformation.

Sufficient contraction theorem. Start from any legal frame diagram with its immutable vertices. Choose a set S of mutable vertices satisfying, for every edge e -> f with f in S and e outside S, F_e <= H. Replace F_e by F_e intersect H for e in S and leave all other vertices unchanged. The resulting diagram is legal and has identical immutable boundaries.

Proof, edge by edge. If both vertices are changed, intersection is monotone. If neither changes, use the original inclusion. If only the source changes, it only shrinks, so inclusion survives. If only the destination changes, the stated boundary condition gives F_e <= F_f intersect H. These are all cases. No unknown extension, common apartment or unproved gadget appears.

Construct S from a seed by following predecessor edges. Whenever a predecessor's frame is not contained in H, include it as well. Stop with failure if this would change an immutable vertex. Otherwise the resulting finite closure satisfies the theorem. It is the smallest predecessor closure for this prescribed uniform-intersection action after vertices already inside H are ignored. Minimal closure does not imply optimal cost. A cost bound is computed from every affected register edge, including internal edges when codimension exceeds one.

The dual sufficient theorem adds a fixed line L on a successor closure, stopping when a successor already contains L. The same four-edge-case proof applies. This gives a second family of checked moves, even though the selected witness uses only contractions.

## Operator correctness is a separate obligation

Only frames change; the full scalar instructions, order, cuts, preconditioner, compensation and literal inverse cleanup are held fixed. The scalar endpoint therefore stays the same on arbitrary inputs. Changing frames changes the physical lifted word and its phases, however. The old phase receipt cannot be reused wholesale. The actual construction rebuilds changed Clifford phases, wrappers and local programs, audits all728 columns in both orientations, then rebuilds every global owner chart and the complete finite invoice. This is the necessary bridge from the order-theoretic theorem to the retained compiler interface.

## Concrete witness and universal moment improvement

The frozen input is the prior static44/PR534/syndrome word. Single-event frame changes over999 present frames, followed by whole equal-frame-plateau changes, found no improvement. The closure search instead selected eight hyperplane waves, using functionals33,33,39,39,192,192,198,198 on F2^9. Each wave changes8 to10 scalar-event frames together; no scalar instruction is deleted or reordered.

Every wave changes the complete local paid histogram by

    2 e1 - 2 e2 - 2 e3 + 2 e4.

All eight give16 copies of the same replacement. Rank mass, helper widths and complete-call signatures remain unchanged. The pair (2,3) is a doubly stochastic averaging of (1,4): use the matrix with diagonal2/3 and off-diagonal1/3. Strict concavity therefore proves

    1^a + 4^a < 2^a + 3^a  for every 0<a<1.

This proves a strict paid-moment gain for every relevant recurrence exponent, not just at the optimizer's floating score. Child count is unchanged, so the count-proportional fallback term is unchanged too. Each complete call uses this improved local word; the actual owner map is then reconstructed with the new frames. The global delta is72 times the local delta.

The constructor checks every actual finite subspace chain and unchanged boundary. Eight omission controls restore one necessary frame change in each wave and are rejected by the chain checker. An independent worker reconstructs the edge model and verifies every wave's exact histogram delta. Final physical verification remains essential and is performed by the package's replay.

## Bounded searches and sources

The single-functional search examined31,627,350 seed/direction candidates across the improvement sequence, including the final pass with no further gain. The extension with two simultaneous functionals examined7,381,812 seed cases, of which1,920 closures were feasible; it found no further paid gain. These are finite neighborhood results, not an impossibility theorem or a global optimum.

Source structures inspected:

- Mathlib Algebra/Module/Submodule/Map.lean, gc_map_comap: the exact image/preimage adjunction.
- Mathlib LinearAlgebra/FiniteDimensional/Lemmas.lean, finrank_sup_add_finrank_inf_eq: the dimension arithmetic of the subspace lattice.
- [Parallel computation of interval bases for persistence module decomposition](https://arxiv.org/abs/2106.11884): persistence modules as type-A quiver representations, and flag-based computation. Our application only uses the elementary finite injective-chain specialization proved above.
- The registered source catalog and typed DAG were queried for submodule meets, map/comap adjunctions, filtrations and kernels. Results and source hashes are retained. No fresh Lean compilation is claimed.

OpenAI's coarse-assembly Persistence.lean was inspected, but its direct-limit nonvanishing theorem is not the needed finite flag theorem and is not used as a spurious citation. The source search led to the actual order/subspace structures instead of forcing a semantic filename match.
