# Verification and engineering limits

## Scope and principles

Build the Lever led to a standalone deterministic checker instead of manual
matrix arithmetic. Prove It Works led to literal preimage reconstruction,
separate dirty-column and frame checks, semantic mutants and publication-byte
comparison. No predecessor Python module is imported or executed.

The audited object is the exact PR3042 head in VENDOR.json. Its original notices
are retained. The checker does not modify that package, shared tooling, frozen
inputs or the selected result. The maintained code is frames.py, verify.py and
test_verify.py in this package only.

## Power of Ten review

1. All proof control flow is structured and nonrecursive. Failure propagates as
   an exception before the final JSON is printed. Only the byte-mutation test
   acquires a temporary directory, owned by a context manager on every exit.
2. Source inventories have at most 32 entries; a scalar operator has at most
   1,000 gates on at most 704 rows. Frame lists have at most nine generators,
   each section at most 20,000 gates, and B has at most 704 warps. Cleanup has
   at most 60,000 forward events. Source bytes are hash-checked before decoding;
   compressed/JSON input is at most 3 MB and decoded input at most 8 MB. Other
   loops traverse these pinned bounded arrays, two edits, two providers, 704
   registers or fixed 512-vector subspaces. Registered commands have 120-second
   timeouts each. Input-shape failures propagate rather than retrying.
3. Deviation. CPython, Fraction and immutable JSON containers allocate during
   execution; static allocation would require another implementation/runtime.
   Scope is this bounded offline audit, not a service. The cache holds at most
   4,096 subspaces, each containing at most 512 vectors. Sparse matrices contain
   at most 704 squared rational entries and only the pinned dyadic coefficients
   are used in the accepted artifact. No process concurrency is used. A future
   unpinned-input service would need explicit coefficient-growth and allocator
   limits before reusing this implementation.
4. Functions remain below the repository-independent 60-line review limit.
   check_variant is near that limit and owns one cohesive variant obligation.
5. Proof checks use ordinary require calls and survive Python optimization.
   They cover source pins, literal equality, arbitrary dirty rows, monotone
   frames, derived cleanup, widths, actual skipped registers and complete cost.
6. Mutable rows and frame histories are local to a single calculation. The
   only cache is the bounded pure span function. Tests temporarily patch the
   package path only inside a context manager to test real byte corruption.
7. Every proof return contributes to the receipt or an equality check. Invalid
   gate kinds, zero denominators, dirty-state differences, illegal frames and
   stale bookkeeping fail. Test temporary writes and copies propagate errors.
8. There is no exec, evaluation, generated code or production registration.
   Deviation. Standard unittest discovery and mocking use runtime dispatch;
   scope is the fixed test class and the one context-managed path substitution.
   Thirteen named behavioral groups exercise that bounded mapping.
9. Proof calls target ordinary functions directly. Dictionaries contain scalar
   rows or explicit histories rather than chains of callbacks. The test-only
   unittest dispatch deviation in rule 8 applies here as well. No pointer or
   unsafe memory operations are used.
10. The verification run uses warnings-as-errors, normal and optimized receipt
    equality, source compilation and Ruff's E/F/B/UP/C4/SIM/PIE/PGH/RUF checks
    with a 100-column line limit. The registered replay runs the proof and all
    behavioral controls. Lint is a documented local check, not a new shared CI
    dependency.

## Commands

From the repository root, with RUN a fresh session-owned external directory:

```sh
python3.12 -W error -B research/rank7-restore-substitution-audit/verify.py > "$RUN/result.json"
python3.12 -W error -O -B research/rank7-restore-substitution-audit/verify.py > "$RUN/optimized.json"
cmp "$RUN/result.json" "$RUN/optimized.json"
TMPDIR="$RUN" python3.12 -W error -B research/rank7-restore-substitution-audit/test_verify.py
ruff check --no-cache --config line-length=100 \
  --select E,F,B,UP,C4,SIM,PIE,PGH,RUF research/rank7-restore-substitution-audit/*.py
python3.12 -B scripts/research_package.py --package research/rank7-restore-substitution-audit
python3.12 -B scripts/check_research_commit.py --package research/rank7-restore-substitution-audit
```

Direct verification emits only stdout. Test scratch uses the operating system's
temporary-directory API and is removed on normal exceptions and success; setting
TMPDIR keeps it inside RUN on this POSIX host. The registered launcher isolates
bytecode-cache reads. Direct -B execution does not provide that isolation.
No full native, geometry, selected cold replay, Lean or Docker run was performed.
