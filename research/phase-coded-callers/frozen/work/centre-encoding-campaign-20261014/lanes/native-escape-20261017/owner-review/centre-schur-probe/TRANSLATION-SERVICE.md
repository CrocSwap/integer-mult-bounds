# Centre translation services with one owned field

The actual translation operator `T=B Q_U^2 D` and its inverse give
centre-to-centre additive services with no native children. Each service
uses two existing eight-field FULL centre banks and one owned field C0.
The source bank is unchanged. C0 can have arbitrary input and is zero
at the output. All other data and borrowed fields are unchanged.

The inverse service needs 16 real division-by-2145 scans. Two literal
schedules give different scalar and translation costs. The exact odd
grid and its bit cost must be supplied when this word is placed in a
supplier. This packet does not give an inverse of `B Q_U D`.

## Pinned operator

The frozen `SCHUR-PROBE.json` has SHA-256
`ebff70f4ff3d28c345080a4d7b1d90cd952a6208b7f6449037b96dbf3531c024`.
It proves, for the actual selected set and graph,

```text
A = [0,7,20,27,36,46,57,111],
U = {0,...,111} minus A,
B = R_A^T R_U/4,         D = B^T,
T = B Q_U^2 D,
V = T^-1 = sum_delta K_delta tau_delta.
```

The inverse kernel has 4,544 nonzero scalar coefficients and 256
translation shifts. Every shift has odd weight. Its common denominator
is `8580=4*2145`. For each source component j there are exactly 256
source/shift groups. The integers

```text
w_(delta,i,j) = 8580 K_(delta,i,j)
```

are stored exactly through the pinned rational kernel. They have a
total of 14,288 nonzero binary digits, counted with multiplicity over
all coefficients. Their largest absolute value is 1,533.

At every width lambda, tau_delta applies the same nine-bit translation
delta in every tensor copy. The remaining 64 coordinates in each copy
are unchanged. The frozen XOR-character proof establishes this same
kernel for every positive width. No tensor power of an eight-by-eight
inverse matrix is substituted for the kernel.

## One-field inverse construction

Let x be the source centre bank and y the target centre bank. For each
source component j, in order:

1. Copy x_j to C0. Divide C0 by 2145. Halve C0 twice. It now holds
   `x_j/8580`.
2. Apply the required translations to C0. For each kernel numerator,
   add its signed binary digits to the corresponding target y_i.
   A binary digit uses a signed unit ADD from the current scaled C0.
3. Clear C0 after the last contribution from source component j.

This gives `y <- y+Vx`. Change the sign of each target ADD to obtain
`y <- y-Vx`. The eight source fields stay available throughout the
word, so C0 can process them in series. Only eight owned COPYs and
eight owned CLEARs are needed. The eight complex odd divisions are
16 real scans. No ninth field or additional centre bank is used.

This construction applies to any finite rational translation kernel
with a common denominator `2^a d`, where d is odd. One owned field can
hold one divided source component across all shifts and all target
broadcasts. The finite kernel controls the count; it need not be a
small count.

### Schedule with fewer translations

For each j, visit its 256 shifts in increasing order. If the old shift
is delta_old and the next shift is delta_new, apply the translation
`delta_old XOR delta_new`. Thus there is one map per group. Process
the numerator bits from low to high and double C0 between bit levels.
Restore the starting power of two after the group, except at the last
group, where CLEAR follows. The translation itself need not be undone.

There are 2,048 translation maps. The sum of the largest bit indices
over the 2,048 groups is 13,168. The sum for the final group of each
source component is 64. Thus the complete scalar price is

```text
8*14288 + 2*(13168 + 13168-64) + 32 + 32 = 166912.
```

The two final terms charge the 16 initial halves and the eight COPYs
plus eight CLEARs. Every source coefficient is included.

### Schedule with fewer scalar operations

For each j, visit all needed shifts at one binary level, then advance
to the next level. Keep the current scale and shift across transitions.
There are 80 doubles in total and no power restoration before CLEAR.
There are 8,944 nonempty bit/shift groups. Each transition has a nonzero
XOR shift, so all 8,944 maps are charged. The scalar price is

```text
8*14288 + 2*80 + 32 + 32 = 114528.
```

The source bank is unchanged in both schedules. Neither schedule needs
all eight owned core fields at once.

## Forward translation service

The forward operator has a shorter direct word. Clear C0. For each
ordinary port p:

```text
C0 += sum_j D_(p,j) x_j
C0 <- tau_(q_p) C0
y_i += B_(i,p) C0          for each nonzero B_(i,p)
CLEAR C0
```

Every ordinary graph column has four signed-half entries. This word
has 832 half ADDs, 105 CLEARs, and 104 translations. Its scalar price
is `832*10+105*2=8530`. The exact replay agrees with every coefficient
of the frozen forward kernel. Negating only the target ADDs gives
the inverse shear `y <- y-Tx`.

## Completed physical views

The service acts on two existing selected centre banks with FULL frame
F at the selected completed cut. The payload uses abstract rows 0 to 7
for x, 8 to 15 for y, and row 16 for C0. Rows 17 to 24 are arbitrary
borrowed test fields. The bank owners must be distinct. Each component
corresponds to its port in A.

