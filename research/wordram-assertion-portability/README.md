# Preserve bounded-kernel certificate checks under optimized Python

This contribution was produced by Nick Petalas. New work is Apache-2.0.

The unchanged PR5466 bounded Word RAM entry point rejects `-O` because its
certificate checks use Python assertions. This opt-in, source-bound adapter
executes its complete checklist under `-O` with all 55 assertion sites retained
as explicit failure branches. Frozen source files and their credit are unchanged.

Claim type: scoped implementation-preservation proof with finite conformance
evidence. The adapter's complete scientific output equals the original normal
entry point's output after removing its clock field. This is a portability
improvement. It supplies no new arithmetic result, storage improvement, runtime
speedup, supplier admission, kappa or independent predecessor audit.

[PROOF.md](PROOF.md) explains predicate/message evaluation, the exact entry-guard
change, the import boundary and the full checklist comparison. The new adapter
compiles authenticated source bytes in memory; it never rewrites the predecessor.
Every imported source module bypasses stale bytecode. The separate NTT child
runs its unchanged eight-test discovery domain with the same optimization level
and a fresh bytecode-cache prefix.

## Evidence and reproduction

From the repository root, with standard-library CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/wordram-assertion-portability/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/wordram-assertion-portability/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/wordram-assertion-portability
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/wordram-assertion-portability --check-source-history
```

Use another CPython 3.12 path elsewhere. `--scratch PATH` puts temporary cache
directories in an existing external directory. The commands emit generated
JSON receipts on stdout and write no package files. Expected markers include
`PASS_WORDRAM_ASSERTION_PORTABILITY`, `PASS_REGISTERED_RESEARCH_PACKAGE` and
`PASS_RESEARCH_COMMIT_BYTES`. The publication command requires committed bytes
and full Git history.

Each invocation compares against a fresh original normal execution. The retained
checklist covers all eight NTT unittest groups, 65,537 modular-multiply inputs,
5,096 butterfly fixtures, 2,197 circuit fixtures, 277 complete-program cases and
20 approximate-backend pairs at each of two precisions. These are predecessor
coverage domains, preserved here rather than claimed as new mathematical results.

New checks compare eight assertion-evaluation fixtures at compiler levels 0, 1
and 2, giving 24 semantic comparisons. Nine controls reject five boundary faults
and wrong RAM, circuit, whole-program and FFT results. The receipt enumerates
every adapted assertion site. A site inventory is not a claim that each site
has a separate falsifying fixture.

## Scope and sources

Card `portable-replay`, priority revision 8, is refined to this exact optimized-
interpreter refusal. Base `7c49fe32c55de02c2c873655c804b16e4c3fef0a` contains the
entire 33-file original package closure. [SOURCES.json](SOURCES.json) pins every
file; [VERIFY.json](VERIFY.json) declares every live input. No pending Git object,
network service or predecessor installation is needed. The direct command also
works in a Git-free export containing these declared inputs.

[Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19361778).
Live claims, local reservations, open/account/merged PR searches and distinctive
main README searches were checked. The card overlap snapshot covered 380 open
PRs and 6,300 Discussion records with complete remote pagination; its sparse
local scan omitted 8,797 note paths. Main-tree term searches supplemented that
scan. Unpublished work and arbitrary historical diffs remain coverage limits.
PR5886 concerns address liveness and reduced RAM storage, a separate result.

The scientific statement remains the predecessor's informal theorem and bounded
executable evidence. No selected cold replay, native/compiler/physical replay,
Lean build, Docker run or independent human/proof-kernel review is claimed.
The selected frontier and five framework assumptions remain unchanged. Full
source replays cover normal Python and `-O`; `-OO` has synthetic semantic checks
only. Native Windows execution is unrun. See the proof's explicit restrictions
on introspection, tracebacks, dynamic allocation and controlled metaprogramming.

## Open next questions

Can every retained assertion site receive an explicit falsifying fixture without
changing the scientific domain? Start with a site-visit trace and distinguish
unreached contracts from repeated predicates. The present inventory and four
component faults do not establish that stronger coverage.

Does the same complete command pass on native Windows CPython 3.12? Start from
the committed Git-free export and retain subprocess return codes, output and
file hashes. No platform-specific success follows from the source-preservation
argument alone.

## Credit

David Ganz / Dugongue supplied PR5466's bounded kernel, exact NTT, interpreted
Word RAM programs, circuit checks, approximate recovery and complete checklist.
The original tcslib, FastPoly, CatCrypt, mpfx, arithmetic and multiplication
lineages retain all credit in the unchanged NOTICE.txt and source notices.
Python assertion semantics, AST lowering and fresh-cache execution are standard
techniques. The contribution here is their restricted, source-bound adapter and
its preservation checks. Predecessor scientific claims are cited premises.
