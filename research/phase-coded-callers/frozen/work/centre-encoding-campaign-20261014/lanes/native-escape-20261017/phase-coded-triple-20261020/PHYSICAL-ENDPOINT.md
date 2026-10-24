# A phase-coded triple has one common line factor

The actual D25 forward-backward-forward word has a simple physical
endpoint after three scalar shears. With Q entry on the selected
borrowed fields, the result is

```text
X = -F25 q Y0,
Y =  F25 q X0.
```

Here X0 and Y0 are the original physical inputs. Both can be arbitrary.
The line operator q acts at each port. The word has no remaining centre
correction. It still has q on both banks. The result does not admit
that factor as a free terminal or as a free recursive interface.

The I-entry variant removes q from the sixteen selected borrowed
outputs. Its direct terminal then uses 208 positive line operations.
The Q-entry variant uses 224. In both cases the native mass, including
this direct terminal, is 5,600. This is not a strict supplier improvement.

## Sources and local types

The local source is the phase-coded clean word from
`controller-followthrough-20261017/phase-coded-clean-20261020`.
Its freeze SHA256 is
`284e6239ae3287bb139497fe610e67def239ad50697f230b61ac7c7280fb4b75`.
The decompressed `final-normal/PHASE-CODED.json.gz` SHA256 is
`ffdbe1c84af50e58ee0ab3a9ada15571476146caad1119f55e17d655934f0874`.

That source removes the 592 ordinary cross-bank transfer ADDs from
the earlier clean word. It puts a physical ordinary ADD before the
inherited input views. Its replay covers all 640 independent local
input columns, both providers, and all 416 arbitrary helper fields.
The native kernels, frames, and endpoint adapters are inherited
without a change. The present checker binds the stored operator-valued
content rows. It does not repeat that native transcript replay.

The selected set is

```text
P = [0,27,36,111,20,7,57,46,1,3,6,8,17,18,24,23].
```

R contains the other 96 ports. The actual row code gives
`H=code[P,R]` and `D=response[R,P]=-H*`. These are the same
matrices as in the preceding natural clean triple.

The local Q-entry input type is

```text
X = Q(a,u),  Y_P = Q_P z,  Y_R = v.
```

The output type is FULL on X and selected Y, and `F9 q_R` on
ordinary Y. In those types the stored local maps are

```text
F_Q(a,u,z,v) = (-z,u,a+H u,v+Q_R u),
B_Q(a,u,z,v) = (z,u+D z-q_R v,-a,v).
```

The Q in the forward map stays on its source ordinary field.
The q in the backward map stays on its source borrowed field.
Neither operator is commuted through H or D.

At stage 0, the I-entry variant uses `Y_P=z` instead. The same
displayed content map then has sixteen more units of native mass.

## Actual stage access

Use the literal D25 views from
`bridge-access-20261017/matched-stage-access-20261018/DIMENSION25-VIEWS.json`,
SHA256
`125e74660e99d824f8699eed72c1facb59287976bf2c47fda533d654b8344473`.
Define G_s to be only the portwise orthogonal route rho_s. It is not
the accumulated Fourier prefix. Set

```text
H_s = G_(s,P) H G_(s,R),
D_s = G_(s,R) D G_(s,P).
```

Every G_s is an involution and fixes its own port line. The exact
entry and exit identities are

```text
Ventry_s Fprev_s = Fext_s Q G_s,
Vexit_s Fnext_s = Fnext_s G_s.
```

Their translations are the literal source translations. At a natural
boundary, X and selected Y have frame Fprev, while ordinary Y has
frame `Fprev q_R`. Thus the next local call has exactly its declared
input type with a common Fext exterior. The logical contents change
only by G_s. No additional native line operation is inserted.

The checker verifies these identities, their ordinary-hole forms,
the final F25 FULL views, and the involution property of each FULL
view. There are 1,344 checked phase identities. Each identity tensors
over the spatial columns.

## The unmodified three-call word

Write the initial Q-entry contents as

```text
X0 = Q(a,u),  Y0 = (Q_P z,v),
alpha = a+H_0 u.
```

Apply F_Q at stage 0, B_Q at stage 1, and F_Q at stage 2.
Do not insert a physical bank reset. The first two global content
states are

```text
after stage 0:
X = (-z,u),       Y = (alpha,v+Q_R u),

after stage 1:
X = (alpha,R),    Y = (z,v+Q_R u),
R = D_1 alpha-q_R v.
```

