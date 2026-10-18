# B3R: rank-8 SSS (hourglass) word, priced. VERDICT: LOCAL-PRICE (word built + exact; engine pricing ill-posed at fixed cover). ship=false

Scope: #623 ck provider word content map M (112x112, exact replay of ck-step7-cold_end A+B+cut), moment engine complex-allcold/engines/moment.py, m=73, W=7168. Files here: m.py hr.py fit.py sss.py build.py price.py price2.py clmb.py (B3 tools copied, not edited).

## Gate (passed, not killed)
Shipped word climb mass (monotone frame replay, clmb.py): A+B+cut 4932 (3364 climbs, widths 1:2420 2:536 3:200 4:200 5:8); with cleanup to FULL 6186. 716 registers.
SSS word: 8 helpers, mass 1976 (0.32x of 6186). Gate ratio << 1.15 -> proceed.

## Structure found (key fact)
- M has Hankel rank <=8 at every cut, and EXACTLY: for every row i, M[i,j<i] = O_i . R_j and M[i,j>i] = P_i . R_j with R_j the integer D8 root vectors (root_lines), O_i,P_i 8-vectors with ~3 nonzeros, entries in {0,+-1/8,+-1/4,+-3/8,+-1/2} (a few early-row pinv artifacts, rationalised to /64 with exact check), D = diag(+-1/2). So SSS order 8 with A_k = I, B_j = R_j (entries 0,+-1): no mixing generators, no LR basis change needed (state basis already integer, minimal-span LR form irrelevant).
- Word (sss.py/build.py): 8 centre helpers c; sweep i: y_i += (O_i-P_i).c, then c += R_i u_i; second pass y_i += P_i.c (c=total) and y_i += (D_i - P_i.R_i) u_i; uncompute c. 1372 adds. EXACT replay: max err 0.0, centres return to 0, sources untouched.
- Frames (ports from word, minimal union frames, all regs end FULL=9): climbs 414, mass 1976, widths {1:152 2:20 3:19 4:6 5:12 6:18 7:42 8:64 9:81}. Centres all FULL immediately (ports of any 9 sources span F2^9). Frame is NOT the wall: mass is just the mandatory end-climb floor (sources 8, targets 9, helpers 9).
- Not done: transposed orientation (Tellegen transpose of the op list gives M^T, itself SSS-8; trivial but not emitted), local-program events (wrappers/centre events), cleanup-phase refactor, owner-map MIP.

## Pricing (engine facts, the real finding)
- check_moment/invoice assert m*W - sum(r*n) == deficit (2560): paid climb mass is a FORCED COVER of the live families, not a cost to minimise. Helpers are the rank SUPPLIERS (4428 of 6186 mass/call). b solves sum_r p_r (m/r)^a = 1 with p_r = r n_r/(mW): b ~ (deficit fraction)/(mass-weighted mean ln(m/r)). Wider climbs are cheaper per unit mass.
- SSS x72 at W=7168: mass 142,272 vs 520,704 required (27%): deficit 380,992 != 2560; certify() fails its bracket (root a>0.003; a=0.51 unbracketed) -> the word cannot occupy the shipped cover; price undefined/invalid. Thus 'fewer helpers' is not a gain on this metric by itself.
- Shape-only bounds (same total mass 520,704, counts rescaled, NOT realizable as stated): shipped profile b=0.0016382 (reproduced); SSS-shaped profile b=0.0020048 (+22%); shipped word with every register climbing once (max coalescing) b=0.0022888 (+40%). Mean ln(m/r): shipped 2.99, SSS 2.44.
  Caveat: these require supplying the same mass in wide climbs; legality of coarse frames (PR583 frame_coalesce / frame_regroup already exploit it) and of padding mass is unverified. Treat as an upper-bound lens, not a result. No incremental verified gain found.

## Verdict: LOCAL-PRICE
Scope: fixed-W (7168), fixed-deficit cover, word-level profile; SSS-8 word is valid/exact but supplies 27% of required cover mass, so it prices as infeasible on the shipped cover. Not proven that no SSS-based cover exists.
Escapes (>=3):
1. Re-solve the cover: shrink W (live) so m*W - mass = deficit with the SSS profile (new geometry, fewer data families per call or more calls per word); needs owner/window MIP, ~hours.
2. Mass padding: supply the missing ~5256 mass/call in few WIDE climbs (cold dummy/idle children climbing 0->9, or hosted-residual banks) -> engine says wide mass is cheaper (shape bound b up to 0.0020). Needs legality check of idle/dummy climbs vs owner charts.
3. Hybrid: keep shipped K-triangle helpers for mass/ownership but replace pair/quad helper network by SSS centres in the A/B body; or merge width-1 climbs in the shipped word toward the max-coalescing profile (shape bound +40%): check what frame legality forbids beyond PR583.
4. Different cover interpretation of deficit (2560 fixed constant in emit_allcold.py): derive it; if deficit can scale with geometry, fewer climbs is a gain.
Rescue check (not run, ~40 min): take shipped ck word, compute the max legal coarsening of frames per register (union frames at first touch subject to the owner/dirt audit in audit_allcold.py) and rerun price2.py on the real resulting profile; if b rises >=1% with audits passing, reopen escape 3; also determine in emit_allcold.py/audit_allcold.py why deficit==2560.
