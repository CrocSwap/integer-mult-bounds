import Current596NativeUpperAggregate

/-!
Exact seven-update native bootstrap arithmetic from pinned main5996's PR596
assemble.py:177-185. The source complex saving is the accepted native input;
the PR543 bit saving, initial saving and charged coefficient remain supplied
finite inputs. This proof checks each update and all source min/ceiling choices.
It does not import the historical six-update bootstrap or its coefficient6464.

Current beta=eta=10^-24 and strict offset10^-27 are explicit. Eta belongs to
the subsequent q/grid/outer formulas; the present endpoint proof does not use
eta to claim any of the47 outer slacks. All-size bootstrap interpretation,
bit-supplier validity, native recurrence validity and physical realization
remain separate. Author-checked conditional source context:
kappa=16127213726553/10000000000000000=0.0016127213726553.
Attribution: PR596 complex-571-hpeq5/assemble.py and accepted rational
certificate interfaces. Prepared with OpenAI assistance; kernel checks only.
-/
namespace CurrentMain.Current596BootstrapCertificate
open Current596NativeUpperAggregate
set_option Elab.async false

/-- Source minimum/maximum use exact comparisons and retain tie order. -/
def ratMin (x y : Rat) : Rat := if x ≤ y then x else y
def intMax (x y : Int) : Int := if x ≤ y then y else x

def nativeComplexSaving : Rat := bCurrent
def suppliedBitSaving : Rat := ((413456747036699736067 : Rat) / 250000000000000000000000)
def eta : Rat := ((1 : Rat) / 1000000000000000000000000)
def beta : Rat := ((1 : Rat) / 1000000000000000000000000)
def strictOffset : Rat := ((1 : Rat) / 1000000000000000000000000000)
def selectedShrink : Rat := ratMin suppliedBitSaving ((1-beta)*nativeComplexSaving) - strictOffset
def recordedShrink : Rat := ((1615326444135573078562997384673555864426921437 : Rat) / 1000000000000000000000000000000000000000000000000)
def chargedCoefficient : Nat := 512

def bootstrapStep (s old : Rat) : Rat := (1-s)*s+s*old
/-- The source's left-associated minimum of all four gap expressions. -/
def sourceGap (s old next : Rat) : Rat :=
  ratMin (ratMin (ratMin (s-next) (1-next-s)) (1-next-s*(1-old))) (1-s)
def quadraticCeiling (gap : Rat) : Int := Rat.ceil (36/(gap*gap))
def linearCeiling (gap : Rat) : Int := Rat.ceil (2*(4+(chargedCoefficient : Rat))/gap)
def sourceCutoff (gap : Rat) : Int := intMax (quadraticCeiling gap) (linearCeiling gap)

/-- The native complex branch is the smaller of the two supplied candidates. -/
theorem saving_minimum_is_native :
    ratMin suppliedBitSaving ((1-beta)*nativeComplexSaving) =
      (1-beta)*nativeComplexSaving ∧
    (1-beta)*nativeComplexSaving < suppliedBitSaving := by decide +kernel

theorem shrink_matches_literal : selectedShrink = recordedShrink := by decide +kernel

/-- Arithmetic domains only, without a validity theorem for either supplier. -/
theorem supplied_input_domains :
    0 < nativeComplexSaving ∧ 0 < suppliedBitSaving ∧
    0 < selectedShrink ∧ selectedShrink < suppliedBitSaving ∧
    selectedShrink < (1-beta)*nativeComplexSaving ∧ selectedShrink < 1 := by
  rw [shrink_matches_literal]
  decide +kernel

