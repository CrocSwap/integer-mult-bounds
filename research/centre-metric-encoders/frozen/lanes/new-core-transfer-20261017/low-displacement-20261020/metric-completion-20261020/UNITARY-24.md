# A unitary centre code with 24 output coordinates

The actual sixteen centre readers can be recovered from 24 output
coordinates of a Gaussian dyadic unitary code C on 112 ports.
The other 88 rows of C E equal the same rows of C. Each of these
88 rows has zero diagonal in the actual native mode basis.

The code and its adjoint each have a complete scalar word. Each word
costs 8,052 real scalar primitives and uses no extra field or odd
division. Both words pass all 1,280 real input columns. These columns
represent 640 arbitrary complex fields; the 528 fields outside the
code remain unchanged.

This packet proves the code, its scalar words, and its native support.
It also checks that the 24 selected target paths can be removed from
each pinned forward provider without a retained read of a removed
target. A complete replacement native word and a routed caller are
separate constructions.

## The eight-port change

Keep the large six-mode codes from the pinned 32-coordinate packet.
They use sixteen selected physical outputs and preserve the actual
physical pair closure. Change only the eight disjoint small blocks.

On one small block use the unnormalized Haar rows

```text
h0 = (1,1,1,1,1,1,1,1)
h1 = (1,1,1,1,-1,-1,-1,-1)
h2 = (1,1,-1,-1,0,0,0,0)
h3 = (0,0,0,0,1,1,-1,-1)
h4 = (1,-1,0,0,0,0,0,0)
h5 = (0,0,1,-1,0,0,0,0)
h6 = (0,0,0,0,1,-1,0,0)
h7 = (0,0,0,0,0,0,1,-1).
```

Normalize rows 0 and 1 by beta=(1+i)/4, rows 2 and 3 by 1/2,
and rows 4 through 7 by alpha=(1+i)/2. The normalized rows are
orthonormal.

Put v=(1,1,-1,0,-1,0,0,0) and R=I-v v^T/2. Since v^T v=4,
R is a real dyadic orthogonal involution. Since v^T 1=0,
R fixes the centre reader. Apply R to the input of the Haar code.

Assign Haar rows 0 through 7 to output positions

```text
(0,1,5,3,2,7,6,4).
```

Each noncentre row now omits its assigned input coordinate. Thus
its diagonal entry is zero. The first row is still beta times
the all-one reader. The complete block code is unitary, and

```text
1^T x = (2-2i) out_0.
```

Only one output field is needed for this small-block centre.
The field contains a normalized centre; the other seven fields
retain the independent contrast information.

## The actual 112-port code

Use the stored order of each pinned small clique. Its first port
is the one selected output. The large part and its actual pair
code remain as in the 32-coordinate packet. No abstract new port
placement is used.

The exact full matrices satisfy

```text
C* C = C C* = I,
C^-* = C,
(C E)_R88 = C_R88.
```

Let V contain the sixteen original centre readers. The stored
decoder is T=V C*. Every row of T uses only the selected 24
coordinates, and T C=V. The eight large readers use four physical
coordinates each. The eight small readers use one each. The large
supports overlap in their two complete physical pair matchings;
their union has sixteen ports.

The code has eight nonzero diagonal entries, all at the selected
small ports. All 88 ordinary diagonals vanish for both C and C E
in both the native mode basis and the physical basis. Every mode
entry stays in an original six-mode vertex or small clique.

This support permits an ordinary-row response C_R88 in the existing
off-diagonal grammar. It does not permit an all-hole response C:
the eight selected small diagonals are real exceptions.

## Literal scalar words and target paths

The program copies the closed large-port part of the frozen
32-coordinate component word. On each small block it then applies
the real reflection, the paid Haar row word with its stated output
assignment, and the explicit complex normalizations.

Every row exchange in the real factor word is paid. The complex
normalizations use only real component ADDs and signed binary
scales. The factor beta uses the alpha word followed by a binary
half scale on each component. No complex multiply primitive is
assumed.

The code and its inverse each contain 2,418 component instructions
and cost 8,052 real scalar primitives. The exact local
real-component row one-norm reaches 16 for C and 28 for C*.
The additional binary denominator heights are three and two,
respectively. These are instruction-boundary bounds; they do not
include a recursive child or rounding error.

For each actual forward provider, remove every event whose target
is a selected Y field. This removes 380 events, including 192
rank-one native calls. No retained event reads a removed selected
Y field. This is an exact path-isolation check, not a complete
replacement service. A new service must still add the selected
FULL progress, retune the ordinary scalar transfers, apply the
source code at a common FULL cut, and verify its complete endpoint.

## Validation and scope

The checker verifies both unitary orders, the complete centre
decoder, all ordinary row and diagonal identities, Gaussian dyadic
coefficients, native block support, and both provider path censuses.
Both scalar words pass all 1,280 real columns. A missing component
ADD is rejected in each direction. Their full real-component
inverse composition also passes.

Run into new directories:

```text
python3 check_twenty_four.py --out <new-directory>
python3 -O check_twenty_four.py --out <another-new-directory>
```

Normal and optimized payloads and receipts are byte-identical.
Independent review is separate. This packet does not prove a
complete supplier, recursive hosting, or a final cost improvement.

The root lane proposed the 24-coordinate lower-bound target and
the earlier positive unitary normalization. This lane found the
small dyadic reflection and output assignment, bound the actual
ports, and emitted the paid scalar words. The original native and
controller packets supply the centre readers and transfer supports.
AI assistance was used throughout.

No PR, commit, push, or publication is authorized. Before any future
PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
