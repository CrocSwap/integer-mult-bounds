# Eight centres on a 48-port native response

The emitted native response `E` is symmetric. On 64 ports it is the
Hadamard response from `../partial-orthogonal/PARTIAL-ORTHOGONAL.md`. On
the other 48 ports it has the form

`E_48 = -I + K^T K/2`, with `K K^T = 12I_8`.

Each row of `K` has 12 entries, all equal to `1` or `-1`. Thus the inverse
defect has eight centres, all supported on those 48 ports. The other 64
ports need no centre correction in the local inverse.

Both native words pass the full ordered replay on both providers. Each
word costs 87,360 real scalar primitives, with native rank mass 5,073 and
3,507 native children. The native records are unchanged. Each replay
checks 640 input columns, restores 408 arbitrary helper fields and 91
private zero buffers, and leaves the eight owned fields zero.

The supplied backward word is the negative transpose of `E`. It is not
its inverse. The inverse formula and the scalar gauge programs below do
not complete a supplier or change the complete kappa bound.

## Native construction and inverse

In the pinned symmetric response family, give directions 0 through 31
weight two at indices congruent to 2 or 3 modulo 4, and weight one at the
other indices. Give directions 32 and 37 weight `1/2`. Give the other six
directions from 32 through 39 weight `-1`. Give directions 40 and 41
weight zero. Expand their pinned recipes into the original scalar
transfer sites. Keep every native call unchanged.

Let `O = K^T K/12`, extended by zero on the 64-port set. Then `O` is an
orthogonal projector of rank eight, and

```text
E^2 = 4I_64 + I_48 + 24O.
E^-1 = E_64/4 - I_48 + (6/5)O.
det(E) = 2^64 * 5^8.
```

The checker verifies both inverse orders with exact fractions. This
response is invertible over the rationals. It is not a unit over the
dyadic rationals. Division by five in the direct inverse is not supplied
or priced by this packet.

## Six orthogonal minors

The pair graph from the previous packet is `K_8` minus a perfect matching.
Partition its remaining edges into six perfect matchings. Use both
physical ports of each edge. Each matching then gives an eight-port
minor `K_A` with

`K_A K_A^T = 2I_8`.

The six minors are disjoint and cover all 48 ports. Their exact port lists
are in `STRUCTURED-CENTRES.json`, under `orthogonal_minor_ports`. The
checker finds the partition and verifies each identity independently
from the centre rows.

This structure gives an exact family of smaller source interfaces. For
the negative response `J_48 = I - K^T K/2`, select `k` complete minors.
Write `S` for these `8k` ports and `U` for the other ports in this block.
Then

```text
K_S K_S^T/2 = kI.
K_U K_U^T/2 = (6-k)I.
H = I_U - K_U^T K_U/2.
H^-1 = I_U + K_U^T K_U/(2(k-5)).
```

The ordinary inverse exists for `k != 5`. For `k = 1`, the selected block
of `E_48` is zero and its two off-diagonal blocks satisfy `BD = 5I`.
The ordinary centre eigenvalue of `H` is `-4`, so this ordinary inverse
is dyadic.

Let `P` be diagonal, equal to `-1` on `S` and `1` on `U`. The algebraic
data map that occurs in the diagonal borrowed-source construction is

```text
A = P + K^T K/(2(k-5)).
A^-1 = P + P K^T K P/(2(k-1)).
```

For `k = 2, 3, 4`, the checker verifies both inverse orders. The second
denominator is singular at `k = 1`; this limitation remains explicit.
For `k = 3`, both denominators are dyadic units. Thus a 24/24 split has
both an ordinary inverse and a data inverse with only dyadic scalars.
The other 64 ports form a separate Hadamard block; their gauge and the
physical selected-exchange boundary are not emitted in this packet.

## Serial gauges for the 24/24 split

For `k = 3`, `K P K^T = 0`. Consequently every query row of `K` is
unchanged by each rank-one shear in

`I - P K^T K/4`.

This gives a serial implementation with one owned field `C0`. For each
centre row, copy one source into `C0`, add the other eleven signed
sources, apply its signed scatter, then subtract the same query from the
updated data. The field returns to zero. Negating the selected ports
after these shears gives `A = P - K^T K/4`. For the inverse, negate those
ports first and use the opposite shear sign.

The ordinary gauge uses only the six entries of each centre row that
lie in `U`. A scatter for `H` multiplies its query by `-2`; a scatter for
`H^-1` multiplies its query by `-1/2`. Scale `C0` by that same factor before
subtracting the updated query. The field again returns to zero.

The emitted scalar programs have these exact bills:

| Gauge on the 48-port block | Real scalar primitives | Native children |
| --- | ---: | ---: |
| `A` | 2,688 | 0 |
| `A^-1` | 2,688 | 0 |
| `H` on the 24 ordinary ports | 1,236 | 0 |
| `H^-1` on the 24 ordinary ports | 1,332 | 0 |

Each program uses one owned field and restores it to zero. All 112 data
input columns are checked, including identity action on the other
ports. The two inverse orders are checked. The program requires a common
physical frame for all operands. It does not grant access to an old query
on a retired Y bank or to a future query on X.

## Remaining supplier obligations

The local response and common-frame scalar gauges are implemented. A
complete use in the supplier must still prove the selected physical
exchanges, the 64-port gauge, each routed stage transition, helper access
at the required cuts, the terminal map, and the complete recursive bill.
It must also choose whether it uses the dyadic 24/24 interface or a
different interface with an explicit odd-division service. No such choice
is assumed by the present packet.

Run these commands from the workspace root, both normally and with
`python3 -O`:

```text
python3 work/centre-encoding-campaign-20261014/lanes/controller-followthrough-20261017/structured-centres/check_structured_centres.py
python3 work/centre-encoding-campaign-20261014/lanes/controller-followthrough-20261017/structured-centres/check_rank8_gauges.py
```

The first command ends with `PASS_NATIVE_STRUCTURED_CENTRES`. The second
ends with `PASS_SERIAL_RANK8_GAUGES`. The freeze manifest pins the proof,
checkers, receipts, and native payload.

This work uses the response directions and native core from the
oblique-native lane, the pair geometry from the preceding packet, and
the native replay and cost model from the new-core-transfer lane. It is
AI-assisted research. It is not a PR or a selected frontier result.
