import FramedExponentMetadata

/-!
Finite keyed storage bridge for the accepted marked paired-bit XOR segment.
The executable structural locate returns the actual before/block/after split;
its result constructs a head positioned at that block. Accepted ambient framing
then changes only that block's target bits and preserves the remaining packed
symbols. A derived total semantic view refines Function.update at the located
Nat key, with an explicit ambient fallback for keys absent from the layout.

All supplied blocks, markers and payload cells are charged, not just the active
block. Keys are logical labels here: their bit encoding/storage, sequential key
comparison cost, head travel to the constructed focus, width choice, pairing,
allocation/initialization and source-track refresh are not supplied or free.
Other BoundaryState fields and compound arithmetic workspace stay separate.
James Chang with OpenAI assistance; Apache-2.0. Reuses accepted machine paired
XOR and metadata interpretation plus signed ambient framing without replay.
Pinned conditional context: kappa=836330098538459/500000000000000000.
Uncompiled candidate.
-/
set_option Elab.async false
set_option autoImplicit false
namespace CurrentMain.PackedMetadataSlots
open PairedBitXorScan (Pair value xorPair)
open MarkedBitXorScan

structure Block where
  key : Nat
  rows : List Pair

structure Focus where
  before : List Block
  selected : Block
  after : List Block

/-- An executable sequential search, not unit-cost random access. -/
def locate (key : Nat) : List Block → Option Focus
  | [] => none
  | block :: rest =>
      if block.key = key then some ⟨[], block, rest⟩
      else (locate key rest).map (fun f => ⟨block :: f.before, f.selected, f.after⟩)

def Unique : List Block → Prop
  | [] => True
  | block :: rest => (∀ b, b ∈ rest → b.key ≠ block.key) ∧ Unique rest

def pack : List Block → List Symbol
  | [] => []
  | block :: rest => marked block.rows ++ pack rest

def capacity : List Block → Nat
  | [] => 0
  | block :: rest => block.rows.length + 2 + capacity rest

def keys (blocks : List Block) : List Nat := blocks.map Block.key

def targetValue (b : Block) : Nat := value (b.rows.map Prod.fst)
def sourceValue (b : Block) : Nat := value (b.rows.map Prod.snd)

/-- Total semantic observation of a supplied finite store. The ambient function
is retained off-layout; this definition does not implement a memory lookup. -/
def metadata (ambient : Nat → Nat) : List Block → Nat → Nat
  | [] => ambient
  | block :: rest => Function.update (metadata ambient rest) block.key (targetValue block)

def toggleBlock (b : Block) : Block := ⟨b.key, b.rows.map xorPair⟩
def replaced (f : Focus) : List Block := f.before ++ toggleBlock f.selected :: f.after

def toggleAt (key : Nat) (blocks : List Block) : Option (List Block) :=
  (locate key blocks).map replaced

/-- Exact successful search decomposition and absence of earlier matches. -/
theorem locate_spec (key : Nat) (blocks : List Block) : ∀ f,
    locate key blocks = some f →
      blocks = f.before ++ f.selected :: f.after ∧ f.selected.key = key ∧
      (∀ b, b ∈ f.before → b.key ≠ key) := by
  induction blocks with
  | nil => intro f h; simp [locate] at h
  | cons block rest ih =>
      intro f h
      by_cases hk : block.key = key
      · simp only [locate, hk, ↓reduceIte, Option.some.injEq] at h
        cases h
        exact ⟨rfl, hk, by intro b hb; cases hb⟩
      · simp only [locate, hk, ↓reduceIte] at h
        cases he : locate key rest with
        | none => simp [he] at h
        | some tail =>
            rcases tail with ⟨pre, selected, post⟩
            simp only [he, Option.map_some, Option.some.injEq] at h
            cases h
            obtain ⟨hr, hs, hp⟩ := ih ⟨pre, selected, post⟩ he
            refine ⟨by simpa only [List.cons_append] using congrArg (block :: ·) hr, hs, ?_⟩
            intro b hb
            rcases List.mem_cons.mp hb with h | h
            · subst b; exact hk
            · exact hp b h

theorem locate_none (key : Nat) (blocks : List Block) :
    locate key blocks = none ↔ ∀ b, b ∈ blocks → b.key ≠ key := by
  induction blocks with
  | nil => simp [locate]
  | cons block rest ih =>
      by_cases hk : block.key = key
      · simp [locate, hk]
      · simp only [locate, hk, ↓reduceIte, Option.map_eq_none_iff, ih, List.mem_cons]
        constructor
        · intro h b hb
          rcases hb with rfl | hb
          · exact hk
          · exact h b hb
        · intro h b hb
          exact h b (Or.inr hb)

