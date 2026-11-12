# Tensor E8 transport: a scalable construction, its optimal center bill, and its rate obstruction

Research report, 13 October 2026. Mathematical proofs and newly written exact certificates; not a Lean certification.

## 0. Completed result and precise scope

There is an explicit family of physical Gaussian–Walsh programs with

\[
 h_n=9^n,\quad v_n=120^n,\quad r_n=8^n,\quad c_n=h_nr_n=72^n.
\]

Every center descent is paid. The copied-center cost per port is nevertheless
\(c_n/v_n=(3/5)^n\to0\). A recursively factored correction circuit and a batched non-star decoder use **linear numbers of scalar instructions, live helper arrays, and private arrays in \(v_n\)**. Both chronological dirty orientations are explicitly implemented. A three-stage orthogonal-cover assembly has

\[
 m_n=3h_n,\qquad W_n=2v_n+R_n,
 \qquad D_n=2v_n-3c_n>0.
\tag{0.1}
\]

Here \(R_n=(885v_n-1081r_n)/14\). Its complete paid child profile is given below and generated independently of the source programs. The construction yields a uniform-in-input-size exact-arithmetic RAM algorithm for the Gaussian Walsh kernel and the Walsh–Hadamard transform, with

\[
 T_n(N)=O\!\left(N(\log_2 N)^{1-\kappa_n}\right),\qquad N=2^\ell,
\tag{0.2}
\]

for each fixed architecture depth \(n\ge1\). For example, \(\kappa_2=1/25000\) is certified by a strict rational moment bound. A positive formula valid for every depth is

\[
 \kappa_n={D_n\over18W_nm_n}.
\tag{0.3}
\]

The fixed architecture's constants are enormous. This is not a practical transform implementation.

There is also a structural obstruction: in the precisely defined faithful response-channel class below, the center bill is at least \(h_nr_n\). Thus this construction attains that bill, rather than making center transport free. Moreover, the largest exponent admitted by this family's paid profile satisfies

\[
 \kappa_n^*=\Theta(9^{-n}),\qquad
 \lim_{n\to\infty}9^n\kappa_n^*={28\over2739\log 3}.
\tag{0.4}
\]

Consequently the copied-loss fraction vanishes, but the transform exponent does **not** approach a positive zero-copy benchmark. Tensor ambient-dimension growth becomes the limiting cost.

**Not claimed:** a cyclic discrete Fourier transform theorem, the original Family 130 Fourier-transfer interface, any finite-alphabet multitape integer-multiplication bound, a better exponent than P193/PR390, or global priority for tensorization, inverse-adjoint compilation, or orthogonal covers. The new contribution developed here is the specific recursively realized tensor supplier, its fully compensated physical word and prices, and the matching response-code and rate obstructions. The all-size theorem is proved for the explicit RAM model in Section 10, not imported from an assumed compiler contract.

## 1. Source audit and attribution

The supplied archive is `public-research-sources-20261011(2).zip`. The independent script `audit_sources.py` checks all **389 manifest entries** against byte count, SHA-256 and Git blob SHA-1. The archive has 393 members including its four metadata files. All these byte checks passed. They establish consistency with the supplied manifest, not independent online retrieval of every upstream blob, and do not prove mathematical assertions.

The source pins are:

| Label | Repository and immutable commit | Material used |
|---|---|---|
| P390 | `CrocSwap/integer-mult-bounds@0e790f2dfb64e17bdee154aee151bb0c1dddb28e` | selected `research/e8-prefix-restoration/` files, data and notices |
| S | `jacobalansussman/wht-power-saving-lean@f010392c923279e3dd59ef3aa5fedad23affc5fd` | supplied 313 Lean files plus Lake metadata; P193, frame and bridge material |
| P397 | `CrocSwap/integer-mult-bounds@a4e0135990efa1df734d8b9dd3af0f17cfae6f5d` | supplied 13-file packet, retained as provenance rather than an imported theorem |
| O | `openai/math@fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb` | 17 supplied integer-multiplication manuscript files; model separation |
| P401 | `CrocSwap/integer-mult-bounds@7844f72c6051a4408284c3092490687061675c1a` | separately retrieved `research/e8-response-subspaces/PROOF.md` and `frames/PROOF.md` |

The manifest declares **26 missing source artifacts**, including `lean/docs/130.md`, the two original Fourier manuscript source sets, and four PDF artifacts (one figure and three papers). Their exact paths, expected blobs and URLs are preserved in `source-audit/MISSING-SOURCES.txt` and the audit JSON. Those missing artifacts were not recovered for this work. No argument below treats their absence as a mathematical defect.

P193 is not the same local port system as the 120-port E8 word. In S, `Work/GCert/Data/Gen/P193.lean` records
\((h,v,R,N,cst)=(22,1320,9412,262944,440)\).
Its ports are paired triples in 22 binary coordinates; its 22 retained centers each cost 20. The independent arithmetic check gives

\[
 262944=9412\cdot22+2\cdot1320\cdot21+440.
\]

`Work/GCert/Data/RateB2Gp193.lean` has the five-stage list with \(W=14692,m=110,D=3080\), and explicitly warns that the correspondence to a Lean word's histogram is not proved *in that arithmetic file*. The source's sharper rate files contain the quoted P193 rate near \(7.474547\cdot10^{-4}\); this report does not rebuild their Lean dependency closure.

P390 uses the 120-port rank-eight E8 system at local dimension nine. The audit confirms that its literal port set is exactly the weight-three/complementary-pair set used here, with \(R=783,N=9039,cst=72\) and eight retained centers. Its much smaller local helper count is not inherited by our new DAG: the new core is explicitly rebuilt and pays its larger \(R_n\). Its proof retains copied-center work, applies 18 target-prefix recoveries, and two early helper restorations. Its selected global invoice has width 73, live stock 58,899, rank mass 4,289,643 and deficit 9,984. Its proof explicitly retains all-size interfaces. Our tensor circuit is not one of those 18 rewrites and does not add their savings to our invoice.

P401's two proof texts were retrieved at the requested commit, so their contents are not merely inaccessible metadata. They describe helper response-space entrance gauges and two-sided normalization of complete independently restored helper blocks. They report a 265 local rank-mass reduction and a conditional global deficit 2,496 at width 73 and live stock 14,412. These remain **source claims**, not results independently replayed here. Their finite selection data and full pipeline were not run. The root response-code obstruction in Section 3 does not contradict P401: root source-response forms and the full helper-response kernel are different spaces. Its two-sided wrapper explicitly requires more than zero response, exactly the distinction respected in Section 5.

The three-stage cover is a specialization of the inherited frame/bridge mechanism, not a new scalar identity. Relevant S files include `Work/BridgeGeom/Blocks.lean`, `Stage.lean`, `Net.lean`, `B2.lean`, `Work/SharedSumStructured/Network.lean`, and the related frame material. P390's preserved `NOTICE.md` credits the E8 local supplier, dirty-response machinery, stage constructions and their antecedents. That notice is included unchanged. No claim of worldwide novelty follows from this limited overlap audit.

## 2. Exact objects and computational model

Binary vector spaces have the standard dot product over \(\mathbb F_2\). Real/rational response coefficients are a separate scalar field. In particular, a binary port label is not a real root.

For binary dimension \(b\), an array is a function \(f:\mathbb F_2^b\to\mathbb C\). Let \(X_u f(x)=f(x+u)\). Define

\[
 C_1={1+i\over2}I+{1-i\over2}X_1,\qquad C_b=C_1^{\otimes b}.
\tag{2.1}
\]

On the character \(\chi_y(x)=(-1)^{x\cdot y}\), \(C_b\) has eigenvalue \(i^{\operatorname{wt}(y)}\). It is unitary, preserves constants and satisfies \(C_1^2=X_1\).

For a symmetric binary orthogonal projector \(P\), define the exact chart

