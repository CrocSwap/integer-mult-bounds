# Physical phase controllers: 100 sufficient construction theorems

This volume contains P001–P100, all **informally proved**. It gives finite mathematical constructions and exact counts in declared alphabets, not a new numerical κ, an admitted supplier, a novelty claim, a Lean development or a quantum hardware experiment. Generic Weyl identities are uncounted background. Every numbered result supplies a returned-bank consumer, a corrected order, an encoded endpoint, a legal reuse/routing plan or a fully specified finite realization. Classical reconstructions and frontier-specific adaptations are distinguished in the index.

## Shared domain, conventions and cost units

Write F₂ for the two-element field. A data label d and a bank label c range over F₂ⁿ and F₂ᵇ. The state space is the full complex vector space with basis |d,c⟩; its coefficients may be arbitrary and correlated. Every identity is an equality on this entire space unless a support promise is stated explicitly. There is no prepared bank, erased address lane or separability assumption. Empty matrices and zero-dimensional banks have their literal identity meanings.

Controls a(d), b(d) take values in F₂ᵇ and remain unchanged while their instructions execute. Define Sₐ|d,c⟩ = (−1)^{a(d)·c}|d,c⟩, T_b|d,c⟩ = |d,c+b(d)⟩, and D_q|d,c⟩ = (−1)^{q(d)}|d,c⟩. A chronological W(a,b) executes Sₐ then T_b. Chronological notation is used throughout: the leftmost listed instruction runs first. Thus W acts as (−1)^{a·c}|d,c+b⟩. Products of matrices, when used, retain their usual rightmost-first meaning.

The uncounted background calculation is that a chronological list W(a₁,b₁),…,W(a_L,b_L) sends |d,c⟩ to

    (−1)^{A·c+Q}|d,c+B⟩,
    A = Σ_t a_t,  B = Σ_t b_t,
    Q = Σ_{s<t} a_t·b_s.

It follows by substituting c+Σ_{s<t}b_s into the t-th sign. Also W(a,b)² = D_{a·b}, Sₐ² = T_b² = I. These are classical finite-Heisenberg calculations; the counted results below use them in specified consumers.

A **control-map bill** counts each executed S, T and D separately. None is free: each is an explicitly given finite sign mask or permutation. A table for a b-bit control on n data bits has b·2ⁿ bits; generating such a table must write those bits. Later results give sparse linear-control circuits and full-array read/write/scratch/head bills. If a = A d is linear, Sₐ is the product of wt(A) elementary signs (−1)^{d_j c_k}; if b = B d, T_b uses wt(B) controlled XORs c_k += d_j. Here wt counts nonzero binary matrix entries; zero controls emit no instruction. Counts are sufficient counts for the specified construction, never lower bounds or optimality claims. All supplied gate implementations are charged when substituted. Numerical private arithmetic registers are separately declared work storage: their initialization and clears are paid. They are not logical input bank coordinates, which may never be erased.

Computational labels in this volume are not automatically accessible Fourier labels of a physical caller. Whenever a statement is transported to that basis, the Walsh/chart adapters and their inverses must also be emitted and paid. P020 and P081–P100 make that obligation constructive. The full array size N includes every data, bank and spectator lane at every child, even when a gate touches few address axes.

Actual targets are Gareth Davidson/bitplane’s PR #2850, head a007c32f992195ad372806db38c9359dd49382ad, `research/phase-accumulator-tensor-closure/{model.py,invoice.py}`, and Dennis/antunishdPursuit’s PR #2859, head 5d6e821853ba71e91a7665c8fe3ffbbb0589ef6f, `research/phase-order-bank-audit/{audit.py,physical.py}`. Latest-head readback at `186a38eb124bc2fead44ae9d03a6edcf7649c882` found PR #2859 README.md, audit.py and physical.py byte-identical to the scientific pin above. Their bank-return/cross-term distinction, reverse continuation, scoped order theorem and critical old budget retain credit. The present volume supplies sufficient transformations, not a claim that the unchanged C/monomial alphabet now contracts.

## I. Closed consumers for arbitrary dirty banks

<a id="p001"></a>

### P001. A terminating consumer for every finite Pauli prefix

**Statement.** Given a finite prefix with controls A, B and Q from the background formula and any specified target sign F(d), append W(A,B), then D_{F+Q+A·B}. The complete controller is D_F ⊗ I_bank on arbitrary joint input.

**Proof.** The prefix contributes A·c+Q and leaves c+B. The appended W contributes A·(c+B), restores c, and leaves total sign Q+A·B. The final sign adds F+Q+A·B, leaving F because every repeated binary term cancels. The equality holds at every (d,c), so it holds on arbitrary coefficients. No bank initialization is used.

**Action and bill.** Normalize an open predecessor boundary instead of calling it restored. The repair adds one S, one T and one explicitly charged data sign mask; the prefix bill is retained. Its control tables and sign table are finite objects computed from the displayed sums. Dependencies: background. Target: PR #2850 open P boundary; PR #2859 wrong-order returned phase. Provenance: constructive adaptation of Weyl normal form.

<a id="p002"></a>

### P002. A doubled prefix closes to its aggregate pairing

**Statement.** Execute the same finite prefix twice with unchanged controls. It returns the entire dirty bank and applies exactly D_{A·B}, independently of its internal phase Q.

**Proof.** The first execution gives sign A·c+Q and shift B. The second gives A·(c+B)+Q and another B. The shifts cancel and the signs sum to A·B. Internal cross terms Q occur twice and cancel, even when Q is nonzero. Thus this is a sufficient consumer for the aggregate pairing, not for an arbitrarily chosen sum of pairings.

**Action and bill.** A target F with the explicitly checked identity F=A·B has a two-copy consumer costing twice every instruction of the prefix and no repair. A different target requires the D_{F+A·B} mask and its bill. Dependencies: background. Target: PR #2850 aggregate-parity shortcut. Provenance: source-directed reconstruction with the correct target specified.

<a id="p003"></a>

### P003. Palindromic consumption with no clean bank

**Statement.** For any f control pairs, run W₁,…,W_f,W_f,…,W₁. The endpoint is D_{Σ_j a_j·b_j} ⊗ I_bank.

**Proof.** The two middle W_f instructions give the scalar D_{a_f·b_f}. Data-only sign masks commute with every bank instruction because all controls read unchanged d. Move that scalar outside the remaining word. The middle pair then becomes W_{f−1}². Repeating this exact deletion leaves the product of all f scalar masks and no bank instruction. For f=0 the empty word is I and the sum is zero.

**Action and bill.** Use a reverse consumer when the caller admits that order. It uses 2f W instructions, hence 2f S and 2f T, and no correction mask or bank preparation. Any required caller reordering or movement is an additional bill. Dependencies: background. Target: PR #2850 reverse continuation, with arbitrary vector controls. Provenance: credited extension of the predecessor’s reverse schedule, not a new reverse-order discovery.

<a id="p004"></a>

### P004. Reverse consumers with separately prescribed local phases

**Statement.** After W₁,…,W_f, consume in reverse order with D_{q_j+a_j·b_j} followed by W_j. The endpoint is D_{Σ_j q_j} and the bank is identity.

**Proof.** Inverse W_j is D_{a_j·b_j}W_j because W_j²=D_{a_j·b_j}. Consequently the proposed consumer is D_{q_j}W_j⁻¹. Its data mask commutes through all bank words. The noncentral factors cancel in reverse order, while the masks multiply to D_{Σ q_j}. This also proves that arbitrary incoming bank amplitudes survive, rather than just bank addresses returning.

**Action and bill.** A consumer may request a different local phase from the producer’s self-pairing, provided it executes the displayed mask. The bill is 2f S, 2f T and at most f data masks, with zero masks omitted. Dependencies: P003. Target: changed consumer contract in PR #2850. Provenance: constructive central-phase repair.

<a id="p005"></a>

### P005. Quadratic bank echoes produce data phase and return both dirt and gauge

**Statement.** Let q:F₂ᵇ→F₂ have degree at most two, and define its polar form B_q(s,t)=q(s+t)+q(s)+q(t)+q(0). For controls s(d),t(d), run the four sign masks q(c), q(c+s), q(c+s+t), q(c+t), using translations around the rectangle and returning c. The resulting data phase is D_{B_q(s,t)}.

**Proof.** Execute D_{q(c)},T_s,D_{q(c)},T_t,D_{q(c)},T_s,D_{q(c)},T_t. The four observed bank values are c,c+s,c+s+t,c+t and the final translations sum to zero. A constant monomial occurs four times, and a linear monomial has zero second difference. For a quadratic monomial c_i c_j, expansion leaves s_i t_j+s_j t_i. Summing proves that all c terms disappear and that the remaining sign is exactly the polar form. This is valid even for correlated controls and dirty bank values.

**Action and bill.** Implement a specified bilinear data interaction through an existing quadratic bank gauge. Pay four bank sign masks and four translations; neither the gauge nor either translation is a free resource. Dependencies: background. Target: an alternative mixing primitive for PR #2850. Provenance: classical finite-difference identity with a complete returned-bank word.

<a id="p006"></a>

### P006. Arbitrary consumer permutation repaired by its actual crossings

**Statement.** Let producers be W₁,…,W_f and consumers be the same W instructions in any permutation π. Put Ω_ij=a_i·b_j+a_j·b_i. For every i<j whose consumers occur in order i,j, include Ω_ij in E. Appending D_E gives exactly D_{Σ_j a_j·b_j} and returns the bank.

**Proof.** Every a_j and b_j occurs twice. Hence the final shift and all terms involving the incoming c vanish. A self pair contributes a_j·b_j. For i<j, the occurrence pattern i,j,j,i contributes zero cross phase: each ordered pairing appears twice or not at all. The pattern i,j,i,j contributes Ω_ij by direct expansion of the four incoming bank values. Summing unordered pairs gives the total sign Σ self+E. The final mask cancels E.

**Action and bill.** Keep a caller-required consumer order rather than commuting it for free. The word uses 2f S, 2f T and one charged correction mask. P012–P019 provide smaller explicit circuits for that mask. Dependencies: background. Target: PR #2859 exact cross-term contract. Provenance: credited order formula extended to vector controls with a sufficient correction.

<a id="p007"></a>

### P007. A locally corrected adjacent exchange

**Statement.** In any larger controller with unchanged data controls, adjacent W_i,W_j may be exchanged if D_{Ω_ij} is inserted at that location. The full operator is unchanged, including every dirty-bank column.

**Proof.** In order i,j the bank shift is b_i+b_j and the bank-linear phase is (a_i+a_j)·c; the extra scalar is a_j·b_i. In order j,i the only changed scalar is a_i·b_j. Their difference is Ω_ij. The inserted mask supplies exactly that difference and commutes with the surrounding controlled bank operations. Thus the local replacement is an operator identity inside any admissible context.

**Action and bill.** Exchange a producer/consumer pair to meet an actual window, paying one D mask and preserving the other instructions. If Ω_ij is the identically zero function, the correction emits nothing. Dependencies: background. Target: paid consumer reordering in PR #2859. Provenance: explicit commutator correction, not free commutation.

<a id="p008"></a>

### P008. Transport through a paid data permutation

**Statement.** Let R be a specified invertible permutation of data labels and let controls a′,b′ on its output satisfy a′(R d)=a(d), b′(R d)=b(d). Then W(a,b),R,W(a′,b′),R⁻¹ closes the bank and applies D_{a·b} to the original data labels.

**Proof.** The first W leaves bank c+b(d) and sign a(d)·c. R changes only d. The second W reads the same two control values by the stated equations and therefore adds a(d)·(c+b(d)), restoring c. Its sign combines to a·b. R⁻¹ restores the original data coordinate. Basiswise equality proves the joint-array claim.

**Action and bill.** A consumer may read a changed coordinate chart when the labels are transported explicitly. Pay two W words, R and R⁻¹; a chart is not a promise of unchanged data. Dependencies: P002. Target: PR #2850 encoded caller boundary. Provenance: paid conjugation construction.

<a id="p009"></a>

### P009. Nontrivial intervening data work that is safe for the open bank

**Statement.** Partition data by the joint values of a(d),b(d). Let U be any given linear operator block diagonal in that partition. Then W(a,b),U,W(a,b) equals U followed by D_{a·b}, with identity on the bank.

**Proof.** Write U|d⟩=Σ_e U_ed|e⟩. A nonzero coefficient requires a(e)=a(d), b(e)=b(d). For each summand, the two W instructions therefore have the same controls. Their signs and shifts close as in P002, leaving the scalar (−1)^{a(d)·b(d)}. That scalar is constant within the block, so it can be placed before or after U. The equality permits arbitrary U within a block and arbitrary correlated bank amplitudes.

**Action and bill.** Insert only work proved to preserve the two control labels; its full circuit cost is added to two W words. This is an explicit sufficient mutable-data condition, not a deduction from bank return. Dependencies: P002. Target: actual intercall consumer work in PR #2850. Provenance: block-invariant adaptation.

<a id="p010"></a>

### P010. Affine label offsets with all linear and global signs paid

**Statement.** Put a(u)=A u+a₀ and b(v)=B v+b₀ on disjoint data blocks. Two W(a,b) words followed by the data sign uᵀAᵀb₀+a₀ᵀBv+a₀·b₀ implement exactly D_{uᵀAᵀBv} and return the bank.

**Proof.** P002 gives phase (Au+a₀)·(Bv+b₀). Expanding yields the desired bilinear term and precisely the three displayed offset terms. Applying their sum again cancels them in F₂, including the constant sign. The bank shift occurs twice and vanishes independently of offsets.

**Action and bill.** Reuse an affine rather than purely linear bank encoding without silently discarding its gauge. Pay two W words and at most two linear data phase masks plus one global sign; constants in the controls also require the corresponding bank flips/signs. Dependencies: P002. Target: encoded source-label associations in PR #2850. Provenance: explicit affine correction.

## II. Constructive cross-term correction circuits

<a id="p011"></a>

### P011. A crossing-graph correction from the actual literal schedule

