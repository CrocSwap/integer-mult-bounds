# The physical adapter of selected helper 759

**Evidence class.** This is a proof for one helper. The scalar-adapter identity
is derived from the published basis constructor and checked against the
selected word. The chart identity is the published lowering of one frame pair,
recomputed and compared with the frozen receipt. It is not an exhaustive
census of the 1,080 helpers, not a heuristic search, and not an application of
either rank-dependent fee theorem. No κ changes.

## Objects

The selected word is `research/shared-wire-split-composition/data/final.json.gz`,
the word admitted with PR #7000. It has 1,480 public fields and 71,261 events.
Public field 759 has entry frame 3 and exit frame 660. In the #6936 base word
used by `chart_delta.py`, the same field has entry frame 3 and exit frame 127.
Frame 3 is empty. Frame 660 has support `(5, 9, 18, 33, 64, 130, 256)`. Frame
127 has support `(1, 2, 4, 8, 16, 32, 64, 128, 256)`. The dimension gaps are

```
|660| - |3| = 7,    |127| - |660| = 2,    |127| - |3| = 9.
```

Exactly one public field has endpoint `(3, 660)`, namely 759, and exactly one
has endpoint `(660, 127)`, namely 1478. Field 759 is not a main field. These
are the head and the tail of the published split of helper 759. The witness
vectors in `data/split759.proof.json` are

```
a = e_759,                         b = e_759 - e_758,
c = e_759 - e_1472,                d = -e_758 - e_1472,
```

with `a·b = c·d = 1` and `c_759 = 1`.

## Scalar basis adapter

The published constructor `basis(c, d, p, f)` is used with `c_p = 1`, so it
emits no swap and no SCALE. It emits one ADD `p += v·j` for each off-pivot
nonzero of `c`, then one ADD `j += (-v)·p` for each off-pivot nonzero of `d`.
The off-pivot counts are 1 and 2, so the entry program `B0` has three ADDs:

```
759 += -1 · 1472     at frame 3
758 +=  1 · 759      at frame 3
1472 += 1 · 759      at frame 3
```

`BF` is the same program at frame 127. For `(a, b)` at frame 660 the off-pivot
counts are 0 and 1, so `BC` is the single ADD `758 += 1 · 759` at frame 660.
Reversing a program and negating its coefficients is its inverse. The split
inserts `B0^{-1}`, then `BC`, then the tail-renamed `BC^{-1}`, then the
tail-renamed `BF`. The tail rename sends register 759 to register 1478 and
leaves every other register fixed. The inserted program therefore has length
`2·3 + 2·1 = 8`, and it is exactly

```
1472 += -1 · 759      at frame 3
758  += -1 · 759      at frame 3
759  +=  1 · 1472     at frame 3
758  +=  1 · 759      at frame 660
758  += -1 · 1478     at frame 660
1478 += -1 · 1472     at frame 127
758  +=  1 · 1478     at frame 127
1472 +=  1 · 1478     at frame 127
```

Each of these eight ADDs occurs once in the selected word, at event indexes
`9, 10, 11, 42546, 42547, 71249, 71250, 71251`, and none of them occurs in the
#6936 base word. No other opcode or coefficient occurs in the program. Rebuilding `basis(c, d, 759, f)` at a frame label other
than 3 keeps the opcodes and the coefficients and changes only that label, so
the coefficients are not a function of the dimension gap 7 or 2.

This is the scalar physical adapter of the split. It is ordinary scalar work
in the sense of the construction review: eight coefficient-±1 ADDs, and no
MOVE.

## Whole-job chart adapter

Relative to the #6936 base, the chart-delta classifier introduces the pair
`(3, 660)` and does not introduce `(660, 127)`. The head pair is not a MOVE.
It is field 759's endpoint: forcing 759 into the main set removes the pair
from the introduced set. The tail pair is a new endpoint of field 1478, but
the same frame pair is already a MOVE in both words, four times in the final
word. The frozen receipt therefore has a new recipe only for the head.

The published lowering of `adjoint(frame 3)` followed by `frame 660` is the
rank-7 recipe whose native circuit is the right monomial, the Fourier child
on the first seven axes, and the left monomial:

```
D (33, 18, 12, 12, 18, 1, 0, 0, 0) / (1, 1, 3, 3, 3, 0, 2, 0, 2)
P (1, 144, 41, 37, 130, 64, 256, 45, 146)
X 97
phase 3
C_1, C_2, C_4, C_8, C_16, C_32, C_64
D (1, 18, 12, 12, 18, 0, 0, 0, 0) / (3, 3, 3, 3, 3, 2, 2, 0, 0)
P (141, 272, 5, 9, 18, 1, 32, 2, 64)
X 0
phase 0
```

`native_verify.recipe` of the frozen record equals
`adjoint(frame(frames[3])) + frame(frames[660])`. The child rank equals the
head dimension gap, 7. The inherited MOVE chart `(660, 127)` lowers at rank 2;
that recomputation is only a rank check. It is not a new recipe and it is not
a second fee.

This rank-7 circuit is the physical whole-job adapter of helper 759. It is the
factorization of that helper's own endpoint, hence of its productive target of
rank 7. The selected assumption `native_all_columns` still treats whole-job
adapters as retained hypotheses. Naming this circuit does not discharge that
assumption.

## What is not instantiated

A theorem of #7299 applies to a split only after a reading, a nonnegative flat
fee `c`, a rational slope `d`, and a nondecreasing concave tariff `φ` with
`φ(0) = 0` have been identified, with the physical extra charge equal to that
reading's formula `c + d φ(r_i)`.

The two objects above do not contain that identification.

- The chart circuit's only rank is 7, the head target's rank. The circuit is
  the factorization of that endpoint. This package does not identify it with
  an extra fee `c + d φ(7)`.
- The scalar program's coefficients lie in `{+1, -1}` and do not change when
  the frame label changes. For the identity tariff and slope `d = 1`, the
  piece values `φ(7) = 7` and `φ(2) = 2` are not coefficients of the program.
  The program also assigns no separate number to each piece: it is one shared
  list of eight ADDs. Reading two different rank-dependent charges out of it
  needs an allocation rule that the program does not contain.
- No ordinary per-ADD unit price is stored in either object. A later proof
  that those eight ADDs cost a constant `c` in the units of `φ` would be the
  case `d = 0`, where both #7299 readings reduce to the uniform-fee theorem.
  That unit price is not proved here, so `d = 0` is not instantiated either.

Therefore neither Reading A nor Reading B is applied to helper 759. The
obstruction is scoped to the executed adapter records and to the contract that
the fee parameters have to be exhibited by those records. It is not a proof
that every future pricing of this helper is impossible, and it is not a
statement about the other 1,079 helpers.

The fixed-paid-profile ceilings in discussion comment 19530156 are a different
question. This argument does not evaluate `18(7^p + 2^p - 9^p)` and does not
compute a split-depth ceiling.

## Controls

The checker rejects a left-monomial phase shifted by one, a Fourier child with
the last axis removed, a scalar coefficient changed from `-1` to `2`, a chart
classifier that hides field 759, and a forged selected κ equal to the previous
record `781451/250000000`. The selected file is read and not written.
