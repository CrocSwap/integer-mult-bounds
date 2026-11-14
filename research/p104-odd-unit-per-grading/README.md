# P104: the odd unit, paid per grading (no κ)

This package collects one day of P104 research (Nov 14) on two questions:

- **The decoder wall.** Can the 56 owned decoder units per plane be reduced?
- **The t = −1 park.** Can a one-plane t = −1 native (X = x − y, Y = x) beat #7546's t = 0 word?

It has three parts:

- **Part I.** The lemmas and theorems we proved.
- **Part II.** Every route we closed, each as a scoped negative result with the reason it fails.
- **Part III.** The words we built that did not pay, with exact replays.

It makes **no κ claim** and ships no new frontier word. The base word is ToikY's #7546 (κ 0.003648411294790).
At the time of writing the frontier is aliromman's #7605 (κ 0.0036504442446), stacked on #7604 (FanPUYen),
#7603 (SYLforge) and our #7601. None of the results below depends on those edits.

**One cost behind both walls.** The bill for t = −1 and the bill for the decoder are the same object: the **odd
unit**, paid separately in each port's own grading σ_p.

- o(N) = rank of N's σ-odd part, for any block, any ring and any port coupling (I1).
- t = −1 holds exactly when the σ-even part is singular (I2, the Cayley form of the park).
- No contract can share that unit between ports. Two ports never share a grading inside a word, and the isotropic
  combination q_a + q_b is even in both gradings (I5).
- On the decoder side, the odd diagonal (q·q = 1) forces both an UP and a DOWN decoder in every plane. The 56 owned
  rows are the price of that diagonal (I6).
- Every construction that tries to move the park elsewhere meets one fact. Content is never cloned without a
  **moved owned row** (the Rank, Lock and Clone lemmas, Theorem W, NT, AS/VA, the lift law, Freeze, the Cut
  Lemma, Commutation). That costs about 1 owned unit per port per call, against a break-even of 0.214.

Tags:

- **[P]** proved in [PROOF.md](PROOF.md).
- **[C]** exact computation, re-run by a checker in this package.
- **[C-lane]** exact computation by our lane code. Its number is reported, but CI does not re-run it.
- **[C-param]** priced by our invoice tool. Its control reproduces #7546's κ 0.003648411294790 and S = 1424.
- **[S]** judgement.
- **[open]** open question.

Nothing tagged [S] or [open] is claimed as a result.

A network-compiler effort (recompiling the helper layer from requirements) is ongoing. **Nothing from it is
claimed here.**

## How to verify

```
python3 -I -B research/p104-odd-unit-per-grading/odd_unit.py   # Part I.1–I.2 contract identities      PASS_ODD_UNIT_PER_GRADING
python3 -I -B research/p104-odd-unit-per-grading/e8laws.py     # E8/P104 exact structure              PASS_E8_LAWS
python3 -I -B research/p104-odd-unit-per-grading/walls.py      # register-machine toys for the walls   PASS_WALL_TOYS
python3 -I -B research/p104-odd-unit-per-grading/onerank.py    # Theorem F, descent toy               PASS_ONERANK
python3 -I -B research/p104-odd-unit-per-grading/cuts.py       # Cut Lemma on two real words          PASS_CUT_LEMMA
python3 -I -B research/p104-odd-unit-per-grading/words.py      # Part III exact replays               PASS_UNPAID_WORDS
python3 scripts/research_package.py --package research/p104-odd-unit-per-grading
```

- All checkers use the standard library only and run in minutes.
- [VERIFY.json](VERIFY.json) lists what each one checks, including its positive and negative controls.

---

## Part I. Theorems and lemmas

### I.1 The odd unit, per grading (`odd_unit.py`)

