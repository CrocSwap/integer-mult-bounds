# P2 implementation handoff

Status: source implemented; AST parsed; runtime correctness and performance remain untested. Parent is the sole scientific runner. These files stay inside the runtime-guards lane; PR5995, shared harnesses and other lanes are unchanged.

## API and installation

`guard_candidate.make_runtime_guard(backend)` returns a `RuntimeGuard` class. It has the original `(module, label, native, original_functions)` constructor, `check(self)` method and original public state fields. It supports the existing `backend._OBJECT.__new__(RuntimeGuard)` followed by explicit constructor invocation. The constructor retains its final virtual `self.check()` call.

The parent loads the candidate file inside the authenticated candidate source closure, calls the factory once with the isolated candidate backend, and assigns the result to `candidate_backend.RuntimeGuard` before any candidate `bind`. The untouched reference backend must be a different module object with its original class. Neither factory creation nor installation changes the original backend, source helpers, arithmetic or trace observer.

Finalize helper/trace replacements and all source-wrapper closure-cell identities before guard construction. If combined integration adds encoder owner/entry checks through a subclass, initialize those extra snapshot fields before calling this base constructor: the constructor's virtual check will already invoke the combined check. Parent owns that extension. The primary implementation retains the original two native entries and does not claim to protect P3's encoder by itself.

The factory captures the backend's original anchored operations, types and constants. This has the same stated supported scope as the original backend: serial stable runtime with no mutation during a call; arbitrary alteration of the backend itself is unsupported. No per-call result or PASS is cached.

## Exact change

The constructor filters the small incoming function sequence using nested `is` comparisons and preserves the first occurrence. Traced records fall from 13 to 11; untraced records from 13 to 10. Same-code distinct functions remain. All separate global/class/native slot checks remain.

The ten syntactic predicate/message templates in `check` are unchanged. They now branch directly to the same anchored RuntimeError, which eliminates successful `require` dispatch and eager string construction. The original predicate and short-circuit order, captured-cell access, type and message survive. Ordinary lookup failures and empty-cell ValueError propagate; the engineering traceback no longer contains a `require` frame.

`STATIC-CHECK.json` records an AST-only comparison of all ten predicate/message templates against immutable PR5995 and the source hashes. AST parsing is not runtime verification. No extension was compiled, module imported for scientific execution, corpus decoded, numerical case run or benchmark performed here.

## Controls API and bill

`guard_controls.run_guard_controls(reference_backend, candidate_backend, native)` returns a JSON-serializable receipt or raises. Supply two distinct, source-authenticated backend modules and the already cold-built real native module. Install the candidate guard first. The controls do not install classes or build extensions. The original independent finite suite must still run unchanged; the returned receipt explicitly states that requirement.

The new suite makes four source loads and bindings: traced and untraced reference/candidate. Two additional directly constructed guard objects per mode test same-code distinct functions, without additional source loads. Each binding is held privately and reused only after mutations are restored in `finally` and its live guard passes again.

Meaningful comparisons include successful native/wide/container behavior followed by mutation, every distinct function's code/default/keyword-default identity, every wrapper/rank closure cell rebound and emptied, all six global slots changed/deleted, fourteen builtin shadows and fourteen shared builtin replacements, writable class methods/metadata and callback-bearing descriptors, both native entries changed/deleted, module subclass dispatch, and four first-failure precedence cases. A same-code separate function must still reject its own mutation.

Each drift is tested through a held guard and both saved wrapper entries for native, wide-integer and custom-container inputs. Outcomes compare exact value/error type and message. State comparisons cover native/fallback counters, complete rank lists, trace prefix receipts and ordered callback logs. No drift may advance those observations or call a modified helper. Shared runtime-cell mutation additionally compares the actual wrapper's original AttributeError/NameError behavior. Immutable/read-only function globals/builtins pointers and MRO are covered by retained source predicates and original admission controls; no ctypes or unsupported layout mutation is used.

The source-derived expected matrix has 115 untraced and 122 traced mutation pairs, seven action pairs each: 237 mutation pairs / 1,659 action pairs, plus 14 stable action pairs. Parent execution must confirm these counts; no measured receipt exists yet. Baseline/candidate failures are retained by the parent runner rather than automatically retried.

Every candidate process pays source custody/import/factory/deduplication, the four module loads, temporary metadata and perturbation fixtures, outcome comparisons and transcript serialization. Existing cold native build/load, old independent controls, full verifier and final observations remain payable. There is no new compiler unit. The source-derived call budget is in `CALL-BUDGET.json`; combined integration must revise it if new wrappers or native checks change the inventory. None of these counts establish a wall or CPU saving.
