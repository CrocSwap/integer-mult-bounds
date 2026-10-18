# The 9/17 pairing-cost floor for bit label decoders through 25 punctures

Facts marked **(Vx)** are checked by section x of `verify.py` with exact integer, rational and F2
arithmetic; `independent_check.py` cross-checks the code, witness chain, hyperplane and rank-six
thresholds, D7 directions, and P110 costs by other methods. It does not repeat every primary check. One
classical premise is cited rather than computed (P below). Everything else is written argument.

## 1. Model

This is the bit-side label-decoder model of PR620, PR757 and PR761, priced by PR446 Theorem C.

Take the 120 E8 root lines with representatives of norm 2 and Gram matrix G (diagonal 2, other entries
0 or ±1). Over F2 put

    B0[s, t] = (1 + G[s, t]) mod 2,

so B0 has ones on the diagonal and on orthogonal pairs. **(VA)** B0 has F2 rank 9. Because B0 is
symmetric with a nonzero diagonal, it factors as B0 = U Uᵀ with U of size 120 × 9 (labels u_t ∈ F2^9 with
u_s · u_t = B0[s, t]); only B0 enters the checks. A **functional** is a nonzero λ ∈ F2^9 and its reader
set is R(λ) = {t : λ · u_t = 1}. **(VA)** The 511 reader sets form a code with weight enumerator
1 + 255z^56 + 255z^64 + z^120. For a line a write λ_a = u_a; then

    R(λ_a) = {t : B0[t, a] = 1} = {lines orthogonal to a} ∪ {a},                 (1)

and the 120 sets (1) are distinct weight-64 words. **(VA)** Every reflection in a root permutes the
lines and maps the code onto itself, so W(E8) acts on functionals and preserves reader sets.

A **puncture** P is a set of p lines; the live set is L, with v = 120 − p. A **label decoder** is a list of
n terms (p_j, q_j) of functionals with

    Σ_j p_j q_jᵀ = I_9.                                                         (2)

Term j adds the payload Σ_{s ∈ R(q_j) ∩ L} x_s to every target t ∈ R(p_j) ∩ L. By (2),
Σ_j [t ∈ R(p_j)] [s ∈ R(q_j)] = u_tᵀ (Σ_j p_j q_jᵀ) u_s = B0[t, s], so the decoder reproduces the fixed
matrix B0 on L × L. Its **cost** is

    cost_j = rank_Q G[R(p_j) ∩ L, R(q_j) ∩ L],        cst = Σ_j cost_j.

For n = 9 the label restriction is automatic when p < 56: B0|LL has rank 9, so nine rank-one F2 terms
summing to it have column vectors spanning its column space, which is the code restricted to L, and the
restriction is injective because every nonzero codeword has at least 56 lines. For n ≥ 10 the label
restriction on each factor is part of the model, as in PR757 and PR761.

## 2. Premise and checked facts

**(P)** Every root-spanned subspace of Q^8 is W(E8)-conjugate to the span of a subset of the simple roots
(the same parabolic-coverage premise as PR939, PR954 and PR968). The span of any set of lines is
root-spanned, and every proper root-spanned subspace lies in a root-spanned hyperplane. The retained
[PR939 argument](../e8-first-rank-drop/reference/PR939-PROOF.md) explains the coverage: choose a generic
normal to the subspace, move it into a closed Weyl chamber, and use nonnegative simple-root
coefficients to identify its orthogonal roots as a standard parabolic subsystem. Enumerating 28
subsets alone would not establish coverage of arbitrary rank-six subspaces.

For a functional λ and a root-spanned subspace V let τ(λ, V) = |R(λ) \ V|, the number of punctures
needed to bring R(λ) ∩ L into V.

- **(VB)** For the eight standard hyperplanes (one per type) and all 511 functionals, the two smallest
  values of τ are: E7 1 and 24; D7 14 and 34; E6+A1 27 and 28; A7 28 and 35; D5+A2 33 and 41; A6+A1 35
  and 35; A4+A3 40 and 43; A4+A2+A1 43 and 43. The minimizers for E7 and D7 are unique.
- **(VB)** For each of the 120 root hyperplanes a^⊥ directly: τ(λ_a, a^⊥) = 1 (the line a) and every
  other functional has τ ≥ 24.