| # | statement | tag |
|---|---|---|
| I1 | o(N) = rank(σN·N⁻¹ − I) = rank Odd(N), for any size, ring or coupling (40/40 random coupled 2–4×4, both gradings) | [P, C] |
| I2 | Cayley form: ker(R + I) ≅ ker E. So t = −1 ⇔ the σ-even part E is singular (40/40, 17 of them with singular E) | [P, C] |
| I3 | Per port, N = [[c, aq], [b/q, d]]: det(R + I) = −4cd/(ab − cd) and t_eff = ab/(cd − ab). So t_eff = −1 ⇔ cd = 0 (the park) | [P, C] |
| I4 | Dressing: R(ANB) = A·R(N)·A⁻¹ for σ-fixed A, B. Free caller ops cannot change t_eff. Control: a q-odd dressing changes tr R on 165/200 | [P, C] |
| I5 | The ledger is per grading. A q-free coupling keeps m_a = 2. A singular pencil moves the park into ledger b as o_b = 2 junk. The isotropic kernel a + b·q_a²q_b² is even in both gradings, while q_a·q_b is odd in both but is two child calls. 05-layers.tex l.4–7 and l.86–91 allow no per-port relabel inside a word | [P, C] |
| I6 | t = −1 needs UP and DOWN decoders in each plane, because the diagonal is odd: C(t = −1) ≥ 2·C_min. #7546 already runs UP 56 + DOWN 56 across its two planes, so every decoder saving also applies at t = 0 | [P; C-lane histograms] |
| I7 | A joint decoder over k calls has rank ≥ 8k: a port and its copy form an odd cell | [P, C] |

**Exact E8 structure** (`e8laws.py`) [C]:

- G² = 26G, so G/2 = 13·proj(range G).
- The transposed-twin decoder is frame-legal, with M_L = G/2 and WᵀU = 13·I.
- Composing the full UP decoder with the full DOWN decoder leaves exactly **−12·I** on the diagonal and odd cells
  (0 of 5,720 odd cells nonzero). In the full order the composition is a per-port park with no owned charge. A
  partial order breaks 1,360 cells.
- One shared crossing serves at most **8** pairwise-orthogonal ports, and the maximum pairwise-odd set α(P104) is 8.

### I.2 The contract invariant (`odd_unit.py`)

- **C1 [P, C].** For a 2×2 contract, t = bc/det and 1 + t = ad/det are invariant under both diagonal gauges.
  t = −1 exactly when a diagonal entry is zero.
- **C2 [P, C].** M45 = [[1, −q], [1/q, 1]] is the B-port contract.
  - The factorisation is M45 = U_q + L_q − I, while H = L_q·U_q.
  - Its invariants are o = 2, R² = −I and det = 2.
  - diag(1, ½)·M45 = HOST(−1, ½), so t = −½ on a ρ = 2 caller. The factor 2 costs one free SCALE.
  - H·M45⁻¹ has o = 1: turning M45 into t = −1 costs the park, as a caller op.
- **C3 (b-family) [P algebra, C-lane words].** The merged window word reaches X = x − y, Y = x + b·y exactly for
  every b ∉ {0, −1}, using window scalars only (t = −1/(1 + b)). t = −1 is the limit b → 0, where one scalar
  (1 + b)/b has a simple pole. This is Fable-assisted analysis, reproduced by our lanes.
- **C4 [P, root callers].** ρ = 1 forces t = −1 at every stage. M45 therefore needs ≥ 1 q-odd op per A port per
  call, i.e. c ≥ 1 against the break-even 0.214 [C-param]. Non-root callers are not covered.

### I.3 No-cloning lemmas (`walls.py`, `cuts.py`)

