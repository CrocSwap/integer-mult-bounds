import PortData

/-! Reverse orthogonality extracted from the checked exact source table.
Apache-2.0. Prepared with substantial OpenAI Codex assistance. -/
namespace PortGeometry

def doubledRowDot (port : Fin 120) (i j : Fin 8) : Int := rowDot (doubledBasis port) i j

theorem doubled_row_orthogonal_entries (port : Fin 120) (i j : Fin 8) :
    doubledRowDot port i j = if i = j then 4 else 0 :=
  (portData port).row_correct i j

end PortGeometry
#print axioms PortGeometry.doubled_row_orthogonal_entries
