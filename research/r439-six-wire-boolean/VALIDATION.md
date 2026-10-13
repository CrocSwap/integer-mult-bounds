# Executed verification

Run on Linux x86_64, CPython 3.14.4 and CPython 3.12.3, with GCC C++ 15.2.0 and
Boost 1.83 headers. The Boost headers came from Ubuntu
`libboost1.83-dev_1.83.0-5ubuntu5_amd64.deb`, SHA-256
`c17abc5a40a074c3d959655191ebec1561fa25f14f4948f6788be49417d4b234`.
No runtime Python package or solver is required.

The full documented verification command passed on Python 3.14.4. A second
complete execution passed under `python3.12 -I -O -B`, from `/tmp`, with only
this package and the thirteen manifest-listed upstream files copied into a
read-only input tree. Both executions freshly compiled the native checkers.
Their complete deterministic JSON receipts are byte-identical to each other
and to `EXPECTED.json`; SHA-256 of the pretty-printed receipt is
`462160c4fa5fc4c624b055ee9cece91a95d3b443f1758717abf465698b35371f`.

Completed coverage:

- All 172,800 nominations regenerated; every certificate field and the full
  decoded candidate reproduced. The 60-block domain gives 119,983 distinct
  per-block programs, 15,469 shorter programs and 440 positive-guard passes.
- Separate truth-table and positive-column code checks 448 Boolean inputs
  and 84 old/new positive column pairs across the seven replacements.
- A set-valued interpreter replays all 661 arbitrary dirty-input columns in
  both directions for all three complete words. It lowers and charges
  143,486 individual ADD/COPY/ERASE instructions across these six replays.
- The unchanged source checker passes exact E8 labels, frame closure and
  nesting, all 661 full-word columns, original H1-H5, and U/J/K/C-inverse on
  PR589, PR936 and the candidate. This rechecks the pinned PR936 artifact;
  it does not claim rerunning PR936's own discovery search.
- Fresh unchanged native legality and 5/9/11-stage checks pass on all three
  words, covering 883 / 1,327 / 1,549 formal columns for each word. All 144
  omitted-bridge controls reject. The ADD counts, exact local positive bounds
  and payload upper bounds agree with the independent interpreter. Every
  per-register MOVE sequence and COPY/ERASE record agrees across all words.
- Twelve local controls reject malformed gates, partial-block splices,
  incorrect physical participants, Boolean-typed coordinates, unpaid savings,
  Boolean-equivalent positive growth, stale literal cleanup, a dropped actual
  gate, unrelated payload edits and weak receipt equality.
- Seven artifact-admission tests pass in both Python environments. They cover
  semantically equivalent gzip recompression, corrupted input words, duplicate
  JSON keys, nonfinite JSON, missing sources and altered pinned checker bytes.
- All thirteen upstream source files match the named base Git objects, and all
  five predecessor artifacts match the PR936 tree objects. The exact byte
  hashes used at runtime are in `SOURCES.json`.
- `make selected-record-check` passes before and after the rebase onto
  `007664306fff84fbb1c9a1b4053b69f439764034`. All consumed source bytes are
  unchanged, so the full mathematical replays remain applicable.

An initial development run stopped before source/native replay because the
prefix-source binder expected an assignment to `nb`. The source establishes
the bridge count by an assertion after unpacking `small()`. The binder now
checks that exact assertion and the actual prefix assignment; the full runs
above include the fix. No numerical witness or expected certificate value was
changed to bypass the failure.

The final overlap inspection initially covered 716 open PRs and was refreshed
through PR949 before submission. PR936 remains the exact frozen input;
PR925 treats frame 267 with fixed integer transfer, untouched here. The newer
PR944/945/947/949 constructions and PR948 audit concern other objects. The
batch932 integration incorporates several earlier research packages but
changes no consumed input or selected bit word. There was no pinned sprint
coordination issue; `CLAIM.json` records the local scope.

The finite checks above do not constitute a full repository `make verify`,
selected complex cold replay, changed hosted-parent invoice or outer assembly,
or formal proof of the multiplication theorem. Hosted CI and maintainer
adoption are separate from these completed local checks.
