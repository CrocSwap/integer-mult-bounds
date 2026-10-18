# Tensor, common-label and exact-recovery action theorems

Exactly 100 constructive informal theorems, T001–T100. These are sufficient application contracts for changing a paid supplier, not a claim of a new numerical κ or TI = TI_SL. No Lean process or proof service is used. Classical ingredients are credited; no global novelty claim is made.

## Shared language and charged interfaces

K is an explicitly represented field; dimensions are positive unless a zero case is expressly included. Parameters used as bit lengths and polynomial degrees are nonnegative integers. CRT moduli are positive integers at least 2, and all supplied coefficient tables are finite. A bilinear provider is an actual identity B(x,y)=Σ_{a=1}^r u_a(x)v_a(y)w_a, with coefficient tables in K. A query is one indexed product u_a(x)v_a(y); a query list retains its specified labels and multiplicities. A decoder is an explicit linear map, never an existence oracle. F1 means a candidate changed block-query/tensor response interface, including its explicit source embedding and input/output conversion. The incumbent native words are linear all-column operators: a bilinear rank certificate alone does not implement their recursive C contract. Only an actual compatible source realization with the complete paid invoice can connect an F1 construction to that incumbent. F2 means a common-label batch-query/decoder contract. F3 means actual transporter or coefficient recovery. F4 means exact scalar descent and integer specialization. F5 means the integer convolution/bit-supplier interface. F6 means the selected-address source contract: chart maps are input-independent and preserve untouched labels. A change at F1–F6 is an actionable candidate only after the actual native and whole-package admission consumers accept its complete priced contract.

An arithmetic operation is one field addition, subtraction, multiplication or nonzero division. A nonzero-entry matrix application costs at most twice its number of nonzeros, with output initialization and coordinate copies separately counted. Dense a-by-b application therefore costs at most 2ab arithmetic operations and a+b coordinate accesses. Constant multiplications are included. A field-operation bound is not a bit bound: T061–T070 provide explicit integer/rational encodings. Preprocessing and memory bounds are stated separately; they may be amortized only with an explicit number of later uses. Every savings action is a sufficient comparison against the incumbent's complete charge, including these adapters. No saving is inferred from a smaller raw tensor rank alone.

Source hooks: S1 actual PR #2839 replica and blocknorm contracts; S2 PR #2855 mixed-fibre/exact-recovery applications; S3 actual PR #2863/T185 fixed-word packing attainment; S4 canonical CodePrimeFieldDescent20260913 declarations; S5 canonical CodeMatrixRecovery20260913 declarations; S6 registered derived-factor recovery notes; S7 central TI/TI_SL findings and explicit determinant certificates; S8 primary classical finite-field/trace/bilinear-algorithm literature. Exact paths, hashes, inspected declarations and retrieval limits are in TENSOR-self-review.md. Source indexing is not kernel verification.

## 1. Query-list compression with exact output recovery

<a id="t001"></a>

### T001 — Proportional-query fusion with a paid decoder

**Statement.** Given a provider and a group G of indices with u_a=α_a u and v_a=β_a v, replace those |G| products by the single product u(x)v(y), with output vector w=Σ_G α_aβ_a w_a. The resulting provider is exact. Preprocessing costs at most 3|G|q operations for q output coordinates; runtime uses one product, the two chosen input forms, and at most 2q output operations instead of the group's individual decoders. A strict complete-cost reduction gives an F1 replacement.
**Proof.** Distributivity gives Σ_G u_a(x)v_a(y)w_a=u(x)v(y)Σ_G α_aβ_a w_a, coordinate by coordinate, including zero coefficients. Form each scalar α_aβ_a and accumulate its multiple of each output coordinate; the displayed preprocessing bound covers multiplication and addition. Runtime evaluates the displayed forms and accumulates the one vector. All other terms and labels are untouched; relabel the merged query once and redirect every old decoder coefficient into w. Thus no output is discarded and all added work is counted.

<a id="t002"></a>

### T002 — Output-aware common-left-factor fusion

**Statement.** Suppose u_a=u for a∈G and w_a=γ_a w, with explicitly given γ_a and w. Replace the group by u(x)(Σ_G γ_a v_a(y))w. With input dimension n, the new right form is constructed in at most 2|G|n operations and evaluated in at most 2n operations. This uses one paired query and a q-coordinate decoder, preserving the complete vector output.
**Proof.** Expand the new right form and distribute u(x) and w; the sum is exactly the old group. Coefficient accumulation gives the preprocessing bound and a dense dot product gives the runtime bound. This is more restrictive than merely sharing u: the common output line is the reason the different right forms can be combined without losing separately requested outputs. Store the output label vector w as part of the new decoder. Comparing the one-query circuit, its forms and its decoder with the original complete subcircuit is therefore a sound local savings test.

<a id="t003"></a>

### T003 — Duplicate input-form caching across labelled outputs

**Statement.** For r labelled queries with a distinct-left-form dictionary of size a and distinct-right-form dictionary of size b, there is a circuit with the same r products and decoder, at most 2am+2bn input operations, and a+b cached field elements in addition to output accumulators. It preserves every label even when the decoder requests the same product several times.
**Proof.** Evaluate each dictionary form once. For query j, use the two dictionary indices attached to j, multiply their stored values, and retain j's original decoder column. The values equal the original forms by dictionary equality, so every decoded coordinate is identical. The dense dot-product bound proves the stated arithmetic cost. Storage is the a+b cached values plus the incumbent output accumulation; query products may be streamed. Charge the two index reads for each query separately. Repeated labels have not been identified or erased, so this circuit is admissible when the consumer requires multiplicities.

<a id="t004"></a>

### T004 — Shared response contraction without full output materialization

**Statement.** If a consumer requests only L B(x,y), for an explicitly supplied s-by-q matrix L, the same queries with decoder columns Lw_a suffice. Preprocessing costs at most 2sqr operations; runtime decoder work is at most 2sr and storage s+r, rather than materializing q outputs and applying L afterward.
**Proof.** Linearity gives LΣ_a u_av_aw_a=Σ_a u_av_a(Lw_a). Compute each Lw_a beforehand. At runtime initialize s accumulators and add each scalar query times its s-vector. This computes every requested observable exactly; no claim is made about unrequested coordinates. If an F2 consumer promises q outputs, this theorem applies only after its declared output interface has actually been changed to L B. Its benefit is the explicit removal of the intermediate q-vector and its later matrix application, with preprocessing and extra stored coefficients charged.

<a id="t005"></a>

### T005 — Certified zero-query elimination at a restricted source interface

**Statement.** Let allowed inputs be x=Eξ and y=Fη, with explicit matrices E,F. Any query with u_aE=0 or v_aF=0 can be deleted from the restricted provider B(Eξ,Fη). The remaining queries use forms u_aE,v_aF and the old decoder. Restriction preprocessing costs at most 2r(md+ne) for E:m×d,F:n×e.
**Proof.** Substitute Eξ,Fη into each term. The indicated form vanishes identically, not merely on sampled inputs, hence its product is zero. Matrix multiplication constructs all surviving forms within the bound, and their direct evaluation avoids separately materializing Eξ,Fη. The equality is an identity on all ξ,η, so dirty exterior or spectator coordinates outside the declared E,F interface are neither assumed zero nor overwritten. Admission requires this actual restricted source interface; it cannot be inferred from a convenient test input.

<a id="t006"></a>

### T006 — Sparse bilinear coefficient verification by basis probes

**Statement.** A proposed r-query provider for B:K^m×K^n→K^q is correct if its output matches B(e_i,e_j) for all mn basis pairs. Verification uses at most 3qrmn field operations from its coefficient tables and mn supplied q-vectors; once verified, it is a universal exact provider.
**Proof.** The candidate is bilinear because every term is a product of two linear forms times a constant vector. Write x=Σ_i x_i e_i and y=Σ_j y_j e_j. Both candidate and B expand to Σ_{i,j}x_i y_j times their basis-pair output. The assumed equalities make these sums equal for every x,y. For each basis pair compute r scalar coefficient products and q-coordinate accumulation; 3qr operations suffice. This is an explicit sufficient certificate of the changed native response, not a test of a finite random sample.

<a id="t007"></a>

### T007 — Common-label multioutput decoding through a pivot subsystem

**Statement.** Let the desired response vector z lie in the explicitly given image of an injective q-by-d matrix E. Suppose a provider returns Pz, where P selects d rows and PE is invertible. Then z=E(PE)^−1(Pz). Recovery preprocessing is O(d^3) field operations and runtime at most 2d^2+2qd; all q labels are recovered.
**Proof.** Write z=Ec. The observed vector is PEc, so c=(PE)^−1Pz and the formula follows. Gaussian elimination on the explicit square matrix PE constructs the inverse and either certifies invertibility or rejects. Applying the inverse and E gives the bound. The image hypothesis is an actual declared identity for every input, verifiable by T006 on B's coefficient table. It is not inferred from observed rank on one input. Thus fewer supplied responses may replace the old common-label decoder exactly when this image certificate and the paid reconstruction are present.

<a id="t008"></a>

### T008 — One-sided shared-input batch evaluation

**Statement.** Given an r-query provider, one x and k independent y_b, compute all B(x,y_b) with r cached left-form values, kr products, and at most 2rm+2krn+2krq other arithmetic operations, using r+kq+2 field cells if right operands are streamed. This is a common-label batch contract with all b labels retained.
**Proof.** Evaluate each u_a(x) once. For each b, evaluate all v_a(y_b), form the r products and run the original decoder into output b. The provider identity proves each output independently. No sharing of right values or output labels is assumed. The bound sums the left preparation, k right preparations and k decoders; r cached left forms, k output vectors, one retained right-form/product temporary and one decoder accumulator suffice; the two temporaries are reused. The action at F2 is a priced replacement of k separate left preparations, not a reduction in the number of nonlinear products.

<a id="t009"></a>

### T009 — Decoder composition through exact quotient outputs

**Statement.** Let L:K^q→K^s and S:K^s→K^q be supplied, and verify SLB=B as a bilinear identity. A provider for LB followed by S computes B exactly, at additional cost at most 2qs operations and q output cells. This permits quotienting responses even if L has a kernel.
**Proof.** For every x,y the verification says S(L(B(x,y)))=B(x,y). Apply the LB provider and then the explicit matrix S. Its input dimension is s and output dimension q, giving the cost. Verify SLB=B on basis pairs by T006, or multiply its complete coefficient table. Unlike a bare dimension or rank statement, the section identity is an explicit sufficient recovery certificate for the actual response image. It preserves all original output labels after S, and prices both S and the changed provider.

<a id="t010"></a>

### T010 — Three-product quadratic-block provider over every commutative ring

**Statement.** Over a commutative ring, multiplying x_0+x_1t and y_0+y_1t uses three variable products A=x_0y_0, B=x_1y_1, C=(x_0+x_1)(y_0+y_1). Output coefficients are A,C−A−B,B. There are four additions/subtractions, no divisions, and three labelled coefficient outputs. Applying it to degree-bounded polynomial blocks gives an exact F5 child with no field-size restriction.
**Proof.** Expansion gives C=A+x_0y_1+x_1y_0+B, so subtracting A and B recovers the middle coefficient. The constant and quadratic coefficients are A and B. Two input sums and two output subtractions give the count. If x_i,y_i are themselves polynomial blocks of degree below b, the calculation holds in their commutative coefficient ring; shifts by t^b merely place the recovered polynomials, and overlapping coefficients are added rather than overwritten. All block additions, shifts and any carry normalization remain separate charged operations. This is the classical Karatsuba identity, not a new rank claim.

## 2. Common-label compatibility and batching

<a id="t011"></a>

### T011 — Input-independent label-chart transport

**Statement.** Let X,Y,Z be finite labelled coordinate sets. Given explicit permutations π_X,π_Y,π_Z, a provider for B gives a provider for B′(x,y)=π_Z B(π_X^−1x,π_Y^−1y). It has exactly the same variable-product count and coefficients; its adapters use |X|+|Y|+|Z| coordinate copies, with no data-dependent index computation.
**Proof.** Replace every occurrence of input coordinate i by π_X(i), every right coordinate j by π_Y(j), and every output coordinate k by π_Z(k) in the coefficient tables. Substitution in the provider identity gives B′ entry by entry. A permutation table is bijective, so no input or output label is lost or identified. The copied-index implementation supplies the stated memory charge. In the source interface the tables must be fixed before x,y are read; the theorem therefore licenses static owner-chart specialization but makes no claim about a chart selected from current data values.

<a id="t012"></a>

### T012 — Coupled relabelling across a shared intermediate

