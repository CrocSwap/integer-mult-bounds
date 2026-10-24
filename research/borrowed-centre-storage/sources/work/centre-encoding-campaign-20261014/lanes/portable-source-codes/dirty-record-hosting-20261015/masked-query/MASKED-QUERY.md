# A unit code for a prescribed masked current query

The actual clean-J forward core can export the masked query

    R_U(X_U+Y_U)

in eight selected FULL target fields. Here U is the 96-port complement
of the earlier A and T sets. The new word uses eight rank-one children
beyond the clean-J core, the same count as the earlier full-sum query
word. Its complete local scalar allowance is 213,466. It preserves all
target information with a dyadic unit code, restores all 480 arbitrary
helper contents, and clears the eight owned private fields. No helper
baseline becomes a new record.

The input mask costs only 64 half ADDs at the original I cut. A selected
source correction makes the source query equal to the same mask. This
provides the eight directions missing from the selected-16 dirty erase.
It changes the F2 target code and its selected Y frame type. It does not
close the later controller or improve the complete kappa calculation.

## Exact unit and query theorem

Work over a ring. Use free coordinate modules and compatible linear maps.
Let R:V->W and K:W->V. Choose output coordinates A such that R_A is
invertible, and assume the A part of K is the embedded inverse
P_A=iota_A R_A^-1. Define

    L_A=R_A pi_A,     R_offA=R-L_A,
    K_offA=K-P_A,     J=I-KR.

The earlier current-query unit is

    T=(I-K_offA L_A)(I+P_A R_offA).

Each factor is a unit shear. Their inverse factors have the opposite
sign and reverse order. Direct expansion gives

    L_A T=R,          pi_offA T=pi_offA J.

No inverse of J or I-RK is used.

Choose a set U of target coordinates to retain in the query. Let V0 be
its complement, R_U=R pi_U, and L_V0=R pi_V0. Suppose R_U has a right
inverse P_U supported on U:

    R_U P_U=I,        pi_V0 P_U=0.

Set

    B=I-P_U L_V0,     B^-1=I+P_U L_V0.             (1)

The product L_V0 P_U is zero. Thus both inverse products in (1) are I.
Also R P_U=I, so

    R B=R-L_V0=R_U.                                (2)

For any prescribed source query D:V->W, define

    H_D=J+P_A(D-L_A J).                            (3)

Only the A output rows differ from J, and L_A H_D=D. The complete map

    X_out=X,       Y_out=H_D X+T B Y               (4)

is invertible. Its exact content inverse is

    X=X_out,
    Y=B^-1 T^-1(Y_out-H_D X_out).                 (5)

Its selected query is

    L_A Y_out=D X+R_U Y.                          (6)

This proof makes no commutation assumption about the displayed maps.
All products retain their stated order. The source response H_D need
not be invertible: X remains available, and the target block T B is a
unit. Equation (5) is not a circuit for mixed native frames.

The right-inverse condition is also necessary for any invertible target
code C with L_A C=R_U. Indeed, C^-1 P_A is a right inverse of R_U. Thus
the theorem gives an exact algebraic condition for this masked-query
interface. A dyadic coordinate minor is one sufficient way to obtain
P_U; it is not asserted to be the only way.

## The actual section and selected source response

Use the pinned 8-by-112 R and K=R^t/4. The output set and excluded set are

    A=[0,7,20,27,36,46,57,111],
    T_ports=[21,37,47,76,81,87,92,110],
    V0=A union T_ports,       U=all other ports.

The retained set contains the exact orthogonal minor

    H_ports=[1,6,22,28,33,49,58,109].

Its Gram matrix is 4I and its determinant is -256. Its transpose divided
by four gives the dyadic section P_U. A separate greedy minor
[1,2,3,4,5,6,8,12] has determinant -32 and provides an independent check
that the retained query has a dyadic section.

The map B-I has exactly 64 nonzero entries: 40 coefficients -1/2 and
24 coefficients +1/2. Its destinations are H_ports and its sources are
V0. These supports are disjoint, so its 64 literal ADDs commute and no
snapshot or scratch field is required.

Choose D=R_U. Equation (6) is then the masked sum R_U(X_U+Y_U). In this
case the selected correction simplifies to

    H_D-J=P_A(2R_U+L_T),       L_T=R_T pi_T.

It has 384 unit ADDs and 32 half ADDs. Its scalar allowance is 3,392,
the same as the earlier full-sum source correction. The target-only
choice D=0 is also allowed by the theorem. Its literal selected suffix
would have 416 half ADDs and complete scalar allowance 214,234. That
second word is not emitted by this packet.

## Native chronology and complete local cost

The literal word has this order:

1. Apply B to Y at the original I input cut.
2. Apply the two unchanged T prefix factors to Y at I.
3. Run the complete unchanged clean-J core.
4. Apply the eight unchanged positive lines to Y_A.
5. Add (H_D-J)X to those now-FULL selected Y fields.