For a selected stage, enter the actual serialized completed-X view on
both banks. Its forward order is route rho, then translation delta.
Leave with the inverse translation, then inverse route. Reverse the
owner order on exit. This gives 16 entering and 16 leaving view maps.

The checker verifies all 64 selected port-and-stage views. The exact
FULL phase polynomial is

```text
weight(rho^T f) + 2 delta.f - weight(f) modulo 4.
```

Every linear and quadratic coefficient vanishes. The zero constant
also vanishes. The stored inverse order and the orthogonal route are
checked. Omitting the translation fails in every case. Thus both banks
join the same FULL chart with the required phase. The word acts on
their contents in that chart. The source bank returns to its physical
input after the inverse view. The target returns to its prescribed
FULL frame with the stated content update.

The payload stores each literal body and all eight pairs of stage
wrappers. Its complete word is the concatenation `enter + body + leave`.
There are no omitted arithmetic instructions in that concatenation.
Translations within a body act only on C0. All other live owners are
outside the target set of every instruction.

No native child is called, so this service adds no recursive helper
endpoint obligation. It still requires one available owned field with
the stated discardable-input contract at the chosen cut. The packet
does not supply a new global ownership schedule.

## Coded centre exchange

Three complete additive shears give

```text
x += T y
y -= V x
x += T y

(x,y) -> (T y, -V x),          V=T^-1.
```

For example, after the middle shear,
`y = y_old - V(x_old+T y_old) = -V x_old`.
The last shear therefore leaves `x=T y_old`.
The inverse changes all three shear signs and sends
`(x,y)` to `(-T y,V x)`. The square is `-I`, and the fourth power is I.

The checker verifies the exact operator products in the Laurent ring
generated by T and V, using both inverse orders from the pinned kernel
proof. The emitted exchange bodies contain the actual three checked
shear words with the source and target bank indices exchanged where
required. One pair of physical view wrappers surrounds the whole word.

These outputs have their FULL physical frames. Their contents carry
the explicit codes T and V. This is a coded exchange, with its inverse
priced below. It is not a raw exchange or a completed decoder.

## Complete local invoice

The retained prices are eight real scalar primitives for a complex
signed unit ADD, ten for a signed-half ADD, and two for a COPY, CLEAR,
or one complex doubling or halving. Odd division is listed separately.

| Word, either sign | Real scalar primitives | Body translations | Real odd scans | Completed views | Native children |
| --- | ---: | ---: | ---: | ---: | ---: |
| Add T x | 8530 | 104 | 0 | 32 | 0 |
| Add V x, fewer maps | 166912 | 2048 | 16 | 32 | 0 |
| Add V x, fewer scalars | 114528 | 8944 | 16 | 32 | 0 |
| Coded exchange, fewer maps | 183972 | 2256 | 16 | 32 | 0 |
| Coded exchange, fewer scalars | 131588 | 9152 | 16 | 32 | 0 |

The body translations and completed views are separate charged map
applications. They are not included in the scalar column. No native
wrapper maps are needed. The fixed-odd charge is exactly 16 real
division-by-2145 scans for an inverse shear or an exchange. It is not
16 dyadic primitives. The accepted odd-grid backend must supply the
bit cost of these scans.

DIVIDE_ODD means exact rational division on an explicit grid with odd
factor 2145. It does not assert that an arbitrary integer numerator is
divisible by 2145. The coefficient ring is `Z[i,1/2,1/2145]`. Starting
on an input grid of odd height h, one shear or one exchange increases
the required prefix height by at most one. The inverse word divides
copies of eight unchanged source fields; it does not divide a value
which a preceding divided copy has modified. The first exchange shear
uses only dyadic arithmetic, and the last also uses only dyadic
arithmetic. No height bound for an arbitrary sequence of calls is
claimed here.

The exact maximum intermediate formal row one-norm is 53 for the
forward shear and 9073/715 for either inverse-kernel schedule. The
exchange has the proved upper bound 472511/715. For that bound, the
first source update has norm at most 53; the middle target update has
norm at most `1+53*(8358/715)`; its completed value has norm 8358/715;
the last update has norm at most `53+52*(8358/715)`.
This is a local coefficient bound, not a complete supplier precision
bound.

## Checks and scope

Run with one process:

```text
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/native-escape-20261017/owner-review/centre-schur-probe/check_translation_service.py
```

The first line is `PASS_ONE_OWNED_TRANSLATION_SERVICE`.

The exact sparse replay checks every coefficient for all 16 arbitrary
live inputs, one arbitrary owned input, and eight arbitrary borrowed
inputs. It checks both signs and both inverse orders for all three
shear bodies. It checks every literal invoice and all completed view
phases. Removing the odd division, translations, or initial halves
fails the claimed inverse-kernel output. Exchange correctness is a
separate exact composition proof from the checked full shear maps.

The frozen spectral packet, the minor service receipt, and all five
original source byte hashes are checked before use. The source hashes
and frozen spectral receipt are checked again after emission. The
payload has deterministic compressed and uncompressed hashes.
Normal Python and Python with `-O` produced byte-identical receipts
and compressed program payloads.

This local construction does not invert `B Q_U D`, supply a controller,
admit a complete supplier, or improve kappa. No owner-fill or interior
forward scan was run. Independent review of the new word is pending.
OpenAI Codex assisted the construction and exact checks. No PR, push,
or commit was made. Before any future PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
