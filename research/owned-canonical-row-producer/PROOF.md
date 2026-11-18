# A literal owned canonical row producer

## 1. Result

Put `N=2^h`. One fixed fifteen-tape graph reads the four supplied descriptors
`h,s,a,j` and returns all `N` bits of the canonical padded-rotation row in
current-wire order. It preserves the borrowed inputs, clears every private
body and temporary guard, and returns every head. Its successful bounds are

```text
T <= 1280 N (h+4),
K_after <= K_entry + N + 20(h+4).
```

Each read, write, unit move, jump and halt costs one transition. `K` counts
historical visited cells. Erasing a cell does not release its history.
The graph has 3,397 instruction locations, independent of the input values.
Its compact sorted-JSON digest is
`1e0115c00b85d77ad78fb6c6202e442b79e82d338b63d8b7171e368d694c2383`.

This is a complete local producer with an owned output. It is not a new
kappa, a complete CRT caller or a discharge of any framework assumption.
The output-linear arithmetic stream in PR7740 has a sharper work bound;
this graph does not claim that bound in literal transitions. See
`CREDITS.md` for source links and `SOURCE-PINS.json` for all exact bytes.

## 2. Entry and return boundary

Use the fixed alphabet `0,1,B,L,E`, represented by `0,1,2,3,4`. Put `W=h+1`.
All fifteen tape owners are distinct. Every head starts at its own origin.
Origins can differ. The caller supplies these roles:

| Tape | Entry body and boundary |
| --- | --- |
| 0 | Positive canonical LSB-first binary `h`, then blank; permanent left marker |
| 1..3 | Exactly `W` LSB-first bits for `s,a,j`, then blank; permanent left markers |
| 4 | Blank address window through relative position `h+2`; blank left guard |
| 5 | Blank point-output window through relative position `h+2`; blank left guard |
| 6..13 | Blank point-private windows through relative position `h+2`; blank left guards |
| 14 | Blank output cells `0..N`, with a permanent left marker |

The legal numeric domain is `h>=1`, `1<=s<=N`, `0<=a<s` and
`0<=j<2h-1`. The input and output markers are at relative position `-1`.
Opaque exteriors are not used. The graph installs and retires its ten
private guards. It never writes a borrowed input or a permanent marker.

On success, output cells `0..N-1` contain the row and cell `N` stays blank.
The output owner remains live. The caller must consume and dispose of it.
Tapes 4..13 return to their complete blank entry states. Every head returns
to its own origin. The preconditions include the supplied windows and
well-formed input framing; there is no promise to recover from aliasing,
unterminated input, corrupted markers or insufficient capacity.

For canonical positive `h` and correctly sized binary fields, invalid
numeric `s,a,j` return `REJECT` before any row output. The point service
validates those values on its first call. Its return clears its private
state; the wrapper clears its own address and bit roles. This is a scoped
rejection guarantee, not rollback for arbitrary malformed physical input.

## 3. Retained point graph and literal composition

PR7735 supplies a 3,237-location graph on fourteen roles. Its input contract
is the same as tapes 0..3 above, plus an exactly `W`-bit current-wire address
on tape 4. Tape 5 holds one owned output bit. Tapes 6..13 are private. It
preserves all five inputs, returns all heads and clears its private state
in at most `1024(h+4)` transitions. Its historical span is at most
`13h+49`, below its published `16(h+4)` allowance.

The new emitter calls the unchanged retained constructor. Each emitted
source instruction gets one new location. Read targets and jump targets
are relocated by this bijection. All read, write and move operands remain
unchanged. A source `DONE` halt becomes one jump to the row controller; a
source `REJECT` halt becomes one jump to wrapper rejection cleanup. Thus
the source transition count is unchanged at the call boundary. The checker
compares every embedded instruction with this exact relocation and checks
the published source graph digest. No Python callback runs during a query.

The wrapper installs `L` on its address and bit roles. These act as the
point service's supplied permanent markers while a call runs. The point
service does not write them. The wrapper retires them only after the final
call. The source's eight private guards are installed and erased on every
call, at the same physical locations. Reuse does not allocate fresh history.

The byte-pinned source loader is retained at its original relative module
name. Its required source paths also remain unchanged. Import resolution
uses that loader directly; no source function or module is patched.

## 4. Address production and row invariant

The wrapper first copies the positive binary height to a private canonical
countdown on tape 6. Canonical zero is the end marker at the origin. It
writes one zero address bit and then one more for each decrement from `h`
to zero. It therefore constructs exactly `h+1` zero bits followed by blank.
Every decrement and every move is part of the finite graph. The countdown
and its temporary guard are cleared before the first point call.

At entry to the call for `x`, the following invariant holds:

1. The address tape has the `W`-bit binary value `x`, where `0<=x<N`.
2. Output cells `0..x-1` have the correct row prefix. The output head is at
   cell `x`, which is blank. The remaining output cells are also blank.
3. The point-output body is blank; all eight point-private tapes are blank.
4. The four borrowed descriptors are unchanged and their heads are home.

