# Three calls with current-stage port codes

This packet gives a complete three-call content word for the fresh
matched response. It uses one X bank and one Y bank. Each bank has 112
productive fields. The five added port codes use current Y cuts or
current/past completed X cuts. There is no borrowed helper, bridge,
idle data job, or retained record in this controller.

The exact preterminal output is

```text
(-y, T x),       T = E2 E1 E0.
```

The remaining physical code is `diag(Q T Q^-1,I)`. This packet keeps
that code explicit. It does not claim that the three-call supplier is
closed without a terminal decoder.

## Actual local source

The data source is the frozen
[matched native involution](../../oblique-native-20261017/matched-native-involution/MATCHED-NATIVE.md).
Its payload is
[MATCHED-NATIVE-PROGRAM.json.gz](../../oblique-native-20261017/matched-native-involution/MATCHED-NATIVE-PROGRAM.json.gz),
with decompressed SHA-256
`95f11d2b13fc75cb0d07e79ea17afdf3f46b4aca294117ffe1a988779e99f025`.
The source supplies

```text
F_s(x,y) = (x, y + E_s x),
B_s(x,y) = (x - E_s^-1 y, y).
```

The local coefficient matrix E is symmetric and satisfies E^2=I. Its
48-port part uses the paired-mode matching. Its other 64 rows form a
negative port permutation with 32 swaps and no fixed point. Those 64
rows are not a diagonal minus identity.

Each E_s is the response after the actual stage cover views. The three
operators need not be equal. The proof below uses only their inverses;
it does not use E_s^2=I. The source word supplies the inverse because its
actual coefficient matrix is a symmetric involution.

The native entrance and exit types remain the original types:

```text
X_p: C_qp -> F9,
Y_p: I -> F9 C_qp^-1.
```

The source has no helper reads, owned C fields, or private fields. Its
three successive local jobs advance the productive data through the
25-axis construction. The complete owner and recursive host checks
belong to the separate one-pair admission packet.

## Ordered word

Execute these operations in the stated order:

| Step | Operation | Code cut |
| --- | --- | --- |
| 1 | F0 | Native word |
| 2 | X <- E0 X | Completed X at level 0 |
| 3 | Y <- E1 Y | Current Y entrance at stage 1 |
| 4 | B1 | Native word |
| 5 | X <- E1 X | Completed X at level 1 |
| 6 | Y <- E2 Y | Current Y entrance at stage 2 |
| 7 | F2 | Native word |
| 8 | X <- E1^-1 X | Completed X at level 2 |

Both providers have the same scalar code decomposition. The route views
for each occurrence still depend on its stage and cut. The code in step
8 is a past-stage code at a completed X cut. No code uses a past-stage
Y query or a future-stage completed-X query.

For arbitrary input x,y, the successive states are

```text
after step 2: (E0 x, y + E0 x),
after step 5: (-E1 y, E1 y + E1 E0 x),
after step 7: (-E1 y, E2 E1 E0 x),
after step 8: (-y, E2 E1 E0 x).
```

Every product has its displayed order. The cancellation at B1 uses its
actual reciprocal response E1^-1. The cancellation at F2 uses the E1
code on X and the E2 code on Y. No commutation is used.

For the literal endpoint `(-y,x)`, the exact condition is T=I. Equality
of the three local coefficient matrices does not establish this
condition after stage routing. Even if the routed response were one
common involution E, the product would be E, not I.

## Literal scalar codes

The emitted port circuit factors the actual local response as

```text
E = A^-1 M A,
```

where A is the 24-pair Hadamard code on the 48 coupled ports and the
identity elsewhere. M is a signed permutation on all 112 ports. The
checker obtains M from the exact response and verifies every entry.
It lowers every swap into three unit ADDs and a sign. It then applies
the inverse pair code.

The resulting circuit has 494 scalar gates and costs 2,668 real scalar
primitives. It needs no helper, owned field, private field, or native
child. The inverse circuit is also emitted and checked on all 112 input
columns. The code needs a common physical frame in its stage view.
The separate cut check supplies that view. A conservative allowance is
224 view calls per code, for gather and scatter on all 112 ports.

This circuit is an implementation of the local port matrix in a proved
common-frame chart. It is not an implementation of Q E Q^-1 at a hole
cut. Those two operations are not identified.

## Physical endpoint and direct decoder

Let Q be the diagonal intrinsic line operator, q=Q^-1, and let F be the
common completed 25-axis frame. The raw input is W(x,y), where
W=diag(Q,I). The preterminal physical frame is F diag(I,q). The old
signed terminal is

```text
A = [[0,Q^2],[-I,0]].
```

The ordered endpoint equation is

```text
A diag(I,q) [[0,-I],[T,0]] W^-1
    = diag(Q T Q^-1,I).
```

Thus a direct decoder on the first output bank has three steps, all in
the common-F coordinate convention:

1. Apply Q^-1 to all 112 fields.
2. Apply T^-1=E0^-1 E1^-1 E2^-1. The chronological order of these three
   scalar codes is E2^-1, then E1^-1, then E0^-1.
3. Apply Q to all 112 fields.

The second step uses only current or past stage charts at final FULL.
The two line passes use 224 rank-one children. This is an explicit
costed construction hypothesis for the line calls; this packet does
not emit their 25-axis native recipes or their global hosting.

A cheaper decoder, or a changed native response that makes the routed
product T simpler, is still useful. One cannot instead leave T in the
output and use the unchanged outer twiddle or pointwise product.
Such a change needs a separate encoded outer-operation contract.

## Local invoice and native-rank limit

Three data calls have profile

```text
{1:480, 2:144, 5:144, 7:336, 8:192},
```

with 1,296 children and rank mass 5,376. The three local scalar bills
and the five port codes sum to 22,436 real scalar primitives. The old
signed terminal costs 2,688 more. The five codes have a conservative
1,120-view allowance. These counts exclude precision and recursive
hosting costs.

The direct two-pass decoder adds 224 rank-one children and three scalar
port codes. Its resulting rank mass is exactly

```text
5376 + 224 = 5600 = 224 * 25.
```

It therefore leaves no rank deficit. In the unit-width native-only
moment test, it also fails every positive b: each native child has rank
less than 25, so r^(1-b) > r*25^(-b). Summing this strict inequality and
using total rank 5,600 gives a native moment greater than the productive
weight 224*25^(1-b). This conclusion applies to this direct decoder,
not to every implementation of the remaining code.

## Verification

The checker imports no producer. It reads the pinned native data word,
builds and checks both scalar code orders on all 112 columns, and checks
the generic three-call word in a free ordered group. It checks the raw
Q boundary and the complete direct inverse in the same group. It
rejects deletion of each of the five required port codes.

```text
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 -I -B work/centre-encoding-campaign-20261014/lanes/encoded-controller/one-pair-current-codes-20261018/check_and_emit.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/encoded-controller/one-pair-current-codes-20261018/check_and_emit.py
```

Both runs must report `PASS_ONE_PAIR_CURRENT_CODES` and produce the same
payload and receipt. `FREEZE.json` records their hashes. The native
phase checks are pinned predecessor results, not a new full native
replay in this packet.
