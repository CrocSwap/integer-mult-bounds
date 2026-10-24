# Serial row factors on the complete native words

An existing owned C0 field gives cheaper balanced local words. The
forty-field family needs 171554 scalar primitives for the backward word
with diagonal borrowed response, and 171266 for its forward companion.
Both retain rank mass 5073 and add no recursive child or private field.
The original forty-field pivot words remain frozen as a separate
construction that does not need C0 at this boundary.

The eight-field family also has exact balanced local words if exact
division by three is admitted. Its backward words have sixteen real
division scans in addition to their old scalar bill. These scans are
listed separately; they are not counted as free dyadic operations.

## Scalar construction

Select one or five complete eight-port minors from
`BALANCED-FIVE-MINORS.md`. Let S be the selected set and U its complement.
Use the actual R, K=R^T/4, J=I-KR, and H=J_UU. Then

    R_U R_U^T = 4 lambda I,
    H = I-R_U^T R_U/4,
    H^-1 = I-R_U^T R_U/[4(lambda-1)].

For one minor, lambda=13 and each ordinary row has 52 signed unit
entries. For five minors, lambda=9 and each ordinary row has 36 signed
unit entries. Every full R row has 56 signed unit entries.

For each ordinary row r_j, form r_j u in C0. For H, divide this query by
4 and subtract r_j^T C0 from ordinary data. For H^-1, divide by
4(lambda-1), then use the same scatter. For the fused upper variant,
scatter the inverse query to the full R row, including selected data.
This also applies x_S += K_S R_U H^-1 x_U.

Different row updates do not change later row queries: their cross Gram
entries are zero. The selected scatter does not affect any query because
the queries read only U. Thus no saved query or restored source is
assumed. C0 is cleared once at the start and after each row, for nine
CLEARs total. It stays in the common frame between rows. Its last CLEAR
sets frame I. No borrowed field is cleared.

For five minors, the inverse divisor is 32. For one minor, it is 48:
the literal word divides by 16 and then performs exact division by 3.
Each complex division by 3 is two real scans. Positive query SCALEs and
negative ADDs avoid unnecessary negative SCALE cost.

| Factor | Eight selected fields | Forty selected fields |
| --- | ---: | ---: |
| H | 6706 | 4658 |
| H^-1 | 6738 + 16 division scans | 4706 |
| H^-1 with selected upper | 6994 + 16 division scans | 5986 |

The numbers are real scalar primitives, except the separately stated
division scans. Each factor uses existing C0 and zero new native children.

## Complete native integration

The backward words exchange selected physical X and Y, run the complete
new clean-J backward core, and apply the selected inverse factor to FULL
X. The forward word applies H to ordinary Y at I, exchanges selected
physical X and Y, runs the complete forward core, and exchanges selected
physical X and Y at exit.

The maps are the balanced equations in `BALANCED-FIVE-MINORS.md`, with
8 replaced by lambda-1 in the inverse coefficient. In particular, with
q=Q_S^-1 and c=R_S Q_S a+R_U u, the fused backward map is

    X_S' = q b-Q_S a-K_S c/(lambda-1),
    X_U' = u-v-K_U c/(lambda-1),
    Y_S' = Q_S a,
    Y_U' = v.

The forward map is

    X_S' = a+q J_SS q b+q J_SU u,
    X_U' = u,
    Y_S' = b,
    Y_U' = H(u+v)+J_US q b.

No Q is commuted through a dense matrix. Physical selected Y after
backward execution is F a. The original selected X information is in
productive output fields.

| Selected fields | Word | Old real scalar primitives | Additional real /3 scans |
| ---: | --- | ---: | ---: |
| 8 | Balanced backward | 171474 | 16 |
| 8 | Diagonal-borrowed backward | 171730 | 16 |
| 8 | Balanced forward | 171650 | 0 |
| 40 | Balanced backward | 170274 | 0 |
| 40 | Diagonal-borrowed backward | 171554 | 0 |
| 40 | Balanced forward | 171266 | 0 |

Every row has native profile `{1:2433,2:724,3:228,4:102,5:20}`, rank mass
5073, and 3507 children. Every row includes the full clean-J core, all
physical exchanges and factor operations, C0 preparation and restoration,
and the final 14-scalar cleanup of C1 through C7. No private field is
added. The eight-field and forty-field interfaces have different global
obligations; these local bills alone do not select a supplier.

The forty-field X response remains the dyadic unit from the earlier
proof. The eight-field X response still has an eight-dimensional kernel.
Division by three removes its ordinary-block restriction, not that
kernel. The complete data map remains invertible because selected Y
retains selected X.

## Verification and source comparison

`emit_serial_balanced.py` replays twelve complete native words: three
variants for two selected sets on both providers. It checks all 640
arbitrary input columns, including 408 arbitrary helpers and eight owned
fields. All helpers restore; all eight owned fields and all 91 private
zero buffers return to zero. Every source scalar frame, native frame
transition, warp order, and buffer lifetime is checked. All added factor
operands are checked in the actual common I or FULL boundary frame.

The exact replay treats an odd scan as division by 3 over the rational
coefficient field. The implementation and grid-height theorem for that
scan are a separate dependency in the independent review lane. This
packet does not replace that obligation with a favorable hypothetical
price. Complete recursive precision and scan cost remain separate.

The scalar factors were emitted independently from the actual R.
`compare_serial_sources.py` matches all forty-field events to the frozen
bridge-access scaled-row packet after the C0 role change. It also matches
the eight-field events to the independent review packet after seven
adjacent zero-CLEAR pairs are merged and actual endpoint frames are set.
The comparison receipt pins both sources. Both provider instances match.

Run with one process:

    python3 -I -B emit_serial_balanced.py
    python3 -I -B compare_serial_sources.py

The new source-core phase dependency is already independently reviewed,
including separate literal dual warp recipes. Independent review of this
integrated extension remains required. Inter-call views and operator
codes, exterior phase, owner hosting, recursive precision, and the full
supplier bill remain open.

Source credit for the native core and prior mechanisms is in
`CLEAN-J-TRANSFER.md` and `BALANCED-FIVE-MINORS.md`. The bridge-access lane
and independent review lane derived the serial scalar factors. The
bridge-access lane also reduced the CLEAR count. This lane emitted the
same factors from R, bound them to the actual native endpoints, and
checked the complete words. OpenAI Codex assisted the work. No PR, push, or publication commit
was made.
