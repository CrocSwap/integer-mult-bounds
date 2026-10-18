# Follow-up to PR2177: the census-only attainment cases, and k destination errors

Status: written proofs with exact finite checks by the author (scripts and logs in this
directory). Not independently reviewed. The domain, notation, Facts F1–F2 and Lemmas S, L2, L1,
I, X, P are those of `PROOF.md` (PR2177). H = fl(n) = floor(log2 n), b = floor(n/2),
a = ceil(n/2). Monomials are written with the newest factor on the left. "Level ℓ" is scratch
level ℓ (level 1 = z of the top call, level ℓ is register ℓ+1 in the scripts).

## Part A. Attainment in the three remaining source-dirty cases

PR2177 §3 proves the upper bound fl(m) for the source-dirty LCA cases, and §4 proves attainment
only for (U,V) with sign +. Here we prove attainment for (U,V′) +, (U′,V′) + and (U,V′) −.
Lemma P does not apply to a sign − readout phase. The fix is to read a scratch row instead of y.

**Lemma E (exit of the y-keeping chain).** Let C be a call of size k, of either sign, with factor
offset 0. Follow the y-keeping U-phase at every level (U′ in a sign + call, U in a sign − call).
This gives calls C = C_0 ⊃ C_1 ⊃ … ⊃ C_r, with r = fl(k), |C_i| = k_i = floor(k/2^i), and
y_{C_{i+1}} = z_{C_i}. Inject at the leaf C_r. At C's end, the column is supported exactly on
y_{C_0}, …, y_{C_r}, and

  entry at y_{C_i} = (−1)^{r−i} f_{k_i−1} … f_1   (the empty word for i = r).

This entry does not depend on the signs.
*Proof.* Downward induction on i. At the end of the y-keeping phase C_{i+1}, the column of C_i
has entry e at z_{C_i} = y_{C_{i+1}}, plus deeper entries, and x_{C_i} = 0 (L1). In a sign + call
the only later phase is V′, and it does y −= A z. In a sign − call the later phases are V′, which
does y −= A z, and then U′, which reads x_{C_i} = 0 and so acts trivially. In both cases
y_{C_i} = −A_{C_i} e with A_{C_i} = f_{k_i−1} … f_{k_{i+1}}, and every other entry is unchanged
(F2). ∎

**Lemma Q (sign − readout).** Let K′ be a sign − call of size a ≥ 2. Its phases are V, U, V′, U′,
and U is a sign + call x′ → z′ on its first c = floor(a/2) factors. Let t be U's Lemma P cut,
which follows V at every level inside U. Then row z′ of Pre_{K′}(t) is

  z′ ↦ 1,   x′ ↦ P_U,   level-ℓ scratch of U ↦ (the Lemma P segment of U), ℓ = 1..ceil(log2 c),

and it is 0 on every other register, y′ included.
*Proof.* Pre_{K′}(t) = Pre_U(t) ∘ T, where T is the completed phase V. By F2, T changes only y′,
and y′ is outside U's footprint. So Pre_U(t)[z′, y′] = 0, and row z′ equals row y_U of Pre_U(t).
That row is 1 on y_U (by F1, y_U is never read), and Lemma P gives the rest. ∎

**Theorem A.** Let n ≥ 4 and c = floor(a/2). Let t* be the Lemma Q cut of the top call's V′, and
read register z_{V′} (level 2). For each of the three cases, inject at the y-keeping-chain leaf
of the top phase α:

| top sign | case | α |
|---|---|---|
| + | (U, V′) | U |
| + | (U′, V′) | U′ |
| − | (U, V′) | U |

In each case, z_{V′} at t* equals

  Σ_{ℓ=1}^{H} (−1)^{H−ℓ} λ_ℓ · f_{floor(n/2^ℓ)−1} … f_1,

where λ_1 = f_{b+c−1} … f_b, λ_2 = 1, and λ_ℓ = f_{b+c−1} … f_{b+c−ceil(c/2^{ℓ−2})} for ℓ ≥ 3.
Its mass is exactly H = fl(n). With PR2177 §4, all four source-dirty cases attain fl(m) for every
m ≥ 2. (For m = 2, 3 the value is 1. It is attained because z_K stays nonzero through V′, by F1.)

*Proof.* α has size b. By Lemma E applied to α, with r = fl(b) = H − 1, the exit of α has entry
(−1)^{H−ℓ} f_{floor(n/2^ℓ)−1} … f_1 at level ℓ, for ℓ = 1..H. Level 1 is y_α = z_K.

Between α and V′, the top phases change only y_K:
- +, α = U: V adds A c_z to y_K, and U′ reads x_K = 0.
- +, α = U′, and −, α = U: nothing lies between α and V′.

So the column q at V′'s start agrees with Lemma E on levels 1..H and is 0 on deeper levels.

