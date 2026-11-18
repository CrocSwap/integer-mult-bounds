/-
JOINT-CEILING (; CORRECTED by , Nov 17 per CALLERFLOOR R2 + AUDIT2: arms of 1 repriced).  Formalises the AUDITED structure of CALLERFLOOR R1 (internal notes + AUDIT1.md)
on top of Nov15/CallerCost.lean.  Kernel only (no sorry, no native_decide; `decide +kernel` is kernel evaluation, no extra axiom).
F(s) = sum (T-P) r^s,  s = 1-t  (so F = the R1 "F(t)" = sum (T-P) r^(1-t)).
 1. invoice F = caller F + k * native F for ALL s (invoice_F, same proof as D0).
 2. native floor Nfl(s) = 400*8^s + 16 + 88*(2-2^s): the exact F of the floor histogram (natFloor_F); the bound F_nat <= -Nfl is a HYPOTHESIS (hN).
 3. class lemmas as HYPOTHESES (structure InClass): B-form per-split optimality pointwise in F, sign floor th >= 4 (or 3), two arms (rho = 2).
 4. closed form FB a b th (all a,b >= 1) with bridge to CallerCost.caller for a,b >= 2 (FB_eq).
 5. ceiling theorem, REDUCED to the named numeric hypothesis NumCert th tbar (finite list of rational inequalities, tail.py).
 6. kernel-checked numerics: split 2|2 at t >= 141/4096, the CORRECTED argmax split 1|1 at t >= 176/4096 (36 rational cells), and the control C(8|9): root of the invoice F in (.0204,.0205).
 CORRECTION (R2/AUDIT2): R1's FB overcharged every arm of length 1 by 208 one-stage lines (P[8]) -- FBc below adds 208*8^s per arm of 1;
 the old .0336 ceiling (and the NumCert built from cf.py) is WITHDRAWN; the certified ceiling is kappa <= .0419448764 (A = 4 QUERY, B-form masks, peak 1|1).
-/
import Nov15.CallerCost
import Mathlib.Analysis.SpecialFunctions.Pow.Real

namespace JointCeiling
open CallerCost Real

/-! ### 1. F-form of the invoice -/
noncomputable def Fh (s : ℝ) (l : Hist) : ℝ := (l.map fun p => (p.2 : ℝ) * (p.1 : ℝ) ^ s).sum
noncomputable def Finv (s : ℝ) (i : Inv) : ℝ := Fh s i.T - Fh s i.P

theorem Fh_append (s : ℝ) (l m : Hist) : Fh s (l ++ m) = Fh s l + Fh s m := by simp [Fh]
theorem Fh_scale (s : ℝ) (L : ℕ) (l : Hist) : Fh s (scale L l) = L * Fh s l := by
  induction l with
  | nil => simp [Fh, scale]
  | cons p l ih =>
    simp only [Fh, scale, List.map_cons, List.sum_cons] at ih ⊢
    rw [ih]; push_cast; ring

/-- the invoice in kappa form: F = caller part + k * native part, for every s (hence every t = 1 - s) -/
theorem invoice_F (s : ℝ) (c n : Inv) (L : ℕ) : Finv s (invoice c n L) = Finv s c + L * Finv s n := by
  simp only [Finv, invoice, Fh_append, Fh_scale]; ring

theorem Fh_mono (l : Hist) (hl : ∀ p ∈ l, 1 ≤ p.1) {s s' : ℝ} (h : s ≤ s') : Fh s l ≤ Fh s' l := by
  induction l with
  | nil => simp [Fh]
  | cons p l ih =>
    have ih' := ih (fun q hq => hl q (by simp [hq]))
    have hp : (1 : ℝ) ≤ p.1 := by exact_mod_cast hl p (by simp)
    simp only [Fh, List.map_cons, List.sum_cons] at ih' ⊢
    have := Real.rpow_le_rpow_of_exponent_le hp h
    have h2 : (p.2 : ℝ) * (p.1 : ℝ) ^ s ≤ (p.2 : ℝ) * (p.1 : ℝ) ^ s' :=
      mul_le_mul_of_nonneg_left this (Nat.cast_nonneg _)
    linarith

/-! ### 2. native floor -/
noncomputable def Nfl (s : ℝ) : ℝ := 400 * (8 : ℝ) ^ s + 16 + 88 * (2 - (2 : ℝ) ^ s)
/-- the per-call native floor histogram: 88 stops priced T[2]-2P[1], 400 rank-8 mains, 16 owned (rank 1) + 176 stop credits -/
def natFloor : Inv := ⟨[(2, 88)], [(8, 400), (1, 192)]⟩
theorem natFloor_F (s : ℝ) : Finv s natFloor = -Nfl s := by
  simp [Finv, natFloor, Fh, Nfl]; ring

/-! ### 3. closed form of the caller family, all a,b >= 1 -/
noncomputable def FB (a b th : ℕ) (s : ℝ) : ℝ :=
  208 * (∑ i ∈ Finset.range a, ((8 * i + 9 : ℕ) : ℝ) ^ s + ∑ i ∈ Finset.range b, ((8 * i + 9 : ℕ) : ℝ) ^ s
      + ((8 * (a + b) + 1 : ℕ) : ℝ) ^ s)
  - 208 * (∑ i ∈ Finset.range (a - 2), ((8 * i + 16 : ℕ) : ℝ) ^ s + ∑ i ∈ Finset.range (b - 2), ((8 * i + 16 : ℕ) : ℝ) ^ s)
  - (384 + 16 * ((a + b : ℕ) : ℝ)) * (8 : ℝ) ^ s - 96 * th - 32 * (9 : ℝ) ^ s

theorem Fh_armT (s : ℝ) (n c : ℕ) :
    Fh s (armT n c) = c * ∑ i ∈ Finset.range n, ((8 * i + 9 : ℕ) : ℝ) ^ s := by
  induction n with
  | zero => simp [armT, Fh]
  | succ n ih =>
    have : armT (n + 1) c = armT n c ++ [(8 * n + 9, c)] := by simp [armT, List.range_succ]
    rw [this, Fh_append, ih, Finset.sum_range_succ]; simp [Fh]; ring
theorem Fh_armP (s : ℝ) (m c : ℕ) :
    Fh s (armP m c) = c * ∑ i ∈ Finset.range m, ((8 * i + 16 : ℕ) : ℝ) ^ s := by
  induction m with
  | zero => simp [armP, Fh]
  | succ n ih =>
    have : armP (n + 1) c = armP n c ++ [(8 * n + 16, c)] := by simp [armP, List.range_succ]
    rw [this, Fh_append, ih, Finset.sum_range_succ]; simp [Fh]; ring

/-- bridge: CallerCost's histogram caller (a' + 2 | b' + 2), thin 4, has F = FB (a'+2) (b'+2) 4 -/
theorem FB_eq (s : ℝ) (a' b' : ℕ) : Finv s (caller a' b') = FB (a' + 2) (b' + 2) 4 s := by
  have hk : a' + 2 + (b' + 2) = a' + b' + 4 := by ring
  simp only [Finv, caller, callerT, callerP, Fh_append, Fh_armT, Fh_armP, FB, hk]
  simp [Fh]
  ring

theorem FB_th_mono (a b : ℕ) {th th0 : ℕ} (h : th0 ≤ th) (s : ℝ) : FB a b th s ≤ FB a b th0 s := by
  unfold FB
  have : (th0 : ℝ) ≤ th := by exact_mod_cast h
  linarith

/-! ### 3b. CORRECTION (R2/AUDIT2): arms of length 1.
    cf.py / CALLERCO s1h priced every arm of 1 with 208 spurious one-stage lines (P[8]); the ledger-correct caller (r2.py port model)
    has the same histograms except P[8] is lowered by 208 per arm of 1.  FBc = FB + 208 * 8^s per arm of 1; for a,b >= 2 FBc = FB. -/
def ind (x : ℕ) : ℕ := if x = 1 then 1 else 0
noncomputable def FBc (a b th : ℕ) (s : ℝ) : ℝ := FB a b th s + 208 * ((ind a + ind b : ℕ) : ℝ) * (8 : ℝ) ^ s

theorem FBc_two (a b th : ℕ) (s : ℝ) (ha : 2 ≤ a) (hb : 2 ≤ b) : FBc a b th s = FB a b th s := by
  have h1 : ind a = 0 := by unfold ind; split_ifs <;> omega
  have h2 : ind b = 0 := by unfold ind; split_ifs <;> omega
  simp [FBc, h1, h2]

theorem FBc_th_mono (a b : ℕ) {th th0 : ℕ} (h : th0 ≤ th) (s : ℝ) : FBc a b th s ≤ FBc a b th0 s := by
  unfold FBc
  have := FB_th_mono a b h s
  linarith

