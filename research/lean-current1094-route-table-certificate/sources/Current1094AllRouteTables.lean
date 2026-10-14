import Current1094CallRoutesBlock000
import Current1094CallRoutesBlock001
import Current1094CallRoutesBlock002
import Current1094CallRoutesBlock003
import Current1094CallRoutesBlock004
import Current1094CallRoutesBlock005
import Current1094CallRoutesBlock006
import Current1094CallRoutesBlock007
import Current1094CallRoutesBlock008
import Current1094CallRoutesBlock009
import Current1094CallRoutesBlock010
import Current1094CallRoutesBlock011
import Current1094CallRoutesBlock012
import Current1094CallRoutesBlock013
import Current1094CallRoutesBlock014
import Current1094CallRoutesBlock015
import Current1094CallRoutesBlock016
import Current1094CallRoutesBlock017

/-! UNCOMPILED exact selected PR1094 source certificate. Preserve Rohan Arun,
Jeremy Kothe T16, Hao Yan, columbia-git PR1553 and inherited Lean/owner credits.
Apache-2.0; OpenAI assistance. Source context kappa=836330098538459/500000000000000000.
No physical chart/allocation claim or supplier execution. -/
namespace CurrentMain.Current1094SourceRoutes
open CertifiedSourceRouteTable Current1094OwnerDeclarationDecoder
open Current1094CallSequenceHelpersStructural
set_option Elab.async false

def selectedCalls : Fin 144 → CallRoutes :=
  (Fin.cases call000 (Fin.cases call001 (Fin.cases call002 (Fin.cases call003 (Fin.cases call004 (Fin.cases call005 (Fin.cases call006 (Fin.cases call007 (Fin.cases call008 (Fin.cases call009 (Fin.cases call010 (Fin.cases call011 (Fin.cases call012 (Fin.cases call013 (Fin.cases call014 (Fin.cases call015 (Fin.cases call016 (Fin.cases call017 (Fin.cases call018 (Fin.cases call019 (Fin.cases call020 (Fin.cases call021 (Fin.cases call022 (Fin.cases call023 (Fin.cases call024 (Fin.cases call025 (Fin.cases call026 (Fin.cases call027 (Fin.cases call028 (Fin.cases call029 (Fin.cases call030 (Fin.cases call031 (Fin.cases call032 (Fin.cases call033 (Fin.cases call034 (Fin.cases call035 (Fin.cases call036 (Fin.cases call037 (Fin.cases call038 (Fin.cases call039 (Fin.cases call040 (Fin.cases call041 (Fin.cases call042 (Fin.cases call043 (Fin.cases call044 (Fin.cases call045 (Fin.cases call046 (Fin.cases call047 (Fin.cases call048 (Fin.cases call049 (Fin.cases call050 (Fin.cases call051 (Fin.cases call052 (Fin.cases call053 (Fin.cases call054 (Fin.cases call055 (Fin.cases call056 (Fin.cases call057 (Fin.cases call058 (Fin.cases call059 (Fin.cases call060 (Fin.cases call061 (Fin.cases call062 (Fin.cases call063 (Fin.cases call064 (Fin.cases call065 (Fin.cases call066 (Fin.cases call067 (Fin.cases call068 (Fin.cases call069 (Fin.cases call070 (Fin.cases call071 (Fin.cases call072 (Fin.cases call073 (Fin.cases call074 (Fin.cases call075 (Fin.cases call076 (Fin.cases call077 (Fin.cases call078 (Fin.cases call079 (Fin.cases call080 (Fin.cases call081 (Fin.cases call082 (Fin.cases call083 (Fin.cases call084 (Fin.cases call085 (Fin.cases call086 (Fin.cases call087 (Fin.cases call088 (Fin.cases call089 (Fin.cases call090 (Fin.cases call091 (Fin.cases call092 (Fin.cases call093 (Fin.cases call094 (Fin.cases call095 (Fin.cases call096 (Fin.cases call097 (Fin.cases call098 (Fin.cases call099 (Fin.cases call100 (Fin.cases call101 (Fin.cases call102 (Fin.cases call103 (Fin.cases call104 (Fin.cases call105 (Fin.cases call106 (Fin.cases call107 (Fin.cases call108 (Fin.cases call109 (Fin.cases call110 (Fin.cases call111 (Fin.cases call112 (Fin.cases call113 (Fin.cases call114 (Fin.cases call115 (Fin.cases call116 (Fin.cases call117 (Fin.cases call118 (Fin.cases call119 (Fin.cases call120 (Fin.cases call121 (Fin.cases call122 (Fin.cases call123 (Fin.cases call124 (Fin.cases call125 (Fin.cases call126 (Fin.cases call127 (Fin.cases call128 (Fin.cases call129 (Fin.cases call130 (Fin.cases call131 (Fin.cases call132 (Fin.cases call133 (Fin.cases call134 (Fin.cases call135 (Fin.cases call136 (Fin.cases call137 (Fin.cases call138 (Fin.cases call139 (Fin.cases call140 (Fin.cases call141 (Fin.cases call142 (Fin.cases call143 (fun z => Fin.elim0 z)))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))

def selectedRawOwners (c : Fin 144) := rawTable c (routeAt (selectedCalls c))

def selectedDecodedOwners (c : Fin 144) := matchedTable c (routeAt (selectedCalls c))

theorem all_tables_decode (c : Fin 144) :
    owners c (selectedRawOwners c) = some (selectedDecodedOwners c) :=
  call_table_success c (selectedCalls c)

theorem decoded_owner_binding (c : Fin 144) (i : Fin 704) :
    ownerAt (selectedDecodedOwners c) i = selectedOrdinaryOwner c i :=
  ownerAt_eq (selectedDecodedOwners c) i

theorem decoded_owner_injection (c : Fin 144) :
    Function.Injective (ownerAt (selectedDecodedOwners c)) :=
  decoded_owner_injective (selectedDecodedOwners c)

end CurrentMain.Current1094SourceRoutes
#print axioms CurrentMain.Current1094SourceRoutes.all_tables_decode
#print axioms CurrentMain.Current1094SourceRoutes.decoded_owner_binding
#print axioms CurrentMain.Current1094SourceRoutes.decoded_owner_injection
