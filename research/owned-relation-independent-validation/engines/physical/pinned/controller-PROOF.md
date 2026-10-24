# Construction and proof obligations

## 1. Exact predecessor and changed object

The input is PR4447 at commit `322e0ec764aa7ef7801383feb1f656e460dd8bed`, with its credited THREE-base native word, PR4441 helper-boundary retiming, and the added three-dimensional frame at B/480. `SOURCES.json` binds all external proof inputs by Git blob and SHA-256.

There are 632 persistent local fields: 224 main fields and 408 helpers. Each helper is an arbitrary independent input, not initialized scratch. The separate owned center is initialized and erased under the inherited native contract. None of its eight uses receives productive-input credit.

The patch retains the scalar order and coefficients in each orientation. It retains all native warp events and every main-field boundary. It changes 38 helper entrance frames, 47 helper terminal frames, and 414 scalar contact frames. A source pin accompanies every changed boundary or contact. The two orientations retain their exact inverse-transpose scalar correspondence.

The optional search jointly optimized both helper boundaries and every mutable scalar contact over the finite intervals of subspaces of F2^9. Fixed main and warp events bound those intervals. The largest quotient dimension was five, so its interval has 374 subspaces. The discovery model used one-hot frame choices and edge marginals, with negative whole-helper credit. Its floating-point solution is a proposal, not a certificate. The following construction and exact tests do not use its claimed optimum.

## 2. Frame-coordinate invariant

Let C_F be the source's exact canonical frame operator for subspace F. Interpret a field at frame F as C_F applied to its logical arbitrary value. For nested frames E contained in F, the paid transport is C_F C_E^{-1}. Its Fourier rank is dim(F)-dim(E). The implementation follows the source's `adjoint().then(...)` composition convention and lowers the operator itself, not only that rank formula.

At each scalar operation, all participating persistent fields are first moved into its declared common frame. A scalar linear combination commutes with the common frame operator. Therefore the operation implements the unchanged logical scalar step. A native warp is run only at its original pinned input frame, and leaves the original pinned output frame. This proves the invariant by induction through the complete chronological word.

At the end of the word, main fields have their unchanged original endpoints. Helper r has the whole residual C_{T_r} C_{S_r}^{-1}, where S_r and T_r are its new entrance and exit. Every checked S_r is a proper subspace of T_r. Its positive productive rank is dim(T_r)-dim(S_r). There is no duplicate field, discarded helper, clean-input assumption, or free temporary productive input.

The helper normalizers are recomputed on these whole-job boundaries. Every new transport and each distinct helper boundary is lowered in both orientations with exact Clifford tableaux and absolute phases. The receipt contains 423 distinct transport/boundary pairs, including 406 newly occurring transport pairs relative to PR4447. Two retained literal interpreters check the complete 632-column endpoint. The argument is the frame-coordinate invariant; the finite replay independently checks its application to the submitted circuit.

## 3. Complete local bill and uniform moment gain

Write H_r for productive helpers of rank r and P_r for paid jobs of rank r. The predecessor has

    H_old = {4:26, 5:2, 7:29, 8:42, 9:309}
    P_old = {1:2254, 2:514, 3:444, 4:103, 5:40, 8:8}.

The new word has

    H_new = {4:28, 7:7, 8:47, 9:326}
    P_new = {1:2237, 2:388, 3:494, 4:147, 5:36, 8:8}.

There are 408 helpers in both words. The new paid list has 3,310 entries, 53 fewer than the predecessor. Helper rank mass increases from 3,434 to 3,471, and paid rank mass from 5,290 to 5,327. Their difference remains 1,856. In particular, the improvement is not obtained by keeping old productive credit after removing paid work.

For 0<t<1, define the local surplus as sum H_r r^t minus sum P_r r^t. The new-minus-old surplus is exactly

    D(t) = 17 + 126*2^t - 50*3^t - 42*4^t + 2*5^t
           - 22*7^t + 5*8^t + 17*9^t.

The verifier first checks D(1)=0. It then encloses D'(t) on 128 rational subintervals covering [0,1]. On [l,r], positive terms use the upper bound for rank^r log(rank), and negative terms use the lower bound for rank^l log(rank). Every resulting upper bound is strictly negative. Thus D is strictly decreasing on [0,1], and D(t)>D(1)=0 for every 0<t<1. This proves a uniform local improvement, not just a favorable rounded score at the chosen saving.

The whole rank-eight center jobs are included in both profiles. Scalar work, helper normalizers, fixed monomial routes and owned allocation/erasure are included under the explicit finite nonrecursive allowances in RESULT.json. These allowances do not claim those operations are free.

## 4. The new p16 controller

Use the PR4440 constructor with p=16 and prefix length a=7, hence suffix length 8. Keep the thick stages {0,32,1,3,...,31}. There are 18 full native calls and 15 query-only shears. Each full call receives a fresh, disjoint set of 408 helper fields. Each query-only shear costs one rank-one job per port and contributes no helper or scratch productive credit.

CONTROLLER.json contains the complete emitted native/query/idle word and its rational scalar boundary programs. A separate literal Laurent replay checks every coefficient. The left and right boundary matrices transform it to the declared diagonal, with central exponents exactly +1 or -1. Changed query orientation and replacing a paid thin query by an unpaid full stage both change the operator and are rejected.

