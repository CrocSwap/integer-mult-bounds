# Retained backing of the literal elementary interchange

This answers the retained-backing question in JoyboyBrian's
[PR5188](../literal-elementary-interchange/README.md), at source head
`bffbe6f4b31c102bbf53d12ebbefde6c1a86337a`. It gives exact capacities for
that unchanged program's fifteen private tapes, including erased backing
across varying successful calls. Its all-width interchange semantics and
instruction bound remain predecessor results; they are not reproved here.
The input hashes and source provenance are recorded in `SOURCES.json`.

## 1. Domain, storage measure, and history

For one call let `H>=0`, `A,G,S>=1`, and `V=A*4^H*G*S`. The five borrowed
ports have the source's canonical binary descriptors and `V` binary payload
cells, supplied at their required heads. All borrowed and private roles are
disjoint. A live owner's fifteen private tapes have a LEFT marker at index
zero and blank bodies at each call boundary. They may retain arbitrary
finite blank backing beyond the marker.

A successful history consists of one `init`, followed by finitely many
admitted `run` calls, each followed by successful `consume` or `install`,
and optionally the terminal `close`. The borrowed input geometry may vary
between calls. Input replacement and descriptor production belong to the
caller. In particular, `install` is the source's paid copy-back entry, which
may change SOURCE; it has the same private-storage effect as consumption.
Malformed or interrupted executions and rollback are outside this theorem.

The storage measure is the number of retained cells in the explicit tape
arrays. In the source `machine.py`, a read beyond an array returns BLANK
without extending it; a move changes the head only; a write at index `j`
extends the array to at least `j+1`. Erasure writes BLANK and never shrinks
an array. Thus a blank cell retained after a call still counts.

Let `a_r>=1` be the retained length of private role `r` immediately after
`init`, and `K0=sum_r a_r`. A fresh minimal owner has `a_r=1` for every
role. Arbitrarily large erased entry tails are permitted, but their capacity
is included in `K0`. The statements below bound the complete private bank;
borrowed input backing and any caller-retained old input objects must be
added separately. The fixed instruction word and finite-control encoding
are constant program memory, excluded from the tape-cell totals. These are
logical tape cells, not CPython allocator capacity or heap metadata.

Write `b(n)=max(1, bit_length(n))`, so the canonical zero word has one bit,
and put `d=max(H-1,0)`. An allocated numerical prefix of a `w`-bit word has
length `w+2`: LEFT, its bits, and RIGHT. A payload prefix of `v` bits has
length `v+1`: LEFT and its bits; its following BLANK may remain implicit.

## 2. Exact capacities of one successful call

For each role define the following capacity `c_r(H,A,G,S)`. It is the
retained length reached from a fresh minimal owner after `run` and its
consumption or installation, and bounds every write during that call.

| Private role | Capacity |
| --- | ---: |
| PRE | `b(A)+d+2` |
| GAP | `b(G)+d+2` |
| TAIL | `b(S)+d+2` |
| SCAN, REMAIN, each | `b(H)+2` |
| OUTER | `b(A)+H+1` if `H>=1`, otherwise `1` |
| BETWEEN | `b(G)+H+1` if `H>=1`, otherwise `1` |
| BITS | `b(S)+H+1` if `H>=1`, otherwise `1` |
| Q00, Q01, Q10, Q11, each | `V/4+1` if `H>=1`, otherwise `1` |
| B0 | `V+1` if `H>=1`, otherwise `1` |
| B1 | `V+1` if `H>=2`, otherwise `1` |
| OUTPUT | `V+1` |

For the numerical roles, setup copies `A,G,S,H` into PRE,GAP,TAIL,SCAN.
It doubles GAP and TAIL exactly `d` times and copies `H` into REMAIN.
For `H>0`, pass `i=0,...,H-1` has

```text
PRE  = A*2^i,
GAP  = G*2^(H-1),
TAIL = S*2^(H-1-i).
```

