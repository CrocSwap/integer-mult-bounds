# Longer refined chains over mode-preserving frames

All objects are those of CubeJerry's PR6327 (`research/refined-native-recovery`),
for the literal 112×8 matrix M pinned from #5444 in
`research/precision-state-frontier/FIXTURE.json`.

## 1. Statement

R is nearest-integer rounding with half ties away from zero, and
K(z)=z−M R(Mᵀz/52). The source facts are MᵀM=56I, C=ker_F2(M mod 2) is the
self-dual [8,4,4] code, and F=W_C(13,1)/16=(13^8+14·13^4+1)/16=51,008,161.
Let G={U∈GL_112(Z): MᵀU=Mᵀ}. Fix t≥1 and U_1,…,U_(t−1)∈G with no parity
restriction. The chain is

    z_1=K(2x),   z_(j+1)=K(U_j z_j),   y=z_t.

Write W_j=(U_(j−1)⋯U_1)^−1 (W_1=I) and N_j=im_F2(W_j M mod 2).

**Theorem.**

(a) Every frame sequence has |fiber(0)| ≥ F^t. Equality holds exactly when
N_1,…,N_t form a direct sum.

(b) If N_1,…,N_t form a direct sum, every output has fiber at most F^t.
The maximum fiber is then exactly F^t.

(c) For this M, every N_j lies in one fixed 104-dimensional subspace and has
dimension 4. A direct sum therefore needs t≤26. FRAMES.json gives an
explicit sequence for t=26, so every t≤26 is attained by a prefix.

Consequently, over all mode-preserving frame sequences,

    min_U max_y |fiber(y)| = F^t     for 1≤t≤26,
    min_U max_y |fiber(y)| > F^t     for t≥27.

The minimum packed tag at depth t≤26 is ceil(t·log2 F) bits. That is 26,
52, 77, … and 666 bits at t=26, compared with ceil(log2 A_t) for the
parity-I class. At t=2 this recovers PR6327's 52-bit theorem and its
direct-sum criterion (2).

## 2. Fiber parametrization

Put m_j=Mᵀz_j. Since MᵀU_j=Mᵀ and MᵀM=56I, the j-th kernel call has quotient
q_j=R(Mᵀ(U_(j−1)z_(j−1))/52)=R(m_(j−1)/52), with m_0=2Mᵀx, and
m_j=m_(j−1)−56q_j. Going backward from s=Mᵀy,

    q_t∈Q(s),  q_(t−1)∈Q(s+56q_t),  …,  q_1∈Q(s+56(q_2+⋯+q_t)),       (1)

per mode coordinate, where Q(s)={q: R((s+56q)/52)=q}. Reverse execution gives

    2x = Σ_j W_j M q_j + W_t y.                                          (2)

Conversely every chain (1) with integral x in (2) is a preimage: forward
execution reproduces each m_j, and therefore each q_j. Forward execution is
deterministic and reproduces the chain of each preimage. The map from
preimages to chains (1) satisfying the parity condition

    Σ_j (W_j M) q̄_j ≡ W_t y  (mod 2)                                    (3)

is therefore a bijection. verify.py replays (2) on random inputs at depth
3 and depth 26 for the constructed frames.

PR6327's CHAIN_PROOF Section 2 proves that Q(s) is a nonempty interval of at
most 13 consecutive integers for every integer s, retaining ties. It also
proves Q(56w)=[−6,6]−14w. verify.py rechecks both on a finite window. The
general statement is the predecessor's.

## 3. Box lemma

Let B=I_1×⋯×I_8 with each I_k an interval of at most 13 integers, and let
c∈F2^8. Then #{q∈B: q̄∈c+C} ≤ F.

Proof. C is self-dual with |C|=16, so 1[v∈c+C]=16^−1 Σ_(h∈C)(−1)^(h·(v+c)).
Summing over B factorizes per coordinate. The h_k=0 factor is |I_k|≤13.
The h_k=1 factor is a signed sum of consecutive ±1 values, so it has
absolute value at most 1. The triangle inequality gives the bound
16^−1 Σ_(h∈C) 13^(8−wt h)=W_C(13,1)/16=F. verify.py also checks the maximum
exhaustively at length 13, over every start parity and every coset.

