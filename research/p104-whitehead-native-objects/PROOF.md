# Whitehead native objects and price targets: construction, checks, targets, routes

Tags: [R] replayed by `check.py` or `checks/check_joint_w.py` in this package; [B] recorded from the build of the object and not rerun here; [Q] quoted from an earlier analysis, not recomputed here; [J] judgement. Nothing here has been reviewed by a human. No kappa claim above #6936.

## 0. Summary

1. **The the hosted Whitehead word [R].** #6936's mixed word with the outer Whitehead (W) stage on its 8 hosted ports. At stages 1 and 18 those ports run a native with X = x - 2y, Y = x/2 (alpha = -2, beta = 1/2, t = -1, d = 0 raw). Exact kappa **.0035927413806393823240**, S = 1504, D = 421735.2023, **-0.9451%** against #6936. The 16 other stages, the root of the 96 two-chain ports and their natives are #6936's.
2. **A helper-free d = 0 native on all 104 ports [R].** Exact, two engines, 100 mutants. Public 1652.63 R0, owned 208. It is not a candidate: the replacement budget allows 172.78 (outer) / 175.86 (rho = 1) owned.
3. **The connected rho = 1 all-Whitehead root [R].** 18 stages at t = -1, every requirement of the root checker passes.
4. **The targets [R arithmetic, Q ledger].** Break-even 0.1099 / 0.1395 UP per port-call; replacement budget `owned <= 111.573 + T - dpub`; pass line 1.66 owned per port.
5. **Closed and open routes** with their scope: sections 5 and 6.

## 1. Objects

### 1.1 The hosted pair and the Whitehead stage

A hosted stage is two consecutive unit reflections T = I - 2xy^T of the root, with alpha = y_u . x_v and beta = y_v . x_u, t = alpha beta. In the basis (x_u, x_v) the caller needs the plane block W = [[1, -2 alpha], [-2 beta, 1 + 4t]] (the product of the two unit reflections); the native's -1 sector must be conjugate to it by a dyadic matrix. At t = -1 the hosted native has d = 0: T[Y,K] = 0 with no helper content left in Y. [R] `window_native.py` checks that a dyadic conjugator exists for (alpha, beta) = (-2, 1/2) and (-1, 1); the two are one gauge apart (alpha lambda, beta / lambda with lambda = 2).

The roots: `rootw1g.json` is the type B root of #6936's word with W stages 1 and 18 (outer, w = 1), t = -1 exactly at those two stages and t = -1/2 elsewhere, in the gauge of #6936's root. `root_h.json` (no W stage) and `rootw1.json` (ungauged W root) are controls and must fail. [R]

### 1.2 The the Whitehead native, caller and invoice

