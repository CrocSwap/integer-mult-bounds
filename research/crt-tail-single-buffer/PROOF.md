# One-buffer complete-fiber switches

This contribution was produced by Nick Petalas. It is a scoped sequential
construction with a written all-size proof. Finite replay corroborates the
construction; independent human and formal proof-kernel review are unclaimed.

## Contract

Let `L>=1`, `R>=1`, `0<=H<L`, `M=2^L`, and `V=MR`. The source is a complete
stream of all binary addresses in lexicographic order, with an arbitrary
`R`-bit payload at each address. The output region and the private buffer
start blank. The input remains unchanged. The three payload heads start and
finish at their data origins. Payload cell reads, writes and unit head moves
are separate actions. A write of blank, including erasure, costs one action.
Marker visits and encoded counters are outside this exact payload invoice.

Write an address as `a|b|r`, with `a` of length `L-H-1`, `b` one bit, and `r`
of length `H`. A prepared Boolean control `g(a)` specifies the permutation

```text
a|b|r  ->  a|(b XOR g(a))|r.
```

There are `F=2^(L-H-1)` prefix fibers. Put `S=2^H R`, so `V=2FS`.
Let `B` be the number of prefixes with `g(a)=1`. Every payload and every
suffix address is arbitrary. No zero-padding or valid-address-only premise
is used. Output ownership and blank private workspace are required.

The complete-fiber contract, transported control and ordinary width-one
exchange are from ToikY's [PR4187](https://github.com/CrocSwap/integer-mult-bounds/pull/4187),
head `45fc0750436ae5cc14b95fba81c030a3d7df3412`, following Cinna Davis's
PR4100 and Hiroki KUMAZAKI's PR4174. Its two-buffer `13V` invoice and
`2S` scratch are cited prior results. This package replaces its staging
schedule. It does not audit or replay that predecessor.

## Schedule and correctness

Process prefixes in binary order. Prepare and retain `g(a)` once. The next
two consecutive source slices are `U_a=[a|0|r]` and `W_a=[a|1|r]`, each
of `S` payload bits.

If the control is zero, copy both slices directly to output. If it is one:

1. Copy `U_a` to the single private buffer, advance the source, and return
   the buffer head to its origin.
2. Copy `W_a` directly from source to output.
3. Drain the buffer to output in forward order. Erase every buffer cell
   immediately after reading it. Return the buffer head to its origin.

The zero branch outputs `U_a,W_a`; the one branch outputs `W_a,U_a`.
Within each slice every bit retains its position. Thus each address changes
exactly the specified `b` bit, with its payload unchanged. The source head
ends each fiber at the next fiber, and the output head ends at the next
output fiber. The buffer is blank and its head is at its origin before
the next control is prepared. Induction on the `F` fibers proves the endpoint
and workspace invariant. Finally return the source and output heads over
exactly `V` cells each. No source cell is written.

Applying the same permutation again restores the input payload order,
because neither `a` nor the retained control changes. This is an endpoint
involution with a fresh owned output on each invocation; it is not an
in-place reversible transition-table claim.

## Exact payload cost and space

A direct copied bit uses one source read, one output write and two right
moves. All `V` bits take this route in the zero-control baseline. Returning
the source and output heads costs another `2V` moves. The baseline therefore
uses `V` reads, `V` writes and `4V` moves, totaling `6V` actions.

At a switched prefix only its first slice changes route. Staging one bit
costs one read, one write and three moves, including buffer return. Draining
it costs one read, two writes and three moves, including erasure and buffer
return. Relative to copying that bit directly, the route adds one read,
two writes and four moves. The second slice still copies directly.

Consequently the exact complete middle-stage bill is

```text
reads  = V + SB
writes = V + 2SB
moves  = 4V + 4SB
total  = 6V + 7SB <= 19V/2.
```

The upper endpoint is attained whenever every control is one. The stated
schedule therefore saves at least `7V/2` payload actions against the cited
two-buffer `13V` schedule, with identical preserved-source/owned-output and
head-return conventions. This is an exact action-count comparison, not a
wall-time benchmark, a full-machine instruction count or an optimality claim.

The buffer uses at most `S` payload cells, and it touches all `S` when
`B>0`. This halves the predecessor's `2S` staging capacity. There are three
payload tapes instead of four. The source and output streams, evaluator and
counter workspaces are additional; no reduction of total asymptotic space
follows merely from halving this buffer.

## Caller transport and uniform overhead

For an original target position `j<L-H`, use the predecessor's paid
width-one exchange `Q` that moves it to the last position before the suffix.
If `f` omits that target and the complete suffix, define
`g(a)=f(Q(a|0|0^H))`. Varying `b,r` changes only omitted coordinates, so
`f(Q(a|b|r))=g(a)`. The preceding endpoint, conjugated by `Q`, is the original
controlled target flip. This algebraic transport does not implement `Q`.

Retain PR4187's uniform encoded evaluator tariff `E_*`, including descriptor
decoding, clearing and returned heads, and its ordinary exchange tariff
`T_X(V)`. The number of preparations is still exactly `F`. The new complete
conditional bound is

```text
T <= 2 T_X(V) + (6V + 7SB)
     + O(V + F(E_* + L + log(R+1))),
middle-stage extra space <= S + O(E_* + L + log(R+1)).
```

There are still two private intermediate streams when both `Q` calls are
needed. Their erasure and returned heads remain in the additional `O(V)`;
the original source and final owned output are preserved. When the target
is already adjacent to the suffix, omit both calls and both intermediates.

The encoded loop overhead has the same uniform lowering as the predecessor:
one reusable suffix counter and record counter delimit the passes. Ripple
counter carry traversals sum to a constant times their enumerated range;
initialization and returned heads cost `O(H+log(R+1))` per fiber. The changed
schedule has only a fixed number of passes per slice, and uses a fixed tape
inventory. The written bound charges `O(V+F(L+log(R+1)))` for these operations.
The Python interpreter does not execute those encoded counters or markers.
There is no free evaluator or uncharged family of control advice in this
conditional statement.

For the source's proposed CRT application, suffix omission, full reservoir
placement, the actual numerical evaluator and ordinary callee remain cited
premises. Sparse incomplete fibers are outside the contract. All five
selected framework assumptions remain. This result supplies no full CRT
admission, rounded multiplier, native supplier, complete signed recursive
invoice or new kappa.

## Executable boundary

`stream.py` executes each payload read, write and unit move with explicit
heads and blank symbols. `verify.py` uses a separate sparse interpreter to
replay its action trace, and an address-wise permutation oracle to check
the output. It also checks the inverse endpoint, exact costs, one preparation
per fiber, source preservation, buffer erasure and head returns.

The finite interpreter admits `1<=L<=12`, `1<=R<=16`; the universal theorem
above is not bounded by these test limits. Python allocation and host loop
counters are explicit Power of Ten deviations in this bounded verification
model. Payload volume is at most `2^12*16=65536` bits. Trace length is below
`10V`, and traces are released between cases. Every new function is at most
60 lines and there is no recursive call path. The bounded lambdas used by
rejection tests are the only indirect call targets. The physical theorem
charges a streaming implementation, not the memory used by this host trace.
