# Delimited continuation without a saved-frame oracle

This package replaces the missing control-stack operation in
`research/complex-segment-boundary`. A fixed set of sixteen payload tapes,
one control tape and one descriptor tape supports every finite nesting depth.
The return routine finds the frame and the parent payload delimiters by unit
moves. It does not read a saved frame length, parent pointer or absolute origin.
The generic stack uses a seven-symbol alphabet. Its tape count is eighteen
at every depth.

This is a constructive interface result, not a complete recursive caller or
a new kappa. The selected value remains 60403/20000000. The physical child C,
delivery of its designated output, descriptor producer and source role
allocation remain separate obligations. The new result closes Open next
question 3 of the retained segment package. It does not close its other three
questions.

## Contract and result

Each payload tape has an arbitrary untouched ancestor prefix, a left delimiter,
a contiguous binary current word and a head within that word or at its right
end. An absent role is empty. The descriptor is an arbitrary finite binary word
on its own tape. The control head is at its free top. These are entry conditions,
not a promise to locate a remote initial origin for free.

Push writes a frame containing a presence bit and a unary head offset for each
role, then a separator, the opaque descriptor and an end marker. It discovers
the current extent by scanning that word. It inserts one payload delimiter at
each current end and clears the descriptor tape. Pop requires child payloads
to be empty at their new origins. It clears the current child descriptor,
finds the frame start, decodes it, removes each child delimiter, finds each
parent delimiter, restores the saved heads and reconstructs the descriptor.
It erases the entire current frame and finds the preceding control top.

Let k be the fixed payload-role count, S the sum of current payload extents,
H the sum of current head offsets, d the parent descriptor length, q the child
descriptor length at pop, and A the number of absent roles. In the stated
unit model, every read, write and unit move costs one. The exact boundary bill is

    push = 4H + 2S + 10k + 7d + A + 11
    pop  = 9H + 2S + 21k + 11d + 5q + A + 28
    total = 13H + 4S + 31k + 18d + 5q + 2A + 39
          <= 17S + 33k + 18d + 5q + 39.

The live control frame has H+2k+d+3 symbols. Thus both time and live additional
space are O(S+d+q+k), independent of ancestor extent and nesting depth. Unary
headers trade compact metadata for a linear current-volume bound. If the
actual caller proves S,d,q=O(V polylog(p)), this boundary fits its proposed
O(V e^(1-a2) polylog(p)) node allowance for e>=1 and 0<a2<1, with the polynomial
log factor adjusted as needed. This conditional absorption does not prove
that caller's descriptor-size or payload-volume premises.

`PROOF.md` gives the invariant, induction and full count. `stack.py` is the
sequential routine. Its only persistent fields are the physical tapes.
The sizes and heads returned by pop are observer counts for the source adapter:
they do not choose a branch, address or movement in the return routine.

## Source use and evidence

`adapter.py` lets the unchanged retained `streams.py`, `compact.py` and
`monomial.py` execute through current segments. Push and pop never consult its weak-reference allocation registry. The registry
records live handles by depth and slot so an empty role can be released after
return. It supplies no payload bytes, head, origin, descriptor or frame length.
A resumed source handle names its fixed slot. This is not a new physical allocator or a
general API for stale handles. The source's proper lexical lifetimes and fixed
sixteen-role bound remain premises. Array snapshots and byte views belong only
to the test oracle; the source algorithms use the local size and sequential
read/write/rewind/erase interface.

All inputs are pinned to canonical main
`7c472563474e60185e6ca101a17622133d047e56` in `SOURCES.json`. The predecessor
retains the earlier PR2250 source and the provisional event8814/family65689
descriptor. That historical descriptor is used as opaque payload here; this
package does not recertify the full dispatcher/cover/rho chain.

The checker covers 1,452 complete small push/pop invoices, with absent roles,
empty heads and unequal descriptors. It constructs a new Stack object before
return, so the push object cannot supply saved return state. Twelve nested
cases cover depths 1,2,7,31 and ancestor lengths 0,17,4096. Six source cases
park all sixteen parent roles, execute unchanged compact calls at two nested
levels in both source layouts, and compare exact outputs to an independent
address oracle. Ancestor lengths 16,257,4096 have identical cost. The actual
right-recipe phase is checked on 1,024 addresses against Gaussian arithmetic,
including its inverse. Six controls reject a missing end, missing start,
bad unary terminator, out-of-range head, unretired child and false absence.

From the repository root, with Python 3.12 and the standard library:

```sh
python3 -I -W error -B research/delimited-continuation-stack/verify.py
python3 -I -O -W error -B research/delimited-continuation-stack/verify.py
python3 -B scripts/research_package.py --package research/delimited-continuation-stack
```

Expected marker: `PASS_DELIMITED_CONTINUATION_STACK`. The committed receipt
must match the full calculated result. Source byte hashes are checked before
import. A generated package export supports replay without Git.

The written induction covers arbitrary finite properly nested successful
calls in the stated ABI. The finite tests corroborate that proof; they do not
replace it. The adapter's reduced f=2 compact rectangles and phase fibre are
not full e=147 production payloads. Initial tape setup, descriptor construction,
arbitrary stale-handle behavior, complete allocation control, recursive C,
output delivery, native phase admission, precision, full stock and the complete
multiplication theorem remain outside scope. No selected cold replay, Lean or
Docker build is required by this isolated result.

## Open next questions

1. Bind the actual packet's output role to a sequential return transfer before
   child retirement. This is the remaining data-delivery boundary. Start with
   the pinned event8814 recipe and one complete reduced active rectangle; its
   full physical packet order and child contract remain dependencies.
2. Compile the retained lexical allocation into a finite slot schedule. Start
   at repair/radix's maximum live cut and remove the weak-reference allocation
   simulator. The stack proof supplies no new allocation theorem.
3. Bind an actual descriptor producer and its bit-length bound. The stack treats
   its bits as input and charges all transport. A general node invoice needs the
   producer and source-size bounds as well.

## Credit

JoyboyBrian supplied PR5329's segment refinement and explicit stack-oracle gap,
and PR5041's locality invoice. Jose Manuel/jmbarrancoml supplied PR2250's
sequential compact/monomial source. Douglas Colkitt supplied the guard and
repair construction. Cinna Davis supplied the PR4100/4088 caller; Matarener
supplied the cover/stock lineage. All source notices remain unchanged and are
declared replay inputs. Ali Romman prepared this stack construction, proof,
adapter and checks with substantial OpenAI Codex assistance. Apache-2.0.
This is author-checked evidence, subject to independent review.
