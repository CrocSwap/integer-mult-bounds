# Complete key service at the retained repair port

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.

This is a fixed-geometry program theorem, with a replay of its actual caller.
The domain is the existing u2,t2,y8 fixture, not arbitrary CRT parameters.

## Proposition and port contract

Fix J in {0,1,2} and any 32-bit ROM F satisfying
`F[v] = F[v xor 2^J]` for 0 <= v < 32. Define `f(y)=F[y mod 32]`.
For every address `q=(u,t,y)` with 0 <= u,t < 4 and 0 <= y < 256,
`Service.evaluate_key` appends the twelve MSB-first bits of `T(S^-1(q))`
to the existing bad stream. Here S is exactly the ten-shear word from the
pinned `key_subroutine.py` / `check_batched_crt.py`, and T is the ideal
switch `(u,t,y) -> (u,t,y xor (f(y)<<J))`. No good-set test is used by the
service: the caller supplies only marked holes.

The borrowed `counter` contains `<` followed by exactly twelve bits and `>`;
its head starts at zero. The borrowed `rom` contains `L`, exactly 32 bits,
and `R`, also at head zero. These framed finite records and the initially
blank owned tapes are the contract. The stream head is at the first free
key cell after an opaque payload record, with twelve blank cells available.
Its prior prefix may contain the caller's existing payloads and keys.

On acceptance, counter/ROM cells are unchanged and both heads are zero;
the stream prefix is unchanged and its head has advanced exactly twelve;
all private cells are blank and all private heads zero. The stream is an
append port, so returning *its* head to zero would violate the original
bridge interface. The service never reads the stream.

There are 15 tape roles. The twelve owned roles and their maximum payload
widths are:

| Role | h | s | offset | target | out | count | col | row | limit | u | t | y |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Width | 3 | 2 | 1 | 4 | 1 | 3 | 4 | 2 | 5 | 2 | 2 | 8 |

Two framing cells are reserved for each owned record. These finite extents,
including formerly used markers, are erased on every return. The query roles
h,s,offset,target are borrowed *by the nested query*, but owned by this service.
The service creates their headers through charged writes on every invocation.

## Program versus host observer

`assemble` emits one of three fixed programs for J=0,1,2: respectively
5,313, 5,323 and 5,333 instructions. Its Python loops, shifts and constants
are assembly-time operations over this fixed geometry. The evaluator has no
instruction to obtain a tape's length, head coordinate, address integer,
decoded descriptor, Python list index from data, or host key result. Runtime
registers contain one symbol/bit or a Boolean, and the PC destinations are
fixed integers. `xorbit`, `andbit` and `orbit` are Boolean operations on two
one-bit operands. Every read, write, unit move, equality, bit operation,
register operation, branch, jump and halt contributes one to the census.

Python dictionaries, physical tape-head integers, instruction addresses and
counters implement the emulator/observer. They are never exposed as data to
the program. A tape read uses only its current cell. The `trace` option changes
logging only. `verify.py` independently decodes output, key epochs and the
caller's address log to compare results; none of those decoded values feeds
back to the executor. The actual caller adapter adds an address to the original
oracle's observer list because its existing assertions inspect that list; it
never calls that oracle's `key_of`, nor supplies its result to the service.

This is not a uniform compiler in u/t/y widths: those widths and J are fixed
when the three programs are assembled. The ROM is a parameter supplied in tape
form; its construction is not computed by this package.

## Correctness of current-state queries and shears

The input copy reads the twelve counter cells and writes u,t,y as separate
little-endian bit records. It checks every payload symbol and the exact right
marker. Invalid finite twelve-cell framing paths enter cleanup before any
stream append. Four such rejection controls are replayed; arbitrary unframed
inputs with missing left markers are outside the port contract.

At every source access, the descriptor is rebuilt from the *current* y.
Offset is y4, and target is y0..y3 with its highest nonzero position selected
by finite tests (zero is one `0` digit). The service writes h=4 and s=2 in
canonical little-endian form. The unchanged 752-instruction program from
`crt-uniform-rom-query/machine.py` therefore returns
`F[offset*16+target] = F[y mod 32]`. All 32 source cells are scanned; there is
no dynamic table lookup. This reasoning is for every legal F, not just the
five ROMs replayed. Each nested query clears count/col/row/limit and returns
all ten query heads. The service reads and clears out before continuing.

To invert the ten-shear word, process steps 9 down to 0. At step 9 add f(y)
to u modulo 4; at step 4 subtract f(y). At other steps, let
`r=step` for step<4 and `r=step-5` otherwise. Read z=u0, digit=t0+2t1,
and bit=yJ from the current records. The inverse update is:

