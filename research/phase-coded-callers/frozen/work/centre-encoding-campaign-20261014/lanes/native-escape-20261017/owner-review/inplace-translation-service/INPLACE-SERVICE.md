# In-place inverse of the centre translation operator

The actual operator `T=B Q_U^2 D` has an in-place inverse on one
existing eight-field selected bank. The word uses one owned field C0
and no native children. C0 can have arbitrary input. It is zero at the
output. The eight live input fields are arbitrary. Every other field
is unchanged.

This construction uses new address-conditioned scalar scans. These
scans are not instructions of the old uniform ADD alphabet. The direct
stream implementation below uses a marked address counter. It does not
split a field into full temporary streams.

The complete common-chart word has 2,080 uniform real scalar units,
110,284 conditional real scalar units, 144 simultaneous translation
maps, and 16 real division-by-2145 scans. A physical completed-X call
also has 16 view maps. The odd-grid format and the bit cost of its
division scan remain explicit supplier obligations. This result does
not invert `B Q_U D`, supply a global lease, or complete a decoder.

## Actual operator and source contract

Use the retained selected ports and the actual source matrix:

```text
A = [0,7,20,27,36,46,57,111],
U = {0,...,111} minus A,
B = R_A^T R_U/4,        D = B^T,
T = B Q_U^2 D.
```

The frozen `SCHUR-PROBE.json` has SHA-256
`ebff70f4ff3d28c345080a4d7b1d90cd952a6208b7f6449037b96dbf3531c024`.
Its five source pins are retained in this receipt. The checker reads
the source R and q arrays again. It forms every actual character matrix
directly and checks both inverse orders against the frozen kernel.

At width lambda, each address has lambda copies of the 73-coordinate
chart. Let `g_delta` put delta in the first nine coordinates of every
copy and put zero in the other coordinates. Write `tau_delta` for
translation by this vector. Then

```text
Q_p^2 = tau_(q_p),
T_chi = sum_(p in U) B_p B_p^T (-1)^(q_p dot chi).
```

All 512 matrices `T_chi` are invertible integer matrices. Their inverse
entries have common denominator 2145. These statements concern the
simultaneous translation group, for every positive lambda. They do not
replace T by a tensor power of an eight-by-eight matrix.

For a physical call, take the eight selected physical X owners at a
completed local B output, where their frame is FULL. Supply one owned
C slot. The local word also accepts arbitrary C-slot contents because
its first instruction overwrites those contents. Apply the eight
actual completed-X views at the chosen stage before the common-chart
word. Apply their inverses after it.

If `V_s` is this diagonal set of views, the physical operator is

```text
V_s^-1 T^-1 V_s.
```

The common-chart operator is `T^-1`. These two descriptions are kept
separate. The entry view applies its route and then its translation.
The exit view undoes the translation and then applies the inverse
route. All 64 selected stage/port views are checked from their actual
serialized columns. The checker verifies their inverse direction and
the complete FULL phase identity. No global ownership or chronology
claim follows from this local cut contract.

## Walsh transform on nine global directions

For `0 <= j < 9`, let `g_j=g_(2^j)`. Let `ell_j(x)` be bit j in the
first copy of x. Then `ell_j(g_k)` is one when j equals k and zero
otherwise. In particular, the nine directions are independent at
every positive width. The addresses with all nine first-copy bits
zero form a transversal of the translation orbits.

Let `Z_j f(x)=(-1)^ell_j(x) f(x)` and `X_j=tau_(2^j)`. Define

```text
H_j = (Z_j+X_j)/2.
```

Here `Z_j X_j=-X_j Z_j`, while operators with distinct indices commute.
It follows that `H_j^2=I/2`, `H_j^-1=2H_j`, and
`H_j X_j H_j^-1=Z_j`.

The following literal word applies `H_j` to one live field x:

```text
COPY x to C0
TRANSLATE C0 by g_j
NEGATE x only where ell_j is one
ADD x += C0
HALVE x
CLEAR C0
```

On an orbit pair, with the first address selected by `ell_j=0`, this is

```text
(a,b) -> ((a+b)/2,(a-b)/2).
```

Omit HALVE to apply the inverse. No final multiplication by two is
needed. Each step overwrites C0 before use and clears it after use.
The copied field is translated; the live field stays in place.

Apply all nine forward steps to each of the eight fields. Call this
operator W. On each orbit,

