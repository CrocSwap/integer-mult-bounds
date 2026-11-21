# PRICEH (Nov 20, Sonnet, Lean + certificates). General-h price lemma for rung_port.
Files: gen.py (LP search + exact Fractions), verify.py (independent exact check, verify.log), mol_h{4..19}.json, genlean.py, budget.py (budget.log), buildall.sh/log.
Lean (Nov15/): PriceH.lean (HCall, MolData, abel, price_h), PriceHRung.lean (rung_port_h), PriceHI{4..15}.lean (md_h by decide+kernel), PriceHMain.lean (rung_port_h7/h8/h9, toy8 non-vacuity). All kernel-only, axioms [propext, Classical.choice, Quot.sound].

## 1. What the molecule LP certifies [P/C]
Per call, banks B and fields F carry height pairs; contract hcut: for every height mask m, #crossing fields + 2n[m separates {1,h}|{0,h-1}] <= #crossing banks (P104: BankFitHS1.cut_hs, 208 = 2n).
Concave price g (g0 = 0): g(d) = sum_{L=1}^{h-1} c_L min(L,d) + (g_h - g_{h-1}) d on 0..h, c_L = 2g_L - g_{L-1} - g_{L+1} >= 0 (abel, [P] Lean).
Each window min(L,.) is an exact nonneg cut combination; a cut combination's separating weight is <= (mu_1 + mu_{h-2} - mu_{h-1})/2 (triangle (1,h-1,h)) [P], so the best possible total is (g1 + g_{h-2} - g_{h-1})/2 per unit of 2n, i.e. the invoice n(1 + (h-2)^s - (h-1)^s).
Pure min(L) windows have sep 0; sep needs non-interval cuts. Molecule M_L = D min(L) + E min(1) (helper beta_L = E/D, paid from c_1) has sep weight exactly (D+E)/2 (every cut combination found has 2 sep cuts {1,h}, [1..h]\{h-1}).
Budget: c_1' = c_1 - sum_{L=2}^{h-2} beta_L c_L >= 0. Everything else is mass: sum banks dh >= sum fields dh + X gives X(g_h - g_{h-1}).
## 2. Closed form? NO uniform closed form found. [C] min beta_L per (h,L) (LP over cuts with <= 2 runs, <= 3-5 for L=1; equals the full 2^h LP for h <= 10 checked):
beta_L = 1 for L >= about h/2; below that irregular, depends on (h-1) mod L (L=2: 0 for odd h, 1/(h-3) for even h <= 14; L=3: 0 when 3 | h-1, else 1/3, ...). Per-h tables in verify.log. Certified betas are upper bounds on the LP minimum (h=15 L=2: 1/37 and h=19 L=2: 3/79 are probably not minimal; irrelevant for soundness).
Per-h exact certificates: h = 4..19 [C] (verify.py, Fractions); Lean decide+kernel for h = 4..15 (PriceHI*); h = 16..19 exceed the 3.5 GB runlean guard (JSON certs only).
## 3. Lean result
price_h (any h >= 3, MolData h, HCall h n QR): mains (h-1)^s + X (h^s-(h-1)^s) + n (1 + (h-2)^s - (h-1)^s) <= banked price - helper credit, X <= excess, given bud >= 0.
rung_port_h: discharges UniPort.rung_port's hprice (S = 0). Instances rung_port_h7, rung_port_h8, rung_port_h9 (h9 with n=104, QR=96 = the P104 shape; molecules identical to BankFitHS2 betas 0,0,1/3,0,1,1,1).
## 4. Gaps
(a) hcut (the height-cut contract) at h != 9 is a PREMISE: BankFitHS1/BankFlagC2.cut_extras are typed at charts Fin 9 -> ZMod 2 and HSContract needs n rows 1->h with a 0->h-1 partner, each direction. Whether half-spin 64 / E7+A1 (h = 8, n = 64) admit that contract is open: it is the P104 chart structure again.
(b) hbud: [C float] bud_h(1-kappa) > 0 for every h in 4..19 on kappa in (1e-5, 0.2] (budget.log; at kappa=.0093454 h=8: .0052, h=7: .0088, h=9: .0072), so the budget is never binding; NOT Lean-proved (would need an rpow certificate like UniBud.cert).
(c) S_spec normalisation (RETYPE note 4): rung_port_h has S = 0; S_spec > 0 (865.58 at P104) needs its own per-call premise and a port-set value.
(d) wall densities rhoD, rhoR (decoder walls per port set at h = 7, 8: PORTWALL(h)) and the caller Cert at that h are inputs, not produced here.
