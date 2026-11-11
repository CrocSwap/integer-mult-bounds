# P3 source integration contract

This directory contains source only. The lane did not import scientific modules, compile the extension, or run its controls. The parent owns immutable staging, cold compilation/load, live freshness integration, serial controls, full pilots and all costs. The original GF(2) source remains `e9c3c9194a08718bd1575c1cf08c6c6772d3b644c2e274c25a84a1f9249d06cc`.

## Files and public interfaces

- `trace_encoder.c`: standalone extension `_trace_encoding` with `encode_record(call, us, vs, output)`. It uses `METH_FASTCALL`, exactly four positional arguments and no keywords.
- `trace_adapter.py`: `make_trace_type(backend, native_encoder_module)` returns a candidate trace subclass. It does not change `backend.ComplementTrace` or any backend/global/native method.
- `trace_controls.py`: `run_controls(backend, native_encoder_module)` returns a JSON-safe receipt or raises. It does not compile, time, write files, or invoke the complete caller. The parent must have both Python modules available from the same source-checked isolated stage.

Keep `backend.ComplementTrace` original. The old finite controls must continue comparing their original observers. Construct the candidate class and full-run trace explicitly:

```python
CandidateTrace = make_trace_type(backend, trace_native)
trace = CandidateTrace(circuit_module.Label)
# Parent finalizes the guarded adapter environment before bind captures cells.
binding = backend.bind(circuit_module, gf2_native, rank_calls, trace)
```

The final line assumes the parent's guard integration below is already installed. Neither the factory nor direct `trace.after` adds a per-call native freshness check itself. This avoids silently claiming protection at an unimplemented boundary or charging the same check twice.

## Mandatory parent-owned freshness

`CandidateTrace._h25_native_entries` is a tuple containing `(exact_owner_module, "encode_record", exact_builtin_entry)`. These strong references are stable metadata, not a cached verification result. The `after` closure uses that same fixed native entry. Before every original arithmetic/fallback boundary, check the captured owner is an exact `ModuleType` and its exact dictionary slot still contains the captured entry by identity. Capture only after validating that the entry is a `BuiltinFunctionType` whose `__self__` is its owner.

Add the check after the old distinct guard checks, before either arithmetic or fallback, to preserve the old rejection ordering. If attached to the general guard, charge all 298,644 original guard boundaries, including Gram calls. Keep the original constructor and final guard checks too. Set up the guard class, trace object, owner/entry records, all helper replacements and wrapper closure identities **before** `RuntimeGuard` captures state. No post-capture replacement or rebuilding after drift to bless new values.

The parent must execute a new integration control: replace the public encoder slot while a wrapper retains the old callable, then call the guarded arithmetic path. Require rejection before arithmetic, unchanged old native counters and unchanged trace prefix; restore the exact original slot in `finally`. Exercise both complement and Gram guard paths if the entry is checked globally. A new factory rejecting a replacement is covered locally but is not this live-drift control.

## Exact encoding domain and behavior

The native domain is an exact nonnegative uint64 count; exact tuple `us`/`vs`; and None or an exact list output. Each vector contains at most 64 exact nonnegative uint64 integers. Bool, integer subclasses, negative/wide integers, larger vectors and other container shapes return `NotImplemented`. The Python adapter retains the original output validation before this dispatch, so unsupported output types still raise the same original error.

Native bytes are the literal sorted-key, compact, ASCII JSON record with final LF: record key order `call,result,us,vs`; list result order `type,values`; None result has only `type`. Decimal conversion uses unsigned arithmetic, never floating point or masks. The longest admitted record is 4112 bytes: 192 twenty-digit vector values, 189 commas, one twenty-digit count and 63 schema/punctuation bytes. The 8192-byte stack buffer checks every append despite that bound.

For fallback, the adapter builds the original result/record dictionaries and executes the literal original `json.dumps(..., sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii") + b"\n"`. Count is read once and the same object is used for admission and fallback. This preserves ordinary JSON handling of negative/wide integers, direct-call input shapes, and decimal-limit errors. The supported environment is the frozen ordinary CPython 3.12 JSON runtime, not arbitrary monkeypatch equivalence.

`before` and `receipt` are inherited unchanged. `after` retains original unpacking, output validation, `hasher.update(encoded)`, `bytes += len(encoded)` and `count += 1` order. Every completed record is immediately visible. No cross-call buffers, cached receipts, changed checksum, new per-record performance counters or output-object mutation are introduced. Hash failure or a later counter failure preserves the original partial-state behavior.

## C ownership, errors and optional embedding

The encoder holds the GIL throughout. Exact-container borrowed references are consumed within the owning argument lifetime; no container reference or scratch pointer is retained. `PyLong_AsUnsignedLongLong` is preceded by exact type admission, and `PyErr_Occurred` distinguishes valid UINT64_MAX from failure. Only `OverflowError` is cleared to choose fallback. Other conversion errors and final bytes-allocation failure propagate. A rejected partially built record never escapes. The only returned allocation is `PyBytes_FromStringAndSize` copying the initialized prefix.

All implementation identifiers use `h25_trace_` or `H25_TRACE_`. Defining `H25_TRACE_EMBEDDED` excludes only the standalone method table/module definition/init. The parent may include this same C source before its own combined method table and register the unchanged static `h25_trace_encode_record` with `METH_FASTCALL`. The kernel source and logic are otherwise unchanged. A combined source is a new pinned parent artifact and must include the trace entry in its native freshness inventory. This option establishes no build-cost amortization claim; standalone compilation is the default.

The calling convention and reference/error requirements follow the [CPython C API](https://docs.python.org/3.12/c-api/structures.html#c.METH_FASTCALL), [integer conversion](https://docs.python.org/3.12/c-api/long.html), and [bytes ownership](https://docs.python.org/3.12/c-api/bytes.html) documentation.

## Controls and complete cost bill

The local control suite compares the original observer, a separate literal JSON oracle and the candidate. It covers every byte and intermediate hash/receipt; None/list distinctions; order; decimal and uint64 boundaries; the 4112-byte maximum; 64/65 entries; negative/wide values; bool/subclasses/custom callbacks; unpacking and output errors; failing hash updates before/after mutation; failing byte/count increments; snapshots and later mutations; no retained caller references; sentinel/error clearing; arity/keyword rejection; and factory owner/entry rejection. Decimal-limit settings and temporary native-entry replacement are restored in `finally`.

The parent runs it in normal and optimized finite modes, retains all original controls, adds the live freshness controls above, then keeps the complete caller assertion-on. The control suite intentionally creates no native coverage counters in the hot path: its receipt reports direct finite admissions/fallbacks, not measured full coverage. Full exact receipts and the unchanged old native counters remain mandatory.

Charge source preparation/custody, both cold build/load and all new controls, added live entry checks, native dispatch/conversion/decimal/buffer/bytes work, original snapshots/hash/counters, fallback costs, failed attempts and cleanup. Exact byte arithmetic and source call budgets are not speed measurements. Only the parent's complete frozen-baseline/candidate pilots can establish performance evidence.
