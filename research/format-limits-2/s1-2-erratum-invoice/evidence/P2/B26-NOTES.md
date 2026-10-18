# B26: bit invoice calculus (exact word -> c map). VERDICT: PROVEN-MAP (gate passed). ship=false
Scope: #555 R439 word (pr head 65a6bc1, work/pr; research/e8-bit-p111), nine-stage chain (m=64, L=9, K=4, T=32). Files: gate.py (c from profile), reg.py (per-register climbs of the word via export_records), knobs.py/k2.py (all derivatives). Run: ../../venv/bin/python3 knobs.py (~1 min). Full verify.sh NOT run (heavy slots busy; not needed: EXPECTED.json carries the profile).

## Gate (PASSED)
c = root a of  sum_r (r n_r/(m W)) (m/r)^a + 32 m (sum n)/(1e16 W) m^a = 1  (moment.certify, bad=True), P = EXPECTED nine.profile {1:380448,2:400416,3:23040,4:27744,5:29376,6:17088,7:26496,42:288}, m=64, W=28416.
Result 0.001733052823330162099157209 = shipped 1733052823330162099157/1e24 (agrees to the 24-digit grid, rel 1.2e-22). Mass 1808352, deficit 10272.

## Chain: word -> c
1. W = 2 K v T = 256 v = 28416 (live data), PER WORD-SET; R never enters W (R<=4v only gates hosting). m = 1+7L = 64.
2. Local children per invocation = the forward replay's climbs (op 0 ranks) + 9 centre copies of rank 7 (cst 63). 288 = L*T invocations, each the same: H = {1:1321,2:1342,3:80,4:47,5:102,6:10,7:18}; local mass 8R+cst+14v = 5129. Registers: 111 sources (mass 7 each, patterns (1,2,2,1,1)x98,(3,2,1,1)x10,(1,2,4)x3), 111 targets (7 each: (2,5)x92,(1,6)x10,(7,)x9 = the 9 totals), 439 helpers (8 each, ALL width 8, 10 climb patterns).
3. Idle cover (fixed geometry, 2vT windows per type): ranks 14,28,42 (128v windows each) and 7 (192v). Whole helper residuals (width 8) are hosted: 14-window 1 slot, 28 -> 3, 42 -> 5; slots 4v=444 per (stage,replica). Leftovers: 14->6, 28->4, 42->2, plus the 5 free slots per stage-replica = ONE empty rank-42 window (288 r42 children, tight at R=439). Rebuilt P = 288*H + {2:13920,4:14208,6:14208,7:21312,42:288} EXACTLY.
4. Total mass = 288(cst+14v) + I(v) is independent of R; deficit = T(2KV - L cst) = 256v - 288 cst (=10272). Helpers are mass-neutral (8 local + 8 hosted cancel); only sources/targets/copies (cst) move mass. c rises with deficit, falls with mean ln(m/r).

## Knob table (exact, Decimal root, % of c; ALL 288 calls unless noted; one call = 1/288 of it)
| knob | exact dc | notes |
|---|---|---|
| 1 cst unit (copy 7->6; deficit +288) | +2.8017% (2nd unit +5.603%) | any child r->r-1 on a source/target/copy: 2.8017 (r7) .. 2.816 (r1); width irrelevant |
| lose 1 cst unit | -2.8011% | 2 units = -5.63% (the descent price) |
| whole source / target register (7 units) | +19.7% / +19.7% | just 7 units; not a move |
| one retained total (target (7,) + its copy, 14 units) | +39.3% | cst 63->56 |
| 1 port (v-1; src+tgt gone, W-256, idle -128 windows each) | -2.13..-2.16% (so +1 port at same cst = +2.15%) | break-even: +0.77 cst unit per added port; +1 cst/port = -0.65% |
| 1 helper removed (R-1), best idle repack | +0.085..0.114% | pattern (1,1,2,2,1,1) .114, (2,2,2,2) .101, (1,3,4) .085; free slot goes to a 14-window |
| same, narrow (slot stays in its original window) | +0.062..0.092% | |
| remove 2 / 5 / 10 helpers (best) | +0.238 / +0.694 / +1.398% | 5 free slots make a 2nd empty 42-window: superlinear |
| add 1 helper (R+1) | -0.166% | breaks the empty 42-window (r42 -> r8) |
| merge 2 unit climbs -> width 2 (all calls) | +0.0068% | 1+2->3 .0093, 2+2->4 .0135, 1+5->6 .0132 |
Largest per structural change: (1) cst unit +2.80%; (2) port +2.15% (cst-neutral); (3) one helper +0.06..0.11% (merge 0.007%). cst/descent are the only >=1% bit levers; ~25-45 helpers = 1 cst unit.

## Misprice check vs registered bit mechanisms
- Oct 11 rmdec "+2.70% c per cst unit": exact 2.80% (1.04x). OK.
- J24-C1 / ledger "descent = 2 cst units = -5.8..-6.3% c": exact -5.63% (1.03-1.12x). OK.
- Count ledger "0.047-0.125% c per register": exact 0.062-0.114% (narrow .062-.092). Within 1.3x. OK.
- B16 "ports -1% at cst 65": exact is -3.45% at cst +2/port (+2.15 -5.60) and -0.65% at +1; the "-1%" does not match either; the 63->65 reading is a ~3.5x gap (or the ledger meant +1 cst: 1.5x). Re-read B16 before reuse.
- NO >=2x misprice of a registered bit mechanism on the helper/cst/descent lines. Bit B8/B17 proxies stand.
## Escapes/limits
1. Hosting repack (best vs narrow) is a bound: stage-level window availability and the owner MIP are not rebuilt; the 5-free-slot structure at R439 is exact. 2. Per-register classes by climb pattern only (line/cell/keeper provenance not separated). 3. Port/helper knobs priced on the invoice, word not rebuilt. 4. #589 tuned word (c +0.0216%) not used; same chain, shifts knobs <0.1%. ship=false.
