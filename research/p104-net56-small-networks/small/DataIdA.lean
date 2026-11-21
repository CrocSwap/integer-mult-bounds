import Nov15.FrameCert
import Nov15.LinP104Base
import Mathlib.Tactic.IntervalCases
/-!
DATAID (lane DATAID, Nov 20).  Kernel-only (no native_decide / sorry / new axioms).
Identifies the data embedded in the P104 Lean files with first-principles E8 objects.

Source objects.  E8 in standard coordinates, DOUBLED so everything is integral: a vector x : List Int with
x = 2 * (root).  `isRoot x` is the textbook root system: either exactly two entries are +-2 and the rest 0
(the 112 roots +-e_i +-e_j of D8), or all entries are +-1 with an even number of -1 (the 128 half-spin roots).
The E8 inner product of two roots is `dot x y / 4`.

What the repo calls P104: 104 of the 120 root lines of E8 (96 "A" ports from NETCODE + 8 "B" lines), given in the
repo by REBASET1/lines104.json (9-bit labels) and the signed Gram REBASET1/G104.npy.  Here the 104 ports are
the explicit roots `rootTab` (standard coordinates).  Nothing about WHICH 104 lines is derived: that choice is the
instance.  What is proved (kernel decide):
  * every row of rootTab is a root; dot(r_t, r_s) = 4 * G104[t][s] on all 104^2 cells with G104 the repo's signed
    Gram; off diagonal |G| <= 1 so the 104 roots are 104 distinct lines;
  * betaTab = 8 roots forming a Z-basis of E8 (Gram has an integer inverse, so det = +-1); bmMasks = its Gram mod 2;
    binvMasks is its inverse over F2 (already proved in LinP104Base: Binv * Bm = 1);
  * coordTab t = integer coordinates of r_t in the basis beta (sum_j C_tj beta_j = r_t exactly);
    xMasks t = those coordinates mod 2 (the F2^8 labels = E8 / 2 E8);
  * labMasks (the 9-bit labels.txt) have overlap parity = [<r_t, r_s> even]  (Q pattern);
  * the 759 frames of FrameCert = ALL 8-subsets of the 104 ports pairwise orthogonal (enumeration with proof of the
    enumerator), in lexicographic order, in the packed bitmask encoding used by FrameCert.
-/
set_option Elab.async false
namespace DataId
open P104Data

theorem forall_of_chunks (P : Nat → Bool) {n : Nat}
    (h : ∀ c, c < n → (List.range 13).all (fun i => P (13 * c + i)) = true) : ∀ t, t < 13 * n → P t = true := by
  intro t ht
  have h1 := h (t / 13) (by omega)
  rw [List.all_eq_true] at h1
  have h2 := h1 (t % 13) (List.mem_range.2 (Nat.mod_lt _ (by norm_num)))
  have e : 13 * (t / 13) + t % 13 = t := Nat.div_add_mod t 13
  rwa [e] at h2

def betaTab : List (List Int) := [
  [2, 2, 0, 0, 0, 0, 0, 0],
  [2, 0, 2, 0, 0, 0, 0, 0],
  [0, 0, 0, 2, 2, 0, 0, 0],
  [2, 0, 0, 2, 0, 0, 0, 0],
  [-2, 0, 0, 0, 0, 2, 0, 0],
  [0, 0, 0, 0, 2, 0, 2, 0],
  [0, -2, 0, 0, 2, 0, 0, 0],
  [-1, -1, 1, 1, -1, 1, -1, 1]]

def gbInvTab : List (List Int) := [
  [4, -2, -1, -1, -1, 1, 2, 3],
  [-2, 2, 1, 0, 1, -1, -1, -2],
  [-1, 1, 2, -1, 0, -1, -1, -1],
  [-1, 0, -1, 2, 1, 0, 0, -1],
  [-1, 1, 0, 1, 2, -1, 0, -2],
  [1, -1, -1, 0, -1, 2, 0, 2],
  [2, -1, -1, 0, 0, 0, 2, 1],
  [3, -2, -1, -1, -2, 2, 1, 4]]

