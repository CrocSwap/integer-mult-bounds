# Construction and proof obligations

## 1. Exact predecessor and changed object

The input is PR589's regenerated E8 word at
`research/kappa-rebuild/bit/sources/pr589-regenerated`: `WORD.json.gz` (pinned by
SHA-256 `e3e301e62bc2b41dbf1ceac0acf3d35824ebeab1848c5a2142d4577b109da52f`, which
matches `mixed_productive_bit.py`'s own `WORD_HASH`), `records/frames.json`
(636 frames stored by annihilator rows) and `records/249-records.bin` (249
records, `<6i`: `op, x, y, c, f, z`). The local record interpreter and the
declared local bill `{1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}` are those of
`research/kappa-rebuild/bit/mixed_productive_bit.py`.

There are 661 persistent fields: `2V = 222` main fields and `R = 439` helpers, in
an eight-axis ambient. A frame's dimension is the dimension of the GF(2) nullspace
of its annihilator rows; frame 1 is the full ambient.

The changed object is the ambient. For a kernel subspace `K` of dimension `k` with
annihilator basis `r_1..r_(8-k)`,

```
phi : F2^8 -> F2^(8-k),   phi(x)_i = r_i . x
```

`phi` is linear and surjective with kernel exactly `K`. `build.py` maps every
frame's vector set through `phi`, deduplicates each image basis by exact GF(2)
rank, identifies frames with equal image, and rewrites every role boundary and
every record's frame fields. Every MOVE rank is recomputed as
`dim(image(destination)) - dim(image(source))`. The record order, the ADD/COPY
structure and every helper boundary are otherwise unchanged.

The kernel is `span{150, 102, 255}`, dimension 3. It is not chosen by hand:
`scan_kernels.py` prices the dimension ladder and samples the solids. The value is
a plateau in the dimension — 445 of 455 sampled three-dimensional kernels replay
and all price at 0.032249423394893.

## 2. Frame-coordinate invariant under the quotient

A field at frame `F` carries the frame operator `C_F`; a chosen frame `E subset F`
carries `C_E`, and the paid transport between them has rank `dim F - dim E`.
Because `phi` is linear, `E subset F` implies `phi(E) subset phi(F)`, so every
nesting the records rely on survives and the transport's rank becomes
`dim phi(F) - dim phi(E)`.

The induction is unchanged: at each scalar step the participating fields are moved
into the operation's declared frame, and a scalar linear combination commutes with
a common frame operator, so the logical step is the same before and after the
quotient. The replay checks that directly — the arbitrary-column test and the
endpoint test are frame-independent value tests, and both are exact in both
directions.

No MOVE is lengthened, since `dim phi(F) <= dim F` for every `F`; a move is
shortened by the number of kernel dimensions its destination meets minus the number
its source meets.

## 2b. Re-padding the full ambient and the block

The tensor block is `ambient - 1`, and the block-7 ladder charge is correct only if
the word's ambient is eight-dimensional. The quotient leaves `k` axes unused, so
`build.py` re-pads the full-ambient image with all `k` of them: the 5-dimensional
image becomes the whole of `F2^8` again. Every role that ended at the full ambient
ends there again, so helper finals are dimension 8, helper ranks are preserved, and
the ambient is eight axes.

## 3. Complete local bill

Read off the replay:

```
emitted   {1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}          mass 5,129
quotient  {1:1020, 2:495, 3:75, 4:442, 5:143, 6:4, 7:12, 8:2}      mass 4,842
```

The paid mass falls by 287 ranks per call and its shape shifts into ranks 4 and 5.
With the frontier's sixteen-stage controller, eighteen thick calls, fifteen thin
queries, `ports = 111` and `block = 7`:

```
targets = 63,216 (helpers) + 154,290 (ladder)              = 217,506
paid    = 18*paid_mass + 1,665 (thin) + 122,766 (idles)

emitted   217,506 - (18*5,129 + 1,665 + 122,766) =   753
quotient  217,506 - (18*4,842 + 1,665 + 122,766) = 5,919
```

The two-constraint screen gives

```
emitted   BIT kappa = 0.003464248972    (the frontier's declared BIT value)
quotient  BIT kappa = 0.032249423394893    (+830.92% over the emitted word)

Against this package's own one-dimensional quotient, the frontier base
0.012401086416, the step is +160.05%.
```

## 3b. Where the composition stands

The frontier base for this package is its own one-dimensional quotient,
0.012401086416. With the complex supplier at 0.015637149091
(`research/complex-ambient-quotient`) and the BIT supplier now at
0.032249423394893, the outer `min(complex, BIT)` is the complex side. The BIT is no
longer binding and has 2.06x of headroom over the complex.

The complex side cannot follow with the same construction yet: `synthesize` in
`research/fresh-helper-boundary/native.py:85` hardcodes the centre transport's rank
as `8`

```python
e = ['center', 0, e[2], second[3], 8]
```

and the centre frames are dim-8 hyperplanes, so a kernel of dimension >= 2 always
shrinks them and the stored rank stops matching the frame dimensions. The
one-dimensional complex quotient avoids this because its kernel direction misses
the centre frames. Deriving that rank instead of fixing it at 8 is the change the
complex side needs.

## 4. What is checked, and what is not

Checked by `verify.py` from the artifact and the pinned source word, with the
shipped record interpreter: 661 roles; ambient dimension 8; the kernel basis is
independent and the declared quotient width matches its dimension; no helper final
below dimension 8; all 439 helper starts at ground; both directions replay with
24,305 ADDs and 9 COPY episodes; all arbitrary input columns exact; all 661
endpoints exact; owned COPY cleanup exact; forward and backward paid profiles
identical; the source word reproduces the declared local bill; the emitted invoice
reproduces the frontier's BIT kappa; and the quotient strictly improves the screen.

Not claimed:

- This is not a multiplication theorem and not a Lean verification.
- **The outer kappa does not move here.** The complex supplier sets it; this
  package moves the BIT supplier from the base 0.012401086416 to 0.032249423394893.
- **The frame charts are not preserved**: 636 frames become 65. The interpreter
  validates the word's own frame record and `inventories` reads only the paid and
  helper profiles, so no consumer in this tree reads the charts — but a contract
  requiring particular charts would reject the word. This is the #4604 question.
- Kernel dimension 4 replays but prices worse (0.0175); the plateau break is
  unexplained. Dimension 5 was not searched exhaustively.
- Only PR589's E8 word is exercised; 292 other `h = 8` words are untested.
- The admission parameters in `research/query-thinned-controllers/verify.py` are
  declared literals, not functions of the supplier, and are not raised here.
