# A phase-coded clean response with a FULL terminal

The clean native word admits the following changed response:

```text
F_Q(a,u,z,v) = (-z, u, a+B u, v+Q_R u).
B_Q(a,u,z,v) = (z, u+D z-q_R v, -a, v),   D=-B*.
```

Each Q-entry word uses native mass 1792 and 4632 real scalar
primitives. It uses no owned field. The I-entry formation word has
native mass 1808 and the same scalar cost. All 416 borrowed helper
fields are restored.

The three-call word `F_Q0, B_Q1, F_Q2` exposes its data and selected
record in FULL fields. Its direct terminal has 208 positive-line
calls. The total native mass is 5600. This is an exact closure of the
operator algebra. It is not a strict supplier improvement. The
routed terminal invoice, recursive hosting, and numerical grid are
separate obligations.

## Source and native change

The source is the frozen clean late exchange in
`new-core-transfer-20261017/low-displacement-20261020/clean-late-exchange-20261020`.
Its forward payload has decompressed SHA256
`b0432322c28ad3a03af8da550a0b7c7df048c7ff5a0664acc7f78efffcffd083`.
Its freeze has SHA256
`96048355033e5f5bdd26dadddb869708faae6f8b0d9a61a1ae696e5a5c20c0bc`.
The selected-role inverse-adjoint construction is pinned by
`DUAL-FREEZE.json`, SHA256
`fa8f910fe7f22a696f47513c95e814588723dc8abaaa68061fcba3676c308d43`.
All paths in this note are relative to the campaign `lanes` directory.

The local input has physical types

```text
X = Q(a,u),       Y_P = Q_P z,       Y_R = v.
```

The formation variant has `Y_P=z`. Both variants output X and
selected Y in F9. Ordinary Y has frame `F9 q_R`.

Delete the 592 ordinary X-to-Y transfer ADDs from the retained core.
Keep every native event, frame, input adapter, and output adapter.
Keep the FULL source code and the signed selected exchange. The
remaining native word has content map

```text
F_zero(a,u,z,v) = (-z,u,a+B u,v).
```

The checker verifies this map on all 640 arbitrary input fields.
In particular, the internal target code and its inverse still cancel
when the cross-bank transfers are absent.

Before all input adapters, apply 96 physical unit ADDs:

```text
physical Y_p <- physical Y_p + physical X_p,    p in R.
```

The physical input on X is Q, while ordinary Y enters in I. Thus this
prefix adds `Q_R u` to v. It is not a same-frame logical addition.
Composition with `F_zero` gives the displayed `F_Q`.

## The backward word

Take the same-chronology inverse adjoint of `F_zero`, then conjugate
it by the selected X/Y role exchange. This gives

```text
B_zero(a,u,z,v) = (z,u+D z,-a,v).
```

The native operators and endpoint adapters are unitary. Their inverse
adjoints are the same physical operators. For a scalar ADD, reverse
source and target and negate the coefficient. For a real SCALE,
invert the coefficient. The producer applies these rules in the
original event order.

The selected input frames are equal in the Q-entry variant. The
selected output frames are also equal. Thus the role conjugation
uses wire labels and adds no boundary swap instructions.

The inverse adjoint of the physical entry prefix is

```text
physical X_p <- physical X_p - physical Y_p,    p in R.
```

Its logical effect is `u <- u-q_R v`. It therefore gives the displayed
`B_Q`. No q operator is moved through B or D.

## Native and scalar invoice

The Q-entry profile is

```text
1392 H1 + 64 H2 + 48 H3 + 16 H8.
```

The formation profile replaces the last sixteen H8 calls by H9.
There are 1520 native calls in each word.

The retained scalar core costs 1720. The FULL source code or its
dual costs 1760. The signed selected exchange costs 384. The physical
entry prefix costs `96*8=768`. Thus the complete scalar cost is

```text
1720 + 1760 + 384 + 768 = 4632.
```

