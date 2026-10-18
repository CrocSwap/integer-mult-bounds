# Independent proof and finite circuit audit

The fixed witness in `WITNESS.json` gives **88 scatter ADDs and 11,061
complete local ADDs**. It retains all 306 target-undo ADDs, nine rank-seven
COPY calls, nine ERASE operations, one copy slot, and the original ordered
frame moves. This is a finite construction and an independent verification
of that construction. There is no minimum, new supplier exponent, selected
supplier admission, or full multiplication theorem claim.

## Fixed assumptions and provenance

The scientific input is Sagar Thakrar's PR1062 word at
`research/r439-bsection-stars-seed01/candidate.json.gz`, SHA-256
`b452d2c2b0b2a546d1105b1da9769aa78e5c54d6f00e97b30c77e3f54ce445ee`,
from base `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`. The scalar endpoint
model is linear over F2. All 111 input registers, 111 target registers and
439 helpers are arbitrary independent inputs. The additional COPY slot
is absent/empty before COPY and after ERASE, as in the inherited literal
COPY interface; this does not assume a newly supplied arbitrary dirty
scratch register.

The PR1062 target basis originates in Gareth Davidson's PR915 lineage.
PR2115 supplies the known split retaining undo indices `{31,51,52}` in D;
PR2279's all-ideal optimum concerns its stated split class. PR2356 proves
a fixed-order five-tap floor for column 7. This witness uses column 0,
so it does not contradict that floor. Historical results retain these
restrictions. The new witness is a solver nomination subsequently checked
with exact arithmetic, with no use of a solver's status as an optimality
certificate.

## Relocation and scatter identity

Use zero-based target indices throughout. The 306 target-basis preparation
gates are D records `[236:542]`. Their literal reverse is D records
`[653:959]`, the 306-gate undo. Each is an elementary zero-frame target ADD
`y_d <- y_d + y_s` over F2. The undo is followed by 236 helper-restoration
records; it is not the literal end of D. Those remaining records and all
of A touch no target register, which the independent verifier checks.
Consequently a target-only undo commutes with this continuation. The
published literal D stream is `D[:653] + D[959:] + kept`: the three kept
gates also move past the helper-only tail, with the same checked disjoint
support justification. The independent interpreter uses this exact order.

Let `U` denote the full undo operator, with matrices multiplying on the
left of a column vector. Let `K` denote the execution of undo indices
`31,51,52`, in that order. Let `H_0,...,H_302` be the remaining undo gates
in their original relative order, and set

    H = H_302 ... H_0.

The split obligation is `H K = U`. The independent checker applies both
sides to all 111 formal target basis columns. This is an exact equality
of the fixed finite matrices; it does not rely on an informal assertion
that the selected gates commute.

Let `b_j` be column j of the original 111-by-9 scatter matrix. For each
of the eight early totals, inject `a_j = H^(-1) b_j` at cut zero, using
one complete COPY/read/ERASE block at a time. In characteristic two each
elementary gate is its own inverse, so applying the deferred gates in
reverse order reconstructs these columns exactly. Their supports have
sizes

    j:       0   1  2  3  4   5   6  7   8
    |a_j|:  16  16  8  4  8  11  13  5  13.

Column 0 is instead copied after those eight blocks. For a tap into
target i at cut k, exactly k deferred gates have already executed; its
final response is `H_302 ... H_k e_i`, taking the product as identity
when k=303. The supplied ten taps are

    (0,13), (0,26), (0,34), (0,58), (0,79),
    (0,90), (0,95), (104,6), (126,24), (182,3).

Their sum is exactly `b_0`. The independent checker establishes this by
executing the taps and intervening gates forward from 111 zero rows.
It does not import a suffix-vector constructor or a search dictionary.

For an arbitrary target state z at the original undo entrance, and
arbitrary retained values `c_0,...,c_8`, the modified block therefore ends
with

    H K z + sum_(j=1..8) H a_j c_j
            + sum_(k,i tapped) (H_302 ... H_k e_i) c_0
      = U z + sum_(j=0..8) b_j c_j.

Thus it agrees with the original block on arbitrary target and retained
values, including every dirty contribution. The helpers and retained
sources are unchanged during the scatter block. A, B, C and the rest of
D retain their original arithmetic. This algebraic argument holds over
every F2-module once its fixed matrix equalities hold. It does not assert
an integer or real-valued endpoint equality for uncompiled ADD lifts.

## Complete arbitrary-input and accounting checks

