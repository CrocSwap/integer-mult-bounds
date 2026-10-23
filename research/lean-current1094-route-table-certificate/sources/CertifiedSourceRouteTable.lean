import Current1094OwnerDeclarationDecoder

/-!
UNCOMPILED source-certificate interfaces for complete selected route tables.
A CertifiedRoute carries an actual strict decoder equation, never an assumed
success bit. Concrete route catalog entries must prove this equation. Ordered
runs retain every occurrence; their total count is checked separately. The
accepted selectedOrdinaryOwner supplies families without a new owner proof.

This file does not identify a supplied route table with JSON bytes. The concrete
generator and source binding must preserve every original call/register index.
The generic success theorem is useful only after those actual typed inputs are
constructed. No physical route/chart or C allocator interpretation is asserted.
Source context: kappa=836330098538459/500000000000000000.
Credits: Rohan Arun PR1094, Jeremy Kothe T16, Hao Yan PR514/484/507, columbia-git
PR1553, frame strict syntax and accepted owner interfaces; Lean List/Option.
Apache-2.0; prepared with OpenAI assistance.
-/
set_option Elab.async false
namespace CurrentMain.CertifiedSourceRouteTable
open SelectedSourceSyntax (Value bounded natValue)
open Current1094OwnerDeclarationDecoder
open Current1094CallSequenceHelpersStructural

structure CertifiedRoute where
  raw : Value
  decoded : Route
  parsed : route raw = some decoded

/-- Every bounded data route is decoded symbolically, once for all stages/ports. -/
def dataRoute (s : Fin 9) (p : Fin 112) : CertifiedRoute where
  raw := .array [.integer 1, .integer s.val, .integer p.val]
  decoded := .data s p
  parsed := by
    simp [route, bounded, natValue, s.isLt, p.isLt]

def ownerValue (f : Fin 14336) (r : CertifiedRoute) : Value :=
  .array [.integer f.val, r.raw]

def ownerResult (f : Fin 14336) (r : CertifiedRoute) : OwnerRow :=
  ⟨f, r.decoded⟩

theorem ownerValue_decode (f : Fin 14336) (r : CertifiedRoute) :
    ownerRow (ownerValue f r) = some (ownerResult f r) := by
  simp [ownerValue, ownerResult, ownerRow, bounded, natValue, f.isLt, r.parsed]

/-- List order and every occurrence survive the complete strict parser. -/
theorem mapM_owners (xs : List (Fin 14336 × CertifiedRoute)) :
    (xs.map (fun p => ownerValue p.1 p.2)).mapM ownerRow =
      some (xs.map (fun p => ownerResult p.1 p.2)) := by
  induction xs with
  | nil => rfl
  | cons x xs ih =>
      simp only [List.map_cons, List.mapM_cons, ownerValue_decode, ih]
      rfl

def tablePairs (c : Fin 144) (rs : Fin 704 → CertifiedRoute) :=
  List.ofFn (fun i => (selectedOrdinaryOwner c i, rs i))

def tableRows (c : Fin 144) (rs : Fin 704 → CertifiedRoute) :=
  (tablePairs c rs).map (fun p => ownerResult p.1 p.2)

theorem tableRows_families (c : Fin 144) (rs : Fin 704 → CertifiedRoute) :
    (tableRows c rs).map OwnerRow.family = List.ofFn (selectedOrdinaryOwner c) := by
  unfold tableRows tablePairs
  rw [List.map_map, List.map_ofFn]
  all_goals rfl

def matchedTable (c : Fin 144) (rs : Fin 704 → CertifiedRoute) : MatchedOwners c :=
  ⟨tableRows c rs, tableRows_families c rs⟩

def rawTable (c : Fin 144) (rs : Fin 704 → CertifiedRoute) : Value :=
  .array ((tablePairs c rs).map (fun p => ownerValue p.1 p.2))

theorem complete_table_success (c : Fin 144) (rs : Fin 704 → CertifiedRoute) :
    owners c (rawTable c rs) = some (matchedTable c rs) := by
  have success (xs : List (Fin 14336 × CertifiedRoute))
      (hfamily : (xs.map (fun p => ownerResult p.1 p.2)).map OwnerRow.family =
        List.ofFn (selectedOrdinaryOwner c)) :
      owners c (.array (xs.map (fun p => ownerValue p.1 p.2))) =
        some (⟨xs.map (fun p => ownerResult p.1 p.2), hfamily⟩ : MatchedOwners c) := by
    simp only [owners, mapM_owners]
    change (if h : (xs.map (fun p => ownerResult p.1 p.2)).map OwnerRow.family =
        List.ofFn (selectedOrdinaryOwner c) then
      some (⟨xs.map (fun p => ownerResult p.1 p.2), h⟩ : MatchedOwners c) else none) =
        some (⟨xs.map (fun p => ownerResult p.1 p.2), hfamily⟩ : MatchedOwners c)
    rw [dif_pos hfamily]
  exact success (tablePairs c rs) (tableRows_families c rs)

/-- Run lengths are independent of route proof terms. Zero runs are harmless. -/
def runCount : List (CertifiedRoute × Nat) → Nat
  | [] => 0
  | (_, n) :: rest => n + runCount rest

def expandRuns : List (CertifiedRoute × Nat) → List CertifiedRoute
  | [] => []
  | (r, n) :: rest => List.replicate n r ++ expandRuns rest

theorem expandRuns_length (xs : List (CertifiedRoute × Nat)) :
    (expandRuns xs).length = runCount xs := by
  induction xs with
  | nil => rfl
  | cons x xs ih =>
      simp only [expandRuns, runCount, List.length_append, List.length_replicate, ih]

structure CallRoutes where
  stage : Fin 9
  helpers : List CertifiedRoute
  helper_length : helpers.length = 480

/-- The actual first224 routes use local port modulo112; helpers retain order. -/
def routeAt (call : CallRoutes) (i : Fin 704) : CertifiedRoute :=
  if h : i.val < 224 then
    dataRoute call.stage ⟨i.val % 112, Nat.mod_lt _ (by omega)⟩
  else
    call.helpers[i.val - 224]'(by rw [call.helper_length]; have := i.isLt; omega)

theorem call_table_success (c : Fin 144) (call : CallRoutes) :
    owners c (rawTable c (routeAt call)) = some (matchedTable c (routeAt call)) :=
  complete_table_success c (routeAt call)

end CurrentMain.CertifiedSourceRouteTable
#print axioms CurrentMain.CertifiedSourceRouteTable.ownerValue_decode
#print axioms CurrentMain.CertifiedSourceRouteTable.mapM_owners
#print axioms CurrentMain.CertifiedSourceRouteTable.complete_table_success
#print axioms CurrentMain.CertifiedSourceRouteTable.expandRuns_length
#print axioms CurrentMain.CertifiedSourceRouteTable.call_table_success