**Statement.** In P006 suppose column j uses bank bit g(j), with a_j=u_j e_g(j), b_j=v_j e_g(j). Form the graph whose edges are same-bank alternating pairs in the literal producer/consumer word. Executing one data phase u_i v_j+u_j v_i for every graph edge repairs the word to the dot-product phase.

**Proof.** Different bank bits have zero pairing. A same-bit alternating pair contributes exactly its two displayed monomials by P006, while a nested pair contributes zero. The graph therefore lists every error term with its correct coefficient. Multiplying the edge masks adds that exact error polynomial again and removes it. Vertices of degree zero need no mask, and the empty graph already has the desired endpoint.

**Action and bill.** Extract edges from the actual schedule, not from a claim that the bank returned. Pay 2f W and one edge mask per listed edge. P016 or P017 may compile several edge masks jointly, but their costs are then substituted explicitly. Dependencies: P006. Target: `conflicts` in PR #2859 `audit.py`. Provenance: sufficient repair added to the credited graph criterion.

<a id="p012"></a>

### P012. A bilinear correction with explicit paired controls

**Statement.** Let M be any binary m×n matrix and supply a factorization M=AᵀB, with A having r rows and B having r rows. On any dirty r-bit bank, the word S_Au,T_Bv,S_Au,T_Bv applies D_{uᵀMv} and returns the bank.

**Proof.** The word is W(Au,Bv) twice. Its phase is (Au)·(Bv)=uᵀAᵀBv and its translation is zero by P002. Binary Gaussian elimination constructs such a factorization with r=rank M: choose r independent columns L of M, express all columns in that basis as R, and take A=Lᵀ, B=R. This construction also covers M=0 with an empty bank and empty word.

**Action and bill.** A correction never requires an assumed phase oracle. For linear controls the stated word costs 2 wt(A) elementary bank signs and 2 wt(B) controlled XORs; alternatively count four aggregate control maps. All r bank coordinates and all spectator lanes remain in the operand. Dependencies: P002. Target: paid repair outside PR #2859’s restricted sharing model. Provenance: rank factorization used as a physical phase construction, not a new rank theorem.

<a id="p013"></a>

### P013. Rank corrections serialized through one dirty bank bit

**Statement.** If M=Σ_{k=1}^r a_k b_kᵀ, the product of r scalar-bank words S_{a_k·u},T_{b_k·v},S_{a_k·u},T_{b_k·v} implements D_{uᵀMv} while restoring the same arbitrary bank bit after each factor.

**Proof.** The k-th four-map block gives D_{(a_k·u)(b_k·v)} and bank identity by P012 with one row. The next block therefore receives the original arbitrary bank, even when its coefficients are correlated with the data. The data signs multiply by adding their exponents, giving the displayed matrix sum. No state preparation is inserted between blocks.

**Action and bill.** Trade active bank width for an explicitly longer schedule. The bill is 4r aggregate maps, or 2Σ wt(a_k) elementary signs plus 2Σ wt(b_k) XORs; bank stock is one bit when r>0. This is a constructive upper bound, not a claim that child volume shrinks. Dependencies: P012. Target: general encoded consumers beyond PR #2859’s assigned-bit restriction. Provenance: serialized physical adaptation.

<a id="p014"></a>

### P014. Bounded-width factor chunks with returned boundaries

**Statement.** For the factorization in P013 and any integer b≥1, partition the r factors into consecutive groups of at most b. Each group is implementable by four aggregate maps on the same dirty b-bit bank; the concatenation gives D_{uᵀMv}, using 4⌈r/b⌉ maps when r>0.

**Proof.** For a group, put its a_k and b_k as rows of two b-row matrices, padding unused rows with zero. P012 implements that group and is identity on every bank coordinate, including padded ones. Concatenating the returned groups adds their matrix contributions and preserves all bank amplitudes. There are exactly ⌈r/b⌉ nonempty groups; r=0 emits no operation.

**Action and bill.** Choose a concrete bank-width/time tradeoff without invoking a general bank optimum. Aggregate-map count is as stated; elementary control count is the same weighted support sum as P013. Any b-axis basis implementation pays full b-axis children and full operand volume. Dependencies: P012–P013. Target: paid bank-width choices for PR #2850 successors. Provenance: constructive batching.

<a id="p015"></a>

### P015. Every assigned-bit order has a finite corrected consumer

**Statement.** For any f, bank assignment g and consumer permutation π, let E be the f×f binary matrix with E_ij=E_ji=1 exactly on the alternating same-bank pairs and zero diagonal. Append a P012 or P013 implementation of D_{uᵀEv} to the literal schedule. The complete endpoint is the intended dot-product phase with bank identity.

**Proof.** P011 says the actual error is the sum u_i v_j+u_j v_i over those pairs, which equals uᵀEv. The appended controller applies this same phase, is identity on its own arbitrary bank and hence cancels the error. It can reuse the original bank only after its complete return, as P006 guarantees; otherwise a distinct dirty bank is used and returned. No particular order or graph coloring is required.

**Action and bill.** A rank-r factorization yields 2f W plus the explicit 4r scalar-map correction, or four maps on r bank bits. A repaired schedule need not satisfy the old zero-cross-term criterion because its missing data phase is now executed and charged. Dependencies: P011–P013. Target: PR #2859’s changed-consumer handoff. Provenance: sufficient corrected continuation, with no new favorable native bill assumed.

<a id="p016"></a>

### P016. Complete bipartite crossing blocks need two phase factors

**Statement.** For disjoint index sets A,B, the phase Σ_{i∈A,j∈B}(u_i v_j+u_j v_i) is implementable through one dirty bit by two P013 factor blocks, regardless of |A|·|B|.

**Proof.** Distributivity rewrites the phase as (Σ_A u_i)(Σ_B v_j)+(Σ_B u_j)(Σ_A v_i). Execute the four-map scalar controller for each of these two products. Each restores the bank and contributes precisely its product; their sum is the full bipartite crossing phase, with every edge represented once. Empty A or B gives zero and both blocks may be omitted.

**Action and bill.** Repair exchanging two fully interacting batches without issuing a separate correction per pair. Pay eight aggregate maps, or 4(|A|+|B|) elementary sign/XOR gates in total. This count includes computing each parity by its elementary controls, not a free parity register. Dependencies: P013. Target: batch consumer permutations in PR #2859. Provenance: distributive factorization applied to a paid crossing correction.

<a id="p017"></a>

### P017. An edge-parity star cover compiles a crossing correction

**Statement.** Suppose a finite crossing graph is represented as the symmetric difference of stars (a_k,L_k), where a_k∉L_k. Its entire correction phase is obtained by applying P016 to every star’s center and leaves.

**Proof.** For one star, P016 contributes u_a Σ_L v_j+v_a Σ_L u_j, exactly its incident edge monomials. A repeated edge contributes the same two monomials twice and cancels. Because the supplied star list has the graph’s edge parity, the total exponent equals its crossing correction. Every star controller closes its dirty bank before the next.

**Action and bill.** A concrete star cover with s nonempty stars costs 8s aggregate maps and 4Σ_k(1+|L_k|) elementary gates. One always obtains such a cover by assigning each graph edge to its lower-numbered endpoint. A smaller supplied cover is checked by edge parity, not assumed. Dependencies: P016. Target: structured cross-term corrections in actual consumer graphs. Provenance: constructive graph decomposition.

<a id="p018"></a>

### P018. Clique crossing correction by aggregate parity plus diagonals

**Statement.** For f≥2, the complete-graph crossing phase is (Σ_i u_i)(Σ_i v_i)+Σ_i u_i v_i. It has a one-dirty-bit implementation with f+1 scalar factor blocks.

**Proof.** Expanding the first product lists every ordered pair (i,j). Its diagonal terms are cancelled by the second sum, leaving exactly u_i v_j+u_j v_i for i<j. Apply one P013 block to the two total parities and one to each diagonal pair. All blocks are returned-bank controllers, so their composition implements the desired phase on every incoming lane.

**Action and bill.** Pay 4(f+1) aggregate maps and exactly 8f elementary linear-control gates before any cancellation optimization. This replaces a quadratic list of separate edge repairs by a linear-size explicit controller, with no free data phase. Dependencies: P013. Target: same-order shared-bank consumers in PR #2859. Provenance: elementary identity with an executed correction recipe.

<a id="p019"></a>

### P019. Canonical polynomial repair removes all degree-two data phase

**Statement.** Let an actual returned-bank word have residual sign q(d) of degree at most two. Reduce d_i² to d_i and collect coefficients over F₂, obtaining q₀+Σ l_i d_i+Σ_{i<j} q_ij d_i d_j. Then it is corrected by one global sign if q₀=1, one data sign per nonzero l_i and one scalar four-map bank block per nonzero q_ij.

**Proof.** Boolean variables satisfy d_i²=d_i on every basis address. Collecting equal monomials therefore preserves the exact function q. Each quadratic block gives the required product d_i d_j by P013; each linear/global instruction gives its stated term. Adding the collected polynomial again cancels q. Every quadratic block restores its bank, so the correction is identity on it throughout the boundaries between factors.

**Action and bill.** If t quadratic and ℓ linear coefficients survive, the bill is 4t aggregate bank maps, ℓ data signs and at most one global sign. Coefficient collection uses the literal word’s polynomial, not a claim that returned coordinates imply zero phase. Dependencies: P013. Target: exact symbolic residual emitted by PR #2859 `pauli_polynomial`. Provenance: constructive canonicalization, not a new Boolean polynomial theorem.

<a id="p020"></a>

### P020. A fully paid physical-basis correction

**Statement.** Let F_n be the unnormalized binary Walsh matrix, F_n²=2ⁿI, and let H_n=2⁻ⁿF_n. A label-space correction D_q on n data bits becomes the exact physical controller H_n, D_q, H_n⁻¹. It is identity on every bank and spectator bit not acted on, with full operand volume retained.

**Proof.** The listed chronological word is the matrix H_n⁻¹D_qH_n. A physical vector first moves into the stated Walsh-label basis, receives the proved sign, and returns through the literal inverse. Since H_n⁻¹=F_n, the normalization factors cancel exactly, with no square-root convention. Tensoring each step with identity on omitted axes gives the same equality for arbitrary correlated spectator coefficients; it does not discard any lane.

**Action and bill.** Charge n forward and n inverse one-axis Walsh transforms, the complete sign-mask controller, all chart translations, and the inverse scale. P085 gives finite butterfly counts and P089 gives the predecessor’s C expansion. This theorem supplies a physical correction even when label access is unavailable; it does not call that correction cheap. Dependencies: P019 and the displayed Walsh identity. Target: both PRs’ missing physical consumer repair. Provenance: paid Fourier conjugation.

## III. Encoded banks and explicit chart consumers

<a id="p021"></a>

### P021. Kernel-preserving changed labels admit the original consumer

**Statement.** Open W(Au,Bv). Suppose an intervening data permutation R changes labels to u′,v′ but satisfies A u′=Au and B v′=Bv at every input. Applying W(Au′,Bv′) and then R⁻¹ returns the bank and implements D_{uᵀAᵀBv} on the original labels.

**Proof.** The producer’s two control values are preserved, even if the full labels change. The consumer therefore uses exactly the same values and closes to their pairing by P002. Reversing R restores the data address; the pairing is invariant because its two factors were invariant. Thus information in ker A or ker B may move without invalidating the bank association. This conclusion would fail without the two stated equations.

**Action and bill.** A source update confined to these kernels is a usable changed-label caller contract. Pay two W words and the full R/R⁻¹ circuits, rather than asserting that the entire source was untouched. Dependencies: P008. Target: PR #2850 source-label association. Provenance: explicit kernel-invariant physical continuation.

<a id="p022"></a>

### P022. Contravariant consumer controls for invertible label updates

**Statement.** After W(Au,Bv), let the caller apply u′=Lu, v′=Kv with specified invertible binary L,K. The consumer W(AL⁻¹u′,BK⁻¹v′), followed by inverse label charts, implements D_{uᵀAᵀBv} and returns all original coordinates.

**Proof.** Substituting the updated labels gives AL⁻¹Lu=Au and BK⁻¹Kv=Bv. P008 then closes the bank with the required phase. Applying the inverse charts gives the original u,v, so no operand-layout change is hidden at the output. Matrix inverses exist by the hypotheses and can be constructed by finite elimination; no source-recovery oracle is assumed.

**Action and bill.** Compile the consumer from AL⁻¹ and BK⁻¹. Charge the producer controls, these new consumer supports, and both directions of the L,K circuits. Dense transported controls may cost more than the originals. Dependencies: P008. Target: a concretely encoded recursive caller in PR #2850. Provenance: paid dual-control transport.

<a id="p023"></a>

### P023. Active-bank compaction from a nondegenerate pairing

**Statement.** Let U,V⊆F₂ᵇ each have dimension r and let their dot pairing be nondegenerate. All words with a(d)∈U and b(d)∈V admit a paid linear bank chart in which only the first r bank coordinates are touched; the other b−r coordinates are identity even on arbitrary joint dirt.

**Proof.** Choose a basis v_i of V and its dual basis u_i in U. Extend v_i by a basis of U⊥, forming an invertible column matrix C. With bank chart c′=C⁻¹c, translations become C⁻¹b, supported in the first r positions. Signs become Cᵀa, also supported there because a annihilates U⊥. Hence each transformed instruction is literally identity on the remaining coordinates. Conjugating back gives the original word on the full bank, not a quotient or projection.

**Action and bill.** Compile the chart and its inverse by row elimination: each uses at most b(b−1)+3b elementary XORs, counting a row swap as three XORs. Pay both charts and all transformed controls; every spectator lane remains in N. Dependencies: background. Target: actual narrow-axis bank basis changes in PR #2850. Provenance: constructive paired-subspace adaptation.

<a id="p024"></a>

### P024. A promised linear source subspace permits a smaller corrected phase

**Statement.** On the explicitly declared source subspace Au=0, Bv=0, the phase matrices M and M′=M+AᵀS+TB induce identical data operators. A factorization of M′ therefore supplies a returned-bank implementation of D_{uᵀMv} on that subspace.