The final physical fields are

```text
X_P = -F25 z,
X_R =  F25 R,
Y_P =  F25 beta,
Y_R =  F25(u+D_1 alpha),

beta = alpha+H_2 R.
```

In the last line for ordinary Y, the local q output frame cancels
an explicit Q in its computed content. Therefore this ordinary
output is FULL. This cancellation is checked as an operator identity.
It is not inferred from a dependency on original data.

All the data can be recovered by four FULL shears:

```text
Y_P <- Y_P-H_2 X_R,
X_R <- X_R-D_1 Y_P,
Y_R <- Y_R-D_1 Y_P,
Y_P <- Y_P-H_0 Y_R.
```

The result is `X=(-z,-q_R v)` and `Y=(a,u)` under F25.
The next section gives a shorter placement of the same correction.

## Three FULL shears

After stage 1, X_P is alpha and X_R is R in the common F17
frame. Apply

```text
X_R <- X_R-D_1 X_P.
```

This changes X_R to `-q_R v`. Use the literal stage-1 FULL
views on the source and target fields, with their translations.
The ordinary Y bank is not accessed by this shear.

Then perform the stage-2 F_Q call. Its endpoint is

```text
X = F25(-z,-q_R v),
Y = F25(alpha-H_2 q_R v,u).
```

Apply the two final FULL shears

```text
Y_P <- Y_P-H_2 X_R,
Y_P <- Y_P-H_0 Y_R.
```

The first uses the stage-2 FULL views. The second is a scalar
port map in the global common FULL frame. This gives

```text
X = F25(-z,-q_R v),
Y = F25(a,u).
```

In Q entry, `z=q_P Y0_P` and `(a,u)=q X0`. Consequently the
complete result is the common-q signed exchange stated at the start.
In I entry, `z=Y0_P`, so the selected borrowed output already has
the required F25 frame.

The checker reads all the operator-valued local rows from the native
source payload. It composes each call with the literal entry and exit
views. It inserts the middle shear on the actual physical state,
then checks the two final shears on that state. This is done for all
224 independent data inputs and both initial entry variants. Before
the shears, the final matrix has 22,160 stored input-operator terms.
After the shears, it has exactly 224.

## Cost and the remaining obligation

The three native local words have these total profiles:

```text
Q entry: 4176 H1 + 192 H2 + 144 H3 + 48 H8,
I entry: 4176 H1 + 192 H2 + 144 H3 + 32 H8 + 16 H9.
```

Their native masses are 5,376 and 5,392. Each local word has
4,632 scalar primitives in the producer invoice, for a sum of
13,896. No odd division or owned field is introduced.

A direct coefficient implementation of each added H or D shear has
216 ADDs and 2,048 scalar primitives under the inherited tariff.
The three shears therefore add at most 6,144 scalar primitives.
The two routed shears use 448 affine field-map calls. All map calls
retain their stream and address cost. This direct bound does not
consume the smaller factored scalar code from the producer.

The signed endpoint is intentional. An unsigned output convention
requires the stated signs or an equivalent signed bank exchange in
the caller. If signs are added directly, they cost 224 scalar
primitives on the 112 X fields. No such signs are hidden in the
three-shear invoice.

The direct terminal applies Q to all 112 Y fields. It also applies
Q to the 96 ordinary X fields, and to the sixteen selected X fields
in the Q-entry variant. The result is

```text
X = -F25 Y0,
Y =  F25 X0.
```

The checker verifies this terminal as an operator on arbitrary
physical inputs. It has 208 positive line operations in I entry
and 224 in Q entry. In both cases the total native mass is
`5600=224*25`. The line side maps, global helper host, bank routing,
complete recursive invoice, and numerical precision proof are not
supplied here.

An intended recursive consumer must accept the literal common-q
endpoint, including its port directions and gathered-axis views.
A match of formal code names is insufficient. This packet provides
the exact physical endpoint for that test. It does not prove that
the next consumer accepts it.

## Verification

Run with two new output directories:

```text
python3 -B check_phase_coded_triple.py --out <new-directory>
python3 -O -B check_phase_coded_triple.py --out <another-new-directory>
```

The normal and optimized receipts are byte-identical. The checks
include all 224 input columns, both initial entry types, all 1,344
phase identities, the direct line terminal, and two negative
controls. The wrong middle sign fails. Omission of the remaining
q correction fails.

No PR, commit, push, or publication is authorized. Read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`
before any future PR description.
