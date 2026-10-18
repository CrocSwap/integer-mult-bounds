# Native response constructions with explicit dirt and complete local charges

This volume contains exactly 100 informal proved application theorems, N001–N100. They construct local native/helper rewrites, not a new numerical κ or an unconditional multiplication theorem. A named action is a concrete circuit transformation or finite algebraic output. Its compatibility with the complete supplier remains the root volume's global bridge; no missing native primitive is assumed free.

## Shared definitions and accounting

Unless a theorem explicitly changes the scalar domain, registers take values in the real dyadic ring R = Z[1/2]; N083 explicitly introduces the doubled-register complex extension. The same formulas act on finite vectors over these rings. All input registers, including helpers, are arbitrary dirty values. Distinct named register blocks are disjoint. An additive output means its old value is retained and the stated increment is added. A private work register may be cleared only when the contract explicitly permits it; it is zero again before release.

Primitive scalar charges count ADD/SUBTRACT between distinct registers, DOUBLE, HALF, NEGATE and CLEAR. For a nonzero real dyadic c = a/2^b in reduced form, with integer a and b ≥ 0, let A(c) be 1 for c = ±1 and otherwise 2L + 2 popcount(|a|) + 2b + 1, where L is the binary length of |a|. The operation t += c s has an implementation at this charge: initialize a private zero coefficient register, build |a|s by binary doubling and additions, halve b times, add or subtract it into t, then reverse the coefficient construction before release. Both lifecycle CLEAR operations act on zero. It preserves s and returns work to zero; N080 supplies the complete proof. Set A(0)=0 and A(M)=Σ A(M_ij) for a matrix between disjoint source and target blocks. Complex coefficients are lowered to their real/imaginary components in N083. These are conservative explicit scalar charges, not recursive rank charges. They count enumerated scalar coordinates; lifting a scalar circuit independently to a d-coordinate fibre multiplies its charges by d unless an explicitly charged native block implementation is supplied.

An elementary helper word G is a displayed finite word of reversible additions and permitted unit scales; |G| is its fully expanded scalar charge, and G⁻¹ is obtained by reversing and negating additions and inverting unit scales. A matrix inverse is never assumed a primitive: a theorem using one must supply its dyadic entries or an explicit elementary word. A specified native child or frame transition carries its actual positive-rank tariff H_r; composing a word carries the multiset of every such transition, including inverse cleanup. Logical scalar identities do not delete those charges. The entry-by-entry frame constructions in Chapter VII explain when rank transitions can actually merge.

**Frontier interfaces.** `A`, `B`, `compensation`, `cleanup`, `start_extra`, `helper_final`, `warps`, and `cut` refer to those exact fields of the inspected PR #2857 words. `LOCAL` means the normalized forward/dual programs and private-clear interface. `CHILD` means the actual positive-rank transition ledger. `SOURCE` means an explicitly stated changed source-consuming contract, not the old source-preserving ABI. The fixed-word packing optimum of PR #2863 is not optimized here.

The local proofs below are independent derivations. Source precedents are identified in the self-review: the actual PR #2857 matrix S, its C_new = C S orientation, arbitrary-dirt formal replay and fully charged cleanup were read; canonical transvection and recorder sources were inspected without treating source-only catalogue entries as fresh kernel certificates. The later-read PR #2776 already gives a literal all-size ordered unit-shear controller on 14 tapes; these local scalar words neither duplicate that physical claim nor claim to discharge its remaining carry, scaling and caller interfaces. Classical identities are not claimed as discoveries.

## I. Compensation and changed arbitrary-dirt interfaces

<a id="n001"></a>

### N001 — Dirty-middle product echo

**Theorem.** For dyadic matrices U and V of compatible sizes, the four updates h += Ux; y += Vh; h -= Ux; y -= Vh send (x,h,y) to (x,h,y+VUx). All blocks may start dirty. The scalar charge is 2A(U)+2A(V), with at most one reusable coefficient register.

**Proof.** Name the initial values x₀,h₀,y₀. The first two updates give h=h₀+Ux₀ and y=y₀+Vh₀+VUx₀. The third restores h₀ without reading y. The fourth subtracts precisely Vh₀. Thus the only remaining output increment is VUx₀, and both source blocks are exactly restored. Each displayed matrix addition is a collection of reversible additions between disjoint blocks, so its coefficient-work contract follows from the accounting definition; no dirty middle value is cleared. All four operations are charged, including the second read of Vh.

**Action/interface.** Replace an explicitly factored response product in `A`/`compensation` by this no-clean-middle circuit when its full charge is favorable. Dependencies: shared accounting. Status: classical identity, native-contract adaptation.

<a id="n002"></a>

### N002 — Correct orientation of transported compensation

**Theorem.** Suppose a linear native word has target increment Dx+Ch, non-target transformation M(x,h), and inverse non-target cleanup. Let S be an explicit helper-only elementary word of charge g. Prepending S and appending S⁻¹ after cleanup changes the helper dirt response to C S, leaves the x contribution D unchanged, and restores the original helper input. Its additional scalar charge is 2g; the new compensation is −C S h, costing A(C S).

**Proof.** The original forward word now receives (x,S h), so linearity gives target increment Dx+C S h. Its non-target outputs are M(x,S h). The old inverse cleanup returns (x,S h), since it inverts M on every input, not merely on zero helpers. The appended S⁻¹ therefore returns h. Subtracting C S h cancels the transformed dirt exactly. A right multiplication by S⁻¹ would instead cancel the response of a different input and is not justified. The two explicit basis words and every new compensation read appear in the stated charge.

**Action/interface.** Generate the exact `compensation` replacement after a changed `A` helper basis, as in the inspected quartet mechanism. Dependencies: accounting. Status: classical transport, explicit local application.

<a id="n003"></a>

### N003 — One sparse kernel direction removes a response source

**Theorem.** Let C=[c₁ … c_n] and let k=(1,k₂,…,k_n) satisfy Ck=0. The word h_j += k_j h₁ for j=2,…,n has matrix S, satisfies C S=[0,c₂,…,c_n], and is inverted by the same additions with negative coefficients. Its forward-plus-inverse charge is 2Σ_(j>1)A(k_j).

**Proof.** This word replaces the first column of the identity by k and leaves every other column unchanged: only h₁ controls updates and h₁ itself never changes. Therefore S e₁=k and S e_j=e_j for j>1. Multiplication by C gives the claimed columns. The inverse subtracts each k_j h₁, restoring every arbitrary dirty helper. Applying N002 makes the first compensation column literally zero; it does not assume the helper was initially zero. No inverse of k_j is required, so dyadic compilation is available for every stated coefficient. Frame costs of the new word remain explicit CHILD charges.

**Action/interface.** Turn a verified sparse compensation-kernel vector into an actual `A`/`cleanup` basis word and delete its now-zero compensation source. Dependencies: N002. Status: adaptation.

<a id="n004"></a>

### N004 — Incrementally absorb a newly dependent helper

**Theorem.** Suppose a response bank already has columns C and one additional column c=C a, with a explicit and dyadic. The helper change h_old -= a z, leaving the new helper z fixed, changes the combined response [C,c] to [C,0]. Forward and inverse changes cost 2A(a).

**Proof.** Substitute h_old−a z for the old helper vector in C h_old+c z. The result is C h_old+(c−C a)z=C h_old. The new source z is not overwritten or cleared. The inverse adds a z back, so all helper inputs are restored after the corresponding inverse native cleanup. Every coefficient of a is used once in the forward change and once in the inverse; there are no hidden solves at runtime. The relation c=C a is a finite matrix equality whose entries can be checked directly before construction. This appends one helper without rebuilding an entire existing basis.

**Action/interface.** Extend an established shared-kernel chart to a new dependent `compensation` column. Dependencies: N002. Status: constructive adaptation.

<a id="n005"></a>

### N005 — Rank-one response bank with one shared aggregate

**Theorem.** If C=u vᵀ with explicit dyadic u,v, then y += Ch can be implemented with one private scalar aggregate t, charge 2A(vᵀ)+A(u)+2 CLEAR, and exact restoration of h and t=0 on release.

**Proof.** Clear t, add vᵀh into it, update y by u t, subtract vᵀh, and clear the already-zero t. During the middle update t equals vᵀh, hence the target increment is u(vᵀh)=Ch. The h registers are read-only. Subtracting the same linear form returns t to zero for every original h, including dirty inputs; the initial clear is legal only because t is declared private. Each coefficient read, inverse read, target fanout and both lifecycle clears is charged. This is a concrete aggregate circuit rather than treating a rank-one matrix as a free primitive.

**Action/interface.** Share compensation columns with a common target vector across a complete invocation. Dependencies: accounting. Status: classical factorization with paid local realization.

<a id="n006"></a>

### N006 — Collect response reads across a known helper trajectory

**Theorem.** Let explicit helper words J₁,…,J_s act independently of y, and let a read C_i h occur after prefix P_i=J_i…J₁. All those reads can be replaced by the single initial read C_total h, where C_total=Σ_i C_i P_i, without changing final helpers or target. The read charge becomes A(C_total); the helper-word charge is unchanged.

**Proof.** At the i-th read the helper value is P_i h₀, so its contribution is C_i P_i h₀. Additive target updates commute because none of the J_i reads or changes y, and no intervening operation observes y in this contract. Summing their contributions gives C_total h₀. Performing that read at entry therefore yields exactly the same final y and the same product P_s h₀. Each P_i is the displayed finite matrix product, so C_total is computable offline; it is not replaced by Σ_i C_i unless all prefixes are identities. The replacement includes all nonzero entries of the collected matrix.

**Action/interface.** Move and share `compensation` reads only after accounting for actual helper prefixes in `A` or `B`. Dependencies: accounting. Status: adaptation.

<a id="n007"></a>

### N007 — Explicit quotient consumer erases a dirty response

**Theorem.** If a producer returns y=Lx+Ch and a supplied dyadic matrix R satisfies R C=0, a consumer can add R y to an arbitrary output z and obtain z += R Lx with charge A(R), without reading h. Neither y nor h is claimed restored by this consumer.

**Proof.** Matrix distributivity gives R y=R Lx+R C h=R Lx for every h. The stated circuit consists solely of additions from the disjoint y block into z and therefore preserves both source blocks while incrementing z. It is valid for dirty h because the vanished coefficient matrix is identically zero, not because h belongs to a promised subspace. The equality R C=0 is a directly checkable finite certificate. If the global caller needs the original y rather than only this quotient output, that requirement is outside this changed consumer contract and is not silently supplied.

**Action/interface.** Expose a source-consuming quotient output before paying standalone target compensation. Dependencies: accounting. Status: classical annihilator applied to SOURCE.

<a id="n008"></a>

### N008 — Fuse a residual correction into a known consumer

**Theorem.** For a producer y=Lx+Ch and a desired consumer increment D Lx, the two explicit reads z += D y; z -= D C h implement that increment with charge A(D)+A(D C), preserving y and h.

**Proof.** The first read contributes D Lx+D C h. The second subtracts exactly the latter term using the original helper coordinates. No inverse of C or D is used. Thus this works even when C has full column rank or D C is nonzero, unlike an annihilating quotient. Both reads are executed into the same additive target z, so its original value is retained. The circuit offers a finite changed boundary: the consumer accepts the producer's uncorrected y and the still-live h. It cannot be used after h has changed unless the known transformed coordinates are included, as in N010. Its cost explicitly pays the carried correction.

**Action/interface.** Replace separate producer correction and consumer multiplication by the composed `SOURCE` read D C. Dependencies: accounting. Status: adaptation.

<a id="n009"></a>

### N009 — Disjoint kernel rewrites compose without cross terms

**Theorem.** Partition h into blocks h^(j). Suppose each explicit S_j acts only within its own block, and the forward helper change is their direct sum S. Then C S is obtained by transforming each column block separately, all S_j commute, and forward/inverse scalar charges are Σ_j 2|S_j|. Any zeroed response columns remain zero in the combined rewrite.

**Proof.** A coordinate in block j is untouched by every S_i with i≠j. Applying two such maps in either order therefore gives identical coordinates, proving commutation. Matrix multiplication by the block-diagonal S multiplies C's j-th column block by S_j and cannot add another block's columns to it. The inverse is block-diagonal with S_j⁻¹; executing all inverse words restores every dirty helper. Scalar charges add because the displayed words have disjoint roles, even if their target response supports overlap. Only the column-bank disjointness is needed; disjoint target supports are a sufficient stronger condition but are not assumed here.

**Action/interface.** Combine independently proved quartet kernel edits before generating one complete `compensation` and inverse `cleanup`. Dependencies: N002. Status: adaptation of direct-sum algebra.

<a id="n010"></a>

### N010 — Defer correction through a fully known helper change

**Theorem.** Suppose the available helper output is h'=J h for an explicit invertible elementary word J. A dirt response C h can be canceled at that later boundary by subtracting (C J⁻¹)h'. The read costs A(C J⁻¹); returning the original helper ABI costs the explicit inverse word |J| if it has not already been applied.

**Proof.** Since J⁻¹h'=h, the later read equals C h on every original helper vector. Thus it removes exactly the old response even when J mixes several dirty helpers. The inverse entries are available from the displayed inverse word, so no division oracle is assumed. If h' is accepted as the new boundary, no restoration is asserted. If the old helper ABI is required, applying J⁻¹ restores it and is charged. This separates two valid contracts rather than counting a changed basis as a free return to the old one. Any new nonzero entries in C J⁻¹ are included in the read charge.

**Action/interface.** Retiming `compensation` past a known `B` helper change, with an honest transformed-helper or restored-helper boundary. Dependencies: N002. Status: adaptation.

## II. Constructive helper coordinates and reusable kernels

<a id="n011"></a>

### N011 — Nilpotent kernel stabilizer with a paid implementation

**Theorem.** Let C u=0 and vᵀu=0 for explicit dyadic vectors. Then S=I+u vᵀ is invertible with inverse I−u vᵀ and C S=C. It can be applied to arbitrary dirty h using one cleared aggregate t at charge 2A(vᵀ)+A(u)+2 CLEAR.