**Proof.** The difference of exponents is (Au)ᵀSv+uᵀT(Bv), zero under the two equations. P012 realizes M′ and preserves u,v, so the source subspace is invariant. Equality holds on every basis vector in that subspace and therefore on arbitrary superpositions supported there, with any bank correlation. No claim is made for an input outside the declared subspace.

**Action and bill.** First certify the actual caller’s two linear equations; then explicitly factor a chosen M′ and charge its controls. This is a usable sufficient promised-domain construction, not a free assumption that independent labels satisfy a convenient relation. Dependencies: P012. Target: source-access restrictions at PR #2850’s encoded boundary. Provenance: physical phase reduction modulo explicit linear constraints.

<a id="p025"></a>

### P025. Affine source promises retain their exact correction signs

**Statement.** Under Au=a₀ and Bv=b₀, replace M by M′=M+AᵀS+TB. Follow a returned-bank implementation of M′ by the data mask a₀ᵀSv+uᵀTb₀. This implements M on the promised source subspace.

**Proof.** The exponent difference is (Au)ᵀSv+uᵀT(Bv)=a₀ᵀSv+uᵀTb₀. The supplied mask cancels it. Both terms are explicitly linear in the surviving labels, so no unknown nonlinear recovery is present. The controller preserves the labels and thus preserves the affine support promise; arbitrary coefficients and bank lanes within it are retained.

**Action and bill.** Pay the M′ factor controller and both nonzero linear phase masks. Check the affine equations as actual admission facts; a zero-offset theorem cannot justify dropping these masks. Dependencies: P012, P024. Target: affine source labels for a changed PR #2850 consumer. Provenance: constructive affine extension of the promised-domain correction.

<a id="p026"></a>

### P026. Time-varying bank charts with a literal transport word

**Statement.** For any logical sequence W(a_j,b_j) and invertible binary bank charts L₀,…,L_f, encode initially by L₀. At step j execute W(L_{j−1}⁻ᵀa_j,L_{j−1}b_j), then the bank permutation L_jL_{j−1}⁻¹. Decode by L_f⁻¹. The total operator equals the original logical sequence.

**Proof.** If the encoded bank is r=L_{j−1}c, its sign is (L_{j−1}⁻ᵀa_j)·r=a_j·c. Its translation changes r to L_{j−1}(c+b_j). The following chart makes this L_j(c+b_j). This proves the invariant at each step, including its accumulated sign. Initialization and final decoding convert the invariant to equality on original coordinates. No temporary bank coordinate is forgotten.

**Action and bill.** An actual frame change is paid by the L_jL_{j−1}⁻¹ circuit; all endpoint encoders and transported control supports are also paid. Identity transitions emit no chart. Dependencies: background. Target: recursive bank frames in PR #2850. Provenance: explicit charted continuation rather than an unpriced change of basis.

<a id="p027"></a>

### P027. A quadratic bank gauge has a computable phase-corrected consumer

**Statement.** Let q(c) be binary quadratic with q(0)=0 and polar matrix S, so q(c+b)+q(c)=q(b)+cᵀSb. The word D_q,W(a,b),D_q equals D_{q(b)} followed by W(a+Sb,b).

**Proof.** At input c the total sign is q(c)+a·c+q(c+b). The displayed quadratic identity makes this (a+Sb)·c+q(b). The output coordinate is c+b in both words. This is an equality at every data and bank label, including the phase q(b); ignoring that phase would give the wrong consumer. The polar identity follows by expanding each quadratic and linear monomial.

**Action and bill.** A bank-gauge adapter requires two actual q masks or the transformed controls plus one q(b) data mask. Choose between those explicit bills; do not infer unitarity or free cost from a similarity alone. Dependencies: background. Target: phase/gauge variants of PR #2850’s Pauli boundary. Provenance: classical quadratic conjugation with its central correction retained.

<a id="p028"></a>

### P028. Adjacent bank-gauge adapters fuse by polynomial difference

**Statement.** Suppose a chronological circuit consists of L modules D_{q_j},U_j,D_{q_j}, with no instruction between consecutive modules. Replace each adjacent pair D_{q_j},D_{q_{j+1}} by D_{q_j+q_{j+1}}. The full operator is unchanged, with only L+1 gauge masks before omissions of zero masks.

**Proof.** The adjacent masks are diagonal on the same unchanged bank coordinate and their signs add, giving exactly D_{q_j+q_{j+1}}. This local replacement does not move either mask through U_j. Performing it at each boundary leaves the first and last masks and one difference mask per internal boundary. Every intermediate U_j and every endpoint phase is retained.

**Action and bill.** Emit the two endpoint gauges and all nonzero differences. If masks are compiled monomial by monomial, the cost is their actual support weight, which can be smaller than 2Σ wt(q_j). This is adapter cancellation at genuine adjacency, not arbitrary phase commutation. Dependencies: P027. Target: priced chart wrappers between physical children. Provenance: constructive boundary fusion.

<a id="p029"></a>

### P029. Orthogonal control re-encoding preserves every closed phase

**Statement.** For an explicitly supplied binary O with OᵀO=I, replace every pair a_j,b_j in a bank-returning word by Oa_j,Ob_j. If Σa_j=Σb_j=0, the new word has the identical data phase and identity bank endpoint.

**Proof.** The transformed sums remain zero. Each term in the scalar phase satisfies (Oa_t)·(Ob_s)=a_tᵀOᵀOb_s=a_t·b_s. The normal-form formula therefore gives exactly the same Q and zero incoming-bank phase/translation. This proof covers every dirty bank lane; it does not rely on a clean vector fixed by O.

**Action and bill.** Compare the explicitly recomputed support weights of all transformed linear controls. If a bank chart is also physically materialized, pay O and O⁻¹; the identity alone licenses only the closed-word replacement. Dependencies: background. Target: encoded-bank control sparsity with a certified returned boundary. Provenance: a sufficient circuit replacement, not a new orthogonal-group fact.

<a id="p030"></a>

### P030. Affine bank adapters with the global sign exposed

**Statement.** Let E(c)=Lc+t with invertible L. The chronological sandwich E,W(a,b),E⁻¹ equals D_{a·t} followed by W(Lᵀa,L⁻¹b).

**Proof.** After E the coordinate is Lc+t. The W sign is a·(Lc+t)=(Lᵀa)·c+a·t. Applying E⁻¹ to Lc+t+b gives c+L⁻¹b. These are exactly the sign and translation of the stated right side. Thus the affine offset is paid as a data phase, even though the final bank coordinate is restored by the sandwich.

**Action and bill.** Use a concrete affine location change without losing its central sign. Pay two linear charts, two fixed translations, the transported controls and the possible a·t mask if using the right-side implementation. Dependencies: background. Target: frame/origin changes in a physical phase bank. Provenance: complete affine adapter contract.

## IV. Block and tensor factorizations with complete consumers

<a id="p031"></a>

### P031. Disjoint bank axes allow a literal split controller

**Statement.** Decompose c=(c₁,c₂), a=(a₁,a₂), b=(b₁,b₂). A W(a,b) instruction equals consecutive W(a₁,b₁) on bank 1 and W(a₂,b₂) on bank 2, even when both controls depend on the same immutable data.

**Proof.** The split instructions contribute a₁·c₁+a₂·c₂ and shift the two disjoint coordinates by b₁,b₂. Neither instruction changes the other’s bank coordinate or its data controls. This is the full sign and translation of the original W. The argument is pointwise in all data, so it also handles correlations between the two bank blocks.

**Action and bill.** A wide bank operation may be implemented in separate native axis blocks. Charge both pairs of control maps and both native basis changes when those are used; the factorization itself does not reduce N or grant parallel hardware. Dependencies: background. Target: tensor versus shared-bank physical calls in PR #2850. Provenance: explicit bank-splitting implementation.

<a id="p032"></a>

### P032. Dependency components compile to tensor-independent circuits

**Statement.** Partition data and bank axes into components. Suppose every sign coordinate and translation coordinate depends only on data in its own component and acts only on that component’s bank axes. Then the entire controller equals the tensor product of the component controllers, interleaved in any component-respecting order.

**Proof.** Each elementary map changes and phases only basis coordinates of one component. On a product basis vector it therefore equals its local matrix tensored with identity on all others. Maps in distinct components commute by direct evaluation on that basis. Gathering all maps of each component preserves their internal order and gives the claimed tensor product. Linearity extends equality to arbitrary nonproduct states.

**Action and bill.** Form the actual dependency graph before splitting or reordering. Serial bills add; any parallel schedule also needs its own processor model. In the inherited whole-array model every component child still runs on the full N-cell array. Dependencies: P031. Target: physical bank-interaction factoring without lost spectator volume. Provenance: a support-certified tensor compiler.

<a id="p033"></a>

### P033. Block diagonal phase forms give independent returned-bank modules

**Statement.** After specified row and column permutations, let M=diag(M₁,…,M_k). Realize each D_{u_iᵀM_i v_i} by P012 and restore the coordinate permutations. The endpoint is D_{uᵀMv}, with each bank returned.

**Proof.** Matrix multiplication expands uᵀMv as the sum of the k block terms, with no cross-block term. Each supplied module contributes precisely its block sign and bank identity. Their product therefore gives the required sign on the permuted labels. The inverse permutations restore the original ABI. This proof uses the explicit block-zero condition, not merely equal ranks.

**Action and bill.** Pay every block factor controller and both directions of the row/column permutations. The bank width may be the maximum block width when returned blocks are serialized. All data/bank/spectator lanes remain counted. Dependencies: P012. Target: physically separated phase columns in PR #2850. Provenance: constructive block factorization.

<a id="p034"></a>

### P034. A triangular interaction is three closed physical phases

**Statement.** For M=[[A,B],[0,C]] and matching data partitions, the three controllers for u₁ᵀAv₁, u₁ᵀBv₂ and u₂ᵀCv₂ implement D_{uᵀMv}. They may share a dirty bank serially after padding factor widths to their maximum.

**Proof.** Expansion of the block product gives exactly the three terms and no fourth term. Their diagonal data signs commute, so multiplying the three exact closed controllers gives the required phase. Because each is identity on the entire padded bank, the next receives its original arbitrary bank state, not a newly prepared state. Zero blocks emit no controller.

**Action and bill.** Factor A,B,C separately and pay all three control support sums. Shared-bank stock is at most the maximum supplied factor width; data volume is unchanged. This supplies an explicit off-diagonal consumer rather than omitting triangular cross terms. Dependencies: P012, P014. Target: block-coupled phase banks. Provenance: paid triangular decomposition.

<a id="p035"></a>

### P035. A Kronecker interaction has an explicit product-bank circuit

**Statement.** If M=AᵀB and N=CᵀD, then a bank with r·s coordinates implements D_{uᵀ(M⊗N)v} by the four-map controller with controls (A⊗C)u and (B⊗D)v, where r,s are their row counts.

**Proof.** The elementary Kronecker multiplication rule follows entrywise: summing over a pair of row indices factors into the product of two independent sums. Thus (A⊗C)ᵀ(B⊗D)=M⊗N. P012 gives the asserted phase and a returned bank. The rule is valid for empty factors and all matrix shapes for which these products are defined.

**Action and bill.** The elementary bill is 2 wt(A)wt(C) bank signs and 2 wt(B)wt(D) XORs. Any physical reshaping permutation and its inverse must be emitted. This is not a claim that tensorization preserves a favorable recursion invoice. Dependencies: P012. Target: higher-column tensor phase contracts in PR #2850. Provenance: explicit physical use of a classical tensor identity.

<a id="p036"></a>

### P036. Closed block phases reuse one arbitrary bank allocation

**Statement.** Given finitely many complete phase controllers, each identity on a bank of at most b bits, pad them to b bits and execute them consecutively on the same bank. Their endpoint is the product of their data phases and identity on all b bank bits.

**Proof.** Padding tensors a controller with identity on the unused bits. After the first controller the bank factor in the operator is exactly I, so the next acts on its original arbitrary coordinate amplitudes. Multiplication yields I⊗D_{q₁}D_{q₂} and iteration gives the claimed product. The proof uses equality as operators, not a factorization of the initial state.

**Action and bill.** Replace separate allocated banks by a shared bank only at these closed boundaries. The bill is the sum of the emitted controller bills; no reset, clean preparation or lane deletion is introduced. Dependencies: P012. Target: legitimate bank reuse after complete physical returns. Provenance: a concrete resource-reuse sufficient condition.

<a id="p037"></a>

### P037. A rooted tree phase compiles by parent parity stars

**Statement.** For a finite forest on data bits, orient each edge from parent to child. The phase Σ_edges d_i d_j is implemented by one scalar-bank factor block for each vertex with children, using controls d_parent and the parity of its children.

**Proof.** Every edge occurs once in exactly its parent’s product d_parent·Σ_children d_j. Expanding and summing these products gives precisely the forest phase. P013 realizes each product and returns the common dirty bank, so all products compose. Isolated vertices contribute nothing, and the empty forest requires no bank operation.

**Action and bill.** If s vertices have children and e edges, the construction uses 4s aggregate maps and 2(s+e) elementary sign/XOR controls. It needs no stored child-parity register: the controls are applied directly to the dirty bank. Dependencies: P013. Target: tree-structured bank/phase interactions. Provenance: constructive edge grouping with an explicit bill.

<a id="p038"></a>

### P038. A bipartite phase chooses the cheaper explicit parity side

**Statement.** For any binary bipartite adjacency matrix A between data x and y, implement xᵀAy either row by row using x_i and the row parity of y, or column by column using column parity of x and y_j. Both exact returned-bank circuits are available.

**Proof.** The row expansion is Σ_i x_i(Σ_j A_ij y_j); the column expansion is the same sum grouped by j. Each nonzero row or column supplies a P013 scalar factor, so both groupings give the exact sign and restore the bank after every block. Repeated zero rows/columns emit nothing.

**Action and bill.** With e nonzero entries and r nonzero rows, the row bill is 4r aggregate maps and 2(r+e) elementary controls. With c nonzero columns the column bill is 4c and 2(c+e). Choose the actual smaller paid implementation, retaining any physical basis adapters. Dependencies: P013. Target: sparse cross-term correction in an actual bank interaction graph. Provenance: explicit dual grouping, not an optimal circuit claim.

