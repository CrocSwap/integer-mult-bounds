# Adversarial review: active local query lower bound

**Result:** I found no gap in the stated local theorem after making the scope conditions below explicit. This is a separately derived AI-agent mathematical review and binary coset census, not a proof-kernel result and not a lower bound for the global coded p2 caller.

## Precise scope

Fix a finite projective Clifford group G on a fixed number of one-column address axes, and its monomial subgroup H. Free field operators are finite scalar sums/products of the f-column tensor lifts of H; owner mixing, owned storage, COPY, fanout and CLEAR are allowed. Scalar coefficients and finite free circuit lengths may depend on f. Paid calls are chronological unary, zero-preserving linear maps on one field of that same address dimension. A paid map may be otherwise arbitrary. There are 112 arbitrary input fields x. Initial auxiliaries are independent arbitrary data, known constants, or free linear functions of x. They are not preexisting nonmonomial observations of x.

The target is Jx or (J-I)x, where J=Q^-1 C Q and C_ij=a_ij K_i^-1 K_j for the actual 112-port code. Then every exact such circuit at every sufficiently large width requires at least 112 paid unary field calls.

## 1. Right-coset separation

Put e=e0 and O=G_j^-1 G_k. Since the G's are orthogonal, O is orthogonal. Linear signed phases in K_j and K_k do not alter the binary symplectic blocks. The upper-right block of Q^-1 K_j^-1 K_k Q is

    B = (Oe)e^T + e(O^T e)^T.

For j=k it is zero. For j != k, distinct port vectors imply Oe != e. Orthogonality also gives O^T e != e. Over F2, each of the pairs (Oe,e) and (e,O^T e) is therefore linearly independent; the displayed factorization has rank two. Thus the conjugate is nonmonomial.

For fixed i, g_ij=Q^-1 K_i^-1 K_j Q obeys

    g_ij^-1 g_ik = Q^-1 K_j^-1 K_k Q.

Consequently g_ij H are pairwise distinct right cosets, and g_ij H != H for j != i. Projective scalar phases do not affect these assertions.

The independently written check_cosets.py reads the physical normalizer receipt and scalar code, checks the actual G's, and obtains 112 grade-zero self pairs and 12,432 grade-two distinct pairs. Every code row and column has 52 nonzero off-diagonal entries; all 112 diagonal entries vanish.

## 2. No free-column kernel

Let A_f be the twisted complex group algebra of H with the cocycle raised to power f; let R_f be the corresponding algebra of G. For any F0 in Mat_112(A_f), suppose (J-F0)w=0 with w in A_f^112.

In row i, every nonzero off-diagonal term a_ij g_ij w_j lies in the distinct right-coset subspace g_ij A_f, while all contributions from F0 w lie in A_f. Group-algebra basis independence forces g_ij w_j=0 for each supported (i,j). Multiplication by g_ij is invertible and a_ij is a nonzero scalar, so w_j=0. Each column has a supported off-diagonal entry, hence w=0. The vanishing diagonal is convenient but not necessary: arbitrary diagonal terms in A_f could be absorbed in F0. Replacing J by J-I changes only F0 and preserves the claim.

## 3. Chronological active-query kernel

Write y_t for the response of paid call t. Because every operation between calls is free and linear, each call input has a straight-line normal form

    B_t x + sum_{s<t} E_ts y_s,

where B_t is a 1-by-112 row over A_f and E_ts belongs to A_f. The final output has form F0 x + sum_t F_t y_t. This permits overwritten input registers, snapshots, feedback, fanout and arbitrary owned CLEAR: the normal form is a dependency identity, not an assumption of reversible storage.

Stacking the B_t gives a complex-linear map A_f^112 -> A_f^r. Since dim_C(A_f)=|H|, if r<112 this map has a nonzero kernel column w. On inputs x_j=w_j z, the first call input is zero and therefore y_1=0. Inductively every paid response vanishes. Correctness would then give (J-F0)w z=0 for every field vector z, contradicting the no-free-column-kernel statement once the group-algebra representation is faithful.

Independent dirty auxiliaries can be set to zero. Fixed affine constants can be removed by differencing executions; equivalently apply the argument to the homogeneous input dependence. Correlated inputs x_j=w_j z are a valid test of an identity required for all input tuples. They do not assume that the original independent jobs are allowed to share their arbitrary inputs in the claimed implementation.

## 4. Tensor lift and phase audit

