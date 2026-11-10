# One causal odd stage forces the 5q pair rank bound

This external written review of thu-nmrc PR6717 section5 proves a weaker-hypothesis form of its odd-pair implication. Neither stage map needs to be idempotent, and only **one** needs its own complete-prefix commutation. The other query remains two-sided compatible and the two maps still commute. The generic closure/rank-defect method and source5q bound retain predecessor credit; this is no full7q theorem or physical/cost admission.

## 1. Exact statement and inherited interface

Let K be a commutative field of characteristic different from2, including characteristic0. Let n>=4 be even, q>=1, and i<j distinct odd indices in{1,3,...,n-1}. Work on X=K^n tensor K^q. The inherited common canonical query tuple and complete-prefix formulas from source sections2–3 are:

    a_s=sum_(k=0)^s (-1)^k e_k,
    h_s=sum_(k=0)^s e_k^T,       tail_s=sum_(k=s+1)^(n-1) e_k^T,
    v_s=h_(s-1)-tail_s,          h=sum_(k=0)^(n-1) e_k^T,
    J_s=diag(-I_(s+1),I_(n-s-1)),
    R_s=(e_s v_s) tensor I_q,
    B_s=(J_s+2a_s h) tensor I_q.

Here B_s is the actual complete chronological prefix in that canonical interface. The common-normal-form reduction and source-to-caller realization are inherited; this note does not independently admit them. All unknown maps below act on the entire nq-dimensional space and may have arbitrary coupled, noncommuting internal q-by-q blocks.

Let P_i,P_j be arbitrary K-linear endomorphisms satisfying

    P_s R_s=R_s P_s=R_s         for s=i,j,
    P_i P_j=P_j P_i.

Assume **at least one** of P_i B_i=B_i P_i or P_j B_j=B_j P_j. Then

    rank(P_i)+rank(P_j)>=5q.                               (T)

No P_s^2=P_s, second-prefix condition, minimal-rank hypothesis or tensor structure for P_s is required. Conjugating this statement by one common invertible ordinary basis preserves every hypothesis and rank. Tensor notation applies to the fixed source matrices, not a scalar classification of unknown stages.

## 2. The retained prefix forces a fixed summand without idempotence

Call the prefix-constrained map P, at site s; call the other map Q, at site t. Put U_s=e_s tensor I_q and V_s=v_s tensor I_q. U_s is injective and V_s surjective, so two-sided query compatibility implies P U_s=U_s and V_s P=V_s. For odd s, direct contraction of the stated prefix gives

    B_s e_s=-e_s+2a_s,          v_s B_s=2h_s-v_s.

Using [P,B_s]=0 and cancelling2 therefore yields P a_s=a_s and h_s P=h_s. Also

    h_s e_s=1,  h_s a_s=0,  v_s e_s=0,  v_s a_s=1.

Thus, with all scalar factors tensored by I_q,

    A_s=(e_s,a_s),        C_s=(h_s;v_s),
    C_s A_s=I_(2q),       E=A_s C_s,
    E^2=E,               rank(E)=2q,       PE=EP=E.

In the decomposition X=im(E) direct-sum ker(E), the arbitrary map P has block form diag(I_(2q),T). Hence

    F=P-E=diag(0,T),       rank(P)=2q+e,   rank(F)=e>=0.    (1)

F need not be idempotent. This direct-sum rank equality, rather than F^2=F, is the property needed below. The only division in K used here is by2.

## 3. A fixed-space rank lemma for an arbitrary linear map

Suppose Q fixes every vector of an a-dimensional column space A0, every row r in a c-dimensional row space C0 satisfies rQ=r, and C0 A0=0. Then

    rank(Q)>=a+c.                                         (2)

Indeed A0 lies in im(Q). Restriction of C0 to im(Q) is injective as a map of row spaces: if r annihilates im(Q), then rQ=0, so r=rQ=0. The row map C0 on im(Q) therefore has rank c, and its kernel contains A0. Rank-nullity proves(2). No Q^2=Q is used.

**Image/row containment alone would be false.** For Q=e0 e1^T on K^2, im(Q)=span(e0), row(Q)=span(e1^T), and their pairing is zero, but rank(Q)=1<2. Neither space is fixed. In particular the argument must never substitute the false non-idempotent identity(I-Q)Q=0.

## 4. The other odd query has a zero-paired 2q+2q closure

Let U=e_t tensor I_q and V=v_t tensor I_q for the other selected query. Compatibility gives QU=U and VQ=V. Define A=span(U,EU) and C=span(V,VE). In both orientations these spaces have dimensions2q and2q, with CA=0.

If s=i<t=j, ordered contraction gives

    E_i e_j=-a_i,           v_j E_i=h_i,
    A=span(e_j,-a_i),       C=span(v_j,h_i).

The four pairings vanish: v_j e_j=v_j a_i=h_i e_j=h_i a_i=0. A has unit minor on rows(j,0) equal to diag(1,-1). C has unit minor on columns(i+1,0) equal to[[1,1],[0,1]].

If s=j>t=i, put t_j=e_j^T+tail_j. Then

    E_j e_i=e_j+a_j,        v_i E_j=-t_j,
    A=span(e_i,e_j+a_j),    C=span(v_i,-t_j).

