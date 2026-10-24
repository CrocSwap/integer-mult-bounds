# A source interface with free selected baselines

A larger selected target set can remove the odd source inverse that
occurs in the eight-row interface. The actual R has five disjoint
orthogonal minors whose union has 40 rows and contains both earlier
selected minors A and T. On the other 72 rows, the target becomes an
identity shear. The source can retain all 32 selected baseline fields
outside A and place any supplied systematic query in A.

This note proves the ordered source theorem and its complete affine
freedom. It checks the actual 40-row example and a supplied scalar word.
It does not give a complete nine-stage controller or supplier invoice.

## General selected-block theorem

Let J=I-KR. Divide the source and target coordinates into S and U.
Write K_S and K_U for K with rows outside the named set replaced by
zero. Suppose the r by r matrix

    D=I-RK_U

is a unit over the allowed coefficient ring. Define

    H=(I-K_U R)^-1=I+K_U D^-1 R.                  (1)

The ordered identities are

    RH=D^-1R,
    JH=I-K_S D^-1R.                               (2)

The first follows from I+(RK_U)D^-1=D^-1. The second follows by
writing J=(I-K_U R)-K_S R. The map H fixes every S coordinate.
Neither formula assumes that unrelated operators commute with D.

Every source map F with

    (JF)_U=I_U

has a unique factorization

    F=H E,                                        (3)

where E fixes the U coordinates pointwise. To prove this, put
E=H^-1F. The U rows of H^-1=I-K_U R are exactly the U rows of J.
The converse follows from (2). The source F is a unit if and only
if E is a unit, or equivalently if the selected block E_SS is a unit.
Thus (3) describes all source freedom under this target-row condition.
The selected map may contain arbitrary allowed linear reads from U.

The unit condition on D is equivalent to the unit condition on the
large block J_UU=I_U-K_(U)R_(U). The inverse in (1) supplies the exact
small-rank lowering. It is not a general large-matrix inverse oracle.

## Future query storage with selected baselines retained

Let A be a subset of S with r fields. Let B=S minus A. Suppose the
desired query row M has a unit restriction M_A. The systematic source
map E_M is

    (E_M y)_A=M_A^-1 M y,
    (E_M y)_B=y_B,
    (E_M y)_U=y_U.                                (4)

This is an elementary lower shear: its A-by-A block is I, and its
added read has no A columns. Its inverse changes the sign of that
added read. Apply E_M first, then H. The map F=H E_M preserves the
selected log and every B baseline because H fixes S. Moreover,

    (JF)_U=I_U.

The target correction C=JF-I is supported on S. The actual input-copy
theorem therefore gives at most |S| rank-one children when every
nonzero row of C has a legal common-Y read and the original X port
differs by its one native line. It still needs a cleared owned
accumulator and the complete scalar and address invoice.

For the routed future query M=R_t, the selected pivot is an explicit
unit: R_(t,A)=R_A(D_t)_A, up to the stated mode-coordinate gauges.
No inverse of R_tZ_s is involved. At the input of B_s, before both
positive charts s and t, E_(R_t) uses the future chart and H_s uses
the current chart. The accepted phase-corrected Y alignments support
both source codes there. A literal full-cover implementation must
still respect the global sweep order and every coefficient read.
This note claims the source algebra, not a new emitted global word.

## A 40-row actual instance

Use K=R^T/4 and RK=14I. The following five minors are disjoint:

    A=[0,7,20,27,36,46,57,111],
    T=[21,37,47,76,81,87,92,110],
    C=[1,6,22,28,33,49,58,109],
    E=[2,9,14,19,88,95,101,106],
    F=[3,8,15,18,89,94,102,105].

Each minor has Gram 4I. Let S be their union. Then

    RK_S=5I,   RK_U=9I,   D=-8I.

The source word is particularly simple:

    H=I-K_U R/8,
    H^-1=I-K_U R,
    RH=-R/8,
    JH=I+K_S R/8.                                 (5)

The 32 selected fields B=S minus A remain literal arbitrary source
baselines. They are not assumed zero and receive no source write.
For M=R, the A output is R_A^-1 R y. Thus the old T minor and the
other 24 selected fields can retain their old values while A stores
the complete original query.

The source H can use one private field. In component k, form R_k y
in that field and scatter -K_(U),k/8 times the result into U, then
clear. The relation R_i K_(U),j=9 delta_(i,j) means an earlier update
does not change any later query row. Its own already-read query can
change; no later step uses that original value. The inverse word uses
the coefficient -K_(U),k and has the same cross-component property.
This proves a literal serial source word on arbitrary source inputs.

For a general unit D, the r query values can instead be formed in r
owned private fields before any source write. Scatter K_U D^-1 times
those values, then clear. The original local interface has eight
private fields, so this does not by itself require a new field. Their
native frames and lifetime must still be bound in the emitted word.

## Same-chart scalar check and allowance

The checker uses E_R in (4), then the serial H word in (5). It tests
all 112 columns, both complete source inverse orders, every serial
query read, all 32 unchanged baseline coordinates, and the exact
identity target outside S. It forms C=JH E_R-I directly and checks
that all and only the 40 rows in S are used.

The scalar allowance is for this same-chart instance only. A future
chart adds real scalar and address work that is not included here.
The source E_R has 416 signed-half ADDs. The source H has 448 unit
query ADDs, 288 coefficient scatters of magnitude 1/32, and 16 CLEARs.
Their total scalar allowance is 12960 real primitives.

The input correction has 2120 coefficient ADDs. The eight A rows each
have one coefficient 1/8 and 52 coefficients of magnitude 5/8. Each
of the other 32 selected rows has one coefficient 1/4, 48 coefficients
of magnitude 1/8, and four of magnitude 1/16. Including 40 target ADDs
and 80 CLEARs, the input allowance is 32848. The total added scalar
allowance is 45808. Native calls and their address maps are separate:
40 rank-one children and 80 maps in the direct input-copy lowering.

The larger selected set buys independent baseline channels. It does
not prove that the controller can exploit them at a lower complete
cost. In particular, the source H is not the identity on U, and its
effect must be included in every later bank bridge and local call.

Run:

    python3 -I -B work/centre-encoding-campaign-20261014/lanes/cover-algebra/check_selected_block_normalization.py

Expected status: PASS_EXACT_SELECTED_BLOCK_SOURCE_NORMALIZATION.
The receipt gives the source and proof pins, the complete selected
sets, all scalar counts and the stated scope. There is no new native
phase replay, owner assignment, full controller or kappa claim.

The parent proposed selected-block normalization and future query
storage. This lane supplied its ordered classification and the simple
rank-eight H word. The controller lane supplied the common five-minor
witness, which this checker verifies independently. The controller and
selection lanes investigate its global use and
smaller selected sets. Research used OpenAI Codex under the user's
direction. New material uses Apache-2.0.
