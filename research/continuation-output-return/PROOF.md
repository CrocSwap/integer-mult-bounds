# Designated child-output return

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.

## Contract and retained stack

Use the seven-symbol tape alphabet and physical push/pop of
[PR #5356](https://github.com/CrocSwap/integer-mult-bounds/pull/5356), at
[the exact source](https://github.com/aliromman/integer-mult-bounds/blob/ef1cc26e1e9a08c11cf382de948ee433bebab16d/research/delimited-continuation-stack/stack.py).
That result restores k=16 payload roles, their presence bits, heads and an
opaque binary descriptor. It requires every child segment empty at return.
The unchanged stack and source adapter are retained in vendor/. Their source
bytes and notices are checked. This PR adds output delivery, not a new stack.

Reserve one occupied empty parent output role before push. Its head is at its
segment origin. All other parent segments and heads are arbitrary under the
retained ABI. The child leaves one designated binary output of length L on
one fixed role, with its head anywhere in that segment. The child may leave
other binary work on its roles. Slots are compile-time control labels; the
child and parent labels may be equal. Descriptors are arbitrary finite binary
words. All calls succeed and are properly nested.

Add one relay tape with a BASE marker and an empty current segment at its
origin. It is distinct from all payload, control and descriptor tapes. Its
arbitrary ancestor prefix is preserved. There are nineteen tapes in total,
independent of nesting depth. The source API's logical counters and lexical
allocation remain a separate calibration facade; the return routine never
reads them, a saved origin, a saved length or a parent object.

## Schedule and invariant

First check that the relay head is immediately after BASE and reads blank.
Rewind the child output to its nearest LEFT marker by unit moves. Copy its
binary symbols, in order, to the relay until blank. Rewind the relay to BASE.
This preserves the output in relay cells before any child cell is erased.

For each of the fixed payload roles, rewind to LEFT, erase each current
binary symbol while moving right, then rewind to LEFT. No ancestor cell is
read or changed. Invoke the unchanged physical pop. It erases its frame and
returns each parent payload, head, presence bit and descriptor exactly.
The relay is outside this bank, so pop cannot erase it.

Check that the reserved target is blank immediately after LEFT. Copy relay
symbols to that role in order. Erase each relay symbol after copying it.
Rewind both tapes to their markers. The target now contains exactly the
child output, with head zero. The relay is empty at its original head.
All other parent roles and the descriptor have the exact pre-push state.

These assertions prove a matched boundary by loop induction. The copy loop
preserves the copied prefix and unread suffix. The erase loops affect only
current segments. The retained pop theorem restores the parent. The final
copy loop preserves the delivered prefix and the unread relay suffix. Its
postcondition restores the entry condition of the shared relay. Induction
on a finite call tree therefore reuses the same relay for arbitrary finite
proper nesting. At an outer return, a previously delivered inner result is
an ordinary child output. No recursion frame stores return data in host state.

## Complete bill

Count each current-symbol read, write and unit move as one action. Let Sp be
the sum of parent extents and Hp the sum of parent head offsets. Let A be the
number of absent parent roles. Let d and q be the parent and child descriptor
lengths. Let W and Hc be the sums of child extents and head offsets immediately
before return. Thus L<=W and Hc<=W. All these symbols are analysis variables;
the routine does not receive their values.

The retained push costs

```text
4Hp + 2Sp + 10k + 7d + A + 11.
```

The retained pop, after payload retirement, costs

```text
9Hp + 2Sp + 21k + 11d + 5q + A + 28.
```

Rewinding from offset h to its marker costs 2h+3. Erasing a current segment
of size s from offset h costs 2h+5s+7. If the original output head is h0,
checking the relay and copying the output costs 2h0+6L+11. It leaves that
source at offset L. Retiring all roles then costs
2(Hc-h0+L)+5W+7k. Checking the target and installing the output while erasing
the relay costs 9L+11. Thus the complete matched push/return boundary costs
exactly

```text
13Hp + 4Sp + 38k + 18d + 5q + 2A + 2Hc + 5W + 17L + 61.
```

Child computation and its input/descriptor production are separate costs.
They are not hidden in this formula. Output copying, child cleanup, frame
cleanup, descriptor return and relay cleanup are included. Since Hp<=Sp,
Hc<=W, L<=W and A<=k, the boundary is at most

```text
17Sp + 40k + 18d + 5q + 24W + 61.
```

There is no ancestor-length or nesting-depth factor. If Sp,W,d,q=O(V), this
is O(V) and fits the retained per-node allowance. Those actual volume and
descriptor bounds are explicit premises, not established production facts.

The relay visits L cells in one boundary and is empty at its end. Across
successful calls its retained backing needs at most the maximum output
length seen so far, not a sum over nesting depths. The parent output owns L
cells in its reserved role. During the first copy the child and relay both
hold the result; neither this duplicate nor the parent output is free stock.
All inherited continuation frames and parked payload backing remain charged.

## Evidence and scope

The verifier checks 1800 exact small return bills, including zero-length
outputs and every head position through length three. Twelve nested cases
use depths 1,2,7,31 and ancestor lengths 16,257,4096. Six actual compact-source
cases run both retained layouts and deliver all 1024 output bits to the
parent. An independent direct record permutation checks their values. All
six returns cost 24388 actions. Six malformed-state controls reject. Errors
outside the ABI need not restore a partially executed boundary.

The source calibration still uses the predecessor's weak-reference allocator
and host logical counters. This result does not compile those facilities.
It does not implement recursive C, packet reorder, a general descriptor
producer, the full production rectangle, native admission, stock matching,
precision or outer recovery. It closes the physical output-return boundary
under a reserved-slot ABI. It does not change kappa or prove the complete
multiplication theorem. Independent human and proof-kernel review remain open.
