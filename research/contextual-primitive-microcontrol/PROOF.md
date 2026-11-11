# Finite-state lowering of the actual primitive wrapper with protected contexts

Prepared for **@CubeJerry** with substantial **OpenAI assistance**. Apache-2.0.

## 1. Exact source, purpose and boundary

Canonical base is `e54523517d0f03e58352e647c403a5af3e525a57`. The selected
conditional result there is `363005817/100000000000`; its application review
retains the five framework assumptions. This package changes neither that
record nor the supplier invoice.

The source operation is the **actual** `Controller.primitive(token, fields)`
in `research/scalar-table-microcontrol/vendor/machine.py`, Git blob
`acf475e4fccaff2fb64bd5b0b3f3fc0d246dc592`. Its steps are:

1. Retire each `primitive_work` tape, in the fixed order.
2. Execute the fixed selected table on coded `fields + primitive_work`,
   followed by raw binary `primitive_context` ports.
3. On successful return only, retire each work tape again, in the same order.

The source `execute_table` returns all coded and context heads to their
local origins on `halt`. A source rejection raises before those successful
returns and before step 3. This exact distinction is part of the theorem.

PR #6999 already proves an explicit finite-control lowering of the
**no-context executor**, with exact clock `C=A+U`; the proof and source are
retained unchanged. It explicitly excludes even unused readonly contexts,
wrapper retirement and the Controller. We reuse its coded-port construction.
The new implication is that the real primitive entry/return interface,
including raw descriptor access and ownership cleanup, admits the same
kind of concrete machine. This is not another proof of the qualitative
principle that finite interpreters can be simulated.

The full `Controller.run`, its recursion stack, row services, header
producer, actual complete supplier registry, numerical correctness of
every provider and the physical-to-invoice conversion are **not** lowered
or admitted here. The source Controller constructor is not executed by
the new target. Its relevant fixed separation conditions are explicit
construction-time hypotheses below.

## 2. The quantified primitive contract

Before runtime input varies, fix:

- A finite nonempty `N`-row table in the closed six-opcode grammar of
  #6999: `branch`, `write`, `move`, `goto`, `halt`, `reject`. Targets and
  fallthroughs are in range; ports and write symbols are literal integers;
  branch keys are unique symbols `0..6`; moves are `-1` or `+1`.
- A total fixed inventory of `P >= 1` physical tapes. Select ordered tuples
  of `F >= 1` fields, `K >= 0` work tapes and `R >= 0` contexts. All selected
  tape identities are pairwise distinct and in the global inventory.
  Let `L=F+K+R`. Table ports `0..F+K-1` are coded ports; the last `R`
  ports are raw readonly contexts. A table-port index is not silently
  identified with its global tape index.
- A service token whose table and layout are fixed parts of this finite
  template. The compiler resolves the token before runtime. Unbounded
  input-dependent table generation or service-token lookup is outside the
  claim.

All tapes use the same physical alphabet `0..6` as the retained source.
The normal local-origin domain has a unique `LEFT=2` at coordinate `-1`,
no other physical LEFT in the local body, and physical `BLANK=6` after a
finite contiguous body. Old work bodies are arbitrary finite binary words;
their initial head positions `h_i >= 0` may exceed their current lengths.
Thus the entry contract includes formerly larger or displaced work tapes.
Data tapes contain complete three-bit codes and have aligned heads when
the provider requires that numerical domain. A context contains a finite
raw binary word, and its head is between origin and frontier, inclusive.
No context is encoded as three-bit virtual symbols.

The compiled program has exactly the same `P` tapes and alphabet. Every
state is a fixed one-tape read, write, unit move, no-op or terminal. It
contains no runtime source-table lookup, host integer accumulator, port
dictionary, dynamic continuation stack or extra work tape.

**Theorem.** For every terminating admitted execution of the source
primitive, the generated program has identical mathematical tape contents,
heads and terminal/rejection label. Its active raw-operation trace is
identical. If `A` is the number of source physical reads, writes and unit
moves across the **whole wrapper**, and `U` is the number of fetched source
table rows, then its serialized multitape clock is exactly

`C = A + U`.

`A` includes old-work entry positioning, all pre-retirement, actual context
reads/moves, table-final origins and successful post-retirement. If
pre-retirement rejects, `U=0`. Success returns all participating heads to
their origins and leaves every work body physically blank. Rejection
preserves the exact source partial effects and does not imply rollback,
successful head return or post-cleanup.

Readonly context contents and nonparticipating global tapes are unchanged
at **every prefix**. Head visits and historical maxima agree with the
source. A prefix correspondence holds even when the table or an origin
scan does not terminate; this is not a termination theorem for arbitrary
tables. Outside the normal origin domain the simulator can still match
the source operation-by-operation, but no intended-origin or totality
guarantee is inferred from malformed markers.

## 3. Construction and protected-context semantics

