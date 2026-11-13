# Proofs and scope

Each section states one law, its premises and scope, and what its checker
reproduces. Tags: **[P]** proved here; **[C]** exact computation by the named
checker; **[Q]** quoted from a repository file. Every [C] number is printed
and asserted by the checker; every checker runs at least one control that
must fail.

## 1. Credit/cut law for credited public fields

Tags: **[P]** proved here, **[C]** checked by `credit_cut.py`.

**Setting.** A word has public and owned registers. Each register sits at a
frame (a subspace of F₂⁹). The operations are:
- ADD and COPY between two registers at a common frame, and SCALE;
- MOVE E → F;
- owned INIT (zero content) and owned CLEAR (any content, "dirty").

Public register r starts with the unit coordinate e_r and ends with the row
T_r. A MOVE E → F is priced at its Fourier rank
d(E,F) = dim E + dim F − 2 dim(E ∩ F). A credited public path S = E₀ → … → E_m = T
earns the net credit dim T − dim S. An **up-set** U is a set of frames closed
under enlargement. For example, the principal up-set U_q is the set of frames
that contain the vector q.

For an up-set U, define:
- o_in(U), o_out(U): owned MOVEs entering or leaving U;
- p_out(U): public MOVEs leaving U;
- pubArr(U), ownArr(U): the contents that arrive in U. These are the initial
  residents of U and the contents carried by MOVEs into U;
- F_U: the public final rows whose final frame lies in U;
- junk_U = dim span(all arrivals) − dim span(F_U);
- cout_U = rank T[public finals outside U, public initial coordinates inside U];
- need_in(U) = dim(span pubArr + span F_U) − dim span pubArr.

**Premises.**
- (H1) ADD and COPY act only at a common frame.
- (H2) Every owned register is dead at the end.
- (H3) For the entry side only: T is invertible, so the public finals are
  independent.

Nothing else is assumed. The coefficients may lie in any field; the checks use
rationals with odd denominators and ℤ/(2³¹−1).

**Lemma 1.1 (loss identity) [P][C].** For every path,
paid − credit = Σ d(E_i, E_{i+1}) − (dim T − dim S) = 2 Σ_i k_i,
where k_i = dim E_i − dim(E_i ∩ E_{i+1}) is the descent depth of step i.

*Proof.* d(E,F) = (dim F − dim E) + 2(dim E − dim(E ∩ F)), and the first terms
telescope. ∎

[C] All 366,299 paths of two steps over subspaces of F₂⁴ and of three steps over
F₂³, plus every public path in the random words below, show 0 violations.
*Control:* pricing a MOVE at |Δdim| instead breaks the identity on 140 pairs.

**Lemma 1.2 (span invariant) [P].** Under (H1), every content held inside U at any
time lies in span(pubArr(U) ∪ ownArr(U)).

*Proof.* By induction over events:
- ADD, COPY and SCALE act inside one frame, so they stay inside U or outside U.
- INIT contributes 0.
- Departures and CLEARs only remove registers.
- Arrivals are counted in the span. ∎

**Theorem 1.3 (two-sided cut law) [P][C].** For every up-set U:
1. junk_U ≤ o_in(U) + p_out(U), under (H1)–(H3);
2. cout_U ≤ o_out(U) + p_out(U), under (H1).

*Proof.*
1. A public register's arrivals into U exceed its exits from U by 1 if it ends
   in U, and by 0 otherwise. Hence |pubArr| = |F_U| + p_out(U).
   - By Lemma 1.2 and (H2), span F_U ⊆ span(all arrivals).
   - So junk_U = dim span(all arrivals) − |F_U| ≤ |pubArr| + o_in − |F_U| = o_in + p_out, using (H3) for dim span F_U = |F_U|.
2. Let π be the coordinate projection onto the public registers that start in U.
   - Every register outside U starts with π-content 0, and only exits from U
     bring content out of U.
   - By the outside analogue of Lemma 1.2, every π-content outside U lies in
     the span of the π-images of the ≤ o_out + p_out exiting contents. ∎

Public entries into U appear on neither right-hand side.

[C] The checks use seeded random words over F₂³ (20,000 words, 1,200,000 cuts)
and F₂⁴ (1,500 words, 90,000 cuts). The words contain public ascents, descents
and laterals, owned ascents and descents, dirty CLEARs, and coefficients
{1, −1, ½, −⅓, ⅖, 3}. There are 0 violations on every word with invertible T.

*Controls:*
- Without the p_out term the bound fails on 409,113 and 22,583 cuts.
- All 726 (F₂³) and 19 (F₂⁴) violations of the full statement occur on the 21
  and 1 words with singular T, so (H3) is needed.

**Corollary 1.4 (need form) [P].** need_in(U) ≤ o_in(U), under (H1)–(H2) alone, by
Lemma 1.2. If p_out(U) = 0, then |pubArr| = |F_U|. Writing
pubjunk = dim(span pubArr + span F_U) − |F_U|, this gives
pubjunk ≤ need_in ≤ o_in.