**Proof.** The square of u vᵀ is u(vᵀu)vᵀ=0, so multiplying the two displayed matrices gives I in both orders. Also C S=C+(Cu)vᵀ=C. To implement S, compute t=vᵀh, add u t to h, then subtract vᵀh from t. After the update the new aggregate is vᵀh+(vᵀu)t=t, so this subtraction clears t exactly; the lifecycle clear charges are explicit. The helper change can therefore alter internal coordinates without changing the compensation matrix. Its inverse uses −u and the same construction. This supplies an actual sparse stabilizer word rather than inferring physical freeness from invariance.

**Action/interface.** Search cheap kernel stabilizers that alter `start_extra` geometry while leaving `compensation` unchanged. Dependencies: N005. Status: constructive adaptation.

<a id="n012"></a>

### N012 — One helper chart serving several response banks

**Theorem.** Given dyadic response matrices C₁,…,C_s on the same helpers, a kernel vector of their vertically stacked matrix is a common kernel vector. Applying the explicit N003 word to a unit-pivot stacked kernel removes its pivot source from every bank, at the same helper-word charge, while paying every remaining bank's transformed reads.

**Proof.** Stacking means that the product of the stacked matrix with k is the vertical list of C_i k. It vanishes exactly when every listed product vanishes. N003 constructs a single invertible helper word S from this k. Its pivot column is k, hence every C_i S has zero in that position. The helper word is executed once because all banks see the same changed input h; separate compensation reads then cancel each bank's actual C_i S response. Inverse cleanup executes S⁻¹ once. This avoids charging one basis change per receiver but does not identify their distinct target additions or erase any nonzero residual column.

**Action/interface.** Build a common `A` chart for several target/centre response ledgers instead of independently incompatible rewrites. Dependencies: N002–N003. Status: adaptation.

<a id="n013"></a>

### N013 — Global response compression with explicitly certified pivots

**Theorem.** Let C have independent columns B and suppose every other column is B a_j, with all a_j explicitly dyadic. Form A from these coefficient columns. The single block word h_B -= A h_rest changes C to [B,0]; its complete forward/inverse charge is 2A(A). The coefficients may be obtained by elimination on a supplied unit-pivot row minor of B.

**Proof.** The new response is B(h_B−A h_rest)+B A h_rest=B h_B. Every rest helper is unchanged, so all updates into basis helpers commute; subtracting them is inverted by adding them back. To obtain a_j, restrict c_j=B a_j to the chosen square row minor and solve it by the stated unit pivots. The solution is dyadic because each pivot inverse is dyadic; substitution into all rows verifies the full column equality before the word is accepted. The inverse cleanup therefore restores every source, not only the chosen row minor. This gives a complete executable chart with a finite coefficient certificate.

**Action/interface.** Compress an actual multi-column `compensation` matrix using its checked dyadic column basis. Dependencies: N004. Status: constructive Gaussian application.

<a id="n014"></a>

### N014 — Kernel extraction that fixes protected helpers pointwise

**Theorem.** Split helpers as (p,e), where p must never change. If C=[C_p,C_e] and C_e S_e=[B,0] for an explicit editable-helper word S_e, then diag(I,S_e) yields response [C_p,B,0], fixes p at every intermediate gate, and costs exactly the editable word and its inverse.

**Proof.** Every gate of S_e has both source and target in e, so it cannot modify a protected coordinate at any prefix. Multiplying the block response matrix by diag(I,S_e) gives the displayed response. The inverse word also acts only on e and restores its arbitrary input after native cleanup. Thus protection is stronger than an endpoint coincidence: it holds during the entire change of basis. All p-dependent reads remain in C_p and must still be paid. A full kernel of [C_p,C_e] that mixed p would not establish this contract; the construction uses only a verified kernel chart internal to e.

**Action/interface.** Apply response compression when some `A` helpers are source partners with a fixed input ABI. Dependencies: N013. Status: adaptation.

<a id="n015"></a>

### N015 — Integer two-column compression without dividing a runtime value

**Theorem.** If two response columns are a u and b u for integers a,b not both zero, Euclid's algorithm supplies an integer unimodular helper word taking their response to [g u,0], where g=gcd(a,b)>0. If its quotients are q_i, one implementation uses at most Σ_i(A(q_i)+4)+2 scalar primitives forward; restoring helpers pays the inverse word too.

**Proof.** Replace the larger coefficient by its remainder after subtracting q times the smaller column, then exchange columns. A column operation col_i ← col_i − q col_j is right multiplication by E_(j,i)(−q), so its helper gate is h_j ← h_j − q h_i, with transposed indices. Record the whole right product S of column operations and emit those helper factors in reverse chronological order, so their complete map is S. Column swaps give ordinary helper swaps. A swap is three additions and one negation, so each Euclidean step has the displayed bound. Signs can be normalized with at most two negations. If an initial exchange is needed, record it as a quotient-zero Euclidean step, including its swap charge. The terminating coefficient pair is (g,0); no register is divided by g. Each intermediate operation has determinant ±1 and an explicit integer inverse, so reversing the sequence restores arbitrary dirty helpers. Thus the construction remains in the dyadic compiler even when g is odd.

**Action/interface.** Compress proportional integer `compensation` columns without introducing an unavailable odd-denominator scale. Dependencies: accounting. Status: classical Euclid with native charges.

<a id="n016"></a>

### N016 — An annihilating polynomial yields a paid Krylov kernel

**Theorem.** Suppose response columns are c,Tc,…,T^d c and explicit dyadic coefficients satisfy (T^d+Σ_(j<d)a_jT^j)c=0. Then the helper word h_j += a_j h_d for j<d removes the last response column, at forward/inverse charge 2Σ_(j<d)A(a_j).

**Proof.** The word adds to column d the combination Σ_(j<d)a_j T^j c, leaving all other response columns unchanged. The declared polynomial identity makes the resulting column zero. All controls are h_d, which the word does not modify, so the inverse subtracts the same coefficients and restores every helper. Powers here are powers of the same actual operator T; the argument does not commute unrelated warp symbols. The polynomial identity can be checked on the complete finite response columns before compilation. Its coefficients and both helper-word directions are charged; a minimal-polynomial name alone supplies neither the identity nor the runtime word.

**Action/interface.** Exploit repeated single-warp response orbits in `A`/`warps` with a verified annihilator. Dependencies: N003's construction with the pivot moved last. Status: adaptation.

<a id="n017"></a>

### N017 — Fundamental-cycle compensation elimination

**Theorem.** Let C be the signed vertex-edge incidence matrix of a finite directed graph, with response columns indexed by edges. Choose a spanning forest. For each nonforest edge, its fundamental cycle gives an integer kernel vector with coefficient 1 on that edge. Updating only forest helpers by the signed nonforest helper contributions removes all nonforest response columns; forward/inverse charge is twice the total forest-path length.

**Proof.** Along a directed path, incidence columns telescope to the difference of its endpoints, with signs adjusted when an edge is traversed backward. Adding the nonforest edge closes the cycle, so its signed incidence sum is zero. Distinct cycle updates use nonforest helpers only as controls and forest helpers only as targets. Therefore they commute even when their paths share forest edges. Each removes its own nonforest column and leaves the other nonforest columns unchanged as controls of the helper chart. Reversing all unit additions restores the arbitrary edge values. Every path contribution costs one addition each way.

**Action/interface.** Recognize incidence-like sparse receiver responses and remove entire cycle banks in `compensation`. Dependencies: N003 and N009's block reasoning. Status: classical graph kernel, charged application.

<a id="n018"></a>

### N018 — Block elimination removes a dense off-diagonal response

**Theorem.** For response C=[A,B;0,D], suppose explicit dyadic X satisfies A X=B. The helper change h₁ -= X h₂ changes C to [A,0;0,D], with charge 2A(X) including restoration.

**Proof.** Substitute (h₁−Xh₂,h₂). The first target block receives A h₁+(B−A X)h₂=A h₁. The second still receives D h₂. The first helper block is the only modified block, while all h₂ controls remain unchanged, so the inverse adds Xh₂. This construction never requires an inverse of the whole response matrix; X may be verified by direct multiplication even if A is rectangular. The resulting target reads are precisely the two diagonal blocks, each fully charged. If X was computed by a unit-pivot solve, its admissible dyadic coefficients are explicit in the witness.

**Action/interface.** Remove cross-bank compensation using an actual rectangular solve rather than a free Schur-complement label. Dependencies: N002. Status: constructive block elimination.

<a id="n019"></a>

### N019 — Reuse a helper kernel across known target charts

**Theorem.** If an explicit helper word S zeros specified columns of C, the same columns of D C S vanish for every known target matrix D. If a reversible target word realizes D and the old target ABI is restored, the added target-chart charge is 2|D|; a changed consumer that accepts D y instead pays its one stated chart application.

**Proof.** A zero column remains zero after left multiplication by any matrix, since D0=0. Consequently the helper chart S need not be rediscovered after the target coordinates change. The runtime distinction is important: executing a target basis word maps old y to D y; returning old coordinates requires its displayed inverse and is charged. If the consumer accepts the transformed target, the boundary explicitly changes and no inverse is asserted. Either contract is exact for arbitrary y and helper dirt because the zero-column statement is a matrix identity. Nonzero target columns remain fully present after multiplication by D.

**Action/interface.** Reuse verified quartet kernels across `cut`/consumer target bases with honest chart costs. Dependencies: N002. Status: adaptation.

<a id="n020"></a>

### N020 — Signed relabelling transports a kernel word without runtime swaps

**Theorem.** Let P be a signed permutation of helpers, R a signed permutation of targets, and C'=R C P. If S is an elementary addition word, S'=P⁻¹ S P has the same scalar charge, after renaming indices and signs, and C'S'=R(C S)P.

**Proof.** Conjugating an update h_i += c h_j by a signed permutation changes only its two indices and multiplies c by a sign. Distinct indices remain distinct, and A(−c)=A(c), so no runtime permutation is needed: emit the renamed update directly. Conjugating the whole product gives S'. Multiplying C' by S' cancels the adjacent P P⁻¹, yielding R(C S)P. Thus every known zero response direction transports to the corresponding relabelled coordinate, while the old inverse word transports by the same rule. Target relabelling is a source identity here, not an uncharged physical wire move.

**Action/interface.** Reuse a proved native kernel edit across the actual `base`/`extra` or symmetry-related source labels. Dependencies: N002. Status: classical conjugation with alphabet-preserving compilation.

## III. Fully charged structured response sharing

<a id="n021"></a>

### N021 — A certified low-rank factor becomes a restored-input circuit

**Theorem.** Given explicit dyadic matrices C=UV with inner dimension r, the additive response y += Ch has a circuit of charge 2A(V)+A(U)+2r CLEAR, using r private aggregate registers plus coefficient work, and returning all aggregates to zero.

**Proof.** Clear t, compute t += Vh, update y += Ut, then subtract Vh from t. The response equals U(Vh)=Ch by the supplied finite matrix identity. The h block is read-only and may be arbitrary dirty input. Since it has not changed, the subtraction clears t exactly. Each of the r aggregate registers is cleared at entry and release, even though the last clear is redundant mathematically. A factorization name does not provide this implementation: all entries of V, U, the inverse V read and private lifecycle are included in the charge. No recursive child is deleted solely from the rank bound.

**Action/interface.** Compile a concrete response factor into `compensation` with an honest r-register private contract. Dependencies: N005. Status: classical rank factoring, paid realization.

<a id="n022"></a>

### N022 — Streaming the same factor with one aggregate

**Theorem.** For the factorization in N021, one scalar aggregate suffices: process each rank-one term U_:j V_j: separately. The charge is Σ_j[2A(V_j:)+A(U_:j)+2 CLEAR], and the original helpers are restored exactly.

**Proof.** For term j, clear t, accumulate V_j:h, add U_:j t into y, then subtract V_j:h and release t at zero. This contributes precisely U_:jV_j:h. Repeating all r terms gives their sum UVh. Previous target increments do not affect any later aggregate because every aggregate reads only h, and h never changes. The same physical private scalar can therefore be reused after each proven zero return. Unlike a parallel factor circuit, the intermediate vector Vh is never simultaneously retained; the output contract and total coefficient charges remain explicit. This is a workspace tradeoff, not an assertion that private storage or clears are free.

**Action/interface.** Realize a large response factor under a one-aggregate `LOCAL` scratch budget. Dependencies: N021. Status: constructive streaming adaptation.

<a id="n023"></a>

### N023 — Share one analysis map across several target banks

**Theorem.** If C_i=U_i V for target banks i=1,…,s, all responses y_i += C_i h can share one computation of Vh. Their complete charge is 2A(V)+Σ_iA(U_i)+2r CLEAR, where r is the number of rows of V.

**Proof.** Clear a private vector t and compute Vh once. Each bank then reads the same fixed t and adds U_i t; these reads do not change t or h. After every bank has consumed it, subtract Vh and clear t on release. For each bank the increment is exactly U_iVh, and the argument holds jointly on all dirty inputs. The analysis cost is paid twice total rather than twice per bank. Every fanout remains paid through Σ_iA(U_i); merely sharing a row space does not make the output writes disappear. The construction requires the aggregate to remain live until the last read, which is its declared retention interval.

**Action/interface.** Share a common compensation analysis between multiple receiver groups inside one complete invocation. Dependencies: N021. Status: adaptation.

<a id="n024"></a>

### N024 — Keep an explicitly factored intermediate instead of multiplying it out

**Theorem.** If C=U W V with inner sizes r,s, a restored-input circuit costs 2A(V)+2A(W)+A(U)+2(r+s) CLEAR, using both intermediate vectors. This can replace the different explicit charge 2A(WV)+A(U)+2s CLEAR without assuming either is smaller.

**Proof.** Clear t∈R^r and q∈R^s. Compute t=Vh and q=Wt, add Uq into y, undo q by subtracting Wt, then undo t by subtracting Vh. The order matters: t is retained until q is cleared. At the target read, q=WVh, giving Ch. All source h values are unchanged. Thus a sparse W and sparse V remain separately compiled rather than being replaced by a potentially dense matrix product WV. Both intermediate lifetimes, both inverse computations and every clear are present in the bound. The choice between these two complete implementations is a finite comparison of actual coefficients.

**Action/interface.** Preserve a useful multi-level response DAG when flattening it would densify `compensation`. Dependencies: N021. Status: constructive circuit sharing.

<a id="n025"></a>

### N025 — Add a low-rank response correction to an existing supplier

**Theorem.** If a verified response circuit adds Ch and an explicit correction is U Vh, appending the N021 circuit realizes (C+UV)h, preserves the same helper input, and adds exactly its stated private space and scalar charge.