V′ is a sign − call of size a on x′ = z_K. Its U-phase has size c = floor(a/2) ≥ 2^{H−2}, so
Lemma Q covers levels 1, 2 and 3..2+ceil(log2 c) ⊇ 3..H. Row z_{V′} ignores y_K. So it is
Σ_ℓ λ_ℓ q_ℓ, with the λ_ℓ of Lemma Q, which are exactly the λ_ℓ above.

Each word is (letters of index ≥ b)(letters of index ≤ b − 1). Its right part has length
floor(n/2^ℓ) − 1, and these lengths are pairwise distinct. So the H words are distinct, nothing
cancels, and the mass is H. ∎

**Checks.** `fam3.py 4 128` checks every case for each n ≤ 128, and all pass
(`logs/fam3_4_128.log`). It checks Lemma E's exit formula, Lemma Q's row exactly, mass = #terms
= fl(n), and the row equal to the closed form. PR2177's `check2.py` already showed that the
census case values equal fl(m) for m ≤ 80.

## Part B. k errors at distinct completed-leaf destinations

**Model.** Inject unit errors e_1..e_k, each of norm ≤ 1, at the destinations of k distinct
completed leaves i_1 < … < i_k ≤ t. Read register w at the cut after leaf t. The error there is
Σ_j M_{i_j→t}[w, y_{i_j}] e_j. Its norm is at most the channel mass Σ_j |M_{i_j→t}[w, y_{i_j}]|.
This is PR2067's independent-defect model.

E_k(n) is the maximum channel mass over both orientations, all t, all w and all sets of at most
k leaves. Note that the errors must be kept as separate symbols. If one common symbol is
superposed in the free algebra, monomials collide across channels, and `multi.py` counts many
such collisions for n ≤ 24. That number would not be a norm bound for independent errors.

**Relation to PR2067.** PR2067 treats only the final cut, with every leaf erroneous. There each
channel is a single monomial (mass 1), and the counts are C_y = T(n) and C_{z_k}. `multi3.py`
reproduces those endpoint counts exactly, for every register, both orientations and n ≤ 40 (check
END). Everything below is about interior cuts, where one channel can carry mass up to fl(n).
Interior accumulation is much larger than the endpoint value. For example, at n = 64, E_∞ = 6173,
against T = 729 at the target and 4^h/2 = 2048 for PR2067's whole-state endpoint coefficient.

**Theorem M1.** E_k(n) ≤ k · max(1, fl(n)).
*Proof.* Apply the triangle inequality, and bound each channel by PR2177's Theorem 1. ∎

**Theorem M2.** E_2(n) = 2 · max(1, fl(n)) for every n ≥ 2.
*Proof.* The upper bound is M1. For the lower bound, use top sign +. The (U,V′) and (U′,V′)
families of Theorem A inject at two different leaves and read the same register z_{V′} at the
same cut t*. Each has mass H, so together they give 2H when n ≥ 4. For n = 2, 3, inject in U and
in U′ and read z_K at any cut in V′. This gives 1 + 1. ∎

**Lemma F (full-exit leaves).** In a call of size k, let F(k) be the number of injection leaves
whose exit support has the maximal size fl(k) + 1. Then F(1) = 1, and

  F(k) = F(floor(k/2)) + 2·[k + 1 is a power of 2]·F(ceil(k/2)).

In closed form, F(k) = 2j − 1, where j is the number of leading 1-bits of k. So F(k) = 1 unless k
starts with "11".
*Proof.* Use Lemma X's proof. A V-type phase (there are two) exports S = S(φ), and
|S(φ)| ≤ fl(a) + 1. This reaches fl(k) + 1 only if fl(ceil(k/2)) = fl(k), that is, only if k + 1
is a power of 2.

A U-type phase gives |S| ≤ |S(φ)| + [y_K set], and y_K is set only by the y-keeping U-phase. A
full S(φ) contains y_φ, so c_z ≠ 0 and y_K = −A c_z ≠ 0. So exactly F(b) leaves come from that
phase, and none come from the other U-phase.

The closed form follows. F(2^m) = 1, and F(2^j − 1) = F(2^{j−1} − 1) + 2. Dropping the last bit
of a number that is not all ones keeps its leading-ones count. ∎

**Theorem M3 (sharper bound).** Let n ≥ 4 with n + 1 not a power of 2. At any cut and register,
at most 2F(b) channels have mass H = fl(n), and every other channel has mass ≤ H − 1. So

  E_k(n) ≤ k·H − max(0, k − 2F(floor(n/2))).

For n = 2^h (h ≥ 2), 2F(b) = 2, so E_k(2^h) ≤ 2h + (k − 2)(h − 1) for k ≥ 2.

