# Actual source cuts for the reciprocal centre readers

The three centre readers in the reciprocal F/B/F controller can be
formed from current data at their stated cuts. The accumulated P codes
do not require a separate old-chart read. They are already present in
the stored source values.

The middle reader is not a FULL record. In global coordinates, its
natural accumulator frame is `F9 q_anchor`. The first and last reader
frames are FULL, at F9 and F25. A complete construction must supply,
carry, and restore these accumulator fields. This packet does not
supply that storage or restoration.

At each cut, the conditional operation that adds the reader to a
separate accumulator has 136 complex signed ADDs, or 1,088 inherited
real scalar units. It uses no additional native source-line transform.
That count requires the accumulator to be present in the stated body
frame. It excludes accumulator views, preparation, transport, leases,
and a later erase.

## Actual response and local contracts

The pinned physical response has

```text
E = P R,       R = I+U ell,
P^2=R^2=I,    ell U=-2 I16.
```

The model is the actual 112-port response from
`oblique-native-20261017/signed-metric-reciprocal-20261020/model-normal-v2/RESPONSE.json.gz`,
with decompressed SHA256
`df2d2028c99028db3c645b3311d7f31ff96efe72f6f9257f99157ce030ff43d0`.
The checker uses its physical matrices and its `reflection_L` and
`reflection_U`. P changes 32 physical fields and fixes the 16 specified
centre anchors. P is a dyadic scalar matrix, not a physical monomial.

The emitted native contracts are

```text
F_E:     (Qx,y) -> (F x, F q(y+E x)),
B_(E^-1):(Qx,y) -> (F(x-E^-1 y), F q y).
```

Here F is the local nine-dimensional FULL transform and `q=Q^-1`.
Every target uses the hole output. The native source is
`oblique-native-20261017/signed-metric-reciprocal-20261020/native-normal/NATIVE.json.gz`,
with decompressed SHA256
`f528752be6222da2b64522f9a124622acab4413e79d403d58b592d2533307d1e`.
Both providers contain both required literal words. Their native
transcripts and arbitrary-helper restoration are inherited. This
checker pins them and checks the cut metadata; it does not replay
their native events.

Apply P to current-I Y before the raw service. Apply P to raw FULL X
after the service. These wrappers give

```text
F_s = diag(P_s,P_s) [[I,0],[R_s,I]],
B_s = diag(P_s,P_s) [[I,-R_s],[0,I]].
```

For B, the exact cross identity is `P E^-1 P=P R`. The backward
cross is E^-1. It is not E or E^-T. No P is commuted through Q.

## Global routed maps and centre coordinates

Let Gamma_s be the diagonal data route with port-p entry rho_(s,p).
Let Gamma_c,s use the same routes at the 16 declared centre anchors.
Both are involutions. Define

```text
P_s   = Gamma_s P Gamma_s,
R_s   = Gamma_s R Gamma_s,
U_s   = Gamma_s U Gamma_c,s,
ell_s = Gamma_c,s ell Gamma_s.
```

Then `R_s=I+U_s ell_s` exactly. The centre coordinates have a declared
anchor route. They are not an unspecified scalar output space.

For the three-call word, put

```text
t = y+R0 x,
w = x-(P0^-1 R1 P0)t.
```

Immediately after F0, the logical data banks are `P0 x,P0 t`.
Immediately after B1, they are `(P1 P0)w,(P1 P0)t`. Consequently the
three effective readers are

```text
c0 = ell0 x,
c1 = ell1 P0 t,
c2 = ell2 (P1 P0)w.
```

The corresponding reflection factors in the stripped coordinates are

```text
U0 ell0,
(P0^-1 U1)(ell1 P0),
((P1 P0)^-1 U2)(ell2 P1 P0).
```

These are ordered products. In particular, the second and third
readers are not ell1 t and ell2 w.

## Exact view convention

Let F_s be FULL on the root block and fresh blocks 1 through s.
Let F_ext,s be FULL only on those fresh blocks. The current literal
entry and exit views obey

```text
V_in,s F_(s-1)   = F_ext,s Q Gamma_s,
V_in,s F_(s-1) q = F_ext,s Gamma_s,
V_out,s F_s     = F_s Gamma_s.
```

The same identities hold on the declared centre anchors.

The D25 source stores the entry translation BEFORE the route:

```text
V_in,s = P_rho T_delta0
       = T_(rho delta0) P_rho.
```