**Corollary 1.5 (price of a credited substitute) [P].**
- A public register can add an arrival into U only after an exit from U.
- An exit E → F from an up-set has F ⊉ E, so its depth is k ≥ 1. By Lemma 1.1 it
  costs at least 2k in uncredited loss.
- An owned move that covers the same up-sets costs k: E ∩ F → E for entries, or
  E → E ∩ F for exits.
- One public exit can serve an entry-type and an exit-type deficit together.
  Owned moves then need both directions (2k), which is a tie.
- A zero-loss credited path is all nested ascents. It leaves no up-set, so it
  supplies zero capacity on both sides of Theorem 1.3.

**Census of #7334 [C]** (the vendored `WORD.json.gz`, exact mod 2³¹−1):
- All 6,232 public MOVEs strictly ascend, so p_out = 0 on every up-set.
- All 73 owned lifetimes are monotone: 38 have MOVEs, of which 19 only go up
  and 19 only go down.
- T is invertible (1,501 independent public final rows).
- On all 511 principal up-sets U_q, both sides of Theorem 1.3 hold.
- On each of the 501 up-sets with an owned entry, pubjunk = o_in. By
  Corollary 1.4 this forces **need_in = o_in with zero slack**. That is 2,032
  forced entry incidences in total: every owned entry carries a dimension that
  the public arrivals alone cannot supply.
- The copy-out side has minimum slack 0.

**Scope.**
- The credit rule is net credit dim T − dim S for a public path, with MOVEs priced
  at d(E,F), laterals included.
- A credit rule that also credits lateral paths or net-down paths is outside
  this law.
- The census is a statement about #7334's public layer. A different public
  layer changes pubArr.

## 2. Legality is forced by the specification

Tags: **[Q]** quoted from repository text (checked verbatim), **[P]**, **[C]**
checked by `legality.py`.

**Quoted facts.**
1. [Q] `upstream/build/sections/03-motifs.tex`: "For the complex network, take
   instead F = F₂ʰ with the ordinary dot product". The terminal labels are
   X_a : U_a → 𝓕 and Y_a : 0 → U_a^⊥.
2. [Q] `notes/general-clifford-frames.tex`: the charts are
   L_U = {(u, u+v) : u ∈ U, v ∈ U^⊥}, with L₀ = {(0,z)} and L_F = {(z,z)}.
   Fourier rank is d(L,L′) = h − dim(L ∩ L′).
3. [P] The dot product is also structural. wt(z+w) = wt z + wt w − 2|z ∩ w|, so
   the polar form of weight mod 4 is 2(x·y). This is the identity the phase
   frames telescope on in Prop. `complex-motif-interface`.

**Theorem 2.1 (charts are canonical) [C].** Over all Lagrangians of F₂ʰ ⊕ F₂ʰ,
for h = 4 (2,295 Lagrangians) and h = 5 (75,735):
- the charts are exactly the Lagrangians split by the pair (L₀, L_F), i.e.
  L = (L ∩ L₀) + (L ∩ L_F). These are 67 at h = 4 and 374 at h = 5;
- d(L_U, L_V) = dim U + dim V − 2 dim(U ∩ V) holds on all chart pairs.

**Theorem 2.2 (light cone over all frames) [C].** Take any Lagrangian, not only
charts, and q with q·q = 1.
- The zero-excess frames on x's route L_[q] → L_F are exactly the charts L_U
  with q ∈ U.
- The zero-excess frames on y's route L₀ → L_{q^⊥} are exactly the charts L_U
  with U ⊆ q^⊥.
- So the x_p cone and the y_t cone share a frame **iff p·t = 0**. This holds on
  56 pairs at h = 4 and 240 at h = 5.
- In particular the own pair (t = p) never shares a frame.

**Theorem 2.3 (no other form is free) [P][C].**
1. A relabelling by GL(h) fixes L₀ and L_F and maps L_U to L_{gU}. It sends ⊥
   to g^{−T}, so the incidence (g q_p)·(g^{−T} q_t) = q_p·q_t is unchanged.
2. Another symmetric Gram M needs the unipotent [[I,0],[M+I,I]]. That map moves
   L_F to graph(M) at price d(graph M, L_F) = rank(M + I). [C] all 448 invertible
   symmetric Grams at h = 4.
   *Control:* for each of the 447 Grams M ≠ I the rule "common frame iff
   p·M·t = 0" fails.
3. The charts transverse to L_[a] are exactly b^⊥ with a·b = 1 [C]. So any
   legality relation between endpoint pairs has the form R(p,t) = [a_p·b_t = 0]
   with a_p·b_p = 1. An alternating form has ω(v,v) = 0 and therefore never has
   this form.
4. The most general sound variant moves a Y end q^⊥ → b^⊥ with b ≠ q. That
   costs d(L_{q^⊥}, L_{b^⊥}) = 2 per moved end [C: all pairs, h = 4, 5].

*Control:* splitting by (L₀, L′) for some L′ ≠ L_F transverse to L₀ gives a
different chart family.

**Scope.**
- The target is C^{⊗m} as in the specification.
- The free (rank-0) adapters are block-lower-triangular, i.e. they fix L₀.
- The endpoint labels are the specification's.
- Ascend-only nesting of helpers is a separate verifier convention. It is not
  claimed to be SPEC-forced.

