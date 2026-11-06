# Exact native square forces at least 4096 real affine-period classes

@CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
This follow-up leaves the first-round phase-covariant package frozen.

**Theorem.** Put Z=Z^16, W_rs=(-1)^popcount(r&s), A=W/4,
S=diag((-1)^popcount(j)), J(z)_j=z_(j xor 15), and K=SJ. If R:Z→Z
is odd, commutes with K, and Γ is a full-rank affine period with linear part A,
then [Z:Γ] is divisible by 4096. An affine period means
R(z+λ)=R(z)+Aλ for every z∈Z and λ∈Γ. No error or sum premise is used.

For F=-D R_C D, D_j=(-i)^wt(j), oddness and D²=S, DJD=J give
F²=D R_C S R_C D, because oddness cancels the two minus signs.
Since DJD=J, this gives F²=J iff RSR=J. The theorem concerns this componentwise real architecture
and exact square, not merely F⁴=I, nonperiodic maps, or arbitrary coupled
complex architectures. Existence at index 4096 is not established.

## Forced period invariance

For the exact-square corollary, set T=SR and B=SA. Then B²=K and T²=K. Hence T commutes with K;
S commutes with K, so R=ST also commutes with K. Also AK=KA. For any R commuting with K,

    R(z+Kλ)=K R(Kz+λ)=R(z)+A Kλ.

Thus Γ'=Γ+KΓ is a K-invariant affine period. Its index divides that of Γ.
This closure avoids assuming that an arbitrary declared period is invariant.
Alternatively the maximal period group is invariant. It is enough to bound Γ'.

## Integrality and oddness

L={z∈Z:Az∈Z} is characterized by sum(z)=0 mod4 and
sum_(s:bit_j(s)=1) z_s=0 mod2 for j=0,1,2,3. Indeed
(Wz)_r=sum(z)-2 sum_j bit_j(r)sum_(s:bit_j(s)=1)z_s modulo 4.
The resulting map onto Z4⊕Z2^4 is surjective, so [Z:L]=64.
Both A and K preserve L. Let V=L/2L and E=(L∩2Z)/2L.
Then dim V=16 and E≅(Z/L)[2] has dimension 5, with basis represented by

    u0=4e0,  u_(j+1)=2(e_(2^j)-e0), j=0,1,2,3.

Every affine period lies in L. If λ∈Γ' is even, oddness and translation
at -λ/2 give 2R(λ/2)=Aλ; hence λ/2∈L. Thus Γ'∩2Z⊂2L.
Consequently H=(Γ'+2L)/2L is K-invariant and H∩E=0, so dim H≤11.

## Two image witnesses

Write C=K+I on V. Direct substitution gives
C u0=0 and C uj=u0 for j=1,2,3,4. Thus C restricted to E has rank 1.
But E∩C V contains independent u0 and v=u1+u2+u3+u4: the first is C u1,
and the second is C w modulo 2L for

    w=(1,-2,-1,0,-1,0,0,-1,-1,0,0,-1,0,-1,0,-1)∈L.

The exact half-residuals are

    (C u1-u0)/2=(-3,1,0,0,0,0,0,0,0,0,0,0,0,0,-1,-1),
    (C w-v)/2=(4,-2,-1,0,-1,0,0,0,-1,0,0,0,0,0,1,0).

Both lie in L by the total/bit-sum criterion. Independence follows because
v/2 has odd bit sums, while u0/2 and (u0+v)/2 have total 2 modulo 4.

If dim H=11, the quotient π:V→V/H restricts to an isomorphism on E.
The induced C_bar consequently has rank 1. But π(u0),π(v) are independent
elements of im C_bar, because u0,v∈C V. Contradiction. Therefore dim H≤10.
Without assuming 2L⊂Γ', [L:Γ'+2L]=2^(16-dim H) is divisible by64.
The index formula then shows [Z:Γ'] and [Z:Γ] are divisible by 4096.

## Evidence and next question

`verify.py` imports neither the first-round package nor the module
solver. It checks the integer witnesses, all 31 nonzero E combinations and
three false-witness controls, including the omitted sign phase. Normal and -O modes are used. The theorem rests
on the quotient argument, not on a failed matching search. An exploratory module search suggested the obstruction; no search result
is a premise or replay dependency of this proof.

Nick Petalas's #6561 at e8a55a6edf91c5067b26cdfefbcc76517f86ab02 was inspected.
Its equivariant rounders concern integral conjugates of complete signed-
permutation groups, without bijection or exact-square requirements, so its
contract is distinct. Credit Nick Petalas #6574, Ali Romman and the retained
Gaussian native lineage for the starting interface. No kappa or admission is
claimed, and no exact-square map at the larger index has been constructed.

A next step is a B-invariant index 4096 period followed by coupled correction
cycles. For T(z)=Bz+c([z])/4, c=S e and p(s)=[T(r_s)], exact square requires
c(p(s))=-B c(s), in addition to integrality, oddness, sharp energy, weighted
sum and a class bijection. Ordinary bipartite matching does not impose this.

Published phase-only predecessor (discovery context, no upstream PR):
https://github.com/CubeJerry/integer-mult-bounds/tree/362b20bc934500bc503e850059f0d34daa5dcae3/research/four-axis-phase-covariant-grid