private theorem unique_middle (pre post : List Block) (selected : Block)
    (h : Unique (pre ++ selected :: post)) :
    ∀ b, b ∈ pre ++ post → b.key ≠ selected.key := by
  induction pre with
  | nil => exact h.1
  | cons block pre ih =>
      have hne : block.key ≠ selected.key :=
        Ne.symm (h.1 selected (by simp))
      have ht := ih h.2
      intro b hb
      rcases List.mem_cons.mp hb with rfl | hb
      · exact hne
      · exact ht b hb

/-- Unique-key input ensures the selected key occurs in no spectator block. -/
theorem locate_unique (key : Nat) (blocks : List Block) (f : Focus)
    (hu : Unique blocks) (h : locate key blocks = some f) :
    ∀ b, b ∈ f.before ++ f.after → b.key ≠ key := by
  obtain ⟨he, hk, _⟩ := locate_spec key blocks f h
  rw [he] at hu
  simpa only [hk] using unique_middle f.before f.after f.selected hu

private theorem pack_append (xs ys : List Block) : pack (xs ++ ys) = pack xs ++ pack ys := by
  induction xs with
  | nil => rfl
  | cons block rest ih => simp only [List.cons_append, pack, ih, List.append_assoc]

/-- Entire supplied tape capacity, including a marker pair for every block. -/
theorem pack_capacity (blocks : List Block) : (pack blocks).length = capacity blocks := by
  induction blocks with
  | nil => rfl
  | cons block rest ih => simp [pack, capacity, marked, ih, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm] <;> omega

theorem uniform_capacity (blocks : List Block) (width : Nat)
    (h : ∀ b, b ∈ blocks → b.rows.length = width) :
    capacity blocks = blocks.length * (width + 2) := by
  induction blocks with
  | nil => simp [capacity]
  | cons block rest ih =>
      have hb := h block (by simp)
      have ht := ih (fun b hb => h b (by simp [hb]))
      simp only [capacity, List.length_cons, hb, ht, Nat.succ_mul]
      omega

/-- Focus construction uses the real located prefix in stored reverse order.
Moving a physical head from a different position to this focus is unpriced. -/
def focusState (f : Focus) : State :=
  MarkedXorFraming.embed (pack f.before).reverse (pack f.after) (initial f.selected.rows)

def tapeWord (s : State) : List Symbol := s.tape.left.reverse ++ s.tape.right

/-- The constructed entrance contains exactly all supplied blocks in order. -/
theorem focus_pack (key : Nat) (blocks : List Block) (f : Focus)
    (h : locate key blocks = some f) : tapeWord (focusState f) = pack blocks := by
  obtain ⟨he, _, _⟩ := locate_spec key blocks f h
  rw [he, pack_append]
  simp only [tapeWord, focusState, MarkedXorFraming.embed, initial, pack,
    List.nil_append, List.reverse_reverse, List.append_assoc]

/-- Actual framed execution changes only the focused payload; both complete
spectator lists remain byte-for-symbol identical, with the returned marker head. -/
theorem run_focused (f : Focus) :
    run (5 * f.selected.rows.length + 4) (focusState f) =
      ⟨⟨(pack f.before).reverse,
        marked (f.selected.rows.map xorPair) ++ pack f.after⟩, false, .halt⟩ := by
  exact MarkedXorFraming.framed_scan_result (pack f.before).reverse (pack f.after) f.selected.rows

theorem run_repacked (f : Focus) :
    tapeWord (run (5 * f.selected.rows.length + 4) (focusState f)) = pack (replaced f) := by
  rw [run_focused]
  simp only [tapeWord, replaced, pack_append, pack, toggleBlock, List.reverse_reverse, List.append_assoc]

/-- Every prefix charges the whole packed store, not merely the active block. -/
theorem located_storage (key : Nat) (blocks : List Block) (f : Focus)
    (h : locate key blocks = some f) (k : Nat) :
    cells (run k (focusState f)) = capacity blocks := by
  have hs := MarkedXorFraming.framed_scan_storage (pack f.before).reverse (pack f.after) f.selected.rows k
  change cells (run k (focusState f)) = _ at hs
  rw [List.length_reverse] at hs
  rw [hs, ← pack_capacity]
  obtain ⟨he, _, _⟩ := locate_spec key blocks f h
  rw [he, pack_append]
  simp [pack, marked, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm] <;> omega

/-- Absent keys retain the supplied ambient metadata, including dirty values. -/
theorem metadata_avoids (ambient : Nat → Nat) (blocks : List Block) (key : Nat)
    (h : ∀ b, b ∈ blocks → b.key ≠ key) : metadata ambient blocks key = ambient key := by
  induction blocks with
  | nil => rfl
  | cons block rest ih =>
      have hb : key ≠ block.key := Ne.symm (h block (by simp))
      rw [metadata, Function.update_of_ne hb]
      exact ih (fun b hb => h b (by simp [hb]))

