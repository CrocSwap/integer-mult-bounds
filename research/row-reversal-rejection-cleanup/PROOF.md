# Retirement after a finite rejection

The transformer and this supplied-interface application were produced by Nick
Petalas. The visited-interval method is classical. The successful reversal,
its original implementation, and its original successful-run accounting are
Jerry Chen / CubeJerry's #7427, not results claimed here.

## Statement and premises

Fix a program on n tapes with the local instructions `read`, `write`, unit
`move`, `goto` and `halt`. A missing read branch is rejection. The program
and its finite alphabet are fixed before execution. Some tapes are public;
the rest are private. Each private cell the source execution will visit is
initially blank. Public cells may contain arbitrary alphabet symbols.

Add n distinct monitor tapes. Each starts at its own origin. Its window
corresponding to the source run's visited interval, with one additional cell
on each side, is blank on entry. These whole-window blankness premises must
be supplied by the caller. Opaque exterior contents are permitted. This is
not a method for discovering whether a borrowed dirty interval is blank.

Suppose the source halts or rejects after T instructions, counting its
terminal halt or rejecting read. Let I_i be its visited interval on tape i,
let l_i = |I_i|, and let L = sum_i l_i. The transformer emits a fixed program
on 2n tapes that has the following behavior.

1. It simulates every source instruction up to that terminal event.
2. It preserves the source's public contents at that event, erases every
   visited private cell, and returns every original and monitor head to its
   entry position. It erases all monitor marks.
3. It terminates at distinct accepting and rejecting locations, matching the
   source's terminal event.
4. Its time is at most `5T + 16L + 6n <= 21T + 22n` local instructions.
5. Each original head visits at most one extra cell at each end of I_i.
   Each monitor visits the corresponding interval with those two cells.

This is a scoped simulation and cleanup theorem. It asserts no cleanup on a
nonterminating execution, on a host interruption, on an absent blank window,
or on a machine fault outside the declared alphabet and instruction model.
Public writes already performed by a source are not rolled back.

The implementation supports 1 <= n <= 32, source tables of 1 to 10,000
locations, and alphabets of at most 16 symbols. These are compiler input
bounds, not bounds on T or the runtime descriptor values. The theorem holds
for each supported fixed table and every finite run meeting the premises.

## Simulation invariant

For tape i, the monitor head has the same displacement from its origin as
the original head has from its origin. The monitor stores `|` at its origin,
`1` at each other visited source position, and blank at unvisited positions.
Unit head motion makes the visited set an interval containing the origin.

Initialization writes the n origin markers. A source read, write or jump
uses one instruction. Read branches are relocated to the corresponding
compiled locations; absent branches go to rejection cleanup. A halt goes
to acceptance cleanup. A move becomes these local instructions:

1. Move the original head one cell.
2. Move its monitor head in the same direction.
3. Read the monitor. A prior mark branches directly to the next source
   location. On blank, write `1` and jump there.

Thus every source instruction costs at most five compiled instructions.
No source value, integer, coordinate, length or history counter enters the
runtime control. The simulated original contents agree instruction by
instruction with the source. Marks never change a public or private source
symbol during simulation.

## Cleanup invariant

Acceptance and rejection have separate copies of the same cleanup graph.
The terminal status therefore needs no runtime status register.

For each tape and its monitor, the graph first moves both heads left until
the monitor is blank. This is exactly the cell immediately left of I_i.
It moves both heads right once and sweeps the l_i marked cells to the right.
On private tapes it writes blank at every such source cell; on public tapes
it makes no source write. It clears each `1` on the monitor, retaining `|`.
The first blank after the interval ends this sweep. No source cell outside
I_i is written.

Both heads move left once, then continue left through the now blank monitor
until `|`. They are then at their original origins. Erasing `|` leaves the
monitor blank and makes the pair ready for another call. This loop stops
because the origin lies in I_i. Its stopping condition does not depend on
source symbols, which may include blanks and markers anywhere.

Processing a pair never moves or writes another pair. Induction through
the fixed list of n pairs proves all head returns and erasures. Initial
private blankness makes erasure restore its entry contents; exterior cells
retain their contents even when an end cell is visited by cleanup.

## Time and historical backing

Write a for the number of marked cells traversed in the first left scan and
b for the distance from the rightmost source position to its origin. Then
`a <= l_i` and `b <= l_i - 1`.

The first scan and its turn cost `4a + 3`. A right-sweep nonorigin cell
costs at most seven instructions, and the unique origin cell saves one.
The right turn costs three. The return costs `4b + 2`. Hence one pair costs
at most `15l_i + 3`, before the final cleanup halt. With n initialization
writes and that halt, the full run costs at most

`5T + 15L + 4n + 1 <= 5T + 16L + 6n`.

Each source move can enlarge the sum of visited lengths by at most one, so
`L <= T+n`. This gives the displayed bound `21T + 22n`. All loops have a
finite scan bound from l_i, a or b; no numerical length is supplied to the
runtime graph.

Relative to the source execution's historical backing, cleanup adds at most
2n original cells. The monitor run visits at most `L+2n` cells. If its prior
historical backing is H0, the combined historical backing is at most

`source historical backing + H0 + L + 4n`.

Erasing cells does not reduce historical backing. On subsequent calls the
same monitor objects, origins and histories persist. An old long erased
tail is not scanned: the current run marks only its current interval, whose
adjacent unmarked cells stop the cleanup sweeps.

## Whole-record reversal application

The retained table is precisely #7427 at commit
`7662d01d827c95d90032579c168cae78aa531f2f`. Its three descriptor tapes and
DATA are public, and its nine other tapes are private. The two retained
source files are byte-bound in `program.py` and `SOURCES.json`.

The predecessor stages the result and validates packet cardinality before
writing DATA. Its stated rejection contract preserves all public contents
but does not retire private state or heads. Taking that source property as
a premise, the new simulation preserves public contents on rejection and
adds the missing retirement. On acceptance it implements the same complete
record permutation. The new graph uses 26 tapes and the original four
symbols. It adds no trusted shape, address stream, runtime decoded integer
or payload callback.

For a valid packet the predecessor's source bound is O(V+E), so the new
bound is O(V+E). For malformed packets the statement is O(T) in the actual
finite rejected source execution. A descriptor can request much more work
than the actual DATA length, so no O(actual payload) rejection bound is
claimed. Providing the additional monitor windows and their owned lifetime
is an explicit caller obligation.

`verify.py` executes the emitted graph on valid and malformed packets and
on a rejected-then-valid reuse of the same 26 objects. Generic fixtures
also move left of the origin, retain public writes made before rejection,
and erase private intervals. These finite checks corroborate the invariant
proof; they do not enumerate all descriptors or prove a multiplication
theorem. Independent human and formal proof-kernel review are unclaimed.