## 3. Owned-unit deletion bound for exact 8-term decoders on punctured E8 units

Tags: **[P]** proved in this note; **[C]** checked by `owned_deletion.py` (standard library only, exact integer, bit-mask
and `Fraction` arithmetic; `python3.12 -I -B owned_deletion.py` prints `PASS_OWNED_DELETION_BOUND` on success);
**[Q]** quoted from `research/complex-frame-pair-decoders/PROOF.md` (PR968; below, "PR968").

### 3.1 Statement

Let P be a puncture of p of the 120 E8 root lines, v = n = 120 − p live lines, and (A, B) an exact 8-term decoder on the
live lines in the normal form of PR968 §1. Then

    cst ≥ 56 − E(p),     E(p) = 0 (p ≤ 24),  1 (p = 25),  2 (26 ≤ p ≤ 35),  6 (36 ≤ p ≤ 38).

Consequences, for 82 ≤ n ≤ 120 (0 ≤ p ≤ 38):

* cst ≥ 50, so cst = 48 is impossible for every n ≥ 82;
* for n ≥ 85 (p ≤ 35), cst ≥ 54.

**Z16 variant.** Let Z16 be the sixteen lines left over when the 104-line clique of the PR968 decoder file `research/complex-frame-pair-decoders/inputs/pr717/P104_HIT_flip_3a.txt` is removed
(two disjoint frames F0, F1 of eight mutually orthogonal lines; every F0 line is non-orthogonal to exactly four F1 lines).
For punctures P ⊇ Z16 the same bound holds with

    E_Z(p) = 0 (p ≤ 34),  1 (p = 35),  2 (36 ≤ p ≤ 38).

These are lower bounds on cst. Attainment is not claimed.

### 3.2 Scope

* Exact 8-term decoders in PR968's normal form D = RA, T = RB, ABᵀ = 2I; decoders with n ≥ 9 terms are outside the scope.
* The 120 E8 root lines with the label pairing S9(u_i, u_j) = (⟨r_i, r_j⟩ + 1) mod 2 (h = 9 labels).
* Punctures with p ≤ 38 lines (the script can be run to p = 40; see §7). Non-root normals first admit a 2-dimensional
  reduction at p = 42, so the argument itself is unchanged for p ≤ 41.
* The Z16 variant requires the puncture to contain Z16 and is stated for p ≤ 38.

### 3.3 Premises

**(M) [Q, PR968 §1].** For p ≤ 56 the live lines span R⁸, so D = RA, T = RB with ABᵀ = 2I; with a_k, b_k the columns of
A, B: ⟨a_k, b_l⟩ = 2δ_kl, the a_k are pairwise non-parallel, the b_k are pairwise non-parallel, and a_k ∦ b_l for k ≠ l.
Term k costs ρ_k = rank S9[R_k, A_k], R_k = live ∩ C(a_k), A_k = live ∩ C(b_k), where C(a) is the set of lines not
orthogonal to a. cst = Σ ρ_k.

**(F0) [Q, reproduced C].** S9 has F2-rank 9, with 120 distinct rows. Let Λ be the 9-dimensional label space, on which S9
is non-degenerate; for a set X of lines V_X = span{u_i : i ∈ X}, and for each of the 511 nonzero functionals λ,
Viol(λ) = {i : λ(u_i) = 1}.

**(W) [P, C].** Every permutation of the lines that preserves |⟨r_i, r_j⟩| (in particular every element of W(E8)) preserves
S9, hence acts on Λ by a linear isometry (non-degeneracy), hence permutes the 511 violator masks. The script checks the
invariance of the pairing under all 120 reflections (sampled columns) and that three reflections permute the 511 masks.
Everything below that is stated "up to W" uses only this.

**(F6) [Q standard, P].** Every hyperplane flat of the E8 arrangement is W-conjugate to one of the eight flats ω_i⊥.
Proof from standard facts (Bourbaki, Lie Groups, Ch. V §3): every vector is W-conjugate into the closed dominant chamber;
the roots orthogonal to a dominant vector n are the integral span of the simple roots orthogonal to n. A rank-7 flat has a
normal n, which may be taken dominant, orthogonal to 7 independent roots, hence to exactly 7 simple roots, so n is a
multiple of one fundamental weight.

### 3.4 Proof chain

Notation. For a normal n and a puncture P let X(n) = live ∩ C(n), red(n) = 9 − dim V_{X(n)}, and
N(n, P) = {λ : Viol(λ) ∩ C(n) ⊆ P}. Then N(n, P) is the annihilator of V_{X(n)}, so red(n) = dim N(n, P). For a subspace
W of functionals write R(n, W) = (∪_{λ ∈ W∖0} Viol(λ)) ∩ C(n). Then dim N(n, P) ≥ r iff some r-dimensional W has
R(n, W) ⊆ P. A normal "of type red-r" is one with an r-dimensional such W.

