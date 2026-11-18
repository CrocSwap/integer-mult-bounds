# A complete local flat-guide lifecycle

## Domain and machine

Let N and W be positive integers and L=N(2W+3). The caller supplies their
canonical positive binary encodings, least significant bit first, between
LEFT and RIGHT markers. Their heads start at the first bit. N is the
complete record count, including spectators. Its production from root
geometry, and the derivation of W, are outside this result.

There are seven distinct tapes: two preserved descriptors, reusable binary
work, unary N, unary W, an owned guide and an owned target. The three work
tapes start blank at their origins. The guide has an exact granted window
of L+2 cells. Its old cells can be arbitrary. The target has L arbitrary
payload cells between fixed LEFT and RIGHT guards. Guide and target heads
start at their origins. Exterior cells are borrowed and must be preserved.
No hidden old private tail is admitted by this contract.

The unchanged David Arias machine and counter are declared inputs. The
machine has seven symbols and six instruction forms: branch on a scanned
symbol, write, unit move, fixed goto, halt and reject. Only the external
interpreter stores head coordinates and resource statistics. The emitted
program cannot inspect them. Assembly accepts no runtime N or W. The
producer has 210 instructions; INIT and CLEAR each have 40; retirement has
16. All use the same seven physical tapes for every input size.

The current source guide is encoded by

| Source guide value | Tape symbol |
| --- | --- |
| left boundary | LEFT |
| right boundary | RIGHT |
| numeric zero cell | ZERO |
| real/imaginary separator | UNIT |
| end-of-record separator | MARK |
| represented blank cell | BLANK |

This map is injective on the current zero-template format. Interior BLANK
is a legitimate guide value, not an end marker. The two consumers are the
unchanged PR7663 reset graph restricted to these produced values and
lowered by this symbol map. They are not callbacks into the source simulator.

## Production and complete return

Install LEFT at each of the three work origins. Apply the retained binary
converter first to N and then to W, reusing its fully cleared binary work.
It emits unary N and W, preserves the binary descriptors and returns all
three participating heads to their first cells. The converter's canonical
decrement proof covers every positive integer, including powers of two.

Write LEFT at the guide origin. For each unary N mark, traverse unary W
twice. Write W numeric zero symbols, the first separator, another W zeros,
the second separator and one represented blank. Rewind W after each pass.
Advance the unary N head once per complete record. At its RIGHT marker,
write the guide's RIGHT marker. Rewind the guide to its origin.

Induction on records proves that after j outer iterations the complete
first j records have the required values and the output head is at their
successor cell. The inner unary loop proves the two width counts. No old
guide symbol controls production. Every old cell in the granted guide
window has been overwritten before its rewind begins. The only LEFT in
the resulting guide is its origin, so the rewind returns correctly even
when the old guide had false markers or interior blanks.

Erase both unary bodies, their RIGHT markers and their installed LEFT
markers. Erase the remaining binary-work LEFT marker. All three work
tapes are blank in every visited cell and their heads return to zero.
The descriptors keep their complete bytes and heads. The target is
untouched. The produced guide remains at head zero for its consumer.

## Actual source consumption and retirement

The finite INIT and CLEAR tables branch only on the produced guide. Their
outward pass writes exactly the L target payload cells. INIT writes the
scientific zero template, including both separators and represented blanks.
CLEAR writes physical blank. Both graphs return guide and target heads to
zero. The guide, target guards and exterior are unchanged. The source's
position induction applies to arbitrary old target payloads.

After consumers return the immutable guide at its origin, retirement
scans its body to RIGHT and blanks every cell it crosses. It erases RIGHT,
rewinds through the now-blank body to LEFT, and erases LEFT last. Thus the
entire granted guide window is blank and its head is zero. The left marker
is retained only until the return finishes. No backward scan tries to use
a marker that was already erased. Descriptors, target and other tapes
remain unchanged during guide retirement.