- **(VB)** The W-orbit of the D7 normal has 1080 directions. For each direction ω there is a unique
  functional λ_ω with τ(λ_ω, ω^⊥) = 14; it has weight 56, so it is not a root functional; every other
  functional has τ ≥ 34. Write S_ω for its 14 lines outside ω^⊥. Two distinct directions have
  |S_ω ∪ S_ω'| ≥ 21.
- **(VB)** θ6 := min τ(λ, V) over the 28 standard rank-6 subspaces V and all functionals equals 26.

## 3. Lemmas

**Lemma 1 (reduced sides).** Let p ≤ 25. For every functional λ, X = span(R(λ) ∩ L) has dimension at
least 7. If p ≤ 23 and dim X = 7, then either λ = λ_a with a ∈ P and X = a^⊥, or λ = λ_ω for a D7
direction ω with S_ω ⊆ P and X = ω^⊥.

*Proof.* If dim X ≤ 6, then X lies in a rank-6 root-spanned subspace V, and R(λ) \ V ⊆ P. By (P) some
w ∈ W maps V to a standard rank-6 subspace; w maps λ to a functional w·λ with
τ(w·λ, wV) = τ(λ, V) ≤ p ≤ 25 < θ6, a contradiction. If dim X = 7, then X is a root hyperplane H with
τ(λ, H) ≤ p ≤ 23. By (P) and the type table, H is an E7 hyperplane (τ = 1) or a D7 hyperplane (τ = 14);
all other pairs need at least 24. The direct checks then identify λ: for H = a^⊥ only λ_a has τ < 24,
and R(λ_a) \ a^⊥ = {a}; for a D7 hyperplane only λ_ω has τ < 34. ∎

A side (reader or source) of a term is **reduced** when its span has dimension 7.

**Lemma 2 (term cost).** For subspaces X, Y of Q^8, the Gram pairing between spanning sets of X and Y
has rank dim X − dim(X ∩ Y^⊥). Hence, for p ≤ 25: every term costs at least 6; a term with no reduced
side costs 8; a term with exactly one reduced side costs 7; a term whose sides are x^⊥ and y^⊥ costs
7 − [x ⊥ y], so 6 exactly when the two normals are orthogonal, and 7 when x = y. **(VC)** For one root a
and all 119 other lines b with P = {a, b}: cost 6 for the 63 orthogonal b, 7 for the 56 others, and 7 for
b = a.

*Proof.* The Gram matrix of spanning sets has the rank of the induced pairing X × Y → Q, whose left
kernel is X ∩ Y^⊥. Each dimension is at least 7 by Lemma 1, so the rank is at least 7 + 7 − 8 = 6. The
cases follow from Y^⊥ = 0 (dim Y = 8) and Y^⊥ = span(y) (Y = y^⊥). ∎

**Lemma 3 (duality).** In a 9-term label decoder, p_j · q_k = δ_jk. Consequently:

- (a) a line a with λ_a = p_j and λ_a = q_k forces j = k, because u_a · u_a = B0[a, a] = 1;
- (b) if p_j = λ_a and q_j = λ_b, then B0[a, b] = 1, so a = b or a ⊥ b;
- (c) if p_j0 = λ_ω and q_k = λ_b with k ≠ j0, then λ_ω(u_b) = 0, so b ∉ R(λ_ω) and in particular b ∉ S_ω.

*Proof.* With nine terms, (2) reads M Nᵀ = I for the 9 × 9 matrices with columns p_j and q_j, so
Nᵀ M = I. The functionals p_j are distinct, and so are the q_j. ∎

## 4. Theorem

Let P be a puncture with p ≤ 25 and let (p_j, q_j), j = 1..n, be a label decoder on L.

**(a)** n ≥ 9 and cst ≥ 6n ≥ 54.

**(b)** If n = 9, then cst ≥ max(72 − p, 54).

**(c)** cst / v ≥ 9/17. Equality holds exactly when p = 18, n = 9, cst = 54, each term is
(λ_a_j, λ_b_j) with a_j ⊥ b_j, and P is the set of these 18 lines.

**(d)** If p ≤ 13 and n ≥ 10, then cst ≥ 6n + 18 − 2p.

