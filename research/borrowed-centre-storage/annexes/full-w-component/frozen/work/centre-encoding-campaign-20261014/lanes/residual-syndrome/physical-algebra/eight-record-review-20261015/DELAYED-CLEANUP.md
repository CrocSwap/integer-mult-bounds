# Delayed restoration of the eight dirty A records

The dirty eight-record repair has a later cleanup at a common completed
stage-2 cut. The cleanup restores all 224 original data values and all
eight arbitrary donor values. It uses the actual ordered stage-2 query.
It does not use a clean-record assumption.

There are two literal cleanup words. The first uses no work field and
has scalar allowance 25,152. The second reuses the one owned scratch
field from the local repair and has allowance 23,780. Each word has 224
complete stage-2 cover maps and no native child. The owner views that
put the donors at this cut have a separate cost and proof obligation.

This is a conditional construction. It does not supply a donor allocation
or prove the other data-bank outputs. It does not give a full supplier
or kappa bound. The literal words have producer checks; independent
review of this continuation is a separate step.

## Exact state after the local repair

Use the source sets A, T, U and the eight-record word reviewed in
`REVIEW.md`. Write z=(x,y) for the arbitrary original logical data and
h for the arbitrary eight record values in their F_L coordinates.
The dirty word gives

    d=z+E h,       r=h+G z.

The fixed selected error map is

    E_X,A h=-h,       E_Y,A h=h,
    E_X,T h=P0T ell0A h,   E_Y,T h=-P0T ell0A h,
    E_U h=0.

Define the off-A source alias V by

    (Vz)_U=y_U+x_U-K0U R0 x,
    (Vz)_T=y_T+x_T-P0T R0 x.

Then G=N2 V, with N2=P2A R2offA. All route order is retained. In
particular, N2 is the future stage-2 read, not the current stage-1 read.

The error map preserves every selected sum x_p+y_p and has R0 E_X=0.
It follows at once that V E=0 and hence G E=0. Therefore

    r-Gd=h,       d-E(r-Gd)=z.

These equations alone do not admit physical access. The next two
sections give the required cut and a literal access word.

## The completed cut and donor transport

Use the already reviewed full-W consumer, with W equal to all 112
ports. Its first physical bank swap parks the coded pair in pair 1
during the next F2 call. The complete pair-1 idle then advances the
parked fields to common frame F_U2. The second swap can occur after
the cleanup. The earlier consumer proof applies to arbitrary physical
parked fields, including z+E h. It does not require their logical
contents to be independent of a donor.

This continuation uses the full-W case. Parking only A union T is not
enough: the cleanup reads every off-A source value at the same cut.
The active F2 call must not consume the parked coded pair. Whole helper
jobs are permitted only through their complete arbitrary-input contract.
That contract has zero cross-dependence between the helper and active
outputs. No partial helper cut is used.

Each donor has two actual native intervals. Let T1 be its complete
physical map from capture to the post-B1 repair. Let T2 be its map from
that repair to cleanup. Let C0, C1, C2 be the separately priced boundary
views that align this donor at the three cuts. They may include a cover
isometry and exact phase adapters. The required identities are

    C1 T1 C0^-1 = F_U1 F_L^-1,
    C2 T2 C1^-1 = F_U2 F_U1^-1.

The same owner and the same chosen cover isometry must be used in both
identities. All translations and adapter phases are part of these
equalities. A final rank-16 match alone does not imply either equality.

For an arbitrary original physical donor a, put h=F_L^-1 C0 a. Capture
adds F_L u_A in the C0 view. At the repair, the C1 view gives
F_U1(h+u_A). The dirty local word then leaves F_U1(h+Gz). After the
second native interval, the C2 view gives F_U2(h+Gz). The cleanup below
returns F_U2 h. Removing C2 gives exactly T2 T1 a, the donor value that
its original jobs require. Its arbitrary original input is preserved.

No data, bridge, terminal, or other untracked donor use can occur before
cleanup. Complete helper jobs can occur if their exact endpoint maps
are included in T1 or T2. The donor cannot alias a live local data role
inside the same invocation. An actual allocation must check these
conditions. An unchanged strictly idle donor has T1=I and does not
satisfy the first identity without an additional nontrivial adapter.