<a id="p039"></a>

### P039. Removing an actual bank-bank quadratic interaction

**Statement.** Suppose a preceding controller leaves an unwanted sign c_LᵀMc_R on two dirty bank blocks, whose coordinates otherwise return. Factor M as a sum of r outer products. Apply P013 to those two bank blocks as read-only data, using a further arbitrary scratch bank bit. The interaction is cancelled and every bank coordinate returns.

**Proof.** During the correction, c_L,c_R are unchanged controls. P013 applies exactly their unwanted sign and restores the scratch bank. The sign therefore appears twice and vanishes. Neither original bank coordinate is overwritten, and the scratch bit is returned as an operator on its entire two-dimensional space, so correlations among all three banks are preserved.

**Action and bill.** Pay the r four-map factors and one extra live dirty coordinate during correction, unless a previously returned coordinate is explicitly available. A mere return of bank coordinates would not justify omitting the interaction phase. Dependencies: P013. Target: constructive repair of coupled physical bank returns. Provenance: a concrete corrective consumer for a full bank-bank phase.

<a id="p040"></a>

### P040. Selector-controlled phase modules with dirty-bank preservation

**Statement.** Let h(d) be a specified finite selector, unchanged by all modules. In sector h=t require phase q_t with a supplied P012 factorization. Mask every control in module t by δ_t(d), the indicator of h=t, pad bank widths and execute all modules. The endpoint is D_{q_{h(d)}} and bank identity.

**Proof.** In its selected sector δ_t=1 and the original controller acts. Outside it both controls vanish, so every S and T is identity. Equivalently, each factor’s phase is δ_t² times its former phase, equal to δ_t times that phase over F₂. Summing modules leaves exactly one sector’s phase at each data label. Every module closes on every bank lane in every sector.

**Action and bill.** This is a finite multiplexed consumer with no assumed clean branch flag. Pay all masked-control evaluations or their explicit truth tables, plus the maximum live bank width; no branch is free in a whole-array scan. Dependencies: P012. Target: an actual state-dependent caller continuation. Provenance: constructive direct-sector phase compilation.

## V. Bank lifetimes, migration and constructive reuse

<a id="p041"></a>

### P041. Certifying a reusable subbank while another part remains open

**Statement.** In a Pauli word with summary (A,B,Q), let J be bank coordinates on which A_J=B_J=0. The complete prefix is identity on subbank J tensored with a possibly open controller on its complement. Therefore J may be reassigned at that boundary.

**Proof.** The summary’s incoming-bank sign A·c contains no c_J and its translation leaves c_J unchanged. Its residual phase Q depends only on data, not on any incoming bank coordinate. Hence on a basis vector the c_J coordinate and amplitude factor are passed through identically, while the remaining operator is independent of c_J. This is a literal tensor-identity factor, even when the initial state is correlated across the two subbanks.

**Action and bill.** Compute the actual coordinate sums and reuse precisely their common zero subset, without resetting it. The prefix cost is unchanged; later users pay their own controls. Checking only B_J=0 would be insufficient because A_J may still phase the returned coordinates. Dependencies: background. Target: partial live-bank reuse in PR #2850. Provenance: a constructive release test with a usable returned subsystem.

<a id="p042"></a>

### P042. Compute–accumulate–uncompute with one dirty borrowed bit

**Statement.** Let x be immutable data, c an arbitrary borrowed bit, z a k-bit output accumulator, and f(x) a bit, g(x) a k-bit vector. Execute c+=f(x), z+=c g(x), c+=f(x), z+=c g(x). The output is z+f(x)g(x), with x and c unchanged.

**Proof.** After the first update c becomes c+f. The two z updates add (c+f)g and cg, whose sum is fg. The second c update restores its original value. Every operation is a permutation of the full address space, so the equality extends to arbitrary complex coefficients, including correlations between the output accumulator and the dirty bit. There is no clean-copy assumption.

**Action and bill.** This supplies an actual mutable-output consumer for a borrowed bit. Pay two f-controlled bank translations and two c g-controlled accumulator translations, including whatever finite circuits evaluate f and g. For given truth tables these maps are explicit involutive permutations. Dependencies: binary distributivity. Target: physical read-only source/output borrowing beyond a phase-only boundary. Provenance: a dirty-work construction with an exact output ABI.

<a id="p043"></a>

### P043. A bank automorphism between producer and consumer is explicitly transportable

**Statement.** Let L be an explicitly implemented invertible binary bank map. The word W(a,b),R_L,W(L⁻ᵀa,Lb),R_L⁻¹ has endpoint D_{a·b} and identity on the original bank.

**Proof.** The first instruction leaves c+b with sign a·c. After R_L the bank is L(c+b). The second W adds sign (L⁻ᵀa)·L(c+b)=a·c+a·b and translation Lb, leaving Lc. R_L⁻¹ restores c. The two incoming-bank signs cancel and the remaining sign is a·b. The proof does not assume that R_L fixes a special initial bank state.

**Action and bill.** An intervening bank operation is permitted only with its transported consumer. Pay both chart circuits and both control sets; dense L can increase the control support bill. Dependencies: background. Target: nontrivial intercall bank transformations. Provenance: explicit transported return, not an inferred restored-bank implication.

<a id="p044"></a>

### P044. An eight-vertex dirty-bank echo for cubic phases

**Statement.** Let q(c) have degree at most three. For three data-controlled translations s,t,u, traverse the eight vertices of their Boolean cube in cyclic Gray order, applying the q sign at each vertex and returning to c. The endpoint is the data sign Δ_sΔ_tΔ_u q, independent of c.

**Proof.** The accumulated exponent is the sum of q over all eight vertices c+ε₁s+ε₂t+ε₃u. Each monomial of degree less than three has zero third difference: one of the three difference operations removes its dependence and the next cancels it. Expanding a cubic monomial leaves only products selecting one factor from each of s,t,u, hence no c. A cyclic Gray traversal visits each cube vertex once and changes one translation at each edge, so it returns the bank after eight translations. Repeated or zero translation directions merely make the displayed sum zero where appropriate.

**Action and bill.** Pay eight actual bank-q masks and eight controlled translations. The theorem implements a specified trilinear correction without preparing a bank; it does not assume the cubic mask has a cheap native realization. Dependencies: finite-difference expansion as in P005. Target: explicit higher-order corrections after nonlinear caller updates. Provenance: constructive extension beyond the bilinear return model.

<a id="p045"></a>

### P045. An anticommuting scratch pair yields a returned dirty-bank phase

**Statement.** Let A,B be supplied involutive linear maps on a scratch register with AB=−BA, and let f,g be unchanged data bits. For bank control c, define C(c) as the four-map commutator A^c,B^f,A^c,B^f. Then T_g,C(c),T_g,C(c) applies D_{fg} and returns both bank and scratch.

**Proof.** If either control exponent is zero, C(c)=I. If both are one, its matrix is BABA=−I; thus C(c)=(-1)^{cf}I on the entire scratch space. The first T_g makes its first exponent c+g; the second restores c. The two commutator signs add (c+g)f+cf=gf. Every scratch action cancels to a scalar, so arbitrary scratch coefficients and correlations are restored.

**Action and bill.** Pay eight controlled scratch involutions and two bank translations, plus their concrete control circuits. One may take literal single-bit X and Z on scratch, so no unproved anticommuting gadget is required. Dependencies: direct four-case evaluation. Target: an explicit noncommuting consumer alphabet for PR #2850. Provenance: charged dirty-bank echo.

<a id="p046"></a>

### P046. Interval allocation of single-bit bank jobs

**Statement.** Suppose each job has a fixed half-open lifetime [s_j,t_j), touches one assigned bank bit only within that interval, and is an exact returned-bank controller at t_j. If at most b lifetimes overlap, all jobs are implementable using b arbitrary bank bits without resets.

**Proof.** Process starts in increasing order, releasing bits for jobs ending at that time first. At a new start there are at most b−1 other live jobs, so at least one bit is free. Assign it until the job ends. Overlapping jobs never share a bit; when a bit is reused its previous job is exactly identity on that bank factor. Thus replacing logical bank names by these physical coordinates preserves every operation and every returned endpoint. Common data controls are unchanged by hypothesis.

**Action and bill.** Emit the same job instructions with fixed physical coordinates; bank stock is b bits. No runtime migration is required by this construction, but descriptor generation and the full N-cell volume remain paid. Dependencies: returned-subsystem semantics in P041. Target: bank reuse under actual producer/consumer lifetimes. Provenance: constructive interval allocation applied to exact bank contracts.

<a id="p047"></a>

### P047. Variable-width bank jobs admit a noncontiguous peak-stock allocation

**Statement.** Let job j need r_j independent bank coordinates throughout its fixed lifetime and return them all. If the total live requirement never exceeds B, compile all jobs into B physical coordinates, permitting a job’s coordinates to be noncontiguous.

**Proof.** At each start, already live jobs occupy at most B−r_j coordinates by the peak hypothesis. Choose any r_j currently free coordinates and keep that set fixed until the job ends. The injective coordinate renaming preserves each job’s literal tensor instructions; distinct live jobs have disjoint bank supports. Returned boundaries justify reuse even for initially correlated bank values. Endpoint ties are handled by releasing ending jobs before allocation.

**Action and bill.** Bank stock is B, with no movement if the native interface accepts arbitrary listed axes. If it requires a contiguous block, gathering/scattering must be paid using P061 or P077. This theorem explicitly provides noncontiguous allocation, not a false contiguous-packing claim. Dependencies: P046. Target: actual bank-stock versus chart cost. Provenance: sufficient allocation with its physical limitation stated.

<a id="p048"></a>

### P048. Repairing coordinate return into actual subsystem return

**Statement.** Suppose a known monomial prefix sends (x,y) to (x,Rx+Ky+b(d)), with invertible K, and multiplies by (−1)^{q(x,y,d)}. Apply y+=Rx, then a sign equal to the part of q involving x, evaluated at the inverse image of the current coordinates. The repaired endpoint is identity on x tensored with an operator on y and data.

**Proof.** The added XOR removes Rx from the output y, leaving Ky+b. Its inverse image is y_old=K⁻¹(y_new+b), while x is unchanged. Write q=q_dep+q_free by collecting monomials with and without x. The supplied sign evaluates q_dep at exactly these old input values, cancelling it. The remaining sign q_free(y_old,d) and the remaining y map are independent of x. Hence the entire operator factors as I_x⊗V, not merely an output coordinate identity.

**Action and bill.** Pay wt(R) elementary bank XORs and the explicit correction mask, including inverse-image evaluation or its finite table. For quadratic q and linear b the correction remains quadratic and can be compiled by P019/P039. Dependencies: P019, P039. Target: repairing the exact returned-coordinate fallacy identified by PR #2859. Provenance: a sufficient, executed subsystem-release construction.

<a id="p049"></a>

### P049. Migrating a live bank through arbitrary spare dirt

**Statement.** Let U act on data and a b-bit live bank A, with a disjoint b-bit spare bank B. Swap A with B, execute the same U using B, then swap back. The endpoint is exactly U on the original data/A and identity on B, with no condition on either initial bank.

**Proof.** The swap permutation exchanges the two complete tensor factors. Conjugating the B-supported U by that swap therefore replaces every occurrence of B by A. This equality holds on every product basis vector and hence on arbitrary correlated inputs. The original contents of B are returned by the final swap; no garbage is erased.

**Action and bill.** Pay 2b bit swaps, or 6b controlled XORs using three XORs per swap, and U’s full bill. Both bank stocks count during migration. The construction gives a legal location change for an open bank, not a free move to a clean register. Dependencies: explicit swap evaluation. Target: live-bank routing to a different consumer location. Provenance: paid endpoint migration.

<a id="p050"></a>

### P050. Releasing and reopening an open Pauli summary

**Statement.** Let a prefix have summary D_Q W(A,B). Immediately append W(A,B)⁻¹=D_{A·B}W(A,B), yielding D_Q with the bank released. After any intervening data operation commuting with these controls, reopen with W(A,B) before the original continuation. The resulting operator equals the original prefix, intervening operation and continuation in their intended order.

**Proof.** The release multiplies the prefix on its output side by the literal inverse of W, leaving D_Q. The reopened W reconstructs its former bank state. A data operation commuting with the controls also commutes with W. In matrix order, the released/reopened prefix is W U D_Q, while the unreleased prefix followed by that operation is U W D_Q; these are equal. Thus no commutation with D_Q is additionally needed, and cancelling the release/reopen pair after the stated move gives the original circuit. Without that condition an arbitrary middle operation is not licensed.

**Action and bill.** Pay two extra W words and one A·B data mask for the inverse; physical implementations of all three are explicit. A released bank may serve a closed intervening job, but its use is not free. Dependencies: P001, P009. Target: checkpointing an open PR #2850 boundary. Provenance: constructive release/reopen with its exact central sign.

## VI. Caller-respecting order and paid fusion

<a id="p051"></a>

### P051. Topologically scheduled consumers with exact inversion repairs

**Statement.** Let a finite acyclic precedence graph specify the allowed consumer tasks after a producer prefix. Choose a topological order π by repeatedly removing a vertex with no incoming edge. Execute that consumer order and the correction from P006. The desired phase and bank return are obtained without violating the graph.

**Proof.** A finite nonempty acyclic graph has a source: otherwise following incoming edges indefinitely repeats a vertex and forms a cycle. Removing a source preserves acyclicity, so the procedure returns an order satisfying every edge. The actual permutation π then has the exact error polynomial specified by P006, and that correction cancels it. No consumer is moved through a dependency for free.

**Action and bill.** The constructive output is the actual topological task list, 2f W words and its fully compiled crossing correction. Precedence may encode source windows or data availability, but those obligations must really be present in the graph. Dependencies: P006, P015. Target: a changed but legal physical caller order. Provenance: sufficient schedule-plus-correction assembly.

<a id="p052"></a>

### P052. Whole-module exchange uses only aggregate bank response

