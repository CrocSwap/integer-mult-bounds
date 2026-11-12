# Lane-wise IDLE regrouping at the paired BIT target

**NO VERIFIED GAIN.** With all 36 old LOCAL calls and productive targets fixed, the complete optimistic BIT moment is strictly below **−8.16416603986435** at the exact target 10018846261809/2500000000000000. This covers nonuniform, separately charged IDLE masks even with arbitrary copy and port mixing and extra body incidences.

## Contract

Use the formal independent q and body variables of exact #7001, specialized at one. On the 38N root coordinates, N=111, the desired q derivative is identity and the desired body derivative T_s is the literal diagonal stage projector. Fresh productive helper inputs are set to zero for this necessary condition. Across every opposite-half pair the support intersection is the common 2N-plane E (roles 0 and 19). The two other 18-role blocks belong to separate halves. Each old LOCAL's constant shear C and q derivative M satisfy that MC⁻¹ is square-zero of rank N. Arbitrary rectangular scalar preparation, recovery, cross-copy mixing and scratch preserve the transported body and q factorizations shown in the [uniform special case](PROOF.md). The old paid and productive helper channels are retained.

Each paid IDLE mask may vary from lane to lane and contributes one common rank-at-most-one derivative in every included stage. Its tariff is H(7ℓ) for ℓ included stages, with H(r)=r^(1−κ*) and H(0)=0. Additional head operations are body-free and each derivative rank is at most its paid rank. Setup, scalar routing, restoration, precision and tape charges are granted free in the upper bound. A job supplying distinct derivative directions across its stages or coupled head/body action under one charge is outside this model.

## Head rank with excess body incidences

At stage s, write T_s=U_sV_s with latent dimension m_s and excess e_s=m_s−rank(T_s). Rank of the block matrix with identities on the diagonal and U_s,V_s off-diagonal, eliminated in either order, gives

```text
rank(I−V_sU_s) = m_s−d + rank(I−T_s) = e_s.
```

Thus (I−T_s)U_s and V_s(I−T_s) each have rank at most e_s. The two retained LOCAL head factors X_s,Y_s inherit these bounds on output and input leakage. A rank-one mask shared by multiple stages can use the same abstract rank factorization at each stage because its embedded derivative is common. A zero mask derivative may be represented with zero factors.

For stages s,t in opposite halves, let P denote the q shared factor positions. Since V_PU_P differs from I_q by a submatrix of each stage's rank-e defect, rank(V_P) and rank(U_P) are each at least q−min(e_s,e_t). The literal target projectors commute and satisfy T_sT_t=E, the common 2N-plane. From

```text
I−E = (I−T_s)+T_s(I−T_t)
```

and commutation, rank(V_P(I−E))≤e_s+e_t. This gives rank(V_PE)≥q−min(e_s,e_t)−e_s−e_t. The off-diagonal LOCAL-to-IDLE block gives rank(V_PX_s)≤e_s, hence rank(V_PEX_s)≤2e_s+e_t. Decomposing E X_s through the kernel of V_P on E gives

```text
rank(E X_s) ≤ 2N−q+min(e_s,e_t)+3e_s+2e_t.
```

Finally rank(Y_t(I−E)X_s)≤e_s+e_t by writing I−E=(I−T_t)+T_t(I−T_s). Hence rank(Y_tX_s)≤2N−q+4(e_s+e_t). Both inequalities permit arbitrary oblique and rectangular contexts.

In A=I+YX each stage's 2N×2N principal diagonal differs from identity by rank at most e_s. This follows by replacing V_sU_s by identity and using the old LOCAL internal square-zero factors' K_iJ_i=0. Correcting the two diagonal blocks to identity loses at most e_s+e_t in the lower rank bound. Schur elimination on the corrected principal block gives rank at least 2N+q−4(e_s+e_t). The full correction rank is therefore at least 4N+q−5(e_s+e_t). For K=max q over the 8×8 active opposite pairs and e=sum e_s, this implies 444+K−5e, with a zero lower bound allowed if the expression is negative.

## Complete optimistic tariff

Let d_s be the minimum physical IDLE count at stage s. Its actual count is d_s+e_s. Separate every cross mask into its two half-masks. Remove e_s incidences from each stage to recover all d_s exactly. Within a half, each removal costs at least H(63)−H(56), by concavity and the nine-stage length cap. The residual within-half bill is at least the old majorizing bill.

For a cross mask with a,b positive incidences in the two halves, its saving relative to separation is at most δ(a+b)/2≤δ ab, with δ=2H(7)−H(14). Indeed a balanced real split maximizes the saving at fixed a+b, yielding δ((a+b)/2)^(1−κ*), at most δ(a+b)/2. The sum of ab over masks counts opposite-stage pairs with multiplicity. Active pairs contribute at most 64K and each inactive incidence creates at most nine pairs. The inactive stages have d_s=0, so total cross savings are at most δ(64K+9e).

For a fixed active stage s, let q_s count its cross masks. Their output factor has rank at least q_s−e_s. Assign each mask to one opposite partner t, keeping its common output factor. The exterior part (I−E)U_P is a sum of (I−T_s)U_P of rank at most e_s and grouped T_s(I−T_t)U_{P,t} terms of total rank at most e_otherHalf. Thus q_s≤2N+2e_s+e_otherHalf. Summing the 16 active stages, then adding inactive incidences, yields total cross incidence at most 3552+10e. Consequently the alternate saving bound is δ(1776+5e).

Because H increases by at most one per added integer rank, packed head cost is at least H(444+K)−5e even if the earlier correction-rank bound is negative. Relative to the old full invoice the directed upper is therefore

```text
old_margin + 444 − H(444+K) + δ min(64K,1776)
− e (H(63)−H(56)−5−9δ).
```

Independent Fraction arithmetic proves δ≈0.038533759504261536 and excess penalty >1.51192534742538. Hence e=0 maximizes the relaxed upper. As K increases from 0 to 28 the minimum credit increment is 48δ>1.8496, exceeding every head increment. At and after 28 the credit is flat and head price strictly increases. Therefore the global optimum over nonnegative integer K is 28. Its upper interval lies strictly below −8.16416603986435. The adjacent K=27 and K=29 values are approximately −9.04206464049120 and −9.13587964502015.

## Replay and credit

Use CPython 3.12 with assertions. The four canonical inputs and their exact hashes are listed in SOURCES.tsv. The clean repository replay in README.md regenerates both the uniform and nonuniform results and independently checks the lane-wise price using directed rational arithmetic. Omitting the extra cross-mask head debit gives a positive relaxed upper, an explicit negative control for that pricing error.

Credit [#7001](https://github.com/CrocSwap/integer-mult-bounds/pull/7001), [#6726](https://github.com/CrocSwap/integer-mult-bounds/pull/6726), [#6834](https://github.com/CrocSwap/integer-mult-bounds/pull/6834), [#6980](https://github.com/CrocSwap/integer-mult-bounds/pull/6980), and [#7160](https://github.com/CrocSwap/integer-mult-bounds/pull/7160) for the paired word, caller, ledger and earlier head-rank scope. [#7177](https://github.com/CrocSwap/integer-mult-bounds/pull/7177) supplies a distinct formal caller identity requiring a changed LOCAL. OpenAI Codex and subagents materially assisted. No admitted supplier or complete bound changes.