First invoke the authenticated #6999 compiler with `L` local ports. Keep
its coded-port row expansions, dispatches, error paths and final origin
chain unchanged. Every source row has exactly one dispatch no-op. Replace
only a row whose accessed port is a raw context:

| Source operation | Emitted active operations and continuation |
| --- | --- |
| Context `branch` | Read once; accept raw `0`, `1`, `6` and take the specified/default successor; reject any other symbol as `binary context alphabet`. |
| Context `write` | Enter `native context is read-only` immediately after the row dispatch; perform no physical write. |
| Context move right | Read once; on `0` or `1`, move right once and continue; otherwise reject as `context frontier cannot be crossed`. |
| Context move left | Move left once and read. On LEFT, move right once before `native context crossed its local origin`; otherwise continue at the displaced head. |

The last rule deliberately checks only LEFT, exactly as the source does.
It does not introduce an unpriced full header validation, and it does not
reject another malformed physical symbol that the source left-step
accepts. Raw context blank is `6`; coded-port frontier denotes virtual
symbol `4`. Confusing them changes source branch behavior.

The pre-existing origin routine is a literal physical scan, so the same
three-state loop applies to raw heads as to coded heads. It does not round
a raw head to a multiple of three. All ports, including unused contexts,
retain the source order of final origin returns.

Next splice literal retirement graphs before the first row and after the
table's success-origin chain. Each retirement graph has:

1. A three-state origin loop.
2. A body read. On `0` or `1`, write BLANK and move right, then repeat.
   On BLANK, leave the loop. On any other symbol, enter the exact source
   `contiguous binary body` rejection terminal.
3. Another three-state origin loop and the fixed successor.

There are nine new states per retirement occurrence. The post-retirement
chain is reached only from the source executor's success exit. It is not
connected to any rejection terminal. The work tuple is statically
unrolled in the source order both times.

The context replacement leaves obsolete coded-context expansions in the
construction array. A standard finite reachability pass removes them;
no source jump can enter a microstate because source targets are table
rows. Finally map all local port constants to their fixed global tape
identities. The target graph contains no write state addressed to a
context, and no state addresses an unselected global tape.

The implementation checks closure and port domains after this remapping.
Reachability and remapping are finite precompilation operations, not a
runtime address oracle.

## 4. Bisimulation and caller substitution

At entry, relate the source wrapper to the first pre-retirement state with
identical tapes and heads. Within a retirement, relate the next literal
source raw action to the corresponding target action. The three origin
states implement `move(-1)`, the marker test and either the next loop or
`move(+1)`. The body loop implements the source read/write/move order,
including the final BLANK read and malformed-body rejection. This relation
is independent of body length and head displacement.

After pre-retirement, relate source row `pc` to its one target dispatch.
The unchanged #6999 coded-port theorem supplies the relation for each
coded row, including malformed codewords, repeated first-bit reads,
frontier materialization and displaced rejection heads. The four cases in
section 3 prove the relation for every raw-context row and every scanned
physical symbol. Each source fetch contributes one dispatch transition;
each raw action contributes one target transition. Neither a terminal
label nor a splice boundary contributes another transition.

On `halt`, both machines execute the same full ordered origin chain, then
the same post-retirement chain, then succeed. On rejection, both stop at
the matching terminal before these later operations. Induction on this
interleaving proves endpoint and active-trace equality. Counting the two
event classes proves `C=A+U`. The same argument on finite prefixes proves
the nontermination qualification.

The theorem is consequently an **interface substitution lemma**. An
enclosing caller that enters the pinned primitive under the stated
separation/domain conditions and inspects only its permitted tape/head/
terminal interface can replace that primitive call by the generated entry
graph. The caller observes the same success or partial failure and pays
the explicit clock above. A fixed finite service registry can use a
disjoint finite union of these graphs with entry states selected by its
fixed caller control; no new tapes are needed. This transports a proved
source provider contract through the wrapper. It does not prove the
remaining caller, install a non-finite token family or infer numerical
provider semantics from a table's syntax.

## 5. Complete local cost, setup and history

For a successfully retired contiguous binary work body of physical length
`B`, starting at local position `h >= 0`, the first origin costs `2h+3`.
The forward erasure loop costs `3B+1`; its final origin costs `2B+3`.
Therefore the exact retirement bill is

`R(B,h) = 2h + 5B + 7`.

Let `B_i` and `h_i` describe the old work entries, and `B'_i` the work
lengths after successful table return. The table has already returned
each head to zero. Writing `A_table` for all raw actions inside the source
executor, including its final origins, the full successful bill is

`C = U + A_table + sum_i (2h_i + 5B_i + 5B'_i + 14)`.

