# Real physical normalizers for the coded producer

This is local constructive research on canonical/pr4929, not a completed supplier or exponent claim. Source code and Gaussian conventions retain the original authors' credit.

Let n=9 and let q be any of the source's 112 port vectors (weight 3 or 7). Let e0=1. Construct an orthogonal binary matrix G taking e0 to q. If q_0=0, use the orthogonal transvection T_(e0+q). If q_0=1, select j>0 with q_j=0 and use T_(ej+q) T_(e0+ej). Here T_v(x)=x+(v dot x)v; both v have even weight, hence T_v is orthogonal. Such j exists because q is not the all-ones vector.

For row j of G put z_j=(wt(row_j G)-1)/2 modulo 2. Define K=Z_z P_G. It is a real signed permutation. The full Gaussian R has entries alpha*(-i)^wt(x+y), with alpha=(1+i)^9/2^9. Orthogonality gives

wt(G^-1 d)-wt(d) = 2 z dot d (mod 4).

Indeed the degree-two coefficients vanish modulo four because distinct columns of G^-1 have even dot product; the linear coefficient is the weight of that column minus one. Therefore K R K^-1=R exactly, including absolute phase. K also maps the central line to span(q), and its orthogonal complement to q-perp, at the canonical-frame Lagrangian level. All these statements tensor to every positive digit-column count.

Let Q be the central C gate, D the product of the other eight C gates, so R=DQ. Let E_i and S_i be the actual retained entrance-line and exit-hyperplane frame operators. With the operator convention that rightmost applies first, use

input X: E_i K_i Q^-1
input Y: K_i
output X: K_i^-1
output Y: D K_i^-1 S_i^-1.

All four wrappers are monomial. Their Lagrangian incidences prove this for every port, and the scratch verifier checks exact tableaus and absolute phases at every one of the 112 source ports. With A from PR4929, define C_ij= A_ij K_i^-1 K_j. Then the full main endpoint is

F = diag(D,D) [[I,0],[C Q^-1,I]].

C is a physically implementable fixed owner recoding: apply K_i to each owner, apply A among the owners at common physical coordinates, and apply K_i^-1. Its inverse uses A^-1=(A+12I)/13. Since each K_i is real orthogonal and A is real symmetric, C^T=C. Since K_i commutes with R, C commutes with R. The polynomial C^2+12C-13I=0 follows by similarity. The 408 independent helper jobs and every paid Gaussian child are unchanged.

For the actual raw inverse transpose, F^-T=diag(D^-1,D^-1) [[I,-Q^-1 C],[0,I]], since Q,D are symmetric. Multiply both outputs by D^2, then conjugate the physical X bank by Q^2 (input Q^-2 and output Q^2). These are explicit monomial powers. The result is

B = diag(D,D) [[I,-Q C],[0,I]].

The old source convention using Y-only Q^2 conjugation cannot simply be copied for noncommuting C. The X-only convention above is exact.

For a prior code B0 commuting with the current D, set G(B0)=diag(B0,Q^-1 B0 Q). The following two constructive local identities hold without requiring C and Q to commute:

(post X C) F (pre Y C) = G(C B0) F_standard G(B0)^-1,
(post X C^-1) B (pre Y C^-1) = G(C^-1 B0) B_standard G(B0)^-1.

They use [C,DQ]=0 and [B0,D]=0. Every additional operation on the left is physically cheap fixed recoding. For disjoint fresh blocks, codes from earlier stages commute with the current D. These identities do not yet settle interstage ADD/IDLE compatibility, terminal gauges, productive jobs, or the complete moment.

## Literal recoding and complete local bill

The source code has an exact factorization A=I-MM^T/4 with M a 112-by-8 matrix having entries 0,+1,-1 and M^T M=56I. Each mode column has 56 nonzero entries, and each owner row has four. The mode columns are emitted in NORMALIZERS.json and all 12,544 entries are checked against the pinned CODE.json. This factorization is used here as a constructive scalar program, without relying on any common physical address chart for separate Gaussian mode transformations.

To execute A on arbitrary independent owner fields x, allocate eight owned zero fields t. Compute t=M^T x with 448 signed ADDs; update x-=M t/4 with 448 scaled ADDs; clear the eight owned temporaries. Reading x is finished before any x is updated. Hence no input field is overwritten before its last source read. For A^-1 use the same program with coefficient -1/52, since A^-1=I-MM^T/52. Both are exact rational linear programs. The helper fields of the native producer are never used as scratch, copied as free credit, or erased.

Conjugating this scalar program by the 112 K_i and their inverses implements C or C^-1. This pays 224 monomial field maps, 896 scalar ADDs and 16 owned CLEARs per recoding, with eight owned fields reusable sequentially. The two additional recodings in either local gauge identity therefore cost at most 448 monomial maps, 1,792 scalar ADDs and 32 CLEARs, with no recursive Gaussian child. The four actual port normalizers contribute 448 monomial maps per native invocation. The displayed backward conversion contributes at most 448 further monomial maps (112 input X powers, 112 output X powers and 224 output D-squares); fusing maps can reduce this upper bound but is not assumed.

