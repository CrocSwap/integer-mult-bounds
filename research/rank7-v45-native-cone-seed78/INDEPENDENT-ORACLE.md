# Independent abstract SSA dependency oracle

Prepared with substantial OpenAI Codex assistance; Apache-2.0.
This module implements only an abstract dependency-closure oracle. Native
kernels, source construction and predecessor package credit remain with
their original authors and packages.

## Implementation independence

The SSA implementation and its normative controls were prepared by a separate
AI-assisted implementation without reading or importing the primary cone or
source-binding code. Preparation without execution was not counted as a
passing validation receipt. Actual execution evidence appears below and in
`VALIDATION.json` and both `RESULT-*.json` files.

The oracle independently constructs a forward versioned graph, then follows
its predecessor edges backwards. The primary implementation uses reverse
demand over the same abstract records. Agreement checks those two closure
algorithms. It does not independently prove that the event-to-record semantics
correctly model the actual word, native program, chart transitions or resource
obligations. Those require the separately checked decoder and semantic controls.

## Interface

```python
dependency_cone(records, initial_slots, final_slots=())
```

Each ordered record is exactly:

```python
{
    'index': 42,
    'outputs': {'value:L:249': ['value:L:249', 'value:L:17']},
    'roots': ['lifetime:Z:249'],
}
```

This is a schema illustration, not a valid standalone fixture: every read/root
must be explicitly initialized or written by an earlier event. Indices must be
strictly increasing nonnegative integers; booleans are rejected. State slots are
nonempty `channel:name` strings. The oracle treats channels opaquely; the semantic decoder supplies
the value/chart/lifetime interpretation. Outputs are a dictionary of state slot
to a list of input state slots. Dependencies resolve to **pre-event** versions
for every output before any output is installed. Roots resolve **after** all
simultaneous writes in that record. Final roots resolve after the last record.

Outputs may introduce fresh state slots, but inputs may not read a new slot
from the same event. An output with no predecessors creates a constant node
that still retains its producing event. This handles allocation and clear
without inventing arbitrary initial private/center inputs. Slots persist after
being introduced; lifetime activation/deactivation must be represented in
explicit lifetime values and checked by the semantic decoder.

`initial_slots` and `final_slots` accept lists, tuples, sets, or frozensets.
Initial order is normalized to sorted unique names for deterministic node IDs.
Dependency/root repetitions are normalized to one graph edge/reference: the
oracle does not perform XOR or coefficient cancellation. Records and their
nested collections are never mutated.

Returned fields:

- `event_indices`: sorted events producing any backward-reachable value,
  including constant-producing events with empty predecessor lists.
- `boundary_inputs`: sorted initialized slots reached by the roots.
- `versions`: every node's integer ID, state slot, per-slot version number,
  producing event index (or `None` for explicit initial input), and predecessor
  node IDs. Initial nodes start at version zero. A newly introduced slot also
  starts at version zero; a rewrite advances its per-slot version.
- `events`: every input event, including zero-output events, with its output
  and post-event root node IDs.
- `event_roots`: event index to resolved post-event root node IDs.
- `root_versions` and `reachable_versions`: sorted node IDs.
- `initial_versions` and `final_versions`: state-slot to selected node ID maps.

An event with zero outputs has no producer edge of its own. Merely listing a
root in that event requests the current value; it does not make the event itself
causal. A guard/free whose own execution must be certified should produce an
explicit obligation/lifetime value, dependent on its pre-event value, chart,
and lifetime, then root that output. This is the explicit private-free obligation model.

## Bounds and failure behavior

The module rejects more than 100,000 records, more than 4,096 total state slots,
or an individual slot collection larger than 4,096. It rejects malformed record
shapes, unknown pre-event reads, unknown post-event/final roots, and invalid
indices. Exceptions use explicit `ValueError`, surviving Python optimization.
There are no assertions, dependencies, imports, threads, subprocesses, filesystem
writes, environment changes, or CLI execution hooks in the module. The limits
bound domain shape, not a claim that the largest possible graph fits available
memory: actual execution must budget output/edge counts and authenticate the records
before building this graph. The graph preserves every written version rather than
discarding versions whose consumers have not yet appeared.

## Normative fixtures proposed before execution

These were proposed before primary-code access. The separate worker later
implemented `graph_controls.py`; it was executed during the
source-bound audits. Eight positive examples, the missing-edge control and
fifteen oracle input guards are recorded in both `RESULT-*.json` files.

1. **ADD dependency:** initialize `value:t` and `value:s`; event0 writes
   `value:t <- [value:t,value:s]`. The target root reaches event0 and both inputs;
   an unchanged source root reaches only the source boundary, not event0.
2. **Simultaneous swap:** event0 writes `value:a <- [value:b]` and
   `value:b <- [value:a]`. Root the new a: it reaches the old b only. Installation
   order cannot introduce a self-edge or replace the old a read of new b.
3. **COPY overwrite:** event0 modifies target; event1 writes target from source
   only. The target root reaches event1/source; event0 and old target are excluded.
4. **CLEAR/alloc constant:** write a fresh private slot from `[]`; root it. The
   allocating event remains selected with no boundary inputs. A prior target
   writer is killed by clear. No fictitious dirty private input is introduced.
5. **Post-event root:** rewrite a slot and root it in the same event. Reach the
   new version and its producer, not the overwritten version alone.
6. **Private free obligation:** free writes a new lifetime from pre-free value,
   chart and lifetime, then roots it. Earlier value/chart/lifetime producers must
   remain covered even if the private value is not a final output slot.
7. **Unary chart chain:** chart rewrites and a scalar value node referencing
   that chart must retain the complete earlier chart dependencies. Dropping a
   decoder-supplied chart edge must visibly change closure on the fixture.
8. **Unknown slot guards:** a read of an uninitialized private, a same-event read
   of a fresh output, and an unknown final root all reject. A previously written
   fresh private can be read subsequently.
9. **Noncontiguous event labels:** indices2/9/31 are accepted in chronological
   order; duplicates, decreasing labels and boolean labels reject.
10. **Root without outputs:** a zero-output record with a root keeps that value's
    real earlier producer; it does not manufacture the empty event as a writer.

## Exact scope

A passing comparison supports abstract closure. Actual source decoder coverage is supported separately
by source reconstruction and its semantic controls. It does not establish phase/native identities, chart commutative
diagrams, free private-zero return, backing ownership, precision, paid storage,
full-supplier admission, or any κ. Those remain separately checked evidence
obligations. Preserve this distinction in any final package and receipts.

## Execution evidence

Both frozen-provider certificates now record agreement with the reverse-demand
closure on both actual programs, with the normative controls passing. The
full result also includes separate source binding and exact native identities;
those are separate evidence, not independent capabilities of this abstract
oracle. Preparation without execution was not counted as validation.