**Statement.** Let two bank modules have summaries D_{Q₁}W(A₁,B₁) and D_{Q₂}W(A₂,B₂), with unchanged data labels. Exchanging the whole modules is exact after inserting D_{A₁·B₂+A₂·B₁}.

**Proof.** Their internal data masks commute with all controlled bank maps and remain Q₁+Q₂ in either order. The remaining two W summaries differ by exactly their aggregate symplectic pairing, as P007 proves. Therefore one displayed mask corrects the exchange of the entire modules, regardless of their internal lengths. No internal bank sign is dropped.

**Action and bill.** Exchange two actual batches only when their task windows permit it. Pay one aggregate correction, whose binary coefficient matrix can be factored by P012, rather than assuming all pairwise gates commute. Module circuits and their movement bills remain. Dependencies: P007. Target: paid producer/consumer batch movement. Provenance: aggregate-response correction with a complete module contract.

<a id="p053"></a>

### P053. A reverse-consumer schedule with explicit release/deadline feasibility

**Statement.** Fix the reverse consumer order j=1,…,f and durations τ_j≥0, including its chosen travel and wrappers. Give releases r_j and deadlines d_j. If max_{h≤j}(r_h+Σ_{k=h}^j τ_k)≤d_j for every j, starting each task as early as possible in that order gives a valid shared-bank reverse continuation.

**Proof.** Define finish F_j=max(r_j,F_{j−1})+τ_j, with F₀ no later than all releases. Induction expands F_j into the displayed maximum. Hence the hypothesis gives every deadline and the recurrence gives every release and nonoverlap constraint. The resulting order is exactly the reverse continuation, so P003 gives its desired phase and return. Idle waiting is permitted and explicitly occupies schedule time.

**Action and bill.** This is a computable sufficient caller-window test, not a promise that reversing consumers is always legal. Emit the recurrence’s start times and the literal reverse circuit; charge waiting, durations and movement as chosen. Dependencies: P003. Target: PR #2859’s warning that an actual caller may forbid reordering. Provenance: constructive timed continuation.

<a id="p054"></a>

### P054. Physical allowed-bank lists give a sufficient allocation algorithm

**Statement.** Fix a crossing graph and a vertex order. Give each column j an explicit allowed set L_j of physical bank bits, with |L_j| greater than its number of earlier neighbors. Greedily assign j any allowed bit not already used by those neighbors. The resulting literal producer/consumer word gives the desired dot-product phase without repair and uses only allowed locations.

**Proof.** At most the number of earlier neighbors can be forbidden by earlier assignments, so the strict cardinality condition leaves an allowed bit. When the later endpoint of an edge is processed, it avoids the earlier endpoint’s bit. Thus the final coloring is proper. No alternating pair shares a bank, so P011 gives zero error and the required return. All assigned locations meet the explicit physical lists, a restriction not represented by an unconstrained LIS optimum.

**Action and bill.** Emit those actual locations and the unchanged caller order. Pay 2f W words, their native wrappers, any routed access to the assigned bits and the full operand volume of the used physical bank. This is a sufficient list-constrained placement, not a general optimality claim. Dependencies: P011. Target: caller-reserved or unavailable bank coordinates beyond PR #2859’s unconstrained model. Provenance: constructive list allocation with a physical contract.

<a id="p055"></a>

### P055. Bipartite bank choices can minimize an actual location bill

**Statement.** Suppose the crossing graph is bipartite and only two specified bank locations are permitted, with a per-column allowed subset and nonnegative placement costs c(j,0),c(j,1). If each connected component has a bipartition orientation respecting all its allowed subsets, choose its cheaper allowed orientation. This gives a valid zero-repair continuation minimizing the summed placement cost among all such two-bank colorings.

**Proof.** A breadth-first parity coloring of a connected component is unique up to exchanging its two colors: along each edge the color must flip, so fixing one vertex fixes all others. Bipartiteness guarantees consistency. Check both orientations against the given allowed subsets and compute their two finite cost sums. By hypothesis at least one survives. Different components have no crossing edges and their costs add, so choosing the minimum independently gives a proper globally optimal two-color assignment under these explicit constraints. Isolated vertices are one-vertex components with the same two choices.

**Action and bill.** Emit the selected locations; actual routing costs are the supplied c values and must already describe concrete paths. The 4f unfused C-call bill and all full-array lanes remain. Dependencies: P011. Target: physically distinct bank ports and restricted caller placement. Provenance: a constructive location optimization, not a restatement of a bank-bit lower bound.

<a id="p056"></a>

### P056. Odd-incidence codes construct a correct encoded bank assignment

**Statement.** Let G be the crossing graph. Supply sets C₁,…,C_k of columns, none containing both ends of a crossing edge. Give each column one bank-coordinate incidence for every C_t containing it; if its incidence count is even, add a private coordinate for that column. Calling the resulting vector g_j, the word with a_j=u_jg_j and b_j=v_jg_j has the desired dot-product phase for the fixed consumer order.

**Proof.** Every g_j has odd Hamming weight, hence g_j·g_j=1. A crossing pair never shares a C_t coordinate, and its private coordinates are distinct, so g_i·g_j=0 on every crossing edge. The general vector-control formula P006 therefore has self term u_jv_j and zero crossing term. All controls still occur twice, giving identity on the entire encoded bank. This construction can use several coordinates per column; it is outside the one-assigned-tensor-bit-per-column model.

**Action and bill.** Bank stock is k plus the number of even-incidence columns. The literal elementary control bill is 4Σ_j wt(g_j), and any physical bank basis calls use their actual active supports and full N. These extra controls are not free merely because the encoding is correct. Dependencies: P006. Target: an explicit encoded-bank continuation beyond PR #2859’s restricted assignment theorem. Provenance: sufficient incidence-code construction with its complete added controls.

<a id="p057"></a>

### P057. Closed batch barriers construct a reusable one-bank schedule

**Statement.** Partition columns into ordered batches. If the actual caller permits all producers of a batch followed by its reverse consumers before the next batch begins, the same arbitrary bank bit implements every batch’s dot-product phase and is returned at every barrier.

**Proof.** P003 proves the exact returned phase of one batch. Because no unfinished bank state crosses its barrier, P036 permits reuse by the next batch. The product of all batch phases is the full dot-product phase, and all bank boundaries are exact identities. The caller hypothesis concerns actual event dependencies; it is stronger than merely choosing a convenient column partition.

**Action and bill.** Emit the legal batch order and its barriers. The schedule retains 2f W instructions and, in the predecessor’s unfused physical alphabet, 4f one-axis C calls plus all wrappers and barrier control. Dependencies: P003, P036. Target: fully priced serialization rather than an imaginary free batched bank. Provenance: sufficient caller-constrained reuse.

<a id="p058"></a>

### P058. Arbitrarily interleaved matched words have a chord correction

**Statement.** Let a literal word contain each W_j exactly twice, in any interleaving, with unchanged controls. Draw a chord between its two occurrences. Its endpoint is bank identity with phase Σ_j a_j·b_j plus Ω_ij for exactly those pairs whose chord endpoints alternate. Appending that chord correction gives the desired sum.

**Proof.** Each translation and incoming-bank sign occurs twice, so they cancel. For two distinct labels, their four occurrences are either separated, nested or alternating. In the separated case each ordered cross pairing occurs twice or zero times; in the nested case the same cancellation holds. In an alternating case the remaining terms are a_i·b_j+a_j·b_i. Self occurrences contribute a_j·b_j. Summing all pairs gives the formula because the normal-form phase has no terms involving three occurrences.

**Action and bill.** Use the actual recursively interleaved word, not just a producer-prefix abstraction. Charge its 2f W instructions and compile its explicitly extracted chord correction by P012–P019. Dependencies: background. Target: nested open-state boundaries through more than one parent level. Provenance: constructive generalization of the predecessor’s order repair.

<a id="p059"></a>

### P059. Certified zero-pairings permit dependency-safe rescheduling

**Statement.** Add an ordering edge for every pair of W instructions whose Ω is not identically zero, preserving their original relative order; also add all caller dependencies. If this graph is acyclic, any topological order executes the identical operator without a phase correction.

**Proof.** Compare the original list and the target list as two linear extensions of the nonzero-pairing edge graph alone. Move the first task of the target extension leftward in the other list. Every crossed task is incomparable: a predecessor would also have to precede it in the target, and a successor cannot precede it in the original extension. Such a pair has Ω=0 by construction. P007 therefore exchanges it exactly without a mask. Remove the agreed first task and repeat. This constructs exact swaps preserving the nonzero-pairing edges. The final emitted list, independently, satisfies all added caller edges because it is topological for their union.

**Action and bill.** Reorder only with the explicit zero-pairing and dependency certificate. Instruction counts are unchanged; movement and new task-window charges must be recounted for the selected order. Dependencies: P007, P051. Target: safe physical retiming rather than free commutation. Provenance: sufficient trace-rescheduling construction.

<a id="p060"></a>

### P060. Producer fusion with its complete correction phase

**Statement.** Let the desired phase be Σ_j a_j·b_j. Put A=Σa_j, B=Σb_j and E=A·B+Σ_j a_j·b_j. Two aggregate W(A,B) words followed by D_E have the desired phase and return the bank.

**Proof.** The aggregate pair gives D_{A·B} by P002. Adding E cancels that aggregate product and leaves the specified diagonal sum. The expression for E includes all cross products created by fusion; none is assumed absent. Its computation is a finite polynomial calculation on the actual controls. If E=0 as a function, no correction instruction is emitted.

**Action and bill.** Replace 2f scalar W words by two aggregate W words only together with the charged E implementation and all parity controls. A physical aggregate producer has two bank basis changes, so the pair has four; the correction may erase any apparent benefit and must be expanded as well. Dependencies: P002, P012–P020. Target: PR #2850’s failed aggregation, now as a correct paid construction. Provenance: a sufficient fusion transform, not a new κ claim.

## VII. Endpoint adapters that preserve the declared ABI

<a id="p061"></a>

### P061. Disjoint role placement by a paid coordinate permutation

**Statement.** Let a controller act on listed distinct data/bank axes, and let an injective placement send those roles to equally many distinct physical axes. Extend the placement to a permutation σ of the finite axis set. Conjugating the controller by σ and its inverse realizes the same logical controller on the placed roles and returns every spectator role.

**Proof.** On a basis address, the first permutation puts exactly each logical coordinate in its declared physical position. The relabelled controller applies the original transition/sign to those coordinates and no others. The inverse permutation restores every position, including spectators that were temporarily moved. This proves the full operator identity without a zero-spectator assumption. A permutation extension exists by matching the two finite complements bijectively.

**Action and bill.** Emit both endpoint permutations or their explicit swap circuits, plus the controller. No two distinct roles may be placed on the same axis. Dependencies: direct basis evaluation. Target: physical caller layouts and bank placement. Provenance: an ABI-complete permutation adapter.

<a id="p062"></a>

### P062. Moving an accumulator endpoint without altering its operands

**Statement.** Suppose an explicit circuit U acts as |x,y,z⟩↦|x,y,z+F(x,y)⟩ on k-bit z, with a disjoint arbitrary k-bit w. Swap z,w, execute U on its original z wires, then swap back. The endpoint is |x,y,z,w+F(x,y)⟩.

**Proof.** The first swap gives (x,y,w,z); U gives (x,y,w+F,z); the second gives (x,y,z,w+F). This calculation uses arbitrary original values of z and w. It therefore preserves both literal operand registers and the unused accumulator, not merely their values on a zero-initialized example. Linearity gives the same joint-array identity.

**Action and bill.** Pay U and 2k bit swaps, or 6k elementary XORs. F must have its explicit supplied circuit; for finite F a truth-table permutation is also constructive, but not granted cheap. Dependencies: direct reversible calculation. Target: output-location changes with unchanged source ABI. Provenance: complete accumulator endpoint transport.

<a id="p063"></a>

### P063. The physical chart is the inverse transpose, with a circuit bound

**Statement.** Let R_L|x⟩=|Lx⟩ for invertible binary L on n axes. Then F_n R_L=R_{L⁻ᵀ}F_n. Thus a desired label chart A is physically implemented by R_{A⁻ᵀ}; both chart directions have explicit circuits of at most n(n−1)+3n XORs each.

**Proof.** The (u,x) entry of F_n R_L is (−1)^{u·Lx}=(−1)^{(Lᵀu)·x}. The right side has exactly that entry, because its row u reads Fourier row Lᵀu. For the circuit bound, eliminate L by choosing one pivot in each column, swapping rows with at most n swaps and clearing at most n(n−1) off-pivot entries. Each row addition is one reversible XOR and each row swap is three. Reversing these gates implements the inverse with the same bound.

**Action and bill.** Emit the actual inverse-transpose chart and its inverse. Confusing L with L⁻ᵀ changes the physical consumer. Dependencies: Walsh definition. Target: the chart comment in PR #2850 `c_word`. Provenance: classical Fourier covariance with a paid physical synthesis.

<a id="p064"></a>

### P064. A bank Fourier exchange retains its central sign and scale

**Statement.** The chronological bank sandwich H_b,W(a,b),H_b⁻¹ equals D_{a·b}W(b,a). Here H_b=2⁻ᵇF_b and its literal inverse is F_b.

**Proof.** Walsh conjugation exchanges a bank translation with its diagonal sign and exchanges a diagonal sign with its translation; direct summation of (−1)^{x·y} verifies both statements. Conjugating T_bS_a therefore produces S_bT_a in matrix order. Moving that sign past the translation contributes (−1)^{a·b}, leaving the normal W(b,a) order. The scalar normalization in H_b cancels only because its inverse includes the full factor 2ᵇ.

**Action and bill.** Use two paid bank basis changes and the retained data sign if implementing the exchanged normal form. Their finite/native expansions are P085 and P089; an inverse scale cannot be dropped. Dependencies: P020. Target: alternate producer/consumer polarizations in PR #2850. Provenance: complete physical Fourier adapter.

<a id="p065"></a>

### P065. Affine data re-encoding preserves a phase after explicit masks

