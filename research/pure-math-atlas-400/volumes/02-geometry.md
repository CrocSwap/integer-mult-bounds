# Volume II — Finite geometry, frames, and constructive unbiasedness

This is informal mathematics, not a Lean verification report. B001–B090, B094, B097 and B098 are proved below; the other seven numbered entries are explicitly conjectural. Classical constructions are reconstructed and attributed, not claimed as discoveries. In particular, no existence of four or seven MUBs in complex dimension six is asserted.

Throughout, a Hilbert space has positive finite complex dimension d unless another field is specified. Inner products are conjugate-linear in the first variable. A unit vector x defines P_x=xx*. Matrices act on column vectors. Hermitian matrices have real Hilbert–Schmidt inner product tr(AB); operator and Hilbert–Schmidt norms are distinguished. An orthonormal basis is unbiased to another when every cross inner product has squared modulus 1/d. Designs and vectors may be indexed with repetitions only when explicitly allowed. Standard background used below is finite-dimensional spectral decomposition, Gram–Schmidt, finite-field arithmetic, the elementary Eisenstein irreducibility criterion, and the contraction mapping theorem; uses are identified in the proofs.

Primary precedents are listed in the bibliography and machine-readable source ledger. Local sources were read as statements with hypotheses. A `Goal` definition is not a proof, and a conditional completion theorem is not an existence theorem for its hypotheses.

## 1. Finite incidence geometry and symplectic constructions

<a id="b001"></a>

### B001 — Affine lines form an explicit resolvable design [proved; classical reconstruction]

**Statement.** Let F be a finite field of order q. On F², the q vertical lines x=c and, for each a in F, the q lines y=ax+b form q+1 parallel classes. Every line has q points; every class partitions F²; two lines from distinct classes meet exactly once. Every pair of distinct points lies on exactly one of these lines.

