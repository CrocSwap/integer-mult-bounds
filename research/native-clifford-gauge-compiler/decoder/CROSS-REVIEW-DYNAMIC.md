# Independent review of the coordinated Clifford contact search

The transvection-distance formula and its current C++ implementation pass independent exact checks. This validates the local discovery tariff; it does not certify a completed supplier, a new κ, actual phase lowering, or the numerical/native compiler contract.

## Exact formula and proof

Let U,V be Lagrangians in a 2n-dimensional symplectic vector space over F₂. Put d(U,V)=n−dim(U∩V), and T_a(x)=x+ω(x,a)a for a nonzero axis a. If a lies in U, T_a fixes U and the distance change is zero. For a not in U:

- If a is in V, the change is zero.
- If a is not in U+V, the change is +1.
- Otherwise choose a=u+v with u in U and v in V. The change is −1 when ω(u,v)=1, and zero when ω(u,v)=0.

To prove this, set I=U∩V. First, a in V implies T_a V=V, so symplectic invariance gives d(T_a U,V)=d(U,V). Next I⊥=U+V. If a is outside U+V, the old intersection vectors fixed by T_a form I∩a⊥, of codimension one in I. No new intersection vector can arise: T_a x in V and ω(x,a)=1 would imply a=x+T_a x in U+V. The distance therefore increases by one.

If a=u+v is in U+V, every vector in I is orthogonal to a, so I survives. The decomposition is unique modulo replacing u,v by u+i,v+i with i in I, and ω(u,v)=ω(u,a) is unchanged. A new intersection vector outside I exists precisely when ω(u,a)=1: then T_a u=v. Conversely, any such new vector must be u+i for i in I, so its pairing with a has that same value. Thus the intersection dimension increases by one exactly when the quadratic pairing is one. This proves the stated formula without an assumption about a preferred basis or decomposition.

The former rule that always assigned −1 to a in (U+V) minus (U union V) is false. The exact exhaustive replay records 227,160 quadratic-zero cases exposing that error.

## The actual native map

For a nine-bit invertible coordinate map G, the source uses the symplectic lift

    S_G(x,z) = (Gx, G^(−T)(x+z)+Gx).

Let J(x,z)=(x,x+z). Then S_G=J diag(G,G^(−T)) J, so S_G is symplectic. The canonical frame Lagrangian is

    L_U={(x,z): x in U and x+z in U⊥}.

Consequently S_G L_U=L_(GU), including nonorthogonal coordinate maps G. This is the correct source chart convention; replacing the map by diag(G,G^(−T)) without the two J factors would use a different convention.

For an edge from a to b, the tariff is d(S_G U_a,U_b). A move at node a can pull its neighbor back by S_G inverse and use d(U_a,S_G inverse U_b); a move at b uses d(S_G U_a,U_b) directly. These are equal because S_G is symplectic. The C++ orientation matches this calculation.

## Code review and exact evidence

Reviewed source SHA-256 values:

- dynamic.cpp: 85c867037f70bc591bb8eae6062a34cc16958fe959ea5beed08dc252b1a0518d.
- prepare_dynamic.py: 41b9ddadf5abe0c5bfba18913da9e0a1557e5951e609a927e27ec9f4dd0724c0.

The decomposition stored by make_local carries the U component of each elimination row. Thus its recovered u satisfies a−u in V. Its call symp(u,axis) computes ω(u,v), not an arbitrary linear membership test. ann computes the ordinary binary annihilator, which is exactly what contains needs for membership. The current inverse routine uses a 64-bit augmented row: the highest used bit is 35, so the former 32-bit truncation is avoided. Reconstruction of inverse columns from the right half is correct.

The independent standard-library testformula.py checks every Lagrangian pair and every nonzero axis for n=1,2,3: respectively 27, 3,375, and 1,148,175 cases. It separately validates all 4,429 actual nine-dimensional Lagrangians and all 145 prepared native maps. Its deterministic mapped-edge test checks 79,360 axes on all 240 actual warp edges and 1,000 ordinary edges. The exact receipt is TRANSVECTION-EXPECTED.json.

A second test compiles a harness that includes the unchanged reviewed C++ source and directly calls its make_local, change, turn, basis and inverse functions. It passes 1,023,318 nonfixed-axis cases, with 128,259 fixed-U controls, and verifies both inverse compositions on all 145 prepared maps. This checks the literal implementation in addition to the independently implemented Python mathematics. The harness-only renamed-main warning does not affect the tested functions; the ordinary program has a real C++ main with the standard implicit return rule.

Portable package replay, from the package directory:

    python3 -I -O -B decoder/testformula.py --graph inputs/round3-contact-graph.txt
    c++ -std=c++20 -O2 decoder/cpp_formula_check.cpp -o cpp_formula_check
    ./cpp_formula_check decoder/SMALL-LAGRANGIANS.txt inputs/round3-contact-graph.txt

The packaged harness includes dynamic_neighbors.cpp, the complete-neighborhood derivative of the original reviewed dynamic.cpp. Its exact tariff and inverse routines are unchanged; the packaged discovery main has an explicit success return, avoiding a renamed-main harness warning. The historical source hashes above identify the reviewed campaign source, not a byte-identity claim about the packaged derivative.

The source graph SHA-256 is f802be993525ec7b944a2622c4fd47db76101d7a558ea449ece7254780f6efef. It contains 19,199 nodes and 35,046 constraints. No floating calculation is used in these formula checks.

## Acceptance boundary

The discovery objective still uses floating rank powers and floating stopping tolerances. A positive move ledger must be replayed from the pinned graph, with each exact rank and productive width recomputed and the complete paid/target moment certified with rigorous numerical bounds. Every changed chart additionally needs an actual phase-aware Bruhat/native lowering, arbitrary-input endpoint replay, owned-field checks, precision/guard funding and the full outer compiler. Local rank correctness does not discharge those obligations.

The C++ code already recomputes all incident ranks after every accepted move. This is a valuable independent guard against a mistaken tariff formula; it is not a substitute for replaying the final full supplier. Independent node gauges also require their actual fixed finite symplectic words and exact absolute phase. No assertion is made that the restricted searches prove optimality or an impossibility theorem.

Credit the retained PR #4610 contact word and native/helper lineage, PR #4690 chart convention, and the coordinating worker's current dynamic implementation. The elementary symplectic calculation is used as a checked discovery method, not claimed as a novel standalone mathematical result.

## Binding searched Lagrangians to physical chart words

For an actual physical chart A_v mapping logical data to stored data, the correct searched Lagrangian is L_v=A_v inverse Z. If a logical edge is M from a to b, the corresponding physical operator is

    A_b M A_a inverse.

Its paid Fourier rank is

    d(Z, A_b M A_a inverse Z)
      = d(A_b inverse Z, M A_a inverse Z)
      = d(L_b, M L_a).

This is exactly the mapped-distance objective used by the search. Canonical source Gaussian charts happen to have the same forward and inverse Z image, but a generic changed Clifford chart need not. Therefore a searched update L_v to T_a L_v must be realized by right multiplication A_v to A_v C_a inverse, where C_a is the actual phase-retaining Clifford lift of T_a. A left multiplication of A_v would generally bind a different Lagrangian and could invalidate the invoice despite correct abstract distance calculations.

The independent compiler review finds its pure dyadic Bruhat construction sound: the projected active block determines a symmetric shear, S C S supplies the scaled dyadic Walsh representative with its global phase, and the exact zero-column amplitude fixes the monomial scalar. The optimized compiler replay passes. The inverse-image convention above is an application requirement for the new chart emitter, not a defect in that standalone compiler theorem.
