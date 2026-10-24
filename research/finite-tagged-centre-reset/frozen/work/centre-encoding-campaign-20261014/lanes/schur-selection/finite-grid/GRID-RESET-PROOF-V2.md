# A finite-grid backward centre reset, version 2

This version includes the independent return-format correction and the
fixed nonzero carrier witness. The previous proof and addenda stay
unchanged as review history. Use this version for the mathematical claim.

The redundant input code `(1+delta)` permits an exact nonlinear reset of
the eight backward centre carriers. It restores all 480 arbitrary helper
contents and gives the unit backward data map. It uses no new native
child. The price is extra accuracy on 132 old native children, of total
rank 156. This price exceeds the benefit of the eight removed rank-eight
centre children. This note gives a local mechanism and its precision
contract. It does not claim a supplier or kappa improvement.

All claims about exact restoration in the first five sections refer to
inputs on the declared finite grid. The later section on recursion
distinguishes this domain from the finer records of an approximate caller.

## Sources and literal interface

The raw word is `history-encoding/FULL-MODE-PROGRAMS.json.gz`, with
decompressed SHA-256
`f271842a741584389e166e700e262f161b0dd570ce8c7a540f2717e90ead5205`.
The matrix source is `circuit-interface/INTERFACE.json`, SHA-256
`5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3`.
The exact cut and suffix maps are also proved in
`history-encoding/CENTRE-RESET-INTERFACE.md` and `CROSS-CUT-PROOF.md`.

Run backward events 0 through 12994. Omit the eight signs at events
12996 through 13003. Resume the suffix at event 13004. The centre fields
are `[92,57,81,224,11,240,9,256]`, in native frames 415 through 422.
The initial mode fields are `[225,226,229,232,241,242,257,258]`.

Write `R` for the actual 8 by 112 matrix and `K=R^T/4`. Before the signs,
the logical centre value is

    w_k = u_k + R_k y/4.

It has no initial X coefficient or other helper coefficient. If this
value is replaced by `v_k`, the unchanged positive suffix gives

    y_out = y,
    x_out = x-y+R^T(v-u),
    u_out = v.

The other 472 helper contents are restored. The inherited native entry
and exit frames remain part of this statement. In particular, logical
restoration does not assert that an old helper job has been removed.

Let `B_k` denote the physical frame of centre k. The required physical
replacement is `B_k u_k`. The reset below acts on physical coefficients.
It does not move a scalar matrix through unequal native frames.

## A scalar grid lemma

Use the maximum absolute real or imaginary component as the norm. Let
`h,q` belong to `Delta Z[i]`. Let `delta` be a positive power of two.
Suppose

    |delta q| <= Delta/16,
    |e| <= delta Delta/16,
    0 < delta <= 1.

Let `Round_Delta` round each component to the nearest grid point. From
the observed value `z=h+(1+delta)q+e`, compute

    b = Round_Delta(z),
    q_hat = Round_Delta((z-b)/delta),
    h_hat = b-q_hat.

Then `b=h+q`, `q_hat=q`, and `h_hat=h`. Indeed, the first perturbation
has magnitude at most `Delta/8`, and the second has magnitude at most
`Delta/16`. Neither rounding reaches a tie. The same proof works when
the grid for the second rounding is coarser, provided it contains q.

Only the coarse bound `|e|<=Delta/16` is needed to recover `h+q`.
It does not suffice to recover h. The division by delta amplifies e.
An exact rational negative control in the checker demonstrates this
distinction. No claim that a native approximation error lies on the
coarse grid is used.

## The complete local chronology

First tag both data banks by `(1+delta)`, and leave all 480 helper inputs
unchanged. Run the raw prefix. Its physical value in any field is

    z = h+(1+delta)q,

where h and q are the prefix responses to helper and data inputs.
At the cut, round every non-centre field to its untagged value `h+q`.
At each centre use the grid lemma to retain h alone. The exact cut
state is now the ordinary untagged prefix state, with its eight centre
values replaced by `B_k u_k`. Run the positive suffix. It gives the
unit backward data map and restores every helper content. A final
rounding to a known output grid removes the suffix approximation error.
There is no division by delta at the final data outputs.

