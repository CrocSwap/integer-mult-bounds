# Independent operational review: scalar-table microcontrol

**Verdict: the reviewed generator preserves the retained context-free
executor's ordered raw action trace, final heads, cells, outcome and
rejection label on admitted executions.** Its added row-dispatch
microsteps give exactly C=A+U under the stated serialized transition
convention. This is a scoped operational verdict; it does not establish
a numerical conversion to the project's current tariff.

Prepared for @CubeJerry with OpenAI assistance on 2026-11-09. The reviewer
derived the expected traces from the retained source before the author's
generator existed. The checker does not import the author's verifier,
simulator or test oracle. It independently traverses generated tuples.

## Exact reviewed sources

* `vendor/machine.py`: SHA-256
  `ec597bce13275003ff30e4be481c936401826c1d4af642b55eec0c410774d1df`.
* `lower.py`: SHA-256
  `f378d44b7a208ac9b876549a28afe0b6905d74ba109194b83bd2e3becbe5b671`.

The original machine comes from
`CubeJerry/integer-mult-bounds@ab239cb6ee884e7a900dd9101c34448077fad0b0`,
`research/compiled-owned-bank-lifecycle/machine.py`, Git blob
`acf475e4fccaff2fb64bd5b0b3f3fc0d246dc592`. Canonical contribution base is
`CrocSwap/integer-mult-bounds@7c49fe32c55de02c2c873655c804b16e4c3fef0a`.

## Independently derived primitive traces

For a coded read at physical head h, an initial read of BLANK returns
virtual symbol4 immediately. Otherwise the service reads three binary
symbols, advancing after each, and then performs three left moves. A
malformed symbol at offset j=0,1,2 rejects immediately at h+j; the initial
peek is additional to the j+1 decoder reads. The unused binary111 code
rejects only after all three reverse moves, at h. Consequently a complete
nonblank read uses four reads and six unit moves.

Writing a virtual symbol0 through6 performs three writes interleaved with
three right moves, followed by three left moves. A right virtual move
performs one read and three right moves; at a physical blank it first
materializes code100 through the above nine-action write. A left virtual
move performs move(-1),read; if it sees LEFT it restores the old head by
move(+1) before rejecting, otherwise it performs two further left moves.

Successful execution runs the original origin loop on each port in tuple
order. At head h>=1 with LEFT only at0 this contributes h reads and h+1
unit moves and ends at1. Rejection does not run these origin loops. Every
fetched table row, including halt/reject, contributes one row fetch U.

## Graph inspection and universal operational argument

The generator's recursive `bit(j,value)` has the exact invariant that j
physical bits have been consumed and the current head is h+j. Its two
binary outgoing edges first move right and then enter the state for
`(j+1,2*value+digit)`. All five nonbinary edges stop immediately with the
original malformed-code label. At j=3 it emits exactly three left moves;
the terminal is either the branch destination for value0..6 or the
unused-code rejection for7. The separate initial read implements the
frontier shortcut without an extra decoder read. Thus the complete read
trace, including both malformed and unused-code endpoints, is identical.

`write_code` constructs the nine actions listed above by a reverse-built
linked chain. `coded_move` uses the exact source action sequences,
including materialization of virtual4 and restoration of the rejected
left step. The three-state origin cycle implements one left move, one
read, and either a repeated left move or a final right move. Iterating
the fixed ports in reverse during construction links these cycles in
the original ascending port order at execution.

Every source row is represented by its own no-op dispatch. Its successor
is the corresponding primitive chain, the next row, the goto/branch
destination, the cleanup chain, or the matching rejection terminal.
Primitive endpoints therefore re-establish equality of the two
configurations at the next row boundary. Induction over fetched rows
proves finite execution equality; induction over finite prefixes also
covers cyclic programs without claiming that they terminate. Each raw
action is one non-no-op target transition, and each fetched row has
exactly one no-op transition. Terminal states have no outgoing charged
transition. Hence C=A+U, with the source's successful origin actions
included in A. There is no extra success-only origin on rejection.

The compiler deliberately admits only a positive fixed port count and
unique branch keys; its closure validator also fixes exact row shapes,
literal symbols/directions, in-range ports and closed row successors.
The retained source's duplicate-key behavior is last-key-wins, but the
target does not claim that larger source grammar. No runtime dispatch
search, dictionary construction, PC arithmetic or decoder integer is
needed by the target graph; those are construction or emulator notions.

## Executed checks and failure detection

`check_operations.py` passes2,806 primitive cases: every one of343
physical triples for reads, all2,401 symbol/write-body combinations,
seven right moves,15 left-move cases and40 origin distances. It also
passes2,843 source table executions against an independently written
trace interpreter, covering defaults, duplicate branch keys, multiport
effects, goto, rejection, normal halt and frontier materialization.

Of those executions,2,827 satisfy the target's narrower admission rule;
they instantiate26 distinct generated programs and run30,375
microsteps. Every complete ordered read/write/move trace, final cell
dictionary, head, terminal label and row count agrees. The16 excluded
cases are14 duplicate-key cases and two zero-port programs, rather than
unreported failures. Normal and optimized Python runs return identical
results.

Six source semantic defects are detected: wrong blank value, incomplete
read rewind, accepting111, reversed write bits, wrong blank
materialization and failing to restore the left-origin rejection head.
Six separately mutated target graphs are detected: omitted row dispatch,
wrong written bit, treating blank as a codeword, lost left-rejection
restoration, lost111 rewind and lost final successful origin move.

Reproduction from this directory, passing the package path explicitly:

```sh
python -B check_operations.py ../worker-micro-control/research/scalar-table-microcontrol
python -O -B check_operations.py ../worker-micro-control/research/scalar-table-microcontrol
```

## Limits

These finite checks supplement the graph argument; their finite extent
is not a universal input search. The theorem needs the stated physical
tape/origin admission, closed scalar grammar and fixed finite program.
This review does not establish arbitrary termination, binary-context
support, Controller dispatch, recursive continuations, lifecycle
wrappers, setup-cost amortization, whole-caller execution, a tariff
exchange rate, or a new multiplication exponent. The complementary
machine-model review is responsible for interpreting stationary-head
transitions and expanding inactive-port wildcards in the canonical
multitape model. No author files were changed by this reviewer.