private theorem metadata_skip (ambient : Nat → Nat) (pre rest : List Block) (key : Nat)
    (h : ∀ b, b ∈ pre → b.key ≠ key) :
    metadata ambient (pre ++ rest) key = metadata ambient rest key := by
  induction pre with
  | nil => rfl
  | cons block pre ih =>
      rw [List.cons_append, metadata, Function.update_of_ne (Ne.symm (h block (by simp)))]
      exact ih (fun b hb => h b (by simp [hb]))

private theorem metadata_replace (ambient : Nat → Nat) (pre post : List Block)
    (selected : Block) (rows : List Pair)
    (h : ∀ b, b ∈ pre → b.key ≠ selected.key) :
    metadata ambient (pre ++ { selected with rows := rows } :: post) =
      Function.update (metadata ambient (pre ++ selected :: post)) selected.key (value (rows.map Prod.fst)) := by
  induction pre with
  | nil => simp only [List.nil_append, metadata, targetValue, Function.update_idem]
  | cons block pre ih =>
      have hb := h block (by simp)
      have ht := ih (fun b hb => h b (by simp [hb]))
      simp only [List.cons_append, metadata]
      rw [ht]
      exact Function.update_comm (Ne.symm hb) _ _ _

/-- Executable replacement and exact decoded Nat update. The original target
value is derived from search, and the increment is the retained source track. -/
theorem located_toggle (ambient : Nat → Nat) (key : Nat) (blocks : List Block) (f : Focus)
    (h : locate key blocks = some f) :
    toggleAt key blocks = some (replaced f) ∧
    keys (replaced f) = keys blocks ∧
    metadata ambient (replaced f) =
      Function.update (metadata ambient blocks) key
        (metadata ambient blocks key ^^^ sourceValue f.selected) := by
  obtain ⟨he, hk, hp⟩ := locate_spec key blocks f h
  have hv : metadata ambient blocks key = targetValue f.selected := by
    rw [he, metadata_skip ambient f.before (f.selected :: f.after) key hp, metadata, hk, Function.update_self]
  refine ⟨by simp only [toggleAt, h, Option.map_some], ?_, ?_⟩
  · rw [he]
    simp only [keys, replaced, List.map_append, List.map_cons, toggleBlock]
  · have hu := metadata_replace ambient f.before f.after f.selected (f.selected.rows.map xorPair)
      (by simpa only [hk] using hp)
    change metadata ambient (replaced f) = _ at hu
    rw [PairedBitXorScan.value_xor, ← he, hk] at hu
    change metadata ambient (replaced f) = Function.update (metadata ambient blocks) key
      (targetValue f.selected ^^^ sourceValue f.selected) at hu
    rw [← hv] at hu
    exact hu

/-- Numeric restored-exponent equality gives literal cleared target bits; no
canonical-width assumption or free clearing instruction is introduced. -/
theorem located_clear (ambient : Nat → Nat) (key : Nat) (blocks : List Block) (f : Focus)
    (h : locate key blocks = some f)
    (hequal : metadata ambient blocks key = sourceValue f.selected) :
    (toggleBlock f.selected).rows.map Prod.fst = List.replicate f.selected.rows.length false ∧
    metadata ambient (replaced f) = Function.update (metadata ambient blocks) key 0 := by
  obtain ⟨he, hk, hp⟩ := locate_spec key blocks f h
  have hv : metadata ambient blocks key = targetValue f.selected := by
    rw [he, metadata_skip ambient f.before (f.selected :: f.after) key hp, metadata, hk, Function.update_self]
  constructor
  · exact ExponentMetadataBitAdapter.xor_targets_clear f.selected.rows (hv.symm.trans hequal)
  · rw [(located_toggle ambient key blocks f h).2.2, hequal, Nat.xor_self]

end CurrentMain.PackedMetadataSlots
#print axioms CurrentMain.PackedMetadataSlots.locate_spec
#print axioms CurrentMain.PackedMetadataSlots.locate_none
#print axioms CurrentMain.PackedMetadataSlots.locate_unique
#print axioms CurrentMain.PackedMetadataSlots.pack_capacity
#print axioms CurrentMain.PackedMetadataSlots.uniform_capacity
#print axioms CurrentMain.PackedMetadataSlots.focus_pack
#print axioms CurrentMain.PackedMetadataSlots.run_focused
#print axioms CurrentMain.PackedMetadataSlots.run_repacked
#print axioms CurrentMain.PackedMetadataSlots.located_storage
#print axioms CurrentMain.PackedMetadataSlots.metadata_avoids
#print axioms CurrentMain.PackedMetadataSlots.located_toggle
#print axioms CurrentMain.PackedMetadataSlots.located_clear
#check @CurrentMain.PackedMetadataSlots.located_toggle
#check @CurrentMain.PackedMetadataSlots.located_storage
