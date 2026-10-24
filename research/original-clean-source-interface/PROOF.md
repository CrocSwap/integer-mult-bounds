# All-width single-core cleaning and original-owner substitution

All products act on column contents from the left. The order of each
factor is part of the statement. The actual centre matrix has eight
rows and 112 columns, with `RR^T=56I`. Put `K=R^T/4`. Let `Q` be the
port-dependent intrinsic complex line transform. No commutation of
`Q` with `R`, `K`, or `KR` is assumed.

## Pinned raw contract

After the original entry alignment, use the physical frame types

```text
X: Q -> F9,
Y: I -> F9 Q^-1,
u: I -> F9.
```

There are eight selected helper fields `u` and 472 other helper
fields. The complete raw content maps on data and selected helpers are

```text
F_raw:
  x'=x,
  y'=y+(I-KR)x-Ku,
  u'=-u-2Rx;

B_raw:
  x'=x-(I+KR)y-8Ku,
  y'=y,
  u'=-u-Ry/4.
```

The other helper content rows are the identity in their stated output
frames. This raw content contract and its native phase identification
are inherited pinned premises. The new replay verifies the raw frame
chronology and source binding, but does not repeat the dense native
kernel compiler. The full raw source and review are retained in
`frozen/` and listed in `SOURCES.json`.

## Forward construction

Let `z` be the arbitrary selected-helper input. Execute these physical
operations between the old entry alignment and the old exit view:

```text
u += R X_phys;
Y_phys += K u;
u -= R X_phys;
raw forward core;
u += 2 R X_phys_out;
u = -u.
```

At entry, `X_phys` contains `Qx` in the common exterior frame. The
first three operations restore `u=z` and change the Y content to
`y+Kz+KRQx`. Substitution in the raw core gives

```text
y_out = y+Kz+KRQx+(I-KR)x-Kz
      = y+(I-KR+KRQ)x,
u_out = -z-2Rx.
```

At exit, X and the selected helpers have the same full local frame.
The last ADD gives `-z`; the last sign restores `z`. This proves the
forward shear with `D_plus=I-KR+KRQ`. Every arbitrary helper term
cancels. No finite-order identity for `Q` was used.

## Backward construction

Execute

```text
u -= R Y_phys/4;
raw backward core;
u += R Y_phys_out/8;
X_phys_out -= 8 K u;
u -= R Y_phys_out/8;
u = -u.
```

The input mode is `z-Ry/4`. The raw core therefore gives

```text
x_raw=x-y+KRy-8Kz,
u_raw=-z,
y_raw=y.
```

The Y output frame is `F9 Q^-1`. The first output read gives mode
content `-z+RQ^-1y/8`. Its target scatter contributes
`8Kz-KRQ^-1y`. Thus

```text
x_out=x-(I-KR+KRQ^-1)y.
```

Y is unchanged in content. The next read removes the same query and
the last sign restores `z`. This proves the backward shear with
`D_minus=I-KR+KRQ^-1`. Replacing the output `Q^-1` by `Q` changes the
data map, even though the helper read and cleanup could still cancel.

The two computations use only the stated raw maps and physical frame
types. They are identities over a free group of invertible port
operators. In particular, they do not require `Q^4=I`, a scalar square,
even tensor width, or a characteristic phase.

## The two kernels are distinct

At actual port zero, the intrinsic label is `q=11`. Character 1 gives
eigenvalue `i` for `Q` and `-i` for `Q^-1`. Also `(KR)_(0,0)=1`.
An input on that port has same-port difference `2i` under
`D_plus-D_minus`. At larger tensor width, use this character in one
layer and character zero in every other layer. The difference remains
nonzero at every positive width.

Expansion does give the useful ordered identities

```text
D_plus Q^-1 + D_minus = I+Q^-1,
D_minus Q + D_plus = I+Q.
```

They do not supply a cheap kernel inverse or a complete routed
controller. A shear is invertible by reversing its update sign
regardless of whether its coefficient kernel is a unit. The forward
and backward maps above are not mutual inverses on the same banks.

The complete original content proof and separate free-group review are
[ORIGINAL-CLEAN-SOURCE.md](frozen/work/centre-encoding-campaign-20261014/lanes/residual-syndrome/physical-algebra/ORIGINAL-CLEAN-SOURCE.md)
and [content REVIEW.md](frozen/work/centre-encoding-campaign-20261014/lanes/residual-syndrome/physical-algebra/review-gauss/original-clean-source/REVIEW.md).

