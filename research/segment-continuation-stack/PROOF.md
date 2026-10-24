# Delimited continuation primitive

This is a written all-size proof for `Controller` in `stack.py`, with exact
finite corroboration in `verify.py`. It is not a proof-kernel certificate or
a compilation of the entire retained PR2250 source interpreter.

## Contract and finite control

Fix k=16 physical payload tapes. Each has an arbitrary inaccessible ancestor
prefix, a local delimiter `|`, a contiguous binary word of length s_i, and
blanks thereafter. Its head is h_i cells after the start, 0 <= h_i <= s_i.
An absent role has s_i=h_i=0; a present role may also be empty. A 16-bit mask
specifies presence. No alias between any two of the nineteen physical tapes
is allowed. The source/caller supplies this well-formed entry state.

The remaining three tapes are:

* `control`, whose head is at the blank just after the current stack top;
* `descriptor`, with its own local `|`, an opaque binary word of length d,
  and its head at that word's beginning;
* `reverse`, an empty scratch segment with its head just after its local `|`.

All bodies have no internal blanks. Initial local markers and tape identity
are entry conditions. There is no supplied absolute position, frame length,
parent pointer, numeric h_i or numeric s_i available to the controller.

`Controller` uses only current-symbol reads, one-symbol writes, and moves
by +1 or -1. Its other variables are a symbol from a nine-symbol alphabet,
a role index in {0,...,15}, and a mask in {0,...,65535}. Fixed `range(16)`
loops can be unrolled. Helper call depth is fixed and independent of nesting;
the helper return labels can be duplicated at their finitely many call sites.
Thus this is a constructive finite-control program, although we do not emit
a flat transition table or formal compiler certificate. The Python `Tape`
dictionary, integer head, meter and visited-set are simulator internals;
no controller method reads those fields. The syntax check is only a regression
guard on that access boundary, not a proof of finite-state expressibility.

`push` consumes the current descriptor into the control tape, parks the
payload heads, installs child delimiters and sets the mask to zero. The
caller may perform successful local binary child work, including arbitrarily
many properly nested push/pop pairs. It must preserve the stack and its
payload suspension delimiters and leave reverse scratch empty. At `pop`,
each current child payload has finite size t_i and a head g_i in [0,t_i];
the current child descriptor has size e and head g_D in [0,e]. All intended
child outputs must already have been delivered: pop erases every child body.

The postcondition is exact restoration of all parent words, parent physical
head positions, descriptor and its head, mask, older control symbols and
control-head position. Every symbol of this new frame and of child/scratch
work is blank. Visited blank cells are not claimed to be deallocated.

## Frame grammar and push invariant

Let H_i=s_i-h_i and H=sum H_i. The appended frame is exactly

```
[ descriptor : b_0 u^H_0 ; b_1 u^H_1 ; ... b_15 u^H_15 ; ]
```

where b_i is the presence bit. Its length is

```
F = d + H + 2k + 3 = d + H + 35.
```

The delimiter alphabet is disjoint from the descriptor's binary alphabet.
Zero distance is the empty run of `u`, including an occupied empty role.
There is no ambiguous zero-width binary-integer header.

The descriptor loop copies each bit forward to control, erases it from the
descriptor tape and moves one cell right on both tapes. At its first blank,
the descriptor tape is blank from its marker to that head. The erased-rewind
loop walks left to `|` and one cell right, so descriptor is empty at its entry
head. It never visits the descriptor's ancestor prefix.

For role i, after j iterations of its scan, the payload head is at h_i+j
and exactly j `u` marks follow b_i. The parent symbols are only read, never
written. The first blank occurs precisely at j=H_i. Writing `|` there and
moving right establishes an empty child segment. The suffix `;` closes that
role. Consequently the grammar and all child entries hold at the end of push.

Unary H uses more header space than a binary offset. The relevant bound is
H <= sum s_i: the original local suspension already moves H cells to park
the heads. This representation exchanges logarithmic header space for a
fully local linear construction and inverse. It claims no improved constant
over a compiled binary counter implementation.

## Cleanup and pop invariant

For a contiguous local binary word of length t and current head g, `clear`
walks left to the nearest `|`, then right to the first blank while erasing
every bit, then left through those erased blanks to the same marker. It
returns one cell right of the marker. No ancestor symbol left of the marker
is visited. This applies also to t=g=0. Therefore the first part of pop
establishes empty child bodies with their heads at their origins.

`take` moves the control head one cell left, reads that symbol, erases it
and leaves the head at that cell. After checking `]`, pop handles roles in
reverse order. Each `;` is consumed. The corresponding payload head is one
cell right of the child delimiter, so moving left and erasing that delimiter
leaves the head at the parent's end s_i. For each consumed `u`, the payload
head moves one cell left. All H_i such cells belong to the original binary
parent word. The next symbol is b_i, and the head is now s_i-H_i=h_i.
Restoring b_i into the fixed mask restores the complete role state. Roles
are distinct tapes, so one restoration cannot disturb another.

