# Area 3 implemented API revision 3

This revision retains every API, regular-file contract, scientific pin and cost item in API-v2.md and CONTRACT-v2.json. The production and control filenames remain `bounded_serialization.py` and `serialization_controls.py`. Exact v2 source/doc bytes are preserved under `versions/v2/`; no v2 receipt or historical measurement was changed.

The factory call and `writer.last_operation` interface are unchanged. Add the following source-bound checks to the integration contract:

- The original writer, canonical encoder and require function must be ordinary closure-free functions with no defaults. This is their inspected source shape. Unsupported reference function shapes are rejected at factory creation.
- Capture JSON function code, effective globals/builtins, defaults and keyword-default entries, including names in nested code objects. Check absence of formerly missing globals to reject new shadows. Capture the JSONEncoder class dictionary and actual hashlib SHA constructor in addition to prior JSON/_json bindings.
- Fast-path freshness runs at entry, before success cleanup, and immediately before returning the successful receipt. Literal fallback delegates first, then checks freshness before returning success. A fallback callback that mutates bound runtime dependencies can retain its original output files but now raises; status is `FALLBACK_EXIT_FRESHNESS_FAILED`. Arbitrary mutating-runtime callback equivalence was never admitted.
- Original exception paths still propagate their primary errors. The added exit checks do not replace a failed original fallback's exception or delete evidence. Guard checks never treat the reporting attribute as an authority.

These checks add captured dependency/keyword/class metadata, setup inspection of code names, and three bounded freshness traversals per successful fast write or two per successful literal fallback. This is charged overhead; there is no timing claim. Complete caller/native arithmetic does not invoke these checks on every arithmetic boundary.

The finite runner now has 70 expected cases from source: v2's 65 plus effective builtin drift, new JSON global shadowing, keyword-default content drift, late fast-path drift and successful-fallback runtime drift. Parent alone executes the normal/-O finite suite and full original/candidate comparison. This lane has performed only AST/JSON/source/hash checks.
