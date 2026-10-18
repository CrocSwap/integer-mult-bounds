# Local replacement and cost argument

Fix the PR589 word identified in SOURCES.json. Expand every A/B multi-source
gate into one elementary addition per listed source. Distinct source
operands of one gate commute, so this expansion preserves its F2 map and
nonnegative integer transfer. The native exporter already charges one ADD
per operand. Moving the source operands just before their own elementary
ADD instead of before the entire multi-source gate preserves each register's
frame path; the unchanged legality checker also checks the exported result.

## Exact local maps and their lengths

A window uses n≤4 distinct physical z registers (sources or helpers), all at
one frame. Its elementary operations are `x[d] ^= x[s]`, with d≠s. They
generate GL(n,2). `build.py` performs breadth-first search from the identity
using row bitmasks. An independent routine in `verify.py` represents a map by
the images of its input basis columns and explores the generators in a
different order. It obtains exactly ∏(2ⁿ−2ᵏ), k=0..n−1, states.

The verifier additionally checks that the distance potential is zero only
at identity and differs by at most one along every directed generator edge.
Consequently every word reaching state M has length at least distance(M).
For each selected replacement, the explicit new word reaches the same M
as the original and has exactly that length. This proves each nominated
local minimum in its full transvection group; it does not assert a minimum
for the entire R439 circuit. There are no gates on extra physical wires.

## Frames, dirt, targets and literal cleanup

Only original contiguous windows are selected; chosen windows are disjoint.
Every selected old and new word uses exactly the same physical participant
set, and each instruction is assigned the original common frame. No target
register participates. During such a window there are no accesses at other
frames; the first access to each participant makes the same frame movement
as before, and its frame on exit is the same. All subsequent accesses
therefore start at the same frames. The native harness compares the full
per-register MOVE sequences, including ranks, as well as every COPY/ERASE
record, between baseline and candidate. All 661 initial columns are arbitrary;
helpers are never initialized to zero by this reasoning.

The same local F2 map restores the identical complete state at each window
boundary. Hence the raw A/scatter/B map is unchanged, including every
interleaved target read. D and scatter are retained verbatim. In the
candidate, C is the **literal reverse** of all new z-destination A/B gates,
placed at the full frame. Each such elementary XOR is its own inverse.
Thus C satisfies the original H4 and restores the raw z map exactly.
H1–H3 follow from unchanged D/scatter and the source/helper-only replacements;
H5 follows from the unchanged raw map. The unmodified PR589 checker separately
checks all five hypotheses, all four conclusion components, complete geometry,
frame nesting and the full `y ← y+x` endpoint.

For the original grouped C, reversing sources within one multi-source gate
does not matter: they share a destination which is distinct from every
source, so those elementary transvections commute over F2 and over the
nonnegative integer bound calculation. This justifies counting its scalar
expansion as the reverse of the expanded A/B z word.

## Positive bounds in both orders

Replace XOR with positive integer addition, and let P(old), P(new) be the
resulting n×n nonnegative matrices. Every selected window satisfies

```
P(new) ≤ P(old),  P(reverse(new)) ≤ P(reverse(old))
```

entry by entry. For any nonnegative incoming bound vector, this gives the
same domination of the outgoing vector. Inside a positive-addition window,
every coordinate is monotone, so every new prefix is at most the new window's
endpoint, itself at most the old endpoint. The unchanged surrounding positive
updates propagate inequalities. Fresh copied centers inherit their actual
source bound; discarding the temporary resets the same coordinate to zero in
both programs, so those operations are also monotone between corresponding
boundaries. The paired C windows and the reversed complete word use the same
two inequalities in the appropriate order. This proves that neither full
cancellation-free prefix maximum increases. The exact native replay improves
the two maxima to 43,671 and 928,888.

The retained checker uses the same expression

```
payload = 64 * forward^3 * reverse^2
```

yielding 4,599,240,171,725,128,575,517,618,176 for this candidate, with bit
length 92. It stays below the inherited 2^104 ceiling. This is the native
finite-word signed-lift bound, not a newly derived full recursive precision
or multiplication-exponent certificate.

## Complete local bill and search boundary

The 85 A windows save 115 elementary additions and the 10 B windows save 12.
All are z gates, so rebuilding literal C saves exactly the same 127 again.
D costs 18,085 and scatter costs 527 in both words. The full exported ADD bill
therefore changes from 24,305 to 24,051. Every helper, copy and paid rank has
been retained: rank histogram
`{1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}`, rank mass 5,129,
and nine rank-seven retained totals. Native 5/9/11-stage bridge bills stay
666 / 1,998 / 2,664; copy bills stay 45 / 81 / 99.

The nomination exhausts the original length≥2 windows of the declared class,
chooses one seeded shortest representative for each map, applies the stated
guards, and selects compatible intervals by weighted dynamic programming.
Other shortest representatives might satisfy the guards when the nominated
one does not. Rescanning after rewriting, crossing frame/target boundaries,
adding helpers, changing whole blocks, and joint optimization with pending
PRs are outside this certificate. The window receipts and fresh regeneration
make the actual finite domain explicit.
