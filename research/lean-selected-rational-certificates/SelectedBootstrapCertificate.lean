import SelectedOuterGridCertificate
import SelectedMomentUpperAggregate

/-! Exact finite bootstrap and cutoff arithmetic for the pinned f19
PR531 direct-ASSEMBLY certificate. This transcribes assemble.py:27-34.
The bit/complex input savings and charged coefficient are supplied certificate
values. Their operator, moment-enclosure and all-size validity are not proved
here. Each of the six finite updates, four-way gap minima and two-ceiling
cutoffs is checked separately; the endpoint is connected to the already
accepted outer-grid arithmetic. No upstream generator is executed.

Attribution: inherited PR361/PR144/PR23 arithmetic and the pinned balanced
assembly; see SOURCE_BINDING.json. Conditional selected context:
kappa = 1517760977820331 / 1000000000000000000
      = 0.001517760977820331.
No multiplier, complete outer-constraint or analytic-transfer theorem follows.
-/
namespace CurrentMain.SelectedBootstrapCertificate
open CurrentMain.SelectedOuterGridCertificate
open CurrentMain.SelectedMomentUpperAggregate
set_option Elab.async false

/-- Source min/max use exact comparisons, with no rounded intermediate. -/
def ratMin (x y : Rat) : Rat := if x ≤ y then x else y
def intMax (x y : Int) : Int := if x ≤ y then y else x

def bitLower : Rat := ((391360506745414227149 : Rat) / 250000000000000000000000)
def beta : Rat := (1 : Rat) / 1000000000000000000
def strictOffset : Rat := (1 : Rat) / 1000000000000000000000000
def selectedShrink : Rat := ratMin bitLower ((1-beta)*bMinus) - strictOffset
def recordedShrink : Rat := ((304013615566499291326786384433500708369 : Rat) / 200000000000000000000000000000000000000000)
/-- Exact supplied certificate field, not a proved runtime bound. -/
def chargedCoefficient : Nat := 6464

def bootstrapStep (s old : Rat) : Rat := (1-s)*s+s*old
/-- Left-associated source minimum of all four listed candidate gaps. -/
def sourceGap (s old next : Rat) : Rat :=
  ratMin (ratMin (ratMin (s-next) (1-next-s)) (1-next-s*(1-old))) (1-s)
def sourceCutoff (gap : Rat) : Int :=
  intMax (Rat.ceil (36/(gap*gap)))
    (Rat.ceil (2*(4+(chargedCoefficient : Rat))/gap))

/-- The complex branch is strictly smaller in this exact selected record. -/
theorem shrink_matches_literal : selectedShrink = recordedShrink := by decide +kernel

theorem supplied_input_domains :
    0 < bMinus ∧ 0 < bitLower ∧ (1-beta)*bMinus < bitLower ∧
    0 < selectedShrink ∧ selectedShrink < bitLower ∧
    selectedShrink < (1-beta)*bMinus := by
  rw [shrink_matches_literal]
  decide +kernel