/-- the corrected caller histograms (a, b >= 1; thin queries th): arms as in CallerCost, P[8] = 384 + 16 (a+b) - 208 (#arms of 1) -/
def callerG (a b th : ℕ) : Inv :=
  ⟨armT a 208 ++ armT b 208 ++ [(8 * (a + b) + 1, 208)],
   armP (a - 2) 208 ++ armP (b - 2) 208 ++ [(8, 384 + 16 * (a + b) - 208 * (ind a + ind b)), (1, 96 * th), (9, 32)]⟩

theorem ind_le (a b : ℕ) (ha : 1 ≤ a) (hb : 1 ≤ b) : 208 * (ind a + ind b) ≤ 384 + 16 * (a + b) := by
  unfold ind; split_ifs <;> omega

theorem callerG_F (a b th : ℕ) (ha : 1 ≤ a) (hb : 1 ≤ b) (s : ℝ) : Finv s (callerG a b th) = FBc a b th s := by
  have hle := ind_le a b ha hb
  have hc : (((384 + 16 * (a + b) - 208 * (ind a + ind b) : ℕ)) : ℝ) = 384 + 16 * ((a + b : ℕ) : ℝ) - 208 * ((ind a + ind b : ℕ) : ℝ) := by
    rw [Nat.cast_sub hle]; push_cast; ring
  simp only [Finv, callerG, Fh_append, Fh_armT, Fh_armP, FBc, FB]
  simp [Fh, hc]
  push_cast
  ring

/-- for a, b >= 2 the corrected caller has the same F as CallerCost.caller (so reproduction of #7113 is unaffected) -/
theorem callerG_eq_caller_F (a' b' : ℕ) (s : ℝ) : Finv s (callerG (a' + 2) (b' + 2) 4) = Finv s (caller a' b') := by
  rw [callerG_F _ _ _ (by omega) (by omega), FBc_two _ _ _ _ (by omega) (by omega), FB_eq]

/-- LEDGER LAW for ALL arms >= 1: S(callerG) = 3408 (a+b) - 208 (+ 96 (4 - th)); at a,b >= 2 this is CallerCost.S_caller.
    (cf.py's version gave 3408 (a+b) - 208 - 1664 per arm of 1: the broken ledger.) -/
theorem Sh_armP' (x : ℕ) (hx : 1 ≤ x) :
    Sh (armP (x - 2) 208) = 208 * (4 * ((x : ℤ) - 2) * ((x : ℤ) - 2) + 12 * ((x : ℤ) - 2)) + 1664 * (ind x : ℤ) := by
  rw [Sh_armP]
  rcases Nat.lt_or_ge x 2 with h | h
  · have : x = 1 := by omega
    subst this; simp [ind]
  · have h1 : ((x - 2 : ℕ) : ℤ) = (x : ℤ) - 2 := by omega
    have h2 : ind x = 0 := by unfold ind; split_ifs <;> omega
    rw [h1, h2]; simp

theorem callerG_S (a b : ℕ) (ha : 1 ≤ a) (hb : 1 ≤ b) :
    Sinv (callerG a b 4) = 3408 * ((a : ℤ) + b) - 208 := by
  have hle := ind_le a b ha hb
  have hc : (((384 + 16 * (a + b) - 208 * (ind a + ind b) : ℕ)) : ℤ) = 384 + 16 * ((a + b : ℕ) : ℤ) - 208 * ((ind a + ind b : ℕ) : ℤ) := by
    rw [Nat.cast_sub hle]; push_cast; ring
  simp only [Sinv, callerG, Sh_append, Sh_armT, Sh_armP' a ha, Sh_armP' b hb]
  simp only [Sh, List.map_cons, List.sum_cons, List.map_nil, List.sum_nil]
  rw [hc]
  push_cast
  ring

/-! ### 4. class lemmas as explicit hypotheses -/
/-- A caller in the audited class (CALLERFLOOR R1 sec 1): two-arm nested rho = 2 root with arms a|b >= 1 (k = a+b calls),
    thin queries th.  The CLASS LEMMAS are fields (hypotheses; a parallel lane proves them):
    hB  : B-form per-split optimality, pointwise in F(t) (CALLEROPEN Crossing + Floor lemmas; AUDIT1 item 1: only the D0/ratio form is proved);
    hth : sign floor thin >= th0 (SIGNCAP/BEAUTY84; th0 = 4 built, 3 unbuilt);
    hrho: rho >= 2 (rho = 1 needs t = -1, closed).  rho = 2 enters only through the shape of FB (the two-arm closed form). -/
structure InClass (th0 : ℕ) where
  a : ℕ
  b : ℕ
  th : ℕ
  rho : ℕ
  ci : Inv
  ha : 1 ≤ a
  hb : 1 ≤ b
  hth : th0 ≤ th
  hrho : 2 ≤ rho
  hB : ∀ s : ℝ, 0 ≤ s → s ≤ 1 → Finv s ci ≤ FBc a b th s


/-- the NUMERIC CERTIFICATE as a named hypothesis (REGENERATED, , from the AUDITED r2c.py; R1's cf.py-based list is withdrawn).
    Statement: for every split a|b (a,b>=1) and 0 <= s <= 1-tbar,  FBc a b th0 s - (a+b) Nfl s < 0.
    Source: internal notes (lines 8-12: 1|1 root via cf.cert on the ledger-correct port model, th = th0; lines 13-17: 1|b, b = 2..59,
    interval cover on [t0, 1] with pk._coef of joint(A(1,b), B(1,b), 1+b); lines 18-26: tail k >= 61 with R1's U plus the arm-of-1 correction
    +208*8^s, U < 0 and U' < 0 by cover) together with a,b >= 2 splits from R1 tail.py lines 6-26 / cf.py `cert` lines 33-40 (unchanged: FBc = FB there,
    FBc_two + callerG_eq_caller_F; r2.py asserts identity with the port model).  Output r2c.out (th4: kbar .041944876391, cert True, 1|b True, tail True;
    th3: .068120327915).  Not discharged in Lean: ~1,800 (a,b) pairs of 40-digit interval covers, plus the R1 tail Jensen/MVT step (AUDIT2: unaudited).
    tbar = .0419448764 (th0 = 4, rounded UP from .041944876391; A = 4 QUERY, B-form masks) and .0681203280 (th0 = 3: th3 B-form-A class only;
    AUDIT2: scanned, not covered, for the true sign-floor class). -/
def NumCert (th0 : ℕ) (tbar : ℝ) : Prop :=
  ∀ a b : ℕ, 1 ≤ a → 1 ≤ b → ∀ s : ℝ, 0 ≤ s → s ≤ 1 - tbar → FBc a b th0 s - ((a + b : ℕ) : ℝ) * Nfl s < 0

noncomputable def tbar4 : ℝ := 419448764 / 10 ^ 10
noncomputable def tbar3 : ℝ := 681203280 / 10 ^ 10

/-- CEILING THEOREM (conditional on the class lemmas hB/hth/hrho, the native floor hN, and NumCert):
    for every caller in the class and every native meeting the floor, the invoice F(t) = Finv (1-t) is < 0 for t >= tbar. -/
theorem ceiling {th0 : ℕ} {tbar : ℝ} (hnum : NumCert th0 tbar) (c : InClass th0) (n : Inv)
    (hN : ∀ s : ℝ, 0 ≤ s → s ≤ 1 → Finv s n ≤ -Nfl s) (htb : 0 ≤ tbar)
    (s : ℝ) (hs0 : 0 ≤ s) (hs : s ≤ 1 - tbar) :
    Finv s (invoice c.ci n (c.a + c.b)) < 0 := by
  have hs1 : s ≤ 1 := by linarith
  rw [invoice_F]
  have h1 := c.hB s hs0 hs1
  have h2 := hN s hs0 hs1
  have h3 : ((c.a + c.b : ℕ) : ℝ) * Finv s n ≤ ((c.a + c.b : ℕ) : ℝ) * (-Nfl s) :=
    mul_le_mul_of_nonneg_left h2 (Nat.cast_nonneg _)
  have h4 := FBc_th_mono c.a c.b c.hth s
  have h5 := hnum c.a c.b c.ha c.hb s hs0 hs
  linarith

theorem ceiling4 (hnum : NumCert 4 tbar4) (c : InClass 4) (n : Inv)
    (hN : ∀ s : ℝ, 0 ≤ s → s ≤ 1 → Finv s n ≤ -Nfl s) (t : ℝ) (ht : tbar4 ≤ t) (ht1 : t ≤ 1) :
    Finv (1 - t) (invoice c.ci n (c.a + c.b)) < 0 :=
  ceiling hnum c n hN (by unfold tbar4; norm_num) (1 - t) (by linarith) (by linarith)

theorem ceiling3 (hnum : NumCert 3 tbar3) (c : InClass 3) (n : Inv)
    (hN : ∀ s : ℝ, 0 ≤ s → s ≤ 1 → Finv s n ≤ -Nfl s) (t : ℝ) (ht : tbar3 ≤ t) (ht1 : t ≤ 1) :
    Finv (1 - t) (invoice c.ci n (c.a + c.b)) < 0 :=
  ceiling hnum c n hN (by unfold tbar3; norm_num) (1 - t) (by linarith) (by linarith)


/-! ### 5. kernel-checked numerics: rational rpow bounds through natural-number powers -/
theorem rp_pow {x : ℕ} {p q : ℕ} (hq : 0 < q) : (((x : ℝ) ^ ((p : ℝ) / q)) ^ q) = (x : ℝ) ^ p := by
  rw [← Real.rpow_natCast, ← Real.rpow_mul (Nat.cast_nonneg x), div_mul_cancel₀ _ (by exact_mod_cast hq.ne'),
    Real.rpow_natCast]

theorem rp_le_nat {x p q n d : ℕ} (hq : 0 < q) (hd : 0 < d) (h : x ^ p * d ^ q ≤ n ^ q) :
    (x : ℝ) ^ ((p : ℝ) / q) ≤ (n : ℝ) / d := by
  by_contra hc
  have hc := not_le.mp hc
  have hdr : (0 : ℝ) < d := by exact_mod_cast hd
  have h1 : (((n : ℝ) / d)) ^ q < (((x : ℝ) ^ ((p : ℝ) / q)) ^ q) :=
    pow_lt_pow_left₀ hc (by positivity) hq.ne'
  rw [rp_pow hq, div_pow, div_lt_iff₀ (by positivity)] at h1
  have h2 : ((x ^ p * d ^ q : ℕ) : ℝ) ≤ ((n ^ q : ℕ) : ℝ) := by exact_mod_cast h
  push_cast at h2
  linarith

theorem rp_ge_nat {x p q n d : ℕ} (hq : 0 < q) (hd : 0 < d) (h : n ^ q ≤ x ^ p * d ^ q) :
    (n : ℝ) / d ≤ (x : ℝ) ^ ((p : ℝ) / q) := by
  by_contra hc
  have hc := not_le.mp hc
  have hdr : (0 : ℝ) < d := by exact_mod_cast hd
  have h1 : (((x : ℝ) ^ ((p : ℝ) / q))) ^ q < (((n : ℝ) / d)) ^ q :=
    pow_lt_pow_left₀ hc (by positivity) hq.ne'
  rw [rp_pow hq, div_pow, lt_div_iff₀ (by positivity)] at h1
  have h2 : ((n ^ q : ℕ) : ℝ) ≤ ((x ^ p * d ^ q : ℕ) : ℝ) := by exact_mod_cast h
  push_cast at h2
  linarith

/-- upper bound of F-sum of a histogram at s = p/q by natural numerators U r / d -/
theorem Fh_le (l : Hist) (p q d : ℕ) (U : ℕ → ℕ) (hq : 0 < q) (hd : 0 < d)
    (h : ∀ pr ∈ l, pr.1 ^ p * d ^ q ≤ (U pr.1) ^ q) :
    Fh ((p : ℝ) / q) l ≤ ((l.map fun pr => pr.2 * U pr.1).sum : ℕ) / (d : ℝ) := by
  induction l with
  | nil => simp [Fh]
  | cons pr l ih =>
    have ih' := ih (fun r hr => h r (by simp [hr]))
    have h1 := rp_le_nat hq hd (h pr (by simp))
    simp only [Fh, List.map_cons, List.sum_cons] at ih' ⊢
    rw [Nat.cast_add, Nat.cast_mul]
    have h2 : (pr.2 : ℝ) * (pr.1 : ℝ) ^ ((p : ℝ) / q) ≤ (pr.2 : ℝ) * ((U pr.1 : ℝ) / d) :=
      mul_le_mul_of_nonneg_left h1 (Nat.cast_nonneg _)
    have h3 : (pr.2 : ℝ) * ((U pr.1 : ℝ) / d) = ((pr.2 : ℝ) * U pr.1) / d := by ring
    rw [add_div]
    linarith

theorem Fh_ge (l : Hist) (p q d : ℕ) (L : ℕ → ℕ) (hq : 0 < q) (hd : 0 < d)
    (h : ∀ pr ∈ l, (L pr.1) ^ q ≤ pr.1 ^ p * d ^ q) :
    ((l.map fun pr => pr.2 * L pr.1).sum : ℕ) / (d : ℝ) ≤ Fh ((p : ℝ) / q) l := by
  induction l with
  | nil => simp [Fh]
  | cons pr l ih =>
    have ih' := ih (fun r hr => h r (by simp [hr]))
    have h1 := rp_ge_nat hq hd (h pr (by simp))
    simp only [Fh, List.map_cons, List.sum_cons] at ih' ⊢
    rw [Nat.cast_add, Nat.cast_mul]
    have h2 : (pr.2 : ℝ) * ((L pr.1 : ℝ) / d) ≤ (pr.2 : ℝ) * (pr.1 : ℝ) ^ ((p : ℝ) / q) :=
      mul_le_mul_of_nonneg_left h1 (Nat.cast_nonneg _)
    have h3 : (pr.2 : ℝ) * ((L pr.1 : ℝ) / d) = ((pr.2 : ℝ) * L pr.1) / d := by ring
    rw [add_div]
    linarith

/-- certificate cell: for s in [px/q, py/q], F(s) <= (T-part at py) - (P-part at px) < 0 by natural-number checks -/
theorem cell_neg (i : Inv) (px py q d : ℕ) (U L : ℕ → ℕ) (hq : 0 < q) (hd : 0 < d)
    (hrT : ∀ pr ∈ i.T, 1 ≤ pr.1) (hrP : ∀ pr ∈ i.P, 1 ≤ pr.1)
    (hT : ∀ pr ∈ i.T, pr.1 ^ py * d ^ q ≤ (U pr.1) ^ q)
    (hP : ∀ pr ∈ i.P, (L pr.1) ^ q ≤ pr.1 ^ px * d ^ q)
    (hsum : (i.T.map fun pr => pr.2 * U pr.1).sum < (i.P.map fun pr => pr.2 * L pr.1).sum)
    (s : ℝ) (hx : (px : ℝ) / q ≤ s) (hy : s ≤ (py : ℝ) / q) : Finv s i < 0 := by
  have a1 := Fh_mono i.T hrT hy
  have a2 := Fh_mono i.P hrP hx
  have a3 := Fh_le i.T py q d U hq hd hT
  have a4 := Fh_ge i.P px q d L hq hd hP
  have hdr : (0 : ℝ) < d := by exact_mod_cast hd
  have a5 : (((i.T.map fun pr => pr.2 * U pr.1).sum : ℕ) : ℝ) < (((i.P.map fun pr => pr.2 * L pr.1).sum : ℕ) : ℝ) := by
    exact_mod_cast hsum
  have a6 : (((i.T.map fun pr => pr.2 * U pr.1).sum : ℕ) : ℝ) / d < (((i.P.map fun pr => pr.2 * L pr.1).sum : ℕ) : ℝ) / d :=
    div_lt_div_of_pos_right a5 hdr
  unfold Finv
  linarith

/-- the converse cell for a positive sign (used for the control bracket): F(s) > 0 at the single point s = p/q -/
theorem pt_pos (i : Inv) (p q d : ℕ) (U L : ℕ → ℕ) (hq : 0 < q) (hd : 0 < d)
    (hT : ∀ pr ∈ i.T, (L pr.1) ^ q ≤ pr.1 ^ p * d ^ q)
    (hP : ∀ pr ∈ i.P, pr.1 ^ p * d ^ q ≤ (U pr.1) ^ q)
    (hsum : (i.P.map fun pr => pr.2 * U pr.1).sum < (i.T.map fun pr => pr.2 * L pr.1).sum) :
    0 < Finv ((p : ℝ) / q) i := by
  have a3 := Fh_le i.P p q d U hq hd hP
  have a4 := Fh_ge i.T p q d L hq hd hT
  have hdr : (0 : ℝ) < d := by exact_mod_cast hd
  have a5 : (((i.P.map fun pr => pr.2 * U pr.1).sum : ℕ) : ℝ) < (((i.T.map fun pr => pr.2 * L pr.1).sum : ℕ) : ℝ) := by
    exact_mod_cast hsum
  have a6 : (((i.P.map fun pr => pr.2 * U pr.1).sum : ℕ) : ℝ) / d < (((i.T.map fun pr => pr.2 * L pr.1).sum : ℕ) : ℝ) / d :=
    div_lt_div_of_pos_right a5 hdr
  unfold Finv
  linarith

/-! ### 6. the argmax split 2|2 (k = 4, thin 4): F < 0 for t >= 141/4096 (= .034424), 28-cell rational cover (python: internal notes cover, generators Nov15/jointceiling_gen/)
    (the exact crossing .0336321541 needs rpow to 1e-10: held in NumCert, see sec 4) -/
def I22 : Inv := invoice (caller 0 0) natFloor 4
theorem I22_F (s : ℝ) : Finv s I22 = FBc 2 2 4 s - ((2 + 2 : ℕ) : ℝ) * Nfl s := by
  rw [FBc_two 2 2 4 s (by norm_num) (by norm_num)]
  have h := invoice_F s (caller 0 0) natFloor 4
  rw [natFloor_F, FB_eq] at h
  show Finv s (invoice (caller 0 0) natFloor 4) = _
  rw [h]; push_cast; ring
theorem cell22_0 (s : ℝ) (hx : ((0 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((988 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I22 < 0 :=
  cell_neg I22 0 988 4096 100000000 (fun r => if r = 2 then 118198437 else if r = 9 then 169892315 else if r = 17 then 198060441 else if r = 33 then 232424644 else 0) (fun r => if r = 1 then 99999999 else if r = 8 then 99999999 else if r = 9 then 99999999 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell22_1 (s : ℝ) (hx : ((988 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((1977 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I22 < 0 :=
  cell_neg I22 988 1977 4096 100000000 (fun r => if r = 2 then 139732347 else if r = 9 then 288788857 else if r = 17 then 392550812 else if r = 33 then 540673488 else 0) (fun r => if r = 1 then 99999999 else if r = 8 then 165133497 else if r = 9 then 169892312 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell22_2 (s : ℝ) (hx : ((1977 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((2471 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I22 < 0 :=
  cell_neg I22 1977 2471 4096 100000000 (fun r => if r = 2 then 151915755 else if r = 9 then 376415325 else if r = 17 then 552452252 else if r = 33 then 824282651 else 0) (fun r => if r = 1 then 99999999 else if r = 8 then 272829196 else if r = 9 then 288788854 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell22_3 (s : ℝ) (hx : ((2471 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((2718 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I22 < 0 :=
  cell_neg I22 2471 2718 4096 100000000 (fun r => if r = 2 then 158400208 else if r = 9 then 429744898 else if r = 17 then 655381507 else if r = 33 then 1017763102 else 0) (fun r => if r = 1 then 99999999 else if r = 8 then 350597193 else if r = 9 then 376415322 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell22_4 (s : ℝ) (hx : ((2718 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((2966 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I22 < 0 :=
  cell_neg I22 2718 2966 4096 100000000 (fun r => if r = 2 then 165189399 else if r = 9 then 490893330 else if r = 17 then 778025837 else if r = 33 then 1257731609 else 0) (fun r => if r = 1 then 99999999 else if r = 8 then 397436025 else if r = 9 then 429744895 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell22_5 (s : ℝ) (hx : ((2966 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((3213 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I22 < 0 :=
  cell_neg I22 2966 3213 4096 100000000 (fun r => if r = 2 then 172240432 else if r = 9 then 560441857 else if r = 17 then 922982473 else if r = 33 then 1552953737 else 0) (fun r => if r = 1 then 99999999 else if r = 8 then 450761181 else if r = 9 then 490893327 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell22_6 (s : ℝ) (hx : ((3213 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((3336 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I22 < 0 :=
  cell_neg I22 3213 3336 4096 100000000 (fun r => if r = 2 then 175863141 else if r = 9 then 598667655 else if r = 17 then 1004946564 else if r = 33 then 1724878163 else 0) (fun r => if r = 1 then 99999999 else if r = 8 then 510981649 else if r = 9 then 560441854 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell22_7 (s : ℝ) (hx : ((3336 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((3460 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I22 < 0 :=
  cell_neg I22 3336 3460 4096 100000000 (fun r => if r = 2 then 179592434 else if r = 9 then 639843844 else if r = 17 then 1094946471 else if r = 33 then 1917472133 else 0) (fun r => if r = 1 then 99999999 else if r = 8 then 543906765 else if r = 9 then 598667652 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell22_8 (s : ℝ) (hx : ((3460 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((3583 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I22 < 0 :=
  cell_neg I22 3460 3583 4096 100000000 (fun r => if r = 2 then 183369777 else if r = 9 then 683485377 else if r = 17 then 1192181571 else if r = 33 then 2129751667 else 0) (fun r => if r = 1 then 99999999 else if r = 8 then 579247408 else if r = 9 then 639843841 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell22_9 (s : ℝ) (hx : ((3583 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((3645 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I22 < 0 :=
  cell_neg I22 3583 3645 4096 100000000 (fun r => if r = 2 then 185303816 else if r = 9 then 706599503 else if r = 17 then 1244421092 else if r = 33 then 2245506338 else 0) (fun r => if r = 1 then 99999999 else if r = 8 then 616571231 else if r = 9 then 683485374 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell22_10 (s : ℝ) (hx : ((3645 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((3707 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I22 < 0 :=
  cell_neg I22 3645 3707 4096 100000000 (fun r => if r = 2 then 187258254 else if r = 9 then 730495304 else if r = 17 then 1298949666 else if r = 33 then 2367552420 else 0) (fun r => if r = 1 then 99999999 else if r = 8 then 636287037 else if r = 9 then 706599500 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell22_11 (s : ℝ) (hx : ((3707 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((3769 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I22 < 0 :=
  cell_neg I22 3707 3769 4096 100000000 (fun r => if r = 2 then 189233305 else if r = 9 then 755199213 else if r = 17 then 1355867597 else if r = 33 then 2496231861 else 0) (fun r => if r = 1 then 99999999 else if r = 8 then 656633287 else if r = 9 then 730495301 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell22_12 (s : ℝ) (hx : ((3769 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((3800 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I22 < 0 :=
  cell_neg I22 3769 3800 4096 100000000 (fun r => if r = 2 then 190228629 else if r = 9 then 767862713 else if r = 17 then 1385255112 else if r = 33 then 2563171002 else 0) (fun r => if r = 1 then 99999999 else if r = 8 then 677630139 else if r = 9 then 755199210 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell22_13 (s : ℝ) (hx : ((3800 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((3831 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I22 < 0 :=
  cell_neg I22 3800 3831 4096 100000000 (fun r => if r = 2 then 191229188 else if r = 9 then 780738560 else if r = 17 then 1415279582 else if r = 33 then 2631905189 else 0) (fun r => if r = 1 then 99999999 else if r = 8 then 688379017 else if r = 9 then 767862710 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell22_14 (s : ℝ) (hx : ((3831 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((3862 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I22 < 0 :=
  cell_neg I22 3831 3862 4096 100000000 (fun r => if r = 2 then 192235010 else if r = 9 then 793830314 else if r = 17 then 1445954812 else if r = 33 then 2702482558 else 0) (fun r => if r = 1 then 99999999 else if r = 8 then 699298398 else if r = 9 then 780738557 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell22_15 (s : ℝ) (hx : ((3862 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((3877 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I22 < 0 :=
  cell_neg I22 3862 3877 4096 100000000 (fun r => if r = 2 then 192723596 else if r = 9 then 800243619 else if r = 17 then 1461035469 else if r = 33 then 2737309242 else 0) (fun r => if r = 1 then 99999999 else if r = 8 then 710390987 else if r = 9 then 793830311 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell22_16 (s : ℝ) (hx : ((3877 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((3893 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I22 < 0 :=
  cell_neg I22 3877 3893 4096 100000000 (fun r => if r = 2 then 193246122 else if r = 9 then 807141597 else if r = 17 then 1477294906 else if r = 33 then 2774952534 else 0) (fun r => if r = 1 then 99999999 else if r = 8 then 715821366 else if r = 9 then 800243616 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell22_17 (s : ℝ) (hx : ((3893 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((3908 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I22 < 0 :=
  cell_neg I22 3893 3908 4096 100000000 (fun r => if r = 2 then 193737278 else if r = 9 then 813662443 else if r = 17 then 1492702427 else if r = 33 then 2810713133 else 0) (fun r => if r = 1 then 99999999 else if r = 8 then 721659532 else if r = 9 then 807141594 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell22_18 (s : ℝ) (hx : ((3908 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((3924 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I22 < 0 :=
  cell_neg I22 3908 3924 4096 100000000 (fun r => if r = 2 then 194262553 else if r = 9 then 820676089 else if r = 17 then 1509314276 else if r = 33 then 2849365870 else 0) (fun r => if r = 1 then 99999999 else if r = 8 then 727176050 else if r = 9 then 813662440 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell22_19 (s : ℝ) (hx : ((3924 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((3931 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I22 < 0 :=
  cell_neg I22 3924 3931 4096 100000000 (fun r => if r = 2 then 194492808 else if r = 9 then 823763539 else if r = 17 then 1516639972 else if r = 33 then 2866443162 else 0) (fun r => if r = 1 then 99999999 else if r = 8 then 733106824 else if r = 9 then 820676086 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell22_20 (s : ℝ) (hx : ((3931 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((3939 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I22 < 0 :=
  cell_neg I22 3931 3939 4096 100000000 (fun r => if r = 2 then 194756291 else if r = 9 then 827306279 else if r = 17 then 1525055745 else if r = 33 then 2886085429 else 0) (fun r => if r = 1 then 99999999 else if r = 8 then 735716725 else if r = 9 then 823763536 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell22_21 (s : ℝ) (hx : ((3939 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((3943 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I22 < 0 :=
  cell_neg I22 3939 3943 4096 100000000 (fun r => if r = 2 then 194888167 else if r = 9 then 829083358 else if r = 17 then 1529281127 else if r = 33 then 2895956979 else 0) (fun r => if r = 1 then 99999999 else if r = 8 then 738710847 else if r = 9 then 827306276 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell22_22 (s : ℝ) (hx : ((3943 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((3947 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I22 < 0 :=
  cell_neg I22 3943 3947 4096 100000000 (fun r => if r = 2 then 195020132 else if r = 9 then 830864255 else if r = 17 then 1533518216 else if r = 33 then 2905862294 else 0) (fun r => if r = 1 then 99999999 else if r = 8 then 740212475 else if r = 9 then 829083355 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell22_23 (s : ℝ) (hx : ((3947 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((3949 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I22 < 0 :=
  cell_neg I22 3947 3949 4096 100000000 (fun r => if r = 2 then 195086147 else if r = 9 then 831756137 else if r = 17 then 1535641161 else if r = 33 then 2910827650 else 0) (fun r => if r = 1 then 99999999 else if r = 8 then 741717155 else if r = 9 then 830864252 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell22_24 (s : ℝ) (hx : ((3949 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((3951 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I22 < 0 :=
  cell_neg I22 3949 3951 4096 100000000 (fun r => if r = 2 then 195152186 else if r = 9 then 832648977 else if r = 17 then 1537767044 else if r = 33 then 2915801489 else 0) (fun r => if r = 1 then 99999999 else if r = 8 then 742470642 else if r = 9 then 831756134 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell22_25 (s : ℝ) (hx : ((3951 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((3953 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I22 < 0 :=
  cell_neg I22 3951 3953 4096 100000000 (fun r => if r = 2 then 195218246 else if r = 9 then 833542775 else if r = 17 then 1539895871 else if r = 33 then 2920783828 else 0) (fun r => if r = 1 then 99999999 else if r = 8 then 743224894 else if r = 9 then 832648974 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell22_26 (s : ℝ) (hx : ((3953 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((3954 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I22 < 0 :=
  cell_neg I22 3953 3954 4096 100000000 (fun r => if r = 2 then 195251285 else if r = 9 then 833990034 else if r = 17 then 1540961389 else if r = 33 then 2923278189 else 0) (fun r => if r = 1 then 99999999 else if r = 8 then 743979912 else if r = 9 then 833542772 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell22_27 (s : ℝ) (hx : ((3954 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((3955 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I22 < 0 :=
  cell_neg I22 3954 3955 4096 100000000 (fun r => if r = 2 then 195284329 else if r = 9 then 834437532 else if r = 17 then 1542027645 else if r = 33 then 2925774680 else 0) (fun r => if r = 1 then 99999999 else if r = 8 then 744357709 else if r = 9 then 833990031 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem I22_neg (s : ℝ) (h0 : 0 ≤ s) (h1 : s ≤ ((3955 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) : Finv s I22 < 0 := by
  rcases le_total s (((988 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h2 | h2
  · exact cell22_0 s (by rw [Nat.cast_zero, zero_div]; exact h0) h2
  · rcases le_total s (((1977 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h3 | h3
    · exact cell22_1 s h2 h3
    · rcases le_total s (((2471 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h4 | h4
      · exact cell22_2 s h3 h4
      · rcases le_total s (((2718 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h5 | h5
        · exact cell22_3 s h4 h5
        · rcases le_total s (((2966 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h6 | h6
          · exact cell22_4 s h5 h6
          · rcases le_total s (((3213 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h7 | h7
            · exact cell22_5 s h6 h7
            · rcases le_total s (((3336 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h8 | h8
              · exact cell22_6 s h7 h8
              · rcases le_total s (((3460 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h9 | h9
                · exact cell22_7 s h8 h9
                · rcases le_total s (((3583 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h10 | h10
                  · exact cell22_8 s h9 h10
                  · rcases le_total s (((3645 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h11 | h11
                    · exact cell22_9 s h10 h11
                    · rcases le_total s (((3707 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h12 | h12
                      · exact cell22_10 s h11 h12
                      · rcases le_total s (((3769 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h13 | h13
                        · exact cell22_11 s h12 h13
                        · rcases le_total s (((3800 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h14 | h14
                          · exact cell22_12 s h13 h14
                          · rcases le_total s (((3831 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h15 | h15
                            · exact cell22_13 s h14 h15
                            · rcases le_total s (((3862 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h16 | h16
                              · exact cell22_14 s h15 h16
                              · rcases le_total s (((3877 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h17 | h17
                                · exact cell22_15 s h16 h17
                                · rcases le_total s (((3893 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h18 | h18
                                  · exact cell22_16 s h17 h18
                                  · rcases le_total s (((3908 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h19 | h19
                                    · exact cell22_17 s h18 h19
                                    · rcases le_total s (((3924 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h20 | h20
                                      · exact cell22_18 s h19 h20
                                      · rcases le_total s (((3931 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h21 | h21
                                        · exact cell22_19 s h20 h21
                                        · rcases le_total s (((3939 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h22 | h22
                                          · exact cell22_20 s h21 h22
                                          · rcases le_total s (((3943 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h23 | h23
                                            · exact cell22_21 s h22 h23
                                            · rcases le_total s (((3947 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h24 | h24
                                              · exact cell22_22 s h23 h24
                                              · rcases le_total s (((3949 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h25 | h25
                                                · exact cell22_23 s h24 h25
                                                · rcases le_total s (((3951 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h26 | h26
                                                  · exact cell22_24 s h25 h26
                                                  · rcases le_total s (((3953 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h27 | h27
                                                    · exact cell22_25 s h26 h27
                                                    · rcases le_total s (((3954 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h28 | h28
                                                      · exact cell22_26 s h27 h28
                                                      · exact cell22_27 s h28 h1

/-- t >= 141/4096 (s <= 3955/4096): the invoice F of EVERY native at the floor with the argmax caller 2|2 is negative -/
theorem split22_ceiling (t : ℝ) (ht : (141 : ℝ) / 4096 ≤ t) (ht1 : t ≤ 1) : Finv (1 - t) I22 < 0 := by
  apply I22_neg (1 - t) (by linarith)
  have : ((3955 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) = 1 - 141 / 4096 := by norm_num
  rw [this]; linarith

/-! ### 7. the control C(8|9) (= #7113 caller, CallerCost.reproduction) at the native floor, k = 17: the root of F(t) lies in (.0204, .0205)
    (R3 control .0204110964; exact root needs rpow to 1e-10, not done in kernel) -/
def I89 : Inv := invoice (caller 6 7) natFloor 17
theorem I89_F (s : ℝ) : Finv s I89 = FB 8 9 4 s - ((8 + 9 : ℕ) : ℝ) * Nfl s := by
  have h := invoice_F s (caller 6 7) natFloor 17
  rw [natFloor_F, FB_eq] at h
  show Finv s (invoice (caller 6 7) natFloor 17) = _
  rw [h]; push_cast; ring
/-- F(t = .0204) > 0 (s = 2449/2500) -/
theorem control_pos : 0 < Finv (((2449 : ℕ) : ℝ) / ((2500 : ℕ) : ℝ)) I89 :=
  pt_pos I89 2449 2500 100000000 (fun r => if r = 1 then 100000001 else if r = 8 then 766773248 else if r = 9 then 860549711 else if r = 16 then 1512014428 else if r = 24 then 2249339100 else if r = 32 then 2981569375 else if r = 40 then 3710034667 else if r = 48 then 4435513611 else if r = 56 then 5158518488 else if r = 64 then 5879412111 else 0) (fun r => if r = 2 then 197191859 else if r = 9 then 860549708 else if r = 17 then 1604529710 else if r = 25 then 2341111144 else if r = 33 then 3072813876 else if r = 41 then 3800870438 else if r = 49 then 4526015947 else if r = 57 then 5248739375 else if r = 65 then 5969389592 else if r = 73 then 6688228062 else if r = 137 then 12391716458 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel)
/-- F(t = .0205) < 0 (s = 1959/2000) -/
theorem control_neg : Finv (((1959 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ)) I89 < 0 :=
  cell_neg I89 1959 1959 2000 100000000 (fun r => if r = 2 then 197178194 else if r = 9 then 860360650 else if r = 17 then 1604075180 else if r = 25 then 2340357693 else if r = 33 then 3071739655 else if r = 41 then 3799459223 else if r = 49 then 4524254849 else if r = 57 then 5246617715 else if r = 65 then 5966898261 else if r = 73 then 6685359123 else if r = 137 then 12385621260 else 0) (fun r => if r = 1 then 99999999 else if r = 8 then 766613815 else if r = 9 then 860360647 else if r = 16 then 1511595264 else if r = 24 then 2248624359 else if r = 32 then 2980536218 else if r = 40 then 3708666329 else if r = 48 then 4433796864 else if r = 56 then 5156442418 else if r = 64 then 5876967437 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) _ le_rfl le_rfl
/-- the control brackets the R3 value .0204110964: F(.0204) > 0 > F(.0205) for the exact #7113 caller invoice at the floor native -/
theorem control_bracket :
    0 < Finv (1 - (204 : ℝ) / 10000) I89 ∧ Finv (1 - (205 : ℝ) / 10000) I89 < 0 := by
  constructor
  · have h := control_pos
    have e : ((2449 : ℕ) : ℝ) / ((2500 : ℕ) : ℝ) = 1 - 204 / 10000 := by norm_num
    rwa [e] at h
  · have h := control_neg
    have e : ((1959 : ℕ) : ℝ) / ((2000 : ℕ) : ℝ) = 1 - 205 / 10000 := by norm_num
    rwa [e] at h


/-! ### 8. the CORRECTED argmax split 1|1 (k = 2, thin 4, arms of 1 priced by the ledger): F < 0 for t >= 176/4096 = 0.042969 (root .0419448764), 36 rational cells.
    (internal notes; the exact root needs rpow to 1e-10, held in NumCert) -/
def I11 : Inv := invoice (callerG 1 1 4) natFloor 2
theorem I11_F (s : ℝ) : Finv s I11 = FBc 1 1 4 s - ((1 + 1 : ℕ) : ℝ) * Nfl s := by
  have h := invoice_F s (callerG 1 1 4) natFloor 2
  rw [natFloor_F, callerG_F 1 1 4 le_rfl le_rfl] at h
  show Finv s (invoice (callerG 1 1 4) natFloor 2) = _
  rw [h]; push_cast; ring
theorem cell11_0 (s : ℝ) (hx : ((0 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((980 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I11 < 0 :=
  cell_neg I11 0 980 4096 100000000000 (fun r => if r = 2 then 118038526172 else if r = 9 then 169164790567 else if r = 17 then 196967474893 else 0) (fun r => if r = 1 then 99999999999 else if r = 8 then 99999999999 else if r = 9 then 99999999999 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell11_1 (s : ℝ) (hx : ((980 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((1470 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I11 < 0 :=
  cell_neg I11 980 1470 4096 100000000000 (fun r => if r = 2 then 128243590121 else if r = 9 then 220021419926 else if r = 17 then 276434202378 else 0) (fun r => if r = 1 then 99999999999 else if r = 8 then 164464184067 else if r = 9 then 169164790564 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell11_2 (s : ℝ) (hx : ((1470 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((1960 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I11 < 0 :=
  cell_neg I11 1470 1960 4096 100000000000 (fun r => if r = 2 then 139330936607 else if r = 9 then 286167263672 else if r = 17 then 387961861652 else 0) (fun r => if r = 1 then 99999999999 else if r = 8 then 210914774109 else if r = 9 then 220021419923 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell11_3 (s : ℝ) (hx : ((1960 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((2450 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I11 < 0 :=
  cell_neg I11 1960 2450 4096 100000000000 (fun r => if r = 2 then 151376843687 else if r = 9 then 372198774216 else if r = 17 then 544485468158 else 0) (fun r => if r = 1 then 99999999999 else if r = 8 then 270484678412 else if r = 9 then 286167263669 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell11_4 (s : ℝ) (hx : ((2450 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((2695 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I11 < 0 :=
  cell_neg I11 2450 2695 4096 100000000000 (fun r => if r = 2 then 157784882305 else if r = 9 then 424475308227 else if r = 17 then 645037439188 else 0) (fun r => if r = 1 then 99999999999 else if r = 8 then 346879262320 else if r = 9 then 372198774213 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell11_5 (s : ℝ) (hx : ((2695 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((2940 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I11 < 0 :=
  cell_neg I11 2695 2940 4096 100000000000 (fun r => if r = 2 then 164464184070 else if r = 9 then 484094252257 else if r = 17 then 764158682436 else 0) (fun r => if r = 1 then 99999999999 else if r = 8 then 392822333018 else if r = 9 then 424475308224 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell11_6 (s : ℝ) (hx : ((2940 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((3185 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I11 < 0 :=
  cell_neg I11 2940 3185 4096 100000000000 (fun r => if r = 2 then 171426232010 else if r = 9 then 552086871782 else if r = 17 then 905278448145 else 0) (fun r => if r = 1 then 99999999999 else if r = 8 then 444850419381 else if r = 9 then 484094252254 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell11_7 (s : ℝ) (hx : ((3185 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((3307 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I11 < 0 :=
  cell_neg I11 3185 3307 4096 100000000000 (fun r => if r = 2 then 175002198569 else if r = 9 then 589426533829 else if r = 17 then 984988805396 else 0) (fun r => if r = 1 then 99999999999 else if r = 8 then 503769462655 else if r = 9 then 552086871779 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell11_8 (s : ℝ) (hx : ((3307 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((3430 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I11 < 0 :=
  cell_neg I11 3307 3430 4096 100000000000 (fun r => if r = 2 then 178682995252 else if r = 9 then 629629276888 else if r = 17 then 1072459277781 else 0) (fun r => if r = 1 then 99999999999 else if r = 8 then 535957699595 else if r = 9 then 589426533826 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell11_9 (s : ℝ) (hx : ((3430 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((3491 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I11 < 0 :=
  cell_neg I11 3430 3491 4096 100000000000 (fun r => if r = 2 then 180537047876 else if r = 9 then 650573014604 else if r = 17 then 1118678695528 else 0) (fun r => if r = 1 then 99999999999 else if r = 8 then 570492148478 else if r = 9 then 629629276885 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell11_10 (s : ℝ) (hx : ((3491 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((3552 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I11 < 0 :=
  cell_neg I11 3491 3552 4096 100000000000 (fun r => if r = 2 then 182410338542 else if r = 9 then 672213416478 else if r = 17 then 1166890016018 else 0) (fun r => if r = 1 then 99999999999 else if r = 8 then 588435695526 else if r = 9 then 650573014601 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell11_11 (s : ℝ) (hx : ((3552 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((3613 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I11 < 0 :=
  cell_neg I11 3552 3613 4096 100000000000 (fun r => if r = 2 then 184303066870 else if r = 9 then 694573656069 else if r = 17 then 1217179083616 else 0) (fun r => if r = 1 then 99999999999 else if r = 8 then 606943616478 else if r = 9 then 672213416475 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell11_12 (s : ℝ) (hx : ((3613 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((3675 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I11 < 0 :=
  cell_neg I11 3613 3675 4096 100000000000 (fun r => if r = 2 then 186246949593 else if r = 9 then 718062766164 else if r = 17 then 1270513956070 else 0) (fun r => if r = 1 then 99999999999 else if r = 8 then 626033662444 else if r = 9 then 694573656066 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell11_13 (s : ℝ) (hx : ((3675 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((3705 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I11 < 0 :=
  cell_neg I11 3675 3705 4096 100000000000 (fun r => if r = 2 then 187194885136 else if r = 9 then 729712000715 else if r = 17 then 1297153933706 else 0) (fun r => if r = 1 then 99999999999 else if r = 8 then 646052044837 else if r = 9 then 718062766161 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell11_14 (s : ℝ) (hx : ((3705 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((3736 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I11 < 0 :=
  cell_neg I11 3705 3736 4096 100000000000 (fun r => if r = 2 then 188179487410 else if r = 9 then 741948120277 else if r = 17 then 1325268869852 else 0) (fun r => if r = 1 then 99999999999 else if r = 8 then 655966912907 else if r = 9 then 729712000712 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell11_15 (s : ℝ) (hx : ((3736 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((3766 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I11 < 0 :=
  cell_neg I11 3736 3766 4096 100000000000 (fun r => if r = 2 then 189137258933 else if r = 9 then 753984850330 else if r = 17 then 1353056941668 else 0) (fun r => if r = 1 then 99999999999 else if r = 8 then 666372158432 else if r = 9 then 741948120274 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell11_16 (s : ℝ) (hx : ((3766 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((3797 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I11 < 0 :=
  cell_neg I11 3766 3797 4096 100000000000 (fun r => if r = 2 then 190132077649 else if r = 9 then 766627987305 else if r = 17 then 1382383537787 else 0) (fun r => if r = 1 then 99999999999 else if r = 8 then 676598876371 else if r = 9 then 753984850327 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell11_17 (s : ℝ) (hx : ((3797 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((3812 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I11 < 0 :=
  cell_neg I11 3797 3812 4096 100000000000 (fun r => if r = 2 then 190615318327 else if r = 9 then 772821526227 else if r = 17 then 1396801175565 else 0) (fun r => if r = 1 then 99999999999 else if r = 8 then 687331395485 else if r = 9 then 766627987302 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell11_18 (s : ℝ) (hx : ((3812 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((3827 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I11 < 0 :=
  cell_neg I11 3812 3827 4096 100000000000 (fun r => if r = 2 then 191099787212 else if r = 9 then 779065102357 else if r = 17 then 1411369182812 else 0) (fun r => if r = 1 then 99999999999 else if r = 8 then 692585501907 else if r = 9 then 772821526224 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell11_19 (s : ℝ) (hx : ((3827 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((3842 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I11 < 0 :=
  cell_neg I11 3827 3842 4096 100000000000 (fun r => if r = 2 then 191585487426 else if r = 9 then 785359119943 else if r = 17 then 1426089127815 else 0) (fun r => if r = 1 then 99999999999 else if r = 8 then 697879771828 else if r = 9 then 779065102354 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell11_20 (s : ℝ) (hx : ((3842 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((3858 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I11 < 0 :=
  cell_neg I11 3842 3858 4096 100000000000 (fun r => if r = 2 then 192104928378 else if r = 9 then 792128795609 else if r = 17 then 1441959657406 else 0) (fun r => if r = 1 then 99999999999 else if r = 8 then 703214512268 else if r = 9 then 785359119940 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell11_21 (s : ℝ) (hx : ((3858 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((3873 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I11 < 0 :=
  cell_neg I11 3858 3873 4096 100000000000 (fun r => if r = 2 then 192593183263 else if r = 9 then 798528353945 else if r = 17 then 1456998647283 else 0) (fun r => if r = 1 then 99999999999 else if r = 8 then 708949858185 else if r = 9 then 792128795606 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell11_22 (s : ℝ) (hx : ((3873 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((3881 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I11 < 0 :=
  cell_neg I11 3873 3881 4096 100000000000 (fun r => if r = 2 then 192854093080 else if r = 9 then 801962565455 else if r = 17 then 1465083472409 else 0) (fun r => if r = 1 then 99999999999 else if r = 8 then 714369220704 else if r = 9 then 798528353942 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell11_23 (s : ℝ) (hx : ((3881 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((3889 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I11 < 0 :=
  cell_neg I11 3881 3889 4096 100000000000 (fun r => if r = 2 then 193115356356 else if r = 9 then 805411546396 else if r = 17 then 1473213159894 else 0) (fun r => if r = 1 then 99999999999 else if r = 8 then 717276466233 else if r = 9 then 801962565452 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell11_24 (s : ℝ) (hx : ((3889 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((3896 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I11 < 0 :=
  cell_neg I11 3889 3896 4096 100000000000 (fun r => if r = 2 then 193344252046 else if r = 9 then 808441570194 else if r = 17 then 1480363633263 else 0) (fun r => if r = 1 then 99999999999 else if r = 8 then 720195543287 else if r = 9 then 805411546393 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell11_25 (s : ℝ) (hx : ((3896 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((3900 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I11 < 0 :=
  cell_neg I11 3896 3900 4096 100000000000 (fun r => if r = 2 then 193475171374 else if r = 9 then 810178127625 else if r = 17 then 1484465189525 else 0) (fun r => if r = 1 then 99999999999 else if r = 8 then 722759479103 else if r = 9 then 808441570191 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell11_26 (s : ℝ) (hx : ((3900 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((3904 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I11 < 0 :=
  cell_neg I11 3900 3904 4096 100000000000 (fun r => if r = 2 then 193606179351 else if r = 9 then 811918415234 else if r = 17 then 1488578109728 else 0) (fun r => if r = 1 then 99999999999 else if r = 8 then 724228681377 else if r = 9 then 810178127622 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell11_27 (s : ℝ) (hx : ((3904 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((3908 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I11 < 0 :=
  cell_neg I11 3904 3908 4096 100000000000 (fun r => if r = 2 then 193737276037 else if r = 9 then 813662441034 else if r = 17 then 1492702425356 else 0) (fun r => if r = 1 then 99999999999 else if r = 8 then 725700870199 else if r = 9 then 811918415231 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell11_28 (s : ℝ) (hx : ((3908 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((3910 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I11 < 0 :=
  cell_neg I11 3908 3910 4096 100000000000 (fun r => if r = 2 then 193802857665 else if r = 9 then 814535858265 else if r = 17 then 1494768866317 else 0) (fun r => if r = 1 then 99999999999 else if r = 8 then 727176051638 else if r = 9 then 813662441031 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell11_29 (s : ℝ) (hx : ((3910 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((3912 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I11 < 0 :=
  cell_neg I11 3910 3912 4096 100000000000 (fun r => if r = 2 then 193868461493 else if r = 9 then 815410213056 else if r = 17 then 1496838167982 else 0) (fun r => if r = 1 then 99999999999 else if r = 8 then 727914766490 else if r = 9 then 814535858262 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell11_30 (s : ℝ) (hx : ((3912 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((3914 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I11 < 0 :=
  cell_neg I11 3912 3914 4096 100000000000 (fun r => if r = 2 then 193934087529 else if r = 9 then 816285506414 else if r = 17 then 1498910334309 else 0) (fun r => if r = 1 then 99999999999 else if r = 8 then 728654231779 else if r = 9 then 815410213053 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell11_31 (s : ℝ) (hx : ((3914 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((3916 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I11 < 0 :=
  cell_neg I11 3914 3916 4096 100000000000 (fun r => if r = 2 then 193999735779 else if r = 9 then 817161739346 else if r = 17 then 1500985369266 else 0) (fun r => if r = 1 then 99999999999 else if r = 8 then 729394448267 else if r = 9 then 816285506411 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell11_32 (s : ℝ) (hx : ((3916 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((3917 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I11 < 0 :=
  cell_neg I11 3916 3917 4096 100000000000 (fun r => if r = 2 then 194032568237 else if r = 9 then 817600208467 else if r = 17 then 1502023963721 else 0) (fun r => if r = 1 then 99999999999 else if r = 8 then 730135416717 else if r = 9 then 817161739343 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell11_33 (s : ℝ) (hx : ((3917 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((3918 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I11 < 0 :=
  cell_neg I11 3917 3918 4096 100000000000 (fun r => if r = 2 then 194065406252 else if r = 9 then 818038912861 else if r = 17 then 1503063276823 else 0) (fun r => if r = 1 then 99999999999 else if r = 8 then 730506183167 else if r = 9 then 817600208464 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell11_34 (s : ℝ) (hx : ((3918 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((3919 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I11 < 0 :=
  cell_neg I11 3918 3919 4096 100000000000 (fun r => if r = 2 then 194098249824 else if r = 9 then 818477852652 else if r = 17 then 1504103309069 else 0) (fun r => if r = 1 then 99999999999 else if r = 8 then 730877137893 else if r = 9 then 818038912858 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem cell11_35 (s : ℝ) (hx : ((3919 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) ≤ s) (hy : s ≤ ((3920 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) :
    Finv s I11 < 0 :=
  cell_neg I11 3919 3920 4096 100000000000 (fun r => if r = 2 then 194131098954 else if r = 9 then 818917027968 else if r = 17 then 1505144060957 else 0) (fun r => if r = 1 then 99999999999 else if r = 8 then 731248280993 else if r = 9 then 818477852649 else 0) (by norm_num) (by norm_num)
    (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) s hx hy
theorem I11_neg (s : ℝ) (h0 : 0 ≤ s) (h1 : s ≤ ((3920 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) : Finv s I11 < 0 := by
  rcases le_total s (((980 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h2 | h2
  · exact cell11_0 s (by rw [Nat.cast_zero, zero_div]; exact h0) h2
  · rcases le_total s (((1470 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h3 | h3
    · exact cell11_1 s h2 h3
    · rcases le_total s (((1960 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h4 | h4
      · exact cell11_2 s h3 h4
      · rcases le_total s (((2450 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h5 | h5
        · exact cell11_3 s h4 h5
        · rcases le_total s (((2695 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h6 | h6
          · exact cell11_4 s h5 h6
          · rcases le_total s (((2940 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h7 | h7
            · exact cell11_5 s h6 h7
            · rcases le_total s (((3185 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h8 | h8
              · exact cell11_6 s h7 h8
              · rcases le_total s (((3307 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h9 | h9
                · exact cell11_7 s h8 h9
                · rcases le_total s (((3430 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h10 | h10
                  · exact cell11_8 s h9 h10
                  · rcases le_total s (((3491 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h11 | h11
                    · exact cell11_9 s h10 h11
                    · rcases le_total s (((3552 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h12 | h12
                      · exact cell11_10 s h11 h12
                      · rcases le_total s (((3613 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h13 | h13
                        · exact cell11_11 s h12 h13
                        · rcases le_total s (((3675 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h14 | h14
                          · exact cell11_12 s h13 h14
                          · rcases le_total s (((3705 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h15 | h15
                            · exact cell11_13 s h14 h15
                            · rcases le_total s (((3736 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h16 | h16
                              · exact cell11_14 s h15 h16
                              · rcases le_total s (((3766 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h17 | h17
                                · exact cell11_15 s h16 h17
                                · rcases le_total s (((3797 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h18 | h18
                                  · exact cell11_16 s h17 h18
                                  · rcases le_total s (((3812 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h19 | h19
                                    · exact cell11_17 s h18 h19
                                    · rcases le_total s (((3827 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h20 | h20
                                      · exact cell11_18 s h19 h20
                                      · rcases le_total s (((3842 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h21 | h21
                                        · exact cell11_19 s h20 h21
                                        · rcases le_total s (((3858 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h22 | h22
                                          · exact cell11_20 s h21 h22
                                          · rcases le_total s (((3873 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h23 | h23
                                            · exact cell11_21 s h22 h23
                                            · rcases le_total s (((3881 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h24 | h24
                                              · exact cell11_22 s h23 h24
                                              · rcases le_total s (((3889 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h25 | h25
                                                · exact cell11_23 s h24 h25
                                                · rcases le_total s (((3896 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h26 | h26
                                                  · exact cell11_24 s h25 h26
                                                  · rcases le_total s (((3900 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h27 | h27
                                                    · exact cell11_25 s h26 h27
                                                    · rcases le_total s (((3904 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h28 | h28
                                                      · exact cell11_26 s h27 h28
                                                      · rcases le_total s (((3908 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h29 | h29
                                                        · exact cell11_27 s h28 h29
                                                        · rcases le_total s (((3910 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h30 | h30
                                                          · exact cell11_28 s h29 h30
                                                          · rcases le_total s (((3912 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h31 | h31
                                                            · exact cell11_29 s h30 h31
                                                            · rcases le_total s (((3914 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h32 | h32
                                                              · exact cell11_30 s h31 h32
                                                              · rcases le_total s (((3916 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h33 | h33
                                                                · exact cell11_31 s h32 h33
                                                                · rcases le_total s (((3917 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h34 | h34
                                                                  · exact cell11_32 s h33 h34
                                                                  · rcases le_total s (((3918 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h35 | h35
                                                                    · exact cell11_33 s h34 h35
                                                                    · rcases le_total s (((3919 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ)) with h36 | h36
                                                                      · exact cell11_34 s h35 h36
                                                                      · exact cell11_35 s h36 h1

/-- t >= 176/4096: the invoice F of EVERY native at the floor with the 1|1 caller (thin 4) is negative -/
theorem split11_ceiling (t : ℝ) (ht : (176 : ℝ) / 4096 ≤ t) (ht1 : t ≤ 1) : Finv (1 - t) I11 < 0 := by
  apply I11_neg (1 - t) (by linarith)
  have : ((3920 : ℕ) : ℝ) / ((4096 : ℕ) : ℝ) = 1 - 176 / 4096 := by norm_num
  rw [this]; linarith

/-- UNCONDITIONAL-NUMERICS instance of the ceiling theorem: argmax split 2|2, thin >= 4, any native meeting the floor:
    F(t) < 0 for t >= 141/4096 (class lemmas hB/hth and the native floor hN stay hypotheses; no NumCert needed). -/
theorem ceiling_split22 (c : InClass 4) (ha : c.a = 2) (hb : c.b = 2) (n : Inv)
    (hN : ∀ s : ℝ, 0 ≤ s → s ≤ 1 → Finv s n ≤ -Nfl s) (t : ℝ) (ht : (141 : ℝ) / 4096 ≤ t) (ht1 : t ≤ 1) :
    Finv (1 - t) (invoice c.ci n (c.a + c.b)) < 0 := by
  have hs0 : (0 : ℝ) ≤ 1 - t := by linarith
  have hs1 : 1 - t ≤ 1 := by linarith
  rw [invoice_F]
  have h1 := c.hB (1 - t) hs0 hs1
  have h2 := hN (1 - t) hs0 hs1
  have h3 : ((c.a + c.b : ℕ) : ℝ) * Finv (1 - t) n ≤ ((c.a + c.b : ℕ) : ℝ) * (-Nfl (1 - t)) :=
    mul_le_mul_of_nonneg_left h2 (Nat.cast_nonneg _)
  have h4 := FBc_th_mono c.a c.b c.hth (1 - t)
  have h5 := split22_ceiling t ht ht1
  rw [I22_F] at h5
  rw [ha, hb] at h1 h3 h4 ⊢
  push_cast at h3 ⊢
  norm_num at h3 h5 ⊢
  linarith

/-- CORRECTED argmax split 1|1 (k = 2, thin >= 4, any native meeting the floor): F(t) < 0 for t >= 176/4096 = .04297 (kernel-checked, 36 cells;
    the sharp value .0419448764 is the certified root, NumCert).  Class lemmas hB/hth and the native floor hN stay hypotheses. -/
theorem ceiling_split11 (c : InClass 4) (ha : c.a = 1) (hb : c.b = 1) (n : Inv)
    (hN : ∀ s : ℝ, 0 ≤ s → s ≤ 1 → Finv s n ≤ -Nfl s) (t : ℝ) (ht : (176 : ℝ) / 4096 ≤ t) (ht1 : t ≤ 1) :
    Finv (1 - t) (invoice c.ci n (c.a + c.b)) < 0 := by
  have hs0 : (0 : ℝ) ≤ 1 - t := by linarith
  have hs1 : 1 - t ≤ 1 := by linarith
  rw [invoice_F]
  have h1 := c.hB (1 - t) hs0 hs1
  have h2 := hN (1 - t) hs0 hs1
  have h3 : ((c.a + c.b : ℕ) : ℝ) * Finv (1 - t) n ≤ ((c.a + c.b : ℕ) : ℝ) * (-Nfl (1 - t)) :=
    mul_le_mul_of_nonneg_left h2 (Nat.cast_nonneg _)
  have h4 := FBc_th_mono c.a c.b c.hth (1 - t)
  have h5 := split11_ceiling t ht ht1
  rw [I11_F] at h5
  rw [ha, hb] at h1 h3 h4 ⊢
  push_cast at h3 ⊢
  norm_num at h3 h5 ⊢
  linarith

#print axioms invoice_F
#print axioms natFloor_F
#print axioms FB_eq
#print axioms ceiling
#print axioms ceiling4
#print axioms ceiling3
#print axioms rp_le_nat
#print axioms rp_ge_nat
#print axioms I22_F
#print axioms split22_ceiling
#print axioms ceiling_split22
#print axioms callerG_F
#print axioms callerG_S
#print axioms callerG_eq_caller_F
#print axioms split11_ceiling
#print axioms ceiling_split11
#print axioms I89_F
#print axioms control_bracket

end JointCeiling
