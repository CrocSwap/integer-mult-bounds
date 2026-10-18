# Volume I — Tensor, orbit, and constructive algebra

An informal atlas of 100 distinct numbered entries. Unless an entry says **Conjecture**, its proof is supplied below; this means a mathematical argument, not a new Lean/kernel certification. Standard results are credited as standard, and no global novelty claim is made. Research conjectures are precise proposals not established here; the limited source search does not establish that they are globally open.

Throughout, a field is commutative; vector spaces and algebras are finite-dimensional when dimensions or determinants are used. Group actions are left actions. A transporter sends the first object to the second. Tensor actions are covariant on all factors. Entries cite earlier numbered arguments and inspected source precedents L1–L8. Exact paths, SHA256 hashes, declarations, source-only limitations, and historical read-only DAG rows are in [01-sources.json](../sources/01-sources.json). No `Prop := True` scope marker, `sorry`, goal declaration, or conditional algorithm is used as a proved premise.

Primary context: [Stacks, trace and norm](https://stacks.math.columbia.edu/tag/0BIE) for norm definitions; [Milne, Fields and Galois Theory](https://www.jmilne.org/math/CourseNotes/FT.pdf) for classical field-theory context; [Chen–Grochow–Qiao–Tang–Zhang](https://arxiv.org/abs/2306.03135) for the distinct subject of complexity reductions between tensor actions. The proofs here are independent informal derivations, not quotations of those sources. Algebraic orbit criteria alone are not polynomial-time reductions.

## I. Transporters, stabilizers, and exact orbit information

<a id="a001"></a>

### A001 — Lemma: a nonempty transporter is a bitorsor
**Claim.** If a group G acts on X and g₀x=y, then the transporter T(x,y) equals g₀Gₓ=Gᵧg₀; its right Gₓ and left Gᵧ actions are free and transitive, and Gᵧ=g₀Gₓg₀⁻¹.

**Proof.** For gx=y, g₀⁻¹gx=x, so g=g₀h with h∈Gₓ. Conversely every g₀h carries x to y. Likewise gg₀⁻¹ fixes y, giving the left description. Cancellation in G proves freeness, and the displayed decompositions prove transitivity. Conjugating an element fixing x by g₀ fixes y; applying the same argument to g₀⁻¹ gives equality of stabilizers. These formulas do not require finite groups or faithful actions.

**Use/dependencies.** Construct witnesses by correcting one known transporter; foundational group-action fact underlying L1.

<a id="a002"></a>

### A002 — Theorem: kernel-orbit refinement is an exact coset space
**Claim.** Let φ:G→D be a surjective group homomorphism, K=ker φ, and H=Gₓ. The K-orbits inside Gx are naturally in bijection with the left cosets D/φ(H), by K·(gx)↦φ(g)φ(H).

**Proof.** Replacing g by gh, h∈H, preserves the coset. Replacing gx by kgx, k∈K, also preserves it. Conversely, equal cosets give φ(g₂)=φ(g₁h) for some h∈H. Then k=g₂h⁻¹g₁⁻¹ lies in K and g₂x=kg₁x. Surjectivity of φ makes every coset appear. Thus this map is both well-defined and bijective, even when D is nonabelian; no quotient-group structure on D/φ(H) is asserted unless φ(H) is normal.

**Use/dependencies.** Exact information lost by replacing G with a character kernel; A001, source pattern L1.

<a id="a003"></a>

### A003 — Theorem: correcting a supplied transporter
**Claim.** Under A002, if gx=y, a K-transporter exists exactly when φ(g)∈φ(Gₓ). If h∈Gₓ has φ(h)=φ(g), then gh⁻¹ is such a transporter.

**Proof.** The displayed correction fixes the character because φ(gh⁻¹)=1 and sends x to y because h fixes x. Conversely, if k∈K sends x to y, then k⁻¹g fixes x and φ(k⁻¹g)=φ(g). This also proves that the criterion is independent of the initially supplied g. It is a sufficient construction once the stabilizer element h is supplied, but does not supply an algorithm for finding h.

**Use/dependencies.** Character normalization without assuming roots or an unknown gadget; A001–A002, L1.

<a id="a004"></a>

### A004 — Theorem: exact stabilizer sequence and fibre size
**Claim.** Restriction of φ gives an exact sequence 1→K∩Gₓ→Gₓ→φ(Gₓ)→1. Each nonempty character fibre in Gₓ is a coset of K∩Gₓ. For finite Gₓ, |Gₓ|=|K∩Gₓ||φ(Gₓ)|.

**Proof.** The restricted map has kernel precisely K∩Gₓ and is onto its stated image by definition. If φ(h)=d and φ(h₀)=d, then h₀⁻¹h lies in that kernel; the converse follows by multiplication. Translation therefore bijects every nonempty fibre with the kernel. These fibres partition Gₓ, so their common size gives the cardinal identity. The exact sequence specifies the maps and their actual images, rather than assuming a split extension.

**Use/dependencies.** Counts correction choices and separates existence from multiplicity; A001–A003.

<a id="a005"></a>

### A005 — Theorem: orbit-count multiplication under refinement
**Claim.** Assume G and D are finite in A002. Then Gx contains exactly [D:φ(Gₓ)] K-orbits, and each has size |K|/|K∩Gₓ|.

**Proof.** The number follows from the bijection A002. For a point gx its K-stabilizer is K∩gGₓg⁻¹. Normality of K identifies this with g(K∩Gₓ)g⁻¹, so it has size |K∩Gₓ|. The map K→K(gx) has precisely that many elements in each fibre, yielding the orbit size. Multiplying gives |D|/|φ(Gₓ)| times |K|/|K∩Gₓ|=|G|/|Gₓ|, agreeing with the original orbit size by A004.

**Use/dependencies.** An exact finite audit of character-induced orbit splitting, not an approximation; A002–A004.

<a id="a006"></a>

### A006 — Theorem: sufficient fibrewise orbit recovery
**Claim.** Let f:X→Y be G-equivariant. If each nonempty fibre f⁻¹(y) is transitive under Gᵧ, then two points of X are G-equivalent exactly when their images are G-equivalent.

**Proof.** Equivariance proves the forward implication. For the reverse, suppose gf(x)=f(x′). Then gx and x′ lie in the same fibre overf(x′). By the hypothesis some h∈G_{f(x′)} sends gx to x′, so hg is a transporter. Conversely, if f is injective on G-orbits, then any two points of one fibre are related by some g; equivariance forces g to stabilize its common image. Thus the stated fibre condition is also necessary for orbit injectivity.

**Use/dependencies.** A precise recovery test for an equivariant encoding; the hypothesis is a concrete transitivity condition, not an assumed compiler.

<a id="a007"></a>

### A007 — Theorem: pairs of orbit points are classified by double cosets
**Claim.** For stabilizers H=Gₓ and J=Gᵧ, diagonal G-orbits on Gx×Gy correspond to double cosets H\G/J. The pair (x,gy) has stabilizer H∩gJg⁻¹.

**Proof.** Apply a⁻¹ to a general pair (ax,by), reducing it to (x,a⁻¹by). Two reduced pairs (x,gy),(x,g′y) are equivalent precisely when some h∈H satisfies hgy=g′y, or g′∈HgJ. This is exactly double-coset equivalence. An element fixes (x,gy) exactly when it fixesx and its conjugate by g⁻¹ fixesy, giving the intersection formula.

**Use/dependencies.** Correct gluing of two local orbit choices; A001. This prevents replacing simultaneous equivalence by two unrelated existential witnesses.

<a id="a008"></a>

### A008 — Theorem: character images survive unipotent splitting
**Claim.** Suppose G=U⋊L and a homomorphism χ:G→D is trivial on U. Then χ(G)=χ(L). More generally, for a subgroup S≤G whose projection to L is S₀ and which contains U, χ(S)=χ(S₀).

**Proof.** Every element has unique form uℓ, and χ(uℓ)=χ(ℓ). If S contains U, an element uℓ belongs to S exactly when ℓ=u⁻¹(uℓ) belongs to S. Thus S=U⋊S₀ and the same computation gives its image. For flag-preserving matrix groups, strict block-unipotent matrices have determinant one because their diagonal blocks are identities, so determinant characters satisfy the premise.

**Use/dependencies.** Reduces a concrete character computation to its graded diagonal part; it does not assert that arbitrary stabilizers admit such a splitting.

<a id="a009"></a>

### A009 — Theorem: abelian stabilizer characters are orbit invariants
**Claim.** Let D be abelian and φ:G→D a homomorphism. If x,y lie in one G-orbit, then φ(Gₓ)=φ(Gᵧ). In particular the determinant image of a tensor stabilizer is unchanged by an invertible tensor transporter.

**Proof.** Write y=gx. By A001, Gᵧ=gGₓg⁻¹. For h∈Gₓ, φ(ghg⁻¹)=φ(g)φ(h)φ(g)⁻¹=φ(h), using commutativity of D. This proves both inclusions. For a tensor take G to be the product of the three general linear groups and φ the ordered determinant triple. The product action is a genuine group action, and determinant is multiplicative, so the abstract proof applies without choosing another transporter.

**Use/dependencies.** Justifies attaching character data to an orbit rather than to a chosen basis; A001, L1.

<a id="a010"></a>

### A010 — Conjecture: a uniform fixed-field determinant-automorphism compiler
**Proposal.** For each fixed finite field F_q there are polynomial-size, uniformly constructed pairs of ordinary three-tensors C(A,d),D(A,d) such that C(A,d)≅D(A,d) exactly when A admits an automorphism with determinant triple d∈(F_q*)³. The polynomial bound is in the number of entries of A; no transporter is supplied.

**Evidence/approach.** A003 reduces supplied-transporter normalization to this exact membership question, and A029 gives a short abstract character description. Neither supplies the coefficient table from A. A possible attack encodes stabilizer equations together with inverse variables and then proves intrinsic recovery through unmarked tensor constructions. The falsifier for a proposed compiler is an unintended tensor isomorphism or a failed size bound. The classical-group reductions in primary source P3 give context, not a proof of this proposal. **Not proved here; no claim of global openness or novelty.**

## II. Tensor supports, faithful restriction, and algebra recovery

<a id="a011"></a>

### A011 — Theorem: intrinsic mode supports are the minimal tensor carriers
**Claim.** For t∈U⊗V⊗W, let S_U be the span of all contractions (id⊗β⊗γ)t. Define S_V,S_W similarly. Then t∈S_U⊗S_V⊗S_W, and every carrier U′⊗V′⊗W′ containingt has S_U⊆U′, S_V⊆V′, S_W⊆W′.

**Proof.** In bases of V,W the coefficients of t in U are exactly contractions by dual basis vectors, so belong to S_U. Thus t lies in S_U⊗V⊗W. Choose complements to all three supports and bases adapted to them. Any coefficient with an index outside a support is zero by the corresponding contraction definition; only the three-support block remains. If t lies in U′⊗V′⊗W′, every first-mode contraction lies in U′, proving minimality and its cyclic analogues.

**Use/dependencies.** Basis-independent concise cores, including zero tensors; elementary tensor coordinates, source theme L1.

<a id="a012"></a>

### A012 — Theorem: transporters restrict to concise cores
**Claim.** If (P,Q,R)t=t′ with all three maps invertible, then P(S_U(t))=S_U(t′), and similarly in the other modes. Conversely an isomorphism of the three supported tensors extends to an ambient transporter whenever the corresponding ambient dimensions agree.

**Proof.** Contracting t′ against β,γ gives P applied to the contraction of t against Q*β,R*γ. Invertibility makes the dual maps surjective, so the resulting contraction spans are equal. For the converse choose complementary subspaces to the supports on both sides. Their dimensions agree because both the ambient and support dimensions agree. Extend each given support isomorphism by any complement isomorphism. Since every tensor coefficient is inside its support by A011, the extended maps still carryt to t′.

**Use/dependencies.** Honest recovery after adding unused coordinates; A011. Upper-left corners of an arbitrary transporter are not used.

<a id="a013"></a>

### A013 — Theorem: zero padding turns GL-equivalence into SL-equivalence
**Claim.** Add one zero coordinate in each mode of two tensors of the same dimensions. The padded tensors are equivalent under special-linear maps exactly when the original tensors are equivalent under general-linear maps, over every field.

**Proof.** Given invertible P in one mode, extend it to diag(P,det(P)⁻¹); its determinant is one. Do this in each mode. The added coordinates do not occur in either tensor, so the extended triple transports the padded tensors. Conversely any special-linear transporter is in particular invertible. By A012 it restricts to isomorphisms of the intrinsic supports of the originals; extending those support maps to the original ambient spaces gives a general-linear transporter. This covers deficient supports and the zero tensor.

**Use/dependencies.** A complete orbitwise padding statement, not a runtime theorem; A011–A012, earlier project finding reflected in L1.

<a id="a014"></a>

### A014 — Theorem: rank-one stabilizers and free determinant coordinates
**Claim.** A nonzero decomposable tensor u⊗v⊗w has stabilizer consisting of triples preserving the three factor lines, with line multipliers a,b,c satisfyingabc=1. If each ambient dimension is at least two, its determinant image is all(K*)³.

**Proof.** Its three supports are exactly Ku,Kv,Kw, so preservation of the tensor forces preservation of these lines by A012. On the support the tensor is multiplied by abc, proving necessity and sufficiency. To prescribe determinantsd₁,d₂,d₃, use identity on each support line, scale one complementary basis vector by d_i, and fix the remaining complementary vectors. The tensor is unchanged while the three determinants are the prescribed values. No root extraction is involved.

**Use/dependencies.** Explicit stabilizer witnesses and small tests of character claims; A011–A012. The dimension-at-least-two condition is essential.

<a id="a015"></a>

### A015 — Theorem: flattening ranks give independent tensor invariants
**Claim.** The first flattening of t is the linear map U*→V⊗W induced by contraction. Its rank equals dim S_U(t), and invertible changes in all modes preserve this rank.

**Proof.** In bases, the flattening matrix has columns indexed by U and rows by pairs of V,W. The first-mode contraction coefficients form the transpose matrix, whose column span is S_U. Row reduction gives equal row and column ranks over any field, so the ranks agree. Under an invertible tensor action the flattening is multiplied on the left by Q⊗R and on the right by P*, both invertible. Multiplication by invertible matrices preserves rank because it induces isomorphisms on image spaces.

**Use/dependencies.** Computable support dimensions and immediate nonisomorphism certificates; A011. The three ranks need not determine an orbit.

<a id="a016"></a>

### A016 — Theorem: tensor products multiply mode ranks
**Claim.** For tensors t and s over K, the first-mode flattening rank of t⊗s, with corresponding modes grouped together, is the product of their first-mode ranks. The same holds in the other modes.

**Proof.** In grouped bases the flattening is a row/column permutation of the Kronecker product of the two flattening matrices. Reduce the matrices by invertible row and column operations to diag(I_r,0) anddiag(I_s,0). Tensoring these operations is invertible, and the resulting Kronecker matrix has exactlyrs independent unit positions. Hence its rank isrs. Basis permutations do not alter rank.

**Use/dependencies.** Exact invariants for tensor powers and stabilization attempts; A015 and Gaussian elimination. It gives actual multiplicativity rather than an asymptotic estimate.

<a id="a017"></a>

### A017 — Theorem: tensor rank is unchanged by injective ambient padding
**Claim.** Injective linear maps in the three factors preserve the tensor rank of a tensor. Thus zero extension does not create a shorter decomposition into pure tensors.

**Proof.** Applying the injections to a decomposition cannot increase its length. Conversely, over a field each injection has a linear left inverse: extend a basis of its image and project back. Apply the three left inverses to any pure-tensor decomposition of the padded tensor. Each term remains pure or becomes zero, and the sum is the original tensor. Therefore its rank is no greater than the padded rank. Both inequalities give equality, including rank zero.

**Use/dependencies.** A different invariant from flattening rank; excludes artificial rank savings obtained solely by enlarging ambient spaces.

<a id="a018"></a>

### A018 — Theorem: recovering a bilinear map from its radical algebra
**Claim.** Let β:V×V→W be symmetric, have image spanning W, and satisfy {v:β(v,V)=0}=0. Define A=K⊕V⊕W with identity1, product vv′=β(v,v′), and W(V⊕W)=0. Algebra isomorphisms between two such algebras induce equivalences of their β maps.

**Proof.** J=V⊕W is nilpotent with J³=0, and A/J=K. Every element with nonzero scalar part is invertible by a finite geometric series, so J is precisely the nonunits and is intrinsic. The spanning assumption gives J²=W. Thus an algebra isomorphism induces linear isomorphisms J/J²≅V and J²≅W. Multiplication of representatives in J is independent of the chosen lifts because J²J=0; its induced product is exactly β. Hence the induced maps carry β to β′. Conversely equivalences of β extend by identity on K to algebra isomorphisms by direct multiplication.

**Use/dependencies.** Intrinsic recovery, without falsely declaring a chosen complement V characteristic.

<a id="a019"></a>

### A019 — Theorem: isotopy of unital associative algebras normalizes to isomorphism
**Claim.** For unital associative K-algebras A,B, suppose invertible linear F,G,H:A→B satisfy H(xy)=F(x)G(y). Then A and B are isomorphic as unital K-algebras.

**Proof.** Put a=F(1), b=G(1). Then H(x)=F(x)b=aG(x), so right multiplication by b and left multiplication by a are bijective. A bijective multiplication map makes its element a unit: a one-sided inverse exists by surjectivity, and injectivity supplies the other side. Consequently H(xy)=H(x)b⁻¹a⁻¹H(y)=H(x)(ab)⁻¹H(y). Set f(x)=(ab)⁻¹H(x). This map is linear and bijective, f(1)=1, and f(xy)=f(x)f(y) by the displayed identity. It is the required algebra isomorphism.

**Use/dependencies.** Converts three independent tensor-factor maps on multiplication into a genuine algebra isomorphism; associativity and units are explicitly used.

<a id="a020"></a>

### A020 — Theorem: centroid idempotents split a bilinear tensor intrinsically
**Claim.** Let β:U×V→W be bilinear. Suppose idempotents e_U,e_V,e_W satisfy β(e_Uu,v)=e_Wβ(u,v)=β(u,e_Vv). Then β is the direct sum of its restrictions to the image triples and the kernel triples; all cross terms vanish.

**Proof.** An idempotent splits each space as image⊕kernel: x=ex+(x−ex), and an element in both summands is zero. If u is in imagee_U and v in ker e_V, then β(u,v)=e_Wβ(u,v)=β(u,e_Vv)=0. The other cross term vanishes symmetrically. If both inputs are in the images, their output is inimagee_W; if both are in the kernels, e_Wβ=β(e_Uu,v)=0, so the output lies in ker e_W. Expansion by bilinearity now gives precisely the two summands.

**Use/dependencies.** An explicit sufficient direct-sum certificate for tensor decomposition; no uniqueness assertion is hidden in the splitting.

## III. Integer lattices, torus characters, and exact power equations

Here m denotes a positive integer whenever C_m or Z/mZ occurs.

<a id="a021"></a>

### A021 — Theorem: subgroups of a finite-rank free abelian group are free
**Claim.** Every subgroup L≤Z^r has a basis of at most r integer vectors.

**Proof.** Induct on r. Project L onto the first coordinate. Its image is dZ for a unique d≥0, since a nonzero subgroup of Z is generated by its least positive element. Ifd=0, apply induction inside0×Z^{r−1}. Otherwise choose v∈L with first coordinate d. The kernel L₀ of the projection is free of rank at most r−1 by induction. Forx∈L, its first coordinate iskd, so x−kv∈L₀. This decomposition is unique because a multiple of v in L₀ has zero first coordinate. Thusv together with a basis of L₀ is a free basis.

**Use/dependencies.** Finite presentations of character lattices without assuming finite generation in advance.

<a id="a022"></a>

### A022 — Theorem: Smith normal form by decreasing Euclidean pivots
**Claim.** An integer matrix M can be transformed by unimodular row and column operations into diag(d₁,…,d_s,0), with each d_i>0 and d_i dividingd_{i+1}.

**Proof.** IfM is nonzero, move a nonzero entry to the upper left and make it positive. Euclidean row/column division either clears the rest of its row and column or replaces that pivot by a smaller positive remainder. This strictly decreasing process terminates. If the resulting pivotd fails to divide a remaining entry, add its row to the first row; Euclidean column division again produces a positive pivot smaller than d. Thus eventuallyd divides every remaining entry and its row/column can be cleared. Recurse on the smaller submatrix. Every operation used is an integer swap, sign change, or addition of a multiple, hence unimodular. All remaining entries are divisible by d, and this property survives recursion, producing the divisibility chain.

**Use/dependencies.** An effective exact normal form; A021 gives compatible lattice interpretation.

<a id="a023"></a>

### A023 — Theorem: monomial equations reduce to independent power fibres
**Claim.** For an abelian group H and integer matrix M, define f_M:H^s→H^r by (f_M(x))_i=∏_j x_j^{M_ij}. Smith operations turn f_M(x)=a into independent equations y_i^{d_i}=b_i and equations b_i=1 for zero rows.

**Proof.** Integer exponent rules give f_A∘f_B=f_{AB}. A unimodular matrix U has an integer inverse, so f_U is an automorphism for every abelian H, including groups with torsion. If UMV is the Smith diagonal form, set x=f_V(y) and b=f_U(a). Applying the automorphism f_U to the original equation gives exactly the diagonal equations. All changes are invertible, so this is an equivalence of full solution sets, not just of solvability.

**Use/dependencies.** Constructive simultaneous root conditions over arbitrary fields and unit groups; A022, source arithmetic L3.

<a id="a024"></a>

### A024 — Theorem: two simultaneous powers have one residual root
**Claim.** Let H be abelian, d,M,N integers, and Mr+Ns=1. Then t^{dM}=a and t^{dN}=b are simultaneously solvable exactly when a^N=b^M and a^r b^s has a d-th root in H.

**Proof.** A solutiont gives the compatibility by commuting exponents and gives a^rb^s=t^{d(Mr+Ns)}=t^d. Conversely, suppose u^d=a^rb^s and a^N=b^M. Then (a^rb^s)^M=a^{rM}b^{sM}=a^{rM+Ns}=a; likewise its N-th power isb. Therefore u^{dM}=a and u^{dN}=b. Negative exponents cause no problem in a group. This also specifies the witness rather than merely eliminating it.

**Use/dependencies.** Exact gcd reduction of power certificates; L3 supplies the same algebraic pattern, independently proved here.

<a id="a025"></a>

### A025 — Theorem: finite cyclic monomial fibres have exact sizes
**Claim.** IfH is cyclic of orderm, then x↦x^d has kernel sizeg=gcd(m,d), image size m/g, and a belongs to its image exactly when a^{m/g}=1. A nonempty Smith-system fibre therefore has size m^{s−rank M}∏_i gcd(m,d_i).

**Proof.** Write H=〈z〉. The equation (z^u)^d=1 says m dividesdu, giving exactlyg residue classesu mod m. Its image consists of exponents divisible by g, equivalently those elements killed by m/g. Every nonempty fibre is a translate of the kernel. For a Smith system the coordinates are independent; each nonzero diagonal coordinate contributes its kernel size, and each unconstrained input contributesm. Multiply these counts, assuming the zero-row equations are satisfied.

**Use/dependencies.** Complete finite-field unit counts when a generator is known; A023.

<a id="a026"></a>

### A026 — Theorem: a subgroup of(C_m)^r is cut out by r characters
**Claim.** Every subgroup S≤D=(Z/mZ)^r is the simultaneous kernel of at most r homomorphisms D→Z/mZ.

**Proof.** Let L be its inverse image in Z^r; then mZ^r⊆L. By A021 choose a lattice basis and put its inclusion matrix in Smith form. After a unimodular ambient change, L=⊕_i d_i Z with each d_i dividingm; this follows from mZ^r⊆L. In these coordinates, membership in S says d_i dividesx_i. The character χ_i(x)=(m/d_i)x_i mod m vanishes exactly on that condition. There are r coordinates, including trivial characters when d_i=1. Transform these characters back by the ambient unimodular change.

**Use/dependencies.** An elementary constructive finite-duality statement; L4 proves a related three-coordinate field version.

<a id="a027"></a>

### A027 — Theorem: finite character sums are exact subgroup projectors
**Claim.** Let K contain a primitive m-th root ζ and assume char K does not dividem. For S≤D=(Z/mZ)^r, average all characters trivial on S. The resulting function is1 on S and 0 outside S.

**Proof.** By A026, if x∉S, some character χ₀ trivial on S satisfies χ₀(x)≠1. Let A be the group of all characters trivial on S and Z=∑_{χ∈A}χ(x). Multiplication by χ₀ permutes A, so Z=χ₀(x)Z, forcing Z=0. Ifx∈S, every summand is1, giving Z=|A|. The group A is a subgroup of(C_m)^r, so its order has only prime factors dividingm and is nonzero in K. Division by|A| completes the projector.

**Use/dependencies.** Explicit invariant projection and finite harmonic membership certificates; A026, with roots-of-unity and characteristic conditions stated.

<a id="a028"></a>

### A028 — Theorem: scalar kernels constrain semi-invariant degrees
**Claim.** Over an infinite field, let a nonzero homogeneous polynomialf of degree d on U₁⊗⋯⊗U_s satisfy f((g_i)t)=∏det(g_i)^{a_i}f(t), with integersa_i≥0. Then d=(dim U_i)a_i for every i.

**Proof.** Set all group elements to identity except g_i=zI. The tensor is multiplied by z, so homogeneity gives z^d f(t)=z^{n_i a_i}f(t). Choose t over an extension if needed with f(t)≠0; equivalently compare nonzero polynomial coefficients in t. Thus z^d=z^{n_i a_i} for all nonzeroz∈K. Distinct powers cannot agree on an infinite field because a nonzero univariate polynomial has finitely many roots. The exponents therefore agree. Over F_q the argument gives only congruence moduloq−1, not integer equality.

**Use/dependencies.** Reliable weight/degree tests for invariant constructions; the infinite-field qualification is indispensable.

<a id="a029"></a>

### A029 — Theorem: finite-field determinant images admit three bounded equations
**Claim.** For a tensor over F_q, its stabilizer determinant image Δ≤(F_q*)³ is described by three monomial equations with a3×3 exponent matrix whose entries lie in[0,q−2].

**Proof.** A finite subgroup of a field's multiplicative group is cyclic: take elements of maximal prime-power orders, multiply their commuting components to obtain an element of exponent equal to the group's exponent; every group element is a root of X^e−1, so the group size is at most e, forcing equality and cyclicity. Apply A026 with m=q−1 and identify characters to C_m with integer monomials using a chosen generator of F_q*. Every exponent may be reduced mod m. The determinant image is a subgroup because determinant is multiplicative on stabilizers, so the result applies. Ifq=2 the target is trivial and the three zero equations suffice.

**Use/dependencies.** Short exact descriptions exist; recovery from the tensor alone is not supplied. Precedent L4.

<a id="a030"></a>

### A030 — Conjecture: intrinsic extraction of a bounded determinant equation table
**Proposal.** Fix q. There is a deterministic algorithm using polynomially many field operations in the tensor size that, from an arbitrary tensor A over F_q, outputs three bounded monomial equations defining its stabilizer determinant image, without enumerating its automorphism group.

**Evidence/approach.** A029 guarantees a table of nine bounded integers, and A004 shows that this compressed image can be far smaller than the stabilizer. For representations with an explicitly computable endomorphism algebra, units and graded diagonal factors offer an extraction route (A041–A049). The general tensor stabilizer is not such an algebra automatically. An approach must prove actual image equality and complexity; a short answer alone is not a short computation. This proposal is unproved here, and the inspected sources do not establish its global novelty or openness.

## IV. Polynomial invariants and usable covariants

<a id="a031"></a>

### A031 — Lemma: Contractions transport their kernels and images

**Statement.** Let finite-dimensional spaces over a field K carry a tensor t in U⊗V⊗W, and let g=(a,b,c) be invertible. The contraction C_t:U*→V⊗W satisfies C_{gt}=(b⊗c)C_t a*, where a*(λ)=λ∘a. Consequently its image, kernel, and every exterior-power rank certificate are transported by these explicit maps.

**Proof.** Write t=Σu_i⊗v_i⊗w_i. Contracting gt gives Σλ(a u_i)b v_i⊗c w_i, which is precisely the displayed composition. Both outside maps are invertible. Thus the image is (b⊗c)im C_t and the kernel is (a*)⁻¹ker C_t. Applying the functor ∧^j gives the same composition on exterior powers. A map has rank at least j exactly when its jth exterior power is nonzero: an independent j-tuple has a nonzero wedge, whereas every wedge of j image vectors vanishes when the image dimension is smaller. This proves all assertions.

**Use and dependencies.** Supplies explicit covariant subspaces and determinantal certificates, rather than just invariant dimensions. Uses elementary tensor contraction; compare A011 and A015.

<a id="a032"></a>

### A032 — Lemma: Semi-invariants constrain, and sometimes identify, transporter characters

**Statement.** Let G act on X and let f:X→K satisfy f(gx)=χ(g)f(x), with χ:G→K× a character. If f(x)≠0, then χ(G_x)=1 and every transporter g:x→y satisfies χ(g)=f(y)/f(x). For several such functions with combined character φ, if y∈Gx and G_x=ker φ, their nonzero ratios determine the transporter coset exactly.

**Proof.** For h∈G_x the identity f(x)=χ(h)f(x) permits cancellation, giving χ(h)=1. Substituting gx=y proves the ratio formula. For the final assertion, two transporters g,g' have equal combined character exactly when g⁻¹g'∈ker φ=G_x. This is exactly equality of their cosets gG_x. Given one transporter g_0:x→y, any candidate u with φ(u)=φ(g_0) satisfies g_0⁻¹u∈ker φ=G_x, so ux=y. Existence of a transporter is a separate hypothesis: the ratio calculation does not produce one between arbitrary points.

**Use and dependencies.** Converts computable covariant values into complete character information when the stated stabilizer equality has independently been established. Depends on A001; related to source L1.

<a id="a033"></a>

### A033 — Theorem: Weight-zero monomials describe torus invariants

**Statement.** Let the algebraic torus (K×)^r act diagonally on K[x_1,…,x_n], with integer weights w_j∈Z^r, and assume K is infinite. Its invariant polynomials are precisely the K-linear combinations of monomials x^α with Σα_jw_j=0.

**Proof.** A monomial is multiplied by the Laurent character t↦t^{Σα_jw_j}, so every indicated polynomial is invariant. Conversely collect a polynomial into its distinct weight components f=Σ_v f_v. Invariance says Σ_v(t^v−1)f_v=0. Comparing the coefficient of any monomial with nonzero coefficient in f_v shows t^v=1 for every t∈(K×)^r. If v≠0, hold all but one nonzero coordinate equal to 1; the remaining coordinate would satisfy z^a=1 for every z∈K× with a≠0. After clearing negative powers this contradicts the root bound for a nonzero polynomial over an infinite field. Thus v=0. Over finite fields the group-of-points version instead permits weights divisible by |K×|; no infinite-field conclusion is asserted there.

**Use and dependencies.** Turns a torus invariant calculation into a nonnegative integer kernel calculation. Uses A023 for subsequent lattice computations.

<a id="a034"></a>

### A034 — Lemma: Diagonal covariants are explicit weight-matching polynomials

**Statement.** In the setting of A033, suppose a finite-dimensional target E has a basis e_i with weights v_i. A polynomial map F:K^n→E is equivariant exactly when every monomial occurring in its ith coordinate has weight v_i, using the coordinate-action convention of A033 consistently.

**Proof.** Expand F=Σ_i f_i e_i. Equivariance means f_i(t x)=t^{v_i}f_i(x) separately for every i. Expanding f_i into monomials and comparing their coefficients gives t^{weight(α)}=t^{v_i} for each nonzero coefficient. The character-independence argument of A033 makes the weights equal. The converse follows by applying the indicated character to each monomial and summing. Changing from point-coordinate to pullback-coordinate conventions reverses every weight simultaneously and does not change the criterion.

**Use and dependencies.** Provides actual covariant formula spaces, including semi-invariants as one-dimensional targets; does not assume an invariant-ring oracle.

<a id="a035"></a>

### A035 — Theorem: Averaging makes finite-group invariants exact

**Statement.** Let a finite group G act K-linearly, with |G| invertible in K. The averaging operator R(v)=|G|⁻¹Σ_g gv is a projection onto V^G. For every surjective equivariant map V→W, the induced map V^G→W^G is surjective.

**Proof.** For h∈G, reindexing the sum by g↦hg gives hR(v)=R(v). If v is fixed, every summand equals v and R(v)=v; these facts prove the projection assertion. Given a fixed w∈W, choose any lift v. Equivariance yields image R(v)=R(w)=w, giving a fixed lift. Injections and kernels commute with taking fixed vectors directly from the defining equalities gv=v, so this also proves exactness of the invariants functor on short exact sequences.

**Use and dependencies.** A constructive sufficient lifting theorem; the characteristic hypothesis is essential to this proof. Finite-group averaging is classical and is not claimed new.

<a id="a036"></a>

### A036 — Theorem: Finite-group polynomial invariants are finitely generated

**Statement.** For any finite group G acting linearly on A=K[x_1,…,x_n], the algebra A^G is finitely generated over K, in every characteristic.

**Proof.** For each coordinate x_i form ∏_{g∈G}(T−g x_i). Its coefficients are invariant because G permutes its factors. Let B be the K-algebra generated by all these finitely many coefficients. Each x_i satisfies a monic polynomial of degree |G| over B. Repeated reduction of a power ≥|G| expresses A as a B-module generated by the finitely many monomials with each exponent below |G|. The Hilbert basis theorem makes the finitely generated K-algebra B Noetherian. The invariant algebra A^G is a B-submodule of this finite B-module, hence is generated by finitely many elements as a B-module. Those generators, together with the chosen generators of B, generate A^G as a K-algebra. This argument does not divide by |G|.

**Use and dependencies.** Gives a concrete finite base algebra and a module-finiteness proof; it supplies existence, not a small degree or efficient algorithm bound. Uses the standard Hilbert basis theorem; P5, [Stacks finite and integral extensions](https://stacks.math.columbia.edu/tag/00GH), supplies the finite/integral background.

<a id="a037"></a>

### A037 — Theorem: Finite orbits are separated by invariant polynomials

**Statement.** For a finite linear group G over any field K, two distinct G-orbits of K-rational vectors are separated by an invariant polynomial.

**Proof.** For any finite set S of distinct K-points and any p∈S, construct δ_p as follows. For each q≠p choose a coordinate j with p_j≠q_j and include the factor (x_j−q_j)/(p_j−q_j). Their product is1 at p and 0 at every other point of S. Summing δ_p over the points of the second orbit produces h which is0 on the first orbit and 1 on the second. The polynomial F(v)=∏_{g∈G}h(gv) is invariant by permutation of factors. It is0 on the first orbit and 1 on the second. No averaging or assumption on the characteristic was used.

**Use and dependencies.** A complete finite-orbit separation theorem, including modular characteristic; useful as an existence certificate even when its degree is large.

<a id="a038"></a>

### A038 — Theorem: Every stabilizer-fixed vector is a covariant value

**Statement.** Let G be finite with |G| invertible in K, acting linearly on V and E. For x∈V, evaluation of polynomial equivariant maps V→E onto E^{G_x} is surjective.

**Proof.** Necessity follows from F(hx)=hF(x). For sufficiency let w be fixed by H=G_x. Use the finite-point interpolation of A037 to choose p with p(x)=1 and p=0 at all other points of Gx. Define F(v)=|H|⁻¹Σ_{g∈G}p(g⁻¹v)g w. Reindexing g=ak proves F(av)=aF(v). At x only g∈H contribute, and each such term is w, so F(x)=w. The integer |H| is invertible because it divides |G|. This is an explicit covariant, not a separation argument with an unspecified map.

**Use and dependencies.** Recovers every available fixed-vector feature from polynomial covariants. Depends on A037 and the nonmodular hypothesis.

<a id="a039"></a>

### A039 — Theorem: Polynomial covariants form a finite module

**Statement.** For a finite group G and a finite-dimensional representation E, the covariant module (A⊗E)^G is finite over A^G, without a characteristic restriction.

**Proof.** Use the finitely generated Noetherian subalgebra B⊂A^G constructed in A036. The module A⊗E is finite over B because A is finite over B and E has a finite basis. Its invariant subspace is a B-submodule and is therefore finite over B. A set generating it over B also generates it over the larger coefficient algebra A^G: its A^G-span is contained in the invariant module and already contains its B-span, which is the whole module. Hence it is finite over A^G.

**Use and dependencies.** Complements invariant finite generation with a sufficient finite list of covariants. Depends on A036; no claim of a uniform small generating degree.

<a id="a040"></a>

### A040 — Theorem: Nonmodular invariants commute with quotient by a stable ideal

**Statement.** If |G| is invertible and I is a G-stable ideal of a G-algebra A, then the natural homomorphism A^G/(I∩A^G)→(A/I)^G is an isomorphism.

**Proof.** Its kernel is exactly the invariant elements lying in I, so it is injective after the displayed quotient. For an invariant residue class choose a lift a∈A. Averaging its G-translates gives R(a)∈A^G. Since the residue class was fixed, every translate of a has the same class, and R(a) has that class too. This proves surjectivity. Multiplication is respected by the original quotient map; no assertion that R itself is an algebra homomorphism is needed.

**Use and dependencies.** Gives actual invariant lifts on a stable closed subspace. This is a ring-theoretic application of A035, stated separately because it identifies the quotient algebra and its exact kernel.

## V. Intertwiner algebras and constructive decomposition

Throughout this section the quiver has finitely many vertices and arrows, and all its vertex spaces are finite-dimensional over the field K. Intertwiners are K-linear.

<a id="a041"></a>

### A041 — Lemma: Endomorphisms of a diagram form a computable algebra

**Statement.** A representation M of a finite quiver assigns finite-dimensional spaces M_v and arrow maps A_e. Its endomorphisms are tuples X_v satisfying X_{head(e)}A_e=A_eX_{tail(e)}. They form a unital finite-dimensional K-algebra, obtained as the kernel of an explicit linear system.

**Proof.** Each displayed equation is linear in the matrix entries of X. Their simultaneous solution is therefore a linear subspace of ⊕_v End(M_v). The identity tuple satisfies every equation. If X,Y satisfy them, then X_hY_hA_e=X_hA_eY_t=A_eX_tY_t, so the coordinatewise product satisfies them as well. Addition and scalar multiplication follow directly from linearity. Associativity is inherited from matrix multiplication. Listing the matrix-entry equations gives an ordinary homogeneous linear system whose nullspace is exactly this algebra.

**Use and dependencies.** Classical representation-theory precedent P4, [Etingof and coauthors, Chapters2 and 5](https://ocw.mit.edu/courses/18-712-introduction-to-representation-theory-fall-2010/pages/lecture-notes/). An executable algebraic replacement for an abstract stabilizer search in linear diagram problems. Actual source L5 has related intertwiner operations; its excluded placeholder propositions are not used.

<a id="a042"></a>

### A042 — Lemma: Diagram automorphisms are exactly the units of the endomorphism algebra

**Statement.** An endomorphism X of M is a unit precisely when every X_v is invertible; its inverse is the tuple X_v⁻¹.

**Proof.** A unit has a two-sided inverse tuple, so evaluating its inverse identities at a vertex proves that vertex matrix invertible. Conversely multiply X_hA_e=A_eX_t on the left by X_h⁻¹ and on the right by X_t⁻¹. This gives X_h⁻¹A_e=A_eX_t⁻¹, the intertwining equation for the inverse tuple. Its products with X are the identity coordinatewise. Thus it lies in the same algebra and is a unit there.

**Use and dependencies.** Reduces existence of a diagram isomorphism in an intertwiner space to a determinant nonvanishing test; see A048 and A095.

<a id="a043"></a>

### A043 — Theorem: Idempotents are precisely direct-sum projectors

**Statement.** An idempotent e in End(M) gives M=im e⊕ker e as quiver representations. Conversely every direct-sum decomposition gives such an idempotent; nontrivial decompositions correspond to e≠0,1.

**Proof.** At each vertex, any vector z equals e z+(z−e z), with the second term killed by e. If z is simultaneously an image vector and killed by e, then z=e y implies e z=e²y=e y=z, so z=0. Every arrow commutes with e, hence maps image to image and kernel to kernel. These vertexwise decompositions therefore form subrepresentations. Conversely projection onto one summand along the other commutes with every arrow because the arrows preserve both summands. It squares to itself and has exactly those image and kernel representations.

**Use and dependencies.** A complete constructive criterion for decomposition, not merely an obstruction. Depends on A041.

<a id="a044"></a>

### A044 — Theorem: Fitting decomposition for a diagram endomorphism

**Statement.** For X∈End(M), sufficiently large N gives M=ker X^N⊕im X^N. Both are subrepresentations and X is nilpotent on the first and invertible on the second. If M is indecomposable, every endomorphism is either invertible or nilpotent.

**Proof.** Choose N for which the kernels and images of all vertex powers have stabilized, also at power 2N; such N exists by finite dimensionality. If z=X^N y and X^N z=0, then X^{2N}y=0. Stabilization gives y∈ker X^N, so z=0. Rank-nullity then shows that image and kernel sum to the whole vertex space. They are arrow-stable because X commutes with the arrows. On the image, X is surjective by stabilization and hence bijective; on the kernel X^N=0. Indecomposability forces one summand zero, giving the final dichotomy by A042.

**Use and dependencies.** Establishes the local-algebra mechanism behind decomposition uniqueness; depends on A043.

<a id="a045"></a>

### A045 — Theorem: The endomorphism ring of an indecomposable finite diagram is local

**Statement.** For a nonzero indecomposable M, the nonunits of End(M) form a two-sided ideal; the quotient by it is a division ring.

**Proof.** By A044 every nonunit is nilpotent. Suppose nonunits a,b had invertible sum u. Then u⁻¹a and u⁻¹b are nonunits and sum to 1. The first is nilpotent, so 1−u⁻¹a=u⁻¹b is invertible by its finite geometric-series inverse, a contradiction. Thus nonunits are additively closed, and are closed under negatives. If ra were a unit, a would have a left inverse; in a finite-dimensional algebra a left inverse implies a two-sided inverse: multiplication by a is injective and thus surjective, producing a right inverse which equals the left inverse. The same argument treats ar. Therefore the nonunits form an ideal. Every element outside it is a unit, so every nonzero residue class is invertible. This proves the local-ring assertion.

**Use and dependencies.** Supplies the precise algebra used by Krull–Schmidt, including the finite-dimensional hypothesis needed in the one-sided-inverse argument.

<a id="a046"></a>

### A046 — Theorem: Krull–Schmidt uniqueness for finite-dimensional quiver representations

**Statement.** Every such representation is a finite direct sum of indecomposables, uniquely up to permutation and isomorphism of the summands.

**Proof.** Existence follows by splitting any decomposable nonzero summand; each split lowers positive total dimensions, so the process ends. For uniqueness write M=⊕_i U_i=⊕_j V_j with indecomposable summands. On U_1, identity is the sum of composites U_1→V_j→U_1. By A045 the nonunits form an ideal, so some composite is invertible. Its two factors make U_1 a direct summand of V_j: rescale the projection to make its composite identity, and split the resulting idempotent by A043. Indecomposability of V_j makes the complementary kernel zero, hence V_j≅U_1. More explicitly the projection of that V_j onto U_1 is invertible, so V_j is the graph of a map U_1→⊕_{i>1}U_i. The automorphism subtracting that graph map fixes the latter complement and carries V_j onto U_1. Quotienting by this common summand leaves two decompositions of a smaller representation. Induction proves uniqueness.

**Use and dependencies.** Justifies canonical multiplicity data and decomposition algorithms; depends on A043–A045.

<a id="a047"></a>

### A047 — Lemma: Intertwiner spaces commute with field extension

**Statement.** For finite diagrams M,N over K and an extension L/K, L⊗_K Hom(M,N) is naturally Hom(M_L,N_L).

**Proof.** Choose bases and write all intertwining equations as one matrix C over K. Row reduction uses only operations over K and gives a basis of its kernel and a set of pivot columns. The same row reduction over L has the identical pivots: every nonzero pivot in K remains nonzero. Hence the K-kernel basis becomes an L-kernel basis. Tensoring the coordinate solution space with L gives exactly the extended solution space. The identification respects evaluation and composition because the defining matrix formulas do.

**Use and dependencies.** A source-bound descent tool for linear constraints; no algebraic-closure assumption or semisimplicity is needed.

<a id="a048"></a>

### A048 — Theorem: Isomorphism of finite diagrams descends over infinite fields

**Statement.** Let K be infinite. If M_L≅N_L over an extension L/K, then M≅N over K.

**Proof.** Vertex dimensions agree. Choose a K-basis f_1,…,f_s of Hom(M,N). By A047 an L-isomorphism is Σa_i f_i. The product P(z)=∏_v det(Σz_i(f_i)_v) is a polynomial over K nonzero at a=(a_i), hence is not the zero polynomial. A nonzero polynomial over an infinite field has a nonzero evaluation: induct on the number of variables, choosing values that keep one nonzero coefficient nonzero and then avoiding finitely many roots in the last variable. Choose z∈K^s with P(z)≠0. The resulting intertwiner is vertexwise invertible, hence an isomorphism by A042. The zero-dimensional representation is harmless and has the identity isomorphism.

**Use and dependencies.** An actual sufficient descent theorem for linear diagrams, not for arbitrary tensor orbit equations. Depends on A042 and A047.

<a id="a049"></a>

### A049 — Theorem: A finite-field size bound also descends diagram isomorphisms

**Statement.** Over K=F_q, the conclusion of A048 holds whenever q>D=Σ_v dim M_v.

**Proof.** The determinant product P constructed there has total degree D. A nonzero polynomial whose degree in each variable is below q cannot vanish on all K^s. To prove this, write it as a polynomial in the last variable. If it vanished at every point, then after fixing the other coordinates the resulting polynomial of degree below q would have q roots and be zero. All its coefficient polynomials vanish on K^{s−1}; induction makes each zero, a contradiction. Since each variable degree is at most D<q, P has a nonzero K-evaluation. The same intertwiner argument completes the proof.

**Use and dependencies.** Makes the descent hypothesis quantitative and records why small finite fields require a different argument. Depends on A047–A048, not on any claimed general finite-field descent theorem.

<a id="a050"></a>

### A050 — Theorem: Semisimple diagrams have canonical central blocks

**Statement.** If M=⊕_{i=1}^r S_i^{m_i}, where the S_i are pairwise nonisomorphic simple finite-dimensional representations, then End(M)≅∏_i M_{m_i}(D_i), D_i=End(S_i) a division ring. Its primitive central idempotents project onto the isotypic summands.

**Proof.** A nonzero map between simple representations has zero kernel and full image, hence is an isomorphism. Thus Hom(S_i,S_j)=0 for i≠j, while every nonzero endomorphism of S_i is invertible. Writing maps of direct sums as block matrices yields the displayed product algebra. The centre of a matrix algebra over a division ring consists of scalar matrices with scalar in the centre of that division ring: commuting with matrix units first forces equal diagonal scalars and zero off-diagonal entries, and commuting with scalar entries forces centrality. Its only idempotents are 0 and 1 because a division ring has no other idempotents. Therefore the primitive central idempotents of the product are exactly its factor identities, giving the claimed intrinsic isotypic projections.

**Use and dependencies.** Turns semisimple multiplicity decomposition into canonical algebraic blocks, useful for centroid and intertwiner recovery. This strengthens the noncanonical splitting in A043 under an explicit semisimplicity hypothesis.

## VI. Flags, adapted coordinates, and paired geometry

<a id="a051"></a>

### A051 — Theorem: Two flags admit a common adapted basis

**Statement.** Given increasing flags U_0=0⊂⋯⊂U_a=V and W_0=0⊂⋯⊂W_b=V, there are subspaces E_{ij} with U_i∩W_j=⊕_{k≤i,l≤j}E_{kl}.

**Proof.** Put F_{ij}=U_i∩W_j. Induct in i+j and choose E_{ij} complementing F_{i−1,j}+F_{i,j−1} inside F_{ij}. The intersection of those two smaller spaces is F_{i−1,j−1}. By the inductive decompositions, their sum is the direct sum of the previously chosen E_{kl} in the two adjacent rectangles, with their common rectangle counted once. Adding the chosen complement gives the asserted direct sum for the larger rectangle. The boundary rectangles are zero, which starts the induction. Bases of all E_{ij} together form the required basis of V.

**Use and dependencies.** Gives constructive simultaneous coordinates for two flags; it makes no claim that three arbitrary flags have such a decomposition.

<a id="a052"></a>

### A052 — Theorem: Intersection dimensions classify pairs of flags

**Statement.** Two pairs of flags with identical index sets are related by an invertible linear map precisely when all corresponding dimensions dim(U_i∩W_j) agree. The numbers e_{ij}=dim F_{ij}−dim F_{i−1,j}−dim F_{i,j−1}+dim F_{i−1,j−1} are nonnegative and give a complete invariant.

**Proof.** An isomorphism preserves intersections and dimensions. Conversely A051 gives adapted summands whose dimensions are the displayed differences, by taking dimensions of its direct sums. Thus e_{ij}≥0. Equality of the intersection dimensions gives equal dimensions for each corresponding pair of E_{ij}. Choose arbitrary isomorphisms between these pairs and take their direct sum. The formulas in A051 show that the resulting isomorphism carries each flag space to its partner. This proves both sufficiency and completeness.

**Use and dependencies.** An actual orbit classification with a witness construction; depends on A051.

<a id="a053"></a>

### A053 — Theorem: The flag stabilizer is an extension by a split unipotent group

**Statement.** For a flag with successive dimensions d_i, its stabilizer P maps onto ∏_i GL_{d_i}(K) by its action on successive quotients. The kernel consists of identity-diagonal block triangular matrices, and det g is the product of the graded determinants.

**Proof.** Choose a basis adapted to the flag. The flag-preservation equations say that the matrix is block triangular. Its diagonal blocks are precisely the quotient actions. Arbitrary invertible diagonal blocks lift by a block diagonal matrix, proving surjectivity and a splitting. The kernel has diagonal identity and strictly triangular remainder N; N^a=0 where a is the number of blocks. Its inverse is the finite sum I−N+⋯+(−N)^{a−1}, so these matrices form the kernel group. The triangular determinant formula gives the product assertion. The strict-block filtration has additive successive quotients, which is the stated split unipotent structure.

**Use and dependencies.** Supplies an exact sequence with explicit lifts and determinant bookkeeping; related to the orbit refinement of A002.

<a id="a054"></a>

### A054 — Theorem: Prescribed graded isomorphisms lift, with no extra determinant obstruction

**Statement.** Given two flags with equal successive dimensions and chosen isomorphisms on their corresponding graded spaces, there is a flag isomorphism inducing exactly them. Its determinant relative to chosen adapted volume bases is the product of their determinants; every other lift differs by the kernel of A053.

**Proof.** Choose complements to consecutive flag terms in both spaces. Lift each prescribed quotient isomorphism through these complements and take their direct sum. The resulting block diagonal map is invertible, preserves the flags, and has the prescribed quotient actions. Any other lift composed with its inverse induces the identity on every quotient, hence belongs to the explicit kernel in A053. Such a kernel matrix has determinant1, so all lifts have the same determinant, equal to that of the constructed block diagonal lift. Thus determinant1 can be imposed exactly when the displayed product is1.

**Use and dependencies.** A complete sufficient lifting statement for flagged transporters, including their determinant normalization; depends on A053.

<a id="a055"></a>

### A055 — Theorem: Common flag stabilizers have a poset-triangular description

**Statement.** In the common decomposition of A051, a linear endomorphism preserves both flags exactly when its E_{ij}→E_{kl} blocks vanish unless k≤i and l≤j. The invertible such maps surject onto ∏_{ij}GL(E_{ij}); their kernel is identity plus a nilpotent block ideal, and their determinant is the product of diagonal determinants.

**Proof.** A vector in E_{ij} belongs to U_i∩W_j, so flag preservation forces its image into the direct sum indexed by k≤i,l≤j. Conversely that block condition preserves each flag by summing its indexed summands. The strict-block maps form a two-sided ideal in this block algebra: composition can only decrease indices, and any sufficiently long strictly decreasing chain is impossible. Thus the ideal is nilpotent. A linear extension of this finite partial order makes every such matrix triangular. Invertibility is equivalent to invertibility of all diagonal blocks, the diagonal map is surjective by block diagonal lifts, and its kernel and determinant follow as in A053.

**Use and dependencies.** Gives exact common-stabilizer character data for two flags, rather than treating their constraints independently. Depends on A051 and A053.

<a id="a056"></a>

### A056 — Theorem: All feasible nested subspace choices form an interval lattice

**Statement.** Let lower and upper subspaces L_t,U_t⊂V be specified for 1≤t≤r. Increasing choices L_t⊂X_t⊂U_t exist exactly when Σ_{s≤t}L_s⊂∩_{u≥t}U_u for every t. When they exist, their least and greatest choices are respectively those cumulative sums and future intersections; pointwise sums and intersections preserve feasibility.

**Proof.** For a feasible chain, every L_s with s≤t lies in X_t, while X_t lies in U_u for every u≥t, proving necessity. Put A_t=Σ_{s≤t}L_s and B_t=∩_{u≥t}U_u. Both sequences are increasing. The assumed inclusions imply L_t⊂A_t⊂U_t and L_t⊂B_t⊂U_t, so both are feasible. Any feasible X lies between them by the necessity argument. Sums and intersections of increasing chains are increasing and still contain each L_t and lie inside each U_t. Thus all finite meets and joins are the stated pointwise operations.

**Use and dependencies.** A constructive sufficient criterion for simultaneous frame-window constraints; no dimension-only replacement of the subspace inclusions is asserted.

<a id="a057"></a>

### A057 — Theorem: Nested containment constraints admit an invertible witness exactly by dimensions

**Statement.** For two increasing chains U_i,V_i in spaces of the same dimension N, there is an invertible f with f(U_i)⊂V_i for all i if and only if dim U_i≤dim V_i for all i.

**Proof.** Necessity is immediate from injectivity. Choose a basis adapted to the U-chain. At the earliest stage choose images for its new basis vectors independently in V_i, extending all images already selected. There is room because the number required by stage i is dim U_i and dim V_i is at least that number; all previously chosen images lie in V_i by nesting. Continue through the chain, then extend the independent selected images to a basis of the whole target and send the remaining source basis vectors there. This defines an invertible map with all required containments.

**Use and dependencies.** Produces actual feasible witnesses for a single nested matching problem; the conclusion does not extend to arbitrary unrelated subspace families.

<a id="a058"></a>

### A058 — Theorem: Paired inverse-transpose maps are exactly the two-Lagrangian symplectic stabilizer

**Statement.** On V⊕V* with ω((v,λ),(w,μ))=μ(v)−λ(w), the map diag(A,A⁻ᵀ) is symplectic and has determinant1. Conversely every symplectic map preserving V and V* individually has this form.

**Proof.** Substitution gives (A⁻ᵀμ)(Av)−(A⁻ᵀλ)(Aw)=μ(v)−λ(w), proving preservation. Its determinant is det A times det A⁻ᵀ=1. Conversely preserving both summands makes the map diag(A,B). The pairing condition says (Bμ)(Av)=μ(v) for every v,μ. Therefore B=(A⁻¹)*, which is A⁻ᵀ in dual bases. Both diagonal blocks are invertible because the whole map is. The argument is valid in characteristic2 as well, where the displayed alternating form remains nondegenerate.

**Use and dependencies.** An explicit Levi lift with exact determinant, related to actual source L6; it is not a free tensor-cost reduction.

<a id="a059"></a>

### A059 — Theorem: Lagrangian graphs have explicit symplectic chart transitions

**Statement.** In V⊕V* with the pairing of A058, half-dimensional subspaces transverse to V* are graphs of unique S:V→V*. Such a graph is Lagrangian exactly when S(v)(w)=S(w)(v). For a symplectic block map g=[[a,b],[c,d]], its image of graph S is transverse to V* exactly when a+bS is invertible. On precisely that chart its new graph map is T=(c+dS)(a+bS)⁻¹, which is symmetric if and only if S is symmetric. These statements hold in every characteristic.

**Proof.** Projection from a half-dimensional transverse subspace onto V is bijective, yielding its unique graph map. The alternating pairing of two graph vectors is S(w)(v)−S(v)(w), so isotropy is exactly symmetry; half dimension makes an isotropic graph Lagrangian. Now g(v,Sv)=((a+bS)v,(c+dS)v). Because g and the graph parameterization are isomorphisms onto their images, the image projection to V is bijective exactly when a+bS is invertible. Under that condition set u=(a+bS)v; the second coordinate becomes (c+dS)(a+bS)⁻¹u, proving the formula and its uniqueness. Symplecticity and invertibility preserve isotropy in both directions, so the first part proves T symmetric if and only if S is symmetric, without division by 2. Conversely if the image is a graph, its projection must be bijective and forces that same invertibility. Applying the same reasoning to g⁻¹ recovers S on the inverse chart. As a special case the shear (v,λ)↦(v,λ+Sv) is symplectic exactly for symmetric S, by direct substitution in the pairing.

**Use and dependencies.** Builds on the basic symmetric graph parameterization, also covered in Volume II B006, by giving the exact rational transition and its necessary-and-sufficient domain. Useful for changing Lagrangian coordinate charts without assuming an everywhere-defined fractional expression. Depends on A058 and the displayed pairing, with no characteristic2 exception.

<a id="a060"></a>

### A060 — Conjecture: Uniform unmarked tensor recovery of paired flags

**Statement and status.** For each field K, seek a uniform polynomial-size construction from two finite flags in V to a single ordinary order-three tensor T, with no externally marked summands, such that a distinguished intrinsic quotient of T recovers V and both flags, and the induced map Aut(T)→GL(V) has image exactly the common flag stabilizer. The construction must also lift every member of that stabilizer. This precise package is **not proved here**; no assertion of global novelty or global openness is made.

**Evidence and approach.** A051–A055 give explicit block descriptions and lifts once the flags are marked. One can encode inclusions as a finite linear diagram and then seek intrinsic radical or centroid tags, as in A018 and A020, that recover the diagram after all markings are forgotten. The missing work is a complete proof that unwanted tensor automorphisms cannot mix these tags, with polynomial size uniform in the flag lengths and field.

**Use and falsifier.** Such a compiler would turn paired-flag character calculations into ordinary tensor stabilizer calculations. A construction allowing extra quotient automorphisms, or failing to lift one legitimate common stabilizer, fails the stated target. P3 supplies tensor-reduction context, not this conjecture's proof.

## VII. Norms, restriction of scalars, and determinant descent

<a id="a061"></a>

### A061 — Theorem: Coprime powers have an explicit inverse on bounded torsion

**Statement.** In any group, if x^n=1 and gcd(m,n)=1 with n>0, then x has a unique mth root in the cyclic subgroup it generates. If um+vn=1, that root is x^u. More generally the mth-power map is an automorphism on any abelian group of exponent dividing n.

**Proof.** The identity (x^u)^m=x^{um}=x^{1−vn}=x proves existence. If y,z in the cyclic subgroup have y^m=z^m, their quotient has both mth and nth power 1, so raising the two equations to u and v and multiplying gives y z⁻¹=1. In an abelian exponent-n group the same calculation works for every element and the power maps are homomorphisms. The identity um+vn=1 makes the mth and uth power maps two-sided inverses. No uniqueness of roots in a nonabelian ambient group is asserted.

**Use and dependencies.** Explicit correction for finite component groups, underlying A077; related to source L8.

<a id="a062"></a>

### A062 — Theorem: Nonzero Kummer fibres are separable root torsors

**Statement.** If n>0 is invertible in a field K and a∈K×, then T^n−a is separable. Over a field containing a root b and all nth roots of unity, its roots are exactly bμ_n, freely and transitively acted on by μ_n. The algebra K[T]/(T^n−a) is a product of finite separable field extensions.

**Proof.** A common root of T^n−a and its derivative nT^{n−1} would be0, impossible since a≠0. Thus there are no repeated irreducible factors. Factor into distinct monic irreducibles over K; the Chinese remainder theorem identifies the quotient algebra with their field quotients, each separable by the derivative test. A root c satisfies (c/b)^n=1, and every bζ with ζ^n=1 is a root. Multiplication on these ratios proves freeness and transitivity.

**Use and dependencies.** Identifies when a root-fibre calculation is an étale torsor rather than an inseparable equation. Complements A024.

<a id="a063"></a>

### A063 — Theorem: The norm is a multiplicative determinant with exact scalar powers

**Statement.** For a finite extension L/K of degree d, N_{L/K}(b)=det_K(m_b), m_b(x)=bx, is multiplicative; it is nonzero exactly when b≠0, and N_{L/K}(a)=a^d for a∈K.

**Proof.** Multiplication operators satisfy m_{bc}=m_bm_c, so determinants multiply. For b≠0, m_{b⁻¹} is inverse to m_b; for b=0 and d>0, m_b is zero and has determinant0. For a∈K, multiplication is the scalar matrix aI_d in any K-basis, with determinant a^d. These also show N(1)=1 and N(b⁻¹)=N(b)⁻¹ for nonzero b.

**Use and dependencies.** Supplies actual arithmetic for the next descent theorems. Primary precedent P1, Stacks tag0BIE; source L7 was inspected, without a new kernel claim.

<a id="a064"></a>

### A064 — Theorem: Restriction-of-scalars determinants are norms of determinants

**Statement.** For A∈M_n(L), det_K(A acting on L^n)=N_{L/K}(det_L A). Consequently norms are transitive in finite towers.

**Proof.** If A is singular over L it has a nonzero kernel vector, so both sides vanish. Otherwise Gaussian elimination expresses A as a product of elementary row additions, diagonal coordinate scalings, and coordinate swaps. A row addition acts as a K-block transvection of determinant1. Scaling an L-coordinate by b has K-determinant N(b), by A063. Swapping two L-coordinate blocks of dimension d has K-determinant (−1)^d=N(−1). Multiplicativity proves the formula. For K⊂L⊂E, apply it to the L-linear multiplication operator m_b on E: its K-determinant is N_{E/K}(b), while the right side is N_{L/K}(N_{E/L}(b)).

**Use and dependencies.** Exact determinant accounting for coefficient-algebra recovery, also in inseparable extensions. Depends on A063; P1 is a precedent.

<a id="a065"></a>

### A065 — Theorem: Coprime extension degree forces root descent

**Statement.** Let [L:K]=d, a∈K×, b∈L× and b^n=a, with n>0 and gcd(n,d)=1. If ud+vn=1 then c=N_{L/K}(b)^u a^v∈K× satisfies c^n=a.

**Proof.** By A063, N(b)^n=N(b^n)=N(a)=a^d. Negative exponents are legal since all quantities are nonzero. Hence c^n=a^{du}a^{vn}=a. This constructs a root in K without normality, separability, or a Galois action. Coprimality is substantive: adjoining a missing nth root in degree sharing a factor with n need not permit descent.

**Use and dependencies.** A sufficient scalar descent theorem with explicit witness; depends on A063 and Bézout. A classical norm argument, not claimed globally new.

<a id="a066"></a>

### A066 — Theorem: Coupled scalar determinant corrections descend together

**Statement.** Let n_i>0 for i=1,2,3 and [L:K]=d coprime to N=lcm(n_1,n_2,n_3). Suppose a_i∈K× and b_i∈L× satisfy b_i^{n_i}=a_i and b_1b_2b_3=1. There are c_i∈K× with c_i^{n_i}=a_i and c_1c_2c_3=1.

**Proof.** Choose u,v with du+Nv=1 and define c_i=N_{L/K}(b_i)^u a_i^{Nv/n_i}; each exponent is integral. Taking n_i-th powers gives a_i^{du+Nv}=a_i. Multiplying the c_i gives N(b_1b_2b_3)^u times ∏a_i^{Nv/n_i}. The first factor is1. Inside L the second equals ∏b_i^{Nv}=(b_1b_2b_3)^{Nv}=1. Since K embeds in L, it equals1 already in K. Thus the common formula preserves the coupling equation, unlike arbitrary independent choices of roots.

**Use and dependencies.** A simultaneous sufficient certificate for scalar corrections in three tensor factors. Depends on A063–A065.

<a id="a067"></a>

### A067 — Theorem: Split-torus monomial image membership descends in coprime degree

**Statement.** Let M be an integer matrix with nonzero Smith entries d_1,…,d_r>0. For [L:K]=e coprime to every d_i, a target y∈(K×)^s belongs to M((L×)^n) exactly when it belongs to M((K×)^n).

**Proof.** Integer row and column operations from A023 act as automorphisms on the relevant products of multiplicative groups over both fields, and keep the transformed target in K. The transformed equation is z_i^{d_i}=y'_i for i≤r and y'_i=1 in the remaining rows. Solvability over L gives the zero-row equalities in K by injectivity. Each nonzero row has a K-root by A065. Choose these roots and set free coordinates to 1, then undo the column transformation. The reverse implication follows from inclusion K⊂L.

**Use and dependencies.** Descends a full finite system of coupled multiplicative equations under precise sufficient coprimality. Depends on A023 and A065.

<a id="a068"></a>

### A068 — Theorem: Finite-field norms are surjective with equal fibres

**Statement.** For F_{q^d}/F_q, the norm is b↦b^{(q^d−1)/(q−1)}. It maps the multiplicative group onto F_q×, with every nonzero fibre of size (q^d−1)/(q−1).

**Proof.** Frobenius z↦z^q generates the degree-d Galois group, and its powers give the d embeddings: the conjugates follow the Frobenius orbit of a minimal-polynomial root. The determinant norm is their product: after extending scalars to a splitting field the separable multiplication algebra is diagonal on its embedding factors, with eigenvalues b,b^q,…,b^{q^{d−1}}. Their product gives the exponent. The finite group F_{q^d}× is cyclic, as established in A029. The displayed power map has kernel of the stated size and image of order q−1. Its values are Frobenius-fixed, so the image is exactly F_q×.

**Use and dependencies.** Gives exact norm fibres and counts. Uses A029 and A063; P2 supplies standard finite-field Galois background.

<a id="a069"></a>

### A069 — Theorem: Marked coefficient actions recover extension-linear transporters

**Statement.** For finite-dimensional L-spaces V,W, a K-linear map f:V→W is L-linear precisely when it commutes with multiplication by a set of K-algebra generators of L. With those actions marked, restriction of scalars neither loses nor introduces isomorphisms of L-linear tensor or algebra diagrams.

**Proof.** An L-linear map commutes with every scalar. Conversely the λ satisfying f(λv)=λf(v) for all v are closed under addition, multiplication and K-scalars, and contain the generators; thus they form all of L. Once component maps are L-linear, the multilinear diagram equations are the identical equations before and after forgetting to K. An invertible K-map respecting the marks is therefore an invertible L-map; its inverse commutes with the marks by multiplying the original commutation equations by that inverse. Without the marks no recovery claim is made.

**Use and dependencies.** A sufficient witness-recovery theorem for restriction-of-scalars reductions; A064 gives its separate determinant bookkeeping.

<a id="a070"></a>

### A070 — Theorem: Quadratic norm-one elements have a rational parameter chart

**Statement.** Let char K≠2 and L=K(u), u²=d∈K× nonsquare. Every norm-one z∈L× other than−1 has a unique form z=(1+tu)/(1−tu), t∈K. Every such expression has norm1; −1 is the omitted point.

**Proof.** Conjugation σ(u)=−u gives σz=z⁻¹. For z≠−1 put t=(z−1)/(u(z+1)). Its conjugate is (z⁻¹−1)/(−u(z⁻¹+1)), which simplifies to t; hence t∈K. Rearrangement gives the displayed expression. Its denominator cannot vanish since tu=1 would put u in K. Conversely conjugation swaps numerator and denominator, proving norm1. The inverse formula proves uniqueness. The expression cannot equal−1, since that would force 2=0.

**Use and dependencies.** An explicit chart for a norm-one torus and rational witness construction; depends on quadratic conjugation and A063.

## VIII. Frobenius and cyclic correction equations

For A071–A075, H and D are groups, φ:H→D is a group homomorphism, N=ker φ, and the automorphisms F of H and D commute with φ. In A076–A080, F denotes an automorphism of the stated abelian group N. Fixed subgroups and correction equations always refer to these actions.

<a id="a071"></a>

### A071 — Lemma: Fixed character values place the lifting obstruction in the kernel

**Statement.** Let φ:H→D be a group homomorphism commuting with automorphisms F of both groups. If φ(h) is F-fixed then c=h⁻¹F(h) belongs to the F-stable subgroup N=ker φ.

**Proof.** Applying φ gives φ(c)=φ(h)⁻¹F(φ(h))=1, exactly the kernel condition. For n∈N, φ(Fn)=Fφ(n)=1, so N is F-stable. The actual equivariance of φ is needed; an unrelated automorphism and character would not suffice.

**Use and dependencies.** Identifies a concrete correction problem without assuming it solvable; a precedent is actual source L2.

<a id="a072"></a>

### A072 — Theorem: Fixed lifts are exactly kernel Lang corrections

**Statement.** In A071 an F-fixed lift of φ(h) exists exactly when c=nF(n)⁻¹ for some n∈N. These lifts are precisely h n for such n. Replacing the initial lift by h b, b∈N, changes the obstruction to b⁻¹cF(b).

**Proof.** Every lift is hn with n∈N. Since F(h)=hc, fixedness is hcF(n)=hn, equivalently c=nF(n)⁻¹. Conversely that equation makes hn fixed. Expansion gives (hb)⁻¹F(hb)=b⁻¹h⁻¹F(h)F(b)=b⁻¹cF(b). This proves the equivalence with all factor orders intact.

**Use and dependencies.** A precise correction identity used in the sufficient results below, not alone advertised as solving descent. Source L2 is a direct precedent.

<a id="a073"></a>

### A073 — Theorem: Nonempty fixed fibres are torsors with exact counts

**Statement.** An F-fixed lift h_0 of d gives a bijection N^F→{h:Fh=h, φ(h)=d}, n↦h_0n. For finite groups every nonempty fixed fibre therefore has |N^F| elements.

**Proof.** Products of fixed elements are fixed, and φ(h_0n)=d for n∈N. Conversely h in the stated fibre gives n=h_0⁻¹h∈N, and that quotient is fixed. Multiplication and cancellation make the maps inverse. Counting proves the assertion. Only if surjectivity onto D^F has separately been established does this imply |H^F|=|D^F||N^F|.

**Use and dependencies.** Turns a sufficient lifting theorem into exact counts; related to the fibre equivalence in L2.

<a id="a074"></a>

### A074 — Theorem: Component correction plus an internal Lang solution suffices

**Statement.** Let J≤N be F-stable and suppose every j∈J has form aF(a)⁻¹ with a∈J. If b∈N satisfies b⁻¹cF(b)∈J, then φ(h) has an F-fixed lift.

**Proof.** Write b⁻¹cF(b)=aF(a)⁻¹. Rearranging gives c=baF(a)⁻¹F(b)⁻¹=(ba)F(ba)⁻¹. The element ba lies in N, so A072 gives the fixed lift hba. No commutativity is used. This proof requires actual surjectivity of the displayed map on J, not a connectedness slogan or an unspecified theorem.

**Use and dependencies.** A complete sufficient assembly with explicit final witness. In an algebraic-group application its Lang hypothesis must be supplied independently; L2 and L8 motivated the decomposition.

<a id="a075"></a>

### A075 — Lemma: The twisted obstruction norm telescopes

**Statement.** For c=h⁻¹F(h) and r>0, cF(c)⋯F^{r−1}(c)=h⁻¹F^r(h). An F^r-fixed initial lift therefore has twisted norm1.

**Proof.** Expand the product as (h⁻¹Fh)(Fh⁻¹F²h)⋯(F^{r−1}h⁻¹F^rh). Adjacent factors cancel, leaving the claimed endpoints. In a nonabelian group the displayed order is essential and no factors have been reordered.

**Use and dependencies.** Supplies the actual norm-one hypothesis for explicit cyclic correction. It does not claim norm-one sufficient in arbitrary nonabelian kernels.

<a id="a076"></a>

### A076 — Theorem: Weighted multiplicative averaging gives explicit corrections

**Statement.** Let N be abelian, F^r=1, and c∈N. Put B=∏_{i=0}^{r−1}F^i(c)^{r−1−i} and P=∏_{i=0}^{r−1}F^i(c). Then B/F(B)=c^r/P. If P=1 and c has order m coprime to r, choose k with rk≡1 mod m; n=B^k solves c=n/F(n).

**Proof.** The exponent of c in B/F(B) is r−1, and the exponent of each F^i(c) for 1≤i≤r−1 is−1. The wrapped F^r(c) term contributes0 because its originating exponent was0. This is exactly c^r/P. If P=1, raising to k gives n/F(n)=c^{rk}=c. Commutativity licenses the collected exponents; without it this calculation is not asserted.

**Use and dependencies.** An explicit sufficient cyclic descent formula, related to weighted averaging in L8. Uses A061.

<a id="a077"></a>

### A077 — Theorem: Coprime cyclic norm-one is exactly the correction criterion

**Statement.** For finite abelian N, F^r=1 and gcd(r,|N|)=1, an element c has twisted norm1 precisely when c=n/F(n) for some n∈N.

**Proof.** A correction's twisted norm telescopes to n/F^r(n)=1. Conversely the order of c divides |N|, so is coprime to r; A076 constructs n. Combined with A071–A072, this proves fixed-lift existence whenever the actual obstruction has norm1 in this setting. The coprimality and abelian hypotheses are explicit parts of the sufficient theorem.

**Use and dependencies.** A complete finite-kernel descent statement, with sources L8 and L2 as nearby precedents.

<a id="a078"></a>

### A078 — Theorem: Primary components solve abelian corrections independently

**Statement.** For finite abelian N, every primary subgroup N_ℓ is F-stable and N=∏_ℓN_ℓ. A correction c=n/F(n) exists precisely when it exists in each primary component; component solutions multiply to a global solution.

**Proof.** Elements of ℓ-power order form a subgroup and automorphisms preserve orders. For exponent M=∏ℓ^{a_ℓ}, choose integers e_ℓ equal to 1 modulo ℓ^{a_ℓ} and 0 modulo all other prime powers. The Chinese remainder theorem gives Σe_ℓ≡1 mod M. Thus x=∏x^{e_ℓ}, with each factor in its primary subgroup. Intersections of distinct primary subgroups are trivial, proving uniqueness. These power projections commute with F. Projecting a correction gives necessity; multiplying component equations gives sufficiency.

**Use and dependencies.** Constructive local-to-global correction and isolation of the primes that violate A077's hypothesis.

<a id="a079"></a>

### A079 — Theorem: Invariant characters detect every finite abelian correction obstruction

**Statement.** For finite abelian N, c lies in I={n/F(n)} exactly when χ(c)=1 for every complex character χ with χ∘F=χ.

**Proof.** The set I is a subgroup because N is abelian. A character vanishes on I exactly when χ(n)=χ(Fn) for every n, the stated invariance. Characters of a finite abelian quotient separate points: Smith normal form decomposes it into cyclic groups, and a nonzero cyclic coordinate is separated by a character taking its generator to a primitive root of unity of its order. If c∉I, apply this to its nonidentity class in N/I and pull back the separating character. If c∈I every such character is1 on it directly.

**Use and dependencies.** A complete finite certificate for the abelian Lang image. Depends on A022 and A026–A027.

<a id="a080"></a>

### A080 — Theorem: Cyclic kernels give explicit congruence tests and all solutions

**Statement.** Let N=⟨z⟩ have order m>0 and F(z)=z^q, gcd(q,m)=1. For c=z^a, the correction equation is solvable exactly when g=gcd(m,1−q) divides a, and then has exactly g solutions.

**Proof.** Writing n=z^b gives (1−q)b≡a mod m. Its possible integer values generate the ideal gZ, proving the criterion. A Bézout identity for m and 1−q, multiplied by a/g, supplies a solution b_0. Every homogeneous solution is a multiple of m/g modulo m: divide the congruence by g and use the coefficient's coprimality to m/g. There are exactly g such residues. Substitution gives all correction elements and their explicit computation by the extended Euclidean algorithm.

**Use and dependencies.** Converts A079's abstract character criterion into a small arithmetic certificate with exact multiplicities.

## IX. Galois descent with reconstructed witnesses

In A082–A090, L/K is finite Galois with group Γ; A082 imposes cyclicity additionally. In A084–A089 the vector spaces carrying an action are finite-dimensional L-spaces with semilinear Γ-actions. The fixed field is K. A081 itself concerns arbitrary distinct field homomorphisms.

<a id="a081"></a>

### A081 — Theorem: Distinct field homomorphisms are linearly independent

**Statement.** Distinct field homomorphisms σ_1,…,σ_r:L→E are linearly independent as functions over E.

**Proof.** Suppose Σc_iσ_i(x)=0 for every x, and take a nontrivial relation with the fewest nonzero coefficients. A one-term relation is impossible by evaluation at1. Relabel so σ_1≠σ_r and both coefficients are nonzero. Choose a with σ_1(a)≠σ_r(a). Evaluate at ax and subtract σ_r(a) times the original relation at x. The σ_r term disappears while the σ_1 coefficient stays nonzero. This is a shorter nontrivial relation, a contradiction.

**Use and dependencies.** Dedekind independence supplies the nonvanishing in Hilbert90 and semilinear descent. Classical precedent P2.

<a id="a082"></a>

### A082 — Theorem: Cyclic Hilbert90 has an explicit construction

**Statement.** For a cyclic Galois extension L/K with generator σ of order r, a∈L× has norm1 exactly when a=b/σ(b) for some b∈L×.

**Proof.** Necessity telescopes the product of conjugates. For sufficiency put p_0=1 and p_i=aσ(a)⋯σ^{i−1}(a). The operator B(t)=Σ_{i=0}^{r−1}p_iσ^i(t) is nonzero by A081, since its identity coefficient is1. Choose t with b=B(t)≠0. Multiplying σ(B(t)) by a shifts each summand's index by 1. Its final summand becomes p_rσ^r(t)=t because the norm is1. Therefore aσ(b)=b, as required. For r=1 the hypothesis forces a=1 and the same formula works.

**Use and dependencies.** Constructs a witness by finding a nonzero value of an explicit linear operator; no root oracle. Depends on A081; P2 is a classical source.

<a id="a083"></a>

### A083 — Theorem: Every finite Galois extension contains an element of trace1

**Statement.** For finite Galois L/K with group Γ, including characteristic dividing [L:K], some t∈L satisfies Σ_σσ(t)=1.

**Proof.** By A081 the sum of the distinct automorphisms, with all coefficients1, is a nonzero function. Its values are fixed by Γ because the summands are permuted, hence lie in K. Choose t_0 of trace a≠0 and set t=t_0/a. K-linearity gives trace1. Division by |Γ| was not used and could be invalid in the stated characteristic.

**Use and dependencies.** Distinguishes genuine Galois descent from nonmodular group averaging. Depends on A081 and the fixed-field property of a Galois extension.

<a id="a084"></a>

### A084 — Theorem: Fixed vectors span every semilinear Galois representation

**Statement.** If a finite-dimensional L-space V has a semilinear action of the finite Galois group Γ of L/K, then V^Γ spans V over L.

**Proof.** For a∈L and v∈V the vector A_a(v)=Σ_σσ(av) is fixed by reindexing. If their L-span were proper, choose a nonzero L-linear functional f annihilating it by extending a basis of that span. For every a, Σ_σσ(a)f(σv)=0. Independence A081 forces every coefficient f(σv)=0, especially f(v)=0. This holds for every v, contradicting f≠0. Thus the explicitly constructed fixed vectors span V, without dividing by |Γ|.

**Use and dependencies.** The sufficient spanning theorem behind full vector-space descent. Depends on A081; valid in all characteristics.

<a id="a085"></a>

### A085 — Theorem: Semilinear descent reconstructs a basis over the fixed field

**Statement.** The map L⊗_K V^Γ→V, a⊗v↦av, is an isomorphism. In particular dim_K V^Γ=dim_L V.

**Proof.** Select from A084 an L-basis e_1,…,e_n of fixed vectors. A vector Σa_ie_i is fixed precisely when σ(a_i)=a_i for all i,σ, by independence of the basis. The fixed-field property makes this equivalent to a_i∈K. Thus the e_i are also a K-basis of V^Γ, and the displayed map carries an L-basis to an L-basis. This proves both injectivity and surjectivity.

**Use and dependencies.** Full descent once the semilinear action is supplied. It does not create such an action on an arbitrary extension-field transporter fibre. Depends on A084.

<a id="a086"></a>

### A086 — Theorem: Matrix Hilbert90 reconstructs a simultaneous change of basis

**Statement.** For A_σ∈GL_n(L) satisfying A_{στ}=A_σσ(A_τ), some B∈GL_n(L) satisfies A_σ=Bσ(B)⁻¹ for all σ. Conversely every such B gives a cocycle.

**Proof.** Define σ⋆v=A_σσ(v). The cocycle identity is exactly the group-action equation; it forces A_1=I by cancellation. Apply A085 to select an L-basis of fixed vectors and put them in the columns of B. Fixedness says A_σσ(B)=B, giving the formula. Conversely substitute that formula into A_σσ(A_τ). The adjacent σ(B)⁻¹σ(B) factors cancel, leaving Bστ(B)⁻¹, proving the cocycle identity.

**Use and dependencies.** A simultaneous sufficient matrix correction theorem with an invariant-basis construction. Depends on A085; a classical Hilbert90 form, not a global novelty claim.

<a id="a087"></a>

### A087 — Theorem: Morphisms, exact sequences, tensors and duals descend

**Statement.** For semilinear Γ-spaces U,V, equivariant L-linear maps correspond bijectively to K-linear maps U^Γ→V^Γ. Fixed vectors preserve short exact sequences and commute with tensor products and duals.

**Proof.** In fixed bases from A085 a matrix is equivariant exactly when all its entries are fixed by Γ, hence in K. This proves the morphism assertion and its inverse by scalar extension. A short exact sequence has matrices over K; row reduction computes the same ranks over K and L, proving injectivity, surjectivity and equality of image and kernel over K. Products of fixed basis vectors form a fixed basis of a tensor product. The dual basis is fixed under the dual action. Their fixed parts therefore have exactly the claimed tensor and dual bases, proving the remaining identifications.

**Use and dependencies.** Descends entire finite linear diagrams and exact constructions, not merely objects. Depends on A085.

<a id="a088"></a>

### A088 — Theorem: Galois-stable subspaces are defined over the base field

**Statement.** A coordinatewise Γ-stable subspace W⊂L^n is the L-span of W∩K^n; L⊗_K(W∩K^n)→W is an isomorphism.

**Proof.** Restrict the semilinear action to W. Its fixed elements are exactly vectors whose coordinates lie in K, namely W∩K^n. A085 gives both assertions. A fixed basis of W gives a matrix over K of the same rank before and after extension, an explicit certificate for the descended space.

**Use and dependencies.** Descends supports, kernels and Grassmannian points after their stability has been proved. Depends on A085; arbitrary extension-defined subspaces are not asserted stable.

<a id="a089"></a>

### A089 — Theorem: Compatible algebra and tensor operations descend with their identities

**Statement.** A finite-dimensional L-algebra with semilinear Γ-action by algebra automorphisms is obtained by scalar extension from its fixed K-algebra. The same holds for finite families of multilinear operations and equivariant units. Structure-coefficient polynomial identities and nondegeneracy of bilinear forms descend.

**Proof.** Choose a fixed basis by A085. Products of fixed vectors are fixed, so all structure coefficients lie in K. The same reasoning applies to each multilinear operation and fixed unit. Their scalar extensions recover the original operations by multilinearity. Any polynomial identity in the structure coefficients holds over K precisely when it holds after embedding into L, by injectivity. This includes associativity, symmetry and unit equations. A bilinear form has the same matrix over K and L, and its determinant is nonzero over one precisely when nonzero over the other. Thus its nondegeneracy also descends.

**Use and dependencies.** A sufficient reconstruction theorem for algebra objects and tensor diagrams, with an explicit equivariant-action hypothesis. It does not infer that action from a single L-isomorphism.

<a id="a090"></a>

### A090 — Theorem: Galois-stable polynomial ideals descend coefficientwise

**Statement.** A coefficientwise Γ-stable ideal I⊂L[x_1,…,x_n] is generated as an ideal by I∩K[x_1,…,x_n].

**Proof.** For each d the polynomials in I of total degree at most d form a finite-dimensional stable space W_d. By A088 it is the L-span of its elements with K-coefficients. Given f∈I, choose d≥deg f. Thus f is an L-linear combination of elements of I∩K[x], and belongs to their generated ideal. The reverse inclusion follows because I contains these elements and is an ideal. This proves equality without assuming any rational-point existence statement.

**Use and dependencies.** Descends equations of stable affine subschemes with a degree-by-degree reconstruction. Depends on A088.

## X. Exact certificates and controlled reconstruction

<a id="a091"></a>

### A091 — Theorem: Schur complements preserve rank, determinant and explicit solutions

**Statement.** For M=[[A,B],[C,D]] with A invertible set S=D−CA⁻¹B. Then rank M=dim A+rank S; when square, det M=det A·det S. Its kernel is {(-A⁻¹By,y):Sy=0}.

**Proof.** Multiply on the left by [[I,0],[−CA⁻¹,I]] and on the right by [[I,−A⁻¹B],[0,I]]. Direct multiplication gives diag(A,S), and both multiplier matrices are invertible with determinant1. This proves the rank and determinant formulas. The first equation in M(x,y)=0 forces x=−A⁻¹By. Substitution into the second gives Sy=0, proving the kernel formula in both directions.

**Use and dependencies.** Eliminates a nonsingular block while retaining an actual recovery map, stronger information than a rank obstruction alone.

<a id="a092"></a>

### A092 — Theorem: Rank-one updates have exact determinant and inverse tests

**Statement.** For invertible A and columns u,v, det(A+uvᵀ)=det A·(1+vᵀA⁻¹u). If s=1+vᵀA⁻¹u≠0, the inverse is A⁻¹−A⁻¹uvᵀA⁻¹/s; if s=0 it is singular.

**Proof.** Put x=A⁻¹u. For x=0 the assertions are immediate. Otherwise a basis starting with x makes I+xvᵀ act on Kx by 1+vᵀx and on the quotient by identity. Its determinant is the former scalar; multiplication by A proves the determinant formula. For s≠0 multiply I+xvᵀ by I−xvᵀ/s: the coefficient of xvᵀ is1−1/s−(vᵀx)/s=0. This gives the inverse formula. For s=0 the nonzero vector x is killed by I+xvᵀ, proving singularity directly.

**Use and dependencies.** Exact low-rank correction witnesses for controlled basis changes without full repeated elimination.

<a id="a093"></a>

### A093 — Theorem: Rank normal forms give explicit, field-stable certificates

**Statement.** For an m×n matrix M of rank r, invertible P,Q give PMQ=diag(I_r,0) in rectangular block form. The last n−r columns of Q form a kernel basis and the first r columns of MQ form an image basis. The same certificate holds after every field extension.

**Proof.** Choose a basis k_i of ker M and extend it by vectors v_1,…,v_r whose images form an image basis. Let Q have columns v_1,…,v_r,k_1,… . Extend Mv_1,…,Mv_r to a target basis and let P send it to the standard basis. Multiplication gives exactly the claimed normal form. Its zero and identity blocks identify both bases. All matrix and inverse identities remain valid under field extension, proving the certificate and rank persist.

**Use and dependencies.** Verifiable sufficient certificates for nullspaces and ranks, underlying the scalar-extension argument A047.

<a id="a094"></a>

### A094 — Theorem: A nonzero minor reconstructs a subspace in a rational chart

**Statement.** If an r-dimensional W⊂K^n projects isomorphically onto some r coordinates I, it has a unique basis matrix C whose I-rows are I_r. Each other entry is a signed ratio of r×r minors of any basis matrix, and these chart entries determine W.

**Proof.** For any basis matrix B let C=BB_I⁻¹. Its selected block is identity. Replacing B by BT changes this expression to BT(B_IT)⁻¹=C, proving independence and uniqueness. Cramer's rule gives the coefficients of any row of B in the selected-row basis by replacing one selected row and dividing its determinant by det B_I. These are exactly the indicated signed minor ratios. Conversely the columns of C span W, so the chart reconstructs the entire subspace without another equivalence choice.

**Use and dependencies.** Turns Plücker ratios into an actual subspace witness on a stated nonvanishing chart.

<a id="a095"></a>

### A095 — Theorem: Matrix-space invertibility has a bounded evaluation certificate

**Statement.** If the span of n×n matrices M_i over K contains an invertible evaluation over an extension, then every finite S⊂K with |S|>n has some z∈S^s for which Σz_iM_i is invertible. More generally a nonzero polynomial of total degree d has at most d|S|^{s−1} zeros in S^s.

**Proof.** Induct on s for the polynomial bound. For s=1 use the root bound. Write P=Σ_{j=0}^kQ_jz_s^j with Q_k≠0 and deg Q_k≤d−k. If d≥|S| the desired bound is already at least all |S|^s points, so assume d<|S|. By induction at most (d−k)|S|^{s−2} first-coordinate choices kill Q_k. Count every last coordinate over those; over the others there are at most k roots. The resulting sum is at most d|S|^{s−1}. The determinant polynomial det(Σz_iM_i) has total degree n and is nonzero because of its extension-field invertible value. Its zero count is smaller than |S|^s, proving the matrix assertion.

**Use and dependencies.** Supplies a finite exact search domain, without claiming that enumerating S^s is polynomial time in s.

<a id="a096"></a>

### A096 — Theorem: Modular nullspace reconstruction has an exact height certificate

**Statement.** Let an integer matrix C have rank r>0 and entries bounded in absolute value by B≥1. Choose a nonzero r×r minor D. Its pivot-equation kernel basis has reduced rational numerators and denominators bounded by H=r!B^r. Every prime p∤D preserves the chosen pivot rank r. Rational entries of these bounds, with denominators coprime to M, are uniquely determined by residues modulo M when M>2H².

**Proof.** Choose the corresponding r independent rows and pivot columns. Give one free coordinate value1 and the other free coordinates0. Cramer's rule solves the pivot coordinates by determinants replacing one column with the negative free column. These determinants and D are bounded by r!B^r using the permutation expansion. All remaining rows are rational linear combinations of the chosen ones and impose no new equations. Distinct free coordinates give a kernel basis. Modulo p the minor D stays nonzero, so rank is at least r; all larger integer minors are zero, so it is at most r. Finally residues a/b=c/d mod M imply M divides ad−bc. That integer has absolute value ≤2H²<M, so is0. This proves uniqueness. Proposed reconstructed vectors must still be checked exactly by Cv=0.

**Use and dependencies.** Separates safe modular reconstruction from observed numerical ranks. Rank0 has the coordinate kernel basis and needs no pivot argument.

<a id="a097"></a>

### A097 — Theorem: A short finite extension contains a nonsingular evaluation

**Statement.** A matrix space over F_q with an invertible extension-field evaluation has one over F_{q^e} whenever q^e>n. For n≥1 one may take e=1+⌊log_q n⌋.

**Proof.** Its determinant polynomial is nonzero and of total degree n. It remains nonzero over F_{q^e}; use A095 with S the entire extension field. The resulting nonzero evaluation is invertible. The displayed integer e is the smallest positive one with q^e>n, including when n is a power of q. This proves a bounded extension degree and a finite enumeration method; it does not place the witness in F_q.

**Use and dependencies.** Exact finite-field search certificates without confusing extension and base-field witnesses. Depends on A095.

<a id="a098"></a>

### A098 — Theorem: Invariant hulls stabilize within the ambient dimension

**Statement.** For endomorphisms T_1,…,T_s on an N-dimensional space, iteration W_0=W, W_{j+1}=W_j+Σ_iT_iW_j reaches the least common invariant subspace containing W after at most N−dim W strict steps.

**Proof.** The sequence increases, and every strict step increases dimension by at least 1. At equality all T_i preserve the space, so later steps remain equal. Every invariant subspace containing W contains all W_j by induction. The final space is therefore both invariant and contained in every eligible space, proving minimality. A basis at each step and the computed images T_iW_j give exact certificates for every inclusion and termination.

**Use and dependencies.** Constructs intrinsic algebraic closure spaces with a termination bound, rather than invoking unspecified saturation.

<a id="a099"></a>

### A099 — Theorem: First-order diagram deformations form an explicit linear quotient

**Statement.** For a quiver representation with polynomial relations, write arrow maps over K[ε]/(ε²) as A_e+εB_e. Their relation constraints form a linear space Z. Basis changes I+εX_v shift B_e by X_{head(e)}A_e−A_eX_{tail(e)}; these shifts form a subspace B⊂Z. First-order equivalence classes with identity reduction are exactly Z/B. The shift map's kernel is End(M).

**Proof.** Expand every relation, replacing one arrow factor at a time by B_e. Terms with two replacements vanish because ε²=0; constant terms vanish by the original relations. The remaining equations are linear, defining Z. The inverse of I+εX is I−εX, so multiplication on both sides of an arrow gives exactly the stated shift. Conjugation preserves all relations, placing its image in Z. Such changes add, again because ε²=0, so their orbits are precisely the cosets of B. Vanishing of all shifts is exactly the intertwiner system in A041, proving the kernel formula. Equivalence was restricted to basis changes reducing to identity, as the statement requires.

**Use and dependencies.** Parameterizes all first-order deformations and their gauge equivalence; no claim that each integrates to an actual one-parameter family.

<a id="a100"></a>

### A100 — Conjecture: Fixed-dimensional unipotent transporter fibres have polynomial-height points

**Statement and status.** Fix dimensions of three rational tensor factors. For tensors x,y over Q with reduced entry numerators and denominators bounded by H≥2, suppose a rational GL-transporter exists and the effective algebraic stabilizer G_x/Z is a split unipotent Q-group, where G=GL(U)×GL(V)×GL(W) and Z={(aI_U,bI_V,cI_W):abc=1} is the central kernel. Seek C depending only on the dimensions such that some rational transporter has all reduced entry numerators and denominators bounded by H^C. This is **not proved here** and is not asserted globally new or globally open.

**Evidence and approach.** Fixed-dimensional linear systems have polynomial-height solutions by determinant estimates such as A096. Split triangular correction equations have finite back-substitution formulas when their coordinates and divisions are controlled. A route is to construct bounded-degree triangular charts on these orbit fibres, uniformly bound their denominators, and select a nonvanishing chart by bounded evaluation. The effective-stabilizer promise has not supplied those charts here. Quotienting by Z is essential: the full stabilizer always contains this split central torus, so calling the full stabilizer unipotent would make the intended nonzero-dimensional class empty.

**Use and falsifier.** Such a bound would turn rational transporter existence in this class into bounded exact certificate search, not settle general rational tensor isomorphism. A fixed-dimensional family satisfying the promise but requiring superpolynomial rational height would refute it. An unspecified rational-point oracle would not prove it.

## Source and status boundary

There are 100 numbered entries:96 proved informal results and 4 research conjectures (A010,A030,A060,A100). The proofs are ordinary mathematics; no new Lean verification, model proof or kernel audit is claimed for this volume. The companion manifest distinguishes source inspection from historical DAG metadata. Hypotheses and the cited standard background, including the Hilbert basis theorem and finite Galois theory, are explicit. Conjectures are not counted as established, and none of the 100 entries is represented as a globally novel discovery.