def checkpoint0 : Rat := ((384599 : Rat) / 10000000000)
def checkpoint1 : Rat := ((1612779289907958213596228631246307552066462285707741835517689345469087061013100424950629855031 : Rat) / 1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000)
def recordedGap1 : Rat := ((2547154227614864966768753427248312360459151292258164482310654530912938986899575049370144969 : Rat) / 1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000)
def quadraticCutoff1 : Int := 5548709869643
def linearCutoff1 : Int := 405158035
def recordedCutoff1 : Nat := 5548709869643
def checkpoint2 : Rat := ((1615322329649991920551028861423901308029991446297271274665388442473733018748595453673447249762255004551184891052164960397498833503548936199547 : Rat) / 1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000)
def recordedGap2 : Rat := ((4114485581158011968523249654556396929990702728725334611557526266981251404546326552750237744995448815108947835039602501166496451063800453 : Rat) / 1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000)
def quadraticCutoff2 : Int := 2126529497787376855
def linearCutoff2 : Int := 250821148755
def recordedCutoff2 : Nat := 2126529497787376855
def checkpoint3 : Rat := ((1615326437489335715303939032508799960205555995186684884259486538008390401917961439804365842691306219935308833321819862426696528960015963751510758459242357631885417206978373612435739923989039 : Rat) / 1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000)
def recordedGap3 : Rat := ((6646237363259058352164755904221365441813315115740513461991609598082038560195634157308693780064691166678180137573303471039984036248489241540757642368114582793021626387564260076010961 : Rat) / 1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000)
def quadraticCutoff3 : Int := 814987233284840378036151
def linearCutoff3 : Int := 155275826545856
def recordedCutoff3 : Nat := 814987233284840378036151
def checkpoint4 : Rat := ((1615326444124837235596123142834567620664408430532028678654870387002043243125416937716975979914918570444419496880212796966900720231187715379535186775440728381704275302249909244162132582917796577277245172101988919441199654648682367302129043 : Rat) / 1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000)
def recordedGap4 : Rat := ((10735842966874241838988243762513006467971321345129612997956756874583062283024020085081429555580503119787203033099279768812284620464813224559271618295724697750090755837867417082203422722754827898011080558800345351317632697870957 : Rat) / 1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000)
def quadraticCutoff4 : Int := 312341865517677357899777532789
def linearCutoff4 : Int := 96126592311778987
def recordedCutoff4 : Nat := 312341865517677357899777532789
def checkpoint5 : Rat := ((1615326444135555736671952905803408907482049087481343406301002615595021496634468623698392228321225215382294988432472664022029437975279127083030070249078329438926092931623457046426646122479018058566244249950924250069569134365456276184775157904254437944780039204775693595002544896196994791 : Rat) / 1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000)
def recordedGap5 : Rat := ((17341891044478870146956944872349518656593698997384404978503365531376301607771678774784617705011567527335977970562024720872916969929750921670561073907068376542953573353877520981941433755750049075749930430865634543723815224842095745562055219960795224306404997455103803005209 : Rat) / 1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000)
def quadraticCutoff5 : Int := 119704256668970717993126960017304341
def linearCutoff5 : Int := 59509081065790536379
def recordedCutoff5 : Nat := 119704256668970717993126960017304341
def checkpoint6 : Rat := ((1615326444135573050550182189208963159801127620122988804238193329307115965644887664865354058034451409703758466962360157850041262886513982311255435238930615205894190807403038059451242376180360135297701070710912531171922290623389306004820862363384898720793090725740452435651112263786206693606954544743867677896001566370396941275255234667 : Rat) / 1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000)
def recordedGap6 : Rat := ((28012815195464592704625793816877011195761806670692884034355112335134645941965548590296241533037639842149958737113486017688744564761069384794105809192596961940548757623819639864702298929289087468828077709376610693995179137636615101279206909274259547564348887736213793306393045455256132322103998433629603058724744765333 : Rat) / 1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000)
def quadraticCutoff6 : Int := 45876363839095555735239306537247644852199
def linearCutoff6 : Int := 36840281592515045824396
def recordedCutoff6 : Nat := 45876363839095555735239306537247644852199
def checkpoint7 : Rat := ((1615326444135573078517747543513639095370184462957734196302511947648303660427450393333252127304059266360647888303105442714513354974042579367974603564565660944103563469568919557707845730447855537789831695297764003510871837527856819080350852009404345760288387375198992134019970442357578699777593113487379576886817142646737251194169276570666585907694167997148539648964290514613807856479 : Rat) / 1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000)
def recordedGap7 : Rat := ((45249841159916769056736974042265803697488052351696339572549606666747872695940733639352111696894557285486645025957420632025396435434339055896436530431080442292154269552144462210168304702235996489128162472143180919649147990595654239711612624801007865980029557642421300222406886512620423113182857353262748805830723429333414092305832002851460351035709485386192143521 : Rat) / 1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000)
def quadraticCutoff7 : Int := 17582004330198821475011877820092338200199342050
def linearCutoff7 : Int := 22806709892148010889880651
def recordedCutoff7 : Nat := 17582004330198821475011877820092338200199342050

/-- Twelve source arithmetic obligations, with both ceiling candidates exposed. -/
def StageFacts (old next gap : Rat) (quad linear : Int) (cutoff : Nat) : Prop :=
  bootstrapStep selectedShrink old = next ∧
  sourceGap selectedShrink old next = gap ∧
  gap = selectedShrink-next ∧
  quadraticCeiling gap = quad ∧ linearCeiling gap = linear ∧
  sourceCutoff gap = (cutoff : Int) ∧
  old < next ∧ next < selectedShrink ∧ selectedShrink < 1-next ∧
  0 < gap ∧ 36 ≤ (cutoff : Rat)*gap*gap ∧
  2*(4+(chargedCoefficient : Rat)) ≤ (cutoff : Rat)*gap

