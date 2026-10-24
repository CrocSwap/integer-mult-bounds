# Sixteen unitary centre outputs with divisor three

The actual sixteen centre readers admit a Gaussian rational unitary
code on 112 ports whose decoder uses exactly sixteen output fields.
Its entries have denominators dividing a power of two times three.
No entry needs a second factor of three.

The sixteen-coordinate count is the ordinary rank minimum. In
contrast, a unitary code with no factor of three in its denominators
needs at least 24 output fields. Thus the factor three changes the
possible coordinate interfaces. This is a representation theorem
and an actual matrix construction. It is not a native supplier.

The dyadic part of the construction has a complete scalar word and
inverse. Each costs 4,862 real scalar primitives and uses no extra
field. The final four small packing matrices still need their
separate component words, paid division scans, and grid admission.
Those obligations are assigned to the bridge-access lane.

## Pinned input

The actual reader V and response E come from
`new-core-transfer-20261017/low-displacement-20261020/metric-completion-20261020/twenty-four-v2-normal/UNITARY-24.json.gz`.
Its decompressed digest is
`9be7deb70acfc20d98408c84d59a24dbd6e2eddaea408958ec64b6003eb75f8c`.

The actual pair matrices and signed mode blocks come from
`signed-probe/METRIC-COMPLETION.json.gz` in the same source directory.
Its decompressed digest is
`88a9f75fa87b1a258d6465e309785c1aaec1be6393d46e51bc0a469e62f09e5e`.

The matrix and scalar arithmetic is imported from the preceding
independent review with digest
`a834f297f9cc82de9b29f4cd17ac762ed371d9a0b13bbac25b3430d2f87de25e`.
No producer interpreter is imported. All source geometry is retained.

## A dyadic preliminary code

Let alpha=(1+i)/2. On each actual physical pair, the real pair matrix
H has H*H=2I. Thus alpha H is Gaussian dyadic and unitary.
Apply these normalized pair matrices on the 48 large ports.

In each signed six-mode block, first apply its recorded input signs.
Apply H4/2 to the first four stored coordinates, where H4 is the
four-point Walsh matrix. Apply alpha H2 to the last two. The two
sum outputs occur at the first and fifth stored ports.

The corresponding actual physical centre reader has coefficients

```text
2(1-i), -2i
```

on those two outputs. To verify the normalization, the original
reader is d^T H. The normalized pair input is alpha H x.
The four-mode sum has decoder coefficient 2/alpha, and the two-mode
sum has decoder coefficient 1/alpha^2. These are exactly the two
displayed coefficients.

On each small eight-port clique, use ((1+i)/4) H8. Its centre
reader is 2(1-i) times the first output. Let Cpre be this complete
dyadic unitary code. It has sixteen large sum outputs and eight
small sum outputs.

This preliminary code differs from the native-compatible
24-coordinate code. It is chosen to make the odd packing explicit.
It does not inherit that code's zero-diagonal support.

## A four-field packing matrix

Define

```text
A = [[1,1+i],[-1+i,1]],
B = [[1-i,-i],[-i,1+i]].
```

Direct multiplication gives A A*=B B*=3I. Let P reorder four
coordinates as (0,2,1,3), and put

```text
R = (1/3) diag(A*,A*) P diag(B,B).               (1)
```

Then R is unitary. Its only non-dyadic divisor is three. Moreover,

```text
[2A,0] R
  = [[2(1-i),-2i,0,0],
     [0,0,2(1-i),-2i]].                         (2)
```

Indeed, multiplication by the first block of A cancels A*/3.
The first two rows of P diag(B,B) are the first row of each
copy of B. This proves (2) without a square root or an extension
of the scalar field.

Pair the eight large readers in their stored order. For each pair,
apply R to its four preliminary sum outputs. The new first two
outputs recover both readers through the decoder 2A. Their other
two outputs retain independent information.

Embed these four disjoint R matrices into a 112-port unitary
Rall. Define

```text
C16 = Rall Cpre.
```

