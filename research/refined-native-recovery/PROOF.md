# Optimal two-stage refined recovery over mode-preserving integer frames

This theorem concerns the literal 112-by-8 integer matrix from
[#5444](https://github.com/CrocSwap/integer-mult-bounds/pull/5444), pinned
in SOURCES.json. It gives a minimum abstract recovery alphabet for a
specified family of changed output functions. It does not give a paid
physical memory saving, a supplier invoice, or a new multiplication exponent.

## 1. Exact statement

Let R be componentwise nearest-integer rounding with half ties away from
zero, and let

    K(z)=z−M R(Mᵀz/52),             z∈Z^112.

The actual source satisfies MᵀM=56I8 and

    C=ker_F2(M mod2)=row_F2(M mod2),
    |C|=16,       W_C(a,b)=a^8+14a^4b^4+b^8.

These finite source identities are inherited from #5444 and independently
rechecked on its pinned fixture. All indices below are zero-based.
Let G be the class of all fixed, known matrices

    U∈GL_112(Z) with MᵀU=Mᵀ,

without imposing U≡I modulo two. For U∈G define the output function

    H_U(x)=K(U K(2x)),             x∈Z^112.

The factor 2 is exactly one relative precision bit before the first call;
there is no additional refinement before the second. Only the declared
final output H_U(x) and a tag are available for exact recovery. Put

    F=W_C(7,6)=(13^8+14·13^4+1)/16=51,008,161.

**Theorem.** The optimal worst-case fiber over this entire class is

    min_(U∈G) max_y |H_U^−1(y)| = F²
                                = 2,601,832,488,601,921.       (1)

A frame attains this minimum if and only if

    im_F2(M) ∩ im_F2(U^−1M) = {0}.                            (2)

An explicit integer frame satisfying (2) is constructed in Section 3.
For it the zero output attains the maximum. Consequently its minimum
fixed recovery-tag alphabet has F² states and its packed width is 52 bits.
By contrast, every frame in the parity-I subclass has sharp two-step
maximum A2=(13^16+14·13^8+1)/16=41,588,538,787,713,121, requiring 56 bits.
The output map changes with U; this is not a claim that a caller can
retain its original output contract and save four physical bits.

The separate [CHAIN_PROOF.md](CHAIN_PROOF.md) proves the complementary
all-finite-depth formula A_t=(13^(8t)+14·13^(4t)+1)/16 for mode-preserving
parity-I frame sequences, including genuinely noncommuting ones. Its
scalar lemmas and full chronology are restated where needed below.

## 2. Full two-step fiber parametrization and universal lower bound

For a final output y put s=Mᵀy, coordinatewise, and define

    Q(s)={q∈Z: R((s+56q)/52)=q},
    F_s(T)=T−R((s+56T)/52),
    I2(s)={T: F_s(F_s(T))=0}.

The scalar interval proof in CHAIN_PROOF.md, Section 2, shows that Q(s)
is a nonempty interval of length at most 13, I2(s) is a nonempty interval
of length at most 169, and

    F_s^−1({w})=w+Q(s+56w).

The half-away convention is retained even at endpoints. At s=0,
Q(0)=[−6,6] and I2(0)=[−84,84]. For every U∈G the actual fiber is in
bijection with the eight-coordinate total quotient T satisfying

    T_j∈I2(s_j),       U^−1(y+Mq2)+Mq1 is even,              (3)
    q2=F_s(T),         q1=T−q2.

Indeed reverse chronology gives

    x=(U^−1(y+Mq2)+Mq1)/2.                                 (4)

Integrality is exactly the second condition in (3). Mode preservation
shows that the two actual pre-kernel modes are s+56T and s+56q2,
respectively, so their rounded quotients are precisely q1 and q2.
Thus forward execution returns y. Conversely any actual preimage gives
these quantities. Distinct T give distinct inputs because

    2Mᵀx=s+56T.                                           (5)

For the universal lower bound in (1), take q2∈[−6,6]^8 with q2 mod2∈C.
At y=0 the first quotient lies in

    q1∈Q(56q2)=[−6,6]^8−14q2.

This translation is even and has no half ties. The choices with q1 mod2∈C
number F for every such q2, and the choices of q2 number F. Both Mq1 and
Mq2 are even. Since U^−1 is integral, every one of these F² pairs gives
an actual input by (4) for every U∈G. No two pairs give the same T,
since q2=F_0(T), and (5) then proves input distinctness. Consequently
|H_U^−1(0)|≥F² universally. This is constructive attainment, not a
volume or determinant lower bound.

## 3. Explicit source-sized frame and binary image separation

Let E have rows e0ᵀ,e1ᵀ,e2ᵀ,e4ᵀ, and let V have columns

    v0=e64−e65−e96+e97,
    v1=e10−e11+e62−e63,
    v2=e14−e15+e41−e42,
    v3=e18−e19+e39−e40.

Their disjoint supports exclude 0,1,2,4, so EV=0. Write ρ_i for row i
of M and f7 for the last standard mode vector. The pinned rows satisfy

    ρ64−ρ65=−2f7=ρ96−ρ97,
    ρ10−ρ11=−2f7,      ρ62−ρ63= 2f7,
    ρ14−ρ15= 2f7,      ρ41−ρ42=−2f7,
    ρ18−ρ19=−2f7,      ρ39−ρ40= 2f7.

Thus MᵀV=0 exactly. Set U=I+VE. Then (VE)²=0,
U^−1=I−VE is integral, and MᵀU=Mᵀ, proving U∈G.

For the quotient condition let L have rows

    (e4+e64)ᵀ, (e10+e70)ᵀ, (e14+e52)ᵀ, (e18+e54)ᵀ.

The paired source rows have identical binary masks 153,165,170,150,
respectively, hence LM=0 modulo two; the displayed supports give LV=I4
over the integers. Therefore the four V columns are independent modulo
im(M mod2). The rows of EM have binary masks 15,51,85,153 and rank four:
the first three span {0,15,51,60,85,90,102,105}, excluding 153.
Their span is C, so ker_F2(EM)=C.

If Mp=(M−VEM)q modulo two, then M(p−q)=−VEMq. Multiplying by L gives
EMq=0; hence q∈C and the common vector is zero. This proves (2).
The source identities, exact inverse and full binary ranks are checked
independently. The frame is four commuting sparse transvections, with
16 signed coordinate additions algebraically; these are not paid machine
tariffs. It need not commute with the rounded kernel.

## 4. Scalar joint-parity Fourier bound


Define a two-by-two integer table and its binary Fourier coefficients by

    w_s(p,q)=#{T∈I2(s): T mod2=p, F_s(T) mod2=q},
    ŵ_s(α,β)=Σ_(p,q) (−1)^(αp+βq) w_s(p,q).

At s=0 the interval is [−84,84] and F_0(T)=−R(T/13), giving

    w_0 = [[49,36],[42,42]],
    (ŵ_0(0,0),ŵ_0(1,0),ŵ_0(0,1),ŵ_0(1,1))=(169,1,13,13).

We prove the componentwise bound

    |ŵ_s(α,β)| ≤ ŵ_0(α,β)  for every integer s.             (W)

Here are the complete cases, retaining signs at ties. The exact quotient
endpoints obey

    ceil((-26−s)/4) ≤ q ≤ floor((26−s)/4),

where the lower extreme at residual −26 requires q≥1, and the upper
extreme at residual +26 requires q≤−1. If s is not 2 modulo 4, there are
no endpoint ties, Q(s) has length 13, and

    Q(s+56q2)=Q(s)−14q2.

The parity counts of both q2 and q1 are therefore 7 and 6, with a fixed
preferred q1 parity independent of q2. Since p=q1+q2 and q=q2, the table
is a row/column permutation of w0. Such permutations only change signs
of Fourier coefficients, proving (W) in this case.

For the tie case write s=4k+2. The exact intervals are

    k≥7:       Q(s)=[−k−6,6−k],
    −7≤k≤6:   Q(s)=[−k−6,5−k],
    k≤−8:      Q(s)=[−k−7,5−k].                            (5)

If s≥34, then k≥8 and every q2∈Q(s) satisfies
s+56q2≤338−52k≤−78. Hence the inner quotient interval is in the last
case of (5) and is

    Q(s+56q2)=[−k−7,5−k]−14q2.

All outer and inner intervals again have length 13 and a fixed preferred
q1 parity, so the same Fourier conclusion follows. Oddness of R sends
(s,T,q2) to (−s,−T,−q2), preserving both parities. Thus w_−s=w_s and the
case s≤−34 follows too.

Only s=±2,±6,...,±30 remain. Using (5), each table follows from the finite
identity w_s(p,q)=Σ_(q2∈Q(s),q2≡q) #{q1∈Q(s+56q2):q1+q2≡p}.
The eight nonnegative representatives are:

|s|w_s (rows p, columns q)|Fourier coefficients (00,10,01,11)|
|---|---|---|
|2|[[38,39],[39,39]]|(155,−1,−1,−1)|
|6|[[39,38],[38,40]]|(155,−1,−1,3)|
|10|[[37,40],[40,38]]|(155,−1,−1,−5)|
|14|[[40,37],[37,41]]|(155,−1,−1,7)|
|18|[[36,41],[41,37]]|(155,−1,−1,−9)|
|22|[[41,36],[36,42]]|(155,−1,−1,11)|
|26|[[36,42],[42,36]]|(156,0,0,−12)|
|30|[[42,42],[36,48]]|(168,0,−12,12)|

These complete (W). Entrywise domination by a permuted w0 is false, for
example at s=2; the proof specifically uses absolute Fourier domination.

## 5. The sharp all-output upper bound and necessity

Suppose (2) holds. Reducing (4) modulo two gives

    Mq1+U^−1Mq2=U^−1y.

Disjointness implies that this equation either has no solution or uniquely
fixes each of Mq1 and U^−1Mq2. Their binary kernels are both C. Thus
(q1 mod2,q2 mod2) ranges over one affine coset of C×C. Under the
invertible change (p,q)=(q1+q2,q2), the kernel is still C×C.

For any fixed modes s=Mᵀy the full fiber count is therefore the product
weight of an affine coset b+(C×C) under the eight scalar tables w_sj.
Since C is self-dual, character orthogonality gives exactly

    1/256 Σ_(h∈C×C) (−1)^(h·b) Π_(j=0)^7 ŵ_(sj)(h_pj,h_qj).

The absolute coefficient bound in Section 4 and the triangle inequality
bound this by the same sum with all factors replaced by their nonnegative
w0 coefficients and all signs positive. That sum is the actual zero-output
fiber, since y=0 gives s=0 and b=0. At zero the q1,q2 parities separate,
and Section 2 counts precisely F². This proves the all-output upper bound
and the sufficiency direction of (2), completing (1).

For necessity, suppose the two binary images have a nonzero common vector z.
Choose binary quotient cosets mapping to z under M and U^−1M. Every binary
parity vector is represented in each of the nonempty 13-element scalar
intervals for q2 and q1 at zero, so these cosets give additional actual
inputs via (4). They lie outside the C×C family because z≠0. Their
trajectory and total quotient are unique by Section 2. Thus the zero fiber
is strictly larger than F². This proves the converse, without assuming an
unproved classification of coset weights.

## 6. Effective full-output codec and exact scope

For the explicit frame, let δ=Ly modulo two. Equation (3) is equivalent to

    Mp=y+Vδ,          (EM)q=δ+Ey,          p=T mod2, q=q2 mod2.

The first syndrome is either impossible or a C-coset; the second is a
C-coset. For every coordinate, enumerate at most 169 values of I2(s_j)
and partition them into four joint (p_j,q_j) cells. At most 256 code-pair
blocks then give exact Cartesian products. Mixed-radix rank/unrank within
these finite cells implements the full fiber bijection. It is effective
for every integer output, not merely zero. The executable validates the
literal forward result of every decode, and tests arbitrary nonzero
outputs, endpoint tags, all 256 zero-output blocks, and large integers.

Fixed known frames, unbounded exact integers, the specified relative grid,
and complete output access are assumptions of this interface theorem.
Input-dependent frames, mode-changing frames, prescribed finite ranges,
later extra refinement and longer parity-changing chains are not proved.
Arbitrary-precision arithmetic, finite storage, quotient workspace, owner
access, routing, reversible cleanup and restoration are unpriced. The
52-bit result alone does not discharge any selected framework assumption.

The output function H_U changes with U. Postcomposing by U^−1 does not
in general restore the unframed K(K(2x)) output. If a corrected procedure
must return exactly that unframed output with only a recovery tag and no
additional retained side data, its maximum fiber is again A2, forcing
56 packed bits. An actual accepting caller or a completely charged
restoration interface is required before asserting a physical benefit.
See COST_SCOPE.md for the reachable source witness and symbolic ledger.

The theorem resolves the two-step mixed-refinement question of #5444
within the full mode-preserving integer frame class, including all
parity-changing frames in that class. General mode-changing frames and
physical realization remain open. All five selected assumptions remain;
No new κ.

A concrete limitation prevents blindly extending the Fourier argument to
three parity-changing stages. Let q3∈Q(s), q2∈Q(s+56q3), and
q1∈Q(s+56(q2+q3)). The character sum Σ(−1)^(q2+q3) equals 13 at s=0
but −14 at s=2. For s=2 the outer (q2,q3)-parity counts are
38,39,39,39, with signed sum −1; every inner Q has length 13 except
(q2,q3)=(0,0), whose length is12. Thus the sum is 13·(−1)−1=−14.
The corresponding zero-mode sum is 13. This explicitly disproves the
same componentwise zero-coefficient majorant for three quotient parities.
It does not disprove a three-stage optimum or any different counting
argument. The exact two-case negative control is registered in this package.

Prepared for @CubeJerry with substantial OpenAI Codex assistance in
primary derivation/codec, separate source-frame construction, independent
proof/checker review, and the caller-cost audit. Credit zxv/#5444 for the
precision question and source one-step/code facts, Ali Romman/#5323 for
same-grid source counts, Brian/#5035 for the literal rounded kernel, and
all retained native/caller contributors. Character duality and mixed-radix
coding are classical. New proof and code are Apache-2.0. Independent human
acceptance or formal proof-kernel admission is not claimed.
