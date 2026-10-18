# Verification contract and implementation limits

The retained artifact is a deterministic lowerer and receipt, not a physical
multiplication implementation. Inputs are two frozen words and two source-pinned
native compiler scripts. No frozen predecessor or shared implementation changes.

## Decisions

- Build the Lever led to a rerunnable lowerer and serialized-stream checker
  instead of a hand-counted scalar saving.
- Prove It Works led to reading back the actual compressed output and checking
  its literal registers, component labels, frames and linear maps.
- Test Behavior, Not Implementation led to wrong-register, wrong-frame,
  source-restoration and scratch-erasure controls, plus a separate integer census.
- Laziness Protocol led to unsigned digit walks. Their monotone normalized
  partial sums avoid the extra target overshoot of signed-digit variants.

## Bounds and checks

New code has no recursion or dynamic code generation. Each function is at most
60 physical lines in the checked formatting. Scalar recipes contain at most
32 instructions. The generic ADD domain has numerator magnitude at most 255
and denominator at most 4096. Its exhaustive tests check 6643 input pairs under
all three policies. The unit-word search takes exactly three closure steps over
30 instructions, with actual cumulative states 1,19,208,1769. Its theoretical
path count is at most `1+30+30^2+30^3=27931`.

Files and decoded input payloads are limited to 8 MB. Native streams have at most
30000 events; expanded streams have at most 400000. Each compilation is sequential
and each of its two subprocesses has a 90-second timeout. The registered command
has a separate 240-second cap. Caches have at most 128 entries. The actual macro
alphabet has 38 entries. Only session-owned output directories are writable.

Contracts use explicit exceptions and remain enabled under optimization.
Inherited compiler children run without `PYTHONOPTIMIZE` or inherited
`PYTHONPATH`, with fresh bytecode-cache paths. Their assertions stay enabled.
No process delegates proof work to a background child. Files and logs use scoped
cleanup. Default work is disposable; explicit work is fresh and retained even
on failure. The tests exercise refusal to overwrite an existing workspace.

Every proof-relevant file is SHA256-authenticated before compilation. The
retained source records also identify the original commits and Git blobs.
Program equality and receipt comparison use canonical decompressed JSON, not
compressed-container hashes. Publication-byte checking is separate.

## Power of Ten deviations

Rule 3, fixed memory. Python's JSON, Fraction and container operations allocate
dynamically. This applies only to the bounded verifier. Input, event, recipe,
search and cache caps limit live work. Normal/optimized replays and the complete
bounded coefficient test exercise those paths. A fixed-capacity physical
implementation is a prerequisite for any later machine-cost claim.

Rules 4 and 5, inherited compiler structure. The byte-pinned native scripts have
long functions and assertion-based checks. Rewriting frozen scientific inputs
would invalidate this comparison. They execute only the authenticated finite
fixtures in nonoptimized, timeout-bounded subprocesses. New code does not adopt
their assertion dependency. Any compiler refactor needs its own source-bound
semantic comparison rather than an edit to these pins.

Rules 8 and 9, caching. The standard-library `lru_cache` wrapper has one fixed
call target, `literal.local_map`, and a 128-entry bound. Cache misses and repeated
checks must give the same exception-or-success validation result. The serialized
mutants exercise both new and repeated recipe shapes. No plugin or callback
registration is used.

Rule 10, Python diagnostics. Validation runs warnings as errors, Ruff formatting
and correctness diagnostics `E4,E7,E9,F,B,UP,SIM,PLE,PLW,RUF`. No full static type
proof is claimed for these untyped research scripts. The exact commands and
results are retained in `evidence/CHECKS.json`. Fixed-width data types and their
stronger static checks belong with the future physical implementation.

## Review boundary

Local source/control-flow and mathematical-accounting reviews were performed.
No separate reviewer process, independent human review, formal kernel, full
physical warp/wrapper replay, new owner/admission replay or outer release is
claimed. In particular, the writable-source guard is not silently assumed free;
the target-only alternative has its own explicit integer-width obligation.
