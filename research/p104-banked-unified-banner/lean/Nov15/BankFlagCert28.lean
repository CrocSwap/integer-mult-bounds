/-
BankFlagCertFlagX28 (generated).  Exact certificate CertFlagX28, no hypothesis.
Convex piece-wise envelope (SafeCertGen.piece_le) on grid 991/50000, 1983/100000, 62/3125, 3/20, 27/100, 11/25, 63/100, 17/20, 1; rational enclosures a/10^24 <= r^(1-t) <= (a+1)/10^24
certified by integer inequalities a^Q <= r^(Q-k)*D^Q (decide +kernel: kernel Nat arithmetic, no native_decide).
-/
import Nov15.SafeRungsPrice
import Nov15.SafeCertGen

open SafeCertGen SafeRungsPrice

namespace BankFlagCertFlagX28

def TB : List (ℕ × ℕ) := [(9, 416), (17, 416), (25, 416), (33, 416), (41, 416), (49, 416), (57, 416), (65, 416), (129, 208)]
def PB : List (ℕ × ℕ) := [(1, 384), (8, 640), (9, 32), (16, 416), (24, 416), (32, 416), (40, 416), (48, 416), (56, 416)]
/-- DATA: the 16 calls; NC0: 400 mains at g(8); excess mass X=28 at D9=g(9)-g(8) (premise: mass bounds, BankFlagMass). -/
noncomputable def FceilBank (s : ℝ) : ℝ := cdat s TB - cdat s PB - 16 * (400 * 8 ^ s + 28 * (9 ^ s - 8 ^ s))
def cs : List (ℝ × ℝ) := [(-64, 9), (416, 17), (416, 25), (416, 33), (416, 41), (416, 49), (416, 57), (416, 65), (208, 129), (-384, 1), (-6592, 8), (-416, 16), (-416, 24), (-416, 32), (-416, 40), (-416, 48), (-416, 56)]

theorem cs_pos : ∀ p ∈ cs, 0 < p.2 := by
  intro p hp
  simp only [cs, List.mem_cons, List.not_mem_nil, or_false] at hp
  rcases hp with rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl <;> norm_num

