# Independent review of the direct live-field eight-port suffix

The eight new native recipes and all four complete forward words pass
independent review. The balanced words cost 92,784 real dyadic scalar
primitives; the raw words cost 89,088. Each has 3,515 native children
with rank mass 5,081. The eight new rank-one calls and their sixteen
permutation wrappers are explicit. No material defect was found.

The complete X output is `(Qh,k)`. This holds for arbitrary current
selected Y input d. The physical selected Y output remains `q d`.
No clean-d assumption or old query is used.

## Frozen source and independent method

The producer freeze is
`new-core-transfer-20261017/forward-eight-phase-20261018/FREEZE.json`,
SHA-256
`af400bac97eeb1231b30e6ee74ccf7ffc818133c555d7232c2b60234dd04fc42`.
The final scaled payload has decompressed SHA-256
`f2369cd8928d3c6fe64ec87b18e5993db167ef362f326e173a752bbb8fe64de3`.
The checker validates every artifact in this freeze, the signed source
freeze, and the preceding physical-transfer freeze.

The complete-word interpreter comes from the frozen independent S24
review, SHA-256
`d55b2bcdce6764fb97d38bae212840047a739ecf20f17d180f3435e613e2df90`.
The preceding reduced-interface review freeze has SHA-256
`a5c4619ba3e3a627f136dadda4b3c2e94ca0653acc4943f66a9ceab595218f9e`.
The new spatial interpreter is separate code. It uses only integer
pairs for Gaussian integers, binary permutations, and explicit matrix
columns. It imports no producer code or Clifford interpreter.

The source native-child convention is pinned to
`interface-proof/verify_native_lift.py`, SHA-256
`087ad4cc683e5caf1f2a8cd62d5f65c9b4dde2636593b417f8f5099a29875c8b`.
The review reads that definition but does not import its interpreter.

## Exact live-field kernel and FULL placement

On the nine binary spatial coordinates, let T_v be translation by v.
The positive rank-one line operation is

```text
Q_v = ((1+i)I + (1-i)T_v)/2.
```

For each selected label v, the packet supplies two binary matrices.
The independent checker verifies their complete permutations on all
512 positions, verifies that they are mutual inverses, and verifies
that the left matrix sends the first coordinate vector to v. Both
wrappers have zero translation, zero quadratic phase, zero linear
phase, and zero global phase. The complete operation is

```text
P_G Q_e0 P_G^-1 = Q_v.
```

The selected port and label pairs are

| Port | Spatial label |
| --- | ---: |
| 0 | 11 |
| 7 | 21 |
| 15 | 265 |
| 36 | 146 |
| 42 | 322 |
| 46 | 140 |
| 79 | 502 |
| 89 | 445 |

These labels match both actual canonical providers. For every input
basis position z, the checker applies the right permutation, the child,
and the left permutation. The resulting column has numerator `1+i`
at z and numerator `1-i` at `z+v`, with denominator two. All other
entries are zero. All 4,096 recipe columns pass, including global phase.

FULL is the product of the nine coordinate Q operations. Its matrix
coefficient for displacement t is

```text
(1+i)^(9-|t|) (1-i)^|t| / 2^9.
```

The translations commute, so `Q_v FULL = FULL Q_v`. The checker also
computes both matrix products independently on every spatial input
column for all eight recipes. Each product has denominator `2^10`.
All 4,096 commutation columns pass with exact Gaussian-integer
numerators. This includes global phase, not only support or Pauli
action. Wrong inverse-line and wrong global-minus-sign controls reject.

Consequently, if a current live field contains `FULL w`, the emitted
call produces `FULL Q_v w`. The proof applies to every spatial vector
w. It does not require an owned field or a copy of the data. This is
the new direct-target binding; it is not inferred from the earlier
programs that restricted native line calls to C0.

The rank-one child uses the existing native interface contract: it
performs the exact spatial transform on the selected target and
preserves all other fields. The local program adds eight such calls.
Their recursive storage and global hosting are not supplied by the
matrix identity and remain separate obligations.

## Complete map and current-source use

Write the actual signed response as `J=[[L,B],[D,H]]`. Before the new
suffix, the balanced forward word has, after removal of the common
FULL factor,

```text
physical X_S = h + q(L q d + B k),
physical X_U = k,
physical Y_S = q d,
logical  Y_U = H(v+k) + D q d.
```

