# The irregular 38-port split on both native providers

The exact irregular 38-port witness now has complete native backward
and forward words. They add no recursive children or private fields.
Both the ordinary borrowed-state block and the normalized original-X
response are dyadic units. The response inverse also has an explicit
scalar word at the completed FULL-X boundary.

This moves the witness beyond a matrix test. It does not give a complete
inter-call decoder or a new supplier bound. The selected interface has
two fewer fields than the complete-minor construction. Its local scalar
bill is slightly higher.

## Source and matrices

The selected set S is

    1,3,4,17,18,19,20,23,24,26,27,29,35,36,38,39,40,42,45,
    60,63,66,69,74,75,77,78,84,86,88,97,99,104,105,107,108,109,111.

Let U be the other 74 ports. Use the actual R, K=R^T/4, and J=I-KR
from the new clean-J core. Define

    D=R_S K_S,  T=D-13I,  H=I_U-K_U R_U,  W=I-D.

The independent witness receipt gives both inverses T^-1 and W^-1. The
emitter reads that pinned receipt, recomputes the selected Gram matrix
from the native core's R, checks both T inverse orders, and checks the
explicit factor

    L=I+(E_02+E_03+E_14+E_15)/4,
    T^-1=-L^-T L^-1/8.

The finite matrix identities imply

    H^-1=I_U+K_U T^-1 R_U.

They do not assume that the ordinary query rows are orthogonal.

## The eight current queries

The inverse word clears existing C0 through C7 in the current FULL
frame. It forms all eight current queries R_U x_U before it changes any
data field. It then applies L^-1 and L^-T to those eight query fields:

    C0-=C2/4; C0-=C3/4; C1-=C4/4; C1-=C5/4;
    C2-=C0/4; C3-=C0/4; C4-=C1/4; C5-=C1/4.

It divides every C field by 32, scatters the negative R_U^T columns
back to ordinary X, and clears all eight C fields at I. This is H^-1.
Scattering to the full R^T columns instead also gives the upper change
`X_S += K_S R_U H^-1 X_U`. The same finite query code is used in both
variants.

For H at the input-I boundary, form all eight R_U y_U queries first,
divide each by 4, scatter negative R_U^T, and clear. These are current
queries within one boundary operation. No saved source or old query is
used after a data change.

Each query field is owned, and each can contain arbitrary data on entry.
The initial CLEARs remove that data. The borrowed helpers are not used by
these factors. Eight existing fields are live at once. No new record
cohort or private buffer is allocated.

| Factor | Real scalar primitives |
| --- | ---: |
| H on ordinary input Y | 4800 |
| H^-1 on ordinary output X | 4944 |
| H^-1 with selected upper change | 6160 |

The query and ordinary scatter each have 296 unit ADDs. The full scatter
has 448. The inverse has eight additional quarter-unit ADDs. All scales
and ADD coefficients are dyadic. Every operand has the same physical
frame, either I or FULL.

## Complete local words

The balanced backward word exchanges selected physical X and Y, runs
the complete clean-J backward core, and applies H^-1 to ordinary FULL X.
It has the map

    X_S' = q b-J_SS Q a-J_SU v,
    X_U' = H^-1 u-v-H^-1 J_US Q a,
    Y_S' = Q a,
    Y_U' = v.

Here x=(a,u), y=(b,v), Q is the diagonal positive selected line operator,
and q=Q^-1. The physical input and output conventions are those in
`RAW-SELECTED-TRANSFER.md`. No Q is commuted through a dense matrix.

Use the full scatter to obtain the diagonal-borrowed word. Put
c=R_S Q a+R_U u. Its map is

    X_S' = q b-Q a+K_S T^-1 c,
    X_U' = u-v+K_U T^-1 c,
    Y_S' = Q a,
    Y_U' = v.

Physical selected Y is F a in both variants. The original selected X
information is therefore carried by productive outputs.