`independent.py` reads only the pinned source word and the fixed witness.
It imports neither the primary checker nor a predecessor implementation.
Its full circuit interpreter uses sets of independent input labels and
symmetric difference. All 661 initial registers receive different basis
labels. The complete forward endpoint is checked to be

    input_i -> input_i,
    target_i -> target_i + input_i,
    helper_r -> helper_r.

The inverse stream is checked independently from another complete set of
661 input columns. ADD is self-inverse over F2; COPY and ERASE exchange
roles in the reverse stream. A live COPY records its exact source row
and source frame; ERASE requires the slot and unchanged source to agree
exactly. This checks every dirty helper coefficient and both orientations,
without random evaluations or a clean-helper restriction.

The interpreter derives each frame dimension over Q by fraction-free
integer row elimination, independently of the pinned exporter's rational
basis routine. Every ADD has equal operand frames, every forward move is
a strict frame inclusion, and each source and copy frame is checked.
The full ordered list of 2,911 MOVE events equals that of PR1062. The
longer live interval remains at zero frame and introduces no new role.
The copied retained source stays unchanged through all 303 deferred ADDs.

| independently checked quantity | value |
|---|---:|
| scatter ADDs | 88 |
| complete local ADDs | 11,061 |
| undo ADDs, kept plus deferred | 3 + 303 = 306 |
| COPY / ERASE | 9 / 9 |
| COPY ranks | nine instances of 7 |
| maximum simultaneous copy slots | 1 |
| paid rank profile | `{1:1323,2:1342,3:79,4:44,5:102,6:11,7:19}` |
| paid rank mass | 5,129 |
| forward / reverse positive majorants | 25,717 / 5,026,856 |
| inherited local / nine-stage guard bit lengths | 95 / 181 |

The two positive-majorant formulas are inherited unchanged:
`64 F^3 B^2 < 2^104` and `2^18 F^5 B^4 < 2^192`. Their evaluation here
checks the entire executed scalar record stream in both orientations.
This arithmetic does not by itself prove physical precision or a tape
implementation. The 94-ADD cut-zero listing becomes 88 because only its
16-tap column 0 is replaced, by ten taps. All other scalar and paid child
costs are included unchanged. The resulting full count is
`11500 - 527 + 88 = 11061`.

Five defect controls reject an omitted tap, a wrong tap target, an omitted
deferred undo, an undercharged COPY, and a changed live copy. Each control
must fail at its named obligation; unexpected acceptance is raised outside
the exception handler. Reordering the witness's tap list is accepted as
an equivalent presentation, because cuts determine execution chronology.

Reproduce the independent audit from the repository root:

```sh
python3 -I -B research/r439-single-copy-interleaving/independent.py
python3 -I -O -B research/r439-single-copy-interleaving/independent.py
```

The result marker is `PASS_INDEPENDENT_SINGLE_COPY_INTERLEAVING`.
The reported values were independently recomputed before comparing them
with the primary checker. Both agree on every quantity in the table.

The independently constructed events were also projected into the native
six-integer little-endian convention and compared byte-for-byte with the
primary checker's optional exported stream. All **13,990 records / 335,760
bytes** agree. The common SHA-256 is
`856873eac7d6d9d737e83a28c321b6e760ee183d9648bd98e80761b8d4dc9aba`.
Complete byte equality decided that check; the digest records the result.
This includes the precise placement of the three retained undo gates after
the helper-only D tail, rather than just an equivalent commuting order.

## Covered domain and remaining obligations

The completed result covers this one frozen source word, this witness,
the exact 111-target split equality, all 661 dirty input columns in each
direction, the single-slot COPY lifecycle, the complete frame stream and
the stated local accounting and inherited precision guards. The oracle
also supports the literal306 order for separately supplied witnesses;
that support does not constitute an exhaustive search or an optimum
statement for either order. No proof assistant or formal kernel was used.

Native phase-parser admission remains separate: the changed schedule
places target-to-target undo ADDs inside a live copied-total block. A
parser whose phase contract requires every scatter ADD to read the copy
does not automatically accept this exact scalar identity. Native replay,
full-call hosting and supplier binding, the semantic-D interface, all-size
compiler/tape realization, physical precision, and outer assembly remain
separate inherited or unexecuted obligations. The primary package owns
any additional native/exporter evidence; this independent audit makes no
claim that those obligations have been discharged.

Prepared by Ross Richardson with substantial OpenAI Codex assistance.
The independent checker was written by a separate verification agent in
the same AI-assisted run, not independently reviewed by a human. New
work is Apache-2.0; the inherited source word and notices are unchanged.
