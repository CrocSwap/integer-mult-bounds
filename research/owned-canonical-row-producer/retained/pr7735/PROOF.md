# A linear-transition physical switch query

## 1. Result and dependencies

One fixed graph with 3,237 instruction locations and fourteen tapes computes
the canonical padded-rotation switch at every legal `(h,s,a,j,x)`. On the
unchanged PR7593 entry contract it returns one owned Boolean, preserves five
borrowed descriptors, clears eight private bodies and their temporary guards,
and returns every head. Its successful bounds are

```text
T <= 1024(h+4),
K_after <= K_entry + 16(h+4).
```

`T` counts every read, write, unit move, jump and halt. `K` counts historical
visited cells; clearing does not release history. The new time bound is
linear in `h`. The earlier graph's published bound is `1024(h+3)^2`.
This comparison concerns the supplied query service. It is not a full CRT
caller bound, a measured runtime speedup, a new kappa, or a selected-frontier
change. The word "linear" includes validation, preparation and cleanup.

Jerry Chen's PR7593 supplies the physical ABI, unchanged builder primitives,
primary interpreter and cleanup routine. Nick Petalas supplies the endpoint
and child formulas through PR7504. Ali Romman's PR7734 supplies the closed
descent and bit-probe lower bound. Cinna Davis's PR4100 compiler defines the
finite canonical-table oracle. See `CREDITS.md` and `SOURCE-PINS.json`.

The new graph digest, with the retained compact sorted-JSON convention, is
`530e83add1f22dcbb2b207e7ede64b2cecc44cce71db5fb26706ce18b842f92c`.
The optional mutation argument emits separate control graphs. It is never
a runtime input. No input integer reaches a generated instruction operand.

## 2. Entry and return contract

The fixed alphabet is `0,1,B,L,E`, encoded by `0,1,2,3,4`. `B` is blank,
`L` is the left marker and `E` is a private end marker. Put `W=h+1`.

| Tapes | Entry state |
| --- | --- |
| 0 | Borrowed positive canonical LSB-first binary `h`, then blank |
| 1..4 | Borrowed `s,a,j,x`, each exactly `W` LSB-first bits, then blank |
| 5 | Owned output body and its next cell blank |
| 6..13 | Disjoint private windows, blank through relative position `h+2` |

Every head starts at its own first body cell. Origins can differ. Tapes 0..5
have a permanent `L` immediately before the body. That cell is initially
blank on tapes 6..13; the graph installs and later erases their guards.
The supplied windows and distinct owners are preconditions. No row-label
count is treated as free physical storage. Opaque exteriors are not used.
Input bodies have no interior `L` markers.

The legal numeric domain is `h>=1`, `1<=s<=2^h`, `0<=a<s`,
`0<=j<2h-1`, `0<=x<2^h`. The query is indexed by the **current wire**.
All fields are validated before an identity result can be returned. The
graph has no write instruction on tapes 0..4. It writes tape 5 exactly once
on success, after the answer is known. The caller must consume and retire
that bit and pay descriptor production and transport.

For canonical positive `h`, finite format/domain failures in the other
fields return `REJECT`, preserve the output, and perform the same cleanup.
They have the same linear envelope. Empty or noncanonical height words also
reject; their parser cost depends on the number of consumed digits and
requires the corresponding supplied capacity. No recovery is promised for
aliasing, missing/interior left markers, opaque-guard corruption, an
unterminated stream, or an undersized physical window. These are the same
framing boundaries as the predecessor ABI.

## 3. Canonical countdowns

The private countdown represents zero by `E` at its origin. A positive
count has its ordinary LSB-first digits, highest digit one, then `E`.
All cells beyond that end are blank. The first symbol therefore tests zero
in one read.

To decrement positive `n`, change its `k=v2(n)` low zero bits to one and
the following one to zero. Inspect the next cell. If it is `E`, the changed
bit was the highest digit: erase the old end and replace the changed bit by
the new end. Otherwise retain the zero digit. Return to the left marker.
This preserves the canonical representation, including `1 -> empty zero`.

