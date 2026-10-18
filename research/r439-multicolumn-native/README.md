# Native replay of the R439 multi-column COPY handoffs

**PR2440's exact 84-ADD scatter passes the unchanged native legality and
5/9/11-stage column engines.** Its three nontrivial COPY windows share one
private slot, including handoffs at the same target-undo cut. This closes the
finite native-replay handoff in Sagar Thakrar's
[PR2440](https://github.com/CrocSwap/integer-mult-bounds/pull/2440), head
`1b38482a3a749f5815b074326b7ebda177a76f63`. The construction, 84 scatter ADDs
and 11,057 total ADDs remain his results. No new circuit, optimum or kappa is
claimed.

The prior [PR2421](https://github.com/CrocSwap/integer-mult-bounds/pull/2421)
native audit covers Ross Richardson's earlier 88-ADD stream with one long
COPY window. It does not execute this three-window stream. Here the exact
RAW6 SHA256 is
`8f2fa71b38492104a4ba7558b150dcdd7db9191b43fa4e1ee9c7d4e1d5d7f50c`.
The native engines receive these bytes, rather than a re-export of the
non-interleaved split word.

## Evidence

Both the 94-ADD split baseline and the 84-ADD candidate pass. The candidate's
13,986 records contain 11,057 ADDs, 2,911 MOVEs, nine COPYs and nine ERASEs.
The three long intervals span 18, 24 and 140 target-undo gates and contain
5, 15 and 10 scatter taps. All nine actual intervals and their record indices
are independently extracted from RAW6 in [REPLAY.json](REPLAY.json).

| Stages | Formal columns | Candidate scalar ADDs | Bridge ADDs | Omitted-bridge controls |
| ---: | ---: | ---: | ---: | ---: |
| 5 | 883 | 55,285 | 666 | 6 rejected |
| 9 | 1,327 | 99,513 | 1,998 | 18 rejected |
| 11 | 1,549 | 121,627 | 2,664 | 24 rejected |

These 48 bridge controls also reject on the baseline, for 96 in total.
The complete receipts, including each stage and every bridge omission, are
retained in [NATIVE.json](NATIVE.json). Paid rank mass remains 5,129 with the
predecessor's full histogram. The native positive envelopes agree exactly
with the predecessor: `F=25717`, `B=5030078`, 95 local bits and 181 bits in
the inherited nine-stage scalar bound, below the 104/192 caps.

Three additional controls run through the actual native binaries:

| Changed RAW6 stream | Native legality | All three column engines |
| --- | --- | --- |
| Next long COPY issued before the preceding ERASE | Rejects COPY lifecycle | Reject overlapping copies |
| ERASE names the preceding interval's owner | Rejects ERASE lifecycle | Reject original-source binding |
| A tap from the first long window moved just after the second long COPY | Passes, identical receipt | Reject dirty-column endpoint |

The last control preserves the complete instruction multiset. It demonstrates
that correct slot lifetimes, frame paths and paid counts do not establish that
a tap reads the intended retained column after a handoff.

## Reproduce

Python 3.12, Git and the standard library suffice for the registered checks:

```sh
python3.12 -B scripts/research_package.py --package research/r439-multicolumn-native
```

That command prints `PASS_R439_MULTICOLUMN_PYTHON_ONLY` and runs Git-free
export/corruption controls. It **does not run native code**. The native check
requires a C++17 compiler and Boost headers:

```sh
python3.12 -I -O -B research/r439-multicolumn-native/verify.py --native
```

Expected: `PASS_R439_MULTICOLUMN_NATIVE scatter=84 ADDs=11057 windows=3 controls=3 receipts_matched`.
Set `CXX` to the compiler and `BOOST_INCLUDE` to the Boost include root when
they are not on the normal search paths. `TEMP`/`TMP` on Windows or `TMPDIR`
on POSIX selects the temporary workspace. Each native build/run has a
180-second timeout. `--write` explicitly regenerates requested receipts;
default replay only compares them.

Local execution used CPython 3.12.14, GCC 16.2.0 from w64devkit 2.10.1 and
Boost 1.90.0 on Windows. Compiler/header archive hashes and commands are in
[VALIDATION.md](VALIDATION.md). The engine source bytes are unchanged.
[native_diagnostics.cpp](native_diagnostics.cpp) adds a separate translation
unit that prints the existing exception on termination: this GCC runtime
otherwise exits silently on an uncaught legality exception. It changes no
checker predicate or successful control path. Exact diagnostic substrings
and nonzero exits are required; a generic crash is not accepted as a control.

Source pins are checked before any predecessor code executes. Six exact
PR2440 files, including its CLI, witness, search receipt and result, are
retained under `vendor/pr2440/` and pinned by SHA256 and Git blob in
[PREDECESSOR.json](PREDECESSOR.json). The original CLI and complete receipt
are replayed first. All consumed live main inputs are pinned in
[SOURCES.json](SOURCES.json). Staging verifies full RAW6 and frame/state
metadata equality before native execution. Native comparisons discard only
elapsed time and the temporary input path; the latter is replaced by the
consumed stream's SHA256. The complete remaining receipt is compared using
typed canonical JSON.

## Limits

This is a source-bound execution audit with new handoff controls. It reuses
the credited construction verifier and native mathematical engines; it is
not a new derivation of the 84 circuit or an optimality proof. The copied
source is immutable in each tested interval, but physical recursive scratch
realization is not thereby proved.

The native legality receipt's inherited
`nondegeneracy_checked_by_separate_exact_bank_audit` field is not evidence
that this package runs that audit. Owner/selection fixtures are empty here.
Whole-call owner/hosting and projector routing, bank nondegeneracy,
all-size/compiler/common-label realization, precision/tape beyond the stated
scalar bounds, exact recovery, analytic transfer and replacement-interface
adoption remain external. Native engines do not authenticate ADD phase
labels; complete pinned RAW6 supplies phase provenance, as documented in
PR2421. No selected cold replay, hosted invoice, Lean proof or hosted CI pass
is claimed. The selected complex primitive remains binding.

## Open next questions

Can the exact 84 stream satisfy the complete physical owner/routing and
recursive scratch contract? Extend PR2437's binding for the 88 stream to all
three nontrivial COPY windows and same-cut handoffs recorded here. That would
connect this finite execution result to supplier admission. Physical hosting,
projector/scratch implementation and the all-size/compiler/common-label
obligations are the remaining blockers.

## Credit and scope

Sagar Thakrar supplies PR2440's construction and verifier, PR1062's source word
and PR2115's deferred basis. Ross Richardson supplies PR2407's interleaving
and PR2437's distinct hosting line; Sricharan Vagvala supplies PR2356's
interleaving method; Charles Bethin supplies PR2279's split-ideal optimum.
The native harness and staging checks follow starship-s PR2421 at
`71d10b283795d071c3680797f0e63856e6499fd2` and Gareth Davidson PR2373.
Gareth Davidson's target-basis lineage, Sricharan Vagvala's helper stars,
Aaron Wang's B circuits, Ross Richardson's frame circuit, DreamingOfClouds'
PR589 on eumemic's PR555, and the interface/exporter/native work of Zhihao
Chen, eumemic, woklerx, Arham Tahir, Dylan Crow and DaysSky retain their credit.
The carrier-skeleton LICENSE and NOTICE are pinned inputs.

The picker drew `bit-helper-contract`; [TASK.json](TASK.json) records the
deliberate change from already covered H2/K semantics to PR2440's concrete
native handoff. Base `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority 4.
All work stays in this new package; frozen predecessors and the selected
record are unchanged. Prepared for **ywz65** with substantial **OpenAI Codex
assistance** in implementation, validation and writing. No independent human
review is claimed. New material is Apache-2.0.
