# Independent review of the complete structured S24 words

The 24 frozen words pass an independent reverse-column check. This covers
the original and scaled query gauges, both current providers, and six
complete words in each case. No material defect was found.

The scaled balanced backward word costs 91,208 real dyadic scalar
primitives. The scaled diagonal backward word costs 91,592. The scaled
normalized backward word costs 96,012. The scaled balanced forward word
costs 91,830. Each word retains 3,507 native children with rank mass
5,073. These are complete local word bills. They do not establish a
complete supplier or a change to the complete kappa bound.

## Frozen inputs and independent method

The producer freeze is
`new-core-transfer-20261017/structured-centres-transfer-20261018/FREEZE.json`,
with SHA-256
`e0cd1e8a7c99e7aecf663e735e56a5b7e98b4bff4f696e6b0339463ccad4c280`.
The original payload has decompressed SHA-256
`334ae2c970d591fd2999d4472dea2add296c978d5e7479b69210e4c3d05f76ff`.
The scaled payload has decompressed SHA-256
`ea140f936e4832d19db406bada5d4ab12ec6ea1dfc0d6e3e3a4c86991414ee2b`.
The checker verifies the complete producer manifest and the two source
manifests. The input record and its pinned phase bridge give the exact
input hashes.

The review does not import a producer module. It imports only the prior
independent ordered-polynomial and scalar-price functions in
`new-native-recipes-20261017/check_raw_selected.py`, with SHA-256
`c6ba81bd2e382e021b2c2ea853f75576dc101400a7cce3408003fe365c7e7bef`.
The new interpreter propagates each output column backward through the
literal program. It uses exact rational coefficients. Port operators
and native warp operators are free invertible letters. The interpreter
cancels adjacent inverse letters only. The two warp orientations use
disjoint alphabets. Thus this check makes no assumption that a port
operator commutes with a coordinate matrix or a warp.

Each complete check covers 640 input columns: 224 data fields, 408 helper
fields, and eight owned fields. It also includes all 91 private output
fields. The helper map is identity in the source's logical coordinates.
Its physical meaning uses the exact inherited residual wrappers. The
owned fields finish at zero in the initial frame. The private fields
finish at zero, and their actual allocation and return records close.
Owned admission is the permitted CLEAR operation; this review does not
claim to restore an arbitrary state that preceded owned admission.

## Actual response and physical representation

The checker reads the actual response and centre rows from the frozen
structured-centre payload. It verifies the six disjoint eight-port
minors, each with row Gram matrix `2I_8`. Their union is the 48-port
centre support. The first three minors define the selected set S of
24 ports. The other set U has 88 ports, including the complete 64-port
Hadamard block.

The response has the exact form

```text
E = E_64 direct-sum (-I_48 + K^T K/2),
E_64^2 = 4I_64,
K K^T = 12I_8.
```

The new core uses `J=-E`. The checker finds the actual forward transfer
sites and checks all 184 paired backward sites. It verifies that the
producer changed only the signs at those sites. Every native record is
unchanged. The complete replay proves the forward response `y += Jx`
and backward response `x -= Jy`. Here J is symmetric. No inverse-response
interpretation is used.

Write `Q_p` for the actual input-line operator on port p and
`q_p=Q_p^-1`. The physical input is `X_p=Q_p x_p`, `Y_p=y_p`.
After the common output FULL transform is removed, physical output is
`X_p=x'_p`, `Y_p=q_p y'_p`. The review inserts both conversions at their
actual positions. It checks every actual input line and output hole.
It also checks all scalar operation frames, nested native child ranks,
signed warp classes, helper endpoints, and private lifetimes.

Partition J into selected and ordinary blocks:

```text
J = [J_SS J_SU]
    [J_US H   ].
```

On the 24 ordinary centre ports,
`H=I-K_U^T K_U/2` and `H^-1=I-K_U^T K_U/4`.
On the other 64 ports these maps are `-E_64` and `-E_64/4`.
Let P be minus one on S and plus one on the ordinary centre ports.
The full data map and its inverse are

```text
A_48    = P - K^T K/4,
A_48^-1 = P + P K^T K P/4,
A_64    = -E_64/4,
A_64^-1 = -E_64.
```

The checker derives these maps from the actual source matrix and proves
both inverse orders for H, A, and the 64-port map.

## Complete maps

For logical input `x=(a,u)`, `y=(b,v)`, the raw backward word gives

```text
X_S = q_S b - J_SS Q_S a - J_SU v,
X_U = u - J_US Q_S a - H v,
Y_S = Q_S a,
Y_U = v.
```

The balanced backward word applies `H^-1` to this completed X_U.
The diagonal backward word then applies `X_S -= J_SU X_U`, with the
selected update included in the serial query word. Put
`L=diag(Q_S,I_U)` and `D=diag(q_S,-I_U)`. The complete diagonal result is

```text
X' = A L x + D y,
Y'_S = Q_S a,
Y'_U = v.
```

The normalized word appends the actual full A inverse. A single reverse
pass through this complete computation proves

```text
X'' = L x + A^-1 D y.
```

