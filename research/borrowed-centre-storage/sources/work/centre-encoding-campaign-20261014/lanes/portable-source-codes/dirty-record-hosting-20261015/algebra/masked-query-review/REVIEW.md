# Independent review of the masked current query

The masked unit is valid. Its selected query is R_U(x+y). It adds 64
half ADDs before the accepted UNIT-QUERY prefix. It changes the final
source correction to 384 unit ADDs and 32 half ADDs. The complete local
word has 26,587 events and scalar cost 213,466 in the inherited invoice.
The native word and its eight positive selected lines do not change.

The conditional F2 read also passes. On 360 independent data and donor
columns, the read gives the exact eight donor-erase rows from the frozen
dirty-record algebra. All other-pair and donor coefficients cancel.
This review does not admit the later B3 call or retire the mixed target
code. It does not extend the full-W global output result to this word.

The checker uses exact rational coefficients and ordered route words.
It imports no producer. It does not replay the complete 712-column native
word. The source pins and coverage are in CHECK.json. REVIEW.json binds
this note, the checker, and that receipt. The prior packets remain fixed.

The final masked-sum payload is pinned at
42a9d4bab68fe25f5592a4105b0b7cefa289187165f1d3dd0db6540afca98263.
The checker compares every stored matrix and all 26,587 events with its
independent reconstruction. This includes all retained native records.
The inherited UNIT-QUERY independent review is pinned at
58620b41e6b6aef4250bea4c4b4e66ab4c8fd03cd8bdd1f438a61377f297e756.

## The mask and its inverse

Let R:V->W. Let A be a set for which R_A is invertible. Put

    L_A = R_A pi_A,       P_A = iota_A R_A^-1,
    K_A = P_A,            K_offA = K-P_A,
    R_offA = R-L_A,       J = I-KR.

The accepted unit completion is

    T = (I-K_offA L_A)(I+P_A R_offA),
    T^-1 = (I-P_A R_offA)(I+K_offA L_A).

It satisfies L_A T=R and T-J=P_A(2R-L_A). The checker reconstructs both
matrices from the actual R. It checks both inverse orders and compares
the results with the frozen UNIT-QUERY payload.

Let V0=A union T_ports and U be its complement. Write

    L_V0 = R pi_V0,       R_U = R pi_U.

Suppose P_U has support in U and R_U P_U=I. Define N=P_U L_V0. The
disjoint supports give L_V0 P_U=0, so N^2=0. Thus

    B = I-N,             B^-1 = I+N,
    R B = R-R P_U L_V0 = R-L_V0 = R_U.

No input value is assumed to be zero. B preserves every V0 coordinate.
It adds a known combination of these values to U. The inverse subtracts
that change. Both operations preserve arbitrary data.

The section condition is also necessary for an invertible C with
L_A C=R_U. The exact supported section is pi_U C^-1 P_A:

    R_U pi_U C^-1 P_A=R_U C^-1 P_A=L_A P_A=I.

C^-1 P_A alone is a right inverse but need not have support in U. The
projection makes the support condition explicit. This is a clarification
of the source proof's necessity argument, not a failure of its theorem.

The actual selected sets and section are

    A = [0,7,20,27,36,46,57,111],
    T_ports = [21,37,47,76,81,87,92,110],
    H = [1,6,22,28,33,49,58,109].

All H ports lie in U. The exact matrix has R_H R_H^t=4I and determinant
-256. Therefore the section has rows R_p^t/4 on H and zero rows elsewhere.
The separate minor [1,2,3,4,5,6,8,12] has determinant -32. This second
minor confirms dyadic admission but is not used by the word.

B-I has 64 nonzero coefficients: forty -1/2 and twenty-four +1/2. Each
ADD reads a V0 field and writes an H field. Thus none of these writes
changes a later mask source. All 64 gates run on Y at its input I frame.
They use no scratch, native child, cover map, or extra private field.

## The source query can be chosen independently

Let D:V->W be any linear map with available coefficients. Define

    S_D = P_A(D-L_A J),       H_D = J+S_D.

Then S_D is supported on A and L_A H_D=D. Apply the following blocks:

1. Apply B to Y at I.
2. Apply the two accepted T factors to Y at I, in their existing order.
3. Run the complete accepted clean-J core.
4. Run the same eight positive C_q lines on Y_A.
5. Add S_D X to Y_A in the completed frame.

Before the final source correction, the logical target is Jx+TBy.
After the correction, the joint logical map is

    X_out=x,       Y_out=H_D x+T B y,
    L_A Y_out=D x+R_U y.

The target precode is T B. Its inverse is B^-1 T^-1. The joint data map
is invertible even if H_D is not a unit:

    x=X_out,
    y=B^-1 T^-1 (Y_out-H_D X_out).

For the final specialization D=R_U,

    H_D=T-P_A L_V0,
    S_D=P_A(2R_U+L_T),       L_T=R pi_T_ports,
    L_A Y_out=R_U(x+y).

The source correction has 384 coefficients of magnitude one and 32 of
magnitude one half. It has no coefficient from x_A. Its scalar cost is
384*8+32*10=3,392, equal to the old 424-unit-ADD correction. There are
eight fewer suffix events. The mask adds 64 events and cost 640. Thus
the total is 26,531-8+64=26,587 events and 212,826+640=213,466.

The unchanged complete native profile is inherited from UNIT-QUERY:
{1:2420,2:418,3:432,4:142,5:82}, with mass 5,530. The mask and replacement
suffix add no native child or native wrapper. The selected eight lines
already account for eight rank-one children and sixteen wrappers in that
profile. This review checks their exact retention; it does not rerun their
native kernels. No global read, hosting, bridge, or stream cost is added
to this local scalar total.

