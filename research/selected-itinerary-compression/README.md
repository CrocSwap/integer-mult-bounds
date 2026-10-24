# Compact residual itineraries with unchanged physical continuation PCs

The authenticated physical compiler can retain one descriptor per complete
residual block run instead of every block tuple, while its original `Machine`
continues to fetch by the same `(mode, pc)`. This package implements that scoped
refinement, preserves every original `Residual` identity, and checks complete
recursive return, payload and cleanup on a bounded source fixture. It does not
claim faster compilation: validation makes the measured compact compile slower.

The predecessor [wrapper sharing](../selected-wrapper-sharing/README.md), PR
#4758, operates after a full operations tuple already exists. This sink operates
*during* the original append stream and keeps the original wrappers. All frozen
sources remain unchanged; the new adapter is opt-in and is not selected adoption.

## Exact adapter and observer contract

`itinerary.compiler` authenticates the complete `macro_code.py` bytes against
SOURCES.json. It requires exactly one of each original construction/finalization
boundary, substitutes a sink there, extracts only `compile_node`, and compiles
that function in a private copy of the authenticated module namespace. Original
`Cursor`, factory, routing and schedule calls retain their order and arguments.
No original function or module global is patched by the compiler adapter. The
replay importer authenticates each imported byte stream using the predecessor
source bridge. As in that bridge, it initializes its loader directly: this is
not a cold selected-loader admission test.

The accepted source is the pinned emitter and its good/fallback/axis grammar.
Plans and all nested plan fields must be frozen dataclasses, tuples or typed
immutable scalar leaves; mutable fields and unknown fallback commands reject.
The full plan snapshot includes reductions, permutation and sign, not just a
command count. Reuse is by **plan object identity**, with a snapshot consistency
check, never by equal-looking residual keys. Modes are compiled separately.
Every segment stores its exact original `Residual`; each emitted block and end
must refer to that same object, with the same role and expected block label.
The sink rejects missing/extra/reordered/foreign blocks and interrupted segments.

Plans, Residual fields and binding-provided data are immutable for the simulation
statement. Every reconstructed block fetch checks that the definition still
owns the same plan and axis and that its complete plan snapshot is unchanged.
This catches illicit `object.__setattr__` plan mutation, even though frozen
Python dataclasses can otherwise be bypassed. It is not a claim to make arbitrary
concurrent Python mutation safe, or to reject all mutation before any earlier
non-block instruction executes. Source factory call order, arguments and returned objects are retained within
a stable source namespace. Replacing emitter globals during compilation, Python
frame/stack tracing, and container/type/allocation identity observers are outside
the contract. A binding that rewrites `macro_code.Cursor` mid-call is not covered
by the private-namespace simulation. The
original block tuple itself is reconstructed and need not have the same `id`;
the original Residual **does** have the same `id`.

The physical caller has only two operations consumers: header sizing with
`len`, and indexed instruction fetch. Its checker receipts use `len`. Nearby
visitation/lifetime/sharing audits iterate the word. The sequence supports all
of these, Python integer-index conversion (including negative indices), bounds,
and tuple-valued slices; slices intentionally materialize their requested word.
It does not claim tuple type, tuple hashing, tuple concatenation, pickling, or
container-identity compatibility with arbitrary external extensions.

## Pointwise word refinement and continuation proof

Write the original word as retained non-block instructions and maximal block
runs. For a run with fallback commands `c_0,...,c_(C-1)`, give command `i` weight
3 if it is `child`, and 1 otherwise, and let `e_i` be cumulative weight, with `e_-1=0`. The
least `i` with `e_i > k` gives the command of local block offset `k`. A child
returns `("pair", i, k-e_(i-1))`; another command returns `("sweep", i, 0)`.
This is exactly the original Cursor's stage advance, including all three child
stages. A good plan gives the three fixed forward/good/backward blocks; an axis
run gives its single fixed axis block.

Induct over source appends. Before a residual, the sink has the same word
prefix. Each original block is checked against the formula before being
released; the descriptor reserves the whole run span, and later block appends
check the remaining offsets. The provisional sink is not published as a Code
until `finish` confirms that every reserved run is complete. End requires the exact run length
and original identity. All other tuples are retained unchanged. Empty fallback
runs contribute zero blocks. At finish, prefix ends therefore partition exactly
the original PC interval. Binary search followed by the formula returns the
same operation fields and original Residual at **every** original index. Length
is bounded by `sys.maxsize`, matching the original Python tuple/`len` domain.

The Machine's step at an equal mode/PC consequently dispatches an equal
operation. Its residual geometry owner test sees the original same object.
A child call saves `pc+1` with the original finite header; the same length gives
the same header schema. The unchanged park/restore restores the same mode/PC,
and fetching there gives the same successor. Induction on physical steps,
including nested call/return, yields the same payload and observable runtime
trace under the immutability and finite termination premises. This is a written
simulation argument plus finite checks, not a formal theorem about all selected
GL64 execution or a full multiplication theorem.

## Retained allocation and lookup costs

Let `A` be non-block tuples, `B` block instructions, `S` nonempty residual runs,
and `P` the total structural size of distinct plan objects. The old operations
container retains `A+B` tuples (plus its list-to-tuple peak); the new container
retains `A+S` entries and prefix ends, with O(P) immutable snapshots/command
prefixes. Original Residual objects, routing tuples and binding data remain.
The comparison is O(A+S+P), not O(S) total memory. Plans are already source inputs;
the **new** snapshot/index allocation is included in the measured compile peak.