The graph uses at most `12(k+1)` transitions for this operation. A sequence
from `n` to zero costs less than `24n`, because

```text
sum_(v=1)^n (v2(v)+1)
  = n + sum_(r>=1) floor(n/2^r) < 2n.
```

This bound includes head returns. It does not charge a full-width zero scan
at every step. `compact` converts a supplied padded private word to this
representation: scan to its end, erase high zero digits, put the new end
after the highest one, and return. Zero receives an end at the origin.
Every cell removed from the representation is cleared.

The graph copies and validates `h`, then uses the canonical countdown to
produce `W` unary guide cells. This takes linear work even though the height
is supplied in binary. The guide initializes six `W`-bit numeric records
and validates/copies the four padded descriptors. The retained binary
primitives compute `R=2h-2`, create `2^h` by setting the high temporary bit,
and perform all domain comparisons. The borrowed originals remain intact.

## 4. A single pair of carry scans

After validation, the graph computes `b=s-a` and `r=2h-2-j`. A comparison
between `j` and `r` selects one of three fixed control branches:

```text
j<r: first endpoint, d=j;
j=r: center endpoint, d=j=h-1;
j>r: last endpoint, d=r.
```

The chosen `d` is compacted on the private `J` tape. There is no runtime
recursive call or child-descent loop. The two data scans have this invariant:

- Before low-digit step `i<d`, the heads on the offset, complement and
  wire tapes are at digit `i`. Two carry bits in finite control are the
  carries from adding the first `i` bits of `x` to `a`, and their binary
  complements to `b`, respectively.
- Read these three digits. Update the two carries with ordinary binary
  addition, move the three heads one cell, and decrement the compact counter.
  The discarded low sums need not be written.
- After `d` steps, the wire head is at `d`. Scan the remaining offset and
  complement digits once, propagate the two carries, and write the two high
  sums to separate private destinations. End markers close the new records.

Put `t=x mod 2^d` and `M=2^d-1`. The resulting words are exactly

```text
A_d = floor((a+t)/2^d),
B_d = floor((s-a+M-t)/2^d).
```

There is no high contribution from either `t` or `M-t`; only the saved
carry remains. Both full sums fit in `W` bits, so the final carries vanish.
Each quotient has `m=W-d>=2` bits. The wire head already selects the suffix
`y=x>>d`; copy it to a spare private record. Form `S=A_d+B_d` with one
equal-width addition. These are literal scans, not variable shifts or
unit-cost integer operations.

The earlier full-width data beyond a shortened end remain allocated until
cleanup. They have no role in arithmetic. They contain only digits or old
end markers, with no blank gap before the original frontier. Cleanup thus
erases them as well. Compacted counters are different: their shortened
tails are already blank. This establishes the cleanup precondition in both
cases; it does not discard hidden storage.

## 5. Canonical answer and restoration

PR7734 proves that the pair in Section 4 is the exact unreduced interval
pair after `d` source child steps. If either quotient is zero, the whole
child is identity. The graph tests both and returns zero. At the center,
both positive quotients must be one, so the one-row switch is one.

Otherwise the first-endpoint graph returns

```text
[S and A_d are odd] [floor(y/2)=floor(S/2)].
```

The last-endpoint graph returns

```text
[A_d is odd] [y<S]       if S is even;
[y<A_d]                  if S is odd and A_d is even;
[A_d-1<=y<=S]            if S and A_d are odd.
```

The retained comparisons and one safe decrement implement these formulas,
including the first padded wire. The source endpoint theorem and the scan
invariants prove the answer for every legal height. Neither fixture
enumeration nor host-decoded data is used in this argument.

Each endpoint writes the owned bit and enters the unchanged cleanup graph.
Cleanup returns the six input/output heads, clears all private digits and
end markers through the first blank, returns across the cleared cells, and
erases each temporary left marker. Section 4 proves that no live private
data lie beyond an early blank. Every head returns to its original body
cell. Each private guard has exactly the write history `L,B`; permanent
guards and opaque exteriors remain unchanged. The output remains owned.

## 6. Complete transition and historical-backing bill