If one fixed monomial donor map M is enough, the special case is
C0=C1=C2=M^-1. In a literal implementation, gather and return the eight
donors at each of the three cuts. This adds 48 donor-view maps per
replica. More general phase adapters have their own native invoice.
None of these donor costs is included in the cleanup counts below.

## A cleanup with no work field

At common F_U2 every constant scalar operation on the data fields is
legal. Let F0_content be the scalar content map of the old F0 call,
without its native frame change. It is an invertible map on arbitrary
X and Y values. Apply F0_content to d. Its off-A Y coordinates are Vd.

Gather those 104 Y fields and the eight A donors in the completed
stage-2 chart. Apply r-=N2 Y_offA directly. Return all 112 fields from
their views. Apply F0_content^-1 to the data. The donor is now h because
Vd=Vz. Finally apply d-=E h by scalar ADDs on A and T. This restores z.

The literal scalar source-code inverse is the pinned 970-event block
in the accepted repair. Its inverse implements the source part of
F0_content. The target part consists of the selected-sum updates and
ordinary target ADDs. Thus the construction uses no new matrix-inverse
oracle and no extra query buffer.

The exact actual coefficient counts are:

- each F0_content direction: scalar allowance 10,112;
- N2: 416 coefficients equal to plus or minus one half, allowance 4,160;
- minus E: 16 unit ADDs and 64 half ADDs, allowance 768.

The total is 25,152, with 224 stage-2 views and no new native child or
work field. The literal word is `DELAYED-CLEANUP-WORD.json`.

## A cheaper cleanup with the existing owned C

Only the off-A Y alias is needed. Keep X fixed and apply the shear

    Y_offA += X_offA-P0offA R0 X.

At each owner, the existing owned C forms one of the eight R0 X rows.
It then supplies that row's quarter responses to Y_offA. Clear C before
each row and return it to zero in the identity frame before the next
owner. Every source X and target Y has common frame F_U2 at this cut.

After this shear, perform the same completed-stage N2 read into the
donors. Undo the Y shear and apply minus E from the restored donors.
No data or donor is cleared. The only discarded input is the explicitly
owned scratch baseline, which may be arbitrary.

Each alias direction has 448 unit query ADDs, 416 quarter-response
ADDs, 104 unit Y ADDs, and nine owned clears. Its allowance is 9,426.
The whole cleanup has allowance

    2*9426+4160+768 = 23780.

It has the same 224 cover maps and zero native mass. The scratch is
reused from the local repair; it adds no physical role. The word is
`DELAYED-CLEANUP-ONE-C-WORD.json`. Its complete private sweep occurs
before or after the cover-map sweeps, not inside them.

## Exact verification and limits

The two checkers replay their complete literal words on all 224 data
columns and all eight arbitrary donor columns. They keep distinct
ordered owner routes distinct. They check the actual 73-axis stage-2
views and every ADD frame as an exact quadratic phase over Z/4Z.
All 480 unused borrowed helpers are preserved. The one-C check also
starts with an independent arbitrary owned scratch input and proves
zero output. There is no assumption of cover-constant data.

The zero-work checker separately verifies F0_content on all 224 input
columns. The one-C checker separately verifies the alias shear and its
inverse. Controls reject a missing second donor advance and show that
restoring a donor alone does not remove the data error E h.

Run from the workspace root:

```sh
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/residual-syndrome/physical-algebra/eight-record-review-20261015/check_delayed_cleanup.py
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/residual-syndrome/physical-algebra/eight-record-review-20261015/check_delayed_cleanup_one_c.py
```

The expected statuses are `PASS_CONDITIONAL_DELAYED_DIRTY_A_CLEANUP`
and `PASS_CONDITIONAL_ONE_C_DELAYED_CLEANUP`. Neither checker imports
or runs the portable producer. Both use the separate independent local
review algebra in this directory.

The reviewed consumer supplies the named parked-data history. A new
donor certificate must supply both cut identities, all owner exclusions,
and all new phase costs. Stream movement, rounding, guard bits, recursive
child hosting, and the other output-bank maps remain open. In particular,
the old common-frame precision table does not cover this later cleanup
or its arbitrary donor-frame conversions.

The portable-source-codes lane supplied the dirty-record algebra and
the suggestion to use only the Y alias. The retained QQ16 source and
common-frame work supplied the source code and the completed views.
This proof and its literal words were developed with substantial
OpenAI Codex assistance. No PR, push, or commit was made.
