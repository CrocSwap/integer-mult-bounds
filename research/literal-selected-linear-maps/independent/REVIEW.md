# Independent review of the two selected literal linear maps

**Disposition: accepted for the stated packed two-matrix enabling lemma.**
Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
This is separate root review of another agent's work, not human or proof-kernel
acceptance. No complete multiplication bound or global assumption is discharged.

## Frozen scope and source authentication

Reviewed `linear.py` SHA256
`d56704082b82e37d4a360b8aad7e0af63499f4160c6bbcfd338804453c46fa33`
and `PROOF.md` SHA256
`217b6bbe9271aa5d5c0f0999a231d7386c7ba3fc432a88e3796d70ca283eb322`.
The source is canonical `e54523517d0f03e58352e647c403a5af3e525a57`,
actual MOVE24472 `["MOVE",415,3,99,false]`, frames `[]` and `[239]`.
The exact right and left binary matrices are independently fixed in the
review checker. Their addresses use native coordinate i as bit i, while the
packed field places coordinate zero first. This distinction is substantive.

All fourteen `SOURCES.json` entries were separately authenticated against
their actual `commit:path` through Git: tree entry/blob, complete bytes,
length and SHA256. `SOURCE-BINDINGS.json` retains the receipt. This is stronger
than testing a locally declared checksum against itself. The original frame
lowering and accepted recipe evidence establish the source matrices; this
review does not claim a new proof of the retained Clifford compiler.

## Universal obligations reviewed

I read the complete graph generator and proof. Reversed row-elimination
operations give the claimed matrix in temporal order. Each fixed gate acts
on all f columns, and operations on different columns commute. Both physical
directions use the correct four-chunk permutation. The generated geometry
`[A] x [2] x [M] x [2] x [B]` satisfies `4AMB=V`, with the specified
coordinate order, spectators, Gaussian components and individual bits.
No coefficient-length absorption or supplied-stride premise is used.

The split/chunk/merge invariant preserves full bit records. Alternating
whole-field banks avoid overwriting unread input. Every public DATA read and
return occurs before the sole final commit. The first-five Gamma header,
its opaque trailing symbols, all private guards and bodies, and successful
head positions have matching entry and return contracts. Blank distinct
private owners are explicit premises, and named rejection preserves public
data without promising failure cleanup or retry.

Historical backing is a sum of the intervals of actual roles. In particular,
a smaller reused call retains its earlier larger allocation. The stated
`K_entry+64(V+E+1)` bound and per-role maximum rule handle this correctly;
replacing this with `64(V_current+E_current+1)` would be false on shrinking
calls. External entry supply is not part of the component's runtime theorem.

## Independent full cost census

Before reading the author's cost proof I derived the following counts from
the emitted loops: rewind `3n+3`, clear `7n+4`, unary copy `11n+7`, doubling
`47n+18`, even halving `15n+14`, and unary product `11nm+10n+7`.
The complete column count is

`58V + 78AM + 48A + 16`.

Its next-column update costs `47B+15A+33`, and final guide retirement costs
`3f+15+7(A_last+M+B_last)`. The independent checker sums all header parsing,
volume/geometry preparation, source cloning, every gate and column, final
commit, guide cleanup and guard operations. It agrees exactly with complete
executions, not only their asymptotic order. Algebraic expansion also agrees
with the author's initial-geometry and VOLUME formulas.

The proof's inequalities follow from positive encoded fields, B>=2,
AM,A<=V/8 and V>=1024f. Summing at most 27 fixed gate bills and the explicit
overhead gives the claimed `65536(fV+E+1)` envelope. These are direct-leaf
costs; they do not establish an O(V) arbitrary-f affine service.

## Independent execution and failure detection

The companion `dense_check.py` and `literal_dense_runner.cpp` were written
separately from the author interpreter, test oracle and compiled runner.
Expected outputs are obtained by inverting the complete nine-bit source
matrix truth table, extracting each OUTPUT bit column, and reconstructing
its source address. They are not computed by executing the CNOT word.

The check executes fourteen complete actual m9 packets, including both full
f2 fields, variation of r/P/S/w, and two fixed-inventory grow/shrink/regrow
sequences. It also exercises four malformed inputs. Total counted transitions
across those eighteen packets are 3,076,553,809. The full f2 counts are
1,230,072,483 for the right map and 1,726,632,151 for the left. Whole output,
all private and opaque cells, heads, retained history, exact complete cost,
and DATA's `[V+1 reads, V writes, 4V moves]` census are checked.

Three program mutations are detected: corrupted original-owner commit,
a numerically correct extra instruction that violates the exact cost, and
processing only the first column of every gate. Normal and optimized Python
produce identical structured receipts. Both commands compile the separate
C++17 interpreter in a temporary directory; a compiler named `c++` is required.

```
python -I -W error -B independent/dense_check.py linear.py
python -I -W error -O -B independent/dense_check.py linear.py
```

Finite execution supports, but does not replace, the universal induction and
cost proof. The phases, translation, positive C, old coded/strided layout
bridge, source caller and global precision/cutoff/ownership admission remain
outside this package. A complete MOVE must compose their actual interfaces
and preserve public data through any later arithmetic failure.