```text
(W f)(z+g_chi) = (1/512) sum_h (-1)^(chi dot h) f(z+g_h).
W tau_delta W^-1 = multiplication by (-1)^(chi dot delta).
```

Thus the required inverse is

```text
T^-1 = W^-1 diag_chi(T_chi^-1) W.
```

The inverse Walsh steps use the reverse direction order. The identity
is an all-width operator proof. It uses the selector duality above,
not a sample at width one. The checker also reconstructs all 32,768
scalar kernel positions from the emitted inverse Walsh pair rule.

## Exact scalar mode word

The actual character matrices give 172 distinct matrices up to sign.
For each class, choose its sign so that the first nonzero entry is
positive. Exact integer row and column operations give

```text
L J R = diag(d_0,...,d_7),
T_chi = epsilon_chi J,
T_chi^-1 = (epsilon_chi/2145) R diag(2145/d_j) L.
```

L and R are unimodular integer matrices. The seven diagonal types are

```text
[1,1,1,1,1,1,1,1]       2 classes
[1,1,1,1,1,1,3,3]      48 classes
[1,1,1,1,1,3,3,39]     16 classes
[1,1,1,1,1,5,5,55]      8 classes
[1,1,1,1,3,3,3,165]    96 classes
[3,3,3,3,3,3,3,3]       1 class
[13,13,13,13,13,13,13,13] 1 class.
```

Every divisor divides 2145. No new odd prime is used. The payload has
all factors, all elementary row words, and the mode-to-class table.
The checker verifies `L J R=D` and the Smith divisor chain. It also
checks the order used to apply R to a column vector. Column operations
are converted to vector row operations in reverse order.

There are 5,802 integer factor gates. The largest absolute integer ADD
coefficient is 132. Each integer ADD is expanded into signed unit ADDs,
doublings of its source, and matching halvings. The source is restored
before the next factor gate. A swap uses three signed unit ADDs and one
sign change. Every expanded instruction has an explicit mode selector.

The diagonal multiplier `m_j(chi)=2145/d_j(chi)` uses one C0. Copy x_j
to C0. Double C0 through binary levels 1 through 11. At level k, add
C0 to x_j only in modes where bit k of `m_j(chi)-1` is one. Clear C0.
The multiplier is odd, so bit zero is zero. This gives the exact
integer multiplication without clearing the live field. Its selector
tables are finite and are stored in the payload.

Apply the right factors, then the required class sign. Finally divide
each of the eight live fields by 2145. All preceding mode arithmetic
is integral on integral inputs. This arrangement avoids additions
between fields with different mode-dependent odd grids. It gives one
common increase in odd height.

The checker replays the complete emitted mode word on nine formal
input columns at all 512 modes: eight live inputs and arbitrary C0.
It checks the exact inverse matrix, absence of the C0 input from each
live output, and zero C0 output each time. The first COPY in the full
word overwrites C0 before any instruction reads it. Both operator inverse orders are checked
against the directly rebuilt T matrix. No random matrix is substituted.

## Direct conditioned-stream backend

Two exact source files are pinned in the receipt:

- `upstream/build/sections/02-streams.tex`: the machine model, elementary
  stream operations, binary counter proof, and exact fixed-point scans.
- `upstream/build/sections/05-layers.tex`: the column layout, address
  sign wrappers, and the individual selected-bit kernel.

The first source permits a fixed pointwise map selected by specified
address bits. The second source applies exact arithmetic at a selected
bit. Their split/map/merge constructions show this capability, but this
word does not use their full-stream splits for a conditional scalar gate.

Use the existing binary record-address counter. On a second fixed
track, mark the nine first-copy positions. Keep their current values
in a finite 512-state control register. When an increment changes a
marked counter bit, change the corresponding register bit. The selector
tables then select a gate without rereading the complete address.

The markers can be placed in one pass over the counter after the nine
positions are prepared. This takes O(p) work for a p-bit address. The
source already charges descriptor preparation and head returns. In N
consecutive counts, bit j changes O(1+N/2^j) times. Increment carries
and counter-head returns therefore take O(N+p) work. No O(p) lookup is
performed for each record. The finite counter checks in the receipt
test the stated update rule at separated selected positions and across
carries; the sum above proves the general bound.

The data scan changes only the target coefficient record. If the
selector is false, it leaves that record unchanged. If the selector is
true, it performs the same exact arithmetic as the unconditioned gate.
For example, a two's-complement sign change complements the bits and
adds one with a one-bit carry. A signed unit addition uses the aligned
source record and a bounded carry. A power-of-two step shifts within
the guarded record. The source's fixed-point conventions include all
record reversals and head returns.

