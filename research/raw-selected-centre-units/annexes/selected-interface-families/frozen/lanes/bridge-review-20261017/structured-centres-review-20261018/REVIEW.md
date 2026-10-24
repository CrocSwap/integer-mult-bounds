# Independent review of the changed centre response

The partial and structured native responses pass this review. The changed
48-port response has six disjoint complete eight-port minors. Any three
of these minors give a dyadic 24/24 algebraic interface. All 20 choices
pass exact verification. The frozen common-frame scalar gauges implement
one such interface with a serial owned field.

This is a useful change of the response and query geometry. It is not a
complete supplier. The backward native word supplies the negative
transpose of the new response, not its inverse. The selected physical
boundary, routed transitions, 64-port gauge, source access at the required
cuts, terminal map, and complete recursive cost remain open.

## Inputs and independent method

The review pins the following two producer freezes:

```text
controller-followthrough-20261017/partial-orthogonal/FREEZE.json
b3938cd51d756df996f8421742c88bd96ab8fcddc7372c373c6fcbc5048d2bf1

controller-followthrough-20261017/structured-centres/FREEZE.json
5e762396d55ac47b34bbe60e30c62a429ddd6fc1f018cb4b4b94d3670d374a19
```

The checker verifies every artifact in both manifests. It also pins the
decompressed original clean native core and the structured payload:

```text
clean core:
a6c5dc63a47c1fdb0a97314a3b8541035f507beccb1029762f703039465187fa
structured response:
2b9de1454c2025ae4e230bd64de36b4f6c937628c63fc5afede6640dd3c0e1e1
```

`check_review.py` imports no producer checker. It uses exact fractions and
its own sparse ordered-word interpreter. It checks both orientations on
both providers for both responses: eight complete words. Each replay
uses 640 independent input columns. It includes all 408 arbitrary
borrowed helper fields and all eight owned input fields. Owned CLEARs
are explicit; all owned outputs are zero. The 91 private zero buffers
are allocated and returned under their zero contract.

Every scalar source and target must have the declared physical frame.
Every native, adapter, and private-buffer record equals its pinned source
record. Only the first descriptive phase label changes; the other phase
labels are unchanged. Physical warp operators are formal invertible
operators in this replay. The proved endpoint identity therefore holds
for their actual phase-correct realizations as well. This review inherits
the actual native map definitions from the pinned unchanged core. It does
not re-prove the implementation of each recursive child.

`replay_producers.py` also runs all five unchanged producer checkers. It
redirects their declared output files to this review directory. Every
output is byte-identical to its frozen producer output. The source files
remain unchanged. `PRODUCER-REPLAY.json` records the comparisons.

## Native operation and cost

For response matrix `E`, the forward word gives `Y += E X`. The backward
word gives `X -= E^T Y`. The checks include unchanged remaining data,
all helper columns, owned zero outputs, and endpoint frames.

| Response | Real scalar primitives per word | Native children | Native rank mass |
| --- | ---: | ---: | ---: |
| Partial orthogonal response | 86,664 | 3,507 | 5,073 |
| Structured centre response | 87,360 | 3,507 | 5,073 |

Both orientations and both providers have the same stated bill. The
exact rank profile is `{1:2433, 2:724, 3:228, 4:102, 5:20}`. The scalar
invoice is derived from each literal operation, not from its endpoint
matrix. These are local word bills, not a complete recursive supplier
bill or a kappa result.

## Response geometry and complete-minor interfaces

The partial response has a closed 64-port symmetric Hadamard block with
square `4I`. Its full determinant is `-2^88`. The structured response
keeps that block and changes the remaining 48 ports to

`E_48 = -I + K^T K/2`, with `K K^T = 12I_8`.

Every row of the actual `K` has twelve nonzero entries, all `1` or `-1`.
With `O=K^T K/12`, its centre eigenvalue is five and its other eigenvalues
are minus one. Thus the full determinant is `2^64 * 5^8`, and

`E^-1 = E_64/4 - I_48 + (6/5)O`.

Both inverse orders are checked with exact fractions. This direct inverse
requires division by five; the frozen native packet does not implement
that division or a full inverse word.

Each of the six actual complete minors has Gram `2I_8`. They partition
the 48 ports. The reviewer checks all 64 unions, rather than only the
producer's first `k` choices. For a union of `k` minors, the selected
and ordinary Grams are `2k I_8` and `2(6-k) I_8`.

For the negative response `J_48=-E_48`, let `P` be minus one on selected
ports and one on ordinary ports. The ordinary and data maps are

```text
H = I_U - K_U^T K_U/2,
H^-1 = I_U + K_U^T K_U/[2(k-5)],
A = P + K^T K/[2(k-5)],
A^-1 = P + P K^T K P/[2(k-1)].
```

All 20 choices with `k=3` have dyadic coefficients and satisfy both
inverse orders. They also have `K P K^T=0`. The resulting rank-one
data shears preserve every centre query, so the query can be removed
after its scatter without a second source copy.

The review derives the general complete-minor criterion in
`COMPLETE-MINOR-INTERFACES.md`. If there are `d` square minors with a
common Gram that is a positive power of two, an interior split is
dyadic exactly when `k-1` and `d-1-k` are powers of two. The balanced
query-preserving case requires `k=d/2`. This explains the distinction
between the original fourteen-minor family and the new six-minor family.
It applies only to unions of complete minors. Irregular port subsets
are outside its scope.