**Proof.** Within a fixed slope a, the intercept b=y−ax is uniquely determined by a point; the vertical class is analogous. Distinct nonvertical slopes meet at the unique solution of (a−a')x=b'−b. A vertical line meets each nonvertical line at its prescribed x-coordinate. For two distinct points, equal x-coordinates force the vertical line; otherwise their difference determines the unique slope (y−y')/(x−x') and then the intercept. These cases exhaust the possibilities. Thus the construction supplies both a design and its resolution, without any existence oracle.

**Use/dependencies.** Starting incidence object for B003, B014–B016; only field division is used.

<a id="b002"></a>

### B002 — Projective completion of the affine plane [proved; classical reconstruction]

**Statement.** Adding one point for each of the q+1 directions in B001 and a line containing exactly those points gives a projective plane with q²+q+1 points and the same number of lines. Every line has q+1 points, every point lies on q+1 lines, and distinct points or distinct lines determine a unique incident line or intersection point.

**Proof.** Adjoin the direction point to every line in its parallel class. Parallel affine lines now meet there; nonparallel lines retain their unique affine intersection. The new line meets every old line at its direction point. Two old points retain their unique old line. An affine point and a direction point determine the unique line of that class through the affine point; two direction points determine the new line. Each old point lies on one line of each class; each direction point lies on q lines of its class and the new line. Counting the q(q+1) old lines plus one completes all assertions.

**Use/dependencies.** Concrete projective examples; B001. The result concerns finite-field orders, not arbitrary integers.

<a id="b003"></a>

### B003 — Exact singular spectrum of projective incidence [proved]

**Statement.** If N is the point-by-line 0–1 incidence matrix of B002 and v=q²+q+1, then NN*=qI+J. Its singular values are q+1 once and √q with multiplicity v−1. Consequently N is invertible over R.

**Proof.** A diagonal entry of NN* counts the q+1 lines through a point; an off-diagonal entry counts the unique line through two points. This gives qI+J. The all-ones vector has eigenvalue q+v=(q+1)². On its orthogonal complement, J vanishes and the eigenvalue is q. Both are positive because q≥2. Singular values are the positive square roots of these eigenvalues. There are v of them, proving invertibility.

**Use/dependencies.** An exact reconstruction and conditioning certificate for incidence data; B002.

<a id="b004"></a>

### B004 — Higher-dimensional projective point and hyperplane counts [proved]

**Statement.** In an n-dimensional F_q-vector space with n≥2, the number of one-dimensional subspaces and of hyperplanes is v=(q^n−1)/(q−1). Every hyperplane contains k=(q^(n−1)−1)/(q−1) projective points; each pair of distinct projective points lies in λ=(q^(n−2)−1)/(q−1) hyperplanes.

**Proof.** The nonzero vectors partition into one-dimensional subspaces, each with q−1 nonzero vectors. Hyperplanes are kernels of nonzero linear functionals, and two such functionals have the same kernel exactly when they differ by a nonzero scalar, giving the same count in the dual space. A hyperplane has dimension n−1 and the same point-count argument applies. Functionals vanishing on a fixed two-dimensional span form a dual space of dimension n−2; its nonzero scalar classes count the common hyperplanes. For n=2 this number is zero, as the formula states.

**Use/dependencies.** Supplies explicit symmetric design parameters for B011–B013.

<a id="b005"></a>

### B005 — Counting Lagrangian subspaces [proved]

**Statement.** A nondegenerate alternating form on F_q^(2n) has exactly ∏_{i=1}^n(q^i+1) Lagrangian subspaces, including the value 1 when n=0.

**Proof.** Every one-dimensional subspace is isotropic because the form is alternating. For an isotropic line ℓ, the quotient ℓ⊥/ℓ is nondegenerate symplectic of dimension 2n−2: the radical of the restricted form on ℓ⊥ is exactly ℓ by nondegeneracy. Lagrangians containing ℓ correspond to Lagrangians in that quotient. Count pairs (ℓ,L) with ℓ contained in a Lagrangian L. Each L contains (q^n−1)/(q−1) lines, while the ambient space has (q^(2n)−1)/(q−1) lines. If a_n is the desired count, then a_n(q^n−1)=(q^(2n)−1)a_(n−1), hence a_n=(q^n+1)a_(n−1). Start at a_0=1 and iterate.

**Use/dependencies.** Exact finite search-space size; also explains why enumeration should exploit geometry.

<a id="b006"></a>

### B006 — Symmetric matrices parametrize transverse Lagrangians [proved]

**Statement.** In F_q^n⊕F_q^n with form ω((x,y),(x',y'))=x·y'−y·x', the graph L_A={(x,Ax)} is Lagrangian precisely when A is symmetric. Moreover dim(L_A∩L_B)=dim ker(A−B).

**Proof.** On two graph vectors the form is xᵀ(A−Aᵀ)x'. It vanishes for all x,x' exactly when A=Aᵀ, including characteristic two. A graph always has dimension n, so isotropy is exactly the Lagrangian condition. A vector lies in both graphs precisely when its first coordinate x satisfies Ax=Bx. The map x↦(x,Ax) identifies that intersection with ker(A−B). Conversely, any Lagrangian transverse to the second coordinate summand has an invertible first-coordinate projection and therefore is a unique such graph.

**Use/dependencies.** Converts a geometric construction problem into explicit symmetric-matrix difference tests; B009.

<a id="b007"></a>

### B007 — An explicit symplectic spread from field multiplication [proved; classical reconstruction]

**Statement.** Let p be prime, r≥1, E=F_(p^r), q=p^r, and use ω((x,y),(x',y'))=Tr_E/Fp(xy'−yx'). The q subspaces L_a={(x,ax):x∈E}, together with L_∞={(0,y)}, are r-dimensional F_p-Lagrangians partitioning E²\{0}.

**Proof.** The trace is a nonzero F_p-linear functional: its polynomial T(X)=X+X^p+⋯+X^(p^(r−1)) is nonzero and has degree less than q, so it cannot vanish on all E. If x≠0, choose z with Tr(z)≠0 and y=x^−1z; thus the trace pairing is nondegenerate. The displayed alternating form is consequently nondegenerate. Each L_a is isotropic by commutativity of E, and L_∞ is isotropic; each has dimension r. Distinct slopes meet only at zero. Every nonzero vector with first coordinate x≠0 has slope y/x, while the remaining vectors lie in L_∞. This proves the partition.

**Use/dependencies.** A concrete spread, including p=2; B070 turns it into MUBs using an operator construction.

<a id="b008"></a>

### B008 — A verifiable hole-filling criterion for partial spreads [proved]

**Statement.** Suppose a family of pairwise disjoint n-dimensional isotropic subspaces of a 2n-dimensional symplectic F_q-space is given. Let H consist of zero and all nonzero vectors uncovered by the family. If H is closed under vector addition and scalar multiplication, has q^n elements, and is isotropic, then adjoining H extends the partial spread to a full spread.

**Proof.** Closure makes H a subspace. Its cardinality q^n forces dimension n, so isotropy makes it Lagrangian. By its definition it intersects every old member only at zero. Every ambient nonzero vector is either already covered or lies in H. Thus the enlarged family is a spread. All tests in the hypotheses are finite equations or membership checks on the supplied uncovered set; no putative extension is assumed.

**Use/dependencies.** A sufficient extension certificate with an explicit output. It makes no claim that arbitrary uncovered sets pass these tests.

<a id="b009"></a>

### B009 — A clique certificate that constructs a symplectic spread [proved]

**Statement.** Let A be a set of q^n symmetric n-by-n matrices over F_q such that A−B is invertible whenever A≠B. Their graphs together with L_∞ form a symplectic spread.

**Proof.** B006 makes every graph Lagrangian and shows that distinct graphs intersect only at zero. Each graph is transverse to L_∞. Each of the q^n+1 subspaces contains q^n−1 nonzero vectors, so their disjoint union contains (q^n+1)(q^n−1)=q^(2n)−1 vectors, exactly the ambient nonzero count. There are therefore no holes. Equivalently one may search a finite graph whose vertices are symmetric matrices and whose edges mean invertible difference; a clique of the stated size supplies the actual spread.

**Use/dependencies.** Direct constructive algebra-to-geometry certificate; B006 and counting, later B070.

<a id="b010"></a>

### B010 — Every isotropic subspace has a constructive Lagrangian extension [proved]

**Statement.** If U is isotropic in a nondegenerate 2n-dimensional alternating space, then U is contained in a Lagrangian. One can construct it by at most n−dim U single-vector extensions.

**Proof.** If dim U=k<n, nondegeneracy gives dim U⊥=2n−k>k. Select v∈U⊥\U by solving the linear equations defining U⊥ and extending a basis of U. The span U+F_qv is isotropic: old pairs are orthogonal, v is orthogonal to U, and ω(v,v)=0. Its dimension increases by one. Repeat until dimension n, when isotropy is maximal. The argument works in characteristic two because the form is alternating, not merely skew-symmetric. The zero-dimensional ambient case is immediate.

**Use/dependencies.** An unconditional constructive extension theorem for one isotropic subspace, distinct from extending a whole partial spread.

## 2. Design matrices and spectral construction tools

<a id="b011"></a>

### B011 — The incidence operator of a 2-design [proved]

**Statement.** Let a finite incidence structure have v points, b blocks of size k, each point in r blocks, and each distinct pair of points in λ blocks. Its incidence matrix N satisfies NN*=(r−λ)I+λJ, vr=bk, and r(k−1)=λ(v−1).

**Proof.** The matrix product counts common incident blocks, giving the diagonal r and off-diagonal λ. Count point-block incident pairs in two ways to get vr=bk. Fix a point and count pairs consisting of a block through it and a different point in that block. Counting by blocks gives r(k−1); counting by the other point gives λ(v−1). These arguments allow repeated blocks if b counts their indices consistently.

**Use/dependencies.** Computes spectra, embeddings and rank exactly from actual incidence hypotheses; B012–B014.

<a id="b012"></a>

### B012 — A symmetric design supplies a regular simplex [proved]

**Statement.** Suppose B011 is symmetric, b=v and r=k, with 0<k<v. Center each row of N by subtracting (k/v)1. After normalization, the v resulting real vectors have pairwise inner product −1/(v−1) and span a (v−1)-dimensional space.

**Proof.** The centered Gram matrix is (k−λ)I+(λ−k²/v)J. The parameter equation in B011 gives λ−k²/v=−(k−λ)/v. Since k−λ=k(v−k)/(v−1)>0, this Gram matrix is (k−λ)(I−J/v), positive of rank v−1. Its diagonal is (k−λ)(v−1)/v and its off-diagonal is −(k−λ)/v. Dividing by the common diagonal yields the asserted inner products. Factorization of this Gram matrix also supplies the simplex even if an incidence embedding is not retained.

**Use/dependencies.** Explicit spherical configurations and exact Gram certificates; B011.

<a id="b013"></a>

### B013 — Fisher's inequality with an explicit reconstruction map [proved]

**Statement.** Under B011, if r>λ≥0, then b≥v and the map N*:R^v→R^b is injective. Data y=N*x reconstruct x by x=((r−λ)I+λJ)^−1Ny.

**Proof.** For nonzero x, xᵀNN*x=(r−λ)||x||²+λ|∑x_i|²>0, so NN* is invertible and N* has trivial kernel. Its codomain therefore has dimension at least v. Multiplying y=N*x by N and then by (NN*)^−1 proves reconstruction. On 1⊥ the inverse is division by r−λ, and on span{1} it is division by r+(v−1)λ, so the formula has no hidden singular boundary case.

**Use/dependencies.** A rank bound coupled to a sufficient recovery procedure, rather than a standalone obstruction.

<a id="b014"></a>

### B014 — Resolutions produce orthogonal contrast spaces [proved]

**Statement.** Let v=sk points be partitioned into s blocks of size k in each of t parallel classes. Assume blocks from different classes meet in k/s points. The centered indicators u_B=1_B−1/s·1 span mutually orthogonal (s−1)-dimensional spaces D_a. Within one class ∑_B u_Bu_B*=kΠ_(D_a). If t(s−1)=v−1, all centered indicators form a k-tight frame for 1⊥.

**Proof.** Within a class, ⟨u_B,u_C⟩=kδ_BC−k/s. Thus the Gram matrix is k(I−J/s), of rank s−1 and with all nonzero eigenvalues k; this proves the projection identity. Across classes the assumed intersection gives inner product k/s−k/s=0. Every u_B lies in 1⊥, whose dimension is v−1. If the dimensions sum to v−1, their orthogonal sum is exactly 1⊥; summing the projection identities gives kI there. The intersection assumption implicitly requires k/s to be an integer.

**Use/dependencies.** An explicit real tight-frame construction from resolved designs; applies to B001 with s=k=q.

<a id="b015"></a>

### B015 — Nets and flat matrices construct MUBs [proved; classical reconstruction]

**Statement.** Suppose s² points admit t parallel classes, each partitioning them into s blocks of size s, with any blocks from different classes intersecting once. If H is an s-by-s unitary matrix all of whose entries have modulus 1/√s, then these data construct t MUBs in C^(s²).

**Proof.** For each block choose a bijection with {1,…,s} and embed every column of H into that block, putting zero outside it. In one class different blocks have disjoint supports, and within a block the embedded columns are orthonormal; its s² vectors form a basis. Vectors from different classes overlap at exactly one coordinate. The product of their two nonzero entries there has modulus 1/s, hence squared modulus 1/s². This proves unbiasedness independently of the chosen block orderings. The flat unitary H always exists over C as the discrete Fourier matrix, proved in B061.

**Use/dependencies.** Constructive design-to-Hilbert-space bridge; no unproved MUB completion is used.

<a id="b016"></a>

### B016 — Orthogonal Latin squares give the net input explicitly [proved]

**Statement.** A family of m pairwise orthogonal Latin squares of order s gives m+2 classes satisfying B015, hence m+2 MUBs in C^(s²). Over F_q, the q−1 squares L_a(x,y)=ax+y for a≠0 give q+1 such bases.

**Proof.** Use the s² cells as points. Rows and columns give two classes; the cells containing each symbol of a Latin square give another partition into s blocks. Latinness means every symbol block meets each row and column once. Orthogonality means a symbol block from one square meets a symbol block from another once. Thus B015 applies. For the finite-field examples, a≠0 ensures each row and column of L_a is a permutation. If a≠a', the simultaneous equations ax+y=b and a'x+y=b' have a unique solution, proving orthogonality. The construction is explicit for every q, though it need not give the maximum possible number of bases in dimension q².

**Use/dependencies.** B001 and B015; a sufficient combinatorial input with a finite verification rule.

<a id="b017"></a>

### B017 — Laplacian energy reconstructs connected components [proved]

**Statement.** For a finite undirected simple graph with adjacency A and degree matrix D, L=D−A is positive semidefinite, and ker L consists exactly of functions constant on each connected component. Hence its nullity equals the number of components.

**Proof.** Expanding yields x*Lx=∑_{edges {i,j}}|x_i−x_j|². This proves positivity. If Lx=0, its energy is zero, so x_i=x_j on every edge and hence along every path. Conversely any componentwise constant function has zero coordinatewise Laplacian. Component indicators are linearly independent and span exactly these functions. Thus spectral nullspace computations give the actual component partition by grouping vertices on which all nullspace functions agree.

**Use/dependencies.** Incidence/spectral search decomposition and certificate reduction.

<a id="b018"></a>

### B018 — A spectral gap is a quantitative averaging criterion [proved]

**Statement.** If a connected graph has smallest positive Laplacian eigenvalue γ>0, then for every vector x, ||x−mean(x)1||²≤γ^−1∑_{edges}|x_i−x_j|². Replacing x by its mean is therefore a certified approximate solution of all equality constraints along edges.

**Proof.** Subtracting the mean puts x in 1⊥, the direct sum of the positive eigenspaces of L by B017. Spectral decomposition there gives x*Lx≥γ||x||². Constants do not change any edge difference, so the inequality follows for the original vector. Equality occurs exactly when its centered part belongs to the γ-eigenspace. This gives an explicit repair map and a norm bound, including the constant-vector case with zero error.

**Use/dependencies.** Robust matching of repeated labels and synchronization constraints; B017.

<a id="b019"></a>

### B019 — Expander mixing from a directly checkable spectrum [proved]

**Statement.** In a k-regular graph on n≥1 vertices, assume ||A|_(1⊥)||≤λ. For vertex sets S,T, let e(S,T)=1_SᵀA1_T, counting oriented incidences. Then |e(S,T)−k|S||T|/n|≤λ√(|S|(1−|S|/n)|T|(1−|T|/n)).

**Proof.** Write 1_S=(|S|/n)1+s and 1_T=(|T|/n)1+t with s,t perpendicular to 1. Since A1=k1, the two mixed terms vanish. The remaining discrepancy is sᵀAt, bounded by λ||s||||t||. Directly expanding the centered indicator norms gives the displayed factors. The formula covers empty and full sets, for which the discrepancy and the appropriate factor are zero.

**Use/dependencies.** Certifies the existence of an incidence between two candidate sets whenever its predicted main term exceeds the error bound.

<a id="b020"></a>

### B020 — A dense compatibility graph contains a constructive clique [proved]

**Statement.** Let r≥2 and let a simple graph on N vertices have minimum degree δ>N(1−1/(r−1)). Then it contains a clique of size r, obtainable by successive common-neighbor choices.

**Proof.** After selecting a clique of t≤r−1 vertices, a vertex fails to be a common neighbor only if it belongs to one of their sets of nonneighbors, each of size at most N−δ; these sets include the selected vertex itself. The common-neighbor set therefore has size at least N−t(N−δ)>0. Choose a member, which is automatically new, and continue to t=r. For r=2 the hypothesis is δ>0 and the same argument chooses an edge. This is a sufficient criterion, not an assertion that the degree threshold is necessary.

**Use/dependencies.** Converts certified compatibility degrees into actual collections of mutually compatible geometric objects; B071 and B075.

## 3. Finite frames as explicit linear reconstruction devices

<a id="b021"></a>

### B021 — Synthesis and Gram operators have the same positive spectrum [proved]

**Statement.** For a d-by-N complex matrix F with columns f_i, put S=FF* and G=F*F. Their positive eigenvalues, with multiplicity, agree. In particular span{f_i}=C^d exactly when S is positive definite.

**Proof.** If Gv=λv with λ>0, then Fv≠0 because ||Fv||²=λ||v||²; moreover S(Fv)=λFv. Conversely, from Sw=λw we obtain the nonzero vector F*w in the λ-eigenspace of G. The maps F and λ^−1F* are inverse on the corresponding eigenspaces, proving multiplicity equality. Finally ker S=ker F*, since ⟨x,Sx⟩=||F*x||²; this kernel is the orthogonal complement of the column span.

**Use/dependencies.** Exact spectral certificates can be checked in whichever matrix dimension is smaller.

<a id="b022"></a>

### B022 — Canonical duals reconstruct and control measurement noise [proved]

**Statement.** If S=∑f_if_i* satisfies S≥aI with a>0, set g_i=S^−1f_i. Then x=∑g_i⟨f_i,x⟩. If the measured coefficients have error e∈C^N, the reconstruction error has norm at most ||e||/√a.

**Proof.** The reconstruction operator is S^−1F, and S^−1FF*=I. Its product with its adjoint is S^−1FF*S^−1=S^−1, whose largest eigenvalue is at most 1/a. Thus ||S^−1F||≤1/√a, proving the noise bound. This construction needs no selection of a square submatrix and remains valid with redundant or repeated nonzero frame vectors.

**Use/dependencies.** Stable inversion from sufficient frame lower bounds; B021.

<a id="b023"></a>

### B023 — Frame potential equality constructs tightness [proved; classical reconstruction]

**Statement.** If N≥1 and f_1,…,f_N are unit vectors in C^d, their frame potential FP=∑_{i,j}|⟨f_i,f_j⟩|² satisfies FP≥N²/d. Equality holds exactly when ∑f_if_i*=(N/d)I.

**Proof.** Cyclicity of trace gives FP=tr(S²), and tr S=N. If λ_1,…,λ_d are the nonnegative eigenvalues of S, then ∑(λ_j−N/d)²=tr(S²)−N²/d≥0. Equality means all eigenvalues are N/d, which is equivalent to the stated tightness identity by spectral decomposition. Conversely that identity gives equality. When N<d equality is impossible, since S has rank at most N; the inequality remains valid.

**Use/dependencies.** An exact scalar equality certifies a useful operator identity. This is the classical frame-potential argument, not a novelty claim.

<a id="b024"></a>

### B024 — Polar whitening is a quantitative Parseval repair [proved]

**Statement.** If S=∑f_if_i*>0, the vectors g_i=S^−1/2f_i satisfy ∑g_ig_i*=I. If ||S−I||≤ε<1, then ||S^−1/2−I||≤(1−ε)^−1/2−1.

**Proof.** Multiplication gives S^−1/2SS^−1/2=I. The spectrum of S lies in [1−ε,1+ε], and the spectral theorem makes the norm of S^−1/2−I the maximum of |t^−1/2−1| over its eigenvalues. The largest value on this interval is the displayed bound at t=1−ε. Therefore ||g_i−f_i|| is at most this factor times ||f_i||. This repairs the Parseval identity; individual column norms must be tracked separately when unit norms are also required.

**Use/dependencies.** A constructive stable normalization tool, with its exact scope stated.

<a id="b025"></a>

### B025 — Naimark complementation constructs a second tight frame [proved]

**Statement.** If F is d-by-N, FF*=I and every column has squared norm d/N, with 0<d<N, there is an (N−d)-by-N matrix H with HH*=I and H*H=I−F*F. After normalizing its columns, it is a unit-norm tight frame, and its off-diagonal Gram entries are −d/(N−d) times those of the unit-normalized F-columns.

**Proof.** The rows of F are orthonormal. Extend them to an orthonormal basis of C^N by Gram–Schmidt, and let H consist of the added rows. Orthogonality of the resulting unitary gives both identities. Each H-column has squared norm 1−d/N. For i≠j, (H*H)_ij=−(F*F)_ij. Normalizing the two column families divides these entries by (N−d)/N and d/N respectively, giving the factor −d/(N−d). Finally the normalized H synthesis operator has frame operator N/(N−d)I.

**Use/dependencies.** Explicitly transfers equiangularity and constructions between complementary dimensions.

<a id="b026"></a>

### B026 — Direct sums and tensors preserve explicit tight-frame identities [proved]

**Statement.** If frames in H_1,H_2 have tight bounds c_1,c_2, their tensor-product vectors form a c_1c_2-tight frame on H_1⊗H_2. Their disjoint direct-sum embeddings form a tight frame on H_1⊕H_2 exactly when c_1=c_2.

**Proof.** Summing rank-one tensor operators gives (∑f_if_i*)⊗(∑g_jg_j*)=c_1c_2I. For the disjoint embeddings the frame operator is c_1I_(H1)⊕c_2I_(H2). If both spaces are nonzero, this is a scalar multiple of the identity precisely when the two bounds agree. These formulas also determine the new vector norms, so normalization factors can be chosen without altering the claimed bounds silently.

**Use/dependencies.** Construction operations for frames and later tensor-product MUBs.

<a id="b027"></a>

### B027 — Irreducible unitary orbits are tight [proved; classical reconstruction]

**Statement.** Let a finite group act irreducibly and unitarily on C^d. For x≠0, the indexed orbit (U_gx)_(g∈G) is a tight frame of bound |G|||x||²/d.

**Proof.** Its frame operator S is invariant under conjugation by every U_h, because multiplication by h permutes the group indices. Each eigenspace of the Hermitian S is therefore invariant under all U_h. Irreducibility forces a single eigenspace, so S=cI. Taking traces yields cd=|G|||x||². Since x≠0, c>0, and B021 gives spanning. Repeated orbit vectors are allowed here because the family is indexed by G.

**Use/dependencies.** Produces frames from an actual finite representation and seed, with no optimization step.

<a id="b028"></a>

### B028 — Balanced seeds work for multiplicity-free representations [proved]

**Statement.** Suppose a finite group's unitary representation is the orthogonal sum of pairwise inequivalent irreducibles H_j of dimensions d_j, and d=∑d_j. A unit seed x has tight orbit precisely when ||Π_jx||²=d_j/d for every j.

**Proof.** The orbit frame operator commutes with the representation. Its diagonal block on H_j is scalar by the eigenspace argument in B027. An off-diagonal block intertwines two inequivalent irreducibles and must vanish: the kernel and image of a nonzero intertwiner are invariant, so it would be an isomorphism. The jth block trace is |G|||Π_jx||², hence its scalar is |G|||Π_jx||²/d_j. All these scalars agree exactly for the displayed balance condition. Such seeds exist explicitly by choosing any unit vector in each H_j and giving it coefficient √(d_j/d).

**Use/dependencies.** A sufficient orbit construction when irreducibility fails; multiplicities greater than one require extra matrix conditions.

<a id="b029"></a>

### B029 — A deterministic erasure budget preserves reconstruction [proved]

**Statement.** If S=∑f_if_i*≥aI and ||f_i||²≤μ, removing any r vectors leaves a frame whenever a−rμ>0. Its canonical-dual noise amplification is at most (a−rμ)^−1/2.

**Proof.** For each removed vector, f_if_i*≤||f_i||²I≤μI by Cauchy–Schwarz. The sum of r removed operators is at most rμI, so the remaining frame operator is at least (a−rμ)I. Positivity gives spanning and B022 gives the explicit reconstruction and noise bound. The sufficient budget can be conservative; no claim is made that every erasure beyond it destroys spanning.

**Use/dependencies.** Fault-tolerant geometric measurements; B022.

<a id="b030"></a>

### B030 — Weighted minimum-noise reconstruction is uniquely optimal [proved]

**Statement.** Let F be a d×N complex matrix of row rank d, where d≥1, and let Σ be a positive definite N×N Hermitian matrix. Put S=FΣ⁻¹F* and L₀=S⁻¹FΣ⁻¹. Then L₀F*=I. Every other exact linear reconstruction L, meaning LF*=I, has the covariance identity

LΣL*=S⁻¹+(L−L₀)Σ(L−L₀)*.

Consequently L₀ minimizes the reconstruction-noise covariance in positive-semidefinite order and uniquely minimizes its trace. This applies to measurements y=F*x+ε with mean-zero noise of covariance Σ.

**Proof.** Since F* is injective, x*Sx=(F*x)*Σ⁻¹(F*x)>0 for nonzero x; hence S is invertible and L₀F*=I. Set K=L−L₀. Then KF*=0 and, by adjoint, FK*=0. Thus L₀ΣK*=S⁻¹FK*=0, and its adjoint vanishes too. Also L₀ΣL₀*=S⁻¹. Expanding (L₀+K)Σ(L₀+K)* gives the identity. Its additional term is positive semidefinite, so every scalar output variance increases or stays fixed. If the trace remains equal, then tr(KΣK*)=‖KΣ¹ᐟ²‖²_F=0, which forces K=0. Finally Ly=x+Lε, so its noise covariance is exactly LΣL*, proving the statistical assertion without assuming Gaussian noise.

**Use/dependencies.** Gives an explicit sufficient optimal reconstruction for unequal or correlated measurement errors. For Σ=I it recovers the canonical dual of B022; the statement also compares every competing exact reconstruction, rather than only bounding one inverse.

## 4. Constructive tight-frame and fusion-frame completion

<a id="b031"></a>

### B031 — Spectral defects give optimal arbitrary-vector completions [proved]

**Statement.** Given S=∑f_if_i* and c>0 with c≥λ_max(S), put D=cI−S. Adding vectors whose rank-one operators sum to D completes the family to a c-tight frame. The smallest possible number of nonzero added vectors is rank D.

**Proof.** The completion equation is exactly ∑z_jz_j*=D. Spectrally decompose D=∑_{i=1}^r λ_i u_iu_i* with λ_i>0, and choose z_i=√λ_i u_i. This supplies r=rank D vectors and the desired identity. Conversely a sum of m rank-one operators has rank at most m, so any completion needs at least r nonzero vectors. If D=0, no added vector is needed. If c<λ_max(S), positivity makes any such completion impossible; the constructive theorem uses the stated sufficient inequality.

**Use/dependencies.** Explicit minimal-length completion when added norms are free.

<a id="b032"></a>

### B032 — Every Hermitian matrix has a constant-diagonal basis [proved; classical reconstruction]

**Statement.** A Hermitian operator A on C^n, n≥1, admits an orthonormal basis e_j with ⟨e_j,Ae_j⟩=tr(A)/n for every j.

**Proof.** Let μ=tr(A)/n. The smallest and largest eigenvalues bracket μ. A unit vector in the real two-plane of corresponding eigenvectors has Rayleigh quotient varying continuously between them, so choose e_1 with quotient μ; if A=μI, any vector works. The compression of A to e_1⊥ is Hermitian and has trace tr(A)−μ=(n−1)μ. Apply the same argument inductively to that compression. Inner products of its basis vectors with the compression equal those with A, completing the construction. The n=1 case is immediate. Only two-dimensional rotations and orthogonal compression are needed.

**Use/dependencies.** A constructive constant-diagonal special case of Schur–Horn; B033.

<a id="b033"></a>

### B033 — Exact equal-norm defect completion [proved]

**Statement.** Let D≥0 on C^d and let N≥1 and t>0. There exist N vectors z_j with ||z_j||²=t and ∑z_jz_j*=D exactly when tr D=Nt and rank D≤N.

**Proof.** Necessity follows from trace and rank. For sufficiency let r=rank D≤N. On C^N form A with the r positive eigenvalues of D and N−r zeros. B032 gives a unitary V for which V*AV has every diagonal equal to t. Factor D=UU* with U a d-by-r matrix of scaled eigenvectors and embed U into a d-by-N matrix W by adding zero columns. Choose the unitary on C^N so that W*W is conjugated to the constant-diagonal version of A, and put Z=WV. Then ZZ*=D and the jth column norm squared is (Z*Z)_jj=t. For t=0 the only possible family is zero and D must be zero; that boundary is excluded above explicitly.

**Use/dependencies.** A sufficient completion criterion with prescribed common norm, not an assumed gadget.

<a id="b034"></a>

### B034 — Unit-norm tight frames exist for every N≥d [proved]

**Statement.** For integers N≥d≥1, take the first d rows of the N-by-N Fourier unitary and multiply them by √(N/d). The resulting N columns are unit vectors and form an (N/d)-tight frame in C^d.

**Proof.** Distinct Fourier rows are orthonormal by the geometric-sum identity in B061. The selected rows therefore have product FF*=I_d before rescaling. Each selected column has d entries of squared modulus 1/N, so its squared norm is d/N. Rescaling gives unit columns and multiplies the frame operator by N/d. For N=d this is an orthonormal basis. The formula constructs the vectors for every allowed pair of integers.

**Use/dependencies.** A universal explicit family and a source of flat synthesis matrices.

<a id="b035"></a>

### B035 — A unit-norm frame can be completed without changing old vectors [proved]

**Statement.** Given m unit vectors in C^d with frame operator S and a proposed N≥1 extra vectors, put c=(m+N)/d. If c≥λ_max(S) and rank(cI−S)≤N, there is a c-tight unit-norm completion by exactly N additional vectors.

**Proof.** D=cI−S is positive by the first condition. Since tr S=m, tr D=dc−m=N. Apply B033 with t=1 to factor D into exactly N unit-vector operators. Adding these to S gives cI and preserves every supplied vector. The rank hypothesis is automatic if N≥d, so choosing N≥d and m+N≥dλ_max(S) is a simple unconditional sufficient budget. When D has smaller rank, B033 distributes its mass among redundant vectors rather than replacing the old family.

**Use/dependencies.** A concrete sufficient extension theorem; B033.

<a id="b036"></a>

### B036 — A two-column block spends fractional spectral mass exactly [proved]

**Statement.** For 0≤x≤2 the real unit vectors a=(√(x/2),√(1−x/2)) and b=(√(x/2),−√(1−x/2)) satisfy aaᵀ+bbᵀ=diag(x,2−x).

**Proof.** Each squared norm is x/2+1−x/2=1. Their off-diagonal rank-one entries have equal magnitude and opposite signs, so cancel. The diagonal entries add to x and 2−x. At x=0 or 2 one coordinate vanishes and the same identity holds. Thus fractional row energy can be assigned with a literal two-sparse unit-vector pair, using no nonconstructive diagonal theorem.

**Use/dependencies.** Elementary block behind spectral-tetris constructions; B037.

<a id="b037"></a>

### B037 — Spectral tetris for spectra bounded below by two [proved; classical reconstruction]

**Statement.** If λ_1,…,λ_d≥2 and N=∑λ_i is an integer, there is a real unit-norm frame with frame operator diag(λ_1,…,λ_d), each column supported on at most two coordinates.

**Proof.** Process rows in order. Spend the integer part of the current remaining row budget using copies of its coordinate unit vector. If a fractional remainder x∈(0,1) remains and another row exists, insert the pair in B036 on the current and next rows. This consumes x in the current row and 2−x<2 in the next, whose untouched budget is at least two; hence no budget becomes negative. Continue on that next row with its reduced nonnegative budget. Each step uses finitely many unit vectors and clears one row. When the last row is reached, its remaining budget is an integer because the total trace N and the number of columns already used are integers. Finish with coordinate vectors. Off-diagonal terms always cancel within a pair. Trace ensures exactly N columns.

**Use/dependencies.** Explicit sparse construction; the ≥2 assumption is used exactly when a block borrows from an untouched row. Compare the spectral-tetris primary precedent [ST].

<a id="b038"></a>

### B038 — Projection defects construct equal-rank fusion completions [proved]

**Statement.** Suppose orthogonal projections P_i and a scalar c satisfy D=cI−∑P_i≥0 and D²=D. If rank D=mk for integers m≥0,k≥1, then m rank-k orthogonal projections Q_j can be added so that ∑P_i+∑Q_j=cI.

**Proof.** Since D is a Hermitian projection, choose an orthonormal basis of its range and partition it into m groups of k vectors. Let Q_j project onto the span of the jth group. Their ranges are mutually orthogonal and their sum is D. The desired identity follows by addition. If m=0, D=0 and there is nothing to add. The test D²=D is a substantive sufficient hypothesis; an arbitrary positive defect is not silently treated as a sum of mutually orthogonal projections.

**Use/dependencies.** Constructive fusion-frame completion from an explicitly verifiable defect.

<a id="b039"></a>

### B039 — Two nontrivial projections can be tight only by complementing [proved]

**Statement.** If P is an orthogonal projection with both nonzero range and nonzero kernel, and Q is another orthogonal projection satisfying P+Q=cI, then c=1 and Q=I−P. Conversely this choice always works.

**Proof.** From Q=cI−P, the equation Q²=Q becomes (c²−c)I+(2−2c)P=0. On ker P it says c(c−1)=0; on ran P it says (c−1)(c−2)=0. The only common root is c=1. Substitution gives the complement and proves sufficiency. If P is zero or identity, the common-root argument does not apply, and those trivial boundary cases can have c=0 or 2; they were excluded explicitly.

**Use/dependencies.** An exact constructive classification for the two-subspace case, useful before applying more complicated fusion constructions.

<a id="b040"></a>

### B040 — Finite unitary orbits construct tight fusion frames [proved]

**Statement.** Let an irreducible finite unitary group act on C^d and let P have rank k with 1≤k≤d. The indexed projections U_gPU_g* sum to (|G|k/d)I.

**Proof.** Their sum is Hermitian and commutes with the whole representation by permutation of indices. The irreducible eigenspace argument of B027 therefore makes it scalar. Its trace is |G|k, determining the scalar. Every summand remains an orthogonal projection of rank k because unitary conjugation preserves both equations P*=P and P²=P. Thus the actual orbit subspaces, with repetitions indexed by the group if present, form a tight fusion frame.

**Use/dependencies.** An explicit sufficient construction for equal-rank subspace measurements; B027.

## 5. Tensor moments, projective designs, and informational completeness

<a id="b041"></a>

### B041 — The tensor-power Welch inequality with equality data [proved; classical reconstruction]

**Statement.** For N≥1 unit vectors x_1,…,x_N in C^d and integer t≥1, set D_t=binom(d+t−1,t). Then ∑_{i,j}|⟨x_i,x_j⟩|^(2t)≥N²/D_t. Equality means ∑|x_i^⊗t⟩⟨x_i^⊗t|=(N/D_t)I on Sym^t(C^d).

**Proof.** The symmetric tensor space has basis indexed by monomials of total degree t in d variables, hence dimension D_t. Each x_i^⊗t is a unit vector there, and their inner products are ⟨x_i,x_j⟩^t. Apply the trace-square proof of B023 on this space. It proves both the inequality and its equality condition, including the rank obstruction when N<D_t. No assertion about existence of equality configurations is built into this argument.

**Use/dependencies.** Converts scalar moment equality into a complete constructive operator certificate.

<a id="b042"></a>

### B042 — A finite second-moment identity defines a projective 2-design [proved]

**Statement.** A family of unit vectors with positive weights w_i summing to one is a complex projective 2-design exactly when ∑w_i P_i⊗P_i=2Π_sym/[d(d+1)], where Π_sym=(I+Swap)/2. In particular its weighted fourth-overlap potential is at least 2/[d(d+1)], with equality exactly for this identity.

**Proof.** Here the displayed moment identity is the operational definition of a projective 2-design. Put A=∑w_i|x_i^⊗2⟩⟨x_i^⊗2| on Sym², of dimension D_2=d(d+1)/2. Its trace is one. Thus tr(A²)−1/D_2=||A−I/D_2||_HS²≥0. Expanding tr(A²) gives ∑w_iw_j|⟨x_i,x_j⟩|⁴. Equality is equivalent to A=I/D_2 on Sym², and both sides vanish on its orthogonal complement, yielding the displayed identity.

**Use/dependencies.** A finite, checkable definition and equality certificate; B041; projective-design precedent [KR05].

<a id="b043"></a>

### B043 — Second-moment designs reconstruct every matrix [proved]

**Statement.** For a weighted design in B042 and any complex d-by-d matrix A,
∑w_i tr(AP_i)P_i=(A+tr(A)I)/[d(d+1)]. Consequently its rank-one projectors span the full complex matrix space.

**Proof.** Take matrix entries in the identity of B042. They state ∑w_i (P_i)_(ab)(P_i)_(cd)=(δ_abδ_cd+δ_adδ_cb)/[d(d+1)]. Multiply by A_(dc) and sum over c,d to obtain the claimed formula entrywise. The linear map on the right is invertible: on traceless matrices it is multiplication by 1/[d(d+1)], and on scalar matrices it is multiplication by 1/d. Thus every A is a linear combination of the P_i by applying the inverse to this formula.

**Use/dependencies.** Explicit informational completeness; not merely a cardinality bound.

<a id="b044"></a>

### B044 — Design measurements have a closed reconstruction formula [proved]

**Statement.** For B042, the operators E_i=dw_iP_i form a positive operator-valued measurement. If tr ρ=1 and p_i=tr(ρE_i), then ρ=(d+1)∑p_iP_i−I.

**Proof.** Partially tracing the second-moment identity gives ∑w_iP_i=I/d: the partial trace of I+Swap is (d+1)I. Hence ∑E_i=I, and each E_i is positive. By B043, ∑p_iP_i=d∑w_i tr(ρP_i)P_i=(ρ+I)/(d+1). Rearranging gives reconstruction. Positivity of ρ is needed to interpret p_i as probabilities, but the algebraic formula holds for any trace-one matrix. This separates the measurement condition from the linear recovery identity.

**Use/dependencies.** An actual finite measurement and inverse; B042–B043.

<a id="b045"></a>

### B045 — Complete MUBs give a projective 2-design [proved; classical reconstruction]

**Statement.** In dimension d≥2, the union of d+1 pairwise unbiased orthonormal bases, with uniform weight on its N=d(d+1) vectors, is a projective 2-design.

**Proof.** The unweighted fourth-overlap potential has N diagonal contributions. Distinct vectors in the same basis contribute zero. There are d(d+1) ordered pairs of distinct bases, and for each such pair the d² vector pairs each contribute 1/d². Their contribution is therefore another d(d+1)=N. The total is 2N=N²/D_2, so B041 at t=2 gives the moment identity in B042 after dividing by N. This proves the design assertion from the full MUB hypotheses and does not supply those bases in an arbitrary dimension.

**Use/dependencies.** Constructive bridge from complete MUBs to tomography; B041–B044; [KR05].

<a id="b046"></a>

### B046 — A SIC equality certificate gives a 2-design [proved; classical reconstruction]

**Statement.** If d² unit vectors in C^d have |⟨x_i,x_j⟩|²=1/(d+1) whenever i≠j, their uniform measure is a projective 2-design.

**Proof.** Their fourth potential is d²+d²(d²−1)/(d+1)²=2d³/(d+1). With N=d² this equals N²/D_2. B041 therefore gives equality on Sym² and hence B042. In particular the frame is tight and the corresponding weighted rank-one measurement reconstructs states by B044. The theorem is a sufficient certificate for a supplied configuration; existence of such configurations in every dimension is a separate conjecture, B093.

**Use/dependencies.** Exact geometry-to-measurement certificate; [KR05] supplies the classical design precedent.

<a id="b047"></a>

### B047 — SIC projectors form a minimal informationally complete simplex [proved]

**Statement.** Under B046 with d≥2, put Y_i=P_i−I/d. Their Gram matrix has diagonal (d−1)/d and off-diagonal −1/[d(d+1)]. They span the traceless Hermitian space, satisfy ∑Y_i=0, and for every Hermitian A,
A=(d+1)/d∑tr(AP_i)P_i−tr(A)I.

**Proof.** Since tr(P_iP_j)=|⟨x_i,x_j⟩|², centering gives the displayed entries. The Gram matrix is d/(d+1)(I−J/d²), of rank d²−1. This equals the dimension of the traceless Hermitian space, proving spanning and the unique linear dependence. The sum vanishes also from tightness in B046. Specialize B043 with weights 1/d² and multiply by d(d+1) to get (d+1)/d∑tr(AP_i)P_i=A+tr(A)I, then rearrange. Adding I to the traceless span proves that the d² projectors are a basis of the full Hermitian space.

**Use/dependencies.** Minimal measurement reconstruction, with all normalization constants explicit.

<a id="b048"></a>

### B048 — Approximate moment operators still give stable tomography [proved]

**Statement.** Let unit vectors and weights define T(A)=∑w_i tr(AP_i)P_i on the real Hilbert space of Hermitian matrices. If ||T−T_0||≤ε<1/[d(d+1)], where T_0(A)=(A+tr(A)I)/[d(d+1)], then T is invertible and ||T^−1||≤(1/[d(d+1)]−ε)^−1.

**Proof.** The scalar and traceless eigenspaces of T_0 have eigenvalues 1/d and 1/[d(d+1)]. For Hermitian A, ⟨A,TA⟩≥(1/[d(d+1)]−ε)||A||_HS² by the operator-norm hypothesis. Hence T has the asserted positive lower eigenvalue and is invertible. Given measurements m_i=tr(AP_i), reconstruct A=T^−1(∑w_i m_iP_i); errors in the assembled matrix on the right are amplified by at most the stated inverse norm. This is a sufficient approximate-design certificate without requiring exact design repair.

**Use/dependencies.** Stable informational completeness; B043.

<a id="b049"></a>

### B049 — Design tomography tolerates a certified erasure set [proved]

**Statement.** For an unweighted projective 2-design of N unit vectors, the centered projectors Y_i=P_i−I/d form a tight frame of bound N/[d(d+1)] on traceless Hermitian matrices. Removing r of them preserves this spanning property if N/[d(d+1)]>r(d−1)/d.

**Proof.** For traceless Hermitian A, B043 says ∑tr(AP_i)P_i=N A/[d(d+1)]. Taking its traceless part replaces P_i by Y_i, while tr(AY_i)=tr(AP_i), proving the frame identity. Every ||Y_i||_HS²=tr(P_i²)−1/d=(d−1)/d. Apply B029 in this real Hilbert space with that common squared norm. The resulting canonical dual reconstructs any traceless perturbation, and a separately known trace restores the scalar part.

**Use/dependencies.** Constructive robustness of finite projective designs; B029 and B043.

<a id="b050"></a>

### B050 — Product designs give explicit local tomography in composite dimensions [proved]

**Statement.** If designs in C^a and C^b have tomography maps T_a,T_b from B043, their product measurement has map T_a⊗T_b on matrices on C^a⊗C^b. It is invertible, so it reconstructs arbitrary entangled states as well as product states.

**Proof.** On a simple matrix tensor A⊗B, each product projector has expectation tr(AP_i)tr(BQ_j), and summing the weighted projector outputs gives T_a(A)⊗T_b(B). Simple tensors of matrix units span the full matrix space, so this determines the whole map. Since T_a and T_b are invertible by B043, its inverse is T_a^−1⊗T_b^−1. Explicitly T_a^−1(C)=a(a+1)C−a tr(C)I_a, and similarly for b; apply these maps to the respective tensor factors. Global second-design equality is not required for this sufficient recovery construction.

**Use/dependencies.** A composite-dimensional constructive application even when maximal MUB existence is unknown.

## 6. MUB operator geometry and sufficient missing-basis certificates

<a id="b051"></a>

### B051 — Unbiased bases are orthogonal diagonal contrast spaces [proved]

**Statement.** For an orthonormal basis B=(b_i), set Q_i=P_(b_i)−I/d and let D_B be their real span. Then dim D_B=d−1 and tr(Q_iQ_j)=δ_ij−1/d. Two bases B,C are unbiased exactly when D_B and D_C are Hilbert–Schmidt orthogonal.

**Proof.** Orthogonality of B gives tr(P_iP_j)=δ_ij, and expanding the centered products proves the Gram formula. Its kernel is the all-ones line, so its rank is d−1. Across two bases the centered inner product is |⟨b_i,c_j⟩|²−1/d. All such entries vanish exactly for unbiasedness, and this is equivalent to orthogonality of the spans. This identifies unbiasedness with a concrete operator-space orthogonality condition, rather than just an overlap table.

**Use/dependencies.** The basic geometric bridge for B052–B060; local precedent `MUBResidualProjection.lean`.

<a id="b052"></a>

### B052 — The complex MUB bound follows with its equality decomposition [proved]

**Statement.** For d≥2, k pairwise unbiased bases have k≤d+1. If k=d+1, their spaces D_B are an orthogonal direct-sum decomposition of all traceless Hermitian matrices.

**Proof.** That ambient real space has dimension d²−1: a Hermitian matrix has d real diagonal parameters and d(d−1) real off-diagonal parameters, and trace zero imposes one real equation. By B051 the k subspaces are mutually orthogonal of dimension d−1. Thus k(d−1)≤d²−1, and division by d−1 gives the bound. At equality their sum has the full dimension, proving the decomposition. Dimension one is deliberately excluded: all basis overlaps there have modulus one and the counting convention needs separate treatment.

**Use/dependencies.** An upper bound paired with the constructive equality structure used in tomography; classical [WF, BB01].

<a id="b053"></a>

### B053 — Real unbiasedness has a different equality space [proved]

**Statement.** For d≥2, k pairwise unbiased real orthonormal bases satisfy k≤d/2+1. Equality gives an orthogonal decomposition of traceless real symmetric matrices by their diagonal contrast spaces.

**Proof.** The projector calculation in B051 stays inside real symmetric matrices. Their traceless subspace has dimension d(d+1)/2−1=(d−1)(d+2)/2. Orthogonality of k spaces of dimension d−1 gives k≤(d+2)/2. Equality of dimensions again gives the direct sum. Thus the bound for real vectors is not obtained by replacing complex parameters silently: the ambient operator space is genuinely smaller. The same argument supplies its exact equality decomposition.

**Use/dependencies.** Real-frame design targets and dimensional boundary checks; compare [RealMUB].

<a id="b054"></a>

### B054 — Collision probabilities obey an exact Bessel budget [proved]

**Statement.** If B_a are k MUBs and ρ is Hermitian of trace one, put p_ai=tr(ρP_ai). Then ∑_(a,i)(p_ai−1/d)²≤tr(ρ²)−1/d. Equality holds when ρ−I/d lies in ⊕_a D_(B_a).

**Proof.** For traceless A=ρ−I/d, the orthogonal projection onto D_B is ∑_i tr(AP_i)P_i. It is traceless because the coefficients sum to tr A=0. Its squared norm is ∑_i tr(AP_i)² because the P_i are orthonormal in Hilbert–Schmidt space. The D_B are orthogonal by B051, so the sum of these squared projection norms is at most ||A||_HS²=tr(ρ²)−1/d. The equality condition is precisely membership in their orthogonal sum. Positivity of ρ is optional for the algebra but makes the p_ai probabilities.

**Use/dependencies.** Quantitative information recovered by an incomplete MUB collection.

<a id="b055"></a>

### B055 — Complete MUBs reconstruct trace-one matrices [proved]

**Statement.** If d+1 MUBs are supplied and p_ai=tr(ρP_ai) for tr ρ=1, then ρ=∑_(a,i)p_aiP_ai−I.

**Proof.** First let ρ be Hermitian. By B052, A=ρ−I/d is the sum of its orthogonal projections onto the D_(B_a). Each projection is ∑_i(p_ai−1/d)P_ai by the proof of B054. Summing gives A=∑p_aiP_ai−(d+1)I/d. Add I/d and simplify. This agrees with B044 after noting that the uniform-union POVM has E_ai=P_ai/(d+1). The proof thus verifies the normalization by two independent routes. For an arbitrary complex trace-one ρ, decompose it into its Hermitian and i-times-Hermitian parts and extend the same projection identity by complex linearity; the formula follows unchanged.

**Use/dependencies.** An explicit inverse measurement map, conditional on the actual complete family; B051–B054.

<a id="b056"></a>

### B056 — The residual operator is an explicit orthogonal projection [proved]

**Statement.** For k MUBs define, on Hermitian A,
R(A)=A−tr(A)I/d−∑_a[∑_i tr(AP_ai)P_ai−tr(A)I/d].
Then R projects orthogonally onto the traceless space perpendicular to every D_(B_a), of dimension d²−1−k(d−1).

**Proof.** The first two terms project onto traceless matrices. The bracket is the orthogonal projection onto D_(B_a), as in B054, and vanishes on scalar matrices. These projections have pairwise orthogonal ranges by B051. Subtracting their sum from the traceless projection is consequently a self-adjoint idempotent whose range is the indicated common orthogonal complement. Subtracting the dimensions of the orthogonal ranges gives the formula. This proves an operator identity on arbitrary Hermitian input, not existence of rank-one elements in its range.

**Use/dependencies.** An executable source of candidate residual matrices; local precedent `MUBResidualProjection.lean`.

<a id="b057"></a>

### B057 — A rank-one residual witness gives an actual unbiased vector [proved]

**Statement.** A unit vector x is unbiased to every supplied basis B_a exactly when P_x−I/d belongs to ran R from B056. Equivalently, a positive semidefinite trace-one matrix P with tr(P²)=1 and P−I/d∈ran R constructs such a vector by taking its nonzero eigenvector.

**Proof.** B051 gives tr((P_x−I/d)(P_ai−I/d))=|⟨x,b_ai⟩|²−1/d, proving the first equivalence. For the second, the nonnegative eigenvalues λ_j of P sum to one, so each is at most one. The equality ∑λ_j²=∑λ_j forces λ_j(1−λ_j)=0 for every j. Exactly one eigenvalue is one, all others zero; hence P=P_x for a unit eigenvector. Positivity is essential to this spectral argument and is explicitly part of the certificate.

**Use/dependencies.** A sufficient construction of a vector, while preserving the distinction between one vector and a complete new basis.

<a id="b058"></a>

### B058 — Commuting residual matrices suffice to construct a missing basis [proved]

**Statement.** If ran R contains d−1 real-linearly independent, pairwise commuting Hermitian matrices K_1,…,K_(d−1), then the supplied MUB family extends by one orthonormal basis.

**Proof.** Simultaneously diagonalize the K_i. This follows by diagonalizing K_1 and restricting the others to its invariant eigenspaces, repeating until all commute diagonally. Since the K_i are traceless and independent, their span together with I has dimension d. It lies in the d-dimensional diagonal algebra in that common basis, and therefore equals it. Every rank-one projector P_j of the common basis belongs to this span. For an old basis vector v, residual orthogonality says ⟨v,K_iv⟩=tr(K_i)/d=0, and the same equality holds for I. By linearity it holds for each P_j, whose trace is one. Thus |⟨v,e_j⟩|²=1/d for every old v, proving the new basis is unbiased.

**Use/dependencies.** A concrete sufficient extension theorem. Local precedent is `six_MUBs_residual_commuting_suffices`; its residual/commutation/independence hypotheses are retained here.

<a id="b059"></a>

### B059 — A simple-spectrum matrix yields a smaller extension certificate [proved]

**Statement.** Suppose a Hermitian H has d distinct eigenvalues and H^m−tr(H^m)I/d∈ran R for every m=1,…,d−1. Then its eigenbasis extends the supplied MUB family.

**Proof.** The rank-one spectral projector for eigenvalue λ_j is the polynomial P_j=∏_(l≠j)(H−λ_lI)/(λ_j−λ_l), of degree d−1; denominators are nonzero by the simple-spectrum hypothesis. For any old basis vector v, the residual moment equations and ||v||=1 give ⟨v,H^mv⟩=tr(H^m)/d for m=0,…,d−1. Apply the same linear identity to the polynomial P_j. Since tr P_j=1, it gives |⟨v,e_j⟩|²=1/d. This explicitly constructs the new basis by ordinary spectral decomposition.

**Use/dependencies.** A single-matrix sufficient certificate using finitely many exact polynomial moment tests; no genericity assumption is substituted for simple spectrum.

<a id="b060"></a>

### B060 — A Hermitian channel supplies a constructive commuting certificate [proved]

**Statement.** Let Hermitian K_1,…,K_d be real-linearly independent, with ∑K_i²=I and Φ(K_j)=K_j for Φ(X)=∑K_iXK_i. If every old basis vector v satisfies ⟨v,K_iv⟩=tr(K_i)/d, then a common eigenbasis of the K_i is unbiased to every old basis.

**Proof.** For Hermitian X, expansion and cyclicity give ∑||K_iX−XK_i||_HS²=2tr(X²)−2tr(XΦ(X)); the two positive terms use ∑K_i²=I. Set X=K_j and use Φ(K_j)=K_j. The sum is zero, so every commutator vanishes. Simultaneous diagonalization follows as in B058. The d independent Hermitian matrices then span the full d-dimensional real space of diagonal Hermitian matrices; every spectral rank-one projector is their real linear combination. The supplied trace equations extend to that projector and give expectation 1/d. Thus the actual common eigenbasis is the required output.

**Use/dependencies.** A finite sufficient channel certificate, following the explicitly conditional local declarations `channel_reconstruct_unbiased_basis` and `six_MUBs_channel_certificate_suffices`. It does not assume the existence of suitable K_i.

## 7. Explicit character, Gauss-sum, and Weyl constructions

<a id="b061"></a>

### B061 — Finite Fourier matrices are unitary [proved]

**Statement.** For G=∏_(j=1)^r Z/n_jZ with n_j≥1, the functions χ_a(x)=exp(2πi∑a_jx_j/n_j), normalized by |G|^−1/2, form an orthonormal basis of C^G. In particular a flat unitary exists in every positive integer dimension.

**Proof.** The inner product of two characters factors into geometric sums. For a cyclic coordinate, ∑_(x=0)^(n−1)exp(2πikx/n) equals n when k≡0 mod n, and otherwise is zero because multiplying the sum by exp(2πik/n) leaves it unchanged with a multiplier different from one. The product therefore equals |G| for equal character indices and zero otherwise. There are |G| functions, so they form a basis. Taking G=Z/NZ proves the final assertion, including N=1.

**Use/dependencies.** Flat matrices for B015 and B034, with their orthogonality proved rather than assumed.

<a id="b062"></a>

### B062 — The odd-prime quadratic Gauss magnitude [proved; classical reconstruction]

**Statement.** If p is odd prime, ζ=exp(2πi/p), a≠0 in F_p, and b∈F_p, then |∑_x ζ^(ax²+bx)|²=p.

**Proof.** Multiply the sum by its conjugate and substitute u=x−y, v=x+y. Since 2 is invertible, this substitution is a bijection of F_p². The squared magnitude becomes ∑_u ζ^(bu)∑_v ζ^(auv). For u=0 the inner sum is p. For u≠0, au≠0 and the geometric-sum calculation in B061 gives zero. The outer sum is therefore p. This argument establishes the magnitude needed for unbiasedness without choosing a sign for a square root or a phase of the Gauss sum.

**Use/dependencies.** Exact construction input; odd characteristic is essential to this particular substitution.

<a id="b063"></a>

### B063 — Chirps construct p+1 MUBs for every odd prime [proved; classical reconstruction]

**Statement.** In C^(F_p), let c_b^a(x)=p^−1/2ζ^(ax²+bx), for a,b∈F_p. For each a, the p vectors c_b^a form a basis. These p bases and the coordinate basis are p+1 MUBs.

**Proof.** At a fixed a, inner products cancel the quadratic terms and reduce to p^−1∑_xζ^((b'−b)x), equal to δ_bb' by B061. Between a≠a', the overlap is a quadratic Gauss sum divided by p, so its squared magnitude is 1/p by B062. Every coordinate of every c_b^a already has squared modulus 1/p, establishing unbiasedness to the coordinate basis. This proves every pair condition and supplies all vectors explicitly.

**Use/dependencies.** A complete odd-prime construction, following the Ivanović/Wootters–Fields family; [WF, KR03].

<a id="b064"></a>

### B064 — Trace characters extend the Gauss magnitude to odd prime powers [proved]

**Statement.** Let E=F_(p^r) with p odd, q=|E|, and ψ(x)=exp(2πiTr(x)/p). For a≠0, |∑_(x∈E)ψ(ax²+bx)|²=q.

**Proof.** The trace character is nontrivial by the nonzero trace argument in B007. For any c≠0, multiplication by c permutes E, and ∑_xψ(cx)=0: translate by an element z with ψ(cz)≠1 to see that the sum equals itself times a scalar different from one. Now use u=x−y, v=x+y as in B062; 2 is invertible in E. The inner sum over v vanishes unless u=0 and is q then. The result is q. This proof works for every r≥1 and does not assume that the field's additive group is cyclic.

**Use/dependencies.** A fully stated finite-field Gauss-sum bridge; B007.

<a id="b065"></a>

### B065 — Complete MUBs in every odd prime-power dimension [proved; classical reconstruction]

**Statement.** With E and ψ as in B064, the q vectors q^−1/2ψ(ax²+bx), indexed by b∈E, form a basis for each a∈E. Together with the coordinate basis these give q+1 MUBs in C^q.

**Proof.** Within a basis, the inner product is the additive-character sum of (b'−b)x, divided by q. Character orthogonality from B064 makes it δ_bb'. Between different a, B064 gives squared overlap 1/q. Coordinate overlaps also equal 1/q because each component is unimodular before normalization. These statements exhaust every pair of distinct bases. The construction is explicit once a multiplication table and trace for E have been supplied.

**Use/dependencies.** Complete odd prime-power construction; [WF, KR03]. This addresses a cyclotomic/Gauss-sum bridge that some local combinatorial modules explicitly leave unproved.

<a id="b066"></a>

### B066 — The qubit three-basis seed [proved]

**Statement.** In C² the coordinate basis, {(1,1)/√2,(1,−1)/√2}, and {(1,i)/√2,(1,−i)/√2} are pairwise unbiased.

**Proof.** Each listed pair consists of unit vectors with zero inner product. Their coordinate entries have squared modulus 1/2. Across the latter two bases, the inner products have form (1±i)/2 or their conjugates, whose squared modulus is (1+1)/4=1/2. This verifies all cross pairs. The three bases attain the complex upper bound B052 at d=2. The use of complex entries is necessary here: the real bound B053 allows at most two real unbiased bases in dimension two.

**Use/dependencies.** An actual small-dimensional seed, not a symbolic existence assumption.

<a id="b067"></a>

### B067 — Tensor products preserve the supplied number of MUBs [proved]

**Statement.** If H_1 and H_2 have t_1 and t_2 MUBs, then H_1⊗H_2 has at least min(t_1,t_2) MUBs. In particular B063 and B066 construct three MUBs in C^6.

**Proof.** Pair the first t=min(t_1,t_2) bases in the two spaces. Tensor products within each paired basis are orthonormal and their number equals the product dimension. Between two different paired bases, squared overlaps multiply, giving (1/d_1)(1/d_2)=1/(d_1d_2). Thus all t product bases are unbiased. For dimensions two and three, the supplied counts are three and four, giving three in dimension six. This construction makes no claim that a fourth basis exists or that every possible basis is a product basis.

**Use/dependencies.** Unconditional composite-dimensional lower bounds from actual factors; B026, B063, B066.

<a id="b068"></a>

### B068 — Weyl matrices give an orthogonal unitary operator basis [proved]

**Statement.** For E=F_(p^r), let X_a e_x=e_(x+a), Z_b e_x=ψ(bx)e_x, and W_(a,b)=X_aZ_b on C^E. The q² W_(a,b) are unitary and satisfy tr(W_u*W_v)=qδ_uv. Their commutator scalar is ψ(bc−da) for u=(a,b), v=(c,d).

**Proof.** X permutes coordinates and Z is diagonal with modulus-one entries, so both are unitary. Direct application to e_x yields W_(a,b)W_(c,d)=ψ(bc)W_(a+c,b+d); comparing the reverse product gives the commutator scalar. If a≠0, W_(a,b) has no diagonal entries. If a=0 and b≠0, its trace is the zero character sum from B064, whose character argument also works when p=2. The identity has trace q. Applying this trace rule to W_u*W_v gives the orthogonality formula. There are q² matrices, so they form a basis of the q²-dimensional matrix space.

**Use/dependencies.** Exact finite operator labels for stabilizer-type constructions; [BB01].

<a id="b069"></a>

### B069 — Disjoint isotropic Weyl classes construct unbiased bases [proved]

**Statement.** Let L,M be r-dimensional F_p-isotropic subspaces of E² for the trace symplectic form, with L∩M={0}. Common eigenbases of {W_l:l∈L} and {W_m:m∈M} are unbiased.

**Proof.** The commutator rule in B068 makes each family commute. Commuting normal matrices admit a common orthonormal eigenbasis: diagonalize one and restrict the others to its invariant eigenspaces, iterating. The q Weyl matrices of one class are linearly independent by B068, so their span is the full q-dimensional algebra of diagonal matrices in that common basis. Its traceless diagonal subspace is the span of its nonidentity Weyl matrices. Disjointness of L and M and B068 make the two such traceless spans orthogonal. Their Hermitian parts are exactly the spaces D_B of B051, which therefore proves unbiasedness. This argument requires no division by two and includes characteristic two.

**Use/dependencies.** An explicit sufficient linear-algebraic bridge from finite symplectic geometry to Hilbert-space geometry.

<a id="b070"></a>

### B070 — A symplectic spread constructs a complete MUB family [proved; classical reconstruction]

**Statement.** Any spread of E² by r-dimensional F_p-isotropic subspaces produces q+1 MUBs in C^q. In particular B007 constructs complete MUB families in every prime-power dimension, including powers of two.

**Proof.** Each spread member has q−1 nonzero vectors. Their partition of the q²−1 nonzero vectors therefore has q+1 members. Form a common eigenbasis for each Weyl class as in B069. Any two distinct members intersect only at zero, so B069 proves every cross pair unbiased. Applying this to the explicit field-multiplication spread in B007 supplies actual finite classes and hence the promised bases. Simultaneous eigenspace computation is finite linear algebra on explicitly given matrices, not an assumed missing-basis oracle.

**Use/dependencies.** Full finite-geometry construction; [BB01, Spread]. This does not apply to dimension six, which is not a prime power.

## 8. Finite sufficient certificates for compatible bases and equiangular frames

<a id="b071"></a>

### B071 — A candidate graph can certify a missing unbiased basis [proved]

**Statement.** Let X be a finite indexed set of unit vectors already unbiased to every old basis in C^d, d≥2. Connect two distinct indices when their vectors are orthogonal. A clique of size d constructs a new unbiased basis; the degree hypothesis of B020 with r=d is a sufficient certificate that such a clique exists.

**Proof.** The clique vectors are pairwise orthogonal and unit. A set of d such vectors in dimension d is a basis. Their already verified overlaps with the old bases give the required unbiasedness. B020 constructs the clique from its stated degree bound. Repeated rays in X do not create a loophole, since unit multiples of the same vector have nonzero inner product and hence cannot both enter a clique.

**Use/dependencies.** Turns finite vector searches into a constructive extension theorem, rather than treating an individual unbiased vector as a whole basis.

<a id="b072"></a>

### B072 — Positive rank-one moment certificates construct a basis [proved]

**Statement.** Suppose d Hermitian matrices P_j are positive semidefinite, have tr P_j=tr(P_j²)=1, satisfy ∑P_j=I, and have tr(P_jP_ai)=1/d for every old basis projector. Then their nonzero eigenvectors form a new unbiased orthonormal basis.

**Proof.** The eigenvalue argument in B057 shows P_j=x_jx_j* with ||x_j||=1. Let F have these x_j as its d columns. The sum condition gives FF*=I. Since F is square, it is invertible and F*F=I as well, so its columns form an orthonormal basis. Finally the trace-overlap equations give |⟨x_j,b_ai⟩|²=1/d. Positivity cannot be omitted: Hermitian trace-one matrices may have tr(P²)=1 without being projections, for example diag(2/3,2/3,−1/3).

**Use/dependencies.** Exact semidefinite-and-polynomial sufficient extension data with explicit recovery.

<a id="b073"></a>

### B073 — Partitioned orthogonal unitaries construct MUBs [proved; classical reconstruction]

**Statement.** Suppose k classes each contain d−1 traceless, pairwise commuting unitary matrices, and together with I all the listed matrices are pairwise orthogonal for tr(U*V). Then their common eigenbases give k MUBs.

**Proof.** In each class, adjoining I gives d independent commuting normal matrices. Simultaneous diagonalization puts their d-dimensional span inside a diagonal algebra of dimension d, so it is the entire algebra. The traceless spans from different classes are orthogonal by the supplied Hilbert–Schmidt equations. Their Hermitian parts are thus orthogonal diagonal contrast spaces. B051 proves unbiasedness. Every condition involves the actual supplied matrices, and the basis output is obtained by simultaneous diagonalization as in B069.

**Use/dependencies.** Generalizes the Weyl-class construction beyond a chosen group label system; primary precedent [BB01].

<a id="b074"></a>

### B074 — Gauge normalization preserves all MUB constraints [proved]

**Statement.** A common unitary, permutations of bases and basis vectors, and independent unit-modulus phases on vectors preserve a MUB family. Any family with a chosen first basis can be normalized so that it is the coordinate basis; every other basis can then have its first row equal to the positive constant 1/√d.

**Proof.** A common unitary preserves all inner products. Permutations merely relabel them, and individual phases multiply them by modulus-one factors. To normalize, apply B_0* to all basis matrices, making the first matrix I. Every entry of the other matrices now has modulus 1/√d by unbiasedness to I. Multiply each column by the conjugate phase of its first entry. This makes the first row positive while preserving all modulus constraints and orthogonality. The construction claims a convenient representative, not a unique representative of an equivalence class.

**Use/dependencies.** A sound reduction of finite search variables; local precedent `MUBDefs20260902.MUBEquiv.isMUBFamily`.

<a id="b075"></a>

### B075 — Multipartite exclusion budgets suffice for a basis transversal [proved]

**Statement.** Let C_1,…,C_d be finite nonempty sets of unit vectors, all unbiased to the old family. Suppose for i<j every vector in C_i is nonorthogonal to at most a_ij vectors of C_j, and |C_j|>∑_(i<j)a_ij for every j≥2. Then one can choose x_j∈C_j forming a new unbiased basis.

**Proof.** Choose any x_1. At step j, the previously selected x_i exclude at most ∑_(i<j)a_ij members of C_j by the union bound. The strict inequality leaves a vector orthogonal to every previous choice. Continue to d. The selected vectors are unit and pairwise orthogonal, so are a basis; all remain unbiased to the old family by the original membership test. If the same vector occurs in several candidate sets, it is excluded after its first selection because it is not orthogonal to itself.

**Use/dependencies.** A constructive sufficient criterion using uneven candidate pools, often less demanding than the uniform graph density criterion B071.

<a id="b076"></a>

### B076 — Deleting a flat-unitary row constructs a regular simplex [proved]

**Statement.** Let H be an N-by-N unitary with entries of modulus 1/√N, N≥2. Delete one row and multiply the remaining matrix by √(N/(N−1)). Its columns are unit vectors forming a tight frame in C^(N−1), with all off-diagonal inner-product magnitudes 1/(N−1).

**Proof.** The surviving N−1 rows are orthonormal, giving frame operator N/(N−1)I after scaling. Each column loses squared norm 1/N and is then normalized. Its Gram matrix is N/(N−1)(I−h*h), where h is the deleted row. Off-diagonal entries have magnitude N/(N−1)·1/N=1/(N−1). Rephasing columns to make h constant turns the off-diagonal entries into −1/(N−1), exhibiting a regular simplex rather than just its angle set.

**Use/dependencies.** A concrete flat simplex for the block-design construction B079; B061 supplies H.

<a id="b077"></a>

### B077 — A quadratic Seidel equation is a sufficient ETF certificate [proved]

**Statement.** Let N>1 and S be Hermitian with zero diagonal, |S_ij|=1 for i≠j, and S²=(N−1)I+μS for a real μ. If ρ_-<0<ρ_+ are the two roots of t²−μt−(N−1), then G=I−S/ρ_- is the Gram matrix of a unit-norm equiangular tight frame.

**Proof.** Spectral decomposition places every eigenvalue of S among ρ_±. Both occur because tr S=0 and S≠0. The eigenvalues of G are zero on the ρ_- eigenspace and 1−ρ_+/ρ_->0 on the other. Thus G≥0. Its diagonal is one and its off-diagonal magnitudes are 1/|ρ_-|. Factor G=F*F by its positive eigenspace; the columns are unit and equiangular. If d=rank G, its sole positive eigenvalue is N/d because tr G=N, so FF*=(N/d)I by B021. This supplies the vectors from the finite matrix certificate.

**Use/dependencies.** A direct polynomial-matrix construction criterion, not an appeal to an unspecified ETF.

<a id="b078"></a>

### B078 — Symmetric conference matrices construct half-dimensional ETFs [proved]

**Statement.** If N≥2 and C is a real symmetric N-by-N matrix with zero diagonal, ±1 off-diagonal entries, and C²=(N−1)I, then N is even and I+C/√(N−1) constructs N equiangular unit vectors in R^(N/2), tight with bound two.

**Proof.** The eigenvalues of C are ±√(N−1). Its zero trace makes their multiplicities equal, hence N even. The displayed Gram matrix has eigenvalues two and zero in equal multiplicities, diagonal one, and off-diagonal magnitude 1/√(N−1). A real spectral factor gives the vectors and their tightness. This is also B077 with μ=0 and a choice of sign. The N=2 case gives two collinear unit vectors in R; distinct-line applications use N>2.

**Use/dependencies.** A finite ±1 certificate with an explicit geometric output.

<a id="b079"></a>

### B079 — Steiner designs and flat simplices construct sparse ETFs [proved; classical reconstruction]

**Statement.** A 2-(v,k,1) design with v>k≥2 has r=(v−1)/(k−1) blocks through each point and b=vr/k blocks. With a complex Hadamard matrix of order r+1, it constructs N=v(r+1) equiangular unit vectors in C^b, each supported on r coordinates, with common overlap magnitude 1/r.

**Proof.** Regard the blocks as coordinate positions. For each point, embed the r rows of an unnormalized order-(r+1) Hadamard with one row deleted into its r incident block positions, scaling by 1/√r. Its r+1 columns have norm one, and distinct columns at the same point have inner-product magnitude 1/r by the omitted-row identity. Columns belonging to different points share exactly one block coordinate, so also have overlap magnitude 1/r. Within one point's embedded family, the frame operator is (r+1)/r times the coordinate projection onto its incident blocks. Each block contains k points, so summing gives k(r+1)/r I_b=N/b I_b. This proves both equiangularity and tightness, with literal sparse vectors.

**Use/dependencies.** A constructive design-to-frame theorem; B011, B061, B076; primary precedent [Steiner].

<a id="b080"></a>

### B080 — Weighted projective designs admit finite support reduction [proved]

**Statement.** Any finite weighted projective 2-design in C^d can be replaced by one supported on a subset of at most D² of its original vectors, where D=d(d+1)/2, preserving its exact moment identity and nonnegative weights summing to one.

**Proof.** Work in the real D²-dimensional space of Hermitian operators on Sym²(C^d). Each tensor projector A_i=|x_i^⊗2⟩⟨x_i^⊗2| has trace one. If more than D² positively weighted A_i remain, there is a nonzero real dependence ∑c_iA_i=0. Taking traces gives ∑c_i=0, so some c_i>0 and some c_i<0. Set t=min_(c_i>0)w_i/c_i and replace w_i by w_i−tc_i. No weight becomes negative, at least one becomes zero, and both the moment and total weight remain unchanged. Iterate until the support bound holds. This is a finite elimination algorithm on supplied design data, with no assertion that its remaining weights are equal.

**Use/dependencies.** Constructive compression of exact moment certificates; B042.

## 9. Border completion and robust finite existence certificates

<a id="b081"></a>

### B081 — A flat codimension-one core determines all moduli [proved]

**Statement.** Let U be an n-by-n complex matrix with n≥2 and U*U=cI for c>0. If |U_ij|²=c/n whenever i,j<n, then the same equality holds for every entry.

**Proof.** The column equation makes U invertible, with inverse c^−1U*, so UU*=cI and every row also has squared norm c. In each column j<n the first n−1 entries already contribute (n−1)c/n, forcing the last entry to contribute c/n. The same row argument determines every last-column entry above the final row. The remaining corner follows from the last column's total squared norm c. Thus no phase of the missing border is guessed; its moduli follow from exact row and column budgets.

**Use/dependencies.** Core-to-border construction support; generalized independently from the local partial-Hadamard completion proof.

<a id="b082"></a>

### B082 — Partial flat orthogonal columns have a flat completion [proved]

**Statement.** Let n≥2 and A be n-by-(n−1), with A*A=nI and |A_ij|²=1 for i<n and all columns j. There is an n-by-n H with H*H=nI, all entries unimodular, and first n−1 columns exactly A.

**Proof.** Divide A by √n to obtain n−1 orthonormal vectors. Gram–Schmidt extends them by a unit vector in their one-dimensional orthogonal complement. Multiply the added vector by √n to obtain H with H*H=nI and the original columns preserved. Its top-left (n−1)-square core has squared moduli one. Apply B081 with c=n to force every remaining entry to have squared modulus one. This includes the supplied last row, whose flatness need not be postulated independently.

**Use/dependencies.** A sufficient completion theorem for actual partial data; local precedent `complete_partial_family`, with its strong input hypotheses visible.

<a id="b083"></a>

### B083 — Simultaneous border completion preserves cross unbiasedness [proved]

**Statement.** Let A_a be a finite family of matrices satisfying B082. If every entry of A_a*A_b has squared modulus n for a≠b, their individual completions H_a from B082, together with the coordinate basis after dividing each H_a by √n, form a MUB family.

**Proof.** Each completed H_a is flat and satisfies H_a*H_a=nI. For M=H_a*H_b, matrix multiplication gives M*M=H_b*(H_aH_a*)H_b=n²I. Its top-left (n−1)-square block is A_a*A_b, with the stated squared moduli n. B081 with c=n² therefore makes every entry of M have squared modulus n. Dividing both H matrices by √n makes squared overlaps 1/n. Their entrywise flatness gives the same overlaps with the coordinate basis. Any choices of the final-column phases preserve these assertions.

**Use/dependencies.** Explicit family completion preserving all supplied columns; it does not establish existence of the partial matrices themselves.

<a id="b084"></a>

### B084 — Flat border completion stays in the input conjugation field [proved]

**Statement.** Under B082, let K⊂C be a field closed under complex conjugation and containing all entries of A. A flat completion can be chosen with entries in K and with the first entry of its last column equal to one. Any two completions differ only by a phase in that column.

**Proof.** The nullspace of A* is one-dimensional. A nonzero null vector w can be obtained from signed maximal minors of A*, so w has entries in K. By B082 there is a flat last column z in this nullspace; hence w=αz for some α≠0. All entries of w therefore have the same nonzero modulus, in particular w_1≠0. The vector w/w_1 belongs to K^n, has all entries of modulus one, and is orthogonal to every supplied column; it completes A as required. Any other normalized last column lies on the same one-dimensional nullspace and has the same norm, so differs by a unit-modulus scalar.

**Use/dependencies.** An explicit cofactor construction and algebraic-field preservation. It does not assert preservation of a smaller root-of-unity alphabet.

<a id="b085"></a>

### B085 — Polar correction repairs an almost-unitary square matrix [proved]

**Statement.** If ||U*U−I||≤ε<1, then V=U(U*U)^−1/2 is unitary and ||U−V||≤1−√(1−ε)=ε/(1+√(1−ε)).

**Proof.** U*U is positive definite, with eigenvalues in [1−ε,1+ε]. Thus V*V=I; since V is square it is unitary. Writing U=V(U*U)^1/2 and using unitary invariance of the norm reduces the distance to the maximum of |√t−1| on the spectrum. The larger endpoint deviation is 1−√(1−ε). Rationalizing gives the alternative expression. Every column is therefore repaired by at most this norm bound. At ε=0, V=U.

**Use/dependencies.** An explicit approximate-basis normalization; separate unbiasedness residuals still need certification.

<a id="b086"></a>

### B086 — Overlap errors survive controlled vector repair [proved]

**Statement.** For unit x,y,x',y' with ||x−x'||≤α and ||y−y'||≤β, the squared overlap changes by at most 2(α+β). Therefore a finite table of approximate unbiasedness errors remains valid after repairs, with this explicitly added error budget per pair.

**Proof.** Insert and subtract ⟨x',y⟩ to bound |⟨x,y⟩−⟨x',y'⟩|≤α+β by Cauchy–Schwarz. Both overlap magnitudes are at most one. The identity ||a|²−|b|²|≤(|a|+|b|)|a−b| gives the result. If the original error from 1/d is η, the repaired error is at most η+2(α+β). This certifies approximate overlaps; an exact zero is obtained only when the full resulting error certificate is zero or an independent exact-existence argument applies.

**Use/dependencies.** Combines B085 with rigorous finite approximate geometry rather than mistaking numerical residuals for exact solutions.

<a id="b087"></a>

### B087 — An almost-fixed channel gives a commutator-energy bound [proved]

**Statement.** If Hermitian K_i satisfy ∑K_i²=I and Φ(X)=∑K_iXK_i, then for Hermitian X with ||Φ(X)−X||_HS≤η,
∑||[K_i,X]||_HS²≤2||X||_HSη.

**Proof.** Expand each commutator norm as in B060. Summing the two square terms gives 2tr(X²), while the mixed terms give −2tr(XΦ(X)). Thus the sum is 2⟨X,X−Φ(X)⟩_HS. Cauchy–Schwarz bounds it by 2||X||_HS||X−Φ(X)||_HS. This also shows that exact fixed points commute with every K_i. The conclusion is an explicit approximate-commutation output, not a claim that small commutators alone already supply an exact missing MUB basis.

**Use/dependencies.** A stable local version of the actual sufficient channel identity B060.

<a id="b088"></a>

### B088 — A spectral gap constructs a nearby commuting matrix [proved]

**Statement.** Let A be Hermitian with distinct eigenvalues separated by γ>0, and B Hermitian. In an eigenbasis of A, let D_A(B) retain only the diagonal entries of B. Then D_A(B) commutes with A and ||B−D_A(B)||_HS≤||[A,B]||_HS/γ.

**Proof.** In that basis the (i,j) commutator entry is (λ_i−λ_j)B_ij. Its squared Hilbert–Schmidt norm is therefore ∑_(i≠j)|λ_i−λ_j|²|B_ij|²≥γ²∑_(i≠j)|B_ij|². The final sum is exactly ||B−D_A(B)||_HS². The diagonal matrix D_A(B) is Hermitian and commutes with A. This produces the approximation by a concrete projection, and identifies the exact hypothesis preventing division by a vanishing gap.

**Use/dependencies.** A sufficient repair operation for almost-commuting residual candidates, with dimension-dependent gaps exposed.

<a id="b089"></a>

### B089 — Vandermonde conditioning quantifies the moment certificate [proved]

**Statement.** Let H have d distinct real eigenvalues λ_j and eigenvectors e_j. For a unit v, put η_m=⟨v,H^mv⟩−tr(H^m)/d, 0≤m<d, and V_mj=λ_j^m. Then the vector r_j=|⟨e_j,v⟩|²−1/d satisfies r=V^−1η, so ||r||_2≤||V^−1||·||η||_2.

**Proof.** Spectral decomposition gives η_m=∑_jλ_j^mr_j. This is precisely Vr=η; η_0=0 because v is unit. The Vandermonde matrix is invertible: the polynomials ∏_(l≠j)(t−λ_l)/(λ_j−λ_l) interpolate each coordinate evaluation and explicitly give its inverse. The norm estimate follows. Thus exact zero moments give an unbiased vector, while rigorously bounded moments give a quantitative approximate-unbiasedness statement without assuming a uniform interpolation condition number.

**Use/dependencies.** A robust version of B059, with an explicit finite conditioning diagnostic.

<a id="b090"></a>

### B090 — A contraction certificate constructs an exact geometric configuration [proved]

**Statement.** Let U_a(x) be specified complex matrix polynomials in x∈R^n. Let R_i(x) be all real and imaginary orthonormality residuals and all unbiasedness residuals d|(U_a*U_b)_jk|²−1. Supply a square polynomial system F:R^n→R^n, explicit polynomial identities R_i=∑h_ijF_j, an invertible real J, and a closed ball B(x_0,r), r>0. If sup_B||I−JF'(x)||≤θ<1 and ||JF(x_0)||≤(1−θ)r, then the ball contains x_* for which every U_a(x_*) is a member of a genuine MUB family.

**Proof.** The map T(x)=x−JF(x) is θ-Lipschitz on the convex ball by its derivative bound. For x in the ball, ||T(x)−x_0||≤||T(x)−T(x_0)||+||JF(x_0)||≤θr+(1−θ)r=r. Thus T maps the complete closed ball into itself and is a contraction; its unique fixed point satisfies JF(x_*)=0, hence F(x_*)=0 by invertibility of J. The supplied coefficient identities then force every full residual R_i to vanish, proving the matrix constraints. These are finite certificate inputs, including the identities for omitted equations; a mere numerical solution of a selected subsystem is insufficient.

**Use/dependencies.** A constructive sufficient existence criterion suitable for interval bounds and exact polynomial identity checks. No claim is made that it has been instantiated for the unresolved dimension-six problem.

## 10. Research targets and three completed construction arguments

B091–B093 are classical conjectural directions, not newly announced problems. B095, B096, B099 and B100 are precise atlas proposals; “unproved here” does not mean “nobody has proved this,” and global literature status is not established unless explicitly cited. B094 is a classical constructive theorem, while B097 and B098 are completed elementary arguments developed during atlas review without a claim of global originality. Evidence and falsifiers for conjectures remain separate from proofs.

<a id="b091"></a>

### B091 — A fourth MUB in dimension six does not exist [conjecture; classical direction]

**Statement.** Every family of pairwise unbiased orthonormal bases in C^6 has size at most three.

**Evidence and status.** B067 explicitly attains three. B052 only gives seven, so it cannot justify this stronger conjecture. The 2026 author review [MW26] treats the dimension-six problem as unresolved and distinguishes special restricted exclusions from the unrestricted question. The bounded primary-source check here is not a proof that no later resolution exists; no restricted product-basis or Fourier-family exclusion is being promoted to the displayed universal claim.

**Useful next target and falsifier.** A fourth exact basis, certified by full polynomial overlap identities, falsifies the conjecture immediately. A proposed nonexistence proof must cover arbitrary entangled vectors and all unitary gauges; excluding a chosen alphabet or ansatz is insufficient. Constructive extension certificates B058–B060 and B090 provide positive tests that could find such a falsifier.

<a id="b092"></a>

### B092 — Complete complex MUB families occur exactly in prime-power dimensions [conjecture; classical direction]

**Statement.** For an integer d≥2, there exist d+1 MUBs in C^d if and only if d is a prime power.

**Evidence and status.** The forward construction direction for prime powers is proved here in B070, including characteristic two. The proposed converse remains conjectural in this volume. [MW26] explicitly describes the existence of complete families in non-prime-power dimensions as unresolved. A finite-field construction covers one direction only; it does not show that every possible Hilbert-space construction must arise from a finite field, a spread, or a nice error basis.

**Useful next target and falsifier.** A complete family in one non-prime-power dimension falsifies the converse. Any reduction of all complete MUB families to one of the algebraic constructions in B069 or B073 would require a new representation theorem, not an unsupported universality assumption. No such theorem is supplied here.

<a id="b093"></a>

### B093 — Weyl–Heisenberg SIC construction in every dimension [conjecture; classical direction]

**Statement.** For every integer d≥2 there is a unit vector x∈C^d such that the d² rays of X^aZ^b x, with cyclic shift X, diagonal clock Z and a,b∈Z/dZ, have squared pairwise overlaps 1/(d+1).

**Evidence and status.** Such a witness would construct the design and tomography of B046–B047. In d=2, take a Bloch vector (1,1,1)/√3: its orbit under Pauli conjugations is the tetrahedron of sign vectors with product positive. Distinct vertices have dot product −1/3, so the projector overlaps (1+r·s)/2 are 1/3. The 2025 primary construction paper [SIC25] treats universal SIC existence conditionally: its all-dimensional conclusion uses the Stark conjecture and an additional special-value identity. Those assumptions are not silently discharged here.

**Useful next target and falsifier.** An exact fiducial in a new dimension is a finite positive result; a proof of nonexistence in one dimension would falsify this universal assertion. Numerical fiducials alone do neither.

<a id="b094"></a>

### B094 — Paley's quadratic-character construction gives real Hadamard matrices [proved; classical reconstruction]

**Statement.** If q is a prime power with q≡3 mod4, one can explicitly construct a real (q+1)-by-(q+1) matrix H with entries ±1 and HHᵀ=(q+1)I.

**Proof.** On F_q put χ(0)=0 and χ(x)=1 or−1 according as a nonzero x is a square or nonsquare. The squaring homomorphism has kernel {±1}, so both classes have size(q−1)/2 and χ is multiplicative. Also χ(−1)=−1: a square root of−1 would have order4, contradicting4∤q−1. For a≠0, count pairs(t,w) with w²=t(t−a). Their number is q+∑_tχ(t(t−a)). The bijection to pairs(2t−a−2w,2t−a+2w) with product a² gives exactly q−1 possibilities, so the character sum is−1. Now set C_xy=χ(x−y). Its row sums are zero, Cᵀ=−C, and CCᵀ=qI−J: diagonal entries are q−1, and off-diagonal entries are the just-proved correlation sum. Set H=[[1,1ᵀ],[−1,I+C]]. All entries are ±1. The first row is orthogonal to every other row because their sums are−1+1=0; the lower Gram block is J+(I+C)(I+C)ᵀ=(q+1)I. The first row has squared norm q+1 as well, proving the claim.

**Use/dependencies.** Explicit infinite real-flat families for B076/B079. This is Paley's classical construction, credited through [Had25], not a second statement of the all-order Hadamard conjecture or a novelty claim.

<a id="b095"></a>

### B095 — Uniqueness of a complete MUB family in complex dimension seven [conjecture; atlas proposal]

**Statement.** Every family of eight MUBs in C^7 is equivalent to B063's chirp family under a common unitary or antiunitary, basis permutations, vector permutations, and individual phases.

**Evidence and status.** B063 supplies the proposed representative. Brierley–Weigert–Bengtsson [SmallMUB] establish complete-family uniqueness in dimensions two through five; that result is evidence for a low-dimensional classification program, not a proof at seven. The status of the displayed dimension-seven assertion is not established by the bounded search in this volume, and no global novelty or open-status claim is made for it.

**Useful next target and falsifier.** An exact eight-basis configuration with a rigorously different equivalence invariant falsifies it. A proof route must classify arbitrary bases after the sound normalization B074, not merely classify Weyl-covariant or root-of-unity configurations. Even an already-known classification proof would be valuable to retrieve and integrate into the local library.

<a id="b096"></a>

### B096 — A quantitative stability exponent for the qutrit complete family [conjecture; atlas proposal]

**Statement.** For four unitary 3-by-3 matrices U_a, set Δ=∑_(a<b,i,j)(|(U_a*U_b)_ij|²−1/3)². Let dist be the square root of the sum of squared Frobenius distances to the orbit of the standard complete qutrit family under B074's equivalences. There exist constants C,ε>0 such that Δ≤ε implies dist≤CΔ^(1/4).

**Evidence and status.** Complete-family uniqueness in [SmallMUB] and compactness give a qualitative repair modulus: otherwise a sequence with Δ→0 and distances bounded below would have a convergent subsequence in U(3)^4; its limit would be a complete family outside the classified orbit, a contradiction. This proves qualitative convergence, not the stated power or a usable constant. B085–B089 supply quantitative local ingredients. The exponent and constants are unproved here; global literature status has not been established.

**Useful next target and falsifier.** A degenerating family with dist/Δ^(1/4)→∞ falsifies the exponent. A positive proof could make near-solutions into rigorous local starting points for B090 without pretending that small residuals already prove existence.

<a id="b097"></a>

### B097 — Prime-phase codimension-one Hadamard completion [proved; atlas derivation, no novelty claim]

**Statement.** If p is prime and A is a p-by-(p−1) matrix of pth roots of unity with A*A=pI, then it has a completion H with all entries pth roots of unity and H*H=pI, preserving every supplied column.

**Proof.** First establish a root-count fact. Write α=∑_(j=0)^(p−1)c_jζ^j with nonnegative integers c_j summing to p−1 and |α|=1. Put s_t=∑_j c_jc_(j+t), with cyclic indices. Then ∑_t(s_t−δ_t0)ζ^t=0. The polynomial Φ_p(X)=1+X+⋯+X^(p−1) is minimal over Q: Φ_p(X+1)=((X+1)^p−1)/X is Eisenstein at p (its nonleading coefficients are divisible by p, and its constant term is p, not divisible by p²). Thus the degree-at-most-p−1 relation implies that all p integer coefficients s_t−δ_t0 equal one integer L. Their sum is (p−1)²−1=p(p−2), so L=p−2. Hence ∑c_j²=s_0=p−1=∑c_j, forcing every c_j∈{0,1}. Exactly one root ζ^m is missing, and α=−ζ^m.

Apply B082 to obtain a flat completion, and multiply its last column by a phase to make its first entry one. For a row i≠1, row orthogonality says that its new entry z_i is the negative of the inner product of the two old length-(p−1) rows. That inner product is a sum of p−1 pth roots and has modulus one because |z_i|=1. The root-count fact therefore gives z_i∈μ_p. The first entry is already one, so the entire added column has the required alphabet. The argument includes p=2: the negative of its missing root is exactly the present root in the counting lemma.

**Use/dependencies.** A constructive strengthening of B084 from field preservation to a finite alphabet for prime orders. The proof was developed while reviewing the atlas proposal; its global originality has not been investigated. Root counts use primeness via the cyclotomic minimal polynomial and do not establish the analogous composite-alphabet claim.

<a id="b098"></a>

### B098 — Deficiency-one symplectic partial spreads always complete [proved; atlas derivation, no novelty claim]

**Statement.** Let q be a prime power and n≥1. Any q^n pairwise trivially intersecting n-dimensional isotropic subspaces in a nondegenerate2n-dimensional alternating F_q-space extend uniquely to a full symplectic spread, by adjoining the uncovered nonzero vectors together with zero.

**Proof.** Each old subspace is Lagrangian and contains q^n−1 nonzero vectors. There are therefore exactly q^n−1 uncovered nonzero vectors; call their union with zero H. Fix nonzero h∈H. No old L contains h. Since L⊥=L, the functional ω(h,−) on L is nonzero, so L∩h⊥ has dimension n−1. The covered nonzero vectors inside the hyperplane h⊥ number q^n(q^(n−1)−1). Subtracting this from q^(2n−1)−1 leaves q^n−1 uncovered vectors in h⊥, exactly the global uncovered count. Thus every vector of H is orthogonal to h. Since h was arbitrary, H is pairwise orthogonal. Its linear span is isotropic, hence has dimension at most n, but contains the q^n elements of H and therefore has dimension at least n. The span has exactly q^n elements, so equals H. Thus H is itself Lagrangian and fills all holes. Any full-spread extension must use precisely those holes, giving uniqueness.

**Use/dependencies.** An unconditional constructive completion theorem within the Lagrangian subclass, stronger than requiring the closure tests in B008 separately. It replaces an uncertain deficiency-two proposal with a proved deficiency-one result; no global novelty claim is made. B069 turns the output into an additional stabilizer-type unbiased basis.

<a id="b099"></a>

### B099 — Square-root normalized-Hilbert–Schmidt repair for three Hermitian matrices [conjecture; atlas proposal]

**Statement.** There is a universal C such that for all d and Hermitian contractions A_1,A_2,A_3, writing δ=(∑_(i<j)||[A_i,A_j]||_(2,d)²)^(1/2), one can find commuting Hermitian contractions B_1,B_2,B_3 with (∑||A_i−B_i||_(2,d)²)^(1/2)≤Cδ^(1/2). Here ||X||_(2,d)=||X||_HS/√d, and all three matrices may move.

**Evidence and status.** If A_1 has simple gap γ, B088 lets B_1=A_1 and B_j=D_(A1)(A_j), j=2,3. These diagonal contractions commute and have total error at most δ/γ, proving the conjectured scale whenever γ≥√δ. No gap is assumed in the conjecture. [HS10] supplies qualitative precedent; [HS26] proves a two-matrix 1/3 bound with the additional condition [X,X']=0 and states sharpness within that constrained problem. Neither its optimality nor an operator-norm obstruction is being misapplied to this unrestricted normalized-HS triple proposal. Global status of the exact displayed exponent is not established here.

**Useful next target and falsifier.** A dimension-growing family whose optimal repair ratio diverges would refute it. A positive result would turn approximate channel certificates such as B087 into controlled commuting candidates; exact MUB moment equations would still require separate checking.

<a id="b100"></a>

### B100 — Unweighted projective 2-designs at the MUB cardinality scale [conjecture; atlas proposal]

**Statement.** For every d≥2 there exist N≤d(d+1) pairwise distinct rank-one projectors in C^d whose uniform measure is a projective 2-design.

**Evidence and status.** For every prime power, B045 and B070 give N=d(d+1); a SIC would give d² by B046. B080 only compresses weighted designs and cannot equalize its resulting weights. Recent weighted Sidon-set constructions [Design25] and equal-weight spherical constructions of quadratic size [Sphere26] prevent a false claim that generic O(d²) design existence is the unresolved target. The proposed sharp constant-scale, unweighted, distinct-ray statement is unproved here, and its global literature status was not established by the bounded check.

**Useful next target and falsifier.** A construction at d=6 with at most 42 distinct rays would already be useful tomography data without implying a complete MUB family: no angle-set or basis-partition condition is imposed. Conversely a rigorous lower bound exceeding d(d+1) at any one dimension would refute this statement. Future searches should distinguish weighted support size, repeated indexed vectors, and distinct unweighted rays.

## Primary precedents and source-scope notes

These links identify mathematical precedents and bounded status checks. The proofs B001–B090 are self-contained reconstructions from the stated elementary background, not quotations or claims of novelty.

- **[WF]** W. K. Wootters and B. D. Fields, *Optimal state-determination by mutually unbiased measurements* (1989), [publisher DOI](https://doi.org/10.1016/0003-4916(89)90322-9). Precedent for complete prime-power MUB construction and tomography.
- **[KR03]** A. Klappenecker and M. Rötteler, *Constructions of Mutually Unbiased Bases*, [arXiv:quant-ph/0309120](https://arxiv.org/abs/quant-ph/0309120). Precedent for exponential-sum constructions; used as attribution, not as an unstated hypothesis.
- **[KR05]** A. Klappenecker and M. Rötteler, *Mutually Unbiased Bases are Complex Projective 2-Designs*, [arXiv:quant-ph/0502031](https://arxiv.org/abs/quant-ph/0502031). Precedent for the MUB/design and SIC/design connections.
- **[BB01]** S. Bandyopadhyay, P. O. Boykin, V. Roychowdhury and F. Vatan, *A new proof for the existence of mutually unbiased bases*, [arXiv:quant-ph/0103162](https://arxiv.org/abs/quant-ph/0103162). Precedent for commuting orthogonal unitaries and prime-power constructions.
- **[Spread]** K. Abdukhalikov, *Symplectic spreads, planar functions and mutually unbiased bases*, [arXiv:1306.3478](https://arxiv.org/abs/1306.3478). Geometry-to-MUB precedent; it is not cited as proof of B098.
- **[ST]** P. G. Casazza, M. Fickus, A. Heinecke, Y. Wang and Z. Zhou, *Spectral Tetris Fusion Frame Constructions*, [arXiv:1108.4061](https://arxiv.org/abs/1108.4061). Precedent for the constructive row-budget method in B036–B037.
- **[RealMUB]** P. O. Boykin, M. Sitharam, M. Tarifi and P. Wocjan, *Real Mutually Unbiased Bases*, [arXiv:quant-ph/0502024](https://arxiv.org/abs/quant-ph/0502024). Precedent for real operator-space bounds.
- **[Steiner]** M. Fickus, D. G. Mixon and J. C. Tremain, *Steiner equiangular tight frames*, [arXiv:1009.5730](https://arxiv.org/abs/1009.5730). Attribution for B079's sparse design construction.
- **[SmallMUB]** S. Brierley, S. Weigert and I. Bengtsson, *All Mutually Unbiased Bases in Dimensions Two to Five*, [arXiv:0907.4097](https://arxiv.org/abs/0907.4097). The cited complete-family classification is limited to those dimensions.
- **[MW26]** D. McNulty and S. Weigert, *Mutually Unbiased Bases in Composite Dimensions — A Review*, [arXiv:2410.23997v2](https://arxiv.org/abs/2410.23997v2), revised March 2026. Author survey used for the bounded conjecture-status check, not as a proof of nonexistence.
- **[SIC25]** M. Appleby, S. T. Flammia and G. S. Kopp, *A Constructive Approach to Zauner's Conjecture via the Stark Conjectures*, [arXiv:2501.03970v2](https://arxiv.org/abs/2501.03970v2). Its conditional inputs are preserved in B093's discussion.
- **[Had25]** M. Cati and D. V. Pasechnik, *A database of constructions of Hadamard matrices*, [arXiv:2411.18897v2](https://arxiv.org/abs/2411.18897v2). A construction database and source-status check, not an all-order proof.
- **[HS10]** L. Glebsky, *Almost commuting matrices with respect to normalized Hilbert-Schmidt norm*, [arXiv:1002.3082](https://arxiv.org/abs/1002.3082). Qualitative approximation precedent only.
- **[HS26]** M. Bansil and I. Kachkovskiy, *On almost commuting matrices with respect to the normalized Hilbert–Schmidt norm*, [arXiv:2608.31000](https://arxiv.org/abs/2608.31000). The extra pinning constraint in its two-matrix result is explicitly distinguished from B099.
- **[Design25]** J. Jasper and D. G. Mixon, *Nearly tight weighted 2-designs in complex projective spaces of every dimension*, [arXiv:2501.14938](https://arxiv.org/abs/2501.14938). Weighted constructions are distinguished from B100's uniform distinct-ray target.
- **[Sphere26]** A. Arman, A. Bondarenko, A. Prymak and D. Radchenko, *A construction of spherical 5-designs with O(d²) points*, [arXiv:2606.01376](https://arxiv.org/abs/2606.01376). Prevents mislabeling broad quadratic-order equal-weight design existence as a new open target.

The local source ledger `sources/02-sources.json` records exact file hashes, declarations inspected, the read-only canonical DAG query, and the difference between source evidence and a fresh proof audit. No Lean compilation or source edit was performed for this volume.
