import MultitapeToolkit.FrameRule
import Mathlib.Data.List.GetD
import Mathlib.Tactic.DeriveFintype

/-!
# Actual finite marked-stream movement and bit flipping

The four-symbol marker convention and movement table follow pinned PR1379,
commit `3a45bd089ad56c38b55da8d80d7b056f2d90e5fa`. Lists and absolute
positions occur only in tape specifications and proofs, never in control.
-/
namespace MultitapeToolkit.Absolute.MarkedStreams

open MultitapeToolkit.Locality MultitapeToolkit.Absolute.FrameRule

inductive Symbol where
  | blank
  | separator
  | bit (value : Bool)
  deriving DecidableEq, Repr, Fintype

instance : Inhabited Symbol := ⟨.blank⟩
@[simp] theorem default_symbol : (default : Symbol) = .blank := rfl
@[simp] theorem alphabet_card : Fintype.card Symbol = 4 := by decide

/-- Finite nearest-first left and head-first right descriptions, with arbitrary
unchanged absolute data beyond the described left boundary. -/
def cellView (head : ℤ) (left right : List Symbol) (past : ℤ → Symbol) (x : ℤ) : Symbol :=
  if x < head then
    if (head - x - 1).toNat < left.length then left.getD (head - x - 1).toNat .blank
    else past x
  else right.getD (x - head).toNat .blank

/-- Separator at -1, arbitrary payload at 0 through length-1, right blanks,
and arbitrary dirty data strictly left of -1. -/
def markedStream (bits : List Bool) (past : ℤ → Symbol) : ℤ → Symbol :=
  cellView 0 [.separator] (bits.map .bit) past

/-- The clean-exterior specialization used at a complete boundary's entry. -/
def word (bits : List Bool) : ℤ → Symbol := markedStream bits (fun _ => .blank)

inductive MovePhase where
  | copy | rewind | done
  deriving DecidableEq, Repr, Inhabited

instance : Fintype MovePhase :=
  ⟨{.copy, .rewind, .done}, by intro q; cases q <;> simp⟩

abbrev FlipPhase := MovePhase

@[simp] theorem view_head (h : ℤ) (l r : List Symbol) (p : ℤ → Symbol) :
    cellView h l r p h = r.getD 0 .blank := by simp [cellView]

theorem view_left (h : ℤ) (v : Symbol) (l r : List Symbol) (p : ℤ → Symbol) :
    cellView (h-1) l (v::r) p = cellView h (v::l) r p := by
  funext x
  by_cases hx : x < h-1
  · have hh : x < h := by omega
    have hi : (h-x-1).toNat = (h-1-x-1).toNat + 1 := by omega
    simp only [cellView, if_pos hx, if_pos hh, hi, List.length_cons]
    simp
  · by_cases hh : x < h
    · have he : x = h-1 := by omega
      subst x
      simp [cellView, show h - 1 < h by omega]
    · have hi : (x-(h-1)).toNat = (x-h).toNat + 1 := by omega
      simp [cellView, hx, hh, hi]

theorem view_expand (h : ℤ) (l r : List Symbol) (p : ℤ → Symbol) :
    cellView h l ((r.getD 0 .blank)::r.tail) p = cellView h l r p := by
  cases r with
  | cons v r => rfl
  | nil =>
    funext x
    simp only [cellView]
    split <;> simp

theorem view_right (h : ℤ) (l r : List Symbol) (p : ℤ → Symbol) :
    cellView (h+1) ((r.getD 0 .blank)::l) r.tail p = cellView h l r p := by
  have hs := view_left (h+1) (r.getD 0 .blank) l r.tail p
  have hh : h+1-1 = h := by omega
  rw [hh] at hs
  exact hs.symm.trans (view_expand h l r p)