theorem hi_8_991_50000 : phi 8 (991/50000:ℝ) ≤ (7676985908710385909419273:ℝ)/1000000000000000000000000 :=
  enc_hi 8 991 50000 7676985908710385909419273 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_8_1983_100000 : phi 8 (1983/100000:ℝ) ≤ (7676826271936033731595023:ℝ)/1000000000000000000000000 :=
  enc_hi 8 1983 100000 7676826271936033731595023 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem lo_8_1983_100000 : (7676826271936033731595022:ℝ)/1000000000000000000000000 ≤ phi 8 (1983/100000:ℝ) :=
  enc_lo 8 1983 100000 7676826271936033731595022 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_8_62_3125 : phi 8 (62/3125:ℝ) ≤ (7676666638481200441600677:ℝ)/1000000000000000000000000 :=
  enc_hi 8 62 3125 7676666638481200441600677 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem lo_8_62_3125 : (7676666638481200441600676:ℝ)/1000000000000000000000000 ≤ phi 8 (62/3125:ℝ) :=
  enc_lo 8 62 3125 7676666638481200441600676 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_8_3_20 : phi 8 (3/20:ℝ) ≤ (5856342783782501682774526:ℝ)/1000000000000000000000000 :=
  enc_hi 8 3 20 5856342783782501682774526 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem lo_8_3_20 : (5856342783782501682774525:ℝ)/1000000000000000000000000 ≤ phi 8 (3/20:ℝ) :=
  enc_lo 8 3 20 5856342783782501682774525 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_8_27_100 : phi 8 (27/100:ℝ) ≤ (4563054863473694534679341:ℝ)/1000000000000000000000000 :=
  enc_hi 8 27 100 4563054863473694534679341 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem lo_8_27_100 : (4563054863473694534679340:ℝ)/1000000000000000000000000 ≤ phi 8 (27/100:ℝ) :=
  enc_lo 8 27 100 4563054863473694534679340 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_8_11_25 : phi 8 (11/25:ℝ) ≤ (3204279510358488308730308:ℝ)/1000000000000000000000000 :=
  enc_hi 8 11 25 3204279510358488308730308 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem lo_8_11_25 : (3204279510358488308730307:ℝ)/1000000000000000000000000 ≤ phi 8 (11/25:ℝ) :=
  enc_lo 8 11 25 3204279510358488308730307 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_8_63_100 : phi 8 (63/100:ℝ) ≤ (2158456473008854384529807:ℝ)/1000000000000000000000000 :=
  enc_hi 8 63 100 2158456473008854384529807 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem lo_8_63_100 : (2158456473008854384529806:ℝ)/1000000000000000000000000 ≤ phi 8 (63/100:ℝ) :=
  enc_lo 8 63 100 2158456473008854384529806 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem lo_8_17_20 : (1366040256754395518851229:ℝ)/1000000000000000000000000 ≤ phi 8 (17/20:ℝ) :=
  enc_lo 8 17 20 1366040256754395518851229 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_9_991_50000 : phi 9 (991/50000:ℝ) ≤ (8616470845896860548462630:ℝ)/1000000000000000000000000 :=
  enc_hi 9 991 50000 8616470845896860548462630 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_9_1983_100000 : phi 9 (1983/100000:ℝ) ≤ (8616281524761648365786744:ℝ)/1000000000000000000000000 :=
  enc_hi 9 1983 100000 8616281524761648365786744 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem lo_9_1983_100000 : (8616281524761648365786743:ℝ)/1000000000000000000000000 ≤ phi 9 (1983/100000:ℝ) :=
  enc_lo 9 1983 100000 8616281524761648365786743 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_9_62_3125 : phi 9 (62/3125:ℝ) ≤ (8616092207786200996230102:ℝ)/1000000000000000000000000 :=
  enc_hi 9 62 3125 8616092207786200996230102 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem lo_9_62_3125 : (8616092207786200996230101:ℝ)/1000000000000000000000000 ≤ phi 9 (62/3125:ℝ) :=
  enc_lo 9 62 3125 8616092207786200996230101 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_9_3_20 : phi 9 (3/20:ℝ) ≤ (6473007839923779298664847:ℝ)/1000000000000000000000000 :=
  enc_hi 9 3 20 6473007839923779298664847 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem lo_9_3_20 : (6473007839923779298664846:ℝ)/1000000000000000000000000 ≤ phi 9 (3/20:ℝ) :=
  enc_lo 9 3 20 6473007839923779298664846 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_9_27_100 : phi 9 (27/100:ℝ) ≤ (4972754646800378493123114:ℝ)/1000000000000000000000000 :=
  enc_hi 9 27 100 4972754646800378493123114 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem lo_9_27_100 : (4972754646800378493123113:ℝ)/1000000000000000000000000 ≤ phi 9 (27/100:ℝ) :=
  enc_lo 9 27 100 4972754646800378493123113 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_9_11_25 : phi 9 (11/25:ℝ) ≤ (3422754934844259461519433:ℝ)/1000000000000000000000000 :=
  enc_hi 9 11 25 3422754934844259461519433 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem lo_9_11_25 : (3422754934844259461519432:ℝ)/1000000000000000000000000 ≤ phi 9 (11/25:ℝ) :=
  enc_lo 9 11 25 3422754934844259461519432 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_9_63_100 : phi 9 (63/100:ℝ) ≤ (2254601172360982324799830:ℝ)/1000000000000000000000000 :=
  enc_hi 9 63 100 2254601172360982324799830 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem lo_9_63_100 : (2254601172360982324799829:ℝ)/1000000000000000000000000 ≤ phi 9 (63/100:ℝ) :=
  enc_lo 9 63 100 2254601172360982324799829 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem lo_9_17_20 : (1390389170315909340485254:ℝ)/1000000000000000000000000 ≤ phi 9 (17/20:ℝ) :=
  enc_lo 9 17 20 1390389170315909340485254 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_16_991_50000 : phi 16 (991/50000:ℝ) ≤ (15144478555810160978337610:ℝ)/1000000000000000000000000 :=
  enc_hi 16 991 50000 15144478555810160978337610 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_16_1983_100000 : phi 16 (1983/100000:ℝ) ≤ (15144058667526595060010076:ℝ)/1000000000000000000000000 :=
  enc_hi 16 1983 100000 15144058667526595060010076 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem lo_16_1983_100000 : (15144058667526595060010075:ℝ)/1000000000000000000000000 ≤ phi 16 (1983/100000:ℝ) :=
  enc_lo 16 1983 100000 15144058667526595060010075 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_16_62_3125 : phi 16 (62/3125:ℝ) ≤ (15143638790884642950055852:ℝ)/1000000000000000000000000 :=
  enc_hi 16 62 3125 15143638790884642950055852 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem lo_16_62_3125 : (15143638790884642950055851:ℝ)/1000000000000000000000000 ≤ phi 16 (62/3125:ℝ) :=
  enc_lo 16 62 3125 15143638790884642950055851 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_16_3_20 : phi 16 (3/20:ℝ) ≤ (10556063286183154074992016:ℝ)/1000000000000000000000000 :=
  enc_hi 16 3 20 10556063286183154074992016 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem lo_16_3_20 : (10556063286183154074992015:ℝ)/1000000000000000000000000 ≤ phi 16 (3/20:ℝ) :=
  enc_lo 16 3 20 10556063286183154074992015 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_16_27_100 : phi 16 (27/100:ℝ) ≤ (7568461173804767260040896:ℝ)/1000000000000000000000000 :=
  enc_hi 16 27 100 7568461173804767260040896 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem lo_16_27_100 : (7568461173804767260040895:ℝ)/1000000000000000000000000 ≤ phi 16 (27/100:ℝ) :=
  enc_lo 16 27 100 7568461173804767260040895 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_16_11_25 : phi 16 (11/25:ℝ) ≤ (4723970645718121598201863:ℝ)/1000000000000000000000000 :=
  enc_hi 16 11 25 4723970645718121598201863 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem lo_16_11_25 : (4723970645718121598201862:ℝ)/1000000000000000000000000 ≤ phi 16 (11/25:ℝ) :=
  enc_lo 16 11 25 4723970645718121598201862 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_16_63_100 : phi 16 (63/100:ℝ) ≤ (2789487332700810840550984:ℝ)/1000000000000000000000000 :=
  enc_hi 16 63 100 2789487332700810840550984 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem lo_16_63_100 : (2789487332700810840550983:ℝ)/1000000000000000000000000 ≤ phi 16 (63/100:ℝ) :=
  enc_lo 16 63 100 2789487332700810840550983 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem lo_16_17_20 : (1515716566510398082347259:ℝ)/1000000000000000000000000 ≤ phi 16 (17/20:ℝ) :=
  enc_lo 16 17 20 1515716566510398082347259 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_17_1983_100000 : phi 17 (1983/100000:ℝ) ≤ (16071230104242913644320127:ℝ)/1000000000000000000000000 :=
  enc_hi 17 1983 100000 16071230104242913644320127 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_17_62_3125 : phi 17 (62/3125:ℝ) ≤ (16070774778457252171381767:ℝ)/1000000000000000000000000 :=
  enc_hi 17 62 3125 16070774778457252171381767 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_17_3_20 : phi 17 (3/20:ℝ) ≤ (11114286384685567659471384:ℝ)/1000000000000000000000000 :=
  enc_hi 17 3 20 11114286384685567659471384 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_17_27_100 : phi 17 (27/100:ℝ) ≤ (7910933113741146990645810:ℝ)/1000000000000000000000000 :=
  enc_hi 17 27 100 7910933113741146990645810 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_17_11_25 : phi 17 (11/25:ℝ) ≤ (4887101916434683345559587:ℝ)/1000000000000000000000000 :=
  enc_hi 17 11 25 4887101916434683345559587 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_17_63_100 : phi 17 (63/100:ℝ) ≤ (2852765678666218744854941:ℝ)/1000000000000000000000000 :=
  enc_hi 17 63 100 2852765678666218744854941 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_17_17_20 : phi 17 (17/20:ℝ) ≤ (1529562889743815436100792:ℝ)/1000000000000000000000000 :=
  enc_hi 17 17 20 1529562889743815436100792 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_17_1_1 : phi 17 (1:ℝ) ≤ (1000000000000000000000001:ℝ)/1000000000000000000000000 :=
  enc_hi 17 1 1 1000000000000000000000001 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_24_991_50000 : phi 24 (991/50000:ℝ) ≤ (22534890644396759324066849:ℝ)/1000000000000000000000000 :=
  enc_hi 24 991 50000 22534890644396759324066849 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_24_1983_100000 : phi 24 (1983/100000:ℝ) ≤ (22534174484821499035413761:ℝ)/1000000000000000000000000 :=
  enc_hi 24 1983 100000 22534174484821499035413761 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem lo_24_1983_100000 : (22534174484821499035413760:ℝ)/1000000000000000000000000 ≤ phi 24 (1983/100000:ℝ) :=
  enc_lo 24 1983 100000 22534174484821499035413760 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_24_62_3125 : phi 24 (62/3125:ℝ) ≤ (22533458348005813902033256:ℝ)/1000000000000000000000000 :=
  enc_hi 24 62 3125 22533458348005813902033256 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem lo_24_62_3125 : (22533458348005813902033255:ℝ)/1000000000000000000000000 ≤ phi 24 (62/3125:ℝ) :=
  enc_lo 24 62 3125 22533458348005813902033255 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_24_3_20 : phi 24 (3/20:ℝ) ≤ (14899769690160642867898149:ℝ)/1000000000000000000000000 :=
  enc_hi 24 3 20 14899769690160642867898149 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem lo_24_3_20 : (14899769690160642867898148:ℝ)/1000000000000000000000000 ≤ phi 24 (3/20:ℝ) :=
  enc_lo 24 3 20 14899769690160642867898148 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_24_27_100 : phi 24 (27/100:ℝ) ≤ (10175463632660441334046422:ℝ)/1000000000000000000000000 :=
  enc_hi 24 27 100 10175463632660441334046422 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem lo_24_27_100 : (10175463632660441334046421:ℝ)/1000000000000000000000000 ≤ phi 24 (27/100:ℝ) :=
  enc_lo 24 27 100 10175463632660441334046421 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_24_11_25 : phi 24 (11/25:ℝ) ≤ (5928137869105510860131135:ℝ)/1000000000000000000000000 :=
  enc_hi 24 11 25 5928137869105510860131135 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem lo_24_11_25 : (5928137869105510860131134:ℝ)/1000000000000000000000000 ≤ phi 24 (11/25:ℝ) :=
  enc_lo 24 11 25 5928137869105510860131134 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_24_63_100 : phi 24 (63/100:ℝ) ≤ (3240993495544224076558562:ℝ)/1000000000000000000000000 :=
  enc_hi 24 63 100 3240993495544224076558562 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem lo_24_63_100 : (3240993495544224076558561:ℝ)/1000000000000000000000000 ≤ phi 24 (63/100:ℝ) :=
  enc_lo 24 63 100 3240993495544224076558561 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem lo_24_17_20 : (1610763152657914834363615:ℝ)/1000000000000000000000000 ≤ phi 24 (17/20:ℝ) :=
  enc_lo 24 17 20 1610763152657914834363615 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_25_1983_100000 : phi 25 (1983/100000:ℝ) ≤ (23454104633738678096859911:ℝ)/1000000000000000000000000 :=
  enc_hi 25 1983 100000 23454104633738678096859911 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_25_62_3125 : phi 25 (62/3125:ℝ) ≤ (23453349687385141406792350:ℝ)/1000000000000000000000000 :=
  enc_hi 25 62 3125 23453349687385141406792350 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_25_3_20 : phi 25 (3/20:ℝ) ≤ (15425846568000240914266380:ℝ)/1000000000000000000000000 :=
  enc_hi 25 3 20 15425846568000240914266380 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_25_27_100 : phi 25 (27/100:ℝ) ≤ (10483256361580175788765467:ℝ)/1000000000000000000000000 :=
  enc_hi 25 27 100 10483256361580175788765467 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_25_11_25 : phi 25 (11/25:ℝ) ≤ (6065217855863152132602166:ℝ)/1000000000000000000000000 :=
  enc_hi 25 11 25 6065217855863152132602166 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_25_63_100 : phi 25 (63/100:ℝ) ≤ (3290317468810911613362903:ℝ)/1000000000000000000000000 :=
  enc_hi 25 63 100 3290317468810911613362903 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_25_17_20 : phi 25 (17/20:ℝ) ≤ (1620656596692762435150455:ℝ)/1000000000000000000000000 :=
  enc_hi 25 17 20 1620656596692762435150455 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_25_1_1 : phi 25 (1:ℝ) ≤ (1000000000000000000000001:ℝ)/1000000000000000000000000 :=
  enc_hi 25 1 1 1000000000000000000000001 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_32_991_50000 : phi 32 (991/50000:ℝ) ≤ (29875687340674294205007560:ℝ)/1000000000000000000000000 :=
  enc_hi 32 991 50000 29875687340674294205007560 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_32_1983_100000 : phi 32 (1983/100000:ℝ) ≤ (29874651946194043019143989:ℝ)/1000000000000000000000000 :=
  enc_hi 32 1983 100000 29874651946194043019143989 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem lo_32_1983_100000 : (29874651946194043019143988:ℝ)/1000000000000000000000000 ≤ phi 32 (1983/100000:ℝ) :=
  enc_lo 32 1983 100000 29874651946194043019143988 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_32_62_3125 : phi 32 (62/3125:ℝ) ≤ (29873616587597208255137622:ℝ)/1000000000000000000000000 :=
  enc_hi 32 62 3125 29873616587597208255137622 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem lo_32_62_3125 : (29873616587597208255137621:ℝ)/1000000000000000000000000 ≤ phi 32 (62/3125:ℝ) :=
  enc_lo 32 62 3125 29873616587597208255137621 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_32_3_20 : phi 32 (3/20:ℝ) ≤ (19027313840043537067480000:ℝ)/1000000000000000000000000 :=
  enc_hi 32 3 20 19027313840043537067480000 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem lo_32_3_20 : (19027313840043537067479999:ℝ)/1000000000000000000000000 ≤ phi 32 (3/20:ℝ) :=
  enc_lo 32 3 20 19027313840043537067479999 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_32_27_100 : phi 32 (27/100:ℝ) ≤ (12553345566348011771597606:ℝ)/1000000000000000000000000 :=
  enc_hi 32 27 100 12553345566348011771597606 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem lo_32_27_100 : (12553345566348011771597605:ℝ)/1000000000000000000000000 ≤ phi 32 (27/100:ℝ) :=
  enc_lo 32 27 100 12553345566348011771597605 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_32_11_25 : phi 32 (11/25:ℝ) ≤ (6964404506368993113090161:ℝ)/1000000000000000000000000 :=
  enc_hi 32 11 25 6964404506368993113090161 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem lo_32_11_25 : (6964404506368993113090160:ℝ)/1000000000000000000000000 ≤ phi 32 (11/25:ℝ) :=
  enc_lo 32 11 25 6964404506368993113090160 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_32_63_100 : phi 32 (63/100:ℝ) ≤ (3605001850443320973824025:ℝ)/1000000000000000000000000 :=
  enc_hi 32 63 100 3605001850443320973824025 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem lo_32_63_100 : (3605001850443320973824024:ℝ)/1000000000000000000000000 ≤ phi 32 (63/100:ℝ) :=
  enc_lo 32 63 100 3605001850443320973824024 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem lo_32_17_20 : (1681792830507429086062250:ℝ)/1000000000000000000000000 ≤ phi 32 (17/20:ℝ) :=
  enc_lo 32 17 20 1681792830507429086062250 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_33_1983_100000 : phi 33 (1983/100000:ℝ) ≤ (30789441307777684757620425:ℝ)/1000000000000000000000000 :=
  enc_hi 33 1983 100000 30789441307777684757620425 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_33_62_3125 : phi 33 (62/3125:ℝ) ≤ (30788364771454921667813524:ℝ)/1000000000000000000000000 :=
  enc_hi 33 62 3125 30788364771454921667813524 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_33_3_20 : phi 33 (3/20:ℝ) ≤ (19531556258452538078439195:ℝ)/1000000000000000000000000 :=
  enc_hi 33 3 20 19531556258452538078439195 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_33_27_100 : phi 33 (27/100:ℝ) ≤ (12838526330030258519355421:ℝ)/1000000000000000000000000 :=
  enc_hi 33 27 100 12838526330030258519355421 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_33_11_25 : phi 33 (11/25:ℝ) ≤ (7085456014333451311722874:ℝ)/1000000000000000000000000 :=
  enc_hi 33 11 25 7085456014333451311722874 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_33_63_100 : phi 33 (63/100:ℝ) ≤ (3646281195781395728926953:ℝ)/1000000000000000000000000 :=
  enc_hi 33 63 100 3646281195781395728926953 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_33_17_20 : phi 33 (17/20:ℝ) ≤ (1689573506756217421119274:ℝ)/1000000000000000000000000 :=
  enc_hi 33 17 20 1689573506756217421119274 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_33_1_1 : phi 33 (1:ℝ) ≤ (1000000000000000000000001:ℝ)/1000000000000000000000000 :=
  enc_hi 33 1 1 1000000000000000000000001 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_40_991_50000 : phi 40 (991/50000:ℝ) ≤ (37179809677558049640642832:ℝ)/1000000000000000000000000 :=
  enc_hi 40 991 50000 37179809677558049640642832 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_40_1983_100000 : phi 40 (1983/100000:ℝ) ≤ (37178438184494293983929318:ℝ)/1000000000000000000000000 :=
  enc_hi 40 1983 100000 37178438184494293983929318 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem lo_40_1983_100000 : (37178438184494293983929317:ℝ)/1000000000000000000000000 ≤ phi 40 (1983/100000:ℝ) :=
  enc_lo 40 1983 100000 37178438184494293983929317 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_40_62_3125 : phi 40 (62/3125:ℝ) ≤ (37177066742022331029835699:ℝ)/1000000000000000000000000 :=
  enc_hi 40 62 3125 37177066742022331029835699 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem lo_40_62_3125 : (37177066742022331029835698:ℝ)/1000000000000000000000000 ≤ phi 40 (62/3125:ℝ) :=
  enc_lo 40 62 3125 37177066742022331029835698 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_40_3_20 : phi 40 (3/20:ℝ) ≤ (23001226394252433556918295:ℝ)/1000000000000000000000000 :=
  enc_hi 40 3 20 23001226394252433556918295 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem lo_40_3_20 : (23001226394252433556918294:ℝ)/1000000000000000000000000 ≤ phi 40 (3/20:ℝ) :=
  enc_lo 40 3 20 23001226394252433556918294 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_40_27_100 : phi 40 (27/100:ℝ) ≤ (14774193871559801387209028:ℝ)/1000000000000000000000000 :=
  enc_hi 40 27 100 14774193871559801387209028 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem lo_40_27_100 : (14774193871559801387209027:ℝ)/1000000000000000000000000 ≤ phi 40 (27/100:ℝ) :=
  enc_lo 40 27 100 14774193871559801387209027 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_40_11_25 : phi 40 (11/25:ℝ) ≤ (7891391598736293521737107:ℝ)/1000000000000000000000000 :=
  enc_hi 40 11 25 7891391598736293521737107 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem lo_40_11_25 : (7891391598736293521737106:ℝ)/1000000000000000000000000 ≤ phi 40 (11/25:ℝ) :=
  enc_lo 40 11 25 7891391598736293521737106 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_40_63_100 : phi 40 (63/100:ℝ) ≤ (3915274328099089739953733:ℝ)/1000000000000000000000000 :=
  enc_hi 40 63 100 3915274328099089739953733 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem lo_40_63_100 : (3915274328099089739953732:ℝ)/1000000000000000000000000 ≤ phi 40 (63/100:ℝ) :=
  enc_lo 40 63 100 3915274328099089739953732 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem lo_40_17_20 : (1739037706702249353377766:ℝ)/1000000000000000000000000 ≤ phi 40 (17/20:ℝ) :=
  enc_lo 40 17 20 1739037706702249353377766 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_41_1983_100000 : phi 41 (1983/100000:ℝ) ≤ (38089244002174142923140041:ℝ)/1000000000000000000000000 :=
  enc_hi 41 1983 100000 38089244002174142923140041 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_41_62_3125 : phi 41 (62/3125:ℝ) ≤ (38087829556911843968609216:ℝ)/1000000000000000000000000 :=
  enc_hi 41 62 3125 38087829556911843968609216 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_41_3_20 : phi 41 (3/20:ℝ) ≤ (23489094666520747446882529:ℝ)/1000000000000000000000000 :=
  enc_hi 41 3 20 23489094666520747446882529 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_41_27_100 : phi 41 (27/100:ℝ) ≤ (15042922408082054033525786:ℝ)/1000000000000000000000000 :=
  enc_hi 41 27 100 15042922408082054033525786 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_41_11_25 : phi 41 (11/25:ℝ) ≤ (8001270626291626665930423:ℝ)/1000000000000000000000000 :=
  enc_hi 41 11 25 8001270626291626665930423 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_41_63_100 : phi 41 (63/100:ℝ) ≤ (3951209223835537442010981:ℝ)/1000000000000000000000000 :=
  enc_hi 41 63 100 3951209223835537442010981 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_41_17_20 : phi 41 (17/20:ℝ) ≤ (1745490857867660998433844:ℝ)/1000000000000000000000000 :=
  enc_hi 41 17 20 1745490857867660998433844 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_41_1_1 : phi 41 (1:ℝ) ≤ (1000000000000000000000001:ℝ)/1000000000000000000000000 :=
  enc_hi 41 1 1 1000000000000000000000001 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_48_991_50000 : phi 48 (991/50000:ℝ) ≤ (44454838419642654725998168:ℝ)/1000000000000000000000000 :=
  enc_hi 48 991 50000 44454838419642654725998168 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_48_1983_100000 : phi 48 (1983/100000:ℝ) ≤ (44453117516798375117224421:ℝ)/1000000000000000000000000 :=
  enc_hi 48 1983 100000 44453117516798375117224421 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem lo_48_1983_100000 : (44453117516798375117224420:ℝ)/1000000000000000000000000 ≤ phi 48 (1983/100000:ℝ) :=
  enc_lo 48 1983 100000 44453117516798375117224420 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_48_62_3125 : phi 48 (62/3125:ℝ) ≤ (44451396680572414340109879:ℝ)/1000000000000000000000000 :=
  enc_hi 48 62 3125 44451396680572414340109879 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem lo_48_62_3125 : (44451396680572414340109878:ℝ)/1000000000000000000000000 ≤ phi 48 (62/3125:ℝ) :=
  enc_lo 48 62 3125 44451396680572414340109878 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_48_3_20 : phi 48 (3/20:ℝ) ≤ (26856848652104212372378912:ℝ)/1000000000000000000000000 :=
  enc_hi 48 3 20 26856848652104212372378912 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem lo_48_3_20 : (26856848652104212372378911:ℝ)/1000000000000000000000000 ≤ phi 48 (3/20:ℝ) :=
  enc_lo 48 3 20 26856848652104212372378911 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_48_27_100 : phi 48 (27/100:ℝ) ≤ (16877421756578652486718323:ℝ)/1000000000000000000000000 :=
  enc_hi 48 27 100 16877421756578652486718323 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem lo_48_27_100 : (16877421756578652486718322:ℝ)/1000000000000000000000000 ≤ phi 48 (27/100:ℝ) :=
  enc_lo 48 27 100 16877421756578652486718322 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_48_11_25 : phi 48 (11/25:ℝ) ≤ (8739671176279918106478672:ℝ)/1000000000000000000000000 :=
  enc_hi 48 11 25 8739671176279918106478672 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem lo_48_11_25 : (8739671176279918106478671:ℝ)/1000000000000000000000000 ≤ phi 48 (11/25:ℝ) :=
  enc_lo 48 11 25 8739671176279918106478671 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_48_63_100 : phi 48 (63/100:ℝ) ≤ (4188507118044278593397019:ℝ)/1000000000000000000000000 :=
  enc_hi 48 63 100 4188507118044278593397019 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem lo_48_63_100 : (4188507118044278593397018:ℝ)/1000000000000000000000000 ≤ phi 48 (63/100:ℝ) :=
  enc_lo 48 63 100 4188507118044278593397018 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem lo_48_17_20 : (1787253620920980199152258:ℝ)/1000000000000000000000000 ≤ phi 48 (17/20:ℝ) :=
  enc_lo 48 17 20 1787253620920980199152258 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_49_1983_100000 : phi 49 (1983/100000:ℝ) ≤ (45360673246262694677149894:ℝ)/1000000000000000000000000 :=
  enc_hi 49 1983 100000 45360673246262694677149894 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_49_62_3125 : phi 49 (62/3125:ℝ) ≤ (45358907924725730757238855:ℝ)/1000000000000000000000000 :=
  enc_hi 49 62 3125 45358907924725730757238855 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_49_3_20 : phi 49 (3/20:ℝ) ≤ (27331701439859054333906956:ℝ)/1000000000000000000000000 :=
  enc_hi 49 3 20 27331701439859054333906956 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_49_27_100 : phi 49 (27/100:ℝ) ≤ (17133383599655813471524560:ℝ)/1000000000000000000000000 :=
  enc_hi 49 27 100 17133383599655813471524560 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_49_11_25 : phi 49 (11/25:ℝ) ≤ (8841171291775487234155612:ℝ)/1000000000000000000000000 :=
  enc_hi 49 11 25 8841171291775487234155612 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_49_63_100 : phi 49 (63/100:ℝ) ≤ (4220584013515329193605384:ℝ)/1000000000000000000000000 :=
  enc_hi 49 63 100 4220584013515329193605384 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_49_17_20 : phi 49 (17/20:ℝ) ≤ (1792789962520997228317172:ℝ)/1000000000000000000000000 :=
  enc_hi 49 17 20 1792789962520997228317172 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_49_1_1 : phi 49 (1:ℝ) ≤ (1000000000000000000000001:ℝ)/1000000000000000000000000 :=
  enc_hi 49 1 1 1000000000000000000000001 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_56_991_50000 : phi 56 (991/50000:ℝ) ≤ (51705761702359805798678000:ℝ)/1000000000000000000000000 :=
  enc_hi 56 991 50000 51705761702359805798678000 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_56_1983_100000 : phi 56 (1983/100000:ℝ) ≤ (51703680405496952635015255:ℝ)/1000000000000000000000000 :=
  enc_hi 56 1983 100000 51703680405496952635015255 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem lo_56_1983_100000 : (51703680405496952635015254:ℝ)/1000000000000000000000000 ≤ phi 56 (1983/100000:ℝ) :=
  enc_lo 56 1983 100000 51703680405496952635015254 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_56_62_3125 : phi 56 (62/3125:ℝ) ≤ (51701599192411931741923651:ℝ)/1000000000000000000000000 :=
  enc_hi 56 62 3125 51701599192411931741923651 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem lo_56_62_3125 : (51701599192411931741923650:ℝ)/1000000000000000000000000 ≤ phi 56 (62/3125:ℝ) :=
  enc_lo 56 62 3125 51701599192411931741923650 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_56_3_20 : phi 56 (3/20:ℝ) ≤ (30616801812968475027982362:ℝ)/1000000000000000000000000 :=
  enc_hi 56 3 20 30616801812968475027982362 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem lo_56_3_20 : (30616801812968475027982361:ℝ)/1000000000000000000000000 ≤ phi 56 (3/20:ℝ) :=
  enc_lo 56 3 20 30616801812968475027982361 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_56_27_100 : phi 56 (27/100:ℝ) ≤ (18887621005759085694739151:ℝ)/1000000000000000000000000 :=
  enc_hi 56 27 100 18887621005759085694739151 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem lo_56_27_100 : (18887621005759085694739150:ℝ)/1000000000000000000000000 ≤ phi 56 (27/100:ℝ) :=
  enc_lo 56 27 100 18887621005759085694739150 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_56_11_25 : phi 56 (11/25:ℝ) ≤ (9527639036258389176089621:ℝ)/1000000000000000000000000 :=
  enc_hi 56 11 25 9527639036258389176089621 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem lo_56_11_25 : (9527639036258389176089620:ℝ)/1000000000000000000000000 ≤ phi 56 (11/25:ℝ) :=
  enc_lo 56 11 25 9527639036258389176089620 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_56_63_100 : phi 56 (63/100:ℝ) ≤ (4434345929245096251086307:ℝ)/1000000000000000000000000 :=
  enc_hi 56 63 100 4434345929245096251086307 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem lo_56_63_100 : (4434345929245096251086306:ℝ)/1000000000000000000000000 ≤ phi 56 (63/100:ℝ) :=
  enc_lo 56 63 100 4434345929245096251086306 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem lo_56_17_20 : (1829061060723849586057934:ℝ)/1000000000000000000000000 ≤ phi 56 (17/20:ℝ) :=
  enc_lo 56 17 20 1829061060723849586057934 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_57_1983_100000 : phi 57 (1983/100000:ℝ) ≤ (52608492505758407537761989:ℝ)/1000000000000000000000000 :=
  enc_hi 57 1983 100000 52608492505758407537761989 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_57_62_3125 : phi 57 (62/3125:ℝ) ≤ (52606365560432199546938048:ℝ)/1000000000000000000000000 :=
  enc_hi 57 62 3125 52606365560432199546938048 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_57_3_20 : phi 57 (3/20:ℝ) ≤ (31080902954246664800591168:ℝ)/1000000000000000000000000 :=
  enc_hi 57 3 20 31080902954246664800591168 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_57_27_100 : phi 57 (27/100:ℝ) ≤ (19133245528024117695415585:ℝ)/1000000000000000000000000 :=
  enc_hi 57 27 100 19133245528024117695415585 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_57_11_25 : phi 57 (11/25:ℝ) ≤ (9622544300278941572964684:ℝ)/1000000000000000000000000 :=
  enc_hi 57 11 25 9622544300278941572964684 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_57_63_100 : phi 57 (63/100:ℝ) ≤ (4463481063469591963636031:ℝ)/1000000000000000000000000 :=
  enc_hi 57 63 100 4463481063469591963636031 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_57_17_20 : phi 57 (17/20:ℝ) ≤ (1833923553762518389037397:ℝ)/1000000000000000000000000 :=
  enc_hi 57 17 20 1833923553762518389037397 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_57_1_1 : phi 57 (1:ℝ) ≤ (1000000000000000000000001:ℝ)/1000000000000000000000000 :=
  enc_hi 57 1 1 1000000000000000000000001 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_65_1983_100000 : phi 65 (1983/100000:ℝ) ≤ (59836100753221644982800665:ℝ)/1000000000000000000000000 :=
  enc_hi 65 1983 100000 59836100753221644982800665 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_65_62_3125 : phi 65 (62/3125:ℝ) ≤ (59833603014782001003947456:ℝ)/1000000000000000000000000 :=
  enc_hi 65 62 3125 59833603014782001003947456 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_65_3_20 : phi 65 (3/20:ℝ) ≤ (34751723899925785082096123:ℝ)/1000000000000000000000000 :=
  enc_hi 65 3 20 34751723899925785082096123 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_65_27_100 : phi 65 (27/100:ℝ) ≤ (21058466894502251202387404:ℝ)/1000000000000000000000000 :=
  enc_hi 65 27 100 21058466894502251202387404 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_65_11_25 : phi 65 (11/25:ℝ) ≤ (10356940463317201358450902:ℝ)/1000000000000000000000000 :=
  enc_hi 65 11 25 10356940463317201358450902 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_65_63_100 : phi 65 (63/100:ℝ) ≤ (4685737356010009618549104:ℝ)/1000000000000000000000000 :=
  enc_hi 65 63 100 4685737356010009618549104 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_65_17_20 : phi 65 (17/20:ℝ) ≤ (1870410808602758621266757:ℝ)/1000000000000000000000000 :=
  enc_hi 65 17 20 1870410808602758621266757 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_65_1_1 : phi 65 (1:ℝ) ≤ (1000000000000000000000001:ℝ)/1000000000000000000000000 :=
  enc_hi 65 1 1 1000000000000000000000001 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_129_1983_100000 : phi 129 (1983/100000:ℝ) ≤ (117148495736809158599575724:ℝ)/1000000000000000000000000 :=
  enc_hi 129 1983 100000 117148495736809158599575724 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_129_62_3125 : phi 129 (62/3125:ℝ) ≤ (117142802678018927159341140:ℝ)/1000000000000000000000000 :=
  enc_hi 129 62 3125 117142802678018927159341140 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_129_3_20 : phi 129 (3/20:ℝ) ≤ (62230208167557497500768478:ℝ)/1000000000000000000000000 :=
  enc_hi 129 3 20 62230208167557497500768478 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_129_27_100 : phi 129 (27/100:ℝ) ≤ (34732055674941243504733037:ℝ)/1000000000000000000000000 :=
  enc_hi 129 27 100 34732055674941243504733037 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_129_11_25 : phi 129 (11/25:ℝ) ≤ (15203032985131043880524834:ℝ)/1000000000000000000000000 :=
  enc_hi 129 11 25 15203032985131043880524834 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_129_63_100 : phi 129 (63/100:ℝ) ≤ (6038348754863190399562463:ℝ)/1000000000000000000000000 :=
  enc_hi 129 63 100 6038348754863190399562463 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_129_17_20 : phi 129 (17/20:ℝ) ≤ (2072948232033259181647999:ℝ)/1000000000000000000000000 :=
  enc_hi 129 17 20 2072948232033259181647999 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem hi_129_1_1 : phi 129 (1:ℝ) ≤ (1000000000000000000000001:ℝ)/1000000000000000000000000 :=
  enc_hi 129 1 1 1000000000000000000000001 1000000000000000000000000 _ _ _ _ (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by decide +kernel) (by norm_num)

