# Root helper exchange in the exact forest caller

This note completes the proof of the **exchanged F19** construction. The
underlying recursive forest and its physical leaf normalization are proved in
`FOREST-CONTROLLER-PROOF.md`. The exchanged construction is the qualified
improvement; the later triangular two-full candidate is not used here.

## 1. The subtree interface, including the selected helper

A binary subtree containing `k>1` full leaves has two carry fields with endpoint

    D [I+(q-1)N],   N=-E12,

where `D` is the product of its `k` fresh body transforms. Every fresh internal
coordinate pair has endpoint `q` times the product of the body transforms
below that pair. In particular, either coordinate of the subtree's own fresh
root pair is an independent `qD` field. Selecting one of those coordinates
does not add a query: it removes that field from the separately counted
internal targets and includes it in the three-field macro interface.

For a one-leaf subtree, select one of that leaf's independent full-height
native helpers. It has endpoint `qD` after the same ordinary head adapter.
This helper is explicitly subtracted from the native-helper inventory. The
complex source has 385 full H9 helpers for 104 ports; the BIT source has 419
full H8 helpers for 111 ports. The root construction selects one such helper
per port from its middle leaf, so both inventories suffice.

Thus all three root children provide a two-field rank-one shear and a third
independent `qD` field, with every other target retained. No scratch field is
promoted or assumed zero at entrance.

## 2. Five-field exact exchange

Place the three selected macro interfaces on coordinate sets

    {0,1,2}, {1,2,3}, {1,3,4}.

For the complex branch, the three responses in those coordinates are

    N0 = [[1,0,0], [0,1,1], [0,-1,-1]],
    N1 = [[-1,-1,-1], [-1,0,0], [3,2,2]],
    N2 = [[-1,-1,0], [1,1,0], [0,0,1]].

Each is conjugate over Q to `J2(0) direct-sum [1]`. The stored basis and inverse
are exact Gaussian-dyadic matrices. The literal emitter adjusts the sign of
the forest carry `-E12`, conjugates each complete child word by that basis,
and embeds the child body projector on the same three coordinates. The BIT
branch uses a separately checked GF(2) conjugation; it is not obtained by
reducing a rational matrix with an even denominator.

The complete five-field product is diagonal. Its body histories are

    A, A+B+C, A+B, B+C, C,

and all five fields carry one `q`. This is an exact identity over
`Q[q,d_A,d_B,d_C]/(q^2-1)` and separately over GF(2). The body variables are
generic commuting variables, not involutions. Every full subtree is expanded
into its original FULL, THIN and grouped IDLE events before checking the
identity. The root's independent checker expanded every coefficient and
checked all 1,225 entries of the 35-field complete F19 endpoint.

Relative to the three unmodified root macros, the net target change per port
is

    +H_(1+s(A+B)) + H_(1+s(B+C))
    -H_(1+s(A+B+C)) - H_(1+sB).

All selected-helper debits are included in this expression. The paid profile
does not change. The best enumerated binary forest uses `(A,B,C)=(9,1,9)`;
the two large child trees and every scalar basis are contained in the emitted
controller files.

## 3. Complete bill and qualified result

The complete word has 19 full native leaves, 16 thin queries and 16 grouped
two-field idle events per port. The selected middle-leaf helper is debited
once per port. Its ordinary changes of basis use only fixed rational
coefficients, and its owned scratch is covered by the explicit reserves in
`forest_admission.py`. The original source normalizers, absolute phases,
spectator routes, finite precision and analytic recovery assumptions remain.

The exact rational crossing enclosures are

    BIT:     (0.0036610024320228, 0.0036610024320240),
    complex: (0.0032431420948645, 0.0032431420948658).

The rank surpluses are 801 and 808 respectively. Both complete moments remain
negative at 0.004. The finite certificate uses power 768, paid cutoff
`15^768`, productive floor `16^768`, and strict rational tail bounds. After
uniformization and the separately checked BIT ordinary wrapper, the admitted
branch savings are 0.00366100237 (BIT ordinary) and 0.00324314204 (complex).
The root's independent outer ledger admits the qualified overall value
**0.00324314203**. No conditional triangular-source saving enters that ledger.

## Reproduction and evidence