**Statement.** Suppose a labelled circuit first computes z=F(x,y) and then applies a linear map Gz. If an intermediate permutation π is inserted, the exact implementation πF followed by Gπ^−1 computes the same result. Adjacent intermediate permutations π and ρ can be replaced by ρπ with at most |z| table preprocessing steps, eliminating one full intermediate copy.
**Proof.** Matrix composition gives (Gπ^−1)(πF)=GF. For a chain, the value arriving at the consumer at label i is the value whose original label is (ρπ)^−1(i), which equals successive inverse lookup by ρ and π. Compute the composed table once by one lookup per label; its inverse is recorded if needed. The adapter cancellation is valid only at this shared intermediate boundary: independently relabelling the producer while retaining G would change the circuit. The saved copy is a concrete source-interface charge; the table and all surviving copies are still priced.

<a id="t013"></a>

### T013 — Constructive common-label alignment by a supplied perfect matching

**Statement.** Two r-query lists have an r-edge perfect matching whose matched left forms are α_i multiples and right forms β_i multiples, with α_iβ_i≠0. Then their paired products can share one indexed query stream after a permutation and diagonal scaling. Constructing the stream from the supplied matching costs O(r) index work; adjusting a q-output decoder costs at most (q+1)r multiplications including the proportionality products.
**Proof.** A perfect matching assigns each query of each list exactly once. At matched positions the second product equals α_iβ_i times the first for every input. Number the first list, reorder the second by its matching, and multiply the second decoder's corresponding column by α_iβ_i. The two consumers then read the same computed value with their respective decoder columns. Verify the proportional-form equations from explicit tables before applying the construction. This returns actual common labels and actual scaling constants; existence of some unspecified matching is not a recovery algorithm.

<a id="t014"></a>

### T014 — Tree reconstruction of compatible label frames

**Statement.** On a connected finite graph, each oriented edge u→v carries an explicit invertible d-by-d matrix A_vu, with reverse A_uv=A_vu^−1. If every edge satisfies A_vu=F_vF_u^−1 for frames recovered along one rooted spanning tree with F_root=I, those frames glue all query coordinates consistently. Recovery costs at most O(|V|d^3+|E|d^3) operations and supplies every F_v.
**Proof.** Set F_v=A_vuF_u on each tree edge from parent u. Induction computes invertible frames. Test the displayed equation for every edge by comparing A_vuF_u with F_v, avoiding any assumed cycle oracle. When all tests pass, transporting an intermediate vector by any edge agrees with changing from its source frame to its target frame. Products of edge transitions telescope to F_targetF_source^−1, hence every closed walk acts as identity. All vertex decoders can now be explicitly conjugated into the root coordinates. The procedure is a sufficient constructive gluing test, with all frame applications charged separately at runtime.

<a id="t015"></a>

### T015 — Query-orbit compression on a verified invariant source

**Statement.** Let a finite generated group act by supplied input permutation matrices P_g,Q_g and permutations of the r query indices, satisfying u_(ga)=u_aP_g^−1 and v_(ga)=v_aQ_g^−1 for each supplied generator. On the declared source subspaces fixed by those input generators, one product per query orbit suffices, with decoder vector Σ_(a in orbit)w_a. Computing all orbits and checking the generator coefficient identities costs O((t+1)r(m+n+q)) preprocessing for t generators.
**Proof.** Generator identities extend along words by composition. For fixed source inputs x,y, u_(ga)(x)=u_a(x) and v_(ga)(y)=v_a(y), so every product in the same query orbit has exactly the representative value. Sum its original decoder vectors and compute that product once. Substitution in the original expansion proves every output coordinate, without division by orbit size or group order. Traverse the finite query-permutation graph to find all orbits; sum decoder entries and verify the generator coefficient equations from the explicit tables. Source fixedness is checked on an explicit basis for the declared input subspaces. Arbitrary dirty inputs outside those subspaces are not asserted invariant. This is a real query-count reduction when an orbit has more than one term and the complete adapters remain affordable.

<a id="t016"></a>

### T016 — Tensor-product query composition with explicit label pairing

**Statement.** Providers with r and s products for B and C give an rs-product provider for B⊗C on the product input coordinates. Its left forms are u_a⊗u′_b, right forms v_a⊗v′_b, and outputs w_a⊗w′_b, labelled by (a,b). Dense direct evaluation costs at most 2rs(m m′+n n′+q q′) additional field operations.
**Proof.** On basis inputs e_i⊗e_i′ and f_j⊗f_j′, multiplying the two provider expansions gives precisely the displayed rs-term expression. Bilinearity extends that coefficient identity to arbitrary inputs of the product spaces, including inputs that are not pure tensors. Coefficient tables are obtained by multiplying pairs of explicit coefficients, so no factor-recovery problem is hidden. Product labels retain both original query indices; product output labels retain both old output indices. The dense dot products and decoder establish the bound. Tensor powers may therefore be used only with their enlarged dimensions and adapter costs explicitly invoiced.

<a id="t017"></a>

### T017 — Direct-sum batching with protected output namespaces

**Statement.** For providers B_j on disjoint input/output coordinate blocks, their direct sum is computed with Σ_j r_j products and the sum of their adapter costs, using disjoint output namespaces. If sequential evaluation is permitted, temporary storage is the maximum temporary storage of one provider plus all retained outputs.
**Proof.** Project inputs to block j, run its exact circuit and place the result in output block j. The direct-sum definition has no mixed-block coefficients, so the concatenated circuit agrees on every basis pair. Namespace disjointness prevents a decoder accumulation for one block from overwriting another. Reuse temporary cells only after the previous circuit has returned its declared boundary state; any required clearing is charged. This proves a constructive upper bound, not additivity of unrestricted tensor rank. It is useful for heterogeneous query batches whose consumer requires all original block labels and cannot accept their accidental identification.

<a id="t018"></a>

### T018 — Streaming common-label products with decoder sparsity

**Statement.** Given an r-query provider and a fixed order of queries, each product can be multiplied into every output accumulator whose decoder coefficient is nonzero and then discarded. Runtime decoding costs at most twice the decoder's nonzero count, and live response storage is one field element plus q accumulators.
**Proof.** Initialize each accumulator to zero. At query a compute z_a, and for each nonzero coordinate w_a,k add w_a,k z_a. At the end accumulator k equals Σ_a w_a,k z_a, the exact provider output. The product value is never needed after its last listed outgoing decoder edge, so it can be overwritten. This is valid even when queries share a label, because the loop follows the complete list and its multiplicities. Count one scalar multiplication and addition per decoder edge, plus output initialization and the original query preparation. This reduces a concrete private response-bank requirement without assuming free erasure of inputs or private coefficient work.

<a id="t019"></a>

### T019 — Translation-covariant response reuse with explicit inputs

**Statement.** Let a finite group act by known permutations P_g,Q_g,R_g, and verify B(P_gx,Q_gy)=R_gB(x,y) on all basis pairs for a supplied generator set. Then for any generator word g of length ℓ the response for (P_gx,Q_gy) is obtained from B(x,y) by ℓ output permutations, costing at most ℓq coordinate accesses and no new paired products.
**Proof.** The verified identities extend to every input by bilinearity. Apply them successively along the word: after each step the transformed response is the corresponding output permutation of the preceding response. This proves the product-word identity without assuming a faithful action or a unique word. If two words name the same actual input permutations, the computed outputs agree because both equal B on those transformed inputs. The theorem reuses a response only for the displayed coupled transformation of both inputs; it does not infer reuse for independently shifted operands. The word, permutations and memory accesses remain explicit.

<a id="t020"></a>

### T020 — Common-label joins through a verified overlap decoder

**Statement.** Let E:K^q→K^a⊕K^b be injective with a supplied left inverse D, and suppose two suppliers compute its two components E_1B,E_2B. Their concatenated responses followed by D compute B, with product count r_1+r_2 and decoder overhead at most 2q(a+b). Any overlap responses that are literally equal may be stored once while retaining both decoder references.
**Proof.** The concatenation equals EB by the two supplier identities; applying DE=I returns B. The dense matrix cost bounds D. If coordinate i of the first supplier and coordinate j of the second are verified equal as bilinear forms, both decoder references may point to the same stored value; linear accumulation with the original two coefficients preserves their sum. Otherwise they must remain separate even if their informal label names coincide. This supplies a complete join contract with explicit injectivity and recovery, rather than assuming that two overlapping lists automatically cover every requested output.

## 3. Priced tensor transport and adapter recovery

<a id="t021"></a>

### T021 — Actual tensor transport with a complete adapter invoice

**Statement.** Suppose explicit invertible A,D,C satisfy B′(x,y)=C B(Ax,Dy). A provider of cost L for B implements B′ with the same variable-product count and at most L+2(nnz A+nnz D+nnz C) arithmetic operations, plus matrix storage and coordinate accesses. The displayed identity can be certified by basis-pair verification.
**Proof.** Evaluate Ax,Dy, invoke the provider and apply C. Substitution gives the required equality for every input. Each sparse matrix row is a sum of products of stored coefficients and source coordinates, costing at most twice its nonzero count. No cost for recovering A,D,C is suppressed: if they are recovered rather than supplied, their recovery belongs to preprocessing and must be added. This theorem turns an actual returned isomorphism into an executable replacement; bare existence of an orbit relation provides none of these data or bounds.

<a id="t022"></a>

### T022 — Cancellation of paid intermediate basis transforms

**Statement.** Suppose a circuit stores z in coordinates Pz and its next consumer first applies P^−1, with P explicitly invertible and no intervening operation reading the encoded coordinates. Replacing both by the original z boundary removes both matrix applications exactly. More generally QP can be precomputed once at cost at most 2abc for P:b×c,Q:a×b and applied for at most 2ac operations per use.
**Proof.** In the inverse case the composite value is P^−1Pz=z. The no-intervening-reader hypothesis ensures that no other response depends on the deleted intermediate representation. In the general case, associativity gives Q(Pz)=(QP)z; coefficient expansion constructs every entry using b scalar products and sums. One application of the composite therefore replaces two applications with the stated paid preprocessing. This is a source-interface cancellation theorem, not permission to delete an arbitrary basis change inside a dirty-bank or phase-sensitive native word.

<a id="t023"></a>

### T023 — Query gauge normalization with exact decoder compensation

**Statement.** For each nonzero query term choose explicit nonzero coefficients a in u and b in v. Replace u by u/a, v by v/b, and w by abw. The provider is unchanged and the chosen two coefficients become 1. Preprocessing costs at most m+n+q+1 operations per term; no runtime divisions are required once normalized tables are stored.
**Proof.** The new term is (u(x)/a)(v(y)/b)(abw)=u(x)v(y)w because a,b are units. Choosing the pivots by scanning tables is constructive; zero terms are deleted instead of dividing by zero. Multiply and divide the coefficient tables during preprocessing. Every remaining runtime coefficient and its bit size must be charged from the normalized tables; this theorem guarantees equality and a canonical gauge, not that normalization always lowers bit cost. It makes comparison and exact common-label matching possible while compensating both pivots in the actual decoder.

<a id="t024"></a>

### T024 — Triangular input transport without a dense inverse

**Statement.** If A is an explicit invertible lower-triangular m-by-m matrix, a provider requiring A^−1x can receive it using forward substitution in at most m^2+m arithmetic operations and m temporary cells. For k right-hand sides the cost is at most k(m^2+m), with diagonal inverses precomputed once.
**Proof.** Compute z_i=(x_i−Σ_{j<i}A_ij z_j)/A_ii in increasing i. Nonzero diagonal entries exist by the hypothesis. Substituting each computed value proves row i of Az=x, while earlier rows remain unchanged; induction proves the complete solution. The row sums require at most 2Σ_i(i−1) operations and m divisions, bounded as stated. Store inverse diagonals to replace later divisions by multiplications. The provider then sees exactly its required coordinates. This specifically prevents pricing a sparse recovered triangular map as a free dense inverse or ignoring repeated-use solve costs.

<a id="t025"></a>

### T025 — Elementary arithmetic-factor adapters with certified inverses

**Statement.** Suppose A is given as a product of s coordinate permutations, nonzero coordinate scalings, or elementary updates x_i←x_i+c x_j with i≠j. A and A^−1 each have an explicit implementation of at most 2s arithmetic operations, plus the listed permutation accesses. The same factorization supplies a determinant certificate from the scale factors and permutation signs.
**Proof.** Apply the factors in their specified order. An update is inverted by subtracting c x_j because its source coordinate j was not changed by that factor; a scaling is inverted by its nonzero reciprocal; a permutation by its inverse table. Reverse the factor order to invert the product. These statements hold for all coordinates, so they provide actual maps rather than support-pattern guesses. A transvection has determinant 1, a coordinate scaling has determinant its scalar, and a permutation has its sign, as follows by row multilinearity. Multiplying these certificates gives det A and identifies whether an SL-constrained consumer can accept this particular recovered adapter.

<a id="t026"></a>

### T026 — Tensor-power adapters through fibres rather than dense tables

