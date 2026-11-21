# Open targets for the P104 lower-bound programme

Guidance for contributors; builds on the toolkit of PR #7852 (referred to as #7852). Each section gives the exact target,
the strongest partial result we have, and where the witness data and code live in this package. No kappa claim is made.
Labels: [P] proved on paper (Lean name where #7852 or `lean_extra/` has one), [C] computed exactly, [CONJ] conjecture.
Lane notes are in `notes/<lane>.md` (index: `notes/INDEX.md`); later corrections are in `CORRECTIONS.md`.

## (a) NET-D56 in drop form (the network side, D >= 56)
Target. For every legal network realising -I@Q96 (P104 labels), D >= 56, where D is the total descent (owned drop).
- [P Lean, #7852] NET8: with at most 8 gathering and 8 depositing nodes, D >= 56 for any carriers; level-cut identity; word -> network bridge (drop = owned descent).
- [P] DX cut (notes/nogain.md section 1): D >= sum_l rank M*_l over downward-crossing walks (equals 16 on the E8 network, which has level sum 0: so the plain level wall is FALSE, see CORRECTIONS).
- [P] Zero-drop contraction (nogain section 2): after contracting zero-drop nodes every walk crosses a level downward at its own node; counterexamples to D >= 56 would have at most 55 nodes.
- [P] DX-inv: D >= sum_l mu_l with mu_l <= rank M*_l <= |C_l| (nogain section 4a).
- [CONJ] JUNK-PAYS-inv: sum_{l=2..8} (8 - mu_l)_+ <= sum_l (|C_l| - mu_l) on every legal -I@Q96 network. It implies NET-D56. Plain-rank JUNK-PAYS was refuted as stated (notes/l2test.md) and repaired in the invariant form; 124 Gibbs evaluations on Z4 decoders found 0 violations of the plain-rank form [C, weak].
- [P] Carrier law (notes/ycarrier.md): D_call >= sum_l rank M_l^net, relay-blind; rigid content is uncarriable unless its span is a port hyperplane. So carriers save R only.
- Residual: some level with rank M_l <= 7, i.e. at least 9 gathering or 9 depositing descents with low-rank level slices (the >= 9-row regime of Wall56).
- Data/code: notes/nogain.md, notes/unify.md sections 9-12, notes/ycarrier.md; code/nogain, code/unify, code/ycarrier. ZIGZAG network (h=5, D=4, e=1; legal, level sum 4, own-price 4, budget-5 mass search: none): code/unify/zzcx.py, recorded output code/unify/evidence/zzcx.log.txt (the budget-6 run is long and was not repeated here).

## (b) R side (run cost R >= 56 per call)
Target. For every pinned run realising -I@Q96, R >= 56.
- [P] Chain law for multi-epoch class F and Chain Lemma A: in the rank-8 (E8) sector R >= 56 (notes/reuse96.md); Rendezvous Lemma A at Q96 for CF runs with rank-8 epoch factors (notes/carrier8.md). Carriers are free relays, not nodes.
- [P Lean, #7852] R >= mass for class F / P / carrier-tree runs.
- [C] CT-COVER is false over every field: a climb-sharing run with R = 2 < mass 3 (code/ctcover/ctsplit.py: pinned all-GTD run, R = 2, mass >= 3 over GF(2) and Q, run it from its own directory). So the R side needs one of:
  - ChainWall56@Q96: the minimum over climb-sharing (chain) decoders of -I@Q96 is >= 56 (stronger than Wall56); or
  - a 2-adic / Z4 tensor-rank bound for -I@Q96 reaching 56 (halving-law type).
- Open: factor rank >= 9 sector (same core as (a)); rendezvous K-jumps and public hot deliveries; cyclic junk loops outside class CF (none found in 18.6k runs [C]).
- [P] A relay-blind R-side cut is impossible (public wires rise with owned ascents in both time directions).
- Data/code: notes/reuse96.md, notes/carrier8.md, notes/ctcover.md, notes/r2test.md; code/reuse96, code/carrier8, code/ctcover, code/r2test.

## (c) Caller mid-k window (k = 5..71, Q = 0 and Q >= 1)
Target. For every legal caller word with k stages, chat(.99) < 128.891. Currently only closed for large k.
- [P] HP(k) = (208/k)[(k-2)(17^s - 16^s) + (8k+1)^s - 8^s k], s = .99 bounds chat for the Q = 0 model (n = 2k-2, MAINS, RC2); HP peaks at k = 13 (143.273) and decreases in k (notes/kasym.md). Lean: CallerHP in #7852; `CallerAsm` word form.
- [C, certs/] Full-LP exact duals (rows: sep, e, ones, ell, coord, shal, pfix, dyadic, RC, RC2): k = 72 gives 128.8500719 and k = 73 gives 128.6813251, both below the bar; k = 71 gives 129.0372595 (above). These are conditional LP bounds: RC2 is [P] (Lean rc2_pair), the other rows are paper-[P] (notes/scherk.md, notes/bilinear.md) and are not in Lean.
- [P Lean] Q >= 1 with T = Q thin columns (notes/thinq.md, notes/leanthin.md): closed form HQ2(k); [C certs/] exact certificates below the bar for every k = 77..100, 110, 120; k = 76 gives 129.0076 (above). Lean: CallerHPQ.valQ_lt for all k >= 77.
- Window laws: LEAF-CHANNEL d1 <= k + T (notes/tribuild.md); eigenspace laws E1/E2, IDLE LAW (nu_t >= 2 non-invariant events at every middle stage), COVER-CAP (#events containing S <= 2(k-|S|-1)) (notes/eigencap.md); SPARSE, TURAN, TRIPLE, RELAY-HALL, TWO-HUB SIGN FLATNESS (notes/intcaller.md, notes/maskk13.md, notes/mainplace.md). Exact integer program over role-type multiplicities with these laws: sup 143.1905 at k = 13, 129.0349 at k = 71, above the bar at every k <= 71 (integrality is worth <= 0.09).
- [CONJ SINGLE] (eigencap): valid-control numerics do not decide it; with E2/COVER-CAP/SPARSE/SINGLE the LP+IDLE value stays 130.07 (k5) .. 136.41 (k11): no k closes.
- Real words (data/q0_callers): legal tight Q = 0 words for k = 3..13 (ML chain, chain frames, C1) with chat from 113.84 (k4), peak 115.43 (k5), to 104.49 (k13), against HP 127.4..143.3: the type LP is loose by 13..39 on built words. The target is a law (or construction) between these.
- Q >= 1 and excess thins e = T - Q >= 1: direct sums give no fixed-k law for e >= 2 (notes/extrathin.md); the e = 1 TRIANGLE type-level witness is unbuildable for k >= 7 [P] (notes/tribuild.md). HQ2 for the e = 0 branch only.
- Tightness is needed: padding is false [P Lean CallerTightNeed; data/direct_sum]: 109 copies of C1 give chat 107.910089 > HP(327) = 107.902838. Open: a tightness-free Q = 0 law (per-component laws for e >= 2; notes/decomp.md, notes/tightpad.md).
- DECOMP (every non-tight Q = 0 frame with invertible K-blocks is a direct sum of tight frames) is FALSE [P Lean decomp_false, source in lean_extra/CallerDecomp.lean (not rebuilt here); code/decomp/dc1.py exact word, k3 n2].
- Repo-invoice vs cHatQ: cHatQ is only a lower bound of the repo invoice for words with a nonempty IDLE_ODD set (notes/schemacost.md): one-sided gap.
- Tooling: CERTKIT (#7829) certifies pricing of its packed data; binding the normalized role/record/J-contact sequence to the source word and instantiating legality (a source-identity theorem) is open — see #7864, which exhibits two one-field mutations with identical packed data.

## (d) Loose decoder rows
Target. Rule out price-<= 55 decoders among the B-linear class with loose rows (rows y in Z4^8).
- [P] Row centre formula: price = dim(U + n_y) - 1; loose order-4 rows have price dim U (notes/loose.md). Reductions leave exactly one open row type: EFFICIENT order-4 loose rows with B^-1 ybar not in Zbar16 (239 mod-2 classes, 11 Aut-orbits, at most 18 rows, each dim U >= 3 and |D| >= dim U + 1).
- [P] The F2 shadow relaxes the whole class.
- Tight sub-class (rows in Z16, any A side): budget 55 is UNSAT with a sound per-cube symmetry scheme, certified in #7852 (drat/). The first symmetry-breaking scheme had a gap: data/tight55_gap.
- Target: '+1 per generic row' (every generic loose row costs one more than its centre price).

## (e) General decoder wall
Target. Wall56: every half-integer decoder of -I@Q96 has C >= 56.
- [P+C] Linear class: C >= 56 for every half-integer linear decoder, equality only for fully tight 8-row decoders; rho_A, rho_B >= 28 (notes/linear56.md). Linear rows never have price <= 6, so the danger is non-linear rows whose one-side support spans a codim-2 subspace of F2^9.
- [CONJ] double56: rho_A + rho_B >= 56 (the conjecture implies m4(P104) >= 56). Proved: isotropic-pair lemma (reduces to the rank of the tau-form, tight at E8) and clique theorem (rho_A + rho_B >= n on tau-trivial label sets such as the P104 frames) (notes/double56.md).
- [CONJ] tau48 (notes/tau48.md): not proved, no counterexample; three obstructions and one new tight family. Arf/Brown invariants of P104 computed exactly (notes/arf.md): Brown = 7 mod 8, no invariant proof.
- [P] Carry polynomial identity and rank bound for 2^e denominators (notes/den4.md); graded Smith floors HS64 6, E7 7, P104 8; half-spin quarter decoder (C = 48): forced bounds 38 (canonical gauge) and 42 (gauge maximum).
- Open: the 8-row mod-4 floor 28 -> 42 -> 56; rule out rows of price <= 6.
