# Proofs: one number governs the native call

Status tags used for every claim:

| tag | meaning |
|---|---|
| **PROVED-LEAN** | machine-checked in `lean/Skel.lean` (Lean 4 + Mathlib, no `sorry`), under the stated hypotheses |
| **PROVED-PAPER** | proof given here, not formalised |
| **CHECKED-EXACT** | exact or 60-digit computation. "verify.py" means it is rebuilt by `verify.py` from the public #4610 package; "source" means it was run in the research notes on data not shipped here |
| **CONDITIONAL** | holds only under a stated modelling assumption, named in its scope |

Every claim carries its scope. Pointers `[k]` refer to numbered lines of `data/verify_output.txt`.

Notation. P = `research/joint-helper-lattice/PROOF.md`; Q = `research/kappa-round3-warp-20261022/PROOF.md`; V = that directory's `verify_candidate.py`; NE = `research/kappa-rebuild/complex/native_extensions.py`. "#4610" is the word `kappa-round3-warp-20261022/ACTUAL-WORD.json.gz`, whose κ is in (0.0030217758, 0.0030217759) [8].

## 0. Setting

An invoice is a pair of multisets: credits T and paid jobs P of positive integer ranks. Its moment is f(t) = Σ_T k^t − Σ_P r^t. The pricer returns the first crossing of f in C = 1 − t on (0, 0.05], and f > 0 at small C. Fix a bar and write t* = 1 − bar; the default is bar = 0.0030233 (about 0.05% above κ(#4610)). Because the pricer returns the first crossing, **κ ≥ bar implies f(t*) ≥ 0** with no further assumption. The converse needs f to have a single crossing on (0, 0.05] (assumption S1, checked on a 1000-point grid for the invoices used here).

**Frames and fields.** A frame is a subspace of F₂⁹. A persistent field carries one logical value in a current frame, from a start frame S_f to a final frame T_f. Events on a field are paid transports E → F (which cost a rank) and free events (warps K_G with G ∈ GL(9,2), and scalar operations). A climb is a nested paid transport E ⊂ F. A field's history is an integer dimension path d₀ = dim S_f, …, d_n = dim T_f with costs c_j ≥ 0. Write R_f = dim T_f − dim S_f.

**Contract hypotheses (used explicitly).**

| | statement | source | status |
|---|---|---|---|
| H1 | A field's frame dimension changes only at paid transports. Warps preserve dimension. Scalar operations act inside one frame. | P:15–17; Q:5–8 | package contract. On #4610 all 240 warps preserve dimension and every field replays start → final in both orientations [2] |
| H2 | A nested transport E ⊂ F costs dim F − dim E. A general transport costs dim E + dim F − 2 dim(E ∩ F) ≥ \|dim F − dim E\|, with the parity of dim F − dim E. | nested: P:15, Q:5–6. General formula: L_E ∩ L_F = (E ∩ F) ⊕ (E + F)^⊥ | nested: package contract. General formula: **PROVED-LEAN** (`rankCost_ge_abs`, `rankCost_nested`, `rankCost_parity`) |
| H3 | A helper is credited once, with its whole residual rank R_f = dim T − dim S, S ⊊ T. No duplicate field, discarded helper, clean input or free temporary productive input. | P:19; Q:18–21; V:40 | package contract |
| H4 | Transports of helper and main fields are ascending climbs. | NE:123 | a verifier convention. Section 3 shows the results hold with or without it |
| H5 | Unit (v, d) = (112, 8). One pair per LOCAL, port-uniform. Kap path controller with thick set {0, 2p, odd}, e = 1. | model family | model assumption. The p16 a7 invoice is public [1] |

The **centre** is the owned rank-8 jobs on the C buffers. In #4610 there are 8 per call (M = 64).

## 1. Analytic core (PROVED-LEAN)

For 0 < t ≤ 1 and x ↦ x^t on [0, ∞):

- **Lemma 1 (subadditivity).** (Σxᵢ)^t ≤ Σxᵢ^t, strictly for 0 < t < 1 when two terms are positive. `rpow_add_le`, `rpow_sum_le`, `rpow_add_lt`, `rpow_sum_lt`.
- **Lemma 2 (chord).** For 0 ≤ x ≤ y: x^t ≥ x·y^{t−1}. `mul_rpow_sub_one_le`.
- **Lemma 3 (exchange).** For 0 ≤ x ≤ y and r ≥ 0: (y+r)^t − y^t ≤ (x+r)^t − x^t. Proof: concavity applied at μ = r/(y−x+r). `rpow_increment_antitone`.

## 2. Paths, Theorem B and Theorem C

**Lemma 4 (path identity; PROVED-LEAN).** For an integer path with R = d_n − d₀ and down-mass D = Σ max(−Δ_j, 0): Σ|Δ_j| = R + 2D. Hence under H1–H2, Σ c_j ≥ R + 2D. `FieldPath.sum_abs_eq`, `mass_ge`.

**Theorem B (per-call decomposition; PROVED-LEAN under H1–H3).** Every paid native job is a single-field climb or a centre job. The native per-call moment φ(t) := Σ_helpers h^t − Σ_paid r^t satisfies

  φ(t) = −2v·d^t − Σ_centre c^t − Λ(t),  Λ(t) = Σ_f Λ_f(t),  Λ_f(t) = Σ_j c_j^t − R_f^t ≥ 0.

For 0 < t < 1, Λ_f = 0 iff the field pays a single job of rank R_f (or none if R_f = 0); two positive jobs give Λ_f > 0. Proof: partition the jobs by field; Lemma 4 gives Σ c_j ≥ R_f, then Lemma 1 and monotonicity give Σ c_j^t ≥ R_f^t. `decomposition`, `FieldPath.lam_nonneg`, `lam_pos_of_two`, and for real subspace histories `lam_nonneg_ofSubspaces`.

*Application to #4610 (CHECKED-EXACT, verify.py).*
- Σ climbs = R_f on all 632 fields, in both orientations [2].
- Climb profile plus the 8 centre jobs equals the public `local_paid` exactly [2].
- Λ(t*) = **23.8746264727**: helpers 16.2711462249, mains 7.6034802478 [4].
- The identity closes to 6·10⁻⁵⁷ [5].

**Theorem C (no net-productive helpers; PROVED-LEAN under H1–H3).** For every helper, Hnet_f = Σ c_j − R_f ≥ 0, and its moment contribution R_f^t − Σ c_j^t = −Λ_f ≤ 0, with equality iff it has exactly one climb. A helper is at best neutral whatever its credited rank, so the helper census enters κ only through Λ_h. Crediting descents as well does not change this: credit mass R_f + D against paid mass ≥ R_f + 2D. `hnet_nonneg`, `hnet_inverse_nonneg`, `helper_contribution_nonpos`.

*Consequence (PROVED-PAPER).* A net-productive helper (Hnet < 0) needs either a free dimension increase (violating H1) or credit for a non-independent input (violating H3). The moment can turn positive only by crediting finer than paying: credit {1,1} against paid {2} gains 2 − 2^t* = 0.0041868 [10].

**Lemma 5 (descents never help; PROVED-LEAN for nested endpoints, PROVED-PAPER otherwise).** With endpoints fixed, replacing a field's path by the single transport start → final never raises the paid moment. For nested endpoints (all helpers and mains in the contract) this is exactly Λ_f ≥ 0. For non-nested endpoints it is the triangle inequality of the rank metric, which is outside the verifier's current scope. A single-field exhaustive search (all walks of at most 5 steps, ranks 1–9, dimensions 0–12, 40 digits) agrees: the minimum paid moment is that of the single climb (CHECKED-EXACT, source). Hence H4 is a convention that costs nothing.

## 3. Descent price (Theorem D)

**Theorem D (PROVED-LEAN under H1, H2).** A field with fixed endpoints, R ≥ 0, and one descent of rank r has

  Λ_f(t) ≥ r^t + (R+r)^t − R^t ≥ r^t + (9+r)^t − 9^t  (second step for R ≤ 9).

Proof: the descent step pays ≥ r; the other steps telescope to R + r (Lemma 4), so by Lemma 1 their moment is ≥ (R+r)^t; the second inequality is Lemma 3. `descent_price`, `descent_price_nine`.

At t* [9] (CHECKED-EXACT, verify.py): the bound is 1.99022 (r = 1), 3.97594 (r = 2), 5.95983 (r = 3), 7.94244 (r = 4). Corollary: any word with Λ ≤ Λ* contains at most ⌊Λ*/1.99022⌋ = **11** rank-1 descents.

*Order of magnitude (PROVED-PAPER).* A descent costs first order in mass (about 2r). Any unlock of fragmentation is a concavity gain, second order in 1 − t (about 0.003 per unit of mass).

*Application to #4610 (CHECKED-EXACT, source; not rebuilt by verify.py).* With the scalar program fixed, relaxing the frame model so that all 44 frame-infeasible helpers are free gains at most 1.3293 + 0.1176 of Λ, below the price 1.9902 of one descent. A relaxation freeing the hub field 225 completely gains 0.07417 against that price, net −1.916 per call. These are relaxation bounds, and are scoped to a fixed scalar program with nested descents only (CONDITIONAL on that scope).

## 4. Theorem A and the exact ship threshold

**Theorem A (controller separation; PROVED-PAPER, CHECKED-EXACT at p16 a7 by verify.py).** Under H5, f(t) = (p+2)·φ(t) + Γ_{p,a}(t), where Γ depends on the controller only: targets 2v at 1 + d(p+2) and 2v at 1 + d(j+1) for j = 1..a and j = 1..b (b = p−1−a); paid v(p−1) rank-1 thin shears and 2v at d(j+1) for the same j. This is the invoice construction itself. Public check [1]: at (16, 7), with (H, N) from `ARITHMETIC.json`, it reproduces `targetMoment` and `paidMoment` of `NumericalMoments.lean` coefficient by coefficient (13 target and 14 paid terms).

**Corollary A1 (universal controller; CHECKED-EXACT for p ≤ 400 plus PROVED-PAPER tail, verify.py; CONDITIONAL on the kap family).** Define φ* = −max_{p,a} Γ_{p,a}(t*)/(p+2). Over all p ≥ 1 and all a the maximum is at p = 16, a ∈ {7, 8} (the same invoice): φ* = **−1868.2220388492** [7], [7b]. For p ≤ 400 this is an exact search. For p > 400, write Γ/(p+2) = F(p) + Σ_{k=1}^{p−1}(2v·δ_{j_k} − v)/(p+2) with F(p) = 2v(1+d(p+2))^t/(p+2), which decreases in p, and δ_j = (1+d(j+1))^t − (d(j+1))^t ≤ δ_1 (Lemma 3), each bracket positive; so Γ/(p+2) ≤ F(401) + 2vδ_1 − v = 1858.7424 < −φ* [7b]. In the family, some (p, a) clears the bar with native call φ only if φ(t*) ≥ φ*, and under S1 also if.

**Theorem (ship threshold).** Under H1–H5 and the #4610 centre (8 rank-8 jobs per call):

  κ ≥ bar ⟹ Λ(t*) ≤ **Λ\* = −φ\* − 232·8^{t\*} = 23.8536932758.**

PROVED-PAPER from Theorem B, Theorem A and the first-crossing remark in §0. The converse holds under S1 (CONDITIONAL). For #4610 [6]:

- Λ − Λ* = **0.0209331969 per call**.
- 18(Λ* − Λ) = −0.3767975440, which equals the public invoice f(t*) to 10⁻⁴⁰. This closes the whole chain independently.
- At #4610's own root t₀ = 1 − κ, Λ(t₀) = Λ*(bar = κ) = 23.8626369199 to 10⁻⁴⁰ [12].

**Exchange values per call at t\*** (CHECKED-EXACT, verify.py [10]; the gap to close is 0.0209332):

| move | value |
|---|---|
| merge two rank-1 climbs on one field (1+1 → 2) | 0.0041868 (5 per call clear the bar) |
| uneven split 4+4 → 3+5 (the #4610 mechanism) | 0.00075844 |

*Scope.* The threshold applies to words in the family 𝔉: the kap path controller at unit (112, 8) with the 8-job centre. It says nothing about other units, other controllers outside the kap family, or words that change H1–H3.

## 5. A30-CUT: the owned centre is moment-optimal

**Setting.** H1–H3, linear contents over any field, U uses of the centre. Each use must deliver a vector whose p-part is c_u·p_u. Write g(x) = x^t and y = g(8)/8.

**Hypotheses.**
- **P-ATOM (contact restriction).** Carriers acquire p-content only by reading the port, and no new L–L contacts are added. Relative to the frozen L word, p_u is then an atomic item independent of all other carrier content. This is a modelling step; in real coordinates it needs the lemma that with no L–L contacts every carrier's content lies in span(its own native input, port reads received).
- **DELIV.** Every add that changes an L register's p-coefficient happens at frame 0. In the variant ψ there is one port frame P and the adds happen at frames F with F ∩ P = 0.
- **Mains are net-up.** True for #4610 (starts are lines in P and finals are pinned at dimension 8). Without it the dual fails: a credited 8 → 0 field that need not end holding its own input gives −7.95.

**Theorem (A30-CUT).** Σ_fields [Σ_jobs g(c_j) − g(credit_f)] ≥ U·g(8) + Σ_f slack_f with every slack_f ≥ 0. Fields with no centre traffic keep slack_f = Λ_f. The number of owned, helper, main and target registers, dirty contents, inverse credit, sharing across uses and order are arbitrary.

*Proof.* Take φ = dim (or ψ = dim(· ∩ P)); both are integer-valued and 1-Lipschitz for rank.

1. **(i) Cut lemma (PROVED-PAPER, CONDITIONAL on P-ATOM and DELIV).** For a level λ ∈ {1..8} let N_λ = span{r_j : φ(S_j) < λ}. By induction over events, every content held below λ lies in N_λ plus the vectors moved by transports that crossed λ downward. At the end, below λ sit the U delivered vectors and the r_j of every helper with φ(S_j) ≥ λ > φ(T_j); by P-ATOM these are independent modulo N_λ. Each crossing transport moves one field's content, so downward crossings at λ number at least U + (net-down helpers at λ).
2. **(ii) Per-level telescoping (PROVED-LEAN).** On each field, up(λ) − down(λ) = [λ ≤ final] − [λ ≤ start]. `FieldPath.up_sub_dn`. Summing (i) over fields and levels gives Σ_f cov_f ≥ 8U, where cov_f = Σ_{λ=1..8} min(up, down) (owned fields: down).
3. **(iii) Rank pays for crossings (PROVED-LEAN).** A job crosses at most min(c_j, 8) of the levels 1..8. `levels_crossed_le`, `crossings_le_mass`.
4. **(iv) Dual feasibility of y (PROVED-LEAN for each case given Σ c_j ≥ R + 2k; that mass bound is PROVED-PAPER; k ≥ 2 case for t ∈ [0.99, 1]).** We need loss_f ≥ y·cov_f on every field.
   - Owned fields: g(a) ≥ y·min(a, 8) by Lemma 2 (`owned_dual`).
   - Credited fields with cov = 0: loss = Λ_f ≥ 0.
   - Credited fields with k = cov ≥ 1: levels 1..8 give Σ c_j ≥ R − 1 + 2k and parity makes it Σ c_j ≥ R + 2k (`rankCost_parity` per step; the summation of parity along the path is PROVED-PAPER, not in Lean). For k = 1, Lemmas 1 and 3 give loss ≥ 1 > y (`credited_k1`, `y_lt_one`). For k ≥ 2, Lemma 2 with y = 9 and Bernoulli (9^{t−1} ≥ 25/27 for t ≥ 0.99) give loss ≥ y·k (`credited_k2`, `nine_rpow_sub_one_ge`).
   - The owned 8 → 0 job attains the bound, so it is tight.

At t*: y = 0.993733 and 9^{t−1} = 0.993379 [11]. ∎

**Corollaries (CONDITIONAL on the hypotheses above).**
1. No dirty, inverse-credited, catalytic or shared centre gets below g(8) = 7.9499 per use.
2. Recruiting an existing helper or main as a carrier costs slack ≥ 0.9968 (minimum at path 1 → 0 → 9; CHECKED-EXACT, source, on all dimension paths of at most 6 jobs, see below), while the largest baseline Λ_f in #4610 is 0.05959 [11]. Any gain must therefore come from fields with no centre traffic, which is Λ.

*Independent checks (CHECKED-EXACT, source).* An exhaustive Dijkstra over all subspace states of F₂ⁿ and F₃ⁿ (n = 3, 4; helpers, owned registers, inverse credit on or off, one or two uses) found no pattern below the owned centre. An independent re-derivation checked dual feasibility on all 5,978,700 dimension paths of at most 6 jobs (minimum reduced cost 0, no violations; smallest credited traffic slack 0.99682), and on real-subspace ψ models (19,558,506 and 13,017,840 paths).

**Scope not covered.** Cross-use sharing with different ports and deliveries at a common frame z; deliveries at frames meeting P; dropping P-ATOM (the decoder question); carriers that ride warps; query shears.

## 6. Centre-free (coded) family: exact budget and ceiling

Context. #4929 (Dugongue) is a centre-free producer with an explicit code A = I − 14P. #4694 and #4698 (Cinna Davis, 1337isnot1337) supply a 640-field interface, +112 cache pricing and eight chains. #4933 (dillona) is a coded p16 caller with deferred decoding. #4932 and #4931 (Clear1nsight) give a one-bank decoder ceiling and a one-port prefix offer. #4940 (SethBurkart123) proposes A⁻¹-mixed query shears. This section prices these constructions in the Λ currency. Claims about their contents are as stated in those PRs and were not re-run here.

**6.1 The coded endpoint is #4610 with the centre deleted (CHECKED-EXACT, source, on #4929's SOURCE-WORD).** Same 3290 climbs, same Λ (helpers 16.2711462249, mains 7.6034802478), same 632 start and final frames, in both orientations; the difference is 6,596 free dyadic adds.

**6.2 Exact budget (CHECKED-EXACT, verify.py [13]).** With φ_coded = φ(#4610) + 8·8^{t*}:

  B = φ_coded − φ* = **63.577975271157 per call** = 8f(8) − (Λ − Λ*), where f(8) = 8^{t*} and 8f(8) = 63.5989084680.

Over the 18 calls of the invoice, 18B = 1144.40355488. Any adapter that restores the contract endpoint must therefore cost less than 8f(8) − 0.0209332 per call.

**6.3 Per-call restoration (CONDITIONAL on A30-CUT scope).** The repair ΔY = 14PX is exactly the source's eight centre deliveries (22 Y targets per port; 24 distinct needed vectors). A30-CUT applies under its hypotheses: DELIV and mains net-up hold here (p_u is read at a port register of dimension 8, mains are net-up, deliveries are at frame 0), and P-ATOM is assumed for the adapter. Then the cost is ≥ 8f(8) = 63.5989 > B, short by exactly 0.0209331969. The deleted centre is the cheapest in-scope adapter, and coded + adapter ≤ κ(#4610).

Cheapest designs priced (CHECKED-EXACT, source): owned centre re-instated 63.5989 (margin −0.0209); hub at line 114/115 (in all ports) 63.6715; hub at a dim-2 meet 63.7072; #4694 direct cache 112; post-call up-and-down 224.

**6.4 Single-commodity lemma at any frame and time (CHECKED-EXACT, source; SUBCLASS: owned carriers, fixed #4610 main chains, no warp-riding carriers, no target-to-target relays).** If every carrier holds a multiple of one p_u and deliveries are at any frame the target occupies after p_u exists, each use costs ≥ f(8). Proof: if some target is served at frame 0, the content path from P_u to 0 has total rank ≥ 8, so cost ≥ f(8) by Lemma 1. Otherwise the 22 targets need ≥ h_u distinct nonzero arrival frames, each costing ≥ 1; exact hitting-set MILPs give h_u = 16, 16, 16, 16, 14, 18, 14, 18, all ≥ 14 > f(8). Nested stops with shedding at a common frame M ⊆ K (K the intersection of the 8 ports, dimension 5) were checked on all 31 lines of K against all 203,360 (line, hyperplane) pairs: no design gives every late target a nested stop.

**6.5 Deferred decoding (#4933).** The budget becomes whole-invoice: 18B = 1144.4036, i.e. at most 71.5252 per negative bank if the positive half is free (CHECKED-EXACT, verify.py [13]).
- (CONDITIONAL: P-ATOM, owned carriers, fixed main chains.) Decoding one stage-s factor means delivering 8 independent items. At the stage this is the per-call adapter, so ≥ 8f(8) by A30-CUT. Later or post-hoc, items of different debt classes are independent modulo N_λ, so the count adds over the **53** debt classes (class counts EXACT on #4933's `GAUGE.json`): 53·8f(8) = 3370.74.
- Any mix of at-stage and later decoding costs ≥ 18·8f(8) = 1144.78035 against 1144.40355, a shortfall of 18 × 0.0209332 = 0.376798 (CONDITIONAL: P-ATOM, owned carriers, fixed main chains). Reinstating all 144 centre calls attains it and is #4610.
- #4932's one-bank decoder needs ≥ 112 grade-2 channels per bank, 112f(2) = 223.53. Its grade-2 projection is block-diagonal over independent banks, so 16 banks cost 3576.5 against 1144.40 (scope: the single-layer decoders that #4932 treats).
- #4931's one-port prefix offer costs +0.0057610 per use with no reward in the moment.
- Past the invoice, handing codes to the parent recursion is not allowed by the current compiler (#4933's own README); that would need a typed recursive coded product.

**6.6 A⁻¹-mixed query shears (#4940).** Frame replay on #4929's canonical frames (CHECKED-EXACT, source): the 112 x-roles enter their calls at 112 distinct non-nested dimension-1 lines, so a cross-port add at the call entrance fails the verifier's scalar-source-frame rule, and each source must first leave its line by a paid rank-1 transport: ≥ 112 rank-1 jobs per thick call. Commutation (CHECKED-EXACT, F₂-symplectic, all 5,824 coupled pairs): in the physical ABI of #4933 the code C = K⁻¹AK does not commute with Q, so the needed input conversion QCQ⁻¹ is non-monomial. The sub-lemma that one boundary conversion per thick call is Q-twisted is PROVED-PAPER for conversions inside the stage-s recode group, and argued for common-frame conversions (CONDITIONAL). Priced in #4940's own invoice, break-even is about 63.6 per call and the repair costs ≥ 112, so there is no root at any p (CONDITIONAL on the Q-twist sub-lemma above); the model reproduces #4940's published 0.0030201659770. The credit for #4940 is the idea and its exact diagonalisation: with it the question reduces to the same centre budget B.

**6.7 What reopens the coded route (stated as scope, not as a claim).** Every statement in 6.3–6.6 is inside the A30-CUT and single-commodity scope. Doors outside it, shared with #4610 without any coding: network-coded carriers with stops and shedding; decoders that read X directly (breaking P-ATOM); a native word with port-independent entrance lines.

## 7. Claim index

| claim | tag | rebuilt by verify.py |
|---|---|---|
| Lemmas 1–3 | PROVED-LEAN | text check only |
| H2 for subspaces (general formula, nested, parity) | PROVED-LEAN | |
| Lemma 4, Theorem C | PROVED-LEAN | |
| Theorem B: identity, Λ_f ≥ 0, strictness | PROVED-LEAN | |
| Theorem B on #4610 (Λ = 23.8746264727, identity to 10⁻⁵⁷) | CHECKED-EXACT | yes [2]–[5] |
| Lemma 5 (nested endpoints) | PROVED-LEAN | |
| Lemma 5 (non-nested); inverse-credit remark | PROVED-PAPER | |
| Theorem D, descent price table, cap of 11 | PROVED-LEAN; numbers CHECKED-EXACT | yes [9] |
| Descent unlock bounds on #4610 (44 helpers, hub 225) | CHECKED-EXACT, scoped to fixed scalar program | no |
| Theorem A, p16 a7 invoice | PROVED-PAPER; CHECKED-EXACT | yes [1] |
| Corollary A1 (best controller in the kap family, all p) | CHECKED-EXACT (p ≤ 400) + PROVED-PAPER tail; CONDITIONAL on the family | yes [7], [7b] |
| Ship threshold Λ\* = 23.8536932758, gap 0.0209331969 | PROVED-PAPER (necessity); CHECKED-EXACT numbers | yes [6] |
| Sufficiency of Λ ≤ Λ\* | CONDITIONAL on S1 | no |
| A30-CUT (ii), (iii), (iv) | PROVED-LEAN; in (iv) the parity summation Σ c_j ≥ R + 2k is PROVED-PAPER | |
| A30-CUT (i) cut lemma | PROVED-PAPER, CONDITIONAL on P-ATOM, DELIV, mains net-up | |
| A30-CUT exhaustive and independent dual checks | CHECKED-EXACT | no |
| Coded budget B = 63.577975271157, 18B, 71.5252, shortfall | CHECKED-EXACT | yes [13] |
| Coded endpoint equals #4610 minus centre | CHECKED-EXACT | no (needs #4929 data) |
| Per-call and deferred kills (6.3–6.5) | CONDITIONAL on A30-CUT scope (P-ATOM, DELIV, mains net-up) and, for 6.4–6.5, owned carriers and fixed main chains; counts CHECKED-EXACT | no |
| #4940 no-root conclusion (6.6) | CONDITIONAL on the Q-twist sub-lemma | no |
| #4940 frame and commutation witnesses | CHECKED-EXACT | no (needs #4940 data) |

## 8. Lean build

`lean/Skel.lean` imports only Mathlib. It builds with the shipped `lean/lakefile.toml` and `lean/lake-manifest.json` (Lean `v4.33.0-rc1`, pinned Mathlib): `cd lean && lake exe cache get && LEAN_NUM_THREADS=4 lake build Skel`, with "Build completed successfully". `#print axioms` on the headline theorems gives only `propext`, `Classical.choice`, `Quot.sound`. Not formalised: the cut lemma (i), the identification of verifier events with `FieldPath`s (that is H1–H3, checked on #4610 by `verify.py`), the invoice structure, S1, and the real-number constants at t*.