The composition is production, literal INIT, literal CLEAR and retirement.
Numerical work between the reset consumers is a separately charged service.
It must preserve the immutable guide and return its required heads. It is
not supplied by this theorem.

## Exact instruction ledger

Count every emitted instruction, including branches and fixed gotos. The
retained converter has exact cost

```text
c(x) = 24x - 7 popcount(x) + 15 bitlength(x) + 12 <= 44x.
```

Its proof uses sum from k=1 to x of v2(k)=x-popcount(x), so binary borrow
scans are charged. A retained rewind from head h costs exactly 3h.

One width pass emits W cells in 5W+1 instructions, then rewinds in 3W+3.
The two passes, three separator/blank writes and the outer advance cost
16W+17 per record. There is one final outer branch. Guide termination and
return cost 3L+5. Unary N cleanup costs 10N+11, including its initial
rewind; unary W cleanup costs 7W+8. Marker setup costs six, guide opening
costs two, binary-work cleanup costs two and the final halt costs one.
Consequently

```text
T_produce = c(N)+c(W)+22NW+36N+7W+36.
T_INIT = T_CLEAR = 9L+11.
T_retire = 7L+10.
T_lifecycle = c(N)+c(W)+72NW+111N+7W+68.
```

For a reset, the outward cell costs five instructions and a return cell
costs four. Start, turn, final boundary and halt add eleven. For retirement,
each forward erased cell costs four; the rewind costs 3L+3, and entry,
delimiter erase, origin erase, final goto and halt add seven.

The producer satisfies T_produce<=40L. After applying c(x)<=44x, the
difference is at least W(58N-51)+40N-36, which is positive for N,W>=1.
Retirement is at most 9L because L>=5. The two resets cost 18L+22.
Thus the complete lifecycle is at most 72L instructions. This is an
all-size count from the emitted paths, not an extrapolated timing result.
The smallest case takes 346 instructions for L=5. The complete N=512,W=1
view takes 106258 instructions for L=2560.

## Retained capacity

Include every cell between an origin and the furthest visited position,
even after the cell is blank. Write ell_N=bitlength(N), ell_W=bitlength(W).
The exact total over the seven tapes is

```text
2L + N + W + ell_N + ell_W + max(ell_N,ell_W) + 14 <= 7L.
```

The two full windows contribute 2L+4. The unary tapes contribute N+W+4.
Binary work contributes max(ell_N,ell_W)+2. Preserved descriptors contribute
ell_N+ell_W+4. Heads visit no negative position on valid inputs. Since
ell_x<=x, 2(N+W)<=L and L>=5, the displayed upper bound follows.

This is the visited capacity of one invocation on the stated windows.
If tapes already have reserved historical spans H_i, charge
sum_i max(H_i,s_i), where s_i are the seven current spans. Prior empty
storage is not released by this proof. Changing an owned guide or target
window requires a separate complete old-extent contract. Borrowed exterior
cells in the fixtures do not become free private storage.

## Evidence and limits

The complete tables are saved in TABLES.json and regenerated exactly.
Forty-two shapes exercise binary shrink boundaries, both components,
width 17 and complete current views. A separate dense interpreter executes
every phase and agrees on all cells, heads and instruction counts. The
source guide producer supplies an independent expected-format oracle.
The checker inspects full visited spans and all borrowed exterior cells.

Five actual instruction faults detect a wrong zero value, a skipped
represented-blank write, a premature RIGHT, a missing origin return and
an unerased guide LEFT. The retained binary converter also rejects a
redundant high zero. Rejection need not be atomic or restore dirty work;
the positive theorem assumes canonical descriptors and blank conversion
workspace. These controls are not a global malformed-input recognizer.

Root descriptor production, arbitrary historical-window reuse, numerical
children, native adapter movement, the actual recursive owner map, complete
compiler workspace and the whole physical tariff remain open here. The
delayed-cover root producer in PR6719 has a different consumer; this work
reuses its retained machine/counter and does not repeat that root theorem.
No framework assumption or multiplication theorem is discharged. There
is no new kappa or selected-frontier change.