## 4. Proof of (b)

Assume that N_1,…,N_t form a direct sum. The kernel of each W_j M mod 2 is
C, because W_j is invertible modulo 2. Equation (3) then has no solution,
or it fixes each component W_j M q̄_j uniquely. Hence there are fixed
cosets with q̄_j∈c_j+C for all j, and they depend only on y. Count the
chains (1) from stage t down to stage 1. Once q_t,…,q_(j+1) are fixed,
q_j ranges over a box of intervals of length at most 13 with parity in
c_j+C. By Section 3 there are at most F choices. The fiber therefore has
at most F^t points. This argument conditions stage by stage, so it avoids
PR6327's joint Fourier majorant, which that package shows fails for three
quotient parities.

## 5. Proof of (a)

At y=0, (1) with Q(56w)=[−6,6]−14w gives q_j=r_j−14q_(j+1) with free
r_j∈[−6,6]^8, so q̄_j=r̄_j. The zero fiber is therefore

    Σ_(u∈ker) Π_j 7^(8−wt u_j) 6^(wt u_j),
    ker = {(u_1,…,u_t): Σ_j W_j M u_j ≡ 0 (mod 2)}.

The kernel contains C^t, and that part contributes exactly
Π_j W_C(7,6)=F^t. Every term is positive. The kernel equals C^t exactly when
its dimension is 4t, that is, when dim(N_1+⋯+N_t)=4t, which is the direct
sum condition. Otherwise the zero fiber exceeds F^t. As a consistency
check, verify.py evaluates this formula with every N_j=im M for t=1,2,3
and recovers PR6327's parity-I maximum A_t.

## 6. Proof of (c)

Let K=ker_Z(Mᵀ), a lattice of rank 104. For U∈G, Mᵀ(U^−1−I)=0, so
W_j M q ∈ Mq+K. Hence every N_j lies in im_F2(M mod 2)+red_2(K), where
red_2(K)=(K+2Z^112)/2Z^112 has dimension at most rank K=104.

im_F2(M mod 2) lies inside red_2(K). The lattice MᵀZ^112 contains 2Z^8:
verify.py expresses each 2e_i through eight source rows recorded in
FRAMES.json. So 28q=Mᵀw for an integer w, and Mq−2w∈K reduces to Mq mod 2.
All N_j therefore lie in red_2(K), of dimension at most 104. Each N_j has
dimension 4, so a direct sum requires 4t≤104.

Construction. E has rows e_0ᵀ,e_1ᵀ,e_2ᵀ,e_4ᵀ, as in PR6327, and E M mod 2
has rank 4 with kernel C. FRAMES.json gives 25 integer blocks V_2,…,V_26
of four columns each, with MᵀV_j=0 and E V_j=0 (zero on rows 0,1,2,4).
Put V_1=0 and

    W_j=I+V_jE,     U_j=W_(j+1)^−1 W_j = I+(V_j−V_(j+1))E.

Since E V=0, matrices of the form I+XE multiply by adding the X's. So
U_j∈GL_112(Z) with inverse I−(V_j−V_(j+1))E, MᵀU_j=Mᵀ, and
(U_(j−1)⋯U_1)^−1=W_j. verify.py checks MᵀV_j=0 and E V_j=0. It then forms
all 26 binary images of W_j M directly and finds total rank 104=4·26. Any
prefix of a direct sum is a direct sum, so this attains (b) for every t≤26.

The blocks are lifts of an F2-basis of the kernel of the map
u↦Mᵀũ mod 2Λ on the 108 non-E coordinates, with Λ=MᵀZ^112. They are
chosen to be independent of im M. build_frames.py regenerates FRAMES.json
deterministically. verify.py does not trust that derivation; it checks the
stated properties of the committed integers.

## 7. Scope

This is a scoped proof with an exact finite certificate for one interface:
fixed known frames in G, one relative precision bit before the first call,
unbounded exact integers and complete output access. It does not cover
mode-changing frames, input-dependent frames, extra refinement between
calls, finite ranges or physical tags. It supplies no codec beyond the
count, no physical memory saving and no κ. The output function changes
with the frames, as PR6327 notes at t=2. For t≥27 only the strict
inequality is proved; the exact optimum there is open.
