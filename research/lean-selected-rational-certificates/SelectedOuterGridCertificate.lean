import Batteries.Data.Rat.Basic

/-! Source-only candidate: exact finite final-grid arithmetic for the selected
f19 direct-ASSEMBLY certificate, SHA256
b352aad19ea2f23d70f9913e497b2588d7352d68816bf201cbc35bba2aa71698.
The scalar input below is the recorded bootstrap endpoint (bit_positive).
This file checks its q formula, reported compact-layer slack and final grid
bracket. It does not prove the six bootstrap updates, the paid-profile moment
enclosure, the 47 outer constraints, analytic/all-size transfer, the selected
caller, or a multiplier theorem. No upstream generator is executed here.

Explicit selected conditional context:
kappa = 1517760977820331 / 1000000000000000000
      = 0.001517760977820331.
Formulas are from pinned direct-delivery504-global/code/assemble.py:27,34 and
inputs/data-base/work/pr361/code/engines/outer.py:19-26. They retain upstream
PR361/PR144/PR23 and balanced-assembly attribution; see SOURCE_BINDING.json.
-/
namespace CurrentMain.SelectedOuterGridCertificate
set_option Elab.async false

/-- assemble.py:27 uses the same exact eta and grid. -/
def eta : Rat := (1 : Rat) / 1000000000000000000
def grid : Rat := (1 : Rat) / 1000000000000000000

/-- direct-ASSEMBLY.json /strict_outer_constraints/bit_positive. -/
def selectedBitSaving : Rat := (19456871396255954410965126483989729837567608538784265533445269687084094691447524630538808307685143000502626214026213530825584046670609183473632017543055080309889182544200522322566091835026048248817286022850198107276452392695799180840923992784947540394286030437607804209698866870065031311 : Rat) / 12800000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000

/-- direct-ASSEMBLY.json /strict_outer_constraints/q_positive. -/
def recordedQ : Rat := (9728435698127977186025691845738910507818677785402402929155026304757781812278492628185309462395046869712504799327963764910165809309091060911231962100918356681312573729045180851393863373312501801842551176399050804820940173497701483144009603696674589356219022433856361710563402997424711445801133129934968689 : Rat) / 6400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000

/-- direct-ASSEMBLY.json /strict_outer_constraints/compact_phase_layer_above_kappa. -/
def recordedCompactGap : Rat := (1460796919765288763514469054162733320617540517396562333085142025357987059397238422576833415925686473391798968212640481453257239804719916751781436134930531676549548853760032258218163179043574319444609476180221273672684823221548950012508401738297526350274506175659689036372441381877794553646958343284528103813 : Rat) / 1602432108924531994296506422961434727626954669446350600732288756576189445453069623157046327365598761717428126199831990941227541452327272765227807990525229589170328143432261295212848465843328125450460637794099762701205235043374425370786002400924168647339054755608464090427640850749356177861450283282483742172250000000000000000

/-- direct-ASSEMBLY.json /kappa. -/
def selectedKappa : Rat := (1517760977820331 : Rat) / 1000000000000000000

/-- Outer.assembly's q from the recorded finite bootstrap endpoint. -/
def selectedQ : Rat := selectedBitSaving * (1 - 2 * eta)

/-- The selected compact-phase margin, the minimum used by assemble.py:34. -/
def selectedMargin : Rat := (1 - eta) * selectedQ / (1 + selectedQ)

/-- The formula agrees with the certificate's separately serialized q. -/
theorem q_matches_certificate : selectedQ = recordedQ := by decide +kernel

/-- Recomputed final margin agrees with the recorded strict compact slack. -/
theorem compact_slack_matches_certificate :
    selectedMargin - selectedKappa = recordedCompactGap := by decide +kernel

/-- The selected tick is strictly below the margin; the next tick is not. -/
theorem selected_grid_bracket :
    selectedKappa < selectedMargin ∧ selectedMargin ≤ selectedKappa + grid := by decide +kernel

end CurrentMain.SelectedOuterGridCertificate
#print axioms CurrentMain.SelectedOuterGridCertificate.q_matches_certificate
#print axioms CurrentMain.SelectedOuterGridCertificate.compact_slack_matches_certificate
#print axioms CurrentMain.SelectedOuterGridCertificate.selected_grid_bracket