## Whole helper jobs on arbitrary physical inputs

At invocation stage `s`, let `E_s` act on completed exterior
coordinates 9 through `8s+8`, and put `L=F9` on coordinates 0 through
8. Their supports are disjoint, so `E_sL=LE_s` as exact operators.

For any physical helper input `h`, write `h=E_s z`. This is an
invertible coordinate change in the proof, not a preparation or an
input promise. The complete cleaned content map restores `z` in
physical output frame `E_sL`. Its physical output is therefore

```text
E_s L z = E_s L E_s^-1 h = Lh.
```

There is no cross-helper or helper/data endpoint coefficient. The
equation therefore holds for arbitrary input arrays, including
correlated inputs. It preserves the complete width-nine job. It does
not claim that the physical helper advance is the identity.

With the old whole-job entry and exit views `A_j,B_j`, the job is still
`B_j L A_j`. The old owner's previously completed prefix can be
arbitrary; it need not equal the invocation's exterior frame `E_s`.
All other 472 helper blocks retain their old content and endpoints.

Each original body has 704 distinct owner families. For a fixed role,
the cover route is a bijection. Therefore the complete body can be
replaced on arbitrary correlated input arrays. Keep the prefix, raw
core, suffix, and final signs inside the body, and finish its complete
cover sweep before the next original event.

The exact source review matches all 144 invocations, all 69,120 helper
slots, and all 1,152 selected width-nine occurrences. Each selected job
uses nine actual pending vectors from the original phase recipe. The
vectors are orthogonal, and their full 73-coordinate chart gives exact
native covariance, including phase. The inherited old-axis history is
used only for the unchanged original schedule.

The separate full proofs are
[physical REVIEW.md](frozen/work/centre-encoding-campaign-20261014/lanes/paired-package-review/original-clean-native-review/REVIEW.md)
and [owner REVIEW.md](frozen/work/centre-encoding-campaign-20261014/lanes/paired-package-review/original-owner-review/REVIEW.md).
Neither proof uses the characteristic boundary maps from earlier
even-width experiments.

## Exact original terminal obligation

Let `E` be the complete changed data word, and let `W` be the original
signed bank exchange. The original preterminal frames are
`(F,FQ^-1)`. The old Y translation is `Q^2`, giving frames `(F,FQ)`.
This uses the exact commutation of the native translation polynomials
`F` and `Q`; it does not move `Q` through a centre matrix.

The ordered physical output operator is

```text
F W diag(I,Q) E diag(Q^-1,I).
```

The same port operator occurs on both sides of each exchange, so
`W diag(I,Q) W^-1=diag(Q,I)`. Substituting `E=W^-1` gives `F`.
Conversely, multiplying the desired output equation by the displayed
inverses gives `E=W^-1`. Hence this is the exact terminal condition.
It is not proved for the actual routed `D_plus,D_minus` kernels here.

## Complete component invoice

The source matrix has 448 nonzero entries. The forward prefix and
suffix contain 896 unit, 448 quarter, and 448 double complex ADDs.
The backward word contains 448 quarter, 896 eighth, and 448 double
ADDs. Each word ends with eight complex negations.

The two-real-component primitive bounds for magnitudes `1`, `2`,
`1/4`, and `1/8` are `8`, `10`, `12`, and `14`. Thus the added costs
are respectively

```text
896*8 + 448*12 + 448*10 + 16 = 17040,
448*12 + 896*14 + 448*10 + 16 = 22416.
```

Adding the raw scalar bound 204,418 gives 221,458 and 226,834.
The retained paid profile is
`{1:2412,2:418,3:432,4:142,5:82}`, with mass 5,522.
The 5,056 retained native events include unchanged adapters.
No added operation allocates a field or emits a native child or map.

Across the original 80 forward and 64 backward invocations, the local
scalar subtotal is 32,234,016. With the original idle suffixes, the
retained profile is
`{1:349604,2:60192,3:62585,4:20448,5:11808,7:7,48:4866}`, of mass
1,032,192. These are component counts before closure of the changed
data controller. They do not establish a complete supplier bound.

Literal parser lowering, full routing and control costs, prefix growth,
finite precision, recursive costs, data-controller closure, and final
integer recovery remain open. No kappa improvement follows.