| lemma | content | tag |
|---|---|---|
| Rank lemma | No event raises the full-state rank (public + live owned rows). An invertible endpoint therefore keeps the rank at n_pub throughout. A dirty CLEAR is lossless iff its content is in the span of the rest | [P, C toy] |
| Lock Lemma | After leaving {0}, every content's {0}-part lies in the span of the departure contents. Only a moved owned row snapshotted at {0} adds a direction | [P] |
| Clone lemma | The park needs a clone of the Y main's own departure content m, and only moved owned rows clone. Fable-assisted analysis, which our CLONEAUDIT lane reproduced and strengthened to the premise-free Rank lemma | [P, C toy] |
| Theorem W | Separate twins wired before/after the native need ≥ 96 moved owned rows (Y = x order), or leave a deficit ≥ 1 per A port (other order) | [P, C toy] |
| Lemma NT | New public carriers that old rows never read add 0 usable rank at every frame | [P] |
| Lemma AS / VA | At a corrected frame, everything held is in the span of the arrivals. Unmoved owned rows change *when* registers exchange, never *where* they meet | [P] |
| Lift law | An exact top delivery of x_t needs an **ascending** owned MOVE. Descending decoder rows and unmoved rows cannot make it | [P, C toy] |
| Freeze Lemma | Under no imports, the span at q_t^⊥ equals its arrival span, so time differences deliver nothing | [P] |
| Shared-lift theorem | One crossing MOVE serves only pairwise-orthogonal ports (≤ 8 on P104). m MOVEs cannot serve m + 1 pairwise non-orthogonal ports | [P, C] |
| Commutation Theorem | Same-frame ops act on the field side, and all walls above are token-side. Every wall therefore holds for any enlarged same-frame op set, and label-changing primitives cost ≥ 1 unit per port per call | [P, C toy] |
| XRECALL lemma | Every frame holding x_b contains ⟨q_b⟩, and ⟨q_b⟩ ⊄ q_b^⊥ because q·q = 1 | [P, C] |
| Zone lemma | Two non-chainable receivers cannot be served from a single sender's rank-1 rows, however many helpers relay | [P, C toy] |
| Owned additivity | Owned delivered rank adds across instances, siblings and calls: c ≥ 0.92 per port per call under any sharing | [P] |
| Wiring lemma | Separately wired twins need one extra independent vector per A port at V | [P] |
| **Cut Lemma** (WEBS) | For any up-set G of frames: rank(O mod Π) ≥ def(G) = dim(F + Π) − dim F, for **any helper web**. Here Π is the public vectors entering G, O the owned contents crossing into G, and F the finals in G | [P, C] |

**Cut Lemma validation [C `cuts.py`].**

- **W6805 (t = 0).** This is CubeJerry's #6805 word: def(G_s) = 0 on 104/104 ports, 0 owned crossings, and the
  lemma holds on 104/104.
- **feeder6805 (t = −1, exact).** def = 1 on 104/104, exactly one owned crossing (its feeder) into each G_s, and
  the lemma holds on 104/104.

**Cut Lemma corollaries [P].**

- **C1.** Every t = −1 port needs an owned ascent that leaves its Y-end hyperplane upward.
- **C2.** If all owned rows descend apart from line feeders {0} → ⟨q_t⟩, then M ≥ 104 and S ≤ 712, for any web and
  any schedule.
- **C3 (dual law).** With no owned crossing into {≥ f}, X_s is U-complete at f.
- **C4.** M ≥ |F| + α(R), where F is the set of line feeders, R the unfed ports and α the maximum pairwise-odd
  subset; α(P104) = 8.

**Status of the WEBS sharing question.**

- **Not proved.** Whether one owned ascent can be shared between ports is open. The conjecture M ≥ n at t = −1 is
  [S].
- **What the cuts allow.** Up-set cuts alone allow climb 3 for n = 4 on F2³ (13 sets).
- **What the search found.** None of those sets was realised in the numeric search, while its controls were exact
  [N].
- **In progress.** A lane (TOY4) is deciding the F2³ case exactly. Nothing from it is claimed here.

### I.4 Decoder-wall pieces since #7583