def checkpoint0 : Rat := ((384599 : Rat) / 10000000000)
def checkpoint1 : Rat := ((60712637301500708246352866303830908726379266775820807753155389040451575213359839 : Rat) / 40000000000000000000000000000000000000000000000000000000000000000000000000000000000)
def checkpoint2 : Rat := ((12160517235346615350271707711040890766026096290190121311927508724817968154330756669685454535956417576328265548518995792591 : Rat) / 8000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000)
def checkpoint3 : Rat := ((2432108916205878176512000281868718703046894250036498652298357823907553990982935571525043721691631508175013197636609130194686326438841948984713149895884729101894079 : Rat) / 1600000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000)
def checkpoint4 : Rat := ((486421784903867613447222941688854339428658559255515806482369698934104792727814752644136183264829584006915356397001325620983271543572291792498587358616545186419181184730467505446760831291061088426106847151 : Rat) / 320000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000)
def checkpoint5 : Rat := ((97284356981279003689293810763984019832819692122363374070868885596757637619279723311848112009069154638458677864286324762010992537828947932529578352409324250859993139995125135621355882920050446940735273710727852886457356860369485457536839709506719 : Rat) / 64000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000)
def checkpoint6 : Rat := ((19456871396255954410965126483989729837567608538784265533445269687084094691447524630538808307685143000502626214026213530825584046670609183473632017543055080309889182544200522322566091835026048248817286022850198107276452392695799180840923992784947540394286030437607804209698866870065031311 : Rat) / 12800000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000)
def recordedGap1 : Rat := ((90085811799150019004410582869232947420733224179192246844610959548424786640161 : Rat) / 40000000000000000000000000000000000000000000000000000000000000000000000000000000000)
def recordedCutoff1 : Nat := 7097570097425
def recordedGap2 : Rat := ((27387313356302799747666299137568733903709809878688072491275182031845669243330314545464043582423671734451481004207409 : Rat) / 8000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000)
def recordedCutoff2 : Nat := 3071734057963094733
def recordedGap3 : Rat := ((8326116154102290793599286963905105749963501347701642176092446009017064428474956278308368491824986802363390869805313673561158051015286850104115270898105921 : Rat) / 1600000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000)
def recordedCutoff3 : Nat := 1329405697067353589697069
def recordedGap4 : Rat := ((2531252675635273404746793961741440744484193517630301065895207272185247355863816735170415993084643602998674379016728456427708207501412641383454813580818815269532494553239168708938911573893152849 : Rat) / 320000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000)
def recordedCutoff4 : Nat := 575349126599542919894057132845
def recordedGap5 : Rat := ((769535277832254736206845260307877636625929131114403242362380720276688151887990930845361541322135713675237989007462171052067470421647590675749140006860004874864378644117079949553059264726289272147113542643139630514542463160290493281 : Rat) / 64000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000)
def recordedCutoff5 : Nat := 249003459372181093823622006530189989
def recordedGap6 : Rat := ((233949202119754315498048391461215734466554730312915905308552475369461191692314856999497373785973786469174415953329390816526367982456944919690110817455799477677433908164973951751182713977149801892723547607304200819159076007215052459605713969562392195790301133129934968689 : Rat) / 12800000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000)
def recordedCutoff6 : Nat := 107765389591820574473400445708536466810850

/-- Full finite source obligation for one stage, including the exact cutoff
selection and both inequalities asserted by assemble.py:33. -/
def StageFacts (old next gap : Rat) (cutoff : Nat) : Prop :=
  bootstrapStep selectedShrink old = next ∧
  sourceGap selectedShrink old next = gap ∧
  sourceCutoff gap = (cutoff : Int) ∧
  old < next ∧ next < selectedShrink ∧ selectedShrink < 1-next ∧
  0 < gap ∧ 36 ≤ (cutoff : Rat)*gap*gap ∧
  2*(4+(chargedCoefficient : Rat)) ≤ (cutoff : Rat)*gap

theorem stage1_certificate :
    StageFacts checkpoint0 checkpoint1 recordedGap1 recordedCutoff1 := by
  unfold StageFacts
  rw [shrink_matches_literal]
  refine And.intro ?_ ?_
  · decide +kernel
  refine And.intro ?_ ?_
  · decide +kernel
  refine And.intro ?_ ?_
  · decide +kernel
  refine And.intro ?_ ?_
  · decide +kernel
  refine And.intro ?_ ?_
  · decide +kernel
  refine And.intro ?_ ?_
  · decide +kernel
  refine And.intro ?_ ?_
  · decide +kernel
  refine And.intro ?_ ?_
  · decide +kernel
  decide +kernel

theorem stage2_certificate :
    StageFacts checkpoint1 checkpoint2 recordedGap2 recordedCutoff2 := by
  unfold StageFacts
  rw [shrink_matches_literal]
  refine And.intro ?_ ?_
  · decide +kernel
  refine And.intro ?_ ?_
  · decide +kernel
  refine And.intro ?_ ?_
  · decide +kernel
  refine And.intro ?_ ?_
  · decide +kernel
  refine And.intro ?_ ?_
  · decide +kernel
  refine And.intro ?_ ?_
  · decide +kernel
  refine And.intro ?_ ?_
  · decide +kernel
  refine And.intro ?_ ?_
  · decide +kernel
  decide +kernel

theorem stage3_certificate :
    StageFacts checkpoint2 checkpoint3 recordedGap3 recordedCutoff3 := by
  unfold StageFacts
  rw [shrink_matches_literal]
  refine And.intro ?_ ?_
  · decide +kernel
  refine And.intro ?_ ?_
  · decide +kernel
  refine And.intro ?_ ?_
  · decide +kernel
  refine And.intro ?_ ?_
  · decide +kernel
  refine And.intro ?_ ?_
  · decide +kernel
  refine And.intro ?_ ?_
  · decide +kernel
  refine And.intro ?_ ?_
  · decide +kernel
  refine And.intro ?_ ?_
  · decide +kernel
  decide +kernel

