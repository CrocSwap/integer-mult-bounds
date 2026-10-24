import Mathproof.Meta.Problem18RAMLax13ProofsCompile20261001
import Mathproof.Meta.Problem18RAMLax13ProofsMachine20261001

set_option backward.isDefEq.respectTransparency false


/-!
The simulation theorem: a terminating IMP+ run whose values all stay
below `B` is matched, at every word length `w` with `B ≤ 2 ^ w`, by a
run of the compiled machine program, in a number of steps bounded by a
constant of the layout times the cost of the IMP+ run.

The word length is dealt with in one line of mathematics, repeated at
every instruction: `Nat.mod_eq_of_lt`. Under the bound, every value the
machine produces is already a word, so every `% 2 ^ w` of the concept's
semantics is the identity and the word machine tracks the unbounded
reference semantics of IMP+ exactly — not up to congruence modulo
`2 ^ w`, but on the nose. The one place where a value is *not* a word is
the shifted power of two of the lowered right shift, and there the
truncation is what makes the block right: `2 ^ n % 2 ^ w` is zero for a
shift distance of `w` or more, and division by zero is zero, which is
what the shift of a word by that distance is anyway.

The boundedness invariant is threaded through the ported induction
rather than routed through an auxiliary unbounded machine: there is
exactly one place per instruction where the bound is needed, the
hypotheses that supply it (`Layout.FitsWords` and the bounded
derivation) are already in scope there, and an intermediate machine
would have to be defined, given its own simulation, and then bridged —
three artefacts where the invariant costs one hypothesis.

The invariant is `Represents`: each scalar sits in its cell, each array
entry *within its declared length* sits in its cell, and the tapes
agree. Array lengths never reach the machine — they only decide which
IMP+ programs have a derivation — so the all-zero memory of a starting
machine represents an environment whose arrays are zero-filled, of
whatever lengths.

Straight-line code is described by `Reaches`, which bundles what every
such block guarantees: it gets to the instruction just past itself, in
at most as many steps as it has instructions, with the tapes untouched,
and touching only the temporaries from `d` upwards. That last clause is
the frame condition, and it is why the compiler can compile the operands
of a binary operator at consecutive depths and rely on the first result
surviving the second computation. What a block *computes* is not part of
`Reaches`: on this machine a value lives in a cell, so the value a block
leaves is stated separately, as `s'.mem d = v`, and the frame condition
is what carries it forward.
-/

namespace Lax13Proofs.Simulation

open Lax13.Ram Lax13Proofs.Imp Lax13Proofs.Compile Lax13Proofs.Machine

/-- The machine state `s` represents the environment `σ`. -/
structure Represents (L : Layout) (σ : Env) (s : State) : Prop where
  /-- Every scalar of the layout is in its cell. -/
  vars : ∀ x ∈ L.scalars, s.mem (L.varAddr x) = σ.vars x
  /-- Every array entry within the array's length is in its cell. -/
  arrs : ∀ a ∈ L.arrays, ∀ i, i < (σ.arrs a).length →
    s.mem (L.arrAddr a i) = (σ.arrs a).getD i 0
  /-- The input tapes agree. -/
  inp : s.inp = σ.inp
  /-- The output tapes agree. -/
  out : s.out = σ.out

