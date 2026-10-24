# Conditional sequential-handle control bound

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.

This is a bound for a new executable metadata kernel, conditional on a source
encoding contract. It is not a claim that CPython pointers, dictionaries or
reflection are tape primitives. The original #4790 scientific sources and guards
are unchanged. The kernel consumes exact snapshots of those sources and must
agree with them.

Let K bound the sum of vertices, traversed edges and inspected object attributes
of the three current owner graphs, all supplied role-list lengths, plus one.
Every distinct physical Tape receives a positive stable handle at most K.
Non-Tape vertices have local handles. Tape bodies are opaque. Source field
classification/omission follows exactly the authenticated `owned_tapes` skip
alphabet. A producer/service lifetime must supply this complete encoding at
every check; a constructor-only graph bound does not suffice.

The kernel uses at most Q=64K words of w=bit_length(Q) bits. Every graph pointer,
Tape handle, array address, count and cursor fits this width. It implements
visited sets by encoded flags and follows encoded adjacency, rather than using
Python identity hashes as unit-cost membership. It explicitly checks cached
engine membership/uniqueness, engine disjointness, producer separation, ordered
external roles and the storage/acquisition/external exclusivity predicate.

## Addressed bit model

The macro simulator's host list indexing only fast-forwards a fully charged
sequential scan. For each word read or write, reset a w-bit scan index; scan all
Q words; compare all w address bits at each word; branch; copy the selected
word bit by bit; advance the head; execute a padded eight-instruction-per-bit
increment; test the loop; rewind the entire store; halt. It costs exactly

`A(Q,w) = Q(12w+3)+3w+1`

in the stated bit-instruction model: reset w, per word compare 2w+1 (zero difference bit, then XOR and OR for every
address bit), branch-on-zero 1,
forward movement w, padded increment 8w, loop branch 1; the unique selected
copy costs 2w, complete rewind costs Qw, and halt costs 1. Selected copy reads or writes
only the current head cell and immediately advances one cell per bit; unselected
words perform the same forward moves without copying. No offset cell lookup
is part of the bit machine. Each increment bit pays carry initialization (only
on the first bit; otherwise NOP), old-bit copy, XOR, AND, digit assignment,
carry assignment and two NOPs: exactly eight instructions per bit. Fixed-width
bit loops are unrolled in the compiled control, whose frontend belongs to F. Fixed registers are
bits/Booleans, compiled for this fixed K; no unbounded integer is free. The
independent checker expands these instructions on small stores and checks
values, addresses, preserved cells, restored head and exact prices.

Other bounded-word comparisons, copies, arithmetic and branches are charged
16w+16 per scalar macro, sufficient for two full w-bit scans, fixed-width
increment/subtraction and branch bookkeeping. Source payload operations are
outside this metadata kernel and retain their earlier R/W/move tariff. This
model does not choose the repository's physical-machine compiler or its source
frontend. A physical embedding must provide this bit-register/store interface,
including its additional control storage; no zero-tape-space claim is made.

The simulator charges Q accesses for initial zero fill and Q accesses for full
retirement, even though its Python storage omits unused padding. Each imported
metadata word pays one source read and one owned write. Thus metadata copying,
workspace initialization and cleanup are included; producing a trustworthy
source encoding remains a separately stated embedding condition.

## Counting bound

DFS pops exactly e+1 stack entries (including repeats). There are at most g
first visits and e pushes. A first visit reads four header words, sets one flag,
and either appends one opaque Tape handle or pushes children in reverse order.
The stack has e+1 cells. Both imported graph words and returned handle words
are charged. Three walks use fewer than 96K accesses and 192K scalar macros.

There are four complete mark-array clears (two engine comparisons, combined
inventory, and storage exclusivity). The mark universe is at most K. Every
source role-list element is scanned a bounded number of times: saved engine
lists at most six, current lists at most three, and external/auxiliary/storage
lists at most four. All encodings, result buffers and duplicate imported lists
fit 64K words. Conservatively allowing 128K accesses for initialization and
retirement, 128K for all imports, 96K for walks, and 128K for all remaining
list scans gives less than 1024K accesses. The corresponding loop, branch,
scalar bookkeeping is less than 4096K. `Store.finish` checks both independent
ceilings on every executed kernel call. Therefore

`U(K)=1024K A(64K,w)+4096K(16w+16)`

is a conservative bit-instruction upper bound per validation. The same envelope
also covers an exchange (one scan/copy of a role list), including its own zero
fill/import/cleanup. This intentionally does not optimize metadata reuse.

## Source sites and whole lifetime

Put C=511014Γ and S=336Γ, from #4166/#4790's inherited complete successful root
census. #4790 performs one constructor validation and exactly two validations
per adopted return: **1+2C**, each traversing three owner graphs. Its native cache
exchange runs C times and its service cache exchange S times: **C+S**. The test
harness's final `check_inventory` is not an algorithmic site and is excluded.

Reserve one further U(K) binding budget for initialization and one per return
for remaining fixed dispatch, the credited #4167 finite packet/private/parked
rebinding, and rebuilding external tuples. This last budget is conditional on
the same K contract covering those finite lists and scalar fields; it does not
charge payload clearing again. Copying/clearing common payload intervals retains
the predecessor's cancellation premise. The fixed number of comparisons and
list scans is below the same conservative 1024K/4096K ceilings. The source AST
anchors and actual cache-exchange counts are checked independently of this sum.

Hence this encoded-control realization has additional metadata charge at most

`B(K,Γ) = (4C+S+2) U(K)`.

Let F include any compilation/frontend/encoding-embedding charge not discharged
by this kernel contract and any remaining positive control difference outside
these intervals. Then the sufficient matched D* versus frozen D condition is

`F + B(K,Γ) < C(11v+4)`.

Equivalently v must exceed `(F+B−4C)/(11C)`. F is **not zero** by default. No
uniform production K or physical embedding is established by reduced logs.
The full D* versus B* ledger has additional unmatched costs and remains open.
