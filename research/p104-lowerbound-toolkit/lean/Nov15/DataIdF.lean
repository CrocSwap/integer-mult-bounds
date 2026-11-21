import Nov15.DataIdA
import Mathlib.Tactic.IntervalCases
/-!
DATAID part F (frames).  Kernel-only.  See DataIdA for the E8 objects (`dot`, `rootAt`).
The 759 frames of FrameCert = ALL 8-subsets of the 104 ports with pairwise orthogonal roots.
`ext o k cs` enumerates all k-cliques (increasing lists) of the graph `o` inside the candidate list `cs`;
`mem_ext` PROVES it complete and sound; the enumeration for o = orthogonality of the port roots is then
evaluated in the kernel (in chunks by first vertex) and compared with the packed masks FrameCert.frames.
-/
set_option Elab.async false
namespace DataId

/-- orthogonality masks of the 104 ports (bit s of entry t set iff <r_t, r_s> = 0), certified by adjLit_ok -/
def adjLit : List Nat := [19965346746945776599577163450304, 16080990870767433891002303070112, 3626999457374745047073300592480, 13918738824119356520573632282080, 6604330245524387457888846863328, 8714943431600934006715768094750, 7365888448925228712892743759901, 14877394584145329779401541201947, 4929144307394914058901835606047, 4569813453901545068108874807319, 15636340920909677816868955740175, 19630957698850224338274197866330, 9048900860335892829125008279262, 10882655702354267225978647593934, 15746891960146098245963455805241, 5440237471542417470330740424117, 12960408582569562083649730655603, 3041868262303587606606538370295, 17317133893286487514960338471663, 17512398968464550693912738552295, 15766249753634901962210483912670, 19646253501586115944280232085437, 1329378666526988944741444439931, 11821994337198664302252505044735, 11621119846217607944414652237303, 14892428049978380641534004492412, 17209401492710608971333263305022, 17642389778544070176129208269366, 8695585375725642586054330517721, 18988253197056365521388256838229, 1533877756084370953586702345293, 11202368964960398669632048567063, 8998176867943884274085700187407, 9351898305634260086006067209735, 3642024725179581708993222999939, 16065686607616840380420156651333, 5758163505369664969387545443785, 9998039701153778321226345141922, 9639327817384597730015697388970, 10565888422015704974482032354226, 12126363575464590008791430815332, 7795064590851596539236187990900, 2170357415937308931515161089256, 18347101364523896360601376142064, 17750086023189987883650941166072, 14558348477309440113405649334503, 3976601123657031772472369146211, 4251752016702368954589258676843, 16684078874946671594987310477997, 3675223410742057861403994051765, 6924014222374763071033376090921, 13593453622650446940878069697841, 13630301058131062755572418321977, 18067081113416335470813627521478, 18030232430933236755279867677390, 2487236335058870131557596507350, 8112001595529347470486053671754, 12247300364135438046503587476818, 12443184409038121970190210524762, 10248990445648715911449910500236, 9956177693731504799039395429780, 9681025553687109914705942474396, 6734393662601352929623836459039, 15449487003337423233469397338080, 11329477178085268461761289271329, 15209481223562900153034853105730, 7033810576451796169710118193284, 17526425623849165054649776345344, 17325549886308313876744311112200, 3039062930603735862363033445392, 8398180391975497853876750514176, 3010519967666481929352902592449, 1661465289545403836817036230562, 19314175626769946903706571028324, 9365924754858062678968832224992, 9006592711030574804774997491176, 11199563595776762967633737014256, 14260914657608943560807315128382, 8063772306693514392543884652699, 17764106031105907851106957519135, 18355512523023035919667338443287, 2167550875606785526097250606095, 16397758437822231991131692795804, 3309946550493125314048200445786, 13644114944194740601389069227742, 13601714874347963187572452378070, 6921170205343843878262714655694, 1961036941109342147446642210617, 12453806730938159058442079776445, 12253240478259861658803763461557, 8108577294105793504415155690413, 9667817529831912238948237747835, 9944786647309968312722810811763, 10241233354093211549123489207147, 19659975349957829506753858006263, 322693033675051362897685236463, 5244353426342419392443223453373, 1034423602584869597565746108827, 12247353456916476238022789746028, 8109665485568670491513147106287, 13021816542355266506222750931921, 12071223359939213615414384991149, 10882815275761321670231830879347, 9221170781784978238872911441035]