**(a) Per-term saving [P].** With s_k = 9 − ρ_k: ρ(X, Y) = dim V_X − dim(V_X ∩ V_Y^⊥) ≥ dim V_X + dim V_Y − 9
(PR968 eq. (2)), so

    s_k ≤ red(a_k) + red(b_k).                                                       (1)

If a_k ∥ b_k = n and X = X(n), then ρ_k = dim V_X − dim(V_X ∩ V_X^⊥), so

    s_k = red(n) + dim(V_X ∩ V_X^⊥) ≤ 2 red(n),                                      (2)

because V_X^⊥ ≅ N(n, P) has dimension red(n). Moreover, if n = α is a root with α ∈ P, then λ_α := S9(u_α, ·) lies in
N(α, P) (Viol(λ_α) ∩ C(α) = {α}, see (c)), so u_α ∈ V_X^⊥. If u_α were also in V_X, then S9(u_α, u_α) = 0, because V_X^⊥ is orthogonal to V_X; but
S9(u_α, u_α) = (2 + 1) mod 2 = 1. So u_α ∉ V_X, hence V_X ∩ V_X^⊥ is a proper subspace of V_X^⊥ and

    s_k ≤ 2 red(α) − 1     (parallel term on a root α ∈ P).                           (3)

**(b) Normals with red ≥ 2 are roots, for p ≤ 41 [C + P].**

* *Hyperplane-flat normals.* By (F6) and (W) the census of all hyperplane-flat normals reduces to the eight standard
  representatives. The script generates the W-orbits of the eight fundamental weights by simple reflections (packed Dynkin
  labels), obtaining 240, 2160, 6720, 17280, 60480, 69120, 241920, 483840 vectors, i.e. 440 880 normal lines, and
  computes for each type all 511 single violator sets and all 43 435 two-dimensional subspaces:

  | flat type | flat lines | |C| | min | next | π7 |
  |---|---|---|---|---|---|
  | E7 (root normal) | 63 | 57 | 1 | 24 | 25 |
  | D7 | 42 | 78 | 14 | 34 | 42 |
  | E6+A1 | 37 | 83 | 27 | 28 | 51 |
  | A7 | 28 | 92 | 28 | 35 | 56 |
  | D5+A2 | 23 | 97 | 33 | 41 | 61 |
  | A6+A1 | 22 | 98 | 35 | 35 | 62 |
  | A4+A3 | 16 | 104 | 40 | 43 | 68 |
  | A4+A2+A1 | 14 | 106 | 43 | 43 | 70 |

  This is PR968's table [Q]; it is reproduced [C], and the script recomputes the row directly for 24 randomly chosen orbit members
  (three per type). A flat-type normal n has red(n) ≥ 2 only if |P| ≥ π7(n); for non-root types π7 ≥ 42.
* *Non-flat normals.* If the roots orthogonal to a span at most 6 dimensions, extend a root basis of that span to a root
  basis of R⁸ and drop two different added roots: this gives two distinct root-spanned hyperplanes H1, H2 with
  hyperplane-flat normals ω1, ω2 and C(ω1) ∪ C(ω2) ⊆ C(a), so R(a, W) ⊇ R(ω1, W) ∪ R(ω2, W) for every W. If some ω_i
  is not a root, |R(a, W)| ≥ π7(ω_i) ≥ 42. If both are roots α1 ≠ α2, then (by transitivity of W on root pairs of a given
  inner product) two classes occur, and the script computes min over W of |R(α1, W) ∪ R(α2, W)| = 54 for ⟨α1, α2⟩ = 0 and
  52 for |⟨α1, α2⟩| = 1 [C] (three pairs per class are computed and agree).
* Hence red(n) ≥ 2 forces |P| ≥ 42 unless n is a root.

**(c) Root normals [C].** For every root α (all 120 computed directly): the only single violator set of size < 24 within
C(α) is {α}, from λ_α (min 1, next 24). For the red levels: the smallest R(α, W) over 2-, 3-, 4-dimensional W has 25, 37,
45 lines respectively (all 4-dimensional W with |R| ≤ 45 are enumerated by extension of all lower-dimensional W). The
2-dimensional sets of at most 40 lines have sizes (number of distinct sets): 25 (63), 29 (128), 33 (63), 36 (336), 37 (336),
40 (4977), the same for every root. Hence for p ≤ 44, red(α) ≤ 3, and for p ≤ 36, red(α) ≤ 2. Every red-2 set of at most 35
lines contains α, so α ∈ P in that range.

**(d) Accounting [P].** The 16 normals a_k, b_k are subject to (M): a root appears at most once among the a's and at most
once among the b's, and appears on both sides only in a single term with a_k ∥ b_k. Put the base saving of a term at 2.
By (1), a non-parallel term has s_k ≤ 2 + (red(a_k) − 1)⁺ + (red(b_k) − 1)⁺. By (b), a non-root normal has red ≤ 1; by (2) a
parallel term on a non-root normal has s_k ≤ 2. For a root α with red(α) = r ≥ 2 the contribution above the base is at most

    e(r, α ∈ P) = max(r − 1, 2r − 3),        e(r, α ∉ P) = max(r − 1, 2r − 2) = 2r − 2,