theorem phi1 (t : ℝ) : phi 1 t = 1 := phi_one t

theorem G1 : Gl cs (991/50000:ℝ) (1983/100000:ℝ) (62/3125:ℝ) ≤ (-57843932381378485561237/31250000000000000000000:ℝ) := by
  have h1 := phi1 (991/50000:ℝ)
  have h2 := phi1 (1983/100000:ℝ)
  have h3 := phi1 (62/3125:ℝ)
  norm_num [Gl, cs]
  linarith [lo_9_1983_100000, hi_9_991_50000, hi_17_62_3125, hi_25_62_3125, hi_33_62_3125, hi_41_62_3125, hi_49_62_3125, hi_57_62_3125, hi_65_62_3125, hi_129_62_3125, lo_8_1983_100000, hi_8_991_50000, lo_16_1983_100000, hi_16_991_50000, lo_24_1983_100000, hi_24_991_50000, lo_32_1983_100000, hi_32_991_50000, lo_40_1983_100000, hi_40_991_50000, lo_48_1983_100000, hi_48_991_50000, lo_56_1983_100000, hi_56_991_50000]

theorem U1 : Fl cs (1983/100000:ℝ) ≤ (-9201628554706773497359/15625000000000000000000:ℝ) := by
  have h2 := phi1 (1983/100000:ℝ)
  norm_num [Fl, cs]
  linarith [lo_9_1983_100000, hi_17_1983_100000, hi_25_1983_100000, hi_33_1983_100000, hi_41_1983_100000, hi_49_1983_100000, hi_57_1983_100000, hi_65_1983_100000, hi_129_1983_100000, lo_8_1983_100000, lo_16_1983_100000, lo_24_1983_100000, lo_32_1983_100000, lo_40_1983_100000, lo_48_1983_100000, lo_56_1983_100000]

