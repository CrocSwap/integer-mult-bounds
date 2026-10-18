# Validation and engineering limits

Local environment: macOS arm64, CPython 3.12.15 through uv and CPython 3.14.8
from Homebrew. Standard library only. Registered replay uses Python 3.12.

Commands from the repository root:

```sh
uv run --python 3.12 --no-project python -I -Werror -B scripts/research_package.py --package research/selected-extent-count-backing
/opt/homebrew/bin/python3.14 -I -O -Werror -B research/selected-extent-count-backing/verify.py
/opt/homebrew/bin/python3.14 -I -O -Werror -B research/selected-extent-count-backing/test_verify.py
uvx ruff check --select E4,E7,E9,F,I,UP,B,RUF research/selected-extent-count-backing/verify.py research/selected-extent-count-backing/test_verify.py
```

The registered primary replay and seven optimized tests pass. Optimized Python
3.14 also matches the exact receipt. The primary checks 4,099 products,
58 extent preparations, six complete native ADD fibres and four embedded
controls. Receipt hashes summarize the complete product and extent rows.
The tests separately check three literal asymmetric peaks, a one-cell-short
budget, zero-domain rejection, index padding, corrupt source rejection before
execution, hostile and None module bindings, retained cleared backing and an
actual native ADD endpoint.

A separate internal derivation independently reconstructed the product formula
and checked all 4,096 small pairs. A source review found one loader defect:
using None for both missing and preloaded module bindings broke restoration.
The implementation now uses a distinct missing sentinel, and the regression
covers both None and a hostile module object. The reviewer reran all seven
Python 3.12 tests and reported no remaining objections. This is internal
review with AI assistance, not independent human or formal-kernel review.

The checker compiles authenticated source bytes directly. It does not execute
unrelated top-level numeric/trace imports when extracting Geometry and the
ADD-only action. No stale bytecode or preloaded module can replace the seven
loaded runtime modules. Hashes establish source identity, not mathematical
correctness. Registered replay also applies the repository's bytecode isolation.

No complete selected GL64 node, full selected frontier replay, failure cleanup,
outer transfer, total caller reserve or physical tape placement was run or
proved. The ADD fixtures use fixed callbacks and toy geometries. Their complete
address permutations do not admit the selected catalogue.

## Engineering choices

Build the Lever led to the retained rerunnable backing census. Prove It Works
led to literal source execution and independent integer endpoints instead of
accepting a symbolic inventory alone. The source is frozen; new code adds no
production algorithm or inherited-loop changes.

All new functions fit within 60 physical lines after formatting. The public
fixture boundaries restrict products to positive 16-bit operands, contexts to
q=3/5, w=1/2 and n=1/2, spectator factors to 1..5, and index widths to
8/12/64/256. Each census enforces at most 32 tracked tapes, 2,048 cells per
tape and one million writes per fixture. Each numerical arena has 64 slots.
The fixed primary schedule has fewer than 4,200 source fixtures, with payloads
of at most 144 bits. Registered commands have 120-second timeouts. Assertions
are not acceptance gates; checks remain active under -O. Lint passes the
listed diagnostic set. Existing frozen loops remain within their admitted
finite fixture domains.

Power of Ten deviations are limited to the checker:

- Rule 3, memory allocation. Python and its libraries allocate dynamically.
  Fixed fixture domains, tape/write/arena limits and process timeouts bound
  this replay. The counted source backing is not a Python heap-capacity claim.
  Revisit allocation only when implementing a fixed physical allocator.
- Rule 8, dynamic execution. Seven authenticated modules and exactly two
  authenticated AST definitions must execute to observe unchanged source.
  The loader checks the exact finite inventory before compiling and restores
  all prior module bindings on every exit. Corruption and preload controls
  exercise this boundary. A future packaged runtime API could remove extraction.
- Rule 9, dispatch. Observational subclasses replace exactly three Tape
  bindings for allocation/write observation, and weak references avoid retained
  measurement roots. All bindings restore in finally. No source control flow
  or numerical arithmetic is replaced. The physical compiler must supply its
  own resource accounting; this observation mechanism is not that compiler.

No unrelated repository configuration was changed. Scientific inputs, the
selected result and frozen predecessor packages remain unchanged.
