# Signed-root nomination and its exact certification

## A finite construction, with separate nomination and admission

The contribution is an eight-triangle read schedule for the existing K-triangle
constructor. It does not introduce a new scalar primitive, change the factory,
or claim that fewer helpers necessarily improves the global moment bound.
The source is PR635 at `a6895a69f8ad98ab45777b03e9e6f48888c39f6f`.
The four negative schedules are preserved as `data/BASE-K492-SCHEDULE.json`.

For a full coordinate pair `p=(i,j)`, reflect coordinate `j` of each signed root.
Normalize each resulting root line by making its first nonzero coordinate
positive. This defines a permutation `sigma` and signs `epsilon_s` on the
constructor's 120 root lines. Apply the signed permutation to a source row
`sum_s a_s x_s` to obtain `sum_s a_s epsilon_s x_sigma(s)`.

For each negative read `(t, block, local_source)`, the nominator maps its target
to `sigma(t+8)-8` and finds the unique proportional reflected source row among
the positive triangle's required leavers in that block. The proportionality
test uses exact rational arithmetic. The nominator derives the complete
positive read multiset independently from `reqcoef`, `own_rows`, and the
packet program's face events. Each of the four positive triangles has 30
reads, and the nominated ordered list has exactly the required multiset.

This signed-row argument nominates an order. It alone does not establish
monotonicity of the binary frames. The unchanged full constructor checks
each resulting read against the actual current frames, requires every target
frame to remain in its specified hyperplane, and checks the exact clean
scalar identity and cleanup. The four new positive triangles pass those
checks together with the four inherited negative triangles.

Each selected triangle removes three packet copies. Thus the eight-triangle
base uses `R=504-3*8=480`. The constructor checks rank mass
`9*480+1992=6312` in its 120-port intermediate word. It then restricts the
eight isolated axis ports, leaving a 112-port raw word with mass **6176**.
Its exact paid profile is
`{1:2168,2:688,3:288,4:168,5:168,6:32,8:8}`.
The executable constructor and native audit, rather than a scalar helper
count alone, determine the profile used downstream.

## Composition with existing optimizations

The pinned PR558/568/571/575/583 shadow chains are rebuilt first. The unchanged
`build_port_stage.py` transfers their scalar and frame changes through the
504-to-480 register map. Each transferred intermediate word receives a fresh
native audit. Helpers removed by the triangle schedule have no image; this is
checked by the existing port constructor.

Each provider then applies 48 exact frame changes, with aggregate profile
delta `{1:-144,2:+144,3:-48}`. The scalar operations and helper responses stay
identical. The existing frame constructor rejects omission and over-promotion
of every change: 96 controls per provider. The unchanged HPE constructor
nominates and checks 22 commuting early inverse gates per provider.

The PR635 cold tails are mapped to the new numbering. Their forward
absorptions retain the original input-A anchors, including the order of
absorptions sharing an anchor. A target's last use is insufficient to pick
an anchor: the absorbed source can still be changing afterward. The unchanged
builder checks deadness against the remaining input gates and equality of
both operand frames at every absorption.

Some former low frames are no longer legal after the extra K reads. At each
tail operation, the discovery construction replaces its frame by the join
of the proposed frame and both operands' current frames. Terminal frames are
raised accordingly; ends that reach FULL are omitted. Both transported
providers retain 26 cold ends and two extra entering ends, in addition to the
22 HPE ends. In particular, this composition does not retain PR627's two
extra dimension-seven cold ends as low ends.

After this lower-frame tail, exact rational row and inverse-column checks
show that every declared ended helper is restored and isolated from all
non-target coordinates. Exact dyadic Gauss-Jordan elimination on the
remaining non-target, non-ended registers supplies the FULL remainder. The
native audit independently checks the resulting complete word, including
compensation and wrapper order, rather than trusting those discovery checks.
All 704 arbitrary-dirt columns, both reflected local programs and every
Clifford phase edge are then replayed.

## Global result and the unsuccessful record attempt

The included placement assigns all `72*480=34560` helpers to literal owners
under the unchanged time windows and distinct-owner rules. The independent
physical audit, finite invoice and rational moment engines admit the included
profile, giving conditional kappa `813551628351031/500000000000000000`.
This is below the pinned PR635 result. The larger terminal frames reduce the
stock of width-four residuals, and this placement leaves idle remainders
`{3:846,5:128,7:78,16:1,48:2230}`. Removing twelve helpers therefore does not
translate into a record bound with the transported cold endings.

The packing search used a restricted menu of capacity-filling patterns,
existing patterns and single-role patterns, with exact per-time flows and
bipartite edge colouring. Its floating objective and solver gap nominate a
placement only. They are not an exact lower bound over all possible owner
maps and do not establish an impossibility theorem for K480.

Fourteen intermediate subsets of the four positive triangles were also
screened. Their transported ends pass the exact row/column screen, but they
have not received this package's full native/global certification. No kappa
claim is made for those subsets. A productive next direction is to design
cold endings jointly with the eight-triangle read order, instead of carrying
over PR635's tails and raising their frames afterward.

## Controls and scope

The separate signed-schedule test reproduces the base and rejects four
damages for each positive triangle: omitted read, duplicate read, changed
source, and target from the negative triangle. These 16 checks supplement
the inherited empty-schedule/RAW504 equivalence checks, per-stage omission
controls, 46 cold-end controls per provider, native controls, wrapper and
phase checks, literal-owner controls and both global arithmetic engines.

The historical proof notes in `history/` retain attribution and explanations
of the inherited machinery; their fixture-specific counts do not describe
this package. All-size compilation, common-label/mutable-source realization,
whole-call hosting, precision and tape, analytic transfer, and bit H1-H5
remain assumptions. No unconditional lower-bound theorem or practical
multiplication speedup follows from this finite construction alone.

Prepared by Jeremy Diviney with substantial OpenAI Codex assistance.