Use one existing owned private centre field `C0` for all input tags
and all centre resets. Clear it once at entry. To tag one data field L,
use the following gates in L's current frame:

    COPY L to C0; SCALE C0 by delta; ADD C0 into L; CLEAR C0.

This avoids an inadmissible SCALE by the non-unit `1+delta`. To decode
one centre L, use these gates in its current centre frame:

    COPY L to C0;
    ROUND C0 to Delta;
    ADD -C0 into L;
    SCALE L by delta^-1;
    ROUND L to Delta;
    SCALE L by -1;
    ADD C0 into L;
    CLEAR C0.

All SCALE factors are dyadic units. Every binary access has a common
actual frame. COPY starts with a zero target. CLEAR resets the private
frame because zero belongs to every frame. The word does not erase an
arbitrary borrowed helper. The entry CLEAR acts on owned private space.
No large `delta^-1 b` intermediate is formed: the scaled residue has
size comparable to q.

The literal schedule is `REDUNDANT-GRID-WORD.json.gz`. Its source event
ranges are half-open. Its new operation counts are:

| Operation | Complex field passes |
| --- | ---: |
| COPY | 232 |
| SCALE by a dyadic unit | 240 |
| ADD with coefficient 1 or -1 | 240 |
| CLEAR | 233 |
| ROUND to a declared binary grid | 1416 |
| Total upper bound | 2361 |

The total includes all 224 input tags, 696 ordinary cut roundings,
eight centre decoders, and 704 output roundings. Each pass costs linear
time in the coefficient record length. Shifts by `O(t+e)` bits are one
scan, not that many repeated passes. Rounding uses sign, discarded
bits, and a carry in each signed record. One coefficient buffer and
the existing owned field suffice. These are explicit new stream
operations. Their old finite scalar coefficient is not asserted to
remain unchanged.

## Grids, growth, and error margins

Here is one conservative bound. It is intended to prove the leading
precision coefficient, not to optimize the finite cutoff. Let the
tensor width be lambda, and let every initial physical component lie
in `2^-g Z` with magnitude at most one. Put

    H = 5522 lambda + 16339,
    G = 5522 lambda + 49012,
    L = 2^G,
    Delta = 2^(-g-H),
    delta = 2^(-g-H-G-4),
    Gamma = 2^(-g-2H).

The exact scalar denominator exponents in the raw word sum to 16339.
The checker bounds the product of scalar row norms by `2^49012`.
The retained native rank mass is 5522. A raw native C tensor on
`r lambda` axes has Gaussian dyadic denominator exponent at most
`r lambda` and real component row norm at most `2^(r lambda)`.
Its inherited monomial wrappers are permutations with Gaussian unit
phases. These facts are the retained native recipe premise, not a new
phase claim from the scalar replay. They imply the displayed H and G
bounds for each segment of the local word. The source recipe pin is
recorded in `interface-proof/FULL-MODE-PORT-REVIEW.json`.

Thus h and q at the cut belong to `Delta Z[i]`, and `|q|<=L`.
The tag has magnitude at most `Delta/16`. After the centre replacement,
the exact cut components still have magnitude at most L and belong to
the same grid. The suffix output belongs to `Gamma Z[i]`, with magnitude
at most `L^2`. This coarser grid is valid without an assumption that
every input starts in frame zero.

Suppose `g<=t+B e`, where B is a fixed nonnegative integer, and lambda
is at most e. Let the requested relative error at native child j be

    2^(-a_j t-P),       a_j in {1,2},

where

    P = 2B e + 2H + 4G + 32.

Use at least `2t+P` fractional bits for parent conversion and scalar
rounding. Include the child computation and its normalized input
conversion in its complete relative error contract. Parent return-grid
rounding is a separate absolute error insertion of size at most
`2^(-2t-P)`, even for an ordinary-accuracy child. A tiny child input can
require more fractional bits than the parent retains. The child uses
its own normalized stream; its return is unscaled and rounded directly
to the parent's grid. No parked ancestor record is widened.

