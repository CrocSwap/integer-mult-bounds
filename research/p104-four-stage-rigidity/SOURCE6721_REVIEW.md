# Independent derivation: zero-paired leakage at a far endpoint

External written audit of thu-nmrc PR6717, exact head `3c9072b8738323dda9f9c7dfb421d578ed3fc17a`, PROOF §6. Prepared by ToikY with substantial OpenAI Codex assistance, Apache-2.0. This is a source-bound proof review, not a new rank threshold or acceptance of the full theorem. No scientific program or proof kernel was run.

## Contract and verdict

**No gap found in §6 under the enumerated canonical-source premises.** The conclusion is that the sole-odd-site case contributes at least q extra stage dimensions: if the odd projector has rank 2q+e, one selected endpoint has rank 2q+f with e+f>=q. The other endpoint has rank at least 2q. This confirms this one branch of the source's 7q lower bound. The complete shortest-query normalization, canonical prefix formula, forced odd-projector fact and compatibility floor are inherited premises. We do not independently certify the even-interior branch, two-odd branch, all-n attaining word, physical realization or price.

Let K be a commutative field with char(K) !=2, n>=4 even, q>=1, W=K^(nq). Work in the source's common canonical coefficient frame. The sole odd interior site is i in {1,3,...,n-1}. In scalar notation a_i=(1,-1,...,(-1)^i,0,...,0)^T, h=(1,...,1), h_i is the initial all-ones row through i, v_i=h_(i-1)-tail_i, E_i=e_i h_i+a_i v_i. Tensor these scalar expressions with I_q; arbitrary P,Q,F themselves need not be tensor products and their internal blocks need not commute. The inherited forced-projector statement is P=E+F, E=E_i tensor I_q, EF=FE=0, F idempotent and rank(F)=e=rank(P)-2q. The selected endpoint Q is idempotent, QU=U, VQ=V, [Q,P]=0, for its rank-q query factors U,V. All three selected stages are pairwise commuting under the source contract.

## A general leakage lemma, proved directly

Let Q be an idempotent on a finite-dimensional vector space W over any field. Let A<=W have dimension a and C<=W* have dimension c, with every c0 in C annihilating every a0 in A. Define

    alpha = rank((I-Q)|A),
    beta  = rank(C -> W*, c0 -> c0(I-Q)).

Then

    rank(Q) >= a+c-alpha-beta.                         (L)

Indeed A0=ker((I-Q)|A)=A intersect im(Q), so dim(A0)=a-alpha. Likewise C0=ker(c0->c0(I-Q))=C intersect row(Q), so dim(C0)=c-beta. Restriction C0 -> (im Q)* is injective: if c0 vanishes on im(Q), then c0=c0 Q=0. Therefore the row map im(Q) -> C0* has rank dim(C0), over every field. Its kernel contains A0 because CA=0. Rank-nullity gives rank(Q)>=dim(C0)+dim(A0), proving (L). The two retained spaces are chosen as actual kernels; no incompatible choices of 'most' columns and rows, orthogonal projection, positivity, simultaneous diagonalization or scalar classification is used.

## Obtaining the leakage ranks from actual commutation

For A=im[U,EU], C=row[V;VE], use QU=U and PQ=QP:

    (I-Q) P U = (I-Q) Q P U = 0.

Substitute P=E+F to obtain (I-Q)EU=-(I-Q)FU. Similarly VP=VQP=VPQ, hence VP(I-Q)=0 and VE(I-Q)=-VF(I-Q). Each right-hand side has rank at most e. Since (I-Q)U=0, the image of (I-Q)|A is precisely the image of (I-Q)EU, not an additional q-dimensional U contribution. Thus alpha<=e. Since V(I-Q)=0, the row leakage map has image row(VE(I-Q)); beta<=e. Matrix order has been retained throughout.

If a=c=2q and CA=0, (L) gives rank(Q)>=4q-alpha-beta>=4q-2e. This remains correct when 2q-e is negative; the exact kernel dimensions are nonnegative and the weaker displayed bound can simply be vacuous. Compatibility separately supplies rank(Q)>=2q. No assumption e<=q or rank-minimality is used here.

## Checking the far-endpoint closure, including boundary n=4

All scalar indices below are zero based. The explicit formulas use unit minors, so their ranks do not depend on characteristic-zero arithmetic.