`check_interfaces.py` checks both singular endpoints on all six actual
minors. At `k=1`, the data map has rank 40 and an explicit eight-dimensional
kernel `range(P K^T)`. The source blocks satisfy `BD=5I_8`. Each complete
ordinary minor gives a dyadic-unit minor of `B`. The conditional
query-separation theorem therefore applies modulo five: if `M` and
`(MD)^-1` are dyadic, the stacked observation `[B;M]` has rank sixteen.
The checker supplies exact dyadic `MD=I` examples and verifies rank
sixteen over both the rationals and the field with five elements.
In contrast, `M=B/5` gives rank eight and `MD=I`. At `k=5`, the entire
eight-port ordinary map is zero. These are algebraic facts, not native
child lower bounds.

## Literal serial scalar gauges

The first frozen gauge packet has these independently checked costs:

| Gauge | Real scalar primitives | Native children |
| --- | ---: | ---: |
| `A` | 2,688 | 0 |
| `A^-1` | 2,688 | 0 |
| `H` | 1,236 | 0 |
| `H^-1` | 1,332 | 0 |

Every word acts correctly on all 112 arbitrary data columns. The other
ports are unchanged. The word starts with `C0=0`, forms eight serial
queries, and returns `C0` to zero. Each COPY targets that owned zero
field. An arbitrary borrowed field cannot replace this contract. A
separate CLEAR, if needed at entry, costs two real scalar primitives.
The preceding native word already establishes zero on its owned outputs.

For `H`, the updated query is minus twice the previous query. For
`H^-1`, it is minus one half of that query. The emitted word scales
`C0` by this factor before subtracting the updated query. This is why
the ordinary gauge restores its field despite changing the data.

The separate version-two packet preserves these maps and storage
contracts. It moves the common positive scatter magnitude to `C0`, so
each scatter uses signed unit ADDs. It then rescales `C0` to the updated
query before removal. The reviewer independently checks every operation,
all 112 input columns, zero restoration at every query, and the invoice.

| Version-two gauge | Query scale | Scale before removal | Real scalar primitives |
| --- | ---: | ---: | ---: |
| `A` | `1/4` | `4` | 2,368 |
| `A^-1` | `1/4` | `4` | 2,368 |
| `H` | `1/2` | `-4` | 1,172 |
| `H^-1` | `1/4` | `-2` | 1,172 |

There are no CLEARs in these four words. Every data word costs 290
primitives per query, plus 48 for the selected signs. Each ordinary
word costs 146 per query, plus four for the two negative first entries.
The separate freeze is `GAUGES-V2-FREEZE.json`, with hash
`deea4844f2327a73129c213df915819ec845fb9c97a30498d43f231a2267e733`.
The scale-placement idea is credited by the producer to the
new-core-transfer worker. The preceding frozen packet is unchanged.

These words require one common physical frame for all operands. Their
algebra does not authorize reads from a retired Y bank or a future X
bank. The signs needed to fit a complete supplier and the separate
64-port gauge also require their own literal construction and bill.

## Positive diagonal metric obstruction

The metric theorem is valid in the specified 42-dimensional real
symmetric family. The reviewer reconstructs the exact dyadic matrices
from the pinned directions and checks their rational independence. It
does not infer completeness of all native responses from a modular
search.

Let `E=sum_i w_i S_i` and let `D=diag(d_j)` with all `d_j>0`. The supplied
zero-diagonal witness `Y` gives an exact expression for `tr(Y E D E)`.
For each of the 64 small-block columns, the coefficient of `d_j` is

`(w_40 - 2w_41)^2/6 + 5w_41^2/24`.

For each of the other 48 columns, the coefficient is

`(5/3) sum_(i incident to j) c_i^2 w_(32+i)^2`,

where `c_0=c_5=2` and the other `c_i=-1`. Each centre occurs at twelve
columns. The reviewer expands each of these 112 polynomials directly
and checks every coefficient. The two-variable coefficient matrix is
positive definite, with determinant `5/144`.

If `E D E` is diagonal, the trace is zero. Strict positivity of all
`d_j` forces `w_32,...,w_41=0`. The remaining directions have support
only on the 64-port block, so `rank(E)<=64`. The bound is sharp because
the Hadamard response on that block is invertible.

This excludes full orthogonalization by invertible real diagonal input
and output gauges within this symmetric family: the row Gram of `A E B`
is `A E B^2 E A`, and `B^2` is positive diagonal. It does not exclude a
nonsymmetric reciprocal pair, a larger response family, changed native
words, or another representation. It does not conflict with the useful
structured response, whose dyadic gauges are not diagonal.

## Validation and remaining scope

Run from the workspace root:

```text
python3 -I -B -O work/centre-encoding-campaign-20261014/lanes/bridge-review-20261017/structured-centres-review-20261018/check_review.py
python3 -I -B -O work/centre-encoding-campaign-20261014/lanes/bridge-review-20261017/structured-centres-review-20261018/check_interfaces.py
python3 -I -B -O work/centre-encoding-campaign-20261014/lanes/bridge-review-20261017/structured-centres-review-20261018/replay_producers.py
```

The expected final markers are `PASS_INDEPENDENT_STRUCTURED_CENTRE_REVIEW`,
`PASS_ACTUAL_COMPLETE_MINOR_ENDPOINTS`, and `ALL_PRODUCER_OUTPUTS_BYTE_EQUAL`.
The independent checker uses explicit failures and does not depend on
Python assertions.

No material proof or implementation defect was found in the scoped
producer claims. The exact gauge entry contract is made explicit above.
No selected supplier, recursive precision proof, complete kappa
calculation, or full assembly was run. This review makes no claim that
each native centre capture needs rank eight; the new rank-seven capture
results are a separate construction question.

This is AI-assisted review. It builds on the controller-followthrough
producer, oblique-native response directions, the new-core-transfer
native core, and prior complete-minor and query-separation proofs from
this campaign. No PR, commit, push, or publication was made.