Choose unitary representatives U_g of the projective group. For distinct projective classes, rho_gk=|tr(U_g^* U_k)/d|<1. Let rho be the maximum over the finite group. The normalized Gram matrix of U_g^{tensor f} has diagonal 1 and off-diagonal magnitude at most rho^f. Once (|G|-1)rho^f<1 it is positive definite. Thus the map R_f -> End(V_f), g -> U_g^{tensor f}, is injective for every sufficiently large f. Its multiplication uses the cocycle alpha^f, so no phase-divisibility restriction on f is necessary.

This threshold is uniform over all allowed scalar coefficients, control choices and free circuit lengths. A nonzero abstract (J-F0)w therefore supplies an actual vector z on which it is nonzero. No tensor power of an owner sum is replaced by a sum of tensor powers.

## Scope boundaries that must accompany the claim

- The result does not apply at every small width. At width one, linear dependence among Clifford matrices can make Gaussian maps free in the scalar span of monomials.
- It assumes the fixed finite columnwise Clifford alphabet. Arbitrary noncolumnwise or width-dependent address permutations are not covered by the finite-dimensional algebra argument.
- One paid call has one input field and one output field of the same address dimension. Wider calls, owner-to-address packing, or a simultaneous multi-field native primitive are not one unary call in this theorem.
- Preexisting saved nonmonomial functions of x must either be excluded or have their producing paid calls included. Hence the theorem is not a claim of 112 additional calls after arbitrary global-caller history.
- The result counts total unary calls, not Gaussian grade or a weighted moment. It does not itself exclude a global three-bank-query p2 construction.
- Data-dependent branching, data-dependent scalar coefficients, or nonlinear free arithmetic are outside the fixed linear-circuit contract.

## Evidence

Command:

    python3 -I -B research/coded-active-query-bound/independent.py

Result: PASS_INDEPENDENT_RIGHT_COSET_CENSUS; 112 self pairs grade 0; 12,432 distinct pairs grade 2; 5,824 supported off-diagonal code blocks.

Source SHA-256:

- CODE.json: 8be7f3f073b7981ec91c6af43edff0ac8a89f4824ef6026ae758c287dd6c03d0
- NORMALIZERS.json: ae8aad06aa5d1811d725895b3ab5a4f4daa9dcdd88294aa0d5f723e78bb1e0da

Prepared with substantial OpenAI Codex assistance. The packaged independent.py preserves the separately derived binary formulas, with portable paths, hash authentication, explicit checks that survive -O, and frozen receipt comparison. It imports no Clifford implementation. This review and the proof remain agent work, not independent human or formal-kernel acceptance.

## Addendum: sharp bounds for QP and PQ

Let P=(I-C)/14, so P_ij=b_ij K_i^-1 K_j with b_ij=(delta_ij-a_ij)/14. In particular b_ii=1/14 for the actual code.

For QP, define h_ij=Q K_i^-1 K_j. Every h_ij has grade one, hence lies outside H. For a fixed column j,

    h_ij h_kj^-1 = Q K_i^-1 K_k Q^-1,

which has grade two when i != k by the same orthogonal binary calculation. Thus the left cosets H h_ij are distinct. For any free F0, a left row v over A_f satisfying v(QP-F0)=0 must vanish: columnwise left-coset separation isolates each supported v_i, and b_ii != 0 ensures each row is supported.

At the final output cut, every circuit has the form output=F0 x+F y, where y collects its r paid unary responses and F belongs to A_f^{112-by-r}. If r<112, finite complex dimension gives a nonzero left kernel row vF=0. Correctness gives v(QP-F0)=0, a contradiction. This argument allows all chronological feedback because it uses only the final free decoder. Computing P freely and applying Q separately to its 112 resulting fields attains the bound.

For PQ, use k_ij=K_i^-1 K_j Q. These grade-one operators avoid H, and for fixed row i,

    k_ij^-1 k_ik = Q^-1 K_j^-1 K_k Q.

Their right cosets are distinct. This supplies the no-right-kernel property modulo free F0 and the earlier chronological input-cut lower bound of 112. Applying Q separately to all 112 input fields and then applying P freely attains it.

Therefore QP and PQ each have exact unary paid-field-call complexity 112 for every sufficiently large width under the same finite-alphabet/same-field/local-input contract. No new checker was required: the independently checked distinct-port grade-two assertion is precisely the shared combinatorial condition. The fact that P has ordinary owner-mode rank eight does not contradict these bounds; the free input/output cuts are over the monomial algebra, where the stated one-sided kernel obstruction is stronger than ordinary physical matrix rank.