Grant one insertion to each of 25457 source events, one extra return
insertion to each of 3486 native climbs, and one to each of 2361 new
passes. This gives 31304 sites, less than `2^16`. Exact maps and exact
rounding branches need no error insertion, so this is an upper bound.
All parent scalar and return conversions have the displayed fine
absolute error bound. The local theorem starts on its declared input
grid. Conversion of a finer approximate caller to that coarse grid is
not in this local fine-error budget; it is a separate node obligation
in the recursion section.

The finite perturbation bound is direct. Before the cut, all actual
native inputs have norm at most `4L`, by induction from the usual
sum of inserted errors. A single insertion has downstream gain at
most L. Therefore the total coarse cut error is at most

    4 * 2^16 * L^2 * 2^(-t-P) < Delta/16.

For a selected centre, give `a_j=2` precisely to every native child
with a nonzero linear response at that centre. Every other native
error has zero response there. This remains true for an error that
depends on earlier approximations: write each call's error as an
additive output vector, then use the exact retained suffix. Parent
scalar errors use the fine grid. Consequently the selected centre
error is at most

    4 * 2^16 * L^2 * 2^(-2t-P) < delta Delta/16.

Both inequalities follow by substituting `g<=t+B e` and P. The coarse
cut margin is at least a factor `2^(B e+H+2G+10)`. The fine centre
margin is at least a factor `2^(G+6)`. The coarse cut rounds and centre
decoders are therefore exact. Their errors do not enter the suffix.

In the suffix, actual inputs have norm at most `4L^2`. The total output
error is at most

    4 * 2^16 * L^3 * 2^(-t-P) < Gamma/16.

The suffix margin is at least a factor `2^(B e+G+10)`, so the final
grid rounding is exact. This also closes the induction used for the
input norm bounds. No estimate uses the number of coefficients in the
row stream as a multiplier.

The parent format has `2t+O(e)` fractional bits and `O(e)` magnitude
bits. Input packing fits this format because its exact denominator
exponent is at most `2g+H+G+4`. All stated operations fit a fixed
multiple of `t+e` bits. The native recipe maps do not add address axes.

## Which children need the fine request

The exact reverse response to all eight centre outputs contains 132
native children. Their profile is 124 of rank one and eight of rank
four, of total rank 156. Every input has a nonzero data part and a
nonzero helper part. Every other old child receives ordinary accuracy.
The count includes old errors that later cancel in some fields; only
an exact zero at all selected centres removes a child from the fine set.

The producer checks all 704 input columns, all 480 helper outputs,
the source rows at the eight cut fields, and this reverse response.
The temporal lane reproduced the profile independently. Additional
pure-row resets can break cancellations. They require a new response
calculation. Their cost cannot be inferred by deleting ancestors from
this count. The finite reset-policy study is separate.

This assignment is sufficient under the stated relative-error contract.
It is not a lower bound for a child implementation with correlated
lattice errors. Such a new contract would need its own proof.

## Why divisibility does not shorten these queries

The actual column set

    A = [0,7,20,27,36,46,57,111]

satisfies `R_A R_A^T=4I`. Let e0 be a coordinate vector in the payload
coefficient space and set `h0=e0/8`. Choose eight independent input-grid
scalars s_k in `[-1/8,1/8]`. Put `v_k=s_k e0`, set `y_A=R_A^T v`,
set the other source entries to zero, and set `u_k=h0-v_k`. All input
components have magnitude at most one half. The query is `Ry/4=v`,
and every untagged centre is the same fixed nonzero h0.

The tagged physical centre is

    z_k(s_k) = (1/8+delta s_k) B_k e0.

No frame eigenvector premise is used. For `0<delta<=1/2`, the scalar
multiplier lies between `1/16` and `3/16`. Adjacent query values spaced
by `2^-g` therefore have relative carrier separation between
`(16/3)delta 2^-g` and `16 delta 2^-g`. The same nonzero vector
`B_k e0` cancels from this ratio. An exact local grid decoder cannot
accept arbitrary relative noise beyond half an adjacent separation,
because two different required results would then share an observation.