/-- The straight-line block laid out at `s.pc` gets from `s` to `s'` at
word length `w`. `len` is its length and `d` the first temporary it is
allowed to touch. -/
structure Reaches (w : ℕ) (p : Program) (L : Layout) (d len : ℕ) (s s' : State) : Prop where
  /-- It takes at most as many steps as the block has instructions. -/
  steps : ∃ t ≤ len, run w p t s = some s'
  /-- It falls through to the instruction just past the block. -/
  pc : s'.pc = s.pc + len
  /-- It does not touch the input tape. -/
  inp : s'.inp = s.inp
  /-- It does not touch the output tape. -/
  out : s'.out = s.out
  /-- It writes only to the temporaries from `d` up to `L.temps + 1`. -/
  frame : ∀ i, i < d ∨ L.temps + 2 ≤ i → s'.mem i = s.mem i

theorem Reaches.trans {w p L d d' l₁ l₂ s s₁ s₂}
    (h₁ : Reaches w p L d l₁ s s₁) (h₂ : Reaches w p L d' l₂ s₁ s₂) (hd : d ≤ d') :
    Reaches w p L d (l₁ + l₂) s s₂ where
  steps := by
    obtain ⟨t₁, ht₁, hr₁⟩ := h₁.steps
    obtain ⟨t₂, ht₂, hr₂⟩ := h₂.steps
    exact ⟨t₁ + t₂, by omega, run_trans hr₁ hr₂⟩
  pc := by rw [h₂.pc, h₁.pc]; omega
  inp := by rw [h₂.inp, h₁.inp]
  out := by rw [h₂.out, h₁.out]
  frame i hi := by
    rw [h₂.frame i (by omega), h₁.frame i hi]

/-- The length of a block is only ever needed up to arithmetic. -/
theorem Reaches.congr {w p L d l l' s s'} (h : Reaches w p L d l s s') (hl : l = l') :
    Reaches w p L d l' s s' := hl ▸ h

/-- The empty block. -/
theorem reaches_nil (w : ℕ) (p : Program) (L : Layout) (d : ℕ) (s : State) :
    Reaches w p L d 0 s s :=
  ⟨⟨0, le_refl 0, rfl⟩, rfl, rfl, rfl, fun _ _ => rfl⟩

/-- **The workhorse.** Every instruction the compiler emits inside a
straight-line block writes one cell, and that cell is a temporary: at or
above the depth the block owns, and at most `L.temps + 1`. -/
theorem reaches_write {w : ℕ} {p : Program} {L : Layout} {d a v : ℕ} {s : State} {ins : Instr}
    (hf : p[s.pc]? = some ins)
    (he : ins.effect w s = some { s with pc := s.pc + 1, mem := setCell w s.mem a v })
    (haw : a < 2 ^ w) (hlo : d ≤ a) (hhi : a ≤ L.temps + 1) :
    ∃ s', Reaches w p L d 1 s s' ∧ s'.mem = setCell w s.mem a v ∧ s'.pc = s.pc + 1 := by
  refine ⟨{ s with pc := s.pc + 1, mem := setCell w s.mem a v },
    ⟨⟨1, le_refl 1, by rw [run_one hf, he]⟩, rfl, rfl, rfl, fun i hi => ?_⟩, rfl, rfl⟩
  show setCell w s.mem a v i = s.mem i
  exact setCell_of_ne _ _ haw (by omega)

/-- The invariant survives a straight-line block, which touches only
temporaries and neither tape. -/
theorem Represents.reaches {w L σ s p d len s'} (h : Represents L σ s)
    (hr : Reaches w p L d len s s') : Represents L σ s' where
  vars x hx := by rw [hr.frame _ (Or.inr (temps_le_varAddr L x))]; exact h.vars x hx
  arrs a ha i hi := by
    rw [hr.frame _ (Or.inr (temps_le_arrAddr L a i))]
    exact h.arrs a ha i hi
  inp := by rw [hr.inp]; exact h.inp
  out := by rw [hr.out]; exact h.out

/-- The invariant does not see the program counter. -/
theorem Represents.setPc {L σ s} (h : Represents L σ s) (n : ℕ) :
    Represents L σ { s with pc := n } :=
  ⟨h.vars, h.arrs, h.inp, h.out⟩

/-! ### Word-length housekeeping

Three inequalities are needed at almost every instruction: the two
extra temporary cells are addressable, and so is cell `1`, which the
compiled assignment uses for the address it stores through. -/

theorem one_lt_two_pow {L : Layout} {B w : ℕ} (h : L.FitsWords B w) : 1 < 2 ^ w :=
  lt_of_le_of_lt (Nat.le_add_left 1 L.temps) (L.temps_add_one_lt_two_pow h)

theorem lt_two_pow_of_le_temps {L : Layout} {B w d : ℕ} (h : L.FitsWords B w)
    (hd : d ≤ L.temps + 1) : d < 2 ^ w :=
  lt_of_le_of_lt hd (L.temps_add_one_lt_two_pow h)

/-! ### The block of a binary operator

Six of the nine operators are one instruction; the three that are not
are the blocks of the concept's notes, and this is where the identities
of `Machine.lean` are cashed. Every step writes a temporary, so every
step is one `reaches_write`. -/

theorem reaches_binCode {w B : ℕ} {p : Program} {L : Layout} {op : Bop} {d m n : ℕ}
    {s : State} (hfit : L.FitsWords B w) (hd : d < L.temps)
    (hn : s.mem d = n) (hm : s.mem (d + 1) = m) (hnB : n < B) (hmB : m < B)
    (hvB : op.apply m n < B) (hfits : Fits p s.pc (binCode op d)) :
    ∃ s', Reaches w p L d (binLen op) s s' ∧ s'.mem d = op.apply m n := by
  have hdw : d < 2 ^ w := lt_two_pow_of_le_temps hfit (by omega)
  have hd1w : d + 1 < 2 ^ w := lt_two_pow_of_le_temps hfit (by omega)
  have hd2w : d + 2 < 2 ^ w := lt_two_pow_of_le_temps hfit (by omega)
  have hnw : n < 2 ^ w := lt_of_lt_of_le hnB hfit.bound
  have hmw : m < 2 ^ w := lt_of_lt_of_le hmB hfit.bound
  have hvw : op.apply m n < 2 ^ w := lt_of_lt_of_le hvB hfit.bound
  have hlandw : Nat.land m n < 2 ^ w := lt_of_le_of_lt (land_le_left m n) hmw
  cases op with
  | add =>
      obtain ⟨s', hr, hmem, -⟩ := reaches_write (L := L) (d := d)
        (fits_singleton.mp hfits) (by rw [effect_add hd1w hdw, hm, hn]) hdw (le_refl d)
        (by omega)
      exact ⟨s', hr.congr (by simp [binLen]),
        by rw [hmem]; exact setCell_self _ hdw (by simpa using hvw)⟩
  | sub =>
      obtain ⟨s', hr, hmem, -⟩ := reaches_write (L := L) (d := d)
        (fits_singleton.mp hfits) (by rw [effect_sub hd1w hdw, hm, hn]) hdw (le_refl d)
        (by omega)
      exact ⟨s', hr.congr (by simp [binLen]),
        by rw [hmem]; exact setCell_self _ hdw (by simpa using hvw)⟩
  | mul =>
      obtain ⟨s', hr, hmem, -⟩ := reaches_write (L := L) (d := d)
        (fits_singleton.mp hfits) (by rw [effect_mul hd1w hdw, hm, hn]) hdw (le_refl d)
        (by omega)
      exact ⟨s', hr.congr (by simp [binLen]),
        by rw [hmem]; exact setCell_self _ hdw (by simpa using hvw)⟩
  | div =>
      obtain ⟨s', hr, hmem, -⟩ := reaches_write (L := L) (d := d)
        (fits_singleton.mp hfits) (by rw [effect_div hd1w hdw, hm, hn]) hdw (le_refl d)
        (by omega)
      exact ⟨s', hr.congr (by simp [binLen]),
        by rw [hmem]; exact setCell_self _ hdw (by simpa using hvw)⟩
  | and =>
      obtain ⟨s', hr, hmem, -⟩ := reaches_write (L := L) (d := d)
        (fits_singleton.mp hfits) (by rw [effect_and hd1w hdw, hm, hn]) hdw (le_refl d)
        (by omega)
      exact ⟨s', hr.congr (by simp [binLen]),
        by rw [hmem]; exact setCell_self _ hdw (by simpa using hvw)⟩
  | shiftl =>
      obtain ⟨s', hr, hmem, -⟩ := reaches_write (L := L) (d := d)
        (fits_singleton.mp hfits) (by rw [effect_shiftl hd1w hdw, hm, hn]) hdw (le_refl d)
        (by omega)
      exact ⟨s', hr.congr (by simp [binLen]),
        by rw [hmem]; exact setCell_self _ hdw (by simpa using hvw)⟩
  | or =>
      rw [show binCode .or d = [Instr.and (d + 2) (d + 1) d] ++
            ([Instr.sub (d + 2) d (d + 2)] ++ [Instr.add d (d + 1) (d + 2)]) from rfl,
        fits_append, fits_append] at hfits
      obtain ⟨hf₁, hf₂, hf₃⟩ := hfits
      -- `and t b c`
      obtain ⟨s₁, h₁, hmem₁, hpc₁⟩ := reaches_write (L := L) (d := d)
        (fits_singleton.mp hf₁) (by rw [effect_and hd1w hdw, hm, hn]) hd2w (by omega) (by omega)
      have e₁d : s₁.mem d = n := by rw [hmem₁, setCell_of_ne _ _ hd2w (by omega), hn]
      have e₁d1 : s₁.mem (d + 1) = m := by rw [hmem₁, setCell_of_ne _ _ hd2w (by omega), hm]
      have e₁d2 : s₁.mem (d + 2) = Nat.land m n := by
        rw [hmem₁]; exact setCell_self _ hd2w hlandw
      -- `sub t c t`
      obtain ⟨s₂, h₂, hmem₂, hpc₂⟩ := reaches_write (L := L) (d := d)
        (fits_singleton.mp (by rw [hpc₁]; simpa using hf₂))
        (by rw [effect_sub hdw hd2w, e₁d, e₁d2]) hd2w (by omega) (by omega)
      have e₂d1 : s₂.mem (d + 1) = m := by rw [hmem₂, setCell_of_ne _ _ hd2w (by omega), e₁d1]
      have e₂d2 : s₂.mem (d + 2) = n - Nat.land m n := by
        rw [hmem₂]; exact setCell_self _ hd2w (by omega)
      -- `add a b t`
      obtain ⟨s₃, h₃, hmem₃, -⟩ := reaches_write (L := L) (d := d)
        (fits_singleton.mp (by rw [hpc₂, hpc₁]; simpa [Nat.add_assoc] using hf₃))
        (by rw [effect_add hd1w hd2w, e₂d1, e₂d2]) hdw (le_refl d) (by omega)
      refine ⟨s₃, ((h₁.trans h₂ (le_refl d)).trans h₃ (le_refl d)).congr (by simp [binLen]), ?_⟩
      rw [hmem₃, setCell_self _ hdw (by rw [← lor_eq_add_sub_land]; simpa using hvw),
        ← lor_eq_add_sub_land]
      rfl
  | xor =>
      rw [show binCode .xor d = [Instr.and (d + 2) (d + 1) d] ++
            ([Instr.sub d d (d + 2)] ++
              ([Instr.add d (d + 1) d] ++ [Instr.sub d d (d + 2)])) from rfl,
        fits_append, fits_append, fits_append] at hfits
      obtain ⟨hf₁, hf₂, hf₃, hf₄⟩ := hfits
      have hlorw : Nat.lor m n < 2 ^ w := lor_lt_two_pow hmw hnw
      -- `and t b c`
      obtain ⟨s₁, h₁, hmem₁, hpc₁⟩ := reaches_write (L := L) (d := d)
        (fits_singleton.mp hf₁) (by rw [effect_and hd1w hdw, hm, hn]) hd2w (by omega) (by omega)
      have e₁d : s₁.mem d = n := by rw [hmem₁, setCell_of_ne _ _ hd2w (by omega), hn]
      have e₁d1 : s₁.mem (d + 1) = m := by rw [hmem₁, setCell_of_ne _ _ hd2w (by omega), hm]
      have e₁d2 : s₁.mem (d + 2) = Nat.land m n := by
        rw [hmem₁]; exact setCell_self _ hd2w hlandw
      -- `sub u c t`
      obtain ⟨s₂, h₂, hmem₂, hpc₂⟩ := reaches_write (L := L) (d := d)
        (fits_singleton.mp (by rw [hpc₁]; simpa using hf₂))
        (by rw [effect_sub hdw hd2w, e₁d, e₁d2]) hdw (le_refl d) (by omega)
      have e₂d : s₂.mem d = n - Nat.land m n := by
        rw [hmem₂]; exact setCell_self _ hdw (by omega)
      have e₂d1 : s₂.mem (d + 1) = m := by rw [hmem₂, setCell_of_ne _ _ hdw (by omega), e₁d1]
      have e₂d2 : s₂.mem (d + 2) = Nat.land m n := by
        rw [hmem₂, setCell_of_ne _ _ hdw (by omega), e₁d2]
      -- `add u b u`
      obtain ⟨s₃, h₃, hmem₃, hpc₃⟩ := reaches_write (L := L) (d := d)
        (fits_singleton.mp (by rw [hpc₂, hpc₁]; simpa [Nat.add_assoc] using hf₃))
        (by rw [effect_add hd1w hdw, e₂d1, e₂d]) hdw (le_refl d) (by omega)
      have e₃d : s₃.mem d = Nat.lor m n := by
        rw [hmem₃, setCell_self _ hdw (by rw [← lor_eq_add_sub_land]; exact hlorw),
          ← lor_eq_add_sub_land]
      have e₃d2 : s₃.mem (d + 2) = Nat.land m n := by
        rw [hmem₃, setCell_of_ne _ _ hdw (by omega), e₂d2]
      -- `sub a u t`
      obtain ⟨s₄, h₄, hmem₄, -⟩ := reaches_write (L := L) (d := d)
        (fits_singleton.mp (by rw [hpc₃, hpc₂, hpc₁]; simpa [Nat.add_assoc] using hf₄))
        (by rw [effect_sub hdw hd2w, e₃d, e₃d2]) hdw (le_refl d) (by omega)
      refine ⟨s₄, (((h₁.trans h₂ (le_refl d)).trans h₃ (le_refl d)).trans h₄
        (le_refl d)).congr (by simp [binLen]), ?_⟩
      have hxor : Nat.lor m n - Nat.land m n = Nat.xor m n := by
        rw [xor_eq_sub_add_sub_land, lor_eq_add_sub_land]
      rw [hmem₄, setCell_self _ hdw (by rw [hxor]; simpa using hvw), hxor]
      rfl
  | shiftr =>
      rw [show binCode .shiftr d = [Instr.set (d + 2) 1] ++
            ([Instr.shiftl (d + 2) (d + 2) d] ++ [Instr.div d (d + 1) (d + 2)]) from rfl,
        fits_append, fits_append] at hfits
      obtain ⟨hf₁, hf₂, hf₃⟩ := hfits
      have h1w : 1 < 2 ^ w := one_lt_two_pow hfit
      -- `set t 1`
      obtain ⟨s₁, h₁, hmem₁, hpc₁⟩ := reaches_write (L := L) (d := d)
        (fits_singleton.mp hf₁) (effect_set w (d + 2) 1 s) hd2w (by omega) (by omega)
      have e₁d : s₁.mem d = n := by rw [hmem₁, setCell_of_ne _ _ hd2w (by omega), hn]
      have e₁d1 : s₁.mem (d + 1) = m := by rw [hmem₁, setCell_of_ne _ _ hd2w (by omega), hm]
      have e₁d2 : s₁.mem (d + 2) = 1 := by rw [hmem₁]; exact setCell_self _ hd2w h1w
      -- `shiftl t t c`
      obtain ⟨s₂, h₂, hmem₂, hpc₂⟩ := reaches_write (L := L) (d := d)
        (fits_singleton.mp (by rw [hpc₁]; simpa using hf₂))
        (by rw [effect_shiftl hd2w hdw, e₁d, e₁d2]) hd2w (by omega) (by omega)
      have e₂d1 : s₂.mem (d + 1) = m := by rw [hmem₂, setCell_of_ne _ _ hd2w (by omega), e₁d1]
      have e₂d2 : s₂.mem (d + 2) = 2 ^ n % 2 ^ w := by
        rw [hmem₂, setCell_self_mod _ _ hd2w, Nat.one_mul]
      -- `div a b t`
      obtain ⟨s₃, h₃, hmem₃, -⟩ := reaches_write (L := L) (d := d)
        (fits_singleton.mp (by rw [hpc₂, hpc₁]; simpa [Nat.add_assoc] using hf₃))
        (by rw [effect_div hd1w hd2w, e₂d1, e₂d2]) hdw (le_refl d) (by omega)
      refine ⟨s₃, ((h₁.trans h₂ (le_refl d)).trans h₃ (le_refl d)).congr (by simp [binLen]), ?_⟩
      rw [hmem₃, div_two_pow_mod_two_pow n hmw,
        setCell_self _ hdw (by simpa using hvw)]
      rfl

/-! ### Address arithmetic

`Layout.idxCode` is the only place where the interleaved layout is
computed with: the index in cell `d` becomes the address of that entry
of `a`, in the same cell, through one multiplication and one addition.
Every intermediate is below the address it builds, which the layout's
span keeps a word. -/

theorem reaches_idxCode {w B : ℕ} {p : Program} {L : Layout} {a : String} {d k : ℕ}
    {s : State} (hfit : L.FitsWords B w) (ha : a ∈ L.arrays) (hd : d < L.temps)
    (hk : s.mem d = k) (hkB : k < B) (hfits : Fits p s.pc (L.idxCode a d)) :
    ∃ s', Reaches w p L d L.idxLen s s' ∧ s'.mem d = L.arrAddr a k := by
  have hdw : d < 2 ^ w := lt_two_pow_of_le_temps hfit (by omega)
  have hd1w : d + 1 < 2 ^ w := lt_two_pow_of_le_temps hfit (by omega)
  have hqw : L.arrays.length < 2 ^ w := L.arrays_length_lt_two_pow hfit
  have hbw : L.arrBase a < 2 ^ w := L.arrBase_lt_two_pow hfit ha
  have haddr : L.arrAddr a k < 2 ^ w := L.arrAddr_lt_two_pow hfit ha hkB
  have hmulw : k * L.arrays.length < 2 ^ w := by
    have := L.mul_le_arrAddr a k
    have : L.arrays.length * k = k * L.arrays.length := Nat.mul_comm _ _
    omega
  rw [show L.idxCode a d = [Instr.set (d + 1) L.arrays.length] ++
        ([Instr.mul d d (d + 1)] ++
          ([Instr.set (d + 1) (L.arrBase a)] ++ [Instr.add d d (d + 1)])) from rfl,
    fits_append, fits_append, fits_append] at hfits
  obtain ⟨hf₁, hf₂, hf₃, hf₄⟩ := hfits
  -- the stride into the scratch cell
  obtain ⟨s₁, h₁, hmem₁, hpc₁⟩ := reaches_write (L := L) (d := d)
    (fits_singleton.mp hf₁) (effect_set w (d + 1) L.arrays.length s) hd1w (by omega) (by omega)
  have e₁d : s₁.mem d = k := by rw [hmem₁, setCell_of_ne _ _ hd1w (by omega), hk]
  have e₁d1 : s₁.mem (d + 1) = L.arrays.length := by
    rw [hmem₁]; exact setCell_self _ hd1w hqw
  -- index times stride
  obtain ⟨s₂, h₂, hmem₂, hpc₂⟩ := reaches_write (L := L) (d := d)
    (fits_singleton.mp (by rw [hpc₁]; simpa using hf₂))
    (by rw [effect_mul hdw hd1w, e₁d, e₁d1]) hdw (le_refl d) (by omega)
  have e₂d : s₂.mem d = k * L.arrays.length := by
    rw [hmem₂]; exact setCell_self _ hdw hmulw
  -- the base into the scratch cell
  obtain ⟨s₃, h₃, hmem₃, hpc₃⟩ := reaches_write (L := L) (d := d)
    (fits_singleton.mp (by rw [hpc₂, hpc₁]; simpa [Nat.add_assoc] using hf₃))
    (effect_set w (d + 1) (L.arrBase a) s₂) hd1w (by omega) (by omega)
  have e₃d : s₃.mem d = k * L.arrays.length := by
    rw [hmem₃, setCell_of_ne _ _ hd1w (by omega), e₂d]
  have e₃d1 : s₃.mem (d + 1) = L.arrBase a := by
    rw [hmem₃]; exact setCell_self _ hd1w hbw
  -- the address
  obtain ⟨s₄, h₄, hmem₄, -⟩ := reaches_write (L := L) (d := d)
    (fits_singleton.mp (by rw [hpc₃, hpc₂, hpc₁]; simpa [Nat.add_assoc] using hf₄))
    (by rw [effect_add hdw hd1w, e₃d, e₃d1]) hdw (le_refl d) (by omega)
  have hsum : k * L.arrays.length + L.arrBase a = L.arrAddr a k := by
    simp only [Layout.arrAddr]; rw [Nat.mul_comm]; omega
  refine ⟨s₄, (((h₁.trans h₂ (le_refl d)).trans h₃ (le_refl d)).trans h₄
    (le_refl d)).congr (by simp [Layout.idxLen]), ?_⟩
  rw [hmem₄, hsum]
  exact setCell_self _ hdw haddr

/-! ### Expressions -/

/-- Compiled expressions: the code evaluates `e` into the temporary `d`,
falls through, leaves the tapes alone, and writes only to temporaries
from `d` upwards. The bounded evaluation is what makes this an
equality: every value the machine produces along the way is a word, so
no reduction modulo `2 ^ w` is visible. -/
theorem compileExpr_correct {L : Layout} {B w : ℕ} {σ : Env} {p : Program}
    (hfit : L.FitsWords B w) (e : Expr) :
    ∀ (d v : ℕ) (s : State), d ≤ L.temps + 1 → Expr.Ok L e d → e.evalB B σ = some v →
      Represents L σ s → Fits p s.pc (compileExpr L e d) →
      ∃ s', Reaches w p L d (esize L e) s s' ∧ s'.mem d = v := by
  induction e with
  | lit n =>
      intro d v s hdt _ hv _ hfits
      simp only [Expr.evalB] at hv
      rw [fit_eq_some] at hv
      obtain ⟨rfl, hn⟩ := hv
      have hdw : d < 2 ^ w := lt_two_pow_of_le_temps hfit hdt
      obtain ⟨s', hr, hmem, -⟩ := reaches_write (L := L) (d := d)
        (fits_singleton.mp hfits) (effect_set w d v s) hdw (le_refl d) hdt
      exact ⟨s', hr.congr (by simp [esize]),
        by rw [hmem]; exact setCell_self _ hdw (lt_of_lt_of_le hn hfit.bound)⟩
  | var x =>
      intro d v s hdt hok hv hrep hfits
      simp only [Expr.evalB] at hv
      rw [fit_eq_some] at hv
      obtain ⟨rfl, hn⟩ := hv
      have hdw : d < 2 ^ w := lt_two_pow_of_le_temps hfit hdt
      have hxw : L.varAddr x < 2 ^ w := L.varAddr_lt_two_pow hfit hok
      have hxt : L.temps + 2 ≤ L.varAddr x := temps_le_varAddr L x
      rw [show compileExpr L (.var x) d
            = [Instr.set d (L.varAddr x)] ++ [Instr.load d d] from rfl,
        fits_append] at hfits
      obtain ⟨hf₁, hf₂⟩ := hfits
      obtain ⟨s₁, h₁, hmem₁, hpc₁⟩ := reaches_write (L := L) (d := d)
        (fits_singleton.mp hf₁) (effect_set w d (L.varAddr x) s) hdw (le_refl d) hdt
      have e₁d : s₁.mem d = L.varAddr x := by rw [hmem₁]; exact setCell_self _ hdw hxw
      have e₁x : s₁.mem (L.varAddr x) = σ.vars x := by
        rw [hmem₁, setCell_of_ne _ _ hdw (by omega)]; exact hrep.vars x hok
      obtain ⟨s₂, h₂, hmem₂, -⟩ := reaches_write (L := L) (d := d)
        (fits_singleton.mp (by rw [hpc₁]; simpa using hf₂))
        (by rw [effect_load hdw (by rw [e₁d]; exact hxw), e₁d, e₁x]) hdw (le_refl d) hdt
      exact ⟨s₂, (h₁.trans h₂ (le_refl d)).congr (by simp [esize]),
        by rw [hmem₂]; exact setCell_self _ hdw (lt_of_lt_of_le hn hfit.bound)⟩
  | get a i ih =>
      intro d v s hdt hok hv hrep hfits
      obtain ⟨ha, hoki, hd⟩ := hok
      simp only [Expr.evalB] at hv
      rw [Option.bind_eq_some_iff] at hv
      obtain ⟨k, hk, hv⟩ := hv
      rw [Option.bind_eq_some_iff] at hv
      obtain ⟨u, hu, hv⟩ := hv
      rw [fit_eq_some] at hv
      obtain ⟨rfl, hvB⟩ := hv
      have hkB : k < B := Expr.lt_of_evalB hk
      have hdw : d < 2 ^ w := lt_two_pow_of_le_temps hfit hdt
      have haddr : L.arrAddr a k < 2 ^ w := L.arrAddr_lt_two_pow hfit ha hkB
      have hat : L.temps + 2 ≤ L.arrAddr a k := temps_le_arrAddr L a k
      rw [List.getElem?_eq_some_iff] at hu
      obtain ⟨hklt, hkv⟩ := hu
      rw [show compileExpr L (.get a i) d
            = compileExpr L i d ++ (L.idxCode a d ++ [Instr.load d d]) from by
          simp [compileExpr, List.append_assoc],
          fits_append, fits_append] at hfits
      obtain ⟨hf₁, hf₂, hf₃⟩ := hfits
      obtain ⟨s₁, h₁, e₁d⟩ := ih d k s hdt hoki hk hrep hf₁
      obtain ⟨s₂, h₂, e₂d⟩ := reaches_idxCode hfit ha hd e₁d hkB
        (by rw [h₁.pc]; simpa using hf₂)
      have e₂a : s₂.mem (L.arrAddr a k) = v := by
        rw [h₂.frame _ (Or.inr hat), h₁.frame _ (Or.inr hat), hrep.arrs a ha k hklt,
          List.getD_eq_getElem?_getD, List.getElem?_eq_getElem hklt, hkv]
        rfl
      obtain ⟨s₃, h₃, hmem₃, -⟩ := reaches_write (L := L) (d := d)
        (fits_singleton.mp (by rw [h₂.pc, h₁.pc]; simpa [Nat.add_assoc] using hf₃))
        (by rw [effect_load hdw (by rw [e₂d]; exact haddr), e₂d, e₂a]) hdw (le_refl d) hdt
      exact ⟨s₃, ((h₁.trans h₂ (le_refl d)).trans h₃ (le_refl d)).congr (by simp [esize]),
        by rw [hmem₃]; exact setCell_self _ hdw (lt_of_lt_of_le hvB hfit.bound)⟩
  | bin op e f ihe ihf =>
      intro d v s hdt hok hv hrep hfits
      obtain ⟨hokf, hoke, hd⟩ := hok
      simp only [Expr.evalB] at hv
      rw [Option.bind_eq_some_iff] at hv
      obtain ⟨m, hm, hv⟩ := hv
      rw [Option.bind_eq_some_iff] at hv
      obtain ⟨n, hn, hv⟩ := hv
      rw [fit_eq_some] at hv
      obtain ⟨rfl, hvB⟩ := hv
      have hmB : m < B := Expr.lt_of_evalB hm
      have hnB : n < B := Expr.lt_of_evalB hn
      rw [show compileExpr L (.bin op e f) d
            = compileExpr L f d ++ (compileExpr L e (d + 1) ++ binCode op d) from by
          simp [compileExpr, List.append_assoc],
          fits_append, fits_append] at hfits
      obtain ⟨hf₁, hf₂, hf₃⟩ := hfits
      obtain ⟨s₁, h₁, e₁d⟩ := ihf d n s hdt hokf hn hrep hf₁
      obtain ⟨s₂, h₂, e₂d1⟩ := ihe (d + 1) m s₁ (by omega) hoke hm
        (hrep.reaches h₁) (by rw [h₁.pc]; simpa using hf₂)
      have e₂d : s₂.mem d = n := by rw [h₂.frame d (Or.inl (by omega)), e₁d]
      obtain ⟨s₃, h₃, e₃d⟩ := reaches_binCode hfit hd e₂d e₂d1 hnB hmB hvB
        (by rw [h₂.pc, h₁.pc]; simpa [Nat.add_assoc] using hf₃)
      exact ⟨s₃, ((h₁.trans h₂ (by omega)).trans h₃ (le_refl d)).congr (by simp [esize]), e₃d⟩

/-- Compiled conditions: the code leaves zero in the temporary `d`
exactly when the condition holds. -/
theorem compileCond_correct {L : Layout} {B w : ℕ} {σ : Env} {p : Program} {b : Cond} {d : ℕ}
    {r : Bool} {s : State} (hfit : L.FitsWords B w) (hdt : d ≤ L.temps + 1)
    (hok : Cond.Ok L b d) (hv : b.evalB B σ = some r) (hrep : Represents L σ s)
    (hfits : Fits p s.pc (compileCond L b d)) :
    ∃ (s' : State) (v : ℕ), Reaches w p L d (bsize L b) s s' ∧ s'.mem d = v ∧
      (v = 0 ↔ r = true) := by
  obtain ⟨v, hev, hiff⟩ := condExpr_evalB hfit.one_lt hv
  obtain ⟨s', hr, hval⟩ := compileExpr_correct hfit (condExpr b) d v s hdt hok hev hrep hfits
  exact ⟨s', v, hr, hval, hiff⟩

/-! ### The constant

Every construct of IMP+ costs at least one, and compiles to at most a
fixed number of instructions per unit of that cost. The fixed number
depends neither on the layout nor on the program, the input or the word
length. Nothing here is tight. -/

theorem esize_le_size (L : Layout) (e : Expr) : esize L e ≤ 5 * e.size := by
  induction e with
  | lit n => simp [esize, Expr.size]
  | var x => simp [esize, Expr.size]
  | get a i ih =>
      simp only [esize, Expr.size, Layout.idxLen, Nat.mul_add, Nat.mul_one]
      omega
  | bin op e f ihe ihf =>
      have := binLen_le_four op
      simp only [esize, Expr.size, Nat.mul_add, Nat.mul_one]
      omega

theorem esize_le (L : Layout) (e : Expr) : esize L e ≤ L.const * e.size :=
  le_trans (esize_le_size L e)
    (Nat.mul_le_mul_right _ (by simp only [Layout.const]; omega))

theorem bsize_le (L : Layout) (b : Cond) : bsize L b ≤ L.const * b.size := by
  cases b with
  | eq e f =>
      have he := esize_le_size L e
      have hf := esize_le_size L f
      have h1 : 2 * (5 * e.size) ≤ L.const * e.size := by
        rw [← Nat.mul_assoc]; exact Nat.mul_le_mul_right _ (by simp only [Layout.const]; omega)
      have h2 : 2 * (5 * f.size) ≤ L.const * f.size := by
        rw [← Nat.mul_assoc]; exact Nat.mul_le_mul_right _ (by simp only [Layout.const]; omega)
      have hc : (10 : ℕ) ≤ L.const := by simp only [Layout.const]; omega
      simp only [bsize, condExpr, esize, binLen, Cond.size, Nat.mul_add, Nat.mul_one]
      omega
  | lt e f =>
      have he := esize_le_size L e
      have hf := esize_le_size L f
      have h1 : 5 * e.size ≤ L.const * e.size :=
        Nat.mul_le_mul_right _ (by simp only [Layout.const]; omega)
      have h2 : 5 * f.size ≤ L.const * f.size :=
        Nat.mul_le_mul_right _ (by simp only [Layout.const]; omega)
      have hc : (10 : ℕ) ≤ L.const := by simp only [Layout.const]; omega
      simp only [bsize, condExpr, esize, binLen, Cond.size, Nat.mul_add, Nat.mul_one]
      omega

theorem idxLen_le_const (L : Layout) : L.idxLen + 1 ≤ L.const := by
  simp only [Layout.const, Layout.idxLen]; omega

theorem one_le_const (L : Layout) : 1 ≤ L.const := by simp only [Layout.const]; omega

theorem two_le_const (L : Layout) : 2 ≤ L.const := by simp only [Layout.const]; omega

/-! ### Jumps -/

theorem run_jump {w : ℕ} {p : Program} {s : State} {l : ℕ}
    (h : p[s.pc]? = some (Instr.jump l)) :
    run w p 1 s = some { s with pc := l } := by rw [run_one h]; rfl

theorem run_jzero {w : ℕ} {p : Program} {s : State} {a l : ℕ} (ha : a < 2 ^ w)
    (h : p[s.pc]? = some (Instr.jzero a l)) :
    run w p 1 s = some { s with pc := if s.mem a = 0 then l else s.pc + 1 } := by
  rw [run_one h, effect_jzero ha]

/-! ### The simulation theorem -/

/-- A terminating IMP+ run all of whose values stay below `B` is
matched by a run of the compiled code at any word length that fits the
layout and the bound: from any machine state representing the initial
environment, with the code laid out at the program counter, the machine
reaches the instruction just past the code in at most `L.const` steps
per unit of IMP+ cost, in a state representing the final
environment. -/
theorem compile_correct {L : Layout} {B w : ℕ} {p : Program} {c : Com} {σ σ' : Env} {k : ℕ}
    (hfit : L.FitsWords B w) (hbs : BigStepB B c σ σ' k) :
    Com.Ok L c → σ.InpBounded B → ∀ (a : ℕ) (s : State), s.pc = a → Represents L σ s →
      Fits p a (compile L c a) →
      ∃ (t : ℕ) (s' : State), t ≤ L.const * k ∧ run w p t s = some s' ∧
        s'.pc = a + size L c ∧ Represents L σ' s' := by
  have hzw : (0 : ℕ) < 2 ^ w := two_pow_pos w
  have h1w : 1 < 2 ^ w := one_lt_two_pow hfit
  induction hbs with
  | @skip σ =>
      intro _ _ a s hpc hrep _
      exact ⟨0, s, by simp, rfl, by simp [size, hpc], hrep⟩
  | @assign σ x e v hev =>
      intro hok _ a s hpc hrep hfits
      obtain ⟨hx, hoke⟩ := hok
      have hvw : v < 2 ^ w := lt_of_lt_of_le (Expr.lt_of_evalB hev) hfit.bound
      have hxw : L.varAddr x < 2 ^ w := L.varAddr_lt_two_pow hfit hx
      have hxt : L.temps + 2 ≤ L.varAddr x := temps_le_varAddr L x
      rw [show compile L (.assign x e) a
            = compileExpr L e 0 ++ ([Instr.set 1 (L.varAddr x)] ++ [Instr.store 1 0]) from by
          simp [compile], fits_append, fits_append] at hfits
      obtain ⟨hf₁, hf₂, hf₃⟩ := hfits
      obtain ⟨s₁, h₁, e₁0⟩ :=
        compileExpr_correct hfit e 0 v s (by omega) hoke hev hrep (hf₁.congr hpc.symm)
      obtain ⟨s₂, h₂, hmem₂, hpc₂⟩ := reaches_write (L := L) (d := 0)
        (fits_singleton.mp (by rw [h₁.pc, hpc]; simpa using hf₂))
        (effect_set w 1 (L.varAddr x) s₁) h1w (by omega) (by omega)
      have e₂0 : s₂.mem 0 = v := by rw [hmem₂, setCell_of_ne _ _ h1w (by omega), e₁0]
      have e₂1 : s₂.mem 1 = L.varAddr x := by rw [hmem₂]; exact setCell_self _ h1w hxw
      have hf₃' : p[s₂.pc]? = some (Instr.store 1 0) := by
        rw [hpc₂, h₁.pc, hpc]
        exact fits_singleton.mp (by simpa [Nat.add_assoc] using hf₃)
      obtain ⟨t₁, ht₁, hr₁⟩ := (h₁.trans h₂ (le_refl 0)).steps
      refine ⟨t₁ + 1, _, ?_, run_trans hr₁ (by rw [run_one hf₃', effect_store h1w hzw]), ?_, ?_⟩
      · simp only [Nat.mul_add, Nat.mul_one]
        have := esize_le L e
        have := two_le_const L
        omega
      · show s₂.pc + 1 = a + size L (.assign x e)
        rw [hpc₂, h₁.pc, hpc]; simp [size]; omega
      · refine ⟨fun y hy => ?_, fun b hb i hi => ?_, ?_, ?_⟩
        · show setCell w s₂.mem (s₂.mem 1) (s₂.mem 0) (L.varAddr y) = _
          rw [e₂0, e₂1]
          by_cases hxy : y = x
          · subst hxy
            rw [setCell_self _ hxw hvw]
            simp [Env.setVar]
          · rw [setCell_of_ne _ _ hxw (fun hc => hxy (varAddr_inj L hy hx hc)),
              h₂.frame _ (Or.inr (temps_le_varAddr L y)),
              h₁.frame _ (Or.inr (temps_le_varAddr L y)), hrep.vars y hy]
            simp [Env.setVar, hxy]
        · show setCell w s₂.mem (s₂.mem 1) (s₂.mem 0) (L.arrAddr b i) = _
          rw [e₂0, e₂1, setCell_of_ne _ _ hxw (fun hc => varAddr_ne_arrAddr L hx i hc.symm),
            h₂.frame _ (Or.inr (temps_le_arrAddr L b i)),
            h₁.frame _ (Or.inr (temps_le_arrAddr L b i))]
          exact hrep.arrs b hb i hi
        · show s₂.inp = _; rw [h₂.inp, h₁.inp]; exact hrep.inp
        · show s₂.out = _; rw [h₂.out, h₁.out]; exact hrep.out
  | @seq c d σ σ₁ σ₂ k k' hbs₁ _ ih ih' =>
      intro hok hinp a s hpc hrep hfits
      obtain ⟨hokc, hokd⟩ := hok
      rw [show compile L (.seq c d) a = compile L c a ++ compile L d (a + size L c) from rfl,
        fits_append] at hfits
      obtain ⟨hf₁, hf₂⟩ := hfits
      obtain ⟨t₁, s₁, ht₁, hr₁, hpc₁, hrep₁⟩ := ih hokc hinp a s hpc hrep hf₁
      obtain ⟨t₂, s₂, ht₂, hr₂, hpc₂, hrep₂⟩ :=
        ih' hokd (hbs₁.inpBounded hinp) (a + size L c) s₁ hpc₁ hrep₁ (by simpa using hf₂)
      refine ⟨t₁ + t₂, s₂, ?_, run_trans hr₁ hr₂, ?_, hrep₂⟩
      · simp only [Nat.mul_add]; omega
      · rw [hpc₂]; simp [size]; omega
  | @read σ x v rest hinp' =>
      intro hok hinp a s hpc hrep hfits
      have hvB : v < B := hinp v (by rw [hinp']; exact List.mem_cons_self ..)
      have hvw : v < 2 ^ w := lt_of_lt_of_le hvB hfit.bound
      have hxw : L.varAddr x < 2 ^ w := L.varAddr_lt_two_pow hfit hok
      have hs : s.inp = v :: rest := by rw [hrep.inp]; exact hinp'
      have hf : p[s.pc]? = some (Instr.read (L.varAddr x)) :=
        fits_singleton.mp (by rw [hpc]; simpa only [compile] using hfits)
      refine ⟨1, _, ?_, by rw [run_one hf, effect_read _ hs], ?_, ?_⟩
      · simp only [Nat.mul_one]; exact one_le_const L
      · show s.pc + 1 = a + size L (.read x); rw [hpc]; simp [size]
      · refine ⟨fun y hy => ?_, fun b hb i hi => ?_, rfl, ?_⟩
        · show setCell w s.mem (L.varAddr x) v (L.varAddr y) = _
          by_cases hxy : y = x
          · subst hxy; rw [setCell_self _ hxw hvw]; simp [Env.setVar]
          · rw [setCell_of_ne _ _ hxw (fun hc => hxy (varAddr_inj L hy hok hc)), hrep.vars y hy]
            simp [Env.setVar, hxy]
        · show setCell w s.mem (L.varAddr x) v (L.arrAddr b i) = _
          rw [setCell_of_ne _ _ hxw (fun hc => varAddr_ne_arrAddr L hok i hc.symm)]
          exact hrep.arrs b hb i hi
        · show s.out = _; exact hrep.out
  | @write σ e v hev =>
      intro hok _ a s hpc hrep hfits
      obtain ⟨hoke, htemps⟩ := hok
      have hvw : v < 2 ^ w := lt_of_lt_of_le (Expr.lt_of_evalB hev) hfit.bound
      rw [show compile L (.write e) a = compileExpr L e 0 ++ [Instr.write 0] from rfl,
        fits_append] at hfits
      obtain ⟨hf₁, hf₂⟩ := hfits
      obtain ⟨s₁, h₁, e₁0⟩ :=
        compileExpr_correct hfit e 0 v s (by omega) hoke hev hrep (hf₁.congr hpc.symm)
      obtain ⟨t₁, ht₁, hr₁⟩ := h₁.steps
      have hf₂' : p[s₁.pc]? = some (Instr.write 0) := by
        rw [h₁.pc, hpc]; exact fits_singleton.mp (by simpa using hf₂)
      refine ⟨t₁ + 1, _, ?_,
        run_trans hr₁ (by rw [run_one hf₂', effect_write hzw (by rw [e₁0]; exact hvw)]), ?_, ?_⟩
      · simp only [Nat.mul_add, Nat.mul_one]
        have := esize_le L e
        have := one_le_const L
        omega
      · show s₁.pc + 1 = a + size L (.write e)
        rw [h₁.pc, hpc]; simp [size]; omega
      · refine ⟨fun y hy => ?_, fun b hb i hi => ?_, ?_, ?_⟩
        · show s₁.mem (L.varAddr y) = _
          rw [h₁.frame _ (Or.inr (temps_le_varAddr L y))]; exact hrep.vars y hy
        · show s₁.mem (L.arrAddr b i) = _
          rw [h₁.frame _ (Or.inr (temps_le_arrAddr L b i))]; exact hrep.arrs b hb i hi
        · show s₁.inp = _; rw [h₁.inp]; exact hrep.inp
        · show s₁.out ++ [s₁.mem 0] = _
          rw [e₁0, h₁.out, hrep.out]
  | @store σ arr i e kk v hi hev hk =>
      intro hok _ a s hpc hrep hfits
      obtain ⟨ha, hoki, hoke, htemps⟩ := hok
      have hkkB : kk < B := Expr.lt_of_evalB hi
      have hvw : v < 2 ^ w := lt_of_lt_of_le (Expr.lt_of_evalB hev) hfit.bound
      have haddr : L.arrAddr arr kk < 2 ^ w := L.arrAddr_lt_two_pow hfit ha hkkB
      rw [show compile L (.store arr i e) a
            = compileExpr L i 0 ++ (L.idxCode arr 0 ++
                (compileExpr L e 1 ++ [Instr.store 0 1])) from by
          simp [compile, List.append_assoc], fits_append, fits_append, fits_append] at hfits
      obtain ⟨hf₁, hf₂, hf₃, hf₄⟩ := hfits
      obtain ⟨s₁, h₁, e₁0⟩ :=
        compileExpr_correct hfit i 0 kk s (by omega) hoki hi hrep (hf₁.congr hpc.symm)
      obtain ⟨s₂, h₂, e₂0⟩ := reaches_idxCode hfit ha htemps e₁0 hkkB
        (by rw [h₁.pc, hpc]; simpa using hf₂)
      obtain ⟨s₃, h₃, e₃1⟩ := compileExpr_correct hfit e 1 v s₂ (by omega) hoke hev
        ((hrep.reaches h₁).reaches h₂)
        (by rw [h₂.pc, h₁.pc, hpc]; simpa [Nat.add_assoc] using hf₃)
      have e₃0 : s₃.mem 0 = L.arrAddr arr kk := by
        rw [h₃.frame 0 (Or.inl (by omega))]; exact e₂0
      have hf₄' : p[s₃.pc]? = some (Instr.store 0 1) := by
        rw [h₃.pc, h₂.pc, h₁.pc, hpc]
        exact fits_singleton.mp (by simpa [Nat.add_assoc] using hf₄)
      obtain ⟨t₁, ht₁, hr₁⟩ := ((h₁.trans h₂ (le_refl 0)).trans h₃ (by omega)).steps
      refine ⟨t₁ + 1, _, ?_,
        run_trans hr₁ (by rw [run_one hf₄', effect_store hzw h1w]), ?_, ?_⟩
      · simp only [Nat.mul_add, Nat.mul_one]
        have := esize_le L i
        have := esize_le L e
        have := idxLen_le_const L
        omega
      · show s₃.pc + 1 = a + size L (.store arr i e)
        rw [h₃.pc, h₂.pc, h₁.pc, hpc]; simp [size]; omega
      · have hlen : ((σ.arrs arr).set kk v).length = (σ.arrs arr).length := by simp
        refine ⟨fun y hy => ?_, fun b hb j hj => ?_, ?_, ?_⟩
        · show setCell w s₃.mem (s₃.mem 0) (s₃.mem 1) (L.varAddr y) = _
          rw [e₃0, e₃1, setCell_of_ne _ _ haddr (fun hc => varAddr_ne_arrAddr L hy kk hc),
            h₃.frame _ (Or.inr (temps_le_varAddr L y)),
            h₂.frame _ (Or.inr (temps_le_varAddr L y)),
            h₁.frame _ (Or.inr (temps_le_varAddr L y))]
          exact hrep.vars y hy
        · show setCell w s₃.mem (s₃.mem 0) (s₃.mem 1) (L.arrAddr b j) = _
          have hjlen : j < (σ.arrs b).length := by
            by_cases hb' : b = arr
            · subst hb'; simpa [Env.setArr] using hj
            · simpa [Env.setArr, hb'] using hj
          rw [e₃0, e₃1]
          by_cases hcase : b = arr ∧ j = kk
          · obtain ⟨rfl, rfl⟩ := hcase
            rw [setCell_self _ haddr hvw]
            simp [Env.setArr, List.getD_eq_getElem?_getD, hk]
          · have hne : L.arrAddr b j ≠ L.arrAddr arr kk := fun hc => by
              obtain ⟨rfl, rfl⟩ := arrAddr_inj L hb ha hc
              exact hcase ⟨rfl, rfl⟩
            rw [setCell_of_ne _ _ haddr hne,
              h₃.frame _ (Or.inr (temps_le_arrAddr L b j)),
              h₂.frame _ (Or.inr (temps_le_arrAddr L b j)),
              h₁.frame _ (Or.inr (temps_le_arrAddr L b j)), hrep.arrs b hb j hjlen]
            by_cases hb' : b = arr
            · subst hb'
              have hjk : j ≠ kk := fun hc => hcase ⟨rfl, hc⟩
              simp [Env.setArr, List.getD_eq_getElem?_getD, Ne.symm hjk]
            · simp [Env.setArr, hb']
        · show s₃.inp = _
          rw [h₃.inp, h₂.inp, h₁.inp]; exact hrep.inp
        · show s₃.out = _
          rw [h₃.out, h₂.out, h₁.out]; exact hrep.out
  | @ite_true b c d σ σ' k hb _ ih =>
      intro hok hinp a s hpc hrep hfits
      obtain ⟨hokb, hokc, hokd⟩ := hok
      rw [show compile L (.ite b c d) a
            = compileCond L b 0 ++ ([Instr.jzero 0 (a + bsize L b + 1 + size L d + 1)] ++
                (compile L d (a + bsize L b + 1) ++
                  ([Instr.jump (a + bsize L b + 1 + size L d + 1 + size L c)] ++
                    compile L c (a + bsize L b + 1 + size L d + 1)))) from by
          simp [compile, List.append_assoc],
        fits_append, fits_append, fits_append, fits_append] at hfits
      obtain ⟨hf₁, hf₂, hf₃, hf₄, hf₅⟩ := hfits
      obtain ⟨s₁, v, h₁, e₁0, hv⟩ :=
        compileCond_correct hfit (by omega) hokb hb hrep (hf₁.congr hpc.symm)
      obtain ⟨t₁, ht₁, hr₁⟩ := h₁.steps
      have hzero : s₁.mem 0 = 0 := by rw [e₁0]; exact hv.mpr rfl
      have hf₂' : p[s₁.pc]? = some (Instr.jzero 0 (a + bsize L b + 1 + size L d + 1)) := by
        rw [h₁.pc, hpc]; exact fits_singleton.mp (by simpa using hf₂)
      have hjz : run w p 1 s₁ = some { s₁ with pc := a + bsize L b + 1 + size L d + 1 } := by
        rw [run_jzero hzw hf₂', hzero]; simp
      obtain ⟨t₂, s₂, ht₂, hr₂, hpc₂, hrep₂⟩ :=
        ih hokc hinp (a + bsize L b + 1 + size L d + 1)
          { s₁ with pc := a + bsize L b + 1 + size L d + 1 } rfl ((hrep.reaches h₁).setPc _)
          (by simpa [Nat.add_assoc] using hf₅)
      refine ⟨t₁ + 1 + t₂, s₂, ?_, run_trans (run_trans hr₁ hjz) hr₂, ?_, hrep₂⟩
      · simp only [Nat.mul_add, Nat.mul_one]
        have := bsize_le L b
        have := one_le_const L
        omega
      · rw [hpc₂]; simp [size]; omega
  | @ite_false b c d σ σ' k hb _ ih =>
      intro hok hinp a s hpc hrep hfits
      obtain ⟨hokb, hokc, hokd⟩ := hok
      rw [show compile L (.ite b c d) a
            = compileCond L b 0 ++ ([Instr.jzero 0 (a + bsize L b + 1 + size L d + 1)] ++
                (compile L d (a + bsize L b + 1) ++
                  ([Instr.jump (a + bsize L b + 1 + size L d + 1 + size L c)] ++
                    compile L c (a + bsize L b + 1 + size L d + 1)))) from by
          simp [compile, List.append_assoc],
        fits_append, fits_append, fits_append, fits_append] at hfits
      obtain ⟨hf₁, hf₂, hf₃, hf₄, hf₅⟩ := hfits
      obtain ⟨s₁, v, h₁, e₁0, hv⟩ :=
        compileCond_correct hfit (by omega) hokb hb hrep (hf₁.congr hpc.symm)
      obtain ⟨t₁, ht₁, hr₁⟩ := h₁.steps
      have hne : s₁.mem 0 ≠ 0 := by
        rw [e₁0]; intro hc; exact absurd (hv.mp hc) (by simp)
      have hf₂' : p[s₁.pc]? = some (Instr.jzero 0 (a + bsize L b + 1 + size L d + 1)) := by
        rw [h₁.pc, hpc]; exact fits_singleton.mp (by simpa using hf₂)
      have hjz : run w p 1 s₁ = some { s₁ with pc := a + bsize L b + 1 } := by
        rw [run_jzero hzw hf₂']
        have : s₁.pc + 1 = a + bsize L b + 1 := by rw [h₁.pc, hpc]
        simp [hne, this]
      obtain ⟨t₂, s₂, ht₂, hr₂, hpc₂, hrep₂⟩ :=
        ih hokd hinp (a + bsize L b + 1) { s₁ with pc := a + bsize L b + 1 } rfl
          ((hrep.reaches h₁).setPc _) (by simpa [Nat.add_assoc] using hf₃)
      have hf₄' : p[s₂.pc]? =
          some (Instr.jump (a + bsize L b + 1 + size L d + 1 + size L c)) := by
        rw [hpc₂]; exact fits_singleton.mp (by simpa [Nat.add_assoc] using hf₄)
      refine ⟨t₁ + 1 + t₂ + 1, _, ?_,
        run_trans (run_trans (run_trans hr₁ hjz) hr₂) (run_jump hf₄'), ?_, ?_⟩
      · simp only [Nat.mul_add, Nat.mul_one]
        have := bsize_le L b
        have := two_le_const L
        omega
      · show a + bsize L b + 1 + size L d + 1 + size L c = a + size L (.ite b c d)
        simp [size]; omega
      · exact hrep₂.setPc _
  | @while_true b c σ σ₁ σ₂ k k' hb hbody _ ih ih' =>
      intro hok hinp a s hpc hrep hfits
      obtain ⟨hokb, hokc⟩ := hok
      have hcode : compile L (.while b c) a
          = compileCond L b 0 ++ ([Instr.jzero 0 (a + bsize L b + 2)] ++
              ([Instr.jump (a + bsize L b + 2 + size L c + 1)] ++
                (compile L c (a + bsize L b + 2) ++ [Instr.jump a]))) := by
        simp [compile, List.append_assoc]
      rw [hcode, fits_append, fits_append, fits_append, fits_append] at hfits
      obtain ⟨hf₁, hf₂, hf₃, hf₄, hf₅⟩ := hfits
      obtain ⟨s₁, v, h₁, e₁0, hv⟩ :=
        compileCond_correct hfit (by omega) hokb hb hrep (hf₁.congr hpc.symm)
      obtain ⟨t₁, ht₁, hr₁⟩ := h₁.steps
      have hzero : s₁.mem 0 = 0 := by rw [e₁0]; exact hv.mpr rfl
      have hf₂' : p[s₁.pc]? = some (Instr.jzero 0 (a + bsize L b + 2)) := by
        rw [h₁.pc, hpc]; exact fits_singleton.mp (by simpa using hf₂)
      have hjz : run w p 1 s₁ = some { s₁ with pc := a + bsize L b + 2 } := by
        rw [run_jzero hzw hf₂', hzero]; simp
      obtain ⟨t₂, s₂, ht₂, hr₂, hpc₂, hrep₂⟩ :=
        ih hokc hinp (a + bsize L b + 2) { s₁ with pc := a + bsize L b + 2 } rfl
          ((hrep.reaches h₁).setPc _) (by simpa [Nat.add_assoc] using hf₄)
      have hf₅' : p[s₂.pc]? = some (Instr.jump a) := by
        rw [hpc₂]; exact fits_singleton.mp (by simpa [Nat.add_assoc] using hf₅)
      obtain ⟨t₃, s₃, ht₃, hr₃, hpc₃, hrep₃⟩ :=
        ih' (⟨hokb, hokc⟩ : Com.Ok L (.while b c)) (hbody.inpBounded hinp) a
          { s₂ with pc := a } rfl (hrep₂.setPc _) (by rw [hcode]; exact
          (fits_append.mpr ⟨hf₁, fits_append.mpr ⟨hf₂, fits_append.mpr ⟨hf₃,
            fits_append.mpr ⟨hf₄, hf₅⟩⟩⟩⟩))
      refine ⟨t₁ + 1 + t₂ + 1 + t₃, s₃, ?_,
        run_trans (run_trans (run_trans (run_trans hr₁ hjz) hr₂)
          (run_jump hf₅')) hr₃, hpc₃, hrep₃⟩
      simp only [Nat.mul_add, Nat.mul_one]
      have := bsize_le L b
      have := two_le_const L
      omega
  | @while_false b c σ hb =>
      intro hok _ a s hpc hrep hfits
      obtain ⟨hokb, hokc⟩ := hok
      rw [show compile L (.while b c) a
            = compileCond L b 0 ++ ([Instr.jzero 0 (a + bsize L b + 2)] ++
                ([Instr.jump (a + bsize L b + 2 + size L c + 1)] ++
                  (compile L c (a + bsize L b + 2) ++ [Instr.jump a]))) from by
          simp [compile, List.append_assoc],
        fits_append, fits_append, fits_append, fits_append] at hfits
      obtain ⟨hf₁, hf₂, hf₃, hf₄, hf₅⟩ := hfits
      obtain ⟨s₁, v, h₁, e₁0, hv⟩ :=
        compileCond_correct hfit (by omega) hokb hb hrep (hf₁.congr hpc.symm)
      obtain ⟨t₁, ht₁, hr₁⟩ := h₁.steps
      have hne : s₁.mem 0 ≠ 0 := by
        rw [e₁0]; intro hc; exact absurd (hv.mp hc) (by simp)
      have hf₂' : p[s₁.pc]? = some (Instr.jzero 0 (a + bsize L b + 2)) := by
        rw [h₁.pc, hpc]; exact fits_singleton.mp (by simpa using hf₂)
      have hf₃' : p[s₁.pc + 1]? = some (Instr.jump (a + bsize L b + 2 + size L c + 1)) := by
        rw [h₁.pc, hpc]; exact fits_singleton.mp (by simpa [Nat.add_assoc] using hf₃)
      have hjz : run w p 1 s₁ = some { s₁ with pc := s₁.pc + 1 } := by
        rw [run_jzero hzw hf₂']; simp [hne]
      have hf₃'' : p[({ s₁ with pc := s₁.pc + 1 } : State).pc]? =
          some (Instr.jump (a + bsize L b + 2 + size L c + 1)) := hf₃'
      refine ⟨t₁ + 1 + 1, _, ?_,
        run_trans (run_trans hr₁ hjz) (run_jump hf₃''), ?_, ?_⟩
      · simp only [Nat.mul_add, Nat.mul_one]
        have := bsize_le L b
        have := two_le_const L
        omega
      · show a + bsize L b + 2 + size L c + 1 = a + size L (.while b c)
        simp [size]; omega
      · exact (hrep.reaches h₁).setPc _

/-! ### From an IMP+ derivation to a machine run

The two ends are joined here: the all-zero memory of a starting machine
represents the initial environment for *any* declared array lengths,
and the halt instruction after the code is what stops the machine. -/

/-- The starting machine state represents the starting environment, no
matter what lengths its arrays are declared with: zeroed memory holds a
zero-filled array of every length at once. -/
theorem represents_initState (L : Layout) (ext : String → ℕ) (x : List ℕ) :
    Represents L (initEnv ext x) (initState x) where
  vars _ _ := rfl
  arrs a _ i _ := by
    show (0 : ℕ) = (List.replicate (ext a) 0).getD i 0
    rw [List.getD_eq_getElem?_getD]
    rcases h : (List.replicate (ext a) 0)[i]? with _ | u
    · rfl
    · have := List.mem_of_getElem? h
      simp only [List.mem_replicate] at this
      rw [this.2]; rfl
  inp := rfl
  out := rfl

/-- **The simulation theorem.** Let an IMP+ program `c` run on input
`x` to a final environment at cost `k`, with every value it produces
below `B`, and let `w` be a word length at which the layout and the
bound fit — `B ≤ 2 ^ w` and `L.span B ≤ 2 ^ w`. Then the compiled
machine program, at word length `w`, runs on the same input, halts with
the same output, and executes at most `L.const * k` instructions. The
constant depends on the layout alone: not on the program, not on the
input, and not on the word length. The array lengths `ext` are the
user's free choice and cost nothing. -/
theorem compileProgram_runsTo {L : Layout} {B w : ℕ} {c : Com} {ext : String → ℕ}
    {x : List ℕ} {σ' : Env} {k : ℕ} (hfit : L.FitsWords B w) (hok : Com.Ok L c)
    (hx : ∀ v ∈ x, v < B) (hbs : BigStepB B c (initEnv ext x) σ' k) :
    ∃ t ≤ L.const * k, RunsTo w (compileProgram L c) x σ'.out t := by
  obtain ⟨t, s', ht, hr, hpc, hrep⟩ :=
    compile_correct hfit hbs hok (initEnv_inpBounded ext hx) 0 (initState x) rfl
      (represents_initState L ext x) (fits_self _ _)
  refine ⟨t, ht, s', hr, ?_, by rw [← hrep.out]⟩
  have hhalt : (compileProgram L c)[s'.pc]? = some Instr.halt := by
    rw [hpc, compileProgram]
    rw [List.getElem?_append_right (by simp)]
    simp
  rw [step_eq, hhalt]
  rfl

/-! ### A sanity check

The interface is exercised once, on the smallest program that writes
anything, so that the hypotheses of the simulation theorem are known to
be dischargeable and its conclusion is known to be a statement about
the machine of the concept. Programs are the business of the layers
above this one. -/

example :
    ∃ t ≤ 20, RunsTo 3 (compileProgram ⟨[], [], 1⟩ (.write (.lit 5))) [] [5] t := by
  have hfit : (⟨[], [], 1⟩ : Layout).FitsWords 8 3 :=
    ⟨by norm_num, by norm_num, by simp [Layout.span]⟩
  have hbs : BigStepB 8 (.write (.lit 5)) (initEnv (fun _ => 0) [])
      { initEnv (fun _ => 0) [] with out := (initEnv (fun _ => 0) []).out ++ [5] }
      (1 + (Expr.lit 5).size) := .write (fit_self (by norm_num))
  have hok : Com.Ok (⟨[], [], 1⟩ : Layout) (.write (.lit 5)) := ⟨trivial, by norm_num⟩
  obtain ⟨t, ht, hrun⟩ := compileProgram_runsTo hfit hok (by simp) hbs
  exact ⟨t, le_trans ht (by norm_num [Layout.const, Expr.size]),
    by simpa [initEnv] using hrun⟩

end Lax13Proofs.Simulation