For `R=A+S`, block lookup costs O(log R + log C + P_current): the structural
mutation check walks the entire current plan on every block fetch and allocates
a temporary snapshot. Good and axis blocks still pay that validation cost.
Non-block lookup costs O(log R). Compile continues to enumerate every original
Cursor block, allocates its temporary tuple, validates it, and discards it.
There is no asymptotic source-enumeration time saving. The sink's plan checks and
rank lookup add work; it is not a compiler-speed optimization.

MEASUREMENTS.json records one local CPython 3.12.2 / macOS 27 arm64 run. Compile
measurement uses mode 0 and 64 replicas of the real GL2 source schedule with precompiled
coefficient plans; tracemalloc starts after plans and adapter construction and
includes all sink metadata. It is a host-dependent observation, not a golden
receipt or selected asymptotic estimate. The original word has 30,723 tuples;
the compact word has 3,843 retained entries, including 768 run descriptors for
27,648 block instructions, plus 12 plan indexes / 186 command-prefix entries.
In this run, traced retained/peak bytes were 4,344,080 / 4,591,352 for the
original and 1,986,984 / 2,055,080 for the compact compile. Compile times were
0.062 / 0.633 seconds respectively; the complete recursive fixture took 12.53 /
12.89 seconds. These are single observations with no statistical speed claim.
The axis-only mode keeps the same entry count and adds metadata, so even the
retention saving is not uniform across modes.
The smaller representation trades compile work and lookup validation for lower
retention; use the exact measured bytes and times rather than extrapolating a
whole-program speed or memory ratio.

## Independent finite validation and reproduction

RESULT.json is deterministic. The checks cover:

- Original Cursor enumeration of all length-0..4 command-kind strings, plus a
  good plan: 122 cases, 713 labels. This is independent of the rank formula.
- Complete two-replica GL2 words in both modes: 963 and 123 instructions. A tee
  observes the actual source append tuples and checks exact Residual identities;
  a separate unmodified emitter call checks the complete ordered values.
- An actual recursive physical Machine with q=2, dimension/cutoff 2, the first
  **two** GL2 low classes, four root rows, and all 256 addresses per row (1,024
  payload bits). Both original and compact words execute four calls/returns,
  20 residuals and 675 macros. The unchanged codec parks and restores parents
  at nonzero PCs 4, 7, 14 and 17 in mode 1. It is not the predecessor's full
  six-low/9,216-bit fixture, which is deliberately not replayed here.
- Independent address-permutation output, identical parking/codec counters,
  restored PCs, borrowed tapes/heads/counts, numerical/geometry cleanup and
  complete physical work erasure. Logical `Invocation` construction and host
  numeric decode are forbidden during execution.
- Destructive controls for wrong block order/identity, missing blocks, wrong
  end roles, interrupted/unterminated segments, mutable fields, illicit plan
  mutation, changed source bytes and unsupported source shape. At an actual
  restored parent, the checker corrupts `pc` by -1, requires the continuation
  guard to reject, then restores it before dispatch; the complete run still
  finishes. Tuple index bounds and type behavior are checked separately.

```sh
python3.12 -B scripts/research_package.py --package research/selected-itinerary-compression
```

Both normal and `-O` commands are registered, 180 seconds each, using only the
standard library. All invariants use explicit checks that remain active under
`-O`. Verification is read-only. `verify.py --write --measure` explicitly
regenerates the deterministic receipt and optional local measurements. No Lean,
Docker, historical suite, selected GL64 expansion or selected source admission
is run. No stock coefficient, native tariff or kappa changes.

## Coordination and credit

Task `selected-stock-envelope`, priority revision 7, **changed scope** to the
concrete compiler representation/continuation handoff left by PR #4758; this
reduces a separate implementation obligation, not the card's reserve recurrence.
Base: `624de9dc66858af0945e5f8a0942488d62280d43`.
Canonical claim: https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-19131513
Entry overlap covered 299 open PRs, 3695 Discussion records and all 6319 local
notes. Scoped terms found the wrapper-sharing follow-up and distinct residual/
CALL refinement. Closed histories, all diffs and unpublished work were not
exhaustively searched; absence of a matching implementation is not novelty proof.

Jose Manuel/jmbarrancoml supplied the physical emitter, caller, Cursor and toy
fixtures; Kewin Talaga/PellaML supplied the authenticated source importer and
visitation/identity audits. Nick Petalas and the residual/CALL refinement
contributors supplied the continuation audit lineage. David Arias, ywz65 and
all retained source notices retain their credits. The new adapter, proof and
checks were prepared by JoyboyBrian with substantial OpenAI Codex assistance;
Apache-2.0. Frozen predecessors and LICENSE/NOTICE remain unchanged.

## Open next questions

- Can immutable ownership be enforced cheaply enough to remove the full-plan
  snapshot on each block fetch? First specify mutation/extension observers; a
  frozen dataclass alone does not prevent `object.__setattr__`.
- Can a source-authenticated regional emitter skip enumeration of already
  formula-addressable blocks, while preserving factory and binding observers?
  This sink still visits every block; use its exact PC refinement as the starting
  obligation, not a claim that GL64 compilation is now practical.
- Can the same contract be admitted through the selected loader and all actual
  production bindings? This reduced same-byte runtime replay does not establish
  provider admission, uniform stock/time budgets, or the full outer theorem.