The additional storage is the marked O(p)-bit counter and bounded
arithmetic control. If the record order requires a record reversal, its
temporary record has O(p) bits and is cleared locally. No additional
field array is used. The existing aligned source and target streams
are the actual live fields. Each masked real scan has cost
`O(Nw+N+p)` for N records of guarded width w. This is O(V) under the
source record and descriptor contract. The constant is fixed because
the mode table has 512 entries.

The new mask control does not make the conditional gates old uniform
ADD instructions. Their arithmetic and their counter work are charged
here as a separate extension. Each of the 23,345 conditional complex
instructions scans all its addressed records, including inactive
entries. Source and target heads traverse inactive records too. No
cost reduction is taken from the small fraction of active modes.

Each instruction has a fixed number of real arithmetic passes. Across
the word, the counter term is at most a fixed multiple of
`110284*(N+p)`, in addition to those arithmetic passes. This bound
charges marked-counter control for every pass of all 23,345
instructions. It is not a new native-child charge.

## Complete local invoice and precision

Retain the source arithmetic prices: a complex signed unit ADD is
eight real scalar units; a COPY, CLEAR, sign change, doubling, or
halving is two. Conditional units have the same arithmetic price plus
the counter work just stated. These units are not exact machine-step
counts. Odd division and address maps are separate.

| Part | Uniform scalar units | Conditional scalar units | Translation maps | Real odd scans |
| --- | ---: | ---: | ---: | ---: |
| Forward Walsh | 1008 | 144 | 72 | 0 |
| Mode inverse | 208 | 109996 | 0 | 16 |
| Inverse Walsh | 864 | 144 | 72 | 0 |
| Complete common-chart word | 2080 | 110284 | 144 | 16 |

There are 23,345 conditional complex instructions. Of the conditional
scalar units, 288 are the Walsh selector-sign scans. The 144 simultaneous
translations use the existing map backend and its packed-layout cost;
they are not silently priced as single bit operations. A physical call
adds eight entry and eight exit view maps. It has zero native children
and zero native inverse wrappers.

DIVIDE_ODD means exact rational division on an explicit grid over
`Z[i,1/2,1/2145]`. It does not say that an arbitrary integer numerator
is divisible by 2145. This word requires 16 real scans of that backend.
Its bit cost must be inserted when the supplier's exact-grid format is
chosen. No free odd division is claimed.

If the input has odd height h, every prefix has height at most h+1.
The normalized forward Walsh needs nine extra dyadic fractional bits.
The mode word has integral prefixes before its final odd divisions,
and the inverse Walsh has no halving. Thus nine extra dyadic fractional
bits suffice for this word on its explicit odd grid.

The exact largest mode-prefix row one-norm is 462,848. The largest
completed mode-inverse row one-norm is one. A completed forward Walsh
has row norm one; its unhalved intermediate sum has norm at most two.
An inverse Walsh has prefix row norm at most 512. The complete word
therefore has row one-norm at most 462,848, including C0. Nineteen
integer guard bits suffice for this local growth factor. These are
local coefficient bounds, not a complete supplier precision theorem.

Intermediate live frames can differ from FULL. There are no native
calls in the word. Its final common-chart operator is a finite
translation kernel, which commutes with the common FULL frame. The
actual entry and exit views preserve FULL. The physical output is
therefore FULL, with the explicit centre operator stated above. No
ordinary source frame or extra centre-bank code is left unpriced.

## Verification and boundary

Run one process:

```text
python3 -I -B work/centre-encoding-campaign-20261014/lanes/native-escape-20261017/owner-review/inplace-translation-service/check_inplace_service.py
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/native-escape-20261017/owner-review/inplace-translation-service/check_inplace_service.py
```

Both commands must print `PASS_INPLACE_TRANSLATION_INVERSE`. Their
receipt and compressed literal payload must be byte-identical. The
checker uses explicit failures, not Python assertions. A control that
omits the odd divisions must fail.

The checker verifies the finite arithmetic and view identities. The
marked-counter and orbit arguments prove the width-independent stream
construction. This is not an executed end-to-end Turing-machine trace.
Integration must still bind an actual completed bank and C0 lease,
the fixed-odd format and cost, and all uses in the changed controller.
The singular `B Q_U D` operator is a separate problem. No complete
kappa value, child saving for a whole supplier, or decoder is claimed.
