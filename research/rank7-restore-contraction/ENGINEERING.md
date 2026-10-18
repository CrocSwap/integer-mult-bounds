# Verification and resource limits

## Design choices

Build the Lever led to a deterministic producer and verifier, including an
actual word-emission command. Prove It Works led to exact preimage checks,
arbitrary-dirty and common-idempotent identities, derived cleanup, full frame
itineraries, semantic controls and publication-byte comparison. No full native
replay or physical speedup is inferred from scalar gate counts.

The only new code is `contract.py`, `minimality.py`, `verify.py` and
`test_verify.py`. `frames.py` is an unchanged source-pinned reuse from PR3050.
Original notices and credit are retained. Shared code and frozen inputs are
unchanged.

## Power of Ten review

1. Control flow is structured and nonrecursive. Proof failures propagate before
   receipt or word emission. Test-only temporary directories use scoped cleanup.
   Child CLI processes have explicit 30-second timeouts and checked statuses.
2. Accepted sources have at most 3 MB of compressed/JSON input and 8 MB decoded
   input. Hash checks precede word decoding. A/B have at most 20,000 events each,
   restore 1,000, cleanup 60,000 and B warps 704. Scalar operators have at most
   1,000 gates on 704 rows. The projected block has at most four gates. The
   two-gate proof has 16 templates, four polynomial coefficients and 2x2
   matrices. Numeric template controls cover exactly 400 assignments; dense
   dirty controls cover 81 states and three projections. Registered commands
   each have a 120-second timeout.
3. Deviation, managed allocation. CPython, Fraction and JSON allocate during
   execution; fixed allocation would require another runtime. Scope is this
   bounded offline checker, not a service. A scalar matrix has at most 704²
   entries. The reused span cache holds at most 4,096 subspaces of at most 512
   points. Two pinned providers run sequentially. Coefficients are source-pinned
   and the replacement uses only -1, 1 and 2. A future unpinned-input service
   would need coefficient-growth and allocator limits before reusing this code.
4. Every function is below the 60-line review ceiling. Matrix algebra,
   production, frame enumeration, invoice comparison and CLI emission have
   separate responsibilities without forwarding abstractions.
5. Ordinary `require` calls enforce proof invariants and survive optimization.
   They reject changed preimages, dirty-state operators, frame itineraries,
   widths, cleanups, reports, buffers and inputs. The minimum proof fails on
   known one-gate targets rather than certifying them spuriously.
6. Matrix rows and candidate words have local ownership. The fixed OLD/NEW
   descriptions are never mutated. Production deep-copies the source before
   replacement. Only the bounded pure frame span function caches state. One
   test temporarily substitutes a source-directory constant inside a scoped
   mock context to check a real altered invoice file.
7. Input and return contracts are checked at the source, CLI and proof
   boundaries. Failures stop the command. The invalid CLI control deliberately
   consumes a nonzero status and checks that no output word was emitted.
8. No eval, generated executable code, plugins or production registration is
   used. Deviation, standard unittest and one scoped mock use dynamic dispatch.
   Their scope is the fourteen named test groups and one directory constant,
   with no user-selected callbacks.
9. Proof calls are direct and data ownership is explicit. There are no unsafe
   pointers or callback chains. The bounded unittest dispatch deviation above
   also applies to this rule.
10. Verification uses warnings-as-errors, normal/optimized receipt equality,
    source compilation and Ruff's E/F/B/UP/C4/SIM/PIE/PGH/RUF diagnostics. The
    registered replay repeats the proof and behavioral controls. Lint remains
    a documented local check, not a new repository-wide dependency. No separate
    static type checker is installed; Python runtime contracts and compilation
    are not claimed to replace one.

## Commands

Use an existing session-owned external `RUN` directory. The registered runner
isolates imported bytecode reads; direct `-B` only prevents cache writes.

```sh
python3.12 -W error -B research/rank7-restore-contraction/verify.py > "$RUN/result.json"
python3.12 -W error -O -B research/rank7-restore-contraction/verify.py > "$RUN/optimized.json"
cmp "$RUN/result.json" "$RUN/optimized.json"
TMPDIR="$RUN" python3.12 -W error -B research/rank7-restore-contraction/test_verify.py
ruff check --no-cache --config line-length=100 \
  --select E,F,B,UP,C4,SIM,PIE,PGH,RUF research/rank7-restore-contraction/*.py
python3.12 -B scripts/research_package.py --package research/rank7-restore-contraction
python3.12 -B scripts/check_research_commit.py --package research/rank7-restore-contraction
```

Verification and emission only write stdout. Test scratch is disposable and
removed by its context manager on normal success/failure. Setting TMPDIR keeps
it under RUN on this POSIX host. No selected cold replay, Lean, Docker or full
native/admission/outer replay is part of this package.