**Proof.** The first circuit leaves h unchanged by its contract. The appended circuit therefore sees the same h and adds UVh, so the total target increment is Ch+UVh. Its private work is disjoint from the earlier circuit's live registers and is released at zero. This establishes composition for arbitrary dirty inputs and does not require recomputing a new basis for the entire C+UV matrix. Conversely, a correction with negative U implements C−UV at the same charge because coefficient signs are compiled explicitly. The result is an additive endpoint identity; any new frame transition introduced by this appended read remains in its separate CHILD ledger.

**Action/interface.** Repair a changed kernel's small residual response without discarding an already checked native compensation circuit. Dependencies: N021. Status: low-rank update application.

<a id="n026"></a>

### N026 — Tree aggregation compiles a dense subtree response sparsely

**Theorem.** For a rooted forest with n vertices and c components, let C map node values to all rooted-subtree sums. The response y += Ch can be implemented in 2(n−c)+n unit additions, with no aggregate work and exact restoration of every dirty h.

**Proof.** Process nonroot vertices after all their descendants, adding each current h_v into its parent's helper. An induction in this postorder shows that when v is added, it already equals the sum of original values in its subtree. After all n−c edge updates, every h_v is its original subtree sum. Add each of the n resulting values to its own target coordinate. Reverse the n−c edge additions in exact reverse order to restore the original helper vector. The output is not read by this reversal, so its accumulated subtree sums remain. The circuit uses arbitrary original node values and contains no cleared helper or implicit graph primitive.

**Action/interface.** Replace an incidence-derived dense receiver response by a paid tree word and inverse. Dependencies: accounting. Status: classical tree accumulation, native application.

<a id="n027"></a>

### N027 — Diagonal-plus-rank-one compensation

**Theorem.** For C=diag(d)+u vᵀ, a restored-input response circuit costs Σ_j A(d_j)+2A(vᵀ)+A(u)+2 CLEAR and uses one aggregate, independently of how many off-diagonal entries of C are nonzero.

**Proof.** First add d_j h_j into y_j for every j; these reads preserve h. Then use N005 to add u(vᵀh). The two target increments sum to Ch entrywise, including diagonal entries that receive contributions from both parts. Because both stages are source-preserving, their order does not affect the correctness or the aggregate reset. This implementation does not mistakenly delete the diagonal work when the rank-one factor is introduced. For a dense nonzero u and v it replaces many separate off-diagonal coefficient reads by one shared analysis and one fanout, while every coefficient operation in those two maps remains charged.

**Action/interface.** Compile a response whose dense part is a shared mode plus independent local corrections. Dependencies: N005. Status: structured-matrix application.

<a id="n028"></a>

### N028 — Karatsuba response sharing with global uncomputation

**Theorem.** Let A(t) be a fixed dyadic polynomial with fewer than n=2^k coefficients. Multiplication of an arbitrary input polynomial X by A has a source-preserving additive response circuit. Take L_A(1)=A(A₀). If L_A(n) is the reversible forward straight-line charge retaining all intermediates, then L_A(n)≤L_A0(n/2)+L_A1(n/2)+L_(A0+A1)(n/2)+6n; global restoration costs 2L_A(n)+(2n−1)+2W CLEAR for W retained work registers.

**Proof.** Split both polynomials at n/2. Compute P₀=A₀X₀, P₁=A₁X₁ and P₂=(A₀+A₁)(X₀+X₁). The identity AX=P₀+t^(n/2)(P₂−P₀−P₁)+t^nP₁ follows by expansion. Building the variable half-sum uses n additions; forming the coefficient output from the three retained products uses at most 5n additions. Fixed coefficient sums are computed offline. Each forward instruction writes by additions into initialized private work. Copy the final coefficients additively to y, then reverse the entire forward word once, clearing all W registers. Charging uncomputation recursively sixfold would miss this retained-intermediate construction; the stated charge instead pays its full storage.

**Action/interface.** Replace an actual Toeplitz/convolution response block by a checked shared straight-line circuit. Dependencies: accounting. Status: classical Karatsuba with explicit dirty-source restoration.

<a id="n029"></a>

### N029 — Walsh-structured response with dyadic inverse cleanup

**Theorem.** For n=2^k, the unnormalized Walsh matrix W_n admits y += W_n h with charge at most 4n k+n scalar primitives, preserving arbitrary dirty h and using no aggregate registers.

**Proof.** Each butterfly (a,b)↦(a+b,a−b) is realized by a+=b; b*=−2; b+=a. NEGATE and DOUBLE implement the middle scale, so this costs four primitives. The k standard butterfly stages have n/2 pairs each, giving 2nk forward primitives. Induction on k establishes that their product is W_n: the last block combines W_(n/2)h_left and W_(n/2)h_right as their sum and difference. Add the n resulting coordinates into y, then execute the explicit inverse butterfly word, whose middle scale is −1/2 and also costs two primitives. This restores h for another 2nk. No normalized Hadamard or square-root coefficient is assumed.

**Action/interface.** Share an explicit ±1 receiver block using scalar butterflies, with every inverse and scale paid. Dependencies: accounting. Status: classical fast transform, native-language adaptation.

<a id="n030"></a>

### N030 — Horner evaluation of a known operator polynomial

**Theorem.** Let P be an explicit reversible n-register word of charge g and let C(P)=Σ_(j=0)^d a_jP^j. Then y += C(P)h has a restored-input circuit costing 2dg+2nΣ_jA(a_j)+n+2n CLEAR, with n private aggregate registers.

**Proof.** Starting at t=0, add a_d h. For j=d−1 down to 0, apply P to t and add a_j h. Induction on this loop gives t=Σ_j a_jP^j h at its end. Add t to y, then reverse the complete aggregate-building word, using P⁻¹ and negative coefficient additions; it returns t to zero because h has stayed unchanged. The n entry and n release clears and n target additions are charged separately. The matrices P^j are never multiplied out into a dense response table. This is valid for the one fixed operator P; it does not commute different native warps or assume their products have equal cost.

**Action/interface.** Share repeated-power response reads in a native `compensation`/`B` block. Dependencies: accounting. Status: classical Horner evaluation with explicit reversible boundary.

## IV. Repairs for genuinely noncommuting schedules

<a id="n031"></a>

### N031 — Fuse identical complete wrappers without commuting their interiors

**Theorem.** For an explicit reversible word W and any compatible words R₁,…,R_s, the product (W⁻¹R_sW)…(W⁻¹R₁W) equals W⁻¹(R_s…R₁)W. If W and W⁻¹ have charge g, this replaces 2s g wrapper charge by 2g while retaining every interior operation.

**Proof.** Between consecutive factors the literal adjacent subword W W⁻¹ is an identity on every input. Cancel these adjacent inverse words successively. No R_i is moved through another R_j or through W, so their possible noncommutation does not matter. The final forward and inverse W remain, and every R_i occurs in exactly its original relative order. The equality holds on dirty registers because W is invertible on its entire declared domain. A native use must retain the common wrapper state over the enlarged interval; the theorem supplies that changed retention contract, not an uncharged return after each R_i.

**Action/interface.** Fuse repeated exact entry/exit charts around a block of `A`/`B` reads, paying the retained chart lifetime. Dependencies: accounting. Status: group cancellation with a concrete cost saving.

<a id="n032"></a>

### N032 — Repair a source-target crossing by its ordered product

**Theorem.** Let E_ij(A) denote the block update v_i += A v_j, with i,j,k distinct. Then E_ij(A)E_jk(B)=E_jk(B)E_ij(A)E_ik(AB). The crossing repair costs A(AB) when emitted as an explicit dyadic matrix read; it is not free.

**Proof.** Multiply the block matrices I+e_ijA and I+e_jkB. Their only cross term is e_ik AB, because the shared middle index is j. On the right, the reversed pair has no cross term since k≠i; multiplying by I+e_ikAB contributes exactly the missing block and no further term. The order AB is forced: applying B to a source precedes A's use of that result. This argument remains valid for noncommuting block operators; it never replaces AB by BA. The resulting word has the same complete endpoint, including both modified intermediate blocks, on arbitrary inputs.

**Action/interface.** Move a native read across a write to its source only with its explicitly compiled path correction. Dependencies: accounting. Status: Steinberg-style schedule repair.

<a id="n033"></a>

### N033 — Topological rescheduling with read/write footprints

**Theorem.** Two finite scalar words P,Q commute if neither word writes a register read or written by the other. Repeated exchanges of such adjacent words preserve the complete dirty-input endpoint and exact scalar charge; they provide an explicit new legal schedule.

**Proof.** Every register read by P has the same value whether Q has run or not, because Q does not write it. Thus P computes the same changes to its write set in both orders. The same argument holds for Q, and their write sets are disjoint, so those final coordinate changes cannot overwrite each other. Coordinates outside both write sets are unchanged. This proves equality on every input, rather than only on a test subspace. Applying the argument after each adjacent exchange proves any sequence of legal exchanges correct. Since no gate is inserted or deleted, the scalar charge is identical; a changed frame ledger must be computed separately.

**Action/interface.** Construct alternate `A`/`B` schedules for shared entrance frames without silently commuting dependent gates. Dependencies: accounting. Status: classical dependence scheduling, local sufficient rule.

<a id="n034"></a>

### N034 — A balanced diamond creates an explicit zero dirt direction

**Theorem.** Given A,B,C,D with AC+BD=0, the word h₁+=Cz; h₂+=Dz; y+=Ah₁; y+=Bh₂; h₂-=Dz; h₁-=Cz adds Ah₁⁰+Bh₂⁰ to y and has zero z response. It restores both helpers and costs 2A(C)+2A(D)+A(A)+A(B).

**Proof.** Just before the target reads, h₁=h₁⁰+Cz and h₂=h₂⁰+Dz. Their combined contribution is Ah₁⁰+Bh₂⁰+(AC+BD)z. The last coefficient is the zero matrix by the explicit hypothesis. The final two updates restore h₂ and h₁ because z was never changed. The theorem neither declares the other two dirty responses zero nor removes their compensation costs; it isolates exactly the new z direction. All six operations are present in the charge. The balanced-path identity can be checked on finite matrices before modifying a larger native word.

**Action/interface.** Build new staged kernel schedules with compensating paths rather than requiring each individual read to be dirt-free. Dependencies: accounting. Status: constructive path cancellation.

<a id="n035"></a>

### N035 — Refactor opposing scalar shears through a permitted unit

**Theorem.** Let a,b be real dyadics and u=1+ab a dyadic unit ±2^k. Then the map (x,y)↦(u x+a y,b x+y) equals a lower shear b/u, followed in matrix factorization by diag(u,u⁻¹) and an upper shear a/u. Its factor word has charge A(b/u)+A(a/u)+2|k|+2·1_(u<0).

**Proof.** In matrix order the factorization is L(b/u) diag(u,u⁻¹) U(a/u). Multiplication gives top row (u,a) and bottom row (b,(ab+1)/u)=(b,1). The permitted-unit hypothesis ensures every scale and inverse is a finite sequence of DOUBLE/HALF and at most one NEGATE per coordinate. Thus no general division gate is hidden. Both shears have explicit dyadic coefficients and are charged. This is a different implementation of the complete opposing-shear map, not a claim that arbitrary swaps commute or that all such factorizations are cheaper.

**Action/interface.** Retiming a two-helper feedback block across a legal diagonal entrance chart. Dependencies: accounting. Status: paid Gaussian factorization.

<a id="n036"></a>

### N036 — Construct an explicit block-diagonal preconditioner from four shears

**Theorem.** Let P=(I+AB)⁻¹ have supplied dyadic entries. Then L(−BP) U(A) L(B) U(−PA) is diag(I+AB,I−BPA). This supplies an actual reversible word for both diagonal blocks together, with charge A(BP)+A(A)+A(B)+A(PA).

**Proof.** The middle product U(A)L(B) is [[I+AB,A],[B,I]]. Right multiplication by U(−PA) clears the upper-right block because (I+AB)P=I; its lower-right block becomes I−BPA. Left multiplication by L(−BP) clears the lower-left block because P(I+AB)=I, and leaves the lower-right block unchanged once the upper-right block is zero. Thus the stated diagonal map is implemented entirely by four explicit shears. Its inverse is their reverse signed word, so no separate primitive for the potentially dense diagonal blocks is assumed. This retains the noncommuting order of A,B and pays the products BP, PA as actual coefficient maps.

**Action/interface.** Generate a coupled native helper preconditioner when an explicit dyadic resolvent is available. Dependencies: N035's block idea, not its scalar unit assumption. Status: constructive Schur application.

<a id="n037"></a>

### N037 — Merge repeated reads on the same directed edge

**Theorem.** E_ij(A)E_ij(B)=E_ij(A+B) for i≠j, even for noncommuting coefficient operators A,B. An implementation may choose either the two original reads or the compiled summed read, paying min(A(A)+A(B),A(A+B)).

**Proof.** The cross term is e_ij e_ij AB=0 because j≠i. Therefore the product is I+e_ij(A+B), with no AB or BA contribution. Equivalently, both updates read the unchanged source v_j and add their outputs into v_i. The source remains the same between reads, which is the precise condition absent from a source-target crossing. Entrywise addition computes A+B offline; cancellations can remove entries, but the resulting coefficient compilation may also change binary costs, so the theorem uses the smaller complete implementation rather than assuming entry cancellation implies a particular saving. No other register or dirty coordinate changes.

**Action/interface.** Collect adjacent same-source/same-target compensation reads and choose a fully charged emitted word. Dependencies: accounting. Status: elementary nilpotent algebra, compiler application.

<a id="n038"></a>

### N038 — A feedback commutator with all residual blocks explicit

**Theorem.** For compatible square block maps A,B, the four-shear word U(A)L(B)U(−A)L(−B) equals [[I+AB+ABAB,−ABA],[BAB,I−BA]]. Its scalar charge is 2A(A)+2A(B).

**Proof.** First U(A)L(B)=[[I+AB,A],[B,I]]. Multiplying by U(−A) gives [[I+AB,−ABA],[B,I−BA]]. Multiplying this by L(−B) adds −B times the second block column to the first, giving the claimed four blocks. These products are ordered exactly as displayed; no relation between AB and BA is assumed. The formula is therefore a constructive feedback operator with a four-shear realization and an explicit inverse word. It cannot be treated as a pure off-diagonal correction, since all four residual blocks are retained. A larger native circuit may consume this full block interface instead of separately compiling its dense entries.