theorem stage4_certificate :
    StageFacts checkpoint3 checkpoint4 recordedGap4 recordedCutoff4 := by
  unfold StageFacts
  rw [shrink_matches_literal]
  refine And.intro ?_ ?_
  · decide +kernel
  refine And.intro ?_ ?_
  · decide +kernel
  refine And.intro ?_ ?_
  · decide +kernel
  refine And.intro ?_ ?_
  · decide +kernel
  refine And.intro ?_ ?_
  · decide +kernel
  refine And.intro ?_ ?_
  · decide +kernel
  refine And.intro ?_ ?_
  · decide +kernel
  refine And.intro ?_ ?_
  · decide +kernel
  decide +kernel

theorem stage5_certificate :
    StageFacts checkpoint4 checkpoint5 recordedGap5 recordedCutoff5 := by
  unfold StageFacts
  rw [shrink_matches_literal]
  refine And.intro ?_ ?_
  · decide +kernel
  refine And.intro ?_ ?_
  · decide +kernel
  refine And.intro ?_ ?_
  · decide +kernel
  refine And.intro ?_ ?_
  · decide +kernel
  refine And.intro ?_ ?_
  · decide +kernel
  refine And.intro ?_ ?_
  · decide +kernel
  refine And.intro ?_ ?_
  · decide +kernel
  refine And.intro ?_ ?_
  · decide +kernel
  decide +kernel

theorem stage6_certificate :
    StageFacts checkpoint5 checkpoint6 recordedGap6 recordedCutoff6 := by
  unfold StageFacts
  rw [shrink_matches_literal]
  refine And.intro ?_ ?_
  · decide +kernel
  refine And.intro ?_ ?_
  · decide +kernel
  refine And.intro ?_ ?_
  · decide +kernel
  refine And.intro ?_ ?_
  · decide +kernel
  refine And.intro ?_ ?_
  · decide +kernel
  refine And.intro ?_ ?_
  · decide +kernel
  refine And.intro ?_ ?_
  · decide +kernel
  refine And.intro ?_ ?_
  · decide +kernel
  decide +kernel

/-- Exactly six source-order updates, starting from assemble.py:29. -/
def bootstrapEndpoint : Rat :=
  bootstrapStep selectedShrink (bootstrapStep selectedShrink
    (bootstrapStep selectedShrink (bootstrapStep selectedShrink
      (bootstrapStep selectedShrink (bootstrapStep selectedShrink checkpoint0)))))

theorem bootstrap_endpoint_matches_certificate :
    bootstrapEndpoint = selectedBitSaving := by
  unfold bootstrapEndpoint
  rw [stage1_certificate.1, stage2_certificate.1, stage3_certificate.1,
      stage4_certificate.1, stage5_certificate.1, stage6_certificate.1]
  decide +kernel

/-- Reuse the accepted outer-grid bracket at the derived finite endpoint. -/
theorem bootstrap_grid_bracket :
    let q := bootstrapEndpoint * (1 - 2 * eta)
    let margin := (1 - eta) * q / (1 + q)
    selectedKappa < margin ∧ margin ≤ selectedKappa + grid := by
  rw [bootstrap_endpoint_matches_certificate]
  exact selected_grid_bracket

end CurrentMain.SelectedBootstrapCertificate
#print axioms CurrentMain.SelectedBootstrapCertificate.shrink_matches_literal
#print axioms CurrentMain.SelectedBootstrapCertificate.supplied_input_domains
#print axioms CurrentMain.SelectedBootstrapCertificate.stage1_certificate
#print axioms CurrentMain.SelectedBootstrapCertificate.stage2_certificate
#print axioms CurrentMain.SelectedBootstrapCertificate.stage3_certificate
#print axioms CurrentMain.SelectedBootstrapCertificate.stage4_certificate
#print axioms CurrentMain.SelectedBootstrapCertificate.stage5_certificate
#print axioms CurrentMain.SelectedBootstrapCertificate.stage6_certificate
#print axioms CurrentMain.SelectedBootstrapCertificate.bootstrap_endpoint_matches_certificate
#print axioms CurrentMain.SelectedBootstrapCertificate.bootstrap_grid_bracket
