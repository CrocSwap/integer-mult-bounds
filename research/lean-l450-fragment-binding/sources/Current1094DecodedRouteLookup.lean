import Current1094AllRouteTables

/-!
UNCOMPILED lookup bridge for the accepted selected PR1094 route tables.
The complete decoded OwnerRow, including every route field, is retrieved at
its original register index. A supplied interpretation function may then
rewrite through the exact route equality; no chart interpretation is invented.

The concrete call000 L450 entry is borrowed index226, family10216, with
route [4,2,0,7,[0,8]]. This is not borrowed index450 (ordinary L674).
The source-matched conditional kappa is
836330098538459/500000000000000000 = 0.001672660197076918.
The accepted all144 owner and parser certificates are reused without replay.
Actual Hosting, component addresses, private C allocation, chart/recipe laws,
physical execution, precision and the full multiplication theorem remain open.

Credits: Rohan Arun PR1094; Jeremy Kothe T16/hyperplane-ended emitter; Hao Yan
PR514/484/507; columbia-git PR1553; inherited bank/machine/frame interfaces;
Mario Carneiro/Mathlib list infrastructure. Apache-2.0; OpenAI assistance.
-/
set_option Elab.async false
namespace CurrentMain.Current1094DecodedRouteLookup
open Current1094OwnerDeclarationDecoder CertifiedSourceRouteTable
open Current1094SourceRoutes Current1094CallSequenceHelpersStructural

/-- Lookup in the returned decoded row list, with no default or wrapping. -/
def decodedRowAt {c : Fin 144} (m : MatchedOwners c) (i : Fin 704) : OwnerRow :=
  m.val[i.val]'(by
    have hlen : m.val.length = 704 := by
      have h := congrArg List.length m.property
      simpa only [List.length_map, List.length_ofFn] using h
    rw [hlen]
    exact i.isLt)

/-- Retrieve both fields from a generic successful table, symbolically. -/
theorem decodedRowAt_matchedTable (c : Fin 144) (rs : Fin 704 → CertifiedRoute)
    (i : Fin 704) :
    decodedRowAt (matchedTable c rs) i = ownerResult (selectedOrdinaryOwner c i) (rs i) := by
  simp only [decodedRowAt, matchedTable, tableRows, tablePairs,
    List.getElem_map, List.getElem_ofFn]

/-- The actual selected table preserves the complete family-and-route pair. -/
theorem selected_row_binding (c : Fin 144) (i : Fin 704) :
    decodedRowAt (selectedDecodedOwners c) i =
      ownerResult (selectedOrdinaryOwner c i) (routeAt (selectedCalls c) i) :=
  decodedRowAt_matchedTable c (routeAt (selectedCalls c)) i

/-- Route projection is distinct from the accepted family-only lookup API. -/
theorem selected_route_binding (c : Fin 144) (i : Fin 704) :
    (decodedRowAt (selectedDecodedOwners c) i).route =
      (routeAt (selectedCalls c) i).decoded :=
  congrArg OwnerRow.route (selected_row_binding c i)

/-- Two closed lookup reductions only; no owner-injectivity predicate is rerun. -/
private theorem call000_L450_owner : selectedOrdinaryOwner 0 450 = 10216 := by
  rfl

private theorem call000_L450_route :
    (routeAt (selectedCalls 0) 450).decoded = Route.narrow 2 0 7 [0, 8] := by
  rfl

/-- Full literal decoded row for the source-bound helper450 supplier. -/
theorem call000_L450_decoded :
    decodedRowAt (selectedDecodedOwners 0) 450 =
      (⟨10216, Route.narrow 2 0 7 [0, 8]⟩ : OwnerRow) :=
  (selected_row_binding 0 450).trans
    (congrArg₂ OwnerRow.mk call000_L450_owner call000_L450_route)

end CurrentMain.Current1094DecodedRouteLookup
#print axioms CurrentMain.Current1094DecodedRouteLookup.decodedRowAt_matchedTable
#print axioms CurrentMain.Current1094DecodedRouteLookup.selected_row_binding
#print axioms CurrentMain.Current1094DecodedRouteLookup.selected_route_binding
#print axioms CurrentMain.Current1094DecodedRouteLookup.call000_L450_decoded