**Action/interface.** Use a known feedback word as a changed native block with complete residuals and cleanup, rather than dropping its noncentral terms. Dependencies: accounting. Status: explicit operator construction.

<a id="n039"></a>

### N039 — Series-parallel response circuits with recursive dirty echoes

**Theorem.** A finite expression built from dyadic matrix leaves by sum and compatible product has an additive source-preserving realization. A sum node costs the sum of its child charges; a product node admits the dirty-middle charge 2L_left+2L_right, with a middle block of the declared inner dimension.

**Proof.** A leaf is its explicit matrix-addition circuit. At a sum node, run both child circuits into the same additive target; their common source is restored by each contract, so the increments add. At a product node, apply the right child additively into arbitrary dirty middle h, the left child from h into y, then their inverses in the N001 order. The two h-dependent reads cancel and leave the ordered product. Each child word is reversible, so its inverse has the same expanded charge and returns its private work to zero. Structural induction proves the endpoint and stated recurrence for the whole finite expression, without an unpriced product oracle.

**Action/interface.** Compile explicit shared response expression trees into candidate native words with an a priori complete invoice. Dependencies: N001. Status: constructive algebraic-circuit composition.

<a id="n040"></a>

### N040 — Acyclic path sums with one triangular sweep and its inverse

**Theorem.** Let N be a strictly upper block-triangular dyadic matrix on n helper blocks. The solve h_i += Σ_(j>i)N_ij h_j, executed for i=n−1 down to 1, realizes (I−N)⁻¹h. Adding that transformed vector to y and reversing the sweep realizes y += (I−N)⁻¹h₀ at charge 2Σ_(i<j)A(N_ij)+dim(h) unit target additions.

**Proof.** At the update of row i, every h_j with j>i already has its solved value. Thus the final vector solves h=h₀+Nh coordinate by coordinate. Strict triangularity gives N^n=0, so I+N+…+N^(n−1) is its explicit inverse and the solution is unique. Add the solved values to the target, then reverse every elementary addition; this restores all original dirty helpers while retaining the target increment. The dense sum over all directed paths is therefore produced by one sparse edge sweep, not by separately reading every path product. No unspecified triangular-solve primitive is used.

**Action/interface.** Replace a verified acyclic response path table by a paid sparse staged word. Dependencies: accounting. Status: classical substitution with a restored native boundary.

## V. Exact input restoration and honest changed-source boundaries

<a id="n041"></a>

### N041 — Construct cleanup by reversing only the non-target word

**Theorem.** Consider a word whose target gates only add functions of non-target registers into y and never read y. Suppose its non-target gates form an explicit reversible word U of charge g. Appending U⁻¹ preserves the accumulated target output and restores every non-target input, at total non-target charge 2g plus all target reads.

**Proof.** Delete the target gates while following the non-target state: because none reads y, the remaining trajectory is exactly U on the original non-target vector. The target gates have recorded their increments into y but have not affected that trajectory. The appended inverse therefore returns every non-target register to its original value. It never touches y, so all recorded increments remain. Initialization and release clears are outside the reversible word and must be charged by their private-work contract. In particular a destructive CLEAR inside U cannot be inverted by this theorem. The construction applies to arbitrary helper values and yields a concrete inverse cleanup list.

**Action/interface.** Regenerate `cleanup` after a changed `A`/`B` word instead of assuming the old cleanup remains correct. Dependencies: accounting. Status: classical uncomputation, exact native rule.

<a id="n042"></a>

### N042 — Transpose and inverse-transpose a complete scalar response

**Theorem.** A work-free scalar word realizing the block shear (x,y)↦(x,y+Cx) yields explicit words for the transpose shear and its inverse transpose. For the transpose, reverse the gate order and transpose each elementary addition. For the inverse transpose, keep the original chronological gate order and inverse-transpose each addition, negating its coefficient. Expanded scalar charges are unchanged.

**Proof.** If the original product is G_s…G₁, its transpose is G₁ᵀ…G_sᵀ. The transpose of an addition with coefficient c from j to i is the addition with c from i to j. Thus the displayed reversed list realizes the transposed matrix, whose off-diagonal block is Cᵀ. The inverse transpose is G_s^(−T)…G₁^(−T), so its chronological order is the original order with each gate replaced by its inverse transpose. Addition coefficients change sign but their compilation charges do not. All other source/target coordinates follow the exact transposed block matrix, so no zero-helper assumption is needed. This theorem is scalar; transporting positive-rank native children requires their separate actual dual interface.

**Action/interface.** Produce an explicit `LOCAL` scalar dual before the native frame/phase audit. Dependencies: accounting. Status: classical transposition principle with a restricted valid alphabet.

<a id="n043"></a>

### N043 — A dyadic reflection with exact aggregate cleanup

**Theorem.** For an explicit real dyadic vector u with uᵀu=1, the reflection H=I−2u uᵀ is an involution and preserves the Euclidean norm. It has a one-aggregate implementation of charge 2A(uᵀ)+A(−2u)+2 CLEAR, even when h starts dirty.

**Proof.** Multiplication gives H²=I−4u uᵀ+4u(uᵀu)uᵀ=I, and symmetry gives HᵀH=I. For the circuit, compute t=uᵀh and replace h by h−2ut. The new inner product is uᵀh−2t=−t. Therefore adding uᵀh_new into the retained t clears it, unlike the subtract operation used in ordinary factor evaluation. This proves the exact scratch return as well as the endpoint. Norm preservation holds for the whole stated vector bank; it is not claimed for each separate physical family or charged as a rank-zero native warp without another proof.

**Action/interface.** Build an explicitly paid norm-preserving helper chart for N002 when its entries are dyadic. Dependencies: N005 accounting. Status: classical reflector with native cleanup detail.

<a id="n044"></a>

### N044 — Collision-free logical layers for a bipartite read block

**Theorem.** A response block with disjoint source and target banks and at most Δ nonzero entries incident to any register, with Δ ≥ 1, can be scheduled in at most 2Δ−1 layers of pairwise disjoint scalar reads, with exactly the original total coefficient charge.

**Proof.** Regard each nonzero read as an edge from its source to its target. Greedily color edges. An edge meets at most Δ−1 previously colored edges at either endpoint, hence at most 2Δ−2 forbidden colors; one of 2Δ−1 colors is available. Each color class has disjoint endpoints. Because targets never serve as sources in this block, all reads commute and retain the same output sum under the new ordering. The coloring therefore supplies an actual legal word partition, not merely a degree lower bound. Each coefficient is emitted once. These are logical layers; physical parallel execution or shared frame conversions require their separately stated interfaces.

**Action/interface.** Generate noncolliding native read batches for later entrance/retention construction. Dependencies: N033. Status: constructive greedy scheduling adaptation.

<a id="n045"></a>

### N045 — Balanced dirty aggregation with restored inputs

**Theorem.** For d ≥ 1 arbitrary dirty source registers, their sum can be added into y using 2(d−1)+1 unit additions, with every source restored and no aggregate bank. A balanced choice of pairings gives at most 2⌈log₂d⌉+1 logical addition layers.

**Proof.** Pair live partial sums, adding one register of each pair into the other, and retain the receiver as the representative of the union. Unpaired representatives pass to the next round. After at most ⌈log₂d⌉ rounds one representative contains the sum of all original sources; exactly d−1 additions were used, since each addition decreases the number of representatives by one. Add that representative to y. Reverse the recorded additions to restore every original source, including those temporarily overwritten by partial sums. Disjoint pairs form legal layers; the reverse has the same layer count. No source clear or assumed clean initial value occurs.

**Action/interface.** Replace a high-fan-in unit-coefficient compensation read by an explicit low-depth aggregate word. Dependencies: accounting. Status: classical reduction with complete dirty restoration.

<a id="n046"></a>

### N046 — Retain a helper chart as an explicit consumer boundary

**Theorem.** If a producer computes h'=S h by a known elementary word and adds R h' to y, a consumer accepting h' can omit S⁻¹ with exact endpoint (h',y+RSh) and charge |S|+A(R). A consumer requiring old h must instead pay the inverse |S|.

**Proof.** Applying S to h gives its declared transformed value on every input; the target read adds RSh. There is no further change to h, so h'=Sh is the precise retained state. Omitting the inverse does not somehow restore h; it changes the output contract to expose that state. Since S has an explicit inverse, a later source-preserving consumer may recover h at the stated charge, or a genuinely consuming consumer may operate directly on h'. Both alternatives are complete local endpoints. Thus the construction identifies exactly where a cleanup can be eliminated and exactly which changed boundary must absorb it.

**Action/interface.** Form a source-consuming `SOURCE` candidate instead of silently dropping `cleanup` from the old ABI. Dependencies: N041. Status: constructive boundary change.

<a id="n047"></a>

### N047 — Mutable-source shear with an explicit inverse

**Theorem.** Let M be an explicit reversible source word and L an explicit dyadic matrix. The map (x,y)↦(Mx,y+Lx) is implemented by first adding Lx and then running M. Its inverse is x←M⁻¹x followed by y←y−Lx. Alternatively, after running M first, read L M⁻¹x at charge A(L M⁻¹).

**Proof.** In the first implementation the target sees the original x, so its increment is Lx before the source becomes Mx. On inversion, M⁻¹ first returns that original source, allowing the exact negative read. In the second implementation the available source is x'=Mx, and L M⁻¹x'=Lx. Thus both programs realize the same complete mutable-source endpoint, including arbitrary old y. Every source restoration or later read is explicit; no caller is allowed to read Mx as if it were x. The choice compares two known coefficient maps rather than assuming source mutation is harmless.

**Action/interface.** Build a typed source-consuming preparation/consumer interface with a real inverse word. Dependencies: accounting. Status: constructive semidirect block action.

<a id="n048"></a>

### N048 — Telescope target corrections across source evolution

**Theorem.** For a known sequence x₀,…,x_s generated by reversible source words, target increments L(x_i−x_(i−1)) sum to L(x_s−x₀). If no intermediate target value is read, replace the 2s matrix reads by the two reads −Lx₀ and +Lx_s, preserving the complete source trajectory.

**Proof.** Expand the sum as Lx₁−Lx₀+Lx₂−Lx₁ through Lx_s−Lx_(s−1). Every interior term appears with both signs and cancels in the additive target group, leaving the stated endpoints. The source words never read y, so moving the target writes to entry and exit cannot change that trajectory. The old target value is retained throughout. Both remaining reads cost A(L), and every source word is still paid. If an intermediate y is observed or used as a control, the stated hypothesis fails; no schedule move is inferred in that case.

**Action/interface.** Fuse a chain of explicit correction differences in a mutable `SOURCE` schedule. Dependencies: N047. Status: telescoping with a complete execution boundary.

<a id="n049"></a>

### N049 — Omit cleanup only for an explicitly invariant consumer

**Theorem.** Suppose a producer's completed required data output is already correct, its helper output is S h, and the only remaining use of helpers is an explicit read z += R h with R S=R. The composition may read R(S h) directly and omit S⁻¹, at charge A(R) rather than |S⁻¹|+A(R); the helper bank is then consumed, not returned in the old ABI.

**Proof.** The consumer's required increment is R h. Its actual input is S h, but the finite identity R S=R gives R(S h)=R h for every dirty h. Therefore all observed data and consumer outputs agree with the cleanup-then-read program. The helper coordinates themselves need not agree, which is why they are explicitly discarded after this read and excluded from the returned interface. This is a sufficient composite construction with a specified consumer, not an assertion that arbitrary future uses are unaffected. Its saving is the concrete omitted inverse word, with all remaining reads still charged.

**Action/interface.** Match a changed helper chart to a verified final consumer before deleting its cleanup. Dependencies: N046. Status: observable-contract adaptation.

<a id="n050"></a>

### N050 — A Schur consumer removes dirt using the returned helper

**Theorem.** Suppose a producer returns y=y₀+Ax+Bh and h'=Cx+Dh, with explicit dyadic D⁻¹. The consumer y -= B D⁻¹h' gives y=y₀+(A−B D⁻¹C)x. It costs A(BD⁻¹) and retains h'. Returning old h additionally requires h←D⁻¹(h'−Cx), whose actual word and read must be paid.

**Proof.** Substitute h' into the correction: B D⁻¹h'=B D⁻¹Cx+B h. The B h term cancels exactly, leaving the displayed Schur response for arbitrary original h. The producer's source x is still available in this contract. If original helper restoration is requested, subtract Cx from h' and apply the supplied inverse D word, obtaining h. Thus the construction distinguishes a cheaper retained-helper consumer from a fully restored ABI, and computes the changed data map rather than pretending it remains A. Every inverse entry is explicit; no unspecified decoder is assumed.

**Action/interface.** Compose preparation and consumer so dirty response is canceled at a changed native boundary. Dependencies: N010 and N047. Status: constructive Schur-complement consumer.

## VI. Explicit block operators and small inverse problems

<a id="n051"></a>

### N051 — Two-sided response normalization with both charts charged

**Theorem.** Suppose explicit elementary words S,T satisfy T C S=D, where D has only a specified small active block. A native response can be evaluated in those coordinates by helper chart S and target chart T, with both forward/inverse chart costs 2|S|+2|T| plus A(D). The original target increment is C h and all original inputs are restored.

**Proof.** Apply S⁻¹ to h, so its value is S⁻¹h₀. Apply T to the dirty target y. Add D(S⁻¹h₀) into that target, then apply T⁻¹. The resulting value is y₀+T⁻¹D S⁻¹h₀=y₀+C h₀. Finally apply S to restore h. Both target charts act on its old dirty value and cancel exactly. The active block need not be called a free rank-r primitive: its actual coefficient reads cost A(D). All four chart directions remain in the invoice. This provides a complete evaluation when sparse certified charts genuinely beat the original dense response.

**Action/interface.** Evaluate a low-complexity normal form without forgetting target-basis restoration in `compensation`. Dependencies: N002 and N019. Status: paid normal-form construction.

<a id="n052"></a>

### N052 — Full block elimination with a checked Schur block

**Theorem.** Let M=[A,B;C,D] and let an explicit dyadic A⁻¹ be given. Define X=A⁻¹B, Y=CA⁻¹ and S=D−CA⁻¹B. Then L(−Y) M U(−X)=diag(A,S). The two off-diagonal chart words are explicit, costing A(X)+A(Y), and reversing them costs the same.

