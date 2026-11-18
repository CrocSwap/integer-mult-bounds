# CallerCost.lean: caller cost closed form, reproduction, single crossing, composition
Imports Mathlib only (no Nov15 deps).9 GB. 12 `#print axioms` within [propext, Classical.choice, Quot.sound]; no sorry, no native_decide.

## Model
- Histograms = lists of (rank,count). S = sum r*(T-P) (Sinv), D0 = sum (T-P) f(r), f r = r ln r (fL, FloorD0 convention). invoice c n L = caller + L*native (counts scaled), `invoice_S`, `invoice_D0` exact. In the pricer the number of calls L = nJ = k = a+b (stage count).
- Caller family C(a|b), g=8, 96 A ports x 4 thin queries, 8 B ports (a,b >= 2; Lean params a'=a-2, b'=b-2, k = a'+b'+4). T: ranks 8j+1, j<=arm (and 8k+1), 208 = 2*104 each; P: ranks 8j, 2<=j<=arm-1, plus (8: 384+16k, 1: 384, 9: 32).
- The code does NOT use a Z^4 over ln 2/3/5/7 form (it works in Decimal over all ranks up to 137, which involve many primes). Exact form in Lean: `D0_caller`, a finite sum of f over the ranks 8j+1 and 8j, minus (384+16k) f(8) + 32 f(9) (f(1)=0).

## Proved
- `reproduction`: C(8|9) = caller 6 7 equals the #7113 caller invoice (data lists dataT/dataP, transcribed from the pricer's invoice of the #7113 caller file) term for term as histograms (cnt equal at every rank), hence S and D0 equal (`caller89_S`, `caller89_D0`). S = 57728 (`S_data`). Data are transcribed; the Lean statement is about those lists.
- `S_caller`: S(caller) = 3408 k - 208. `S_invoice`: with calls = k, S = (3408 + S_n) k - 208. `S_7630`: S_n = -3312 gives 96 k - 208, and `S_7630_k17` gives 1424 (S' = 96, rho = 208 as in R1 sec 3).
- Single crossing (first-order proxy K = S/D0, S = sk - rho, D = Dc(k) + k d): `single_crossing`: for k1 <= k2, d <= d', K_d(k1) <= K_d(k2) implies K_d'(k1) <= K_d'(k2). `cheaper_native_lowers_k`: strict contrapositive, a cheaper native (d down) never favours a larger k. `crossing_value`: tie at d* = (S1 Dc2 - S2 Dc1)/(rho (k2-k1)). Convexity of C(k) not attempted (not clean: arm terms are sums of r ln r over unequal strides).
- `composition`: abstract caller class, caller floor Fc(calls) <= Dc, total native floor Fn <= Dn gives Fc(k) + k Fn <= invoice D0. `composition_helper`: with native D0 = helperD0 + rest, needs a cap rest >= -R on the mains/owned credits. `kappa_proxy_le`: S/D <= S/F.

## Statements false / imprecise
1. FALSE as written: "invoice D0 >= caller floor + calls * (helperD0 floor)". With the numbers of the caller-floor note (helper floor 9,928.76 per call as helper D0 on #7630, caller D0 270,813 = 666,499 - 395,686, 17 calls, invoice D0 391,295.63): 270,813 + 17*9,928.76 = 439,602 > 391,296 (`naive_composition_false`). Reason: the native's main/owned MOVEs are credits (negative D0, `rest_negative`: about -2,842 per call). FloorD0's floor is on helperD0 only. Corrected: `composition` with a floor on TOTAL native D0 per call, or `composition_helper` with an explicit credit cap R. A caller-floor statement needs one of these.
2. Sign slip in the caller-ceiling note, section 3: d/dd of the numerator S'D - SD' is +(kS' - S) = +rho (`stationarity_slope`), not -rho. The conclusion (cheaper native lowers k*) is unchanged.
3. Scope: monotonicity is for the proxy S/D0 (kappa ~ S/D), not the exact root kappa of F(t) = 0; the exact-kappa version is not proved here.
