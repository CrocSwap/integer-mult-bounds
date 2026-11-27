import S008.RecountSharp

namespace S008.Recount.TrueLabel
open S008.NumericalCutoff S008.Recount.Sharp
set_option exponentiation.threshold 6000

def Z : ℕ := 7519517465920988
def B : ℕ := 6201245580657120
def q (j : ℕ) : ℕ := 3*j + (3*j+2).log2 + 3
def den : ℕ := 912825708748800
def eNum (j : ℕ) : ℕ := j+(8*q (j+1)).log2+4
def divisor (j a : ℕ) : ℕ := a*q j*2^j
def scaled (j a : ℕ) : ℕ := den*(3*a*q j+eNum j)/(divisor j a)
def edge (j a : ℕ) : ℕ := 240*(a*q j*8^j+2)
def baseIndices : List (ℕ×ℕ) := (List.range 10).flatMap fun k =>
    let j := k+4
    ([1,2,4] : List ℕ).filterMap fun a =>
      let v := edge j a
      if 240*(2^17+2)<v ∧ v≤B then some (j,a) else none

def corners : List (ℕ×ℕ) := [(0,den/2),(240*(2^17+2),scaled 4 1)] ++
  baseIndices.map fun (j,a) => (edge j a,scaled j a)

def height : ℕ → ℕ → ℕ → List (ℕ×ℕ) → ℕ
  | _,_,h,[] => h
  | p,s,h,(v,t)::cs => height v t (h+(v-p)*s) cs

def exactSlope (t : ℕ×ℕ) : Bool := decide
  (scaled t.1 t.2*divisor t.1 t.2=den*(3*t.2*q t.1+eNum t.1))

theorem exact_height : ((4,1)::baseIndices).all exactSlope = true ∧ corners.length=29 ∧
    (corners.getLast?).map Prod.fst=some B ∧
    height 0 0 0 corners*158055205=890362700843914785456*den := by decide

private theorem phi_nonnegative (n : ℕ) : 0≤phi n := by
  have hn : (0:ℝ)≤n := by positivity
  unfold phi logTwo
  exact Real.rpow_nonneg (mul_nonneg (sq_nonneg _) (div_nonneg
    (Real.log_nonneg (by linarith only [hn])) (Real.log_nonneg (by norm_num)))) _

private theorem phi_upper (n : ℕ) (p l : ℝ) (hp : 0≤p) (hl : logTwo ((n:ℝ)+2)≤l)
    (hc : (n:ℝ)^2*l ≤ p^3) : phi n ≤ p := by
  apply le_of_pow_le_pow_left₀ (by decide : (3:ℕ)≠0) hp
  rw [phi_cube (show 0≤(n:ℝ) by positivity)]
  exact (mul_le_mul_of_nonneg_left hl (sq_nonneg _)).trans hc

private theorem phi_lower (n : ℕ) (p l : ℝ) (_hp : 0≤p) (hl : l≤logTwo ((n:ℝ)+2))
    (hc : p^3 ≤ (n:ℝ)^2*l) : p ≤ phi n := by
  apply le_of_pow_le_pow_left₀ (by decide : (3:ℕ)≠0) (phi_nonnegative n)
  rw [phi_cube (show 0≤(n:ℝ) by positivity)]
  exact hc.trans (mul_le_mul_of_nonneg_left hl (sq_nonneg _))

noncomputable def outerUp : ℝ := 52+(3840022900747926746037349160951770+1:ℝ)/2^112
set_option maxRecDepth 100000 in
set_option maxHeartbeats 2000000 in
private theorem outerUp_bound : logTwo 7519517465920990 ≤ outerUp := by
  apply certify Q (first 7519517465920990 52) 7519517465920990 52 3840022900747926746037349160951770
  all_goals decide

noncomputable def outerLo : ℝ := 52+(3840022900747925749842983953229649:ℝ)/2^112
set_option maxRecDepth 100000 in
set_option maxHeartbeats 2000000 in
private theorem outerLo_bound : outerLo ≤ logTwo 7519517465920989 := by
  apply certify_lower Q (first 7519517465920989 52) 7519517465920989 52 3840022900747925749842983953229649
  all_goals decide

noncomputable def scaleUpLog : ℝ := 52+(3840022900747928738426079576395615+1:ℝ)/2^112
set_option maxRecDepth 100000 in
set_option maxHeartbeats 2000000 in
private theorem scaleUpLog_bound : logTwo 7519517465920992 ≤ scaleUpLog := by
  apply certify Q (first 7519517465920992 52) 7519517465920992 52 3840022900747928738426079576395615
  all_goals decide

