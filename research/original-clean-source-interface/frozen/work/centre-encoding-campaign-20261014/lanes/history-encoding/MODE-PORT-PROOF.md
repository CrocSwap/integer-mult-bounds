# Eight promoted helper modes

The exact basis in `PROOF.md` gives a stronger interface than a retained
helper batch. Eight helper positions can become data wires. The other 472
helpers keep a local restoration contract. This note states the resulting
native primitive and a conditional owner patch for the actual selected
supplier. The global controller remains open.

## The local construction

Let `S` be the emitted helper basis. Its eight selected output coordinates
are `u=Hh`, and `SV` is the inclusion of those eight coordinates.
The selected positions are

    225, 226, 229, 232, 241, 242, 257, 258.

Take the physical inputs at those positions to be eight independent data
values `u`. The other 472 physical inputs are arbitrary borrowed helpers.
Before the forward word, apply `S^-1` at frame zero. Run the raw reflected
word from `PROOF.md`. After that word, apply `S` at the full nine-axis frame.
Thus the logical map is the conjugate by `S` of the raw helper map.
It is

    x' = x,
    y' = y + (I-P)x - Ku,
    u' = -u - 2Rx,
    h' = h,

where `P=R^T R/4`, `K=R^T/4`, and `h` now denotes only the 472 ordinary
helper coordinates. The full helper complement is restored before any
new unequal frame is introduced. No encoded complement must be held
between calls in this new interface.

For the backward word, use `S^T` at entry and `S^-T` at exit around the raw
backward reflected word. The logical map is

    x' = x - (I+P)y - 2R^T u,
    y' = y,
    u' = -u - Ry/4,
    h' = h.

These two scalar maps are inverse transposes. This can be proved by block
matrix multiplication; the checker also verifies the complete 704 by 704
identity. The phrase "inverse transpose" refers to logical coordinates
after removal of the stated native entry and exit frames. The physical
maps have their own frame operators.

## Native endpoint choices

All 122 helpers touched by `S` enter frame zero and leave the full frame.
This holds in both orientations. Hence the added basis gates are legal
and the common-frame lift of the original circuit remains valid.

For each promoted wire, choose an ordinary odd label `q` in the local
nine-axis space. Exclude the characteristic vector `511` when using the
standard orthonormal swap chart. The labels may repeat. They need not be
the centre normals. The centre normals give the E8 completion, but that
choice is not needed for the local circuit.

There are two useful native types:

| Type | Extra gate | Physical input frame | Physical output frame |
|---|---|---|---|
| Source | `C_q^-1` before the input basis | `C_q` | `F_L` |
| Target | `C_q^-1` after the output basis | `I` | `F_L C_q^-1` |

The same type may be used in both orientations. In particular, a target
bank may remain a target bank through the full sequence of calls. It need
not alternate between source and target growth types.

Each `C_q^-1` is a rank-one child with the exact compiler convention

    C_q^-1 = ((1-i)I + (1+i)X_q)/2.

Its two rank-zero wrappers are part of its implementation. The native
descent is after the complete output basis for the target type, so no
scalar ADD crosses unequal normal frames. For the source type, the
descent precedes the complete input basis, so all operands again have
frame zero. Every ordinary helper has the same native endpoint as before.

For example, write `T_p=F_L C_p^-1`. With permanent target modes, the
physical forward outputs are

    X'_p = T_p X_p,
    Y'_p = T_p [Y_p + sum_j (I-P)_(p,j) C_j^-1 X_j
                       - sum_k K_(p,k) U_k],
    U'_k = T_(q_k) [-U_k - 2 sum_j R_(k,j) C_j^-1 X_j].

The backward source and old-target endpoints are unchanged. Its mode
output is

    U'_k = T_(q_k) [-U_k - sum_j R_(k,j)Y_j/4].

These are local native identities for every positive tensor size and for
arbitrary spectator arrays. They follow from the legal scalar-frame lift
and the literal rank-one gates, including their phases.

## Local invoice and review

