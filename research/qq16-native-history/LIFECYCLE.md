# Successful Ordinary return and retained native history

This component follows Jose Manuel's physical Ordinary implementation retained
by #4167, through #4166/#4129/#3385 and the nested #2899 archive. It does not
change the six arenas, numerical arithmetic, codec or allocator. The Python
snapshots in `lifecycle.py` are checker observations, not machine operations or
an implementation of canonicalization. Their time and storage do not enter the
claimed machine invoice.

## Six arenas and the legal cut

The complete native engine owns four outer `PhysicalArena` objects:
`banks[0]` (body/modulus), `banks[1]` (high field), `banks[2]` (optional
remainder), and `banks[3]` (indices); its `RootSession` owns `runtime.arena`
and `runtime.indices`. All six capacities and physical Word/slot identities
are fixed at construction. Each bank separately retains its free stack, live
set, permanent template and per-slot physical backing. The numerical parking
codec references the two **runtime** banks, not the four outer banks.

The relevant boundary is after a successful `Ordinary.execute_plan` has
finished and exited its outer factory scope, and after the caller has consumed
the protected ordinary output. At that boundary:

1. Ordinary and RootSession are closed, and the outer scope is disabled.
2. Both scratch-pool live maps and all six numerical live sets are empty.
3. All six `initialized` flags are false. Their words and templates have blank
   bodies and erased LEFT markers, with heads at one. Unvisited body cells may
   be implicit blanks; their storage is not counted as materialized backing.
4. The complete free stacks are duplicate-free permutations of their fixed
   slot domains. **No canonical order follows.**
5. RootSession's protected output is erased; the consumed Ordinary output is
   blank with its legal LEFT-or-blank origin. Its caller must not retain the
   result as a live protected value across reuse.
6. The numerical dictionary codec is `done`, has heads `(0,1)` and two empty
   dictionaries. Its output-port origin has been erased by `RootSession.finish`.
7. All owned stream-role bodies are blank at canonical heads; borrowed payload
   and descriptor bytes and heads remain the caller's property.

These are successful-return conditions, not arbitrary exception recovery.
`RootSession.erase_work` is a different boundary: it preserves initialized
numerical templates and role markers for the second ordinary-wrapper call.
The outer wrapper also retains live numerical and scratch residents during
that inner call. It is therefore not a legitimate six-arena closed-state reset
site. `Ordinary.finish` and `RootSession.finish`, including the expected zero
or two completed inner roots, close that gap at the actual outer return.

## Ownership and escaped handles

The source `ScratchPool.Lease` has an `active` bit and validates live identity.
An ended lease's clear is a no-op and its live operations reject. Wentao Li's
#3993 supplies a source-bound regression method for that exact BIT pool.

`PhysicalWord` has a different contract: it is a stable `(arena,slot,tape)`
view and has no lease-generation token. `Arena.free` validates that the slot
is currently live, rather than that a caller holds the current generation.
Consequently empty live sets and blank bodies do **not** establish absence of
escaped Word handles. A later slot reuse can make a stale handle point to the
new resident. A numerical-history transformation must retain the enclosing
ownership premise: no external observer/callback captures numerical Word
handles, and no live borrowed numerical resident crosses the selected cut.
The checker explicitly reports this premise; it cannot discover every host
reference or turn absence of live slots into a generation theorem.

Ordinary's actual successful call discharges its internal ownership obligations
through `ExitStack` frees, program/directory disposal, pool closure and owned
marker erasure. Source observers are numerical-neutral and cannot retain
residents. Borrowed Tape/Count views passed to RootSession preserve outer
ownership; they must not be reinterpreted as owned scratch leases.

## Numerical representation and backing

`PhysicalArena.prepare` constructs its template from an encoded positive
maximum: bitlength(maximum)+1 binary digits followed by RIGHT. The physical
word extent is never supplied by a host-decoded width. Fitted execution keeps
body, high, optional remainder and index extents distinct, and initializes the
two runtime templates from the actual modulus and index maximum. Closure
erases those contents but does not shrink any tape's already visited backing.
A subsequent rearm initializes markers, then the next invocation prepares its
actual extents through the same source operations. Queue order alone neither
changes a numerical quantum nor permits replacing a stored width.

For a fixed physical numerical role `r`, let `h_r(t)` be the maximum cell index
materialized by time `t`, plus one. The numerical backing is
`sum_r h_r(t)` over all six sets of Word roles and their six templates, and
`h_r(t)` is nondecreasing under source writes/erasure. The current blank body
and current live count are insufficient to reconstruct it. `backing_monotone`
checks this coordinatewise relation on finite receipts. It is not a total
space theorem: stream/count pools, payloads, code/continuation packets,
dictionary-codec visited coordinates and finite control must be counted
separately by the complete resource ledger. In particular a blank dictionary
contains no record of its formerly visited addresses; historical codec backing
requires an execution observer, not dictionary length at closure.

