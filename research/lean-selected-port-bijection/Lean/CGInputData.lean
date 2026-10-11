import GeometryDataBanks
import GeometryReadCoverage
import GeometryAuxiliary
import CGInputData000
import CGInputData001
import CGInputData002
import CGInputData003
import CGInputData004
import CGInputData005
namespace CurrentMain.ComplexGeometryData
open CurrentMain.ComplexGeometry CurrentMain.SignedTrace CurrentMain.GeometryDataBanks
def inputMaskBank : Table (Table Nat) := (.fork (.fork (.fork (.fork (.leaf CurrentMain.CGInputData000.table000) (.leaf CurrentMain.CGInputData004.table008)) (.fork (.leaf CurrentMain.CGInputData002.table004) (.leaf (.leaf 0)))) (.fork (.fork (.leaf CurrentMain.CGInputData001.table002) (.leaf CurrentMain.CGInputData005.table010)) (.fork (.leaf CurrentMain.CGInputData003.table006) (.leaf (.leaf 0))))) (.fork (.fork (.fork (.leaf CurrentMain.CGInputData000.table001) (.leaf CurrentMain.CGInputData004.table009)) (.fork (.leaf CurrentMain.CGInputData002.table005) (.leaf (.leaf 0)))) (.fork (.fork (.leaf CurrentMain.CGInputData001.table003) (.leaf (.leaf 0))) (.fork (.leaf CurrentMain.CGInputData003.table007) (.leaf (.leaf 0))))))
def inputMask (i : Nat) : Nat := bankLookup 7 inputMaskBank i
end CurrentMain.ComplexGeometryData
