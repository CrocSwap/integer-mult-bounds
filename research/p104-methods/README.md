# P104 methods (no κ claim)

This package writes down the construction methods behind our P104 work so that
anyone can reuse them. Each method comes with a precise statement, its scope and
a small exact standard-library demonstration. It makes no κ claim and ships no
new word. It builds on, and does not repeat:

- [#7542](https://github.com/CrocSwap/integer-mult-bounds/pull/7542): two helper
  rung merges on #7334 (conditional κ 0.0036475398277);
- [#7555](https://github.com/CrocSwap/integer-mult-bounds/pull/7555): P104
  structure laws (σ-rank o, Lemma E, hub bound);
- [#7557](https://github.com/CrocSwap/integer-mult-bounds/pull/7557): t = −1
  laws (charge law, corrected anchored law, σ-anchor schedule, odd unit).

Tags used throughout:
- **[P]** proved in [PROOF.md](PROOF.md);
- **[C]** exact run in this package (checker named);
- **[Q]** quoted from our lane runs or a cited PR, **not** reproduced here;
- **open** not known.

Toy results are labelled **frame-free** when the checker does exact algebra
without chart legality.

| # | method | checker | what the checker reproduces |
|---|---|---|---|
| 1 | {0}/V re-basis | `rebasis.py` | the helper-761 rung merge of #7542, rebuilt from #7334's word |
| 2 | absorption | `absorption.py` | clean-iff identity; σ-anchor D = 0 and the last-cell rule (frame-free A3/A4) |
| 3 | range-G pre-loads | `preload.py` | Y_t = x_t with J_t = (11/2)G_t on all 104 columns |
| 4 | signed-row helpers, Rado/LU | `rado_lu.py` | exact group rule, one helper fixing a deficit of 2, LU into ADDs |
| 5 | O+(8,2) quotient | `quotient.py` | port/quadric counts, sign law, 12-port blocks, c-sum triples |
| 6 | t = −1 callers | `callers.py` | MONOHUB joint caller, four 20-odd-op floor callers, form orbit, even fusion |

## 1. {0}/V re-basis (`rebasis.py`)

**What it is.** An exact test for deleting a paid helper rung while keeping every
row of the word. When a helper's stop at chart F only delivers content, deleting
the stop's ADDs leaves an error E on some final rows. Two freedoms are always
available and are exactly linear:

- **{0} freedom [P, Lemma 1.1].** A register leaving {0} may take any combination
  of the departure contents of registers that leave later. Up to SCALE these
  unitriangular images are the whole {0} freedom.
- **V freedom [P, Lemma 1.2].** Nothing leaves V, so the V phase can end with any
  invertible recombination of the V-ending registers. A V-ending register only
  needs its V-arrival row to lie in W_V = span of the V-ending finals.

Together with optional local insertions at intermediate charts (j += β·s, solved
exactly mod p, then replayed over Q), this gives a per-basis-vector column test
(PROOF.md §1). A stop is repairable iff the test passes.

**What it achieved.**
- [Q] Across #7334's 201 source-only zero-need stops it found exactly one
  feasible stop: helper 761 at chart 1053. The near misses (1277@115,
  1322@1049) each fail on one direction that needs a Z-modified carrier, which
  the test does not cover.
- That stop is the 761 half of #7542.
- [C] `rebasis.py` rebuilds the 761 merge from the vendored #7334 word, which has
  the same bytes and SHA256 as in #7542. The edit is:
  - delete the two ADDs at 1053;
  - re-basis 1266 += ½·761 to {0};
  - add 1438 += 591 and 1438 += −2·760 at 1053;
  - add four ADDs at V: 1438 += 311, −591, +2·760, +1439.

  The replay over Q from arbitrary inputs, with full legality, gives:
  - all 1,569 rows and end charts equal to #7334's;
  - owned data unchanged;
  - helper 761's dims 0→5→7→8→9 become 0→7→8→9;
  - paid MOVE ranks per native word {2: −1, 5: −1, 7: +1}.

  The checker also verifies the two re-basis facts on their own:
  - nothing writes 761 between {0} and 1053;
  - 1438's V-arrival row is #7334's final − (e₃₁₁ − e₅₉₁ + 2e₇₆₀ + e₁₄₃₉), which
    lies in W_V.

  Seven corrupted variants are rejected.

**Not in this package.** The chart checks of the new {0}→rank-7 pair, the price
and the κ are #7542's (`chart.py`, `price.py` there).

**Scope.** Zero-need stops whose helper only delivers at the stop, on #7334-family
words. The test is exact for {0} freedom, V freedom and the local slots it is
given. The bilinear family (Z-modified carriers × local slots) is **open**.

## 2. Absorption (`absorption.py`)

Checker: `absorption.py` (stdlib, exact Fractions, 0.3 s). Tags: [P] proved, [C] exact run in the named checker, [Q] lane number quoted, not reproduced here.

**Mechanism.** Helper H is born at {0} with row h and lumps an arbitrary signed row -lambda.y from the Ys there. Readers take it at their low stops, as in a relay. At a higher stop K, H does H += sum_r d_r X_r(tau_K), where each X_r still holds outstanding junk psi_r. At V, H does H -= sum_r d_r X_r^final. No Y is at K, and the X_r are only referenced, never consumed.

**Identity and clean-iff condition.** Write X_r(tau) = X_r^f + sum_t psi_rt y_t. Then H = h + sum_t (sum_r d_r psi_rt - lambda_t) y_t, so H ends clean iff lambda = sum_r d_r psi_r (the lump must match ALL of the absorber's outstanding t; no subset can be chosen). [P: three ADDs, two lines of algebra, UBUS section 2]. [C part 1: identity exact on 40 random instances; clean when lambda = sum d psi; controls coefficient x2, dropped lump, dropped absorb ADD leave H dirty on 40/40.]

**Legality argument** [P, UBUS section 2 / ABSORBAUDIT section 1]. Every ADD is between registers at equal frames (H and X_r at K; at V). H's chain {0} < <q_p> < ... < K < V strictly ascends. Between its read stops and K, H carries charge only on supp(lambda) inside U(K), so it stays in each t-perp; after K its charge is 0. Absorption is public, ascending and equal-frame, so the known frame laws apply to it unchanged. [Q: ABSORBAUDIT replay on real E8 ports (cells (0,2),(0,3)): 0 violations, targets exact, controls fail; the abstract XY instance only, not the MONOHUB endpoint contract.] Not checked in this package.

**Last-outstanding-cell rule** [C part 3, LTOKEN]. An absorber may absorb X_r(K) only when (r,t) is X_r's last outstanding cell (all of X_r's other reads done). Frame-free algebra on A3, seeds 0-4: random absorb time D = 3 = n - r on 5/5; with the rule D = 0 on 5/5. The earlier fixed-order schedules satisfied the rule implicitly.

**Anchors and the GLIFT bill (frame-free algebra on toys; no frame legality checked; E8 not simulated).** Absorbed cells count as settled columns (charge lemma, [Q] ABSORBLIFT section 0), so without anchors the lift bill is n - r owned units [C: all settled gives D = 3 on A3, 6 on A4]. [Q: 96 units on E8, about 25k D0/call, against a 6.8-10k budget.] With the sigma-anchor design (one early pure-anchor relay per column re-added from the parked pure copy, one late direct reference cell per column, every other cell absorbed) [C part 2]: D = 0 and Y exact on A3 (9/9 runs over 3 seeds x 3 absorb timings; also mid-read and d = 3/7) and A4 (6/6; 40 of 60 cells absorbed). Controls D = n - r (3 on A3, 6 on A4): no sigma, absorb ADD dropped, coefficient x2.

**Value caveat** [Q, ABSORBAUDIT section 2]. The in-model STLP-type LP value (U floor 4,176 -> 609 D0/call at fixed tops; 1.3389x as an UNLIFTED ceiling) holds 0 owned units and ignores values: for dim-2 stops K = <q_p,q_r>, 768 of 4,992 pairs are fully rank-1, while 4,224 show a 23:1 split, so one cell per stop comes out wrong and must be re-cleaned. That is a realisation risk, not a refutation.

**Scope.** Mechanism and algebra only. Absorbers cannot be anchors (they are settled); the sigma early cells stay relays with chain {0} -> <q_sigma> -> V [Q ABSORBLIFT section 3]. The L side is untouched; its Y-prefix network remains the gate. No kappa word.

**Achievements.** The absorption identity with controls [C]; sigma-anchor absorption reaches D = 0 where all-settled costs n - r on A3/A4 [C, frame-free]; the last-outstanding-cell rule reproduced [C].

## 3. Range-G pre-loads (`preload.py`)

**Method.** In the relay model each column Y_t is assembled from the y_t anchor, an owned rank-8 L row, and the complete-junk
carrier contents K_s = x_s + sum_u Z_su y_u (Z = G/2 - I) of the 48 partners s, with weights c_s = -G_ts/2. Giving the owned L
row a y part, L'_t = sum_u G_tu (x_u/2 + mu y_u), the junk of the carriers cancels exactly. **Scope:** the junk (window/LC1-per-
coordinate) algebra of the L side on the E8/P104 Gram only; it says nothing about the charge (nu-ledger / token) side.

**Claims.**
- [P] With G^2 = lam G, sum_{s partner of t} G_ts G_su = (lam-2) G_tu; hence the y-residual of Y_t is (mu - mu*) G_t with
  mu* = (lam-2)/4 - 1/2, and the x part is exactly x_t. For lam = 26, mu* = 11/2.
- [C] On all 104 columns (Fractions, PR968 Gram): Y_t = x_t with every y cancelled, 0/104 misses, no zero-Y park; the owned
  rows G(x/2 + mu* y) have rank 8.
- [C] Controls: mu = 0 gives 104/104 misses with residual exactly -11/2 G_t on every coordinate, hence on every window N_p
  (all 104 x 48 pairs (t,p), nonzero); zero-Y park + mu*: 104/104 misses; one partial-junk carrier (20 of 48 cells): 28 missed
  coordinates in every column; wrong mu = mu* + 1/4: 104/104 misses; closed form residual = (mu - mu*) G_t at several mu.
- [P] Legality core: G = D^T T / 2 (PR968 factors), so G_t.y = (1/2) sum_k D_kt (T_k.y) lies in the span of the eight owned U rows;
  with the up-set legality lemma (owned U rows are cleared at V in every frame set) any range-G y vector is legal.
  [C] checks the identity for all t on a fixed integer y; the up-set lemma itself is quoted from the lane proof, not re-derived.
- [Q] LBREAK: windowed solve 0/40 (J = 0) vs 40/40 (J in range G) on sampled (t,p); lane run, not reproduced here.
- Open: the charge half. Carrier tokens need the reader to cancel H_s's token pre-anchor, which re-settles the column
  (D = n - r in the A3/A4 toys); no design found that makes the carrier token-free and charge-free. Not claimed here.

**Data / sources.** No vendored data. Reads `research/complex-frame-pair-decoders/inputs/pr717/P104_HIT_flip_3a.txt`
(PR968 decoder), sha256 8e0178db02c14e1b29058cdbdbd50aac22f2b55a1ba21dc82f417610c9932526, hash checked in the script.

## 4. Signed-row helpers: Rado transversal test and LU into ADDs (`rado_lu.py`)

Checker: `rado_lu.py` (stdlib, exact Fractions, <1 s). Tags: [P] proved, [C] exact run in the named checker, [Q] lane number quoted, not reproduced here. Abstract demo of the algebra; no FANOUT56 geometry.

**Model** [P, FANOUTOPT section 1]. A need row rho_r in Q^d is the content a register must still receive. ADD r += c s acts as rho_r += c rho_s; a load at {0} sets a helper's initial row freely; all rows end at 0. Lemma 1 (support): a register's row is supported on A(S) at frame S, because frames only ascend, co-located registers share A, and no injection happens at forbidden frames.

**Group rule.** At a frame S, members with incoming rows R span Omega. Member p leaves for a frame with allowed set A'_p, so its outgoing row lies in Omega_p = Omega meet R^{A'_p}. Feasible without new helpers iff one vector per Omega_p can be chosen spanning Omega (Rado transversal). Then N = T R with T in SL, realised by LU into transvections (ADD r += c s). A helper is a member with a free signed row that leaves with row 0.

**Test implemented** [C]. Exact deficiency form of Rado: max independent partial transversal = min over member subsets S of (dim sum_{p in S} Omega_p + m - |S|); feasible iff it equals rank Omega. A transversal is built from random integer combinations and verified exactly (each v_p in Omega_p, all v_p spanning Omega). T is found by solving T R = N, adding left-null-space elements until invertible, rescaling one row to det 1; the ADD list comes from Gauss-Jordan with ADDs only (no swaps). Replay of the ADDs must give N exactly.

**Demos** [C]. (i) A feasible 3-member group in Q^3: certificate verified, 7 ADDs replay to N. (ii) Two proportional members, rows (1,1,1,1) and (2,2,2,2), leaving on blocks {0,1} and {2,3}: both Omega_p = {0}, max transversal 0 against rank 1 (deficit 2), infeasible by the Rado test and by brute force over the box [-3,3]. One helper with the free signed row (1,1,0,0) makes both sections 1-dimensional, leaves with row 0, 8 ADDs replay exactly (20 of 624 signed rows in [-2,2]^4 work). (iii) Control: the old pure-helper rule, modelled as helper row restricted to one coordinate e_k, fails for k = 0..3 on the same group. Scope note [C]: with single-coordinate exits ((1,1,0,0),(2,2,0,0) leaving on {0},{1}) a pure e_0 helper suffices, so the free row matters when members leave on coordinate blocks.

**Cross-checks** [C]. Seeded sweep of 118 random small instances (d = 3, 2-4 members, entries in {-1,0,1}): Rado verdict equals the independent brute-force verdict on every instance (61 feasible, each with exact transversal and exact ADD replay; 57 infeasible). Controls: a non-spanning transversal is rejected; a corrupted ADD list fails replay.

**Gather side** [Q]. It is the time-reversed transpose: a dual row is a give vector, the dual op g_x += c g_y is the forward restore ADD, with identical helper prices. Not run here.

**Quoted lane result** [Q, lane exact run, not reproduced in this package]. FANOUTOPT's full build: F = 408.68 D0/call with 50 helpers, against FANOUT56's 1,692.1 (4.14x fewer), with proved floor 315.05 D0/call (the FANOUT56/H2 U-level oracle scope; the build sits 1.30x above it).

**Scope.** Group-level algebra only: no frames, flags, pricing or FANOUT56 census.

**Achievements.** An exact, certificate-carrying Rado feasibility test with LU factorisation into elementary ADDs; the "one helper fixes a deficit of 2" statement shown on a concrete group with a control that pure rows fail.

## 5. O+(8,2) quotient structure and the c-trick (`quotient.py`)

**Method.** Write c for the all-ones vector of F2^9. Every port has q.c = 1, so ports live in W = V/<c> ~ c^perp (representative
q+c, even weight) with symplectic omega = dot; partners are the pairs with omega = 1. The 104 ports are 104 of the 120
nonsingular points of an O+(8,2) quadratic form (16 missing). Two consequences are used by the U-junk layer: a sign law
(two-graph) and c-sum triples. **Scope:** structural facts about this port set and Gram; no D0 pricing.

**Claims.**
- [C] Gram of data/ports104.json: rank 8, G^2 = 26G, 48 partners per port, partner <=> G odd <=> dot(q_p,q_t) = 0; equal entry by
  entry to the PR968 Gram under the vendored permutation with diagonal +-1 switching (data/iso968.json); swapped control fails.
- [C] A unique quadratic form (polar = omega) equals 1 on all ports: 120 nonsingular / 135 singular nonzero points, 16 missing.
- [C] Sign law: over the 19,712 mutually-partner triples, G_py G_yt G_pt = -1 exactly for the 704 triples with q_p+q_y+q_t = c
  (the 704 c-sum triples, all pairs partners); the other 19,008 are +1. No proof is included beyond the exhaustive check.
- [C] Pair law: partner pairs split 2,112 (24 common partners, exactly 1 sign-wrong cell = the port t* with q_t* = q_p+q_y+c) and 384
  (22 common partners, 0 wrong; p-bar+y-bar is a missing point). This is the 3-stop-absorber fact: a partner reference y of reader p
  has exactly one wrong cell t* = p-bar+y-bar (when that point is a port).
- [C] All 200,787 4-dim subspaces of W enumerated: exactly 282 hold 12 ports; each has its 3 non-ports on a line and 16 c-sum triples
  (histogram printed). [C] One packing (data/packing8.json): 8 blocks, each one of the 282, disjoint, covering 96 ports; the 8 leftover
  ports (6, 13, 17, 36, 43, 46, 58, 73) contain no c-sum triple. Not claimed for every packing. Controls: perturbed packing, random
  12-subset.
- [P] c-trick: for ports t.c = 1, so t.a = 1 <=> t perp a+c; hence {partners of p not perp <p,a>} = U<p,a+c>. [C] for all ports p and
  all a in F2^9. [C] on the 33 disjoint c-sum triples (data/triples33.json; q_p+q_q+q_x = c, A2(p) = <p,q>): bottom(p) = U<p,x>, 24 cells,
  and the (reader p, host x) pair has exactly one sign-wrong column, the third triple member (198/198; 4,224/4,224 for all c-sum triples).
- Not re-checked: the order-384 stabiliser (orbits 32/48/24); 33 is the lane's CP-SAT packing (bound 34) — the checker does not prove maximality.
- [Q] Lane runs, not reproduced here: the 11,376.3 D0/call U-junk build (1,439 helpers + 104 anchors), the 8-block CP-SAT proxy 1,135.3
  per block, the J-flag incompatibility (0 of 1,408 oriented triples), the 17,270.2 D0 ABSORBNET build.

**Data.** data/ports104.json sha256 0299f8f7165835231b057e1c6151ad0a8333efcb61a06a0a2aea045aa391c381 (lines104.json + G104.npy of
REBASET1, derived from the #7334 word's charts + reflection closure, gram104.py); data/packing8.json a4bd773ede969488aacdf8feb38487b97ce3daf48d836bbb1bd48f6fd356e12e
(QUOTIENT/bpack2.pkl via blocks.pkl, port index = ports104 order); data/triples33.json f9007e39cf6ce94915848e9c810f28572dc423c929e3c3f4d874301b8359d12e
(ABSORBNET/tripack.pkl); data/iso968.json fd3fb6b90918d6802c7b22b7fe2efdf3a3979e4bc50bb610437957a84b702e1f (permutation/signs found by a
backtracking search over an 8-line basis, verified exactly in the checker). Also reads the PR968 file
`research/complex-frame-pair-decoders/inputs/pr717/P104_HIT_flip_3a.txt` (sha256 8e0178db...2526).

## 6. t = −1 callers: MONOHUB joint caller, the 20-odd-op floor, form orbit, even fusion (`callers.py`)

Tags: [P] proved (where), [C] exact run by `callers.py` (F_p, p = 2147483629, q in {1, i, -1, -i}, generic stage scalars D), [Q] quoted from a cited PR, "open" = not shown. Everything is scoped to the **joint_mono A target** (the scalar -I_36 on the 36 A roles, every exponent odd), PR #7113's B half, masks and idle sets, and one J = one native stage (17 per word).

**The MONOHUB t = -1 caller.** The joint caller `joint_mono` uses PR #7113's JSON format (Rohan Arun's caller; credit to PR #7113). Its A half is a single-hub hosted caller; its B half and B pair (-1, 1/2) are #7113 verbatim.
- Each of the 17 J calls applies on A the pair HOST(alpha, beta) = (-1, 1), i.e. (s, t) -> D_k (s - q t, q^-1 s), matrix H = [[1, -q], [q^-1, 0]], trace 1, t = -1. [C]
- A events: ADD 428, SWAP 101, SCALE 69, LAMBDA 76, IDLE_ONE 47, QUERY 3, plus 17 HOST (741 in all). [C]
- With an idealised native HOST(-1, 1) on the A ports the whole 72-role map equals the target at the four q (bad 0 of 5,184 cells per q). [C]
- The replay is sharp: A pair (-1, 1/2), (0, 1), (1, -1), B pair (-1, 1), each of the 3 thin QUERY dropped, one idle dropped, one LAMBDA flipped (silent at q = 1, -1 as in #7113, caught at q = +-i), an altered idle set all give bad > 0. The #7113 caller with its own native is bad 0, and alpha2 = +1 or one QUERY dropped gives bad > 0. [C]
- This shows the caller is exact for an *idealised* native. No native realising HOST(-1, 1) with the existing helper layer is claimed. [open]

**The 20-odd-op floor.** Let sigma: q -> -q and R = sigma(M) M^-1 for the word M. The target needs R = -I_36.
- R is a product of conjugates of the factors' sigma-factors, so sum of ranks >= 36 + 1 = 37, with equality only if every factor is an involution (Lemma E, #7555; equality clause proved in our GAUGECYCLE lane (not public)). [P]
- J factors are not involutions: a q-odd transvection plane has sigma-rank 1, H has sigma-rank 2, QUERY has 1, QSELF is a reflection (det -1). The ledger is run per op. [C] (ADD/SCALE/SWAP/LAMBDA/IDLE_ONE 0, QUERY 1, J(H) 2, J(SW) 1, QSELF 1, all other det +1.)
- With one q-free plane (sigma-rank 1 per J) the word needs >= 37 - 17 = **20** odd ops per A port per word. [P, scope: one q-free transvection plane per J; a fully q-free HOST(-1, 1) plane has sigma-rank 0 and floor 36.]
- **Four callers sit exactly at the floor** (live-free / hosted-free x odd / even): each replays at bad 0 at the four q. The odd variants hold 2 QUERY + 18 IDLE_ODD = 20 odd ops; the even variants hold 2 QUERY and give up the 18 phase fields as even (priced the same). [C]
- Controls all rejected: free plane given back its q, alpha2 = +1, each QUERY dropped, a phase/idle op dropped, the cancel ADD dropped, an IDLE_ODD made even, a LAMBDA flipped. [C]
- Whether a native with the needed q-free plane can be built at break-even is not shown here. [open]

**Form-orbit growth law.** On joint_mono A, native H, all 17 J on roles (X, Y) = (1, 0), at all four q and two D seeds: [C]
- each J brings exactly 3 new lines (x_k, y_k, x_k - q y_k); 51 distinct lines among 68 forms;
- the 17 input planes span 34 dimensions (pairwise independent); rank of output plane J_k plus input plane J_k+1 is 4 for all 16 consecutive pairs.
- So M is applied once to each plane and its finite order (H^3 = -I) is not exercised on repeated content. [C for this caller only; a different caller is not covered.] Controls: the non-exact native SW fails replay; a repeated-plane list would read as 2 lines / span 2.

**Even-fusion check.** Replacing two consecutive H calls by SW, SW plus a free q^2 on roles (0, 1):
- the o of every consecutive H-pair segment is 4 (7 at the QUERY pair), against 2 (5) for SW + q^2; [C]
- all 8 fused pair replays (pairs (1,2), (3,4), ..., (15,16)) fail at q = i, -1, -i (silent at q = 1); the control (H kept + q^2) also fails; H kept alone and SW with the per-J phases X*q, Y*q^-1 are bad 0, and dropping one J's phases gives bad > 0. [C]
- So a fused pair would need odd part of rank 4, not 2. Fusions other than these 8 pairs of SW + q^2 are not tested. [open]
- Lemma E, the identity o = rank of the q-odd part, and the gauge-shifted bound (m - 16) + (36 - m) = 20 are [P] in #7555 and our GAUGECYCLE lane (not public); only the ledger values are re-run here.

`data/` (gzip, mtime 0, SHA256 checked by `callers.py` before use); provenance is the lane card folder (our own builds) unless stated.
| file | sha256 | provenance |
|---|---|---|
| joint_mono.json.gz | 4ffb61264d446d107de23fd9af05090db77aa16e64840165c6a0329ad0f3f3c4 | MONOCALLER joint_mono.json (A = MONOHUB hosted caller, B = PR #7113 verbatim) |
| caller-7113.json.gz | 7e8038559cd158f6e32ef6d1a3bf15ab6a8ecc2239af32ab1699511ac28e26d9 | PR #7113 (Rohan Arun) caller JSON, byte-identical copy in MONOCALLER and LIVECALLER |
| livecaller-livefree-odd.json.gz | 7b8e8c9dd04ce965f9162950da4270c7bbea1ee1fe97d11b99566abd014ce8b9 | LIVECALLER CALLER_livefree_odd.json |
| livecaller-livefree-even.json.gz | ddfc96cda2c8e4001c6b81c5c5a088d60fdb5423516384cbd8a338d19531a5cd | LIVECALLER CALLER_livefree_even.json |
| livecaller-hostedfree-odd.json.gz | a1fc419bb3c3eb7f756840c60cd3010f15c40bb09088983e56ccc8b24ff439ea | LIVECALLER CALLER_hostedfree_odd.json |
| livecaller-hostedfree-even.json.gz | 688f2464a8239562069be17b5b7e92593eaa7873975ebf86c1f6c6bd5cb49e83 | LIVECALLER CALLER_hostedfree_even.json |

## Checks

```sh
python3.12 -B scripts/research_package.py --package research/p104-methods
```

Six standard-library checkers, listed in VERIFY.json. Each prints its numbers, runs controls that must
be rejected, and ends with a PASS token. Vendored data in `data/` is authenticated by SHA256 inside the
checkers. The repository input (the PR968 decoder file) is pinned in SOURCES.json.

## Open next questions

The two questions recorded in TASK.json, plus the parts of our lane work not reproduced here:

- The general {0}/V re-basis scan, and the bilinear (Z-modified carrier × local slot) extension for
  1277@115 and 1322@1049.
- A frame-legal E8 absorption layer under the σ-anchor schedule. Absorption's D = 0 is frame-free toy
  algebra only.
- FANOUTOPT's full exact fan-out build (408.68 D0/call) and its 315.05 floor.
- QUOTIENT's 11,376.3 D0/call U-junk build, and the order-384 stabiliser.
- A native that realises HOST(−1, 1), or a q-free plane at break-even.
- Lemma A (#7557) stays open.