\[
 T_P\chi_y=i^{\operatorname{wt}(Py)}\chi_y.
\tag{2.2}
\]

These charts are definitions of mathematical operators, **not primitives or oracles**. Section 6 lowers every used chart transition to a smaller \(C_r\), explicit address permutations and a translation. Chart zero is identity and chart identity is \(C_b\).

A register with formal chart \(P\) and logical value \(z\) contains the actual value \(T_Pz\). This is an invariant used to prove a physical program. Assigning a formal chart to an arbitrary initial input does not apply that chart for free: the logical input is correspondingly \(T_P^{-1}\) times the actual input, and this entrance factor remains in the final operator. Only an identically zero private array can be recharted without a physical operation.

The primitive invoice distinguishes pointwise `ADD(t,s,a)` (at most one exact complex multiplication and one addition per entry), `COPY`, `CLEAR`, recursive children, address permutations and translations. No scalar gather, decoder, old-response evaluation or cleanup is assumed as a source primitive. Arbitrary rational coefficients are allowed in the stated exact-arithmetic model; the batched construction in fact uses only the bounded base coefficients displayed below.

Private storage is not treated as an extra free transform input. It is explicitly initialized, owned, charged and eventually cleared. The serial implementation keeps no nonzero private array across a child except that child's active center. The stronger batched implementation reserves an entire center bank in the caller's private segment. A child receives its selected array and a fresh disjoint recursive workspace, so that bank cannot be touched by the child. Section 10 proves the resulting memory bound instead of assuming an inherited scratch-provider theorem.

## 3. E8 response space and a broad transport obstruction

### 3.1 The exact base matrix

Let \(T\subset\mathbb F_2^9\) consist of the 84 weight-three vectors and the 36 complements of pairs. Associate real roots in \(H=\{x\in\mathbb R^9:\sum_i x_i=0\}\):

\[
 u_S=1_S-\tfrac13\mathbf1\quad (|S|=3),\qquad
 u_{\overline{\{a,b\}}}=e_a-e_b\quad(a<b).
\]

All have squared norm two. Put

\[
 G_{ts}=\tfrac12\langle u_t,u_s\rangle,\qquad K=I-G,
\]
\[
 A_{j,s}=u_s(j),\quad
 B_{t,j}=\tfrac12(u_t(j)-u_t(8)),\qquad 0\le j<8.
\tag{3.1}
\]

Since the ninth coordinate of every root is minus the sum of the first eight, \(BA=G\). The roots span \(H\), so the rank is eight. Directly summing their coordinates gives

\[
 \sum_{t\in T}u_tu_t^T=30I-\tfrac{10}{3}\mathbf1\mathbf1^T,
 \qquad G^2=15G,
 \qquad K^2+13K-14I=0.
\tag{3.2}
\]

The diagonal of \(G\) is one. For distinct ports with binary \(t\cdot s=1\), \(G_{ts}=0\). For two triples this follows from \(2G_{ts}=|t\cap s|-1\). For a triple and a complementary pair, the real inner product is nonzero exactly when the triple contains one endpoint of the pair. For two complementary pairs, it is nonzero exactly when the distinct pairs share one endpoint. These cases also show that each row of \(K\) has exactly 56 nonzero entries, all \(\pm1/2\), and all connect binary-orthogonal ports.

The literal nonzero counts are

\[
 z_K=6720,\qquad z_A=736,\qquad z_B=456.
\tag{3.3}
\]

For example, \(z_A=84\cdot8+28\cdot2+8\). For \(B\), the triple rows contribute 336 and the complementary-pair rows contribute 120. These are checked entrywise in `verifier.py`, not imported from an E8 classification.

### 3.2 Every nonzero response has binary-full support

**Lemma 3.1.** For every nonzero binary \(w\in\mathbb F_2^9\), the roots with \(w\cdot t=1\) span the full real eight-dimensional space \(H\).

**Proof.** Write \(S=\operatorname{supp}(w)\), \(k=|S|\). If \(k\) is even, the selected pair roots are precisely the differences across the nonempty bipartition \(S,S^c\). The complete bipartite graph is connected, so its edge differences span \(H\).

If \(k=1,3,5,7\), the selected pair roots are the differences within the two parts; they span the seven-dimensional space of vectors whose sums on both parts vanish. A triple with odd intersection size \(a\) with \(S\) is selected and has sum \(a-k/3\) on \(S\). Choose \(a=1,3,1,3\), respectively. These choices exist and have nonzero sums, supplying the missing direction. If \(k=9\), all pair roots are selected and already span \(H\). ∎

Equivalently, a nonzero word of the real response code \(\mathcal R=\{(\langle z,u_t\rangle)_t:z\in H\}\) cannot be supported in a proper binary subspace of the port-label space. The finite certificate supplies a nonsingular eight-root minor for each of the 511 normals; the verifier uses exact fraction-free determinants.

Now tensor the ports and response code:

\[
 T_n=T^n,\quad p_{(t_1,\ldots,t_n)}=t_1\otimes\cdots\otimes t_n\in\mathbb F_2^{9^n},
 \quad \mathcal R_n=\mathcal R^{\otimes n}.
\]

**Lemma 3.2.** Every nonzero word of \(\mathcal R_n\) has support spanning \(\mathbb F_2^{9^n}\).

**Proof.** Suppose a codeword \(f(t,z)\) vanishes whenever a nonzero binary tensor functional \(w(t\otimes p_z)\) equals one. Expand \(w=\sum_i e_i^*\otimes w_i\). For fixed tail \(z\), let \(\alpha(z)=(w_i(p_z))_i\). If \(\alpha(z)\ne0\), Lemma 3.1 applied to the first factor makes the entire slice \(f(\cdot,z)\) zero. Write this slice in any real basis of \(\mathcal R\): all its coefficient functions \(f_j(z)\in\mathcal R_{n-1}\) vanish there. Choose an index \(i\) with \(w_i\ne0\). The coefficient functions therefore vanish wherever \(w_i(p_z)=1\), so induction gives \(f_j=0\) for every \(j\). This contradicts \(f\ne0\). ∎

### 3.3 What the obstruction actually rules out

A **faithful static response factorization** of \(G_n=G^{\otimes n}\) is

\[
 G_n=\sum_{j=1}^s b_j a_j^T,
 \qquad 0\ne a_j\in\operatorname{row}(G_n),\quad
 0\ne b_j\in\operatorname{col}(G_n).
\]

A gather channel forms \(a_j^Tx\) from source ports by pointwise mixing and monotone frame growth, without having already paid downward source transport. Its completed frame contains every source label in its support. A static scatter channel supplying all its nonzero \(b_j\) outputs has a frame contained in every corresponding target cap.

Lemma 3.2 forces the gather frame to be FULL and the common scatter frame to be zero. Since \(s\ge\operatorname{rank}G_n=r_n\), transporting these channels costs at least \(h_nr_n\). Every minimal-rank factorization is faithful: its row and column spans must equal those of \(G_n\). Arbitrary invertible basis changes therefore do not evade the conclusion. Overcomplete *faithful* factorizations do not help either.

A broader network version covers non-star decoders and persistent or shared channels whenever they expose a rank-\(r_n\) full-frame input interface and a rank-\(r_n\) zero-frame output interface. Unroll any finite chronological linear network in time. Same-frame linear gates may have arbitrary fan-in. Each transport edge carries one scalar-array channel and is charged its downward dimension change; source information is injected only at the full-frame interface. For each threshold \(k=1,\ldots,h_n\), cut all downward edges crossing that threshold. If there are \(q\) such edges, the rank of the source-to-output map is at most \(q\): every source-dependent output factors through their \(q\) scalar values. Thus \(q\ge r_n\). Summing over thresholds counts every downward edge exactly its charged dimension change and proves

\[
 \text{paid downward mass}\ \ge h_nr_n.
\tag{3.4}
\]