The target prefix is T B. Reversing this order is incorrect. Before the
core, its data is (X,T B Y). The core gives target T B Y+JX. The last
two steps change its selected type and add the exact difference in (3).
They do not change any off-selected response. This proves (4) on
arbitrary inputs without transferring a generic budget to a new kernel.

| Fields | Input frame | Output frame |
| --- | --- | --- |
| X_p | C_qp | FULL |
| Y_p in A | I | FULL |
| Y_p outside A | I | FULL C_qp^-1 |
| 480 helpers | Original frames | Original complete job frames |
| C0 through C7 | Owned, arbitrary | Zero at I |

The new mask touches only target data at I. Every new suffix ADD reads
FULL X and writes FULL Y_A. The retained core and the eight complete
native line records are unchanged from the independently reviewed unit
query packet. Their exact phases and kernels are inherited. The new
word does not add a native phase assumption.

| Part | Real scalar primitives |
| --- | ---: |
| Mask B | 640 |
| Retained T prefix | 7,296 |
| Retained clean-J core | 202,138 |
| Masked source correction | 3,392 |
| Complete word | 213,466 |

There are 26,587 literal events. The native profile is
{1:2420,2:418,3:432,4:142,5:82}, of mass 5,530. The eight added rank-one
children have sixteen native wrappers. There is no added field and no
new private use in the mask. New child hosting, address work, primitive
prefix precision, and the complete supplier invoice remain separate.

## The exact missing read at F2

This section states an ordered content identity at the later complete
cut. It does not bind the changed F2 word to the full global schedule.
Use the actual stage-2 routes in the earlier dirty-record packet. Let
z=(x,y), d=z+E h, and let c denote the other pair's X before the first
selected bridge. That bridge gives the F2 source and target

    l_U=x_U+c_U,      l_V0=c_V0,
    v_U=y_U,         v_V0=arbitrary.

The masked word retains the FULL source l. Its selected output supplies

    q=R2_U(l_U+y_U).

At the post-F2 idle, the parked selected fields d_XV0 and d_YV0 and the
other source fields c_U have the same full U2 frame as l. Define

    f=R0_U(l_U-c_U)+R0_V0 d_XV0.

Since R0 E_X=0, f=R0 x. The exact query required to erase the eight
dirty A records is

    Gz=P2_A [q-R2_U c_U+R2_T(d_XT+d_YT)
                -R2_offA P0_offA f].             (7)

The term in brackets is R2_offA of the original F0 target. Every route
in (7) keeps its order. No stage-2 map is moved through a stage-0 query.
There is no read of an off-selected Y field at this cut. The arbitrary
target values v_V0 cancel because the mask removed them before the core.
The exact row check is supplied by the independent proof review.

The unmasked R2(l+v) query does not suffice for this input split. A change
in y_U can be canceled in that query by an independent change in v_A,
while all other named FULL observations remain fixed. The mask resolves
that specific obstacle. It does not retire the new target code T B or
its selected native line code before B3.

The direct selected-16 component has boundary cost

    16(112 initial Y+96 early Y returns+16 final X)+214=3,798.

Appending eight query children per replica gives the diagnostic 3,926,
versus 3,798 for full-W. A complete replacement of the old QQ16 F2 has
a different comparison: its original local word already has eight
rank-one children beyond clean-J, as does this masked word. That
replacement need not add native rank at this local comparison point.
Neither comparison includes retirement of the changed target code or
admission of the next call. The 224-per-pair boundary cost is not removed.

## Reproduction, sources, and scope

Run with standard-library Python 3 and one CPU:

```sh
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/portable-source-codes/dirty-record-hosting-20261015/masked-query/emit_masked_query.py --out /private/tmp/masked-query
```

Expected status is `PASS_MASKED_CURRENT_SUM_QUERY_UNIT_712_COLUMNS`.
The producer checks all 712 input columns, 480 arbitrary helpers, eight
private outputs, both mask and target inverse orders, the exact query,
the legal new scalar cuts, the unchanged native records, and the literal
cost. Controls reject a missing mask, the opposite mask sign, the wrong
prefix order, the old unmasked source suffix, and an incomplete section.

The source is the paired-package-review current-query encoder, especially
UNIT-QUERY.md and its payload 9cb744034b11ef515a9c429264199a03f02fd9c4cb408e6455021ce9c0802a9c.
The source proof supplies T, the clean-J core, and the selected positive
line interface. The coherent-port UNIT-REVIEW supplies its independent
native review. The earlier QQ16 and eight-record work supplies the
actual port sets and equation (7). The source pins are explicit in the
producer and emitted payload. All predecessor files remain unchanged.
OpenAI Codex supplied research, implementation, and review assistance.

This is a local enabling construction. It supplies selective query
access with an explicit unit target code and exact native chronology.
Global owner admission for the replacement, mixed-frame code retirement,
recursive child workspace, precision, the remaining output maps, and
the complete supplier are not proved here. No publication or kappa
change is claimed.