/-- the 104 port roots r_t, doubled standard E8 coordinates; row t packed 3 bits per entry, entry = x + 2 -/
def rootCode : List Nat := [2471625, 6591051, 8986770, 4802706, 2406105, 7116507, 6592203, 8987922, 6657755, 4801554, 2404953, 2463305, 4793508, 5317780, 2987609, 2396875, 4794386, 2462427, 4859028, 2986699, 7116377, 2994907, 599188, 2929355, 4801684, 4727826, 4793602, 6665931, 2987739, 2396745, 4793634, 2462297, 4858898, 2986569, 4858002, 2462283, 2922201, 5316754, 7189083, 4792482, 6665945, 7190217, 2463449, 4726930, 2987721, 4850834, 7181001, 9053330, 2929369, 5325970, 8987778, 6591177, 8463506, 5309586, 2405065, 4801666, 74898, 2471499, 599170, 2470617, 4867218, 6592091, 4793620, 4794512, 2930265, 2405961, 4801680, 2471513, 8987796, 2995785, 4794642, 6656585, 7180889, 4785170, 7115337, 8987666, 2995915, 6657737, 4800658, 7116489, 598162, 6592217, 4269186, 6664905, 5252242, 2462409, 4727970, 2397771, 4727938, 6600267, 4203666, 7123657, 590994, 6599385, 2921161, 5317762, 4269204, 6664793, 4793616, 2405083, 4268178, 4793476, 6656729, 7189065]

def decRow (c : Nat) : List Int := (List.range 8).map fun a => (((c >>> (3 * a)) &&& 7 : Nat) : Int) - 2

def rootTab : List (List Int) := rootCode.map decRow

/-- coordinates of r_t in the basis beta (integers in [-2,2]); packed like rootCode -/
def coordCode : List Nat := [2667737, 7148619, 9278028, 4793554, 2401049, 6657170, 6886546, 9015955, 6890643, 5055627, 2663122, 2668177, 4793491, 4826706, 2438801, 2663577, 4793994, 2667674, 5060179, 2700889, 6657162, 2700442, 571033, 2696345, 5055635, 4789386, 4793497, 7152787, 2438809, 2663569, 4530906, 2667666, 5060171, 2700881, 5059667, 2930258, 2172120, 4826194, 7185484, 4792979, 6890195, 6923410, 2405593, 4788882, 2438808, 4798034, 6923346, 9282636, 2433753, 4826258, 9278539, 6886034, 9245324, 4564561, 2663129, 5055634, 537817, 2930322, 571032, 2667226, 5059731, 6886539, 4793498, 4531409, 2434257, 2663633, 4793042, 2667730, 9278540, 2700945, 4531417, 7152715, 6923339, 4793930, 6919242, 9278532, 2700953, 6890642, 5055123, 6657169, 570521, 6623954, 5022866, 7152275, 4560017, 2667673, 4526802, 2664081, 4789393, 7148683, 4756178, 6918802, 308888, 6885587, 2434200, 4826705, 5022867, 7152268, 4530905, 2663130, 5022355, 5056082, 6890131, 7185483]

def coordTab : List (List Int) := coordCode.map decRow