**(e)** For each integer 0 ≤ p ≤ 25 there exist a puncture P of size p and a 9-term decoder with
cst = max(72 − p, 54). This minimizes over punctures as well as decoders, not every fixed P. **(VD, VE)**

*Proof of (a).* The identity has rank 9, so n ≥ 9; each term costs at least 6 by Lemma 2.

*Proof of (b).* Write s_j = 8 − cost_j ∈ {0, 1, 2}, so cst = 72 − Σ s_j and Σ s_j ≤ 18. If p ≥ 21 then
72 − p < 54 and (a) suffices, so let p ≤ 20. By Lemma 1 every reduced side is a self-line side (λ_a with
a ∈ P) or a D7 side. Two different D7 directions would need |S_ω ∪ S_ω'| ≥ 21 > p punctures, so at most
one direction ω occurs.

*No D7 side.* Attach to every reduced side its line. By Lemma 3(a) different sides get different lines,
except that a self pair p_j = q_j = λ_a uses one line for both of its sides. A self pair saves 1 (Lemma
2, x = y). A term with sides λ_a and λ_b for a ≠ b has a ⊥ b by Lemma 3(b) and saves 2 with two lines.
A term with one reduced side saves 1 with one line. So Σ s_j is at most the number of lines used, which
is at most p. Hence cst ≥ max(72 − p, 54).

*One D7 direction.* Transposing the decoder (Σ q_j p_jᵀ = I) keeps every cost, because
rank G[R, A] = rank G[A, R]; so assume λ_ω = p_j0. The reader functionals are distinct, so every other
reduced reader side is a self-line side: at most 8 savings. By Lemma 3(c), a reduced source side of a
term k ≠ j0 is λ_b with b ∈ P \ S_ω, at most p − 14 distinct lines, or is λ_ω itself for at most one k.
With s_j0 ≤ 2 this gives Σ s_j ≤ 2 + 8 + (p − 14) + 1 = p − 3, so cst ≥ 75 − p > 72 − p.

*Proof of (c).* Take n = 9 first. For p ≤ 18, 17(72 − p) − 9(120 − p) = 144 − 8p ≥ 0 with equality only
at p = 18. For 19 ≤ p ≤ 25, 17 · 54 − 9(120 − p) = 9p − 162 > 0. At p = 18 equality needs Σ s_j = 18, so
every term saves 2. The D7 case gives at most p − 3 = 15, so no D7 side occurs; every term then has two
reduced self-line sides with orthogonal lines, the 18 lines are distinct, and they exhaust P.
For n ≥ 10, (a) gives cst ≥ 60 and 17 · 60 > 9(120 − p) whenever p ≥ 7. For p ≤ 6, (d) gives
cst ≥ 78 − 2p and 17(78 − 2p) − 9(120 − p) = 246 − 25p > 0.

*Proof of (d).* For p ≤ 13 only self-line sides occur (Lemma 1). Let S = span{u_a : a ∈ P}, so
dim S ≤ p, and let π be the quotient map F2^9 → F2^9/S. Composing (2) with π kills every term with
p_j ∈ S, so at least rank π = 9 − dim S terms have p_j ∉ S. Every reduced reader side has p_j ∈ S, so
there are at most n − 9 + p of them; the transpose bounds reduced source sides the same way. Then
Σ s_j ≤ 2(n − 9 + p) and cst ≥ 8n − 2(n − 9 + p). ∎

*Proof of (e).* **(VD)** The nine pairs in `WITNESS.json` satisfy B0[a_j, b_k] = δ_jk, so p_j = λ_a_j and
q_j = λ_b_j satisfy (2); the decoder identity is also checked entry by entry on all 102 × 102 live pairs.
Every term has reader span a_j^⊥, source span b_j^⊥ and cost 6, so cst = 54 on v = 102. **(VE)**
Puncturing a_1..a_p (p ≤ 9), then all a_j and b_1..b_(p−9) (p ≤ 18), then any further p − 18 lines
gives cst = max(72 − p, 54) for every p ≤ 25, by exact rank computation.

**Remarks.**

- At p = 9, (b) gives the n = 9 value 63 of PR757 and PR761; for n = 10 their P111-specific bound 64 is
  stronger than (a). For n = 10, (a) and (d) give 64 at p = 7, 62 at p = 8 and 60 for 9 ≤ p ≤ 11;
  the exact all-n floor in that window is not claimed.
