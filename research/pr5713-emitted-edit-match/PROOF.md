# The emitted PR5713 word matches its credited scalar edit

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

## Claim

Let `S` be the pinned PR5684 word and `E` the emitted word in
`research/p104-temporal-updates/WORD.json.gz`. Let the witness cuts, role,
removed events and four replacement ADDs be the pinned `WITNESS.json`. Then:

1. `E` is exactly `S` after deleting `MOVE 715,3,598` and `ADD 715,747,1`,
   rewriting `MOVE 715,598,396` as `MOVE 715,3,396`, and inserting the four
   witness ADDs at cuts 823 and 14983. Every other word field is unchanged,
   except the schema, which becomes `p104-temporal-updates/1`. The program
   has `25451 - 2 + 4 = 25453` instructions.
2. On `S`, the source functional of the removed ADD equals the sum of the four
   replacement reads. The common-frame and no-read hypotheses of the temporal
   lemma hold on `[823,14983)`. The functional has 105 rational coefficients.
3. Frame supports `[]`, `[491]` and `[13,70,416]` are subspaces of `F_2^9`
   of dimensions 0, 1 and 3, and they form a chain because
   `13 XOR 70 XOR 416 = 491`. Charging each `MOVE` by the absolute difference
   of those list lengths changes the local query profile by one H1 and one H2
   removed and one H3 added. The emitted profile is
   `2184 H1 + 459 H2 + 495 H3 + 92 H4 + 159 H5 + 22 H6 + 15 H7`.
4. The retained native and physical-caller objects in `RESULT.json` are
   summaries of 377 and 595 bytes. Their payload hashes are not the SHA-256 of
   any file in the package or of any member of the nested PR5678 source
   archive. This certificate does not replay native phase, the physical caller,
   or the factor of 18 forward calls recorded in that summary.

No new κ is claimed. Selected κ stays `781451/250000000`.

## Scalar identity

Number fields by the predecessor order: 743 public fields, then 9 owned fields.
Start from the public identity rows and the recorded initial frames. Each
instruction acts as a straight-line update:

- `MOVE` changes only the target frame;
- `INIT` and `CLEAR` erase the target row and set or clear its frame;
- `SCALE` multiplies the target row by the recorded coefficient;
- `COPY` replaces the target row by that coefficient times the source row;
- `ADD` adds that coefficient times the source row into the target row.

Run this replay from the start of `S` through cut 14983. At each witness cut,
before the event at that index, the role and the replacement source have the
witness frame, and the replacement coefficient is added into a total. At the
removed event, the same rule records the source functional of
`ADD 715,747,1`. Between index 823 inclusive and 14983 exclusive, no `ADD` or
`COPY` reads field 715, and 715 is not the target of `SCALE`, `COPY`, `INIT`
or `CLEAR`.

The two accumulated dictionaries are equal and nonempty. Their canonical
coefficient list has SHA-256
`cddffb3e9a025e4a68c44ef66cc5c88b2d8eb88c6180415d7552f04ff6a48689`, the same
digest stored on the author receipt. Equality of the dictionaries is the
identity; the digest is only a cross-check. Changing one replacement sign, or
deleting the last replacement, makes the dictionaries differ.

The temporal lemma then applies verbatim. The four inserted ADDs contribute
the same source functional as the deleted ADD, the target is not read inside
the interval, and every other field keeps its original trajectory. At cut
14983, before the next read of 715, the target difference is zero.

## Program and local rank

The edit above is a literal list operation. Comparing it with `E["program"]`
is equality of finite JSON lists, not an author-constructor import. Deleting
the merged `MOVE 715,3,396` from `E` fails that comparison.

Each frame integer is a vector in `F_2^9`, written as an integer below 512.
The three supports are independent of dimensions 0, 1 and 3, and the one-vector
space of frame 598 sits inside the three-vector space of frame 396 by the XOR
relation above. The empty space sits inside both. A `MOVE` from frame `a` to
frame `b` is charged `abs(len(frames[b]) - len(frames[a]))`. Along this chain
the two deleted transports have ranks 1 and 2, and the merged transport has
rank 3. Counting every `MOVE` in `S` and in `E` gives the stated delta and the
stated emitted profile. The eight dimension drops of size 7 in the unchanged
transport set are what brings the H7 count to 15.

## What remains outside the equality

`RESULT.json` records `full_calls = 18` and therefore suggests a global change
of `-18 H1 -18 H2 +18 H3`. That factor is not re-derived here. The native
object names 2,917 distinct maps and stores one SHA-256, and the caller object
stores another. Neither preimage occurs among the package files or the nested
archive members, and neither object contains an event-length trace. Adding an
event list changes the native key set and is rejected. Complete native,
caller, ordinary, compiler and outer admission stay open, as do the five
selected framework assumptions.