*Proof.* A channel with LCA inside a child has mass ≤ max(1, fl(child)). Here fl(b) = H − 1, and
fl(a) = fl(n+1) − 1 = H − 1 because n + 1 is not a power of 2. With LCA at the top, PR2177's
table bounds (U,U′) by max(1, fl(b)) = H − 1 and every V-start case by fl(a) = H − 1.

That leaves the source-dirty cases. Their bound comes from (*): the row mass is at most the
number of dirty footprint registers, which is at most |exit(φ_α)| ≤ fl(b) + 1 = H. (The (U,V′)+
row-y argument gives the same count.) So mass H forces φ_α ∈ {U, U′} (top +) or φ_α = U
(top −), with the injection leaf having a full exit from φ_α. Lemma F says there are F(b) such
leaves per phase, so at most 2F(b) in all. ∎

**Census** (`multi3.py`, exact, all k, both orientations, n = 1..40, `logs/multi3_ok_*.log`).
Write E_k as runs of increments. For example, n = 16 gives `4x2 3x17 2x62 1x138`: E_k grows by 4
for 2 steps, then by 3 for 17 steps, and so on.

| n | E_k runs | E_∞ | PR2067 T(n) |
|---|---|---|---|
| 4 | 2x2 1x9 | 13 | 9 |
| 8 | 3x2 2x13 1x36 | 68 | 27 |
| 12 | 3x6 2x35 1x91 | 179 | 63 |
| 15 | 3x13 2x56 1x126 | 277 | 79 |
| 16 | 4x2 3x17 2x62 1x138 | 321 | 81 |
| 32 | 5x2 4x21 3x96 2x262 1x526 | 1432 | 243 |
| 40 | 5x2 4x29 3x156 2x458 1x937 | 2447 | 459 |

All checks pass for n ≤ 40: M1, M2, and M3 with equality (the count of mass-H channels equals
2F(b) exactly). For n ≤ 3 every channel has mass 1, and E_k = min(k, T(n)).

For all-ones n = 2^g − 1, Lemma F's V-phase term enters and M3 does not apply. Census shows
c_H = 2F(b) + 3 = 4g − 3 (9, 13, 17, 21, 25 for g = 3..7).

**Conjecture C1 (one universal cut).** For n ≥ 4, a single interval attains E_k(n) for every k
at once. Take top sign +, follow V′ down to the size-2 call D (depth ceil(log2 n) − 1), cut right
after D's U-leaf, and read w = z_D, the deepest scratch level. Then E_k(n) is the sum of the k
largest channel masses at this cut, Ω_n.
Census: true for all n = 4..40, all k. In each case Ω_n and the next cut are the only maximisers.

**Conjecture C2 (exact profile, n = 2^h).** At Ω_n, let c_j be the number of channels of mass j.
Then c_h = 2, c_{h−1} = 4h + 1, c_{h−2} = 4h² − 2h + 6 (h ≥ 3), and

  E_∞(2^h) = Σ_j j·c_j = (11·4^h − 11·3^h + 1)/6   (h ≥ 2).

Status:
- c_h = 2 is proved. It is attained by M2 and bounded by M3.
- The other formulas are checked at Ω_n for h = 2..10 (`omega_fit.py`, `logs/omega_fit.log`), and
  by the full census for h ≤ 5.

If C1 holds, then for 2 ≤ k ≤ 4h + 3, E_k(2^h) = 2h + (k − 2)(h − 1), which is M3 with equality.
M3's equality c_H(Ω_n) = 2F(b) is also checked at Ω_n for every n = 4..300 with n + 1 not a power
of 2.

Not proved: C1 (that no other cut beats Ω_n), the lower-order counts, and E_∞ for general n.

**Controls.** In the ceil-half split mutation (`multi3.py 2 20 swap`), 15 of 19 sizes fail. M1
and M2 fail at n = 6, 7 (E_2 = 6 > 2·fl), M3 fails (for example 6 > 2 at n = 5, 9, 20), and the
PR2067 endpoint counts fail. So the floor-half export count of Lemma X matters here too.

## Files

- `fam3.py`: Part A families, Lemma E and Lemma Q. Log: `logs/fam3_4_128.log`.
- `multi3.py`: Part B census with checks M1, M2, M3, OMEGA and END. Logs: `logs/multi3_ok_1_34.log`,
  `logs/multi3_ok_35_40.log`, `logs/multi3_swap_2_20.log`.
- `omega.py`, `omega_fit.py`: the Ω_n profile and the C2 closed forms. Logs:
  `logs/omega_4_128.log`, `logs/omega_256_512.log`, `logs/omega_fit.log`.
- `explore3.py`, `multi.py`, `multi2.py`: exploration tools (argmax paths, collision counts, the
  first census).

Scope is as in PR2177. Not covered: internal leaf intermediates, correlated errors that use a
common free symbol, rounding, aliasing and kappa.