It stores the exit translation AFTER the route. The checker uses
these literal conventions and verifies all 672 full Z4 identities
for both fresh stages and all 112 ports. Omitting the entry
translation fails the negative control.

## The three source cuts

For c0, wait until the raw F0 source word is complete, and read X
before its added post-P0. This body source is `F9 x`. A same-frame
accumulator ADD forms `F9 ell0 x`. No entry map is needed at stage
zero. The returned global record has frame F9.

For c1, read Y at the stage-1 current-I entrance, before pre-P1 and
before the raw native word. The incoming physical Y bank is

```text
F9 q P0 t.
```

Its literal entry view gives

```text
F_ext,1 Gamma_1 P0 t.
```

Thus the local physical row ell reads the required argument without
removing P0. It adds
`F_ext,1 ell Gamma_1 P0 t` to a same-frame body accumulator.

To express that accumulator at its global centre anchor, use the
inverse entry view. The exact identity is

```text
V_in,c,1^-1 F_ext,1 = F9 q_anchor Gamma_c,1.
```

The returned reader term is therefore

```text
F9 q_anchor Gamma_c,1 ell Gamma_1 P0 t
  = F9 q_anchor c1.
```

Calling this term FULL would omit one centre line. A later native
progression or another proved transport must account for that line.

For c2, wait until the raw F2 source word is complete and read X
before post-P2. Its body source is

```text
F25 Gamma_2 (P1 P0)w.
```

The current scalar row ell gives
`F25 ell Gamma_2 (P1 P0)w`. The centre FULL exit gives

```text
F25 Gamma_c,2 ell Gamma_2 (P1 P0)w = F25 c2.
```

The accumulated P1P0 code stays in its ordered position. The query
does not read a retired ordinary hole. It reads the completed current
source before its postcode.

## Conditional reader word and full local invoice

The physical ell has eight rows of length ten and eight rows of length
seven. All 136 entries are +1 or -1, and their source support contains
96 distinct data ports.

The emitted local interface has 16 independent accumulator fields.
For each nonzero ell_(i,p), it applies

```text
acc_i += ell_(i,p) source_p.
```

The first and third cuts use X. The second cut uses Y. The source
and accumulator must have the same current body frame. These ADDs
have no source address maps because the data is already in that body
view. Any accumulator maps remain a separate cost.

The complete operation on arbitrary inputs is

```text
(data, helpers, acc) -> (data, helpers, acc+ell source).
```

The supplied accumulator can be dirty. Its old value remains present.
A clean query is obtained only if the caller supplies a zero
accumulator or proves a joint use of that old value.

The checker replays all 656 independent input columns: 224 data,
416 other local roles, and 16 accumulator fields. Data and helper
values are unchanged. Reversing the ADDs restores every input if the
source is unchanged. This last condition holds for a local read/erase
test; it is not a late-erasure proof for the complete controller.

A complex signed-unit ADD costs eight real scalar units under the
inherited tariff. Each reader formation costs 136*8=1,088 units.
All three formations cost 3,264 units if their required accumulators
are supplied. An immediate local erase costs another 1,088 per reader.
No claim is made about the cost of the required later erase.

At each prefix of this word, an accumulator row contains its own
baseline and at most ten distinct signed source terms. Its row one-norm
is at most eleven, and the bound is attained. The word introduces no
coefficient denominator. These are local reader bounds; a complete
precision proof must also include the input frames and record lifetime.

## Reproduction and remaining work

Run with new output directories:

```text
python3 -B check_cuts.py --out <new-directory>
python3 -O -B check_cuts.py --out <another-new-directory>
```

Both commands return `PASS_EXACT_CURRENT_READER_CUTS`. Their two output
files must match byte for byte. The checks bind the response and native
source pins, physical factorization, 672 phase identities, actual cut
metadata, and both complete local reader words.

The oblique lane supplied E/P/R and the native words. The cover lane
supplied the ordered reciprocal-controller variables. The bridge lane
supplied the exact current-stage views and is investigating record
retention. This work used AI assistance.

This result resolves the source-access question at these three cuts.
It does not supply 16 safe record fields, a zero baseline, their
recursive host, their phase transport, or their final restoration.
Those obligations determine whether these available readers become
a complete centre service. No complete supplier or kappa gain is
claimed.

No PR, commit, push, or publication is authorized. Before any future
PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