| statement | tag |
|---|---|
| **Lemma A(acyc).** If a decoder's nonzero odd cells on T form an acyclic digraph, every rank certificate gives \|T\| ≤ Σ rank Z[D_k ∩ T, S_k ∩ T]. Certificates are therefore blind to "upper" junk, and C ≥ 52 by certificates needs "no acyclic decoder ≤ 51" | [P] |
| **Lemma B (mod-4 certificates).** For half-integer rows, n ≤ Σ s2(Z[D_k, S_k]) for any integer Z with odd diagonal. The sampled-closure LP gives λ ≥ 2.768, against the 2.039 needed | [P; C-lane] |
| **HALF18 (correction, see below).** Exact certificates of rank **15** on the 120 E8 lines (15 orthogonal 8-frames) and **13** on the 104 P104 ports. The full flag has slack, and intermediate flags bind (sampled LP λ ≥ 2.62) | [C] |
| **Early-set cap (EARLYCAP A).** \|E\| ≤ 5,408 − 43,264/(d + 8). That is ≤ 540.8 cells per contamination rank at d = 2, below the 577 needed. d = 1 (577–600) is open | [P, C arithmetic] |
| **UFLOOR duality.** Duality preserves job type (U ↦ U, L ↦ L, ascents ↦ ascents). The crossing U* = 7,126.97 D0/call is where the park family ties #7546 | [P; C-param] |
| **ACYCDEC.** Cleaning acyclic junk with extra rows turns decoder + cleaner into an exact decoder, so the saving is never positive. Small frames and subsets of 6–14 ports cost exactly n both ways | [P scoped; C-lane] |
| **Pure E8-world rows cost ≥ 56** even when acyclic (frame-partition Z of rank 13 + #7583's rigidity) | [P] |

### I.5 Local re-solve on a fixed schedule (`onerank.py`)

| statement | tag |
|---|---|
| **Theorem F.** With one right-hand side, rank[A \| b] − rank A ∈ {0, 1}. So "every drop misses by exactly one rank" means only "infeasible" (**correction**, see below) | [P, C] |
| **Lemma LIN.** Corrections through drop-dirty wires are exactly linear | [P] |
| **Lemma TR.** A one-block re-solve on interval (t, F, Π) works iff N_t is supported on Π × Π | [P] |
| **Lemma 2B.** A two-block re-solve is linear after eliminating one block, plus an invertibility condition | [P] |
| **Descent Lemma.** The law holds at every local minimum and gives no lower bound. Toy: 4 rigid stays against an optimum of 0, unbounded with copies | [P, C] |
| **Rigidity is schedule-driven.** Random coefficients on the same schedule repair 0/161 drops | [C-lane] |
| **Lemma RT.** A main's route costs exactly what a helper doing it costs (κ identical), so "mains fixed" carries no price | [P, C words.py] |

---

## Part II. Negative results by route

Each row gives what was tried, its exact scope, the reason it fails and the numbers.

- "Built" prices use the measured U layer of today's words, 10,730 D0/call.
- Break-even for one-plane t = −1 is c* = 0.214 owned units per A port per call, or 0.075 for the all-B
  variant [C-param].

### II.1 t = −1 native constructions

| route | scope | why it fails | numbers | tag |
|---|---|---|---|---|
| YCHAN: twin y-channel | twins separate, wired before/after #7546's native, any helpers, free unmoved owned rows | Theorem W (token lock) | 1 moved owned row/A port → S = −112, no crossing. A free channel would give 1.1810× | [P, C toy, C-param] |
| FUSET1: fuse U and L jobs in one plane | twin identification preserving per-register op order/frames | Y side: 0/96 ports admit U reads below a zero-change park point. X side: 0/96 admit L/U order. Wiring lemma | ceiling 1.1810× needs a token-free y-channel ≤ 39 D0/A port | [P, C-lane] |
| BYPASS: merged twins + time-difference corrections | corrections from frame memory at each read | Lemma AS: a read is correctable iff its state is in the span of the arrivals. Full merge 1,806/2,260 uncorrectable (96/96 ports). Controls: unmerged #7546 2,260/2,260 pass | it would price 1.3014× if it worked | [P, C-lane] |
| MERGEBUILD: inserted-stop carriers | carriers that leave #7546's contents fixed | 931/933 missing directions not coverable. Lemma NT: new carriers add 0 | floor 933 dirs = 1,293 D0/call (< 5,652 slack), but no carrier class | [P, C-lane] |
| INNERWIRE / TOPL / TOPL2 / TOPLBUILD: merge Y2 into live Y_t, rebuilt top-L layer | PLN rules (X unwritten until donation) | Lift law: D ≥ 1 per merged port unless an ascending owned row is used. One lift/port → S = −160 | TOPL2 estimated ≈ 8.0k D0 against an 11.0k gate before the lift law closed it | [P, C toy] |
| LIFTTD: shared or unmoved lifts | no imports into q_t^⊥ | Freeze Lemma. Shared-lift theorem (≤ 8 ports per lift). 12 one-unit MOVEs → 0.9837× | | [P, C] |
| GRAMLIFT: E8 Gram lift with 8 MOVEs | Y-side algebra exact | No frame-legal design on A3. V side: Theorem M rank Ψ = 6 → D ≥ 6 on A3, D ≥ 104 − m_o on E8 | | [P, C-lane] |
| YEND: {0}-born helper carrying y to the Y end | merged window | No register visits both X-birth and Y-end (8/8). Y = x needs a dependence inside the invertible {0} basis | D_V = 1/port | [P, C-lane] |
| XRECALL: recall x_b from other ports' registers | public moves | XRECALL lemma: 0/96 sites without moved owned rows | | [P, C] |
| COURIER (outside-session lane, Mason's): Y couriers zeroed after delivery | real P104 frames | Only isolated 2-cycles. Induced matching ≤ 4 pairs → ≤ 8 couriers, each forcing an owned ascent. 0 with W6805's rows | S ≤ 848 with a free decoder; WEBS C4: M ≥ 100, S ≤ 780 | [P, C-lane] |
| YYMIX (outside-session lane, Mason's) k = 2 staged Y–Y mixing → K2REAL with real carriers | cell model → real tokenized carriers | Carrier preloads must happen at {0}. 14 Y mains lose their preload carrier, and X_39 needs ≥ 7 owned rows | M_real ≥ 97, S ≤ 831, ≤ 0.914× (break-even M ≤ 92) | [P, C-lane, C-param] |
| YYMIX singular snapshot route (M = 0 in the cell model) | real tokens | CLONEAUDIT: the cell model's token-free carriers are 12 moved owned rows in disguise. A4 toy: snapshot CLEARs drop rank 20 → 16, and all Y wrong | artefact | [P, C toy] |
| MULTIHELP: multi-sender token-cancelling networks | 85/85 shared-sender pairs rank 2 | Zone lemma. 27 stuck antichains | M_real ≥ 91 (lower bound) against break-even 92 | [P, C-lane] |
| MULTIMIX: C = 0 range-sector fix for k = 2 | family E, W6805 L layer kept | The Y error has rank 8 and never vanishes for nonempty R. The fix needs ≥ 8 paid units | M ≥ 99 → ≤ 0.8955× | [P, C-lane] |
| WEBS: any helper web on MIX14 / COURIER / feeder designs | exact model | Cut Lemma corollaries C1, C2, C4 | W6805 family M ≥ 104 (S ≤ 712). MIX14 + any ascents M ≥ 96 (S ≤ 848). COURIER M ≥ 100 (S ≤ 780) | [P, C] |
| NEWMOVE: new primitives (priced descent, public clone, swaps, block transits, chart rotation mid-word) | linear, label-local up to rank-0 adapters | Commutation Theorem + transit floor (≥ P[1] per field) | ≥ 1 unit/port/call; global rotation is a no-op | [P, C toy] |
| BORDERCL: border/precision route (b → 0) | the repository's specification | The spec requires exact local maps. Its only approximation clause is analytic (06-transforms.tex l.214–224: error < √2·ℓ·2^−p, cost linear in p). Pole order 1 gives λ ≥ 2 on bad slots | cannot cost < 2,660 D0/call | [P from quoted text] |

### II.2 Decoder (owned 56 per plane)

| route | why it fails | tag |
|---|---|---|
| HANDT1: hand-built t = −1 decoder | UP + DOWN forced (I6). Late-L gathers at V cost +8/call (0.7933× built). The twin is the park family | [P, C] |
| DECZERO (outside-session lane, Mason's): zeroing / frame memory / mixing | Each alone is a relabel of the decoder. Zeroing + memory "free lifts" are new freedom (rank 2 per owned register) but cost ≥ 56 for rank-8 networks. Rank ≥ 9 is open | [P] |
| TWINDEC: shared decoder rows across planes | Live (DOWN) and hosted (UP) run opposite ways: C_joint = 112. Round-trip lemma | [P] |
| FACTORSWAP: alternative rank-8 factorisations | Exactly 10 decompositions on F0 ∪ F1 (8 at C = 56, 2 at 64). The C = 56 ones form one Aut orbit (order 384). The native mirror already maximises shared endpoint frames | [C-lane, S] |
| STAIRJUNK → STAIRBUILD → ASSEMBLYLB: staircase deposits | 0/96 interior flag frames exist in #7546. Staircases leave the write vectors per target unchanged (0/864 differ), so the assembly floor moves ≤ 43–146 D0 | [P, C-lane] |
| ACYCDEC / H9CERT: acyclic decoders below n | Sub-n acyclic hits are border-rank artefacts. Exact Gram decoders beat n only on large blocks (48–49 at n = 55) | [P scoped, C-lane] |
| XDEC: joint multi-call decoder | Rank ≥ 8k; joint ≥ 112 for k = 2 | [P, C] |
| ≥ 6 replacement rows (SIXROW), h = 9 wall | Still **open**. The missing union-rigidity lemma and the certificate obstruction (Lemma A, HALF18) are stated above | [open] |

### II.3 Contract

| route | why it fails | tag |
|---|---|---|
| CONTRACTX: bigger blocks, ring extensions | I1: the bill is rank Odd(M) for any size or ring | [P, C] |
| coupled ports, isotropic q_a + q_b | I5: the ledger is per grading; the isotropic kernel is even in both | [P, C] |
| SHAREDGRADING: two ports, one grading | 05-layers.tex l.4–7 and l.86–91: P_M permutes the whole array | [P from quoted text] |
| caller park Y_p += q·X_p | o = 1 per J → 17 odd units/port/word → S = −112 | [P, C-param] |
| DECZERO's mixed target T | o = 0 → the caller buys 34 odd units/port/word (≈ −3,264 S against ≈ 952 saved) | [P, C-param] |
| CALLER45: M45 at ρ = 1 | C4 (root callers) | [P] |

### II.4 Parallel and multi-call

| route | why it fails | tag |
|---|---|---|
| PARALLEL: amortised or batched parks, sibling sharing, direct sums | Owned additivity: c ≥ 0.92/port/call | [P] |
| KSLOT: k-slot coded multicast (a spec change) | On #7546: 2,727 of 3,427 interior stops are pure unicast, 251 merge-only, 449 branching (1,067 D0). Gain ≤ ~48 D0/call (~0.2%) at the toy gap 4.5%; passing needs ≥ 28% | [C-lane] |
| XDEC | Rank ≥ 8k | [P, C] |

### II.5 Early-set and park family

| route | why it fails | numbers | tag |
|---|---|---|---|
| TMLEVER: Theorem-M lever via co-read cancellation | needs ≥ 577–590 early cells per contamination rank to tie the park family; best E8 design 329 | ceiling 0.9301× at built U | [P, C-param] |
| EARLYCAP A | the cap above, for d ≥ 2 | | [P] |
| EARLYCAP B → T1CANCEL | the canceller is the owned L row copied into the σ relay, so it is the park family + 104 useless ADDs | 0.8681× built U, 1.3093× LP U | [C-lane, C-param] |
| UFLOOR | a U-only floor cannot close t = −1. The binding lever is the U-junk layer: built 10,730 against the crossing 7,127 | | [P, C-param] |

### II.6 Merged twins and t = −½

| route | why it fails | numbers | tag |
|---|---|---|---|
| WINDOW8: merged 8-port window (shipped in Part III) | exact X = x − y, Y = x + y, but the park Y = x is impossible with shadows + token-only relays (x's birth frame is never inside the Y-end frame, 0/96) | 201.12 D0/call for the window route; owned fix ≈ 2,400 D0-eq against a gate of 471 | [P, C] |
| all-B single plane (t = −½, ρ = 2) | built 0.9773× (shadows 1,915 + relays 602 D0/call). Break-even shadows ≤ 14.41 D0/port | twins deleted 1.0950× | [C-param] |
| SHADOWCORE: cheaper shadows by editing | forced core 18.86 D0/port (min 15.79 > 14.4); no interior stop removable | | [C-lane] |
| MERGESCAN: per-port merge with cheaper relays | relays 6.279/port everywhere; best port 20.75 against break-even 20.69; A-type relay forced | 0 ports pass | [C-lane, P] |
| other ρ = 2 roots (t = −2, +1) | the invoice is t-invariant | | [C-lane] |

### II.7 Local edits of #7546 (fixed operation graph)

| route | result | tag |
|---|---|---|
| NETCOMPILE-W1 / REROUTE / ZEROSTOP / OWNRETIME: drop one stop or op and repair | 0/161, 0/332, 0/512, 0/101, 0/165 singles, 0/200 groups, 0 of 7,877 two-relay solves. By Theorem F these are plain infeasibility results | [C-lane] |
| ONERANK one- and two-block re-solves; MULTIBLOCK three-block | 0/161 invertible (2,815 corank-1 pairs only singular); 0 invertible in 13,540 triples | [P, C-lane] |
| MAINFUSE2: 2–4-op stop fusion and owned temporaries | 33 first-pass candidates all fail replay. One owned MOVE loses 1–7% | [C-lane] |
| SEEDBUILD: shared decoder partial sums S1–S6 | S1 built exactly; it costs +21.34 D0/call (κ ×0.99907); no stop removable (shipped in Part III) | [C] |
| OWNSCHED: re-schedule owned writes | write placement forced (Lemma F); best-case saving ≤ 380 D0/call against a 500 gate | [P, C-lane] |
| GEOFLOOR: d-geodesic helper paths | all 1,101 helpers have S ⊊ T, so every zero-loss path climbs; 0/332 meetings relocatable lower | [P, C-lane] |
| BREAKER8: joint meeting relocation including mains | 0/1,098 gains (loss concave in frame dimension). Lemma RT | [P, C] |
| TOKDEBT gate: is the one-rank miss token debt? | < 25% repaired (11.0% / 1.8% / 3.7%), so it is not. The rank-0 token-settled drops it found were shipped as #7601 | [C-lane] |
| CONTACTLB / JUNKLB: network floors | contact floor 145.6 D0, junk floor 313 forced stops = 433.9 D0/call (exact rational dual). Both ≈ 3% of the 13,974 D0/call network cost, so no plateau theorem | [C-lane] |

---

## Part III. Words that did not pay (`words.py`, `data/`)

- **Format.** Every word is shipped as an edit list against the vendored #7546 word, with a pinned canonical
  SHA256 of the rebuilt word.
- **Replay.** Each is replayed exactly over the rationals, with legality checks.
- **Rows.** Its rows are compared with the stated targets.
- **Price.** It is priced by the 17-call invoice wherever κ is defined.

| word | what it is | replay | price |
|---|---|---|---|
| #7546 (control) | ToikY's base word | legal, exact | S = 1424, κ 0.003648411294790845… (reproduced) |
| SEEDBUILD S1 | one decoder partial sum at a dim-2 join, serving 25–27 Y ports | legal; all 1,503 rows = #7546 (new helpers end at identity) | +21.3448 D0/call, κ 0.003645014837609… (×0.999069) |
| BREAKER8 relocation control | one 12-register meeting moved from dim 4 to dim 7 | legal; rows = #7546 | +16.8184 D0/call, κ 0.003645741005801… (×0.999268) |
| BREAKER8 Lemma RT swap | a main's route moved onto a new helper plus one main jump | legal; rows = #7546 | κ identical to #7546 |
| WINDOW8 w4_w00 | merged twins on the HALF18 8-frame window {20, 28, 69, 31, 38, 40, 48, 46}, shadow carriers + 2 token-only relays per port | legal; all 1,517 finals exact; X = x − y, Y = x + y on 8/8 ports; only 16 rows differ from #7546 | lane cost model: shadows 150.8892 + relays 16 × 3.1395 = 201.1210 D0/call. No κ (merged plane) |

**Note on the WINDOW8 cost.**

- **What 201.12 is.** It is the lane's route loss, against a design whose twins are deleted.
- **The census delta is smaller.** A plain census delta against #7546, with twins counted as mains, is 50.23 D0/call.
- **They are different questions.** The README quotes 201.12 only for the route comparison of II.6.

**Cut Lemma words (`cuts.py`).**

- W6805 is CubeJerry's #6805 word, vendored as data.
- feeder6805 is a t = −1 feeder word built by an outside-session lane (Fable-assisted, Mason's). It is shipped as an
  edit list against W6805.

**Not included, because the design was not replayed exactly as a word:**

- the YYMIX/K2REAL k = 2 cell-model designs (cell model only);
- the COURIER designs;
- the HANDT1 twin decoder (its algebra is checked in `e8laws.py`);
- the TOKDEBT tier-A attempts (none built: no repair, or strict settlement ranks 1/1/54);
- the b-family variants of WINDOW8 (exact in our lane, not re-shipped);
- the MERGESCAN singleton merges.

---

## Corrections of our own earlier statements

1. **The "one-rank law" is a tautology.** Our NETCOMPILE, SEEDBUILD, TOKDEBT and OWNRETIME notes reported that
   every drop "misses by exactly one rank". We read structure into it (the "contact-minimality conjecture"). By
   Theorem F the count is only infeasibility. The underlying rigidity is schedule-driven and has no lower bound
   (Descent Lemma).
2. **HALF18 (already posted as a comment on #7583).** The HALFWALL notes behind #7583 said a full-flag certificate
   on E8 has minimum rank ≈ 18 = 2h. That numerical search failed its positive control. Exact frame certificates of rank
   15 (E8-120) and 13 (P104) exist (`e8laws.py`); the exact lower bound we check is 8, so the P104 minimum lies in
   [8, 13]. The open question C ≥ 52 is unchanged in status; #7583's proved bounds are
   unaffected.
3. **Duality.** Internal notes treated U builds as duals of L builds ("asc56 = dual of desc56"). Duality preserves
   job type (UFLOOR). No public PR used this.
4. **EARLYCAP part B** ("a diagonal canceller makes early sets free") is refuted by T1CANCEL. It was never public.
5. **BYPASS relaxed screens** (0 failures, then 867) were optimistic. Only the non-descendant test (1,806/2,260
   failures) is sound.
6. **BREAKER8 control word.** The saved control `ctrl_up` is a costly relocation (×0.999268), not the Lemma RT
   swap. The RT swap words are shipped separately.

## Credits

- **Authors.** DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. This includes the
  outside-session lanes DECZERO, COURIER, YYMIX, XBIRTH and WEBS, which are Mason's (DreamingOfClouds).
- **Fable-assisted analysis.** The Clone lemma, the b-family and the identification of M45 as the B-port
  contract. We reproduced each independently (CLONEAUDIT, CALLER45, MERGESCAN).
- **ToikY.** The #7546 base word.
- **CubeJerry.** The #6805 word, used as data in `cuts.py`.
- **SYLforge (#7603), FanPUYen (#7604) and aliromman (#7605).** The current frontier, referenced only.
- **Rohan Arun.** The #7113 signed caller and its B pair.
- **PR968 authors.** The P104 decoder file.
- **Conventions.** Clear1nsight and the P104 price and replay lineage.

## Open next questions

1. Can one owned ascent be shared between t = −1 ports (WEBS)? The cuts allow it, and no realisation is known. An
   exact F2³ decision is in progress.
2. The d = 1 early-set window (577–600 cells per contamination rank at the LP-perfect U layer).
3. ≥ 6 replacement rows and the h = 9 wall (C ≥ 52): either an acyclic decoder ≤ 51 or a certificate that uses
   intermediate flags.
4. A rank ≥ 9 "free-lift" decoder network below 56 (DECZERO).
5. Whether a non-root caller with ρ = 1 can consume M45 with three odd ops in total.
