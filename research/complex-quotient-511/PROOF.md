# Construction and proof obligations

## 1. Exact predecessor and changed object

The input is PR4470 at head `b9a13c1673e0e9697de410de16e8bbf3207a7363`: its
credited THREE-base native word, the PR4441 helper-boundary retiming, the added
three-dimensional frame at B/480, and PR4470's joint helper boundary
(`research/joint-helper-lattice/PATCH.json`, source head
`322e0ec764aa7ef7801383feb1f656e460dd8bed`). `SOURCES.json` binds the live inputs
by Git blob and SHA-256.

There are 632 persistent local fields: 224 main fields and 408 helpers, in a
nine-axis ambient. `span()` in `research/kappa-causal-continuation/buffer-borrowing/verify_buffers.py`
requires `0 <= vector < 512`, so every frame is a subspace of `F2^9`.

The changed object is the ambient itself. The linear map

```
phi : F2^9 -> F2^8,   phi(v) = (v & 0xFF) ^ (0xFF if v & 0x100 else 0)
```

is surjective with kernel `span{511}`. `build.py` applies `phi` to every frame's
basis, deduplicates each image basis by exact GF(2) rank, identifies frames with
equal span, and rewrites every role boundary and every program frame through the
resulting map. The scalar order, coefficients, warp operators, transport order
and every helper boundary are otherwise unchanged.

## 2. Frame-coordinate invariant under the quotient

Let `C_F` be the source's exact canonical frame operator for subspace `F`, and let
`pi` be the linear quotient map on coordinates with `ker pi = span{511}`. For a
frame `F` write `phi(F)` for the image subspace. Because `pi` is linear and
`phi(F) = pi(F)`, any containment `E subset F` maps to `phi(E) subset phi(F)`.

A field at frame `F` carries `C_F` applied to its logical value. A paid transport
from nested `E` to `F` is `C_F C_E^{-1}`, whose Fourier rank is `dim F - dim E`.
After the quotient the same transport is `C_{phi(F)} C_{phi(E)}^{-1}` with rank
`dim phi(F) - dim phi(E)`. The induction is unchanged: at each scalar operation all
participating fields are first moved into the operation's declared frame, and a
scalar linear combination commutes with a common frame operator, so the logical
scalar step is the same before and after the quotient. Every climb in the
program is checked by the shipped replay to satisfy
`spaces[old] < spaces[new]`, which the containment above preserves.

The endpoints are what make the quotient admissible. The union of the 112 dim-8
main finals covers 510 of the 511 nonzero vectors, so `511` is the unique vector
outside all of them, and it is outside every main entrance as well. The only
frames it moves are therefore the full-ambient ones, which lose exactly one
dimension. The net effect on the main roles is

| family | before | after | rank |
|---|---|---|---:|
| ground entrance, dim-8 final | `0 -> 8` | `0 -> 8` | 8 |
| rank-1 entrance, full-ambient final | `1 -> 9` | `1 -> 8` | 7 |

The ground frame stays ground. The saving is therefore carried entirely by the
112 mains that end at the full ambient; the 112 that end at a proper hyperplane
are unaffected because `511` is outside every such hyperplane.

## 2b. The block stays 8

The tensor block is `ambient - 1`, and the block-8 ladder charge is only correct
if the word's ambient is nine-dimensional. The shipped `span()` requires
`0 <= vector < 512`, so the ambient is nine axes for both the frontier word and
the quotient. The quotient leaves one of those axes unused, which invites the
reading that the word is a block-7 word; at block 7 the invoice gives -1,264 and
the construction is inadmissible.

`build.py:pad_ambient` removes that ambiguity: it extends one helper's final
frame by the ninth axis. The helper gains one rank in the paid profile and one
rank in the helper profile, so the deficit is unchanged at 1,744, and the
artifact's frames span all nine dimensions. `verify.py` asserts
`ambient == block + 1 = 9` before pricing. The claim is therefore not "the
quotient is a block-8 word by assumption" but "the submitted word occupies nine
axes and its deficit is 1,744".

## 3. Complete local bill

The quotient passes the shipped evaluators unchanged, so the paid profile is read
off the replay rather than argued:

```
H_old = {4:28, 7:7, 8:47, 9:326}     helper rank mass 3,471
P_old = {1:2237, 2:388, 3:494, 4:147, 5:36, 8:8}   paid rank mass 5,327
H_new = {3:2, 4:26, 6:7, 7:47, 8:325, 9:1}  helper rank mass 3,090
P_new = {1:2034, 2:382, 3:412, 4:139, 5:36, 8:8}   paid rank mass 4,834
```

The local deficit `P - H` is 1,856 before and **1,744** after, a reduction of 112
= 112 mains x 1 rank. No productive credit is retained after removing paid work:
both profiles come from the same replay, and `P - H = 224*width + 64` holds in
both.

With the frontier's sixteen-pair controller, eighteen thick calls, fifteen thin
queries, block 8 and split 7, the invoice's rank surplus is

```
S = ladder - calls*(P - H) - thin
  = 35,840 - 18*1,744 - 1,680
  = 2,768                     (was 752)
```

and the two-constraint screen gives

```
emitted   complex kappa = 0.003020165977    (declared 0.00302015)
quotient  complex kappa = 0.012091850234    (+300.4%)
alpha slack 1.1e-16 ; gamma slack 0.0054   (both satisfied)
```

## 3b. The outer theorem kappa is capped by the BIT

This raises the complex supplier, not the theorem. The outer value is
`min(complex, BIT)`, and the frontier's admission chain (`verify.py` in
`research/joint-helper-lattice`) requires

```
atom 0.004 > ordinary 0.0034363 > admitted 0.0034 > TESTED
```

with `TESTED` the complex tested saving. A complex saving above `admitted =
0.0034` fails that chain, so the outer kappa is at most **0.0034**, which is
**+12.58%** over `0.00302015`. The contribution here is to remove the complex
side as the bottleneck: after it, the BIT sets the limit with 3.6x of headroom on
the complex side.

## 4. What is checked, and what is not

Checked by `verify.py` from the artifacts alone, with the shipped evaluators
unmodified: every frame independent with all vectors `< 512`; both directions
synthesize; 632/632 literal-replay endpoints exact in both directions against
`verify_buffers.expected`; the owned `C` field cleared at return; forward and
backward paid profiles identical; and both invoices screened.

Not claimed:

- This is not a multiplication theorem and not a full Lean verification.
- The ambient is nine-axis and the block stays 8, asserted by `verify.py`. No
  claim is made that the quotient changes the tensor block.
- Only THREE-base is exercised. FOUR-base and FOUR-extra are untested.
- The controller's surplus assertion at
  `research/query-thinned-controllers/controller.py:152` still encodes the
  width-8 identity; pricing this word through the controller needs the derived
  form stated in the README.
- Whether `511` is the unique removable direction, and whether the redundancy is
  a property of the Three-base identity rather than of this schedule, is open.
- At block 7 the same word is inadmissible (-1,264). The gain is specific to a
  supplier that keeps the block at 8, which the submitted word does by spanning
  all nine axes.