theorem view_write (h : ℤ) (l r : List Symbol) (p : ℤ → Symbol) (v : Symbol) :
    cellView h l (v::r.tail) p = fun x => if x=h then v else cellView h l r p x := by
  funext x
  by_cases hx : x < h
  · have hn : x ≠ h := by omega
    simp [cellView, hx, hn]
  · by_cases he : x = h
    · subst x; simp [cellView]
    · have hi : (x-h).toNat > 0 := by omega
      cases r with
      | nil => simp [cellView, hx, he, hi.ne']
      | cons a r =>
        obtain ⟨k,hk⟩ := Nat.exists_eq_succ_of_ne_zero hi.ne'
        simp [cellView, hx, he, hk]

@[simp] theorem view_blank (h : ℤ) (l : List Symbol) (p : ℤ → Symbol) :
    cellView h l [.blank] p = cellView h l [] p := by
  simpa using view_expand h l [] p

theorem view_trailing_blank (h : ℤ) (l r : List Symbol) (p : ℤ → Symbol) :
    cellView h l (r ++ [.blank]) p = cellView h l r p := by
  have hg : ∀ (r : List Symbol) (n : ℕ), (r ++ [Symbol.blank]).getD n Symbol.blank = r.getD n Symbol.blank := by
    intro r
    induction r with
    | nil => intro n; cases n <;> simp
    | cons a r ih =>
      intro n
      cases n with
      | zero => simp
      | succ n => simpa using ih n
  funext x
  simp only [cellView]
  split
  · rfl
  · exact hg r _
structure TapeData where
  head : ℤ
  left : List Symbol
  right : List Symbol
  past : ℤ → Symbol

def TapeData.cell (t : TapeData) : ℤ → Symbol := cellView t.head t.left t.right t.past

def TapeData.read (t : TapeData) : Symbol := t.right.getD 0 .blank

def TapeData.write (t : TapeData) (v : Symbol) : TapeData := {t with right := v::t.right.tail}

def TapeData.rightward (t : TapeData) : TapeData :=
  ⟨t.head+1, t.read::t.left, t.right.tail, t.past⟩

/-- Requires a nonempty described left part when used as a physical operation. -/
def TapeData.leftward (t : TapeData) : TapeData :=
  ⟨t.head-1, t.left.tail, (t.left.getD 0 .blank)::t.right, t.past⟩

@[simp] theorem TapeData.cell_read (t : TapeData) : t.cell t.head = t.read := view_head _ _ _ _
@[simp] theorem TapeData.write_head (t : TapeData) (v : Symbol) : (t.write v).head = t.head := rfl
@[simp] theorem TapeData.write_cell (t : TapeData) (v : Symbol) :
    (t.write v).cell = fun x => if x=t.head then v else t.cell x := view_write _ _ _ _ _
@[simp] theorem TapeData.rightward_head (t : TapeData) : t.rightward.head = t.head+1 := rfl
@[simp] theorem TapeData.rightward_cell (t : TapeData) : t.rightward.cell = t.cell := view_right _ _ _ _
theorem TapeData.leftward_cell (t : TapeData) (hl : t.left ≠ []) :
    t.leftward.cell = t.cell := by
  rcases t with ⟨h,l,r,p⟩
  cases l with
  | nil => contradiction
  | cons v l => exact view_left h v l r p

/-- Exactly one charged local write and unit movement. -/
def Physical (t : TapeData) (a : Symbol × Move) (u : TapeData) : Prop :=
  u.head = t.head + moveOffset a.2 ∧
    u.cell = fun x => if x=t.head then a.1 else t.cell x

theorem physical_stay (t : TapeData) : Physical t (t.read,.stay) t := by
  constructor
  · simp [moveOffset]
  · funext x; by_cases hx : x=t.head <;> simp [hx]

theorem physical_right (t : TapeData) (v : Symbol) :
    Physical t (v,.right) (t.write v).rightward := by
  constructor <;> simp [moveOffset]

theorem physical_left (t : TapeData) (v : Symbol) (hl : t.left ≠ []) :
    Physical t (v,.left) (t.write v).leftward := by
  constructor
  · simp [TapeData.leftward, moveOffset, sub_eq_add_neg]
  · rw [TapeData.leftward_cell (t.write v) hl, TapeData.write_cell]

def SameTape (t u : TapeData) : Prop := t.head = u.head ∧ t.cell = u.cell

theorem Physical.congr {t u v : TapeData} {a : Symbol × Move}
    (h : Physical t a u) (he : SameTape u v) : Physical t a v := by
  exact ⟨he.1.symm.trans h.1, he.2.symm.trans h.2⟩

variable {ι : Type*} [Fintype ι] [DecidableEq ι]

def bank2 {Q : Type*} (s p : ι) (q : Q) (src park : TapeData)
    (heads : ι → ℤ) (cells : ι → ℤ → Symbol) : Config ι Symbol Q :=
  ⟨q, fun i => if i=s then src.head else if i=p then park.head else heads i,
    fun i => if i=s then src.cell else if i=p then park.cell else cells i⟩

def actions2 (s p : ι) (a b : Symbol × Move) (scanned : ι → Symbol) :
    ι → Symbol × Move :=
  fun i => if i=s then a else if i=p then b else (scanned i,.stay)

theorem bank2_step {Q : Type*} [Fintype Q] (P : Program ι Symbol Q)
    (s p : ι) (hne : s ≠ p) (q q' : Q) (t u t' u' : TapeData)
    (heads : ι → ℤ) (cells : ι → ℤ → Symbol) (a b : Symbol × Move)
    (htable : P.transition q
      (fun i => (bank2 s p q t u heads cells).cell i ((bank2 s p q t u heads cells).head i)) =
      some (q',actions2 s p a b
        (fun i => (bank2 s p q t u heads cells).cell i ((bank2 s p q t u heads cells).head i))))
    (ht : Physical t a t') (hu : Physical u b u') :
    step P (bank2 s p q t u heads cells) = some (bank2 s p q' t' u' heads cells) := by
  change P.transition (bank2 s p q t u heads cells).state _ = _ at htable
  simp only [step, htable, Option.map_some]
  congr 1
  apply Config.ext
  · rfl
  · funext i
    by_cases hs : i=s
    · subst i; simpa [bank2, actions2] using ht.1.symm
    · by_cases hp : i=p
      · subst i; simpa [bank2, actions2, hne, Ne.symm hne] using hu.1.symm
      · simp [bank2, actions2, hs, hp, moveOffset]
  · funext i x
    by_cases hs : i=s
    · subst i; simpa [bank2, actions2] using congrFun ht.2.symm x
    · by_cases hp : i=p
      · subst i; simpa [bank2, actions2, hne, Ne.symm hne] using congrFun hu.2.symm x
      · by_cases hx : x = heads i
        · simp [bank2, actions2, hs, hp, hx]
        · simp [bank2, actions2, hs, hp, hx]

end MultitapeToolkit.Absolute.MarkedStreams






