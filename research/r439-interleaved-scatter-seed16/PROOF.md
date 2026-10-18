# A five-tap floor for one R439 scatter column

This is a computer-assisted finite optimality statement for two specified
linear circuits. It is not a formal proof of the multiplication theorem,
an all-order interleaving bound, or a new supplier exponent.

## Model and exact statement

The input is Sagar Thakrar's PR1062 word,
`research/r439-bsection-stars-seed01/candidate.json.gz`, with 111 targets,
439 arbitrary dirty helpers and 9 retained totals. `SOURCES.json` pins its
Git blob and SHA-256 at base `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`.
All indices below start at zero.

Its D section prepares a target basis E, reads helpers, and undoes E with
306 elementary gates. Each gate is `y_d <- y_d + y_s` over F2, at frame
zero. Let S be the original 111-by-9 scatter matrix. We consider column
`j = 16 mod 9 = 7`, with required final response `b = S[:,7]`.

There are two separate orders:

* **literal306:** defer all 306 undo gates, in their literal order.
* **ideal303:** keep undo gates `{31,51,52}` in D and defer the other 303
  in their original relative order. This is PR2115's known attaining split.
  The verifier independently checks that kept gates followed by deferred
  gates have the same full 111-by-111 operator as the original undo.

For either order, permit any number of taps `y_i <- y_i + c_7` before,
between or after its deferred gates. Here `c_7` is the same unmixed retained
total throughout the block. All 111 target destinations are allowed at
every cut, including destinations with zero initial scatter coefficient.
The copied value is available across the entire block in this favorable
model. Repeated taps are allowed and each costs one scalar ADD. The undo
gates and their order are fixed; no extra target mixing gate is free.

**Claim.** The minimum number of taps realizing b is exactly five, in
each of these two models. In particular, this single-column mechanism
cannot reduce PR2115's existing five-tap column to four taps. It does not
bound the other eight columns or arbitrary reorderings of commuting gates.

## Complete reduction to a finite dictionary

Write the deferred gates, in execution order, as G_0 through G_(L-1).
At cut k, exactly k gates have run. Define the suffix operator

    F_k = G_(L-1) ... G_k,    F_L = I.

A tap into target i at cut k has final response `F_k e_i`. By linearity,
an arbitrary interleaving has final copied-value coefficient

    sum_(k,i tapped) F_k e_i.

This identity follows by induction on the remaining gates, and holds on
every F2-module, not merely on sampled payload values. Neither the dirty
initial target state nor other independent copied values change this
coefficient. Thus every tap response belongs to the exact finite dictionary

    V = { F_k e_i : 0 <= k <= L, 0 <= i < 111 }.

Conversely, each dictionary element has an actual cut and destination.
Any finite selection can be executed in cut order while one copied value
stays live. Duplicate response vectors cancel in pairs over F2, so omitting
duplicate atoms loses no representation of smaller cardinality.

The primary checker builds every suffix column backwards. For a gate
`y_d <- y_d + y_s`, right multiplication updates column s by XOR with
column d. The independent checker first constructs F_0 by forward
set-valued row operations, then removes gates by right multiplication and
extracts every column at every cut. It imports no primary or predecessor
implementation. Both obtain identical complete dictionaries and digests.

## Exact exclusion of four taps and attainment

Let B2 contain zero, every element of V, and every XOR of two distinct
elements of V. Every sum of at most four atoms is the XOR of two B2
elements. Conversely, an intersection of B2 with `b + B2` supplies a
representation with at most four atoms. Therefore

    b has a <=4-tap representation iff B2 intersects (b + B2).

Both checkers exhaust these finite sets using exact integers, without
random projections, truncated hashes, floating point or a solver.
Hashes record reproducibility; full 111-bit values decide equality.

| order | cuts | tap locations | distinct responses | distinct B2 values | intersection |
|---|---:|---:|---:|---:|---:|
| literal306 | 307 | 34,077 | 415 | 83,624 | 0 |
| ideal303 | 304 | 33,744 | 412 | 82,435 | 0 |

The target, encoded with target i in bit i, is
`0x19e655a80154dadcda556a83eea5`.
Five taps attain it, with pairs `(cut, target index)`:

    literal306: (40,54), (75,5), (140,7), (178,88), (306,43)
    ideal303:   (39,54), (72,5), (137,7), (175,88), (303,43)

The primary checker XORs suffix columns. The independent checker executes
each witness forwards from zero. Together with the complete exclusion,
these computations establish the stated exact minimum for the frozen
circuits. They are not a proof-assistant certificate or a result for a
larger search class.

## Complete local witness and retained obligations

To embed a witness, remove the target undo from D, retain the specified
three gates there in the second case, and keep A unchanged. Copy/scatter/
erase all totals other than c_7 using the appropriate transformed listing.
Finally copy c_7, perform the fixed undo interleaved with its five taps,
erase c_7, and run the unchanged B and C continuation. Reordering the nine
copy blocks is valid here: their sources remain unchanged and their
target increments commute before the undo. No target has yet climbed.

All 306 undo ADDs remain charged. The schedule uses one existing temporary;
the longer lifetime adds no new role, source access, COPY or frame change.
The verifier checks the source frame at COPY/ERASE, exact equality before
ERASE, zero-frame operands, strict frame inclusions and the full ordered
MOVE stream. It then replays every one of the 661 arbitrary-dirty input
columns forwards and backwards through literal COPY/ERASE records.

The literal order has scatter cost 96 and complete cost 11,069 ADDs.
The ideal order has scatter cost 94 and complete cost 11,067 ADDs, matching
the existing split's count. Both retain paid profile
`{1:1323,2:1342,3:79,4:44,5:102,6:11,7:19}`, rank mass 5,129, nine
rank-seven copies and nine erasures. Direct positive-majorant replay gives
F=25,717 and B=5,024,524, hence 95 local bits and 181 nine-stage bits under
the inherited formulas `64 F^3 B^2` and `2^18 F^5 B^4`.

These are local algebra, frame and accounting checks. An old H3 scatter
parser does not express target-to-target undo gates inside a live COPY
block; the emitted records make that changed schedule explicit. This
note does not claim native phase-parser admission, a complete hosted
supplier invoice, an all-size compiler, tape/precision realization, or
outer assembly. PR2115's target-basis interface and the earlier semantic-D
line remain dependencies for any proposed adoption. The lower bound
itself needs only the pinned finite matrices and its stated tap model.

Known four-tap targets and an added target atom exercise the lower-bound
detector. Wrong taps, an omitted undo, corrupted copied values and an
undercharged COPY are rejected. The independent checker additionally
rejects omitted and wrong witness taps. Package-level controls run the
actual entry points on corrupted sources and a falsely stronger minimum.
