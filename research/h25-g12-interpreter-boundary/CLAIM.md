# What preallocation does and does not establish

This is a conditional source argument about **specific ordinary CPython 3.12.3 paths**, not an experiment on the H25 interpreter and not a theorem about every Python program. The immutable CPython revision is `f6650f9ad73359051f3e558c2431a109bc016664`. The inspected G12 predecessor is PR6339 at `608ad23adc6c01264c8195daf7f18e29c17464a7`. The independent local repairs in [PR6346](https://github.com/CrocSwap/integer-mult-bounds/pull/6346) remain partial.

## Contract and interpretation

The original source contract CP12 requires exact first-primary/raw-secondary objects and actual frame/cause/traceback relationships. CP14 retains the stated callback/finalizer/signal exclusions; CP15 retains terminal ordering. The canonical `CALLER-EQUALITY-DEFINITION-v1.json`, original G12 `DESIGN-v1.json`, and source-scope clarification are byte-bound live inputs. Their original criteria are unchanged.

Let `J(E,T)` mean an already prepared journal retains the actual exception `E` and its pre-existing traceback `T` in separate cells. Distinguish:

- **C:** journal capacity and valid slot replacement suffice for all delivered records;
- **R:** every acquired resource is represented by an authenticated owner before any later failure;
- **D:** each already-created error that the raw contract requires reaches the journal without replacement or loss;
- **P:** the declared original caller channel receives the retained first primary `E`.

The following implications are invalid for the ordinary paths below:

```text
C             => R
C and R       => D
C and R and J(E,T) => P
```

The second implication interprets the required raw error as an already-created error before Python handler dispatch. If the original oracle covers only successfully delivered errors, that interpretation must be resolved explicitly; the pre-capture example alone does not decide that different contract. Retaining `E` in `M.__context__` also differs from returning `E` through the primary channel. No cross-process equality of raw identities is asserted.

The fault model for each witness has **one selected allocation failure followed by successful later allocations**. It assumes no unrelated callback, finalizer, signal, concurrent ownership change, target corruption, process death, or endlessly failing allocator. Frame objects may be unmaterialized when the relevant active frame first fails. An already materialized frame removes that particular allocation site, not all traceback sites.

## Witness 1: acquisition precedes Python return conversion

The CPython [`os_open_impl`](https://github.com/python/cpython/blob/f6650f9ad73359051f3e558c2431a109bc016664/Modules/posixmodule.c#L10232-L10276) returns a C descriptor after acquisition. The generated [`os.open` wrapper](https://github.com/python/cpython/blob/f6650f9ad73359051f3e558c2431a109bc016664/Modules/clinic/posixmodule.c.h#L6224-L6235) then calls `PyLong_FromLong`; its conversion-failure exit cleans the path, without closing that successfully acquired descriptor. [`pidfd_open`](https://github.com/python/cpython/blob/f6650f9ad73359051f3e558c2431a109bc016664/Modules/posixmodule.c#L9547-L9556) similarly converts after acquisition.

At this revision the positive cached-integer bound is [257, exclusive](https://github.com/python/cpython/blob/f6650f9ad73359051f3e558c2431a109bc016664/Include/internal/pycore_global_objects.h#L19-L21). Converting descriptor 257 follows [`PyLong_FromLong`](https://github.com/python/cpython/blob/f6650f9ad73359051f3e558c2431a109bc016664/Objects/longobject.c#L294-L307) into an [allocating medium-integer path](https://github.com/python/cpython/blob/f6650f9ad73359051f3e558c2431a109bc016664/Objects/longobject.c#L204-L219). Let that allocation fail after the acquisition succeeds. Neither a local assignment nor direct assignment into a prepared cell receives the descriptor.

The original G12 parent also has an ordinary returned-handle-to-append gap at lines 149-177. Preallocation can remove that later gap; it does not remove return conversion. The witness requires an uncached descriptor number, not merely a large bound on the number of resources. No claim is made that the genuine fixed launch reaches 257.

An unreturned handle does **not** alone refute an obligation limited to attempting every Python-known cleanup. Incomplete custody must remain UNKNOWN and block publication. This witness refutes a claim of complete acquisition registration from ordinary returned-handle journalling alone.

A fully proved atomic-owner primitive or private-table prediction/recovery protocol could address this boundary. This package implements neither. It does not rule out either alternative or establish the target kernel's allocation behavior.

## Witness 2: an existing error can be lost before capture

The actual S cleanup path calls `_close_known_descriptors`, which calls `os.close` inside a fresh Python helper frame and catches its error. Choose a trace where the body succeeds, a known close creates raw error `E`, that active helper frame has no materialized frame object, and the sole allocation failure occurs while creating that frame object for traceback recording. `E` has no other retained reference.

The [evaluator records traceback information before dispatching the handler](https://github.com/python/cpython/blob/f6650f9ad73359051f3e558c2431a109bc016664/Python/ceval.c#L934-L985). The frame getter [lazily materializes the active frame](https://github.com/python/cpython/blob/f6650f9ad73359051f3e558c2431a109bc016664/Include/internal/pycore_frame.h#L201-L214). The [materialization failure branch](https://github.com/python/cpython/blob/f6650f9ad73359051f3e558c2431a109bc016664/Python/frame.c#L28-L39) takes the current exception, attempts the allocation, decreferences the saved exception on failure and returns without restoring or chaining it. [`PyErr_GetRaisedException`](https://github.com/python/cpython/blob/f6650f9ad73359051f3e558c2431a109bc016664/Python/errors.c#L488-L500) clears the current exception reference when taking it. The [frame allocation](https://github.com/python/cpython/blob/f6650f9ad73359051f3e558c2431a109bc016664/Objects/frameobject.c#L1051-L1067) can fail.

The handler can therefore receive replacement `MemoryError M`, with `E` no longer reachable through that pending-exception reference. With no other root, the raw `E` is lost. A prepared journal cannot recover an error never delivered to it. If a body primary is already active, the same issue can concern the raw cleanup secondary; its context relationships need separate care.

Preparing the **actual active owner frame** and inlining cleanup can remove this particular fresh-frame site. Warming a previous invocation does not materialize a later invocation's frame. This witness is not a proof against such redesigns.

## Witness 3: journal retention does not force outward primary identity

S `_raise_preserved` raises `error.with_traceback(traceback)` at lines 187-198; its final call at 1739-1760 is outside the preceding handlers. Suppose `J(E,T)` already holds. A failure materializing that fresh propagation frame can replace the pending exception with `M`. The journal still contains the exact `E,T`; the caller receives `M`. This refutes the inference from journal retention to outward primary identity, without claiming that the journal lost its objects.

Even if the active frame is materialized, creating a traceback node can fail. [`PyTraceBack_Here`](https://github.com/python/cpython/blob/f6650f9ad73359051f3e558c2431a109bc016664/Python/traceback.c#L264-L279) then calls [`_PyErr_ChainExceptions1`](https://github.com/python/cpython/blob/f6650f9ad73359051f3e558c2431a109bc016664/Python/errors.c#L691-L706). This different branch retains `E` in `M`'s context; **`M` remains the propagated exception**. The pre-existing `T` may remain intact. The failed new traceback node never existed, so it has no identity to retain.

Selecting the deepest context exception is not a justified repair: ordinary context chains also encode legitimate relationships. A successful control must check the declared channel and raw graph, not formatted error equality or reachability alone.

## What would suffice for a bounded successor

A prepared exact-list design with separate resource/error/traceback cells and pre-existing links can eliminate growing containers, snapshots, pair tuples and arithmetic counters from the critical bookkeeping sweep. Conditional induction can show that, if capacity suffices, all handles are represented and every cleanup outcome is delivered, each known cell is visited and delivered errors occupy cells in order. Issued close, confirmed close and UNKNOWN must remain distinct; do not blindly retry an ambiguous numeric descriptor.

That argument still needs exact resource/error capacity bounds, valid primitive operations and decref behavior, original exception-context placement, acquisition ownership, raw capture/delivery and actual caller integration. Bounds of 256 components or 128 generations do not alone prove an error bound of 4096.

The narrow missing assurance is that the remaining acquisition-publication and exception capture/delivery transitions preserve required raw errors, permit bounded known cleanup and transfer the original primary through its declared channel. It may be derived by a redesigned and qualified runtime path. Adding it as an assumption is an **explicit premise amendment**. A reserved Python byte array does not establish it, and an acquisition adapter alone does not repair exception loss during Python unwinding.

## Disposition

The ordinary proposed journal alone does not discharge the original source task. This is a bounded insufficiency result with concrete alternative proof obligations; it is not a universal impossibility claim. The target executable's actual correspondence to these upstream implementation paths remains unqualified. No genuine target execution, fault injection, performance result, all18 branch acceptance, source adoption, N22/P07 body credit, O03 completion or kappa change follows. Original 52 helper IDs, CP01-CP15, both exports, the uncached producer, terminal ordering and complete costs remain intact. Unknown physical and final costs remain **OPEN_NOT_ZERO**.