by (1), (2) and (3) (the value for α ∉ P uses only (2): this is generous). Therefore

    Σ s_k ≤ 16 + Σ_{roots α, red(α) ≥ 2} e(red(α), α ∈ P),        cst = 72 − Σ s_k ≥ 56 − Σ e.      (4)

**(e) The maximum of Σ e over punctures [P + C].** Define E(p) as the maximum of Σ e, with e evaluated as in (d), over
all unions U of "reduction sets" with |U| ≤ p, where a reduction set is R(α, W) for a root α and a W of dimension 2 or 3,
and each root is credited at the level actually reached in U (level 3 if some R(α, W3) ⊆ U, else level 2 if some R(α, W2)
⊆ U). Claim: for every puncture P with |P| ≤ p, Σ e(P) ≤ E(p).

*Proof.* For each root α reduced in P pick a W ⊆ N(α, P) of dimension red_P(α), and let U be the union of the R(α, W). Then
U ⊆ P, red_U(α) = red_P(α) for these roots, and the evaluation of e on U is at least that on P: red is monotone in the
puncture, a root outside U but inside P is evaluated as "not in U", for which e is larger, and further roots reduced in U
only add non-negative terms. So Σ e(P) ≤ Σ e(U) ≤ E(|U|) ≤ E(p). ∎

*Enumeration [C].* By (W), W(E8) is transitive on root lines (the script builds, for every root a, a Weyl element sending
root 0 to a), so the root-0 reduction sets can be moved to every root. The union U contains a reduced root; moving it to
root 0 with a Weyl element, U contains a 2-dimensional reduction set of root 0, which can be moved by Stab(root 0) =
W(E7) × {±1} (generated by the 63 reflections in lines orthogonal to root 0) to one of the six orbit representatives, of
sizes 25, 29, 29, 33, 36, 37 (orbit lengths 63, 72, 56, 63, 336, 336). The script seeds the search with these six sets and
enumerates every union reachable by adding only "useful" sets (a set of a root not yet credited at that level), with
|U| ≤ p. Every minimal union of the construction above is reached (add its sets in any order and skip a set whose root is
already credited at its level). The number of distinct unions is 147 for p ≤ 38. The table is

| p | 24 | 25 | 26–35 | 36–38 |
|---|---|---|---|---|
| E(p) | 0 | 1 | 2 | 6 |

The optimum at p = 36 consists of six roots, all in the puncture, each at level 2. Independent check without the orbit
reduction: seeding with all 926 reduction sets of root 0 of size ≤ 38 (8479 distinct unions) gives the same table.

**(f) Z16 [C].** The repository file `research/complex-frame-pair-decoders/inputs/pr717/P104_HIT_flip_3a.txt` (SHA256
`8e0178db02c14e1b29058cdbdbd50aac22f2b55a1ba21dc82f417610c9932526`, a decoder over a 104-line clique, PR968
`inputs/pr717/`) gives the Gram matrix of the 104 live lines as DTᵀ/2. The script embeds the clique in the E8 root system
by an exact rational solution (eight independent lines are matched to roots with the same Gram matrix; the images of all
104 lines are checked to be roots), and takes the complement Z16. All embeddings differ by W, so Z16 is determined up to
W. For P ⊇ Z16 the argument of (e) applies to U ∪ Z16 and the search is seeded with Z16 (no symmetry reduction); it
visits 7441 distinct unions and gives E_Z = 0 (16 ≤ p ≤ 34), 1 (p = 35), 2 (36 ≤ p ≤ 38).

### 3.5 Controls

The script confirms that the following changes alter at least one checked number (printed as `control ...`):

* flipping one symmetric entry of S9 changes the F2 rank from 9 to 11;
* dropping the unit coordinate of the labels changes (min single violator set, min red-2 set) of a root from (1, 25) to
  (24, 36);
* removing the 25-line orbit representative from the seeds changes E(25) from 1 to 0;
* replacing 2r − 3 by 2r − 2 for a punctured root in (d) changes E(36) from 6 to 12;
* not requiring the root's own line in its reduction sets changes E(24) from 0 to 4;
* replacing Z16 by sixteen lines inside a 25-line reduction set changes E_Z(25) from 0 to 1.

### 3.6 Notes on the use of (d)

The value e(r, α ∉ P) = 2r − 2 and the use of the maximum of the one-sided and parallel values are upper bounds, kept
generous; no punctured configuration with a root outside the puncture occurs in the optimum at p ≤ 38.

### 3.7 Reproduction and range

`python3.12 -I -B owned_deletion.py` runs the whole chain to p = 38 in under one minute and ends with
`PASS_OWNED_DELETION_BOUND`. The optional argument `--pmax 40` extends the enumeration (sets up to 40 lines, about 75 s; the table
beyond p = 38 is printed and not asserted; it gives E(39) = E(40) = 6 and E_Z(39) = E_Z(40) = 2). The PR968 input file is read from the repository and pinned in SOURCES.json.

## 4. Odd-rank classes of per-port contracts