Ross Richardson's #2831 proves a related backing invariant for fixed-width
`Arena` arrays, with growing slot inventories. It explicitly excludes physical
placement, encoded slot maps and movement. Here `PhysicalArena` preallocates
all slots, and each underlying Tape can have a different historical extent;
we adapt only the persistence argument and retain the per-role maxima. Nick
Petalas's #2923 supplies the common-cut method for adding numerical backing to
countdown backing; its ADD-specific constants are not a six-arena reserve.

## Executable evidence and controls

`validate_closed(snapshot(engine))` independently checks the consumed outer
boundary. It does not require equal free orders and does not charge its host
scans as machine operations. `validate_preserved` checks borrowed bytes/heads
while allowing a physically visited blank tail to enlarge backing.

The twelve receipt mutants reject: one-arena-only accounting; a live resident;
an initialized template; a live scratch lease; an active outer scope; an
unconsumed protected output; a stale encoded slot record; an unfinished codec
command; a wrong codec head; a wrong numerical head; a duplicate free-stack
entry; and a false backing length. Mutants are negative checker controls, not
reachable history witnesses. Actual histories and fitted-branch coverage are
provided by the separate source-bound experiment. Finite checks do not replace
the successful-input and ownership premises above.

## Open next questions

If a new history alignment changes free maps, define its actual representation
and finite transition cost, and show all six maps are transformed only at the
safe outer cut. If it relabels encoded slots, prove the parking codec relation
including address-dependent scans and return restoration. Neither a host list
assignment nor the closed-state oracle is a paid mechanism. The complete
comparison must still distinguish changed-core inputs, service calls and
nonchild work after any covered same-payload context term is discharged.

## Exact first-use potential of the original complex child controller

This paragraph concerns the original complex `Machine` surrounding Ordinary,
not the six Ordinary arenas. Fix one newly constructed original-binding child
controller with `s` packet roles, at least one successful complete invocation,
and successful fixed-copy or proved adopted-output consumption between calls.
There is no intervening `discard`, reconstruction, or failed execution. Compare
its controller marker traffic with the same invocation sequence started from
the warmed closed marker pattern. Primitive-engine costs remain separately
subject to the numerical-history theorem; this argument cancels no such costs.

`BankPackets.__init__` erases the origins of its `s` packets, bank output and
bank scratch pool. The remaining controller roles, private roles, capsule,
protected output and parking ports start with LEFT. `Machine.return_node`
executes `origin` and `clear` on **every parked role** before completing a root
return, regardless of rank or whether the node was a leaf. Thus all packet
origins are LEFT after any successful completed C invocation.

Before its first use, each cold packet encounters one of three marker sites:
`BankPackets.gather` calls `arm_empty` on all packets, `Machine.enter_child`
calls `origin` on all parked roles before parking, or `return_node` calls
`origin` on all parked roles before their final clear. These exhaust the first
packet touch in the source. Both marker helpers perform the same reads and
moves on LEFT and BLANK origins, and one additional write exactly when the
origin is BLANK. At the first such site the cold and warm packet marker states
join. Subsequent packet release may erase the marker, but does so in both
executions, preserving the joined relation. Consequently cold packet markers
add exactly `s` writes over the entire nonempty successful backend epoch.

The protected C output gives the opposite one-time contribution. Its constructor
leaves LEFT, while both external fixed-copy consumption and #4167's proved
child-return adoption leave the next backend output with a BLANK origin. The
first `return_node` calls `origin(output)`; it therefore saves one write on the
fresh backend. If the first call contains descendants, this is the first
descendant return, and `transfer(output, packet(target))` preserves the output
LEFT marker thereafter. Subsequent root output consumption joins the warmed
pattern. Bank output and bank scratch origins are BLANK at construction and
returned BLANK after every use; all other controller markers are LEFT in both
patterns. There is no further controller marker discrepancy.

Hence the exact cold-minus-warm controller potential is

```
(delta reads, delta writes, delta moves) = (0, s - 1, 0).
```

For the selected original backend `s=704`, it is **703 writes once**, not once
per child, owner, recursive descendant or Ordinary invocation. The local source
control in `marker_potential_control` executes the actual `origin` and
`arm_empty` implementations on actual Tape roles for `s=1,2,704`; it checks
both helpers and exact counter differences. Its 704-role case tests marker
handling only, not a production payload or complete C call. Constructor and
terminal retirement costs remain in their enclosing ledger.

In #4167 B, `adapter.install` retains `root_layer.machine` as the one original
child backend. In frozen #4166 D, `connection.install` passes that same original
object to both producer and service machines and to `Installation`; it does
not construct a second original C backend for service. Successful calls do not
invoke their exception-only `discard` methods. The source census gives each
variant positive backend use, so both have the same one-time 703-write
potential and it cancels in the complete B/D comparison. This is a whole-epoch
cancellation: do not attach separate first-use adjustments to paired occurrences
or to the 336 service calls. A zero-call run, early failure, discarded/rebuilt
backend or changed output-consumption policy is outside this cancellation and
must retain its own entry/exit correction.