This equation explicitly retains an old dirty physical body that is longer
than the new field. Here `B_i` is the current contiguous nonblank prefix,
not an already blank historical allocated tail. Such a tail is not scanned
solely because it was once allocated, and its storage is not thereby freed.
The equation does not charge only the latest logical width. Context header
reads are in `A_table`, and a context ending at position `g` pays `2g+3`
for its final origin. A supplied unused context still incurs that return.
No runtime full-header validation is present in the source wrapper;
semantic header validation and production setup require their own charged
provider/caller contracts. Static source/layout validation belongs to
precompilation, not this runtime equation.

The source predecessor emits at most `48N+3L+4` states. Context replacement
adds at most three states per accessed row; five shared error terminals
and two nine-state retirement occurrences per work port suffice. Retaining
a harmless extra `N` allowance gives the convenient bound

`S <= 52N + 3L + 18K + 9`.

Reachability pruning only reduces this count. Program fields/ports and
branch targets are fixed control constants. A compact description uses
`O(S(log(S+1)+log(P+1)+1))` bits plus all literal finite error labels and
the source description. If the model requires a full simultaneous
transition function, expand each state's seven-symbol guard over all
`7^P` scanned tuples, preserving inactive symbols and heads. That finite
expansion has at most `7^P S` entries. It changes neither the number of
runtime tapes nor the serialized clock.

Let `F_setup > 0` be the actual finite work of source reading, token/layout
binding, validation, graph construction, encoding and installation. The
total bill is `F_setup + A + U`. These steps are finite and can be executed
with ordinary sequential storage and bit arithmetic; no unit-cost claim
for Python dictionaries or big integers is used. Rebuilding the graph
requires paying setup again. This package supplies neither a numerical
exchange rate into the repository's scalar/pass fees nor a new global
threshold from its state count.

The exact active head trace preserves visited regions and their historical
maxima, including initial head sites. It does not imply that a host
allocator reclaims memory when a mathematical tape cell is blanked.
Ancestor segments, complete containing fields, source delivery, global
ownership, stock reservation and summed history remain caller obligations.

## 6. Evidence and exact limitations

The executable source oracle calls the unchanged `Controller.primitive`;
the target simulator executes only emitted microstates. It compares full
raw-action logs, cells, head positions, visited sites, historical maxima,
terminal labels, dispatch counts and `C=A+U`.

- Twenty-eight protocol cases cover all seven raw symbols, frontier and
  left-origin errors, read-only rejection, global port permutation,
  inactive spectators, a complete binary-context scan, pre-retirement
  failure before the first fetched row, table rejection with dirty live
  work, success retirement and a 31-row infinite-loop prefix.
- The independent equation `2h+5B+7` is checked on 660 length/head pairs,
  and three wrapper cases also include displaced context-return costs.
- Six retained source-generated SCALE tables from #6968 and #6988 are
  run on every signed input of widths 1 through 5: 372 cases, 238 accepted
  and 134 rejected. The tests start with dirty displaced work and a raw
  borrowed context, compare exact traces and independently check integer
  division/rounding and range. Those tables **do not read context values**;
  the separate binary scan is a protocol control, not a production header
  parser or a claimed scalar-to-header semantic join.

The arithmetic builders depend on the fixed rational coefficient `a/b`,
not on input width, component count or context length. The same emitted
graph is used for every width in each coefficient's fixture family; the
universal source-bisimulation theorem has no runtime-width cutoff.
- Six target-graph mutations are rejected: omitted pre-retirement,
  omitted post-retirement, omitted left restoration, forbidden frontier
  crossing, a physical context write and conflated raw/coded blank.
  Five alias/range/type layout controls reject before compilation.

Normal and optimized verification use explicit failures, not removable
assertions. Finite executions corroborate the universal induction; they do
not establish that induction by extrapolation. The simulator's host
containers and state indexing are verification machinery, not target
runtime operations. Retained source is executed by compiling the actual
authenticated bytes directly, so a stale `.pyc` cannot substitute for a
declared predecessor module even in the standalone commands.

The contribution closes the explicit finite-control seam for this
primitive wrapper and its protected contexts. All five global assumptions
remain; no new kappa, complete supplier admission, whole recursive
dispatcher, runtime tariff conversion, human review or proof-kernel
acceptance is claimed.

## 7. Credit and next obligations

Credit Jerry Chen / @CubeJerry for the lifecycle executor and exact and
rounded scalar services (#6968, #6988), and #6999 for the unchanged coded
microcontrol construction and exact serialized-clock convention. The
canonical stream-model authors retain their notices. The public source
application in #7000 motivates the dispatcher obligation without being
replayed or strengthened wholesale here.

The next useful implication is to lower the actual continuation/row
boundary and connect its returning service state to this primitive entry,
with the same fixed tapes and fully paid setup. The header producer must
separately establish its geometry/precision fields. A complete source
registry must bind the actual selected events and numerical provider
contracts before the enclosing dispatcher is admitted. None of these
remaining statements follows merely from the fixed finite state count.