Tags: **[P]** proved below; **[C]** checked exactly by `contracts.py` (standard library only; `python3.12 -I -B contracts.py`; ends with `PASS_CONTRACT_ODD_RANK`).

### Setting
q is a primitive 4th root of unity, sigma: q -> -q (so sigma fixes q-even Laurent monomials and negates q-odd ones). Scalars lie in Z[i,1/2] (checker: exact Gaussian rationals; matrices are Laurent polynomials in q, evaluated at q = chi in {1, i, -1, -i}). For an invertible N(q) put

* sigma-factor R(N) = sigma(N) N^-1;
* o(N) = max over chi of rank(R(N)(chi) - I);
* Odd(N) = (N - sigma(N))/2 = the q-odd part; r(N) = max over chi of rank Odd(N)(chi).

A **q-even monomial** is a signed permutation matrix with entries +-q^e, e even.

### Theorem 4.1 (oddness identity) [P][C]
o(N) = r(N), and more precisely rank(R(N)(chi) - I) = rank Odd(N)(chi) at every point chi.
*Proof.* sigma(N) - N = -2 Odd(N) and 2 is invertible, so R - I = (sigma(N) - N) N^-1 = -2 Odd(N) N^-1, and N^-1 is invertible. QED.
[C] all 32 representatives of Theorem 4.2, and 368 (matrix, point) pairs for random 2x2 and 3x3 Laurent matrices with controlled odd rank (o up to 3).

### Theorem 4.2 (invariance under q-even monomials) [P][C]
o(E1 M E2) = o(M) for q-even monomials E1, E2.
*Proof.* sigma(E) = E, so R(E1 M E2) = E1 R(M) E1^-1. Conjugation preserves rank(R - I). QED.
[C] exhaustive over the 32 x 32 pairs of q-even 2x2 monomials, for all 32 representatives (32768 checks).
*Control:* the odd monomial diag(1,q) sends o(L_1) = 0 to 1, and qI sends it to 2, so evenness is needed.

### Theorem 4.3 (classification of per-port contracts) [C]
Contracts M = W1 L_c W2, with W1, W2 monomial (entries +-q^e), L_c = [[1,0],[c,1]], c in {1, q} (c = 0 gives monomials), up to q-even monomials on both sides, reduce to W = diag(q^a, q^b), a,b in {0,1}: 32 representatives (a,b,c,d,c-exponent). Their invariants:

| class | reps | o | r | sigma-factor | involutive | b_even | b_all |
|---|---|---|---|---|---|---|---|
| A | 4 | 0 | 0 | I | yes | 1 | 1 |
| B (contains L_q) | 4 | 1 | 1 | transvection | no | 1 | 1 |
| C | 16 | 1 | 1 | reflection | yes | 1 | 1 |
| D (contains H below) | 4 | 2 | 2 | non-involutive (-I + nilpotent) | no | 2 | 1 |
| D' | 4 | 2 | 2 | -I | yes | 2 | 1 |

with b_even = min over q-even monomials W of max_chi rank(M - W), b_all = the same minimum over all q-monomials (entries +-q^e, e in Z/4). In particular o = r in every class (o > r never, o > 0 with r = 0 never). The c = 0 monomial cases give 3 classes: even monomial (o = r = 0, I), diag(1,q) type (o = r = 1, reflection; two reps), qI (o = r = 2, -I).
*Proof sketch.* Multiplying by even monomials does not change any invariant (Theorem 4.2 and its analogue for the bill). Pulling the odd part of W1, W2 through L_c reduces to the 32 listed cases; each is a finite computation at the four points. [C] performs it.
*Generic scalars.* Replacing every unit entry by fixed non-trivial Gaussian rationals (3 deterministic draws x 32 reps) gives the same (o, r, sigma-factor type) pattern: 12 / 12 / 48 / 12 / 12 for A, B, C, D, D'. [P] (reason): scalars multiplying a diagonal factor cancel in R, and the scalar in the cross term of L_c rescales a nilpotent part.
*Controls:* (i) with odd monomials allowed in the minimum, D and D' drop from 2 to 1 while o stays 2, so the bill must use q-even W; (ii) sigma = identity gives o = 0 for every representative, sigma': q -> iq changes o on 12 of 32 representatives.

### Theorem 4.4 (o is not a parity) [P][C]
Let L_q = [[1,0],[-q^-1,1]] and H = [[1,-q],[q^-1,0]]. Then
* o(L_q) = 1 and L_q^2 = [[1,0],[-2q^-1,1]] has o = 1 (not 0): o is not a Z/2-valued function that adds under composition. In general o(MN) <= o(M) + o(N) only (R(MN) = (sigma(M) R(N) sigma(M)^-1) R(M) and rank(XY - I) <= rank(X-I) + rank(Y-I)). [C] on all 1024 products of representatives.
* o(H) = o(H^2) = 2 and H^3 = -I as an identity of Laurent matrices (so o(H^3) = 0). [C]
* Factorisation: with J = [[0,-1],[1,0]] and J_q = diag(q, q^-1) J one has exactly H = J_q L_q. (The opposite sign J' = [[0,1],[-1,0]] gives diag(q,q^-1) J' L_q = [[-1,q],[-q^-1,0]], which is not H.) o(J) = 0; o(J_q) = 2 with sigma-factor -I. [C]
* The genuine Z/2 invariant is eps(M) = det R(M). Since det R = det M(-q)/det M(q), eps is multiplicative, equals (-1)^(parity of the q-exponent of det M) for the unit-entry reps, is +1 on transvections (class B) and -1 on reflections (class C). [P][C] multiplicative on all 1024 products of reps; eps = (-1)^(a+b+c+d) on all 32 reps.
* o is not a function of eps: eps = +1 for J, L_q, J_q with o = 0, 1, 2. [C]

