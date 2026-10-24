# Four-centre native words for a reciprocal response pair

The current native core admits two reciprocal rational responses. Each
response uses four of the original eight rank-eight centre calls. Each
word uses one owned field C0 in series and restores all 408 logical
helper inputs under the inherited native wrapper contract. Both current
providers pass the literal checks in both orientations.

The forward words cost 165594 dyadic real primitives. The backward words
cost 165618. Each word also uses eight complex divisions by 13, or
sixteen real division scans. Each word has 3511 native children and rank
mass 5105. The division scans are separate operations; they are not
included in the dyadic primitive count.

This is a local construction. The endpoints contain division by 13.
These words are not completed dyadic recursive providers. A global
controller, legal stage changes, child hosting, a final dyadic endpoint,
and a full precision and cost proof remain open. There is no change to
the selected kappa value. This packet requires independent review.

## Actual responses

Use the eight-row R in the pinned clean-core packet. Set

```text
K = R^T/4,       RK = 14 I_8,       J = I_112-KR,
P = diag(1,1,1,1,0,0,0,0),
M = (12/13)P,                    N = (12/13)(I_8-P),
E = J+KMR,                      G = J+KNR.
```

All indices use the row order of that source R. Thus E keeps centres
0,1,2,3, and G keeps centres 4,5,6,7. In port coordinates,

```text
E_ts = delta_ts - sum(j<4) R_jt R_js/52
                   - sum(j>=4) R_jt R_js/4.
```

The formula for G exchanges the two groups. Direct multiplication gives

```text
EG-I = K[12I-13(M+N)+14MN]R = 0.
GE-I = K[12I-13(M+N)+14NM]R = 0.
```

Here M+N=(12/13)I and MN=NM=0. The checker verifies RK=14I and both
full 112 by 112 inverse products with exact rational arithmetic. E and
G are symmetric for this coordinate P.

The separate
[rank theorem](../../root/RECIPROCAL-CENTRE-RANK-20261018.md) states the
optimal rank sum and the coefficient-ring obstruction for this response
family. This construction does not use a finite test as a proof of that
rank theorem. It implements the coordinate rank-four case directly.

## Centre and helper operations

At the centre cut, the source computes eight values

```text
c_j = R_j x + H_j h.
```

The actual centre fields are `[92,57,81,224,11,240,9,256]`. Their frames
are `[250,264,597,267,599,268,602,269]`, each of rank eight. The source
already has a native transition from each such frame to I and its
reverse. No new frame or native compiler is required.

With all centre blocks deleted, the forward core has the data response
Jx and helper term -KHh. Keeping the centre correction M gives
`Jx+KMRx-K(I-M)Hh`. The entrance correction is therefore
`Y += K(I-M)Hh`. All H helper roles and all Y roles are at I at this
entrance. The selected centre rows have weight 1/13; the other rows have
weight one. The backward entrance is its negative transpose,
`h -= H^T(I-M)^T K^T y`. Replace M by N for G.

The literal entrance uses C0 for each of the eight rows. In the forward
word it queries H_j h, divides C0 by 13 for a selected row, and scatters
through R_j^T/4. In the backward word it queries R_j y/4, divides for a
selected row, and scatters through -H_j^T. A CLEAR starts and ends each
row. No helper or data field is cleared.

For each selected forward centre, copy the actual centre field into C0
at its rank-eight frame. Use the exact original rank-eight transition to
I. Divide C0 by 13, multiply each original scatter coefficient by 12,
and clear C0 at I. Each original scatter coefficient is +1/4 or -1/4,
so the new dyadic scatter coefficient is +3 or -3.

For each selected backward centre, accumulate the original query in C0
at I with its coefficients multiplied by 12. Divide C0 by 13. Use the
exact original transition from I to the rank-eight frame. Apply the
original final ADD to the centre field, then clear C0 at I. An owned
CLEAR may set the empty field's frame; no nonzero value is relabelled.

The centre event's owned target changes from C_j to C0. Its old frame,
new frame, and rank do not change. Every occurrence has a binding to the
original event and the exact recipe for that frame pair. No centre
values need to persist between blocks.

## Complete local maps and frames

For T equal to E or G, the literal words have the maps

```text
forward:  (x,y,h) -> (x, y+T x, h),
backward: (x,y,h) -> (x-T^T y, y, h).
```

The backward word uses T^T. It does not use T^-1. Although T is symmetric
in this coordinate example, its reciprocal is the other response.

The producer propagates exact rational rows through every literal event.
Each row contains formal input fields and free words in the warp
operators. Only adjacent inverse letters cancel. Backward warp symbols
are separate from forward symbols. Thus the check assumes no extra
commutation between port operators or warps.

Each check covers all 632 live input fields and all eight arbitrary
owned input fields. All 408 helper outputs have their original logical
values, and no helper term remains in a data output. C0 ends at zero at
I. C1 through C7 retain their exact arbitrary input values at I, because
the word does not access them. If a caller requires all eight owned
outputs to be zero, seven further CLEARs cost fourteen dyadic real
primitives.

All 91 private buffers are allocated once and are zero at their actual
return. The checker checks every scalar frame, signed warp class,
ordinary adapter endpoint, residual adapter endpoint, private lifetime,
and final live and owned frame. Every ordinary native record has the
same value and order as in the clean source. The complete retained core,
including its scalar events, is copied without change.

The data roles also retain the source convention. Each X input has its
intrinsic port-line frame, each Y input has frame I, each X output has
FULL, and each Y output has its intrinsic port-hole frame. Let q be the
diagonal inverse-line operator. After removal of the common output F,
the physical data maps are

```text
C_F(T) = [[q, 0], [q T q, q]],
C_B(T) = [[q, -T^T], [0, q]].
```