**Proof.** Right multiplication gives [A, B−AX; C,D−CX]=[A,0;C,S]. Left multiplication subtracts Y times the first block row from the second, giving [A,0;C−YA,S]=[A,0;0,S]. This calculation is valid with noncommuting matrix products in their displayed order. It constructs both charts from finite matrices whose entries can be checked directly. A native implementation must realize M through its known circuit or its entries, plus these chart words; the diagonal factors are not assumed to be free children. The identity supplies a concrete sparse-block boundary that a caller may consume or invert.

**Action/interface.** Jointly redesign preparation and consumer around an actual Schur response rather than pricing each cross block separately. Dependencies: N018. Status: classical block elimination with explicit local charges.

<a id="n053"></a>

### N053 — Low-rank inverse update as a finite response circuit

**Theorem.** Let A⁻¹ and W=(I+V A⁻¹U)⁻¹ be supplied dyadic matrices. Then (A+UV)⁻¹=A⁻¹−A⁻¹U W V A⁻¹. A source-preserving inverse response uses the shared intermediates A⁻¹x, V A⁻¹x and W V A⁻¹x, at charge 2A(A⁻¹)+2A(V)+2A(W)+A(A⁻¹U)+n+2(n+2r) CLEAR.

**Proof.** Multiply A+UV by the proposed inverse. The extra terms factor as U[I−W−(V A⁻¹U)W]V A⁻¹=0 because (I+V A⁻¹U)W=I. For the other product order the extra term is A⁻¹U[I−W−W(V A⁻¹U)]V, also zero because W(I+V A⁻¹U)=I. Thus both product orders give the identity. For the circuit, compute the three listed private intermediates, add the first to y, subtract A⁻¹U times the third, then reverse all three computations. Their sizes are n,r,r, explaining the lifecycle clears. The n target additions and every factor read are charged. The inverse hypotheses are explicit finite matrices, not unspecified recovery gadgets.

**Action/interface.** Compile a changed decoder/helper inverse from a small certified correction problem. Dependencies: N024. Status: Woodbury construction with native-language accounting.

<a id="n054"></a>

### N054 — A nilpotent inverse without any runtime division

**Theorem.** If an explicit dyadic K satisfies K^s=0 for an integer s ≥ 1, then (I−K)⁻¹=Σ_(j=0)^(s−1)K^j. Its additive response has charge 2(s−1)A(K)+s n target additions+2(s−1)n CLEAR, using the retained power chain as private work.

**Proof.** Multiplication of I−K by the finite sum telescopes to I−K^s=I on both sides. To evaluate it, take w₀=x and compute each w_j=K w_(j−1) into a separate cleared n-register block. Add all s vectors into y, then reverse the power-chain computations from j=s−1 down to 1. The source of each inverse computation is still retained at that point, so all private blocks return to zero. This pays two K applications per stored power and every target addition. No inverse coefficient, spectral decomposition or uncharged recursion is introduced.

**Action/interface.** Realize triangular/nilpotent correction inverses by a bounded explicit word. Dependencies: N024 and N040. Status: finite geometric series application.

<a id="n055"></a>

### N055 — Idempotent correction with an allowed scalar unit

**Theorem.** If P²=P and u=1+c is a dyadic unit, then (I+cP)⁻¹=I−(c/u)P. Therefore a supplied response circuit for P immediately gives an inverse response using the explicit coefficient −c/u and the identity read, with all coefficient compilation charged.

**Proof.** Multiply the two expressions. The coefficient of P is c−c/u−c²/u=c−c(1+c)/u=0; the remaining term is I. This proves both product orders because every term is a polynomial in P. The unit assumption makes c/u a dyadic scalar, so the inverse does not request an odd-denominator primitive. For a matrix-entry implementation, add x into y and add −(c/u)P x, costing n+A(−(c/u)P). An existing explicitly factored P circuit may instead be used with its complete scaled coefficient costs. Old x is preserved in either additive response.

**Action/interface.** Invert a known projector-like compensation update without a general matrix inversion at runtime. Dependencies: accounting. Status: classical polynomial inverse with permitted coefficients.

<a id="n056"></a>

### N056 — A square-zero full-bank chart with exact private return

**Theorem.** For an explicit dyadic K with K²=0, the invertible helper change h↦h+Kh has inverse I−K. It can be implemented at charge 2A(K)+n unit additions+2n CLEAR using one private n-vector.

**Proof.** Compute t=Kh into cleared work, then add t into h. Since K(h+t)=Kh+K²h=Kh=t, subtracting K times the new h from t clears that work exactly. The helper output is (I+K)h₀, on arbitrary input. The inverse matrix identity (I−K)(I+K)=I follows immediately from K²=0 and gives the opposite-sign construction. This direct implementation is valid even when K has rank greater than one, so it can change an entire response subspace without requiring separate rank-one basis words. It still pays every nonzero coefficient of the explicit K and every lifecycle clear.

**Action/interface.** Build a simultaneous helper gauge from a checked nilpotent response operator. Dependencies: N011's aggregate idea. Status: constructive matrix application.

<a id="n057"></a>

### N057 — Dyadic orbit-mean reflection

**Theorem.** For q a power of two, the map on q helpers h_i↦h_i−(2/q)Σ_j h_j is an involution, preserves the real Euclidean norm, and has charge 2q+qA(2/q)+2 CLEAR with one aggregate.

**Proof.** Let t be the sum of the original coordinates, formed by q additions into cleared work. Subtract (2/q)t from every helper. Their new sum is t−2t=−t, so adding that new sum into work clears it in q further additions. The map negates the constant vector direction and fixes every sum-zero vector, which are orthogonal subspaces; hence it is an involution and norm is preserved. The coefficient 2/q is dyadic by hypothesis and its q uses are explicitly charged. This is an ordinary scalar helper-bank reflection, not a claim of family-local native unitarity or a free physical permutation.

**Action/interface.** Change common-mode receiver coordinates without introducing non-dyadic normalization. Dependencies: N043. Status: constructive averaging chart.

<a id="n058"></a>

### N058 — Block-tridiagonal inverse with a sparse retained solve

**Theorem.** For a block-tridiagonal matrix with diagonal A_i, lower L_i and upper U_i, suppose the pivots D₁=A₁, D_i=A_i−L_iD_(i−1)⁻¹U_(i−1) have supplied dyadic inverses. Forward variables z_i=b_i−L_iD_(i−1)⁻¹z_(i−1) and backward variables x_i=D_i⁻¹(z_i−U_i x_(i+1)) solve Mx=b. They yield an additive source-preserving inverse circuit by one retained computation and its inverse.

**Proof.** Eliminating the previous variable from row i subtracts L_iD_(i−1)⁻¹ times the reduced previous row, producing exactly pivot D_i and right side z_i. Induction proves this reduced upper-bidiagonal system. Substituting from the last row upward gives the displayed x_i and satisfies every reduced equation, hence every original equation. Compute all z_i,x_i privately, add x into the target, then reverse the entire computation. With total dimension n and forward charge Γ=n+ΣA(L_iD_(i−1)⁻¹)+ΣA(D_i⁻¹)+ΣA(D_i⁻¹U_i), the full charge is 2Γ+n+4n CLEAR. All pivots are finite supplied matrices, not runtime inverse oracles.

**Action/interface.** Compile a banded native response inverse without materializing its dense inverse matrix. Dependencies: N052 and N041. Status: classical elimination, complete local realization.

<a id="n059"></a>

### N059 — Arrowhead inverse through one shared aggregate

**Theorem.** Let M=[D,u;vᵀ,a], with diagonal dyadic-unit D and dyadic-unit s=a−vᵀD⁻¹u. Its inverse is diag(D⁻¹,0)+w s⁻¹zᵀ, where w=(D⁻¹u,−1) and zᵀ=(vᵀD⁻¹,−1). It admits the diagonal-plus-one-aggregate circuit of N027.

**Proof.** The block elimination in N052 leaves the scalar Schur pivot s. Solving gives last coordinate s⁻¹(b_last−vᵀD⁻¹b_top) and top coordinates D⁻¹b_top−D⁻¹u times that last coordinate. Expanding these two formulas gives exactly the stated diagonal matrix plus w s⁻¹zᵀ. All inverses are allowed unit scales and all vectors are explicit dyadic data. The response circuit therefore costs Σ_iA(D_ii⁻¹)+2A(zᵀ)+A(w s⁻¹)+2 CLEAR, with no omitted off-diagonal reads. This implements a dense inverse using one aggregate rather than asserting a rank bound without an executable word.

**Action/interface.** Replace an arrowhead correction/decoder block by its charged shared response. Dependencies: N027 and N052. Status: constructive structured inverse.

<a id="n060"></a>

### N060 — Change only a split helper image and preserve its kernel

**Theorem.** Let A B=I_r and let J=I_r+K be an explicit invertible r-register word. Then G=I+BKA is invertible, acts as J on the B-image, and fixes ker A pointwise. With supplied dyadic J⁻¹A, it has charge A(A)+A(BK)+A(J⁻¹A)+2r CLEAR using r aggregate registers.

**Proof.** Compute t=Ah, add BKt into h, then subtract J⁻¹A times the new h from t. Since A h_new=(I+K)Ah=Jt, the subtraction clears t exactly. If h=Bz, then G h=B(z+Kz)=BJz; if Ah=0, the update is zero. Every h splits as BAh+(h−BAh), and the second summand lies in ker A. Thus the explicit inverse applies J⁻¹ on the first component and identity on the second, namely I+B(J⁻¹−I)A. All source directions and their returned states are specified, and no action on an unobserved complement is left unknown.

**Action/interface.** Alter only a chosen response image while preserving protected kernel directions in a helper chart. Dependencies: N056. Status: constructive splitting application.

## VII. Constructive frame ledgers, with no implicit demotions

For this chapter a frame is a binary subspace. A ledger promotion F⊆G is charged H_(dim G−dim F); a scalar read at a declared frame requires its operands aligned there. A zero difference is no positive child. These theorems construct explicit monotone ledgers and scalar words. They do not infer native phase identities from dimensions: instantiation uses the actual finite frame operators and phase recipes. A returned larger frame is a stated changed boundary, not an uncharged return to the old one.

<a id="n061"></a>

### N061 — One common-frame batch with all promotions listed

**Theorem.** Given initial frames F_i and a scalar helper word whose operands all accept the common frame J containing every F_i, promote each used register once to J, execute the word, and, if needed, its scalar inverse at J. The ledger charges exactly Σ_i H_(dim J−dim F_i) plus the scalar word charges; its final frames are J.

**Proof.** The inclusions make every listed promotion legal in the ledger model. After promoting all operands, every scalar gate has both of its registers at the declared common frame. Scalar operations do not change these labels, so induction through the gate list proves validity of the whole word and its inverse. The inverse restores logical data but does not demote a frame; the returned labels remain J. Each register is promoted exactly once, giving the displayed multiset of positive-rank charges. This is a sufficient frame schedule with a completely specified larger-frame boundary, not a claim that logical invertibility alone restores a native entrance frame.

**Action/interface.** Emit an explicit shared-frame `A` batch and its exact CHILD ledger. Dependencies: accounting. Status: constructive ledger application.

<a id="n062"></a>

### N062 — Nested requirements admit a deterministic promotion schedule

**Theorem.** Suppose a register's successive required frames form E₁⊆…⊆E_s and its entrance F⊆E₁. Promote it just before each strict increase. The ledger is valid, ends at E_s, and its positive ranks are dim E₁−dim F and dim E_i−dim E_(i−1), with zero differences omitted.

**Proof.** At the first read the initial promotion places the register at E₁. If a later required frame is unchanged, no operation is needed. Otherwise its containment of the preceding frame makes the next promotion legal, after which the corresponding read is aligned. Induction covers every read, with no downward step. Adding the dimension increments telescopes to dim E_s−dim F, while their separate H charges remain separate; equal rank mass is not silently identified with equal paid cost. The algorithm is constructive from a finite list of subspace bases and records every actual promotion.

**Action/interface.** Generate a complete staged reader ledger before comparing shared-kernel schedules. Dependencies: N061. Status: explicit monotone construction.

<a id="n063"></a>

### N063 — Equal-frame helper mixing adds no recursive promotion

**Theorem.** If every gate of an elementary helper word connects registers in the same current frame class and preserves those labels, the word and its inverse add no positive-rank ledger transition. Their full scalar charge remains 2|S|.

**Proof.** Every gate reads two registers already aligned at its stated frame, so no promotion is required before it. An addition changes logical values, not the common frame label, allowing the argument to continue through the word. The reverse signed word uses the same pairs and labels, hence is valid under the same conditions and restores all dirty helper values. This proves only zero extra promotion cost of this particular mixing word. It does not say the word is scalar-free, unitary on physical families, or compatible with a different initial frame assignment. Each scalar primitive and private coefficient lifecycle is included in |S|.

**Action/interface.** Delay a kernel basis change until its actual helper operands have equal frames, as in staged `A` sharing. Dependencies: N002. Status: native ledger adaptation.

<a id="n064"></a>

### N064 — A certified common entrance replaces only first climbs

**Theorem.** In an existing monotone ledger, let a helper's first required frame be E. Replacing its entrance 0 by any supplied F⊆E leaves all later ledger steps valid and replaces the first rank dim E by dim E−dim F. Its ordered residual width decreases by dim F when its final frame is unchanged.

**Proof.** The replacement first step is the legal inclusion F⊆E. It reaches exactly the same frame E as the original first step, so the remainder of the unchanged ledger starts from identical labels. Thus all subsequent promotions and reads remain valid. The residual width is final dimension minus entrance dimension, so its change is exactly −dim F. This is a constructive frame statement, not an arbitrary-dirt endpoint proof: pairing it with a verified zero-response kernel or a paid compensation construction is required. Both the replaced CHILD label and the changed helper width are explicit outputs to the caller's complete invoice.

**Action/interface.** Turn a proved dirt-entry change into exact first-climb and width edits. Dependencies: N003 or another endpoint constructor, plus the ledger definition. Status: adaptation.

<a id="n065"></a>

### N065 — A row-ordered triangular helper word has a monotone flag schedule

