# Composition and proof boundary

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. Apache-2.0.

This package stacks three independent levers on the R740 bit word of PR #443/#444: the **stage count** of the bit supplier
(nine to eleven, section 2-4), **cross-copy idle-axis hosting** of PR #448 (section 5), and, in its default word, **target
mixing** (section 6). The unmixed word is verified as well (`stacked_unmixed`). Everything else is inherited and run
unchanged: PR #443's local checks, PR #448's complex word and its cross-copy hosting (the complex supplier stays at nine
stages and does not bind), PR #442's hosting lemma, the moment engines and the outer assembly.

## 1. What is unchanged

- **Local word.** PR #443's R740 word (R = 740, 9 retained totals of rank 8, entrance rank 138). Its legality, formal
  columns, source spans, Gram and negative controls run unchanged in `verify.sh` of the parent.
- **Complex supplier.** PR #448's cross-copy hosted complex word (s = 9, m = 73, b = 718766148669433/(5 10^17) = 1.437532e-3),
  reconstructed by running PR #448's verifier. It does not bind: the bit supplier does.
- **Hosting lemmas** (PR #442, `../idle-axis-hosting/PROOF.md` sections 1-2; PR #448, `../cross-copy-hosting/PROOF.md` section 2), the engines `moment.py`,
  `base_two_moment.py`, `outer.py`, and the strict 47-inequality outer assembly.

## 2. The S-stage compressed layout (S = 2K+1)

PR #386 lifts the local word into windows of V = Q^8 + (Q^7)^(S-1), m = 8 + 7(S-1) = 1 + 7S, with E_s the first s
exterior 7-blocks. At stage s it replaces U by U + E_s. Both ends of every local transition contain the same E_s, so it
cancels exactly: the child projector, its rank and its address operator D_U are unchanged. That argument does not use
S. Port routes rho_(s,q) = [[P_q, A_q], [A_q^T, 0]] act on the local block and exterior block s, for s = 1..S-1, and
depend on s only through the position of that block.

`code/geometry_k.py` is `geometry.py` of PR #386 with the stage count as a parameter (default 9; `--no-timing` omits
the wall-clock field). It re-derives all 120 port isometries, checks the four endpoint conjugations for every port,
the elementary factorisation of every route (at most 77 factors, denominators 1, 2 and 4, so no new odd prime), the
240 exact bit endpoint operators, the nested idle ranks, and (when 8 divides m) the whole-block bank slots.
- At S = 9 its output equals PR #386's `GEOMETRY.json` field for field (checked in `verify.py`, apart from `seconds`).
- At S = 11: m = 78, 1,320 route checks (120 ports x 11 stages), the same 77 factors and denominators. Since 8 does not
  divide 78 there are no bank slots; none are needed (section 5).

## 3. The K-pair recipe

Use K data pairs (X_j, Y_j). Start with F_0; for j = 0..K-1 apply B_j, insert two shears when j < K-1, apply F_j, undo
them; after all stages apply the K-1 closing bridges in reverse; finish with the signed exchange. That is
3(K-1) twin bridges, 6(K-1) shears (18 at K = 4, **24 at K = 5**), 2K+1 local invocations (**11**).

