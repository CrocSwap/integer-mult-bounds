# Proofs

Tags as in the README: **[P]** proved here; **[C]** exact computation re-run by a checker in this package;
**[C-lane]** exact computation by our lane code, reported with its number, not re-run in CI;
**[C-param]** priced by our invoice tool (control: it reproduces #7546's κ .003648411294790 and S = 1424);
**[S]** judgement. A statement tagged [P] uses only what its proof says plus the cited earlier lemmas.

Common setting (the P104 relay family, as in #7555 and #7557):

- Registers hold rational linear combinations of input **tokens**. A public register starts at its own token; an owned
  register starts at 0 (INIT) and ends cleared. Frames are F2-subspaces of F2^9. ADD/COPY need both operands at the
  same frame; public MOVEs strictly ascend; owned MOVEs are nested and are the only paid owned events ("moved rows").
- **Ports.** Port t has an odd label q_t ∈ F2^9 (q_t·q_t = 1). x_t and y_t are its two inputs. Cell (t, s) is **odd**
  when q_t·q_s = 1, **even** otherwise. On P104 the Gram G of the 104 lines has G² = 26G; a cell is odd iff G_ts is
  even (diagonal 2, off-diagonal 0), and even iff G_ts = ±1 [C e8laws.py].
- **Contracts.** The per-port t = −1 contract is X = x − y, Y = x; #7546 runs t = 0. A **grading** σ_p flips the
  sign of the phase variable q of port p; for a matrix N of Laurent entries, R(N) = σ(N)N⁻¹ and o(N) = rank(R − I).

---

## 1. The odd unit, per grading

**Theorem I1 (o = rank of the odd part, any size) [P, C odd_unit.py].** For any invertible n×n N over a ring where σ is
an automorphism and 2 is invertible, o(N) = rank Odd(N), Odd(N) = (N − σN)/2.

*Proof.* R − I = (σN − N)N⁻¹ = −2·Odd(N)·N⁻¹, and N⁻¹ is invertible. ∎

The identity is blind to block size, ring and coupling: bigger blocks, ring extensions and coupled port blocks have
the same bill as their odd parts.

**Theorem I2 (Cayley form of the park) [P, C].** Write N = E + O with E σ-even and O σ-odd. Then
R = (E − O)(E + O)⁻¹ and ker(R + I) ≅ ker E. So R has eigenvalue −1 exactly when the σ-even part is singular.

*Proof.* R + I = ((E − O) + (E + O))N⁻¹ = 2E·N⁻¹. ∎

**Corollary I3 (per port) [P, C].** For N = [[c, aq], [b/q, d]] with a, b, c, d σ-fixed and Δ = cd − ab ≠ 0:
R = Δ⁻¹[[cd + ab, −2acq], [−2bd/q, cd + ab]], det R = 1, tr R = 2(cd + ab)/Δ, det(R + I) = −4cd/(ab − cd).
A root stage with pairing t needs tr R = 2 + 4t, so the native's **effective t is t_eff = ab/(cd − ab)**, and
**t_eff = −1 ⇔ cd = 0**: X holds no x or Y holds no y. That is the park.

**Lemma I4 (dressing) [P, C].** For σ-fixed A, B, R(ANB) = A·R(N)·A⁻¹. Free (σ-fixed) caller operations cannot change
tr R, hence cannot change t_eff. *Proof.* σ(ANB) = A σ(N) B. ∎ A q-odd dressing does change tr R (control, 165/200).

**Proposition I5 (the ledger is per grading) [P, C].**
1. The 104 gradings σ_p are distinct (no two ports have parallel gates; quoted from our GAUGECYCLE lane), and a q-free
   coupling P⁻¹TP of the per-port targets leaves each port's σ_a-multiplicity at m_a = 2 [C I6].
2. A unit shared by two ports would have to be odd in both gradings. The monomial q_a q_b is (o_a = o_b = 1), but it is
   two directional kernels, so two child calls (05-layers.tex, "exact recursive contract": one child per residual
   dimension). The isotropic kernel a + b·q_a²q_b², the combination that would let Y's end frame contain X's birth
   frame, is **even in both gradings** (o_a = o_b = 0) [C I5].
3. A coupled block can make E_a singular while E_0 = I (singular pencil E_a = [[1, q_b], [q_b⁻¹, 1]]), but its
   q_b-odd entries are o_b = 2 junk in ledger b [C I4]. The park moves ledgers; it does not disappear.
4. Two ports cannot share one grading inside a word: 05-layers.tex l.4–7 fixes one array with complete address set,
   and eq. (phase-conjugation), l.86–91, makes P_M a permutation of the whole array for any M ∈ GL(m, F2). There is
   no per-port relabel inside a word without a frame event.

**Theorem I6 (the 56 decoder rows are the odd unit) [P].** On every plane, every odd cell and every diagonal cell
must be served in both directions: y_s → X_t (UP: gather at f ⊆ q_s^⊥, deposit at f ∋ q_t) and x_s → Y_t (DOWN:
gather at f ∋ q_s, deposit at f ⊆ q_t^⊥). The diagonal alone forces both, since q_t ∉ q_t^⊥ (q_t·q_t = 1). A
monotone chain is blind to the other direction's odd cells, and a register used in both directions pays the climb
of each (round trip). Hence C(t = −1) ≥ C_up + C_down = 2·C_min per plane.

*Proof.* A gather of s needs f ⊆ q_s^⊥ and a deposit into t needs q_t ∈ f (row model of #7583). UP chains climb from
a frame inside q_s^⊥ to one containing q_t; DOWN chains do the reverse, so a single monotone chain covers odd cells
in one direction only. ∎ #7546 already runs UP 56 + DOWN 56 across its two planes, and the park family
(an ascending 56 plus the W6805 descending 56) has the identical MOVE histogram [C-lane HANDT1], so every decoder
saving applies to t = 0 at the same rate: **the decoder cannot move t = −1 above t = 0.**

**Exact E8 structure [C e8laws.py].** G² = 26G on the 104 ports, so G/2 = 13·proj(range G). The transposed twin of
the E8 decoder is frame-legal with M_L = G/2 and WᵀU = 13·I. The full UP-then-DOWN composition of the two G/2
decoders leaves exactly −12·I on the diagonal and odd cells (0 of 5,720 odd cells nonzero): composing two decoders
is a per-port park with no owned charge, but only in the full order; a partial order breaks 1,360 cells.

**Proposition I7 (XDEC: the joint multi-call decoder has rank ≥ 8k) [P, C].** A port and its copy in another call
carry the same label, so their cell is odd (q·q = 1). An 8-set of pairwise-odd ports and its k copies form a
principal 8k × 8k block with nonzero diagonal and zero off-diagonal pattern forced by the odd cells; any decoder
restricted to it is invertible, so rank ≥ 8k. Duplicate labels also forbid rank 8: w_p is fixed up to scale by its
55 odd neighbours, so w_{p'} ∝ w_p, contradicting w_{p'}·u_{p'} = 1, w_p·u_{p'} = 0. ∎

---

## 2. The contract invariant and the b-family

**Proposition C1 [P, C odd_unit.py].** For any 2×2 contract [[a, b], [c, d]], t = bc/det and 1 + t = ad/det are
invariant under both diagonal gauges; t = −1 iff ad = 0, i.e. a zero diagonal entry ("Y has no y").

**Proposition C2 (M45 is the B-port contract) [P, C].** The merged plane M45 = [[1, −q], [1/q, 1]] satisfies
M45 = U_q + L_q − I while H = L_q·U_q; o(M45) = 2, R² = −I, M45² = 2J_q, M45⁴ = −4I, det M45 = 2, and
diag(1, ½)·M45 = HOST(−1, ½), so t_eff(M45) = −½: it is #7113's B pair on a ρ = 2 caller, and the det-2 factor is
one free SCALE. H·M45⁻¹ = [[1, 0], [1/(2q), ½]] has o = 1: turning M45 into the t = −1 native H is one q-odd op per
J, i.e. the park in caller form.

**Proposition C3 (b-family) [P for the algebra, C-lane for the words].** The merged window word reaches
X = x − y, Y = x + b·y exactly for every b ∉ {0, −1} by changing window scalars only (t = −1/(1 + b)); t = −1 is the
limit b → 0, where one window scalar (1 + b)/b has a simple pole. (Fable-assisted analysis, reproduced by our lanes:
exact on 8/8 window ports for b = 1, ½, −½, −2, 10⁻³, 10⁻⁶.)

**Proposition C4 (ρ = 1 forces the park; scoped to root callers) [P].** In the root-caller family (stages are hosted
pairs, gates σ-fixed, odd ops only at the thin units), a native is callable at a stage only if t_eff equals the stage's
t; ρ = 1 forces t = −1 at every stage (quoted root path theorem). By I4, free ops cannot move t_eff(M45) = −½, so each
of the 17 J needs ≥ 1 extra q-odd op per A port: c ≥ 1 owned-equivalent unit per A port per call against the
break-even 0.214 [C-param] — no crossing. Non-root callers are not covered.

---

## 3. No-cloning lemmas (why every t = −1 construction pays one owned unit per port)

**Rank lemma [P; toy C walls.py].** Every event (MOVE, ADD, COPY, SCALE ≠ 0, INIT, CLEAR) acts linearly on the full
state (public rows plus live owned rows, as functions of the public tokens); INIT adds a zero row and CLEAR removes
one, so rank(state) never increases. If the endpoint map is invertible, rank(state) = n_pub at all times. Hence:
(1) with no owned row live, public contents are independent and zeroing a public register is a permanent loss;
(2) a zeroed direction must sit in a live owned row until an owned → public ADD returns it;
(3) a dirty CLEAR is lossless iff its content lies in the span of the rest of the state at that moment.

*Proof.* Each event's new state rows are linear combinations of the old ones (ADD/COPY/MOVE/SCALE), or a zero row is
added (INIT), or a row is deleted (CLEAR). None raises the row-space dimension. The endpoint is invertible, so the
final rank is n_pub, which equals the initial rank; hence the rank is n_pub throughout. (3): deleting a row keeps the
rank iff the row is in the span of the others. ∎

**Lock Lemma [P].** Let V0 be the span of the tokens of registers that are ever at {0}. After a register leaves {0},
the V0-part of every content anywhere (public, unmoved owned, and decoder rows that snapshot native registers) lies in
the span of the departure contents. Only an owned row snapshotted at {0} and **moved** adds a V0 direction.

*Proof.* Operations act between registers at one shared frame; public MOVEs ascend, so no public register returns to
{0}; unmoved owned rows stay at their frame. So the only way new V0 content reaches a register above {0} is through a
register that left {0} (its departure content) or an owned row that gathered at {0} and moved. ∎

**Clone lemma [P] (Fable-assisted analysis, reproduced independently by our CLONEAUDIT lane).** With ascending public
MOVEs and invertible contents, the contents with which registers leave {0} form a basis of the {0}-born token space
(Rank lemma). After the merge, the Y main arrives at its end frame as m + u, where m is its own departure content and u
is built at X's birth frame before any Y-side content is present. Final Y = x needs m in the span of what else reaches
the Y-end frame, which the basis property excludes; an unmoved snapshot can zero m only by making the global map
singular (Rank lemma (3)). So **the park needs a clone of m, and only moved owned rows clone.**

**Theorem W (separate twins wired before/after the native) [P].** Keep the hosted twins as separate public registers
and wire them to the #7546 native only before or after it. Then either ≥ 96 moved owned rows are needed per call
(order Y = x) or the V-span deficit is ≥ 1 per A port (the other order).
*Proof sketch.* (Y = x order) pick φ ∈ V0* vanishing on all non-Y departure contents; the functional
g = Σ_s φ(c_{Y_s})·coef_{x_s} − φ(V0-part) vanishes on every register at frames ⊆ q_t^⊥ after the native, and its
support stays at frames ∋ q_t; so g(Y_t) = 0 forces φ(c_{Y_t}) = 0 for every exact Y_t, a rank deficit of ≥ 96 that
only moved {0}-rows (Lock Lemma) can fill. (Other order) X arrives at V with x-coefficient 1 and the V targets have
none, so span(V-arrivals) ⊋ span(V targets). ∎

**Lemma NT (new tokens are useless unless debited to old rows) [P].** Add public registers that no old public or
owned register ever reads. Then span(arrivals at f) ∩ old-space = span(old arrivals) at every frame f: the gain is 0.
*Proof.* Only new registers hold new tokens, so their token block stays invertible; registers strictly below f meet
only each other and only leave, so span(arrivals at f) ⊕ span(rows strictly below f) is direct, and the new
arrivals' token parts are independent. ∎

**Lemma AS / VA [P].** At a frame f where every read is corrected, the span of everything held at f is the span of
the arrival contents at f (AS). At V, everything held is in span(public arrivals at V) + span(moved owned rows at V);
with #7557's Theorem M, D ≥ rank_K(merged classes of the V arrivals) − m_moved, and a token-free y_t arriving at V
has class e_t, adding a row it cannot cancel (VA). [C-lane: rank_K{e_t : t ∈ A} = 95; #7546's live X arrivals 88.]
So an unmoved owned row changes **when** registers exchange content, never **where** they meet.

**Lift law [P].** Rows that gather only at frames ∋ q_t hold vectors in span(T_t contents), T_t = registers at
frames ∋ q_t, and that span never shrinks. A delivery of x_t into Y_t at q_t^⊥ that leaves no deficit needs a first
deposit into a T_t register with content reaching outside T_t: an **ascending owned MOVE**. Descending decoder rows
and unmoved rows cannot make it. [toy C walls.py: A3/A4, the PLN variants are top-solvable 0/216 and 0/360 (D = 1); positive controls
D = 0 with one.]

**Freeze Lemma [P].** Under no imports into q_t^⊥, the span of everything ever held at q_t^⊥ equals the span of
its arrival contents. *Proof.* Park every register on arrival at V or at any q_u^⊥ and drop all ops there; below-ops
never read parked registers, so the frozen program replays every below-op, and the parked set's span equals its
arrival span at all times. ∎ Hence time differences at q_t^⊥ (or at V, or below) deliver nothing a single-time
delivery cannot, and ≥ 1 crossing owned MOVE per served port stays necessary.

**Shared-lift theorem [P, C e8laws.py].** One crossing owned MOVE serves only a set of pairwise F2-orthogonal
ports; such labels (q·q = 1) are linearly independent, so at most 9, and the exact maximum on P104 is **8**. With m
MOVEs, no m + 1 pairwise non-orthogonal ports can all be served (the matrix f_v(κ_u) has rank ≤ m, nonzero diagonal
and zeros on non-orthogonal pairs). *Note:* this is not "≤ 8m": the E8 Gram satisfies every Y-side constraint for
all 104 ports with m = 8; that "Gram lift" was then closed by the V side (Theorem M: D ≥ 104 − m_o on E8, and an A3
exact test D ≥ 6 [C-lane GRAMLIFT]).

**Commutation Theorem [P; toy C walls.py].** Every frame-local operation acts on the field side of a register
(C_r ← Σ A_rs C_s, A_rs any linear map on the field); every lemma above is a token-side row-space or support
statement. The two commute, so all of them hold for **any** enlargement of the same-frame op set (operator or
diagonal coefficients, graded registers, half-field swaps, block maps, monomials, lazy CLEAR, time shifts). A
primitive that changes a content's label is a copy plus one transition of Fourier rank ≥ 1, i.e. ≥ P[1] per field
(the d-metric price), so ≥ 1 unit per port per call.

**XRECALL lemma [P, C].** x_b is born only at ⟨q_b⟩, gained only by same-frame ADDs, and public MOVEs ascend, so
every frame holding x_b contains ⟨q_b⟩. Y_b's end frame lies in q_b^⊥ and q_b·q_b = 1, so ⟨q_b⟩ ⊄ q_b^⊥: no frame
inside Y_b's end frame ever holds x_b publicly (0 of 96 recall sites without moved owned rows).

**Zone lemma [P; toy C walls.py].** For two non-chainable receivers r1, r2, the zone Ξ of frames inside
q_r1^⊥ ∩ q_r2^⊥ is a down-set; ops in Ξ act invertibly on the pair of process adjoints, so the source rows
{(B[r1, t], B[r2, t])} entering Ξ must not be one line with both coordinates nonzero. One sender gives rank 1 and
is impossible however many helpers relay; two independent senders escape (A4 toy exact with 0 owned).

**Owned additivity (PARALLEL) [P].** Owned cost is paid per moved row and one row carries one vector. Departure
contents of different instances, siblings or calls are independent tokens, and the Clone lemma's basis holds for
their union, so the delivered rank needed is the **sum** over instances: M(A + B) ≥ M(A) + M(B). A coded row
m_A + m_B needs m_B as side information at A's Y end, and only B's own Y main holds it (Rank lemma). So c ≥ 96/104
= 0.92 owned units per port per call under any sharing, against the break-even 0.214 [C-param].

**Wiring lemma (FUSET1) [P].** Twins kept as public helpers with tokens a, b and wired only before/after the native:
Y's final row restricted to (y, b) is u·E2 with E2 invertible, so Y cannot lose y; with a free owned park at {0},
b and y move together and every vector in span{X, X2, Y2} at V has equal b and y coefficients. One extra
independent vector per A port is needed at V.

**Cut Lemma (WEBS; outside-session lane, DreamingOfClouds') [P, C cuts.py].** Model: public registers with their own
token, ascending moves, ADD/COPY only at a shared frame; any number of helpers with any chains, tokens cancelled
anywhere, each ending at its own token; owned registers token-free, INIT empty, free while unmoved, dirty CLEAR
free, a MOVE a → b costs |dim b − dim a|; time is real time. Let 𝒢 be an up-set of frames, Π the public vectors
entering 𝒢 (tokens of registers born in 𝒢 and public contents at moves from outside into 𝒢), O the owned contents at
moves from outside into 𝒢, and F the finals of public registers ending in 𝒢. Then F ⊆ span(Π + O) and |Π| = dim F,
hence **rank(O mod Π) ≥ def(𝒢) := dim(F + Π) − dim F.**
*Proof.* By induction over the real event order, every content ever held at a frame of 𝒢 (public, owned, or owned
snapshot) lies in span(Π + O): public registers never leave 𝒢, and owned registers are INIT'd empty in 𝒢, carried
their content across the cut (O), or read it inside 𝒢. Each public register ending in 𝒢 contributed exactly one Π
vector (born in 𝒢 or crossed once), and the finals are independent because the word is exact. So
dim span(Π + O) ≥ dim(F + Π) and dim Π ≤ |Π| = dim F. ∎ Nothing about helpers is used: webs, token cancellation,
snapshots and zeroing are inside the induction.
Corollaries [P]: **C1** at t = −1, def(𝒢_s) ≥ 1 for 𝒢_s = {frames ∋ q_s} (x_s is born in 𝒢_s and is in F only
through Y_s's final, which ends in q_s^⊥ ∌ q_s), so some owned MOVE enters 𝒢_s; refining 𝒢_s by the up-sets of
owned ascents whose source is not inside q_s^⊥ shows that some owned ascent leaves q_s^⊥ upward. **C2** if every
owned move except line feeders {0} → ⟨q_t⟩ descends, only s's feeder crosses into 𝒢_s, so M ≥ 104 (S ≤ 712
[C-param]) for any web and schedule. **C3** with no owned crossing into {≥ f}, every content at f lies in
span{x − y, x_r with f ⊆ q_r^⊥, tokens of helpers ending above f}, so X_s is U-complete there. **C4** with line
feeders F, unfed ports R and extra ascents E on a descending decoder, any pairwise-odd I ⊆ R gives an up-set with
def ≥ |I| that a line feeder enters only through an E-move starting on its line, so |E| ≥ |I| and
M ≥ |F| + α(R); α(P104) = 8 [C]. *Not proved:* that ascents cannot be shared between ports (cuts alone allow
climb 3 for n = 4 on F2³); the conjecture M ≥ n is [S].

**UFLOOR duality is type-preserving [P].** The dual of a U job (transfer [[I, Z], [0, I]], X ← y) has transfer
the transpose, whose receivers have X geometry: U ↦ U, L ↦ L; a MOVE A → B dualises to B^⊥ → A^⊥, so ascents stay
ascents. (This corrects internal notes that dualised U builds into L builds; none of those claims is in a public PR.)

---

## 4. Decoder-wall pieces since #7583

Model and notation as in #7583 (row model; certificates Z on odd cells and the diagonal with nonzero diagonal).

**Lemma A(acyc) [P].** Let M = Σ_k w_k u_kᵀ and T a port set with M_pp ≠ 0 on T and the nonzero odd off-diagonal
cells of M on T × T forming an **acyclic** digraph. Then every valid certificate Z has
|T| ≤ Σ_k rank Z[D_k ∩ T, S_k ∩ T]. *Proof.* In a topological order (Z∘M)[T, T] is triangular with diagonal
Z_pp·M_pp ≠ 0; Hadamard linearity and rank subadditivity give the bound. ∎ So rank certificates cannot tell an exact
decoder from one with arbitrary "upper" junk: proving C ≥ 52 on P104 this way requires that no acyclic decoder of
cost ≤ 51 exists.

**Lemma B (mod-4 certificates, half-integer decoders) [P].** For rows with w 2-adically integral and 2u integral, and
any integer Z with odd diagonal and zero on even cells: n ≤ Σ_k s2(Z[D_k, S_k]), s2 = number of 2-adic invariant
factors of valuation ≤ 1. *Proof.* 2Δ = Σ diag(w) Z_k diag(2u); Smith-lift Z_k mod 4; the result is 2(Δ − 2X),
which is nonsingular. ∎ s2 is monotone under row and column deletion, so closures and mixtures go through.
[C-lane: sampled-closure LP with s2 gives λ ≥ 2.768 on 2,509 closures, against the 2.039 needed for C ≥ 52.]

**Proposition H (HALF18 correction) [C e8laws.py].** The minimum rank of a full-flag certificate is far below the
"≈ 18 = 2h" stated in the HALFWALL notes behind #7583: on the 120 E8 lines a certificate of rank **15** exists
(15 pairwise-orthogonal 8-frames, Z = sum of the frame block-J's), and on the 104 P104 ports one of rank **13**
(13 frames); a pairwise-even 8-set gives the exact lower bound 8 (a diagonal block of Z), so the P104 minimum lies
in [8, 13]. The full flag therefore has slack; the binding constraints are on intermediate flags (sampled-flag LP
λ ≥ 2.62 [C-lane] against < 2.039 needed), so C ≥ 52 stays unproved.

**Proposition E (early-set cap, EARLYCAP part A) [P].** Partition the 4,992 partner cells into early E and late F.
With C_all = G − 2I and GK = 0 (K = ker G), C_E K = −(2I + C_F)K. Put N = 2I + C_F (diagonal 2, ±1 on F); then the
contamination rank is d = rank(NK), so rank N ≤ d + 8, and rank N ≥ tr(N)²/‖N‖_F² = 208²/(416 + |F|). With
|F| = 4,992 − |E|: **|E| ≤ 5,408 − 43,264/(d + 8)**, i.e. ≤ 540.8 cells per contamination rank at d = 2 and
decreasing, below the 577 needed to tie the park family [C-param]. d = 0 forces E = ∅ (TMLEVER). The d = 1 window
577–600 is open.

**Proposition T (T1CANCEL refutes EARLYCAP part B) [C-lane, P for the identification].** A diagonal canceller −x_t
added into the σ relay after the restore does make each merged class lie in range G (D = 0 in exact A3/A4/D4
simulations and res = 0 mod p on E8). But the canceller reads Y_t's final at V: it is the owned L row copied into
the σ relay, and the free input is the zero-Y park P_t, so every "early" cell is a post-park cell and the design is
the park family plus 104 useless ADDs (0.8681× at the built U layer, 1.3093× at the LP floor [C-param]).

---

## 5. Local re-solve on a fixed schedule

Setting (NETCOMPILE frame window): wires 1..n, gates E = I + q·e_A e_Bᵀ or SCALE, product C = E_N ⋯ E_1. A gate at
frame F, time t is legal iff both wires are at F at time t. Dropping one interior stay removes its gates (circuit G2,
product C2); D := C2⁻¹T, P_t := product of G2 gates before t, N_t := P_t(D − I)P_t⁻¹.

**Theorem F (the "one-rank law" is the Fredholm alternative) [P, C onerank.py].** A repair decided by comparing
rank A with rank [A | b] for one column b always has rank [A | b] − rank A ∈ {0, 1}. Every engine we used to test
drops (NETCOMPILE, SEEDBUILD, TOKDEBT, OWNRETIME) has one right-hand side, so the reported "every drop misses by
exactly one rank" (161/161, 162/162, 168 cases) means only "infeasible". **Correction:** our earlier
"contact-minimality conjecture" read structure into this count; it carries none.

**Lemma LIN [P].** Insert corrections a_i += k_i·b_i at positions p_i into G2. If no source slot (b_j, p_j) is
reachable in G2's dependency DAG from a target slot (a_i, p_i) with p_i ≤ p_j, then
final = C2 + Σ k_i·S_{p_i}[:, a_i] ⊗ R_{p_i}[b_i, :] exactly. A relay through a drop-dirty wire is linear; only
wires already made dirty by a correction give bilinear terms.

**Lemma TR (one-block re-solve) [P].** Replacing every gate at F during a maximal interval (t, F, Π) by some
X ∈ GL(Π) realises T iff N_t is supported on Π × Π. *Proof.* Gates elsewhere commute with X; C2 = S·X_o·P_t and
T = C2·D give X = X_o(I + N_t), which lies in GL(Π) iff I + N_t does. ∎

**Lemma 2B (two blocks) [P].** For time-disjoint intervals I1 < I2 with M = P2·P1⁻¹ and g = B1⁻¹ = I + E·Y·Eᵀ,
blocks exist iff N2 + (I + N2)·M[:, Π1]·Y·M⁻¹[Π1, :] = 0 off Π2 × Π2 (linear in Y) and det(I + Y) ≠ 0; then
B2 = (I + N2)·M·g·M⁻¹ is forced.

**Descent Lemma [P, C onerank.py].** For any repair family decided by one linear system with one right-hand side,
greedy single drops terminate at a configuration where every single drop is infeasible, and by Theorem F every stay
then "misses by one". So the law holds at every local minimum and gives no lower bound: in the toy W·W⁻¹ (target I,
optimum 0 stays) descent can stop at 4 rigid stays, and m disjoint copies give 4m against 0.

**Lemma RT (BREAKER8) [P, C words.py].** A main's route costs exactly what a helper doing the same route costs:
swapping the route onto a new helper plus one main jump leaves κ unchanged. So "mains are fixed" carries no price.