**Theorem.** Let F₁⊆…⊆F_n. A word that processes target i in increasing i and only reads helpers j<i can be aligned by promoting each source to F_i when it is used in target i's batch. Each such promotion is monotone; all final labels and rank increments are explicitly determined by the last target that reads each register.

**Proof.** Before processing target i, all previously used frames are among F₁,…,F_(i−1), hence are contained in F_i. The target itself has not been written as a later target yet and can be promoted to F_i if necessary. Every control j<i can therefore be promoted from its current contained frame to F_i. All gates in the batch are aligned and leave those labels unchanged. Induction proves the schedule. The logical endpoint is the actual ordered elementary word, including any path terms from earlier updates; it is not automatically the matrix whose entries were naively listed as gate coefficients. Every promotion is recorded at its actual current frame.

**Action/interface.** Build a legal staged triangular `A` rewrite without dropping fill-in or inventing demotions. Dependencies: N033 and N062. Status: constructive flag scheduling.

<a id="n066"></a>

### N066 — Full-frame cleanup accepts inverse scalar and monomial words

**Theorem.** Suppose all cleanup operands are already at FULL, and every declared warp is an explicit invertible monomial preserving FULL. Reversing a helper scalar/warp word gives exact inverse cleanup at FULL with no new positive-rank promotion; all scalar and warp implementation charges remain.

**Proof.** Every scalar gate is aligned because all its operands have the same FULL label. Every stated monomial warp maps FULL to itself, since its invertible address map takes the entire address space onto itself. Its inverse has the same property. Reversing the list and inverting each actual map therefore returns the original logical helper state on every input. At no point does a label leave FULL, so the cleanup adds no positive-rank transition in this ledger. This conclusion uses the complete explicit warp maps, including their phases; merely having equal dimensions would not establish it. Private clears retain their separate initialization/release contract.

**Action/interface.** Charge changed inverse cleanup honestly while avoiding fictitious extra climbs already absent at FULL. Dependencies: N041. Status: native-boundary application.

<a id="n067"></a>

### N067 — Componentwise joins avoid a needless global common frame

**Theorem.** Form the undirected interaction graph of a scalar helper word, connecting every pair that shares a gate. For each component K choose J_K containing all its entrance and required frames, and require every affected scalar gate to accept that chosen J_K as in N061. Promoting register i only to its component's J_K yields a valid batch ledger, with charge Σ_i H_(dim J_K−dim F_i), and no cross-component alignment is needed.

**Proof.** Every gate lies entirely within one connected component by construction of the graph. After the component's registers reach J_K, that gate is aligned, and operations in another component cannot alter its values or frame labels. Apply N061 independently to each component, then interleave their scalar words in any original legal order. The endpoint is unchanged because no gate was moved across a shared register. The listed promotions are sufficient even if two components use incomparable frames. This provides an explicit alternative to promoting all helpers to the join of every component, without making an unsupported minimality claim.

**Action/interface.** Price several disjoint shared-kernel banks separately instead of forcing one global entrance chart. Dependencies: N061 and N009. Status: constructive decomposition.

<a id="n068"></a>

### N068 — Move helper mixing across an identical fibre operator

**Theorem.** Suppose the same explicitly known linear operator K acts on every helper in a bank. A scalar helper matrix S commutes with this simultaneous action. Hence an emitted S word can be moved across that whole block without adding another K child, while retaining all S scalar charges.

**Proof.** On coordinate i, applying K after S gives K(Σ_j S_ij h_j)=Σ_j S_ij K h_j by linearity over the stated central scalar ring. This is exactly S applied after the componentwise K block. Equality holds for every helper vector, so no clean-state hypothesis is involved. The condition is equality of the actual operators, not equality of their ranks or spectra. Replacing one order by the other therefore keeps the same K applications and the same S word; it only changes their placement. Any cancellation with neighboring S inverses can then use the literal group-word rule N031.

**Action/interface.** Retiming a common helper basis through a genuinely identical native child block. Dependencies: N031. Status: tensor-factor commutation in a charged native context.

<a id="n069"></a>

### N069 — Split a response across explicitly known frame maps

**Theorem.** Let a source start at logical value x and follow known frame operators K₁,…,K_s. If supplied dyadic reads R_i satisfy A=Σ_i R_i K_i, reading R_i at the i-th frame adds exactly Ax. Its charge is Σ_iA(R_i) plus every specified frame transition.

**Proof.** At the i-th read the available source is K_i x, so the increment is R_i K_i x. Summing all target increments gives Ax by the supplied complete matrix identity. The target is not used as a control between these additive reads. No equality of the K_i is needed, and none is treated as an uncharged coordinate name: the source trajectory's actual transitions remain in the ledger. The identity is checkable from finite matrices and can expose an early partial response before the last frame is reached. It cannot be replaced by A=Σ_iR_i unless all K_i are identities.

**Action/interface.** Construct an early-read/late-read native schedule with its exact transported coefficients. Dependencies: N006 and N062. Status: adaptation.

<a id="n070"></a>

### N070 — Solve a constrained legal kernel and emit its word

**Theorem.** Fix a compensation matrix C, a pivot helper p and an allowed equal-frame support S containing p. If unit-pivot elimination of Ck=0, k_p=1, k_j=0 outside S terminates consistently, back substitution constructs a dyadic k. The N003 word then deletes pivot response p, touches only S, and adds no frame promotion at that point.

**Proof.** Each elimination operation is an explicit addition or division by a declared dyadic unit, so it preserves the system's solution set inside the dyadic ring. A consistent echelon system allows free variables to be set to zero and pivot variables obtained by back substitution. Substituting the resulting k into all original equations supplies a finite certificate of Ck=0 and the support constraints. The emitted pivot-controlled updates therefore have no forbidden operand and all lie in one equal-frame class. N003 proves their response effect and inverse restoration; N063 proves that their frame labels require no added promotion. All coefficient charges remain explicit.

**Action/interface.** Replace unconstrained kernel guesses by an actual frame-legal dirt-entry word. Dependencies: N003, N063. Status: constructive constrained elimination.


## VIII. Reversible coefficient compilation and explicit arithmetic witnesses

<a id="n071"></a>

### N071 — Compile a matrix-addition program with one clean coefficient register

**Theorem.** Let W be a finite program of real dyadic matrix additions between disjoint live blocks. Suppose its only requested resets are of declared private zero registers. Expand every coefficient c using the reversible macro of N080. The resulting primitive word implements W on arbitrary live inputs, uses one reusable coefficient register, returns that register to zero after every macro, and has scalar charge at most Σ_g A(M_g), in addition to W's explicitly requested resets.

**Proof.** Process the matrix-addition gates in their stated order, and process their entries in any fixed order. Within one matrix addition, no source coordinate is changed, so successive entry updates add exactly the required matrix-vector product. N080 restores its coefficient register before the next entry begins; consequently the same register works for all entries, even when the surrounding program changes source registers between gates. Induction on the gate list identifies every live state with the state of W. Sum the macro charges; there is no uncharged coefficient synthesis, division, or garbage erasure. Frame alignment remains a separate condition on the compiled gates.

**Action/interface.** Turn a rational `A`/`B`/`compensation` matrix witness into a literal scalar word with a complete private-work contract. Dependencies: N080. Status: constructive compiler theorem.

<a id="n072"></a>

### N072 — Reuse an addition-chain bank for several coefficient reads

**Theorem.** Given a source s, let a finite acyclic straight-line list construct multiples v_j=c_j s in initially zero private registers, using copies, additions, subtractions and unit scales. Let Γ be the actual charge of that list. If t output reads request y_l += v_(j_l), all these reads can be implemented with scalar charge 2Γ+t+2m CLEAR charges, where m is the number of private registers. All live inputs and the private bank are restored except for the requested outputs.

**Proof.** Clear the m private registers, execute the supplied list, and perform the t unit output additions. Its intermediate registers retain their computed values; output registers are not controls of the list. Reverse the construction list, replacing each reversible operation by its inverse. The resulting state of every private register is its initial zero, regardless of the dirty source and outputs. Release them with the m final clears. Copies here are additions into known zero destinations and are undone by subtraction; no unknown source is overwritten. The actual Γ includes every copy, not merely each abstract coefficient-chain edge.

**Action/interface.** Share expensive dyadic coefficient analysis across repeated native response reads, while charging retained workspace and cleanup. Dependencies: N041. Status: addition-chain adaptation with an explicit reversible boundary.

<a id="n073"></a>

### N073 — Batch a common denominator without dividing a dirty source

**Theorem.** For integers a_j and b ≥ 0, the update y += 2^(−b)Σ_j a_j h_j has a source-preserving implementation with one aggregate register and charge 2Σ_j A(a_j)+2b+1+2 CLEAR charges. This construction never divides an original helper.

**Proof.** Clear aggregate t and build t=Σ_j a_j h_j using the matrix-addition macros. Halve t exactly b times and add it into y. Double t b times, restoring its integral aggregate, and subtract the same integer combination of the unchanged helpers. Thus t returns to zero before release. The b halvings and b doublings are inverses on the dyadic domain, so the procedure does not require the aggregate to have been divisible in the integers. Summing the two integer combination charges, the scaling charges, the output read and the two lifecycle clears gives the stated bound. Every old value of y is retained.

**Action/interface.** Replace independently synthesized denominators in a compensation row by one explicitly paid aggregate denominator. Dependencies: N071. Status: constructive dyadic batching.

<a id="n074"></a>

### N074 — Construct a native denominator-depth certificate

**Theorem.** Consider a real dyadic linear circuit on initially integral registers. Assign initial exponents e_i=0. For a gate r_i += (a/2^b)r_j with integer a and b ≥ 0, replace e_i by max(e_i,e_j+b); for HALF on i replace e_i by e_i+1; DOUBLE, NEGATE and permitted CLEAR need no increase. At every prefix, 2^(e_i)r_i is integral. The same recurrence bounds each coefficient of that register's formal input row.

**Proof.** Initially both conclusions hold. At an addition gate, multiplying the old target and the added source term by 2 raised to the proposed maximum clears both existing dyadic denominators. Their sum is therefore integral. A halving introduces at most one additional factor of 2, while doubling and negation introduce none; clearing gives zero. Apply this argument separately to each formal input coefficient, whose initial values are 0 or 1. Induction proves the prefix certificate without summing denominator exponents from unrelated paths. This is an exact grid statement; it does not by itself authorize rounding or change a compiler precision invoice.

**Action/interface.** Attach a source-derived denominator-depth table to `LOCAL`, preserving the separate global precision proof. Dependencies: finite circuit semantics. Status: constructive arithmetic audit.

<a id="n075"></a>

### N075 — Signed-digit coefficient words with reversible cleanup

**Theorem.** Suppose a dyadic coefficient is given explicitly as c=2^(−b)Σ_(j=0)^L ε_j2^j with ε_j in {−1,0,1}. Let w be the number of nonzero digits. A source-preserving update y += c s has a clean-work implementation of charge at most 2L+2w+2b+3, using one private coefficient register. No optimality of the chosen expansion is assumed.

**Proof.** Clear t. Run Horner evaluation from the highest digit to the lowest: add or subtract s for a nonzero digit, and double t between successive digit positions. There are L doublings and w signed additions, and the resulting value is the displayed integer multiple of s. Halve b times, add t into y, and reverse all halvings and Horner operations. The register t is zero again and may be released. The two lifecycle clears, the output addition, and the forward/reverse arithmetic give 2L+2w+2b+3. The proof uses the supplied finite signed expansion, so an incorrect digit list fails an exact integer equality check before compilation.

**Action/interface.** Compile compensation coefficients using an explicit sparse signed expansion when its complete clean-work charge improves on binary synthesis. Dependencies: N080's cleanup principle. Status: classical signed-digit arithmetic with native accounting.

<a id="n076"></a>

### N076 — Pay for a dyadic wire gauge before using its coefficient discounts

**Theorem.** Let D be diagonal with entries 2^(k_i), where k_i are integers. Conjugating an elementary addition E_ij(c) by D replaces c by 2^(k_i−k_j)c. A finite scalar word W can therefore be replaced by D⁻¹ W' D, where every W' coefficient is changed in this way. The explicit charge is 2Σ_i |k_i| plus the expanded charge of W'.

**Proof.** Applied to a coordinate vector, D E_ij(c) D⁻¹ changes coordinate i by 2^(k_i)c2^(−k_j) times coordinate j and fixes all others. This proves the single-gate identity. Insert D⁻¹D between consecutive conjugated gates; the middle factors cancel literally, giving W'=D W D⁻¹ and hence the displayed implementation of W. Each D or D⁻¹ costs Σ_i|k_i| doublings or halvings. Arbitrary dirty values are restored to their original scale at the boundary. Discounting coefficients without the two boundary gauges would implement a different helper contract.

**Action/interface.** Test bit-cost-reducing helper wire scales with their actual entrance and exit charges included. Dependencies: N031 and N071. Status: charged conjugation construction.

<a id="n077"></a>

### N077 — Solve a bounded tree gauge exactly and emit it

**Theorem.** Suppose the interaction graph of a scalar addition word is a forest. Restrict every gauge exponent in N076 to the finite set K={−B,…,B}. Let f_ij(k_i,k_j) be the sum of expanded coefficient charges of all gates between i and j after that gauge. There is an explicit dynamic program producing the least charged gauge among these choices, including boundary cost 2Σ_i|k_i|, using O(|V||K|²+|W||K|²) scalar cost-table operations.

**Proof.** Root each tree. For a vertex i and proposed exponent k define D_i(k)=2|k|+Σ_(j child i) min_(l in K)(f_ij(k,l)+D_j(l)). At a leaf this is its boundary cost. Inductively, child subtrees have no edges between them and meet the parent only through their child's exponent, so independent minimization gives exactly the minimum for the whole rooted subtree. Minimize the root value and backtrack stored minimizing labels. Applying N076 emits an actual word of that charge. This proves optimality only inside this finite scalar-gauge family, not for arbitrary native suppliers.

**Action/interface.** Produce a certified finite helper-gauge nominee rather than choosing scales from coefficient bit lengths alone. Dependencies: N076. Status: tree dynamic programming applied to fully charged native arithmetic.

<a id="n078"></a>

### N078 — Build dyadic inverse entries from a determinant certificate