def oAdj (v w : Nat) : Bool := (adjLit.getD v 0).testBit w

def rowAdjOK (v : Nat) : Bool :=
  (List.range 104).all (fun w => oAdj v w == (dot (rootAt v) (rootAt w) == 0))

theorem adjLit_ok_c0 : (List.range 13).all (fun i => rowAdjOK (13*0+i)) = true := by decide +kernel
theorem adjLit_ok_c1 : (List.range 13).all (fun i => rowAdjOK (13*1+i)) = true := by decide +kernel
theorem adjLit_ok_c2 : (List.range 13).all (fun i => rowAdjOK (13*2+i)) = true := by decide +kernel
theorem adjLit_ok_c3 : (List.range 13).all (fun i => rowAdjOK (13*3+i)) = true := by decide +kernel
theorem adjLit_ok_c4 : (List.range 13).all (fun i => rowAdjOK (13*4+i)) = true := by decide +kernel
theorem adjLit_ok_c5 : (List.range 13).all (fun i => rowAdjOK (13*5+i)) = true := by decide +kernel
theorem adjLit_ok_c6 : (List.range 13).all (fun i => rowAdjOK (13*6+i)) = true := by decide +kernel
theorem adjLit_ok_c7 : (List.range 13).all (fun i => rowAdjOK (13*7+i)) = true := by decide +kernel
theorem adjLit_ok : ∀ t, t < 104 → rowAdjOK t = true := by
  intro t ht
  refine forall_of_chunks rowAdjOK (n := 8) ?_ t (by omega)
  intro c hc
  interval_cases c
  · exact adjLit_ok_c0
  · exact adjLit_ok_c1
  · exact adjLit_ok_c2
  · exact adjLit_ok_c3
  · exact adjLit_ok_c4
  · exact adjLit_ok_c5
  · exact adjLit_ok_c6
  · exact adjLit_ok_c7

def extAux (o : Nat → Nat → Bool) (rec : List Nat → List (List Nat)) : List Nat → List (List Nat)
  | [] => []
  | v :: vs => (rec (vs.filter (o v))).map (v :: ·) ++ extAux o rec vs

/-- the contributions of the first n candidates only (same tail candidates as extAux) -/
def extAuxN (o : Nat → Nat → Bool) (rec : List Nat → List (List Nat)) : Nat → List Nat → List (List Nat)
  | 0, _ => []
  | _ + 1, [] => []
  | n + 1, v :: vs => (rec (vs.filter (o v))).map (v :: ·) ++ extAuxN o rec n vs

/-- all k-element cliques (increasing lists) inside the candidate list -/
def ext (o : Nat → Nat → Bool) : Nat → List Nat → List (List Nat)
  | 0 => fun _ => [[]]
  | k + 1 => fun cs => extAux o (ext o k) cs

def Spec (o : Nat → Nat → Bool) (k : Nat) (cs l : List Nat) : Prop :=
  l.length = k ∧ l.Sublist cs ∧ l.Pairwise (fun a b => o a b = true)