theorem piece1 : ∀ t : ℝ, (1983/100000:ℝ) ≤ t → t ≤ (62/3125:ℝ) → Fl cs t < 0 := by
  intro t h1 h2
  have hle := piece_le cs cs_pos (x := (991/50000:ℝ)) (a := (1983/100000:ℝ)) (b := (62/3125:ℝ)) (t := t) (by norm_num) (by norm_num) (by linarith) h2
  have hG := G1
  have hU := U1
  have hw1 : 0 ≤ ((62/3125:ℝ) - t) / ((62/3125:ℝ) - (1983/100000:ℝ)) := div_nonneg (by linarith) (by norm_num)
  have hw2 : 0 ≤ (t - (1983/100000:ℝ)) / ((62/3125:ℝ) - (1983/100000:ℝ)) := div_nonneg (by linarith) (by norm_num)
  have k1 := mul_le_mul_of_nonneg_left hU hw1
  have k2 := mul_le_mul_of_nonneg_left hG hw2
  have hlin : ((62/3125:ℝ) - t) * (-9201628554706773497359/15625000000000000000000:ℝ) + (t - (1983/100000:ℝ)) * (-57843932381378485561237/31250000000000000000000:ℝ) < 0 := by linarith
  have hd : ((62/3125:ℝ) - t) / ((62/3125:ℝ) - (1983/100000:ℝ)) * (-9201628554706773497359/15625000000000000000000:ℝ) + (t - (1983/100000:ℝ)) / ((62/3125:ℝ) - (1983/100000:ℝ)) * (-57843932381378485561237/31250000000000000000000:ℝ) < 0 := by
    rw [div_mul_eq_mul_div, div_mul_eq_mul_div, ← add_div]
    exact div_neg_of_neg_of_pos hlin (by norm_num)
  linarith