**Statement.** If A:K^m→K^m has an implementation using c arithmetic operations and at most m temporary cells, then A^⊗k on K^(m^k) has an implementation using at most k m^(k−1)c operations and at most m^k+m temporary cells in addition to retained input/output arrays, in addition to coordinate traversal. An inverse implementation has the analogous cost if A^−1 is supplied.
**Proof.** For axis j hold all k−1 other indices fixed and apply A to the m-entry fibre. There are m^(k−1) such fibres. Apply this procedure on every axis. Coefficient expansion shows the final entry is Σ_{i_1,…,i_k}Π_j A_(a_j,i_j)x_(i_1,…,i_k), precisely A^⊗k. The order of axis passes is immaterial because they act on different tensor factors. The bound counts every fibre application, and one full tensor buffer suffices with an implementation of A using at most m local temporary cells. Thus a short factor adapter can remain affordable after tensoring, but its growth is explicitly charged.

<a id="t027"></a>

### T027 — Integral unimodular query transport with no rational denominators

**Statement.** A product of integer transvections x_i←x_i+c x_j and coordinate swaps is an invertible integral adapter whose inverse has the same instruction count and coefficient magnitudes. If |c|≤2^h and the input coordinates have absolute value below 2^L, after s instructions every coordinate is below 2^(L+s(h+1)).
**Proof.** Each transvection's inverse uses −c, and swaps invert themselves, so reversing the instruction list proves integral invertibility without divisions. For the magnitude bound, if all current coordinates are bounded by M, an update is bounded by (1+|c|)M≤2^(h+1)M; a swap does not enlarge M. Induction over s steps proves the exponent. Applying this adapter before an integer bilinear provider and its inverse at a promised output boundary therefore needs no new denominator precision. Its larger integer lengths and arithmetic instructions are concrete compiler costs, not consequences of a field-isomorphism statement alone.

<a id="t028"></a>

### T028 — Bilinear adjoint provider with all labels exposed

**Statement.** If B(x,y)=Σ_a u_a(x)v_a(y)w_a, then the bilinear map B*: (λ,y)↦[x↦λ(B(x,y))] has provider Σ_a λ(w_a)v_a(y)u_a. It uses r paired products and the transposed three coefficient tables, with dense adapter cost at most 2r(q+n+m).
**Proof.** Apply λ to the original expression: λ(B(x,y))=Σ_a u_a(x)v_a(y)λ(w_a). The right side is evaluation at x of the displayed covector. Therefore the equality holds for every λ,y and all x, which uniquely identifies B*. No conjugation is used; this is algebraic duality over K. Each of the three coefficient tables is merely reassigned its input or output role, but its new form evaluation and decoder costs remain charged. A consumer that needs this contraction can use the actual adjoint certificate without solving a new tensor-isomorphism or orbit problem.

<a id="t029"></a>

### T029 — Transposed linear-query circuit with explicit fanout accounting

**Statement.** A linear straight-line circuit for L:K^m→K^n with s weighted edges, including a distinct terminal node and unit output edge for each output coordinate, yields a circuit for L^t with at most 2s arithmetic operations, n input adjoints and one zero-initialized accumulator per original node. Fanout is charged by its actual outgoing edges.
**Proof.** Give each output node its supplied adjoint value and all other nodes zero. Traverse original assignments backward. For an edge with coefficient c from node u into node v, add c times v's adjoint to u's accumulator. By induction, an accumulator holds the sum over all paths from that node to an output of the path coefficient times the output adjoint. At an original input this is exactly the corresponding coordinate of L^t. Every edge is used once and costs one multiplication plus one addition; initialization and storage are explicit. Thus a short constructive recovery circuit also supplies a priced transposed query interface, rather than an unpriced dense transpose.

<a id="t030"></a>

### T030 — Deterministic recovery of common query labels from coefficients

**Statement.** Given two r-query certificates with nonzero left and right forms, normalize each form by its first nonzero coefficient. If the two multisets of normalized form pairs coincide, an actual bijection and all nonzero proportionality scalars are recovered in O(r²(m+n)+rq) arithmetic/equality work. The matched stream with T013's compensated decoder computes both original response lists.
**Proof.** Scan each left form to find its first nonzero entry and divide the full form by that pivot; do the same on the right. Two nonzero forms are proportional if and only if these normalized vectors are equal: proportionality preserves the first nonzero position, and equality after normalization supplies the explicit pivot ratio. Thus equality of the normalized pair keys is exactly simultaneous proportionality of both factors. Match equal keys one occurrence at a time, retaining multiplicities; the multiset hypothesis guarantees a complete bijection. Pairwise key comparison takes at most r² comparisons of length m+n. Recover the ratios from the recorded pivots and adjust decoder columns as in T013, with their actual cost. This returns the matching rather than assuming a matching oracle or relying on an informal shared label name.

## 4. Recovering actual factors and transporters

<a id="t031"></a>

### T031 — Recovering a single-query provider from a coefficient pivot

**Statement.** For a nonzero coefficient tensor T_ijk, choose t=T_(i0,j0,k0)≠0. If every entry satisfies t²T_ijk=T_(i,j0,k0)T_(i0,j,k0)T_(i0,j0,k), then T has an explicit one-query provider: u_i=T_(i,j0,k0), v_j=T_(i0,j,k0)/t, w_k=T_(i0,j0,k)/t. Recovery and verification cost O(mnq) field operations.
**Proof.** The displayed identity divided by t² is exactly T_ijk=u_i v_j w_k. Hence Σ_ijT_ijk x_i y_j=(Σ_i u_i x_i)(Σ_j v_j y_j)w_k for every k. Construct the three lists from the pivot slices and check every identity; the check examines mnq entries with a bounded number of operations each. The returned factors, not just a rank label, can replace a larger F1 response circuit after their dot products and q-coordinate decoder are priced. The zero tensor is separately implemented with zero queries and q initialized zero outputs.

<a id="t032"></a>

### T032 — Recovering a Kronecker adapter from its actual entries

**Statement.** Let A be an invertible square matrix on K^m⊗K^n. Reshape its entries into R_(i,j),(a,b)=A_(i,a),(j,b). If R has a nonzero pivot and all its two-by-two minors vanish, one can recover P,Q with A=P⊗Q in O(m²n²) operations. Both P and Q are invertible, and their actual applications replace a dense A adapter.
**Proof.** For pivot R_(u0,v0)=t, put p_u=R_(u,v0), q_v=R_(u0,v)/t. The minor identity gives R_uv=p_u q_v, hence the Kronecker formula. If P had nonzero kernel vector x, choose nonzero y; then (P⊗Q)(x⊗y)=0, while x⊗y≠0, contradicting invertibility of A. The same argument proves Q invertible. Reshape p and q into the square matrices and verify their product entrywise. Applying P along n fibres and Q along m fibres costs at most 2nm²+2mn² operations, explicitly replacing rather than ignoring the original basis change.

<a id="t033"></a>

### T033 — Matrix-unit frame recovery for a query factor

**Statement.** Suppose N-by-N matrices E_ab, 1≤a,b≤d, satisfy E_abE_cd=δ_bcE_ad and Σ_aE_aa=I. A basis v_1,…,v_r of im E_11 gives an explicit frame F(e_a⊗e_s)=E_a1v_s, with N=dr. Recovery uses Gaussian elimination and O(d²N³) recovery operations after the relations are established, or O(d^4N³) including their exhaustive verification; F and F^−1 can then be charged as concrete adapters.
**Proof.** For every x, x=Σ_aE_a1(E_1a x), and E_1a x lies in im E_11. Thus the displayed vectors span K^N. If Σ_as c_asE_a1v_s=0, apply E_1b; matrix-unit multiplication leaves Σ_s c_bs v_s=0, so all coefficients vanish. The vectors form a basis and their number is N. Construct im E_11 by column elimination, build the vectors and invert their full matrix. In these coordinates every E_ab becomes the standard matrix unit on the first factor. A query compiler can therefore use actual recovered factor labels with a priced frame, without assuming that a named simple algebra comes with coordinates.

<a id="t034"></a>

### T034 — Joint recovery of two commuting query factors

**Statement.** Let E_ab and F_cd be two verified matrix-unit systems on K^N, of sizes d and e, commuting entrywise and each summing diagonally to I. From a basis v_s of im(E_11F_11), the vectors E_a1F_c1v_s form an explicit frame K^d⊗K^e⊗K^r≅K^N. Its frame can be recovered in O((d²+e²+de)N³) operations after the relations are established; exhaustive checks of both systems and their commutation add O((d^4+e^4+d²e²)N³).
**Proof.** Commutation permits x=Σ_ac E_a1F_c1(E_1aF_1c x), with each inner vector in the common primitive image. Thus the displayed vectors span. Apply E_1bF_1f to a zero linear combination; the unit relations isolate Σ_s coefficient_(b,f,s)v_s, proving independence. Consequently N=der and the frame is invertible. Form the common projection, obtain its image basis, construct and invert the frame by elimination. The output gives compatible labels for both factors simultaneously. It licenses tensor-query composition only after both actual frame applications and residual r-coordinates are included in the interface.

<a id="t035"></a>

### T035 — Complete matrix-unit transporter family with an actual formula

**Statement.** Given two size-d matrix-unit systems E,F on K^N with recovered frames U,V and equal multiplicity r=N/d, all invertible G satisfying GE_ab=F_abG are exactly V(I_d⊗S)U^−1 for S∈GL_r(K). Their determinants are (det V/det U)(det S)^d. In particular S=I supplies a concrete transporter of the two systems.
**Proof.** In the recovered coordinates write H=V^−1GU in d-by-d blocks of size r. Commutation with every diagonal unit forces all off-diagonal blocks to vanish. Commutation with each off-diagonal unit makes all diagonal blocks equal to one S. Conversely I_d⊗S commutes with every standard matrix unit, proving both directions. Invertibility is equivalent to invertibility of S. The block diagonal determinant is (det S)^d, and multiplication by the frames gives the formula. This recovers the labelled algebra transporter, not a transporter of an additional tensor: any such tensor must still be checked with the returned G by T040.

<a id="t036"></a>

### T036 — Constructive ratio-graph recovery of query scalings

**Statement.** On a finite graph, equations d_v=ρ_vu d_u with supplied ρ_vu≠0 admit a nonzero solution whenever a spanning-forest propagation passes every edge check. The algorithm returns one solution and every other solution is its product by an arbitrary nonzero constant on each connected component. Cost is O(|V|+|E|) field operations and index accesses.
**Proof.** Set one root value to 1 per component and propagate along tree edges, using inverse ratios when traversed backward. Every propagated value is nonzero. Check d_v=ρ_vu d_u on all edges; if they pass the constructed list is the required solution. For any second solution, the quotient of its value by the constructed value is equal at the endpoints of every edge and is therefore constant on a component. Conversely such component rescaling preserves every equation. These actual nonzero scalars can be inserted into a common-label decoder; no search over all field elements or uncomputed ratio assignment is needed.

<a id="t037"></a>

### T037 — Actual response-basis transporter from information-set ratios

**Statement.** Let A,B be explicit invertible d-by-d matrices, X,Y be d-by-n matrices, and nonzero scalars d_i,e_j satisfy diag(d_i^−1)Xdiag(e_j)=Y. Then G=Bdiag(d_i^−1)A^−1 is invertible and G(AX)diag(e_j)=BY. Recovery costs O(d³+dn) operations, with runtime adapter G priced separately.
**Proof.** Multiply out: G(AX)diag(e)=Bdiag(d^−1)Xdiag(e)=BY. Every factor of G is invertible because A,B are invertible and every d_i is nonzero. Compute A^−1 by elimination and form the product, giving the stated bound. When the scalar equation is supplied through ratios on nonzero entries, first verify matching zero support and solve those ratios by T036. The output is the actual row map and coordinate scaling, not merely evidence that two column configurations belong to the same orbit. The precise reconstruction mirrors the inspected canonical CodeMatrixRecovery source.

<a id="t038"></a>

### T038 — Exact extraction of a black-box bilinear response table

**Statement.** If a supplied evaluator is promised bilinear B:K^m×K^n→K^q, mn evaluations at (e_i,e_j) recover its complete coefficient tensor. This yields a deterministic mn-product provider with at most 2qmn decoder operations, and an explicit table for checking any proposed faster provider by T006. Extraction costs mn evaluator calls plus qmn stored field entries.
**Proof.** Set T_ijk=B(e_i,e_j)_k. Bilinearity gives B(x,y)_k=Σ_ijT_ijk x_i y_j. Thus the recovered table implements B for all inputs and directly verifies future candidate decompositions. The promise must be established by the source evaluator's algebraic construction; finitely many probes alone cannot prove an arbitrary function bilinear. Each of the mn calls returns q actual field values, accounting for the storage and preprocessing. The theorem offers an exhaustive motif-scale recovery procedure with explicit cost, not a claim that arbitrary growing black-box tensors can be recovered subquadratically.

<a id="t039"></a>

### T039 — Recovering a complete decoder from the coefficient image

