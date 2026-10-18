# R439 mini-node basis circuits

This finite bit-circuit contribution saves **20 scalar XORs** in the merged
punctured R439 word of [PR #589](https://github.com/CrocSwap/integer-mult-bounds/pull/589).
It replaces two phase-A mini-nodes and their literal reverse cleanup.
The complete word, including the unchanged scatter, goes from **24,305 to
24,285 XORs**. It uses the same 439 helpers, 111 live ports and nine retained
totals, and preserves every register's frame path.

This is a local circuit improvement. It does **not** certify a new recursive
coefficient bill, bit exponent or kappa. The selected record remains the #626
composition with #543's unpunctured R420 bit supplier, conditional
kappa `51110230636731/31250000000000000`.

## Reproduce

From the repository root, with Python 3.10 or later and no third-party packages:

```sh
python3 -B research/p111-mini-node-basis/verify.py
```

Expected output:

```text
PASS_P111_MINI_NODE_BASIS: 186 candidates; 20 scalar XORs saved; 661 dirty-input columns; identical frame paths and paid profile; independent interface check passed; 4 negative controls rejected
```

The command checks the input hashes, exhausts the stated search, reconstructs
the candidate in memory, compares it with [certificate.json](certificate.json),
and runs the retained independent checker. It writes no generated artifacts.
The certificate includes every replacement gate and the candidate's canonical
JSON SHA-256, so no platform-dependent recompressed archive is required.

## Result and exact search class

The object is the four D4 mini-nodes in
`research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz`.
These prepare the block contributions to the nine pseudo-target decoder totals.
They are additional machinery of the punctured word, not the R420 phase-B blocks
currently studied in other PRs.

| Frame | Original A indices, inclusive | Destination registers in matrix order | Original XORs | Minimum in class | Applied |
|---|---|---|---:|---:|---|
| 506 | 1986..1988 | 349, 340, 241 | 20 | 14 | yes |
| 507 | 1989..1990 | 360, 381 | 11 | 11 | no |
| 508 | 1991..1992 | 385, 368 | 11 | 11 | no |
| 509 | 1994..1995 | 444, 413 | 13 | 9 | yes |

The rank-one hoist at original `A[1993]`, `444 += 470` at frame 79, remains
outside the replacements. The later sunk gate from #589 also remains unchanged.

Write a mini-node's exact map as `y' = L y + B x` over F2, where `y` consists
of its destinations and `x` consists of its read-only external operands. Both
vectors contain arbitrary initial values. For every invertible destination
matrix `Q`, the search prices the following complete implementation:

1. Prepare `y <- P y`, with `P = Q^-1 L`.
2. Inject `y <- y + C x`, with `C = Q^-1 B`.
3. Recombine `y <- Q y`.

Thus the result is exactly `Q P y + Q C x = L y + B x`, including dirty
destination and helper inputs. No new helper, external write or source-access
operation is implicit. Every injection entry costs one binary XOR.

Breadth-first search over elementary row additions gives a shortest circuit for
each member of `GL(3,2)` and `GL(2,2)`. The score is
`distance(P) + popcount(C) + distance(Q)`. There are 168 choices for frame 506
and six for each other frame, **186 choices in total**. The stopping rule is
exhaustion of these four finite groups. Assignment seed **8**, drawn from OS
randomness, fixes the BFS generator order and hence ties between shortest
circuits. Matrix-score ties use lexicographic order.

The stated minima are only for this preparation/injection/recombination class.
They do not prove optimality among interleaved circuits, circuits with additional
wires or circuits that write external operands. Frames 507 and 508 give scoped
negative results for this class. The previous #589 search moved summands between
frames and used local Steinberg rewrites; this search changes the destination
basis within a frame and exhausts the small groups.

## Cost and verification boundary

| Section | Original scalar XORs | Candidate scalar XORs |
|---|---:|---:|
| A | 2,130 | 2,120 |
| B | 934 | 934 |
| C, full cleanup | 2,629 | 2,619 |
| D, dirty-helper compensation | 18,085 | 18,085 |
| Scatter | 527 | 527 |
| Total | 24,305 | 24,285 |

Each replacement uses the same operand union at the same frame. The verifier
also checks the complete ordered frame path of every register. The paid local
profile is unchanged:

```text
{1: 1323, 2: 1342, 3: 79, 4: 44, 5: 102, 6: 11, 7: 19}
```

The frame changes and copied ranks therefore stay the same. Source reads inside
the mini-nodes are charged in the XOR counts above.
The cleanup is rebuilt from **every** source/helper gate in the new A and the
unchanged B, so its cost includes the new basis preparation and recombination.
No recursive child is removed or made free. The unchanged paid profile supplies
no new moment saving.

The local symbolic checker compares every input column of each mini-node.
The inherited `wlib.py` then replays all 661 formal columns of the complete
word. The independent `xcheck_p.py`, imported unchanged, checks E8 labels,
636 closed frames, all nine retained copy ranks of seven, frame legality,
the complete F2 map, H1-H5 and the U/J/K/C interface conclusions. Every
non-A/C word field is checked unchanged.

Four controls address different failure modes:

- Removing the first frame-506 preparation gate corrupts the arbitrary-input map.
- Removing a cleanup gate fails the complete endpoint replay.
- Moving the first new gate to frame zero fails frame nesting.
- Reusing the old cleanup still passes the endpoint replay, but fails the
  required literal-reversal condition. Algebraic equivalence alone does not
  discharge H4.

There is a concrete coefficient tradeoff. With all local input norms set to one,
the forward cancellation-free destination row sums at frame 506 change from
`[9,14,8]` to `[9,10,14]`; at frame 509 they change from `[8,7]` to `[10,7]`.
These values are reproduced in the certificate. Componentwise coefficient
domination is false. The hosted nine-stage and eleven-stage prefix, coefficient
and recursive bills have **not** been recertified for this word. A claim about
an assembled supplier would have to perform that work, including both program
orientations. This contribution claims only the finite XOR reduction and the
specific unchanged identities checked above.

All inherited realization assumptions remain: mutable source bases and common
labels, the all-size compiler, whole-call hosting, compressed windows, precision,
tape, exact recovery and analytic transfer. Finite replay is not a formal proof
of the multiplication theorem.

## Provenance and coordination

Base commit: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
The certificate pins the consumed word and both checkers, plus the construction
generator and #589 move list. #589's reviewed source head is
`a5afc8c6169ea61ba7c51dfd3cade02cc7b13b46`; the checked bytes are those retained
at the exact base above. No pending PR is an input dependency.

Credit belongs to eumemic for [#543](https://github.com/CrocSwap/integer-mult-bounds/pull/543)
and [#555](https://github.com/CrocSwap/integer-mult-bounds/pull/555), and to
DreamingOfClouds for [#545](https://github.com/CrocSwap/integer-mult-bounds/pull/545),
[#510](https://github.com/CrocSwap/integer-mult-bounds/pull/510) and #589.
Their construction, checker and licensing notices remain at
[the retained source](../e8-bit-p111-tuned/NOTICE.md).
The #589 transport mechanisms credit Dugongue's #541/#548 and rohanarun's #542.

Concurrent [#670](https://github.com/CrocSwap/integer-mult-bounds/pull/670), head
`2e31fcad7f9ecc8b97039ecb2333e581fd725fa1`, studies a different R420 block.
[#713](https://github.com/CrocSwap/integer-mult-bounds/pull/713), head
`1a19af5c5ddb6de9797a6d085e5df0b90ed6d58b`, uses restored target bases in the
R420 dirt correction. Both are credited as related finite-circuit work. The
additional evidence here is the punctured mini-node construction and a complete
small-group search, not a claim of priority for XOR basis changes.
The [local sprint claim](CLAIM.md) records the selection and alternatives.

Contributor: GitHub `thakrarsagar`, with substantial OpenAI Codex assistance
for synthesis, implementation, documentation and an independent agent review.
New files are under the repository's Apache-2.0 license. No upstream source,
selected frontier, existing supplier or global generated artifact is changed.
