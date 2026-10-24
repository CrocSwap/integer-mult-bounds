# Complete paired-transvection neighborhoods

Two endpoint charts can move together without paying their shared one-endpoint barrier. The following exact enumeration makes that coordinated search finite and substantially smaller while preserving every possible changed pair.

## Theorem

Let U,V be Lagrangians in a 2n-dimensional symplectic space over F₂, let I=U∩V have dimension k, and put r=n−k. For every coset of I choose a representative a₀. Omit the zero coset. If a₀ is orthogonal to I, retain the single axis a₀. Otherwise choose i₀ in I with ω(a₀,i₀)=1 and retain the two axes a₀ and a₀+i₀.

These axes produce every nontrivial pair

    (T_a U, T_a V)

exactly once. Their number is

    2^(n+r+1) − 2^(2r) − 1.

In particular it is 1,022 at n=9,r=0 and 2,043 at n=9,r=1. For a mapped edge S, replace V by S inverse V and apply the transported axis S a at its physical second endpoint.

**Proof.** The single-Lagrangian equivalence from COMPLETE-NEIGHBORS.md says that two nonfixed axes inducing the same changed Lagrangian differ by a vector in U∩a⊥. Applying this to both endpoints shows that their simultaneous equivalence classes are a+(I∩a⊥). The statement also holds when one endpoint is fixed: the axes fixing U lie in U, so equality of the other changed Lagrangian again forces their difference into I∩a⊥. Axes in I fix both endpoints and form the one trivial class.

On a fixed coset a₀+I, the functional i↦ω(a₀,i) is constant under changing its representative, because I is isotropic. If it is zero, the full coset is one class. If it is nonzero, its kernel has codimension one in I, and a₀ and a₀+i₀ represent its two classes. Thus the stated enumeration is complete and has no duplicate changed pair.

There are 2^(2n−k)=2^(n+r) cosets in total. Exactly |I⊥/I|=2^(2n−2k)=2^(2r) of them are orthogonal to I. Each of those contributes one class, and every other coset contributes two. Removing the trivial class gives the formula.

For a symplectic map S, the identity S T_a S inverse=T_(S a) shows that transporting the second axis preserves the shared mapped distance. Other incident edges must still be fully priced. In particular a two-node gain cannot be computed by subtracting only one shared edge if parallel internal edges have different native maps. The discovery implementation separately prices every internal edge that is not exactly coherent with the chosen transport and validates the resulting complete rank histogram.

## Exact positive replay

paired_test.py is self-contained and uses only Python's standard library. It compares the complete pair of transformed subspaces from every axis against the proposed representative set for every ordered pair of Lagrangians at n=1,2,3. It also checks 128 deterministic pairs at n=4. These controls establish equality of the actual finite neighbor sets, rather than only their cardinalities. The theorem itself is all-dimensional and is proved above.

    python3 -I -O -B paired_test.py --expected PAIRED-EXPECTED.json

This is a constructive complete local search algorithm. It establishes no new κ by itself, no globally optimal chart assignment, and no phase-free substitution for an actual supplier. A successful geometry candidate must use the saved transported axes in the literal phase-aware physical chart compiler.

## Relation to the current project

The existing native chart/contact and Clifford normal-form work supplies the application and cost model. This note applies elementary symplectic geometry to enumerate the exact search neighborhoods efficiently; it is not a claim of priority for finite polar-space geometry. The shared Gaussian/Word RAM supplier, arbitrary-input endpoint and paid-rank dependencies remain attributed to their retained source authors. No result of an exhausted local family is presented as a universal obstruction.