Left endpoint: U=u0=e0 and V=v0=-tail_0. For odd i>=3,

    E_i e0=e_i+a_i,     v0 E_i=-(e_i^T+tail_i).

The columns e0 and e_i+a_i are independent by their coordinates 0 and 1: the second column has coefficient -1 at coordinate1 while e0 has zero there. The rows v0 and -(e_i^T+tail_i) are independent by coordinates1 and i, giving a determinant of absolute value1. All four pairings vanish: v0 e0=0; v0(e_i+a_i)=-1+1=0; (e_i^T+tail_i)e0=0; and (e_i^T+tail_i)(e_i+a_i)=1+(-1)=0. Thus a=c=2 and CA=0.

Right endpoint: U=u_n=(-1,1,...,-1,1)^T and V=v_n=h. For odd i<=n-3,

    E_i u_n=-a_i,       h E_i=h_i.

The column pair u_n,-a_i has a unit minor at coordinates0,i+1; the row pair h,h_i has one at coordinates0,i+1. The four pairings are h u_n=0, h a_i=0, h_i u_n=0 and h_i a_i=0. Each vanishes by an even-length alternating sum, as n and i+1 are even. Again both closure dimensions are2 with zero pairing.

Tensoring the verified scalar closure spaces with I_q gives dimensions2q,2q and zero pairing. This step tensors the fixed canonical U,V,E, not the arbitrary selected Q or its extra dimensions.

A far endpoint always exists. If i>=3, use the left endpoint. Otherwise i=1 and n>=4 implies i<=n-3, so use the right. At n=4 the only odd cases are i=1 (right) and i=3 (left). This also covers i=n-1 using the left endpoint. No limiting argument or final-prefix substitution is required.

## Rank debt and precise scope

Write rank(Q)=2q+f. Compatibility gives f>=0 and the leakage bound gives f>=2q-2e. If e>=q, e+f>=q immediately. If 0<=e<=q, e+f>=2q-e>=q. Adding the untouched third stage floor2q gives the sole-odd selected-triple rank sum >=7q. This does not require that either of the odd and far-endpoint stages be rank-minimal.

The lemma (L), its compatibility derivation and closure unit minors work over arbitrary fields; the stated characteristic restriction enters through the retained shortest-query/forced-prefix normalization. It must not be removed from the original theorem.

## Written scope controls; no executable tests

1. **Near endpoint is insufficient.** At n=4,i=1, E_i u0=e0 and v0 E_i=v0. Both left closure dimensions are only1, not2. The proof must choose the right endpoint. This prevents silently applying the far bound to the near endpoint.
2. **Zero pairing is necessary.** Let W=K^2, Q=I, A=W and C=W*. Then alpha=beta=0 and rank(Q)=2, while a+c=4. Dropping CA=0 from (L) gives a false bound. The independent row/column dimensions alone do not add.
3. **Characteristic two cannot be imported into the original theorem.** In char2 let n=4,q=1, R_j=e0 e1^T for all five queries and choose the same P=diag(1,1,0,0) at three distinct sites. Each R_j is square-zero rank1; I-2R_j=I and the five-query product is I=-I. P is compatible, each chronological prefix is I, and the selected projectors commute, but the total selected rank is6<7. The source's char!=2 hypothesis is substantive for its displayed matrix-hypothesis formulation. In characteristic two this five-query word is not genuinely shortest: -I=I already has a zero-query realization. Thus this control refutes deleting the field restriction from those displayed hypotheses; it does not refute a different theorem that separately imposes genuine minimality, nor the leakage lemma itself. This is a hand-derived boundary counterexample, not a machine-checked receipt.

## Credit and remaining obligations

The rank budget, far-endpoint leakage application and uniform construction belong to thu-nmrc PR6717 with substantial OpenAI Codex assistance. Ali Romman PR6398 and alternating-caller-closure supply the scalar obstruction, forced projector/closure method and retained all-length tools; the complete coupled normal form and Cinna Davis's query/controller lineage remain predecessor credit. The kernel/rank-nullity presentation is an external review of those implications using classical linear algebra, not a claim of a newly discovered general rank lemma.

Remaining: independent review of the normal form/actual-prefix source bindings, the other two branches and all-n attaining word; native/helper physical realization, complete invoice, ownership/restoration, stock/precision/tape/compiler/recursive outer applications, and all five selected assumptions. No kappa/frontier change, supplier admission, human review or proof-kernel acceptance follows from this audit.