For `g=t+O(e)` and `delta=2^(-t-O(e))`, this resolution has two leading
copies of t, even after normalization of the carrier. If only absolute
accuracy `2^-t` is needed at the decoded output, space the query values
by `2^-t 2^O(e)` instead. The inverse frame norm supplies a sufficient
factor independent of t. The leading coefficient is unchanged when t
exceeds the dimension guard.

This is a local packed-carrier resolution statement. It does not bound
an algorithm that reads other data fields, changes the code, or uses a
special native error contract. It also does not assign a native cost
to an arbitrary payload query. Each native charge still needs the
separate input and response analysis. The fixed factor one quarter
and fixed binary divisibility in R do not remove a positive fraction
of the t source bits.

## Recursion and the complete bill

An approximate caller can have finer input records than the grid above.
It must first normalize its complete principal stream, including every
row that a child can use as borrowed space. Before a local tagged word,
round its complete role inputs to a declared `g=t+O(e)` grid and charge
that conversion in the finite parent error bound. The exact local helper
restoration statement then applies to these grid inputs. It does not
state exact restoration of a finer pre-conversion helper record.

The selected node has a fixed number of such operations. Its complete
perturbation proof can pay their ordinary errors with a larger fixed
`O(e)` accuracy allowance. Exact restoration of the required public
raw endpoint follows only after the whole node endpoint is proved and
rounded to its known public grid. One cannot infer that endpoint from
this local word alone.

The row and record argument is supplied by the independently reviewed
`temporal-reuse/HETEROGENEOUS-PRECISION-CONTRACT.md`. Extend its finite
word premise here by the stable rounding cells just proved. Each cell
has the indicated exact derivative; after the cut all errors have been
removed. Write the child request as

    t_j = a_j t + A e,       e_j = r_j floor(e/73).

Choose `c>=A/(1-48/73)` and put `w(e,t)=t+c e`. Then
`w(e_j,t_j)<=a_j w(e,t)`. Each child has one 14336th of the parent
coefficient count. The precision moment is therefore

    (1/14336) sum_j a_j (r_j/73)^sigma.

The proof covers repeated precision doublings down a recursive path.
Parked ancestor streams keep their own formats. The simultaneous space
factor from this format rule is at most `14336/(14336-2)`. All new scans,
descriptors, row staging, and finite cutoff constants still need a full
invoice when a candidate profile meets the required moment.

For the all-eight local code, the extra weighted rank at sigma one is
156 while the removed private-centre rank is 64. With 64 backward calls,
the change is `64*(156-64)=5888`. The historical complete rank deficit
is 5120, so this candidate exceeds the total dimension by 768 at sigma
one. This is already a negative result before the new finite scan cost.
The portable lane supplies the separate exact historical comparison.

## Reproduction and scope

Run:

    python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/schur-selection/finite-grid/check_redundant_grid.py

Expected status: `PASS_EXACT_REDUNDANT_GRID_CUT_AND_NATIVE_CONE`.
The receipt is `REDUNDANT-GRID-CHECK.json`. It includes 3267 exact
scalar decoder cases, two failure controls, the actual matrix minor,
the complete native cone, the local endpoint, and the new operation
counts. The scalar replay inherits the native phase recipes; it does
not independently replay every monomial wrapper. A separate independent
review is required before this proof is treated as established.

The earlier `BACKWARD-GRID-WORD.json.gz` uses the different code
`delta data` and a final division by delta. Its fine native profile is
`{1:581,2:108,3:41,4:30}`, of rank 1040. That negative invoice is not
the invoice for the redundant code proved here.

This work uses the source rows and cut response from the history lane,
the independent error-cone and record work from the temporal lane,
the actual centre-frame lattice check from the package reviewer, and
the complete-profile arithmetic from the portable source-code lane.
The package reviewer found the parent return-grid issue corrected in
this version. OpenAI Codex supplied substantial AI assistance. Publication is on hold.
Before any future PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