theorem mem_extAux (o : Nat → Nat → Bool) (k : Nat)
    (ih : ∀ cs l, l ∈ ext o k cs ↔ Spec o k cs l) :
    ∀ cs l, l ∈ extAux o (ext o k) cs ↔ Spec o (k + 1) cs l := by
  intro cs
  induction cs with
  | nil =>
    intro l
    simp only [extAux, List.not_mem_nil, false_iff, Spec]
    rintro ⟨h1, h2, _⟩
    have := List.sublist_nil.1 h2
    subst this
    simp at h1
  | cons v vs ihc =>
    intro l
    simp only [extAux, List.mem_append, List.mem_map, ihc, ih, Spec]
    constructor
    · rintro (⟨l', ⟨h1, h2, h3⟩, rfl⟩ | ⟨h1, h2, h3⟩)
      · refine ⟨by simp [h1], ?_, ?_⟩
        · exact List.Sublist.cons_cons _ (h2.trans (List.filter_sublist))
        · refine List.pairwise_cons.2 ⟨?_, h3⟩
          intro b hb
          have := h2.subset hb
          exact (List.mem_filter.1 this).2
      · exact ⟨h1, List.Sublist.cons _ h2, h3⟩
    · rintro ⟨h1, h2, h3⟩
      rcases List.sublist_cons_iff.1 h2 with h | ⟨l', rfl, h⟩
      · exact Or.inr ⟨h1, h, h3⟩
      · left
        refine ⟨l', ⟨by simpa using h1, ?_, (List.pairwise_cons.1 h3).2⟩, rfl⟩
        have hall := (List.pairwise_cons.1 h3).1
        have hf : l'.filter (o v) = l' := List.filter_eq_self.2 hall
        have := h.filter (o v)
        rwa [hf] at this

theorem mem_ext (o : Nat → Nat → Bool) : ∀ k cs l, l ∈ ext o k cs ↔ Spec o k cs l := by
  intro k
  induction k with
  | zero =>
    intro cs l
    simp only [ext, List.mem_singleton, Spec]
    constructor
    · rintro rfl; simp
    · rintro ⟨h1, _, _⟩; exact List.length_eq_zero_iff.1 h1
  | succ k ih => exact mem_extAux o k ih

theorem extAux_split (o : Nat → Nat → Bool) (rec : List Nat → List (List Nat)) :
    ∀ (n : Nat) (cs : List Nat), extAux o rec cs = extAuxN o rec n cs ++ extAux o rec (cs.drop n) := by
  intro n
  induction n with
  | zero => intro cs; simp [extAuxN]
  | succ n ih =>
    intro cs
    cases cs with
    | nil => simp [extAuxN, extAux]
    | cons v vs =>
      simp only [extAux, extAuxN, List.drop_succ_cons]
      rw [ih vs, List.append_assoc]

def chunkSpec : List Nat := [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 3, 3, 4, 5, 7, 13, 47]

/-- chain of chunk enumerations over candidate list cs starting at offset a -/
def chainE (cs : List Nat) : Nat → List Nat → List (List Nat)
  | _, [] => []
  | a, n :: r => extAuxN oAdj (ext oAdj 7) n (cs.drop a) ++ chainE cs (a + n) r

theorem chainE_eq (cs : List Nat) : ∀ (r : List Nat) (a : Nat),
    extAux oAdj (ext oAdj 7) (cs.drop a) = chainE cs a r ++ extAux oAdj (ext oAdj 7) (cs.drop (a + r.sum)) := by
  intro r
  induction r with
  | nil => intro a; simp [chainE]
  | cons n r ih =>
    intro a
    rw [extAux_split oAdj (ext oAdj 7) n (cs.drop a), List.drop_drop, chainE, ih (a + n)]
    simp [List.append_assoc, Nat.add_assoc, Nat.add_comm n]

/-- the frames, as increasing index lists (computed in chunks by first vertex) -/
def frameLists : List (List Nat) := chainE (List.range 104) 0 chunkSpec

theorem frameLists_eq : frameLists = ext oAdj 8 (List.range 104) := by
  have h := chainE_eq (List.range 104) chunkSpec 0
  have hs : chunkSpec.sum = 104 := by decide
  rw [hs] at h
  have e : (List.range 104).drop (0 + 104) = [] := List.drop_of_length_le (by simp)
  rw [e] at h
  simp only [List.drop_zero, Nat.zero_add] at h
  have e2 : extAux oAdj (ext oAdj 7) [] = [] := rfl
  rw [e2, List.append_nil] at h
  exact h.symm

/-! ### the kernel evaluation, chunk by chunk, against FrameCert.frames -/
def maskOfList (l : List Nat) : Nat := l.foldl (fun a i => a ||| 2 ^ i) 0

def chainS (l : List (Nat)) : Nat → List Nat → List Nat
  | _, [] => []
  | s, m :: r => (l.drop s).take m ++ chainS l (s + m) r

theorem piece0 : (extAuxN oAdj (ext oAdj 7) 1 ((List.range 104).drop 0)).map maskOfList =
    (FrameCert.frames.drop 0).take 57 := by decide +kernel
theorem piece1 : (extAuxN oAdj (ext oAdj 7) 1 ((List.range 104).drop 1)).map maskOfList =
    (FrameCert.frames.drop 57).take 57 := by decide +kernel
theorem piece2 : (extAuxN oAdj (ext oAdj 7) 1 ((List.range 104).drop 2)).map maskOfList =
    (FrameCert.frames.drop 114).take 58 := by decide +kernel
theorem piece3 : (extAuxN oAdj (ext oAdj 7) 1 ((List.range 104).drop 3)).map maskOfList =
    (FrameCert.frames.drop 172).take 61 := by decide +kernel
theorem piece4 : (extAuxN oAdj (ext oAdj 7) 1 ((List.range 104).drop 4)).map maskOfList =
    (FrameCert.frames.drop 233).take 58 := by decide +kernel
theorem piece5 : (extAuxN oAdj (ext oAdj 7) 1 ((List.range 104).drop 5)).map maskOfList =
    (FrameCert.frames.drop 291).take 29 := by decide +kernel
theorem piece6 : (extAuxN oAdj (ext oAdj 7) 1 ((List.range 104).drop 6)).map maskOfList =
    (FrameCert.frames.drop 320).take 33 := by decide +kernel
theorem piece7 : (extAuxN oAdj (ext oAdj 7) 1 ((List.range 104).drop 7)).map maskOfList =
    (FrameCert.frames.drop 353).take 30 := by decide +kernel
theorem piece8 : (extAuxN oAdj (ext oAdj 7) 1 ((List.range 104).drop 8)).map maskOfList =
    (FrameCert.frames.drop 383).take 27 := by decide +kernel
theorem piece9 : (extAuxN oAdj (ext oAdj 7) 1 ((List.range 104).drop 9)).map maskOfList =
    (FrameCert.frames.drop 410).take 31 := by decide +kernel
theorem piece10 : (extAuxN oAdj (ext oAdj 7) 2 ((List.range 104).drop 10)).map maskOfList =
    (FrameCert.frames.drop 441).take 50 := by decide +kernel
theorem piece11 : (extAuxN oAdj (ext oAdj 7) 2 ((List.range 104).drop 12)).map maskOfList =
    (FrameCert.frames.drop 491).take 35 := by decide +kernel
theorem piece12 : (extAuxN oAdj (ext oAdj 7) 2 ((List.range 104).drop 14)).map maskOfList =
    (FrameCert.frames.drop 526).take 36 := by decide +kernel
theorem piece13 : (extAuxN oAdj (ext oAdj 7) 2 ((List.range 104).drop 16)).map maskOfList =
    (FrameCert.frames.drop 562).take 34 := by decide +kernel
theorem piece14 : (extAuxN oAdj (ext oAdj 7) 2 ((List.range 104).drop 18)).map maskOfList =
    (FrameCert.frames.drop 596).take 36 := by decide +kernel
theorem piece15 : (extAuxN oAdj (ext oAdj 7) 2 ((List.range 104).drop 20)).map maskOfList =
    (FrameCert.frames.drop 632).take 31 := by decide +kernel
theorem piece16 : (extAuxN oAdj (ext oAdj 7) 3 ((List.range 104).drop 22)).map maskOfList =
    (FrameCert.frames.drop 663).take 33 := by decide +kernel
theorem piece17 : (extAuxN oAdj (ext oAdj 7) 3 ((List.range 104).drop 25)).map maskOfList =
    (FrameCert.frames.drop 696).take 22 := by decide +kernel
theorem piece18 : (extAuxN oAdj (ext oAdj 7) 4 ((List.range 104).drop 28)).map maskOfList =
    (FrameCert.frames.drop 718).take 14 := by decide +kernel
theorem piece19 : (extAuxN oAdj (ext oAdj 7) 5 ((List.range 104).drop 32)).map maskOfList =
    (FrameCert.frames.drop 732).take 19 := by decide +kernel
theorem piece20 : (extAuxN oAdj (ext oAdj 7) 7 ((List.range 104).drop 37)).map maskOfList =
    (FrameCert.frames.drop 751).take 5 := by decide +kernel
theorem piece21 : (extAuxN oAdj (ext oAdj 7) 13 ((List.range 104).drop 44)).map maskOfList =
    (FrameCert.frames.drop 756).take 3 := by decide +kernel
theorem piece22 : (extAuxN oAdj (ext oAdj 7) 47 ((List.range 104).drop 57)).map maskOfList =
    (FrameCert.frames.drop 759).take 0 := by decide +kernel

theorem drop_chainS (l : List Nat) : ∀ (r : List Nat) (s : Nat),
    l.drop s = chainS l s r ++ l.drop (s + r.sum) := by
  intro r
  induction r with
  | nil => intro s; simp [chainS]
  | cons m r ih =>
    intro s
    conv_lhs => rw [← List.take_append_drop m (l.drop s)]
    rw [chainS, List.drop_drop]
    have := ih (s + m)
    rw [this]
    simp [List.append_assoc, Nat.add_assoc]

def chunkMasks : List Nat := [57, 57, 58, 61, 58, 29, 33, 30, 27, 31, 50, 35, 36, 34, 36, 31, 33, 22, 14, 19, 5, 3, 0]

theorem frames_length : FrameCert.frames.length = 759 := by decide +kernel
theorem frames_masks : FrameCert.frames = frameLists.map maskOfList := by
  have h := drop_chainS FrameCert.frames chunkMasks 0
  have hs : chunkMasks.sum = 759 := by decide
  rw [hs] at h
  have e : FrameCert.frames.drop (0 + 759) = [] := by
    rw [Nat.zero_add]; exact List.drop_of_length_le (by rw [frames_length])
  rw [e, List.append_nil, List.drop_zero] at h
  rw [h]
  unfold frameLists chunkSpec
  simp only [chainE, List.map_append, chainS, chunkMasks, List.map_nil, List.append_nil]
  rw [piece0, piece1, piece2, piece3, piece4, piece5, piece6, piece7, piece8, piece9, piece10, piece11, piece12, piece13, piece14, piece15, piece16, piece17, piece18, piece19, piece20, piece21, piece22]

theorem frameLists_length : frameLists.length = 759 := by
  have := congrArg List.length frames_masks
  rw [List.length_map, frames_length] at this
  exact this.symm

theorem foldl_testBit (l : List Nat) : ∀ (init i : Nat),
    (l.foldl (fun a j => a ||| 2 ^ j) init).testBit i = (init.testBit i || l.contains i) := by
  induction l with
  | nil => intro init i; simp
  | cons j js ih =>
    intro init i
    simp only [List.foldl_cons]
    rw [ih, Nat.testBit_or, Nat.testBit_two_pow]
    by_cases hj : j = i
    · subst hj; simp [List.contains_cons]
    · have hj' : ¬ i = j := fun h => hj h.symm
      by_cases hh : init.testBit i = true <;> simp [hj, hj', hh, List.contains_cons]

/-- the packed masks encode exactly the index lists -/
theorem maskOfList_testBit (l : List Nat) (i : Nat) : (maskOfList l).testBit i = l.contains i := by
  unfold maskOfList
  rw [foldl_testBit]; simp

/-- HEADLINE (frames): a strictly increasing list of 8 port indices < 104 whose roots are pairwise orthogonal
    (an 8-subset of the ports that is an orthogonal frame of E8) is exactly a listed frame. -/
theorem frames_exact (l : List Nat) :
    (l.length = 8 ∧ l.Sublist (List.range 104) ∧ l.Pairwise (fun a b => dot (rootAt a) (rootAt b) = 0)) ↔
      l ∈ frameLists := by
  rw [frameLists_eq, mem_ext]
  unfold Spec
  have hOK : ∀ a b, a < 104 → b < 104 → (oAdj a b = true ↔ dot (rootAt a) (rootAt b) = 0) := by
    intro a b ha hb
    have := adjLit_ok a ha
    unfold rowAdjOK at this
    rw [List.all_eq_true] at this
    have h2 := this b (List.mem_range.2 hb)
    simp only [beq_iff_eq] at h2
    rw [h2]; simp
  constructor
  · rintro ⟨h1, h2, h3⟩
    refine ⟨h1, h2, ?_⟩
    refine h3.imp_of_mem ?_
    intro a b ha hb h
    exact (hOK a b (List.mem_range.1 (h2.subset ha)) (List.mem_range.1 (h2.subset hb))).2 h
  · rintro ⟨h1, h2, h3⟩
    refine ⟨h1, h2, ?_⟩
    refine h3.imp_of_mem ?_
    intro a b ha hb h
    exact (hOK a b (List.mem_range.1 (h2.subset ha)) (List.mem_range.1 (h2.subset hb))).1 h

/-- a packed FrameCert mask is a frame mask iff it is the mask of a listed (= orthogonal 8-set) frame -/
theorem frames_mask_iff (m : Nat) : m ∈ FrameCert.frames ↔ ∃ l, l ∈ frameLists ∧ maskOfList l = m := by
  rw [frames_masks]; simp

#print axioms DataId.frames_exact
#print axioms DataId.frames_masks
#print axioms DataId.frameLists_length
#print axioms DataId.maskOfList_testBit
end DataId