**Statement.** Flatten B's explicit tensor into M:K^(mn)→K^q. Column and row elimination construct rank d matrices E and a d-row selector P with im E=im M and PE invertible. Therefore observing only the selected d coordinates of B permits full recovery by E(PE)^−1. Preprocessing costs O((q+mn)³); recovery costs at most 2d²+2qd per input pair.
**Proof.** Choose independent columns of M as E. Since E has rank d, its row elimination supplies d independent rows, giving P and a nonsingular PE. Every output B(x,y) is M applied to the vector (x_i y_j), hence lies in im E. Apply the explicit formula proved in T007. The source table supplies both the image certificate and its actual pivot, so the consumer is not asked to solve an unspecified recovery problem. The bound covers dense elimination on the displayed finite matrices; online savings require a supplier for the selected coordinates that is cheaper after the reconstruction cost is included.

<a id="t040"></a>

### T040 — Complete coefficient-level transporter admission

**Statement.** For explicit tensors T,S of dimensions m,n,q and candidate mode matrices A,D,C, verify S_ijk=Σ_abc A_ia D_jb C_kc T_abc by three successive mode contractions. The work is at most 2(m²nq+mn²q+mnq²) operations, plus cubic-size elimination to certify invertibility. Successful checks give a complete executable tensor-transport certificate.
**Proof.** First contract index a with A, then b with D, then c with C. At each stage ordinary matrix multiplication and finite-sum distributivity prove that the current table equals the corresponding partial contraction. The final table is the full displayed sum. Compare every entry with S and certify all three determinants nonzero by elimination. These data return actual transport maps; translating between covariant coefficient tensors and bilinear input conventions uses the explicitly determined transposes, not an unmentioned duality. The complete finite identity is sufficient for all input vectors by T006, while the maps' applications and their recovery costs remain paid.

## 5. Constructive scalar descent and specialization

<a id="t041"></a>

### T041 — Coordinate descent of a supplied extension-field provider

**Statement.** Let L/K have a supplied basis e_1=1,…,e_d and multiplication table. Suppose an r-query L-provider agrees with a K-valued bilinear B on K-inputs. It descends to a K-provider with at most d²r products, at most 2rd(m+n) input-form operations and 2rd²q decoder operations. Coefficient preprocessing costs O(rqd³).
**Proof.** Expand each L-valued left and right form in the supplied basis, yielding d K-linear forms on each side. For term a and output k, precompute M_(a,k,i,j)=φ(w_(a,k)e_i e_j), where φ extracts the e_1 coordinate. Since φ fixes K, applying φ to the original provider equality gives B_k=Σ_aij u_(a,i)v_(a,j)M_(a,k,i,j). This is the explicit base-field algorithm. Multiplication-table expansion and each d-term contraction give the preprocessing bound. Every d² product and every decoder coefficient is counted; no efficient descent or K-rational witness is inferred merely from existence of an L-isomorphism.

<a id="t042"></a>

### T042 — Scalar-readout descent through an explicit pairing matrix

**Statement.** Under T041 with one requested K-linear output functional λ:K^q→K, extended coefficientwise to the L-valued q-vector, the scalar response λB has a K-provider with at most dr products. For s explicitly requested functionals, separate such providers use at most dsr products. All pairing matrices and their rank factorizations are recovered in O(sr(d³+d²(m+n)+qd)) preprocessing operations, including the q-coordinate readout contractions.
**Proof.** For one term form the d-by-d matrix M_ij=φ(λ(w_a)e_i e_j). Row elimination gives M=PQ with at most d inner columns, and actual P,Q. Then Σ_ij u_iM_ijv_j=Σ_t(Σ_i u_iP_it)(Σ_jQ_tjv_j). Construct these K-linear forms and use one product per inner column. Sum over original terms and requested functionals. The resulting scalar outputs are exactly the requested readouts by T041. This does not promise simultaneous rank dr for all q original outputs: separate readout decoders must be priced, and recovering the complete response from fewer readouts needs a certificate such as T007.

<a id="t043"></a>

### T043 — Polynomial-basis descent with 2d−1 products per query

**Statement.** Let L=K[t]/f with monic f of degree d, and let K contain 2d−1 supplied distinct points. Every r-query L-provider for a K-valued response on K-inputs descends to a K-provider with at most (2d−1)r products, with O(rd²(m+n+q)) coefficient preprocessing and O(r(2d−1)(m+n+q)) online arithmetic.
**Proof.** Represent each query form by a polynomial of degree below d whose coefficients are K-linear input forms. Evaluate the two polynomials at the supplied points; their product polynomial has degree at most 2d−2 and is recovered by its explicit Vandermonde inverse. Reducing that product modulo f and multiplying each output coefficient w_a before taking the constant-coordinate projection are K-linear operations, so compose them with the interpolation decoder in preprocessing. The resulting products are evaluations of K-linear forms, and their decoded sum equals the original K-valued response by T041. For interpolation preprocessing, build the product of the 2d−1 linear point factors in O(d²) operations, divide it by each factor and normalize by its value at the corresponding point; these are the explicit Lagrange columns. The polynomial identity and these composed matrix operations prove the counts. Small fields require an additional priced extension, not unprovided interpolation points.

<a id="t044"></a>

### T044 — A computable trace projection without division by extension degree

**Statement.** Given an L/K basis with e_1=1 and invertible trace Gram matrix G_ij=Tr(e_i e_j), solve Gc=(1,0,…,0)^t and put τ=Σ_jc_je_j. Then φ(z)=Tr(τz) extracts the e_1 coordinate and fixes K. It can replace φ in T041–T043 without assuming d invertible. Gram computation and inversion use O(d^4) K-operations from the multiplication table.
**Proof.** The defining system gives Tr(τe_i)=δ_i1. Expanding z in the basis yields φ(z)=z_1; for z∈K this is z. Trace is obtained as the trace of the explicit multiplication matrix, so all Gram entries and c are computable. For finite fields L/F_q the Gram invertibility is itself justified: the polynomial X+X^q+⋯+X^(q^(d−1)) has degree below |L| and is nonzero, hence its trace function is not identically zero. For x≠0 choose z with nonzero trace and pair x with z/x. Thus the trace pairing is nondegenerate. No invalid normalization by 1/d is used.

<a id="t045"></a>

### T045 — Generator-commutation recovery of extension-linear maps

**Statement.** Let L=K(α) have a supplied power basis, and let A:L^m→L^n be K-linear with an explicit K-coordinate matrix. If A(αx)=αA(x) on every K-basis vector, then A is L-linear. Its L-matrix consists of the n-vectors A(e_j), and applying this recovered matrix costs at most 2mn L-operations. Checking generator commutation blockwise costs O(mnd³) K-operations for extension degree d.
**Proof.** The checked equality is a K-linear identity and therefore holds on every x. Inductively A(α^i x)=α^iA(x). Every c∈L is a K-linear combination of the power basis, so K-linearity gives A(cx)=cA(x). Finally x=Σ_jx_je_j implies A(x)=Σ_jx_jA(e_j), yielding the actual matrix. The checks and extraction use the supplied base-field representation, not a search for an unknown extension-linear frame. Inserting this recovered map into an F2 query contract requires the same matrix costs as any other adapter; its existence alone is not a decoder.

<a id="t046"></a>

### T046 — Two-graph descent with recovered nonzero private scalars

**Statement.** Let nonzero w_i∈L^n and a spanning family v_i of L^m be supplied. Suppose K-linear A and invertible K-linear b_i:L→L satisfy A(zv_i)=b_i(z)w_i and b_i(αz)w_i=αA(zv_i) for all K-basis z of L. Then b_i(z)=z d_i with d_i=b_i(1)≠0, and A is L-linear. All maps and d_i are recovered from their actual tables; a conservative preprocessing bound for t supplied columns and extension degree d is O(t(m+n+1)²(d+1)^5+(m+1)³(d+1)³) K-operations.
**Proof.** Extend the graph equations to all z by K-linearity. Substituting the first into the second and cancelling the nonzero vector w_i gives b_i(αz)=αb_i(z). Apply the scalar case of T045: b_i(z)=zb_i(1), with b_i(1) nonzero by injectivity. Thus A(zv_i)=zd_iw_i. Express any x as an L-linear combination of the spanning v_i and distribute A using these equalities, proving L-linearity and producing its matrix from a chosen independent subfamily. The graph checks are finite basis computations. This is a sufficient algebraic recovery contract, not a claim that projective-sector recognition or graph encoding is free.

<a id="t047"></a>

### T047 — Frobenius-fixed transporter entries give actual finite-field descent

**Statement.** Let L/F_q be an explicitly represented degree-d extension. If every entry z of recovered mode matrices satisfies z^q=z, those entries lie in F_q, so the same matrices and verified tensor identity are actual F_q transport data. Each fixedness check uses at most 2⌈log_2 q⌉ L-multiplications; coordinate extraction is explicit.
**Proof.** Every element of F_q satisfies X^q−X=0. This polynomial has degree q and a field polynomial has at most q roots, so these are all its roots in L. Each tested entry therefore lies in F_q. In a basis beginning with 1 its nonconstant coordinates are zero and its first coordinate is the desired field entry. Repeated squaring computes z^q within the bound. Invertibility and the tensor identities remain the same equalities, now over F_q. A matrix not passing these tests is not silently descended; in particular averaging its entries is not asserted to preserve invertibility or the tensor relation.

<a id="t048"></a>

### T048 — Good-prime specialization of rational query certificates

**Statement.** A rational provider and its adapter inverses have coefficients in Z[1/D]. For any supplied prime p not dividing D or any recorded adapter determinant numerator, coefficient reduction yields an exact F_p provider with invertible reduced adapters. Checking the prime restrictions and reducing the explicit tables costs polynomial time in their recorded integer lengths.
**Proof.** Reduction Z[1/D]→F_p is a ring homomorphism because D is a unit modulo p. Apply it coefficientwise to every verified finite-sum provider identity and every inverse-product identity. The equalities survive, and nonzero recorded determinant numerators remain nonzero by the hypothesis. Reduction of each stored numerator and denominator followed by a modular inverse supplies actual coefficients. Thus this specialization gives a usable finite-field motif, not a conclusion from an unspecified complex orbit. Its scope excludes the finitely many bad primes and makes no claim that an arbitrary small prime is admissible.

<a id="t049"></a>

### T049 — Newton lifting of an actual modular inverse adapter

**Statement.** Let s≥1 and p≥2 be integers. For an integer n-by-n matrix A and X with AX≡I mod p, the recurrence X′=X(2I−AX) doubles the certified inverse modulus. After ⌈log_2 s⌉ steps, reduction modulo p^s gives an inverse of A there, using at most 6n³⌈log_2 s⌉ modular arithmetic operations, plus initialization.
**Proof.** Put E=I−AX. Then AX′=(I−E)(I+E)=I−E², so divisibility of E by p^k implies divisibility of the new error by p^(2k). Starting at k=1 proves the target modulus by induction. Since det(A)det(X)=1 in the final commutative residue ring, det(A) is a unit; the adjugate formula then also gives the two-sided inverse property. Reducing entries after each step preserves the congruence and bounds operand lengths by O(s log p+log n) in schoolbook matrix products. Two dense products and a subtraction fit the count. The lifted inverse is an explicit recovery adapter for a fixed A. This theorem does not lift arbitrary tensor-isomorphism solutions; those additional nonlinear equations must still be verified independently.

<a id="t050"></a>

### T050 — Explicit power-basis change between scalar presentations

**Statement.** For monic irreducible f,g of degree d over K, let β∈K[t]/g satisfy f(β)=0, with 1,β,…,β^(d−1) linearly independent. Then h(t) mod f↦h(β) is an explicit K-algebra isomorphism. Its coordinate matrix and inverse cost O(d^4) preprocessing; each coefficient conversion costs at most 2d² K-operations.
**Proof.** Evaluation sends f to zero, so polynomial division shows it is well-defined on the quotient. Evaluation respects sums and products. The power-basis independence makes its d-column coordinate matrix invertible, hence the map is bijective and its inverse is recovered by elimination. Build powers using the supplied multiplication table and verify f(β)=0 before converting a certificate. Applying the isomorphism to all provider coefficients preserves each bilinear and decoder identity. This supplies the actual representation adapter needed to combine two finite-field query packages; merely knowing their fields have the same size would not provide those matrices or their cost.

## 6. Interpolation and residue interfaces with complete recovery

<a id="t051"></a>

### T051 — Coefficient-query supplier from sampled bilinear providers

**Statement.** Let B(t) be a bilinear map whose coefficient tensors are polynomials of degree at most D. Given D+1 distinct a_i∈K and exact providers of cost C_i for B(a_i), any requested coefficient [t^j]B(t) has a provider costing Σ_i C_i+2q(D+1), after O((D+1)³) preprocessing. All coefficients can be returned for at most 2q(D+1)² decoder operations.
**Proof.** The evaluation matrix V_ij=a_i^j is invertible: a polynomial of degree at most D vanishing at all D+1 points has that many distinct linear factors and must be zero. Invert V explicitly. For each fixed x,y and output coordinate, its coefficient vector equals V^−1 times its evaluated response vector. Compose the requested row of V^−1 with the actual response decoders, or apply it to all evaluated outputs. The equality holds simultaneously for every x,y because the coefficient tensors themselves obey the same identity. No evaluation point, field extension, or response recovery is left implicit.

