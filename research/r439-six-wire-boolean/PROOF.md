# Finite circuit argument and complete cost

Each selected block uses the same six existing z registers at one unchanged
frame. An ADD over F2 is the transvection `x_d ^= x_s`, with distinct indices.
It is invertible and its own inverse. Let M be the old six-by-six Boolean map.

The builder reduces M to identity using row additions L and, in mixed mode,
column additions R. A zero diagonal pivot is made one by adding a remaining
row with a one in that column. The already completed columns are preserved.
The resulting identity `L M R = I` gives `M = L^-1 R^-1`. The emitted program
executes the accumulated column operations first and the row operations in
reverse chronological order. This constructs a Boolean-equivalent program;
it does not minimize over every possible factorization of M.

The verifier imports no elimination code. It separately compares both programs
on all 64 Boolean input vectors, covering arbitrary dirt in these six
registers. It evaluates six positive unit columns in each direction, replacing
every XOR by addition of nonnegative integers, and requires entrywise
domination in both orientations.

| Frame | PR936 A ADDs | New A ADDs | Paired A+C saving | Positive map changes? |
|---|---:|---:|---:|---|
| 269 | 17 | 14 | 6 | yes |
| 281 | 18 | 13 | 10 | yes |
| 283 | 13 | 12 | 2 | yes |
| 284 | 17 | 13 | 8 | yes |
| 288 | 13 | 12 | 2 | yes |
| 308 | 15 | 13 | 4 | no |
| 314 | 16 | 13 | 6 | no |
| **Total** | **109** | **90** | **38** | **five blocks** |

For any nonnegative incoming bound vector, entrywise matrix domination bounds
the new output by the old output. Every instruction within one such block is
a nonnegative addition, so intermediate coordinates are bounded by that
block's final coordinates. The two local matrix inequalities therefore also
control internal prefixes. All surrounding positive instructions are monotone.
This composes through the whole word in each direction, including the reverse
cleanup. COPY inherits its center's bound; ERASE resets its fresh temporary.
The independent whole-word interpreter and the native checkers recompute these
bounds rather than assuming them from the local certificate.

Only A and its required literal cleanup C change. Every selected program uses
all six old registers, and has no intervening external gate inside its block.
The six-register state at each block boundary is identical over F2. The source
geometry checker and native records independently confirm identical ordered
frame paths for all 661 registers. Thus there is no unpriced extra MOVE,
helper, source read, copy, erase, recursive child or frame. D, scatter, B and
every other payload field are identical to PR936. C is rebuilt as the exact
reverse of z-destination gates in A followed by B, at the full frame.

The unchanged source checker validates H1-H5 and U/J/K/C-inverse. In particular,
the original helper-only D remains compatible with its literal K extraction.
Full source and helper restoration, target `y+x`, and fresh temporary cleanup
are checked on every arbitrary-input column in both orientations. Preserving
the Boolean map suffices for the binary supplier; equality of the forward
positive integer transfer is not asserted for the five changed lifts.

Complete ADD costs include the 18,085 D injections and all scatter, A, B and C
instructions. Counts are independently recomputed from literal instructions
and native records: **24,305 / 23,711 / 23,673** for PR589 / PR936 / candidate.
The paid histogram remains
`{1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}`, with rank mass 5,129 and
nine copies of rank seven. For 5/9/11 stages the unchanged bridge costs are
666 / 1,998 / 2,664 ADDs and the fresh copy counts are 45 / 81 / 99. Every
stage executes the complete local word once, so the new saving is the stage
count times 38.

The candidate's absolute bounds are `F = 41,287` and `B = 833,084`.
The native local payload upper bound is exactly
`64 F^3 B^2 = 3126061681564822569360612352`, needing 92 bits under 104.
The pinned nine-stage controller's expression is `2^18 F^5 B^4`, needing
174 bits under its 192-bit charge. The verifier checks the source expression
and its eighteen-bridge assertion. This substitutes freshly checked local
bounds into the inherited expression; it is not a regenerated whole-hosted
invoice. No exponent improvement follows from removing common-frame ADDs
while leaving the paid recursive profile unchanged.

These are finite computationally checked identities and inequalities, not a
formal proof of the multiplication theorem or a claim that all shorter
six-wire or five-wire circuits have been excluded.