theorem G2 : Gl cs (1983/100000:ℝ) (62/3125:ℝ) (3/20:ℝ) ≤ (-26390229443904170282965561/31250000000000000000000:ℝ) := by
  have h1 := phi1 (1983/100000:ℝ)
  have h2 := phi1 (62/3125:ℝ)
  have h3 := phi1 (3/20:ℝ)
  norm_num [Gl, cs]
  linarith [lo_9_62_3125, hi_9_1983_100000, hi_17_3_20, hi_25_3_20, hi_33_3_20, hi_41_3_20, hi_49_3_20, hi_57_3_20, hi_65_3_20, hi_129_3_20, lo_8_62_3125, hi_8_1983_100000, lo_16_62_3125, hi_16_1983_100000, lo_24_62_3125, hi_24_1983_100000, lo_32_62_3125, hi_32_1983_100000, lo_40_62_3125, hi_40_1983_100000, lo_48_62_3125, hi_48_1983_100000, lo_56_62_3125, hi_56_1983_100000]

theorem piece2 (hFa : Fl cs (62/3125:ℝ) < 0) : ∀ t : ℝ, (62/3125:ℝ) ≤ t → t ≤ (3/20:ℝ) → Fl cs t < 0 := by
  intro t h1 h2
  have hle := piece_le cs cs_pos (x := (1983/100000:ℝ)) (a := (62/3125:ℝ)) (b := (3/20:ℝ)) (t := t) (by norm_num) (by norm_num) h1 h2
  have hG : Gl cs (1983/100000:ℝ) (62/3125:ℝ) (3/20:ℝ) < 0 := lt_of_le_of_lt G2 (by norm_num)
  have hw1 : 0 ≤ ((3/20:ℝ) - t) / ((3/20:ℝ) - (62/3125:ℝ)) := div_nonneg (by linarith) (by norm_num)
  have hw2 : 0 ≤ (t - (62/3125:ℝ)) / ((3/20:ℝ) - (62/3125:ℝ)) := div_nonneg (by linarith) (by norm_num)
  have hs : ((3/20:ℝ) - t) / ((3/20:ℝ) - (62/3125:ℝ)) + (t - (62/3125:ℝ)) / ((3/20:ℝ) - (62/3125:ℝ)) = 1 := by field_simp; ring
  have := conv_neg _ _ _ _ hw1 hw2 hs hFa hG
  linarith