These formulas keep the written order of q and T. The identity EG=I
holds in the shared logical chart. It does not by itself cancel q
factors between differently typed physical calls. That use needs a
controller and a legal chart transition.

## Exact native phases

The unchanged native records use the frozen current-core phase review.
That review covers the current geometry, the literal backward dual warp
recipes, endpoint adapters, and proper helper wrappers. Its receipt is
`../independent-review-20261017/NEW-CORE-NATIVE-REVIEW.json`, SHA256
`924b898621dd25ea9d3330563fdf7acf6c3b63dc99526e15faaee682f4bdd94d`.
This packet does not repeat that full sweep.

The producer does repeat all sixteen centre directions for each of the
two providers. It reads the pinned recipe and compares it with
`T_new T_old^-1` from the source frame vectors. The separate exact
interpreter checks all eighteen Pauli images and one complete Gaussian
state of dimension 512. The state check fixes the global phase. Every
new centre occurrence is bound to one of these thirty-two checks.

Multiplication by a real rational scalar commutes with a linear frame
operator on the same field. All new scalar operations occur at their
declared common frame. This justifies the divide and scatter placement;
it does not commute an index-dependent q through R, K, E, or G.

## Denominators and division scans

The literal replay checks the denominator of every coefficient in every
changed row at every prefix. All coefficients have denominator
`2^a 13^b` with b at most one. At each of the eight divisions, all
coefficients in the completed C0 query have b=0 before division. This
is an exact finite-circuit statement on all formal input columns. It
applies to arbitrary values, not to selected numerical test inputs.

Consequently one word adds at most one factor 13 relative to its input
grid. This includes arbitrary helper payloads. Exact physical frame
operators are Gaussian dyadic and do not add a factor 13 at their ideal
endpoints. The statement is about the emitted operation boundaries;
it does not supply a bound for the internals of recursively implemented
children or for roundoff error.

The fixed-odd-grid dependency is the frozen
[independent grid review](../bridge-review-20261017/odd-grid-a8-review-20261017/REVIEW.md).
Its freeze SHA256 is
`81ebbea971c0902a80479f9af4c82e72c660093c9f712b537690293aaaf21d60`.
That family includes division by 13. Each real scan uses the signed
carry recurrence

```text
a = (b-c) mod 2,       c' = (c+13a-b)/2,       0 <= c < 13.
```

The scan requires an exact divisible grid numerator and its signed end
condition. A common grid must supply the required factor 13 at each
complete query. Arbitrary finest-grid numerators are not an admissible
replacement for root inputs that were converted to that grid.

There are sixteen real scans per word. The inherited arithmetic-head
bound is at most `64(w_g+1)` for those scans, with descriptor work
separate. Here w_g is the full root-grid binary record width. Root
conversion must include every numeric stream, including arbitrary
borrowed fields.

A depth-only recursive odd-height bound requires every completed child
to have its exact Gaussian-dyadic endpoint on all arbitrary input
columns. E and G do not satisfy that condition individually. They can
be rational prefixes inside a future parent whose completed endpoint
is proved dyadic. The number of unfinished such prefixes per level,
root conversion, binary guard, descriptor work, and roundoff analysis
remain part of that future construction.

## Price and checks

| Word | Dyadic real primitives | Complex /13 | Real scans | Children | Rank mass |
| --- | ---: | ---: | ---: | ---: | ---: |
| E forward | 165594 | 8 | 16 | 3511 | 5105 |
| E backward | 165618 | 8 | 16 | 3511 | 5105 |
| G forward | 165594 | 8 | 16 | 3511 | 5105 |
| G backward | 165618 | 8 | 16 | 3511 | 5105 |

These counts hold for both providers. Every word has 23500 events. Its
native profile is `{1:2433,2:724,3:228,4:102,5:20,8:4}`. The original
clean profile has rank mass 5073; four retained centre calls add 32.
Each forward centre block costs 270 dyadic real primitives. Each
backward block costs 276. The weighted entrance has the same dyadic
bill as the old entrance and adds four of the eight divisions.

The checker rejects four changed constructions: omission of an entrance
division, a changed centre scatter sign, a wrong centre input frame, and
use of the same projection for both reciprocal responses. For each
provider it also rejects a changed centre global phase with the exact
state interpreter. The receipt records the failures.

The program is in
[RECIPROCAL-CENTRE-PROGRAMS.json.gz](producer-final/RECIPROCAL-CENTRE-PROGRAMS.json.gz).
Its decompressed SHA256 is
`8b3d6fbba7d7221a82927475bc38d479798f776fa27c22ef9a447c7a9a1d5013`.
The [receipt](producer-final/RECIPROCAL-CENTRE-RECEIPT.json) gives the
input pins, every division position, the per-word checks, and the native
recipe checks. `FREEZE.json` pins the final local packet. The earlier
`producer/` run is a development result, not the frozen receipt.

Run from the workspace root with a new output directory:

```sh
python3 -I -B work/centre-encoding-campaign-20261014/lanes/reciprocal-centre-20261018/emit_reciprocal_centres.py --out /tmp/reciprocal-centre-reproduction
```

The final status is `PASS_RECIPROCAL_CENTRE_NATIVE_PRODUCER`. The output
program bytes are deterministic. The receipt also records elapsed time.
The script requires at least 3 GiB free disk space and uses one process.

The current supplier and clean-core work supply the source R, H, native
chains, and endpoint conventions. The root lane derived the reciprocal
split and its rank classification. The oblique-native lane supplied the
centre-capture and weighted helper-correction plan. The new-native-recipes
lane implemented this packet. The earlier native and grid review lanes
supply the stated dependencies. This work used OpenAI Codex under the
user's direction. No PR, push, commit, or publication is authorized.