Every pass actually occurs and all these values are positive. Therefore the
maximal bit lengths of PRE,GAP,TAIL are respectively `b(A)+H-1`,
`b(G)+H-1`, `b(S)+H-1`. The three nested counters copy these values into
OUTER,BETWEEN,BITS before decrementing them, so they attain the same respective
maxima. SCAN and REMAIN start at `H` and only decrease.

The source helpers do not introduce a larger temporary prefix. `double`
adds at most one high bit and its RIGHT marker; `half` erases the old RIGHT
before moving it left. `dec` and `normalize` erase displaced delimiters;
the zero result is `0 RIGHT` and does not exceed the original positive
word's allocation. Copies write exactly the copied bits and RIGHT.
`clear` writes through the current nonblank body, including a numerical
RIGHT, then stops at its first BLANK. It does not scan a retained blank tail.
These facts also cover the transient states between canonical endpoints.

Each positive-width pass has volume `4*PRE*GAP*TAIL=V`. Its four queues
each receive exactly `PRE*GAP*TAIL=V/4` bits, regardless of their values.
The first pass fills B0. The second fills B1 if and only if `H>=2`;
later passes alternate those same two roles. Every filled buffer has
exactly `V` bits. The selected buffer is copied into OUTPUT and erased.
Queue and buffer erasure cannot increase their allocated prefixes.

For `H=0`, setup still writes PRE,GAP,TAIL,SCAN,REMAIN, including the
canonical zero SCAN and REMAIN. No pass or nested counter executes: all
four queues, both buffers and the three nested counters retain only LEFT.
The identity branch copies all `V` bits directly from SOURCE to OUTPUT.
This proves the `H=0` entries and explains why B1 also remains minimal
when `H=1`.

All stated maxima are attained: copied numerical words include every bit
and their RIGHT marker; every nonempty queue/buffer/output writes its last
payload cell. The remaining cells in the table are the initialized LEFT
markers. `consume` clears OUTPUT, while `install` clears SOURCE, copies
OUTPUT there and clears OUTPUT. Neither entry writes beyond a private
capacity in the table. Terminal `close` erases only the fifteen LEFT
markers and leaves every array length unchanged.

## 3. Exact history formula and a distinguishing example

Let call `i` have geometry `g_i=(H_i,A_i,G_i,S_i)`. After `k>=1` successful
calls and their consumptions or installations, the exact retained private
length is

```text
C_r(k) = max(a_r, c_r(g_1), ..., c_r(g_k)),
K(k)   = sum_r C_r(k).
```

The formula holds at every completed prefix of the history. Its right side
also bounds all intervening writes. To prove it, start with the blank-body
entry invariant supplied by the predecessor. At a subsequent call, implicit
blank cells and explicitly retained blank cells give identical local read
results. Consequently the unchanged program follows the same instruction
trace as it would with minimal blank backing. The call writes through
exactly the prefixes in the table, and the machine extends only when a write
passes the old end. Cleanup restores the blank-body invariant without
shrinking either prefix. Induction gives the rolewise maxima. `close` does
not alter the result.

The sum must be taken **after** the separate maxima. The maximum of the
single-call total capacities can be too small, even at fixed width and
volume. Take the three calls

```text
(H,A,G,S) = (1,64,1,1), (1,1,64,1), (1,1,1,64).
```

All have `V=256`. The seven payload roles together retain `775` cells:
four queues of `65`, B0 and OUTPUT of `257`, and B1 of `1`. For each call
alone, two numerical roles have capacity `9` and the other six capacity
`3`, giving `775+36=811` cells. In order, the large role pairs are
PRE/OUTER, GAP/BETWEEN, and TAIL/BITS. On one owner their capacities
accumulate, so the total is `811`, then `823`, then `835`. At the end,
all private data are blank and all private heads are at one.

This is a counterexample to replacing `sum_r max_i c_r(g_i)` by
`max_i sum_r c_r(g_i)`, not a failure of the predecessor interchange or
cleanup contract. Its written table derivation is corroborated by literal
short program runs; the receipt records that finite evidence separately.