/-- signed Gram G104 (REBASET1/G104.npy): row t packed 2 bits per cell, cell = G + 1 -/
def gramCode : List Nat := [137225813399786426404825676086972193302600562605387151857504899,
 145065915507400341752703207720094061667196243216713835986904108,
 267312549434603434971633748501982504111169779861535190263632952,
 109807016567203071248677166768037738045588893937178436001420994,
 28354291248755230329672907921368430300381862863581098428159874,
 32649298497742871396346365495725577232511940023442160299978068,
 40690267851395299194713718876566748038519434906613170919618905,
 162936901778598392413644259658455190482492971551434525196347749,
 59996662933645751751097683591598625257458412735504624434522453,
 214182664223208113806666655611565051674265702247279101068706197,
 132729938904760272887662396764895743929058671173681763495445077,
 136723565595038978574837660181148806911091374247162415653654854,
 34586955113542721121777294178219712027663377875837660809288020,
 116111112828671036842178744247950427004935604905581250104088660,
 128682596241386550776470306800307636105083879363991405034014017,
 42699356863875623721541838782122290065736068715154923150468377,
 109304768762455623418689150862214351654079705578953699797570949,
 62005751946126076277925803497154167284675046544046376665371925,
 143458477264573917196930062343823475029882077617643714238633045,
 143529909661254391998327253566884882261947273573789965960172565,
 128682677947423696593314372051647025995534285870406876272089428,
 137527112252458215967479804993736887362247530185352090333037905,
 15280478325255122748549264211848444918273993540530736056309061,
 118220717170207763411095840278705010143308552356460636818134357,
 118149284773527288609698649055643602911243356400314385096594837,
 111313939480973093762361336019109283571746745893910923266495832,
 143630424990310794040416229692083923373103587216127600443368790,
 143558992593630319239019038469022516141038391259981348721829270,
 32649216791705725579502300244386187342061533517026689061902657,
 138732736313556448918509845338043738828758414562119639122579737,
 54065297921530050521647426241512037589823865303213000528927313,
 158039131395806901474893810053075616047697392391011092637483285,
 239491856714254742393898068899744923792904423464608430210744405,
 239563289110935217195295260122806331024969619420754681932283925,
 267312467728566289154789683250643114220719373355119719025557541,
 145065833801363195935859142468754671776745836710298364748828697,
 26316119303898978562153003113675254394074111368847963435653697,
 239965103292663408800038365154770066195772900643057254891013156,
 239893670895982933998641173931708658963707704686911003169473636,
 158440945577535093079636915085039351218500673613313665596212516,
 156532290188074024778053706053343460411989946940694076610483858,
 238056447903202340498455156123074175389262173970437665905284498,
 53663483739801858916904321209548302419020584080910427570198082,
 139134550495284640523252950370007473999561695784422212081308968,
 135187641454930174637305771279279017396292811110654016864998722,
 162434572267813798766812178501292414200533376686794317754422293,
 265374811112766439429358754568148979425567935502724218516247589,
 265303378716085964627961563345087572193502739546577966794708069,
 131194014764651468950130507863025954414260108037173364706788945,
 212646740083099309869134766709695262159467139110770702280050065,
 245996983633835512071577598630055694974563761717686513279804521,
 164544258315387671152573339783386387229356730644089175706543401,
 164472825918707196351176148560324979997291534687942923985003881,
 135087207831910918412060860405419366175586903974731853619877908,
 139234984118303896748497861243867125220267602920344375326429782,
 220687709436751737667502120090536432965474633993941712899690902,
 36294745273351256085951285177010559995233044104414474564604486,
 117747470591799097004955544023679867740440075178011812137865606,
 117818902988479571806352735246741274972505271134158063859405126,
 158541379200554349304881825958899002439206580749235828841333330,
 239994104519002190223886084805568310184413611822833166414594450,
 34185222637851675333878254397595366747310503159950559088634200,
 41092000327086344982612758657191093318872309622500272640272725,
 128783111570442952818559282925506677216240193006329039517210242,
 103373403750339922189238893512127763986445158146662075891975809,
 111414373103992349987606246892968934792452653029833086511616646,
 233661007031195443206536787674857377236426189674654440788345490,
 130720768186242802543990211608000812011391630858724540026520194,
 143458558970611063013774127595162864920332484124059185476708456,
 212244925901371118264391661677731526988663857888468129321320834,
 32749732120762127621591276369585228453217847159364323545098882,
 266910735252875243366890643470018768940366498639232617304903721,
 258869765899222815568523290089177598134359003756061606685262884,
 136623131972019722349592749307289155690385467111240252408534040,
 239563370816972363012139325374145720915420025927170153170359336,
 239491938420291888210742134151084313683354829971023901448819816,
 116211546451690293067423655121810078225641512041503413349209474,
 162535087596870200808901154626491455311689690329131952237618518,
 242003275237519660567558269962463242102080652137790389883519333,
 135187723160967320454149836530618407286743217617069488103074133,
 139134468789247494706408885118668084109111289278006740843233557,
 53663565445839004733748386460887692309470990587325898808273493,
 145166349130419597977948118593953712887902150352635999232024922,
 267412983057622691196878659375842155331875686997457353508753766,
 109778015340864289824829447117239494056948182757402524477839700,
 164544176609350525335729274532046997338906324137673704468467990,
 28253857625735974104427997047508779079675955727658935183039060,
 14878745849564076960650224431224099637921118824643634335655241,
 117818984694516717623196800498080664862955677640573535097480537,
 117747552297836242821799609275019257630890481684427283375941017,
 36294826979388401902795350428349949885683450610829945802679897,
 240065618621719810842127341279969107306929214285394889374209381,
 34256573328495004318431380369317384088925292609681339572098309,
 158541460906591495121725891210238392329656987255651300079408741,
 137196812173447644980977956436173949313959851425611240333923605,
 218649537491895485899982215282843257059166882499208577907184725,
 42627924467195148920144647559060882833670872759008671428928857,
 260907937844079067336043194896870774040666755250794741677769061,
 156603722584754499579450897276404867644055142896840328332023378,
 36696559455079447690694390208974295166036325326717047523333717,
 166481914931187520878004268465880522024508168496484676215853353,
 124152082182323464640546097628791597810943099788752260723729497,
 183850653397638123708957304498418264448295708472980629221446949,
 342432095559207383056444644966601489017938982280538330972569701]

