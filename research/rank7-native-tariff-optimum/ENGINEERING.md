# Implementation checks and limits

## Checks run

Linux 6.6.87.2 WSL2, x86-64, glibc 2.41, CPython 3.12.
Commands ran serially, with `TMPDIR` and Python bytecode prefixes in the
session-owned external directory. The main checkout was not edited.

```sh
python3.12 -X dev -W error -B research/rank7-native-tariff-optimum/verify.py
python3.12 -W error -B research/rank7-native-tariff-optimum/test_verify.py
python3.12 -O -W error -B research/rank7-native-tariff-optimum/test_verify.py
python3.12 -B scripts/research_package.py --package research/rank7-native-tariff-optimum
ruff format --check --no-cache research/rank7-native-tariff-optimum/{tariff,verify,test_verify}.py
ruff check --no-cache --select E,F,I,B,UP,SIM,C4,PIE,RUF \
  research/rank7-native-tariff-optimum/{tariff,verify,test_verify}.py
```

Six full native transport/emitter pairs pass, with twelve orientation ledgers.
Normal and optimized behavioral runs each pass fourteen groups. Registered
replay passes. The fresh direct receipt is byte-identical to the committed
`evidence/RESULT.json`. Development-mode direct replay took 14.39 seconds;
Linux reported maximum child RSS of 299,228 KiB. These numbers describe the
verifier workload, not multiplication or a native circuit runtime.

The initial negative-test expectation was wrong. Native transport accepted a
wrong restore with its matched inverse and accepted operator-equivalent stale
cleanup. The revised tests preserve those positive native controls and require
our separate restore/cleanup boundary checks to reject them. No inherited
validator was weakened to obtain a PASS.

No native instruction expansion, physical Clifford warp/wrapper replay,
precision/magnitude, all-size or supplier/outer release was run. There was no
independent human, formal-kernel or separate-agent review. Local review used
two passes, one for the all-length tariff proof and one for source/application
and failure coverage.

## Engineering decisions

Build the Lever led to `tariff.py` plus a rerunnable six-compilation verifier,
rather than a hand-counted saving. Prove It Works led to comparison of literal
compiled streams and the separate native endpoint acceptance controls. Test
Behavior, Not Implementation led to actual compiler invocations, copied source
mutants and proof-hypothesis witnesses rather than tests of constants alone.

## Power-of-ten review

1. New functions use structured flow and do not recurse. Library-traversal
   deviation covers Python's `deepcopy` and JSON codecs on fixed pinned word
   structures, whose measured maximum container depth is four. No recursive
   search is introduced. Exceptions propagate with context-managed output
   files and disposable workspaces. A broader input model must validate depth
   or replace recursive copying before it can reuse this limit.
2. Inputs are source-pinned. Word sections are capped at 20,000 gates except
   cleanup at 60,000 and restore at 1,000; emitted streams are capped at 60,000.
   There are two variants, three words and two compiler stages per word. Every
   native subprocess has a 90-second timeout. The registered audit has 300
   seconds and tests have 180. The finite low-cost census checks 368 cores.
3. Managed-runtime deviation. Python allocates JSON, rational rows and event
   lists after initialization. File and decoded payload limits are eight MB,
   the frame cache has 4,096 entries and each frame has at most 512 points.
   Exact pinned inputs bound rational arithmetic and native rows. Three
   compiled cases remain live per variant, with no concurrent compiler work.
   Live memory was measured above. Follow-up is a streaming comparison if
   larger dimensions or additional providers are proposed; these limits must
   be reassessed before such expansion.
4. The longest new function after formatting is `compile_word`, 46 physical
   lines. Frozen `bw_transport.py::run` and several inherited emitter helpers
   exceed one page. Refactoring those scientific source inputs would break the
   exact-byte replay boundary and is outside this patch. They run only on the
   bounded fixtures above. A future upstream compiler-maintenance task should
   refactor and repin them with unchanged output controls.
5. Production contracts use `require`, so our checks remain active under
   optimization. The inherited scripts rely on assertions and explicitly
   refuse optimized execution. Full replay is refused under `-O`; optimized
   tests launch the inherited stages with assertions enabled.
6. Work directories, event lists and mutable word copies are local. No shared
   compiler output or worker state is used. `--work` refuses existing paths;
   temporary mode cleans success and failure outputs.
7. Input shapes, pin inventories, source containment, word-export byte counts,
   subprocess exit status and all proof-relevant output fields are checked.
   `subprocess.run(check=True)` consumes nonzero exits as exceptions; the
   success process object is intentionally discarded because stdout is a
   diagnostic log and JSON files supply the checked result. Timeouts propagate.
   Deliberate timeout injection and hard-kill cleanup were not tested. Explicit
   work retains diagnostics; a hard kill can bypass disposable cleanup.
8. New code uses ordinary modules and functions, without code generation,
   dynamic evaluation or runtime registration. Native scripts execute in
   isolated subprocesses.
9. No pointers or open-ended dispatch were added. `map` calls use explicit
   local functions. Framework-dispatch deviation is limited to `unittest`
   discovering fourteen fixed methods and the test-only `patch.object`
   changing the copied package path. Frozen native helper closures remain
   unchanged; bounded fixtures and literal output comparisons constrain them.
10. Runtime diagnostics use `-X dev -W error`; recurring registered commands
    use `-W error`. Ruff's applicable correctness, imports, bug, modernization,
    simplification and formatting families pass on new code. No type checker
    or compiled build is configured for this standard-library research package.
    Frozen source style is not reformatted because exact source identity is
    part of the replay contract. A compiler-maintenance follow-up, rather than
    this scientific successor, owns new diagnostics and refactoring there.

Both actual `--emit-word` CLI variants were run; their canonical hashes equal
the candidate hashes in the evidence receipt. The prepublication refresh at
2026-10-16 21:18 UTC retained canonical main
`d8e0f83f00191df62174b641e9fff055c357f641`, priority revision 6, the selected
record and the invoice dependency. PR3056's exact source head was unchanged.
The overlap helper reported complete pagination for 301 open PRs and 1,802
Discussion records. Closed work was covered through local notes and the
ledger, not a remote closed-PR scan. No diff or unpublished-work novelty
claim follows from that coverage.

Byte-exact predecessor files are listed in `VENDOR.json`; package-local Git
attributes preserve their original newline spellings. New code does not alter
or silently repair those frozen sources. Publication-byte comparison is a
separate required preflight, after committing.