- The range is sharp in one sense: **(VI)** a 26-line puncture brings some reader set into a rank-6
  subspace, so cost-5 terms are not excluded at p = 26. Whether some decoder beats 9/17 there is not
  examined.
- The complex frame-pair floor of PR968 is 7/13 > 9/17. The bit model prices rational pairing rank
  (cost 6 for orthogonal pairs), while the complex model prices F2 label pairing rank (cost 7 for odd
  pairs). The violator census is the same: |R(λ) \ ω^⊥| equals |Viol(λ) ∩ C(ω)|.

## 5. The selected bit supplier's own puncture

**(VG)** The PR589 word (`research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz`, SHA-256 equal to
the selected record's `word.file_sha256`) stores 111 live lines in Hamming coordinates with form
⟨x, y⟩/2. Completing them to the 120 lines gives the nine punctured lines, which have 44 ordered
orthogonal pairs. Their labels form a basis; the dual basis contains exactly one root label, the line
b = (0, 1, 0, −1, −1, 0, −1, 0) dual to a = (1, 1, −1, 1, 0, 0, 0, 0). The shipped label decoder
(readers λ_a for the punctured lines, sources the dual basis) costs 9 × 7 = 63 on P111. Puncturing b
gives P110 with costs 8 × 7 + 6 = 62. This one-root count fixes the nine reader functionals above;
it does not exclude other bases on the same puncture. A checked scope control instead takes pairs
(P[0],P[1]) and (P[3],P[4]) in the zero-based order of `RESULTS.json`. Their cross-pairing matrix is I_2,
so they extend to dual label bases with two cost-6 terms. That completion costs 68 overall on P111
and 67 on P110, neither an improvement. Its coefficients and costs are retained in `RESULTS.json`.
The necessary nine-stage hosting inequality R ≤ 4v (PR595) holds numerically at v = 110 for the
439-helper inventory (440 slots) and fails at v = 109 and v = 102 (408 slots). Satisfying this
inequality is not a constructed or verified owner map.

## 6. Favorable pricing

**(VH)** With the engines and PR589 profile pinned by the selected record, the moment root reproduces
PR589's c = 0.001733427039589844234749 exactly (with its inherited fallback term), and
64 · 28416 − mass = 10272 = 32(8 · 111 − 9 · 63). Lowering copy children 7 → 6 on all 288 calls at fixed
W gives +2.8017% c for one unit and +25.2108% c for nine. That is only the copy component: the
orthogonal pairs also delete ports. PR717 records a price of −2.13% to −2.16% c per deleted port on the
#555 invoice (its B26 knob card, not reproduced here), valid while the hosting wall holds. One pair on the
shipped puncture is therefore worth roughly +0.6% c, an estimate that combines one exact and one recorded
number.

The selected κ is complex-bound, so no bit-only change moves it (checked for the nine-unit copy knob).
The bit side matters together with a complex gain. PR968's P104 complex budget (b +5.5111%) is capped
by PR589 at κ = 0.001730427469823602. The same budget gives κ = 0.001753391564497665 (+5.5014%) once the
bit c is at least (1 − 10^−24) b_P104, 1.3294% above PR589's c. One pair on the shipped puncture does not
supply that headroom in this estimate, and a nine-pair unit with the R439 helper network breaks the wall.

## 7. Scope

Covered: label decoders of the fixed matrix B0|LL, any number of terms, label factors, punctures of at
most 25 of the 120 lines, cost = rational pairing rank (PR446 Theorem C, inherited).

Not covered: decoder matrices that differ from B0 on orthogonal pairs (PR620's off-pattern decoders);
non-label factors; punctures of 26 or more lines; non-root ports. No word is built. A cost-6 term needs an
asymmetric copy whose source span b^⊥ differs from its reader span a^⊥; PR620 lists the realization
questions (reader frame chains, a nonzero terminal frame and restoration, the common cut), and none is
addressed here. The pricing is an optimistic budget, not a supplier. All inherited all-size/compiler,
common-label and mutable-source, hosting, precision/tape and analytic assumptions remain. The finite
checks are not a formal proof of integer multiplication, and the written argument has not had
independent human review.