This proof permits cycles after time-unrolling, channel reuse, arbitrary correlated initial dirt, and linear recombination at equal frames. Independent initial dirt cannot transmit additional source rank.

**Boundary.** This is not a lower bound for every conceivable physical program. It does not exclude off-code cancellations, injections of fresh source information below the full interface, nonlinear encodings, or a decoder with genuinely different terminal interfaces. In particular it does not identify P401's helper-response kernels with the root code. The precise obstruction is useful because it eliminates basis-gauge and faithful non-star solutions of the natural full-to-zero problem without overstating the architectural class.

### 3.4 Why a tempting zero-copy polynomial word fails

Equation (3.2) suggests replacing retained centers by a scalar polynomial in \(K\), using several upper/lower \(K\)-shears. This would require identifying routed stage operators with one commuting matrix. They are not.

In the three-block cover of Section 7, put \(\rho_t=\rho_{1,t}\). The first correction has block \(K_{ts}I\); the routed correction has block \(K_{ts}\) times right multiplication by \(\rho_t\rho_s\). Consequently the diagonal port block of their commutator is

\[
 \frac14\sum_{s:K_{ts}\ne0}
  \bigl(R_{\rho_s\rho_t}-R_{\rho_t\rho_s}\bigr).
\tag{3.5}
\]

`owner-commutator.json` provides a concrete orthogonal matrix occurring once in the first sum and zero times in the second, at the first port \(t=7\). Its coefficient is exactly \(1/4\). The verifier constructs both multisets independently. Right multiplication on the full cover is faithful, so an input supported at that owner gives an actual nonzero output difference. This refutes this polynomial identification, not all possible new staged words.

## 4. A recursively realized tensor correction

Let \(A_n=A^{\otimes n}\), \(B_n=B^{\otimes n}\), \(G_n=B_nA_n\), and \(K_n=I-G_n\). Tensor ports are distinct, odd-weight, and not the characteristic all-ones vector. Their number is \(v_n\), their binary ambient dimension is \(h_n\), and \(\operatorname{rank}G_n=r_n\).

The key decomposition is

\[
 K_n=K\otimes I_{v_{n-1}}+
 (B\otimes I_{v_{n-1}})(I_8\otimes K_{n-1})
 (A\otimes I_{v_{n-1}}).
\tag{4.1}
\]

Indeed the second term is \(G\otimes(I-G_{n-1})\), which added to \((I-G)\otimes I\) gives \(I-G\otimes G_{n-1}\). This elementary identity is not itself a new algebraic theorem. Its role here is to supply the following legal physical DAG instead of materializing every tensor correction edge.

### 4.1 Literal core specification

Define a core \(\mathcal C(k,d)\) in ambient binary dimension \(d9^k\). Its inputs \(q_p\) are at frame \(I_d\otimes pp^T\). Every newly allocated helper starts at frame zero. All allocations refer to distinct live helper roles, not clean scratch assumptions. For clean-response analysis only, set their logical entrance values to zero. The dirty compensation is supplied in Section 5.

1. Allocate output helpers \(o_p\), and move each from zero to its cap \(I_d\otimes(I-pp^T)\).
2. For each tail \(b\in T^{k-1}\), and each nonzero base coefficient \(K_{ta}\), allocate one pair helper. Move it to the line frame of \(a\otimes b\), add \(q_{a,b}\), move it to the cap of \(t\otimes b\), add \(K_{ta}\) times it to \(o_{t,b}\), and finish it at FULL. The line lies in the cap because \(a\cdot t=0\) and \(b\cdot b=1\).
3. For each tail \(b\), allocate eight gather helpers \(g_{j,b}\) at \(I_{9d}\otimes bb^T\). Grow each \(q_{a,b}\) to that frame, perform the 736 nonzero base \(A\)-additions for this tail, and finish each input helper at FULL.
4. If \(k=1\), the eight gathers are the retained centers; they are already FULL. Return the outputs and centers.
5. If \(k>1\), invoke \(\mathcal C(k-1,9d)\) separately on each of the eight gather families. Its output for tail \(b\) is at \(I_{9d}\otimes(I-bb^T)\). Allocate a decoder helper for each \((a,b)\) at that frame, accumulate the base \(B_{aj}\) combination of the eight child outputs, grow to the parent cap of \(a\otimes b\), add to \(o_{a,b}\), and finish the decoder at FULL. After all 120 first-factor targets for a fixed tail have used them, finish the eight child outputs at FULL.

Every ADD is at an exactly equal frame. Every listed move is nested. No child output is released before its final use. Outputs are held at their caps; retained centers and every other consumed role finish FULL.

Induction using (4.1) proves that the clean outputs are \(K_kq\), and the retained centers are \(A_kq\). Let \(L_n\) also denote, when used as a matrix, the product of all elementary helper ADDs of this core, disregarding the frame labels. It is invertible as an explicitly listed product of shears. To avoid ambiguity, its **instruction count** will be written \(\lambda_n\).

### 4.2 Exact counts

Include the \(v_n\) root input helpers in \(R_n\). Direct counting gives

\[
 R_1=6968,\quad R_n=59v_n+8R_{n-1},
\]
\[
 \lambda_1=14176,\quad
 \lambda_n=14632\,120^{n-1}+120^n+8\lambda_{n-1}.
\]

Solving these recurrences gives

\[
 R_n={885v_n-1081r_n\over14}<{885\over14}v_n,
 \qquad
 \lambda_n={922v_n-1426r_n\over7}.
\tag{4.2}
\]

For comparison, direct tensor correction edges would require
\(v_n(57^n-1)\) helpers: each row of \(G_n\) has \(57^n\) nonzeros including its diagonal. Equation (4.1) avoids that extra exponential factor.

### 4.3 A second structural improvement: factor the retained-center decoder

Sequentially scattering each retained center with its expanded column of \(B_n\) uses \(456^n\) scalar additions. It is not linear in \(v_n\). The provided serial certificate is a conservative valid implementation, but this is not the final scalar architecture.

For the batched version, reserve \(r_n\) distinct private center arrays. Copy and descend each center into its own array, paying \(h_n\) each. Previously descended centers stay in the caller's reserved segment during later children. They are not handed to those children and are not borrowed as child workspace.

Compute \(B^{\otimes n}\) one tensor factor at a time, with fresh arrays for every intermediate level. At level \(j\), the shape is \(120^j\times8^{n-j}\). The exact addition and temporary-array counts are

\[
 z_n=456\sum_{j=0}^{n-1}120^j8^{n-1-j}
     ={57\over14}(v_n-r_n),
\]
\[
 q_n=\sum_{j=1}^{n}120^j8^{n-j}
     ={15\over14}(v_n-r_n).
\tag{4.3}
\]

Add the final \(v_n\) decoder outputs to the targets, then clear every intermediate and center array. Reverse-mode accumulation through this very same finite DAG computes \(B_n^T\), with all intermediate arrays also explicitly cleared. It is used in the backward orientation. This is a non-star decoder with paid persistent private storage, not free reuse or a missing linear-map oracle.

## 5. Full dirty restoration in both chronological orientations

### 5.1 Forward word, including the old response

Fix a depth and abbreviate \(v,h,r,R\). Let \(H\in\mathbb C^R\) denote the vector of arbitrary logical helper functions. Let \(V\) inject the \(v\) source functions into the root input helper roles. Let \(J\) read the root output helpers plus the \(B_n\) combination of retained centers. The clean-core proof gives

\[
 J L_n V=K_n+B_nA_n=I_v.
\tag{5.1}
\]

The following is the actual chronological forward program. Source charts start at their individual lines; target and helper charts start at zero.

**Old response.** Copy all \(R\) helpers into \(R\) distinct private tableau arrays at frame zero. Replay every scalar ADD of \(L_n\) on the copies, also at zero. Subtract the tableau's root outputs and its factored center decoder from the targets. Clear the entire tableau and every decoder intermediate. This implements \(y\mathrel{-}=JL_nH\) by a priced finite program, not by a response oracle.

