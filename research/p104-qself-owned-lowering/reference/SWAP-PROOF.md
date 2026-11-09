# Actual current SWAP and SIGNED_SWAP services on coded tapes

Prepared for **@CubeJerry**, with substantial OpenAI assistance. Apache-2.0.
This is a source-bound implementation lemma. **No new κ.**

## 1. Exact source and quantified claim

Canonical base is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`. The retained
`research/p104-productive-controller/caller.py`, function `replay`, defines
the two ordered operations exactly as

    SWAP(x,y):        (x,y) <- (y,x),
    SIGNED_SWAP(x,y): (x,y) <- (y,-x).

In particular, the negated operand is the **old first operand**. Both fields
are outputs. This definition is pinned in SOURCES.json and in the unmodified,
reference-only `vendor/current_caller.py`; that file is not imported by the
new verifier. The current `source_ir.current_caller` emits each operation for
all 104 source columns, retaining its ordered actual fields and source token.

For these two operations, `compile_swap` emits finite tables in the unchanged
published lifecycle `execute_table` grammar. Tables use only local-symbol
branch, local-symbol write, unit move, goto, halt and reject. Their ordered
ports are `(x,y,staged-x,guide)`. The two work ports are the **same inventory**
needed by the preceding current ADD/SCALE tables; no extra numerical tape or
runtime payload callback is introduced.

The inputs are nonempty complete complex fields with the same ordered
component shapes and coordinate meanings. Each component is a nonempty
little-endian two's-complement word followed by virtual delimiter 2. The even
component count groups successive real/imaginary pairs into complex records.
Corresponding widths agree, but widths may vary between components. Matching
components use the same numerical grid. Each virtual symbol occupies the
inherited three raw nonblank binary bits. An actual physical blank immediately
follows the complete last component; there is no encoded logical blank or
hidden live tail in a public field.

All public, work and context heads start at their current origins. The two
data tapes and two used work tapes are physically distinct; all other supplied
ports are nonaliasing. Every port retains its current owned segment and protected
ancestor boundary. Initially dirty work consists of contiguous raw binary
prefixes ending at a physical blank. These are the original lifecycle and
`retire` contracts, not facts inferred from numerical values.

**Theorem.** On those inputs, SWAP always succeeds. SIGNED_SWAP succeeds if
and only if no component of x is the most-negative value of its original
signed width. Equivalently, the requested output pair fits the original
component widths. On success it returns the exact ordered pair above,
preserves both complete field extents, component boundaries and common grids,
returns every supplied head to its current origin, and returns all work
physically blank under the original primitive wrapper. It makes no write to
either public field before the complete pair has passed its checks.

The time is `O(V+D+Q)`, with two used work tapes and current work backing
`2V+3+O(1)`. Here V is either public field's physical length, D is total
initially occupied work, and Q is the fixed supplied work/context inventory.
Erased historical backing remains counted as a coordinatewise maximum.

## 2. Finite signed-word admission

For SWAP the staged word is a literal copy of x. Its signed value and width
are unchanged, so its range condition is automatic. The second candidate is
the original complete y field, which remains untouched until installation.

For SIGNED_SWAP the first pass computes the ordinary complement-plus-one
word into the separate staged field. Let x_i be a bit of x, with i increasing
from zero. Set c_0=1 and use

    u_i = 1-x_i+c_i,
    z_i = u_i mod 2,
    c_(i+1) = floor(u_i/2).

Both carries and bits belong to `{0,1}`. These are finite transition choices,
not runtime host arithmetic. The generated table remembers the last input
and output bits sx,sz, then validates the complete component at its delimiter.
The width is never supplied or decoded by the routine.

For a component of width w, write X and Z for the unsigned bit-word values.
Summing the digit equations yields

    Z = 2^w-X-2^w*c_w.

If X=0, the carry remains one and Z=0. Otherwise the carry becomes zero at
the first one bit of X and remains zero, so Z=2^w-X. Consequently:

* If the signed input x is zero, the signed output is zero.
* If x is positive, its sign is sx=0 and the output sign is sz=1; its signed
  value is -x.
* If x is negative, sx=1 and `1 <= Z <= 2^(w-1)`. The output has sign sz=1
  exactly when `X=2^(w-1)`, meaning `x=-2^(w-1)`. That is the sole overflow.
  Otherwise sz=0 and the signed output is -x.

The final finite guard therefore rejects **exactly** `sx=sz=1` in signed
mode. This includes w=1: zero is the only admitted first input, while the
second input may be either -1 or zero. There is no negative-zero convention.
The old second operand may be most-negative at any width; it is copied, not
negated. Equal values on distinct tapes are allowed, with no independence or
uncorrelated-input hypothesis.

For completeness, any representable -x passes this exact guard. For soundness,
the displayed identity proves that any passing staged word represents -x.
No intermediate signed sum, extra signed word or temporary-word headroom is
required. The table emits exactly one bit per input bit and one delimiter per
accepted component. Common numerical grids are preserved without division or
rounding. If the represented inputs already carry numerical errors, the
output error pair is the same signed permutation of those errors; absolute
componentwise bounds and every permutation-invariant norm are unchanged.

## 3. Protecting both outputs with two work tapes

The first pass reads x and y in lockstep. The staged work holds x or -x, and
the original y is the other candidate output. Neither public field is written.
A second work guide holds virtual marker 5 followed by one virtual 1 for
every consumed public symbol, including delimiters. Empty components,
mismatched boundaries/frontiers and an odd or empty component count reject.

The table checks every component's signed guard, both final frontiers, and
the staged frontier before starting installation. In particular a failure in
the last component leaves **both** public contents unchanged. Under valid
geometry, the protected candidate pair at that point is `(original y, staged
signed x)`; it is unnecessary to duplicate y on a third work tape.

Let L be the common virtual field length, so V=3L. The guide contains marker
5 followed by exactly L ones. Starting at its blank frontier, the table moves
the guide left and reads it. For each one, it moves x, y and the staged field
left once. On marker 5 they have each moved exactly L symbols to their current
origins. No numerical length or position query controls this rewind. It stops
before another public left move could cross an origin.

The table then advances past the guide marker. For each guide one it reads
the old y symbol and the staged symbol into its finite control **before**
writing either public field. It writes the saved y symbol to x, the staged
symbol to y, and advances all four ports once. An induction on the installed
prefix proves that the prefix has the required two outputs while the unread
y suffix remains original and the staged field remains unchanged. Reading
before writing is possible with a fixed number of local symbols in control;
there is no unbounded source buffer or uncharged access.

The two candidate symbols have matching delimiter positions. Installation
therefore preserves both complete shapes and ends exactly at their physical
frontiers. All supplied heads are then returned by the unmodified table
executor's raw-origin loops. The unmodified `Controller.primitive` retires
all work before and after a successful service, erasing actual raw bits
including coded guide markers. Writing a coded logical blank is not used as
physical erasure. Additional work is also retired; read-only binary contexts
and all other public spectators are preserved.

The proof is by component and by consumed prefix and is independent of width,
record count, correlation between inputs, and the particular old contents of
the initially valid dirty work. Physical aliasing is excluded by the original
controller and by source binding; equality of numerical values is harmless.

The signed operation can be undone by the same table with **reversed ordered
ports**. If its first call returns `(y,-x)`, a call on the ordered pair
`(-x,y)` returns `(y,x)` in that reversed naming, restoring the original
physical fields. The second negated input -x cannot be most-negative after a
successful first call. Four forward calls need not all be admitted when y
was most-negative; no such stronger same-domain assertion is made.

On rejection the inherited executor raises immediately. Public contents have
not been written, but heads may be advanced and work occupied; success cleanup
has not run. No physical rollback or interruption recovery is claimed.
For otherwise well-formed inputs, arithmetic rejection stops in the first
pass. Its visited prefix and work are bounded by the corresponding complete
pass, so it also obeys the time/backing ceiling below without acquiring a
cleanup guarantee.

## 4. Complete costs and retained backing

The first pass consumes L actual input symbols and performs bounded work per
symbol on both sources, the staged output and guide. The negation carry and
all remaining state (last bits, component parity and initial-field flag) are
finite. The guide rewind and installation each make L iterations. Both
source access passes, writes of both outputs, every head movement and physical
retirement are included.

A `CodedPort` read/write/unit move costs at most 13 physical cell actions.
Charging table-row fetches as well, conservative allowances are 128 per
first-pass symbol, 64 per rewind symbol, 128 per install symbol, and 96 per
symbol for final head restoration and work retirement, plus fixed entry/exit
cost below 256. A dirty initial raw prefix costs at most `5D+O(Q)` to retire;
untouched extra work/context ports add only fixed entry/exit work per port
because their heads start at their origins. Thus one explicit ceiling is

    physical cell actions + table-row steps
        <= 1024*(L+1) + 8D + 32Q.

The fixture observer counts table-row fetches separately without changing
the emitted rows or the original interpreter. The numerical runtime does not
inspect these counters. This ceiling is intentionally loose and does not
certify any complete historical numerical allowance or full supplier bill.

The staged field has V raw bits; the guide has V+3. Current work backing is
therefore at most `2V+3+O(1)`, including the frontiers. A prior larger body is
physically erased before reuse. Later smaller calls stop at their current
blank frontiers and do not scan the old erased high-water range. For each work
tape the retained allocation is bounded by the maximum of its prior backing
and its current needed extent. Repeated calls pay their actual current volumes
and initial dirt, not a fictitious deletion of visited tape cells.

All supplied source fields, descriptors, parked ancestor segments and separate
caller storage remain in the caller's full inventory. This lemma controls
the two used current work tapes; it does not remove those other storage terms.

## 5. Exact current source binding and composition

The original source and lowerer, with immutable pins in SOURCES.json and
DEPENDENCIES.json, give the following complete two-output class:

| Original source region | Raw instructions | Emitted services |
| --- | ---: | ---: |
| Right-boundary SWAP | 27 | 2,808 |
| Left-boundary SWAP | 30 | 3,120 |
| Outer SIGNED_SWAP | 48 | 4,992 |
| Total | 105 | 10,920 |

There are exactly two generated tables: 130 rows for SWAP and 171 for
SIGNED_SWAP. `source_literal` checks the exact boundary instruction or exact
outer source site, column, operation and ordered fields. For an unremapped
event it additionally checks the original `(104*x+j,104*y+j)` binding.
For the original compiler's remappings it follows the active final member
of each exact wrapper grammar. The separate issuing PAID token retained by
`product-right` is provenance, not an active scalar instruction.

The remapped owner tuple is the tuple actually emitted by the authenticated
lowerer. Its geometric alignment and mapping theorem remain premises; merely
wrapping a forged tuple would not prove its provenance. The positive nested
product/unit-fragment check uses the unchanged original `IR.remap`.

Combined with the byte-identical preceding ADD/SCALE tables, this covers all
**377,762 original ADD/SCALE/SWAP/SIGNED_SWAP service occurrences** of the
642,410-event selected caller. The two classes have disjoint source tokens,
compatible input formats and the same two work ports. COPY retains the
original lifecycle implementation. The new tables change no field assignment,
native operation, paid job, chronological order or paid histogram.

Assume each actual source cut supplies matching complete coordinate shapes,
common grids, distinct owned ports and the exact signed range required at its
output. Substitution of the appropriate table at each of these original
arithmetic services preserves its numerical endpoint, geometry and successful
lifecycle contract. Induction over those actual sites proves the scalar
substitution implication. It does not prove the source geometry premises,
native/recursive entrance and return predicates, the full compiler/ownership
theorem, global precision/cost closure or analytic recovery.

## 6. Prior work and remaining obligations

The preceding current-scalar package supplies the authenticated coded
ADD/SCALE interface and its general rational finite-carry proof. This package
retains its `Builder`, physical fixture and current source maps unchanged;
those are credited dependencies, not new results. It completes the omitted
two-output source class on the same inventory and tests their real composition
on the entire original 5,720-service right boundary.

The older #3098 `physical-scalar-stream` executes inherited scalar recipes on
aligned packets; its actual caller/owner join remains distinct. Historical
#969 `complex-swap-runs-seed37` defers scalar names and pays boundary copies in
PR626/PR696 words. It explicitly excludes physical array execution and current
production admission. The exact Laurent controller replay in #4516 checks
the algebraic swap signs, not these numerical tables. Classical swapping and
two's-complement negation are not claimed as new arithmetic discoveries.

Current native phase/Gaussian maps, row/recursive services and their exact
error contracts, complete compiler/owned lifecycle composition, and the
whole-caller precision/full-cost/analytic join remain open. No native service
is replaced by an ordinary swap. All five selected assumptions remain in
force, and the selected conditional κ remains 0.003125804.
