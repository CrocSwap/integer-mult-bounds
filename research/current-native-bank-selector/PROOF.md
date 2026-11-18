# A charged selector at one native child view

## Contract and exact source

Fix the source in VENDORED.json. At zero-based clock 88263 the current
PR7663 word executes `MOVE 1510,477,1090,True`. Role 1510 has lifetime
ordinal 35, from INIT 88260 to CLEAR 91760. There are 34 live parent
lifetimes at this cut. The complete raw native plan has 234 lifetimes.
The verifier reconstructs the edited word and checks these facts directly.

Chart 1090 is a four-dimensional subspace of the eight-dimensional chart
477 in the nine-dimensional native frame. The retained native adapter
contract therefore exposes a positive rank-four child. This result does
not reconstruct or execute those adapters. It starts after they put the
complete view in canonical spectator-first order.

Let R,f,W be positive integers. Each complete complex address has W real
bits, a separator, W imaginary bits, a separator and one represented blank.
Its record length is 2W+3. The parent has R external rows and 9f native axes.
The child has R*2^(5f) external rows and 4f active axes. Both use the same
root width W. Both complete extents are

```text
L = (2W+3) R 2^(9f).
```

For parent address (r,s,c), with s in [0,2^(5f)) and c in [0,2^(4f)),
the linear index is r*2^(9f)+s*2^(4f)+c. The child index is
(r*2^(5f)+s)*2^(4f)+c. They are equal, and Euclidean division gives the
unique inverse. Every bit and structural cell of every record is thus in
the same position. No data permutation or physical copy implements this
reshape. The preceding adapters, their control, and any different address
order remain separate costs. Equal total extent without this shape and
order identity is insufficient.

## Two tapes, fixed banks and a finite selector

Fix P parent slots and C child slots before input sizes vary. Let B=P+C.
Each slot has L payload cells between two guards, so slot k begins at
k(L+2). Slots 0 through P-1 retain the parent. Slots P through B-1 are
distinct child homes. A child may borrow an explicitly named parent slot;
that slot is not also an owned child home.

The data tape and a separate read-only guide tape have B(L+2) cells each.
Each guide slot contains a typed left marker, L typed template cells and
a typed right marker. These are the unchanged PR7663 guide values. A
literal marker in old data cannot act as a guide boundary. The guide and
data heads start at the first slot's left guard. The construction retains
every slot, including inactive or cleared homes. Resident tape capacity
is exactly 2B(L+2) cells for this subsystem, plus its fixed control and
separately charged preparation workspace.

The forward selector starts in finite state k. At each typed left marker
it stops if the state is zero, or decreases the state by one. At all other
guide cells it keeps the state. A nonterminal step moves both heads one
cell right. Induction on the crossed left markers proves that it stops
at slot k, after exactly t=k(L+2) moves of each head. The reverse selector
uses the same states and moves left. From slot k it returns to slot zero
in exactly t moves of each head. Neither selector reads or writes data.

The state range is 0 through B-1. It is finite and independent of R,f,W.
Each selector has 10B literal rows: eight template symbols and two typed
boundaries per state. There is no variable-distance head instruction.
The two heads stay aligned but address distinct tapes.

## Exact local charge and restoration

Count each guide read, payload write, unit move of either head and executed
control row as one unit. One selector executes t+1 guide reads and control
rows, and 2t unit moves. Its cost is 4t+2.

Use the unchanged source reset graph at the selected slot. It executes
2L+3 guide reads and control rows, L payload writes and 4L+4 unit moves.
Its cost is 9L+10. INIT writes the complete scientific-zero template;
CLEAR writes the raw blank. The graph returns to the selected left guard.
The source's position induction applies to arbitrary old payload symbols.
The guide and both exterior guards stay unchanged.

Compose forward selection, reset and reverse selection. The complete
service has exact cost

```text
8k(L+2) + 9L + 14.
```

Only the selected payload is written. Both heads return to the first
slot's origin. Thus every suspended parent, every other child slot, all
guards and the guide are unchanged when k>=P. The conclusion concerns
complete historical backing, not just the current scientific length.

A borrower of parent slot j can instead enter through the two selectors.
If its own service returns both heads at that slot's origin and writes
only the granted payload and its distinct child homes, composition adds
8j(L+2)+4 to its separately charged service cost. The rest of the parent
remains unchanged. This is a frame-condition theorem. It does not provide
the child's Gaussian arithmetic or its internal allocation.

## Apply the complete raw lifetime plan

Give the source's 234 child lifetimes slots 234 through 467, and retain
234 distinct parent slots. Each child ordinal receives one INIT and one
CLEAR at the source clocks. The exact plan supplies the chronology; no
label reuse aliases two lifetime homes. Summing the formula above gives

```text
2 sum_(k=P)^(P+C-1) [8k(L+2)+9L+14]
  = C(16P+8C+10)L + C(32P+16C+12).
```

For P=C=234 this is 1316484L+2631096. The 468-command literal replay checks
that sum at L=5 while preserving the complete parked parent. A separate
actual-extent fixture has R=f=W=1, L=2560 and 1199016 cells on each tape.
It executes INIT and CLEAR at the first and last child slots, checks every
unselected cell and guard, and tests a borrower confined to parent slot 35.
That borrower writes a fixed valid bit pattern. It is not a Gaussian child.

The two selectors and both reset graphs contain 9398 reusable service
rows at B=468. A complete static dispatcher is not free. For example,
unroll the fixed 468-command schedule, retain one operation's 19 reset
rows per command, and connect each terminal transition to the next phase.
This gives at most 468(20*468+19)+1 = 4389373 finite control rows. The
terminal transitions already appear in the charged row count; no extra
unpriced jump is needed. This is a constructive representation bound,
not a claim that the verifier stores that full unrolled table.

The same proof applies to any fixed P,C and a caller-supplied finite
schedule. The 234-slot child tuple here exercises one raw native lifetime
plan. It is not the actual inventory of an entire compiled recursive child.
That inventory can contain many raw occurrences and other workspace.

## Coverage and remaining obligations

The local position and frame-condition arguments hold for every stated
shape and arbitrary old private symbols. The finite cases corroborate
them. Controls detect equal-size wrong formats, missing spectators,
parent/child aliasing, a shortened guide and an omitted head return.

Guide production, staging and retirement have positive costs. The retained
source gives an O(L+1) construction per guide plus descriptor setup. The
verifier uses that producer, but does not compile its full bit-level
production, or provide a common physical tariff for the whole algorithm.
This proof charges the complete local service once the guide and slots
exist. It does not claim that their initial allocation or preparation is free.

The native adapter permutation, actual compiled occurrence tree, complete
child arithmetic, cross-depth ownership, compiler/primitive workspace,
root format delivery and analytic recovery remain open here. The source's
full conditional application was not replayed. No framework assumption is
discharged, no new kappa is established and the selected frontier is unchanged.