**Load and core.** Move each root input helper to its source line and add that source. Run the literal core of Section 4, including every helper entry and exit move. At this point the logical helper vector is \(L_n(H+Vx)\). Root outputs are at their caps, all centers are FULL, and all consumed helpers are FULL.

**Retained centers.** While the targets are still at zero, copy each FULL center into its own reserved private array, pay the FULL-to-zero child, and leave it in the reserved bank. Decode the bank by the factor-by-factor \(B_n\) circuit and add its outputs to the targets. Clear all decoder and center arrays. The serial alternative uses one active private center and expanded scalar scatter; it has the same child profile but a larger asymptotic scalar count.

**Output and cleanup.** Move targets to their caps, add the corresponding root outputs, and finish those output helpers at FULL. Finish source registers at FULL. Now every live helper is FULL. Replay the exact reverse list of core ADDs with negated coefficients; this is \(L_n^{-1}\). Finally subtract each source from its root input helper at FULL.

On logical values, the result is

\[
 (x,y,H)\longmapsto(x,y+JL_nVx,H)=(x,y+x,H).
\tag{5.2}
\]

The two helper-dependent target terms cancel exactly. Cleanup sends
\(L_n(H+Vx)\) to \(H+Vx\) and then to \(H\). Thus the helper endpoint is the identity on *each* helper coordinate, with no helper-to-helper off-diagonal block and no data displacement. This is an identity of linear operators on arbitrary functions. It does not assume statistical independence, clean helpers, uncorrelated banks, or particular source data. Private arrays end zero.

### 5.2 Backward word is the inverse adjoint, not an ordinary transpose

For an invertible linear operator \(M\), define \(\phi(M)=(M^{-1})^*\). It is multiplicative, so it preserves chronological order when applied to a physical instruction word. Real scalar `t += a*s` becomes `s -= a*t`. Every unitary chart transition is fixed by \(\phi\).

The old-response macro is inverted and adjointed as a *complete live macro*. Its backward implementation is

\[
 H\mathrel{+}=L_n^TJ^Ty.
\]

Compute this with a zero private tableau: seed the root-output coordinates with \(y\), compute \(B_n^Ty\) by reverse-mode decoder accumulation into the center coordinates, replay the transpose core in reverse list order, add all \(R\) tableau entries into their respective helpers, then clear the tableau and decoder work. There is no attempt to take the transpose of an erasure instruction.

For the retained-center macro, compute \(B_n^Ty\) into the private center bank at zero, clear the decoder intermediates, then for each center pay the zero-to-FULL child and subtract that private array from its live retained center. Clear it immediately. The other main ADDs swap source and target and negate the coefficient, in their original chronological order. Frame moves stay unchanged.

If \(P_{in},P_{out}\) denote the block-diagonal unitary entrance and exit charts, the forward physical map is
\(P_{out}MP_{in}^{-1}\). Its inverse adjoint is
\(P_{out}\phi(M)P_{in}^{-1}\). Thus the same entrance and exit frames are valid. The logical backward endpoint is exactly

\[
 (x,y,H)\longmapsto(x-y,y,H).
\tag{5.3}
\]

Both implementations are serialized and checked on every independent live input column at depth one. The induction and macro proofs establish the general depth, not a claim that a depth-one experiment proves all sizes.

### 5.3 Scratch ownership and primitive invoice

Let \(q=q_n\), \(z=z_n\), \(\lambda=\lambda_n\). The batched implementation uses exactly

\[
 P_n=R_n+q_n+r_n={450v_n-541r_n\over7}<W_n
\tag{5.4}
\]

private full-width arrays: the \(R\)-array tableau, all \(q\) decoder intermediates, and the \(r\)-array center bank. These namespaces are disjoint from all live data/helpers and from a callee's recursively allocated segment. All are initialized once. All are zero at the end of each complete local invocation. Tableau and decoder intermediates are zero at every recursive call; only the explicitly reserved center bank may remain nonzero during its own sequence of descents/ascents.

With

\[
 F_n=3\lambda_n+2z_n+6v_n={2865v_n-4335r_n\over7},
\]

the exact local instruction counts are

| Primitive | Forward | Backward |
|---|---:|---:|
| pointwise ADD | \(F_n\) | \(F_n+R_n+r_n\) |
| COPY | \(R_n+r_n\) | 0 |
| CLEAR | \(R_n+2q_n+r_n\) | \(R_n+2q_n+r_n\) |
| paid children | \(S_n\) | \(S_n\) |

Initial workspace initialization adds at most \(P_n\) zero writes per entry once. A pointwise ADD costs at most two complex arithmetic operations per entry. Each COPY or CLEAR is a charged memory operation. No stage frees a live helper by erasing it.

All these counts are \(O(v_n)\). In particular the non-star factorized decoder removes the \(456^n\) scalar expansion cost of the serial implementation. It does **not** remove any of the \(r_nh_n\) center-child mass.

## 6. Complete Gaussian phase lowering

### 6.1 Nested charts

If \(P,Q\) are symmetric projectors with \(PQ=QP=P\), put \(R=Q+P\) over \(\mathbb F_2\). Then \(R\) is a projector orthogonal to \(P\). For every binary \(y\), the vectors \(Py,Ry\) have even integer overlap, because their binary dot product is zero. Therefore

\[
 \operatorname{wt}(Qy)\equiv
 \operatorname{wt}(Py)+\operatorname{wt}(Ry)\pmod4,
\]

and exactly, including phase,

\[
 T_QT_P^{-1}=T_R.
\tag{6.1}
\]

Also \(T_R^2=X_{\operatorname{diag}R}\). Indeed
\(\operatorname{wt}(Ry)\bmod2=y^TRy=\operatorname{diag}(R)\cdot y\).
Thus a downward transition uses
\(T_R^{-1}=X_{\operatorname{diag}R}T_R\), not an uncharged inverse child.

### 6.2 One child and explicit monomial adapters

Suppose \(R\) has rank \(s\), and choose an orthogonal binary matrix \(A\) whose first \(s\) columns form an orthonormal basis of \(\operatorname{im}R\). Use the convention \(P_A f(x)=f(A^{-1}x)\), so that \(P_A^{-1}\chi_y=\chi_{A^Ty}\). Define

\[
 \delta_i=\frac{\operatorname{wt}(Re_i)-\sum_{j<s}A_{ij}}{2}\pmod2.
\tag{phase}
\]

The numerator is even: both terms have parity \(R_{ii}\). Then

\[
 T_R=X_\delta\,P_A(C_s\otimes I)P_A^{-1}.
\tag{6.2}
\]

**Proof.** The phase of \(T_R\) is \(\operatorname{wt}(Ry)\bmod4\). Its linear coefficients are the column weights of \(R\); its quadratic coefficient on \(y_iy_j\) is \(-2R_{ij}\), since \(R^TR=R\) over the binary field. The phase of the conjugated child is
\(\sum_{j<s}(A_{\cdot j}\cdot y\bmod2)\). Its quadratic coefficients are the same, because the first \(s\) columns give \(R\). Equation (phase) supplies their entire linear difference. Both phases vanish at zero, so there is no missing constant Gaussian phase. ∎

For a downward move, replace \(\delta\) by \(\delta+\operatorname{diag}R\). Thus every transition is exactly two address permutations, one smaller positive \(C_s\) child and at most one translation. No global sign or Gaussian phase is suppressed.

### 6.3 Every used difference admits the required basis

The relevant binary subspaces and their orthogonal complements are nondegenerate and nonalternating, hence admit orthonormal bases. Here is a constructive justification rather than an appeal to an arbitrary-space normalization theorem.

For completeness, a nondegenerate symmetric space can first be split into orthogonal unit lines and an alternating remainder. The latter has even dimension, by repeatedly splitting a nonzero symplectic pair. One unit line with a symplectic pair \(a,b\) can be replaced by the three mutually orthogonal unit vectors \(e+a,e+b,e+a+b\). Thus every nonalternating nondegenerate space admits an orthonormal basis. This also proves that the characteristic vector has norm equal to the dimension modulo two.