The eight small sum outputs are unchanged. The centre decoder
therefore uses eight large outputs and eight small outputs.
The exact payload includes all four port lists, Cpre, Rall through
its disjoint factors, C16, C16*, and the complete decoder.

## Exact scope of the representation change

The full actual matrices satisfy

```text
C16 C16* = C16* C16 = I,
T16 = V C16*,
T16 C16 = V.
```

The union of the supports of T16 has exactly sixteen coordinates.
The other 96 response rows satisfy

```text
(C16 E)_R96 = (C16)_R96.
```

These identities were checked on every matrix entry. They do not
permit the other independent coordinates to be discarded.
All 96 ordinary rows in this particular assignment have nonzero
diagonal. The current off-diagonal native grammar therefore does
not implement this matrix merely from its centre count.

Every entry of C16 and C16* has binary denominator height at most
two and three-denominator height at most one. Some entries have a
factor three, so the distinction is real.

The lower bound from the preceding footprint theorem applies more
widely than the dyadic ring. It applies over every Gaussian
rational coefficient ring whose denominators are invertible modulo
three. The unitary encoder remains invertible after reduction, and
the actual real reader ranks remain 32 and 16. Thus a unitary
sixteen-coordinate encoder must contain a denominator divisible
by three. Other odd primes alone cannot remove this obstruction.

On the other hand, the rank of V over Q(i) is sixteen. No invertible
linear code with arbitrary inputs can recover those readers from
fewer than sixteen complex coordinates. Construction (1) reaches
that bound with a single factor three in each endpoint coefficient.

This establishes a sharp coordinate change between the two stated
coefficient classes. It is not a lower bound for nonunitary codes,
approximate recovery, promised zero inputs, or a different output
interface.

## Paid dyadic word

The literal Cpre word uses the actual signed pair matrices.
A real two-field Hadamard map is implemented as

```text
x <- x+y
y <- -2y
y <- y+x.
```

The signs from the actual pair matrices are paid before and after
that word. Walsh4 and Walsh8 are products of these pair words.
All permutations are fixed by the displayed port order; none is
inserted as a free circuit operation.

Multiplication by alpha uses the real-component word

```text
r <- r-s
s <- 2s
s <- s+r
r <- r/2
s <- s/2.
```

The inverse word reverses each component operation and its
coefficient. Each direction has 1,854 component instructions
and costs 4,862 real scalar primitives. Both directions pass
all 1,280 real input columns. The 528 outside complex fields
are unchanged and remain arbitrary.

The Cpre word has real-component prefix one-norm bound 16.
Its inverse has bound 8. Both have maximum binary denominator
height two. These bounds do not include the four rational
packing words.

## Access, division, and reuse obligations

The code and these scalar words are stated at one common type,
such as current I or completed FULL. They cannot be applied
across unequal holes without a separate access proof.
The code generally does not commute with the port-dependent Q.

For arbitrary dyadic input, divisibility by three is not promised.
The dyadic unitary Cpre is onto the dyadic input module, so its
four-field carrier inputs can be arbitrary dyadic values.
A component implementation must use an exact paid division
contract or a sufficient common input grid.

The bridge-access lane is checking the literal R and R* words,
code-image divisibility, root-grid cost, and restoration.
This packet claims none of those checks. The fact that C16*
is the exact inverse does not by itself price division scans
or prove a complete recursive grid.

The two scalar types, native responses, full phase lowering,
borrowed-state hosting, recursive entrance, and final code
removal remain open. There is no complete supplier or
integer-multiplication improvement in this packet.

## Reproduction and credit

Run into two new directories:

```text
python3 check_packing.py --out <new-directory>
python3 -O check_packing.py --out <another-new-directory>
```

Both runs must report `PASS_ACTUAL_ODD_UNITARY_PACKING`.
The freeze records their exact payload and receipt comparison.

The root lane supplied the footprint question and emphasized
representation changes. The core lane supplied the actual
reader and pair geometry. This lane derived the explicit
norm-three packing, its physical binding, and the dyadic
precode word. AI assistance was used throughout.

No PR, commit, push, or publication is authorized. Before any
future PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
