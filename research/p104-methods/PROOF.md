# Proofs and premises

Conventions follow [#7555](https://github.com/CrocSwap/integer-mult-bounds/pull/7555) and
[#7557](https://github.com/CrocSwap/integer-mult-bounds/pull/7557). A word is a sequence of
equal-chart ADD/COPY/SCALE events and MOVEs; public MOVEs strictly ascend, owned MOVEs are nested.
{0} is the zero chart and V the full chart. G is the Gram matrix of the port roots, Z = G/2 − I on partner
cells (G_pt odd), and X_p's target is x_p + Σ_t Z_pt y_t (relay family) or the t = −1 contract of #7557.
Only the statements below are claimed as proved. Everything else in README.md is either an exact run
(tag [C], reproduced by a checker in this package) or a quoted lane number (tag [Q], not reproduced here).

## 1. {0}/V re-basis

**Lemma 1.1 ({0} freedom).** Order the registers that leave {0} by departure time d_r. The departure
tuples realisable by changing only the {0}-phase events are exactly the images of the given tuple under
lower-unitriangular maps in that order (and diagonal scalings, if SCALE is allowed).
*Proof.* At {0} every ADD is between registers that both still sit at {0}, so register r can receive only
contents of registers that have not left. Composing the {0}-phase ADDs gives a matrix that is
unitriangular in departure order. Conversely, an ADD r += c·s placed just before d_r, with s still at
{0}, realises each elementary unitriangular factor. Contents of registers still at {0} at d_r equal their
own departure contents up to the same triangular mixing, so the family is linear in the coefficients
with no cross terms. ∎

**Lemma 1.2 (V freedom).** Nothing leaves V. After the last event every V-ending register sits at V,
so any invertible recombination of the V-ending registers can be appended (LU into elementary ADDs,
plus SCALEs if the determinant is not 1). Hence a modified word is correct on the V-ending registers iff
span(new V-arrival contents) = W_V := span(their final rows), i.e. every new V-arrival row lies in W_V.
All other rows (non-V publics, owned) must be exact. ∎

**The exact test.** Let E = (base finals) − (new finals) after a candidate edit (deleting a rung's
ADDs). Choose one basis of content space adapted to the {0} flag S_{r₁} ⊇ S_{r₂} ⊇ … of Lemma 1.1 and to
W_V (a flag and one subspace always admit a common adapted basis). By Lemmas 1.1 and 1.2 the edit is
repairable by {0} and V freedom iff for every basis vector b,
E_b[rows(b)] ∈ col{G_r(d_r)[rows(b)] : d_r < level(b)}, with rows(b) the non-V rows if b ∈ W_V and all
rows otherwise; a vector beyond the flag (an input never at {0}) gets no {0} freedom. This is a
direct reformulation of the two lemmas (sketch; the general test is not re-run in this package). The
package checks the instance used by #7542, helper 761 at chart 1053, with `rebasis.py` [C].

## 2. Absorption

**Identity.** Let X_r(τ) = X_r^f + Σ_t ψ_rt Y_t^f. A helper H born at {0} lumps −λ·y there, is read
at its low stops, does H += Σ_r d_r X_r(τ_K) at a chart K where the X_r sit, and H −= Σ_r d_r X_r^f at V.
Then H = h + Σ_t (Σ_r d_r ψ_rt − λ_t) Y_t^f, so **H ends clean iff λ = Σ_r d_r ψ_r(τ_K)**. Readers at
earlier stops received a_p·(−λ). ∎ (Two lines of linear algebra; `absorption.py` checks it exactly.)

**Legality (premises).** All ADDs are equal-chart (H with the X_r at K; at V). H's chain
{0} ⊂ … ⊂ K ⊂ V strictly ascends. Between its read stops and K, H holds y-charge only on supp λ ⊆ U(K),
so it stays inside each t^⊥ that its charts must respect; after K it holds no y-charge. The X_r are
referenced, not consumed. This was replayed with an LC1 check after every operation on a real E8-port
instance in the lane (ABSORBAUDIT) [Q]; this package checks the algebra, not frames.

**Deficiency.** With every cell settled the relay-family deficiency is n − r (#7557 law 1); absorbed
cells count as settled because every later cleaning of the referenced junk reads Y after it is final.
Under the σ-anchor schedule of #7557 (one early cell per column on a perfect partner matching), the
frame-free toy algebra gives D = 0 with absorbers filling the settled set, provided each absorber reads
X_r(K) only when (r, t) is X_r's last outstanding cell [C on A3/A4, frame-free; no general proof].

## 3. Range-G y pre-loads

**Lemma 3.1 (span law).** For any up-closed set W of charts and any time τ,
span(contents of registers in W at τ) ⊆ span(final rows in W) + span(rows CLEARed in, or owned-moved
out of, W after τ).
*Proof.* An ADD acts between registers at the same chart, so both or neither are in W, and inside W it
is invertible on the span. Public MOVEs ascend, so public registers only enter W. Only CLEARs and owned
MOVEs out of W remove rows. At the end the contents in W are the finals. ∎

Owned U rows U_j = B_j·y (range G·y) are CLEARed at V ∈ W for every W, so the per-coordinate rule
"y_u only inside q_u^⊥" is stronger than the span law by exactly span(U rows): a range-G y vector is not
excluded at any chart by Lemma 3.1.

**Identity (E8, λ = 26).** With G² = λG and complete junk carried at c = −G_t/2, the residual is
Zc = −((λ−2)/4)·G_t − e_t, so an owned gauge G·(x/2 + μ*·y) with μ* = (λ−2)/4 − 1/2 = 11/2 gives
Y_t = x_t with every y cancelled and no zero-Y park. `preload.py` checks it on all 104 columns [C].

## 4. Signed-row helpers: Rado test and LU

**Need rows.** In a deposit word whose product of deposit-side ADDs is the identity, register r carries a
need row ρ_r(τ) (the U-content it must still receive). ADD r += c·s acts as ρ_r += c·ρ_s, an injection
from U_k subtracts a multiple of e_k, a helper's load at {0} sets its row freely, and all rows end at 0.

**Support lemma.** Let A(S) = {k : S ⊂ b_k}. A register at S has row supported on A(S). *Proof.* Fix k;
on registers at k-forbidden charts the k-column changes only by invertible ADDs among co-located
registers (charts only ascend, no e_k injection there), and must end at 0, so it is 0 on entry. ∎

**Group rule.** At chart S, members with incoming rows R span Ω; member p leaves for a chart with allowed
set A′_p, so its outgoing row lies in Ω_p = Ω ∩ R^{A′_p}. Without new helpers the group is feasible iff
one vector from each Ω_p can be chosen spanning Ω (Rado's transversal condition for the subspaces Ω_p);
then N = T·R with T invertible, realised by LU into elementary ADDs. A helper is an extra member with a
free signed row. Example [C]: two proportional members (1,1,1,1), (2,2,2,2) leaving on coordinate
blocks {0,1} and {2,3} are infeasible (deficit 2); one helper with the signed row (1,1,0,0) makes the group
feasible and leaves with row 0, while a helper restricted to a single e_k does not (with single-coordinate
exits a pure helper already suffices, so the free row matters for block exits). `rado_lu.py` checks these exactly.

## 5. O+(8,2) quotient

Every port vector q ∈ F₂⁹ has odd weight, q·c = 1 (c the all-ones vector, itself of odd weight 9).
Each class of V/⟨c⟩ contains exactly one even vector, so V/⟨c⟩ ≅ W := c^⊥, and p̄ := q_p + c. On W the dot
product is alternating (even weights) and nondegenerate (c^⊥ ∩ ⟨c⟩ = 0), so ω = dot is symplectic on the
8-dimensional W. Since ω(p̄, t̄) = q_p·q_t + 1 for odd-weight q_p, q_t, partners (q_p·q_t = 0, i.e. G_pt
odd) are exactly the pairs with ω(p̄, t̄) = 1. ∎ The counts (104 of the 120 nonsingular points of
the E8 quadratic form, the two-graph sign law, the 282 twelve-port 4-spaces, one 8-block packing) are
exact enumerations [C, `quotient.py`], not proofs of uniqueness or optimality.

## 6. The 20-odd-op floor for one q-free plane

Per A port the target needs R := σ(M)M⁻¹ = −I₃₆ (σ: q ↦ −q). R is a product of conjugates of the factors'
sign factors; ops have σ-rank o ∈ {0, 1}, a q-free plane contributes 0 and a q-odd transvection plane
contributes a rank-1 transvection, which is not an involution. By subadditivity Σ o ≥ 36, and by Lemma E
of #7555 (equality only if every factor is an involution) Σ o ≥ 37. With 17 J calls supplying 17, the odd
ops number ≥ 37 − 17 = 20. ∎ (Premises: the #7113 masks and idle sets, σ-fixed stage data D, odd ops of
σ-rank 1 each.) `callers.py` replays four callers that meet the floor exactly [C].