theorem stage1_certificate :
    StageFacts checkpoint0 checkpoint1 recordedGap1
      quadraticCutoff1 linearCutoff1 recordedCutoff1 := by
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
  refine And.intro ?_ ?_
  · decide +kernel
  refine And.intro ?_ ?_
  · decide +kernel
  refine And.intro ?_ ?_
  · decide +kernel
  decide +kernel

theorem stage2_certificate :
    StageFacts checkpoint1 checkpoint2 recordedGap2
      quadraticCutoff2 linearCutoff2 recordedCutoff2 := by
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
  refine And.intro ?_ ?_
  · decide +kernel
  refine And.intro ?_ ?_
  · decide +kernel
  refine And.intro ?_ ?_
  · decide +kernel
  decide +kernel

theorem stage3_certificate :
    StageFacts checkpoint2 checkpoint3 recordedGap3
      quadraticCutoff3 linearCutoff3 recordedCutoff3 := by
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
  refine And.intro ?_ ?_
  · decide +kernel
  refine And.intro ?_ ?_
  · decide +kernel
  refine And.intro ?_ ?_
  · decide +kernel
  decide +kernel

theorem stage4_certificate :
    StageFacts checkpoint3 checkpoint4 recordedGap4
      quadraticCutoff4 linearCutoff4 recordedCutoff4 := by
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
  refine And.intro ?_ ?_
  · decide +kernel
  refine And.intro ?_ ?_
  · decide +kernel
  refine And.intro ?_ ?_
  · decide +kernel
  decide +kernel

theorem stage5_certificate :
    StageFacts checkpoint4 checkpoint5 recordedGap5
      quadraticCutoff5 linearCutoff5 recordedCutoff5 := by
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
  refine And.intro ?_ ?_
  · decide +kernel
  refine And.intro ?_ ?_
  · decide +kernel
  refine And.intro ?_ ?_
  · decide +kernel
  decide +kernel

theorem stage6_certificate :
    StageFacts checkpoint5 checkpoint6 recordedGap6
      quadraticCutoff6 linearCutoff6 recordedCutoff6 := by
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
  refine And.intro ?_ ?_
  · decide +kernel
  refine And.intro ?_ ?_
  · decide +kernel
  refine And.intro ?_ ?_
  · decide +kernel
  decide +kernel

theorem stage7_certificate :
    StageFacts checkpoint6 checkpoint7 recordedGap7
      quadraticCutoff7 linearCutoff7 recordedCutoff7 := by
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
  refine And.intro ?_ ?_
  · decide +kernel
  refine And.intro ?_ ?_
  · decide +kernel
  refine And.intro ?_ ?_
  · decide +kernel
  decide +kernel

def bootstrapEndpoint : Rat :=
  bootstrapStep selectedShrink (bootstrapStep selectedShrink (bootstrapStep selectedShrink (bootstrapStep selectedShrink (bootstrapStep selectedShrink (bootstrapStep selectedShrink (bootstrapStep selectedShrink (checkpoint0)))))))

def recordedEndpoint : Rat := ((1615326444135573078517747543513639095370184462957734196302511947648303660427450393333252127304059266360647888303105442714513354974042579367974603564565660944103563469568919557707845730447855537789831695297764003510871837527856819080350852009404345760288387375198992134019970442357578699777593113487379576886817142646737251194169276570666585907694167997148539648964290514613807856479 : Rat) / 1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000)

/-- Seven ordered source updates reach the exact last serialized exponent. -/
theorem bootstrap_endpoint_matches_certificate : bootstrapEndpoint = recordedEndpoint := by
  unfold bootstrapEndpoint
  rw [stage1_certificate.1, stage2_certificate.1, stage3_certificate.1, stage4_certificate.1, stage5_certificate.1, stage6_certificate.1, stage7_certificate.1]
  rfl

#print axioms saving_minimum_is_native
#print axioms shrink_matches_literal
#print axioms supplied_input_domains
#print axioms stage1_certificate
#print axioms stage2_certificate
#print axioms stage3_certificate
#print axioms stage4_certificate
#print axioms stage5_certificate
#print axioms stage6_certificate
#print axioms stage7_certificate
#print axioms bootstrap_endpoint_matches_certificate
end CurrentMain.Current596BootstrapCertificate