The forward word applies H to ordinary Y at I, exchanges selected
physical X and Y, runs the complete clean-J forward core, and repeats
the exchange at output. Its map is

    X_S' = a+q J_SS q b+q J_SU u,
    X_U' = u,
    Y_S' = b,
    Y_U' = H(u+v)+J_US q b.

| Word | Real scalar primitives | Native rank mass | Native children |
| --- | ---: | ---: | ---: |
| Balanced backward | 170446 | 5073 | 3507 |
| Diagonal-borrowed backward | 171662 | 5073 | 3507 |
| Balanced forward | 171290 | 5073 | 3507 |

Each row includes the full 164514-scalar clean-J core, every physical
exchange, every query operation, and all owned preparation and cleanup.
No extra cleanup of C1 through C7 is needed: the factors already clear
all eight C fields, and the core preserves their zero values. The native
profile is `{1:2433,2:724,3:228,4:102,5:20}` in every row.

## Explicit response inverse at FULL X

Set E=diag(-I_S,I_U). The diagonal-borrowed original-X response and its
inverse are

    A=E+K T^-1 R,
    A^-1=E-E K W^-1 R E.

To apply A^-1, first apply the selected E signs to X. Form all eight
full R queries in C0 through C7. Apply the following finite matrix to
the queries:

    C0+=C2/2; C0+=C3/2; C1+=C4/2; C1+=C5/2;
    C0/=4; C1/=4; C2/=16; C3/=16; C4/=16; C5/=16;
    C6/=16; C7/=16;
    C2+=C0/2; C3+=C0/2; C4+=C1/2; C5+=C1/2.

This finite map is -W^-1/4. Scatter E R^T times the query vector and
clear all eight owned fields at I. The complete cost is 7412 scalar
primitives. It has no native children.

A has a similar word: form all R queries, apply the L inverse factors,
divide by 32, scatter negative E R^T, clear, and apply selected E signs.
Its complete cost is 7452. Both words preserve all other live inputs.
Their two literal composition orders give identity on all live data.

The inverse can follow the diagonal-borrowed backward word at the common
FULL-X boundary. The resulting scalar bill is 179074 and the rank mass
stays 5073. This follows by composition of the two checked words; it is
not a separate whole-core replay. The original-X coefficient becomes the
explicit input code diag(Q_S,I_U). Its inter-call use is still open.

## Checks and scope

`emit_irregular_38.py` replays all six complete native words on both
providers. It checks all 640 arbitrary input columns, all 408 helpers,
the 91 private zero buffers, and all eight owned outputs. It retains and
checks every native scalar frame, native transition, warp, and private
buffer lifetime. All helpers restore, all zero buffers return to zero,
and every owned field ends at zero in frame I.

`emit_irregular_38_unit.py` checks both response maps and both literal
inverse orders on all 640 input columns in the actual provider endpoint
frames. The source phase review, with separate literal dual warp tables,
is inherited unchanged. Independent review of these new words remains
required.

Run with one process:

    python3 -I -B emit_irregular_38.py
    python3 -I -B emit_irregular_38_unit.py

This is an actual native application of the irregular two-unit witness.
It does not prove that 38 selected ports are minimal. It does not price
the inter-call decoder, selected phases in other views, owner histories,
private hosting, full recursive precision, or the complete supplier.

## Sources and credit

The native core and prior raw exchange credit are in
`CLEAN-J-TRANSFER.md`, `RAW-SELECTED-TRANSFER.md`, and
`BALANCED-FIVE-MINORS.md`. The budget-geometry and dyadic-subset-search
lanes found and proved the irregular subset. The coordinating lane
checked both full inverse identities separately in
`root/IRREGULAR-SPLIT-20261017.md`. Its witness receipt has SHA256
`0a8d22fa0b523c261243e9b19cfd51926c9b515a9e6f9a962d1e3b5170105a8f`.
This lane emitted the finite query transforms and complete native words,
priced them, and placed the response unit at FULL X. OpenAI Codex assisted
the research and checks. No PR, push, or publication commit was made.