These are field-level operation counts. A lifted K_i is an explicit binary map on nine f-bit address blocks together with signs given by block parity. Its constants, indexed movement and phase passes use the retained native monomial implementation. It is therefore a fixed finite O(V polylog p) nonrecursive operation under that caller's precision/address ABI, not a zero-work instruction. Each fixed rational ADD is likewise charged at its actual scalar precision. In particular the inverse denominator 52 must be implemented and rounded; no free exact real-division oracle is assumed. This lemma makes no independent TM tariff or outer-budget claim.

The maximum exact component-l1 prefix bound for the scalar A program, including its temporaries, is 57. For A^-1 it is 56 (the output-only bound is 69/13). Signed monomial maps preserve component magnitude. A fixed local sequence has a fixed suffix bound obtained by multiplying elementary bounds 1+|coefficient|; owned CLEAR has bound one. This gives a finite bound for local rounding propagation. The number of local uses, compiler precision and complete outer error allocation still belong to the caller theorem.

The normalized producer still has its exact PR4929 paid profile

    {1:2201, 2:412, 3:510, 4:127, 5:40}

and independent helper profile

    {4:28, 7:7, 8:47, 9:326}.

No productive main ranks are asserted merely from the coupled central ABI. Those depend on the completed caller, its initial/final gauges and every paid correction.

## Universal scope and reproducible evidence

PR4929 supplies the arbitrary-input logical identity over Q[FreeGroup72] for its emitted center-free word with ground-chart helper pre-compensation. Its normalized main endpoint is L(A), its raw dual is L(A)^-T, and every one of the 408 helper endpoints is autonomous. This proof is an inherited premise with exact source pins, not a consequence of this normalizer checker. The present wrappers and owner recodings act exclusively on the 224 main fields; new scratch is explicitly owned. Thus the helper block remains autonomous and its independent inputs, requested transforms and paid profile remain unchanged.

For every f>=1, assign the shared native letters their actual consistent invertible lifted operators. Evaluation of the source free-group algebra is a homomorphism and gives the source logical identity. Independently lift each K_i as its f-fold tensor product, retaining spectator coordinates; its signed-permutation word, the two direct frame identities and its commutation with R lift by operator composition. In every compiled monomial word, P and X act columnwise on the f-bit blocks, D sums its Z4 polynomial over the f columns, and a one-column scalar phase i^gamma becomes i^(f*gamma). Reusing the one-column global phase unchanged would be incorrect. Finally form the owner matrix C_f with entries A_ij K_i,f^-1 K_j,f. One does not tensor the whole 224-by-224 owner matrix and does not assert that tensor powers preserve sums. Instead the finite scalar owner program is evaluated directly in the algebra of these lifted address operators. This proves the central ABI and local gauge identities at every positive width.

Run `python3 -I -B research/coded-native-caller/normalizers.py` or its optimized `-O` form. The checker authenticates the decompressed actual native payload, CODE.json and retained Clifford source before executing the latter. It verifies all 112 real signed normalizers, 57,344 explicit weight-congruence addresses, 896 forward/backward monomial wrappers and eight exact frame/block identities per port, including absolute phase. Each emitted wrapper is separately lowered to a literal P/D/X/phase-only word and checked against its defining expression by exact tableau and absolute-phase state. No C gate remains in an emitted wrapper. The independent incoming-column and outgoing-row identities imply all 5,824 nonzero off-diagonal code blocks, without sampling those pairs. It also executes the eight-mode recoding on all 112 arbitrary-input basis columns in both directions. Omitting the essential signed phase is rejected at every affected port. The default command compares a regenerated mathematical receipt and performs no writes; `--write` is the explicit authoring path.

Source pins: canonical main 624de9dc66858af0945e5f8a0942488d62280d43, `research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz`, decompressed SHA-256 cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd; PR4929 head 361f5d4100640177d6a983dd2f336021c75bfd5e, `research/native-center-free-code/CODE.json`, SHA-256 8be7f3f073b7981ec91c6af43edff0ac8a89f4824ef6026ae758c287dd6c03d0; canonical `research/t74-native-fast/vendor/native/new/code/borrow/vendor/clifford/clifford_exact.py`, SHA-256 2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962. Gzip container bytes are not substituted for decompressed source identity.

Credit Dugongue's PR4929 for the coded producer and stable code; Cinna Davis's PR4694/4698 and the original cache/helper construction; Cao Yifan's PR4610 native word; the retained zxv, Jacob Alan Sussman, Cinna Davis and Clifford/native/compiler lineage. The exact canonical-frame implementation and phase conventions are retained source material. The constructive real centralizing normalizers, their explicit lifted words, X-only raw-dual convention and costed local code gauges are the additions here. New work is Apache-2.0 and has substantial OpenAI Codex assistance; no formal-kernel or independent human acceptance is asserted.
