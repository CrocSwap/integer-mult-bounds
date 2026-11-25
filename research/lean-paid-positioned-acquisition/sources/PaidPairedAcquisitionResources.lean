import PaidPairedTrackAcquisition

/-!
Copyright (c) 2026 James Chang. Apache-2.0. OpenAI-assisted.
Whole-prefix storage and original-entrance volume for the unchanged three-tape
acquisition controller. Actual access, both charged switches, framed copying,
and home return are all covered, including terminal stuttering. The two symbols
of every stored delimiter are counted. No new transition or execution premise.
The input volume includes the complete supplied store and unary control; the
new output is initially empty and its allocation is charged. This is a finite
marked multitape model bound, with physical input construction still explicit.
Author-checked context kappa=836330098538459/500000000000000000.
-/
set_option Elab.async false
set_option autoImplicit false
namespace CurrentMain.PaidPairedAcquisitionResources
open PairedBitXorScan (Tape)
open PackedMetadataSlots (Block pack capacity)
open SequentialBitAddition (Registers)
open PaidPairedTrackAcquisition

private theorem capacity_append (pre post : List Block) :
    capacity (pre++post)=capacity pre+capacity post := by
  induction pre with
  | nil => simp only [List.nil_append,capacity,Nat.zero_add]
  | cons b pre ih => simp [capacity,ih,Nat.add_assoc]
private theorem unary_cells (n : Nat) : tapeCells (PositionalMetadataAccess.unary n)=n+2 := by
  simp [tapeCells,PositionalMetadataAccess.unary,Nat.add_assoc,Nat.add_comm,Nat.add_left_comm]
private theorem output_cells (second : Bool) (selected : Block) :
    tapeCells (PairedTrackExtraction.final second selected.rows).output=selected.rows.length+2 := by
  simp [tapeCells,PairedTrackExtraction.final,MarkedZeroPadding.marked,MarkedZeroPadding.bits,
    Nat.add_assoc,Nat.add_comm,Nat.add_left_comm]

/-- The access phase preserves the whole store and supplied control exactly. -/
theorem access_prefix_cells (second : Bool) (pre : List Block) (selected : Block) (post : List Block)
    (scratch : Bool) (r : Registers) (k : Nat) (hk : k≤travel pre) :
    cells (run second k (initial pre.length (pre++selected::post) scratch r))=
      capacity (pre++selected::post)+(pre.length+2) := by
  rw [access_prefix second pre selected post scratch r k hk]
  change 0+PositionalMetadataAccess.cells (PositionalMetadataAccess.run k
    (PositionalMetadataAccess.initial pre.length (pre++selected::post) scratch))=_
  rw [Nat.zero_add,PositionalMetadataAccess.access_storage]

/-- This includes the post-entry state and the terminal copy state; both source
contexts and the separately carried positional control are counted. -/
theorem extraction_prefix_cells (second : Bool) (pre : List Block) (selected : Block) (post : List Block)
    (scratch : Bool) (r : Registers) (j : Nat) (hj : j≤copyTime selected) :
    cells (run second (travel pre+1+j) (initial pre.length (pre++selected::post) scratch r))≤
      capacity (pre++selected::post)+pre.length+selected.rows.length+4 := by
  rw [extraction_prefix second pre selected post scratch r j hj]
  change tapeCells (PositionalMetadataAccess.unary pre.length)+
    PairedTrackExtraction.cells (PairedTrackExtraction.run second j (focusedInitial pre selected post r))≤_
  rw [unary_cells]
  have h:=PairedTrackExtractionFraming.framed_storage second (pack pre).reverse (pack post) selected.rows r j
  change PairedTrackExtraction.cells (PairedTrackExtraction.run second j (focusedInitial pre selected post r))≤_ at h
  simp only [List.length_reverse,PackedMetadataSlots.pack_capacity] at h
  rw [capacity_append]
  simp only [capacity]
  omega

/-- Actual return and arbitrary later halt stuttering preserve full allocated
storage, including the completed output and the unary control. -/
theorem home_suffix_cells (second : Bool) (pre : List Block) (selected : Block) (post : List Block)
    (scratch : Bool) (r : Registers) (j : Nat) :
    cells (run second (travel pre+1+copyTime selected+1+j)
      (initial pre.length (pre++selected::post) scratch r))=
      capacity (pre++selected::post)+pre.length+selected.rows.length+4 := by
  rw [home_suffix]
  change tapeCells (PairedTrackExtraction.final second selected.rows).output+
    PositionalMetadataReturn.cells (PositionalMetadataReturn.run j
      (PositionalMetadataReturn.initial pre selected post scratch))=_
  rw [output_cells,PositionalMetadataReturn.return_storage]
  omega

/-- The split includes both charged handoffs; no prefix is omitted. -/
theorem machine_storage (second : Bool) (pre : List Block) (selected : Block) (post : List Block)
    (scratch : Bool) (r : Registers) (k : Nat) :
    cells (run second k (initial pre.length (pre++selected::post) scratch r))≤
      capacity (pre++selected::post)+pre.length+selected.rows.length+4 := by
  by_cases ha:k≤travel pre
  · rw [access_prefix_cells second pre selected post scratch r k ha]
    omega
  · by_cases he:k≤travel pre+1+copyTime selected
    · have hs:k=travel pre+1+(k-(travel pre+1)):=by omega
      rw [hs]
      exact extraction_prefix_cells second pre selected post scratch r _ (by omega)
    · have hs:k=travel pre+1+copyTime selected+1+(k-(travel pre+1+copyTime selected+1)):=by omega
      rw [hs,home_suffix_cells]

/-- Constant bounds in the complete original represented entrance volume.
The initially empty output is not silently preallocated. -/
theorem entrance_resources (second : Bool) (pre : List Block) (selected : Block) (post : List Block)
    (scratch : Bool) (r : Registers) :
    let s:=initial pre.length (pre++selected::post) scratch r
    totalTime pre selected≤7*cells s ∧
    run second (totalTime pre selected) s=final second pre selected post scratch ∧
    Halted (final second pre selected post scratch) ∧
    (∀ k<totalTime pre selected,¬Halted (run second k s)) ∧
    (∀ k,cells (run second k s)≤2*cells s) := by
  dsimp only
  have hi:=initial_cells pre.length (pre++selected::post) scratch r
  have hc:capacity (pre++selected::post)=capacity pre+selected.rows.length+2+capacity post := by
    rw [capacity_append]
    simp only [capacity]
    omega
  obtain ⟨hr,hh,hl⟩:=machine_result second pre selected post scratch r
  refine ⟨?_,hr,hh,hl,?_⟩
  · rw [time_eq,hi]
    omega
  · intro k
    have h:=machine_storage second pre selected post scratch r k
    rw [hi]
    omega

end CurrentMain.PaidPairedAcquisitionResources
#print axioms CurrentMain.PaidPairedAcquisitionResources.access_prefix_cells
#print axioms CurrentMain.PaidPairedAcquisitionResources.extraction_prefix_cells
#print axioms CurrentMain.PaidPairedAcquisitionResources.home_suffix_cells
#print axioms CurrentMain.PaidPairedAcquisitionResources.machine_storage
#print axioms CurrentMain.PaidPairedAcquisitionResources.entrance_resources
#check @CurrentMain.PaidPairedAcquisitionResources.entrance_resources
