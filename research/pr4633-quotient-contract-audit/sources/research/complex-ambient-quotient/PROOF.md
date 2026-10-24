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

The changed object is the ambient itself. For a nonzero kernel `v`, let `j` be the
lowest set bit of `v` and define

```
phi : F2^9 -> F2^8,   phi(x) = drop_j( x xor v if bit_j(x) is set else x )
```

`phi` is linear and surjective with kernel `span{v}`: two vectors collide exactly
when they differ by `v`. `build.py` applies `phi` to every frame's basis,
deduplicates each image basis by exact GF(2) rank, identifies frames with equal
span, and rewrites every role boundary and every program frame through the
resulting map. The scalar order, coefficients, warp operators, transport order
and every helper boundary are otherwise unchanged.

The kernel is `v = 153`. It is not chosen by hand: `scan_kernels.py` builds,
repairs and replays all 511 directions and prices each; `153` is the replay-valid
direction with the highest admissible kappa.

## 2. Frame-coordinate invariant under the quotient

Let `C_F` be the source's exact canonical frame operator for subspace `F`, and let
`pi` be the linear quotient map on coordinates with `ker pi = span{v}`. For a
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

Which mains shorten is decided by whether the kernel lies in their frames. Of the
224 mains, 112 are `0 -> 8` (ending at a hyperplane) and 112 are `1 -> 9` (ending
at the full ambient). For `v = 153`, measured on the base word:

| family | `v` in the frame? | before | after | rank |
|---|---|---|---|---:|
| 112 full-ambient finals | — (always) | `1 -> 9` | `1 -> 8` | 7 |
| 56 hyperplane finals | yes | `0 -> 8` | `0 -> 7` | 7 |
| 56 hyperplane finals | no | `0 -> 8` | `0 -> 8` | 8 |

No main entrance contains `153` (`B` starts containing it: 0 of 112), so no
transport is lengthened. The ground frame stays ground. Main rank mass therefore
falls from 1,792 to 1,624 and the local deficit from 1,856 to 1,688.

## 2b. Helper re-padding and the block

Two things must be restored after the quotient, and neither costs a rank of
surplus.

**The block.** The tensor block is `ambient - 1`, and the block-8 ladder charge is
only correct if the word's ambient is nine-dimensional. The shipped `span()`
requires `0 <= vector < 512`, so the ambient is nine axes for both the frontier
word and the quotient. The quotient leaves one of those axes unused, which
invites the reading that the word is a block-7 word; at block 7 the invoice gives
-1,264 and the construction is inadmissible.

**The full-ended helpers.** `native_extensions.embedded_cache_roles` requires

    roles = [i for i in range(224, 632) if start[i] == 0 and final[i] == 1]
    need(len(roles) == 213, '213 genuinely cold, full-ended native helper roles')

with frame 1 the full ambient. `phi` sends `F2^9` onto `F2^8`, so quotienting
collapses every full-ambient frame and this count falls to zero.

`build.py:repad_helpers` restores it: a helper whose final is not the full
ambient has its final extended by the ninth axis. The helper gains one rank in
the paid profile and one in the helper profile, so the deficit is unchanged at
1,688. `build.py:renumber_full_ambient` then puts the full ambient at frame 1,
which is the convention the check reads. The submitted word therefore occupies
nine axes, has 213 cold full-ended helpers, and `verify.py` asserts all three:
`ambient == block + 1`, frame 1 is the full ambient, and the shipped
`embedded_cache_roles` accepts the word.

## 3. Complete local bill

The quotient passes the shipped evaluators unchanged, so the paid profile is read
off the replay rather than argued:

```
H_old = {4:28, 7:7, 8:47, 9:326}                  helper rank mass 3,471
P_old = {1:2237, 2:388, 3:494, 4:147, 5:36, 8:8}  paid rank mass 5,327
H_new = {3:2, 6:7, 7:47, 8:139, 9:213}            helper rank mass 3,406
P_new = {1:2177, 2:424, 3:389, 4:147, 5:50, 8:8}  paid rank mass 5,094
```

The local deficit `P - H` is 1,856 before and **1,688** after, a reduction of 168
= 168 mains x 1 rank. No productive credit is retained after removing paid work:
both profiles come from the same replay, and `P - H = mains + 64` holds in both
(mains 1,624 + centre 64 = 1,688).

With the frontier's sixteen-pair controller, eighteen thick calls, fifteen thin
queries, block 8 and split 7, the invoice's rank surplus is

```
S = ladder - calls*(P - H) - thin
  = 35,840 - 18*1,688 - 1,680
  = 3,776                     (was 752)
```

and the two-constraint screen gives

```
emitted   complex kappa = 0.003020165977    (declared 0.00302015)
quotient  complex kappa = 0.015637149091    (+417.8%)
alpha slack 1.1e-16 ; gamma slack 0.0142   (both satisfied)
```

## 3b. No new outer kappa

This raises the complex supplier and claims no new outer kappa. The outer value
is `min(complex, BIT)` and is unchanged at `0.00302015`; the BIT sets it, and an
open PR already carries the `0.0034` admission. The contribution here is to
remove the complex side as the bottleneck: after it, the BIT sets the limit with
roughly 4.6x of headroom on the complex side.

## 4. What is checked, and what is not

Checked by `verify.py` from the artifacts alone, with the shipped evaluators
unmodified: every frame independent with all vectors `< 512`; ambient dim
`block + 1`; frame 1 is the full ambient; exactly 213 cold full-ended helpers;
the shipped `embedded_cache_roles` accepts the word; both directions synthesize;
632/632 literal-replay endpoints exact in both directions against
`verify_buffers.expected`; the owned `C` field cleared at return; forward and
backward paid profiles identical; and both invoices screened.

Not claimed:

- This is not a multiplication theorem and not a full Lean verification.
- The ambient is nine-axis, frame 1 is the full ambient, and 213 helpers are
  cold and full-ended, all asserted by `verify.py`. The quotient does not change
  the tensor block.
- **The main output charts are not preserved, and no consumer reads them.**
  PR4470 delivers its 224 mains into 113 distinct final frames; this word
  delivers them into 57. `controller.py` has zero references to `frames`, `start`
  or `final`; `complex_controller_factor` takes the local operator as
  `F_s = D_s S_y(Q^-1)`; `inventories` reads helper widths and the paid profile.
  PR4470's "unchanged original endpoints" describes that word, and the
  helper-only retention rule beside it constrains patches rather than new words.
  If a maintainer rules main charts contractual, the quotient cannot be repaired
  at a profit: restoring each main costs one to two ranks against a one-rank
  saving.
- Only THREE-base is exercised. FOUR-base and FOUR-extra are untested.
- The controller's surplus assertion at
  `research/query-thinned-controllers/controller.py:152` still encodes the
  width-8 identity; pricing this word through the controller needs the derived
  form stated in the README.
- Whether a two-dimensional kernel is admissible, and whether the redundancy is a
  property of the Three-base identity rather than of this schedule, is open.
- At block 7 the same word is inadmissible (-1,264). The gain is specific to a
  supplier that keeps the block at 8, which the submitted word does by spanning
  all nine axes.