After all sixteen roles, the next consumed symbol is `:`. Reading and erasing
descriptor bits backwards until `[` writes the reversed descriptor onto
`reverse`. The beginning marker is consumed, leaving the control head at
exactly its old blank top. No older control symbol is even read. Walking
backward on reverse copies bits forward onto descriptor and erases reverse;
both return to their local origins. The two reversals recover the original
descriptor, including empty and nonpalindromic descriptors.

This proves one matched push/pop. Induction on a finite properly nested call
tree proves the same invariant at every depth: a successful inner pair
restores the state in which its caller resumes, and the outer pair's proof
then applies. The induction is in the proof, not an allocated runtime frame
or a Python recursion stack in the controller. The external caller schedules
push/pop; its program counter and arbitrary object state are not supplied by
this primitive.

## Complete action invoice

Count each symbol read, symbol write (including blank erasure), and unit
move as one action. Comparisons and finite-control updates are represented
by a fixed finite expansion; this is an exact tape-action invoice, not an
exact count of Python instructions or a flat multi-tape transition table.

`emit` uses three actions and `take` uses three. `rewind` on a word with head
h costs 2h+3; erased rewind from its end costs 2t+3. Thus `clear(t,g)` costs
exactly 2g+5t+7. This includes the tests of the terminal blank and local marker.

Directly counting every loop, delimiter, failed loop test and rewind gives

```
push = 8d + 5H + 9k + 13
pop  = 14d + 5H + 9k + 16
       + sum_i (2g_i + 5t_i + 7) + (2g_D + 5e + 7).
```

The standalone reverse-scratch blank test is included in pop. Put
W=sum_i t_i+e. Since g_i<=t_i and g_D<=e, the total satisfies

```
push + pop <= 22d + 10H + 25k + 36 + 7W
           <= 24d + 12H + 32k + 64 + 8W.
```

The latter is the exported conservative `action_bound`. The checker also
compares the measured counts to the sharper two exact formulas, so a broken
meter cannot pass merely because the conservative inequality has slack.
Child computation, producing its descriptor, and delivering a useful child
output have their own bills and are excluded; all child erasure performed by
pop is included in W. No claim is made that arbitrary output delivery is free.

All these costs are independent of ancestor lengths. If the caller separately
establishes d+sum s_i+W=O(V), the primitive costs O(V). For e_node>=1 and
0<a_2<1, this is absorbable in the predecessor's stated
O(V e_node^(1-a_2) polylog p) nonchild allowance. This implication does not
establish those size premises for the full actual packet, supply a numerical
production tariff or prove a complete stopped recurrence.

There are always nineteen physical tapes. The live control length is the sum
of F over active frames. Reverse scratch needs at most the returning frame's
d bits. Control and reverse positions are reused on later calls; their
visited high-water extents are bounded by the corresponding maximum active
lengths, not by the sum of all historical calls. Parent payloads stay in place,
with one new delimiter per role. Full caller space also includes child work,
old visited cells, source handles, counters and any output-transfer workspace;
this local statement is not a complete caller storage bound.

## Source binding and limits

PR5329's `Arena.child` saves `(origins, parents, descriptor)` in `frames`.
Its read/write/move charge `6D` assumes already known frame boundaries. This
primitive supplies actual local control delimiters and head restoration for
its sixteen-role binary segment contract. It deliberately changes the header
encoding: no numeric size or head needs to be decoded to move a physical head.

The calibration executes the unchanged retained `compact.execute` at two
nested levels, for both source field orders and complete reduced f=2,
K=G=1 rectangles. All sixteen enclosing roles contain nonzero-length dirty
data, with a mix of zero and nonzero heads. The Python `SourceRole/SourceArena`
facade carries logical sizes/handles and uses weak references for source
lifetimes. It is not part of the finite-state controller theorem. Snapshot
lists, absolute-address observers and expected operator outputs are test
oracles inaccessible to Controller. In particular, this does not compile or
serialize source Python objects, counters or return PCs.

The source-bound descriptor identifies event 8814, family 65689 and the
offset-426/phase-1 right recipe. Those are bindings to retained provisional
inputs, not a reconstruction of production dispatch. This package does not
execute the actual nine-bit phase/affine production recipe or an e=147 packet.
PR5329 retains those separate phase-restriction checks. Recursive C, actual
child-output installation, complete source lifetime compilation and native,
ordinary, precision/stock/outer admission remain open.

Malformed-frame controls test specific detected failures and semantic mutants;
this is trusted owned stack storage, not an authenticated corruption-resistant
codec. On invalid input, failure is not transactional and no preservation of
ancestor data is promised. Every theorem above assumes the stated well-formed
entry and callee contract.