**Statement.** Update u′=Lu+s and v′=Kv+t with invertible L,K. Put N=L⁻ᵀMK⁻¹. Apply D_{u′ᵀNv′}, then the masks uᵀLᵀNt+sᵀNKv+sᵀNt, and undo the two affine charts. The endpoint is D_{uᵀMv} on the original data ABI.

**Proof.** Expanding (Lu+s)ᵀN(Kv+t) gives uᵀMv and exactly the three displayed offset terms. Adding them again cancels them. The inverse affine charts restore u,v and all spectators. Every mask has an explicit finite formula; none requires a clean bank or an unproved recovery map. If a mask is evaluated after encoding, substitute the known inverse charts into its formula.

**Action and bill.** Pay both directions of both charts, the N phase controller and all nonzero linear/global masks. Dependencies: P012, P063. Target: a caller accepting an affine label encoding. Provenance: an ABI-complete affine phase adapter.

<a id="p066"></a>

### P066. A bounded window can move across arbitrary dirty exterior

**Statement.** Let U be a given linear operator supported on a finite set F of physical coefficient cells and identity outside F. A bijection F→G extends to a permutation of F∪G. Conjugating U by that permutation realizes its transported operator on G and identity outside G, with no assumption on the exterior coefficients.

**Proof.** The finite complements (F∪G)\F and (F∪G)\G have the same size, so any bijection between them extends the given bijection. The resulting permutation moves exactly the chosen finite support; conjugation transports the corresponding matrix block. On every other basis cell both permutations and the transported block give identity. Thus arbitrary dirty exterior coefficients pass through, including any correlations represented in a larger tensor space.

**Action and bill.** Emit the finite permutation, U and its inverse permutation. Charge every actual cell swap and head path; bounded support is not a license to assume the exterior is blank. Dependencies: finite complement matching. Target: local physical controllers hosted in an arbitrary larger bank. Provenance: constructive window relocation.

<a id="p067"></a>

### P067. A selector can choose a bank location coherently

**Statement.** Let a preserved data selector h choose one of k disjoint b-bit banks B_t, and supply one further disjoint b-bit workspace bank. For a given controller U acting on data and that workspace and preserving h, controlled swaps place B_h in the workspace, execute U there and swap back. The endpoint is U on the selected bank and identity on all other banks, for arbitrary selector/bank correlations.

**Proof.** Restrict to one selector value t. The two controlled swaps are then ordinary swaps between the workspace and B_t, so P049 proves the asserted operator on that sector. The selector is unchanged and its sectors partition the basis, hence summing their exact identities proves the coherent whole-space identity. The workspace’s arbitrary original contents return; no chosen branch starts clean.

**Action and bill.** A literal implementation enumerates k selector values and uses 2kb controlled bit swaps, with each predicate evaluated and paid or tabulated explicitly. Each controlled swap is three controlled XORs. U’s full array volume includes all candidate banks. Dependencies: P049. Target: dynamic but explicitly encoded bank placement. Provenance: constructive coherent location adapter.

<a id="p068"></a>

### P068. Endpoint permutation adapters have an exact transposition bill

**Statement.** A permutation of s logical bit roles with c cycles, counting fixed points, can be implemented by exactly s−c transpositions in its standard cycle construction. A forward/inverse endpoint adapter therefore costs 2(s−c) bit swaps and preserves all spectator roles.

**Proof.** For a cycle (a₁,…,a_ℓ), successive star transpositions with pivot a₁ implement that cycle in one of the two listed directions; choose the chronological direction matching the desired cycle. There are ℓ−1 such transpositions. Disjoint cycles act on disjoint coordinates, so their products realize the permutation and the sum is Σ(ℓ−1)=s−c. Reverse the same list for the inverse. Composing around a relabelled controller yields P061’s ABI claim.

**Action and bill.** Pay 6(s−c) XORs if swaps use three XORs each, plus their actual full-array movement bills. The statement counts the explicit construction, not a hardware minimum. Dependencies: P061. Target: paid endpoint role permutations. Provenance: cycle synthesis with a full two-sided adapter cost.

<a id="p069"></a>

### P069. Opposite-polarity output ports can be corrected without bank preparation

**Statement.** Suppose a native port supplies S_a,T_b but a caller requires the opposite chronological order T_b,S_a. Append the data mask D_{a·b} to either supplied order to obtain the other exactly, with the same bank translation and no changed data coordinates.

**Proof.** Order S then T has sign a·c. Order T then S has sign a·(c+b)=a·c+a·b. Their shift is b in both cases. Multiplying by the explicitly supplied data mask changes exactly this sign difference. This proves equality on arbitrary bank lanes, not just the lane c=0, and remains true inside a larger control-preserving context.

**Action and bill.** Pay the mask via P012 or its physical implementation P088/P091. Keep both original controls and every movement operation. This is a small but complete producer/consumer ABI adapter, not a claim that ordering is irrelevant. Dependencies: background. Target: actual port-order mismatches in a phase accumulator caller. Provenance: explicit phase-corrected port adapter.

<a id="p070"></a>

### P070. A supplied Clifford chart has a fully computable Pauli adapter

**Statement.** Given an explicit bank circuit G of XOR, one-axis H₀ and S=diag(1,i), conjugating any Pauli-controlled W(a,b) by G gives i^{k(d)}W(a′,b′), with a′,b′ and k computable gate by gate. Emitting that computed scalar gives an exact charted port, without a clean bank.

**Proof.** For H₀, direct 2×2 multiplication exchanges X and Z and contributes (−1)^{ab} on reordering. For S, SXS⁻¹=iXZ and SZS⁻¹=Z. For XOR from control c to target t, the images are X_cX_t, X_t, Z_c and Z_cZ_t respectively; these follow by applying each side to a two-bit basis vector. These rules generate the conjugate of a product by multiplication, moving all X before all Z and recording every anticommutation sign in k modulo four. Induction on the supplied G proves the formula including its scalar.

**Action and bill.** Either execute G, W, G⁻¹ or the computed controls and scalar table, paying their actual circuits. This does not assume that an arbitrary abstract symplectic matrix has a free implementation. Dependencies: the displayed generator checks. Target: a concrete changed native bank chart. Provenance: classical Clifford propagation used as a complete physical adapter.

## VIII. Exact routing, movement and finite record schedules

The following chapter distinguishes a swap of **address-bit axes** from a swap of **complex coefficient cells**. Axis XOR/SWAP is an array permutation and its coefficient-cell implementation still runs on all N cells. Wire-graph distance is not silently substituted for tape-head travel.

<a id="p071"></a>

### P071. A two-cell read/read/write/write record has an exact head path

**Statement.** For coefficient-cell addresses 0≤a≤b, a record starting at cell 0, reading a,b, writing a,b and returning to 0 travels exactly 4b−2a cell steps. It reads and writes four real components each and visits complex cells four times.

**Proof.** Its five path lengths are a, b−a, b−a, b−a and b. Their sum is 4b−2a. Two complex reads and two complex writes give the component counts; distinct addresses are not needed for the arithmetic sum, although a=b may permit a separately optimized record. Scratch arithmetic takes place only after the old inputs are read, so every dirty coefficient is processed by the specified record.

**Action and bill.** Use this literal record for a butterfly or cell swap and charge its actual addresses, not just its gate name. The bill agrees with the predecessor’s declared record convention. Dependencies: absolute-value path summation. Target: PR #2850 `invoice.py` two-cell records. Provenance: exact finite implementation theorem.

<a id="p072"></a>

### P072. Reverse output visits legally halve the outer excursion

**Statement.** A k-input/k-output record whose distinct input locations and output locations are the same a₁<…<a_k, with a supplied arithmetic circuit producing all outputs in at most 2k complex private slots, can read in increasing order, compute all outputs in that work, write in decreasing order and return to 0. Its cell travel is exactly 2a_k and its semantics equals writing the same outputs in increasing order.

**Proof.** All old inputs have been copied before any output write. Therefore the computed output values are independent of the later write order, provided each output address has one specified final value. The head moves monotonically from 0 to a_k and then monotonically back to 0, giving 2a_k. There are k complex reads and k writes. Keeping at most k old inputs and k outputs uses 2k complex private slots, which are explicitly initialized and cleared.

**Action and bill.** Pay 2k real reads and writes each, 4k private-real startup clears once, and up to 4k private-real clears per record, with the arithmetic bill retained. This is a concrete alternative record schedule, not free random access. Dependencies: record input/output discipline. Target: cheaper actual head travel for physical butterflies. Provenance: constructive write-order change.

<a id="p073"></a>

### P073. Removing only inter-record returns preserves every arithmetic prefix

**Statement.** In a sequence of records, replace a completed record’s return from its last address b to 0 and the next record’s trip from 0 to its first address a by the direct trip b→a. Keep each record’s reads, arithmetic, writes and scratch clears unchanged. The program endpoint is identical and saves exactly 2min(a,b) steps at that boundary.

**Proof.** After a record’s writes and clears, the only altered machine state is the data-head position. Moving directly to the next first address therefore gives the same values and private state at the next read. The old route has length b+a and the new route |b−a|, whose difference is 2min(a,b). Applying this replacement at successive boundaries proves equality by induction on completed records. The final return to 0 is retained.

**Action and bill.** Sum the displayed saving over actual adjacent records; pay all unchanged arithmetic/access/clear/dispatch costs. This is a declared alternative machine schedule, not an omission from the inherited invoice. Dependencies: P071–P072. Target: controller record batching and paid movement. Provenance: constructive head-position reuse.

<a id="p074"></a>

### P074. Arbitrary coefficient permutations need no second data array

**Statement.** A permutation of N coefficient cells can be executed cycle by cycle in place, using two complex private slots. A nontrivial cycle of length ℓ uses ℓ complex reads and ℓ writes and restores all cells outside the cycle.

**Proof.** Read the first cell into a carry slot. At each later cycle cell, read its old value into the second slot, write the carry there, and replace the carry by the saved old value. Finally write the carry into the first cell. Each original coefficient moves to its prescribed successor and no old value is overwritten before being saved. Disjoint cycles can then be processed independently. Clear both private slots after each cycle and at startup.

**Action and bill.** Pay 2ℓ real reads and writes each, four private-real clears per cycle plus startup, and the literal cycle-visit head path. Fixed cells require no record. This realizes an arbitrary finite routing map without granting another N-cell operand. Dependencies: cycle decomposition. Target: physical gather/scatter and endpoint permutations. Provenance: explicit in-place array routing.

<a id="p075"></a>

### P075. A path transposition restores every intermediate bank axis

**Statement.** On a path of d edges between two logical bit-axis locations, the adjacent-swap word forward along all d edges and backward along the first d−1 edges swaps only the two endpoints. It uses 2d−1 axis swaps when d≥1; d=0 uses none.

**Proof.** Track the first endpoint value through the forward swaps to the last vertex. Each intermediate value shifts one position toward the first endpoint. The backward swaps then move the original last value to the first and shift each intermediate value back to its original vertex. Thus the endpoint transposition is exact on arbitrary bit values, with all other coordinates restored. The reverse sweep omits the final edge, giving d+(d−1) swaps.

**Action and bill.** Pay three axis XORs per axis swap, and then the full coefficient-array permutation cost of each XOR if that is the implementation model. These graph-edge counts are not tape steps. Dependencies: direct permutation tracking. Target: bank-axis routing through dirty intermediate locations. Provenance: a complete endpoint routing word.

<a id="p076"></a>

### P076. A live bank can walk to a remote port and return

**Statement.** Let a bank axis start at one end of a path of d edges. Swap it successively along all edges, execute a port operation at the remote endpoint, then reverse every swap. If that operation uses the transported bank and external roles outside the path, the result is the intended operation on the original bank and identity on intermediate axes.

**Proof.** The forward path permutation P carries the original bank value to the remote endpoint, though it also cycles intermediate values. The remote operation does not use those intermediate roles. Conjugation by P and P⁻¹ therefore transports its bank argument back to the original axis and cancels every other positional change. The equality is an operator identity on all arbitrary path values.

**Action and bill.** Pay 2d axis swaps, or 6d axis XORs, plus the remote operation and all coefficient movement. For b axes on disjoint supplied paths sum these bills. Dependencies: P049, P061. Target: an actual geographically separated producer/consumer port. Provenance: paid live-bank walk with complete restoration.

<a id="p077"></a>

### P077. Arbitrary axis layouts have a terminating adjacent-swap router

**Statement.** For n ordered axis locations and a desired permutation, bubble each next required logical role leftward into position. The resulting fixed router uses exactly K adjacent swaps, where K is the inversion count of the desired role order; its inverse has the same count.

**Proof.** Whenever adjacent out-of-order roles are swapped, their mutual inversion disappears and no other pair changes relative order, so the inversion count decreases by exactly one. The left-to-right placement procedure always chooses such swaps and ends at the desired sorted role order. Therefore it performs exactly K swaps, with K≤n(n−1)/2. Reversing the list implements the inverse on arbitrary axis values.

**Action and bill.** A two-sided adapter costs 2K axis swaps, or 6K axis XORs, before their whole-array realization. The router is generated from fixed metadata, not by comparing live data amplitudes. Dependencies: P061. Target: explicit layout compilation for bank/controller axes. Provenance: constructive sorting router with a paid endpoint bill.

<a id="p078"></a>

### P078. Disjoint coefficient records may be reordered with an actual support proof

**Statement.** Suppose each completed record acts linearly on a declared coefficient-cell set, and two records’ sets are disjoint. Exchanging those records preserves the array endpoint. Any permutation obtained by such exchanges is legal if descriptor and private-work effects are unchanged or separately restored.

**Proof.** In the decomposition into the two support sets and their complement, the record matrices are respectively A⊕I⊕I and I⊕B⊕I. Their products in either order equal A⊕B⊕I. Private work is cleared at each record boundary by hypothesis, so it introduces no hidden dependence. Repeating these exact local exchanges proves the chosen schedule’s semantics on arbitrary coefficients.

**Action and bill.** Use actual read/write supports to reorder records for a shorter head path, then sum that new path explicitly. Shared-bank or merely similarly named gates do not satisfy the theorem automatically. Dependencies: matrix block evaluation. Target: safe physical-record scheduling. Provenance: support-certified movement optimization.

