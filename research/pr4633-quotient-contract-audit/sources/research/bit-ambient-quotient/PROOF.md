# Construction and proof obligations

## 1. Exact predecessor and changed object

The input is PR589's regenerated E8 word at
`research/kappa-rebuild/bit/sources/pr589-regenerated`: `WORD.json.gz` (pinned by
the SHA-256 recorded in the artifact), `records/frames.json` (636 frames stored by
annihilator rows) and `records/249-records.bin` (249 records, `<6i`:
`op, x, y, c, f, z`). The local record interpreter and the declared local bill
`{1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}` are those of
`research/kappa-rebuild/bit/mixed_productive_bit.py`, whose own `audit_local`
reproduces that bill from this word.

There are 661 persistent fields: `2V = 222` main fields and `R = 439` helpers, in
an eight-axis ambient. A frame's dimension is the dimension of the GF(2) nullspace
of its annihilator rows; `frame 1` is the full ambient.

The changed object is the ambient. For a nonzero kernel `v` with lowest set bit
`j`,

```
phi : F2^8 -> F2^7,   phi(x) = drop_j( x xor v when bit_j(x) is set else x )
```

`phi` is linear and surjective with kernel `span{v}`: two vectors collide exactly
when they differ by `v`. `build.py` maps every frame's vector set through `phi`,
deduplicates each image basis by exact GF(2) rank, identifies frames with equal
image, and rewrites every role boundary and every record's frame fields. Every
MOVE rank is recomputed as `dim(image(destination)) - dim(image(source))`. The
record order, the ADD/COPY structure and every helper boundary are otherwise
unchanged.

The kernel is `v = 150`. It is not chosen by hand: `scan_kernels.py` builds,
replays and prices all 255 directions; all 255 replay, and `150` has the highest
admissible kappa (next: `102` at 0.012370756966, `153` at 0.012297488831).

## 2. Frame-coordinate invariant under the quotient

A field at frame `F` carries the frame operator `C_F`. A chosen frame `E subset F`
carries `C_E`, and the paid transport between them has rank `dim F - dim E`.
Because `phi` is linear, `E subset F` implies `phi(E) subset phi(F)`, so every
nesting the records rely on survives and the transport's rank becomes
`dim phi(F) - dim phi(E)`.

The induction is unchanged: at each scalar step the participating fields are
moved into the operation's declared frame, and a scalar linear combination
commutes with a common frame operator, so the logical step is the same before and
after the quotient. The replay checks that directly — the arbitrary-column test
and the endpoint test are frame-independent value tests, and both are exact in
both directions.

Containment is what makes the quotient admissible: no MOVE is lengthened, because
`dim phi(F) <= dim F` for every `F`, and a move is shortened exactly when its
destination contains `v` and its source does not.

## 2b. Re-padding the full ambient and the block

Two things must be restored, and neither costs a rank of surplus.

**The block.** The tensor block is `ambient - 1`; the block-7 ladder charge is
correct only if the word's ambient is eight-dimensional. The ambient is eight axes
for both words (`span()` requires `0 <= vector < 256`), so the quotient leaves one
axis unused, which invites the reading that the word is a block-6 word.

**The helpers.** Every helper must be physically `D_I8` — start at ground, final at
the full ambient. `phi` sends `F2^8` onto `F2^7`, so quotienting would leave every
helper at dimension 7.

`build.py` restores both at once: the image of the full ambient is replaced by the
whole of `F2^8` again (the 7-dimensional image plus the unused axis). Every role
that ended at the full ambient ends there again, so helper ranks are preserved
exactly, helper finals are dimension 8, and the ambient is eight axes.

## 3. Complete local bill

The bill is read off the replay rather than argued:

```
emitted   {1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}          mass 5,129
quotient  {1:1198, 2:1255, 3:207, 4:86, 5:41, 6:23, 7:1}           mass 5,023
```

The paid mass falls by 106 ranks per call. With the frontier's sixteen-stage
controller, eighteen thick calls, fifteen thin queries, `ports = 111` and
`block = 7`, the invoice's rank surplus is

```
targets = 63,216 (helpers) + 154,290 (ladder)              = 217,506
paid    = 18*paid_mass + 1,665 (thin) + 122,766 (idles)

emitted   217,506 - (18*5,129 + 1,665 + 122,766) =   753
quotient  217,506 - (18*5,023 + 1,665 + 122,766) = 2,661
```

equivalently `S = 31,524 - 18*(paid - 3,512) - 1,665`, where 31,524 is the ladder's
own surplus (154,290 target mass minus 122,766 paid mass). The two-constraint
screen then gives

```
emitted   BIT kappa = 0.003464248972    (the frontier's declared BIT value)
quotient  BIT kappa = 0.012401086416    (+258.0%)
```

## 3b. The outer value becomes BIT-limited 0.012401

The outer value is `min(complex, BIT)`. With the complex supplier at
0.015637149091 (`research/complex-ambient-quotient`) and the BIT supplier here at
0.012401086416, the minimum is the BIT, so the outer kappa moves from 0.00302015
to **0.012401**, **+310.6%**.

That composition needs one contract change: `atom 0.004`, `ordinary 0.0034364` and
`admitted 0.0034` are declared literals in
`research/query-thinned-controllers/verify.py`, not functions of the supplier
word, and a 0.0124 supplier requires them raised. The complex side must also be
throttled to the BIT's value, since the admission chain requires
`admitted > TESTED`.

## 4. What is checked, and what is not

Checked by `verify.py` from the artifact and the pinned source word, with the
shipped record interpreter: 661 roles; ambient dimension 8; no helper final below
dimension 8; all 439 helper starts at ground; both directions replay with 24,305
ADDs and 9 COPY episodes; all arbitrary input columns exact; all 661 endpoints
exact; owned COPY cleanup exact; forward and backward paid profiles identical;
the source word reproduces the declared local bill; the emitted invoice reproduces
the frontier's BIT kappa; and the quotient strictly improves the screen.

Not claimed:

- This is not a multiplication theorem and not a Lean verification.
- **The outer value needs the admission literals raised.** The composition to
  0.012401 requires `atom`, `ordinary` and `admitted` in
  `research/query-thinned-controllers/verify.py` to be re-derived for a 0.0124
  supplier, and the complex side throttled to the BIT's value.
- **The frame charts are not preserved**: 636 frames become 117. The interpreter
  validates the word's own frame record, and `inventories` reads only the paid and
  helper profiles, so no consumer in this tree reads the charts — but a contract
  requiring particular charts would reject the word. This is the question raised
  for the complex quotient in #4604, and it is not settled here.
- Only one-dimensional kernels are explored. All 255 replay and cluster between
  0.0122 and 0.0124.
- Only PR589's E8 word is exercised; 292 other `h = 8` words are untested.
- The admission parameters are declared constants in
  `research/query-thinned-controllers/verify.py`; they are not derived from the
  supplier and are not raised here.