noncomputable def scaleUp : ℝ := (174009038091711304297391326834834585:ℝ)/2^80
private theorem scaleUp_bound : phi 7519517465920990 ≤ scaleUp := by
  apply phi_upper (7519517465920990:ℕ) scaleUp scaleUpLog
  · norm_num [scaleUp]
  · rw [show ((7519517465920990:ℕ):ℝ)+2=7519517465920992 by norm_num]
    exact scaleUpLog_bound
  · norm_num [scaleUp,scaleUpLog]

noncomputable def scaleLoLog : ℝ := 52+(3840022900747927742231714368673759:ℝ)/2^112
set_option maxRecDepth 100000 in
set_option maxHeartbeats 2000000 in
private theorem scaleLoLog_bound : scaleLoLog ≤ logTwo 7519517465920991 := by
  apply certify_lower Q (first 7519517465920991 52) 7519517465920991 52 3840022900747927742231714368673759
  all_goals decide

noncomputable def scaleLo : ℝ := (174009038091711288659060395592429417:ℝ)/2^80
private theorem scaleLo_bound : scaleLo ≤ phi 7519517465920989 := by
  apply phi_lower (7519517465920989:ℕ) scaleLo scaleLoLog
  · norm_num [scaleLo]
  · rw [show ((7519517465920989:ℕ):ℝ)+2=7519517465920991 by norm_num]
    exact scaleLoLog_bound
  · norm_num [scaleLo,scaleLoLog]

noncomputable def cornerLoLog : ℝ := 52+(2396138284422878112802184412360941:ℝ)/2^112
set_option maxRecDepth 100000 in
set_option maxHeartbeats 2000000 in
private theorem cornerLoLog_bound : cornerLoLog ≤ logTwo 6201245580657122 := by
  apply certify_lower Q (first 6201245580657122 52) 6201245580657122 52 2396138284422878112802184412360941
  all_goals decide

noncomputable def cornerLo : ℝ := (152756295623092695295131896528686634:ℝ)/2^80
private theorem cornerLo_bound : cornerLo ≤ phi 6201245580657120 := by
  apply phi_lower (6201245580657120:ℕ) cornerLo cornerLoLog
  · norm_num [cornerLo]
  · rw [show ((6201245580657120:ℕ):ℝ)+2=6201245580657122 by norm_num]
    exact cornerLoLog_bound
  · norm_num [cornerLo,cornerLoLog]

noncomputable def cornerUpLog : ℝ := 52+(2396138284422878112802184412360941+1:ℝ)/2^112
set_option maxRecDepth 100000 in
set_option maxHeartbeats 2000000 in
private theorem cornerUpLog_bound : logTwo 6201245580657122 ≤ cornerUpLog := by
  apply certify Q (first 6201245580657122 52) 6201245580657122 52 2396138284422878112802184412360941
  all_goals decide

noncomputable def cornerUp : ℝ := (152756295623092695295131896528686635:ℝ)/2^80
private theorem cornerUp_bound : phi 6201245580657120 ≤ cornerUp := by
  apply phi_upper (6201245580657120:ℕ) cornerUp cornerUpLog
  · norm_num [cornerUp]
  · rw [show ((6201245580657120:ℕ):ℝ)+2=6201245580657122 by norm_num]
    exact cornerUpLog_bound
  · norm_num [cornerUp,cornerUpLog]

noncomputable def peak : ℝ := 890362700843914785456/158055205
noncomputable def invoice (v : ℝ) : ℝ := 183+4*logTwo (v+2)+48*phi (v+2)+peak-(159/4)*phi B

theorem passing : invoice Z + 53248/10^9 < (Z:ℝ)/1000 := by
  have high : 183+4*outerUp+48*scaleUp+peak-(159/4)*cornerLo+53248/10^9 < (Z:ℝ)/1000 := by
    norm_num [outerUp,scaleUp,peak,cornerLo,Z]
  unfold invoice
  rw [show (Z:ℝ)+2=7519517465920990 by norm_num [Z],show (B:ℝ)=6201245580657120 by norm_num [B]]
  linarith only [high,outerUp_bound,scaleUp_bound,cornerLo_bound]

theorem preceding : ((Z:ℝ)-1)/1000 + 325836/10^9 < invoice ((Z:ℝ)-1) := by
  have low : ((Z:ℝ)-1)/1000+325836/10^9 < 183+4*outerLo+48*scaleLo+peak-(159/4)*cornerUp := by
    norm_num [outerLo,scaleLo,peak,cornerUp,Z]
  unfold invoice
  rw [show (Z:ℝ)-1+2=7519517465920989 by norm_num [Z],show (B:ℝ)=6201245580657120 by norm_num [B]]
  linarith only [low,outerLo_bound,scaleLo_bound,cornerUp_bound]

end S008.Recount.TrueLabel