Each `R`, `W`, `M`, `J` or `H` instruction costs one. A label costs nothing.
All loops in the Python constructor range over fixed tape lists, bit values,
carry states, or the three endpoint modes. Input values affect only the
runtime graph. Its finite alphabet, tape count and instruction table do not
depend on `h,s,a,j,x`.

For records of at most `W` digits, the retained source-loop bounds are:
rewind `3W+6`, zero test `6W+5`, decrement `7W+5`, copy `11W+7`,
left shift `7W+5`, comparison `11W+10`, and full cleanup `98W+179`.
The new equal-width add/subtract takes at most `12W+15`; compaction takes
at most `10W+16`. Copying a suffix takes at most `11W+14`, even when its
source head starts inside the original word.

For example, add/subtract uses two reads, one write, two moves and one jump
per digit, then two end reads and two rewinds. Compaction has one outward
scan, one clearing scan and one return. The canonical decrement count is
proved in Section 3, so its repeated use does not introduce a quadratic
term. Rounding the direct loop counts upward gives:

| Phase | Complete safe bound |
| --- | ---: |
| Guards, binary height, unary guide, initialization, four field copies, limits and validation | `240W+300` |
| Complement, reflected row, mode/depth selection and counter compaction | `60W+80` |
| Both carry scans, shifted wire copy and quotient sum | `100W+100` |
| Identity tests, endpoint arithmetic, result write and dispatch | `50W+60` |
| Full cleanup and halt | `98W+179` |

For the carry phase, the low scan costs at most `32d+2`. The high scan and
its four returns cost at most `15m+6W+28`. The two suffix copies and final
addition add at most `34W+43`. Their sum is at most `87W+73`, below the
table allowance. The height countdown has the same amortized bound and
all remaining setup loops make a fixed number of field passes.

Therefore

```text
T <= 548W+719 = 548h+1267 <= 1024(h+4).
```

These inequalities follow from the emitted loops, not measured timings.
For valid `h` and other malformed fields, rejection occurs during setup
and uses the same cleanup, so the bound also covers those paths.

Private heads stay in `[-1,h+2]`. The height input stays in `[-1,ell]`,
where `ell<=h`; the four padded inputs stay in `[-1,W]`; the output stays
in `[-1,1]`. The total visited span is at most `13h+49<16(h+4)`. Adding
this to entry history conservatively counts all first visits, even where
the caller already supplied backing. Reusing the same windows retains
their per-owner interval union. Relocation corridors remain caller costs.

The linear order is sharp for a standalone exact service: the PR7734
bit-probe family requires `h-1` offset-bit reads on the padded ABI, even if
all other descriptors are supplied free. Each such read needs a literal
transition. This lower bound does not cover preprocessed row advice or an
amortized stream of correlated queries.

## 7. Evidence and remaining work

The retained dense interpreter and a separate sparse instruction interpreter
agree on all 1,566 entries in the 49 complete networks through height three,
all 544 historical `(h,s,j)=(5,17,6)` queries, and 42 wider queries through
height 4096. They compare the full returned owner states, heads, visited
spans, and exact transition counts. A separate canonical network supplies
small expected bits; PR7734 supplies the wide arithmetic oracle. Both
interpreters reject thirteen malformed domains. Three semantic graph
changes and one failed-retirement change are detected; both owner adapters
reject aliasing. This is separate implementation checking, not independent
human or formal-kernel acceptance.

On the same 544 supplied query fixtures, the new graph uses 1,341,888
transitions in total, with maximum 2,545. A fresh run of the retained graph
uses 1,473,152 transitions. Both include their service setup and cleanup.
Host fixture serialization, current-state offset production, transport,
payload consumption and output retirement are excluded from both counts.
This is not an uninterrupted caller or a comparison with retained ROM reuse.

The graph and hardware are source-bound; no complete historical research
suite is invoked. Full current-state CRT composition and workload pricing
remain open. The selected cold replay, Lean and Docker were not run. All
five framework assumptions remain. Prepared by Ali Romman with substantial
OpenAI Codex assistance. Apache-2.0; predecessor notices remain intact.
