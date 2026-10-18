# Verification and review record

Author execution used macOS arm64, CPython 3.12.15 and CPython 3.14.8.
The system `python3` is 3.9.6 and cannot run the repository's package generator;
its initial `Path.write_text(newline=...)` failure created no package. The
successful generator and all registered replay commands use CPython 3.12.

Checks performed before submission:

```sh
uv run --python 3.12 --no-project python -I -Werror -B \
  scripts/research_package.py --package research/selected-layout-numerical-lifetime
uv run --python 3.14 --no-project python -I -O -Werror -B \
  research/selected-layout-numerical-lifetime/verify.py
uvx ruff check --select E,F,I,B,UP,S,PIE,C4,SIM,RUF \
  research/selected-layout-numerical-lifetime/verify.py \
  research/selected-layout-numerical-lifetime/test_verify.py
uvx ruff format --check research/selected-layout-numerical-lifetime/verify.py \
  research/selected-layout-numerical-lifetime/test_verify.py
```

The registered replay recomputes the receipt and runs nine optimized controls.
All eleven exports also match their pinned Git bytes, blobs and SHA256 hashes.
The ten runtime/notice exports independently match the original PR2697 files
through PR2801's source manifest, rather than only its copied runtime claim.
A separate internal reviewer inspected the exact frozen source before the
checker existed and independently derived the same constants. It corrected
two presentation risks: maxima are coordinatewise, and `close` consumes three
entry indices rather than restoring its complete entry live set. The source
review also verified the conditional twelve-index adapter-entry composition.
The subsequent independent review executed normal and optimized CPython 3.12
primary replay and all nine optimized tests, independently checked all eleven
Git byte/blob/SHA256 pins, and found no technical flags. A relocated Git-free
optimized replay also passed with an unchanged complete file-hash inventory.
No independent human,
proof-assistant kernel, selected cold replay or complete GL64 payload check
is claimed.

## Checker constraints and deviations

Build the Lever shaped the rerunnable exact-source checker rather than a
hand-maintained numerical table. Prove It Works required real allocations,
returned cardinalities and erased-cell scans. Test Behavior, Not Implementation
shaped the one-Word-underbudget and output/restoration defect controls.

The Power of Ten inspection is scoped to the new checker and tests. Frozen
predecessor sources are authenticated evidence and retain their original style
and unbounded-by-constant digit/counter loops; they are not rewritten here.
The universal written proof bounds live numerical inventory independently of
loop length. This source audit does not certify the predecessor implementation
against all ten coding rules.

- Rules 1, 2, 4, 5, 6, 7: the checker has no recursive calls; its fixtures have
  45 shapes, at most 21 extent calls per fixture, 64 slots per arena, at most
  nine bits per numerical Word, and 30,000 allocation events per extent call.
  Every new function is below 60 physical lines. Runtime checks remain enabled
  under `-O`. Every phase checks borrowed state and owned-result contracts.
  Exceptions propagate and the replay manifest has a 180-second command cap.
- Rule 3, managed-runtime deviation in `verify.py` and `test_verify.py`: Python
  allocates objects during execution. Fixture limits above bound live replay
  data; cardinality outputs have at most 812 bits for the admitted fixture
  shapes. Test subprocesses have a 180-second timeout and temporary exports
  have scoped cleanup. This is checker resource discipline, not a proof of
  fixed Python heap allocation. Revisit if the finite fixture domain expands.
- Rules 8 and 9, source-loading/observation deviation in `load` and
  `observed_arena`: the checker dynamically compiles seven exact hash-pinned
  modules and the single original Geometry AST class, and subclasses one
  pinned Arena target. The immutable manifest authenticates all eleven source
  exports first; `exec` has only these bounded targets and ignores bytecode
  caches. The two narrow S102 annotations identify those intentional calls. The S603
  annotation in the typed-receipt subprocess test covers only the fixed current
  interpreter and a package copy in a managed temporary directory, with no shell.
  Numeric form/coefficient code is not loaded. A complete physical compiler
  should replace this finite Python observation mechanism when available.
- Rule 10: new Python runs with `-Werror`, Ruff's listed correctness, security,
  modernization and import diagnostics, plus format checks. Frozen sources
  are excluded from formatting/lint changes to preserve their exact bytes.
  No static type checker is configured for these dynamically loaded source
  modules. Additional type tooling is a follow-up if this loader becomes a
  shared API; this package keeps its explicit runtime boundary checks.

The source corruption tests reject modified manifest, Layout and Geometry
bytes before executing them. The mathematical mutation controls intentionally
replace one power operation or omit a free after authentication to prove the
independent output/restoration checks detect these distinct defects. They are
not exposed as an ordinary verifier option. The invalid-order witness expressly
fails the success precondition and documents the source's missing rollback.

## Attention

Independent read-only internal source review and execution found no technical
flags. The remaining mathematical and physical obligations are listed in
README.md. The local append-only trail remains in `.audit/scoped-certificate.tsv`.