- `code/global_k.py` (from PR #443's `global_kernel.py`) replays the complete signed integer 2K x 2K scalar matrix, which
  is the identity, and rejects the omission of each individual shear (24 controls at K = 5).
- It replays all independent columns of the unbanked global state (2KV + S R = 9,340 at K = 5), all restored after the
  exchange, with chronological lowering of every local program (the same events as the parent, 217,019 emitted).
- The C++ formal-column checker of PR #381 (`columns_k.cpp`, `-DKPAIRS=5`) is built with the parent's flags and run on
  the parent's cohort records: 1,940 physical formal columns (10 V + R), 24 twin-bridge additions x 120, 11 stages,
  all 24 omitted-bridge controls rejected, payload prefix 65 bits.
- `verify.py` also checks that `global_k.py` rejects the nine-stage geometry when asked for eleven stages.

## 4. Idle increments and the deficit

A pair at level l has advanced l windows; one window costs a rank-7 block. The pairs are brought to the active level
by idle increments, exactly as in PR #386, with K = 5:

| stage | pair | from -> to | rank |
| --- | --- | --- | --- |
| 1, 3, 5, 7 | 1, 2, 3, 4 | -1 -> 2j-1 | 14, 28, 42, 56 |
| 2, 4, 6, 8 | 1, 2, 3, 4 | 2j-1 -> 2j | 7 each |
| 10 (terminal) | 0, 1, 2, 3, 4 | 2j+2 -> 10 | 56, 42, 28, 14, 0 |

The sum per data member is 7 (K-1) S = 308 (189 at S = 9). With V = 120 ports, T replicas, and 9 copies of rank 8 per
invocation, the rank deficit is exactly D = m W - (rank mass) = T (2KV - 72 S): 312 T at S = 9 and **408 T at S = 11**.
Both emitters assert it from the emitted profile, so it is a computed identity, not a formula that is trusted.

## 5. Cross-copy hosting of every residual

PR #442 moves whole dirty helper residuals from bank streams onto pending coordinates of idle data families, under the
window condition (the family is untouched between the hosting invocation and its advance). PR #448 lets a residual lie
across the pending sets of **two copies of the same idle child**: with P = P1 + P2, D_P1 D_P2 = D_P writes the dirty
invocation's factor on the residual as a product of a factor on each family, each is moved to the child exactly as in
#442 section 2 (the window is a property of the pair, not of the copy), and each copy's remainder is exact; one further
route factor per helper selector is charged (three instead of #442's two). That is PR #448's lemma and review point
(`../cross-copy-hosting/PROOF.md` section 2); it is used here unchanged.

`emit_tape_k.py` is PR #448's `bit_split.py` for any odd stage count: the pending sets of a child's 240 copies are laid
into a tape, residuals are placed contiguously widest first, and a residual that straddles a copy boundary becomes a
two-piece slot (`hosted-split`). With the tape rule the copies of a child are absorbed in order: x copies are emptied,
one copy is partly used, and the others are untouched.
- **Selection.** `hosting_k.solve_tape` maximises the exact paid-cost saving (r ln(m/r), concave) instead of PR #448's
  first-order proxy; the feasible set is PR #448's (counts n(child, stage, width) with capacity copies x r). With every
  residual hosted there is no bank tiling constraint. `--discover-check` recomputes the frozen selection.
- **Capacity grows with S.** Per replica, the pending coordinates are 45,360 against 52,038 residual coordinates at S = 9
  (PR #448: 46,160 of 53,784 residuals hosted, 8,592 live), and **73,920 against 63,602 at S = 11**, so all 8,140
  residuals (1,807 of them split) are hosted, no bank remains and the stock is the data alone (1,200 families).
- **Replicas.** T = 1: replicas exist in PR #443/#448 only to fill width-64 banks, and the price is independent of T.

## 6. Target mixing: the bit-label conjugation lemma (principal review point)

The same statement is in `BIT-LABEL-LEMMA.md` (verbatim from the mixing hand-off). This section concerns only the default word. It is the principal review point of this package, and it extends PR #425's
lemma (which #425 itself flags in the same way) from complex target packets to the F2 bit word. The unmixed variant
(`unmixed_d3`, `unmixed_d2` in `verify.py`) does not use it.

**Construction** (`code/mix_target.py`, deterministic). In the B phase of PR #443's R740 word the targets only receive
helper registers, and helpers are not modified. Each target t climbs a nested chain of frames 0 < T1 < ... < t-perp and
receives registers at those frames. A pi-coset partner pair (t, w) of a Hamming block receives the same three
registers D4(c), M(p5) and N, at the same frames of dimensions 4, 5 and 6; the dimension-6 frame is t-perp meet w-perp.
`mix_target.py` selects a receiver u and a donor w that share a frame G of w's chain, such that the F2 sum of the
registers u receives at frames inside G equals the F2 sum that w receives there, and all of u's later frames contain G.
The selection is a deterministic greedy pass by climb-cost saving; donors keep their chains and there are no cycles.
For each receiver, three places change:
1. **D phase (frame 0):** y_u += y_w after w's own D gates (the frame-0 preconditioner);
2. **centre scatter:** scatter_u := scatter_u xor scatter_w;
3. **B phase:** u's deliveries at frames inside G are dropped, and y_u += y_w is added at G, after w's deliveries inside G
   and before any of w's deliveries above G. B is re-listed by frame dimension (legal: helpers are constant in B).

Sources, helpers, R, every start and final frame and phases A and C are byte-identical to the parent. 46 receivers (42
mix at dimension 6, 4 at dimension 5): a climb 0 -> 4 -> 5 -> 6 (or 0 -> 5 -> 6) becomes the single step 0 -> 6, and the
local paid profile {1:2530, 2:1008, 3:280, 4:347, 5:118, 7:14, 8:9} becomes {1:2460, 2:1012, 3:276, 4:315, 5:108, 6:42,
7:14, 8:9}. Rank mass is unchanged (every target still climbs 0 -> 7); the target climb falls by 185.97 per invocation
(local cost 25798.6 -> 25612.7, -0.72%).

**Scalar identity.** Let y_w(tau) be the content of y_w when the mix happens: y_w0 + D_w s + P_w + scatter_w(x) + X_w(G),
with y_w0 the input, D_w s w's frame-0 dirt compensation, P_w w's own preconditioner if w is itself a receiver, and X_w(G)
the F2 sum of the registers w receives at frames inside G. The preconditioner adds y_w0 + D_w s + P_w to y_u at frame 0,
the corrected scatter adds scatter_w, and the mix adds y_w(tau). The terms cancel in pairs, and X_w(G) = X_u(G) replaces
exactly the deliveries u dropped, so every receiver ends with the parent's value y_u0 + x_u. All other registers are
unaffected.

**Lemma M (bit labels).** PR #425 (section 3, "Why the scalar argument lifts") argues for complex labels: fix a
canonical label operator L(F) for each frame F; a climb A -> B acts as L(B) L(A)^-1; a scalar addition between two
registers that share the current label F commutes with their common L(F); by induction through the stream, the whole
program is the block-diagonal conjugation of its scalar matrix by the current labels. The argument never uses the roles of
the registers. For the bit supplier let the label at frame F act on every register stream by the same operator Lambda_F,
the coordinate-projector form D_P of PR #386/#434 used for climbs and idle advances. Then an F2 addition y_u += y_w
between two target streams at a common frame G commutes with Lambda_G (+) Lambda_G, so the complete local program equals
the conjugation of its scalar matrix by the start and final labels, exactly as for the helper-to-helper and
helper-to-target additions the bit words already use.

*Proof sketch.* On the two streams the addition is the block matrix [[I, I], [0, I]] (target u's row gains w). Both
streams carry the same Lambda_G, so (Lambda_G + Lambda_G) [[I, I], [0, I]] = [[I, I], [0, I]] (Lambda_G + Lambda_G). The
induction over the event stream is the inherited one; the frame-0 preconditioner is a common-label addition at frame 0.

The lemma uses only that both operands are at the same frame, which every checker enforces. What is new for the bit
supplier is that a **target is used as an operand**. The inherited bit checkers allow it: `e8core` exempts target operands
from its source-span test, and the PR #266-lineage cohort legality counts it as an ordinary common-frame ADD.
`code/mix_check.py` adds a stricter test: the integer x-support of each operand target, from its deliveries, lies in the
gate frame (92 target operands, 0 violations).

**What is not proved**: that the physical bit label is a single operator per frame acting identically on target streams
and helper streams. The parent's helper-to-target deliveries assume this, but it is stated nowhere for a target used as an
operand. This is the principal review point of this package.

**What is checked** (all exact): `e8core.replay` on all 980 formal columns including dirt and target inputs; nesting of
every frame chain; D at frame 0 and y at frame 0 at the scatter; the defining identity of the word on independent
bit-vector columns; integer source spans of non-target operands; the strict target-operand span check above; on the mixed
records, the C++ cohort legality, the five-stage and K = 5 formal-column checkers, `mutate_records` (6 of 6) and the Gram
check of all 944 frames. Four mutants must each be rejected: no preconditioner, no scatter fix, mixing at the full frame,
mixing omitted.

**Composition.** Mixing keeps R, the start frames and therefore every helper residual width. The hosting problem depends only
on the schedule and the widths, so the frozen selection applies unchanged; the hosted audit re-derives every window and
owner. Target additions occur only inside the local invocation of the active pair, so they touch neither a hosted family's
untouched window nor any bank.

## 7. Finite invoice at S = 11

`code/assemble_k.py` is PR #448's assembly (itself PR #442's) with L, K, T, m, the deficit and the halving depth as
parameters.
- **Halving.** The largest child after hosting is 56 (184 untouched copies of the rank-56 children): 2 * 56^2 = 6,272 >
  78^2 = 6,084, but 2 * 56^3 = 351,232 < 78^3 = 474,552, so three halving levels are used, as in PR #445 and #447. The
  finite coefficient has 153 bits, its cube times (E+1)^3 has 504 bits (511 for the mixed word), both within the 512 bits
  charged.
- **Row allowance.** The bit row is d (m^2 + 1) + 10,161 = 28,416 at m = 78 and d = 3 (18,355 at m = 64, d = 2), above the
  inherited 20,161, which was itself chosen as 10,000 + 9,909 + 252. The outer assembly needs only 10^6 - (51/25) A > 0
  and passes with A = max(20,161, bit row, complex row). (PR #445 keeps 20,161 with an elementary orthogonal-cover count;
  that argument is not used here.)
- **Prefix.** 2^24 c_f^6 c_b^5 has 153 bits (155 for the mixed word), charged 192.
- **Routes.** Every helper route is charged 77 factors, 144 for the residual isometry, and 3 hosting factors (slot
  permutation, idle basis U_q, cross-copy split), per helper selector.
- **Complex.** PR #448's complex supplier is priced by the same code; b = 1.4375e-3 is 6.5% above the bit
  saving c = 1.3496e-3, so the bit supplier binds.

## 8. The regression anchors

`verify.py` checks
- at S = 9 with 32 replicas, `GEOMETRY.json` of PR #386 (all fields but `seconds`) and PR #443's parent template byte for
  byte (`global_k.py`), with PR #443's `GLOBAL.json` except `seconds`;
- PR #448's bit template byte for byte, regenerated from PR #434's R747 bit template and PR #448's frozen selection by
  `emit_tape_k.py` (GLOBAL.json except `seconds`), the tape audit on it, and PR #448's result recomputed by `assemble_k.py`
  (`--residual-isometry 0 --route-extra 3`): kappa 1330733966732373/10^18, both lower endpoints and both template hashes
  equal PR #448's `EXPECTED.json`.

## 9. Scope

This is a conditional finite certificate. The compressed windows at 11 stages (m = 78) are checked finitely, as the
nine-stage windows were, not proved: the claim that the window bound m = 1 + S (h - 1) is attained at S = 11 is the same
inherited interface extended by two stages, with every projector, route, schedule and ownership checked. The cross-copy
hosting lemma of PR #448 and the hosting lemma of PR #442 are applied to every residual. The target-mixing lemma (section
6) is the principal new review point. No Lean proof and no unconditional integer-multiplication theorem is claimed. The
all-size compiler, restored-work, tape/common-grid, precision and analytic interfaces and the correlated dirty-bank
interface remain inherited assumptions.
