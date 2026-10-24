# Clean centre rows from a late productive exchange

This packet forms the sixteen selected centre rows without a clean
target or an extra field. It puts the old selected target values into
the selected source fields. All 416 auxiliary fields can have arbitrary
initial values and return unchanged.

Two distinct input contracts are supplied. Initial formation accepts
selected targets in I. Reuse accepts selected targets in their positive
line frame Q. Both words cost 8,600 real scalar primitives. Their native
masses are 1,808 and 1,792, respectively. These are complete local
invoices. A full supplier still needs its routed caller, helper host,
recursive bill, and precision bound.

## Exact inputs and source code

The source response is the frozen rank-sixteen response E. Select the
ordered physical ports

```text
P = [0,27,36,111,20,7,57,46,1,3,6,8,17,18,24,23].
```

Write U for the other ninety-six ports. The normalized reader L has
the form L=[I,B] in P,U order. The existing row code is

```text
C = [ I  B ],       C^-1 = [ I -B ].
    [ 0  I ]              [ 0  I ]
```

The literal C word uses no extra field and costs 1,760 real scalar
primitives. It accepts arbitrary source values.

The exact reader and code come from
`controller-followthrough-20261017/row-capture-20261020`.
The exact retained native paths come from
`row-only-capture-20261020`. The I-entry variant uses the reviewed
direct-FULL formation paths. The Q-entry variant uses the reviewed
line-entry prefix in `fixed-reader-reuse-20261020`. Every source file
and review pin is stored in the payload.

Let q=Q^-1. Here Q has one positive line operator on each port, and F9
is the common full nine-coordinate operator.

For initial formation the physical inputs are

```text
X = Qx,       Y = y.
```

For reuse they are

```text
X = Qx,       Y_P = Q_P z,       Y_U = y_U.
```

The x, y, and z values in each stated contract are independent and
arbitrary. In particular, z does not have to be a centre value. The
contract does not assume any relation between z and x.

## Literal construction

First run the complete retained source paths and the ninety-six
ordinary target paths. None of these events reads a selected target.
Then advance the sixteen selected targets to FULL. Initial formation
uses sixteen rank-nine children. Reuse uses sixteen rank-eight
line-to-FULL children, with their actual nontrivial wrappers.

At this cut all X fields and all selected Y fields are FULL. The
content is

```text
X = x,
Y_P = b,
Y_U = (y+Ex)_U,
```

where b=y_P for formation and b=z for reuse. The ordinary Y fields
retain the physical exterior q_U. Apply C to X at the common FULL
cut. Thus X_P=Lx and X_U=x_U. For every p in P, perform the following
three unit ADDs in this order:

```text
Y_p += X_p
X_p -= Y_p
Y_p += X_p
```

For arbitrary values a and b, these three steps map (a,b) to (-b,a).
They cost 24 real scalar primitives per selected pair. No extra sign
instruction or temporary field is needed.

The exact physical result is therefore

```text
X_P = -F9 b,          X_U = F9 x_U,
Y_P = F9 Lx,          Y_U = F9 q_U (y+Ex)_U.
```

The sixteen centre values in Y_P contain no old Y contribution. The
old selected target state is still present, with a minus sign, in
X_P. The construction changes the productive data interface; it does
not erase that state.

## Full-domain correctness

The content map is invertible. If its output content is (u,v), recover

```text
x_U = u_U,
x_P = v_P - B u_U,
b   = -u_P,
y_U = v_U - E_U x.
```

All coefficients are dyadic. The checker forms this inverse independently
from the output equations and checks both product orders on all 224 data
columns. This establishes invertibility of the content map. It does not
price an inverse physical service.

The literal forward replay checks all 640 input columns. It checks the
frame of each scalar source and target, both frames of every native
call, and all final frames. Every native recipe, frame list, and endpoint
adapter is inherited byte for byte from an independently reviewed
source. The new suffix uses only scalar operations at the common FULL
cut. It introduces no new native phase operator.

The selected targets are advanced before the code and the exchanges.
The source code runs only after the complete retained native sweep.
Thus the proof needs no early all-source FULL cut, old source read, or
commutation of Q with the response.

## Complete local invoices

Both variants have the same scalar bill:

```text
retained native word scalar operations       6456
FULL-X row code                              1760
sixteen signed exchanges: 16*24               384
total                                       8600
```

Their exact child and view invoices are:

| Item | Initial I entry | Selected Q entry |
| --- | ---: | ---: |
| Native profile | 1392 H1 + 64 H2 + 48 H3 + 16 H9 | 1392 H1 + 64 H2 + 48 H3 + 16 H8 |
| Native mass | 1808 | 1792 |
| Native children | 1520 | 1520 |
| Input monomial views | 112 | 128 |
| Output monomial views | 96 | 96 |
| Native side-map upper bound | 3008 | 3040 |
| Extra owned or private fields | 0 | 0 |
| Odd divisions | 0 | 0 |

The sixteen direct F9 recipes have identity side maps. The H8 recipes
retain both side maps. The invoice does not transfer the identity-map
claim from F9 to H8.

At the scalar and native operation boundaries, the maximum content row
one-norm is 22. The additional binary denominator height is one. These
are exact local content bounds. They do not include primitive internal
roundoff, recursive child precision, or the complete caller.

## Verification and limits

Both providers and both entry variants pass normal and optimized Python
with byte-identical payloads and receipts. The serialized payload is
replayed in each run. A missing source-code ADD and a missing exchange
ADD are both rejected in every complete word.

Run either command with a new output directory:

```text
python3 emit_clean_exchange.py --out <new-directory>
python3 -O emit_clean_exchange.py --out <another-new-directory>
```

The emitter refuses an existing output directory.

The next productive source can use (Y_P,X_U), whose content is Cx.
The other bank then contains (-b,(y+Ex)_U), with mixed physical phases.
A routed next-entry proof must bind these actual roles and phases. This
packet does not apply C^-1, identify the source with x, or assume that
the same reader survives another service.

The construction builds on the campaign's rank-sixteen response, row
capture, direct-FULL formation, and line-entry reuse packets. AI agents
prepared and checked this extension. Independent review is recorded in
a separate packet.