### Theorem 4.5 (equality clause, Lemma E; char != 2) [P][C]
Let g = h1 h2 ... hk in GL(V), with sum_j rank(h_j - I) = rank(g - I) = m, and g = -1 on Im(g - I). Then every h_j is an involution.
*Proof.* (a) Hypothesis on g means (g + I)(g - I) = 0, i.e. g^2 = I; since 2 is invertible, V = K + W with K = ker(g - I), W = ker(g + I) = Im(g - I), dim W = m.
(b) Put U_j = Im(h_j - I). From g - I = (g' - I) h_k + (h_k - I) with g' = h1...h_{k-1}, induction gives Im(g - I) contained in sum_j U_j. Dimensions force W = direct sum of the U_j, dim U_j = m_j, sum m_j = m.
(c) Hence each h_j is the identity on K (K is the intersection of ker(h_j - I) by the same count) and preserves W (h_j v - v lies in U_j inside W).
(d) For j = k: on W, h_k = -(g')^-1 so h_k + I = (g')^-1 (g' - I), and rank(h_k + I) <= sum_{i<k} m_i = m - m_k. Also rank(h_k - I) + rank(h_k + I) >= rank(2I|_W) = m. So rank(h_k+I|_W) = m - m_k exactly, and dim ker(h_k - I|_W) = m - m_k and dim ker(h_k + I|_W) = m_k, which add to m. These two kernels meet trivially (char != 2), so W is their direct sum, h_k acts as +-1 on W, and as I on K: h_k^2 = I.
(e) For other j, conjugate: h_j ... h_k h_1 ... h_{j-1} = (h_1...h_{j-1})^-1 g (h_1...h_{j-1}) satisfies all the hypotheses (rank and the -1 condition are conjugation-invariant), and h_j is its first factor; apply (d) to the cyclic order ending in h_j. QED.
[C] counts, all with 0 counterexamples:
* GL(2,F_5): 480 elements, 9989 rank-additive pairs, 93 with the hypothesis; GL(2,F_7): 2016 elements, 86407 rank-additive pairs, 171 with the hypothesis.
* GL(2,F_3) triples: 826 rank-additive, 76 with the hypothesis.
* GL(3,F_3): h1 with rank(h1 - I) <= 1 (222) against all g with g^2 = I (236): 1874 qualifying factorisations.
*Controls (hypothesis dropped):* GL(2,F_5): 9896 rank-additive pairs without the hypothesis, 9296 with a non-involutive factor; GL(2,F_7): 86236 and 83884; GL(3,F_3), both factors of rank <= 1: 40456 and 30160 (transvection factors).
Consequence: if a sigma-factor g satisfies the hypothesis (an involution with -1 eigenspace of dimension m), then in any rank-additive factorisation of g all factors are involutions; the sigma-factors of classes B and D are not involutions, so they never satisfy the hypothesis.

### Theorem 4.6 (hub lemma, general form) [P][C]
Let B be h x n over a field, K = ker B (dim K >= n - h). Suppose every "hub" operation on R^2 (x) R^n has the form Y (x) (B^T X B). Let T be an operator on R^2 (x) R^n whose q-odd part is Odd (x) I_n. If T = (hub operations) + (s operations of rank 1), then s >= rank(Odd) * dim K.
*Proof.* Let P be any projector onto K and Pi = I_2 (x) P. Each hub operation vanishes on Pi: (Y (x) B^T X B)(I (x) P) = Y (x) B^T X (B P) = 0. Therefore Odd (x) P = T_odd Pi equals a sum of s rank-1 operators composed with Pi, so its rank is at most s; and rank(Odd (x) P) = rank(Odd) rank(P) = rank(Odd) dim K. QED.
[C] n = 104, h = 8, B a deterministic integer 8 x 104 matrix of exact rank 8 (rational elimination), dim K = 96; exact projector P onto K (P^2 = P, BP = 0, rank 96); hub-form operations B^T X B annihilate K; and the exact rank of Odd(M) (x) P, computed by sparse elimination over Gaussian rationals, equals rank Odd * 96 for the odd parts of A, B, C, D, D', the monomial classes, H and L_q: 0, 96, 96, 192, 192, and 96 / 192 for diag(1,q) / qI; 192 for H, 96 for L_q.
*Controls:* B of rank 7 gives dim K = 97 (bill 97 per unit); without hub structure the same count is rank Odd * n = 104 per unit.

### Theorem 4.7 (units-conserved arithmetic) [P][C]
Parameters: J events per port per word = 17, target odd rank = 36. For a class with (r, o, involutive sigma-factor), set
 total = 17 r + (36 - 17 o if involutive, else 37 - 17 o).
Since o = r (Theorem 4.3), total = 36 - 0 + (0 if involutive else 1) for every class:

| class | r | o | involutive | 17 r + floor | total |
|---|---|---|---|---|---|
| A | 0 | 0 | yes | 0 + 36 | 36 |
| B | 1 | 1 | no | 17 + 20 | 37 |
| C | 1 | 1 | yes | 17 + 19 | 36 |
| D | 2 | 2 | no | 34 + 3 | 37 |
| D' | 2 | 2 | yes | 34 + 2 | 36 |

[P] is pure arithmetic from the stated counts; the involutive branch uses Theorem 4.5 (equality). [C] the table above is computed from the classification output. Control: dropping the involution clause would read 37 for C and D'.

### Scope
2x2 per-port contracts of the form W1 L_c W2 over monomials +-q^e with generic non-zero scalars (and, in Theorems 4.1, 4.2, 4.5 and 4.6, arbitrary invertible matrices where stated). Statements about the target odd rank (36), the event count (17), n = 104 and h = 8 are parameters of Theorems 4.6 and 4.7 and are not derived here. Theorem 4.5 requires characteristic different from 2 (the checks use F_3, F_5, F_7).

## 5. Helper-layer lower bounds on #7334

Tags: **[P]**, **[C]** checked by `helper_floor.py`.

**Setting.**
- The fixed registers are the mains (live X, Y; hosted X2, Y2) and the owned
  registers. They keep their whole schedule.
- Every other public register is a helper. A helper climbs strict inclusions
  a = p₀ < p₁ < … < p_{k+1} = b in dimension.
- Its price is D0 = f(b−a) − Σ f(p_{i+1} − p_i), with f(r) = r ln r.
- Contents are compared after the projection π that deletes helper coordinates.

**Lemma 5.1 (per-frame need) [P][C].** At a frame G, define:
- R_G = rank of the π-contents of fixed registers at every fixed event at G
  (arrivals, departures, both sides of fixed↔fixed ADDs, CLEARs, initial and
  final residents);
- n_G = the number of fixed arrivals (initial residents and every fixed MOVE in);
- m_G = the number of fixed departures (MOVEs out, CLEARs, final residents).

Then the number of helper interior stops at G is at least
B_G = max(0, R_G − n_G, R_G − m_G).

*Proof.* At G, ADD, SCALE and COPY preserve the span of the registers present.
So span(arrivals) = span(departures and final residents). Helper starts and ends
contribute independent tokens in ker π. Only helpers that both arrive and leave
can carry π-content through G. ∎

[C] On #7334: 979 frames, **Σ B_G = 681**. By dimension 1…8 this is 124, 141,
84, 48, 31, 48, 95, 110. #7334 meets stops_G ≥ B_G on every frame.
*Control:* dropping the arrival credit n_G inflates the need to 2,823.

**Theorem 5.2 (sound floor) [P][C].** Every chain in dims 0..9 with k interior stops
has D0 ≥ k·f(2), with minimum slack exactly 0. This is checked exhaustively;
*control:* k·f(3) fails.

So a helper with k stops costs at least k single-stop helpers. When the number of
helpers and their endpoints are free, the minimum chain cover is f(2)·Σ B_G, and
nesting does not bind.

**Helper D0 ≥ f(2)·681 = 944.07**, against #7334's helper layer of **9,983.73**
(1,101 helpers).

**Theorem 5.3 (conditional floor) [P][C].**
- *Additional premise:* the multiset of helper (start dim, end dim) pairs is
  #7334's: 22 classes, 1,101 helpers.
- With a fixed, D0 telescopes into Σ g_a(p_i, p_{i+1}), where
  g_a(p,q) = f(q−a) − f(p−a) − f(q−p) ≥ 0. Dropping a stop never raises D0.
- So a 22-commodity flow over the 530 need frames and their 12,001 strict
  inclusions, with coverage Σ inflow(G) ≥ B_G, is a relaxation of every chain
  cover.
- `data/lp-dual-c2.json` holds dual multipliers. `helper_floor.py` recomputes the
  Lagrangian bound from them. That bound is valid for any multipliers by weak
  duality, so no solver is trusted: **≥ 1,367.08**.
- *Controls:*
  - perturbed multipliers give a far weaker bound;
  - #7334's own chains, restricted to need frames, are a feasible point of
    cost 5,842.98.

**Reading [C].** #7334's 9,983.73 splits as follows:
- 4,140.75 on stops at zero-need frames;
- 5,842.98 on its need-serving chains, against the conditional floor of
  1,367.08 for the same endpoint census.

**Scope.**
- These floors use per-frame ranks of fixed contents only.
- Bounds of this family cannot exceed roughly f(·)·Σ B_G. They cannot certify
  near-optimality of a layer, and no attainment is claimed.
- The 1,367.08 floor holds only under the stated endpoint premise.