<a id="p079"></a>

### P079. Closed travel formula for every butterfly of one axis

**Statement.** Let N=2ⁿ, choose an address axis a<n and put h=2ᵃ. Execute every pair (j,j+h) with bit a of j zero using P071’s record. The total return-to-zero cell travel is N(N−1+3h)/2.

**Proof.** There are N/2 left addresses. Their sum is N(N−1−h)/4: each bit other than a is one at exactly half these addresses, while bit a is always zero. The record travel at j is 4(j+h)−2j=2j+4h. Summing gives 2·N(N−1−h)/4+4h·N/2, the claimed expression. The formula includes h=1 and n=1 without an exceptional convention.

**Action and bill.** Add this exact formula for the actual emitted axes and retain every arithmetic/access/scratch charge. It directly reproduces the predecessor’s full-array C-axis movement, including spectators. Dependencies: P071. Target: PR #2850 native butterfly invoice. Provenance: an exact symbolic finite travel count.

<a id="p080"></a>

### P080. Reverse-write butterflies save a paid N·2ᵃ steps per axis

**Statement.** Replace every P079 butterfly record by reading its two old inputs, computing both outputs and writing the high address before the low address. The array endpoint is unchanged and total cell travel becomes N(N−1+h)/2, saving exactly Nh.

**Proof.** P072 makes one such record travel 2(j+h), with both outputs computed from the same saved old inputs. Summing over left addresses gives 2·N(N−1−h)/4+2h·N/2=N(N−1+h)/2. Subtracting this from P079 gives Nh. Different butterflies of one axis are disjoint, so completing each replacement preserves that whole axis; induction over emitted axes preserves the full program.

**Action and bill.** Keep the existing eight private real slots for a two-complex-input/two-output butterfly and every arithmetic/halving/clear/access count. Only the declared write order and head route change. This is a constructive finite movement reduction, not a new child-width or κ theorem. Dependencies: P072, P079. Target: an implementable cheaper physical record convention. Provenance: explicit alternative to the frozen invoice’s increasing-write schedule.

## IX. Complete finite-array realizations

<a id="p081"></a>

### P081. A sign mask has an exact finite scalar-access bill

**Statement.** For a supplied mask q on the complete N-cell address set, D_q is implemented by negating both real components exactly at addresses S={j:q(j)=1}. It uses 2|S| real negations, 2|S| real reads and writes each, and no division or extra data array.

**Proof.** At a selected address multiplication by −1 negates its real and imaginary parts; at every other address the coefficient is unchanged. Processing selected cells therefore gives precisely the diagonal operator. A one-cell record starts at 0, reads both components, writes their negatives and returns, traveling 2j steps at address j. Two private real slots suffice, initialized once and cleared after each record. Summing gives head travel 2Σ_{j∈S}j and 2|S| private clears plus two startup clears.

**Action and bill.** This realizes a finite correction mask without a phase oracle. Pay the mask table/generation and its actual selected-cell traversal. Bank and spectator lanes are included in S. Dependencies: direct complex negation. Target: the physical cost of corrections in P001/P006. Provenance: explicit array implementation.

<a id="p082"></a>

### P082. An arbitrary controlled bank translation is a known swap list

**Statement.** For a supplied b-bit function β(d), b≥1, T_β on the full address array is a disjoint product of exactly 2^{b−1}·#{d:β(d)≠0} coefficient-cell swaps per fixed spectator lane.

**Proof.** At fixed d with β=0 all bank labels are fixed. If β≠0, c↦c+β is a fixed-point-free involution, partitioning 2ᵇ labels into 2^{b−1} two-cycles. Enumerate each cycle once using the smaller encoded address. Those swaps implement the exact translation; data/spectator labels never change. Arbitrary initial coefficients at both ends are exchanged rather than overwritten.

**Action and bill.** Pay four real reads, four real writes and four private-real clears per swap, plus startup and the P071 or P072 route. This explicitly counts every dirty bank lane. Dependencies: P071, P074. Target: physical realization of a nonzero aggregate bank shift. Provenance: exact permutation-cycle count.

<a id="p083"></a>

### P083. Fusing linear XOR controls has a rank-dependent swap count

**Statement.** Let β(d)=Bd have binary rank r. On N=2^{n+b+s} cells, where s counts spectator bits, one aggregate T_β uses N(1−2⁻ʳ)/2 disjoint cell swaps. The elementary wt(B)-XOR realization uses wt(B)N/4 cell swaps before cancellations, provided each control and target axis is distinct.

**Proof.** The kernel of B has 2^{n−r} elements: select r pivot coordinates and solve uniquely for them from the other n−r free coordinates. Thus the fraction of data labels with β≠0 is 1−2⁻ʳ. P082 gives the first count after multiplying spectator lanes. One elementary controlled XOR moves exactly those addresses with its independent control bit one; half of those form unique target-bit two-cycles, giving N/4 swaps. Summing the literal elementary implementation gives the second count.

**Action and bill.** Choose between the aggregate truth-table swap list and the sparse XOR list, charging generation, storage and actual head paths for that choice. The count does not drop inactive bank lanes from N. Dependencies: P082. Target: complete cost comparison for P060’s aggregate controls. Provenance: an exact physical fusion bill.

<a id="p084"></a>

### P084. The negative entries of a bilinear sign mask are exactly counted

**Statement.** For M of rank r on m+n data bits, D_{uᵀMv} negates exactly (2^{m+n}−2^{m+n−r})/2 data addresses. Multiply this by the number of bank/spectator lanes for the complete array bill.

**Proof.** Sum (−1)^{uᵀMv} over all u,v. For a fixed v, summing over u gives 2ᵐ if Mv=0 and zero otherwise, by pairing u with a coordinate flip having nonzero pairing. There are 2^{n−r} kernel vectors, so the signed sum is 2^{m+n−r}. The signed sum is also the number of positive addresses minus the number of negative ones, while their sum is 2^{m+n}. Solving gives the stated count, including r=0.

**Action and bill.** Substitute that exact number into P081’s scalar/access invoice, still paying basis adapters if the labels are Fourier labels. Dependencies: P081. Target: direct versus bank-factor correction costs. Provenance: constructive full-array mask count from character cancellation.

<a id="p085"></a>

### P085. Dyadic Walsh transforms have literal butterfly programs and inverses

**Statement.** H_b=2⁻ᵇF_b on b specified address axes of an N-cell array is implemented by bN/2 two-cell butterflies. Each butterfly performs four real additions/subtractions and four exact halvings. Its inverse uses the same number of butterflies and four real additions/subtractions but no halvings per butterfly.

**Proof.** On one axis the pair map is (z₀,z₁)↦((z₀+z₁)/2,(z₀−z₁)/2); its inverse is (w₀,w₁)↦(w₀+w₁,w₀−w₁). Splitting complex numbers gives the asserted real arithmetic. The b one-axis maps tensor together, with N/2 disjoint pairs at every axis, to give H_b and its literal inverse. Every pair is processed from saved old inputs, so the program works on arbitrary array values.

**Action and bill.** Forward arithmetic is 2bN real additions and 2bN halvings; inverse arithmetic is 2bN additions and no halvings. Both retain four real reads/writes and eight private-real clears per butterfly, plus startup and actual movement. Exact-grid admission must guarantee even numerators when halvings are used. Dependencies: P071–P072. Target: the priced H₀/H₀⁻¹ bank adapters. Provenance: complete finite dyadic implementation.

<a id="p086"></a>

### P086. A controlled translation has a paid Fourier-bank implementation

**Statement.** For unchanged data control β(d), the chronological word H_b,D_{β(d)·c},H_b⁻¹ implements T_β exactly on a dirty bank.

**Proof.** Its matrix coefficient from c to c′ is 2⁻ᵇΣ_t(−1)^{t·c+β(d)·t+t·c′}. The character sum is 2ᵇ precisely when c′=c+β(d), and zero otherwise. Thus it is the desired permutation, with its normalization exactly cancelled. Data values are unchanged, so β(d) is the same in all three steps. The equality is valid in every spectator fiber.

**Action and bill.** Pay two full bank Walsh transforms from P085 and the complete sign pass from P081/P084. This is an actual implementation when translation is unavailable but the specified basis operations exist; it is not a reduction of the bank’s full operand volume. Dependencies: P085. Target: the physical X(v) portion of PR #2850’s producer. Provenance: Fourier-bank construction with the literal inverse scale.

<a id="p087"></a>

### P087. Every binary bilinear phase has an explicit physical kernel

**Statement.** On m+n physical data bits let Q_M=F_{m+n}⁻¹D_{uᵀMv}F_{m+n}, with rank M=r. Its convolution kernel at displacement (a,b) is zero unless a∈im M and b∈im Mᵀ. Otherwise it equals 2⁻ʳ(−1)^{b·v₀}, where Mv₀=a. Each column has exactly 2^{2r} nonzero entries.

**Proof.** Expanding the Fourier conjugation gives 2^{−m−n}Σ_{u,v}(−1)^{uᵀMv+u·a+v·b}. Summing over u restricts to Mv=a and leaves 2⁻ⁿΣ_{Mv=a}(−1)^{v·b}. A solution set is v₀+ker M. Its character sum vanishes unless b annihilates ker M, which is im Mᵀ by elementary row reduction. In that case it has 2^{n−r} equal terms, proving the formula. The images each have 2ʳ elements; the sign is independent of v₀ because b annihilates the kernel.

**Action and bill.** This supplies an explicit reference endpoint on every dirty spectator lane. A direct realization is P020 with the completely enumerated mask, costing both data Walsh directions and the mask. Dependencies: P020, P084. Target: a nonidentity quadratic phase consumer with no assumed physical oracle. Provenance: a complete constructive Fourier kernel.

<a id="p088"></a>

### P088. Rank-normalized physical Q uses two rank-r Walsh children

**Statement.** Choose invertible binary A,B with M=AᵀJ_rB, where J_r pairs the first r coordinates. Apply physical charts A⁻ᵀ,B⁻ᵀ, then H_r⁻¹ on the first x block, the XOR y_i+=x_i for i≤r, then H_r, and undo the charts. The endpoint is Q_M.

**Proof.** For one paired axis, the middle sandwich has kernel 1/2·(−1)^{(x′+x)(y′+y)}, by summing its two intermediate x values. Tensoring these r kernels gives Q_{J_r}, with identity on the remaining axes. The Fourier-label charts are A,B by P063, so conjugation changes its exponent to (Au)ᵀJ_r(Bv)=uᵀMv. Row/column elimination constructs the required rank normal form and all inverse charts. For r=0 the entire Q is identity and no child is emitted.

**Action and bill.** Pay two r-axis Walsh calls, r axis XORs, both directions of both charts and their native wrappers. In the predecessor’s alphabet this means two C_r children, each on the full N cells, not a half-volume child. Dependencies: P063, P085, P087. Target: a concrete cheaper-than-four-bank-basis comparator for any actual correction matrix. Provenance: the PR #2850 two-C construction extended with paid rank charts.

<a id="p089"></a>

### P089. The predecessor’s unfused producer has a complete native wrapper count

**Statement.** On b bank axes and matching physical x,y controls, emit bank→x XOR, H_b, bank→y XOR, H_b⁻¹. Expanding each H through the predecessor’s C kernel uses two C_b children, six coordinate-phase layers, one positive and one negative b-scale block and one global fourth-root phase. Repeating the producer twice doubles each count and returns the bank with Q_b.

**Proof.** Write S=diag(1,i), β=(1−i)/2 and C=[[1+i,1−i],[1−i,1+i]]/2. Direct 2×2 multiplication gives H₀=βSCS and C⁻¹=−iZCZ. Thus forward H uses two S layers, one C and β scaling. Its inverse uses β⁻¹, two S⁻¹ layers, the two Z layers from C⁻¹, one C and the global −i. Tensoring b axes gives the stated phase/scaling powers. In Fourier data coordinates the whole producer is W(u,v), so its square gives the intended phase by P002.

**Action and bill.** Count two packed XORs per producer as well. The literal inherited denominator counter charges 3b per producer: two C widths plus the positive β scale; the inverse scale is retained rather than erased. This is a sufficient syntactic counter, not a minimal precision bound. Dependencies: P002, P086. Target: exact `accumulator_word`/`h_word` native emission in PR #2850. Provenance: explicit source reconstruction and bill.

<a id="p090"></a>

### P090. A declared finite record program has an explicit bit-machine implementation

**Statement.** Given a valid list of L≥0 finite records, N=2ⁿ with n≥0 and signed width B≥1, of the predecessor’s seven types (C, swap, β-scale in either direction and the three nontrivial fourth-root rotations) on those N cells, with every intermediate fitting B+2 and every required halving even, their arithmetic and control can be implemented on a fixed multitape bit machine. If D_data is the literal data-head bit travel, at most 20D_data + 10⁶(L+1)(B+n+⌈log₂(L+1)⌉+1)² machine steps suffice, including movement control and finite-register startup, plus loading L(4+2n) descriptor bits.

**Proof.** Store at most eight private real registers, two n-bit addresses, a record counter and a constant number of flags. Their total length is below 20D, where D=B+n+⌈log₂(L+1)⌉+1. Implement a signed addition by a ripple pass, negation by complement/carry, and exact halving by a checked shift; each uses fewer than 64D elementary bit/flag actions. One record has at most twelve additions, four halvings, a constant number of sign changes, clears, copies and counter/descriptor passes, all below 2000D such actions. Use marked bit cursors in the fixed register regions; locating each next arithmetic bit needs at most a scan out and back through 20D cells, so no random-address oracle is used. Their product is below 10⁶D². Compute each required travel distance in the same register bill. A binary countdown controls that walk: decrementing visits the trailing zeros and the next one, and the total such visits over M decrements is below 2M+D. A marker on the highest one detects zero and updates locally when that bit disappears. With return visits and fixed flags, fewer than 20M steps pay the M data-head moves and their control. Summing the routes, records and finite-register startup proves the stated bound.