In a nondegenerate binary symmetric space, the characteristic vector \(c\) is defined by \(x\cdot x=c\cdot x\). A nonalternating space has a unit vector. An orthonormal basis can be constructed by repeatedly choosing a unit vector whose orthogonal complement is still nonalternating, then orthogonalizing the remaining basis by \(b\mapsto b+(b\cdot u)u\). The only bad choice is a unit equal to the characteristic vector while a positive-dimensional alternating complement remains. If necessary choose a different unit; in odd dimension greater than one, adding a nonzero even vector to that characteristic unit supplies one. In even dimension the characteristic vector is even and is not a unit. This proves the constructive induction, with dimension one as its endpoint.

Every tensor port \(p\) is unit and is not the characteristic all-ones vector. Therefore \(p^\perp\) is nonalternating. For an orthogonal pair of such unit ports \(p,q\), their common complement is also nonalternating: the ambient characteristic vector cannot lie in their span, because it is odd, whereas \(p+q\) is even and neither \(p\) nor \(q\) is characteristic. These observations supply bases for line-to-cap pair moves. The other core differences are tensor products of coordinate spaces, unit lines and complements of unit ports, for example

\[
 I_d\otimes a^\perp\otimes\langle b\rangle,
 \quad I_{9d}\otimes b^\perp,
 \quad I_d\otimes(\langle p,q\rangle)^\perp.
\]

Tensor products and orthogonal sums of orthonormal bases are orthonormal. Kernels either have the corresponding complementary form or explicitly contain a unit line. Zero-dimensional pieces are allowed. The final global differences are two coordinate lines before orthogonal conjugation. Thus (6.2) lowers **every** child in the program; no arbitrary degenerate entrance-space premise is needed.

For each serialized depth-one transition, the verifier checks the basis, projector, rank and phase at \(0,e_i,e_i+e_j\). Since these determine every coefficient of a \(\mathbb Z/4\) quadratic polynomial, this is an exact verification for all address characters, not sampling a few addresses.

## 7. A complete three-stage physical cover

This section derives the used bridge specialization directly. It does not assume that a scalar three-shear word is already a geometric provider.

### 7.1 Roles and owner routes

Set \(m=3h\) and decompose the binary label space into three standard blocks \(H_0,H_1,H_2\). Let

\[
 W_c=\operatorname{span}\{e_{c,j}:1\le j<h\}\quad(c=1,2),
 \qquad\Omega=O(m,2).
\]

For every \(g\in\Omega\) and port \(t\), allocate the two live data roles \(X_{t,g},Y_{t,g}\). For every helper index \(j\le R\), allocate \(H_{j,g}\). Thus there are \(|\Omega|W\) live arrays. Their values may be arbitrarily correlated.

For each port \(p_t\), choose an explicit orthogonal \(A_t\) with first column \(p_t\). To construct it, choose a zero coordinate \(z\) of \(p_t\); swap coordinate zero with \(z\), then apply the transvection \(I+ww^T\), where \(w=p_t+e_z\). Since \(w\cdot w=0\), the transvection is orthogonal and involutive, and sends \(e_z\) to \(p_t\). Actual inverse matrices are transposes; no nonsymmetric route is replaced by itself.

Let \(\rho_{c,t}\) swap the \(h-1\) basis vectors of \(p_t^\perp\) in block zero with the coordinate basis of \(W_c\). It fixes \(p_t\), the exterior pivot \(e_{c,0}\), and the other exterior block. This is an explicitly conjugated coordinate swap, hence a symmetric orthogonal involution. Let \(\tau_c\) swap the **whole** blocks \(H_0,H_c\).

At stage zero, a local owner \(d\) uses data and helpers with owner \(d\). At stage \(c=1,2\), it uses

\[
 X_{t,d\rho_{c,t}},\quad Y_{t,d\rho_{c,t}},\quad
 H_{j,d\tau_c}.
\tag{7.1}
\]

Right multiplication by each route is a bijection of \(\Omega\). Consequently every data role and every helper role is used exactly once in each stage. Invocation order can be lexicographic in \(d\). No two invocations in one stage alias a given live role.

### 7.2 Exact data-frame identities

Put \(Q_0=0\), \(Q_1=W_1\), \(Q_2=W_1\oplus W_2\), also writing these names for their projectors. Before stage zero, assign formal charts \(P_t=p_tp_t^T\) to \(X_{t,g}\), and zero to \(Y_{t,g}\), conjugated by \(g\). No physical initialization transform is applied.

After stage \(c\), the global data charts relative to owner \(g\) are

\[
 P_X^{(c)}=H_0\oplus Q_c,
 \qquad P_Y^{(c)}=(H_0\cap p_t^\perp)\oplus Q_c.
\tag{7.2}
\]

For a stage \(c\ge1\) local owner \(d\), the local window is \(dH_0\), with common background \(dQ_c\). Directly from the swap definition,

\[
 \rho_{c,t}(H_0\oplus Q_{c-1})=\langle p_t\rangle\oplus Q_c,
\]
\[
 \rho_{c,t}((H_0\cap p_t^\perp)\oplus Q_{c-1})=Q_c,
\]
\[
 \rho_{c,t}(H_0\oplus Q_c)=H_0\oplus Q_c,
\quad
 \rho_{c,t}((H_0\cap p_t^\perp)\oplus Q_c)
 =(H_0\cap p_t^\perp)\oplus Q_c.
\tag{7.3}
\]

These are equalities of projectors after conjugation, not just dimension counts. They make the local line/zero entrance and FULL/cap exit precisely match the actual global chronology. The canonical \(T_P\) charts in Section 6 fix all phases. A local transition is the difference of its two conjugated projectors, lowered by (phase). There is no uncharged "up to a cover phase" correction.

### 7.3 Shared dirty helpers really compose

In a local invocation with window \(U\) and background \(Q\perp U\), Section 5 gives the independently restored helper endpoint

\[
 T_{Q+U}T_Q^{-1}=T_U.
\tag{7.4}
\]

This equation holds on the helper's *actual arbitrary current array*. To see why no entrance normalization is hidden, write that current array as \(T_Qh\), defining \(h=T_Q^{-1}\) times it. This definition does not execute \(T_Q^{-1}\). The physical word proved for every \(h\) maps the array to \(T_{Q+U}h=T_U\) times its previous value. The complete block-diagonal restoration proof is essential; a merely zero target-response column would not suffice.

For the global bank owner \(g=d\tau_c\), its local window \(dH_0\) is \(gH_c\). Across the three stages it therefore receives
\(T_{gH_0},T_{gH_1},T_{gH_2}\). The three projectors are orthogonal and sum to identity. Equation (6.1) gives their product exactly \(T_I=C_m\), on the original helper array. All correlations with data or other banks are permitted. No helper restoration or endpoint transformation is omitted.

### 7.4 Chronological word and final Gaussian correction

Use forward, backward, forward complete local invocations. On each routed pair of logical data functions, these are

\[
 F=\begin{pmatrix}1&0\\1&1\end{pmatrix},\qquad
 B=\begin{pmatrix}1&-1\\0&1\end{pmatrix},\qquad
 FBF=\begin{pmatrix}0&-1\\1&0\end{pmatrix}.
\tag{7.5}
\]

Right multiplication's bijectivity and (7.3) mean that these are successive operations on the same global pair \((t,g)\); one is not multiplying incompatible local matrices. The data become \((-y,x)\) in the charts (7.2).

Each final X chart misses precisely the two exterior pivot lines, so one rank-two child finishes it at FULL. The Y chart also misses those two lines in addition to its port line; a rank-two child finishes it at the cap of \(gp_t\). Then translate Y by \(gp_t\) and perform the signed exchange \((X,Y)\leftarrow(Y,-X)\).