There are 112 port copies. Main productive ranks are 145 with multiplicity 224; ranks 17,25,33,41,49,57,65 each with multiplicity 448; and rank 73 with multiplicity 224. The matching whole-idle paid ranks are 16,24,32,40,48,56,64 with multiplicity 448, and rank 72 with multiplicity 224.

Add 18 copies of H_new to the targets, 18 copies of P_new to the paid list, and 112*15 additional rank-one paid queries. This gives the complete profiles recorded in RESULT.json. They have 10,928 independent productive fields, 64,620 paid jobs, target rank mass 239,886, and paid rank mass 239,134. Their surplus is 752 = 48*18-112. Literal event counting and independent whole-call substitution give exactly the same invoice.

The source contact and phase proof is local to one old nine-axis block and one fresh eight-axis block. It therefore applies at every thick p16 stage after embedding, with all other axes as spectators. The new helper boundaries do not change those main contacts. Their actual residual operators are supplied by Section 2. The BIT controller and its native rational charts remain unchanged.

## 5. Exact root, paid completion and splitting

Let T_t and P_t be the complete target and paid moments. The new root is enclosed strictly between 0.0030201659770 and 0.0030201659771, using t=1-C. An exact interval argument verifies that the surplus is decreasing for 0<=C<=1/20 and negative on the remainder 1/20<=C<=1. This is a fixed-invoice ceiling, not a global bound for other words.

Take TESTED = 0.003020155, tensor power v=1024, tail offset u=1/5, paid cutoff 20^v and productive floor 21^v. Define

    alpha = P_t/T_t,
    gamma = P_(t+u)/(20^u T_t),
    delta = 21 * (# productive fields)/(20^TESTED T_t).

Two independent rational interval implementations verify the positive raw margin. The first also certifies

    alpha < 1 - 10^-9,   gamma < 97/100,   delta < 97/100.

The p16 completion tail is larger than the predecessor's 19/20 limit; this package explicitly replaces that limit with 97/100. No old tail allowance is silently reused. The same exact block inequality (97/100)^128 < 1/16 handles both tails. The inherited paid-completion and higher-moment splitting theorem consequently bounds the normalized final paid moment by

    1/(1 + 1024*10^-9) + 4/2^32 < 1.

Every short productive job is completed on additional disjoint axes of its same arbitrary field. Every original or added large paid job is split with its full rounding surcharge. The strict inequality 20^64 < 21^63 gives paid/target separation. These are paid operations; no padded target appears without its completion charge.

## 6. Effective finite compiler and outer transfer

The raw ambient rank is 145, so the tensor ambient rank is 145^1024. Use theta=63/64 and logarithm power 1000 in the credited logarithmic compiler majorant. The verifier checks

    2*(20^1024)^64 <= (145^1024)^63,
    (1-TESTED)*145^(-1024*TESTED) > theta^1000,
    145^(1024*TESTED) < 2^1000.

Set kappa=0.00302015 and d=(TESTED-kappa)/7=1/1,400,000,000. The integer test

    (1,400,000,000*j + 1)^1000 < 2^j

passes at j=45,868 and fails at j-1. Thus the retained theorem supplies the sufficient uniform rank N=2^64,215,200,000,000. This is an existence construction with explicit finite constants. The resulting word is not materialized and no practical implementation claim follows.

The new local scalar and fixed-route bound remains below 10^7 per full call. Eighteen such calls, all 15 thin-query charges, every scalar controller and boundary operation fit the complete raw bound 10^9. The number of roles, private storage, coefficient matrices and tapes is finite for the compiled template. Their sizes affect the eventual threshold and are not claimed uniform while changing that template.

Retain the source BIT ordinary saving 0.0034, with atom exponent 0.004. Its delayed-cover, weighted-child, row-stock and conversion conditions are rechecked through the source package. Use complex uniform saving kappa+6d, followed by b=kappa+5d, a=kappa+4d, q=kappa+3d, epsilon=1-d, beta=1-3d, r0=d/10, stop=d and layout=d. All nine outer cost rows, 54 strict predicates and four functional guards pass exactly. The old BIT cap and closed exponent gaps are explicit rejected controls.

## 7. Status of the conclusion

Subject to the retained all-column/native and physical-operation contracts, owned erasure, whole-job matching, finite-template compiler closure, precision and fixed-tape bounds, analytic decomposition, prime avoidance and exact recovery, this construction gives the source framework's conditional multiplication saving kappa=0.00302015.

The submitted change establishes an exact finite native word and a fully charged conditional parameter transfer. It does not remove the inherited analytic or physical premises. It does not promote the selected frontier, certify global optimality, claim a runtime speedup, or claim independent human or proof-assistant acceptance.

Credits: zxv's native and higher-moment/logarithmic work; Jacob Alan Sussman's finite mixed-flow theorem; Cinna Davis's prior p7 padding, query-thinned and retimed constructions; and the unchanged credited scalar, Clifford, geometry and outer-ledger sources. New material was prepared for Cinna Davis with substantial OpenAI assistance, Apache-2.0.