<a id="t052"></a>

### T052 — Sparse-parameter recovery with a verified evaluation minor

**Statement.** Suppose B(t) has known exponent support E={e_1,…,e_s}. Given s explicit points for which M_ij=a_i^(e_j) is invertible, s evaluated providers suffice to recover every supported coefficient, with O(s³) preprocessing and at most 2qs operations for one selected coefficient. The support restriction must hold on the complete coefficient tensor.
**Proof.** Write B(t)=Σ_jt^(e_j)B_j. Evaluation gives an s-by-s linear system in the vector-valued B_j(x,y); multiply by the computed inverse M^−1. The same calculation on coefficient tables verifies the support and result universally. The determinant check is essential: different exponents can coincide as functions on a small field, so arbitrary distinct points do not suffice here. The action is a complete sparse-parameter common-label interface using fewer actual providers when this explicit minor exists, not an assertion that degree alone or a sparse-looking sample supplies such a decoder.

<a id="t053"></a>

### T053 — Parity-filtered recovery of bilinear coefficient labels

**Statement.** Assume 2 is invertible in K, deg B≤2D+1, and λ_0²,…,λ_D² are distinct. The even coefficient maps of B are recovered from E_i=(B(λ_i)+B(−λ_i))/2 by a D+1-point decoder in the variables λ_i². It needs 2(D+1) providers, at most 2q(D+1) averaging operations, and the interpolation costs of T051.
**Proof.** Expand B(t)=Σ_jt^jB_j. The paired sum cancels every odd j and equals Σ_k(λ_i²)^kB_(2k). Division by 2 is valid by hypothesis. The squared points are distinct, so the Vandermonde argument of T051 recovers all even maps with an explicit decoder. The construction is exact even when odd coefficient maps are large; no approximation or cancellation tolerance is used. It is applicable only when the consumer requests the even-labelled response, and claims no reduction in paired-query count before the displayed averaging and interpolation costs are compared with that consumer's incumbent.

<a id="t054"></a>

### T054 — Multigraded query recovery on an explicit product grid

**Statement.** For B(t_1,…,t_k) of individual degrees at most D_i, choose D_i+1 distinct points in K for each variable. With N=Π_i(D_i+1), the N evaluated bilinear providers recover any selected mixed coefficient with at most 2qN decoder operations. Decoder preprocessing costs O(Σ_i(D_i+1)³+N k).
**Proof.** Invert the univariate evaluation matrix in each variable. Applying those inverses one variable at a time recovers the complete coefficient tensor. For one selected multiindex, its decoder entry at a grid point is the product of the corresponding k univariate inverse entries; this follows by expanding the tensor product of the inverse matrices. Form these N products and use the resulting one row on the N response vectors, giving the counts. Labels are the entire grid tuples and the requested coefficient multiindex; different variables are not silently identified. This is useful when a degeneration needs a genuinely mixed coefficient, rather than a false univariate specialization that merges unrelated terms.

<a id="t055"></a>

### T055 — Characteristic-free jet recovery with priced truncated products

**Statement.** Let distinct a_i∈K have multiplicities m_i with Σ_i m_i=D+1. Evaluating a degree-D bilinear polynomial provider in K[ε]/ε^(m_i) at t=a_i+ε supplies enough jets to recover every coefficient. Each variable product in that jet evaluation uses at most m_i(m_i+1)/2 K-products; recovery is an explicit (D+1)-square linear solve, costing O((D+1)³) preprocessing. If S scalar coefficients describe the supplied polynomial query tables, truncated Horner forms all jet tables in O(S(D+1)²) further preprocessing.
**Proof.** Jet coefficients are defined by expansion in ε, so they use Hasse coefficients and no factorial division. If a polynomial has every supplied jet zero, it is divisible by each (t−a_i)^(m_i). These factors are coprime, so their product of degree D+1 divides it; its degree bound forces it to vanish. Hence the square jet-evaluation map is invertible and elimination constructs the decoder. Truncated multiplication uses exactly the index pairs u+v<m_i, whose number is m_i(m_i+1)/2. Expanding all linear forms and decoders in the same ring gives an explicit base-field implementation. Jet access is therefore constructed and charged, not assumed as an extra oracle.

<a id="t056"></a>

### T056 — Small-field coefficient queries with an explicit extension and descent

**Statement.** Over F_q, let f be a supplied monic irreducible polynomial of degree d with q^d≥D+1. A polynomial provider over F_q of degree D can be sampled at D+1 explicit distinct elements of L=F_q[t]/f and decoded there, then converted to an F_q provider by T041. If the sampled L-algorithm has R products, the resulting algorithm uses at most d²R base-field products.
**Proof.** Choose the first D+1 distinct coefficient vectors in the supplied power basis; they name distinct field elements. Polynomial identities defining the original provider remain identities after base change, so its evaluated circuits are valid over L. T051 returns the desired coefficient map; because the polynomial originally has F_q coefficient tensors, that map is F_q-valued on F_q-inputs. T041 therefore descends the actual algorithm. Irreducibility is verifiable by division against all monic polynomials of degrees 1 through ⌊d/2⌋; a reducible polynomial has a factor in that range. At most d²Σ_(i=1)^⌊d/2⌋q^i field operations suffice for these trial divisions up to a fixed universal constant. This finite verification and extension construction are charged preprocessing, not a polynomial-time factoring claim in varying q,d.

<a id="t057"></a>

### T057 — Signed convolution recovery from modular query suppliers

**Statement.** For integer vectors x,y of length n with |x_i|,|y_i|≤H, let pairwise coprime moduli m_j have product M>2nH². Exact modular suppliers for the ordinary convolution recover the full signed integer convolution by centred CRT. Extra work is O(sn) reductions and O(sn) multiplications/additions modulo M for s moduli, plus precomputed Bezout coefficients.
**Proof.** Each coefficient c_k=Σ_(i+j=k)x_i y_j has at most n terms, so |c_k|≤nH². CRT supplies its unique residue modulo M, and exactly one integer in (−M/2,M/2] has that residue and lies within the bound; it is c_k. Explicitly precompute M_j=M/m_j and its inverse modulo m_j, then combine Σ_j residue_j M_j inverse_j modulo M. Repeat for all 2n−1 output labels. Input reductions and every large-modulus combination are included. This proves a complete signed recovery interface, not a conclusion that modular suppliers alone already compute an integer product without reconstruction and carry charges.

<a id="t058"></a>

### T058 — Known-denominator response recovery from modular providers

**Statement.** Suppose a response z∈Q^q satisfies Dz∈Z^q and |Dz_k|≤A for known positive integers D,A. Given modular response suppliers at pairwise coprime m_j coprime to D, with product M>2A, exact z is recovered by multiplying each modular response by D, applying centred CRT, and dividing by D. Additional work is O(sq) modular operations plus q exact rational outputs.
**Proof.** Since D is invertible modulo each m_j, the promised modular value of z_k is well-defined from its denominator-dividing-D representation, and multiplying that response by D gives Dz_k modulo m_j. This does not license reducing an unrelated internal coefficient whose denominator is not a unit modulo m_j. CRT and the strict bound reconstruct the integer Dz_k uniquely. Division by the known D returns the original rational coordinate exactly, irrespective of whether its reduced denominator is smaller. This theorem applies to common-label rational readouts whose denominators are proved by the actual coefficient table. It does not allow a guessed denominator or skip the potentially large integer lengths of D and M; those are charged by T061–T070.

<a id="t059"></a>

### T059 — Unknown bounded denominators with explicit finite recovery cost

**Statement.** Suppose each reduced response is a/b with |a|≤A, 1≤b≤D, gcd(b,M)=1 and M>2AD. From its residue modulo M, enumerate b=1,…,D, take the centred residue of bz, and accept a reduced pair satisfying all bounds and its congruence. This returns the unique rational response with at most D modular products and gcd checks per coordinate.
**Proof.** The true denominator appears and its numerator lies in (−M/2,M/2), so it is found. If two accepted fractions have the same residue, M divides ab′−a′b, whose absolute value is at most 2AD<M. Hence that difference is zero; reduced fractions with positive denominators are equal. Every acceptance is checked directly. This is a sufficient executable recovery algorithm; its cost is polynomial in D, not necessarily in log D. It is therefore appropriate for a bounded motif denominator contract, not an unproved efficient general rational-reconstruction oracle. The actual denominator search must be included in any proposed savings.

<a id="t060"></a>

### T060 — Exact modular admission of a new rational bilinear table

**Statement.** Suppose D times every coefficient in three r-term provider tables is integral of absolute value at most H, and the desired tensor has integer coefficients bounded by H_0. Verify the provider against it modulo pairwise coprime moduli coprime to D with product M>2(rH³+D³H_0). Then it is an exact rational provider for all inputs.
**Proof.** Multiply the coefficient identity by D³. Each candidate coefficient is a sum of r integer triple products, of absolute value at most rH³, while the desired coefficient is D³ times an integer bounded by H_0. Their integer residual has absolute value at most E=rH³+D³H_0. Modular verification says M divides each residual. Since M>2E, every residual is zero. Divide by D³ to obtain the rational identity, then use bilinearity as in T006. The method checks every coefficient and supplies its explicit height bound; a few modular samples without that bound would not be this certificate. Its action is a deterministic, fully quantified admission gate for a proposed faster local table.

## 7. Integer encodings and explicit bit invoices

<a id="t061"></a>

### T061 — A complete schoolbook bit implementation of a rational provider

**Statement.** Suppose an integer-valued bilinear B has an explicit r-query rational provider with N stored coefficients, each numerator and positive denominator below 2^h in absolute value. On integer inputs of magnitude below 2^L, it has an exact implementation using at most 64(C+q)(K+1)² elementary bit operations after preprocessing, where C=2r(m+n+q)+r+q and K=2L+3(N+1)h+⌈log_2(mnr+1)⌉+5.
**Proof.** Multiply all coefficient denominators into D, so log_2D≤Nh. Clearing each coefficient by D gives integers of magnitude below 2^((N+1)h). Evaluate the cleared left and right forms, their products and cleared decoder with integer arithmetic; the final vector equals D³B. Triangle inequalities for m,n,r-term sums put every intermediate within K bits, including D³. Divide each output exactly by D³; divisibility follows from integer-valued B and the verified rational identity. Grade-school addition, multiplication and long division on K-bit operands each use at most 32(K+1)² elementary bit operations, so the displayed bound covers all C arithmetic operations and q final divisions. Preprocessing D and the N cleared coefficients is separately paid and uses at most 100N((N+1)h+1)² schoolbook bit operations; it is not hidden in the online count.

<a id="t062"></a>

### T062 — Explicit height and finite bit cost for recovered rational adapters

**Statement.** For an invertible integer n-by-n matrix A with entries at most 2^h in magnitude, its inverse has numerator and denominator magnitudes at most n!2^(nh). It can be constructed deterministically in at most 100n³n!(nh+n⌈log_2(n+1)⌉+1)² bit operations by determinant expansion, with no polynomial-time claim for varying n.
**Proof.** The determinant is a sum of n! signed products, each of magnitude at most 2^(nh), so |det A|≤n!2^(nh). Each adjugate entry is a signed (n−1)-minor, bounded by the same upper bound. The adjugate identity A adj(A)=(det A)I follows by expansion along a row, including the zero determinant with a repeated row. Thus adj(A)/det A is the actual inverse. Enumerating permutations to compute all n² minors uses fewer than n³n! integer multiplications/additions, with operand lengths bounded by nh+n log_2(n+1)+1; the generous constant covers signs and final rational entries. This is a usable fixed-motif preprocessing bound, and explicitly avoids mistaking it for polynomial bit complexity in arbitrary dimension.

<a id="t063"></a>

### T063 — Dyadic provider evaluation with a fixed denominator schedule

**Statement.** If all provider coefficients lie in 2^−h Z with cleared integer magnitudes at most H, inputs lie in 2^−L Z, and input magnitudes are below 2^M, each input form can be stored at scale 2^(h+L), every paired product at scale 2^(2h+2L), and every decoded output at scale 2^(3h+2L). No gcd normalization or data-dependent denominator search is needed.
**Proof.** Write each coefficient as an integer divided by 2^h and each input as an integer divided by 2^L. Each form is an integer sum over the common denominator 2^(h+L). Multiplying two forms multiplies their denominators, and multiplying by one output coefficient contributes one further 2^h. Summing decoder terms requires no further denominator. Store the three kinds of scaled integers and shift only when an interface explicitly demands a different scale. With cleared coefficient magnitude H, each form numerator is bounded by its input dimension times H times 2^(M+L), and the decoded numerator by r times the corresponding two form bounds times H. These exact bounds price every intermediate; dyadic arithmetic is not granted free rescaling or truncation.