/-! ## E8 in doubled standard coordinates -/
def dot (x y : List Int) : Int := (List.zipWith (· * ·) x y).sum

/-- the E8 root system, doubled coordinates: D8 roots (two entries +-2) or half-spin roots (all +-1, even # of -1) -/
def isRoot (x : List Int) : Bool :=
  x.length == 8 &&
  (((x.filter (· != 0)).length == 2 && x.all (fun a => a == 0 || a == 2 || a == -2)) ||
   (x.all (fun a => a == 1 || a == -1) && (x.filter (· == -1)).length % 2 == 0))

/-- E8 inner product of two doubled-coordinate roots -/
def ip (x y : List Int) : Int := dot x y / 4

def rootAt (t : Nat) : List Int := decRow (rootCode.getD t 0)
def betaAt (j : Nat) : List Int := betaTab.getD j []
def coordAt (t i : Nat) : Int := (decRow (coordCode.getD t 0)).getD i 0
def gramAt (t s : Nat) : Int := (((gramCode.getD t 0 >>> (2 * s)) &&& 3 : Nat) : Int) - 1
def gbAt (i j : Nat) : Int := ip (betaAt i) (betaAt j)
def gbInvAt (i j : Nat) : Int := (gbInvTab.getD i []).getD j 0

/-- the pattern Q of the ports, from the roots: Q_ts = 1 iff <r_t, r_s> is even -/
def QrootN (t s : Nat) : Int := if dot (rootAt t) (rootAt s) % 8 = 0 then 1 else 0
def Qroot (t s : Fin 104) : Int := QrootN t.1 s.1

/-! ## The ports are 104 distinct E8 root lines with the repo's signed Gram -/
theorem rootTab_length : rootTab.length = 104 := by decide +kernel
theorem rootTab_isRoot : rootTab.all isRoot = true := by decide +kernel
theorem gramCode_length : gramCode.length = 104 := by decide +kernel

def rowGramOK (t : Nat) : Bool :=
  (List.range 104).all (fun s => dot (rootAt t) (rootAt s) == 4 * gramAt t s)

theorem gram_exact_c0 : (List.range 13).all (fun i => rowGramOK (13*0+i)) = true := by decide +kernel
theorem gram_exact_c1 : (List.range 13).all (fun i => rowGramOK (13*1+i)) = true := by decide +kernel
theorem gram_exact_c2 : (List.range 13).all (fun i => rowGramOK (13*2+i)) = true := by decide +kernel
theorem gram_exact_c3 : (List.range 13).all (fun i => rowGramOK (13*3+i)) = true := by decide +kernel
theorem gram_exact_c4 : (List.range 13).all (fun i => rowGramOK (13*4+i)) = true := by decide +kernel
theorem gram_exact_c5 : (List.range 13).all (fun i => rowGramOK (13*5+i)) = true := by decide +kernel
theorem gram_exact_c6 : (List.range 13).all (fun i => rowGramOK (13*6+i)) = true := by decide +kernel
theorem gram_exact_c7 : (List.range 13).all (fun i => rowGramOK (13*7+i)) = true := by decide +kernel
theorem gram_exact : ∀ t, t < 104 → rowGramOK t = true := by
  intro t ht
  refine forall_of_chunks rowGramOK (n := 8) ?_ t (by omega)
  intro c hc
  interval_cases c
  · exact gram_exact_c0
  · exact gram_exact_c1
  · exact gram_exact_c2
  · exact gram_exact_c3
  · exact gram_exact_c4
  · exact gram_exact_c5
  · exact gram_exact_c6
  · exact gram_exact_c7

/-- off the diagonal |G| <= 1 (so r_t != +-r_s: distinct lines); diagonal 2 -/
theorem gram_lines :
    (List.range 104).all (fun t => (List.range 104).all (fun s =>
      if t == s then gramAt t s == 2 else (gramAt t s).natAbs ≤ 1)) = true := by decide +kernel

/-! ## The Z-basis beta of E8, its Gram, the labels -/
theorem betaTab_isRoot : betaTab.length = 8 ∧ betaTab.all isRoot = true := by
  constructor <;> decide +kernel

theorem coordTab_shape : coordTab.length = 104 ∧ coordTab.all (fun r => r.length == 8) = true := by
  constructor <;> decide +kernel

/-- beta is a Z-basis of E8: its Gram (dot/4, exact) has an integer inverse, so det = +-1 (E8 is unimodular) -/
theorem beta_gram_exact :
    (List.range 8).all (fun i => (List.range 8).all (fun j => dot (betaAt i) (betaAt j) % 4 == 0)) = true := by
  decide +kernel

theorem beta_unimodular :
    (List.range 8).all (fun i => (List.range 8).all (fun j =>
      ((List.range 8).foldl (fun a k => a + gbAt i k * gbInvAt k j) 0) == (if i == j then 1 else 0))) = true := by
  decide +kernel

/-- bmMasks = the Gram of beta mod 2 (row i, bit j) -/
theorem bm_is_gram_mod2 :
    (List.range 8).all (fun i => (List.range 8).all (fun j =>
      (bmMasks.getD i 0).testBit j == (gbAt i j % 2 == 1))) = true := by decide +kernel

/-- the coordinates: sum_j C_tj beta_j = r_t exactly (so r_t = sum_j C_tj beta_j in E8) -/
def lincomb (c : List Int) : List Int :=
  (List.range 8).map fun a => (List.range 8).foldl (fun s j => s + c.getD j 0 * (betaAt j).getD a 0) 0

theorem coord_lincomb : (List.range 104).all (fun t => lincomb (decRow (coordCode.getD t 0)) == rootAt t) = true := by
  decide +kernel

/-- xMasks (the F2^8 labels used everywhere in LinP104*) = coordinates of r_t in beta, mod 2 -/
theorem xMasks_is_coord_mod2 :
    (List.range 104).all (fun t => (List.range 8).all (fun i =>
      (xMasks.getD t 0).testBit i == (coordAt t i % 2 == 1))) = true := by decide +kernel

/-! ## labels.txt (9-bit) realise the pattern Q of the roots -/
def QlabN (t s : Nat) : Int :=
  if ((List.range 9).filter (fun i => (labMasks.getD t 0 &&& labMasks.getD s 0).testBit i)).length % 2 = 1
  then 1 else 0

def rowQOK (t : Nat) : Bool := (List.range 104).all (fun s => QlabN t s == QrootN t s)

theorem Qlab_eq_Qroot_all_c0 : (List.range 13).all (fun i => rowQOK (13*0+i)) = true := by decide +kernel
theorem Qlab_eq_Qroot_all_c1 : (List.range 13).all (fun i => rowQOK (13*1+i)) = true := by decide +kernel
theorem Qlab_eq_Qroot_all_c2 : (List.range 13).all (fun i => rowQOK (13*2+i)) = true := by decide +kernel
theorem Qlab_eq_Qroot_all_c3 : (List.range 13).all (fun i => rowQOK (13*3+i)) = true := by decide +kernel
theorem Qlab_eq_Qroot_all_c4 : (List.range 13).all (fun i => rowQOK (13*4+i)) = true := by decide +kernel
theorem Qlab_eq_Qroot_all_c5 : (List.range 13).all (fun i => rowQOK (13*5+i)) = true := by decide +kernel
theorem Qlab_eq_Qroot_all_c6 : (List.range 13).all (fun i => rowQOK (13*6+i)) = true := by decide +kernel
theorem Qlab_eq_Qroot_all_c7 : (List.range 13).all (fun i => rowQOK (13*7+i)) = true := by decide +kernel
theorem Qlab_eq_Qroot_all : ∀ t, t < 104 → rowQOK t = true := by
  intro t ht
  refine forall_of_chunks rowQOK (n := 8) ?_ t (by omega)
  intro c hc
  interval_cases c
  · exact Qlab_eq_Qroot_all_c0
  · exact Qlab_eq_Qroot_all_c1
  · exact Qlab_eq_Qroot_all_c2
  · exact Qlab_eq_Qroot_all_c3
  · exact Qlab_eq_Qroot_all_c4
  · exact Qlab_eq_Qroot_all_c5
  · exact Qlab_eq_Qroot_all_c6
  · exact Qlab_eq_Qroot_all_c7

theorem labels_agree : (List.range 104).all (fun t => FrameCert.labelAt t == labMasks.getD t 0) = true := by
  decide +kernel

#print axioms DataId.rootTab_isRoot
#print axioms DataId.gram_exact
#print axioms DataId.gram_lines
#print axioms DataId.betaTab_isRoot
#print axioms DataId.beta_unimodular
#print axioms DataId.bm_is_gram_mod2
#print axioms DataId.coord_lincomb
#print axioms DataId.xMasks_is_coord_mod2
#print axioms DataId.Qlab_eq_Qroot_all
#print axioms DataId.labels_agree
#print axioms DataId.beta_gram_exact
end DataId
