import Nov15.BlockLaw
namespace BlockLaw2D8
open FrameCert BlockComplete BlockLaw

def L8 : List Nat := [3, 5, 6, 7, 9, 10, 12, 17, 18, 20, 24, 25, 33, 34, 36, 40, 42, 48, 52, 63, 65, 66, 67, 68, 72, 76, 80, 82, 95, 96, 97, 104, 111, 119, 123, 125, 126, 127, 129, 130, 132, 136, 137, 144, 159, 160, 162, 175, 183, 187, 189, 190, 192, 207, 215, 219, 221, 222, 231, 235, 237, 238, 243, 245, 246, 249, 250, 252, 257, 258, 260, 264, 266, 272, 287, 288, 289, 303, 311, 315, 317, 318, 320, 335, 343, 347, 349, 350, 359, 363, 365, 366, 371, 373, 374, 377, 378, 380, 384, 399, 407, 411, 413, 414, 423, 427, 429, 430, 435, 437, 438, 441, 442, 444, 448, 455, 459, 461, 462, 467, 469, 470, 473, 474, 476, 483, 485, 486, 489, 490, 491, 492, 497, 498, 500, 504]
def tab8 : Nat := 1271567330837011011774465938037642915172567426387399732459356658010658478396555171195396635309281474318589260390112023905842305193602484288199819393384126015764504962518495821814052823875816809878058389546309043630757612725089292952760961278513635175535234450413034878132835067447891281141560305034188236803460168000431588610575914977812544615588955702882779781907938758834646666306634864647368032093495865889497149816533884308908171104678041549224595815498749029187762782525883721687744787758247002877453763481643568459723177287509368141647278483794407765073664407179374825643183980109194361768498815421302230889538256883348465761250200413032971851780686668054591361450100477751374163896644139629262925455951360145086956685105195622354934675111945635066904348607953008920794152573366743519738611209453543341173674360652653441403859883671314098956999832948233319983964825657303778179067469365607247874153135719089600718075777047963977821861036003951249989917814313907511820522989176193016302754163800321644323157988929169224833598276598007267752077391416814567265074193267661837860047664544845330389660565604446525557726882561546067117079668148646320874594621823551743069540662905848189819214454017034078805789380052015482837307395772173594305074599827295642333986433304453534422454245438996296726322108147968711454909214864739020592230036787793040881522404244748254886802974415270000183248944111033053773957746002198226982802066327353875906171971226446078888715539109949295089910495870651493904558327756587693617857158158695045314251808085202828481196480435948961375546071499903078245009121508450797143187724182694047451637305951543266251066029824276607855843106417347536074381144427098068928488032480750366221696651133666998704695205339406588631355696220697042232765228164149021014610290940671188810064654795977985088059793023109808773495021568
def bm8 : Nat := 56899461776159782571886005762059881406691530993736755332044345678051467864140548249679538195176075405984128704690038743542233905999264808853335881160424


/-- w < 759: frame w is disjoint from the 8-dim section (a not blocking, bit unset);
w >= 759: a is flagged (bit set) and really meets every frame -/
def check8 (a : Nat) : Bool :=
  let w := (tab8 >>> (12 * a)) % 4096
  if w < 759 then (frameAt w &&& lamMask' a a == 0) && !(bm8.testBit a)
  else bm8.testBit a && (List.range 759).all (fun i => frameAt i &&& lamMask' a a != 0)

def rng8 (lo : Nat) : Bool := (List.range 64).all (fun j => lo + j == 0 || check8 (lo + j))

theorem r0 : rng8 0 = true := by decide +kernel
theorem r1 : rng8 64 = true := by decide +kernel
theorem r2 : rng8 128 = true := by decide +kernel
theorem r3 : rng8 192 = true := by decide +kernel
theorem r4 : rng8 256 = true := by decide +kernel
theorem r5 : rng8 320 = true := by decide +kernel
theorem r6 : rng8 384 = true := by decide +kernel
theorem r7 : rng8 448 = true := by decide +kernel

theorem check8_all (a : Nat) (h0 : 0 < a) (h : a < 512) : check8 a = true := by
  have key : ∀ lo, lo % 64 = 0 → lo < 512 → rng8 lo = true → ∀ a, lo ≤ a → a < lo + 64 → 0 < a → check8 a = true := by
    intro lo _ _ hr a h1 h2 h3
    have := List.all_eq_true.1 hr (a - lo) (List.mem_range.2 (by omega))
    have e : lo + (a - lo) = a := by omega
    rw [e] at this
    simp only [Bool.or_eq_true, beq_iff_eq] at this
    rcases this with h4 | h4
    · omega
    · exact h4
  by_cases c0 : a < 64
  · exact key 0 rfl (by omega) r0 a (by omega) (by omega) h0
  by_cases c1 : a < 128
  · exact key 64 rfl (by omega) r1 a (by omega) (by omega) h0
  by_cases c2 : a < 192
  · exact key 128 rfl (by omega) r2 a (by omega) (by omega) h0
  by_cases c3 : a < 256
  · exact key 192 rfl (by omega) r3 a (by omega) (by omega) h0
  by_cases c4 : a < 320
  · exact key 256 rfl (by omega) r4 a (by omega) (by omega) h0
  by_cases c5 : a < 384
  · exact key 320 rfl (by omega) r5 a (by omega) (by omega) h0
  by_cases c6 : a < 448
  · exact key 384 rfl (by omega) r6 a (by omega) (by omega) h0
  · exact key 448 rfl (by omega) r7 a (by omega) (by omega) h0

theorem L8_length : L8.length = 136 := by decide +kernel
theorem L8_nodup : L8.Nodup := by decide +kernel
theorem bm8_L8 : (List.range 512).all (fun a => bm8.testBit a == L8.contains a) = true := by decide +kernel

lemma bm8_iff (a : Nat) (h : a < 512) : bm8.testBit a = true ↔ a ∈ L8 := by
  have := List.all_eq_true.1 bm8_L8 a (List.mem_range.2 h)
  simp only [beq_iff_eq] at this
  rw [this]; simp

/-- COMPLETENESS for 8-dim sections: for every nonzero normal a < 512, the hyperplane of labels
orthogonal to a meets all 759 frames iff a is one of the 136 listed normals. -/
theorem blocking8_iff (a : Nat) (h0 : 0 < a) (h : a < 512) :
    (∀ i, i < 759 → frameAt i &&& lamMask a a ≠ 0) ↔ a ∈ L8 := by
  have hc := check8_all a h0 h
  unfold check8 at hc
  simp only [lamMask'_eq] at hc
  by_cases hw : (tab8 >>> (12 * a)) % 4096 < 759
  · simp only [if_pos hw, Bool.and_eq_true, beq_iff_eq, Bool.not_eq_true'] at hc
    obtain ⟨h1, h2⟩ := hc
    constructor
    · intro hb; exact absurd h1 (hb _ hw)
    · intro hm; rw [← bm8_iff a h] at hm; rw [hm] at h2; exact absurd h2 (by simp)
  · simp only [if_neg hw, Bool.and_eq_true] at hc
    obtain ⟨h1, h2⟩ := hc
    constructor
    · intro _; exact (bm8_iff a h).1 h1
    · intro _ i hi
      have := List.all_eq_true.1 h2 i (List.mem_range.2 hi)
      simpa using this

end BlockLaw2D8