## 4. A grant uniform in the number of calls

Let `Vmax=max_i V_i>=1` and `w=b(Vmax)`. Every numerical value appearing
in a call is at most its `V_i`: this follows directly from the three
pass values above, `A,G,S>=1`, and `H<=4^H<=V` for `H>=1`. At `H=0`,
the descriptor value zero still requires only one bit. The eight numerical
roles therefore each have capacity at most `w+2` over the entire history.

Each queue has capacity at most `Vmax/4+1`: inactive `H=0` calls need
only its marker. B0, B1 and OUTPUT each need at most `Vmax+1`. For a fresh
minimal owner this yields

```text
K(k) <= 8(w+2) + 4(Vmax/4+1) + 3(Vmax+1)
     = 4Vmax + 8b(Vmax) + 23.
```

There is no factor `k`. Independent maxima in different calls are already
covered by the individual role grants. For arbitrary erased entry backing,
the exact rolewise formula in §3 applies. Since each `a_r>=1`, a convenient
safe total is

```text
K(k) <= K0 + 4Vmax + 8b(Vmax) + 8.
```

This follows by bounding each role's possible growth beyond its initially
allocated marker; it does not discard the existing `K0` cells. A grant
using only the latest call's volume is not valid after a larger prior call.

Allocated backing and visited cells are different measures. All private
head positions during one call lie between zero and `c_r`, inclusive:
the extra position is the first blank beyond a full allocated prefix.
The helper descriptions above give this bound for clear/copy/end probes;
init, close and unused-role checks visit at most positions zero and one.
Hence the union of private visited cells over a fresh-owner history is
conservatively bounded by

```text
sum_r (max_i c_r(g_i)+1) <= 4Vmax + 8b(Vmax) + 38.
```

This is only a visited-cell upper bound, not a claim of exact equality.
Unvisited preexisting backing still belongs in an allocation grant.

## 5. Analytic application at the retained CRT callee

PR5188's declared actual u/back geometry is `H=2,A=1,G=1024,S=12`,
so `V=196608`. Substitution into the table gives numerical capacities

```text
PRE GAP TAIL SCAN REMAIN OUTER BETWEEN BITS
 4   14   7    4     4      4      14    7
```

Their sum is `58`. Each queue has `49153` cells, and B0, B1 and OUTPUT
each have `196609`. Thus the exact fresh private capacity is

```text
58 + 4*49153 + 3*196609 = 786497 cells.
```

The uniform bound gives `786599` since `b(196608)=18`. This application
is arithmetic derived from the quantified proof, **not a new replay** of
the predecessor's approximately 64-million-instruction fixture. The
bounded new checks use smaller histories and separately test the capacities,
cleanup, retained tails and changed geometry. They do not constitute an
all-size proof by enumeration.

## Attribution and remaining limits

JoyboyBrian/#5188 supplies the unchanged literal program and the explicit
space handoff. PR5162 and Jose Manuel's physical ordinary wrapper supply
the retained callee/source refinement, with PR2809/PR2753 stream and
cardinality lineage. Cinna Davis supplies the CRT context; Hiroki KUMAZAKI,
Douglas Colkitt/OpenAI and the source archives retain their credited
contributions and notices. Ross Richardson's separate numerical-arena and
packet-backing audits already use historical capacity accounting; the new
claim binds this actual callee's extents, not that general principle.
This capacity audit is by Hiroki KUMAZAKI
(@kumagi), with substantial OpenAI Codex assistance, under Apache-2.0.

The result bounds one private tape bank in the existing five-symbol model.
It neither initializes arbitrary dirty storage nor supplies borrowed
descriptors, a recursive/global allocator, a binary alphabet lowering,
raw/ROM/repair composition, a new time tariff, or a complete multiplication
supplier. The selected frontier and all predecessor sources are unchanged.
No independent human review or proof-kernel verification is claimed.