**Theorem.** Let M be an integer n×n matrix with det M=±2^b for an explicitly checked integer b ≥ 0. Its adjugate gives a dyadic inverse M⁻¹=±2^(−b)adj(M). Consequently both additive maps y += Mx and z += M⁻¹x have source-preserving compiled words, with charges A(M) and A(±2^(−b)adj(M)), respectively.

**Proof.** Cofactor expansion proves M adj(M)=adj(M)M=(det M)I over the integers: a diagonal entry is the determinant expansion and an off-diagonal entry is the determinant with two equal rows or columns, hence zero by pairing opposite signed permutation terms. Multiplying by the explicitly given inverse of ±2^b yields the asserted inverse over the dyadics. Cofactors and determinant can be computed by their finite signed permutation sums; their construction is offline and does not assume a unit-cost runtime inverse. Apply N071 to the two resulting explicit matrices. No converse or complexity advantage for this offline algorithm is claimed.

**Action/interface.** Replace an assumed rational chart inverse by a concrete dyadic entry witness and runtime charge. Dependencies: N071. Status: classical adjugate construction with an explicit admissible ring.

<a id="n079"></a>

### N079 — Complete a primitive integer kernel without a unit coordinate

**Theorem.** Let k be a nonzero integer vector with gcd of its coordinates equal to 1 and Ck=0. Integer Euclidean row operations construct an explicit unimodular word P with Pk=e_1. Thus S=P⁻¹ has first column k and C S has first column zero, even when no original coordinate of k is a dyadic unit. If the recorded word costs g, using and restoring this chart costs 2g.

**Proof.** Combine the first nonzero coordinate successively with each remaining coordinate by the extended Euclidean algorithm. Each quotient step is an integer row addition and each exchange or sign correction has an explicit addition/negation implementation. After finitely many steps the vector is (d,0,…,0), where d is the positive gcd. The hypothesis gives d=1; recording these reversible operations produces P rather than merely proving its existence. Reversing them constructs S, so S e_1=k. Multiplication by C now makes column 1 zero. N002 supplies correct compensation and the inverse boundary; all quotient-addition charges are retained.

**Action/interface.** Turn a primitive integral dirt-kernel direction into an emitted helper chart without illegally dividing by an odd pivot. Dependencies: N015 and N002. Status: constructive Euclidean completion.

<a id="n080"></a>

### N080 — A coefficient macro that never erases input-dependent garbage

**Theorem.** For nonzero real c=a/2^b, let L be the binary length of |a| and w its popcount. The update y += c s has a reversible private-work implementation of charge 2L+2w+2b+1, counting two CLEAR operations only when their operand is already zero. For c=±1 a single signed addition suffices; c=0 needs no operation.

**Proof.** Initialize a private zero register t. Starting from its zero value, read the binary digits of |a| from most to least significant, doubling between successive positions and adding s for each digit 1. This costs L−1+w operations and produces |a|s. Halve b times, then add or subtract t into y according to the sign of a. Reverse the b halvings and the binary construction; s has not changed, so every intermediate value is exactly retraced and t becomes zero. The two boundary clears therefore erase no information. The total is 2(L−1+w+b)+1+2=2L+2w+2b+1. These gates are invertible on all live values.

**Action/interface.** Use this macro, rather than an input-dependent scratch erasure, in every compiled native coefficient read. Dependencies: explicit dyadic arithmetic. Status: clean reversible compilation.


## IX. Shared linear analysis, complex coefficients, and output charts

<a id="n081"></a>

### N081 — Reverse accumulation constructs a transposed response circuit

**Theorem.** Let an acyclic linear computation have source nodes x_j and internal nodes v_i=Σ_(j earlier) a_ij v_j, with selected output nodes. Given dirty controls z on those outputs, a reverse-accumulation circuit computes the transposed linear map into additive source outputs. If Γ=Σ A(a_ij) and q output seeds are copied into private adjoints, its compute/copy/uncompute implementation costs 2(Γ+q)+n+2m CLEAR charges, where m is the number of adjoint registers and n the number of source outputs read.

**Proof.** Initialize all adjoints to zero and add each z seed to its output node. Visit internal nodes in reverse topological order; for each edge j→i add a_ij times the adjoint at i into the adjoint at j. A reverse induction shows that a node's adjoint is the sum, over all paths from that node to an output, of the product of edge weights along the path times its output seed. This is exactly the transpose coefficient. Copy source adjoints into the requested outputs, then reverse the entire seed/propagation list. All adjoints return to zero because those output copies did not modify them. Every edge, seed and lifecycle reset is charged.

**Action/interface.** Obtain an emitted dual response compiler from a shared analysis DAG, including its private work rather than assuming a work-free transpose. Dependencies: N071. Status: classical reverse accumulation with a reversible native interface.

<a id="n082"></a>

### N082 — Merge equal linear-analysis nodes with explicit lifetimes

**Theorem.** In an acyclic analysis DAG whose nodes store exact linear forms in unchanged source registers, suppose nodes u and v have identical coefficient rows, and u precedes v in the given topological order. Replace every use of v by u and delete v's construction. If Γ_old and Γ_new are the actual construction charges and m_old,m_new their private-register counts, compute/copy/uncompute charges are respectively 2Γ_old+R+2m_old and 2Γ_new+R+2m_new, where R is the unchanged output-read charge. The replacement preserves every output.

**Proof.** Process the DAG topologically. Before the deleted node, all retained nodes have their old values. Since u and v represent the same exact row, each downstream use of v receives the identical value when redirected to u. Induction preserves every later node and output. Keep u alive through the last redirected use; this lifetime extension is part of the new allocation, not an implicit free register. The resulting DAG is still acyclic because an already available identical row can be selected as representative. Reversing its actual construction restores every private node to zero. The charge formula includes that inverse and both lifecycle clears for every retained register.

**Action/interface.** Deduplicate equal compensation aggregates in a changed native DAG, with a precise cleanup and storage certificate. Dependencies: N081's DAG semantics and N041. Status: constructive common-subexpression sharing.

<a id="n083"></a>

### N083 — Lower complex dyadic reads to real native arithmetic

**Theorem.** Represent a complex register z=x+iy by two real dyadic registers. A complex coefficient c=a+ib acts by the real matrix [[a,−b],[b,a]]. Thus y += C h over Z[1/2,i] has an explicit real source-preserving implementation of charge Σ_(i,j)(2A(Re C_ij)+2A(Im C_ij)), with one reusable real coefficient register. This defines the complex extension used in this volume; it does not identify complex amplitude coordinates with physical helper wires for free.

**Proof.** Multiplication gives (a+ib)(x+iy)=(ax−by)+i(bx+ay). Four real matrix additions therefore produce the required real and imaginary increments while preserving the two source coordinates. Summing these identities over matrix entries proves the matrix statement on arbitrary dirty real pairs. N080 implements every real coefficient and restores its scratch register, so one scratch service can handle the entire sequence. The construction outputs an explicit scalar program on the doubled register representation. Any physical supplier using it must explicitly implement that representation and pay its interface; no new monomial or phase oracle is postulated.

**Action/interface.** Compile complex compensation coefficients into a fully specified real scalar consumer, or reject a proposed physical use lacking the doubled-register interface. Dependencies: N071 and N080. Status: classical realification with explicit charges.

<a id="n084"></a>

### N084 — Construct the complex adjoint word through realification

**Theorem.** For a complex dyadic matrix C, let R(C)=[[Re C,−Im C],[Im C,Re C]]. Then R(C*)=R(C)ᵀ. A finite complex-linear scalar word therefore has an explicitly emitted adjoint word obtained by reversing gate order, transposing indices and conjugating coefficients. Under N083's scalar charge, its cost equals the original cost.

**Proof.** Taking the real transpose changes the four blocks into [[Re Cᵀ,Im Cᵀ],[−Im Cᵀ,Re Cᵀ]], which is exactly the realification of the conjugate transpose. For a product G_s⋯G_1, direct multiplication of conjugate-transpose entries gives (G_s⋯G_1)*=G_1*⋯G_s*. An addition I+cE_ij becomes I+conjugate(c)E_ji; real unit scaling becomes its conjugate. N083 charges a coefficient only through the costs of its real and imaginary parts, which are unchanged by conjugation and transposition. Expand each new gate with its own clean coefficient macro. This constructs the scalar adjoint; actual child and warp duals remain explicitly supplied native operators.

**Action/interface.** Generate the scalar part of a dual `LOCAL` program with exact coefficient conjugation and private cleanup. Dependencies: N042 and N083. Status: adjoint construction, not an automatic physical duality claim.

<a id="n085"></a>

### N085 — Three real coefficient analyses for one complex multiplication

**Theorem.** For fixed real dyadics a,b, the complex read (u+iv) += (a+ib)(x+iy) has a clean-work real implementation costing at most 2(A(a)+A(b)+A(a+b))+17, using four private aggregate registers plus coefficient scratch. It preserves x and y and returns every aggregate to zero.

**Proof.** Compute t=x+y, p=ax, q=by and r=(a+b)t in initially zero private registers. Their construction costs Γ=2+A(a)+A(b)+A(a+b), since t needs two source additions. Add p−q into u and r−p−q into v, using five unit additions or subtractions. Expanding r gives ax+ay+bx+by, so r−p−q=bx+ay, exactly the required imaginary increment. Reverse the four constructions in dependency order after the output reads. Their sources remain unchanged, so all four work registers become zero. The charge is 2Γ+5+8 lifecycle clears, yielding the bound. It is a candidate alternative to N083, not a universal cheaper implementation.

**Action/interface.** Compare direct four-read and shared three-analysis compilation for actual complex coefficients in a new scalar consumer. Dependencies: N080 and N083. Status: Gauss multiplication identity with full linear-circuit charges.

<a id="n086"></a>

### N086 — Walk neighboring response rows instead of recomputing them

**Theorem.** Let v_0,…,v_(m−1) be explicit response rows and d_i=v_i−v_(i−1) for i ≥ 1. The source-preserving multi-output update y_i += v_i h has a one-aggregate implementation of charge 2A(v_0)+2Σ_(i=1)^(m−1)A(d_i)+m+2 CLEAR charges.

**Proof.** Clear t and form v_0h. Read t into y_0. For i=1,…,m−1, add d_i h into t and read t into y_i. Induction gives t=v_i h at its i-th read because v_(i−1)+d_i=v_i. After all outputs, subtract the differences in reverse order, then subtract v_0h. The unchanged source h makes t zero exactly. The outputs were never used as controls, so arbitrary initial values of all y_i are harmless. Counting each initial and difference analysis twice, each output once, and the two zero lifecycle clears proves the formula.

**Action/interface.** Search response-row orders with sparse adjacent differences, then emit the actual analysis walk and inverse. Dependencies: N071. Status: constructive shared-response traversal.

<a id="n087"></a>

### N087 — Compile sliding weighted windows from coefficient jumps

**Theorem.** Fix weights w_0,…,w_(k−1) and unchanged sources h_0,…,h_(m+k−2). All m outputs y_i += Σ_(j=0)^(k−1)w_j h_(i+j) can be implemented with one aggregate at charge 2Σ_j A(w_j)+2(m−1)Δ+m+2 CLEAR charges, where Δ=A(w_0)+A(w_(k−1))+Σ_(j=1)^(k−1)A(w_(j−1)−w_j), for m,k ≥ 1.

**Proof.** The first window costs Σ_j A(w_j). Moving from window i to i+1 removes w_0h_i, changes the coefficient on h_(i+j) by w_(j−1)−w_j for 1 ≤ j < k, and adds w_(k−1)h_(i+k). These are the complete coefficient differences; there is no shift of the source bank. Their charge is Δ, including signs through A(−c)=A(c). Apply N086 to this explicit row path. It reads every window once and reverses the sparse updates, preserving the sources and clearing the aggregate. The k=1 case includes removal and insertion on distinct source coordinates, so the formula remains valid.

**Action/interface.** Recognize and compile piecewise-constant or short-jump response windows without inventing an uncharged source permutation. Dependencies: N086. Status: exact sliding-window response construction.

<a id="n088"></a>

### N088 — Answer a laminar response family with a reversible sum tree

**Theorem.** Let a rooted forest have unchanged source registers at its leaves and one private register for every internal vertex. A query asks for the sum of all leaves below a specified vertex. If the forest has E edges, I internal vertices and q queries, all queries can be added to dirty outputs at charge at most 2E+q+2I CLEAR charges, retaining no private garbage.

**Proof.** Initialize each internal register to zero. In postorder, add every child value into its parent's register. Each edge is used exactly once, so an induction on subtree height shows that each internal register contains the sum of its descendant leaves; distinct leaves occur once because the structure is a forest. Read the requested vertex value into its output, using the unchanged leaf directly when the vertex is a leaf. Reverse the edge additions in reverse postorder, which restores every internal register to zero. The sources and old output values are untouched. The two traversals, q reads and internal lifecycle clears yield the charge. Arbitrary overlapping nonlaminar query sets are not covered.

**Action/interface.** Share a source analysis bank for genuinely laminar compensation supports, with explicit stored aggregates. Dependencies: N072. Status: tree-sum construction for a native response interface.

<a id="n089"></a>

### N089 — Concentrate common dirt in one output bank by an invertible chart

**Theorem.** Suppose m ≥ 1 output banks of equal dimension d have increments L_i x+C h. Apply the invertible output chart z_0=y_0 and z_i=y_i−y_0 for i>0 after the producer. The transformed increments are L_0x+C h in bank 0 and (L_i−L_0)x in every other bank. The chart costs d(m−1) unit subtractions; its inverse has the same charge.

**Proof.** Write each final output as its own initial value plus the stated increment. Subtracting the final y_0 from final y_i changes the initial output basis to y_i^old−y_0^old and subtracts both increments. The common C h cancels exactly, leaving (L_i−L_0)x. Register y_0 is unchanged throughout these subtractions, so all differences use the correct common value. Adding z_0 back to the other banks reverses the chart. Thus no information is discarded and no claim is made that arbitrary initial output dirt vanished. Restoring the old output ABI also restores its old response distribution.

**Action/interface.** Offer a changed `SOURCE` consumer with m−1 dirt-free response channels, while explicitly retaining the common dirty channel and charging any basis restoration. Dependencies: N007 and N019. Status: constructive output-response concentration.

<a id="n090"></a>

### N090 — Localize separable grid dirt to the boundary