Run `python -B emit_exchange_forest.py 19` and
`python -B forest_admission.py --exchange` in this directory. The literal
controllers are `EXCHANGE-F19-BIT-CONTROLLER.json` and
`EXCHANGE-F19-COMPLEX-CONTROLLER.json`; the rational finite receipt is
`EXCHANGE-FOREST-F19-ADMISSION.json`. The independent polynomial replays are
`../root/EXCHANGE-F19-BIT-INDEPENDENT.json` and
`../root/EXCHANGE-F19-COMPLEX-INDEPENDENT.json`, produced without importing the
proposer's controller implementation. The independent outer ledger is in
`../root/close_outer_ledger.py` and its receipt.

## Native replacements admitted later in this run

The same exact controller is also bound to the independently emitted functional-
kernel BIT natives. Their scalar main interface is unchanged, while their
paid/helper profiles and owned inventories are recomputed from their literal
words. The current FUNCTIONAL-KERNEL-05 word has657 public fields,231 owned
fields,34086 events,416 full H8 helpers and19 H4 helpers, so the selected
111 full-helper heads still exist. Its complete paid local profile is
{1:1386,2:1245,3:62,4:49,5:9,6:108,7:10}. The new157-edge route packet uses
fixed avoidance16; the generic prime rule excludes these denominators.

`FUNCTIONAL-KERNEL-05-FOREST-F19-ADMISSION.json` gives the complete new
invoice and finite compiler: raw crossing in
(0.0036953660514800,0.0036953660515600), strict ordinary BIT0.00369536597.
The parent independently replayed the source, routes, interval tails and
ordinary bootstrap. The complex branch is unchanged, and so is overall
kappa0.00324314203. Earlier native/admission packets remain separately pinned.

## Functional06 binding (17:32 UTC)

The same independently replayed F19 controller binds to the corrected
`FUNCTIONAL-KERNEL-06-INPUTS.json` pins. The literal native has659 public
fields,231 owned fields and34110 events, helpers416H8+21H4, and paid profile
{1:1386,2:1247,3:62,4:47,5:9,6:110,7:10}. Its161 route certificates use fixed
denominator avoidance16. No controller identity or helper selection changes.
The complete finite admission is `FUNCTIONAL-KERNEL-06-FOREST-F19-ADMISSION.json`,
SHA256 `40267477da3a96306945af88286e0da5f20f8741c21428fd5cfae22404158068`.
Its strict ordinary BIT saving is0.00369604337; all ordinary and owned reserves
remain explicitly charged. The complex branch and overall bottleneck remain
unchanged. Reproduce with `python -B forest_admission.py --functional06`.

## Functional07 binding: six exact temporal cuts

Six literal cached temporal helper cuts improve functional06 by a certified
local moment of0.0330590773181 at saving0.004. The first four replace an H8
helper by two H4 helpers and split a paid H6 into H4+H2. The fifth splits
an H7 into H4+H3; the sixth creates H6+H2 productive pieces while paying the
recorded H6→H4+H2 fragmentation. Every source column, transposed column,
frame contact and owned lifetime is replayed in two independent scalar
representations. The final existing-frame candidate screen has negative best
remaining gain; this is a scoped saturation result, not a global optimum.

The frozen source is `FUNCTIONAL-KERNEL-07-INPUTS.json`, with word SHA
`8ae7b21aa4f5103c7791ef92ffaedca61e26544b299ead99bae0b15e46b77604`.
It has665 public fields,243 owned fields,34206 events; independent helpers
410H8+31H4+H6+H2 and paid profile
{1:1386,2:1252,3:63,4:53,5:9,6:105,7:9}. Its160 new native/productive route
canonicalizers have fixed denominator avoidance16. Full source rank surplus
remains801 after the same F19 caller, and all global ordinary/owned reserves
are charged by `forest_admission.py --functional07`.

The complete finite receipt `FUNCTIONAL-KERNEL-07-FOREST-F19-ADMISSION.json`
has SHA256 `a0fc4818ed23c4d1c26df16142cee57545524a951ef2ccb72fb2a03c75338866`.
The raw crossing is bracketed by0.0036987459032000 and0.0036987459032200; the
strict ordinary BIT saving is **0.00369874582**. The complex/overall bottleneck
is unchanged.
