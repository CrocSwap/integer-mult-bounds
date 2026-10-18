# Implementation scope and bounds

The retained predecessor files are immutable inputs, not shared-code edits.
New code is limited to this package's exact certificate, separate finite
checks, CLI and tests. There is no network access, native build, recursion,
dynamic evaluation or background process in its replay.

## Design choices

- Build the lever. Keep the complete argument's finite decisions in scripts
  and a deterministic receipt, rather than a hand-maintained numerical table.
- Prove it works. Compare reconstructed roots with the actual pinned input,
  compare independent graph/flat/frame inventories, run deliberate failures
  under optimization, and check the final committed export and publication bytes.
- Do not expand an already covered case. The first `2,4,6^8` candidate was
  discarded after finding PR3162's implication. The one bounded pivot retains
  an actual different profile and two losing controls, 137 and 139.

## Power-of-ten inspection

1. Calls are acyclic. Traversals use explicit bounded stacks or queues.
   The only subprocess is the original TWOSIDE program, waited on with
   `check=True` and a 120-second timeout. Exceptions propagate as replay failure.
2. Dimensions are fixed at eight real coordinates and nine binary coordinates.
   There are 120 root lines, 248 rays, 58 graph vertices, 7,350 five-cliques,
   788,035 six-flats, 3,309,747 four-flats and 2,025 frames. Exhaustion checks
   enforce the predecessor's 40,000-state clique and 407-entry stack limits;
   the new frame traversal allows at most 2,000,000 visits and 961 stack entries.
   Flat loops are finite products of at most nine-bit row choices. The
   root-generated four-flat loop has `binom(35,4)=52,360` iterations. The
   relevant weighted pair check has exactly 963,900 tests.
3. Python and its standard library allocate dynamically. Strict allocation-free
   operation is unavailable in this implementation. The compensating limits
   are the fixed domains above, retained sets of 63 and 135 flat masks, at most
   2,025 frames, and no concurrent replay commands. The independent clique
   list has 7,350 entries; source reads are bounded by two MB and path depth 32.
   Input files and output streams are opened with scoped cleanup. A future
   constrained-memory implementation would use preallocated native buffers
   only if a measured resource limit requires it.
4. New functions remain below the approximately sixty-line review ceiling.
   They separate inventory generation, exact costs, source binding and CLI
   publication. No forwarding framework or migration layer was introduced.
5. Mathematical and source invariants use `require`, which raises normally,
   not Python assertions. The optimized test command checks corruption,
   unsupported domains, exhausted/truncated inventories and changed receipts.
6. Mutable search state is local to its owner. Module constants are fixed
   tuples, integers, paths or immutable sets. No selected record is modified.
7. Boundary reads validate paths, size, raw hashes and source semantics.
   JSON and arithmetic errors fail replay. Output is exclusive-create outside
   the checkout; overwrites and in-checkout destinations are rejected.
8. There is no code generation, reflection-based mathematical dispatch,
   dynamic import selection or evaluation. Standard `unittest` discovery is
   the bounded testing framework, not certificate logic.
9. Python member access and standard-library calls replace pointer operations.
   The test framework uses its normal dynamic method dispatch over sixteen
   named tests. This is a platform deviation from a ban on indirect calls;
   production mathematical calls have visible fixed targets. Removing the
   framework would not improve the certificate and is outside this scope.
10. Verification runs configured Ruff diagnostics on new source, warning-as-error
    compilation in an external bytecode namespace, normal/optimized replays,
    and both installed Python versions. Frozen vendor code keeps its exact
    predecessor bytes, including original formatting and APIs. It is reviewed
    as a dependency; style cleanup would invalidate its source pins and is
    deferred to an explicitly versioned successor, not silently performed here.

The managed-runtime allocation and unittest dispatch deviations are limited
to this finite standard-library package. The recorded checks enforce their
compensating bounds. No timing or multiplication-runtime speedup is claimed.
See `CHECKS.json` for the exact executed commands and verification limits.