| r | Update |
| --- | --- |
| 0 | y -= 2*z*digit*2^J modulo 256 |
| 1 | t -= bit modulo 4 |
| 2 | y -= z*2^J; y += 2*z*digit*2^J modulo 256 |
| 3 | t += (bit xor z) modulo 4 |

The two digit-dependent y terms are decomposed into conditional constants
`2^(J+1)` and `2^(J+2)`, guarded by z AND t0 or z AND t1. For each chosen
constant the full-width carry recurrence is
`sum=a xor b xor carry`,
`nextcarry=(a AND b) OR ((a xor b) AND carry)`.
Discarding only the final width-2/width-8 carry implements the stated modular
addition, including negative constants encoded modulo the full word width.
There is no truncated low-window update. After ten steps, a third current-y
source query gives f(y), and XOR on yJ applies T. Physical reads then copy the
u,t,y bits directly to the stream in MSB order. No host key string is formed.

All operations in the table are inverse shears because the controlling
coordinates do not change in their update; for r=0,2 the multiplier of 2^J
is even in r=0 and has parity z in r=2, as in the original compact word.
More directly, the formulas are the literal reverse order and negated offsets
of the pinned ten-shear source. Target independence of F is the original
ideal-switch condition. The final result is exactly T(S^-1(q)).

The private cleanup performs fixed writes over every reserved cell, then fixed
moves home. This includes headers created by the service and query scratch
already erased by the nested query. Counter rewind scans only the finite
retained record. No early halt precedes cleanup.

## Static complete instruction bound

The pinned query proof gives, for legal h,s and ROM,
`Q <= 512*(s*2^h+1)*(h+bit_length(s)+2)^2`.
Here h=4, s=2, so `Q <= 1,081,344`. Replacing each nested halt by one jump to
the service continuation does not increase this count. There are exactly three
queries on every valid input, for at most 3,244,032 instructions.

Remove the three disjoint 752-instruction query ranges. The remaining static
instruction counts D are 3,057, 3,067 and 3,077. `program_bound` checks their
actual control-flow targets: every backward edge outside a query is exactly
the five-instruction rewind sequence `read,eq,branch,move(-1),jump`, and every
other edge is forward. Rewinds do not nest and no outer loop revisits a query.
Each of the 244 rewind sites is on counter or private roles; no rewind is on
the arbitrary-position stream. The counter head never exceeds 13, and outside
queries private heads never exceed 10. Starting at distance d<=13, a rewind
visits each instruction at most d+1<=14 times (its terminal read/test/branch
are included). All other outside instructions execute at most once. Thus

`T <= 3*1,081,344 + 14*D <= 3,287,110 < 3,300,000`.

This charges full finite control, all header/descriptor construction, carry
work, input copy, all three ROM scans, stream append and final erasure/return.
The observed 41,395–44,928 instructions in COMPONENT.json are merely a much
smaller sampled range; they are not used to prove the bound. The bound covers
all 4,096 addresses and all target-independent 32-bit F in the stated domain.

The executed census is this finite-alphabet instruction model. This package
makes **no numerical binary-action claim for the whole service/caller**.
In particular the caller's stream has opaque 12-bit payload symbols, so the
query component's three-bit/32-action local lowering must not be silently
reused for the full port alphabet. A complete binary encoding of the joined
caller and its outer controls remains separate work.

## Actual caller composition and accounting

`verify.py --part caller` instantiates the pinned original Env and calls its
unchanged `run_layer`, at the middle of the actual five-layer schedule
(target 2), on all 4,096 identity-labelled payloads. Only the function installed
at `env.bridge.evaluate_key` changes. The same source producer constructs the
stencil, the same scanner constructs the mask, and the same repair partitions,
sorts marked-hole records by appended keys and refills the stream. Its 2,944
key invocations all use the actual counter/stream objects. All holes are called
once, no good address is called, the final payload matches the ideal layer,
and all owned caller/service tapes and heads are returned. This is one whole
source layer, not a replay of all five layers or the ten-layer round trip.

The source repair tape invoice already counts the key service's counter and
stream cell actions. The service census counts them too. The exact disjoint
cell invoice is therefore

`repair_and_key = repair_actions + key_cell_actions - key_interface_actions`.

The frozen receipt gives 13,314,027 + 39,360,192 - 229,632 = 52,444,587.
The service's separate complete instruction total is 128,507,264. These are
different ledgers; it would be incorrect to call their sum a fully priced
joined program. Producer 841 and scanner 454,830 are retained cell invoices.
The existing caller's bit-weight meter is not a complete binary lowering.

The raw post-S stream, ideal-output oracle and initial source ROM are supplied
by the unchanged host harness. The program constructing S, all-size CRT/ROM
reconstruction, source-layout conversion, outer producer/scanner/repair Boolean
controls and uniform all-parameter E(p,ell) are outside this result. Removing
the host-word key premise at this finite port does not discharge those costs.