Each orientation has 232 data roles and 472 ordinary helper roles, with
the same total of 704 persistent registers. No private centre is used.
The paid profile is

    {1:2420, 2:418, 3:432, 4:142, 5:82}.

Its rank sum is 5,530. Relative to the original local word, eight rank-eight
centre children are removed and eight rank-one children are added.
The original eight cold helper positions each supplied nine productive
axes. Their new port roles supply eight, so productive growth falls by
eight per call. This loss must be included in a global invoice.

Each orientation has 20,389 scalar macros and a bound of 204,418
real-component scalar primitives. This number includes both basis changes.
It excludes the 16 new rank-zero native wrapper maps, address routing,
global mode preparation or closure, and the owner patch below. The
rank-zero maps do not add recursive children, but they have finite
implementation cost.

The exact emitted words are in `MODE-PORT-PROGRAMS.json.gz` for the dual
endpoint placement, and `TARGET-MODE-PORT-PROGRAMS.json.gz` for permanent
target modes. The mathematical opcode `native_C` states the literal
rank-one operation. It is not yet a registered supplier-emitter opcode.

The independent checker in the interface-proof lane uses a separate
transpose replay, checks all 704 columns and all 472 ordinary helper
outputs, checks chronological frames, and binds every new `C_q^-1` to an
exact native recipe. The receipts are `MODE-PORT-REVIEW.json` and
`TARGET-MODE-PORT-REVIEW.json` in that lane. The rank-one phase controls and
the full basis review are separate from the producer's checks.

## A conditional owner patch

The owner audit uses the selected 1094 replay archive with SHA-256

    f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6.

Its exact hosted template has 14,826 physical families, of which 14,336
are live data families. There are 144 supplier calls. In every call, all
eight promoted positions previously held width-nine helper jobs on live
data families. In total, 1,152 jobs on 973 distinct families are displaced.
The route kind is 3; the child and offset vary. `HOSTING-PATCH.json` retains
each actual owner and route. These old jobs cannot be dropped.

The following patch gives a concrete conditional bill:

1. Keep every original physical family and every original idle obligation.
2. Add eight mode families for each of the 16 replicas, or 128 families.
3. Use each mode family in all nine calls for its replica. Do not use it
   as an ordinary helper.
4. Replace each displaced helper job by a stand-alone rank-nine child on
   its original physical family and its original owner route.
5. Give each permanent target mode one final rank-one closure. For
   permanent source modes, use one initial rank-one preparation instead.

The backfill child can run at the same invocation as the old helper job:
its family has no other role in that invocation. Removing that owner from
the call therefore leaves the one-family-per-call rule intact. The child
performs the exact productive native operation that the old width-nine
helper would have performed. The remaining 472 helper owners are retained.

The new physical family count is 14,954. Per full cover class, the complete
conditional child-profile change is

    {1:+1280, 8:-1152, 9:+1152}.

Thus paid rank increases by 2,432, while productive output rank increases
by `128*73=9344`. This is a conditional cost calculation, not a kappa claim.
It assumes that the controller computes the required operation on every
old data family and on the 128 new modes. It also assumes exact compatible
stage routes and a common finite cover.

The choice `q_k=11` for all eight modes is legal locally and uses an
existing data-port route. It requires no new route generator. This choice
gives the emitted `REPEATED-TARGET-MODE-PROGRAMS.json.gz`. Whether its
changing-chart controller closes is a separate question.

## Open construction step

The primitive gives a dyadic dynamic centre state. The uniform target
version has, in local coordinates, a 120-dimensional target bank `(y,u)`
and a 112-dimensional source bank `x`. Its two update laws above couple
the normal modes to the old data. They must now be composed under the
actual stage-dependent port routes and native phase alignments.

The same-chart echo does not prove this composition. A two-call transfer
that cancels all arbitrary initial mode values would require equality of
the two routed decoder images. The actual routes do not have this
property. The new controller must use the mode dynamics, extra legal data
operations, or a changed sequence of calls. This obligation remains open;
no recursive supplier or complete multiplication bound is claimed here.
