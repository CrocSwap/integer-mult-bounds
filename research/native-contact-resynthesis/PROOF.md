# A source-bound containment proof

Fix the complete word pinned in SOURCES.json, each scalar operation's
persistent owners, all 224 main entrance/exit charts, and the dimension-nine
binary frame space V. The claim concerns this incidence pattern.

A persistent frame is a linear subspace of V. Between native warps, paid
transports only enlarge frames under containment. A scalar ADD requires one
common frame on its two owners. A native warp sends E to G(E) for an
invertible linear G and preserves dimension; its signed inverse uses G
inverse. Other G matrices, warp frame pairs, scalar contact subspaces and
helper boundaries may change. No tariff or native phase formula is used.

These are the nested frame grammar's hypotheses. Changed owner incidence,
main boundary charts or nonnested transitions are outside them.

## 1. Necessary containments

Create a vertex for each scalar contact and each native warp output. For
every persistent owner connect its last contact/output vertex to its next
scalar contact. An ADD has one shared vertex, allowing containment to flow
from one owner's earlier frame to either owner's subsequent frame.

Start a fresh chain at every native warp output. Omit every warp's
input/output relation: no graph edge presumes containment through a warp.
Connect the final contact of each main owner to its actual exit subspace.
Omit helper endpoint caps and initial-frame lower bounds entirely.

Every admissible realization satisfies these edges by the shared scalar
frame and monotone transport rules. Removing other constraints relaxes the
problem. If u has paths to exit caps F_1 through F_k, its subspace S(u)
must satisfy S(u) contained in the intersection of those caps.

Graph search generates the recorded paths. A separate direct-scan checker
validates every successive contact on an actual common persistent owner,
with no intervening contact or warp on that owner. It verifies the final
edge to the actual main exit and does not trust generated adjacency lists.
It runs on both source orientations, whose owned-center contacts differ.

## 2. Exact output caps

For each of the twelve early positive occurrences, labels 47 through 58,
eight recorded rank-eight main exits intersect to L = span{45} over F2.
For their early inverse occurrences the caps are these source lines:

| Native label | Initial source owner | Inverse-output line generator |
| --- | --- | --- |
| 47 | 33 | 138 |
| 48 | 55 | 324 |
| 49 | 74 | 352 |
| 50 | 85 | 505 |
| 51 | 49 | 148 |
| 52 | 83 | 382 |
| 53 | 98 | 487 |
| 54 | 101 | 375 |
| 55 | 68 | 176 |
| 56 | 80 | 494 |
| 57 | 88 | 477 |
| 58 | 31 | 26 |

The verifier computes every intersection as a literal set of binary vectors.
Independently, each rank-eight cap has one nonzero dual normal. Those eight
normals have rank eight and annihilate the recorded nonzero line generator.
Their common kernel has dimension one, corroborating the same cap without
using the point-set intersection result.

There are 24 output claims, eight paths per claim and two actual source
orientations, hence 384 checked paths. These are exact source coordinates,
not numerical ranks or an inference from an optimizer's status.

## 3. Both early contracts are forced

Fix one positive/inverse pair. Let A be its original source entrance line
and L = span{45}. Its persistent source has no preceding native warp, as
checked on the actual source. Its positive input E therefore contains A
under any permitted retiming. The certified positive output cap gives
G(E) contained in L. Invertibility implies

    1 <= dim E = dim G(E) <= dim L = 1.

Thus E = A and G(E) = L, without presuming the new warp's input rank.

The same source participates in four scalar ADDs and no intervening native
warp before the inverse. Its inverse input H consequently contains L.
The certified inverse output lies in A, so

    1 <= dim H = dim G inverse(H) <= dim A = 1.

Therefore H = L and G inverse(H) = A. Every scalar contact between these
warps lies between L and H under containment and must equal L. Growing
these contacts before the inverse is also excluded by this argument.

The proof applies to all twelve pairs in both orientations. G(A) = L
remains necessary at their later uses. Releasing only these early labels
does not remove that shared-map constraint. It may still be profitable to
change other parts of the word.

## 4. Limits and constructive consequence

This is a necessary condition in a relaxed geometric model. It is not
uniqueness or optimality of a complete native implementation. It verifies
no full multiplication theorem and establishes no new paid profile or kappa.

A changed scalar incidence pattern can sever a recorded path. Changed main
charts can change a cap intersection. Nonnested operations can invalidate
containment edges. Each is an explicit possible escape requiring a fresh
exact endpoint and complete cost proof. Extra native-map and helper-boundary
freedom alone does not invalidate this particular certificate.

Prepared for Cinna Davis with substantial OpenAI Codex assistance. Apache-2.0.
Source and shared-map attribution are retained in README.md.
