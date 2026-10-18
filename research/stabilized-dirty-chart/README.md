# Minimum paid companion for a dirty connector chart

The equal-kernel condition in reviewed [PR1858](https://github.com/CrocSwap/integer-mult-bounds/pull/1858)
is sharp for a chart acting only on the connector. A **paid dirty companion**
changes that boundary. For fixed linear maps `B0,B1:X→Z`, let

```
r0 = rank B0,  r1 = rank B1,  r = rank(x ↦ (B0 x, B1 x)).
```

The smallest dimension h for which there are `D,E:X→H`, `dim H=h`, and an
invertible `R:Z⊕H→Z⊕H` satisfying

```
R(B0 x, D x) = (B1 x, E x)    for every x
```

is exactly **`h = r − min(r0,r1)`**, over any field and for finite-dimensional
X and Z. This is a sharp signal-space theorem. It does not price R, D, E or
physical storage automatically.

A complete four-bit F2 pilot uses one extra dirty bit and **56 scalar XORs
versus 68** for two independent closed echoes. Its source maps have different
ranks (two and three), so a connector-only invertible chart cannot work.
Every one of the 131,072 dirty inputs, the inverse and the exact operator are
checked. This is a changed-alphabet pilot, not a selected supplier or new bound.

## Proof of the sharp dimension

Choose bases and write U0,U1 for the row spaces of B0,B1 in the dual of X.
Their sum U has dimension r. If the two augmented maps are related by an
invertible R, they have equal kernels and therefore equal row spaces S.
Since S contains U0 and U1, `dim S ≥ r`. Appending h rows to either map gives
`dim S ≤ r0+h` and `dim S ≤ r1+h`. Hence `h ≥ r−min(r0,r1)`.

Conversely, choose rows of D that extend a basis of U0 to a basis of U, and
rows of E that extend a basis of U1 to a basis of U. They need respectively
`r−r0` and `r−r1` rows. Pad either list with zero rows to the displayed h.
Both augmented maps now have row space U and kernel `ker B0 ∩ ker B1`.
The map sending `(B0x,Dx)` to `(B1x,Ex)` is therefore a well-defined
isomorphism between their images. Extend bases of these images to bases of
the common codomain Z⊕H. Mapping one extended basis to the other gives the
required invertible R. This proves attainment, including zero maps and h=0.

The h=0 case is exactly the credited predecessor's equal-kernel criterion.
The construction is basis-independent despite the row-space proof. Enlarging
H, picking redundant E rows, or choosing a different R may trade source-query
cost against chart cost; the theorem minimizes h alone. It does not minimize
gate count, total storage over a larger program, or a native recursive bill.

## All-dirty boundary and restored word

The execution below is over F2. Source x is read-only. Connector z, companion
w and outputs y0,y1 are distinct and arbitrarily dirty. They are reserved for
this word; private child scratch is distinct and restored. The changed alphabet
adds complete queries `w += D x`, `w += E x`, and the paid invertible chart R
and inverse on the actual pair (z,w). It assumes no free copy, zero initial
row or observation of an intermediate output. A0,A1 are arbitrary fixed exact
F2-linear maps and need not commute, be invertible or be related to B0,B1.

```
y0 += A0 z; z += B0 x; y0 += A0 z;
w += D x;
(z,w) <- R(z,w);
y1 += A1 z; z += B1 x; y1 += A1 z;
w += E x;
(z,w) <- inverse(R)(z,w).
```

The first two reads cancel A0 applied to the original connector dirt and
leave the desired A0B0x in y0. Just before R, the pair is
`(z_in,w_in)+(B0x,Dx)`. After R it is
`R(z_in,w_in)+(B1x,Ex)`. The second read pair cancels the first component of
that transformed dirt and contributes A1B1x. Closing B1 and E removes the
entire signal. The final inverse restores **both actual dirty registers**.
Thus the endpoint is x,z,w unchanged and `yi += Ai Bi x`.

For complete call costs, the two closed echoes and candidate have bills

```
C_closed = I + 2c_B0 + 2c_B1 + 2c_A0 + 2c_A1,
C_carry  = I' + c_B0 + c_B1 + c_D + c_E + c_R + c_Rinv
               + 2c_A0 + 2c_A1.
```

Each c includes its actual coefficient/source access, arithmetic, routing,
frames, scratch restoration, heads and dispatch. I and I' include admission,
preparation, program storage and any remaining control. Sharing is favorable
only when `c_D+c_E+c_R+c_Rinv+(I'−I) < c_B0+c_B1`. A small h alone does not
establish this inequality. The generic existence proof does not provide cheap
charts or free physical memory.

## Complete pilot invoice

All four-bit matrix rows below are binary masks, least-significant bit first:

```
B0=(7,15,8,15),  B1=(11,15,8,15),
D=(11), E=(7), A0=(3,2,4,8), A1=(1,6,4,8).
```

A0 and A1 are noncommuting shears. The common three B rows are unchanged;
R simply swaps z0 and the one-bit companion w. Therefore
`R(B0x,Dx)=(B1x,Ex)` literally, and R is its own inverse. Each swap is three
scalar XORs. D and E each cost three XORs. Each complete B call costs twelve
and each A call five. Constants and row roles are supplied in both programs.

| Work | Closed echoes | Carried pair |
|---|---:|---:|
| Source B calls | 48 XORs | 24 XORs |
| A readout pairs | 20 | 20 |
| Companion D and E | 0 | 6 |
| R and its inverse | 0 | 6 |
| Total | **68** | **56** |

The candidate physically reserves 17 dirty bits: four source, four connector,
one companion and eight output bits. The closed comparator uses 16 bits; its
unused seventeenth bit is preserved in the common test space. One auxiliary
signal dimension is **one actual reserved dirty bit in this pilot**, not a
general claim that a full-size caller can borrow storage for free. E is chosen
redundantly to keep R a cheap swap; the dimension theorem permits other choices.
No claim of an optimal XOR circuit or optimal adapter tariff is made.

`RESULT.json` also prices a fully specified fixed-port movement tariff. Ports
are x=0..3, z=4..7, w=8, y0=9..12, y1=13..16; home is immediately before port
zero. A complete XOR visits its source and target and returns home, paying
`2(max(source,target)+1)` movement plus five units for dispatch, two reads,
one write and XOR. Every primitive and both swaps are included. The instruction
list is explicit; instruction storage/loading, validation and external matrix
preparation remain separate admission costs I,I'. This is a declared tariff,
not a measured tape trace or native machine certificate.

The exact movement totals are 1,156 versus 1,060; adding the stated gate
charges gives **1,496 versus 1,340** tariff units. Those totals exclude I,I'.

## Verification and decision

```sh
python3.12 -I -B scripts/research_package.py --package research/stabilized-dirty-chart
```

The primary implementation constructs actual invertible charts for every one
of the 256 ordered binary 2×2 map pairs, plus 512 deterministic 3×3 pairs.
The latter are fixtures, not a full census. The independent checker enumerates
**all** possible D and E for h=0,1,2 on the 2×2 domain and compares their
literal kernels, without importing the rank or chart constructor. This gives
the same minimum h for every pair. It also composes the complete pilot's
17×17 Boolean operator independently and checks its entire gate invoice.
The primary literal execution checks all dirty inputs and all inverses.
Deleting D, E, R, Rinv or B1 produces an explicit counterexample. Default
replay is read-only; source, receipt and output-path controls run on an
optimized Git-free export. No proof-assistant or hosted CI pass is claimed.

Credit: woklerx's reviewed PR1858 supplies the equal-kernel theorem and
carried-dirt protocol; Ross Richardson's PR943 supplies the original forbidden
alphabet, prefix model and 945-pairing baseline. Their source READMEs are pinned
in `SOURCES.json` at main b5ea56e0. The baseline was reproduced before this
scope, selected by nonce `ade63e0baaeccfa15a623b46e110958f`.
Prepared for ywz65 with substantial OpenAI Codex assistance, Apache-2.0.

The family decision is **finish this bounded changed-contract test**. Signal
dimension, all-dirty restoration and the finite XOR/movement invoice are
proved or checked. A general constructive R exists, but its efficient
implementation is unknown. Selected-caller lifetime, storage, frame routing,
native precision, full recursive cost and eventual supplier integration are
unknown; none are priced as zero. The pilot demonstrates a favorable local
bill under its explicit tariff. It does not authorize an unpriced construction
campaign or assert a new kappa.

## Open next questions

Find a pinned actual consecutive source-map pair for which the complete
D/E plus R/inverse and companion-lifetime bill fits the eliminated B calls.
Extract its actual frames and dirty state before synthesizing a chart. A
selected caller and a physically priced borrowing/routing contract are the
missing inputs; the dimension formula alone supplies neither.