**Action and bill.** This gives a constructive conservative control/ALU bill instead of setting it to zero. Computing the record list itself is not assumed free; if supplied as input, loading writes all descriptor bits. Dependencies: P071–P085 and the explicit width/divisibility admission. Target: the formerly unpriced finite control terms in PR #2850 `invoice.py`. Provenance: a concrete sufficient bit-machine upper bound, not an optimized native admission.

## X. Closed physical assemblies for the live phase/order handoff

<a id="p091"></a>

### P091. A caller-fixed shared-bank order always has a bank-free physical repair

**Statement.** Use one bank bit for the literal producer-prefix/consumer-permutation schedule on f columns. Let E be its actual crossing matrix. Append Q_E on the physical x,y data using P088. The complete endpoint is I_bank⊗Q_{I_f}, without changing the consumer order or adding a prepared bank.

**Proof.** In the Fourier data basis, P006 gives the literal endpoint D_{uᵀ(I_f+E)v} with bank identity. The appended Q_E is D_{uᵀEv} in that same basis. The two exponents add to u·v, and the original arbitrary bank stays untouched by the bank-free repair. Both basis adapters in P088 are explicit physical operators, so the conclusion is a physical-array equality, not just a scalar phase computation.

**Action and bill.** The unfused predecessor contributes 4f one-axis C calls and all wrappers. If rank E=r, the repair adds two C_r calls, the rank charts and their inverses, r XORs and all phase/scale wrappers, on the same full N. No contraction is asserted from that bill. Dependencies: P006, P088–P089. Target: the concrete changed-consumer question in PR #2859. Provenance: sufficient physical repair with the full extra cost exposed.

<a id="p092"></a>

### P092. Correct aggregate production with arbitrary encoded bank controls

**Statement.** For any target binary M and any chosen b-row matrices A,B, implement two aggregate physical producers corresponding to W(Au,Bv), then append Q_{M+AᵀB}. The endpoint is Q_M with the entire arbitrary b-bit bank returned.

**Proof.** For the physical producer, translate x by Aᵀc, apply H_b, translate y by Bᵀc and apply H_b⁻¹. In Fourier data coordinates its action is exactly W(Au,Bv) by P086 and the sign of a controlled physical translation. The doubled producer gives phase uᵀAᵀBv. P088 implements the residual phase M+AᵀB physically and without touching the bank. Adding them gives M. No rank or source relation is assumed unless explicitly used in choosing A,B.

**Action and bill.** Pay four C_b children from the doubled producer, 2wt(A)+2wt(B) axis XORs and the P089 wrappers. A residual of rank r adds two C_r children, its charts/XORs and wrappers. At b=0 omit the producer and use the direct residual. Dependencies: P060, P088–P089. Target: the aggregate-bank shortcut corrected into an actual physical construction. Provenance: a complete encoded producer/consumer pair, without a hypothetical favorable price.

<a id="p093"></a>

### P093. The ternary C/Q assembly is an all-size physical identity

**Statement.** For f≥1 put p=a+b+c, u=a+c, v=b+c on each Fourier-label triple. Implement that invertible chart physically by its inverse transpose, apply C_f on p and Q_f on (u,v), translate all three encoded physical blocks by ones, and undo the chart. This is exactly C_{3f}.

**Proof.** If w=a+b+c is the integer sum, checking w=0,1,2,3 gives w≡p+2(ab+ac+bc) mod 4. Also uv+c=ab+ac+bc in F₂, while p+u+v=c. The child multipliers are i^p and (−1)^{uv}; the encoded all-ones translation contributes (−1)^{p+u+v}=(−1)^c. Their product is therefore i^{a+b+c}, the multiplier of the three C axes. Tensoring columns proves the f-column identity. The chart is invertible and physically implemented as in P063.

**Action and bill.** The predecessor’s four packed XOR chart operations and their inverse give eight packed XORs; also pay one C_f, one Q_f, 3f fixed bit translations and every child’s full operand volume. This recovers its exact assembly, not a favorable recursive budget. Dependencies: P063, P088 and the displayed C eigenvalues. Target: `c_word` in PR #2850. Provenance: credited all-size reconstruction with the wrapper bill retained.

<a id="p094"></a>

### P094. Exact child substitution remains valid at open and nested boundaries

**Statement.** In a finite emitted physical word, replace any C or Q occurrence by an explicit equal matrix on exactly the same full array, and any inverse occurrence by the literal inverse replacement. The entire word and every retained module boundary are unchanged, even when the bank is open there.

**Proof.** Replacing one factor of a matrix product by an equal matrix leaves that product unchanged for every input. Tensoring with all spectator identities is part of the equality hypothesis, so it also covers arbitrary live-bank correlations. Repeating the replacement through the finite syntax tree proves the assertion at every node; each boundary whose surrounding factorization is retained has the same prefix product. The argument never substitutes a zero-bank test for full operator equality.

**Action and bill.** Sum the replacement leaves and all remaining wrappers exactly once. A fully expanded butterfly bill must not also add its abstract child price. This supplies a constructive two-level or finite-depth emitter contract when using P088/P093; it is not an analytic exponent theorem. Dependencies: P088–P093. Target: PR #2850’s nested live-bank substitution. Provenance: exact typed physical assembly with no prepared-state loophole.

<a id="p095"></a>

### P095. A genuine accumulator write can occur inside an open bank interval

**Statement.** Let a(x),b(x) depend only on immutable x, and let U_F update a disjoint dirty accumulator z by z+=F(x), preserving x. Then W(a,b),U_F,W(a,b) implements U_F together with D_{a·b}, returning the bank and preserving x.

**Proof.** On input (x,z,c), the first W reads a(x),b(x). U_F changes only z, so the consumer reads the same controls and produces their pairing exactly as P002. Its bank shift cancels. The output z+F(x) is unaffected by the phase calculation and can be arbitrary initially. This proves the actual accumulator ABI, rather than assuming that all intervening caller work is diagonal.

**Action and bill.** Pay both W words, U_F’s explicit permutation circuit and its access/movement bill. If F is a given finite table it is implementable by P074; if F is bilinear, P096 supplies a direct finite program. Dependencies: P002, P042. Target: an open bank enclosing real output production. Provenance: constructive mutable-output continuation under a read-only label contract.

<a id="p096"></a>

### P096. A binary bilinear accumulator has a complete finite permutation program

**Statement.** Let F:F₂ᵐ×F₂ⁿ→F₂ᵏ be given by coefficients T_ℓij. For each nonzero coefficient execute z_ℓ+=u_i v_j. These t three-axis controlled flips implement z+=F(u,v), preserving both operands and every spectator. On the full N-cell array each such flip is exactly N/8 coefficient swaps.

**Proof.** All controls u_i,v_j are unchanged and only z coordinates are written. The output sums therefore add over F₂ to the specified bilinear tensor coefficients. For one flip, exactly one quarter of addresses satisfy the two independent controls; their target coordinate pairs into two-cycles, giving N/8 swaps. Each controlled flip is an explicit permutation, and P074 implements its swaps in place with arbitrary old accumulator values. No quantum state copying or clean accumulator is used.

**Action and bill.** Pay tN/8 swaps, four real reads/writes/clears per swap, startup and the exact swap routes. This is a fully finite realization, not an assertion that the predecessor has a cheap Toffoli child or that integer carries disappear. Dependencies: P074. Target: an actual producer usable inside P095. Provenance: explicit bilinear-to-accumulator physical synthesis.

<a id="p097"></a>

### P097. An arbitrary finite residual phase has a physical table consumer

**Statement.** Given a complete table q:F₂ⁿ→Z/4Z, the physical operator F_n⁻¹diag(i^{q})F_n has a finite exact implementation using two n-axis Walsh transforms and one table-driven rotation pass, with bank identity and no new irrational arithmetic.

**Proof.** First apply H_n, rotate each label coefficient by its specified fourth root and apply H_n⁻¹. The resulting conjugation is precisely the claimed operator because scalar normalizations cancel. A rotation by i or −i swaps real/imaginary components with one negation; rotation by −1 uses two negations; zero phase does nothing. Thus the middle pass uses only exact copies and signs. All bank/spectator fibers receive the same specified action and remain in the array.

**Action and bill.** Load 2·2ⁿ phase-table bits, pay both Walsh directions and the actual counts of rotations, reads/writes, clears and head travel. This supplies a constructive nonlinear or fourth-root residual consumer from an explicit table, not from an assumed phase oracle. Dependencies: P020, P085. Target: corrections after more general caller mutations or Clifford charts. Provenance: full finite phase-table synthesis with paid data adapters.

<a id="p098"></a>

### P098. Unobserved monomial wrapper runs can be compiled into one exact table

**Statement.** Let a run of L monomial maps send |j⟩ to i^{h_t(j)}|σ_t(j)⟩, with no observation or child call between them. Compute σ=σ_L∘…∘σ₁ and h(j)=Σ_t h_t(σ_{t−1}…σ₁j) modulo four. One h rotation pass followed by the σ cycle permutation replaces the whole run exactly.

**Proof.** Induction on the number of maps shows that the current basis index is the partial permutation and the accumulated exponent is the corresponding partial sum. At L it is exactly the displayed pair (σ,h). The replacement therefore has the same image of every basis vector. Each old and new prefix is monomial with unit-modulus entries, so no amplitude is discarded and no nonunit scalar is hidden. Intermediate observations are explicitly excluded because only the whole run is replaced.

**Action and bill.** Generation performs L N permutation/phase-table lookups and additions and writes N(⌈log₂N⌉+2) output bits. Execution pays the complete rotation pass and P074 cycle routing, not a free fused gate. Dependencies: P074, P081. Target: the phase/XOR/translation wrapper runs in the physical emitter. Provenance: exact wrapper compilation with both generation and execution bills.

<a id="p099"></a>

### P099. Actual C symmetries permit paid chart absorption

**Statement.** Let P=D R_σ, where R_σ permutes address axes and D is an invertible diagonal map (every diagonal entry is nonzero) depending only on axes outside a C-active set A. The chronological sandwich P,C_A,P⁻¹ equals C_{σ⁻¹(A)}. Thus those two adapters may be removed and the child axes reindexed.

**Proof.** Since D has the same value on both members of every active-axis butterfly, it commutes with C_A, and D⁻¹ cancels it in the sandwich. Axis permutation conjugation sends the tensor C factors exactly to the preimage axes σ⁻¹(A), with their order irrelevant because the tensor factors commute on disjoint axes. This proves the equality on the entire array. A phase depending on active axes does not satisfy the hypothesis and cannot be absorbed by this theorem.

**Action and bill.** Emit the same-width C child on the explicitly reindexed axes; omit only these proven adjacent adapters. Recount its head route, charts at other boundaries and all prefix/precision facts. Arbitrary symplectic or dense linear charts are not covered. Dependencies: direct butterfly/tensor evaluation. Target: source-supported endpoint wrapper reduction around actual C calls. Provenance: a sufficient symmetry-based physical compiler rewrite.

<a id="p100"></a>

### P100. Common-label phase jobs fuse into one fully corrected physical consumer

**Statement.** Suppose an unobserved run consists of closed physical phase jobs Q_{M₁},…,Q_{M_L} in the same Fourier-label chart, with no intervening label-changing operation. Put M=Σ_j M_j over F₂. Replace the run by the P088 implementation of Q_M, leaving every returned bank unused. The whole endpoint and external operand ABI are identical.

**Proof.** In the common Fourier basis every job is diagonal with exponent uᵀM_jv. Their product has exponent uᵀ(ΣM_j)v, so it is exactly Q_M after conjugating back. Every original job is identity on its bank; the replacement is bank-free, hence identity on all those arbitrary bank factors. All common data coordinates and spectators have the specified original endpoint. If M=0 the exact replacement is the empty identity word. The hypothesis excludes caller observations that would require intermediate job outputs.

**Action and bill.** A rank-r sum has two C_r children plus the explicit rank charts, XORs, phases, scales and their full-array/bit-machine costs from P088–P090. Compare that complete bill against all original jobs; do not infer a gain from rank alone. Fresh internal-prefix bounds are needed for the replacement, while completed endpoints are exact. Dependencies: P088, P094. Target: a genuinely changed consumer for the live PR #2850/#2859 handoff. Provenance: constructive common-label physical fusion, not a numerical κ claim.

## Source, proof and research boundaries

These are complete informal proofs in the stated finite models. They establish algorithms or sufficient physical contracts with explicit emitted work. They do not supply an actual selected caller merely by naming one. A source-space promise, common-label region, allowed bank location, timing window or supplied chart must be demonstrated by the actual consumer before its associated theorem can be applied. Every additional control, correction, basis change, generator, storage location and restored endpoint is part of the bill. The new words require their own prefix/precision and actual source/native admission; equality of returned bank coordinates is never substituted for equality of the full operator.

Classical background includes finite Pauli/Heisenberg algebra, quadratic-form Clifford descriptions, binary elimination, cycle routing and finite Fourier character sums. Primary references are Jeroen Dehaene and Bart De Moor, [The Clifford group, stabilizer states, and linear and quadratic operations over GF(2)](https://arxiv.org/abs/quant-ph/0304125); Scott Aaronson and Daniel Gottesman, [Improved Simulation of Stabilizer Circuits](https://arxiv.org/abs/quant-ph/0406196); and Daniel Gottesman, [Stabilizer Codes and Quantum Error Correction](https://arxiv.org/abs/quant-ph/9705052). The proofs here are explicit reconstructions/adaptations, not 100 asserted new discoveries. No robustness, hardware speed or global optimality theorem from those papers is imported.

Actual frontier sources are [PR #2850](https://github.com/CrocSwap/integer-mult-bounds/pull/2850) by Gareth Davidson/bitplane and [PR #2859](https://github.com/CrocSwap/integer-mult-bounds/pull/2859) by Dennis/antunishdPursuit, at the immutable heads in the introduction. The source ledger and index record exact inspected bytes. Our prior atlas’s generic operator/Pauli facts are background only, not a novelty basis. Bounded source/DAG retrieval found the CNOT phase bridge and restricted commuting-phase module; neither was kernel-checked in this informal campaign, and neither is used to assume a missing physical contract. The canonical Lean tree, authoritative DAG and persistent services are unchanged.
