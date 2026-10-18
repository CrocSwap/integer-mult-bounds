# B15: invoice calculus (exact word -> b map). VERDICT: PROVEN-MAP (gate passed). ship=false
Scope: #626 (pr626 extracted to ./pr626), providers ck(8 calls)/jp8(64) CANONICAL-WORD replay (B11 coarse.py + reg.py), profile model of check_moment. Tools: reg.py (per-register climbs), calc.py (gate), knobs.py (all derivatives). Run: ../../venv/bin/python3 knobs.py (~2 min).

## Gate (PASSED, exact)
b(#626) = 0.00163820671230808686 -> kappa=b/(1+b)=0.001635527380375392 = PR626 README to all 16 digits. #623 profile (12:1,21:1) gives kappa 0.001635490664920455 (exact). Built from the words alone, no PLAN profile.

## Chain: word -> b (all verified numerically)
1. v=112, h=9, m=73=8h+1, DATA=live=W=8*T*v=7168 (K=4 blocks x T=8 replicas x 2v). W is PER WORD-SET (all 72 calls, one cover), NOT 4v+R: R never enters W in the complex invoice (physical=W+R+8+2 only enters finite inequalities). B12's "W=4v+R" is the five-stage moment.py price(), not this engine.
2. Per-register paid mass (climb widths of the monotone frame replay): source 8 (1,1,1,5), target 8 (end perp(port) dim 8), helper = EXACTLY its residual width w=|U|-|E| (4/5/7/8/9), centre = 9 + 8 (cut climb 8) = 17 (centres are 8 of the R=492 helper columns).
3. Local mass per call L = sum(w_helpers) + 1856, 1856 = 2v*8 + 64 (64 = 8 centres x cut 8; =16v+64). ck: 5714 = 3858+1856; jp8: 5758 = 3902+1856 (checked).
4. Idle cover: fixed geometry I = 72*48*v = 387072 (48-wide idle children). Hosted helper residuals Hz = sum_w*calls (280592) occupy windows, leftover = I - Hz (2215 x 48 + 123 x 1 + 1 x 37 in #626) is paid as children.
5. Total mass = L + I - Hz = 72*(16v+64) + 72*48v = ... = m*W - deficit; deficit = 64v - 4608 = 2560 (derived, linear in v; NOT a free literal: it is the constant L-Hz=1856 per call). So deficit is fixed by 3, and total mass 520704 is invariant under helper changes.
6. b = root of F(a)=sum_r (r n_r/(mW)) (m/r)^a = 1 over H = 64*jp8 + 8*ck local children + idle leftovers; kappa = b/(1+b). b ~ (deficit/(mW))/mean ln(m/r): MORE deficit = bigger b; wider climbs cheaper.

## Knob map (exact finite differences, Decimal root; % of b)
| knob | exact dB | structural move | register status |
|---|---|---|---|
| remove 1 centre (cut rank 7) | +22.60% (add one: -22.56%) | local -17, host -9, deficit +576 | rank-8 cut forced (B3/B10); "more centres" closed |
| 1 cst unit (L-Hz 1856->1855: -1 mass/call) | +2.81% (+2.82% as one unit climb/call) | e.g. cut climb 8->7, source end FULL->8, target end 8->7, one register 1 unit lower | decoder cst 72->71 registered (+2.7%); register-level END-FRAME form NOT registered (below) |
| v-1 (112->111 columns, geometry) | -2.15% (deficit 2496) | not a move: v is the problem size | n/a |
| remove 1 w9 helper, ALL 72 calls (jp8 +ck) | +0.068% narrow idle (freed w returns as one w-child); +0.137% if freed w merges into 48-chunks | mass-conserving: its climbs leave, w freed in host window | count ledger 0.143% = best case; B2 0.043% gross is BELOW even narrow exact (B2 probably includes read-climb loss) |
| remove 1 helper by width, jp8 only (64 calls), narrow / 48-merge | w9 0.060/0.122; w8 0.043/0.102; w7 0.035/0.090; w5 0.027/0.074; w4 (cold unit) 0.023/0.064 | same | ck adds ~13% on top (8 calls) |
| merge 2 unit climbs -> 1 width-2 (72 calls) | +0.0064% (jp8-only 0.0057) | frame coarsening | B11: blocked 96% |
| merge r unit -> width r, per unit absorbed | r=3 .0051, 4 .0064, 5 .0074, 9 .0102 % | | |
| all jp8 unit pairs merged (bound) | +8.8% | | B11 SA: 0% legal |
| mass unit moved width r->48, per 1000 units | r=1 .249%, 2 .204, 3 .178, 4 .159, 5 .145, 8 .115 | | price of any reshaping |
| helper end FULL->d (w9, jp8): d=8/7/6/5/4 | narrow -.003/-.001/+.004/+.007/+.014; 48-merge +.013/+.025/+.038/+.048/+.060 | trailing climbs dropped, hosted width freed equally (deficit unchanged) | cold/hyperplane ends already in word (22+34) |

## Reading
- Helpers are cheap per unit, the CONSTANT is expensive: one mass unit/call in the 1856 is worth 2.8% b = 20-40 helpers. The 1856 is src 8 x 112 + tgt 8 x 112 + 64 centre-cut mass. Helper changes are mass-neutral (climb mass = hosted width); only END FRAMES of non-hosted registers (sources, targets, centres) change the deficit.
- Count-ledger 0.143%/helper is the optimistic 48-merge bound; realistic narrow = 0.068% (w9, all calls); w4-5 helpers 0.02-0.03%. B2's 0.043% is within a factor 1.6 of narrow: consistent, not contradicted.
- Sources/targets/centres are 224*8+136 = 1928 mass per call and carry no hosting counterpart: each unit saved is +2.8% b.

## Unregistered >=1% path (knowledge, UNVERIFIED legality)
Source END frame below FULL (or target below perp(port) dim 8): each saved unit on ONE register (all 72 calls) = +2.81% exactly, 112 sources/targets available. Not in BLOCKED-IDEAS (grep: sources end at FULL appears only as assumption (f) in archive/r13/G_walls, and as taint W4 at r13/Y_synergy). Likely blocker: sources/targets must be restored to the exact frame the next stage reads (taint W4); helpers escape via hyperplane/cold ends because they carry no data. Rescue check (~30 min): for ONE source register, test whether the final climb 4->9 can stop at a hyperplane U that contains the next role's first frame (Y_synergy rule: end(role1) inside U(first event role2)).
## Escapes/limits
1. Freed-w merge fraction (narrow vs 48) is owner-MIP dependent; reported both. 2. face/key/host helper classes of J21-K ledger not separable from register roles here; classes given by width. 3. v and centre knobs are priced on the invoice only (word not rebuilt). ship=false.
