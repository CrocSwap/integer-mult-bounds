# A literal scalar word for the unnormalised capture

The actual rank-thirty capture Csum and its inverse have complete
scalar words on one existing 112-field bank. Each direction costs
2,910 old real scalar units and forty-four real fixed-odd scans.
Capture uses multiplication; decode uses division. There is no new
field and no native child. All 528 other roles in the 640-role test
remain arbitrary and unchanged.

The word requires a proved common chart on its data bank. It does
not establish that chart at a native source cut. Entry translations,
frame changes, and interstage transport are separate operations.

## Exact word and source pins

UNNORMALISED-CODE.md defines the matrices and their full image
test. This packet consumes its payload, SHA256
`8dd0706ad41a843c9e74346b181389712a81ba6f354fdd019688e2d6b094908e`.
The actual source and selected minor have the pins stated there.
The constant B0 and G0 words come from CENTRE-CONSTANTS.json,
SHA256
`9f45130ccde5bf1624bf051f4b10023411d6f35f0ac99bd6ab13572d4c530368`.

The emitted word implements the four exact block updates:

```text
a_A = U_A^-1 a_A
a_O -= U_O a_A
a_A = B0 a_A
a_A += V_O a_O.
```

The selected-minor update has a short factorization. First apply
(x,y)->(x+y,x-y) to each of the first eight selected pairs:

```text
x += y
y *= 2
y -= x
negate y.
```

Next permute the first sixteen selected coordinates. New coordinate
i takes old coordinate j from this list:

```text
0,12,1,14,5,11,3,9,7,15,2,4,10,13,6,8.
```

Each transposition is lowered to three unit ADDs and one sign:

```text
x += y
y -= x
x += y
negate y.
```

Negate coordinates 1,5,7,9,12,14,15 and all coordinates from 16
through 29. Finish the minor update with

```text
a_1  += 2 a_0
a_9  += 2 a_8
a_13 += 2 a_12.
```

Each coefficient-two ADD uses a temporary source doubling, one
unit ADD, and a source halving. The source is restored before the
next operation. The checker compares this complete minor word
with the actual U_A^-1 on all columns.

The U_O scatter has 124 terms. Sixty-four terms have absolute
coefficient one half and sixty have absolute coefficient one.
Each half term uses a temporary source halving, a signed unit ADD,
and a source doubling. The reviewed B0 word follows. The final
V_O gather has 120 unit terms. Every source and target is an
existing data field; no field is set to zero or discarded.

Reverse the event list and invert each event to obtain the decoder.
The only new gate type in that reverse word is exact division by
three or five. The matrices are invertible over the rational field
on arbitrary inputs. Exact dyadic-grid execution of the inverse
requires either a valid code or the separate generic rational-grid
contract.

## Complete common-chart invoice

A complex unit ADD costs eight old real scalar units. A complex
sign or one-bit binary scale costs two. The emitted word has 309
ADDs, 69 signs, 150 binary scales, and 22 complex odd operations.

| Word | Old real scalar units | Real fixed-odd scans |
| --- | ---: | --- |
| Csum | 2,910 | 22 multiplications by 3 and 22 by 5 |
| Csum inverse | 2,910 | 22 divisions by 3 and 22 by 5 |
| Capture, G0, decode | 6,090 | 22 multiplications and 22 divisions for each of 3 and 5 |
| Capture, G0 inverse, decode | 6,090 | 22 multiplications and 22 divisions for each of 3 and 5 |

Each row uses zero new owned fields, zero native children, and zero
address maps inside the common chart. The G0 word or its inverse
costs 270 old units, as proved in CENTRE-CONSTANTS.md.

For n records per real field, the fixed-odd scan bound from the
retained exact arithmetic contract is at most 4n(w_g+1) arithmetic
head steps per real scan. Thus capture or decode adds at most
176n(w_g+1) such steps. Either complete scalar chain adds at most
352n(w_g+1). Descriptor and counter work remains separate and
linear. This packet does not assign a zero cost to an outer view.

## Exact prefixes and arbitrary inputs

The checker carries all 640 formal input columns. Each gate has
source and target in the chosen 112-field bank. The other 528
columns remain identity, and none enters a data output. This
includes arbitrary data in the other bank and arbitrary helper
roles. No zero-state premise is used.

The prefix bounds use the maximum absolute input component as the
unit. The ADD-operand bound is the sum of the two row norms before
an ADD, before any cancellation.

| Execution | Stored row bound | ADD-operand bound | Binary height | Odd height |
| --- | ---: | ---: | ---: | --- |
| Capture on arbitrary dyadic data | 15 | 21 | 1 | 0 |
| Generic decode on arbitrary code coordinates | 9 | 13 | 2 | 1 at 3 and 5 |
| Decode on Csum a, relative to a | 15 | 21 | 1 | 0 |
| Capture, G0, decode | 44 | 52 | 1 | 0 |
| Capture, G0 inverse, decode | 44 | 66 | 2 | 0 |

For each valid execution, the checker verifies every odd division
before it applies the gate. Each coefficient has a denominator
coprime to the divisor and a numerator divisible by it. Thus the
division is exact on arbitrary values from the declared binary
grid. No odd root scale is needed in these valid chains. The table's
binary heights and magnitude bounds must still be paid.

The two complete scalar chains give E and E^-1, respectively, on
all data columns. They are useful checks of the code interface.
They do not replace the supplier's physical action Q E Q^-1 or
its two-bank native triangular endpoints.

## Physical scope

The scalar word is valid when all participating fields have the
same linear frame. The operations then commute with that common
frame. The rank-thirty interfield ADDs are not valid in arbitrary
independent frames without an explicit intertwiner.

An input-side Q^2 on all 112 fields gives the entry code Csum Q^2
from the source section theorem. These are 112 explicit field
translations. Their full map cost remains due. The inverse uses
the translations on the opposite side of the scalar inverse.
Neither direction gives the odd transported code Q^-1 Csum Q^-1
for free.

Code preservation at a later cut must be proved with the whole
state. The congruence tests in UNNORMALISED-CODE.md give an exact
algebraic test. They do not prove legal source access, partial
native helper restoration, or a final raw-output decoder. No
complete supplier cost or kappa improvement is claimed here.

## Reproduction and credit

Run with fresh output directories:

```text
python3 -I -B work/centre-encoding-campaign-20261014/lanes/native-escape-20261017/rational-code-admission-20261020/check_capture_word.py --out /tmp/capture-word-normal
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/native-escape-20261017/rational-code-admission-20261020/check_capture_word.py --out /tmp/capture-word-optimized
```

Expected status: PASS_ACTUAL_UNNORMALISED_CAPTURE_WORD. Both output
files must match byte for byte.

The actual U,V and selected minor come from the new-core and
coherent-port lanes. The earlier constant-code packet supplies
the B0 and G0 words. This packet supplies the complete selected
minor lowering, scatter and gather word, inverse, and prefix
invoice. OpenAI Codex assisted the proof and checks. No
publication is authorised. Before any future PR description,
read /Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md.