**Theorem.** Let r,s ≥ 1 and let output banks y_(i,j), 0 ≤ i < r and 0 ≤ j < s, have helper responses C_(i,j). Suppose every interior mixed difference C_(i,j)−C_(i−1,j)−C_(i,j−1)+C_(i−1,j−1) is zero. Successive backward row differences and backward column differences give an invertible output chart whose interior banks have zero helper response. Its charge is d((r−1)s+r(s−1)) unit subtractions for d-dimensional banks; its inverse has the same charge.

**Proof.** First process i from r−1 down to 1, replacing row i by row i minus row i−1. The decreasing order ensures the subtracted row is its original value. Then process j from s−1 down to 1, subtracting column j−1 from column j in every row of the transformed array. An interior response is precisely the displayed mixed difference and hence zero. Top and left boundary responses are retained; they need not vanish. Reverse the column operations and then the row operations to invert the chart. This proves the endpoint including arbitrary old output values, not only its response coefficients. Each edge difference uses d unit subtractions, giving the exact ledger.

**Action/interface.** Convert a supplied two-dimensional separable dirt pattern into boundary-only dirty channels for an explicitly changed consumer. Dependencies: N089's output-chart semantics. Status: finite-difference response chart.


## X. Concrete dirt-entry rewrites and complete local assembly

<a id="n091"></a>

### N091 — Emit the actual four-helper shared-kernel chart

**Theorem.** Let four equal-frame helpers have compensation columns c_0,c_1,c_2,c_3 with c_0+c_1−c_2−c_3=0. The three updates h_1 += h_0; h_2 -= h_0; h_3 += h_2 emit the matrix S=[[1,0,0,0],[1,1,0,0],[−1,0,1,0],[−1,0,1,1]]. The transported compensation is [0,c_1,c_2+c_3,c_3]. Using this chart and its inverse costs six unit additions and no additional promotion at the equal-frame cut.

**Proof.** Name the original helpers a,b,c,d. The updates give (a,b+a,c−a,d+c−a); the last read uses the already updated third helper. This is the displayed S, whose first column is (1,1,−1,−1). Multiplying C by its four columns gives the stated compensation, including the changed third response c_2+c_3. Reverse the updates by subtracting the updated third helper from the fourth, then adding h_0 back to h_2, then subtracting it from h_1. This returns every original value. All operands share one declared frame, so the scalar chart requires no promotion there. Different-frame staged realizations must instead supply their actual ledger.

**Action/interface.** Emit and check the PR #2857 quartet chart without confusing its three-gate boundary form with its separately charged staged implementation. Dependencies: N002 and N063. Status: explicit source precedent, independently derived; not a new discovery claim.

<a id="n092"></a>

### N092 — Work-free compression of a repeated response column bank

**Theorem.** Suppose n helpers at one common frame have the same response column u. For i=0,…,n−2 in increasing order execute h_i -= h_(i+1). Their chart S changes C=[u,…,u] to C S=[u,0,…,0]. The chart and inverse together cost 2(n−1) unit additions and use no aggregate register.

**Proof.** Increasing order means each h_(i+1) is read before it is changed. Therefore S has 1 on its diagonal, −1 directly above the diagonal and zero elsewhere. Its first column is e_0, and column j>0 is e_j−e_(j−1). Multiplying the repeated-column response by these columns gives u and then zeros. The inverse is obtained by adding h_(i+1) back into h_i in decreasing order, restoring all arbitrary dirty helpers. This is a reversible in-place chart, not an assumption that their sum is initially clean. The equal-frame condition gives a promotion-free placement, while compensation reads and any later native climbs remain separately charged.

**Action/interface.** Concentrate repeated dirty responses in one existing helper instead of allocating a private sum bank. Dependencies: N002 and N063. Status: structured in-place kernel construction.

<a id="n093"></a>

### N093 — Delete inverse pairs across a certified independent interval

**Theorem.** Let a scalar native word contain a reversible gate g, an intervening word V, and g⁻¹. If every gate of V has read/write supports independent of those of g, deleting g and g⁻¹ preserves the complete scalar endpoint and saves exactly their two implementation charges. Repeating this deletion rule terminates and emits an equivalent word with a nonincreasing charge.

**Proof.** N033 allows g to be exchanged successively with each intervening gate: neither gate changes a value read or written by the other. Hence the original substring is equivalent to V followed or preceded by adjacent inverse gates. Their actual maps compose to the identity on all dirty inputs, so deleting them is valid. Each deletion strictly shortens the finite gate list by two, ensuring termination. Record every chosen support test and deleted pair; replaying these finite identities proves equivalence of the final word. This is not an assertion of a unique normal form or globally shortest circuit. If gates include frame changes, their full actual maps and support contracts must satisfy the same independence test.

**Action/interface.** Simplify a newly emitted helper/cleanup word with a replayable cancellation certificate, rather than deleting commuting-looking gates by inspection. Dependencies: N033. Status: constructive trace-word reduction.

<a id="n094"></a>

### N094 — Compute the exact response of one staged insertion

**Theorem.** Encode a linear program on all live registers by a prefix P and suffix Q. Insert a shear I+a u vᵀ between them, with vᵀu=0 and a dyadic. The complete map changes from QP to QP+a(Qu)(vᵀP). For any declared output projection Π, its response change is the explicitly factored row/column product a(ΠQu)(vᵀP). The insertion and its inverse each have charge 2A(vᵀ)+A(a u)+2 CLEAR charges, using the aggregate construction of N011; a coordinate shear may instead use its one addition macro.

**Proof.** Multiply Q(I+a u vᵀ)P and distribute. The two terms are QP and aQuvᵀP, with the original order of every operator retained. The condition vᵀu=0 gives (uvᵀ)²=0, so the inserted map is invertible with inverse I−a u vᵀ. If u and v select distinct registers, it is one ordinary addition macro; for general finite vectors N011 computes t=vᵀz, adds a u t into z, then subtracts vᵀz_new from t, which clears because vᵀu=0. This gives the displayed charge without attempting an invalid in-place dense matrix addition. The prefix factor vᵀP is the actual value of the control at that cut, including any source signal and dirty response. It cannot be replaced by the original control coordinate unless this equality is checked.

**Action/interface.** Evaluate a literal dirt-entry insertion at an internal `A`/`B` cut, preserving noncommuting transport instead of treating it as an entrance basis change. Dependencies: N071. Status: exact staged sensitivity construction.

<a id="n095"></a>

### N095 — Retain the cross term of two ordered insertions

**Theorem.** With prefix P, middle M and suffix Q, insert E_1=I+a u_1v_1ᵀ and E_2=I+b u_2v_2ᵀ in that order, requiring v_1ᵀu_1=v_2ᵀu_2=0 for the reversible insertion contract. Their full map is QMP+aQMu_1v_1ᵀP+bQu_2v_2ᵀMP+abQu_2(v_2ᵀMu_1)v_1ᵀP. In particular the changes add linearly when the explicit transported cross scalar v_2ᵀMu_1 is zero.

**Proof.** Expand Q E_2 M E_1 P first in E_2 and then in E_1. The term selecting neither insertion is QMP; selecting only the first gives aQMu_1v_1ᵀP; selecting only the second gives bQu_2v_2ᵀMP. Selecting both gives the last term with precisely the transported control-response factor v_2ᵀMu_1. These four choices exhaust the product. Applying any output projection preserves the identity. Each insertion is emitted with its actual scalar and frame charges; its individual nilpotence condition supplies an explicit inverse. The vanishing-cross condition is a finite matrix equality, not a guess from disjoint labels before transport.

**Action/interface.** Construct or reject paired staged dirt-entry rewrites using their complete interference term. Dependencies: N094. Status: ordered rank-one insertion formula.

<a id="n096"></a>

### N096 — Construct paired zero-target-defect insertions

**Theorem.** In N095 suppose v_2ᵀMu_1=0. Suppose the first and second projected response terms factor as αD and βD for an explicitly given matrix D and real dyadics α,β. Choosing a=β and b=−α preserves the entire projected target map, while generally changing the non-target path. It costs the two emitted shear words plus their inverse cleanup, with no compensation added for this target defect.

**Proof.** The vanishing transported cross scalar eliminates the term proportional to ab. The remaining projected change is aαD+bβD, which becomes βαD−αβD=0 in the central dyadic ring. This holds as a full input matrix, so it includes dirty-helper and source-signal columns, not just one tested input. The non-target map need not be unchanged; construct its inverse from the new ordered elementary word when restoring the old ABI. Thus the theorem supplies a genuine zero-target-defect deformation, not permission to reuse an obsolete cleanup. It remains meaningful if one coefficient is zero, but a useful two-insertion candidate selects a nonzero pair.

**Action/interface.** Emit a coordinated two-cut preconditioner that may change entrance geometry without creating an uncharged target correction. Dependencies: N095 and N100. Status: constructive compensated deformation.

<a id="n097"></a>

### N097 — Borrow source signal along a dirty-response kernel

**Theorem.** Suppose a producer has increment Dx+Ch and source-preserving inverse non-target cleanup. If Cu=0, prepend h += u Vx, run the producer and its cleanup, then subtract u Vx from h. The complete target increment is still Dx+Ch and the original source/helper inputs are restored. The extra charge is 2A(uV), with an optional explicitly paid factor construction instead of dense multiplication.

**Proof.** The forward producer receives h+uVx, giving target increment Dx+Ch+CuVx. The kernel identity makes the last term zero. Its non-target cleanup restores exactly the producer's new input, namely x and h+uVx, after which the final subtraction restores h. No helper had to be initially zero, and the original source x remained available for the last subtraction. The direct implementation adds the supplied matrix uV twice with opposite signs, giving the stated charge. If a factorized implementation is used, its aggregate initialization, two analyses and release are charged by N021 rather than hidden in A(uV).

**Action/interface.** Store a controlled source borrow in a compensation-invisible helper direction, with a complete old-ABI restoration path. Dependencies: N002 and N021. Status: source-entry kernel borrowing.

<a id="n098"></a>

### N098 — Reversibly dilate a possibly singular response without inverting it

**Theorem.** For any real dyadic n×n matrix M, the map J_M(x,h)=(Mx−h,x) is invertible on two arbitrary dirty banks and has an implementation of charge A(M)+3n. Its inverse is J_M⁻¹(u,v)=(v,Mv−u), also explicitly implementable at charge A(M)+3n. No inverse of M is required.

**Proof.** First perform h -= Mx. Rotate each pair (x_i,h_i) to (−h_i,x_i) using the three updates x_i -= h_i; h_i += x_i; x_i -= h_i, with the later updates using the changed values. On a pair initially (a,b), these yield (a−b,a,−b), hence final (−b,a). Applied after the matrix subtraction this gives (Mx−h,x). From output (u,v), the original x is v and h=Mv−u, proving the inverse formula. Reverse the actual emitted word to realize it at the same charge. This is an explicit changed two-bank source-consuming interface, not the source-preserving map x↦Mx when M is singular.

**Action/interface.** Embed a cheap singular response analysis into a reversible native boundary while retaining the displaced dirt bank for its consumer. Dependencies: N071. Status: unimodular linear dilation with fully paid rotation.

<a id="n099"></a>

### N099 — Finite symbolic columns certify arbitrary-dirt endpoints

**Theorem.** A finite linear circuit with specified source, helper, output and private-zero inputs admits an exact symbolic-column certificate: propagate a formal basis vector for every independent live input and zero for each private input. Equality of the resulting columns with a claimed endpoint proves that endpoint for every allowed dirty input. The propagation also constructs the complete response matrix C used by N100. Ordered operator coefficients may instead be retained as finite noncommutative polynomials; exact polynomial equality then holds under every substitution by actual linear operators.

**Proof.** Each gate replaces its affected formal row by exactly the linear combination prescribed by its real gate. Induction therefore identifies each recorded column with the image of that basis input. Every allowed input is a linear combination of those basis inputs, so linearity proves the claimed endpoint once all columns match. A private-zero input contributes no column; clearing an arbitrary live input must still be represented by its actual zeroing map and is not treated as reversible cleanup. In the operator version, distribution concatenates ordered words without commuting letters. Substitution into linear operators respects sums and ordered products, proving the same identity; expression size is finite but is not promised polynomially small.

**Action/interface.** Produce a deterministic all-dirt response and restoration certificate for a changed literal word, including every private column restriction. Dependencies: finite circuit linearity. Status: exact source-bound verification principle.

<a id="n100"></a>

### N100 — Assemble a fully compensated local native invocation from a finite word

**Theorem.** Let V be an explicit reversible non-target word of charge g, interspersed with additive target reads of total charge r; the target is never a control. Private non-target registers start at zero. Suppose N099 computes total target increment Dx+Ch on the live source/helper inputs. Execute this word, reverse only V, then subtract Ch from the target. The resulting invocation adds exactly Dx, restores all non-target live inputs and returns every private register to zero. Its scalar charge is 2g+r+A(C)+2m CLEAR charges for m private registers. Its child ledger is the full forward and inverse ledger actually implementing V and the reads, plus compensation's actual ledger.

**Proof.** The first pass has the certified target increment Dx+Ch and non-target state Vz, where z includes the zero private inputs. Since no target value controlled that pass, removing target reads does not change V. Reversing V therefore returns z exactly while leaving the accumulated target unchanged. The initial helper h is now available, so the final subtraction removes precisely Ch. The target retains its arbitrary old value plus Dx. The private registers were restored to zero before their release clears, so no input-dependent information is erased. The charge counts every forward non-target operation again in reverse, every original target read once, and the emitted compensation. No rank transition is deleted merely from this scalar proof.

**Action/interface.** Turn an explicitly edited shared-kernel word into a complete local old-ABI supplier, recomputing compensation and cleanup instead of assuming the previous supplier's certificates still apply. Dependencies: N071, N080 and N099. Status: constructive sufficient local assembly; global compiler, recovery, phase and recurrence admission remain separate explicit interfaces.

## Closing scope and action inventory

There are 100 numbered proved local construction theorems in this volume. They supply response matrices, helper words, scalar compilers, source-consuming boundaries and explicit charge formulas. A theorem whose output is a frame ledger certifies that ledger, not an uninspected physical monomial or recursive realization. A theorem whose output is a scalar word retains its actual child and phase obligations. No entry asserts a new numerical κ, global multiplication optimality, formal Lean verification, or that all proposed uses improve the current supplier. The index records a concrete emitted object and the frontier interface for each entry; the self-review binds the source precedents and audits these distinctions.
