# Exact dyadic Clifford transitions with one paid rank-d Gaussian

For a fixed b-bit literal dyadic Clifford U, let Z denote the computational Z Lagrangian and let

    d = dim(Z + U Z U⁻¹) − b.

There is a constructive factorization U = F⁻¹ J_D⁻¹ G, where F and G are monomial Cliffords, D is a set of d bit positions, and J_D = S_D C_D S_D. Here C_D is the product of the d commuting Gaussian letters C_j = ((1+i)I+(1−i)X_j)/2. Hence J_D is the dyadic scaled Walsh operator, not a normalized Hadamard with a discarded square-root/global phase. The factorization uses one paid rank-d Gaussian call when d > 0, and no paid call when d = 0. Equivalently it uses d elementary rank-1 letters if grouping is unavailable. These are distinct invoices; the admitted selected-block Gaussian interface permits the rank-d grouping.

This is a constructive specialization of standard Clifford/Bruhat normal forms, not a newly discovered quantum synthesis theorem. Credit [Bravyi and Maslov, 2021](https://arxiv.org/abs/2003.09412), especially Theorem 1 and its Hadamard-free construction, and the earlier Maslov–Roetteler Bruhat synthesis. The point needed here is preservation of actual dyadic scalar phase, arbitrary spectators, the all-width tensor semantics, and the native paid-rank invoice. The retained project already contains Clifford/frame normal forms and phase-cell fusion; no exhaustive novelty claim is made.

## Construction and proof

Represent a Pauli by i^p X^x Z^z, with x,z binary b-vectors. Let L be the Lagrangian spanned by the images of the b Z generators under U. Its X projection has dimension d. Extend a basis of that projection to a basis of the full binary space, and invert the resulting basis matrix to obtain R. The address permutation P_R sends the projected space to the first d coordinate directions.

Now L ∩ Z consists of every Z vector supported on the last b−d coordinates: isotropy forces its first d coordinates to vanish, and both spaces have dimension b−d. For each first coordinate vector e_j choose a vector (e_j,z_j) in the transformed L. Its last b−d Z coordinates can be changed arbitrarily using L ∩ Z. Let K have columns consisting of the first d coordinates of z_j. Isotropy gives K = Kᵀ. A diagonal Clifford with phase

    i^(Σ_j K_jj x_j + 2 Σ_{j<k} K_jk x_j x_k)

has symplectic shear (x,z) ↦ (x,z+Kx). Therefore F = D_K P_R sends L to span(X_1,…,X_d,Z_(d+1),…,Z_b). J_D exchanges those X and Z axes at the symplectic level. Consequently G = J_D F U preserves Z and is monomial.

There is no missing absolute-phase step. A Clifford preserving Z has an affine address map x ↦ Ax+b and a phase polynomial φ(x) over Z/4, whose quadratic cross-coefficients are even. The algorithm obtains A and b from its Pauli tableau, and φ’s linear and quadratic coefficients from the signed X images. It applies the actual literal word J_D F U to the zero basis state to recover the constant phase. A monomial unitary built from the specified dyadic letters has its nonzero entry in {1,i,−1,−i}: a Gaussian dyadic rational of norm 1 is such a unit, by the unique factorization of Gaussian integers and the fact that 2 is associated to (1+i)². The recovered constant phase is retained explicitly. Equality of all signed Pauli images together with one exact nonzero amplitude proves equality of the full operators: their quotient commutes with every X and Z and hence is a scalar, which the amplitude fixes.

The inverse J_D⁻¹ has the same paid bill as J_D because C_j² = X_j and C_j⁻¹ = X_j C_j. Every remaining gate is an affine address permutation or a Z/4 linear/even-quadratic phase, with no unknown Gaussian decoder.

## Literal all-width lifting

For every positive integer f, tensorize each base letter separately. Functoriality gives

    U^⊗f = (F^⊗f)⁻¹ (J_D^⊗f)⁻¹ G^⊗f.

The d selected bit blocks merge into C^⊗(df), one admitted rank-d call on all spectators. Arbitrary spectator coordinates are retained; no input is initialized to zero, measured, discarded or used as a clean catalyst. If the base global phase is i^a, its lifted phase is i^(af), not i^a. The compiler must not replace a sum P_f + 2 Q_f by (P + 2Q)^⊗f. This theorem applies to actual literal Clifford words and their tensor powers only.

The same construction gives an explicit chosen chart for any specified binary Lagrangian L: B_L = F⁻¹ J_D⁻¹ has B_L Z B_L⁻¹ = L. The `chart_from_lagrangian` function emits that literal word without assuming an orthonormal basis for the projected subspace. It does not identify B_L with an older chart merely because they share L.

For a transition between newly assigned charts, first specify the full literal transition word, including scalar phases and any affine translation, and feed that word to the compiler. A binary Lagrangian label by itself is not a complete physical chart. Rank distances may guide discovery but do not certify the emitted operator without this binding.

## Physical chart convention for a contact graph

Let A_v map logical data at node v to stored physical data. Its searched Lagrangian must be the inverse image L_v = A_v⁻¹ Z. If a logical edge carries a monomial address/phase map M from a to b, its physical transition is A_b M A_a⁻¹. Symplectic invariance gives its paid grade

    d(Z, A_b M A_a⁻¹ Z) = d(L_b, M L_a),

where d(L,L′) = dim(L+L′)−b. A search update L_v ← T_p L_v by a Pauli transvection is realized by the RIGHT chart update A_v ← A_v C_p⁻¹, retaining its normalized dyadic phase. Using a left update would generally change a different Lagrangian and invalidate the edge invoice.

The factory above emits B_L with B_L Z = L, so its inverse is the physical chart A for this convention. Source canonical Gaussian charts can obscure the distinction because their forward and inverse symplectic actions happen to agree; arbitrary newly composed charts do not. Fixed boundary/main/owner charts retain their original actual operator unless an explicit phase-correct free bridge is supplied.

## Sufficient chronological gauge substitution

Take an explicitly specified finite, ownership-typed source program whose logical bank operations and endpoint theorem have already been proved for arbitrary independent inputs. Give every scalar contact one common literal chart A_v for all participating persistent roles. Maintain the invariant that a role’s stored array equals A_v times its current logical array. Before its next contact, apply the exact compiled transition between its current chart and the contact chart, including any intervening logical monomial M. At the contact, a bank update y ← y + a x is valid without a query because A_v(y+a x) = A_v y + a A_v x. Copy and scalar multiplication have the same argument. Clear is valid only on an explicitly owned role; A_v 0 = 0 does not authorize clearing a borrowed input. Unitary transitions preserve all stored information and have explicit inverses.

Induction over the chronological instruction list proves that this transformed physical program has the same logical execution, including every helper’s arbitrary logical initial value. Freezing main and borrowed-owner endpoint operators therefore preserves their exact physical ABI. If the source endpoint theorem says a helper’s logical value is unchanged and independent of all other inputs, its new physical map is A_exit A_entry⁻¹ on that helper alone. Compile that endpoint map by the theorem above. The two free factors provide explicit independent input/output adapters around its rank-d Gaussian, and their costs are included in the free-pass bill. A rank-d endpoint is productive only when d > 0; an invertible but monomial endpoint does not contribute a nonzero Gaussian job.

This supplies a sufficient constructive assembly for arbitrary specified literal charts. It does not certify a proposed graph by its scalar objective alone: actual chart phases, the ownership-typed instruction correspondence, all frozen endpoints, every paid edge and every productive endpoint must be bound to the source. A changed mixed inventory still needs its complete critical-root, mirror, uniform compiler and native caller checks before it implies an improved κ.

## Native implementation and precision

For the application b = 9, every free base letter acts on one of 512 local address digits and contributes a local phase modulo 4. Store its fixed 512-entry address/phase table. Enumerate the f-digit addresses with a base-512 odometer, maintaining the transformed address and the sum of local phases. When a digit changes, update only its output-address block and its phase contribution. Across V = 512^f entries the total number of digit updates is less than 512V/511, after O(f) setup. Thus each free letter costs O(V+f) native Word RAM operations, without a POPCOUNT instruction. This reuses the project’s retained base-digit monomial odometer technique.

All addresses, shifted blocks and table indices must fit the retained O(1)-word address representation; the caller chooses w = C log n sufficiently large for its polynomial address horizon. The O(f) digit/descriptive storage is owned, initialized and cleared. For an in-place affine permutation, Gauss–Jordan factors its 9×9 linear map into at most 9 swaps and 72 row-XORs, each an involution. Each digitwise lifted elementary map can be applied by swapping an address pair only at its smaller address, using one temporary entry and a single O(V) scan. The address map itself uses a fixed number of XOR/shift/mask operations on nine bitplanes. The affine translation is another involution. There are exactly two GL-level maps in this construction, in F and G. Counting their at most 162 elementary passes plus all phase, translation and inverse-J passes gives fewer than 260 elementary free passes per transition. This bound is independent of the length of the discovery word. No additional independent input bank is introduced. Fixed offline compilation costs and these finite pass constants must remain in source-uniformity/funding bounds rather than silently set to one.

The free adapters have norm 1 and apply only exact permutations and powers of i. They introduce no rounding amplification or coefficient denominator. Precision and recursive Gaussian-call errors remain governed by the inherited paid Gaussian contract and number of calls. The Python Fraction implementation is an offline exact compiler/verifier, not a unit-cost Word RAM implementation.

## Replay and limitations

Run `python -I -O -B clifford_compile.py --expected CLIFFORD-EXPECTED.json`. The receipt checks 75 words by 350 exact matrix columns, 28 independently replayed lifted columns at widths 2 and 3, a rank-2 grouping control, three actual 9-bit tableau-plus-absolute-phase cases, an explicit −I word with identity tableau, 20 explicit Lagrangian chart factories, 20 GL involution factorizations, 10 physical contact edges with 60 exact columns, four cases distinguishing the wrong chart orientation, and rejection of a changed global scalar. `--input word.json` accepts a JSON object with `n` and the sequential literal `gates`. `--chart lagrangian.json` accepts `n` and `lagrangian`, a list of packed binary X|Z vectors or [x,z] pairs, and emits an explicitly chosen literal chart. Gate conventions are documented in the source; a `turn` means (I−iP)/(1−i) for the positive Hermitian Pauli P, with its inverse selected by sign −1.

This compiler supplies the constructive changed-chart transition mechanism. It does not show that any proposed collection of new charts improves the complete paid profile, preserves the selected controller endpoints, satisfies the mixed-provider mirror inequalities, or produces a new κ. Those are separate source-bound checks.
