# Engineering decisions and verification limits

The measurable predicate is a strictly smaller sufficient common signed width
than the gatewise control, at the same normalized input precision and covered
arithmetic values. Three deterministic bounds were evaluated: gatewise,
paired-frame, and paired-frame with pair-first C numerators. Their common
P=64 capacities are 92, 85 and 84 bits. Exact rational arithmetic has no
measurement noise. Rank zero and a rank-two Fourier row distinguish the easy
case and the cancellation mechanism before applying it to the source streams.

**Build the Lever** required a retained exact replay rather than a one-time
capacity estimate. **Prove It Works** required fresh emitted bytes, a separate
integer every-prefix comparison, semantic rejection controls and publication-byte
checks. **Power of Ten** kept new functions near one page, bounded the state,
and required explicit failure paths and managed-runtime deviations below.
The parent owns the result. Internal read-only reviews examine the native
mathematics, code and decision trail; none is independent human review.

## Decisions that need interpretation

The first exploratory frame inventory guard assumed at most 1,024 frames and
failed with `bounded canonical frames`. The exact source has 1,124. The guard
was corrected to 4,096, and all 1,124 frame shapes are validated per provider.
This changes a resource guard, not a mathematical acceptance condition.

A refactoring briefly counted the 72 prelude warps as A warps. The positive
literal count test detected 96 instead of 24. The receipt now reports the
72 prelude and 24 A warps separately; the coefficient digests and capacity
values were unchanged. The final behavioral suite passes.

Review caught the need for conjugated inverse-transpose frames. The proof now
states that contract explicitly; its bounds are invariant under conjugation.
The paired control's generic numerator bound was improved only after an exact
local experiment and an independent internal derivation agreed on both signs.

`decisions.tsv` began with the hillclimb fallback's nine-column schema before
the installed show-me-your-work leaf was discovered. Its canonical schema has
six columns. This is a documented schema deviation, not full format compliance.
The existing history stays append-only; the review uses evidence/verdict and
the phase prefix in each note to audit its meaning. Future logs should start
with the installed helper's six-column template.

## Power of Ten assessment

1. New call paths are acyclic. Loops are structured. CLI success and every
   exception leave TemporaryDirectory cleanup in force. Explicit `--work`
   retains diagnostics by request and refuses an existing or internal path.
2. Streams have at most 30,000 events; 632 ordinary rows; each row at most
   4,096 atoms and each word at most 256 symbols; coefficients at most 256
   numerator bits. Frames have at most nine axes, at most 4,096 entries;
   declared warps at most 256. The capacity ledger is capped at 100,000
   observations per mode. C controls have nine ranks, two directions, two
   signs and at most 512 coordinates. Both source generators have 90-second
   subprocess deadlines; registered commands have 180-second deadlines.
3. Python, Fraction, JSON and subprocess machinery allocate dynamically.
   This is an explicit managed-runtime deviation. Fixed byte inputs, the
   capacities above, two serial providers and streaming digests bound live
   work; no complete matrix of every supplier field is retained. Runtime and
   library allocator internals are not independently instrumented.
4. New functions are near or below 60 lines. The formatted `stage` orchestration
   is 63 lines including its explicit count/result dictionaries. Its cohesive
   responsibility is the one chronological pass; no compatibility abstraction
   or duplicated mutable state was introduced to reduce line count.
5. `require` enforces dyadic support, complete frame chronology, common ADD
   frames, exact integer remainder and strict signed capacity. These contracts
   remain enabled under `-O`; the emitter children deliberately run unoptimized.
6. State belongs to one stream or Ledger instance. Vendor imports are local
   to replay setup. No concurrent writer shares generated outputs.
7. Source sizes/hashes, subprocess statuses, complete writes in the inherited
   compiler, deterministic receipts and arithmetic remainders are checked.
   Test faults cover source corruption, missing climbs and invalid formats.
8. No new eval, generated executable code, reflection or runtime registration.
   JSON events are data. The reused emitter is unchanged and source-pinned.
9. New data access and calls are direct. Required dynamic dispatch is limited
   to unittest's fixed 14 test methods and standard-library context managers.
   This Python framework deviation has a fixed target set and scoped lifetime.
10. Python runs with warnings as errors. New files pass Ruff formatting and
    the available correctness checks `E4,E7,E9,F,I,B,UP,C4,SIM,RUF,PLE,PLW`.
    The exploratory all-rule diagnostic also reports optional annotation,
    docstring, naming, import-location and unittest-style rules. Those are
    not repository requirements and were not suppressed in source. The package
    has no statically typed build or available full-program type specification;
    adding one to frozen dependencies would expand the research scope.

Frozen native scripts retain their authenticated CRLF bytes; a local
`whitespace=cr-at-eol` attribute declares those line endings without
normalizing their source. Frozen inherited scripts retain their existing
local style and diagnostic choices. They are authenticated, not rewritten. Changing their importer and
assertion-heavy generator contracts would require a separate scientific replay.
Any future unbounded input mode, recursive service, shared writer, alternate C
order or additional scalar lowering must revisit these capacity assumptions.

## Attention

Internal native-mathematics review resolved the dual-frame convention and
proved the pair-first refinement. The principal remaining limitation is the
explicit exact-adapter endpoint hypothesis and the excluded scalar coefficient
construction, consumer and physical invoice. Neither the capacity improvement
nor a passing replay closes those obligations.