<a id="t064"></a>

### T064 — A denominator certificate propagated through the actual query circuit

**Statement.** In a rational linear adapter whose edges have known denominators, assign input denominator D_i=1, scale-edge denominator bD_u, and sum-node denominator lcm(D_u,D_v). The resulting D_out makes every output integral after multiplication by D_out on integer inputs. Applying the same rule before and after a bilinear query, with product denominator D_uD_v, gives a complete exact denominator certificate.
**Proof.** Induct on the directed acyclic circuit. If D_uu is integral, multiplying u by a/b makes bD_u times the new value integral. If denominators D_u,D_v clear two values, their least common multiple clears their sum because both quotients are integers. Multiplication uses the product denominator. These statements prove the certificate at every node, not only at the endpoint. All lcm values are computed by gcd and exact integer multiplication; their bit costs are paid, and one may conservatively replace lcm by a product. This supplies the actual denominator depth that a source/precision contract needs; a small endpoint norm or tensor identity does not justify lowering it by itself.

<a id="t065"></a>

### T065 — Bit-priced extension multiplication from a supplied structure table

**Statement.** Let an integral d-dimensional algebra have structure constants |μ_ij^k|≤2^h. Multiplying coordinate vectors with |a_i|,|b_i|<2^L uses d² integer products and at most d³ constant products/additions. Every output coordinate has magnitude below d²2^(2L+h), and the operation has a schoolbook bit bound O(d³(2L+h+2log_2(d+1)+1)²).
**Proof.** Compute c_k=Σ_ij μ_ij^k a_i b_j. The d² products a_i b_j may be shared across output coordinates. Each summand has magnitude below 2^(2L+h), and there are d² of them, proving the output bound and the same bound for partial sums. Counting all constant multiplications and additions gives the stated field-to-bit conversion using long integer arithmetic. If the structure constants have denominators, first clear their actual common denominator and keep that output scale explicitly, as in T064. This is the concrete implementation charge for extension-based query suppliers; the degree d is not treated as a free scalar tag.

<a id="t066"></a>

### T066 — Balanced-radix recovery of signed convolution coefficients

**Statement.** For integer B≥2 and coefficients c_0,…,c_(N−1) with |c_i|<B/2, the integer Z=Σ_i c_iB^i determines them uniquely among such N-tuples. Repeated centred remainder and exact division recovers all coefficients in N divisions and O(N) integer additions. The quotient is zero after the last step.
**Proof.** The residue of Z modulo B has exactly one representative in the strict interval (−B/2,B/2), namely c_0; a possible tie at ±B/2 is excluded by the strict bound. Subtract c_0 and divide by B to obtain Σ_(i≥1)c_iB^(i−1). Induct to recover all coefficients and the terminal zero. For uniqueness apply this same first-coordinate argument to two representations and continue. This theorem supplies the signed carry convention required when Kronecker packing is used inside an integer child. Bounds of the form ≤B/2 without a declared tie rule are not covered.

<a id="t067"></a>

### T067 — Signed Kronecker compilation of a convolution provider

**Statement.** If integer input coefficients satisfy |x_i|,|y_i|≤H and have length n, choose B>2nH². Packing X=Σ_i x_iB^i, Y=Σ_i y_iB^i, multiplying them once, and using T066 recovers every ordinary convolution coefficient. Packed operands have bit length at most n⌈log_2B⌉+⌈log_2(H+1)⌉+2.
**Proof.** Distributivity in Z gives XY=Σ_k(Σ_(i+j=k)x_i y_j)B^k exactly. Each coefficient is bounded by nH²<B/2, so T066 recovers those labelled coefficients without sign ambiguity. The geometric sum bounds |X| by H(B^n−1)/(B−1), giving the displayed length bound, and the same holds for Y. Packing and unpacking take O(n) shifts/additions/divisions on these explicit integer lengths and must be charged around the one multiplication. This is a sufficient exact convolution child, not a claim that replacing arithmetic operations by packed multiplication is automatically a net improvement.

<a id="t068"></a>

### T068 — Nonnegative-limb convolution for arbitrary signed integer inputs

**Statement.** Let b≥1 be an integer, n≥0 an integer, and A,B signed integers with |A|,|B|<2^(nb). Extract the n ordinary base-2^b digits of |A| and |B|, compute their ordinary convolution, and propagate carries. Returning the product with sign sign(A)sign(B) gives AB exactly; sign handling and digit extraction/carry cost O(n+1) operations on O(nb+1)-bit integers, separately from the supplier; the conservative schoolbook bit bound is O((n+1)(nb+1)²).
**Proof.** Euclidean division gives |A|=Σ_i a_i2^(bi), with 0≤a_i<2^b, and the analogous expansion for |B|. Their product equals the weighted convolution by distributivity. At coefficient k, replace current value d_k plus incoming carry by its remainder modulo 2^b and its quotient; this preserves the represented integer. Induction through 2n positions gives the ordinary digits of |AB|, with a final carry if necessary. Apply the product sign; if either input is zero return zero. This explicit wrapper makes a positive-limb query supplier sufficient for signed inputs, with no identification of signed integers and modular residue labels.

<a id="t069"></a>

### T069 — A uniform bit invoice for multioutput CRT recovery

**Statement.** Let s pairwise coprime moduli have product M of at most B bits, and let q outputs have already supplied modular residues. Standard explicit CRT, including all Bezout preprocessing, uses at most 1000s(q+1)(B+1)³ bit operations and O(sB+qB) bits of storage. This is a sufficient upper bound for the reconstruction part of T057 or T058.
**Proof.** Compute each M_j=M/m_j by long division. Extended Euclid finds its inverse modulo m_j; every two Euclidean remainder steps at least halve the positive remainder, so there are at most 2B+2 steps. Each division or coefficient update uses O((B+1)²) grade-school bit work, and the Bezout coefficients can be reduced modulo m_j. For each output, sum the s terms residue_j M_j inverse_j modulo M, reducing after each multiplication; all operands then have O(B) bits. The generous stated bound covers these operations and storage of s coefficients plus q results. The bit cost is independent of an unproved unit-cost modular-arithmetic convention.

<a id="t070"></a>

### T070 — Polynomial-bit modular admission with an explicit height ledger

**Statement.** Under T060, suppose all cleared coefficients, D, moduli and their product have at most B bits. Complete modular admission of the r-term tensor over all mnq coefficients has a deterministic bit bound 10^4 s r mnq(B+⌈log_2(r+1)⌉+1)³, including reductions and modular inverses. Together with M>2(rH³+D³H_0), it certifies the exact rational provider.
**Proof.** Reduce each supplied coefficient and D modulo every modulus. Their number is at most r(m+n+q)+mnq≤(3r+1)mnq, since dimensions are positive. Modular inverses use the explicit Euclidean bound of T069. For each modulus and tensor coordinate, accumulate the r triple products, and compare with the reduced target times D³. All operations can be reduced immediately, so working integers have O(B+log(r+1)) bits. Multiply the number of loop iterations by the grade-school operation bound; the stated constant dominates reductions, signs and setup. Exact correctness follows from T060. Thus the certificate has a bit-level cost usable in a compiler invoice, not merely an arithmetic-operation count.

## 8. Exact finite extraction from restrictions and degenerations

<a id="t071"></a>

### T071 — A restricted provider with recovered embeddings and output projection

**Statement.** Given explicit E:K^a→K^m,F:K^b→K^n and P:K^q→K^c, a provider for B gives one for C(ξ,η)=PB(Eξ,Fη), with the same r products and forms u_aE,v_aF, decoder Pw_a. Precomposing these tables costs O(r(ma+nb+qc)); online cost is at most 2r(a+b+c)+r.
**Proof.** Substitute Eξ,Fη into the original expansion and apply P. Matrix multiplication gives exactly the displayed forms and decoder, so no full m- or n-vector need be materialized online. This coefficient identity proves C for all ξ,η. The smaller dimensions are legitimate only because the consumer's declared input and output maps are these actual E,F,P; one cannot restrict arbitrary dirty coordinates merely to improve the bill. The theorem supplies a complete executable restriction certificate, with its table construction and reduced online adapters priced, rather than treating tensor restriction as an unimplemented existential operation.

<a id="t072"></a>

### T072 — Exact finite recovery from a polynomial border certificate

**Statement.** Suppose polynomial query tables give F(t)=t^aB+terms of degrees above a, with 0≤a≤D, degree at most D and r products at each evaluation. With D+1 distinct field elements, B has an exact provider with at most (D+1)r products, plus the actual evaluated linear-table work and a q-by-(D+1) coefficient decoder.
**Proof.** The hypothesis says [t^a]F=B as an identity of complete bilinear coefficient tensors. Evaluate the displayed polynomial tables at the supplied points; these are actual field providers for F at those points. T051 constructs the coefficient row that extracts [t^a]F from all responses. Compose it with their decoders. No limit, infinitesimal evaluation or numerical rounding appears. This is the finite sufficient transfer from a border-style construction to an exact provider; the multiplicative factor D+1 and all input/output adapters are real costs. It does not assert that border rank r is already exact rank r.

<a id="t073"></a>

### T073 — Leading-coefficient recovery by explicit nilpotent arithmetic

**Statement.** For a polynomial r-query identity whose coefficient at degree a is B, evaluating its tables modulo ε^(a+1) and extracting ε^a yields an exact K-provider using at most r(a+1)(a+2)/2 base-field variable products. Constant-table multiplication and decoding cost O(rq(a+1)²), with input-form work O(r(a+1)(m+n)).
**Proof.** Expand each left and right query as Σ_(i=0)^a ε^i u_i and Σ_(j=0)^a ε^jv_j. The degree-at-most-a product coefficients use precisely i+j≤a, giving the triangular number of variable products. Multiplication by the output coefficient polynomial and extraction of degree a is a fixed K-linear decoder on those products. Since evaluation in K[ε]/ε^(a+1) is a ring homomorphism, its degree-a output equals the true coefficient B; terms of higher degree vanish harmlessly. This constructs every jet used by the algorithm and requires no factorial division, so it works in every characteristic. Nilpotent-ring operations are not left unpriced as scalar queries.

<a id="t074"></a>

### T074 — Finite tensor-power extraction from a border supplier

**Statement.** If F(t) in T072 has leading term t^aB and degree D, the kth tensor power gives B^⊗k with at most (kD+1)r^k variable products whenever K contains kD+1 supplied distinct points. Input/output dimensions and their evaluated adapters are the full kth powers.
**Proof.** Expanding F(t)^⊗k, every factor has least possible degree a; the only way to obtain degree ka is to choose its leading B from every factor. Thus [t^(ka)]F(t)^⊗k=B^⊗k, and the total degree is at most kD. T016 constructs the r^k-query evaluated tensor-product tables, including their paired labels. Apply T051 with kD+1 points to recover the indicated coefficient. This proves the finite count and exact output. The algorithm pays tensor-coordinate access, all enlarged forms and the coefficient decoder; no unproved asymptotic sum inequality or free recovery is used.

<a id="t075"></a>

### T075 — Single-parameter encoding of multigraded response labels

**Statement.** Suppose the complete coefficient support of B(t_1,…,t_k) lies in 0≤e_i≤D_i. Put W_1=1,W_i=Π_(j<i)(D_j+1), N=Π_i(D_i+1), and substitute t_i=z^(W_i). Each mixed coefficient retains a unique exponent in {0,…,N−1}; N univariate samples recover it with T051. Computing the parameter powers costs O(Σ_i log(W_i+1)) multiplications per sample.
**Proof.** The exponent becomes E=Σ_i e_iW_i. Repeated Euclidean division by D_i+1 recovers the unique digits e_i, proving injectivity and the bound E<N. Therefore no different mixed coefficient is merged by this substitution. Evaluate the original actual tables at those powers, then use the univariate coefficient decoder at E. Repeated squaring gives the stated parameter-generation cost, which is additional to each supplier invocation. This is useful when the source contract exposes only one parameter label; it does not claim fewer total queries than a full product grid or permit unbounded supports that would collide under the encoding.

<a id="t076"></a>

### T076 — Character-filtered coefficient decoder with explicit roots of unity

**Statement.** Let ω∈K have exact order N, assume N invertible, and deg F<N. Then for 0≤j<N, [t^j]F=N^−1Σ_(i=0)^(N−1)ω^(−ij)F(ω^i). This gives an exact N-invocation bilinear supplier with at most 2qN decoder operations for one coefficient; root tables are paid preprocessing.
**Proof.** For monomial t^k the weighted sum is N^−1Σ_i(ω^(k−j))^i. It is 1 when k=j; otherwise the geometric-series identity gives zero, because ω^(k−j)≠1 for 0≤j,k<N and its Nth power is 1. Extend by linearity to every coefficient tensor. Generate the roots and decoder weights explicitly, checking exact order and invertibility of N. The formula acts on parameter-response labels, not on the cover label Γ in PR #2855's mixed norm. If such a transform is inserted on an actual cover bank, the stronger source/norm conditions must be established separately; this theorem licenses only the stated query decoder.