| file | sha256 (first 16) |
|---|---|
| data/mmW.json.gz (the Whitehead native) | 13019ac4b8a2f051 |
| data/mm.json.gz (#6936's native) | 273e81f176f00168 |
| data/joint_caller_w.json (caller) | 148356dca93357e5 |
| data/rootw1g.json (type B root) | 0e6622d7d27b0e30 |
| data/w.joint.invoice.json | a538d4ea1825fbde |
| data/mm.chain.invoice.json (#6936's invoice) | 2cef5b86ac7d1a7e |

Full hashes are in `data/OBJECTS.json`.

- **Native.** Per hosted port, one prefix: INIT an owned register at Z; add y; MOVE it from Z to the line S(q), an owned UP of rank 1; subtract it from x; CLEAR. That is 8 more owned UPs than #6936's native (rank mass 56 to 64). [R] `verify_host3w.py` replays 71,184 events in exact Fractions with the odd certificate S = 1125, 0 bad endpoint rows, owned UP {1: 18, 2: 4, 3: 1, 4: 6, 5: 1, 6: 1}; #6936's native re-passes (71,144 events, UP {1: 10, ...}, 0 bad rows). A control that declares alpha = -1 for the Whitehead native has 16 bad rows.
- **Caller.** One stream of 78 roles, each contact naming its native (#6936's at 16 stages, the W native at stages 1 and 18); the A events are #6936's caller verbatim. [R] `check_joint_w.py`: the stream replays mod p at the four central characters to the block-diagonal target (12 evaluations, 6,084 entries each, 0 bad); each type alone also replays; each stage's pair read from the root equals its native's; controls reject a W stage served by the wrong native (9 bad), the ungauged root (292 bad), a wrong root entry, a wrong alpha; the invoice is rebuilt from emitted events and, independently, from the two roots plus the natives, term for term.
- **Invoice move [R].** T: 8 x {145} -> 8 x {129} (the hub-2 drop on the hosted ports' mask incidence); P: -16 x {8} (idle runs) and +16 x {1} (8 carriers x 2 W calls). S 1520 -> 1504.
- **Price [Q for the split, R for the totals].** Hub alone (a W root with no UP, illegal at t = -1) would be +0.1167%; the UP alone is -1.0605%. Each paid rank-1 UP costs about -0.066% (about 1/1520); each port-W-call of hub saves +0.0073%. The UP costs about 9 times the hub saving per port. w = 2, 3 outer W stages: -1.896%, -2.853% (priced, the root callers built exactly, the natives not rebuilt).
- **Recorded, not rerun [B].** Second exact engine mod 2^61 - 1 with 174 mutants (126 standard and 48 on the 16 carrier ADDs), 0 accepted; physical streams on two further primes (all 512 characters, raw identity XX = YY = D on all 104 ports); stage and joint physical contacts; 3,234 native chart maps; relaxed verifier accepts, strict rejects at exactly 31 events (the 23 of #6936 and the 8 carriers); raw counts literal 807,429,216, actual 820,670,236, upper 836,955,424, all under 1e9; outer interval engines with minimum logarithm power 2204 (2203 fails).

### 1.3 The 104-port window native

`data/window_native.json.gz`, sha256 56c803aaf5383342. 1,456 events, no helper. [R] `checks/window_native.py` regenerates it from the construction below and requires equality with the shipped object, then:

- **Construction.** Take a perfect matching on the dot-0 graph of the ports (52 pairs). For each pair (a, b): two owned rank-1 registers read x_a and x_b at the lines <q_a>, <q_b>, go UP to <q_a, q_b> and DOWN to the other line, and are subtracted into the partner's X register (X_b := x_a, X_a := x_b), then cleared. Y_b is moved into the window <q_a>, which lies inside q_b-perp because q_a . q_b = 0, and X_a += delta Y_b, Y_b += gamma X_a with gamma = beta, delta = -1/beta. That removes y and makes Y_b = beta x_b. The mains then rise to their final frames and a gate at the full frame swaps X_a and X_b back. d = 0 is free (the window swap); the cost is the beta crossing, **2 owned rank-1 moves per port (UP 1, DOWN 1)**.
- **Exact replay.** 0 violations, 0 bad rows; public paid {1: 104, 7: 104, 8: 104}; owned UP {1: 104}, DOWN {1: 104}; peak owned 2; 104 lifetimes. The mod 2^61 - 1 replay on 4 random inputs has 0 bad entries. The 208 x 208 transfer matrix is exact: T[Y,Y] = 0 on all 10,816 entries, T[Y,X] = beta I, T[X,X] = I, T[X,Y] = alpha I, invertible, det per port 1, every row on its own (x_p, y_p). The mains start at <q> (X) and {0} (Y) and end at the full space and q-perp, for all 104.
- **Price.** Public 1652.628 (rule: `sum P r^(1-k)`, k = .0036270188296, helpers credited at their rise, mains' T not credited); owned 208; the floor with 208 one-hop mains and no helper is 208 x 8^(1-k) = 1651.497, so the public layer is 1.131 above it. Every integer partition of every progress 1..8 costs at least its one-hop cost, so the floor holds for any public layer under these pins (it says nothing about owned mass).
- **Mutants.** 100 single edits at pairs 0, 25, 51 (coefficient, frame, order, drop and duplicate, wrong partner) and four wrong-target judgements: 97 rejected; the 3 accepted are one mutation (C2's exchange before C1's), the same equivalence at each pair, because the two owned registers are independent after both copies.
- **Frame law.** Valid under the owned-ascent allowance only (section 2); the strict owned rule rejects exactly the 104 UPs. Owned lifetimes 104 and peak 2 also exceed the old 11-lifetime pin, like the other hosted words.

### 1.4 The connected rho = 1 root

`data/r1_W18_t3.json`, sha256 e2bd8b71f9e6670a. [R] `rootcheck_w.py`: ALL_REQ_PASS. At rho = 1 every reflection is the scalar -1, G_ij = sgn(i - j), the dual product (-1)^N = -1 needs N odd; layout [9 W stages][3 thin][9 W stages], N = 39, n = 38, L = 18, hub of one field. Checked: isotropy; T_{N-1}...T_0 = -I; stage units consecutive, disjoint, ordered; units inside masks; masks commute with the prefix before and after; the symbolic whole-job identity M(D) = -diag(prod D^eps) over all 18 stage variables; every variable credited on its whole mask; t = -1 exactly at every hosted pair; x, y dyadic (largest entry 2); rank G = n = 38; x and y span; Gram digraph strongly connected; span{x_i y_j} of rank 1444 = 38^2 (irreducible, not a direct sum). A wrong X entry is rejected.

- **Price [B/Q].** D per port 1816.63 R0 (T 6408.60 less line credit 4591.98; the lines are a built line system of mutually orthogonal dual lines, LP bound equal to the greedy construction); change -422.19 per port; S = 1624 - 1872 c (S = 48 x 36 - 104 at c = 0). Free-native ceiling (c = 0) **+19.33%** (kappa .0043280); outer w = 8 +11.17%; outer w = 1 +1.54%.
- Singles at some stages (a mixed root) never raise the break-even: the all-W root has the largest c* (0.1395; 16 W calls 0.1394, 12 0.1370, 8 0.1268, 6 0.1129, 4 0.0796, 2 none) [Q]. Odd numbers of W stages did not build.

## 2. Declared assumption: owned ascent

The change, relative to the strict native rule "owned MOVE descends": an owned MOVE between nested frames may go either way (`frames[b] < frames[a] or frames[a] < frames[b]`), paid |change in dimension| as for a descent; public MOVEs still ascend strictly. The two words here depend on it: the hosted Whitehead word has 31 owned UP events (18 + 4 + 1 + 6 + 1 + 1, rank mass 64, 8 more than #6936's 56 over 23 events), the window native 104 (rank 1 each). [R] `verify_host3w.py` and `window_native.py` count them; the strict rule rejects exactly those.

Cost: a rise and a fall between the same two frames apply C_b C_a^{-1} and its inverse, of the same rank, so the paid rank is direction-free; an owned register is never an input, earns no target and is cleared before return, so a rise creates no credit. This is assumption A6 as declared in #6883 and its precedents (the nested-centre transport of the retained P112 native, whose backward word accumulates into an owned centre, moves it up by rank 3 and 5, reads it and clears it). The numbers here are conditional on A6 exactly as #6934 and #6936 are.

## 3. Exact targets

Notation: k = .0036270188296 (#6936), rank-1 owned row = 1 R0, rank r owned row = r^(1-k).

**Break-even per port-call c\*** (extra owned UP per port per W call, added on top of #6936's native; all 104 ports run t = -1; exact decimal solve against #6936's invoice) [Q table, R arithmetic of T / 104]:

| shape | W calls | change in D per port | c = 0 gain | c\* |
|---|---|---|---|---|
| outer w = 1 | 2 | -61.44 | +1.538% | **0.1099** |
| outer w = 2 | 4 | -120.89 | +3.07% | 0.1081 |
| outer w = 8 | 16 | -407.29 | +11.17% | 0.0911 |
| direct sum J = 1 | 2 | -65.43 | +1.64% | 0.1170 |
| rho = 1 all-W, 9 \| 9 | 18 | -422.19 | +19.33% | **0.1395** |

The BIT cap (+4.15% relative to #6932) is reached at c = 0.1108 (corrected from 0.1096): below about 0.11 the gain is cap-limited, so the usable window for the full capped gain is c <= 0.11, for any gain c <= 0.1395 (rho = 1). First-order rule: c\* = S0 dD / (D0 calls) with S0 = 1520, D0 = 4059.87 per port. T1's carrier costs 1.00.

**Replacement budget** [Q constants, R arithmetic]. A native F that replaces #6936's native at every W call must satisfy

`bill_pub(F) + bill_own(F) <= bill_pub(mm) + bill_own(mm) + T`, i.e. `owned_R0(F) <= 111.573 + T - dpub`, `dpub = bill_pub(F) - 1702.405`,

where mm is #6936's native at the ledger basis (public 1702.405, owned 111.573 = 56 UP + 56 DOWN, total 1813.98), and `T = 104 c*` = 11.426 R0 per call (outer w = 1, F0 = 22.853 over 2 calls) or 14.513 (rho = 1, F0 = 261.236 over 18). Linearisation: bill_pub ~ S cost + k D, within 0.1 R0; 276 R0 of public D saved buys one owned S, and every public S saved buys one. Reference points: if F's public layer is the Gram-based layer's (1680.12, dpub = -22.29) the owned allowance is 145.29 / 148.37; with mm's public layer 123.00 / 126.09; with the helper-free layer here (dpub = -49.78) **172.78 / 175.86**. If 22.29 R0 of hosting D is charged to F as well, 150.5 / 153.6.

**Pass line.** With the helper-free public layer: owned <= **1.661 per port per W call** (outer), **1.691** (rho = 1); 1.447 / 1.477 with the hosting charge. The window native has 2.0: over by 35.22 / 32.14 R0 per call, +46.65 against mm in total, +20.72 against the Gram-based layer with 104 owned UP. It cannot be closed on the public side: at owned 208 the public layer would need to be at most 1617.4 / 1620.5, below the floor 1651.50.

**Gram-based layer replacing mm** [Q]. Public 1680.12 plus owned 55.79 plus 104 owned UP = 1839.91, +25.93 per call over mm, over T by 14.51 (outer) and 11.42 (rho = 1): exact kappa -2.011% (outer w = 1), -4.268% (w = 2), -21.42% (rho = 1). Rank-1 UP break-even u\* = 89.49 (outer), 92.58 (rho = 1); on this public layer a mass-104 owned layer is dead, and a native with under about 89 to 92 owned UP passes.

**Scope of the ledger.** The ledger basis treats all 104 ports as hosted. the hosted Whitehead word's built word has 96 ports at t = 0 with #6936's literal native, so the literal bill differs by the 96 ports' second chain (1524.46 R0 of mains). The budget T does not depend on the choice; only the absolute bill of mm does, and the literal bill must not be applied to an all-hosted F.

## 4. Errors corrected on the way (for readers of earlier statements)

- "The d = 0 correction may cost up to about 123 S, not 11" is the right baseline for a replacement, but it holds only if the new native's non-W work shares owned lifetimes with the old; #6936's owned layer sits at the published P104 floor of 56 per stage, and no sharing exists on it (0 of 54 owned lifetimes co-rest with Y_p and later X_p, on all 8 ports). The kills of the Gram-based-layer-verbatim objects stand: they were either that layer verbatim or failed on rank alone (>= 52).
- Lemma M (an owned read-run with row support U and column support V costs MOVE mass >= rank_F2 Gram(q_U, q_V)) needs the two-phase hypothesis (each x read once with a fixed coefficient, every read before every effective write); born at Z it is **>= rank + 1 per run**.
- An explanation of the 56-unit owned layer as 14 runs of 4 was wrong (19 lifetimes, 24 DOWN moves of rank 1..5; 14 is the defect rank).
- "A block-diagonal P needs rank >= 13" holds only when every block is an orthonormal set (the largest orthonormal port set on P104 is 8, so at least 13 blocks); a general block-diagonal P can be as low as rank 8. The shape 13 runs of 8 ports in dim-4 spans does not occur on P104. A floor of 65 owned for a hybrid is 88 on P104 (137 with the rank law).
- The cost of splitting an 8-dim hop depends on the cut: 1+7 costs 0.0109, 2+6 0.0162, 3+5 0.0191, 4+4 0.0200.

## 5. Closed routes (scope in brackets; each [Q] unless marked)

| route | result | scope |
|---|---|---|
| Owned-UP carriers on #6936's native (this word) | -0.9451% with 8 ports, -1.896% / -2.853% with w = 2 / 3 [R] | #6936's native, hosted ports, its caller |
| Piggyback on #6936's owned lifetimes | 0 of 54 [B] | native verbatim, pure-x window |
| Public helpers as free carriers | 0 of 8 ports close the clean-up pattern: after h reaches X_p's frame it never co-rests with Y_p again [B] | native verbatim; escapes: a clean-up register other than Y_p, an a = 0 variant |
| Amortise the UP across W calls | impossible in the native/caller format (per-call replay, fresh data; block-diagonal additivity at rho = 1) | format fixed by the caller |
| Drop the hosted ports' R part | at most 165 R0 against 1977.5 needed | single deletions on #6936's native |
| a = 0 / d = 0 per-port mixes | rank floor 94, crossings 104 | Gram-based public layers |
| Public edits near Y | impossible on those frames; P-edits cap at 52; exchanges keep T_pub[Y,K] at 104 | Gram-based layer |
| Frame-empty dump | at least 2 S per port in exact toys | its toys (the general "rank >= m" sentence is false) |
| Post-map shape | 104 UP + 104 DOWN, 0 of 104 mergeable | final state of the Gram-based layer |
| Shared landing as rank packing | weight discount <= 1.57% | owned-carrier cleaning |
| R-before-F on the Gram-based layer | 0 legal pairs; 104 needed | its F |
| Flat composites, any M; real orthogonal P; Gaussian orthogonal P on the dot-0 pattern | >= 52 | flat mains, real ring |
| Windowed native with one owned register per crossing (this package) | 208 owned against 172.78 / 175.86 [R] | d = 0 by window swap, no helpers, X-Y contacts only; public side cannot close it |
| Fusing m consecutive Whitehead stages into one hosted stage (any grouping, rho = 1) | deficiency dim ker(W + I) = m - 1 for every grouping (proved: (I + 2 Lo) W = I + 2 Up, so W + I has rank 1; checked on 729 groupings); a hosted-form stage needs rank(C + I) >= p, so m - 1 forced crossings against m/2 for separate pairs: strictly worse for m >= 3, tied at m = 2 | rho = 1 family (Gram = sgn); any ring |
| Mixed rho = 1 roots (singles plus W stages) | never raise c\*; at c >= 0.5 every root with a W call loses | built symmetric roots; odd W counts unbuilt |
| Other port subgroups with an F2/Q gap; complex t factorisations; one skip shared across stages | none helps / gauge / impossible in the domain | P104 groups |
| A 13 x 8 block hybrid on P104 | not on P104; fails the caller rank unless the public layer mixes | see section 4 |

## 6. Open routes (odds are judgement [J], not computed)

1. **Gamma coupling on the Y registers after the bounce.** Bounce every port on a line with Y pre-content Z-mixed to (alpha/delta) y so the X rows come out exact and Y_t = gamma x is pure x; land the owned runs at small frames; then run a public Y-to-Y Gamma network while the Y registers rise. The landings sit at small frames and the mixing is not triangular, which avoids the two rank obstructions of the triangular hybrid. Unknown: (a) whether a frame-legal Y-to-Y network gives rank(beta I - gamma G Sigma) between 8 and 14 (the dot-1 clique forces >= 8); (b) the read cost of a dense row space (the Gram-based layer pays 56 for its read-high, descend, land layer); (c) peak owned registers across the bounce phase. If (a) and (b) land near 56 owned, the total is 56 to 90 against 145 to 173 allowed. Unbuilt. [J] about 3%.
2. **Shared landings for the beta crossing (the hybrid with the window swap).** One owned run serving many ports' crossings (Lemma M floor 1 per port; a pass needs at most 1.66 per port, so a saving of at least 35 of the 208 owned moves). The obstacle: a shared run carries the sum of the x's and leaves junk in other ports' pre-swap X registers; the check "the shadow is beta I" is necessary, not sufficient. An all-ports rank-9 landing sits at an increment of 0.096 to 0.115 per port-call, on the outer target. [J] about 5% for this route or the Gram-plus-window hybrid reaching 1.66 per port; 1 to 2% for the all-ports landing alone.
3. **Hybrid public layer: Gram coupling for the beta crossing, window swap for d.** The swap needs Y_t's pre-content to be disposable while Gram coupling lives in Y. Pass line: owned <= 172.8 / 175.9 per call. First exact step: W' = beta I - T[Y,X] for the chosen public schedule and its rank, before any owned run; with no mixing expect rank >= 52 and a floor of 137. [J] included in the 5% above.
4. **Non-swap d removal** (y leaving through an X that is not its swap partner, two-hop windows) could break the cycle obstruction of the swap family (windows must strictly grow along the swap permutation, so each m-segment costs about 2m). Untested. [J] under 2%.
5. **Real near-resonant non-flat public layer with the pattern minimum rank 8** (the algebra exists; no frame-legal schedule, price unmeasured). [J] about 2%.
6. **A W-stage native in which the hosted ports drop #6936's hosted R part and run plane 1 only, plus the prefix.** The size is unmeasured and no such word is on the frontier. [J] unknown.

## 7. Scope ledger

Replayed in this package: sha256 of all objects; both natives' exact endpoints and owned UP mass; the two roots and their controls; exact kappa and the invoice move; the joint caller replay; the 104-port native end to end (regeneration, two engines, structure, price, floor, budget lines, caller block, 100 mutants); the arithmetic of c\*, the budget lines and the pass lines from the ledger constants.

Quoted, not recomputed here: the kernel ledger (public 1702.405, owned 111.573, T = 11.426 / 14.513, the table of c\* and the free-native ceilings, the Gram-based layer's price and kappa); the hosted Whitehead word's second-engine, physical, ordinary and outer checks; the closed-route table; every odds figure.

Not built: a caller for the window native; the rho = 1 word (the root exists, no native).

Credit: Ali Romman (#5599), CubeJerry (#6912, #6914, #6916), unpaidmoon (#6930), icekylinx (#104).

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.