The checker separately extracts every original-X column. The block is
exactly L. It also verifies that each selected physical Y output is the
common FULL transform of the original a. It does not infer the complete
result from separate tests of the core and suffix.

The balanced forward word applies H to current ordinary Y, then uses
the actual selected input and output exchanges. Its complete result is

```text
X_S = a + q_S (J_SS q_S b + J_SU u),
X_U = u,
Y_S = b,
Y_U = H(u+v) + J_US q_S b.
```

The raw forward word has `Y_U=v+Hu+J_US q_S b`. The ordered Q factors
above are part of the tested maps. As a negative control, the checker
replaces `A^-1 D y` with `D A^-1 y`. All four complete normalized
computations reject that incorrect order.

## Coherent query restoration and scalar invoices

The reverse check inserts an output observable immediately before every
COPY into C0 and every CLEAR after the first owned admission. Every such
observable pulls back to zero. This proves that the query has been
restored before its storage is overwritten or its frame is reset.
The complete normalized word has 20 such observables. Each balanced or
diagonal backward word has ten. Each balanced forward word has nine.

A negative control adds an input-dependent residual to C0 immediately
before the final CLEAR in an ordinary inverse gauge. The complete
endpoint still passes when the zero observables are omitted. The same
mutated word fails when the zero observables are included. Thus this
review checks coherent restoration, not only the final endpoint.

The review reconstructs all sixteen four-port Hadamard kernels and all
32 physical exchanges from the packet's group partition. It compares
the complete literal word and its reversed scalar inverse. Both inverse
orders pass. Each word costs `16*76+32*26=2048`. The selected exchange
pass contains 24 literal exchanges and costs 624. No permutation in
these words is treated as free.

The seven scalar gauge words pass independently on all 640 columns:

| Gauge | Original | Scaled |
| --- | ---: | ---: |
| Ordinary Y | 3,286 | 3,222 |
| Ordinary inverse X | 3,384 | 3,224 |
| Fused inverse X | 3,960 | 3,608 |
| Data X | 4,740 | 4,420 |
| Data inverse X | 4,740 | 4,420 |
| Hadamard X | 2,048 | 2,048 |
| Hadamard inverse X | 2,048 | 2,048 |

The complete words have these independently counted bills:

| Complete word | Original | Scaled |
| --- | ---: | ---: |
| Raw backward | 87,984 | 87,984 |
| Balanced backward | 91,368 | 91,208 |
| Diagonal backward | 91,944 | 91,592 |
| Normalized backward | 96,684 | 96,012 |
| Raw forward | 88,608 | 88,608 |
| Balanced forward | 91,894 | 91,830 |

All entries include the full 87,360 scalar core, required selected
exchanges, gauges, owned admission, and owned frame resets. There is
no odd-division operation. Each word has native profile
`{1:2433,2:724,3:228,4:102,5:20}`, hence 3,507 children and rank mass
5,073. The scaled gauge changes do not alter that native profile.

## Phase dependency and limits

This review binds the entire canonical object to the compressed source
bytes of both previously reviewed phase providers. It also binds every
retained native record to the source clean word. It checks the literal
phase-review manifests and proof pins in `NATIVE-GEOMETRY-BRIDGE.json`.
The earlier independent review receipt has SHA-256
`924b898621dd25ea9d3330563fdf7acf6c3b63dc99526e15faaee682f4bdd94d`.
That review covers the actual orientation-specific warp tables,
ordinary adapters, residual wrappers, and endpoint frames. No new
native event is introduced by these 24 words. This review inherits
that exact phase result; it does not claim a second native phase sweep.

The result proves the complete local operations and their scalar bills.
It does not prove a route between successive supplier stages, access
to every later caller view, caller exterior phase closure, simultaneous
child hosting, a recursive error bound, or a complete supplier. The
local matrix inverse is not by itself a legal global decoder. The
complete kappa bound remains unchanged by this review.

## Executed checks

From the workspace root, these two commands passed:

```sh
python3 -I -B work/centre-encoding-campaign-20261014/lanes/new-native-recipes-20261017/structured-transfer-review-20261018/check.py --out work/centre-encoding-campaign-20261014/lanes/new-native-recipes-20261017/structured-transfer-review-20261018/verified-normal
python3 -I -B -O work/centre-encoding-campaign-20261014/lanes/new-native-recipes-20261017/structured-transfer-review-20261018/check.py --out work/centre-encoding-campaign-20261014/lanes/new-native-recipes-20261017/structured-transfer-review-20261018/verified-optimized
```

Each command ended with
`PASS_INDEPENDENT_STRUCTURED_S24_PHYSICAL_TRANSFER`. The two receipts
and the two input records are byte-identical. The receipt has SHA-256
`2bfa11248a1d1cc38a1b40803fac316e33f525ccf44f23f614cfbf73a805a800`.
The input record has SHA-256
`8dcc35233de782f18cdb189be996376ec872dc06f38ac0d9744a29043b6469ab`.
No optimized-mode assertion removal can skip a claim check: the checker
uses explicit exceptions for all requirements.

The code, this report, input records, and validation receipts were
prepared with AI assistance. Frozen source files were not changed.
No PR, push, commit, or publication was made.