<a id="t077"></a>

### T077 — Laurent-certificate recovery with all pole shifts charged

**Statement.** Suppose actual query tables define F(t) with exponents from −s through D and [t^0]F=B. With D+s+1 supplied distinct nonzero field elements, B is recovered from those evaluated providers by extracting coefficient s of t^sF(t). Each evaluated response requires one extra scaling by its sample's t^s.
**Proof.** Multiplication by t^s makes the complete response a polynomial of degree at most D+s, whose coefficient at s is B. At a nonzero sample all Laurent table entries are defined; scale the returned response by that sample's sth power to obtain the polynomial value. Apply T051 to its full coefficient table. Parameter powers, inverse powers in the query tables, response scaling and interpolation are all finite operations and must be charged. Zero is excluded from the supplied sample set, so no step substitutes a singular parameter into a Laurent expression or hides a limiting argument in the decoder.

<a id="t078"></a>

### T078 — Rational-parameter supplier with deterministic pole avoidance

**Statement.** Let F(t)=P(t)/Q(t) be a bilinear response with known scalar polynomial Q, deg P≤D and Q(0)≠0. From D+deg Q+1 supplied distinct points, at least D+1 are not poles. Evaluating there, multiplying by Q at each sample and applying T051 recovers P(0), hence F(0), with one final division by Q(0).
**Proof.** A nonzero polynomial Q has at most deg Q roots; the surplus points therefore leave enough valid samples. Compute Q at every proposed point and discard only actual zeros. At accepted points the provider gives F, and multiplying by Q gives P exactly. Interpolation recovers the coefficient at zero, and the nonzero Q(0) permits division. This returns a complete endpoint provider with its actual field-size requirement, rejected-point tests, response scalings and decoder priced. It does not extend the claim to Q(0)=0 or assume that an arbitrary finite sample set avoids denominators.

<a id="t079"></a>

### T079 — Integral top-coefficient recovery by finite differences

**Statement.** For an integer-coefficient bilinear polynomial response F(t) of degree at most D, its top coefficient is D!^−1Σ_(i=0)^D(−1)^(D−i)binom(D,i)F(i). The numerator is coordinatewise divisible by D!. This gives a division-exact integer decoder with weights of magnitude at most 2^D and D+1 actual provider calls.
**Proof.** For k≥1, applying the forward difference Δ to a degree-k polynomial lowers its degree to k−1 and multiplies its leading coefficient by k. Iterating D times annihilates degrees below D and sends t^D to D!. Expanding Δ^D=(shift−I)^D gives the displayed signed binomial sum. Apply this identity to every bilinear coefficient and hence to every integer input response. The exact division follows from that coefficient identity, not from rounding. The bounded integer weights and one known exact division give a denominator-controlled compiler interface distinct from treating a general interpolation inverse as free rational arithmetic.

<a id="t080"></a>

### T080 — Division-free extraction of a mixed multilinear response

**Statement.** Let F(t_1,…,t_k) be multilinear in its parameters, with bilinear input/output coefficients. Then its full mixed coefficient is Σ_(S⊆[k])(−1)^(k−|S|)F(1_S). This uses 2^k evaluated providers and at most q(2^k−1) additions/subtractions, with no divisions or extension-field samples.
**Proof.** For parameter monomial Π_(i∈A)t_i, the evaluation at 1_S is 1 exactly when A⊆S. Its signed sum is (−1)^(k−|A|)(1−1)^(k−|A|), zero unless A=[k], when it is 1. Extend over the actual bilinear coefficient table. The identity has integer coefficients and therefore remains valid in characteristic 2, where the signs coincide but cancellation is still encoded by 1−1=0. This provides a concrete small-field mixed-term decoder with known memory and arithmetic costs. The multilinear support certificate is indispensable; repeated powers would make Boolean samples identify different terms.

## 9. Bounded families with actual recovery algorithms

<a id="t081"></a>

### T081 — One-unknown-mode transporter recovery by a full-rank linear system

**Statement.** Fix two actual invertible mode maps between explicit tensors. The remaining n-by-n map has n² unknown entries and a linear coefficient system. If this system has full column rank and is consistent, elimination returns its unique map G; if det G≠0 it is the actual missing transporter. After the two known mode contractions are explicitly paid by T040, dense linear recovery costs O(E n^4+n^6) field operations for E scalar equations, followed by full T040 verification.
**Proof.** Expand the tensor action with the two fixed maps substituted. Every coefficient is a known linear combination of the entries of G. Gaussian elimination on the explicit E-by-n² system either rejects inconsistency or gives the unique solution under full column rank. Test its determinant and then verify the full transported tensor. When these checks pass, the actual invertible triple is returned, giving an executable F1 adapter by T021. The theorem requires no unknown nonlinear tensor-recovery oracle and does not infer a solution merely because some unconstrained three-mode isomorphism exists.

<a id="t082"></a>

### T082 — Two-sided slice transporter recovery through a simultaneous intertwiner

**Statement.** Given labelled square matrix families A_i,B_i with A_0,B_0 invertible, all solutions P A_i Q=B_i with P,Q invertible are recovered from invertible solutions of P(A_iA_0^−1)=(B_iB_0^−1)P by Q=A_0^−1P^−1B_0. Linear-system construction and elimination cost O(k n^6) field operations for k slices, plus the explicit nonsingularity search of T083 when needed.
**Proof.** From the equation at i=0 solve for Q. Substitution into every other equation gives the displayed intertwiner equations, which are linear in the n² entries of P. Conversely an invertible solution P of those equations and the stated Q satisfy every original slice equation by multiplication. Recover the full affine solution space by elimination; apply a supplied invertible solution or T083's finite construction, then compute Q and check all labelled slices. No slice permutation or output-mode mixing is inferred: the source contract fixes the same labels i on both families. The returned maps and their application costs are explicit.

<a id="t083"></a>

### T083 — Finite nonsingular-point recovery inside a known affine solution space

**Statement.** Let P(t)=P_0+Σ_(j=1)^d t_jP_j be an explicit affine n-by-n matrix family over a field containing n+1 supplied distinct elements. If det P(t) is not the zero polynomial, exhaustive evaluation on their d-fold product grid returns an invertible P in at most (n+1)^d determinant tests and O(n³(n+1)^d) operations.
**Proof.** A nonzero polynomial of individual degrees at most n cannot vanish on that whole grid. Prove this by induction on d: expand in the last variable; if it vanished at every last-variable point for each preceding grid tuple, the univariate root bound would make every coefficient vanish on the smaller grid, and induction would make every coefficient polynomial zero. The determinant has individual degrees at most n by its permutation expansion, so one grid point has nonzero determinant. Test points in lexicographic order and return the first. This is an explicit bounded-dimension recovery theorem; it is not polynomial in unbounded d and does not manufacture an invertible point when the determinant polynomial is identically zero.

<a id="t084"></a>

### T084 — Constructive determinant correction from actual stabilizer generators

**Statement.** Over F_q, let G be an actual three-mode transporter and let S_1,…,S_t be verified source-tensor automorphisms. Breadth-first search in (F_q^×)^3 using their determinant triples and inverses returns a word S with det(S_i)=det(G_i)^−1 whenever that triple is in the generated subgroup. Then GS is an actual SL transporter. At most (q−1)^3 character states and at most 2t(q−1)^3 directed generator edges are examined, counting inverse generators.
**Proof.** A product of source automorphisms is still a source automorphism; its determinant triple is the product of their triples. BFS records, for each reached state, an actual generator word realizing it. If the target triple is reached, multiply its recorded mode matrices to obtain S, and compose with G. The source tensor is fixed by S, so GS transports it to the target, while determinant multiplicativity gives determinant 1 in every mode. Character enumeration and matrix-word multiplication are charged. No completeness of the supplied stabilizer generators, reverse TI reduction or efficient recovery from an orbit decision is asserted.

<a id="t085"></a>

### T085 — Simultaneous query frames from one simple-spectrum combination

**Statement.** Suppose commuting n-by-n matrices A_1,…,A_k are supplied with a combination D=Σ_j c_jA_j having n supplied distinct eigenvalues in K. Kernel computations return an eigenbasis U that diagonalizes every A_j. Cost is O(n^4+kn³), plus eigenvalue verification, and every joint eigenlabel is computed explicitly.
**Proof.** Each eigenspace of D is one-dimensional, and eigenvectors for its n distinct eigenvalues are independent: applying ∏_(μ≠λ)(D−μI) isolates each coefficient in a dependence. Commutation gives D(A_jv)=A_jDv=λA_jv, so A_j preserves each eigenline. Compute a nonzero vector in every kernel D−λI, assemble U and extract the diagonal entries of U^−1A_jU. These are actual common labels, not a guessed simultaneous diagonalization. Source and target joint-label lists may be matched explicitly; only a matched list licenses the corresponding frame transporter, whose applications are still priced.

<a id="t086"></a>

### T086 — Scalar normalization of an actual transporter with recovered roots

**Statement.** For equal positive mode dimension n, let actual invertible G_1,G_2,G_3 transport a nonzero tensor. If nonzero a,b satisfy a^n=det G_1, b^n=det G_2, det G_1 det G_2 det G_3=1, put c=(ab)^−1. Then a^−1G_1,b^−1G_2,c^−1G_3 are actual SL transporters. Over F_q, a,b can be searched explicitly in at most (q−1)² trials.
**Proof.** From the determinant-product equation, c^n=(a^nb^n)^−1=det G_3. Scaling an n-by-n matrix by a^−1 divides its determinant by a^n, so each normalized determinant is 1. The trilinear tensor action is scaled overall by (abc)^−1=1, so the transported tensor is unchanged. Evaluate the two power equations by repeated squaring in each finite-field trial, charging O(log n) operations per test and the final matrix scalings. Roots must lie in the stated field and are returned explicitly. The inspected project's power certificates are a scope guide; this does not identify general GL and SL orbits.

<a id="t087"></a>

### T087 — Annihilator compression that preserves every allowed input

**Statement.** For explicit B:K^m×K^n→K^q, compute its left annihilator L={x:B(x,y)=0 for every y}. Elimination yields P:K^m→K^a with kernel L and a section E with PE=I. Then B(x,y)=B(EPx,y); a provider for C(ξ,y)=B(Eξ,y) computes B after the paid input map P.
**Proof.** Stack the q-by-m matrices of B(·,e_j); their common kernel is exactly L by bilinearity. Choose a complementary basis E and define P to read its complement coordinates, giving PE=I and ker P=L. For each x, P(x−EPx)=0, so x−EPx∈L and B(x−EPx,y)=0 for all y. Rearrangement proves the identity. All original x, including arbitrary annihilator components, are accepted. The result changes the response's source-coordinate interface through an explicitly computed quotient; it does not authorize overwriting protected operands or assuming dirty spectator coordinates vanish.

<a id="t088"></a>

### T088 — Constructing a complete decoder for fixed query-form templates

**Statement.** Given fixed left forms u_a and right forms v_a, form M_(i,j),a=u_a,i v_a,j. A target tensor has an r-query provider with these forms whenever the explicit systems M w_k=T_(·,·,k) are consistent for every k. Solving them returns all decoder columns, in O(mnr²+qr²+qmn r) field operations.
**Proof.** For unknown output coefficients w_a,k the provider identity at basis pair (i,j) is exactly the stated linear system. Eliminate M once, apply the recorded row operations to each target column, and back-substitute or choose zero values for free variables. The returned coefficients satisfy every basis-pair identity, so T006 proves the universal provider. The counts are conservative rectangular elimination and repeated right-hand-side bounds. This is a constructive completion theorem for a declared query template and exact labels; it does not promise that arbitrary short templates exist or hide the decoder in an assumed recovery gadget.

<a id="t089"></a>

### T089 — Rational motif recovery guided by a certified modular pivot

**Statement.** Let A z=b be an integer linear system with n unknowns. If an explicit n-row minor is nonzero modulo a supplied prime p, it is nonzero over Q. Solve that square subsystem over Q and verify all remaining rows. If they pass, the returned z is the unique full rational solution; if entries of A,b are bounded by H, each coordinate has numerator and denominator at most n!max(1,H)^n.
**Proof.** A determinant divisible by p could reduce to zero, so the nonzero modular determinant implies the integer determinant is nonzero. Cramer's rule returns each coordinate as the determinant with one column replaced by b divided by that minor. The permutation expansion gives the stated bound on both determinants. A full solution must agree with the square subsystem's unique solution; checking the other rows proves sufficiency. The finite modular pivot therefore selects actual rational recovery coordinates rather than asserting arbitrary modular transporters lift. Arithmetic and bit implementation can use T062 or a separately priced faster exact solver.

<a id="t090"></a>

### T090 — Uniform polynomial transporter certification with an explicit good specialization

