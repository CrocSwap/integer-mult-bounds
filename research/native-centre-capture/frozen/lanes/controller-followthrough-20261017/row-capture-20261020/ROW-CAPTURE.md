# A centre capture that changes only sixteen output rows

The actual rank-sixteen response has a dyadic code on its existing data
fields. The code changes sixteen selected rows and leaves the other
ninety-six rows unchanged. Its inverse changes the same sixteen rows.
Both words cost 1,760 real scalar primitives. They use no additional
field, native child, or odd division.

This code gives a concrete forward-service interface. First apply the
code to the current I-frame Y bank. Keep the original source paths and
the ninety-six ordinary target paths. Replace the sixteen selected
target paths by full F9 children. At the completed source cut, add the
specified centre query to those sixteen FULL targets.

The scalar algebra is checked here. The native emitter and the routed
cut check are separate packets. A complete supplier decoder is still
open.

## Exact source and pivots

The pinned native source is

```text
new-core-transfer-20261017/low-displacement-20261020/
odd16-normal-v2/EXTENSION-PROGRAM.json.gz
decompressed SHA256
d466cea24be92fb7f749d686c5efc63f44ea82575c15f78c38e9d6d4c972eba4
```

Its response is E=I+UV, where U has sixteen columns and V has sixteen
rows. The first eight centre coordinates come from the six-mode blocks.
The other eight come from the eight-port cliques. The exact action is

```text
H = I+VU = diag(-5 I8,-7 I8).
```

Select these physical pivots, in this order:

```text
P = [0,27,36,111,20,7,57,46,1,3,6,8,17,18,24,23].
```

Let R be the other ninety-six ports. The first eight pivots form four
complete physical pair blocks:

```text
(0,27), (36,111), (20,46), (7,57).
```

The matrix V_P has determinant 16. It is a dyadic unit. Its eight-port
part is the signed pair code, with the stated order of its centre
coordinates. Its remaining part is identity. It commutes with H.

Put W=V_P^-1 V and write W=[I,B] in P,R order. This W is a rectangular
reader. It is not the Clifford gauge called W in other campaign notes.
Define

```text
C = [ I   B ],          C^-1 = [ I  -B ].
    [ 0   I ]                  [ 0   I ]
```

Thus C records the normalized centre query in P and retains the original
ordinary values in R. Each selected target can have any initial value.
The inverse subtracts the same query from the unchanged R sources.
There is no clean-record premise.

The large selected rows have twenty coefficients of magnitude 1/2.
The small selected rows have seven unit coefficients. For each large
row, scale the target by 2, add the twenty signed unit sources, and
scale the target by 1/2. The price is 164 per large row. Each small row
costs 56. Hence each complete code costs

```text
8*164 + 8*56 = 1760.
```

## The encoded response

Let A=U_R V_P. Exact multiplication gives

```text
C E C^-1 = [ H   0 ].
           [ A   I ]
```

The centre action is diagonal. A lower fanout into the ordinary fields
remains. The code does not turn the complete response into a diagonal
matrix.

The selected rows of CE are HW. The ordinary rows are the original
ordinary rows of E. In the literal paired-mode chart, CE has nonzero
diagonal entries on exactly the sixteen selected pivots. All other
mode diagonal entries remain zero.

These facts permit a narrower native change than full diagonalization:
the new response needs different target paths on sixteen fields.

## A forward service with FULL centre outputs

Let x,y be arbitrary local data. The physical entry is

```text
X = Qx,       Y = y.
```

The original forward service has physical output

```text
X = F9 x,     Y = F9 q(y+Ex),       q=Q^-1.
```

Use the following ordered construction.

1. Apply C to Y in the common I frame.
2. Run all original X paths and all original Y paths on R.
3. Apply a full F9 child to each selected Y field.
4. After all X fields are FULL, add HWx to the selected Y fields.

The resulting exact physical output is

```text
X   = F9 x,
Y_P = F9 W(y+Ex),
Y_R = F9 q_R (y+Ex)_R.
```