Again CA=0: v_i e_i=t_j e_i=0, v_i(e_j+a_j)=-1+1=0, and t_j(e_j+a_j)=1-1=0. A's minor on rows(i,i+1) is[[1,-1],[0,1]]; C's minor on columns(0,j) is[[1,-1],[0,-1]].

All minors have determinant±1. At widthq they become invertible block minors with±I_q, so the dimension claims hold over every allowed field and for arbitrary q. Distinct odd sites have i+1<j; therefore these same minors cover j=i+2, i=1, j=n-1 and the smallest n=4 pair(1,3). No larger-dimension boundary argument or sampled width is used.

## 5. Leakage produces actual fixed vectors and fixed rows

Use P=E+F, [P,Q]=0, QU=U and VQ=V. Directly,

    (I-Q)PU=PU-PQU=0,
    VP(I-Q)=VP-VQP=0.

Consequently

    (I-Q)EU=-(I-Q)FU,       VE(I-Q)=-VF(I-Q).              (3)

Each right side has rank at most e=rank(F). Thus I-Q restricted to A has rank at most e, while right multiplication by I-Q on C has rank at most e. Their kernels give

    A0=A intersect Fix(Q),              dim(A0)>=2q-e,
    C0={r in C:rQ=r},                  dim(C0)>=2q-e.

Negative lower bounds are vacuous. The zero pairing CA=0 persists on C0 A0. Applying(2) to these **fixed** spaces gives

    rank(Q)>=4q-2e.                                      (4)

The original query factors U,V themselves have dimensionsq,q, zero pairing VU=0, and are fixed by compatibility. Applying(2) separately gives rank(Q)>=2q. Combining with(1),

    rank(P)+rank(Q)
      >=2q+e+max(2q,4q-2e)
       =4q+e+max(0,2q-2e)>=5q.

For e>=q, the last bound uses rank(Q)>=2q. For e<=q, (4) gives6q-e>=5q. These final comparisons concern integer dimensions; they perform no division in the field. This proves(T) for either retained-prefix orientation.

## 6. Written controls for the exact hypotheses

**Mutual commutation matters.** Take P_i=E_i and P_j=E_j. Both are compatible rank2q projectors. For A_s,C_s above and M=[[-1,0],[2,-1]] tensor I_q, direct contraction gives B_s A_s=A_s M and C_s B_s=M C_s, hence each commutes with its own prefix. Their ordered products are

    E_i E_j=-a_i t_j,       E_j E_i=(e_j+a_j)h_i.

Their commutator has rank2q: its scalar minor on rows(0,i+1), columns(j,i) is[[-1,-1],[0,-1]], and its displayed factorization has rank at most2. Thus rank sum4q violates(T) precisely when mutual commutation is omitted.

**Local compatibility cannot replace every prefix condition.** Put

    P_*=(e_i v_j-e_j v_i) tensor I_q,       P_i=P_j=P_*.

The cross pairings v_i e_j=-1 and v_j e_i=1 show P_* is a rank2q idempotent fixing both query images and supporting both query rows. The maps commute, but their rank sum is4q. For either s=i,j, [P_*,B_s]e_s=2(P_*a_s-a_s) has coordinate0 equal to-2I_q, since im(P_*) is supported only at i,j while(a_s)_0=1. Hence **neither** own-prefix condition holds. This control removes all prefixes, not each individually; the theorem needs only one.

**Characteristic2 is excluded substantively.** Reduce the same canonical matrices and P_* modulo2. Every actual query prefix is I because I-2R_s=I. Both prefix conditions, compatibility and mutual commutation now hold, yet rank sum4q<5q. This is a hand countercontrol to extending the displayed canonical matrix implication to characteristic2, not a counterexample in its allowed domain. The endpoint degenerates to I=-I there; it does not assert an n+1 word is minimum length in that characteristic.

**The relaxed interface is strictly larger.** Retain P=I at one odd site and set Q=2I-P_* at the other. Q is compatible, commutes with P, fails its own prefix and satisfies Q^2-Q=2(I-P_*)≠0. Thus the enlarged domain contains genuinely non-idempotent maps without a second prefix condition. This full-rank example makes no claim of5q sharpness or useful physical stage realization.

All controls are hand matrix/rank arguments, not executed finite tests. Source normal-form/prefix admission and the source's separate attainment, even-site and far-endpoint branches are not re-certified here.

## 7. Evidence boundary and credit

Two separate source-aware AI derivations agree on this implication, followed by independent adversarial written review. No scientific program, source checker, finite matrix grid, proof assistant, native suite, Lean or Docker was read/run for this result. Metadata/hash/archive checks authenticate retained bytes only; hosted helper CI is not mathematical acceptance. Arbitrary internal coupled blocks were never commuted or classified by tensoring scalar stages.

Credit thu-nmrc PR6717 for the original odd-pair5q/arbitrary-three7q application and author proof/checks; Ali Romman PR6398 and alternating-caller-closure lineage for common normalization, forced odd projectors, closure and low-rank correction/curvature tools; Cinna Davis and retained query/controller contributors. PR6721's far-endpoint audit supplies credited generic leakage precedent, not newly counted coverage; ferdy252 PR6731's attainment audit is separate and supplied the released lower-bound handoff. The fixed-space rank-nullity method is classical. This source-aware written application/refinement uses substantial OpenAI Codex assistance for ToikY and claims no human/kernel acceptance, full7q extension, physical/native/paid bound, framework discharge, new κ, adoption or frontier change.