theorem G3 : Gl cs (62/3125:ℝ) (3/20:ℝ) (27/100:ℝ) ≤ (-76853801156267355992484725171/101687500000000000000000000:ℝ) := by
  have h1 := phi1 (62/3125:ℝ)
  have h2 := phi1 (3/20:ℝ)
  have h3 := phi1 (27/100:ℝ)
  norm_num [Gl, cs]
  linarith [lo_9_3_20, hi_9_62_3125, hi_17_27_100, hi_25_27_100, hi_33_27_100, hi_41_27_100, hi_49_27_100, hi_57_27_100, hi_65_27_100, hi_129_27_100, lo_8_3_20, hi_8_62_3125, lo_16_3_20, hi_16_62_3125, lo_24_3_20, hi_24_62_3125, lo_32_3_20, hi_32_62_3125, lo_40_3_20, hi_40_62_3125, lo_48_3_20, hi_48_62_3125, lo_56_3_20, hi_56_62_3125]

theorem piece3 (hFa : Fl cs (3/20:ℝ) < 0) : ∀ t : ℝ, (3/20:ℝ) ≤ t → t ≤ (27/100:ℝ) → Fl cs t < 0 := by
  intro t h1 h2
  have hle := piece_le cs cs_pos (x := (62/3125:ℝ)) (a := (3/20:ℝ)) (b := (27/100:ℝ)) (t := t) (by norm_num) (by norm_num) h1 h2
  have hG : Gl cs (62/3125:ℝ) (3/20:ℝ) (27/100:ℝ) < 0 := lt_of_le_of_lt G3 (by norm_num)
  have hw1 : 0 ≤ ((27/100:ℝ) - t) / ((27/100:ℝ) - (3/20:ℝ)) := div_nonneg (by linarith) (by norm_num)
  have hw2 : 0 ≤ (t - (3/20:ℝ)) / ((27/100:ℝ) - (3/20:ℝ)) := div_nonneg (by linarith) (by norm_num)
  have hs : ((27/100:ℝ) - t) / ((27/100:ℝ) - (3/20:ℝ)) + (t - (3/20:ℝ)) / ((27/100:ℝ) - (3/20:ℝ)) = 1 := by field_simp; ring
  have := conv_neg _ _ _ _ hw1 hw2 hs hFa hG
  linarith