For step 4, every source is F9 x and every selected target is already
F9 Wy. Therefore the additive map is a common-frame scalar query. Its
literal word preserves every arbitrary target baseline. It costs 3,424
real scalar primitives, with no scratch field or odd division.
The coefficients with numerators 5 and 7 are ordinary dyadic ADD
coefficients under the pinned scalar tariff.

The complete large selected pair blocks are material. Removing their
target pair code and inverse code does not change an ordinary target.
The original forward target operations do not feed any X source.
The small selected pivots have no target pair-code dependency.
The native packet must check these statements on every actual event.

Removing sixteen target progress paths of mass 8 and inserting sixteen
children of rank 9 gives the provisional mass change

```text
-16*8 + 16*9 = +16.
```

This count is not the full recursive bill. The emitted child profile,
native phases, endpoint adapters, scalar removals, and hosting checks
remain the responsibility of the complete native packet.

At a routed stage, a selected Y output must use the X FULL exit view.
It must not keep the old Y-hole exit view. Under the next stage's old
current-Y view, these selected inputs have an exterior Q_p factor,
while the ordinary inputs have exterior I. The changed service is not
automatically an old all-I Y input.

## A narrower transition

Suppose two routed codes use the same physical pivot set and both have
the form C_s=[[I,B_s],[0,I]]. The B_s entries can be spatial operators.
Keep the phase order exactly. Then

```text
C_t q C_s^-1 Q
  = [ I   B_t - q_P B_s Q_R ].
    [ 0             I       ]
```

There is no product of the two correction terms: each term has rows in
P and columns in R. The transition leaves all ninety-six R fields
unchanged and uses them only as sources.

This statement is stronger than a displacement-rank bound. It still
does not supply the phase-coded reader q_P B_s Q_R at a legal cut.
Sixteen changed outputs do not imply sixteen native children.

## Use in the last call of the one-pair controller

For the actual symmetric, noninvolutive native response, the legal
five-code content word is

```text
F0;
X <- E0 X;
Y <- E1^-1 Y;
B1, with backward cross term -E1;
X <- E1^-1 X;
Y <- E2 Y;
F2;
X <- E1 X.
```

It has content endpoint

```text
(-y,T x),       T=E2 E1^-1 E0.
```

Using the new capture only in F2 changes this to the physical endpoint

```text
X   = -F25 y,
Y_P = F25 [C2 T x]_P,
Y_R = F25 q_R (T x)_R.
```

This equation includes every original borrowed Y input: its
coefficient in the final Y bank is zero. It does not make X a further
clean data record. X retains arbitrary original y.

To see the remaining decoder precisely, put z=E1^-1 E0 x. Write

```text
c = [C2 E2 z]_P = H W2 z,
b = (E2 z)_R.
```

Then the content inverse of the last E2 factor is

```text
d   = H^-1 c,
z_R = b - A2 d,
z_P = d - B2 z_R.
```

The centre c is FULL, while b remains in its ordinary hole frames.
The lower fanout and the last reader therefore have phase and access
obligations. The earlier factors E0^-1 E1 also remain. No 16-line
terminal decoder follows from these equations.

## Checks, credit, and status

Run from the workspace root:

```text
python3 -I -B work/centre-encoding-campaign-20261014/lanes/controller-followthrough-20261017/row-capture-20261020/check_row_capture.py
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/controller-followthrough-20261017/row-capture-20261020/check_row_capture.py --output work/centre-encoding-campaign-20261014/lanes/controller-followthrough-20261017/row-capture-20261020/run-optimized
```

Both runs must report PASS_EXACT_ROW_CAPTURE and produce identical
payload and receipt bytes. The checker reads the pinned response and
pair-code data. It imports no producer. It checks both code inverse
orders, the selected minor, all encoded-response entries, the sixteen
mode diagonal entries, both scalar words, and all 224 columns of the
final arbitrary-baseline query.

The new-core lane supplied the actual rank-sixteen response. The
bridge-access lane found the complete-pair pivot matching and supplied
the native chronology and exit-view requirement. This lane supplied the
row-only normalized code and its ordered transition. The root proposed
the full-F9 selected-target replacement. The new-core lane emits that
complete native word; the new-native-recipes lane reviews it.

AI assistance was used. No PR, commit, push, or publication is
authorized. Before any future PR description, read
/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md.