For D=0, the same identity gives a pure target query. Its source suffix
cost is 4,160 and its local scalar total is 214,234. This is a checked
matrix and count consequence. No separate literal D=0 packet is accepted.

The old core supplies the complete map on all 480 arbitrary helpers and
the eight owned scratch fields. The new gates touch only data. Thus this
composition uses that arbitrary-input contract without a new helper
baseline assumption. All eight owned private fields still end at zero.

## Conditional read after the selected-port F2 step

Use the routed operators from the frozen dirty algebra. For stage s, let
R_s be the sum of R_p D_(s,p), with the owner route on the right. Let
P_(s,S) have rows D_(s,p) R_p^t/4 on S. Stage 0 has the identity route.
Products below retain their displayed order.

The dirty repair state is d=z+E h, for z=(x,y), with

    d_X,A=x_A-h,             d_Y,A=y_A+h,
    d_X,T=x_T+J0 h,          d_Y,T=y_T-J0 h,
    d_X,U=x_U,               d_Y,U=y_U,
    J0=P_(0,T) R_(0,A).

In particular, R_0 d_X=R_0 x and d_X,T+d_Y,T=x_T+y_T.

At the first selected-port swap, let c be the other pair's X values.
The conditional F2 entry is

    l_V0=c_V0,       l_U=x_U+c_U,
    v_U=y_U,        v_V0 arbitrary.

The current source X output remains l. The other pair retains c_U on U
and the parked d values on V0. At the cut after its old idle, suppose
these X fields and the parked selected sums have common frame F_U2.
The eight selected Y_A query fields have that frame as well. This is
the physical read condition; this algebra check does not establish the
new global owner schedule.

The masked query is

    q=R_(2,U)(l_U+v_U).

From the current read fields form

    f=R_(0,U)(l_U-c_U)+R_(0,V0)d_X,V0=R_0 x.

Then the required query before the final A scatter is

    q - R_(2,U)c_U
      + R_(2,T)(d_X,T+d_Y,T)
      - R_(2,offA) P_(0,offA) f
      = R_(2,offA) y1_offA.

Here the source F0 identities give

    y1_U=y_U+x_U-P_(0,U)R_0 x,
    y1_T=x_T+y_T-P_(0,T)R_0 x.

Apply P_(2,A) to the displayed query. The result is exactly Gz, the
frozen eight-row donor erase query. The checker compares all coefficients
with FUTURE-READ-ROWS.json. There are 22,048 terms on 216 original source
columns, with route length at most two. The row digest is

    4f096fac6482c0473241af7cde1e9659431d78736c376b92bb00f83bf6de0e61.

The proof does not commute a stage-2 route through P_(0,offA) or R_0.
The checker reduces only adjacent equal involutions. It starts with
independent x, y, c, sixteen v_V0 values, and eight h values: 360 columns.
Every c, v_V0, and h coefficient cancels from the final read.

This read needs the eight completed query Y_A fields, current l_U, other
pair c_U, parked d_X,V0, and parked d_Y,T. It does not read any mixed-frame
F2 Y outside A. Each current route read still needs its exact cover-map
intertwiner in the common frame. This is an access condition, not a free
permutation claim.

The donor state h+Gz can now be reduced to h by this read. It uses no
destructive donor CLEAR. The final E correction uses the restored donor
values and touches only the parked selected data fields. In the stated
logical representation, all donor baselines and original data values are
restored. This is a local identity relative to the corresponding clean
selected-port construction. It does not identify that construction's
complete global output map.

## Order controls and verification limits

The checker rejects B T in place of T B. Since L_A B=L_A, the wrong
order gives L_A B T=R, so selected target inputs still occur in the query.
For example, target input port 0 has coefficient one in query row 0.
The checker also rejects the wrong mask sign, an omitted mask, an omitted
source correction, the old unmasked source correction, and missing terms
from the F2 compensation formula.

There is an exact obstruction to replacing the masked query with the
unmasked query while keeping only the other named FULL observations.
Change y_1 by an arbitrary field e and change the independent target
v_A by -P_(2,A) R_(2,{1}) e. The unmasked selected query does not change.
Neither the FULL source l nor the other named parked values change.
The required erase query changes by P_(2,A) R_(2,{1}) e, which is nonzero.
The checker verifies both the collision and this nonzero difference with
ordered route words. This obstruction concerns that observation set.

The new prefix is replayed on all 112 independent target inputs and an
arbitrary owned scratch input. The new suffix is replayed on all 224
independent data inputs at its stated completed frame. Both matrix
inverse orders and the full joint data inverse are checked. The retained
core and native lines are compared with the frozen predecessor.

Run from the repository root:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/portable-source-codes/dirty-record-hosting-20261015/algebra/masked-query-review/check_masked_query.py
```

Expected status: PASS_MASKED_QUERY_ALGEBRA_AND_CONDITIONAL_F2_READ.

The algebraic inverse does not make scalar ADDs legal across different
native frames. The output still has X:F, Y_A:F, and Y_offA:F C_q^-1.
This review does not run the complete 712-column source emitter, the
482-event global schedule, native kernel phases, or a finite-precision
implementation. It does not prove later B3 admission, retirement of T B,
new recursive child hosting, a complete supplier, or a kappa improvement.
The prior full-W all-output dirt receipt remains separate.
The source note's global diagnostic count comparisons are not a new
schedule certificate and are not accepted as one by this review.

The parent worker supplied the mask, both minor candidates, and the
independent source-query specialization. The earlier dirty-record work
supplied E and G. This independent check reconstructs the matrix and read
identities. OpenAI Codex was used under the user's research instructions.
