# Literal ordinary-caller restoration generations

## Statement and domain

For the unchanged [PR2809](https://github.com/CrocSwap/integer-mult-bounds/pull/2809) `Machine` retained through [PR2899](https://github.com/CrocSwap/integer-mult-bounds/pull/2899) → [PR3055](https://github.com/CrocSwap/integer-mult-bounds/pull/3055) →
[PR3087](https://github.com/CrocSwap/integer-mult-bounds/pull/3087), consider successful synchronous execution with its concrete
`SelectedBinding` or `ToyBinding`, compiled inputs, the source arena/Tape
implementations, and `observe=None`. External code does not save runtime
objects, mutate the machine during a call, or install replacement methods.
Debugger frames, traceback retention and interrupted-operation recovery are
outside the algorithm. These are closed-program conditions, not a claim about
arbitrary Python clients or arbitrary subclasses of the binding.

A **generation** means the five records reachable through the completed
`Machine.context` and `Machine.program`: Context, Ring, their shared Unsigned,
the fixed-role highs Count view, and Program. It does not mean every object of
these classes. Count temporaries, numerical-constructor temporaries and child
descriptor Programs are additional objects.

At a completed dispatch there is exactly one reachable generation. Immediately
before a replacement there is at most that generation. During a successful
`restore_context`, at most its five records and the five new records coexist:
**ten generation records suffice**, independently of recursion depth and the
number of returns. The number is a reachability bound; CPython collection time
and process RSS are not the theorem. A machine before its first root has zero
generations. Root completion retains the current five records.

The claim discharges the held-old-pair premise of
[#5362](https://github.com/CrocSwap/integer-mult-bounds/pull/5362) for this literal
ordinary caller. That predecessor allows one independently held prior pair
in addition to the current pair and therefore reserves 15 transient records.
Here the old dispatcher aliases the *current* pair before replacement; it is
not an independently retained older generation. Keeping the predecessor's
15-record implementation is conservative. This proof does not modify it or
claim its complete integration or tariff has been replayed.

## Source identity and root graph

`bundle.py` authenticates the complete outer archive and each nested archive
before importing unchanged [PR2809](https://github.com/CrocSwap/integer-mult-bounds/pull/2809) components. `SOURCE-EXPORTS.json` pins the
retained pending predecessor text and constructor. No external pending commit
is needed to reproduce this package. Original notices remain in the archives.

The persistent root audit is:

| Root or carrier | Generation edges |
| --- | --- |
| Machine.context / Machine.program | Current generation only |
| Machine.geometry_state | Derived geometry can reach the current Program/Ring; cleared before replacement |
| Machine.binding / topology / programs | Compiled code, specifications and source constants; no runtime generation history |
| arenas, words, roles, handoff, output, scratch pool | Numerical words, Tapes and leases; no assignment of a generation record into these carriers |
| numerical parking, stream parking, finite header | Encoded physical data and finite labels; no retained Context or Program object |
| counts, control state, size and depth | Scalar telemetry or existing word slots; no generation history |

Word→arena and other fixed cycles are permitted. The audited implementations
store cells, slot tables, live sets, meters and Tape handles in these carriers,
not Context/Program records. Generation fields only point to fixed vocabulary,
fixed word/Tape roles, or their own five-record generation. In particular,
`macro_binding.view` writes just index_arena, residue_arena, code_bits and tape;
it does not store the runtime argument. Restored Context.raw is Ring.raw.
The restored Ring attribute order differs from the ordinary Ring initializer;
the executable observer checks both exact orders separately.

This is an audit of exact immutable implementations. `contract.py` exposes
important structural invalidations; it is not a general escape analyser, and
the absence of `self` assignments alone would not prove the table. The full
archive pins bind the callees used by this argument.

## Callee and stack audit

`run` is one iterative dispatch loop. `call` parks the parent data and replaces
the current roots; it does not recursively call `run`. Parent continuations
therefore contribute no suspended Python dispatch frames. `dispatch` caches
`context=self.context`, which can keep the old generation reachable while
`call` or `complete_return` installs its successor. It returns before the next
dispatch begins.

Before child entry, `block` closes the trace generator in `finally`, exits
the geometry scope, calls `close_geometry`, then calls `call`. Its local page,
layout and first Event can remain in the Python frame during this call. They
can retain the same old generation: the proof does not pretend these locals
are gone. `prepare_child` has already returned only numerical grants; its
callback and descriptor construction frames have unwound. `call` itself also
has a local old Ring. All these edges lead to the one pre-replacement generation.

On return, `complete_return` calls `close_frame` before restoring numerical
and stream state. `close_frame` clears geometry. The header supplies five
finite slot labels to `restore_context`; it does not deserialize Python object
identities. `returned` and `dispatch` can still hold the just-completed child
generation, but not a stack of ancestors. No second replacement occurs before
these frames unwind to `run`.

The concrete binding paths do not introduce a hidden hold:

* `incoming` creates a local coefficient closure over runtime. `node` uses it
  synchronously, including `peel.run`, and returns before a replacement.
* `validate_residual` creates and closes its local Callback. No replacement is
  nested in the call.
* `coefficient` calls the selected numerical page path synchronously; its
  local page/callback does not escape to binding or specifications.
* `child_program` closes its Callback and returns `result.tape`, not the
  descriptor Program. The descriptor wrapper unwinds before `call`.
* ToyBinding likewise returns numerical words or Tapes, not generation roots.

The [PR2899](https://github.com/CrocSwap/integer-mult-bounds/pull/2899) `RootSession` subclass adds completed-root bookkeeping and changes
physical cleanup. Its `run` forwards to the same iterative Machine.run;
`erase_work`, `finish` and `rearm` add no generation aliases. Reuse can carry
the final five records into the next `load_root`, which replaces them in the
same way. The ordinary wrapper stores one RootSession runtime; the binary and
compact wrappers call that reusable engine. Inspection of these wrapper
sources explains the embedding path; it is not a whole-installation alias
theorem. In particular the distinct [PR3464](https://github.com/CrocSwap/integer-mult-bounds/pull/3464) physical machine used elsewhere in
the QQ16 installation is not silently identified with this [PR2809](https://github.com/CrocSwap/integer-mult-bounds/pull/2809) class.

## Induction

Initially the two roots are None. `load_root` constructs one five-record
generation. At a stable dispatch, the root table and callee audit allow only
that generation, possibly also through current geometry. A dispatch that
does not replace roots cannot create a persistent older generation.

A child-entry replacement clears persistent geometry and constructs its new
generation. Local old aliases all belong to the single current generation.
`new_context` also uses a computed highs Count and numerical temporaries:
these are explicitly outside the five-record count. Once the dispatch
returns, no old-generation edge survives in the audited roots or stack.

A return replacement similarly starts with one generation. The literal
`restore_context` allocates exactly Ring, Unsigned, Context, fixed highs Count
view and Program. At every allocation prefix, at most five old plus five new
generation records exist. No new field points back to the old generation.
After dispatch unwinds, only the new five are reachable. This establishes
the invariant for arbitrary successful sequences, not just the finite replay.

For a root return, `close_frame` releases numerical contents but neither
`erase_work` nor RootSession.finish clears context/program. Thus a proposed
zero-record postcondition is false: five wrappers remain reachable. Numerical
blankness must not be substituted for object retirement.

## Executable evidence and limits

`calibrate.py` executes the unchanged original `macro_checks.run` fixture with
genuine constructors and physical CALL/RETURN parking. A weak-reference-only
observer surrounds the original methods; it saves no generation objects.
The observer checks schemas/aliases, at most five before replacement, at most
ten after construction, no nested dispatcher, and five after each replacement
dispatch and root return. Host GC is checker instrumentation, not a paid
algorithm or a heap-size proof. Observation at method boundaries corroborates
the induction; the written allocation-prefix argument covers interiors.

The q2/dimension2/cutoff2 one-family fixture executes 5,859 macros, 12 child
calls and 12 restorations, yielding 25 completed generations, observed peak
ten and final five. Its complete original physical receipt hash is checked,
not merely its final numerical payload. This is finite toy calibration,
not an executed production SelectedBinding supplier. The source argument
includes the concrete SelectedBinding path, while the replay does not cover
its production numerical operations.

Four source mutations reject retained history, recursive run, missing frame
closure and a Program→runtime backedge. Three executed fault injections reject
binding history, arena history and an extra Program edge. These controls show
that the checks do not silently reclaim an alias. They are counterexamples
to extending the domain to arbitrary clients or mutators.

The component adapter replaces the module-level historical loader interface
after authenticating exact archive bytes. The original loader and its historic
selected-record guards remain unmodified, but its all-repository authentication
is not executed. No selected cold replay, precision proof, full frontend
capacity F(K), complete retained-storage bound, complete adoption proof,
physical tariff improvement or multiplication exponent follows here.

Substantial OpenAI Codex assistance in source analysis, proof, code and review.
Apache-2.0; retain all predecessor notices and credits in README.md.