theorem G4 : Gl cs (3/20:ℝ) (27/100:ℝ) (11/25:ℝ) ≤ (-315218319383509733308901/1500000000000000000000:ℝ) := by
  have h1 := phi1 (3/20:ℝ)
  have h2 := phi1 (27/100:ℝ)
  have h3 := phi1 (11/25:ℝ)
  norm_num [Gl, cs]
  linarith [lo_9_27_100, hi_9_3_20, hi_17_11_25, hi_25_11_25, hi_33_11_25, hi_41_11_25, hi_49_11_25, hi_57_11_25, hi_65_11_25, hi_129_11_25, lo_8_27_100, hi_8_3_20, lo_16_27_100, hi_16_3_20, lo_24_27_100, hi_24_3_20, lo_32_27_100, hi_32_3_20, lo_40_27_100, hi_40_3_20, lo_48_27_100, hi_48_3_20, lo_56_27_100, hi_56_3_20]

theorem piece4 (hFa : Fl cs (27/100:ℝ) < 0) : ∀ t : ℝ, (27/100:ℝ) ≤ t → t ≤ (11/25:ℝ) → Fl cs t < 0 := by
  intro t h1 h2
  have hle := piece_le cs cs_pos (x := (3/20:ℝ)) (a := (27/100:ℝ)) (b := (11/25:ℝ)) (t := t) (by norm_num) (by norm_num) h1 h2
  have hG : Gl cs (3/20:ℝ) (27/100:ℝ) (11/25:ℝ) < 0 := lt_of_le_of_lt G4 (by norm_num)
  have hw1 : 0 ≤ ((11/25:ℝ) - t) / ((11/25:ℝ) - (27/100:ℝ)) := div_nonneg (by linarith) (by norm_num)
  have hw2 : 0 ≤ (t - (27/100:ℝ)) / ((11/25:ℝ) - (27/100:ℝ)) := div_nonneg (by linarith) (by norm_num)
  have hs : ((11/25:ℝ) - t) / ((11/25:ℝ) - (27/100:ℝ)) + (t - (27/100:ℝ)) / ((11/25:ℝ) - (27/100:ℝ)) = 1 := by field_simp; ring
  have := conv_neg _ _ _ _ hw1 hw2 hs hFa hG
  linarith

theorem G5 : Gl cs (27/100:ℝ) (11/25:ℝ) (63/100:ℝ) ≤ (-52332938835870293622227187/1062500000000000000000000:ℝ) := by
  have h1 := phi1 (27/100:ℝ)
  have h2 := phi1 (11/25:ℝ)
  have h3 := phi1 (63/100:ℝ)
  norm_num [Gl, cs]
  linarith [lo_9_11_25, hi_9_27_100, hi_17_63_100, hi_25_63_100, hi_33_63_100, hi_41_63_100, hi_49_63_100, hi_57_63_100, hi_65_63_100, hi_129_63_100, lo_8_11_25, hi_8_27_100, lo_16_11_25, hi_16_27_100, lo_24_11_25, hi_24_27_100, lo_32_11_25, hi_32_27_100, lo_40_11_25, hi_40_27_100, lo_48_11_25, hi_48_27_100, lo_56_11_25, hi_56_27_100]

theorem piece5 (hFa : Fl cs (11/25:ℝ) < 0) : ∀ t : ℝ, (11/25:ℝ) ≤ t → t ≤ (63/100:ℝ) → Fl cs t < 0 := by
  intro t h1 h2
  have hle := piece_le cs cs_pos (x := (27/100:ℝ)) (a := (11/25:ℝ)) (b := (63/100:ℝ)) (t := t) (by norm_num) (by norm_num) h1 h2
  have hG : Gl cs (27/100:ℝ) (11/25:ℝ) (63/100:ℝ) < 0 := lt_of_le_of_lt G5 (by norm_num)
  have hw1 : 0 ≤ ((63/100:ℝ) - t) / ((63/100:ℝ) - (11/25:ℝ)) := div_nonneg (by linarith) (by norm_num)
  have hw2 : 0 ≤ (t - (11/25:ℝ)) / ((63/100:ℝ) - (11/25:ℝ)) := div_nonneg (by linarith) (by norm_num)
  have hs : ((63/100:ℝ) - t) / ((63/100:ℝ) - (11/25:ℝ)) + (t - (11/25:ℝ)) / ((63/100:ℝ) - (11/25:ℝ)) = 1 := by field_simp; ring
  have := conv_neg _ _ _ _ hw1 hw2 hs hFa hG
  linarith