No native recipe is changed. The checker compares the complete
native records and all endpoint adapters with the pinned source.
It checks all 640 body columns, then composes the physical prefix
with Q or q kept on its original input source. This checks all 640
ordered columns of each complete local map.

The body prefix bound and the physical entry shear bound are recorded
separately. They are not a complete recursive numerical-grid invoice.

## Three actual stage contents

The no-reset boundary theorem is pinned by
`native-escape-20261017/no-reset-triple-20261020/FREEZE.json`,
SHA256
`089425bdf431d81456e1c988a1fd21a837baca43e510bc92dee98dc2ee571791`.
Its entry and exit identities are independent of the local content
map. Each port route fixes its own Q line. They therefore transport
the changed maps above with the same global Q and q.

Use I-entry formation at stage 0 and Q-entry words at stages 1 and 2.
Define initial contents by

```text
a = q_P X0_P,       u = q_R X0_R,
z = Y0_P,           v = Y0_R.
```

Let B0, D1, and B2 be the routed operators at their actual stages.
They need not commute. Set

```text
alpha = a+B0 u,
R = D1 alpha-q_R v,
beta = alpha+B2 R.
```

After the three calls and their declared exit views, the complete
physical output is

```text
X = F25(-z,R),
Y = F25(beta,u+D1 alpha).
```

The ordinary Y output is FULL because its logical content before
the last q exit is `Q_R(u+D1 alpha)`. This cancellation occurs on the
left of the whole expression. It does not commute Q through D1.

## Ordered terminal

Apply these four shears after the global exits:

```text
Y_P <- Y_P-B2 X_R,
X_R <- X_R-D1 Y_P,
Y_R <- Y_R-D1 Y_P,
Y_P <- Y_P-B0 Y_R.
```

Their content is

```text
X = (-z,-q_R v),       Y = (a,u).
```

All sources and targets are FULL. No ordinary-hole query is used.
Positive Q on the 96 ordinary X fields and on all 112 Y fields gives

```text
(X,Y) = F25(-Y0,X0).
```

The scalar port word for the four shears costs 7040. Their routed
monomial views must also be counted. The 208 positive-line children
and their wrappers must be supplied.

There is a shorter scalar placement. Immediately after the middle
call, apply the current FULL shear `X_R <- X_R-D1 X_P`. The last
call then outputs

```text
X = F25(-z,-q_R v),
Y = F25(alpha-B2 q_R v,u).
```

Only the final B2 and B0 upper shears remain. This uses three FULL
shears in total and has scalar port cost 5280. It has the same
208-line terminal.

## Full native-mass limit of this construction

With formation at stage 0, the complete profile including the direct
terminal is

```text
4384 H1 + 192 H2 + 144 H3 + 32 H8 + 16 H9.
```

Its native mass is

```text
4384 + 192*2 + 144*3 + 32*8 + 16*9 = 5600 = 224*25.
```

For every `0 <= sigma < 1`, all child ranks are below 25. Hence

```text
sum_h count_h h^sigma > 25^(sigma-1) sum_h count_h h
                      = 224*25^sigma.
```

Thus regrouping the same native mass cannot give a strict positive
moment margin while every child rank remains below 25. A strict
improvement must remove some native mass or change this complete
construction. This statement does not give a lower bound for coupled
field encodings or other native schedules.

## Verification

Run the two programs in fresh output directories:

```sh
python3 -I -B emit_phase_coded.py --out NEW_NATIVE_DIRECTORY
python3 -I -B check_caller.py --out NEW_CALLER_DIRECTORY
```

The expected statuses are `PASS_PHASE_CODED_CLEAN_LOCAL` and
`PASS_ORDERED_PHASE_CODED_CALLER`. The caller checker uses a free
operator-word algebra. It cancels only adjacent Q and q factors.
It checks the complete content endpoint, both terminal placements,
and the final original-input phases. It rejects a wrong correction
sign and does not commute Q through a reader.

This packet does not claim a new numerical frontier, recursive child
hosting, or a complete precision certificate.