The entrance X logical value was \(x=T_{gp_t}^{-1}X_{initial}\). The final translated Y before exchange is

\[
 X_{gp_t}T_{I-P_{gp_t}}T_{P_{gp_t}}^{-1}X_{initial}
 =T_{I-P_{gp_t}}T_{P_{gp_t}}X_{initial}=C_mX_{initial},
\]

because \(T_{P_{gp_t}}^2=X_{gp_t}\). The other output is \(C_mY_{initial}\). Thus the complete physical program computes \(C_m\) independently on **every** live data and helper array and clears its private work. The initial formal line chart has been accounted for, not supplied free.

## 8. Paid rank profile and finite primitive costs

Let \(H_n(s)\) be the local histogram, including both data-role moves and center copies. Its exact rank mass is

\[
 \sum_s sH_n(s)=h_nR_n+2v_n(h_n-1)+c_n.
\tag{8.1}
\]

This follows without retiming assumptions: each live helper starts at zero and ends FULL along a monotone path, each source goes from line to FULL, each target from zero to cap, and every center copy crosses all \(h_n\) dimensions.

For exact histogram generation, at a recursion node of depth \(k\), prefix dimension \(d\), ambient \(h=d9^k\), let \(V=120^k\), \(b=120^{k-1}\). Add these `(rank,count)` contributions, discarding rank zero:

| Contribution | Rank, count |
|---|---|
| output entries | \((h-d,V)\) |
| pair entries / line-to-cap / exits | \((d,6720b),(h-2d,6720b),(d,6720b)\) |
| input gather growth / exit | \((8d,V),(h-9d,V)\) |
| new gather entries | \((9d,8b)\) |
| if \(k>1\), decoder entry / growth / exit | \((h-9d,V),(8d,V),(d,V)\) |
| if \(k>1\), child-output final exits | \((9d,8b)\) |

For \(k>1\), include eight child-node profiles at \((k-1,9d)\). Finally add root-input loading and data endpoints \((1,2v_n),(h_n-1,2v_n)\), and private center copies \((h_n,r_n)\). This recipe agrees with the separately implemented recursive histogram generator and the serialized depth-one program.

The total number of local children and global children per orthogonal cover element are

\[
 S_n=\sum_sH_n(s)={1334v_n-1726r_n\over7},
\]
\[
 C_n=3S_n+2v_n={4016v_n-5178r_n\over7}<9W_n.
\tag{8.2}
\]

The global profile per cover element is

\[
 \mathcal H_n(s)=3H_n(s)+2v_n\,1_{s=2}.
\tag{8.3}
\]

Hence

\[
 \sum_s s\mathcal H_n(s)
 =3h_nR_n+6v_n(h_n-1)+3c_n+4v_n
 =W_nm_n-(2v_n-3c_n).
\]

This proves (0.1), and
\(D_n/v_n=2-3(3/5)^n\ge1/5>0\).
All global child ranks are at most \(h_n=m_n/3\).

The two-forward/one-backward global scalar invoice per cover element is

\[
 \mathrm{ADD}=3F_n+R_n+r_n,
\quad \mathrm{COPY}=2(R_n+r_n),
\quad \mathrm{CLEAR}=3(R_n+2q_n+r_n).
\tag{8.4}
\]

There are \(C_n\) child calls, at most \(2C_n\) address permutations from their lowerings, at most \(C_n\) child-lowering translations, \(v_n\) final translations, and \(v_n\) signed exchanges. A signed exchange needs at most three assignments and one negation per entry using a scalar temporary. The initial private initialization and one permutation-work array are also charged. These counts are multiplied by \(|\Omega|\) when the full cover word is used, except that the private segment is reused only after a complete invocation has cleared it.

A permutation is not a free operation: it is implemented using an explicitly owned temporary array, a scatter/gather copy and clearing, with bounded integer address work per entry as detailed in Section 10. That temporary is cleared before the recursive child begins. The batched center bank is the only nonzero private bank retained outside a child's own array; it resides outside the child's address segment.

For depth two the principal numbers are:

\[
 h=81,\ v=14400,\ r=64,\ c=5184,\ R=905344,
\]
\[
 \lambda=1883648,\ z=58368,\ q=15360,
\]
\[
 F=5854080,\ F+R+r=6759488,\ P=920768,
\]
\[
 m=243,\ W=934144,\ D=13248,\ C=8214144.
\]

Its exact global histogram is

```
rank      count
   1    4968000
   2      28800
   8      86400
   9     328320
  63     161280
  72      92160
  79    2419200
  80     129600
  81        384
```

The independently checked sum is \(243\cdot934144-13248\). This price includes all center descents, helper entry/exit work, both data endpoints, and the final two rank-two children per port.

## 9. Strict moment bounds and the genuine asymptotic comparison

Write

\[
 \Phi_n(\kappa)=\sum_s\mathcal H_n(s)(s/m_n)^{1-\kappa}.
\]

The required strict inequality is \(\Phi_n(\kappa)<W_n\). At zero it has the exact gap \(D_n/m_n\).

For \(0\le\kappa\le1/2\) and \(0<x<1\),

\[
 {\partial\over\partial\kappa}x^{1-\kappa}
 =x^{1-\kappa}\log(1/x)\le2/e<1.
\]

There are \(C_n<9W_n\) children, so

\[
 \Phi_n\left({D_n\over18W_nm_n}\right)
 <W_n-{D_n\over m_n}+{D_n\over2m_n}<W_n.
\tag{9.1}
\]

The chosen argument is below \(1/2\), since \(D_n<2v_n\le W_n\). This proves a positive **rational** exponent formula for every depth without numerical root-finding.

The finite certificates also prove the following convenient fixed choices:

| depth | \(h_n\) | \(c_n/v_n\) | certified \(\kappa\) |
|---:|---:|---:|---:|
| 1 | 9 | \(3/5\) | \(1/15000\) |
| 2 | 81 | \(9/25\) | \(1/25000\) |
| 3 | 729 | \(27/125\) | \(1/125000\) |
| 4 | 6561 | \(81/625\) | \(1/1000000\) |
| 5 | 59049 | \(243/3125\) | \(1/10000000\) |

For depth two, the stronger equivalent weighted inequality is certified with more than 1737 units of rank-mass slack:

\[
 \sum_s s\mathcal H_2(s)(243/s)^{1/25000}
 <243\cdot934144-1737.
\tag{9.2}
\]

The certificate is rational, not floating-point evidence. To bound a logarithm, reduce its argument to \([1,2]\), use
\(\log x=2\sum_{j\ge0}u^{2j+1}/(2j+1)\), \(u=(x-1)/(x+1)\), and bound the omitted tail by its geometric majorant. Round upper bounds upward to dyadic rationals with denominator \(2^{80}\). For \(0\le z<3\),

\[
 e^z\le1+z+{z^2\over2(1-z/3)},
\]

because \(k!\ge2\cdot3^{k-2}\) for \(k\ge2\). Summing these rational upper bounds proves (9.2). The consumer uses a separate 24-term logarithm bound instead of the generator's 20-term implementation.

### 9.1 Copied loss vanishes, but the best rate does not stay positive

The loss relative to this assembly's hypothetical zero-center deficit is

\[
 {D_n\over2v_n}=1-\frac32(3/5)^n\longrightarrow1.
\tag{9.3}
\]

No zero-center operation was substituted to obtain this identity. It describes the cost of the actual paid family.

Since all child ranks are at most \(m_n/3\),

\[
 \Phi_n(\kappa)\ge3^\kappa\Phi_n(0).
\]

Thus every exponent passing this profile satisfies

\[
 \kappa<\frac{\log\!\bigl(W_n/(W_n-D_n/m_n)\bigr)}{\log3}
       =O(9^{-n}).
\tag{9.4}
\]

