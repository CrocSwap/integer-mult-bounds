# Verification and code/resource scope

The reusable change is confined to this successor package.
Frozen source files, selected records and native compilers remain unchanged.

## Checks performed

- CPython 3.12.15 optimized exact replay passed.
- Registered Python 3.12 replay passed the scientific verifier and five
  behavioral test groups, including Git-free CLI success, semantic failures,
  source drift, typed receipt rejection and exclusive output creation. The
  final behavioral suite also passes a sixth group for byte, frame and trace
  bounds.
- CPython 3.13.5 replay with `-X dev -W error -I -O -B` passed with the identical
  scientific receipt.
- The unchanged complete PR2497 native checker passed from a pinned local copy,
  reporting 358 inputs, eight collectors, rank mass 3,126 and 12 controls.
  This is inherited native evidence, not a new native interpreter or CI replay.
- One fresh Python 3.12 scientific replay took 7.995 seconds and used 33,276 KiB
  peak resident memory on Linux x86_64 under WSL2. This is a local verifier
  measurement, not a multiplication-runtime claim or a guaranteed limit.

No hosted CI, proof assistant, independent human/peer review, rounded recursive
child, strict-zero physical erase, global hosting, all-size admission or selected
supplier cold replay was run or claimed.

## Code inspection

All changed production functions are at most 40 physical lines; test functions
are at most 31. Control flow is iterative, with no recursive call cycle. The
scientific replay checks return values and propagates file, JSON and arithmetic
failures. Explicit output uses exclusive creation and scoped file closure.
Semantic predicates use ordinary exceptions, so optimized Python does not
silence them. The typed receipt comparison uses canonical JSON, not Python's
numeric equality between integer and floating-point values.

Every scientific trace loop is bounded by 4,982 events. A reverse endpoint pass
has 358 functionals, each at most 4,982 steps. Input rows use at most 358 symbols;
defect rows use at most 4,966 distinct event symbols. There are at most 359 live
roles, including C. GF(2) frames have at most nine generators and 512 elements;
the frame cache holds at most 2,048 entries. Input reads allocate at most
2,000,001 bytes before rejecting oversize input. Source-pin inventories are
limited to 16 rows each. Guard selection examines exactly 64 candidates.
Test subprocesses have 120-second timeouts and finite explicitly enumerated
cases. The registered commands have 120- and 180-second timeouts.

The code directly calls the exact arithmetic and row routines. There is no
code generation, dynamic evaluation, user-selected executable import, global
configuration change or shared mutable research output. The test imports one
fixed sibling verifier module; unittest discovery is restricted to the six
methods in that file. All actual boundary assumptions are executable checks,
including frames, exact zeros, inverse-transpose rows, reverse sensitivities,
source identity and the complete signed receipt.

## Managed-runtime deviations

Rule 3, fixed memory allocation. Python dictionaries, sets and Fraction values
allocate during propagation, so fixed-capacity allocation is not available in
this exact standard-library implementation. This deviation covers only the
bounded finite replay. File, event, symbol, register and cache bounds above
limit live state; no persistent worker or unbounded queue exists. The fresh
replay measured 33,276 KiB peak RSS. A future larger domain must first reassess
those bounds rather than reuse this package's limits.

Rules 8 and 9, decorators and test discovery. `lru_cache(maxsize=2048)` wraps
only the pure binary-span routine, and unittest plus importlib loads one fixed
local verifier. These managed-runtime mechanisms have bounded targets and no
input-controlled dispatch. Positive and negative CLI/semantic cases exercise
both paths. If this package acquires configurable plugins, replace this fixed
boundary with explicit authenticated module selection before accepting them.

Rule 10, diagnostics. Registered checks enable Python development diagnostics
and warnings as errors for the behavioral suite; the production replay is also
checked under those flags on Python 3.13. No Python compiler, static type checker
or linter is configured in this package. Those unavailable checks are not
represented as completed analysis; exact behavioral and AST/function-length
inspection are the current controls. Any future repository-wide Python tooling
adoption should include both new code files without suppressions.