theorem G6 : Gl cs (11/25:ℝ) (63/100:ℝ) (17/20:ℝ) ≤ (-58526999421873742224435421/1187500000000000000000000:ℝ) := by
  have h1 := phi1 (11/25:ℝ)
  have h2 := phi1 (63/100:ℝ)
  have h3 := phi1 (17/20:ℝ)
  norm_num [Gl, cs]
  linarith [lo_9_63_100, hi_9_11_25, hi_17_17_20, hi_25_17_20, hi_33_17_20, hi_41_17_20, hi_49_17_20, hi_57_17_20, hi_65_17_20, hi_129_17_20, lo_8_63_100, hi_8_11_25, lo_16_63_100, hi_16_11_25, lo_24_63_100, hi_24_11_25, lo_32_63_100, hi_32_11_25, lo_40_63_100, hi_40_11_25, lo_48_63_100, hi_48_11_25, lo_56_63_100, hi_56_11_25]

theorem piece6 (hFa : Fl cs (63/100:ℝ) < 0) : ∀ t : ℝ, (63/100:ℝ) ≤ t → t ≤ (17/20:ℝ) → Fl cs t < 0 := by
  intro t h1 h2
  have hle := piece_le cs cs_pos (x := (11/25:ℝ)) (a := (63/100:ℝ)) (b := (17/20:ℝ)) (t := t) (by norm_num) (by norm_num) h1 h2
  have hG : Gl cs (11/25:ℝ) (63/100:ℝ) (17/20:ℝ) < 0 := lt_of_le_of_lt G6 (by norm_num)
  have hw1 : 0 ≤ ((17/20:ℝ) - t) / ((17/20:ℝ) - (63/100:ℝ)) := div_nonneg (by linarith) (by norm_num)
  have hw2 : 0 ≤ (t - (63/100:ℝ)) / ((17/20:ℝ) - (63/100:ℝ)) := div_nonneg (by linarith) (by norm_num)
  have hs : ((17/20:ℝ) - t) / ((17/20:ℝ) - (63/100:ℝ)) + (t - (63/100:ℝ)) / ((17/20:ℝ) - (63/100:ℝ)) = 1 := by field_simp; ring
  have := conv_neg _ _ _ _ hw1 hw2 hs hFa hG
  linarith

theorem G7 : Gl cs (63/100:ℝ) (17/20:ℝ) (1:ℝ) ≤ (-2461428733461187394236283151/687500000000000000000000:ℝ) := by
  have h1 := phi1 (63/100:ℝ)
  have h2 := phi1 (17/20:ℝ)
  have h3 := phi1 (1:ℝ)
  norm_num [Gl, cs]
  linarith [lo_9_17_20, hi_9_63_100, hi_17_1_1, hi_25_1_1, hi_33_1_1, hi_41_1_1, hi_49_1_1, hi_57_1_1, hi_65_1_1, hi_129_1_1, lo_8_17_20, hi_8_63_100, lo_16_17_20, hi_16_63_100, lo_24_17_20, hi_24_63_100, lo_32_17_20, hi_32_63_100, lo_40_17_20, hi_40_63_100, lo_48_17_20, hi_48_63_100, lo_56_17_20, hi_56_63_100]

theorem piece7 (hFa : Fl cs (17/20:ℝ) < 0) : ∀ t : ℝ, (17/20:ℝ) ≤ t → t ≤ (1:ℝ) → Fl cs t < 0 := by
  intro t h1 h2
  have hle := piece_le cs cs_pos (x := (63/100:ℝ)) (a := (17/20:ℝ)) (b := (1:ℝ)) (t := t) (by norm_num) (by norm_num) h1 h2
  have hG : Gl cs (63/100:ℝ) (17/20:ℝ) (1:ℝ) < 0 := lt_of_le_of_lt G7 (by norm_num)
  have hw1 : 0 ≤ ((1:ℝ) - t) / ((1:ℝ) - (17/20:ℝ)) := div_nonneg (by linarith) (by norm_num)
  have hw2 : 0 ≤ (t - (17/20:ℝ)) / ((1:ℝ) - (17/20:ℝ)) := div_nonneg (by linarith) (by norm_num)
  have hs : ((1:ℝ) - t) / ((1:ℝ) - (17/20:ℝ)) + (t - (17/20:ℝ)) / ((1:ℝ) - (17/20:ℝ)) = 1 := by field_simp; ring
  have := conv_neg _ _ _ _ hw1 hw2 hs hFa hG
  linarith

theorem eq_ceil (t : ℝ) : FceilBank (1 - t) = Fl cs t := by
  simp [Fl, phi, cs, FceilBank, cdat, TB, PB]
  ring

theorem end1 : Fl cs (62/3125:ℝ) < 0 := piece1 (62/3125:ℝ) (by norm_num) le_rfl

theorem end2 : Fl cs (3/20:ℝ) < 0 := piece2 end1 (3/20:ℝ) (by norm_num) le_rfl

theorem end3 : Fl cs (27/100:ℝ) < 0 := piece3 end2 (27/100:ℝ) (by norm_num) le_rfl

theorem end4 : Fl cs (11/25:ℝ) < 0 := piece4 end3 (11/25:ℝ) (by norm_num) le_rfl

theorem end5 : Fl cs (63/100:ℝ) < 0 := piece5 end4 (63/100:ℝ) (by norm_num) le_rfl

theorem end6 : Fl cs (17/20:ℝ) < 0 := piece6 end5 (17/20:ℝ) (by norm_num) le_rfl

theorem end7 : Fl cs (1:ℝ) < 0 := piece7 end6 (1:ℝ) (by norm_num) le_rfl

theorem cert : Cert FceilBank (1983/100000) := by
  intro t h1 h2
  rw [eq_ceil]
  by_cases c1 : t ≤ (62/3125:ℝ)
  · exact piece1 t (by linarith) c1
  push_neg at c1
  by_cases c2 : t ≤ (3/20:ℝ)
  · exact piece2 end1 t (by linarith) c2
  push_neg at c2
  by_cases c3 : t ≤ (27/100:ℝ)
  · exact piece3 end2 t (by linarith) c3
  push_neg at c3
  by_cases c4 : t ≤ (11/25:ℝ)
  · exact piece4 end3 t (by linarith) c4
  push_neg at c4
  by_cases c5 : t ≤ (63/100:ℝ)
  · exact piece5 end4 t (by linarith) c5
  push_neg at c5
  by_cases c6 : t ≤ (17/20:ℝ)
  · exact piece6 end5 t (by linarith) c6
  push_neg at c6
  exact piece7 end6 t (by linarith) h2

end BankFlagCertFlagX28
#print axioms BankFlagCertFlagX28.cert
