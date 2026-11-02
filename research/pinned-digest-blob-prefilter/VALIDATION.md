# Validation record

## Frozen inputs and intentional execution

All four external source files were retained and byte-authenticated before the
first scientific source execution. `SOURCE-PINS.json` is itself SHA256-pinned by
both new checkers. It authenticates byte length, Git blob identity and SHA256;
the independent checker separately hardcodes the four source identities.

The primary intentionally executes the authenticated PR6357/PR6428 scanner
variants in a temporary Git fixture. The canonical helper module is not imported:
AST extraction retains exactly `_GIT_REDIRECT_VARS`, `_GIT_CONFIG_PREFIXES` and
`git_source_env`, with `os` supplied. Temporary module registration is restored
after source loading. The independent oracle imports neither source executable
nor the new adapter/verifier. It authenticates those source bytes as provenance,
implements its own fixture and compares native Git per-path truth with a separate
unique-object raw filter and complete report reconstruction.

Git version observed during preparation: `git version 2.50.1 (Apple Git-155)`.
Runtime version and wall/resource measurements are outside deterministic JSON
receipts. POSIX filename fixtures and successful stable ordinary Git semantics
are the declared domain. This is not a Windows lifecycle check.

## Controls and corrections

The first primary launch returned 127 before source execution because the tool
PATH had no `python3.12`. The existing managed Python 3.12 interpreter was then
used; no software was installed. That first failed launch and stderr are retained
in the session evidence outside this package. The first actual source execution
passed the explicit 26-row mixed fixture.

Before final sealing, review tightened two accounting statements: received-byte
metrics increment by actual successful reads, and streaming memory is stated as
O(chunk size), with a chunk-plus-63 bound for each search window rather than an
exact total for all coexisting buffers. The fixture environment also strips Git
repository/config injection before temporary writes, fixes author/committer and
dates, and isolates global/system policy and ignore files. The real adapter keeps
the original source environment contract. These changes do not alter the frozen
source bytes.

The policy controls use actual Git classifications for same-object aliases,
including ASCII custom-binary drivers and NUL-containing forced-text paths.
An actual candidate-expansion mutation removes aliases and loses five full
report rows; it is rejected, not accepted as an optimized result. Fallback
controls cover argument limits, recursive settings, an injected reader failure
and an unsupported invocation. The independent oracle separately tests native
per-path membership, longer-token substrings, stream crossings and literal paths.
Its scope does not independently establish every fallback control.
The injected reader failure tests fallback wiring; it does not inject malformed
batch headers or truncated stream bytes into a live Git child.

Primary strict receipt SHA256:
`87e6fc1f9663f8c55d22f1f267611f6fd438de07609c2c5ecf1f68da4c30d309`.
Independent strict receipt SHA256:
`82db963897be33591b489917ef9cdb578e5374d245abacf229b173ea6158515c`.
The oracle's first receipt was sealed before it read the new primary code or
receipt. Primary normal/optimized emission and strict-default runs passed, with
identical retained JSON. The oracle likewise passed normal/optimized emission
and strict-default runs on its separate history. Root's cold exported replay is
additional transport/reproducibility evidence, not a third independent method.

## Controlled timing comparison

`BENCHMARK.json` retains five alternating warm full-CLI triplets on the same
primary fixture, including Python process startup. Every invocation had identical
complete JSON stdout and exit code 1 (the fixture intentionally has frozen stale
pins). Median seconds were 0.138180 for the repaired predecessor, 0.109483 for
PR6428 reuse, and 0.143418 for the candidate prefilter. The added pass was slower
on this small fixture. This is a measured negative performance outcome, not a
runtime improvement or a historical-main benchmark. `benchmark.py` can repeat
the procedure and prints only stdout; timing values are observations, not strict
replay targets or confidence intervals.

## Scope of verification

Strict complete receipts distinguish JSON types, reject duplicate keys and
nonfinite constants, and require the retained files by default. No `assert`
statement guards acceptance. `--emit` writes only stdout. Complete controlled
reports and CLI stdout/exit behavior are compared, not just aggregate row counts.
Normal and optimized Python, package/source provenance, commit modes/history and
cold exported replays are separate obligations recorded in the public handoff
and session receipts.

No canonical 154-row historical replay, physical I/O/decompression measurement,
universal Git diagnostic equivalence, speedup, mathematical supplier admission,
κ change or selected-frontier update is asserted. Git is intrinsic to replay;
there is no empty-PATH or Git-free claim. All source code changes are confined to
this new package; shared scanners, CI configuration and existing research remain
unchanged.