The retained graph returns the exact canonical bit for the current wire
`x`. The wrapper reads that bit, checks the next output cell is blank,
writes the bit, moves the output head by one and erases the point bit.
It then increments the address using a literal binary carry scan.

If the low `k` address digits are one, the scan changes them to zero and
changes the next zero to one. It reads the next cell. That cell is blank
exactly when the changed digit is the highest padded digit, at position
`h`. Starting from zero, this first occurs at the increment from `N-1` to
`N`. Thus the program stops after exactly `N` successful queries, without
calling the point service at an invalid address. Earlier increments return
the address head and preserve the invariant for `x+1`.

After the final increment, the wrapper returns the address head, erases its
`W` digits, returns across those erased cells and removes its guard. It
removes the blank point-output guard and returns the output head across
all `N` produced bits. The row is preserved during this return. No host
integer, supplied loop count or variable-distance move drives this process.
The source point theorem and this induction prove the row for every legal
height, independently of the finite test range.

## 5. Full transition count

The retained canonical decrement takes at most `12(v2(v)+1)` transitions
on a positive counter `v`, including its head return. Hence the height
countdown costs less than `24h`, since

```text
sum_(v=1)^h (v2(v)+1) < 2h.
```

Height copy, initial guards, address writes, rewinds and countdown retirement
add only a fixed number of scans. Direct inspection of the emitted loops
gives an initial bound of `64(h+4)` transitions.

There are exactly `N` retained point calls. Each costs at most `1024(h+4)`.
Between calls, let `k=v2(x+1)`. Copying and erasing the returned bit costs
six transitions. Each carried one costs four. The final zero change and
next-cell test cost four. The address rewind costs at most `3k+6`, and
the next call jump costs one. This is at most `7k+17`. The final call has
no next-call jump; its address rewind is counted here as well. Since
`N` is a power of two,

```text
sum_(v=1)^N v2(v) = N-1.
```

All these inter-call operations therefore cost less than `24N`. We use
the larger allowance `32N` below. Final address/bit clearing, temporary
marker removal, output rewind and halt cost at most `16(N+h+4)`.
These bounds include visits to blank frontiers and left markers.

| Phase | Safe transition bound |
| --- | ---: |
| Height copy, guards and physical address construction | `64(h+4)` |
| All complete point calls | `1024N(h+4)` |
| Bit append/retirement and address increments/returns | `32N` |
| Final private clearing and output head return | `16(N+h+4)` |

The sum is `1024N(h+4)+80(h+4)+48N`. For `N>=2` and `h+4>=5`, this is
less than `1280N(h+4)`. The bounds come from the literal loops, not measured
fixture timings. A numeric-domain rejection makes only the first point
call and has no output-return scan, so it also fits this envelope.

## 6. Historical backing

The original fourteen point roles visit at most `13h+49` cells in total.
The wrapper's address construction, countdown, increments and clearing stay
inside the same role intervals. Its bit role stays at positions `-1..1`.
The new row tape visits positions `-1..N`, which add `N+2` cells. Thus the
union of every visited interval has size at most

```text
N + 13h + 51 < N + 20(h+4).
```

Every call uses the same owner and origin for every private role. The bill
is a union of visited cells, not a sum of repeated per-call allocations.
Adding this complete union to entry history is a conservative bound even
when some supplied cells already have backing. Clearing does not reduce
that union. Descriptor transport and relocation corridors are caller costs.

## 7. Evidence and scope

The dense instruction path calls the retained source Tape operations. A
separate sparse path keeps its own cells, heads and dispatch. They share the
emitted graph and the fixture boundary; they are not independent human or
formal-kernel reviews. They agree on the complete returned state, instruction
count, head positions, write counts and historical intervals for:

- All 213 rows and 1,566 bits in the 49 complete canonical networks through
  height three, checked against the unchanged PR4100 compiler.
- All seventeen historical `(h,s,j)=(5,17,6)` rows, with 544 output bits.
- Six complete larger rows through height twelve, including the sharp
  three-rectangle example and a 4,096-bit row. The retained closed query
  supplies these wider expected values.

The historical rows take 1,360,554 transitions in total; the maximum row
cost is 80,716. These are exact service counts, not wall-clock timings or a
matched full-caller comparison. Four invalid numeric domains reject before
output in both interpreters. Wrong output, missing tail and private-retirement
mutations fail. Both adapters reject aliased owners. Every embedded source
instruction and all eighteen retained files are checked exactly.

The arithmetic row theorem has an output-linear stream, whose direct tape
lowering remains open. This contribution instead gives a complete `O(Nh)`
physical service. The generic PR5092 producer generates all layers and joins
a key service; its workload and input encoding differ, so no speedup over
that complete construction is asserted here. Actual CRT descriptor production,
conversion, payload routing, transport, output consumption and disposal still
need a complete caller bill. All five framework assumptions and the selected
frontier remain unchanged. Historical full suites, selected cold replay,
Lean and Docker were not run.
