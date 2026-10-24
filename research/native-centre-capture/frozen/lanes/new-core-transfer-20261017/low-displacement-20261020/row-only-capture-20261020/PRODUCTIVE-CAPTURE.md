# Sixteen centre rows in productive output fields

This packet forms the 16 centre rows of the actual rank16 response
in 16 existing target fields. It uses no owned field, private field,
or odd-division scan. The other 96 targets retain their original
output values and phases. The 112 source fields and all 416 arbitrary
helpers retain the original source contract.

The complete local profile is

```
1392 H1 + 64 H2 + 48 H3 + 16 H9.
```

It has 1,520 children and native mass 1,808. The scalar cost is
11,640 real primitives. There are 112 explicit input monomial views,
96 explicit output monomial views, and at most 3,040 native side
maps. These prices apply to each of the two actual providers.

This is an implemented local capture. It does not close the caller
or establish a kappa improvement. A selected FULL target has a
different phase at the next stage from an ordinary hole target.
That phase must be consumed or paid for.

## Reader and row code

Use the frozen rank16 response `E=I+UV`. Its centre factor is

```
VU = diag(-6 I8,-8 I8).
```

The selected physical ports, in centre order, are

```
P = [0,27,36,111,20,7,57,46,1,3,6,8,17,18,24,23].
```

The first eight ports form four complete physical pair-code
blocks: `(0,27)`, `(36,111)`, `(20,46)`, and `(7,57)`.
The other eight ports are in the small cliques. Put

```
L = V_P^-1 V,
H_c = diag(-5 I8,-7 I8).
```

The pinned row-capture algebra proves that `L_P=I16` and
`L E=H_c L`. Define the full row code `C` by

```
(Cz)_P = Lz,       (Cz)_U = z_U.
```

The matrix `C` is a dyadic shear. Its inverse changes the sign of
the off-pivot terms. Its precode and inverse each cost 1,760 scalar
primitives. It needs no clean input or scratch field.

The eight large rows of `L` have 21 nonzero coefficients: one
pivot coefficient 1 and 20 coefficients in `{1/2,-1/2}`.
The eight small rows have eight unit coefficients. The complete
output code is invertible, so using selected fields to carry the
centre rows does not discard their arbitrary input values.

## Complete physical contract

Let `F9` be the actual full spatial frame, and let `q_p=Q_p^-1`.
The input is

```
X_p = Q_p x_p,       Y_p = y_p.
```

All helper fields are arbitrary. The output is

```
X_p = F9 x_p                         for every p;
Y_p = F9 q_p (y+E x)_p               for p outside P;
Y_p = F9 [C(y+E x)]_p                for p in P.
```

The selected rows therefore contain
`F9(Ly+H_c Lx)`. Their borrowed baseline `Ly` is part of the
specified output. It is not assumed to vanish.

## Literal construction

First apply the pinned scalar shear `C` to the current target
bank in frame I. It writes only the 16 selected targets and reads
only ordinary target fields. The ordinary target inputs therefore
remain unchanged.

Next execute the original forward native word with all operations
whose target is a selected Y field removed. Both providers have
the same exact deletion ledger:

```
250 removed events = 128 H1 events + 122 scalar events.
```

The removed scalar events cost 928. No retained operation reads a
selected Y field. No source operation reads Y. The selected large
ports contain complete pair-code blocks, so this deletion does not
split an input or output pair transform. The retained word thus
gives the original 96 ordinary outputs and the original 112 source
outputs. The selected targets still contain `Ly` in frame I.

The final common-FULL query cut is after the entire retained sweep.
It is not before the target pair-code inverses. In the original
event list, event 2638 gives the last source its FULL frame, and
event 2639 completes the final other target. The emitter checks
that all 112 sources are FULL before it starts the late query.

At that cut, advance each selected target from I to FULL with one
explicit H9 call. Then add `(CE)_P x=H_c Lx` from the completed
FULL source bank into the selected FULL targets. Every ADD has
equal actual source and target frames.

For a large selected row, the query first doubles its current
target. It then adds the integer coefficients of twice the required
row, and finally divides the target by two. This retains any
arbitrary baseline exactly. The coefficients are in
`{5,-5,10,-10}`. The small rows use `{7,-7}` directly. These are
ordinary dyadic ADD instructions under the pinned scalar tariff.
There is no division by 5 or 7.

The full scalar bill is

```
precode C                  1760
retained original word     6456
selected FULL progress        0
late selected query        3424
total                     11640.
```

The original native mass was 1,792. The deletion removes 128 H1
calls and the replacement adds 16 H9 calls. Hence the new mass is
`1792-128+16*9=1808`. This mass difference does not by itself price
the complete recurrence: the 16 high-rank calls must be included
with their exact sizes.

## Boundary phases and verification

The 112 source input views are the exact pinned rank-zero maps
from physical `Q_p` to the source's canonical line frame.
The emitter compiles the 96 ordinary output views in the actual
outgoing direction, from the canonical hole to `F9 q_p`.
The selected FULL frame is checked to equal the actual `F9`,
including phase. No ordinary `q_p` is inserted on a selected
output. There is no implicit commutation of `Q` with `C` or `E`.

For each provider the new full-frame call, the FULL identity,
and all 96 ordinary output views receive exact Pauli and Gaussian
state checks. These are 196 fresh checks across the two providers.
All retained native recipes and the source entry views are exact
records from the pinned, independently reviewed rank16 source.

The full literal replay checks all 640 input columns, every source
and target frame at each ADD, every endpoint, and all 416 unchanged
helpers. It checks the serialized payload again. Omitting a precode
ADD is rejected by the borrowed-baseline columns. Omitting a late
query ADD is rejected by the source columns.

The maximum content prefix row one-norm is 132 and the additional
content binary height is one. This row-norm bound applies to the
linear content ledger at the completed primitive cuts. Under the
unitary native charts it is also a bound in the per-field Hilbert
norm. It does not replace an internal recursive-child guard or a
complete numerical precision invoice.

## General row replacement

The construction uses a property of the forward word, not a
special clean-input identity. Suppose a forward word has the
following properties:

1. Source progress is independent of the target bank and ends in
   one common frame.
2. A selected set of target fields is closed under all target
   pair transforms, and no retained operation reads those fields.
3. The selected row code is a unit that changes only selected
   rows and can be applied at the initial common target frame.

Delete the selected target paths, apply the row code to their
initial values, advance them to the final source frame, and add the
selected coded response rows there. The ordinary target outputs
stay unchanged. The selected targets carry the coded complete
output, including arbitrary target baselines. The complete cost
is the retained word plus the row code, the selected frame
advances, the late queries, and all boundary maps.

This gives a concrete family in which centre information can be
formed inside productive fields. It does not require a separate
centre bank. To reuse these fields, a caller must maintain the
reader and the exact phase of each selected field. The present
packet proves the formation step only.

## Credit and replay

The response and cyclic native paths come from the pinned
rank16 extension and the cyclic pair-flag work. The controller lane
supplied the normalized row code, its centre identity, and the two
scalar words. The bridge-access lane checked the deletion cut and
the physical pair closure. The native-review lane independently
checked the scalar rows and corrected a preliminary manual price
before this packet was frozen. This lane emits the complete native
capture and the outgoing views. AI assistance was used.

Normal and optimized Python runs use new output directories. They
must produce byte-identical payloads and receipts. The independent
native review is separate from these producer checks.