**Statement.** Suppose polynomial mode matrices in s parameters have tensor-identity residuals of individual degrees at most D. Verifying every residual on a (D+1)^s product grid proves the identity for all parameters. If the product of their determinants is a nonzero polynomial of individual degrees at most E and K contains E+1 explicit points, a second grid search returns a nonsingular actual transporter.
**Proof.** Apply the multivariate grid argument of T083 to each residual polynomial: zero evaluations on the complete grid force that polynomial to vanish identically. The same argument applied to the nonzero determinant product guarantees a nonzero evaluation on the second grid. Test those points and return the actual matrices at the first successful one. The first stage proves correctness of the complete family, while the second supplies invertibility and actual recovery data. Both exponential grid sizes, table evaluations and T040-style checks are paid finite work; no genericity oracle, random success claim or free specialization is used.

## 10. Concrete changed providers and exact integer assembly

<a id="t091"></a>

### T091 — A fully labelled seven-child matrix-block provider

**Statement.** Over any associative ring, two 2-by-2 block matrices multiply using seven ordered block products and eighteen block additions/subtractions. The four original output blocks are recovered exactly by the formulas below, so a consumer with a verified matrix-block restriction can replace eight child products only after charging those additions and its adapters.
**Proof.** For inputs (a,b;c,d) and (e,f;g,h), compute M1=(a+d)(e+h), M2=(c+d)e, M3=a(f−h), M4=d(g−e), M5=(a+b)h, M6=(c−a)(e+f), M7=(b−d)(g+h). Return (M1+M4−M5+M7, M3+M5; M2+M4, M1−M2+M3+M6). Distribute each ordered product: the four sums reduce respectively to ae+bg, af+bh, ce+dg, cf+dh, since all other ordered monomials cancel with their signs. No commutation is required. The seven preparations use ten additions and the decoder eight. This is Strassen's classical identity with its actual common output labels and full linear-work invoice, not a fresh global κ claim.

<a id="t092"></a>

### T092 — Cyclic convolution provider with charged radix-two Fourier maps

**Statement.** Let L be a power of 2, invertible in K, and ω have exact order L. Cyclic convolution of length L has a provider using L variable products and at most 6L log_2L+2L additional arithmetic operations, with explicit Fourier input and inverse-output maps and O(L) working cells.
**Proof.** Define F(x)_j=Σ_i x_iω^(ij). The geometric-series identity gives F^−1(z)_i=L^−1Σ_jz_jω^(−ij). Expanding products shows F(x∗y)_j=F(x)_jF(y)_j, so pointwise multiplication and the inverse recover all cyclic labels. For the operation bound split inputs into even and odd indices: F(x)_j=F_even(j)+ω^jF_odd(j), and its paired frequency j+L/2 uses subtraction. Each level uses at most 3L/2 operations; recursion depth is log_2L. Apply two forward and one inverse transform, plus L inverse scalings and L products, bounded by the stated generous count. Twiddle tables and roots are explicit preprocessing. These are parameter/address transforms, not an unlicensed mixing of cover fibres.

<a id="t093"></a>

### T093 — Ranked subset-convolution query supplier over every commutative ring

**Statement.** For functions f,g on subsets of an n-element set, their disjoint subset convolution h(S)=Σ_(A⊔B=S)f(A)g(B) is computed with at most (n+1)(n+2)2^n/2 variable products and O((n+1)²2^n) additions, without division. All subset output labels are retained.
**Proof.** Set f_i(A)=f(A) when |A|=i and zero otherwise, and compute F_i(S)=Σ_(A⊆S)f_i(A) by the subset zeta butterfly; define G_i likewise. Form H_k(S)=Σ_(i+j=k)F_i(S)G_j(S), then apply the inverse zeta butterfly, subtracting along each element, to obtain h_k(S). Expanding gives a coefficient Σ_(A∪B⊆T⊆S)(−1)^(|S−T|), equal to 1 when A∪B=S and zero otherwise. Thus h_|S|(S) keeps exactly pairs with A∪B=S and |A|+|B|=|S|, equivalent to disjointness. Count all i,j with i+j≤n and all subset labels for the product bound; the forward/inverse butterflies cost O(n²2^n). This offers an explicit alternative query interface when a native contraction is actually identified with disjoint-subset convolution; that identification and its adapters must be supplied.

<a id="t094"></a>

### T094 — XOR-convolution supplier with exact Walsh recovery

**Statement.** Over K with 2 invertible, XOR convolution on {0,1}^k uses N=2^k variable products, three Walsh transforms, and one inverse scaling. Its linear arithmetic cost is at most 3kN+N; working storage is O(N). It returns every original address label exactly.
**Proof.** The characters χ_s(x)=(−1)^(s·x) satisfy χ_s(x+y)=χ_s(x)χ_s(y). Summing χ_s(x) over s gives N when x=0 and zero otherwise, by factoring into k two-term sums. Hence W²=NI and W(f∗g)=(Wf)(Wg), proving the provider. Each butterfly computes a+b and a−b on a pair, so one transform costs kN additions/subtractions; the inverse additionally multiplies N entries by N^−1. The transform is on the specified selected-bit function domain. It does not authorize applying a dense Walsh map to the independent cover index Γ, which would violate PR #2855's fibre-monomial premise unless a separate norm contract were proved.

<a id="t095"></a>

### T095 — Sparse-support polynomial multiplication with a support-certified decoder

**Statement.** Suppose polynomial inputs have known exponent supports A,B⊂N. Put E=A+B, s=|E|. If s supplied nonzero points make the generalized Vandermonde on E invertible, their s pointwise products recover the complete product coefficient vector on E, with O(s³) decoder preprocessing and O(s(|A|+|B|)+s²) online arithmetic.
**Proof.** Multiplying the inputs produces only exponents a+b∈E. At each sample evaluate both sparse sums and multiply once. The resulting s values are exactly the generalized Vandermonde times the s product coefficients. Apply its verified inverse to recover every labelled coefficient, including zero coefficients from cancellations. Computing sparse powers belongs to preprocessing or is added to the displayed evaluation work if samples change. The determinant test is required over small fields; distinct points alone do not imply this generalized matrix invertible. This is a concrete support-sensitive provider, not a claim that an arbitrary sparse product can be recovered from too few evaluations without checking exponent collisions.

<a id="t096"></a>

### T096 — Symmetric bilinear recovery from an explicit quadratic circuit

**Statement.** Let 2 be invertible and B symmetric bilinear. If its diagonal Q(x)=B(x,x) has an explicit decomposition Q(x)=Σ_(a=1)^r ℓ_a(x)m_a(x)w_a, then B has a provider with at most 2r products, namely half the sum of ℓ_a(x)m_a(y)+ℓ_a(y)m_a(x). Terms with ℓ_a=m_a require only one product each.
**Proof.** Symmetry gives Q(x+y)−Q(x)−Q(y)=2B(x,y). Expanding the supplied quadratic circuit gives exactly the cross terms displayed. Divide the decoder coefficients by 2 during preprocessing. If the two forms coincide, the two cross products coincide and their half-sum is their single product. Thus all left/right forms and complete output vectors are explicit and their evaluations are charged. This permits an actual symmetric motif to exploit a short quadratic certificate; it does not recover a general bilinear map from its diagonal, and in characteristic 2 the required polarization implication is not asserted.

<a id="t097"></a>

### T097 — Short-long convolution through overlap-add with all boundary labels

**Statement.** Let x have length n≥m and y length m, and suppose a length-m ordinary convolution supplier is given. Partition x into k=⌈n/m⌉ consecutive blocks, padding only the last. Then k supplier calls plus fewer than 2mk coefficient additions recover the full n+m−1 convolution. The padding and output accumulation are explicit, with no hidden common-width input promise.
**Proof.** Write x(t)=Σ_(b=0)^(k−1)t^(bm)x_b(t), each x_b of degree below m. Distributivity gives x(t)y(t)=Σ_b t^(bm)(x_b(t)y(t)). Run the child on each actual block and y, then add each of its at most 2m−1 output coefficients at the shifted position bm+j. Every product term of x and y appears in exactly its original block, while overlaps are summed, proving all boundary outputs. Last-block zero padding is a read adapter, not a demand that the user supply padding. This offers a finite unequal-length bit-supplier contract with k rather than k² balanced children and separately paid accumulation/carry work.

<a id="t098"></a>

### T098 — Exact Montgomery residue child from integer products

**Statement.** Let M≥3 be odd, R=2^b>M, and precompute M′≡−M^−1 mod R. For 0≤a,b_0<M, put t=ab_0, m=tM′ mod R, u=(t+mM)/R. Then u<2M and u≡ab_0R^−1 mod M; at most one subtraction of M gives the canonical residue. It uses three integer products, shifts/remainders by R and one conditional subtraction.
**Proof.** By the definition of m, t+mM≡t−t=0 mod R, so the division is exact and is a binary shift. Also t<M² and m<R give u<(M²+RM)/R<2M. Reducing Ru=t+mM modulo M gives the residue formula; R is invertible modulo odd M. Precomputing M′ uses extended Euclid and is charged once. This is a genuine scaled residue interface: callers must encode a as aR mod M or pay conversions, and decoded output requires its corresponding conversion. No ordinary field multiplication is silently replaced by a scaled residue with the wrong labels.

<a id="t099"></a>

### T099 — Exact fixed-modulus reduction through a bounded reciprocal

**Statement.** Let M≥2 have bit length b and precompute μ=⌊2^(2b)/M⌋. For 0≤x<M², set q=⌊xμ/2^(2b)⌋ and r=x−qM. Then 0≤r<2M; one conditional subtraction yields x mod M. Online work is two integer products, one binary shift, subtraction and comparison, with product operand lengths at most 2b and b+2.
**Proof.** Write 2^(2b)/M=μ+δ with 0≤δ<1. Then x/M−xμ/2^(2b)=xδ/2^(2b)<M²/2^(2b)≤1. Consequently q≤⌊x/M⌋≤q+1. Substituting in r proves the interval and the one-subtraction result. The multiplier μ has at most b+2 bits since M≥2^(b−1), with equality possible at the power-of-two boundary, and x has at most 2b bits. Precomputing the reciprocal by one exact division and paying both online products gives a usable modular-field implementation cost, rather than counting quotient extraction as a free machine operation.

<a id="t100"></a>

### T100 — Complete NTT–CRT–carry contract for an integer multiplication child

**Statement.** Let n,b≥1, H=2^b−1, L a power of 2 with L≥2n−1, and supplied distinct odd primes p_j have supplied exact-order-L roots and product M>2nH². Signed integers below 2^(nb) in magnitude multiply exactly by nonnegative limb extraction, L-point modular convolution in each prime, centred CRT and carries. Each prime needs at most 6L log_2L+3L field operations; all CRT and carry costs are those of T069 and T068, and modular operations may use T098 or T099.
**Proof.** Extract ordinary magnitude limbs as in T068 and pad to length L. T092 computes cyclic convolution modulo each prime. Since the ordinary product has degree at most 2n−2<L, no coefficient wraps, so these are residues of the ordinary integer convolution. Its coefficients are bounded by nH², and T057 recovers them uniquely because M>2nH². Carry propagation and the product sign then return the exact signed integer product. Root order is checked by ω^L=1 and, for L>1, ω^(L/2)≠1, which suffices for a power of 2; L=1 is checked separately. Prime/root generation, twiddle tables, input reduction and residue conversion are paid preprocessing or supplied certified data. Thus no unproved fast prime generator, decoder, integer lift or all-size complexity transfer is hidden in this sufficient contract.

## Uncounted source and application boundary

The numbered results are new application contracts in this document, not claims that their underlying tensor identities, interpolation, CRT, linear algebra, or integer arithmetic are new. Classical provenance includes [Strassen’s 1969 paper, official reprint](https://direct.mit.edu/books/edited-volume/chapter-pdf/2248378/9780262363174_c002900.pdf), [Conrad’s finite-field notes](https://kconrad.math.uconn.edu/blurbs/galoistheory/finitefields.pdf), [Conrad’s trace and norm notes](https://kconrad.math.uconn.edu/blurbs/galoistheory/tracenorm.pdf), and [Bini’s author bibliography on exact and approximate bilinear algorithms](https://people.dm.unipi.it/bini/Ricerca/Papers/pub77-89.html). The modern [Designing Strassen’s algorithm](https://arxiv.org/abs/1708.09398) supplies additional primary perspective on that classical construction. All numbered proofs here are explicit rather than appeals to an unstated theorem from those references.

A conditional cost improvement means exactly this: the theorem's actual constructed provider/decoder/recovery replaces a named accepted interface at a strictly smaller complete symbolic charge, with every stated domain and source condition retained. This document does not assert that all 100 substitutions simultaneously improve the current finite source, that a bare bilinear decomposition implements a native linear operator, or that the fixed-inventory packing optimum has been exceeded. The canonical Lean/DAG tree is unchanged. No new numerical κ is claimed.