The suffix first applies positive Q to each selected X. This cancels
only the adjacent same-port product Qq. It then applies

```text
X_S <- X_S - L Y_S - B X_U.
```

The selected source is the actual physical Y value `q d`. The ordinary
source is the actual completed X value k. The resulting map is

```text
physical X_S = Q h,
physical X_U = k,
physical Y_S = q d,
logical  Y_U = H(v+k) + D q d.
```

For the raw word, only the last expression changes, to
`v+Hk+D q d`. The same suffix is valid. No Q is moved through L, B, D,
or H.

The independent reverse replay checks the complete emitted words with
all virtual physical endpoint conversions at their actual positions.
Port operators and native warps remain free ordered letters. All 640
input columns are checked, including all eight independent d columns,
408 arbitrary helper inputs, and eight owned inputs. All 91 private
outputs are zero. Helpers return to their source logical values under
the exact inherited physical wrappers. Owned outputs are zero in the
initial frame. These restoration claims use the stated native-child
contract for every abstract recursive call.

The checker binds every old core and boundary record to the previously
reviewed complete forward word. It checks every new call's target,
actual port label, positive sign, rank-one recipe, and FULL frame.
It also checks all scalar frames. The suffix touches only current data
fields; it uses no owned field, private field, or helper field.

For each complete word, three mutations reject: omit the positive
line, replace it with its inverse, or omit the row subtraction. Thus
the complete arbitrary-input cancellation is checked separately from
the spatial phase calculation.

## Scalar bill and retained native obligations

The selected rows have 160 half-coefficients: sixteen in L and 144 in
B. Their direct subtraction costs 1,600 real scalar primitives. The
optimized row word first multiplies the target by two, uses twenty
signed unit ADDs, then multiplies the target by one half. No target is
also a source: sources are selected Y and ordinary X. Each row costs
`2+20*8+2=164`, so all eight cost 1,312.

Both scalar words pass an independent check on all 640 input columns.
The exact scalar saving is 288. The review reconstructs their literal
events directly from the actual response rows.

| Complete word | Scalar primitives | Native rank mass | Native children |
| --- | ---: | ---: | ---: |
| Raw forward with suffix | 89,088 | 5,081 | 3,515 |
| Balanced forward with suffix | 92,784 | 5,081 | 3,515 |

Both rows apply to both providers. The native profile is
`2441H1+724H2+228H3+102H4+20H5`. The eight new H1 calls and sixteen pure
permutation wrappers are retained explicitly. There is no new scalar
preparation for these exact permutation recipes. The wrappers are not
included in the scalar primitive subtotal. Their descriptor and access
costs in a full supplier still need a legal schedule and an invoice.

The old native core phases inherit the exact previously reviewed
orientation-specific records and geometry. The new eight line kernels
and their FULL commutation are checked afresh here. No old source
phase claim is used as a substitute for that new boundary check.

## Limits

This review proves the direct live-field kernels, the complete local
maps, and their displayed local invoices. It does not prove a routed
transition between calls, all caller views, global child hosting,
wrapper descriptor costs, caller exterior phase closure, recursive
precision, a complete supplier, or a new complete kappa bound.

## Executed verification

From the workspace root, both commands passed:

```sh
python3 -I -B work/centre-encoding-campaign-20261014/lanes/new-native-recipes-20261017/forward-eight-review-20261018/check.py --out work/centre-encoding-campaign-20261014/lanes/new-native-recipes-20261017/forward-eight-review-20261018/final-normal
python3 -I -B -O work/centre-encoding-campaign-20261014/lanes/new-native-recipes-20261017/forward-eight-review-20261018/check.py --out work/centre-encoding-campaign-20261014/lanes/new-native-recipes-20261017/forward-eight-review-20261018/final-optimized
```

Both ended with `PASS_INDEPENDENT_DIRECT_LIVE_EIGHT_PHASE`. The two
receipts and the two input records are byte-identical. The receipt has
SHA-256
`888047aad482d43c6f83955061c97ee54503f2734de6f899e25c6dddc3259a8f`.
The input record has SHA-256
`d9e2f083c08eb92b3df6ceb688371c868ad137b0fd28caacc68721e7ff0502ab`.
Claim checks use explicit exceptions and remain active under `-O`.

The proof, checker, and review records use AI assistance. All frozen
inputs were preserved. No PR, push, commit, or publication was made.
