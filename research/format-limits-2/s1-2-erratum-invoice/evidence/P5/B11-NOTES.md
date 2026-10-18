# B11: climb-width economics, legal frame coarsening. VERDICT: LOCAL-PRICE (fast kill gate hit; gain 0.0%). ship=false

Scope: the shipped #623 providers ck (8 calls) and jp8 (64 calls), CANONICAL-WORD.json.gz of r40/base/work/k492b/{ck,jp8}-local, A+B+tail op frames, fixed scalar word, fixed op ORDER, fixed start/final/centre frames. Tools in work/ (coarse.py opt.py opt3.py upper.py hist*.py lower.py).

## Model (all from the checkers, hpe_emit_local.py / gk_word.profile / hpe_audit_local.py)
A climb is paid only when a register's frame changes between touches. Legal frame assignment = per-register monotone nested chain, ONE common frame per ADD, start <= first, last <= final (targets end at perp(port), dim 8; U-ended helpers at U), centre frame == cf at the A/B boundary, tail/cleanup as given. Profile reproduced exactly: ck {1:2596,2:552,3:304,4:160,5:70,6:8,8:8} (3698 climbs, mass 5714), jp8 {1:2512,2:400,3:448,4:160,5:70,6:8,8:8}. Frame choice does not change mass, only shape (b ~ 1/mass-weighted ln(m/r); S=sum r ln r is the objective).

## Gate
(a) Bounds per op: lazy lower bound G (join of start frames along chains) and eager upper bound U (caps, reverse closure). F0(shipped) == G on 4201/4507 (ck) and 3837/4471 (jp8) ops; G==U (zero freedom) on 3581/4507 and 3133/4471. Only ~926 / 1338 ops have any slack.
 - All-eager (U) assignment: ck climbs 3972, jp8 3972; global b ratio 0.9695 (WORSE, -3.0%). All-lazy (G): 3860 climbs, worse.
 - Hill-climb with raise-cascades (opt.py): 28 of 43k candidate merges even feasible, 0 improving.
 - SA with bidirectional cascade moves inside [G,U] (opt3.py), ck and jp8, T0 0.3 and 1.0, 6M moves each: best dS = 0 for all four runs. Shipped frames are a local optimum for this neighbourhood: 0.0% b (<0.3% gate).
(b) Blocking histogram for the 2081 (ck) / 1993 (jp8) unit mid-chain climbs (no cheaper merge): transitive cap via partner chain 77.5%, direct target perp(port) cap 17.7-18.5%, lowerable 3.2-3.5% (SA shows still no gain), raisable 0.7%, U-end helper 0.5%, centre cf 0.2%. One SPEC rule family (common frame at ADD + monotone chain + target-end frame perp(port) + support from source start frames) blocks >= 96%. => KILL criteria met (gain < 0.3% and rule share >= 90%). Cold-end widths / FULL-lock / owner charts are NOT the binding rules; the audit_allcold owner/dirt layer is never reached.
(c) Deficit: emit_allcold.py asserts M*DATA - sum(paid) == 2560 literal (also assemble.py, invoice_allcold.py, audit_allcold.py). paid = per-call local profiles (64 jp8 + 8 ck) + idle remainders (rank-hosted). It is a literal re-pinned constant: invariant under mass-conserving coarsening, but any change of local mass changes it by 72 per unit per call (and breaks the pins). Not free to scale.

## Escape 2, mass padding
Dummy wide climbs would ADD mass; the engine needs mass = mW - deficit exactly (assertion), so dummy mass must displace real mass, which is a forced cover. Arithmetic upper bound if it could: moving 1% of unit-climb mass into width-9 climbs gives only +0.26% b (so +1% needs about 4% of unit mass). Adding mass beyond the cover lowers the deficit and the bound. Not legal and not useful.

## Verdict: LOCAL-PRICE. Not proven globally; scope above (fixed op order).
Escapes (>=3):
1. Reorder gates: commuting adds (dst1!=src2, dst2!=src1) in A/B change the chains; gate_move_coalesce used only 2 moves. Search op ORDER jointly with frames (per order the optimal F needs a DP/ILP). Largest untested lever.
2. Change target end frame (perp(port), dim 8) or the ports/geometry: targets' cap is the root cap (about 96% of blocks); a geometry with looser target ends would unlock coarsening.
3. Pre-climb sources (1->9 at start, 112 width-8 climbs, same mass) needs source ops to avoid target-touching ops (cap perp(p_t)); would need a K-triangle schedule where source reads precede target caps.
4. Re-derive the owner/idle layer so deficit grows with geometry (not done).
Rescue check (not run): SA over adjacent commuting swaps in A/B/tail with the opt3 frame SA as inner loop; if S gain >= ~170/word-equivalent (+1% b) reopen escape 1.
Queued CPU jobs: none (gate killed). Shape bounds +22%/+40% from B3R are unreachable by frame choice at fixed order.

## Rescue-check job (queued)
Jobs B11_reorder_ck, B11_reorder_jp8 (cpuq/pending; logs jobs/B11_reorder_*.log). work/reorder.py: SA over adjacent commuting swaps within A/B/tail (adds commute iff dst1!=src2 and dst2!=src1; B_K-legality NOT separately modelled; cleanup would need regeneration) plus local frame moves; objective S, price = float root b. Log lines: "HH:MM:SS NEWBEST b <b> ratio <b/b0> S .. swaps .. it .." and final "END b .. ratio ..". Best (order, frames, profile, b) pickled to work/reorder_{ck,jp8}.pkl. 90 s test: ratio 1.0 (no gain yet). Only a ratio >1 reopens escape 1 (then audit and exact-replay required).
