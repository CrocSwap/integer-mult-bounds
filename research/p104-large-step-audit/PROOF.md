# Necessary contact-frame cost bound

This is a necessary-condition rejection at two specified rational C values for
the exact retained #7613 word/invoice. It supplies neither a new κ nor a universal
upper bound for multiplication.

## Model

Keep the scalar instructions (order, operands, coefficients), 400 main fields
and their endpoints, 1101 helpers, owned lifetimes/chart trajectories, and the
complete 17-call signed caller. Each public field follows an ascending nested
sequence of subspaces of F2^9. ADD/COPY require coframed operands; owned contacts
retain that owned frame. Arbitrary bases, new subspaces and additional public
moves between scalar contacts are permitted optimistically.

The first variant fixes all public endpoints and targets. The second frees each
helper's input/output subspace and credits its one target with rank
`dim(output)-dim(input)`. New fields, split targets, scalar rewrites, other callers,
nonmonotone paths and changed owned operators are outside this model.

Equal spans need not have equal ordered physical bases or phases. We do not
identify their physical operators: we drop extra basis/phase costs and legality
restrictions only when taking a lower bound on paid cost.

## Necessary corridors

Start at each fixed public input space (or {0} for a free helper). At a public
contact sum its predecessor lower spaces; at an owned contact use its pinned
space. This gives L. Starting at fixed outputs (or F2^9 for free helpers),
intersect successor upper spaces in reverse order and apply owned pins, giving U.
Induction shows every permitted contact space S satisfies L ⊆ S ⊆ U. SCALE is a
single-field contact. COPY still requires coframed operands and the declared
monotone frame trajectory, despite overwriting one scalar row.

The independent checker constructs a contact DAG instead of scanning instructions,
then applies topological forward/backward anchors. It checks source MOVE directions
and chart/lifetime states; both implementations obtain identical corridor widths.
Contradictory anchors and forced descending dimensions have rejecting controls.

## Dimension relaxation and coupled credit

Set H_C(r)=r^(1-C) for r>0 and H_C(0)=0. Since 0<C<1, subadditivity implies that
multiple ascending moves between contacts cost at least H_C of their total
dimension gap. Replacing them by one gap tariff is therefore optimistic.

For each field independently choose nondecreasing dimensions within [dim L,dim U].
This drops actual subspace containment and equality of the two chosen operand
frames at a common contact. Every legal program induces these independent paths,
whereas the converse is unnecessary. The sum of minimum path costs is consequently
a lower bound on native public paid cost.

For a free helper retain its start dimension in the DP state and minimize

    sum H_C(d_next-d_previous) - H_C(d_end-d_start).

Target subtraction is inside the same path optimization. Optimizing target and
cost separately or leaving old targets unchanged would not implement this bound.
Main fields have no subtraction. Zero-rank helper targets are allowed with zero
credit, making the relaxation more permissive.

The independent checker supplies concrete nonzero modular evaluations for every
public destination row except the sole exactly-zero interval. Both contacts
adjacent to that interval are pinned to frame115 even with free helpers, so the
gap already costs H_C(0)=0. Granting free known-zero relabeling there changes no
bound. Nonmonotone excursions leave the stated ascending-trajectory model.

## Complete invoice and arithmetic direction

Subtract 17 copies of the source public MOVE histogram from complete P. Its
nonnegative remainder P_fixed includes owned and caller costs. With fixed endpoints
keep T. With free helpers subtract 17 copies of their old target histogram from T,
giving T_fixed. The independent checker also separates owned and caller costs and
checks the remaining caller target histogram.

If K is the sum of minimum native costs (cost minus helper credit in the free
variant), every permitted candidate satisfies

    F(C) = target moment - paid moment
         <= moment(T_fixed,C) - moment(P_fixed,C) - 17 K.

The primary engine brackets H_C with directed integer arithmetic at 80 decimal
places, a range-reduced atanh logarithm and alternating exponential series. The
minimum of finite costs in [a_i,b_i] is enclosed by [min a_i,min b_i]. Target
subtraction reverses its interval endpoints. The final upper bound uses the
LOWER paid-cost bound.

The independent implementation uses bitset subspaces, a DAG, reverse endpoint-
conditioned DP and a separate positive-Taylor rational engine rounded outward to
40 decimal places. Its native-net and final-margin intervals must overlap the
primary intervals. Original source paths provide an available-path bound; tiny
ordinary/coupled paths are exhaustively enumerated. Exact fractions are retained.
All four upper margins are negative; rounded values appear in README.

No monotonicity of the optimized margin in C is invoked. The conclusion concerns
the named rational points, not every larger C. Changed scalar dependencies, owned
trajectories, callers, field counts and target interfaces need a new audit. The
separate BIT kernel and interleaving proof is in bit/PROOF.md.