Conversely (9.1), (4.2) and \(D_n/v_n\ge1/5\) give a positive constant times \(9^{-n}\). Therefore the moment threshold is \(\Theta(9^{-n})\). This is an obstruction for this complete paid profile, not a universal transform lower bound.

One can obtain its exact leading constant. Let \(\kappa_n^*\) be the unique solution \(\Phi_n(\kappa)=W_n\) between zero and one. Existence and uniqueness follow from strict monotonicity, \(\Phi_n(0)<W_n\), and \(\Phi_n(1)=C_n>W_n\).

At recursion depth \(j\), the histogram counts divided by \(v_n\) are bounded by a fixed constant times \(15^{-j}\). The ranks divided by \(h_n\), for fixed \(j\) as \(n\to\infty\), tend either to zero or to one: the ranks have the forms \(a9^j\) and \(h_n-a9^j\) with bounded positive \(a\). Rank-two endpoints and center-only terms obey the same limiting conclusion or have vanishing normalized counts. Thus dominated convergence applies to both \(\Phi_n/v_n\) and its derivative at any sequence \(\kappa\to0\), using \(x^{1-\kappa}\log(1/x)\le1\) for \(\kappa\le1/2\). Only the rank-ratio-one mass survives, and its ratio to the global width is \(1/3\). Consequently

\[
 {\Phi_n'(\kappa)\over v_n}\longrightarrow {913\over14}\log3,
 \qquad (\kappa\to0),
\]

where \(W_n/v_n\to913/14\). By the mean value theorem and (9.4),

\[
 h_n\kappa_n^*={D_n\over3\Phi_n'(\xi_n)}
 \longrightarrow {28\over2739\log3},
 \qquad 0<\xi_n<\kappa_n^*.
\]

This establishes (0.4). It explains the tradeoff structurally: tensorization improves copied-center density, while enlarging the binary address dimension destroys a depth-independent exponent. The fixed P193 hypothetical zero-copy number around \(1.28147\cdot10^{-3}\) cannot be interpreted as the limit of this construction.

## 10. Closing the all-size exact-arithmetic RAM theorem

This section proves a recursive compiler for the constructed word. Its assumptions are the ordinary operations of a precisely specified RAM, not an all-size physical-provider hypothesis equal to the desired conclusion.

### 10.1 RAM and uniformity

The machine has exact complex cells, exact addition and multiplication, and indexed reads/writes. A fixed finite constant set such as \(0,1,-1,i,1/2,1/3\) suffices: all other scalar constants used below are generated from it by charged arithmetic or fixed setup. In particular, no arbitrary algebraic-number oracle is present. Address registers use integers of \(O(\log N)\) bits with unit-cost arithmetic, quotient/remainder, comparison and indexing. No packed-integer multiplication is used to simulate complex arithmetic. The use of quotient/remainder and random access is explicit; this is **not** a fixed finite-alphabet multitape model.

For each fixed architecture depth \(n\), one finite, computably specified program handles every input exponent \(\ell\). A single constructor produces these programs from \(n\). Constants depend on \(n\); no bound uniform in both architecture depth and input length is claimed. All base coefficients, binary matrices, role routes and instruction lists are computed from Sections 3–7 by finite algorithms. No externally supplied response matrix, source executable, transform oracle or group-order oracle is required.

### 10.2 Explicit padding without a precomputed orthogonal group

Let \(W=W_n,m=m_n\), and set

\[
 a=m^2+\lceil\log_2 W\rceil,\qquad L=2^a.
\tag{10.1}
\]

Use \(m^2\) role-index bits to represent **every** binary \(m\)-by-\(m\) matrix, and the remaining role-index bits to represent up to the next power of two above \(W\) role types. If the matrix is orthogonal and the role type is below \(W\), it is a live role of the cover word. Every other role is an actual input array handled by one paid ordinary full-window transform. These are padding inputs, not assumed-zero workspace.

Orthogonality is tested by multiplying the matrix by its transpose. For fixed \(m\) this is a fixed finite amount of address computation. Owner routes are explicit right multiplications and remain within orthogonal labels. Their raw matrix-bit labels are already direct row addresses, so there is no dense-rank lookup or source-routing oracle. An exhaustive construction is bounded by \(2^{m^2}\) candidate matrices, but neither generation nor verification in this package enumerates that group.

Let \(G=|\Omega|\) only for analysis; the algorithm does not need its value. There are \(GW\) cover inputs and \(L-GW\) ordinary padding inputs. With

\[
 B_s=G\mathcal H_n(s)+(L-GW)1_{s=m},
\]

any strict local moment gives

\[
 \sum_s {B_s\over L}(s/m)^{1-\kappa}
 = {G\over L}\Phi_n(\kappa)+{L-GW\over L}<1.
\tag{10.2}
\]

Padding has not been omitted from the price. Since identity is orthogonal, \(G\ge1\), so the positive gap can even be bounded below without computing the group order. This padding is very inefficient in constants, but completely explicit and sufficient for an asymptotic theorem.

For depth two, \(a=59049+20=59069\). This demonstrates how far the construction is from practical sizes; it is not a benchmark algorithm hidden behind small notation.

### 10.3 Dilation and chronological correctness

For \(\ell\ge a+m\), write

\[
 \ell=a+mk+b,\qquad k\ge1,\quad0\le b<m.
\]

First transform the \(a\) role bits and \(b\) remainder bits by ordinary tensor butterflies, at cost \(O_n(2^\ell)\). On the remaining bits, replace every one-dimensional binary coordinate of the finite width-\(m\) program by a \(k\)-bit block. A projector becomes \(P\otimes I_k\). Every scalar instruction acts pointwise, and every chart or phase identity tensors over the \(k\) bit positions. In particular a rank-\(s\) child becomes \(C_{sk}\) on each of \(2^{(m-s)k}\) fibers.

Nothing in the dirty proof requires helper functions to factor across these bit positions. Its complete endpoint is block diagonal on arbitrary functions, so it remains true after dilation for arbitrary correlated data. Likewise the owner routing and canonical projector identities remain exact. Thus the expanded word computes \(C_{mk}\) on every cover input, and ordinary padding calls do so on every other role.

Each recursive child is invoked on one explicit array segment/fiber and a newly allocated disjoint workspace. Its program is the same fixed-architecture algorithm at the strictly smaller bit length \(sk\). The induction hypothesis applies to that length; it is not invoked on the current length. For padding calls, \(sk=mk=\ell-a-b<\ell\); for cover calls it is at most \((\ell-a-b)/3\).

### 10.4 All address operations have a linear-time implementation

The lowerings require binary linear address maps on \(m\) blocks of \(k\) bits. Do not assume a unit-cost XOR of arbitrarily long bit strings. Build the table of XOR for two \(k\)-bit integers by the recurrence

\[
 \operatorname{xor}(u,v)=2\operatorname{xor}(\lfloor u/2\rfloor,\lfloor v/2\rfloor)
       +((u\bmod2+v\bmod2)\bmod2).
\]

This takes \(O(2^{2k})\) integer operations and entries. Because \(m\ge3\), it is at most \(O(2^{mk})\). A matrix-vector address map uses at most \(m^2\) table operations per entry. A weight-mod-four table costs \(O(2^k)\) if needed for boundary diagonal factors. Translations use the same XOR table. All tables and integer register widths are within the stated RAM model.

Use one explicitly reserved permutation array: copy according to the computed address permutation, copy back, then clear it. This costs a bounded number of memory operations per entry and leaves that array zero before any recursive child. The role-index matrix routes involve only fixed \(m\)-bit columns, so their computation is also bounded by an architecture-dependent constant per instruction/row. Scalar instruction counts, workspace initialization, clearing, all permutations, translations and signed exchanges therefore contribute \(A_n2^\ell\) for some explicit finite constant \(A_n\).

### 10.5 Recurrence and proof of the exponent

Let \(T(\ell)\) be the number of RAM operations for \(C_\ell\), and \(t(\ell)=T(\ell)/2^\ell\). The fiber multiplicities give the exact form of the upper recurrence

\[
 t(\ell)\le A_n+\sum_s {B_s\over L}\,t(sk).
\tag{10.3}
\]

Put \(p=1-\kappa\) and let \(\delta>0\) be the gap in (10.2). At all smaller lengths assume \(t(u)\le M\max(1,u)^p\). Since \(sk\le(s/m)\ell\), for the recursive range

\[
 t(\ell)\le A_n+M\ell^p\sum_s {B_s\over L}(s/m)^p
 \le A_n+M(1-\delta)\ell^p\le M\ell^p
\]

provided \(M\ge A_n/\delta\). Choose \(M\) also to cover the finitely many smaller lengths, which use ordinary butterflies. Strong induction proves \(T(\ell)=O_n(2^\ell\ell^{1-\kappa})\).

The total workspace is linear in the input array size. At a level it consists of the declared private arrays, the permutation array, address tables and finite indexing state. Every recursive call uses a disjoint segment and a data array of at most \(2^{\ell-a}\) entries. Along a recursion stack, the workspace sizes are bounded by a geometric series with ratio at most \(2^{-a}\le1/2\). The protected center bank remains in its caller's segment and is never addressed by the child. This proves legal persistence and restoration of all other rows by actual address separation, not by an assumed all-size restored-row contract.

### 10.6 Walsh–Hadamard conversion and model boundary

Let \(H_1=\left(\begin{smallmatrix}1&1\\1&-1\end{smallmatrix}\right)\), \(D_1=\operatorname{diag}(1,-i)\), and \(a_0=(1+i)/2\). Then

\[
 C_1=a_0D_1H_1D_1.
\]

Tensoring gives the \(2^\ell\)-point Walsh–Hadamard transform from \(C_\ell\) using two diagonal phase passes and one scalar normalization, at \(O(2^\ell)\) extra RAM cost. The scalar can be generated by repeated squaring from \(a_0^{-1}=1-i\). Thus (0.2) follows for WHT as well.

This is Fourier transformation on a binary product group. It is **not** a proof of the cyclic DFT or a proof of integer multiplication. The required cyclic-Fourier transfer, coefficient-growth/precision analysis, and fixed-tape implementation are not consequences of the RAM recurrence above. The missing original Fourier sources and the inherited unresolved interfaces cannot be silently replaced by this narrower theorem.

## 11. Verification, unsuccessful alternatives, and acceptance boundary

The runnable evidence consists of a constructor, an independently written consumer, an explicit global cover-template generator, and a source-byte audit. The verifier does not import the generator. No repository program was executed and no Lean build was performed.

The default run checks:

* all 14,400 base Gram/correction pairs and all 511 hyperplane restriction minors;
* both serial dirty words (78,776 records each), and both batched dirty words (79,256 records each), on all 7,208 independent live columns;
* every serialized frame equality and endpoint, exact scratch inventories and protected/private lifetimes;
* 7,202 distinct Gaussian lowering recipes per implementation, using 331,292 quadratic-phase determining values;
* 960 concrete projector-routing identities at depth one, the three-stage symbolic cover template and shared-helper block partition;
* all 14,400 depth-two tensor ports, their binary rank 81, and a nonzero exact real rank-64 tensor minor;
* independently unrolled histogram/count formulas and strict rational moments at depths one through six;
* the noncommuting-owner certificate with exact coefficient \(1/4\).

Negative controls reject a wrong Gaussian translation, missing source unloading, missing old-response compensation, uncharged center cost, and recharting live data for free. The mathematical induction, the all-owner conjugation argument and the all-size recurrence are proofs in this report; these finite checks are not presented as substitutes for them.

**Not expanded:** the complete depth-two local instruction list, any full orthogonal cover group, any exponentially sized address array, or an end-to-end large WHT execution. Literal expansion is guarded by a record budget before allocation; full cover enumeration is separately guarded. The default execution uses neither. The batched private-memory argument relies only on the explicitly defined disjoint-segment RAM, not on compatibility with an inherited fixed-scratch compiler.

The development tested several substantively different approaches. Faithful center basis changes and faithful overcomplete channels are blocked by Lemma 3.2 and the transport cut. Polynomial elimination using the two-eigenvalue correction is blocked by the exact routed commutator. Naive tensor correction is valid algebraically but suffers \(v_n(57^n-1)\) helper growth; the recursive source-assisted gather/correction circuit removes that growth. Sequential center scatter still has \(456^n\) scalar work; the protected-bank non-star decoder removes this second growth. A larger two-stage tensor-grid organization was considered but not used for the final theorem; the fully derived three-stage cover has much better width and deficit. None of these discarded routes is reported as a completed superior provider.

The strongest completed conclusion is therefore a **paid-copy scalable tensor family with vanishing copied loss, linear local implementation size, complete physical Gaussian–Walsh realization, and a proved exact-RAM power saving**, together with a sharp order-of-decay obstruction for its exponent. It is not a record improvement over the inherited P193 or PR390 assemblies.

The next architectural boundary is precise: to retain a positive depth-independent exponent while reducing copied loss, one must avoid this family's growing binary ambient dimension relative to its deficit. Off-code source-assisted decoders, a genuinely different port family with better rank–ambient tradeoff, or a new staged/interface mechanism could do that. No such stronger family is proved here, and the transport theorem deliberately does not rule out these possibilities.

## 12. Dependency ledger

| Result | Dependencies actually used | Status / excluded dependency |
|---|---|---|
| base E8 fitting matrix | explicit root formulas (3.1), elementary arithmetic | proved and exact checked; no source classification oracle |
| response support obstruction | Lemma 3.1, tensor-slice induction | proved for \(\mathcal R_n\), not all helper kernels |
| network transport bound | rank factorization through threshold cuts | proved only for the stated full-to-zero interface class |
| routed polynomial failure | explicit \(\rho_{1,t}\), right-regular cover action | exact counterexample, not a universal staged-word lower bound |
| tensor correction supplier | (4.1), five-step recursive frame DAG | proved by induction; no precomputed \(K_n\) routine |
| dirty restoration | literal \(L_n\), computed \(JL_n\), (5.1), explicit cleanup | full operator identity for both orientations |
| batched decoder / memory | factor-by-factor \(B_n\), priced private arrays, disjoint child segments | proved for the stated RAM; no legacy scratch-compiler assertion |
| Gaussian lowering | quadratic \(\mathbb Z/4\) phase formulas, ON basis construction | exact including translations and downward moves |
| three-stage cover | literal routes (7.1), projector identities (7.3), dirty endpoint (7.4), FBF | full arbitrary-owner proof; finite group not enumerated |
| positive deficit | complete local paths, all centers, final rank-two endpoints | proved; no zero-copy substitution |
| moment certificates | paid histogram, rational log/exp bounds | exact checked at depths 1–6; universal bound (9.1) proved |
| asymptotic rate obstruction | maximum child rank, recursive histogram and dominated convergence | proved for this family's moment threshold |
| all-size WHT RAM theorem | matrix-indexed padding, dilation, paid routing, strong induction | proved in the explicit model; not imported from S or P390 |
| cyclic DFT / Family 130 transfer | would need an additional actual Fourier-transfer proof | not completed or assumed |
| Family 109 integer multiplication | would need precision, encoding, fixed-tape scheduling and recovery | not completed or assumed |
| P193/PR390/PR401 numerical claims | pinned source text and selected arithmetic/byte checks | source claims except for expressly checked identities; no blanket validation |

The `source-audit/archive-verification.json` file contains every supplied source path, commit, byte hash, and the complete missing-artifact ledger. `PR401-READ-AUDIT.json` records exactly which separately retrieved texts were read and their Git blob identifiers. The preserved notice carries the upstream attribution. The final archive contains only the new report, new code, finite certificates and these audit records—not an executed or modified source repository.
